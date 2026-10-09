"""``IdempotencyStore`` and ``JobStore`` in a service's own PostgreSQL database (R17).

Several instances of a service share these tables; each service keeps them in its **own** database/schema
(ADR-0009) - the code is shared, the data is not.

* :class:`PgIdempotencyStore` - ``Idempotency-Key`` records. A claim (``in_progress``) carries the claiming
  instance (``owner``), a per-claim ``token`` and a lease (``lease_until``) that :meth:`~PgIdempotencyStore.heartbeat`
  renews while the request still runs in this process. An expired key, or the claim of a stopped instance (lease
  over), is claimed again; ``complete``/``release`` are fenced by the token, so a request whose claim was taken
  over cannot overwrite the new claim.
* :class:`PgJobStore` - jobs of :class:`~jane_kit.jobs.JobRunner`: ``owner`` + ``lease_until`` renewed by
  :meth:`~PgJobStore.heartbeat` for the jobs this process runs; writes follow
  :func:`jane_kit.jobs.decide_save` under ``SELECT ... FOR UPDATE``; a job whose lease expired ends
  ``failed`` (retryable ``service_unavailable``) or ``cancelled`` when read (:meth:`~PgJobStore.get`), listed
  (:meth:`~PgJobStore.page`) or swept (:meth:`~PgJobStore.sweep`). Finished jobs are purged after
  ``job_retention_seconds``.

Existing tables are migrated in place (:meth:`ddl` - ``CREATE ... IF NOT EXISTS`` / ``ADD COLUMN IF NOT EXISTS``,
run by :func:`migrate` under an advisory lock, so instances may start together). Column layouts of earlier
services are kept (``layout="json"`` - one ``response`` column; ``doc_column`` - the job document column), so
their rows stay readable without a data copy.

psycopg is used synchronously (the async driver needs a selector event loop, not the Windows default); the async
methods run it in worker threads (:func:`asyncio.to_thread`).
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import uuid
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from datetime import UTC, datetime
from typing import Any, Literal

from psycopg import Connection, sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from jane_kit.errors import Conflict
from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_kit.jobs import (
    TERMINAL_STATUSES,
    Job,
    JobCancellation,
    JobPosition,
    JobStatus,
    decide_save,
    orphaned,
)

__all__ = [
    "JobPosition",
    "PgConnect",
    "PgDatabase",
    "PgIdempotencyStore",
    "PgJobStore",
    "migrate",
    "pool_tx",
]

log = logging.getLogger(__name__)

PgConnect = Callable[[], AbstractContextManager[Connection[Any]]]
"""Yields a connection inside one transaction (commit on exit, rollback on error)."""

_TERMINAL = sorted(s.value for s in TERMINAL_STATUSES)


def pool_tx(pool: Any) -> PgConnect:
    """:data:`PgConnect` over a ``psycopg_pool.ConnectionPool``."""

    @contextmanager
    def tx() -> Iterator[Connection[Any]]:
        with pool.connection() as conn, conn.transaction():
            yield conn

    return tx


def _table(schema: str | None, table: str) -> sql.Identifier:
    return sql.Identifier(schema, table) if schema else sql.Identifier(table)


def _index(schema: str | None, table: str, suffix: str) -> tuple[sql.Composable, sql.Identifier]:
    """``(qualified table, index name)``; an index lives in the table's schema."""
    return _table(schema, table), sql.Identifier(f"{table}_{suffix}")


def _plain(value: Any) -> Any:
    """JSON-native copy (a non-JSON value becomes its string, as before in the registry)."""
    return json.loads(json.dumps(value, default=str))


def migrate(
    tx: PgConnect, lock: str, *stores: PgIdempotencyStore | PgJobStore, schema: str | None = None
) -> None:
    """Create or upgrade the tables of ``stores`` in one transaction under ``pg_advisory_xact_lock(lock)``.

    Idempotent and safe when several instances start at once. ``schema`` is created first when given.
    """
    with tx() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (lock,))
        if schema:
            conn.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
        for store in stores:
            for statement in store.ddl():
                conn.execute(statement)


class PgDatabase:
    """A psycopg pool of the service's own database (``autocommit``; transactions via :meth:`tx`)."""

    def __init__(self, dsn: str, *, max_size: int, connect_timeout_ms: int, min_size: int = 0) -> None:
        from psycopg_pool import ConnectionPool

        self.connect_timeout_ms = connect_timeout_ms
        self.pool: Any = ConnectionPool(
            dsn,
            min_size=min_size,
            max_size=max_size,
            open=False,
            timeout=connect_timeout_ms / 1000,
            kwargs={"autocommit": True, "connect_timeout": max(1, connect_timeout_ms // 1000)},
        )
        self.tx: PgConnect = pool_tx(self.pool)

    def open(self) -> None:
        self.pool.open(True, self.connect_timeout_ms / 1000)

    def close(self) -> None:
        self.pool.close()

    def ping(self) -> bool:
        with self.pool.connection() as conn:
            conn.execute("SELECT 1")
        return True


# ---------------------------------------------------------------------------------------------- idempotency
class PgIdempotencyStore:
    """jane-kit ``IdempotencyStore`` on table ``table`` (in ``schema``, or on the connection's search path).

    ``layout``: ``"split"`` - response in ``status_code``/``body``/``headers`` columns; ``"json"`` - one
    ``response`` jsonb column (``{"status_code", "body", "headers"}``). ``in_progress_lease_s``: how long a claim
    survives without :meth:`heartbeat` (a stopped instance releases its keys after this).
    """

    def __init__(
        self,
        tx: PgConnect,
        *,
        owner: str,
        in_progress_lease_s: float,
        table: str = "idempotency",
        schema: str | None = None,
        layout: Literal["split", "json"] = "split",
        gc_batch: int = 500,
    ) -> None:
        if in_progress_lease_s <= 0:
            raise ValueError("in_progress_lease_s must be positive")
        self._tx = tx
        self.owner = owner
        self.lease_s = float(in_progress_lease_s)
        self.layout = layout
        self.gc_batch = gc_batch
        self._t = _table(schema, table)
        self._table, self._schema = table, schema
        self._claims: dict[str, str] = {}
        self._lock = threading.Lock()

    def ddl(self) -> list[sql.Composed]:
        t = self._t
        response = (
            sql.SQL("status_code integer, body jsonb, headers jsonb")
            if self.layout == "split"
            else sql.SQL("response jsonb")
        )
        out: list[sql.Composed] = [
            sql.SQL(
                "CREATE TABLE IF NOT EXISTS {} (key text PRIMARY KEY, fingerprint text NOT NULL, "
                "state text NOT NULL, expires_at timestamptz NOT NULL, lease_until timestamptz, owner text, "
                "token text, {})"
            ).format(t, response),
        ]
        columns = ["lease_until timestamptz", "owner text", "token text"]
        columns += (
            ["status_code integer", "body jsonb", "headers jsonb"]
            if self.layout == "split"
            else ["response jsonb"]
        )
        out += [sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS ").format(t) + sql.SQL(c) for c in columns]
        table, name = _index(self._schema, self._table, "expires_at")
        out.append(sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} (expires_at)").format(name, table))
        return out

    # -------------------------------------------------------------------------------- sync
    def _response(self, row: Mapping[str, Any]) -> StoredResponse | None:
        if self.layout == "split":
            if row.get("status_code") is None:
                return None
            return StoredResponse(int(row["status_code"]), row.get("body"), dict(row.get("headers") or {}))
        doc = row.get("response")
        if not isinstance(doc, Mapping) or doc.get("status_code") is None:
            return None
        return StoredResponse(int(doc["status_code"]), doc.get("body"), dict(doc.get("headers") or {}))

    def begin_sync(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        token = uuid.uuid4().hex
        t = self._t
        with self._tx() as conn, conn.cursor(row_factory=dict_row) as cur:
            # an expired key and the claim of a stopped instance (lease over) can be claimed again
            cur.execute(
                sql.SQL(
                    "DELETE FROM {} WHERE key = %s AND (expires_at <= clock_timestamp() OR "
                    "(state = 'in_progress' AND lease_until IS NOT NULL AND lease_until <= clock_timestamp()))"
                ).format(t),
                (key,),
            )
            cur.execute(
                sql.SQL(
                    "INSERT INTO {} (key, fingerprint, state, expires_at, lease_until, owner, token) "
                    "VALUES (%s, %s, 'in_progress', clock_timestamp() + make_interval(secs => %s), "
                    "clock_timestamp() + make_interval(secs => %s), %s, %s) "
                    "ON CONFLICT (key) DO NOTHING RETURNING key"
                ).format(t),
                (key, fingerprint, float(ttl_s), self.lease_s, self.owner, token),
            )
            if cur.fetchone() is not None:
                with self._lock:
                    self._claims[key] = token
                return None
            cur.execute(sql.SQL("SELECT * FROM {} WHERE key = %s").format(t), (key,))
            row = cur.fetchone()
        if row is None:  # removed between the statements: report it as running, the client retries
            return IdempotencyRecord(key, fingerprint, "in_progress", 0.0)
        return IdempotencyRecord(
            str(row["key"]),
            str(row["fingerprint"]),
            "completed" if row["state"] == "completed" else "in_progress",
            row["expires_at"].timestamp(),
            self._response(row) if row["state"] == "completed" else None,
        )

    def complete_sync(self, key: str, response: StoredResponse) -> None:
        with self._lock:
            token = self._claims.pop(key, None)
        if token is None:
            log.warning("idempotency key completed without a claim of this instance", extra={"key": key})
            return
        body, headers = _plain(response.body), _plain(dict(response.headers))
        if self.layout == "split":
            values: sql.Composable = sql.SQL("status_code = %s, body = %s, headers = %s")
            params: tuple[Any, ...] = (response.status_code, Jsonb(body), Jsonb(headers))
        else:
            values = sql.SQL("response = %s")
            params = (Jsonb({"status_code": response.status_code, "body": body, "headers": headers}),)
        with self._tx() as conn:
            done = conn.execute(
                sql.SQL(
                    "UPDATE {} SET state = 'completed', lease_until = NULL, {} "
                    "WHERE key = %s AND state = 'in_progress' AND token = %s"
                ).format(self._t, values),
                (*params, key, token),
            ).rowcount
        if not done:
            log.warning("idempotency claim was taken over before completion", extra={"key": key})

    def release_sync(self, key: str) -> None:
        with self._lock:
            token = self._claims.pop(key, None)
        if token is None:
            return
        with self._tx() as conn:
            conn.execute(
                sql.SQL("DELETE FROM {} WHERE key = %s AND state = 'in_progress' AND token = %s").format(
                    self._t
                ),
                (key, token),
            )

    def heartbeat_sync(self) -> int:
        """Renew the leases of the claims this process still holds (not those of a previous start)."""
        with self._lock:
            tokens = list(self._claims.values())
        if not tokens:
            return 0
        with self._tx() as conn:
            return int(
                conn.execute(
                    sql.SQL(
                        "UPDATE {} SET lease_until = clock_timestamp() + make_interval(secs => %s) "
                        "WHERE token = ANY(%s) AND state = 'in_progress' AND lease_until > clock_timestamp()"
                    ).format(self._t),
                    (self.lease_s, tokens),
                ).rowcount
                or 0
            )

    def gc_sync(self) -> int:
        """Delete up to ``gc_batch`` expired keys (any instance; locked rows are skipped)."""
        with self._tx() as conn:
            return int(
                conn.execute(
                    sql.SQL(
                        "DELETE FROM {t} WHERE key IN (SELECT key FROM {t} WHERE expires_at <= clock_timestamp() "
                        "LIMIT %s FOR UPDATE SKIP LOCKED)"
                    ).format(t=self._t),
                    (self.gc_batch,),
                ).rowcount
                or 0
            )

    # -------------------------------------------------------------------------------- jane-kit protocol
    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        return await asyncio.to_thread(self.begin_sync, key, fingerprint, ttl_s)

    async def complete(self, key: str, response: StoredResponse) -> None:
        await asyncio.to_thread(self.complete_sync, key, response)

    async def release(self, key: str) -> None:
        await asyncio.to_thread(self.release_sync, key)

    async def heartbeat(self) -> int:
        return await asyncio.to_thread(self.heartbeat_sync)

    async def gc(self) -> int:
        return await asyncio.to_thread(self.gc_sync)


# ---------------------------------------------------------------------------------------------- jobs
class PgJobStore:
    """jane-kit ``JobStore`` on table ``table`` (columns ``job_id``, ``doc_column`` jsonb, ``owner``,
    ``lease_until``, ``finished_at``, ``updated_at``); see the module docstring for the rules."""

    def __init__(
        self,
        tx: PgConnect,
        *,
        owner: str,
        lease_s: float,
        retention_s: float,
        table: str = "jobs",
        schema: str | None = None,
        doc_column: str = "doc",
    ) -> None:
        if lease_s <= 0:
            raise ValueError("lease_s must be positive")
        self._tx = tx
        self.owner = owner
        self.lease_s = float(lease_s)
        self.retention_s = float(retention_s)
        self._t = _table(schema, table)
        self._table, self._schema = table, schema
        self._doc = sql.Identifier(doc_column)
        self._owned: set[str] = set()
        self._lock = threading.Lock()

    def ddl(self) -> list[sql.Composed]:
        t, doc = self._t, self._doc
        out: list[sql.Composed] = [
            sql.SQL(
                "CREATE TABLE IF NOT EXISTS {} (job_id text PRIMARY KEY, {} jsonb NOT NULL, owner text, "
                "lease_until timestamptz, finished_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now())"
            ).format(t, doc),
        ]
        for column in (
            "owner text",
            "lease_until timestamptz",
            "finished_at timestamptz",
            "updated_at timestamptz NOT NULL DEFAULT now()",
        ):
            out.append(sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS ").format(t) + sql.SQL(column))
        # rows of an earlier layout: finished_at from the document, a lease for unfinished ones (one lease of grace)
        out.append(
            sql.SQL(
                "UPDATE {t} SET finished_at = ({doc}->>'finished_at')::timestamptz "
                "WHERE finished_at IS NULL AND {doc}->>'finished_at' IS NOT NULL"
            ).format(t=t, doc=doc)
        )
        out.append(
            sql.SQL(
                "UPDATE {} SET lease_until = clock_timestamp() + make_interval(secs => {}) "
                "WHERE finished_at IS NULL AND lease_until IS NULL"
            ).format(t, sql.Literal(self.lease_s))
        )
        for suffix, columns in (
            ("finished_at", "(finished_at)"),
            ("owner_open", "(owner) WHERE finished_at IS NULL"),
        ):
            table, name = _index(self._schema, self._table, suffix)
            out.append(sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} ").format(name, table) + sql.SQL(columns))
        return out

    # -------------------------------------------------------------------------------- sync
    def _dump(self, job: Job) -> Jsonb:
        return Jsonb(job.model_dump(mode="json"))

    def create_sync(self, job: Job) -> None:
        t, doc = self._t, self._doc
        with self._tx() as conn:
            conn.execute(
                sql.SQL(
                    "DELETE FROM {} WHERE finished_at IS NOT NULL "
                    "AND finished_at < clock_timestamp() - make_interval(secs => %s)"
                ).format(t),
                (self.retention_s,),
            )
            created = conn.execute(
                sql.SQL(
                    "INSERT INTO {} (job_id, {}, owner, lease_until, finished_at, updated_at) "
                    "VALUES (%s, %s, %s, clock_timestamp() + make_interval(secs => %s), %s, clock_timestamp()) "
                    "ON CONFLICT (job_id) DO NOTHING RETURNING job_id"
                ).format(t, doc),
                (job.job_id, self._dump(job), self.owner, self.lease_s, job.finished_at),
            ).fetchone()
        if created is None:
            raise Conflict(f"job {job.job_id} already exists")
        if job.status not in TERMINAL_STATUSES:
            with self._lock:
                self._owned.add(job.job_id)

    def _reap(self, conn: Connection[Any], job_id: str | None) -> list[Job]:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                sql.SQL(
                    "SELECT job_id, {} AS doc, owner FROM {} WHERE finished_at IS NULL "
                    "AND (lease_until IS NULL OR lease_until <= clock_timestamp()) "
                    "AND (%s::text IS NULL OR job_id = %s) FOR UPDATE SKIP LOCKED"
                ).format(self._doc, self._t),
                (job_id, job_id),
            )
            rows = cur.fetchall()
            reaped = []
            for row in rows:
                current = Job.model_validate(row["doc"])
                if current.status in TERMINAL_STATUSES:  # finished_at missing in an earlier layout
                    done = current
                else:
                    done = orphaned(current, row["owner"])
                    log.warning(
                        "job of a stopped instance ended",
                        extra={"job_id": done.job_id, "owner": row["owner"], "status": str(done.status)},
                    )
                cur.execute(
                    sql.SQL(
                        "UPDATE {} SET {} = %s, finished_at = %s, updated_at = clock_timestamp() WHERE job_id = %s"
                    ).format(self._t, self._doc),
                    (self._dump(done), done.finished_at or datetime.now(UTC), done.job_id),
                )
                reaped.append(done)
        return reaped

    def get_sync(self, job_id: str) -> Job | None:
        with self._tx() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                sql.SQL(
                    "SELECT {} AS doc, finished_at, (lease_until IS NULL OR lease_until <= clock_timestamp()) "
                    "AS expired FROM {} WHERE job_id = %s"
                ).format(self._doc, self._t),
                (job_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            job = Job.model_validate(row["doc"])
            if job.status in TERMINAL_STATUSES or row["finished_at"] is not None or not row["expired"]:
                return job
            reaped = self._reap(conn, job_id)
            if reaped:
                return reaped[0]
            cur.execute(
                sql.SQL("SELECT {} AS doc FROM {} WHERE job_id = %s").format(self._doc, self._t), (job_id,)
            )
            again = cur.fetchone()
        return Job.model_validate(again["doc"]) if again else None

    def save_sync(self, job: Job) -> None:
        if job.status in TERMINAL_STATUSES:
            # stop renewing first: if the write below fails, the lease runs out and the job is reaped
            with self._lock:
                self._owned.discard(job.job_id)
        with self._tx() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                sql.SQL(
                    "SELECT {} AS doc, owner, finished_at, COALESCE(lease_until > clock_timestamp(), false) AS live "
                    "FROM {} WHERE job_id = %s FOR UPDATE"
                ).format(self._doc, self._t),
                (job.job_id,),
            )
            row = cur.fetchone()
            if row is None or row["finished_at"] is not None:
                return
            saved = decide_save(
                Job.model_validate(row["doc"]), job, mine=row["owner"] == self.owner, live=bool(row["live"])
            )
            if saved is None:
                return
            cur.execute(
                sql.SQL(
                    "UPDATE {} SET {} = %s, finished_at = %s, updated_at = clock_timestamp() WHERE job_id = %s"
                ).format(self._t, self._doc),
                (
                    self._dump(saved),
                    saved.finished_at if saved.status in TERMINAL_STATUSES else None,
                    saved.job_id,
                ),
            )

    def heartbeat_sync(self) -> int:
        """Renew the leases of the jobs this process runs (never those of a previous start)."""
        with self._lock:
            owned = list(self._owned)
        if not owned:
            return 0
        with self._tx() as conn:
            return int(
                conn.execute(
                    sql.SQL(
                        "UPDATE {} SET lease_until = clock_timestamp() + make_interval(secs => %s) "
                        "WHERE job_id = ANY(%s) AND owner = %s AND finished_at IS NULL "
                        "AND lease_until > clock_timestamp()"
                    ).format(self._t),
                    (self.lease_s, owned, self.owner),
                ).rowcount
                or 0
            )

    def sweep_sync(self) -> int:
        """End every job whose lease expired (any owner); returns how many."""
        with self._tx() as conn:
            return len(self._reap(conn, None))

    def release_owned_sync(self, reason: str) -> int:
        """Graceful stop, after the runner cancelled this instance's jobs: unfinished jobs of this owner end
        ``cancelled`` and cancelled ones without a recorded cancellation get ``reason``."""
        with self._lock:
            self._owned.clear()
        changed = 0
        now_cancelled = JobStatus.CANCELLED.value
        with self._tx() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                sql.SQL(
                    "SELECT {doc} AS doc FROM {t} WHERE owner = %s AND (finished_at IS NULL OR "
                    "({doc}->>'status' = %s AND COALESCE(jsonb_typeof({doc}->'cancellation'), 'null') = 'null' "
                    "AND finished_at > clock_timestamp() - make_interval(secs => %s))) FOR UPDATE"
                ).format(doc=self._doc, t=self._t),
                (self.owner, now_cancelled, self.lease_s),
            )
            for row in cur.fetchall():
                job = Job.model_validate(row["doc"])
                stamp = datetime.now(UTC)
                job = job.model_copy(
                    update={
                        "status": JobStatus.CANCELLED,
                        "finished_at": job.finished_at or stamp,
                        "updated_at": stamp,
                        "cancellation": job.cancellation
                        or JobCancellation(requested_at=stamp, requested_by=self.owner, reason=reason),
                    }
                )
                cur.execute(
                    sql.SQL(
                        "UPDATE {} SET {} = %s, finished_at = %s, updated_at = clock_timestamp() WHERE job_id = %s"
                    ).format(self._t, self._doc),
                    (self._dump(job), job.finished_at, job.job_id),
                )
                changed += 1
        return changed

    def page_sync(
        self,
        kind: str,
        *,
        labels: Mapping[str, str],
        statuses: Iterable[str] | None,
        after: JobPosition | None,
        limit: int,
    ) -> list[Job]:
        """Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly after
        ``after``. Jobs of stopped instances are ended first, so a status filter sees them as ``get`` does."""
        doc = self._doc
        with self._tx() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    sql.SQL(
                        "SELECT job_id FROM {} WHERE finished_at IS NULL "
                        "AND (lease_until IS NULL OR lease_until <= clock_timestamp()) AND {}->>'kind' = %s"
                    ).format(self._t, doc),
                    (kind,),
                )
                stale = [str(r["job_id"]) for r in cur.fetchall()]
            for job_id in stale:
                self._reap(conn, job_id)
        where: list[sql.Composable] = [
            sql.SQL("{}->>'kind' = %s").format(doc),
            sql.SQL("COALESCE({}->'labels', '{{}}'::jsonb) @> %s").format(doc),
        ]
        params: list[Any] = [kind, Jsonb(dict(labels))]
        wanted = sorted(set(statuses or ()))
        if wanted:
            where.append(sql.SQL("{}->>'status' = ANY(%s)").format(doc))
            params.append(wanted)
        if after is not None:
            where.append(
                sql.SQL(
                    "(({}->>'created_at')::timestamptz, job_id COLLATE \"C\") < (%s::timestamptz, %s)"
                ).format(doc)
            )
            params += [after[0], after[1]]
        query = sql.SQL(
            "SELECT {doc} AS doc FROM {t} WHERE {where} "
            "ORDER BY ({doc}->>'created_at')::timestamptz DESC, job_id COLLATE \"C\" DESC LIMIT %s"
        ).format(doc=doc, t=self._t, where=sql.SQL(" AND ").join(where))
        with self._tx() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (*params, limit))
            return [Job.model_validate(r["doc"]) for r in cur.fetchall()]

    # -------------------------------------------------------------------------------- jane-kit protocol
    async def create(self, job: Job) -> None:
        await asyncio.to_thread(self.create_sync, job)

    async def get(self, job_id: str) -> Job | None:
        return await asyncio.to_thread(self.get_sync, job_id)

    async def save(self, job: Job) -> None:
        await asyncio.to_thread(self.save_sync, job)

    async def heartbeat(self) -> int:
        return await asyncio.to_thread(self.heartbeat_sync)

    async def sweep(self) -> int:
        return await asyncio.to_thread(self.sweep_sync)

    async def release_owned(self, reason: str) -> int:
        return await asyncio.to_thread(self.release_owned_sync, reason)

    async def page(
        self,
        kind: str,
        *,
        labels: Mapping[str, str],
        statuses: Iterable[str] | None,
        after: JobPosition | None,
        limit: int,
    ) -> list[Job]:
        return await asyncio.to_thread(
            lambda: self.page_sync(kind, labels=labels, statuses=statuses, after=after, limit=limit)
        )
