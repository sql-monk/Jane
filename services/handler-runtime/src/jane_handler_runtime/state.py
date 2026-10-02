"""Service state shared by instances: idempotency keys, jobs and invocation results.

* ``InMemoryState`` - default for a single standalone instance and the CLI (lost on restart);
* ``PostgresState`` - own database/schema ``jane_handler_runtime`` (``JANE_HANDLER_RUNTIME_STATE_DSN``,
  data-ownership.md): implements jane-kit ``IdempotencyStore`` and ``JobStore`` and stores results for
  ``GET /v1/invocations/{id}``, so any instance answers a redelivery with the stored result
  (``duplicate: true``) and reads jobs/invocations created by another instance.

psycopg is used synchronously in worker threads (``asyncio.to_thread``): the async driver does not work with
the Windows Proactor event loop, and the service must run on Windows and Linux.
"""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any, Protocol

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from jane_kit.errors import JaneError
from jane_kit.idempotency import IdempotencyRecord, IdempotencyStore, InMemoryIdempotencyStore, StoredResponse
from jane_kit.jobs import TERMINAL_STATUSES, InMemoryJobStore, Job, JobStatus, JobStore

from .settings import ServiceLimits

__all__ = ["InMemoryState", "PostgresState", "ResultStore", "ServiceState"]


class ResultStore(Protocol):
    async def put(self, result: dict[str, Any]) -> None: ...
    async def get(self, invocation_id: str) -> dict[str, Any] | None: ...


class ServiceState(Protocol):
    name: str
    idempotency: IdempotencyStore
    jobs: JobStore
    results: ResultStore

    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def ping(self) -> bool: ...
    async def heartbeat(self) -> None: ...


class InMemoryResultStore:
    def __init__(self, max_entries: int) -> None:
        self.max_entries = max_entries
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()

    async def put(self, result: dict[str, Any]) -> None:
        self._items[result["invocation_id"]] = result
        self._items.move_to_end(result["invocation_id"])
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    async def get(self, invocation_id: str) -> dict[str, Any] | None:
        return self._items.get(invocation_id)


class InMemoryState:
    name = "memory"

    def __init__(self, limits: ServiceLimits) -> None:
        self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(limits.idempotency)
        self.jobs: JobStore = InMemoryJobStore(limits.jobs)
        self.results: ResultStore = InMemoryResultStore(limits.packages.max_stored_results)

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def ping(self) -> bool:
        return True

    async def heartbeat(self) -> None:
        return None


# ---------------------------------------------------------------------------------------------- PostgreSQL

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
        owner text,
        lease_until timestamptz,
        finished_at timestamptz,
        updated_at timestamptz NOT NULL DEFAULT now()
    )""",
    "ALTER TABLE {schema}.jobs ADD COLUMN IF NOT EXISTS owner text",
    "ALTER TABLE {schema}.jobs ADD COLUMN IF NOT EXISTS lease_until timestamptz",
    """CREATE TABLE IF NOT EXISTS {schema}.results (
        invocation_id text PRIMARY KEY,
        doc jsonb NOT NULL,
        created_at timestamptz NOT NULL DEFAULT now()
    )""",
    "CREATE INDEX IF NOT EXISTS results_created_at ON {schema}.results (created_at)",
    "CREATE INDEX IF NOT EXISTS jobs_finished_at ON {schema}.jobs (finished_at)",
]


class PostgresState:
    name = "postgresql"

    def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None:
        self.schema = sql.Identifier(schema)
        self.limits = limits
        self.instance_id = instance_id
        state = limits.state
        self.pool = ConnectionPool(
            dsn,
            min_size=0,
            max_size=state.pool_max_size,
            open=False,
            timeout=state.connect_timeout_ms / 1000,
            kwargs={"autocommit": True, "connect_timeout": max(1, state.connect_timeout_ms // 1000)},
        )
        self.idempotency: IdempotencyStore = _PgIdempotency(self)
        self.jobs: JobStore = _PgJobs(self)
        self.results: ResultStore = _PgResults(self)

    def q(self, text: str) -> sql.Composed:
        return sql.SQL(text).format(schema=self.schema)

    def run(self, text: str, params: tuple[Any, ...] = (), fetch: bool = False) -> list[dict[str, Any]]:
        with self.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(self.q(text), params)
            return list(cur.fetchall()) if fetch else []

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
            "UPDATE {schema}.jobs SET lease_until = clock_timestamp() + make_interval(secs => %s) "
            "WHERE owner = %s AND finished_at IS NULL AND lease_until > clock_timestamp()",
            (self.limits.state.job_lease_ms / 1000, self.instance_id),
        )

    def rowcount(self, text: str, params: tuple[Any, ...]) -> int:
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.execute(self.q(text), params)
            return int(cur.rowcount)


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
        retention = self.db.limits.jobs.job_retention_seconds
        await asyncio.to_thread(
            self.db.run,
            "DELETE FROM {schema}.jobs WHERE finished_at < now() - make_interval(secs => %s)",
            (retention,),
        )
        await asyncio.to_thread(
            self.db.run,
            "INSERT INTO {schema}.jobs (job_id, doc, owner, lease_until, finished_at) "
            "VALUES (%s, %s, %s, clock_timestamp() + make_interval(secs => %s), %s)",
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
            "SELECT doc, owner, (lease_until IS NULL OR lease_until <= clock_timestamp()) AS expired "
            "FROM {schema}.jobs WHERE job_id = %s",
            (job_id,),
            True,
        )
        if not rows:
            return None
        job = Job.model_validate(rows[0]["doc"])
        if job.status in TERMINAL_STATUSES or not rows[0]["expired"]:
            return job
        failed = job.model_copy(
            update={
                "status": JobStatus.FAILED,
                "finished_at": datetime.now(UTC),
                "error": JaneError(
                    f"instance {rows[0]['owner']} stopped while job was {job.status}",
                    code="service_unavailable",
                    retryable=True,
                ).to_problem(),
            }
        )
        changed = await asyncio.to_thread(
            self.db.rowcount,
            "UPDATE {schema}.jobs SET doc = %s, finished_at = %s, updated_at = clock_timestamp() "
            "WHERE job_id = %s AND finished_at IS NULL "
            "AND (lease_until IS NULL OR lease_until <= clock_timestamp())",
            (Jsonb(failed.model_dump(mode="json")), failed.finished_at, job_id),
        )
        return failed if changed else await self.get(job_id)

    def _save(self, job: Job) -> None:
        with self.db.pool.connection() as conn, conn.transaction(), conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                self.db.q(
                    "SELECT doc, owner, finished_at, lease_until > clock_timestamp() AS live "
                    "FROM {schema}.jobs WHERE job_id = %s FOR UPDATE"
                ),
                (job.job_id,),
            )
            row = cur.fetchone()
            if row is None or row["finished_at"] is not None or not row["live"]:
                return
            current = Job.model_validate(row["doc"])
            if current.status in TERMINAL_STATUSES:
                return
            if job.status == JobStatus.CANCELLING:
                if current.status == JobStatus.CANCELLING:
                    return
                saved = current.model_copy(
                    update={"status": JobStatus.CANCELLING, "cancellation": job.cancellation}
                )
            elif row["owner"] != self.db.instance_id:
                return
            elif current.status == JobStatus.CANCELLING:
                if job.status not in TERMINAL_STATUSES:
                    return
                # Cancellation committed first: a stale success/failure cannot erase it.
                saved = current.model_copy(
                    update={"status": JobStatus.CANCELLED, "finished_at": datetime.now(UTC)}
                )
            else:
                saved = job
            saved = saved.model_copy(update={"updated_at": datetime.now(UTC)})
            cur.execute(
                self.db.q(
                    "UPDATE {schema}.jobs SET doc = %s, finished_at = %s, updated_at = clock_timestamp() "
                    "WHERE job_id = %s AND finished_at IS NULL "
                    "AND lease_until > clock_timestamp()"
                ),
                (Jsonb(saved.model_dump(mode="json")), saved.finished_at, saved.job_id),
            )

    async def save(self, job: Job) -> None:
        await asyncio.to_thread(self._save, job)


class _PgResults:
    def __init__(self, db: PostgresState) -> None:
        self.db = db

    async def put(self, result: dict[str, Any]) -> None:
        ttl = self.db.limits.idempotency.idempotency_ttl_seconds
        await asyncio.to_thread(
            self.db.run,
            "DELETE FROM {schema}.results WHERE created_at < now() - make_interval(secs => %s)",
            (ttl,),
        )
        await asyncio.to_thread(
            self.db.run,
            "INSERT INTO {schema}.results (invocation_id, doc) VALUES (%s, %s) "
            "ON CONFLICT (invocation_id) DO UPDATE SET doc = EXCLUDED.doc",
            (result["invocation_id"], Jsonb(result)),
        )

    async def get(self, invocation_id: str) -> dict[str, Any] | None:
        rows = await asyncio.to_thread(
            self.db.run, "SELECT doc FROM {schema}.results WHERE invocation_id = %s", (invocation_id,), True
        )
        return dict(rows[0]["doc"]) if rows else None
