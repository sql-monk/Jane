"""PostgreSQL store of the registry (ADR-0002 §1): own database ``jane_registry``, tables in ``db_schema``.

Also implements the jane-kit ``IdempotencyStore`` and ``JobStore`` protocols, so several registry
instances share idempotency keys and upstream-port jobs. Publications of one package are serialised by
``SELECT ... FOR UPDATE`` on the package row; ``(package_id, version)`` is the primary key of a version,
so a concurrent duplicate publish fails with ``version_exists``.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

from psycopg import Connection, errors, sql
from psycopg.rows import dict_row
from psycopg.types.json import Json, Jsonb
from psycopg_pool import ConnectionPool

from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_kit.jobs import Job, JobLimits

from .settings import DbLimits
from .store import (
    AlreadyExists,
    LimitReached,
    PackageFilter,
    PackageRecord,
    RevisionMismatch,
    StatusMismatch,
    VersionExists,
    VersionRecord,
    now,
    pick_latest,
)

__all__ = ["PostgresIdempotencyStore", "PostgresJobStore", "PostgresStore"]

SCHEMA_VERSION = 1
_DDL = """
CREATE TABLE IF NOT EXISTS registry_schema_version (version int PRIMARY KEY, applied_at timestamptz NOT NULL);
CREATE TABLE IF NOT EXISTS registry_packages (
    package_id text PRIMARY KEY,
    kind text NOT NULL,
    title text NOT NULL,
    description text,
    auto_changes_allowed boolean NOT NULL,
    deprecated boolean NOT NULL DEFAULT false,
    fork_of jsonb,
    fork_parent text GENERATED ALWAYS AS (fork_of ->> 'package_id') STORED,
    owner text,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    revision bigint NOT NULL DEFAULT 1,
    latest_version text,
    tags text[] NOT NULL DEFAULT '{}',
    entity_types text[] NOT NULL DEFAULT '{}',
    media_types text[] NOT NULL DEFAULT '{}',
    domains text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS registry_packages_kind ON registry_packages (kind);
CREATE INDEX IF NOT EXISTS registry_packages_fork_parent ON registry_packages (fork_parent);
CREATE INDEX IF NOT EXISTS registry_packages_entity_types ON registry_packages USING gin (entity_types);
CREATE INDEX IF NOT EXISTS registry_packages_tags ON registry_packages USING gin (tags);
CREATE TABLE IF NOT EXISTS registry_versions (
    package_id text NOT NULL REFERENCES registry_packages (package_id),
    version text NOT NULL,
    seq bigserial NOT NULL,
    digest text NOT NULL,
    status text NOT NULL,
    test_status text NOT NULL,
    manifest json NOT NULL,  -- json keeps the key order of jane-package.json
    files jsonb NOT NULL,
    size_bytes bigint NOT NULL,
    created_at timestamptz NOT NULL,
    created_by text NOT NULL,
    published_by text,
    ported_parent_version text,
    search jsonb NOT NULL,
    PRIMARY KEY (package_id, version)
);
CREATE INDEX IF NOT EXISTS registry_versions_seq ON registry_versions (package_id, seq DESC);
CREATE INDEX IF NOT EXISTS registry_versions_digest ON registry_versions (digest);
CREATE TABLE IF NOT EXISTS registry_status_history (
    id bigserial PRIMARY KEY,
    package_id text NOT NULL,
    version text NOT NULL,
    entry jsonb NOT NULL,
    FOREIGN KEY (package_id, version) REFERENCES registry_versions (package_id, version)
);
CREATE INDEX IF NOT EXISTS registry_status_history_version ON registry_status_history (package_id, version, id);
CREATE TABLE IF NOT EXISTS registry_test_reports (
    id bigserial PRIMARY KEY,
    package_id text NOT NULL,
    version text NOT NULL,
    record jsonb NOT NULL,
    FOREIGN KEY (package_id, version) REFERENCES registry_versions (package_id, version)
);
CREATE INDEX IF NOT EXISTS registry_test_reports_version ON registry_test_reports (package_id, version, id);
CREATE TABLE IF NOT EXISTS registry_idempotency (
    key text PRIMARY KEY,
    fingerprint text NOT NULL,
    state text NOT NULL,
    expires_at timestamptz NOT NULL,
    response jsonb
);
CREATE TABLE IF NOT EXISTS registry_jobs (
    job_id text PRIMARY KEY,
    doc jsonb NOT NULL,
    finished_at timestamptz,
    updated_at timestamptz NOT NULL
);
"""

_PKG_COLS = (
    "package_id, kind, title, description, auto_changes_allowed, deprecated, fork_of, owner, labels, "
    "revision, latest_version, tags, entity_types, media_types, domains, created_at, updated_at"
)
_VER_COLS = (
    "package_id, version, seq, digest, status, test_status, manifest, files, size_bytes, created_at, "
    "created_by, published_by, ported_parent_version"
)

_INSERT_VERSION = (
    "INSERT INTO registry_versions (package_id, version, digest, status, test_status, manifest, files, "
    "size_bytes, created_at, created_by, published_by, ported_parent_version, search) VALUES "
    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING package_id, version, seq, digest, status, "
    "test_status, manifest, files, size_bytes, created_at, created_by, published_by, ported_parent_version"
)


def _pkg(row: dict[str, Any]) -> PackageRecord:
    return PackageRecord(
        package_id=row["package_id"],
        kind=row["kind"],
        title=row["title"],
        description=row["description"],
        auto_changes_allowed=row["auto_changes_allowed"],
        deprecated=row["deprecated"],
        fork_of=row["fork_of"],
        owner=row["owner"],
        labels=row["labels"] or {},
        revision=row["revision"],
        latest_version=row["latest_version"],
        tags=list(row["tags"]),
        entity_types=list(row["entity_types"]),
        media_types=list(row["media_types"]),
        domains=list(row["domains"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _ver(row: dict[str, Any]) -> VersionRecord:
    return VersionRecord(
        package_id=row["package_id"],
        version=row["version"],
        seq=row["seq"],
        digest=row["digest"],
        status=row["status"],
        test_status=row["test_status"],
        manifest=row["manifest"],
        files=row["files"],
        size_bytes=row["size_bytes"],
        created_at=row["created_at"],
        created_by=row["created_by"],
        published_by=row["published_by"],
        ported_parent_version=row["ported_parent_version"],
    )


def _like(text: str) -> str:
    return "%" + text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


class _SyncStore:
    name = "postgres"

    def __init__(self, dsn: str, schema: str, limits: DbLimits) -> None:
        self.dsn = dsn
        self.schema = schema
        self.limits = limits
        self.pool: ConnectionPool[Connection[dict[str, Any]]] | None = None

    def _configure(self, conn: Connection[dict[str, Any]]) -> None:
        conn.execute(
            sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)),
        )
        conn.execute(
            sql.SQL("SET statement_timeout = {}").format(sql.Literal(self.limits.statement_timeout_ms))
        )
        conn.commit()

    def open(self) -> None:
        self.pool = ConnectionPool(
            self.dsn,
            min_size=self.limits.pool_min_size,
            max_size=self.limits.pool_max_size,
            timeout=self.limits.connect_timeout_ms / 1000,
            kwargs={
                "row_factory": dict_row,
                "connect_timeout": max(1, self.limits.connect_timeout_ms // 1000),
            },
            configure=self._configure,
            open=False,
        )
        self.pool.open(wait=True, timeout=self.limits.connect_timeout_ms / 1000)
        self.migrate()

    def close(self) -> None:
        if self.pool is not None:
            self.pool.close()

    @contextmanager
    def tx(self) -> Iterator[Connection[dict[str, Any]]]:
        assert self.pool is not None, "store is not open"
        with self.pool.connection() as conn, conn.transaction():
            yield conn

    def migrate(self) -> None:
        with self.tx() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(hashtext('jane_registry_schema'))")
            conn.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(self.schema)))
            conn.execute(_DDL.encode())
            conn.execute(
                "INSERT INTO registry_schema_version (version, applied_at) VALUES (%s, now()) "
                "ON CONFLICT (version) DO NOTHING",
                (SCHEMA_VERSION,),
            )

    def check(self) -> bool:
        with self.tx() as conn:
            conn.execute("SELECT 1")
        return True

    # ------------------------------------------------------------------ packages
    def create_package(self, pkg: PackageRecord) -> PackageRecord:
        try:
            with self.tx() as conn:
                cur = conn.execute(
                    f"INSERT INTO registry_packages ({_PKG_COLS}) VALUES "  # noqa: S608
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                    (
                        pkg.package_id,
                        pkg.kind,
                        pkg.title,
                        pkg.description,
                        pkg.auto_changes_allowed,
                        pkg.deprecated,
                        Jsonb(pkg.fork_of) if pkg.fork_of else None,
                        pkg.owner,
                        Jsonb(pkg.labels),
                        pkg.revision,
                        pkg.latest_version,
                        pkg.tags,
                        pkg.entity_types,
                        pkg.media_types,
                        pkg.domains,
                        pkg.created_at,
                        pkg.updated_at,
                    ),
                )
                row = cur.fetchone()
        except errors.UniqueViolation as exc:
            raise AlreadyExists(pkg.package_id) from exc
        assert row is not None
        return _pkg(row)

    def get_package(self, package_id: str) -> PackageRecord | None:
        with self.tx() as conn:
            cur = conn.execute("SELECT * FROM registry_packages WHERE package_id = %s", (package_id,))
            row = cur.fetchone()
        return _pkg(row) if row else None

    def update_package(
        self, package_id: str, changes: dict[str, Any], expected_revision: int | None
    ) -> PackageRecord:
        allowed = {"title", "description", "auto_changes_allowed", "deprecated", "labels"}
        assert set(changes) <= allowed, changes
        with self.tx() as conn:
            cur = conn.execute(
                "SELECT revision FROM registry_packages WHERE package_id = %s FOR UPDATE", (package_id,)
            )
            row = cur.fetchone()
            if row is None:
                raise KeyError(package_id)
            if expected_revision is not None and row["revision"] != expected_revision:
                raise RevisionMismatch(row["revision"])
            sets = [sql.SQL("{} = %s").format(sql.Identifier(k)) for k in changes]
            values = [Jsonb(v) if k == "labels" else v for k, v in changes.items()]
            query = sql.SQL(
                "UPDATE registry_packages SET {}, revision = revision + 1, updated_at = %s "
                "WHERE package_id = %s RETURNING *"
            ).format(sql.SQL(", ").join(sets))
            cur = conn.execute(query, (*values, now(), package_id))
            updated = cur.fetchone()
        assert updated is not None
        return _pkg(updated)

    def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
        where: list[str] = []
        args: list[Any] = []
        if after is not None:
            where.append("package_id > %s")
            args.append(after)
        if flt.kind:
            where.append("kind = %s")
            args.append(flt.kind)
        if flt.fork_of:
            where.append("fork_parent = %s")
            args.append(flt.fork_of)
        if flt.tag:
            where.append("%s = ANY(tags)")
            args.append(flt.tag)
        if flt.entity_type:
            where.append("%s = ANY(entity_types)")
            args.append(flt.entity_type)
        if flt.media_type:
            wanted = flt.media_type.lower()
            where.append("EXISTS (SELECT 1 FROM unnest(media_types) m WHERE lower(m) IN (%s, %s, '*/*'))")
            args.extend([wanted, wanted.split("/", 1)[0] + "/*"])
        if flt.domain:
            d = flt.domain.lower().rstrip(".")
            where.append("EXISTS (SELECT 1 FROM unnest(domains) h WHERE %s = h OR %s LIKE '%%.' || h)")
            args.extend([d, d])
        if flt.q:
            where.append(
                "lower(package_id || ' ' || title || ' ' || coalesce(description, '') || ' ' || "
                "array_to_string(tags, ' ') || ' ' || array_to_string(entity_types, ' ')) LIKE %s ESCAPE '\\'"
            )
            args.append(_like(flt.q.lower()))
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with self.tx() as conn:
            cur = conn.execute(
                f"SELECT * FROM registry_packages {clause} ORDER BY package_id LIMIT %s",  # noqa: S608
                (*args, limit),
            )
            rows = cur.fetchall()
        return [_pkg(r) for r in rows]

    def count_forks(self, package_id: str) -> int:
        with self.tx() as conn:
            cur = conn.execute(
                "SELECT count(*) AS n FROM registry_packages WHERE fork_parent = %s", (package_id,)
            )
            row = cur.fetchone()
        return int(row["n"]) if row else 0

    def delete_package_if_empty(self, package_id: str) -> None:
        with self.tx() as conn:
            conn.execute(
                "DELETE FROM registry_packages p WHERE package_id = %s "
                "AND NOT EXISTS (SELECT 1 FROM registry_versions v WHERE v.package_id = p.package_id)",
                (package_id,),
            )

    # ------------------------------------------------------------------ versions
    def _refresh(self, conn: Connection[dict[str, Any]], package_id: str, touched: datetime) -> None:
        cur = conn.execute(
            "SELECT version, status, search FROM registry_versions WHERE package_id = %s", (package_id,)
        )
        rows = cur.fetchall()
        latest = pick_latest([(r["version"], r["status"]) for r in rows])
        fields: dict[str, list[str]] = next((r["search"] for r in rows if r["version"] == latest), {})
        conn.execute(
            "UPDATE registry_packages SET latest_version = %s, tags = %s, entity_types = %s, media_types = %s, "
            "domains = %s, revision = revision + 1, updated_at = %s WHERE package_id = %s",
            (
                latest,
                fields.get("tags", []),
                fields.get("entity_types", []),
                fields.get("media_types", []),
                fields.get("domains", []),
                touched,
                package_id,
            ),
        )

    def _history(self, conn: Connection[dict[str, Any]], v: VersionRecord) -> VersionRecord:
        cur = conn.execute(
            "SELECT entry FROM registry_status_history WHERE package_id = %s AND version = %s ORDER BY id",
            (v.package_id, v.version),
        )
        v.status_history = [r["entry"] for r in cur.fetchall()]
        cur = conn.execute(
            "SELECT record FROM registry_test_reports WHERE package_id = %s AND version = %s ORDER BY id",
            (v.package_id, v.version),
        )
        v.test_reports = [r["record"] for r in cur.fetchall()]
        return v

    def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord:
        try:
            with self.tx() as conn:
                cur = conn.execute(
                    "SELECT package_id FROM registry_packages WHERE package_id = %s FOR UPDATE",
                    (version.package_id,),
                )
                if cur.fetchone() is None:
                    raise KeyError(version.package_id)
                cur = conn.execute(
                    "SELECT count(*) AS n, bool_or(version = %s) AS taken FROM registry_versions WHERE package_id = %s",
                    (version.version, version.package_id),
                )
                row = cur.fetchone()
                assert row is not None
                if row["taken"]:
                    raise VersionExists(version.version)
                if int(row["n"]) >= max_versions:
                    raise LimitReached(int(row["n"]))
                cur = conn.execute(
                    _INSERT_VERSION,
                    (
                        version.package_id,
                        version.version,
                        version.digest,
                        version.status,
                        version.test_status,
                        Json(version.manifest),
                        Jsonb(version.files),
                        version.size_bytes,
                        version.created_at,
                        version.created_by,
                        version.published_by,
                        version.ported_parent_version,
                        Jsonb(version.search_fields),
                    ),
                )
                inserted = cur.fetchone()
                assert inserted is not None
                for entry in version.status_history:
                    conn.execute(
                        "INSERT INTO registry_status_history (package_id, version, entry) VALUES (%s, %s, %s)",
                        (version.package_id, version.version, Jsonb(entry)),
                    )
                self._refresh(conn, version.package_id, version.created_at)
                return self._history(conn, _ver(inserted))
        except errors.UniqueViolation as exc:
            raise VersionExists(version.version) from exc

    def get_version(self, package_id: str, version: str) -> VersionRecord | None:
        with self.tx() as conn:
            cur = conn.execute(
                f"SELECT {_VER_COLS} FROM registry_versions WHERE package_id = %s AND version = %s",  # noqa: S608
                (package_id, version),
            )
            row = cur.fetchone()
            return self._history(conn, _ver(row)) if row else None

    def list_versions(
        self, package_id: str, status: str | None, before_seq: int | None, limit: int
    ) -> list[VersionRecord]:
        where = ["package_id = %s"]
        args: list[Any] = [package_id]
        if status:
            where.append("status = %s")
            args.append(status)
        if before_seq is not None:
            where.append("seq < %s")
            args.append(before_seq)
        with self.tx() as conn:
            cur = conn.execute(
                f"SELECT {_VER_COLS} FROM registry_versions WHERE {' AND '.join(where)} "  # noqa: S608
                "ORDER BY seq DESC LIMIT %s",
                (*args, limit),
            )
            rows = cur.fetchall()
            return [self._history(conn, _ver(r)) for r in rows]

    def version_numbers(self, package_id: str) -> list[tuple[str, str]]:
        with self.tx() as conn:
            cur = conn.execute(
                "SELECT version, status FROM registry_versions WHERE package_id = %s", (package_id,)
            )
            return [(r["version"], r["status"]) for r in cur.fetchall()]

    def count_versions(self, package_id: str) -> int:
        with self.tx() as conn:
            cur = conn.execute(
                "SELECT count(*) AS n FROM registry_versions WHERE package_id = %s", (package_id,)
            )
            row = cur.fetchone()
        return int(row["n"]) if row else 0

    def set_status(
        self, package_id: str, version: str, expected: str, entry: dict[str, Any]
    ) -> VersionRecord:
        with self.tx() as conn:
            conn.execute("SELECT 1 FROM registry_packages WHERE package_id = %s FOR UPDATE", (package_id,))
            cur = conn.execute(
                f"UPDATE registry_versions SET status = %s WHERE package_id = %s AND version = %s AND status = %s "  # noqa: S608
                f"RETURNING {_VER_COLS}",
                (entry["status"], package_id, version, expected),
            )
            row = cur.fetchone()
            if row is None:
                cur = conn.execute(
                    "SELECT status FROM registry_versions WHERE package_id = %s AND version = %s",
                    (package_id, version),
                )
                current = cur.fetchone()
                raise StatusMismatch(current["status"] if current else "missing")
            conn.execute(
                "INSERT INTO registry_status_history (package_id, version, entry) VALUES (%s, %s, %s)",
                (package_id, version, Jsonb(entry)),
            )
            self._refresh(conn, package_id, now())
            return self._history(conn, _ver(row))

    def add_test_report(
        self, package_id: str, version: str, record: dict[str, Any], test_status: str
    ) -> VersionRecord:
        with self.tx() as conn:
            cur = conn.execute(
                f"UPDATE registry_versions SET test_status = %s WHERE package_id = %s AND version = %s "  # noqa: S608
                f"RETURNING {_VER_COLS}",
                (test_status, package_id, version),
            )
            row = cur.fetchone()
            if row is None:
                raise KeyError(version)
            conn.execute(
                "INSERT INTO registry_test_reports (package_id, version, record) VALUES (%s, %s, %s)",
                (package_id, version, Jsonb(record)),
            )
            return self._history(conn, _ver(row))


class _SyncIdempotency:
    """``IdempotencyStore`` on ``registry_idempotency`` (``INSERT ... ON CONFLICT DO NOTHING``)."""

    def __init__(self, store: _SyncStore) -> None:
        self.store = store

    def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        expires = datetime.now(UTC) + timedelta(seconds=ttl_s)
        with self.store.tx() as conn:
            conn.execute("DELETE FROM registry_idempotency WHERE key = %s AND expires_at <= now()", (key,))
            cur = conn.execute(
                "INSERT INTO registry_idempotency (key, fingerprint, state, expires_at) VALUES (%s, %s, 'in_progress', %s) "
                "ON CONFLICT (key) DO NOTHING RETURNING key",
                (key, fingerprint, expires),
            )
            if cur.fetchone() is not None:
                return None
            cur = conn.execute("SELECT * FROM registry_idempotency WHERE key = %s", (key,))
            row = cur.fetchone()
        if row is None:  # expired and deleted concurrently: let the client retry
            return IdempotencyRecord(key, fingerprint, "in_progress", time.time() + ttl_s)
        response = None
        if row["response"] is not None:
            r = row["response"]
            response = StoredResponse(int(r["status_code"]), r["body"], dict(r.get("headers") or {}))
        return IdempotencyRecord(
            key, row["fingerprint"], row["state"], row["expires_at"].timestamp(), response
        )

    def complete(self, key: str, response: StoredResponse) -> None:
        doc = {"status_code": response.status_code, "body": response.body, "headers": dict(response.headers)}
        with self.store.tx() as conn:
            conn.execute(
                "UPDATE registry_idempotency SET state = 'completed', response = %s WHERE key = %s",
                (Jsonb(json.loads(json.dumps(doc, default=str))), key),
            )

    def release(self, key: str) -> None:
        with self.store.tx() as conn:
            conn.execute("DELETE FROM registry_idempotency WHERE key = %s AND state = 'in_progress'", (key,))


class _SyncJobs:
    """``JobStore`` on ``registry_jobs``; finished jobs older than ``job_retention_seconds`` are purged."""

    def __init__(self, store: _SyncStore, limits: JobLimits) -> None:
        self.store = store
        self.limits = limits

    def create(self, job: Job) -> None:
        with self.store.tx() as conn:
            conn.execute(
                "DELETE FROM registry_jobs WHERE finished_at IS NOT NULL AND finished_at < now() - make_interval(secs => %s)",
                (self.limits.job_retention_seconds,),
            )
            conn.execute(
                "INSERT INTO registry_jobs (job_id, doc, finished_at, updated_at) VALUES (%s, %s, %s, now())",
                (job.job_id, Jsonb(job.model_dump(mode="json")), job.finished_at),
            )

    def get(self, job_id: str) -> Job | None:
        with self.store.tx() as conn:
            cur = conn.execute("SELECT doc FROM registry_jobs WHERE job_id = %s", (job_id,))
            row = cur.fetchone()
        return Job.model_validate(row["doc"]) if row else None

    def save(self, job: Job) -> None:
        job = job.model_copy(update={"updated_at": datetime.now(UTC)})
        with self.store.tx() as conn:
            conn.execute(
                "UPDATE registry_jobs SET doc = %s, finished_at = %s, updated_at = now() WHERE job_id = %s",
                (Jsonb(job.model_dump(mode="json")), job.finished_at, job.job_id),
            )


class PostgresStore:
    """Async facade (``MetadataStore``) over the synchronous store: every call runs in a worker thread.

    psycopg's asyncio driver needs a selector event loop, which is not the default on Windows; the
    synchronous driver behaves the same on Windows and Linux.
    """

    name = "postgres"

    def __init__(self, dsn: str, schema: str, limits: DbLimits) -> None:
        self.sync = _SyncStore(dsn, schema, limits)

    async def open(self) -> None:
        await asyncio.to_thread(self.sync.open)

    async def close(self) -> None:
        await asyncio.to_thread(self.sync.close)

    async def check(self) -> bool:
        return await asyncio.to_thread(self.sync.check)

    async def create_package(self, pkg: PackageRecord) -> PackageRecord:
        return await asyncio.to_thread(self.sync.create_package, pkg)

    async def get_package(self, package_id: str) -> PackageRecord | None:
        return await asyncio.to_thread(self.sync.get_package, package_id)

    async def update_package(
        self, package_id: str, changes: dict[str, Any], expected_revision: int | None
    ) -> PackageRecord:
        return await asyncio.to_thread(self.sync.update_package, package_id, changes, expected_revision)

    async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
        return await asyncio.to_thread(self.sync.list_packages, flt, after, limit)

    async def count_forks(self, package_id: str) -> int:
        return await asyncio.to_thread(self.sync.count_forks, package_id)

    async def delete_package_if_empty(self, package_id: str) -> None:
        await asyncio.to_thread(self.sync.delete_package_if_empty, package_id)

    async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord:
        return await asyncio.to_thread(self.sync.insert_version, version, max_versions)

    async def get_version(self, package_id: str, version: str) -> VersionRecord | None:
        return await asyncio.to_thread(self.sync.get_version, package_id, version)

    async def list_versions(
        self, package_id: str, status: str | None, before_seq: int | None, limit: int
    ) -> list[VersionRecord]:
        return await asyncio.to_thread(self.sync.list_versions, package_id, status, before_seq, limit)

    async def version_numbers(self, package_id: str) -> list[tuple[str, str]]:
        return await asyncio.to_thread(self.sync.version_numbers, package_id)

    async def count_versions(self, package_id: str) -> int:
        return await asyncio.to_thread(self.sync.count_versions, package_id)

    async def set_status(
        self, package_id: str, version: str, expected: str, entry: dict[str, Any]
    ) -> VersionRecord:
        return await asyncio.to_thread(self.sync.set_status, package_id, version, expected, entry)

    async def add_test_report(
        self, package_id: str, version: str, record: dict[str, Any], test_status: str
    ) -> VersionRecord:
        return await asyncio.to_thread(self.sync.add_test_report, package_id, version, record, test_status)


class PostgresIdempotencyStore:
    """``IdempotencyStore`` on ``registry_idempotency`` (``INSERT ... ON CONFLICT DO NOTHING``)."""

    def __init__(self, store: PostgresStore) -> None:
        self.sync = _SyncIdempotency(store.sync)

    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        return await asyncio.to_thread(self.sync.begin, key, fingerprint, ttl_s)

    async def complete(self, key: str, response: StoredResponse) -> None:
        await asyncio.to_thread(self.sync.complete, key, response)

    async def release(self, key: str) -> None:
        await asyncio.to_thread(self.sync.release, key)


class PostgresJobStore:
    """``JobStore`` on ``registry_jobs``; finished jobs older than ``job_retention_seconds`` are purged."""

    def __init__(self, store: PostgresStore, limits: JobLimits) -> None:
        self.sync = _SyncJobs(store.sync, limits)

    async def create(self, job: Job) -> None:
        await asyncio.to_thread(self.sync.create, job)

    async def get(self, job_id: str) -> Job | None:
        return await asyncio.to_thread(self.sync.get, job_id)

    async def save(self, job: Job) -> None:
        await asyncio.to_thread(self.sync.save, job)
