"""State of the assistant shared by instances: onboarding sessions, jobs and idempotency keys.

* ``InMemoryState`` - default for a single standalone instance and tests (lost on restart);
* ``PostgresState`` - the service's own database/schema (``JANE_ASSISTANT_STATE_DSN``,
  ``JANE_ASSISTANT_STATE_SCHEMA``, default ``jane_assistant``; data-ownership.md): ``SessionStore`` and jane-kit's
  shared ``PgJobStore`` / ``PgIdempotencyStore`` (R17), so any instance reads and continues a session or job
  created by another one and replays an ``Idempotency-Key`` response.

Concurrency and failures:

* session state transitions of the API use an optimistic version (``UPDATE ... WHERE version = %s``):
  two instances cannot both select a candidate or accept a proposal;
* a job belongs to the instance that runs it (``owner``) and holds a lease renewed by that instance's
  heartbeat (``limits.state.heartbeat_interval_ms``). A job whose lease expired (the instance was killed)
  is marked ``failed`` with the reason by whichever instance reads or lists it next; a terminal job is never
  overwritten, and only the owner with a live lease writes progress or the result (fencing). On a graceful
  shutdown the instance cancels its jobs and records the reason.

psycopg is used synchronously in worker threads (``asyncio.to_thread``): the async driver does not work
with the Windows Proactor event loop, and the service runs on Windows and Linux.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any, Protocol

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from jane_kit.idempotency import IdempotencyStore, InMemoryIdempotencyStore
from jane_kit.jobs import InMemoryJobStore, Job, JobStore
from jane_kit.stores.postgres import PgDatabase, PgIdempotencyStore, PgJobStore, migrate

from .listing import Position
from .onboarding import InMemorySessionStore, Session, SessionStore
from .settings import ServiceLimits

__all__ = ["InMemoryState", "PostgresState", "ServiceState"]

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


class InMemoryState:
    name = "memory"

    def __init__(self, limits: ServiceLimits) -> None:
        self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(limits.idempotency)
        jobs = InMemoryJobStore(limits.jobs)  # lists its own jobs (``page``), kept for the store's retention
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


_SESSIONS_DDL = [
    """CREATE TABLE IF NOT EXISTS {schema}.sessions (
        session_id text PRIMARY KEY,
        doc jsonb NOT NULL,
        version integer NOT NULL,
        updated_at timestamptz NOT NULL DEFAULT now()
    )""",
    "CREATE INDEX IF NOT EXISTS sessions_updated_at ON {schema}.sessions (updated_at)",
]


class PostgresState:
    """Jobs and ``Idempotency-Key`` records in jane-kit's shared stores (R17), onboarding sessions here.

    The tables ``idempotency`` and ``jobs`` keep their layout; the kit migration adds the claim columns in place.
    """

    name = "postgresql"

    def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None:
        self.schema_name = schema
        self.schema = sql.Identifier(schema)
        self.limits = limits
        self.instance_id = instance_id
        st = limits.state
        self.db = PgDatabase(dsn, max_size=st.pool_max_size, connect_timeout_ms=st.connect_timeout_ms)
        self.pool = self.db.pool
        self._idem = PgIdempotencyStore(
            self.db.tx, owner=instance_id, in_progress_lease_s=st.in_progress_lease_ms / 1000, schema=schema
        )
        self._jobs = PgJobStore(
            self.db.tx,
            owner=instance_id,
            lease_s=st.job_lease_ms / 1000,
            retention_s=limits.jobs.job_retention_seconds,
            schema=schema,
        )
        self.idempotency: IdempotencyStore = self._idem
        self.jobs: JobStore = self._jobs
        self.job_list: JobLister = self._jobs
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
        migrate(
            self.db.tx, f"jane-assistant-{self.schema_name}", self._idem, self._jobs, schema=self.schema_name
        )
        with self.db.tx() as conn:
            for stmt in _SESSIONS_DDL:
                conn.execute(self.q(stmt))

    async def open(self) -> None:
        await asyncio.to_thread(self.db.open)
        await asyncio.to_thread(self._migrate)

    async def close(self) -> None:
        await asyncio.to_thread(self.db.close)

    async def ping(self) -> bool:
        return await asyncio.to_thread(self.db.ping)

    async def heartbeat(self) -> None:
        """Renew this process's job leases and idempotency claims; drop expired keys."""
        await self._jobs.heartbeat()
        await self._idem.heartbeat()
        await self._idem.gc()

    async def release_owned(self, reason: str) -> None:
        """After the runner cancelled this instance's jobs: record why, close anything left open."""
        await self._jobs.release_owned(reason)


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
