"""Persistent state of the LLM service.

Everything that must be shared between instances lives here: configuration documents (providers, model
aliases, budget definitions, connections), budget/rate counters with reservations, the usage ledger,
handler results, ``Idempotency-Key`` records and jobs. The last two are jane-kit's shared stores (R17):
``store.idempotency`` / ``store.jobs`` - in-memory ones for :class:`MemoryStore`, ``jane_kit.stores.postgres``
(token-fenced claims, job leases renewed by the heartbeat, take-over after a crash) for :class:`PostgresStore`.

* :class:`PostgresStore` — the production store (own schema, ``SELECT ... FOR UPDATE`` on counter rows,
  so several instances never overspend a budget together);
* :class:`MemoryStore` — the same semantics in one process, for unit tests and demos only.

The store API is synchronous (psycopg's sync pool works the same on Windows and Linux); async code
calls it through :func:`asyncio.to_thread`.
"""

# SQL is built only from the schema name, validated by Settings.db_schema's pattern; values are bound.
# ruff: noqa: S608

from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, Protocol

from jane_kit.idempotency import IdempotencyLimits, IdempotencyStore, InMemoryIdempotencyStore
from jane_kit.jobs import InMemoryJobStore, JobLimits, JobStore
from jane_kit.stores import LeaseLimits

ConfigKind = Literal["provider", "alias", "budget", "connection"]


# ----------------------------------------------------------------------------- value objects
@dataclass(frozen=True)
class CounterKey:
    scope_type: str
    scope_id: str
    window: str

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.scope_type, self.scope_id, self.window)


@dataclass(frozen=True)
class BudgetCheck:
    key: CounterKey
    limit: float
    currency: str
    period: str
    resets_at: datetime | None


@dataclass(frozen=True)
class RateCheck:
    key: CounterKey
    limit: int
    retry_after_seconds: int


@dataclass
class UsageRecord:
    completion_id: str
    created_at: datetime
    provider_id: str
    model_id: str
    purpose: str
    source_id: str | None
    task_id: str | None
    run_id: str | None
    input_tokens: int
    output_tokens: int
    cost: float
    currency: str
    test_mode: bool
    outcome: str = "ok"


@dataclass
class UsageQuery:
    scope_type: str | None = None
    scope_id: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    group_by: str = "day"


@dataclass
class UsageRow:
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    currency: str = "USD"
    period_start: datetime | None = None
    scope_type: str | None = None
    scope_id: str | None = None
    model: str | None = None
    purpose: str | None = None
    test_mode: bool | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class BudgetExceeded(Exception):
    def __init__(self, check: BudgetCheck, spent: float, reserved: float, requested: float) -> None:
        self.check, self.spent, self.reserved, self.requested = check, spent, reserved, requested
        super().__init__(f"budget {check.key} exhausted")


class RateExceeded(Exception):
    def __init__(self, check: RateCheck) -> None:
        self.check = check
        super().__init__(f"rate {check.key} exceeded")


# ----------------------------------------------------------------------------- protocol
class Store(Protocol):
    def migrate(self) -> None: ...
    def ping(self) -> bool: ...
    def close(self) -> None: ...

    # configuration documents
    def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None: ...
    def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]: ...
    def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
        """Create or replace; returns True if created."""
        ...

    def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
        """Create only if absent; returns True if created."""
        ...

    def delete_doc(self, kind: ConfigKind, key: str) -> bool: ...

    # accounting
    def reserve(
        self,
        reservation_id: str,
        amount: float,
        budgets: list[BudgetCheck],
        rates: list[RateCheck],
        now: datetime,
        stale_after: timedelta,
    ) -> None:
        """Atomically check budgets (spent + reserved + amount <= limit) and rates, then reserve."""
        ...

    def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None:
        """Replace a reservation by the actual cost and append the usage record."""
        ...

    def release(self, reservation_id: str) -> None: ...
    def counter(self, key: CounterKey) -> tuple[float, float]:
        """``(spent, reserved)`` of a counter row (zeros if absent)."""
        ...

    def usage(self, query: UsageQuery) -> list[UsageRow]: ...

    # handler results
    def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None: ...
    def get_invocation(self, invocation_id: str) -> dict[str, Any] | None: ...

    # jane-kit stores of Idempotency-Key records and jobs (shared by the instances of this store)
    idempotency: IdempotencyStore
    jobs: JobStore


def _now() -> datetime:
    return datetime.now(UTC)


def _group_key(rec: UsageRecord, group_by: str) -> tuple[Any, ...]:
    if group_by == "model":
        return (f"{rec.provider_id}/{rec.model_id}", rec.test_mode)
    if group_by == "purpose":
        return (rec.purpose, rec.test_mode)
    if group_by == "scope":
        return (*_most_specific(rec.source_id, rec.task_id), rec.test_mode)
    day = rec.created_at.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    return (day, rec.test_mode)


def _most_specific(source_id: str | None, task_id: str | None) -> tuple[str, str]:
    if task_id:
        return ("task", task_id)
    if source_id:
        return ("source", source_id)
    return ("platform", "platform")


def _row_from_group(group_by: str, key: tuple[Any, ...]) -> UsageRow:
    row = UsageRow(test_mode=bool(key[-1]))
    if group_by == "model":
        row.model = key[0]
    elif group_by == "purpose":
        row.purpose = key[0]
    elif group_by == "scope":
        row.scope_type, row.scope_id = key[0], key[1]
    else:
        row.period_start = key[0]
    return row


def _matches(rec: UsageRecord, q: UsageQuery) -> bool:
    if q.since and rec.created_at < q.since:
        return False
    if q.until and rec.created_at >= q.until:
        return False
    if q.scope_type == "source" and rec.source_id != q.scope_id:
        return False
    return not (q.scope_type == "task" and rec.task_id != q.scope_id)


# ----------------------------------------------------------------------------- memory
class MemoryStore:
    """In-process store with the same semantics as :class:`PostgresStore` (tests, demos)."""

    def __init__(self, jobs: JobLimits | None = None, idempotency: IdempotencyLimits | None = None) -> None:
        self._lock = threading.RLock()
        self._docs: dict[tuple[str, str], dict[str, Any]] = {}
        self._counters: dict[tuple[str, str, str], list[float]] = {}  # spent, reserved, requests
        self._reservations: dict[str, tuple[float, list[tuple[str, str, str]], datetime]] = {}
        self._usage: list[UsageRecord] = []
        self._invocations: dict[str, dict[str, Any]] = {}
        self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(idempotency)
        self.jobs: JobStore = InMemoryJobStore(jobs)

    def migrate(self) -> None:
        return None

    def ping(self) -> bool:
        return True

    def close(self) -> None:
        return None

    def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None:
        with self._lock:
            doc = self._docs.get((kind, key))
            return json.loads(json.dumps(doc)) if doc is not None else None

    def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]:
        with self._lock:
            return [json.loads(json.dumps(d)) for (k, _), d in sorted(self._docs.items()) if k == kind]

    def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
        with self._lock:
            created = (kind, key) not in self._docs
            self._docs[(kind, key)] = json.loads(json.dumps(doc))
            return created

    def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
        with self._lock:
            if (kind, key) in self._docs:
                return False
            self._docs[(kind, key)] = json.loads(json.dumps(doc))
            return True

    def delete_doc(self, kind: ConfigKind, key: str) -> bool:
        with self._lock:
            return self._docs.pop((kind, key), None) is not None

    def _expire(self, now: datetime, stale_after: timedelta) -> None:
        for rid, (amount, keys, created) in list(self._reservations.items()):
            if created < now - stale_after:
                for k in keys:
                    c = self._counters.setdefault(k, [0.0, 0.0, 0.0])
                    c[1] -= amount
                    c[0] += amount
                del self._reservations[rid]

    def reserve(
        self,
        reservation_id: str,
        amount: float,
        budgets: list[BudgetCheck],
        rates: list[RateCheck],
        now: datetime,
        stale_after: timedelta,
    ) -> None:
        with self._lock:
            self._expire(now, stale_after)
            for b in budgets:
                spent, reserved, _ = self._counters.get(b.key.as_tuple(), [0.0, 0.0, 0.0])
                if spent + reserved + amount > b.limit or spent >= b.limit:
                    raise BudgetExceeded(b, spent, reserved, amount)
            for r in rates:
                _, _, requests = self._counters.get(r.key.as_tuple(), [0.0, 0.0, 0.0])
                if requests >= r.limit:
                    raise RateExceeded(r)
            keys = sorted({b.key.as_tuple() for b in budgets})
            for k in keys:
                self._counters.setdefault(k, [0.0, 0.0, 0.0])[1] += amount
            for r in rates:
                self._counters.setdefault(r.key.as_tuple(), [0.0, 0.0, 0.0])[2] += 1
            self._reservations[reservation_id] = (amount, keys, now)

    def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None:
        with self._lock:
            entry = self._reservations.pop(reservation_id, None)
            if entry is not None:
                amount, keys, _ = entry
                for k in keys:
                    c = self._counters.setdefault(k, [0.0, 0.0, 0.0])
                    c[1] -= amount
                    c[0] += cost
            if usage is not None:
                self._usage.append(usage)

    def release(self, reservation_id: str) -> None:
        with self._lock:
            entry = self._reservations.pop(reservation_id, None)
            if entry is not None:
                amount, keys, _ = entry
                for k in keys:
                    self._counters.setdefault(k, [0.0, 0.0, 0.0])[1] -= amount

    def counter(self, key: CounterKey) -> tuple[float, float]:
        with self._lock:
            spent, reserved, _ = self._counters.get(key.as_tuple(), [0.0, 0.0, 0.0])
            return spent, max(reserved, 0.0)

    def usage(self, query: UsageQuery) -> list[UsageRow]:
        with self._lock:
            groups: dict[tuple[Any, ...], UsageRow] = {}
            for rec in self._usage:
                if not _matches(rec, query):
                    continue
                key = (*_group_key(rec, query.group_by), rec.currency)
                row = groups.setdefault(key, _row_from_group(query.group_by, key[:-1]))
                row.currency = rec.currency
                row.requests += 1
                row.input_tokens += rec.input_tokens
                row.output_tokens += rec.output_tokens
                row.cost += rec.cost
            return [groups[k] for k in sorted(groups, key=str)]

    def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None:
        with self._lock:
            self._invocations[invocation_id] = json.loads(json.dumps(result))

    def get_invocation(self, invocation_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._invocations.get(invocation_id)


# ----------------------------------------------------------------------------- postgres
_DDL = """
CREATE TABLE IF NOT EXISTS {s}.config (
    kind text NOT NULL, key text NOT NULL, doc jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (kind, key));
CREATE TABLE IF NOT EXISTS {s}.counters (
    scope_type text NOT NULL, scope_id text NOT NULL, window_key text NOT NULL,
    spent double precision NOT NULL DEFAULT 0, reserved double precision NOT NULL DEFAULT 0,
    requests bigint NOT NULL DEFAULT 0, updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (scope_type, scope_id, window_key));
CREATE TABLE IF NOT EXISTS {s}.reservations (
    reservation_id text PRIMARY KEY, amount double precision NOT NULL, keys jsonb NOT NULL,
    created_at timestamptz NOT NULL);
CREATE TABLE IF NOT EXISTS {s}.usage (
    id bigserial PRIMARY KEY, completion_id text NOT NULL, created_at timestamptz NOT NULL,
    provider_id text NOT NULL, model_id text NOT NULL, purpose text NOT NULL,
    source_id text, task_id text, run_id text, input_tokens bigint NOT NULL, output_tokens bigint NOT NULL,
    cost double precision NOT NULL, currency text NOT NULL, test_mode boolean NOT NULL, outcome text NOT NULL);
CREATE INDEX IF NOT EXISTS usage_created_idx ON {s}.usage (created_at);
CREATE TABLE IF NOT EXISTS {s}.invocations (
    invocation_id text PRIMARY KEY, result jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
"""


class PostgresStore:
    """Store in the service's own PostgreSQL schema; safe for several instances."""

    def __init__(
        self,
        dsn: str,
        schema: str,
        *,
        min_size: int,
        max_size: int,
        owner: str | None = None,
        leases: LeaseLimits | None = None,
        job_retention_s: float | None = None,
    ) -> None:
        from psycopg_pool import ConnectionPool  # local import: memory mode needs no driver

        from jane_kit.stores.postgres import PgIdempotencyStore, PgJobStore, pool_tx

        self.schema = schema
        self.pool = ConnectionPool(dsn, min_size=min_size, max_size=max_size, open=True)
        leases = leases or LeaseLimits()
        owner = owner or f"llm-{uuid.uuid4().hex}"
        tx = pool_tx(self.pool)
        # the tables of WP-10 keep their layout: one ``response`` column, the job document in ``job``
        self.pg_idempotency = PgIdempotencyStore(
            tx,
            owner=owner,
            in_progress_lease_s=leases.in_progress_lease_ms / 1000,
            schema=schema,
            layout="json",
        )
        self.pg_jobs = PgJobStore(
            tx,
            owner=owner,
            lease_s=leases.job_lease_ms / 1000,
            retention_s=JobLimits().job_retention_seconds if job_retention_s is None else job_retention_s,
            schema=schema,
            doc_column="job",
        )
        self.idempotency: IdempotencyStore = self.pg_idempotency
        self.jobs: JobStore = self.pg_jobs

    @contextmanager
    def _tx(self) -> Iterator[Any]:
        with self.pool.connection() as conn, conn.transaction(), conn.cursor() as cur:
            yield cur

    def _t(self, name: str) -> str:
        return f'"{self.schema}".{name}'

    def migrate(self) -> None:
        with self._tx() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (f"jane-llm-migrate-{self.schema}",))
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"')
            cur.execute(_DDL.format(s=f'"{self.schema}"'))
            for statement in (*self.pg_idempotency.ddl(), *self.pg_jobs.ddl()):
                cur.execute(statement)

    def ping(self) -> bool:
        with self._tx() as cur:
            cur.execute("SELECT 1")
            return bool(cur.fetchone())

    def close(self) -> None:
        self.pool.close()

    # -- config
    def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None:
        with self._tx() as cur:
            cur.execute(f"SELECT doc FROM {self._t('config')} WHERE kind=%s AND key=%s", (kind, key))
            row = cur.fetchone()
            return dict(row[0]) if row else None

    def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]:
        with self._tx() as cur:
            cur.execute(f"SELECT doc FROM {self._t('config')} WHERE kind=%s ORDER BY key", (kind,))
            return [dict(r[0]) for r in cur.fetchall()]

    def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
        with self._tx() as cur:
            cur.execute(
                f"INSERT INTO {self._t('config')} (kind, key, doc) VALUES (%s, %s, %s) "
                "ON CONFLICT (kind, key) DO UPDATE SET doc = EXCLUDED.doc, updated_at = now() "
                "RETURNING (xmax = 0)",
                (kind, key, json.dumps(doc)),
            )
            row = cur.fetchone()
            return bool(row and row[0])

    def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool:
        with self._tx() as cur:
            cur.execute(
                f"INSERT INTO {self._t('config')} (kind, key, doc) VALUES (%s, %s, %s) "
                "ON CONFLICT (kind, key) DO NOTHING",
                (kind, key, json.dumps(doc)),
            )
            return bool(cur.rowcount)

    def delete_doc(self, kind: ConfigKind, key: str) -> bool:
        with self._tx() as cur:
            cur.execute(f"DELETE FROM {self._t('config')} WHERE kind=%s AND key=%s", (kind, key))
            return bool(cur.rowcount)

    # -- accounting
    def _expired(self, cur: Any, now: datetime, stale_after: timedelta) -> dict[tuple[str, str, str], float]:
        """Delete stale reservations; return the amount to move from ``reserved`` to ``spent`` per counter."""
        cur.execute(
            f"DELETE FROM {self._t('reservations')} WHERE reservation_id IN ("
            f"  SELECT reservation_id FROM {self._t('reservations')} WHERE created_at < %s "
            "  FOR UPDATE SKIP LOCKED) RETURNING amount, keys",
            (now - stale_after,),
        )
        moved: dict[tuple[str, str, str], float] = {}
        for amount, keys in cur.fetchall():
            for k in keys:
                key = (str(k[0]), str(k[1]), str(k[2]))
                moved[key] = moved.get(key, 0.0) + float(amount)
        return moved

    def reserve(
        self,
        reservation_id: str,
        amount: float,
        budgets: list[BudgetCheck],
        rates: list[RateCheck],
        now: datetime,
        stale_after: timedelta,
    ) -> None:
        check_keys = {b.key.as_tuple() for b in budgets} | {r.key.as_tuple() for r in rates}
        with self._tx() as cur:
            moved = self._expired(cur, now, stale_after)
            # Every counter row touched by this transaction is locked in one global order (sorted keys),
            # so concurrent transactions on several instances cannot deadlock.
            keys = sorted(check_keys | set(moved))
            for st, sid, win in keys:
                cur.execute(
                    f"INSERT INTO {self._t('counters')} (scope_type, scope_id, window_key) VALUES (%s,%s,%s) "
                    "ON CONFLICT DO NOTHING",
                    (st, sid, win),
                )
            state: dict[tuple[str, str, str], tuple[float, float, int]] = {}
            for st, sid, win in keys:
                cur.execute(
                    f"SELECT spent, reserved, requests FROM {self._t('counters')} "
                    "WHERE scope_type=%s AND scope_id=%s AND window_key=%s FOR UPDATE",
                    (st, sid, win),
                )
                row = cur.fetchone()
                spent, reserved, requests = float(row[0]), float(row[1]), int(row[2])
                if (st, sid, win) in moved:
                    delta = moved[(st, sid, win)]
                    cur.execute(
                        f"UPDATE {self._t('counters')} SET reserved = reserved - %s, spent = spent + %s, "
                        "updated_at = now() WHERE scope_type=%s AND scope_id=%s AND window_key=%s",
                        (delta, delta, st, sid, win),
                    )
                    spent, reserved = spent + delta, reserved - delta
                state[(st, sid, win)] = (spent, reserved, requests)
            for b in budgets:
                spent, reserved, _ = state[b.key.as_tuple()]
                if spent + reserved + amount > b.limit or spent >= b.limit:
                    raise BudgetExceeded(b, spent, max(reserved, 0.0), amount)
            for r in rates:
                if state[r.key.as_tuple()][2] >= r.limit:
                    raise RateExceeded(r)
            budget_keys = sorted({b.key.as_tuple() for b in budgets})
            for st, sid, win in budget_keys:
                cur.execute(
                    f"UPDATE {self._t('counters')} SET reserved = reserved + %s, updated_at = now() "
                    "WHERE scope_type=%s AND scope_id=%s AND window_key=%s",
                    (amount, st, sid, win),
                )
            for r in rates:
                st, sid, win = r.key.as_tuple()
                cur.execute(
                    f"UPDATE {self._t('counters')} SET requests = requests + 1, updated_at = now() "
                    "WHERE scope_type=%s AND scope_id=%s AND window_key=%s",
                    (st, sid, win),
                )
            cur.execute(
                f"INSERT INTO {self._t('reservations')} (reservation_id, amount, keys, created_at) "
                "VALUES (%s, %s, %s, %s)",
                (reservation_id, amount, json.dumps(budget_keys), now),
            )

    def _drop_reservation(self, cur: Any, reservation_id: str, cost: float | None) -> None:
        cur.execute(
            f"DELETE FROM {self._t('reservations')} WHERE reservation_id=%s RETURNING amount, keys",
            (reservation_id,),
        )
        row = cur.fetchone()
        if row is None:
            return  # already charged at its estimate after expiry
        amount, keys = float(row[0]), row[1]
        for st, sid, win in sorted(tuple(k) for k in keys):
            cur.execute(
                f"UPDATE {self._t('counters')} SET reserved = reserved - %s, spent = spent + %s, "
                "updated_at = now() WHERE scope_type=%s AND scope_id=%s AND window_key=%s",
                (amount, cost or 0.0, st, sid, win),
            )

    def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None:
        with self._tx() as cur:
            self._drop_reservation(cur, reservation_id, cost)
            if usage is not None:
                u = asdict(usage)
                cols = list(u)
                cur.execute(
                    f"INSERT INTO {self._t('usage')} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})",
                    [u[c] for c in cols],
                )

    def release(self, reservation_id: str) -> None:
        with self._tx() as cur:
            self._drop_reservation(cur, reservation_id, None)

    def counter(self, key: CounterKey) -> tuple[float, float]:
        with self._tx() as cur:
            cur.execute(
                f"SELECT spent, reserved FROM {self._t('counters')} "
                "WHERE scope_type=%s AND scope_id=%s AND window_key=%s",
                key.as_tuple(),
            )
            row = cur.fetchone()
            return (float(row[0]), max(float(row[1]), 0.0)) if row else (0.0, 0.0)

    def usage(self, query: UsageQuery) -> list[UsageRow]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if query.since:
            where.append("created_at >= %s")
            params.append(query.since)
        if query.until:
            where.append("created_at < %s")
            params.append(query.until)
        if query.scope_type == "source":
            where.append("source_id = %s")
            params.append(query.scope_id)
        elif query.scope_type == "task":
            where.append("task_id = %s")
            params.append(query.scope_id)
        group = {
            "model": ["provider_id || '/' || model_id"],
            "purpose": ["purpose"],
            "scope": [
                "CASE WHEN task_id IS NOT NULL THEN 'task' WHEN source_id IS NOT NULL THEN 'source' "
                "ELSE 'platform' END",
                "COALESCE(task_id, source_id, 'platform')",
            ],
        }.get(query.group_by, ["date_trunc('day', created_at AT TIME ZONE 'UTC')"])
        cols = ", ".join(group)
        sql = (
            f"SELECT {cols}, test_mode, currency, count(*), sum(input_tokens), sum(output_tokens), sum(cost) "
            f"FROM {self._t('usage')} WHERE {' AND '.join(where)} "
            f"GROUP BY {cols}, test_mode, currency ORDER BY 1"
        )
        with self._tx() as cur:
            cur.execute(sql, params)
            rows = []
            for rec in cur.fetchall():
                n = len(group)
                key = list(rec[:n])
                if query.group_by not in {"model", "purpose", "scope"}:
                    key[0] = key[0].replace(tzinfo=UTC)
                row = _row_from_group(query.group_by, (*key, rec[n]))
                row.currency = rec[n + 1]
                row.requests, row.input_tokens, row.output_tokens = (
                    int(rec[n + 2]),
                    int(rec[n + 3]),
                    int(rec[n + 4]),
                )
                row.cost = float(rec[n + 5])
                rows.append(row)
            return rows

    # -- invocations
    def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None:
        with self._tx() as cur:
            cur.execute(
                f"INSERT INTO {self._t('invocations')} (invocation_id, result) VALUES (%s, %s) "
                "ON CONFLICT (invocation_id) DO UPDATE SET result = EXCLUDED.result",
                (invocation_id, json.dumps(result)),
            )

    def get_invocation(self, invocation_id: str) -> dict[str, Any] | None:
        with self._tx() as cur:
            cur.execute(
                f"SELECT result FROM {self._t('invocations')} WHERE invocation_id=%s", (invocation_id,)
            )
            row = cur.fetchone()
            return dict(row[0]) if row else None


def iter_keys(checks: Iterable[BudgetCheck]) -> list[CounterKey]:
    return [c.key for c in checks]
