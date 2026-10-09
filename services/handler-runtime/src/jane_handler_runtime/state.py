"""Service state shared by instances: idempotency keys, jobs and invocation results.

* ``InMemoryState`` - default for a single standalone instance and the CLI (lost on restart);
* ``PostgresState`` - own database/schema ``jane_handler_runtime`` (``JANE_HANDLER_RUNTIME_STATE_DSN``,
  data-ownership.md): jane-kit's shared ``PgIdempotencyStore`` / ``PgJobStore`` (R17) and the results of
  ``GET /v1/invocations/{id}``, so any instance answers a redelivery with the stored result
  (``duplicate: true``) and reads jobs/invocations created by another instance.

psycopg is used synchronously in worker threads (``asyncio.to_thread``): the async driver does not work with
the Windows Proactor event loop, and the service must run on Windows and Linux.
"""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from typing import Any, Protocol

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from jane_kit.idempotency import IdempotencyStore, InMemoryIdempotencyStore
from jane_kit.jobs import InMemoryJobStore, JobStore
from jane_kit.stores.postgres import PgDatabase, PgIdempotencyStore, PgJobStore, migrate

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

_RESULTS_DDL = [
    """CREATE TABLE IF NOT EXISTS {schema}.results (
        invocation_id text PRIMARY KEY,
        doc jsonb NOT NULL,
        created_at timestamptz NOT NULL DEFAULT now()
    )""",
    "CREATE INDEX IF NOT EXISTS results_created_at ON {schema}.results (created_at)",
]


class PostgresState:
    """Idempotency keys and jobs in jane-kit's shared stores (R17: leases, fencing, take-over), results here.

    Tables ``idempotency`` and ``jobs`` keep their layout (split response columns, ``doc``); the kit migration
    adds the claim ``owner``/``token`` columns in place.
    """

    name = "postgresql"

    def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None:
        self.schema_name = schema
        self.schema = sql.Identifier(schema)
        self.limits = limits
        self.instance_id = instance_id
        state = limits.state
        self.db = PgDatabase(dsn, max_size=state.pool_max_size, connect_timeout_ms=state.connect_timeout_ms)
        self.pool = self.db.pool
        self._idem = PgIdempotencyStore(
            self.db.tx,
            owner=instance_id,
            in_progress_lease_s=state.in_progress_lease_ms / 1000,
            schema=schema,
        )
        self._jobs = PgJobStore(
            self.db.tx,
            owner=instance_id,
            lease_s=state.job_lease_ms / 1000,
            retention_s=limits.jobs.job_retention_seconds,
            schema=schema,
        )
        self.idempotency: IdempotencyStore = self._idem
        self.jobs: JobStore = self._jobs
        self.results: ResultStore = _PgResults(self)

    def q(self, text: str) -> sql.Composed:
        return sql.SQL(text).format(schema=self.schema)

    def run(self, text: str, params: tuple[Any, ...] = (), fetch: bool = False) -> list[dict[str, Any]]:
        with self.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(self.q(text), params)
            return list(cur.fetchall()) if fetch else []

    def _migrate(self) -> None:
        migrate(
            self.db.tx,
            f"jane-handler-runtime-{self.schema_name}",
            self._idem,
            self._jobs,
            schema=self.schema_name,
        )
        with self.db.tx() as conn:
            for stmt in _RESULTS_DDL:
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
