"""State of the assistant shared by instances: onboarding sessions, jobs and idempotency keys.

* ``InMemoryState`` - default for a single standalone instance and tests (lost on restart);
* ``PostgresState`` - the service's own database/schema (``JANE_ASSISTANT_STATE_DSN``,
  ``JANE_ASSISTANT_STATE_SCHEMA``, default ``jane_assistant``; data-ownership.md): implements
  ``SessionStore`` and jane-kit ``JobStore`` / ``IdempotencyStore``, so any instance reads and continues a
  session or job created by another one and replays an ``Idempotency-Key`` response.

Concurrency and failures:

* session state transitions of the API use an optimistic version (``UPDATE ... WHERE version = %s``):
  two instances cannot both select a candidate or accept a proposal;
* a job belongs to the instance that runs it (``owner``) and holds a lease renewed by that instance's
  heartbeat (``limits.state.heartbeat_interval_ms``). A job whose lease expired (the instance was killed)
  is marked ``failed`` with the reason by whichever instance reads it next; a terminal job is never
  overwritten. On a graceful shutdown the instance cancels its jobs and records the reason.

psycopg is used synchronously in worker threads (``asyncio.to_thread``): the async driver does not work
with the Windows Proactor event loop, and the service runs on Windows and Linux.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Protocol

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from jane_kit.errors import JaneError
from jane_kit.idempotency import IdempotencyRecord, IdempotencyStore, InMemoryIdempotencyStore, StoredResponse
from jane_kit.jobs import InMemoryJobStore, Job, JobCancellation, JobStatus, JobStore

from .listing import Position
from .onboarding import InMemorySessionStore, Session, SessionStore
from .settings import ServiceLimits

__all__ = ["InMemoryState", "PostgresState", "ServiceState"]

TERMINAL = ("succeeded", "failed", "cancelled")


class JobLister(Protocol):
    async def page(
        self,
        kind: str,
        *,
        labels: Mapping[str, str],
        statuses: frozenset[str] | None,
        after: Position | None,
        limit: int,
    ) -> list[Job]:
        """Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly
        after the ``after`` position; a job whose owner stopped is reported ``failed`` (as by ``get``)."""
        ...


def job_position(job: Job) -> Position:
    return (job.created_at, job.job_id)


class ServiceState(Protocol):
    name: str
    idempotency: IdempotencyStore
    jobs: JobStore
    job_list: JobLister
    sessions: SessionStore

    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def ping(self) -> bool: ...
    async def heartbeat(self) -> None: ...
    async def release_owned(self, reason: str) -> None: ...


class _ListedMemoryJobs(InMemoryJobStore):
    """jane-kit's in-memory job store that can list its jobs. It lists the store's own dictionary, so it holds
    nothing beyond the store: finished jobs leave with the store's retention (``jobs.job_retention_seconds``)."""

    async def page(
        self,
        kind: str,
        *,
        labels: Mapping[str, str],
        statuses: frozenset[str] | None,
        after: Position | None,
        limit: int,
    ) -> list[Job]:
        self._gc()  # the store's retention, as on create
        wanted = [
            job.model_copy(deep=True)
            for job in self._jobs.values()
            if job.kind == kind
            and all((job.labels or {}).get(k) == v for k, v in labels.items())
            and (not statuses or str(job.status) in statuses)
            and (after is None or job_position(job) < after)
        ]
        wanted.sort(key=job_position, reverse=True)
        return wanted[:limit]


class InMemoryState:
    name = "memory"

    def __init__(self, limits: ServiceLimits) -> None:
        self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(limits.idempotency)
        jobs = _ListedMemoryJobs(limits.jobs)
        self.jobs: JobStore = jobs
        self.job_list: JobLister = jobs
        self.sessions: SessionStore = InMemorySessionStore()

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def ping(self) -> bool:
        return True

    async def heartbeat(self) -> None:
        return None

    async def release_owned(self, reason: str) -> None:
        return None  # the state disappears with the process


_DDL = [
    "CREATE SCHEMA IF NOT EXISTS {schema}",
    """CREATE TABLE IF NOT EXISTS {schema}.idempotency (
        key text PRIMARY KEY,
        fingerprint text NOT NULL,
        state text NOT NULL,
        expires_at timestamptz NOT NULL,
        lease_until timestamptz,
        status_code integer,
        body jsonb,
        headers jsonb
    )""",
    """CREATE TABLE IF NOT EXISTS {schema}.jobs (
        job_id text PRIMARY KEY,
        doc jsonb NOT NULL,
        owner text NOT NULL,
        lease_until timestamptz NOT NULL,
        finished_at timestamptz,
        updated_at timestamptz NOT NULL DEFAULT now()
    )""",
    """CREATE TABLE IF NOT EXISTS {schema}.sessions (
        session_id text PRIMARY KEY,
        doc jsonb NOT NULL,
        version integer NOT NULL,
        updated_at timestamptz NOT NULL DEFAULT now()
    )""",
    "CREATE INDEX IF NOT EXISTS jobs_owner_open ON {schema}.jobs (owner) WHERE finished_at IS NULL",
    "CREATE INDEX IF NOT EXISTS jobs_finished_at ON {schema}.jobs (finished_at)",
    "CREATE INDEX IF NOT EXISTS sessions_updated_at ON {schema}.sessions (updated_at)",
]


class PostgresState:
    name = "postgresql"

    def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None:
        self.schema = sql.Identifier(schema)
        self.limits = limits
        self.instance_id = instance_id
        st = limits.state
        self.pool = ConnectionPool(
            dsn,
            min_size=0,
            max_size=st.pool_max_size,
            open=False,
            timeout=st.connect_timeout_ms / 1000,
            kwargs={"autocommit": True, "connect_timeout": max(1, st.connect_timeout_ms // 1000)},
        )
        self.idempotency: IdempotencyStore = _PgIdempotency(self)
        jobs = _PgJobs(self)
        self.jobs: JobStore = jobs
        self.job_list: JobLister = jobs
        self.sessions: SessionStore = _PgSessions(self)

    def q(self, text: str) -> sql.Composed:
        return sql.SQL(text).format(schema=self.schema)

    def run(self, text: str, params: tuple[Any, ...] = (), fetch: bool = False) -> list[dict[str, Any]]:
        with self.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(self.q(text), params)
            return list(cur.fetchall()) if fetch else []

    def rowcount(self, text: str, params: tuple[Any, ...]) -> int:
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute(self.q(text), params)
            return int(cur.rowcount)

    def _migrate(self) -> None:
        with self.pool.connection() as conn:
            for stmt in _DDL:
                conn.execute(self.q(stmt))

    async def open(self) -> None:
        await asyncio.to_thread(self.pool.open, True, self.limits.state.connect_timeout_ms / 1000)
        await asyncio.to_thread(self._migrate)

    async def close(self) -> None:
        await asyncio.to_thread(self.pool.close)

    async def ping(self) -> bool:
        await asyncio.to_thread(self.run, "SELECT 1")
        return True

    async def heartbeat(self) -> None:
        await asyncio.to_thread(
            self.run,
            "UPDATE {schema}.jobs SET lease_until = now() + make_interval(secs => %s) "
            "WHERE owner = %s AND finished_at IS NULL",
            (self.limits.state.job_lease_ms / 1000, self.instance_id),
        )

    async def release_owned(self, reason: str) -> None:
        """After the runner cancelled this instance's jobs: record why, close anything left open."""
        rows = await asyncio.to_thread(
            self.run,
            "SELECT doc FROM {schema}.jobs WHERE owner = %s AND (finished_at IS NULL OR "
            "(doc->>'status' = 'cancelled' AND COALESCE(jsonb_typeof(doc->'cancellation'), 'null') = 'null' "
            "AND finished_at > now() - make_interval(secs => %s)))",
            (self.instance_id, self.limits.state.job_lease_ms / 1000),
            True,
        )
        now = datetime.now(UTC)
        for row in rows:
            job = Job.model_validate(row["doc"])
            job = job.model_copy(
                update={
                    "status": JobStatus.CANCELLED,
                    "finished_at": job.finished_at or now,
                    "cancellation": job.cancellation
                    or JobCancellation(requested_at=now, requested_by=self.instance_id, reason=reason),
                }
            )
            await asyncio.to_thread(
                self.run,
                "UPDATE {schema}.jobs SET doc = %s, finished_at = %s, updated_at = now() WHERE job_id = %s",
                (Jsonb(job.model_dump(mode="json")), job.finished_at, job.job_id),
            )


def _epoch(value: datetime | None) -> float:
    return value.timestamp() if value else 0.0


class _PgIdempotency:
    def __init__(self, db: PostgresState) -> None:
        self.db = db

    def _begin(self, key: str, fp: str, ttl_s: float) -> IdempotencyRecord | None:
        lease_s = self.db.limits.state.in_progress_lease_ms / 1000
        with self.db.pool.connection() as conn, conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
            # Expired keys and in-progress claims of a crashed instance (lease over) can be claimed again.
            cur.execute(
                self.db.q(
                    "DELETE FROM {schema}.idempotency WHERE key = %s AND (expires_at <= now() "
                    "OR (state = 'in_progress' AND lease_until <= now()))"
                ),
                (key,),
            )
            cur.execute(
                self.db.q(
                    "INSERT INTO {schema}.idempotency (key, fingerprint, state, expires_at, lease_until) "
                    "VALUES (%s, %s, 'in_progress', now() + make_interval(secs => %s), "
                    "now() + make_interval(secs => %s)) ON CONFLICT (key) DO NOTHING RETURNING key"
                ),
                (key, fp, ttl_s, lease_s),
            )
            if cur.fetchone() is not None:
                return None
            cur.execute(self.db.q("SELECT * FROM {schema}.idempotency WHERE key = %s"), (key,))
            row = cur.fetchone()
        if row is None:  # pragma: no cover - deleted between statements
            return None
        response = None
        if row["state"] == "completed":
            response = StoredResponse(row["status_code"], row["body"], dict(row["headers"] or {}))
        return IdempotencyRecord(
            row["key"], row["fingerprint"], row["state"], _epoch(row["expires_at"]), response
        )

    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        return await asyncio.to_thread(self._begin, key, fingerprint, ttl_s)

    async def complete(self, key: str, response: StoredResponse) -> None:
        await asyncio.to_thread(
            self.db.run,
            "UPDATE {schema}.idempotency SET state = 'completed', lease_until = NULL, status_code = %s, "
            "body = %s, headers = %s WHERE key = %s",
            (response.status_code, Jsonb(response.body), Jsonb(dict(response.headers)), key),
        )

    async def release(self, key: str) -> None:
        await asyncio.to_thread(
            self.db.run, "DELETE FROM {schema}.idempotency WHERE key = %s AND state = 'in_progress'", (key,)
        )


class _PgJobs:
    def __init__(self, db: PostgresState) -> None:
        self.db = db

    async def create(self, job: Job) -> None:
        await asyncio.to_thread(
            self.db.run,
            "DELETE FROM {schema}.jobs WHERE finished_at < now() - make_interval(secs => %s)",
            (self.db.limits.jobs.job_retention_seconds,),
        )
        await asyncio.to_thread(
            self.db.run,
            "INSERT INTO {schema}.jobs (job_id, doc, owner, lease_until, finished_at) "
            "VALUES (%s, %s, %s, now() + make_interval(secs => %s), %s)",
            (
                job.job_id,
                Jsonb(job.model_dump(mode="json")),
                self.db.instance_id,
                self.db.limits.state.job_lease_ms / 1000,
                job.finished_at,
            ),
        )

    async def get(self, job_id: str) -> Job | None:
        rows = await asyncio.to_thread(
            self.db.run,
            "SELECT doc, owner, lease_until < now() AS expired FROM {schema}.jobs WHERE job_id = %s",
            (job_id,),
            True,
        )
        if not rows:
            return None
        job = Job.model_validate(rows[0]["doc"])
        if job.status in TERMINAL or not rows[0]["expired"]:
            return job
        # The owner stopped renewing its lease (killed or hung): the job cannot finish any more.
        failed = job.model_copy(
            update={
                "status": JobStatus.FAILED,
                "finished_at": datetime.now(UTC),
                "error": JaneError(
                    f"instance {rows[0]['owner']} stopped while the job was {job.status} "
                    f"(no heartbeat within limits.state.job_lease_ms)",
                    code="service_unavailable",
                    retryable=True,
                ).to_problem(),
            }
        )
        changed = await asyncio.to_thread(
            self.db.rowcount,
            "UPDATE {schema}.jobs SET doc = %s, finished_at = %s, updated_at = now() "
            "WHERE job_id = %s AND finished_at IS NULL AND lease_until < now()",
            (Jsonb(failed.model_dump(mode="json")), failed.finished_at, job_id),
        )
        return failed if changed else await self.get(job_id)

    async def save(self, job: Job) -> None:
        job = job.model_copy(update={"updated_at": datetime.now(UTC)})
        # A terminal job never changes again (e.g. marked failed after its owner's lease expired).
        await asyncio.to_thread(
            self.db.run,
            "INSERT INTO {schema}.jobs (job_id, doc, owner, lease_until, finished_at) "
            "VALUES (%s, %s, %s, now() + make_interval(secs => %s), %s) ON CONFLICT (job_id) "
            "DO UPDATE SET doc = EXCLUDED.doc, finished_at = EXCLUDED.finished_at, updated_at = now() "
            "WHERE {schema}.jobs.doc->>'status' NOT IN ('succeeded', 'failed', 'cancelled')",
            (
                job.job_id,
                Jsonb(job.model_dump(mode="json")),
                self.db.instance_id,
                self.db.limits.state.job_lease_ms / 1000,
                job.finished_at,
            ),
        )

    async def page(
        self,
        kind: str,
        *,
        labels: Mapping[str, str],
        statuses: frozenset[str] | None,
        after: Position | None,
        limit: int,
    ) -> list[Job]:
        # Jobs of stopped instances first become `failed` (as `get` reports them), so a status filter sees them.
        stale = await asyncio.to_thread(
            self.db.run,
            "SELECT job_id FROM {schema}.jobs WHERE finished_at IS NULL AND lease_until < now() "
            "AND doc->>'kind' = %s",
            (kind,),
            True,
        )
        for row in stale:
            await self.get(str(row["job_id"]))
        where = ["doc->>'kind' = %s", "COALESCE(doc->'labels', '{{}}'::jsonb) @> %s"]
        params: list[Any] = [kind, Jsonb(dict(labels))]
        if statuses:
            where.append("doc->>'status' = ANY(%s)")
            params.append(sorted(statuses))
        if after is not None:
            where.append("((doc->>'created_at')::timestamptz, job_id COLLATE \"C\") < (%s, %s)")
            params += [after[0], after[1]]
        rows = await asyncio.to_thread(
            self.db.run,
            f"SELECT doc FROM {{schema}}.jobs WHERE {' AND '.join(where)} "  # noqa: S608 - fixed clauses only
            "ORDER BY (doc->>'created_at')::timestamptz DESC, job_id COLLATE \"C\" DESC LIMIT %s",
            (*params, limit),
            True,
        )
        return [Job.model_validate(r["doc"]) for r in rows]


class _PgSessions:
    def __init__(self, db: PostgresState) -> None:
        self.db = db

    async def get(self, session_id: str) -> Session | None:
        rows = await asyncio.to_thread(
            self.db.run,
            "SELECT doc, version FROM {schema}.sessions WHERE session_id = %s",
            (session_id,),
            True,
        )
        return Session.from_doc(dict(rows[0]["doc"]), int(rows[0]["version"])) if rows else None

    async def save(self, session: Session) -> None:
        rows = await asyncio.to_thread(
            self.db.run,
            "INSERT INTO {schema}.sessions (session_id, doc, version) VALUES (%s, %s, 1) "
            "ON CONFLICT (session_id) DO UPDATE SET doc = EXCLUDED.doc, "
            "version = {schema}.sessions.version + 1, updated_at = now() RETURNING version",
            (session.session_id, Jsonb(session.to_doc())),
            True,
        )
        session.version = int(rows[0]["version"])

    async def page(
        self, *, statuses: frozenset[str] | None, after: Position | None, limit: int
    ) -> list[Session]:
        where = ["TRUE"]
        params: list[Any] = []
        if statuses:
            where.append("doc->>'status' = ANY(%s)")
            params.append(sorted(statuses))
        if after is not None:
            where.append(
                "((doc->>'created_at')::timestamptz, session_id COLLATE \"C\") < (%s::timestamptz, %s)"
            )
            params += [after[0], after[1]]
        rows = await asyncio.to_thread(
            self.db.run,
            f"SELECT doc, version FROM {{schema}}.sessions WHERE {' AND '.join(where)} "  # noqa: S608 - fixed clauses
            "ORDER BY (doc->>'created_at')::timestamptz DESC, session_id COLLATE \"C\" DESC LIMIT %s",
            (*params, limit),
            True,
        )
        return [Session.from_doc(dict(r["doc"]), int(r["version"])) for r in rows]

    async def save_if(self, session: Session, expected: int) -> bool:
        if expected == 0:
            await asyncio.to_thread(
                self.db.run,
                "DELETE FROM {schema}.sessions WHERE updated_at < now() - make_interval(secs => %s)",
                (self.db.limits.state.session_retention_seconds,),
            )
            rows = await asyncio.to_thread(
                self.db.run,
                "INSERT INTO {schema}.sessions (session_id, doc, version) VALUES (%s, %s, 1) "
                "ON CONFLICT (session_id) DO NOTHING RETURNING version",
                (session.session_id, Jsonb(session.to_doc())),
                True,
            )
        else:
            rows = await asyncio.to_thread(
                self.db.run,
                "UPDATE {schema}.sessions SET doc = %s, version = version + 1, updated_at = now() "
                "WHERE session_id = %s AND version = %s RETURNING version",
                (Jsonb(session.to_doc()), session.session_id, expected),
                True,
            )
        if not rows:
            return False
        session.version = int(rows[0]["version"])
        return True
