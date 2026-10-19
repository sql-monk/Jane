"""Move the news entities into the PostgreSQL ``news`` layout (docs/delivery/news-pg.md, section 4).

Types: ``article``, ``post``, ``news_article``, ``news_event``. Sources, each can be turned off with ``--source``:

* ``mongo`` - MongoDB connection ``results-mongo`` (database ``jane_results``);
* ``legacy-pg`` - the old PostgreSQL connection ``results-pg`` (database ``jane_storage_results``, schema ``public``).

Target: connection ``results-news`` - the same database, schema ``news`` (``--target-schema``), ``layout = "news"``.

Both sources are read through the storage adapter protocol (``list_entities`` / ``list_history``), so the MongoDB
adapter itself rolls forward commits left ``pending``. The events of one entity key from both sources are ordered
by ``received_at``, then source (``legacy-pg`` before ``mongo``), then version, and every event is replayed through
``StorageEngine.store_entity`` over the target ``PostgresAdapter`` with its original ``delivery_key`` and an engine
clock that returns its original ``received_at``. Merge, versions, history, deliveries and the relational
projection come out as with a live write; a repeated run is idempotent (``duplicate``) and only adds the events that
appeared since the previous run. Different keys run in parallel (``--concurrency``), the events of one key never do.

Nothing is deleted or changed in the sources (reading a MongoDB history only completes a commit left ``pending``,
as every reader does). Modes: the default migrates; ``--dry-run`` only counts the sources (entities and events =
sum of versions, one history event per accepted update; it reads states only and writes nothing anywhere);
``--verify`` compares the target with the sources (run it with the same ``--source`` as the migration) and the
projection rows with the target state, writes nothing and exits with 1 on any discrepancy. A key whose target
history has delivery keys no source has was written live after the switch: it is listed, not counted as an error.

Addresses and credentials come from the stack file ``.jane/stack-<project>.json`` (``--stack``, default
``jane-demo``) or from explicit options; passwords only from environment variables or that file, never from argv.
The target schema must be created by and belong to the role of the storage service (``--service-role``,
default ``jane_storage_results``), otherwise the service could not write into it.

Examples (repository root):

    uv run python scripts/migrate_news_to_pg.py --dry-run
    uv run python scripts/migrate_news_to_pg.py
    uv run python scripts/migrate_news_to_pg.py --verify
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from collections import Counter
from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jane_contracts.storage_adapter import (
    AdapterError,
    EntitySnapshot,
    HistoryEvent,
    OrderKey,
    ResolvedConnection,
    StorageAdapter,
    order_tuple,
)
from jane_kit.clients import RetryPolicy
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key
from jane_storage_mongodb import MongoAdapter
from jane_storage_postgres import PostgresAdapter

NEWS_TYPES: tuple[str, ...] = ("article", "post", "news_article", "news_event")
SOURCES: tuple[str, ...] = ("legacy-pg", "mongo")
"""Source names; the order is also the tie-break of events with the same ``received_at``."""
PROJECTION_TABLES: dict[str, str] = {entity_type: entity_type for entity_type in NEWS_TYPES}
"""Parent table of the ``news`` layout per entity type (docs/delivery/news-pg.md, section 3)."""
STATE_TABLE = "jane_entities"
"""State table of the target (``PostgresAdapter`` default ``table_prefix`` ``jane_``)."""
STATUSES: tuple[str, ...] = ("written", "partially_stale", "stale", "duplicate")
TARGET_CONNECTION_ID = "results-news"
LEGACY_CONNECTION_ID = "results-pg"
MONGO_CONNECTION_ID = "results-mongo"
TARGET_LAYOUT = "news"
SERVICE_ROLE = "jane_storage_results"
DEFAULT_STACK = "jane-demo"
DEFAULT_PG_DATABASE = "jane_storage_results"
DEFAULT_MONGO_DATABASE = "jane_results"
DEFAULT_PG_PASSWORD_ENV = "JANE_PG_STORAGE_RESULTS_PASSWORD"  # noqa: S105 - a variable name, not a value
DEFAULT_MONGO_PASSWORD_ENV = "JANE_MONGO_PASSWORD"  # noqa: S105 - a variable name, not a value
DEFAULT_BATCH_SIZE = 200
"""Page size of ``list_entities`` / ``list_history``."""
DEFAULT_CONCURRENCY = 4
"""Entity keys replayed (or checked) at the same time; also the connection pool size of every adapter."""
DEFAULT_PROGRESS_EVERY = 200
"""Keys between two progress lines."""
DEFAULT_MAX_FAILURES = 10
"""Failed keys after which no further keys are started (a broken connection fails every key)."""
DEFAULT_SHOW = 20
"""Failed keys, discrepancies and projection examples printed per list (``--examples``)."""
_IDENT = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
_LOWEST = (datetime.min.replace(tzinfo=UTC), -1, "")


class ConfigError(Exception):
    """Missing or invalid settings (exit code 2)."""


# ----------------------------------------------------------------------------- reading through the protocol
async def list_all_entities(
    adapter: StorageAdapter, entity_type: str, batch_size: int
) -> list[EntitySnapshot]:
    out: list[EntitySnapshot] = []
    cursor: str | None = None
    while True:
        page, cursor = await adapter.list_entities(entity_type, cursor=cursor, limit=batch_size)
        out.extend(page)
        if cursor is None:
            return out


async def list_all_history(
    adapter: StorageAdapter, entity_type: str, key: str, batch_size: int
) -> list[HistoryEvent]:
    """The whole history of one entity, oldest first (adapters list it newest first)."""
    out: list[HistoryEvent] = []
    cursor: str | None = None
    while True:
        page, cursor = await adapter.list_history(entity_type, key, cursor=cursor, limit=batch_size)
        out.extend(page)
        if cursor is None:
            out.reverse()
            return out


# ----------------------------------------------------------------------------- planning (pure)
@dataclass
class KeyPlan:
    """One entity of the target and its states in the sources (source name -> snapshot)."""

    entity_type: str
    key: str
    sources: dict[str, EntitySnapshot] = field(default_factory=dict)

    @property
    def origin(self) -> str:
        """``legacy-pg``, ``mongo`` or ``both``."""
        return next(iter(self.sources)) if len(self.sources) == 1 else "both"


def plan_keys(entity_type: str, snapshots: Mapping[str, Iterable[EntitySnapshot]]) -> dict[str, KeyPlan]:
    """Group the source states by the target key (``canonical_key`` of the entity key, as the engine builds it)."""
    unknown = set(snapshots) - set(SOURCES)
    if unknown:
        raise ValueError(f"unknown sources: {sorted(unknown)}")
    plans: dict[str, KeyPlan] = {}
    for source in sorted(snapshots, key=SOURCES.index):
        for snap in snapshots[source]:
            key = canonical_key(snap.key)
            plans.setdefault(key, KeyPlan(entity_type, key)).sources[source] = snap
    return plans


@dataclass(frozen=True, slots=True)
class SourceEvent:
    source: str
    position: int
    """1-based place in the source history (the source version when the history has no gaps)."""
    event: HistoryEvent

    def order(self) -> tuple[datetime, int, int]:
        return (self.event.received_at, SOURCES.index(self.source), self.position)


def replay_order(streams: Mapping[str, Sequence[HistoryEvent]]) -> list[SourceEvent]:
    """Events of one key from every source (each stream oldest first) in replay order:
    ``received_at``, then source (``legacy-pg`` first), then version."""
    events = [
        SourceEvent(source, position, event)
        for source, stream in streams.items()
        for position, event in enumerate(stream, 1)
    ]
    return sorted(events, key=SourceEvent.order)


def repeated_deliveries(events: Sequence[SourceEvent]) -> tuple[int, int]:
    """(events whose delivery key an earlier event of the key already has, those of them with another record)."""
    first: dict[str, SourceEvent] = {}
    repeated = differing = 0
    for item in events:
        prior = first.setdefault(item.event.delivery_key, item)
        if prior is not item:
            repeated += 1
            differing += prior.event.record != item.event.record
    return repeated, differing


def fixed_clock(at: datetime) -> Callable[[], datetime]:
    """Engine clock of one replayed event: always its original ``received_at``."""
    return lambda: at


# ----------------------------------------------------------------------------- comparison (pure)
def _rank(snap: EntitySnapshot, name: str) -> tuple[datetime, int, str]:
    order = snap.field_orders.get(name)
    return _LOWEST if order is None else order_tuple(order)


def _field_state(snap: EntitySnapshot, name: str) -> tuple[str, Any, OrderKey | None]:
    if name in snap.cleared_fields:
        return ("cleared", None, snap.field_orders.get(name))
    if name in snap.fields:
        return ("set", snap.fields[name], snap.field_orders.get(name))
    return ("absent", None, snap.field_orders.get(name))


def state_differences(sources: Sequence[EntitySnapshot], target: EntitySnapshot) -> list[str]:
    """What differs between the target state and the merge of the source states (empty: nothing).

    Per field, the source whose observation order of the field is the newest wins (ties: any of them) - what
    the replay of their histories through the merge produces; for one source that is its state as it is.
    Compared: value or clear (``fields``, ``cleared_fields``) and the order (``field_orders``)."""
    names: set[str] = set(target.fields) | set(target.cleared_fields) | set(target.field_orders)
    for snap in sources:
        names |= set(snap.fields) | set(snap.cleared_fields) | set(snap.field_orders)
    values: list[str] = []
    orders: list[str] = []
    for name in sorted(names):
        holders = [s for s in sources if _field_state(s, name) != ("absent", None, None)]
        if holders:
            best = max(_rank(s, name) for s in holders)
            expected = [_field_state(s, name) for s in holders if _rank(s, name) == best]
        else:
            expected = [("absent", None, None)]
        actual = _field_state(target, name)
        if actual in expected:
            continue
        if any(actual[:2] == candidate[:2] for candidate in expected):
            orders.append(name)
        else:
            values.append(name)
    out = []
    if values:
        out.append("fields: " + ", ".join(values))
    if orders:
        out.append("field_orders: " + ", ".join(orders))
    return out


# ----------------------------------------------------------------------------- worker pool
async def run_pool[T](
    items: Iterable[T], worker: Callable[[T], Awaitable[None]], concurrency: int, stop: Callable[[], bool]
) -> None:
    """``worker`` for every item, at most ``concurrency`` at a time; no new item once ``stop()`` is true."""
    pending = iter(items)

    async def runner() -> None:
        for item in pending:  # one shared iterator: every item is taken once
            if stop():
                return
            await worker(item)

    async with asyncio.TaskGroup() as group:
        for _ in range(max(1, concurrency)):
            group.create_task(runner())


# ----------------------------------------------------------------------------- dry run
@dataclass
class SurveyRow:
    entity_type: str
    entities: dict[str, int]
    events: dict[str, int]
    keys: int
    both: int


async def survey(
    sources: Mapping[str, StorageAdapter], types: Sequence[str], batch_size: int
) -> list[SurveyRow]:
    """Counts only: entities per source and their events (sum of versions), distinct keys, keys in both sources."""
    rows = []
    for entity_type in types:
        snaps = {
            name: await list_all_entities(adapter, entity_type, batch_size)
            for name, adapter in sources.items()
        }
        plans = plan_keys(entity_type, snaps)
        rows.append(
            SurveyRow(
                entity_type=entity_type,
                entities={name: len(items) for name, items in snaps.items()},
                events={name: sum(s.version for s in items) for name, items in snaps.items()},
                keys=len(plans),
                both=sum(1 for p in plans.values() if p.origin == "both"),
            )
        )
    return rows


# ----------------------------------------------------------------------------- migration
@dataclass
class TypeReport:
    keys: Counter[str] = field(default_factory=Counter)
    """Keys by origin (``legacy-pg``, ``mongo``, ``both``)."""
    events: int = 0
    statuses: Counter[str] = field(default_factory=Counter)
    repeated_deliveries: int = 0
    """Events whose delivery key another event of the key (the other source) already had: replayed as duplicate."""
    differing_repeats: int = 0
    """... of them with a different record (that record is not applied)."""
    failed_keys: int = 0


@dataclass
class MigrationReport:
    types: dict[str, TypeReport]
    failures: list[str] = field(default_factory=list)
    stopped: bool = False
    seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return not self.failures and not self.stopped


async def replay_key(
    target: StorageAdapter,
    events: Sequence[SourceEvent],
    *,
    connection_id: str,
    retries: RetryPolicy,
) -> Counter[str]:
    """Replay the events of one key in the given order; ``WriteAck.status`` counts."""
    statuses: Counter[str] = Counter()
    for item in events:
        engine = StorageEngine(
            target, connection_id=connection_id, retries=retries, clock=fixed_clock(item.event.received_at)
        )
        ack = await engine.store_entity(item.event.record, item.event.delivery_key)
        statuses[str(ack["status"])] += 1
    return statuses


async def migrate(
    sources: Mapping[str, StorageAdapter],
    target: StorageAdapter,
    *,
    types: Sequence[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
    concurrency: int = DEFAULT_CONCURRENCY,
    connection_id: str = TARGET_CONNECTION_ID,
    retries: RetryPolicy | None = None,
    progress_every: int = DEFAULT_PROGRESS_EVERY,
    max_failures: int = DEFAULT_MAX_FAILURES,
    out: Callable[[str], None] = print,
) -> MigrationReport:
    started = time.monotonic()
    policy = retries or RetryPolicy()
    await target.ensure_schema(list(types))
    report = MigrationReport(types={t: TypeReport() for t in types})
    plans: list[KeyPlan] = []
    for entity_type in types:
        snaps = {
            name: await list_all_entities(adapter, entity_type, batch_size)
            for name, adapter in sources.items()
        }
        type_plans = plan_keys(entity_type, snaps)
        report.types[entity_type].keys.update(p.origin for p in type_plans.values())
        plans.extend(type_plans.values())
    total = len(plans)
    out(f"keys to replay: {total}")
    done = 0
    totals: Counter[str] = Counter()

    async def work(plan: KeyPlan) -> None:
        nonlocal done
        stats = report.types[plan.entity_type]
        try:
            streams = {
                name: await list_all_history(sources[name], plan.entity_type, snap.canonical_key, batch_size)
                for name, snap in plan.sources.items()
            }
            events = replay_order(streams)
            repeated, differing = repeated_deliveries(events)
            statuses = await replay_key(target, events, connection_id=connection_id, retries=policy)
        except Exception as exc:  # one key fails, the others go on; a repeated run retries it (idempotent)
            stats.failed_keys += 1
            report.failures.append(f"{plan.entity_type} {plan.key}: {type(exc).__name__}: {exc}")
        else:
            stats.events += len(events)
            stats.statuses.update(statuses)
            stats.repeated_deliveries += repeated
            stats.differing_repeats += differing
            totals.update(statuses)
        done += 1
        if progress_every > 0 and (done % progress_every == 0 or done == total):
            counts = ", ".join(f"{s} {totals[s]}" for s in STATUSES)
            out(f"  {done}/{total} keys; events: {counts}; {time.monotonic() - started:.1f}s")

    def stop() -> bool:
        report.stopped = len(report.failures) >= max_failures
        return report.stopped

    await run_pool(plans, work, concurrency, stop)
    report.seconds = time.monotonic() - started
    return report


# ----------------------------------------------------------------------------- verification
@dataclass(frozen=True)
class ProjectionCheck:
    """Projection of one type against the target state: the sets of ``(canonical_key, version)`` pairs."""

    states: int
    rows: int
    only_state: int = 0
    """Pairs of the state with no projection row (no row, or a row with another version)."""
    only_rows: int = 0
    """Pairs of the projection with no such state."""
    state_examples: tuple[str, ...] = ()
    row_examples: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.only_state == 0 and self.only_rows == 0


ProjectionChecker = Callable[[str], Awaitable[ProjectionCheck | None]]
"""Projection check of a type, or ``None`` when the layout tables do not exist."""

VERIFY_COLUMNS: tuple[str, ...] = ("keys", "ok", "mismatch", "missing", "changed_after")


@dataclass
class VerifyReport:
    rows: dict[tuple[str, str], Counter[str]] = field(default_factory=dict)
    """(type, origin) -> counts of ``VERIFY_COLUMNS``."""
    target_only: Counter[str] = field(default_factory=Counter)
    """Target keys of a type that no source has (written to the target directly): not compared."""
    projection: dict[str, ProjectionCheck | None] = field(default_factory=dict)
    """Per type: the check or ``None`` (layout unavailable). Empty: not checked."""
    problems: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)

    @property
    def projection_ok(self) -> bool:
        return all(check is not None and check.ok for check in self.projection.values())

    @property
    def ok(self) -> bool:
        bad = sum(c["mismatch"] + c["missing"] for c in self.rows.values())
        return bad == 0 and self.projection_ok


async def _delivery_keys(adapter: StorageAdapter, entity_type: str, key: str, batch_size: int) -> set[str]:
    return {e.delivery_key for e in await list_all_history(adapter, entity_type, key, batch_size)}


async def check_key(
    plan: KeyPlan,
    target_snap: EntitySnapshot | None,
    sources: Mapping[str, StorageAdapter],
    target: StorageAdapter,
    batch_size: int,
) -> tuple[str, list[str]]:
    """``ok``, ``missing``, ``mismatch`` or ``changed_after`` (the target got events no source has: a live write
    after the migration) and what differs. Histories are read only when the states alone do not settle it."""
    if target_snap is None:
        return "missing", []
    source_keys: set[str] | None = None

    async def keys_of_sources() -> set[str]:
        nonlocal source_keys
        if source_keys is None:
            source_keys = set()
            for name, snap in plan.sources.items():
                source_keys |= await _delivery_keys(
                    sources[name], plan.entity_type, snap.canonical_key, batch_size
                )
        return source_keys

    problems = state_differences(list(plan.sources.values()), target_snap)
    expected = sum(s.version for s in plan.sources.values())
    if target_snap.version != expected and len(plan.sources) > 1:
        # a delivery key present in both sources is replayed once (the second time it is a duplicate)
        expected = len(await keys_of_sources())
    if target_snap.version != expected:
        problems.append(f"version {target_snap.version} != {expected}")
    if not problems:
        return "ok", []
    if await _delivery_keys(target, plan.entity_type, plan.key, batch_size) - await keys_of_sources():
        return "changed_after", problems
    return "mismatch", problems


async def verify(
    sources: Mapping[str, StorageAdapter],
    target: StorageAdapter,
    *,
    types: Sequence[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
    concurrency: int = DEFAULT_CONCURRENCY,
    projection: ProjectionChecker | None = None,
) -> VerifyReport:
    """(a) every source key against the target state; (b) per type, the ``(canonical_key, version)`` pairs of the
    projection against those of the target state."""
    report = VerifyReport()
    for entity_type in types:
        snaps = {
            name: await list_all_entities(adapter, entity_type, batch_size)
            for name, adapter in sources.items()
        }
        plans = plan_keys(entity_type, snaps)
        state = {s.canonical_key: s for s in await list_all_entities(target, entity_type, batch_size)}
        report.target_only[entity_type] = len(set(state) - set(plans))
        for origin in (*SOURCES, "both"):
            report.rows[(entity_type, origin)] = Counter({column: 0 for column in VERIFY_COLUMNS})

        async def check(plan: KeyPlan, state: dict[str, EntitySnapshot] = state) -> None:
            verdict, problems = await check_key(plan, state.get(plan.key), sources, target, batch_size)
            row = report.rows[(plan.entity_type, plan.origin)]
            row["keys"] += 1
            row[verdict] += 1
            line = f"{plan.entity_type} [{plan.origin}] {plan.key}: {verdict}" + (
                f" ({'; '.join(problems)})" if problems else ""
            )
            if verdict in ("mismatch", "missing"):
                report.problems.append(line)
            elif verdict == "changed_after":
                report.changed.append(line)

        await run_pool(plans.values(), check, concurrency, lambda: False)
        if projection is not None:
            report.projection[entity_type] = await projection(entity_type)
    return report


def postgres_projection_checker(adapter: PostgresAdapter, schema: str, examples: int) -> ProjectionChecker:
    """``(canonical_key, version)`` of ``<schema>.<type table>`` against the states of the type in
    ``<schema>.jane_entities``: counts and up to ``examples`` pairs of each side, one statement (one snapshot)."""
    if not _IDENT.match(schema):
        raise ConfigError(f"invalid schema {schema!r}")

    async def check(entity_type: str) -> ProjectionCheck | None:
        table = PROJECTION_TABLES[entity_type]
        async with adapter.pool.acquire() as con:
            if not await con.fetchval("SELECT to_regclass($1) IS NOT NULL", f'"{schema}"."{table}"'):
                return None
            row = await con.fetchrow(
                f"""WITH s AS (SELECT canonical_key, version FROM "{schema}"."{STATE_TABLE}" WHERE entity_type = $1),
                    p AS (SELECT canonical_key, version FROM "{schema}"."{table}"),
                    d AS (SELECT s.canonical_key AS state_key, s.version AS state_version,
                                 p.canonical_key AS row_key, p.version AS row_version
                          FROM s FULL JOIN p ON p.canonical_key = s.canonical_key AND p.version = s.version
                          WHERE s.canonical_key IS NULL OR p.canonical_key IS NULL)
                SELECT (SELECT count(*) FROM s) AS states, (SELECT count(*) FROM p) AS projection_rows,
                       (SELECT count(*) FROM d WHERE row_key IS NULL) AS only_state,
                       (SELECT count(*) FROM d WHERE state_key IS NULL) AS only_rows,
                       ARRAY(SELECT state_key || ' v' || state_version FROM d WHERE row_key IS NULL
                             ORDER BY state_key COLLATE "C" LIMIT $2) AS state_examples,
                       ARRAY(SELECT row_key || ' v' || row_version FROM d WHERE state_key IS NULL
                             ORDER BY row_key COLLATE "C" LIMIT $2) AS row_examples""",  # noqa: S608 - identifiers validated by _IDENT or constants
                entity_type,
                examples,
            )
        return ProjectionCheck(
            states=int(row["states"]),
            rows=int(row["projection_rows"]),
            only_state=int(row["only_state"]),
            only_rows=int(row["only_rows"]),
            state_examples=tuple(row["state_examples"]),
            row_examples=tuple(row["row_examples"]),
        )

    return check


async def schema_owner_problem(adapter: PostgresAdapter, schema: str, service_role: str) -> str | None:
    """Why writing would leave the target schema (or its tables) not owned by the storage service role."""
    async with adapter.pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT current_user AS me, (SELECT pg_get_userbyid(nspowner) FROM pg_namespace WHERE nspname = $1) AS owner",
            schema,
        )
    me, owner = str(row["me"]), row["owner"]
    if owner is not None and owner != service_role:
        return f"schema {schema!r} belongs to {owner!r}, not to the storage service role {service_role!r}"
    if me != service_role:
        return (
            f"connected as {me!r}: the schema {schema!r} and its tables must be created by the storage service "
            f"role {service_role!r} (--pg-user), otherwise the service cannot write into them"
        )
    return None


# ----------------------------------------------------------------------------- output
def table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    """Plain text table: columns of counts aligned right, the others left."""
    body = [[str(c) for c in row] for row in rows]
    cells = [[str(h) for h in headers], *body]
    widths = [max(len(r[i]) for r in cells) for i in range(len(headers))]
    right = [bool(body) and all(r[i].split(" ")[0].isdigit() for r in body) for i in range(len(headers))]
    return "\n".join(
        "  ".join(
            c.rjust(w) if r else c.ljust(w) for c, w, r in zip(row, widths, right, strict=True)
        ).rstrip()
        for row in cells
    )


def format_survey(rows: Sequence[SurveyRow], sources: Sequence[str]) -> str:
    headers = ["type"]
    for name in sources:
        headers += [f"{name} entities", f"{name} events"]
    headers += ["keys", "in both"]
    body = []
    for r in rows:
        line: list[Any] = [r.entity_type]
        for name in sources:
            line += [r.entities.get(name, 0), r.events.get(name, 0)]
        body.append([*line, r.keys, r.both])
    return table(headers, body)


def format_migration(report: MigrationReport, show: int = DEFAULT_SHOW) -> str:
    headers = ["type", *SOURCES, "both", "events", *STATUSES, "repeated delivery", "failed keys"]
    body = []
    total = TypeReport()
    for entity_type, r in report.types.items():
        body.append(
            [
                entity_type,
                *(r.keys[o] for o in (*SOURCES, "both")),
                r.events,
                *(r.statuses[s] for s in STATUSES),
                f"{r.repeated_deliveries} ({r.differing_repeats} differ)",
                r.failed_keys,
            ]
        )
        total.keys.update(r.keys)
        total.events += r.events
        total.statuses.update(r.statuses)
        total.repeated_deliveries += r.repeated_deliveries
        total.differing_repeats += r.differing_repeats
        total.failed_keys += r.failed_keys
    body.append(
        [
            "total",
            *(total.keys[o] for o in (*SOURCES, "both")),
            total.events,
            *(total.statuses[s] for s in STATUSES),
            f"{total.repeated_deliveries} ({total.differing_repeats} differ)",
            total.failed_keys,
        ]
    )
    lines = [table(headers, body), f"keys: {sum(total.keys.values())}; time: {report.seconds:.1f}s"]
    if report.failures:
        lines.append(f"failed keys: {len(report.failures)} (first {min(show, len(report.failures))}):")
        lines += [f"  {f}" for f in report.failures[:show]]
    if report.stopped:
        lines.append("stopped early: too many failed keys (--max-failures); fix the cause and run again")
    lines.append("result: " + ("OK" if report.ok else "FAILED"))
    return "\n".join(lines)


def format_verify(report: VerifyReport, show: int = DEFAULT_SHOW) -> str:
    body = [
        [t, origin, *(c[col] for col in VERIFY_COLUMNS)]
        for (t, origin), c in report.rows.items()
        if c["keys"]
    ]
    lines = [table(["type", "origin", *VERIFY_COLUMNS], body)]
    if any(report.target_only.values()):
        only = ", ".join(f"{t} {n}" for t, n in report.target_only.items() if n)
        lines.append(f"target-only keys (no source has them, not compared): {only}")
    if report.projection:
        proj: list[list[Any]] = []
        examples: list[str] = []
        for entity_type, check in report.projection.items():
            if check is None:
                proj.append([entity_type, "-", "-", "-", "-", "layout unavailable"])
                continue
            result = "ok" if check.ok else "MISMATCH"
            proj.append([entity_type, check.states, check.rows, check.only_state, check.only_rows, result])
            if check.state_examples:
                examples.append(
                    f"  {entity_type}: state without such projection row: " + "; ".join(check.state_examples)
                )
            if check.row_examples:
                examples.append(
                    f"  {entity_type}: projection row without such state: " + "; ".join(check.row_examples)
                )
        headers = ["type", "states", "projection rows", "state only", "projection only", "result"]
        lines += ["projection (canonical_key, version):", table(headers, proj), *examples]
    else:
        lines.append("projection: not checked (--skip-projection)")
    if report.problems:
        lines.append(f"discrepancies: {len(report.problems)} (first {min(show, len(report.problems))}):")
        lines += [f"  {p}" for p in report.problems[:show]]
    if report.changed:
        lines.append(f"changed after the migration (live writes, not errors): {len(report.changed)}")
        lines += [f"  {p}" for p in report.changed[:show]]
    lines.append("result: " + ("OK" if report.ok else "FAILED"))
    return "\n".join(lines)


# ----------------------------------------------------------------------------- settings
@dataclass(frozen=True)
class Endpoint:
    host: str
    port: int
    database: str
    user: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class Settings:
    pg: Endpoint | None
    mongo: Endpoint | None
    sources: tuple[str, ...]
    types: tuple[str, ...]


def _types(value: str) -> tuple[str, ...]:
    names = tuple(dict.fromkeys(v.strip() for v in value.split(",") if v.strip()))
    unknown = [n for n in names if n not in NEWS_TYPES]
    if not names or unknown:
        raise argparse.ArgumentTypeError(f"types must be a comma-separated subset of {', '.join(NEWS_TYPES)}")
    return names


def _positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return number


def _schema(value: str) -> str:
    if not _IDENT.match(value):
        raise argparse.ArgumentTypeError("must match ^[a-z_][a-z0-9_]{0,62}$")
    return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="migrate_news_to_pg",
        description="Move article/post/news_article/news_event from MongoDB and the old results-pg into the "
        "PostgreSQL news layout (docs/delivery/news-pg.md).",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="only count entities and events; write nothing")
    mode.add_argument(
        "--verify", action="store_true", help="compare the target with the sources; write nothing"
    )
    p.add_argument(
        "--stack", default=DEFAULT_STACK, help="project of .jane/stack-<project>.json (default %(default)s)"
    )
    p.add_argument("--stack-file", type=Path, help="explicit stack file (instead of --stack)")
    p.add_argument("--source", choices=("all", *SOURCES), default="all", help="sources to read (default all)")
    p.add_argument(
        "--types", type=_types, default=NEWS_TYPES, help="comma-separated entity types (default: all four)"
    )
    p.add_argument(
        "--target-schema", type=_schema, default="news", help="target schema (default %(default)s)"
    )
    p.add_argument(
        "--source-schema", type=_schema, default="public", help="schema of results-pg (default %(default)s)"
    )
    p.add_argument(
        "--batch-size", type=_positive, default=DEFAULT_BATCH_SIZE, help="page size (default %(default)s)"
    )
    p.add_argument(
        "--concurrency",
        type=_positive,
        default=DEFAULT_CONCURRENCY,
        help="keys at a time (default %(default)s)",
    )
    p.add_argument(
        "--progress-every", type=int, default=DEFAULT_PROGRESS_EVERY, help="keys per progress line (0: none)"
    )
    p.add_argument(
        "--max-failures", type=_positive, default=DEFAULT_MAX_FAILURES, help="failed keys before stopping"
    )
    p.add_argument("--skip-projection", action="store_true", help="--verify without the projection check")
    p.add_argument(
        "--examples",
        type=_positive,
        default=DEFAULT_SHOW,
        help="failed keys / discrepancies / projection pairs printed per list (default %(default)s)",
    )
    p.add_argument(
        "--service-role", default=SERVICE_ROLE, help="role of the storage service that owns the schema"
    )
    pg = p.add_argument_group("PostgreSQL (results-pg and the target)")
    pg.add_argument("--pg-host")
    pg.add_argument("--pg-port", type=int)
    pg.add_argument("--pg-database", default=DEFAULT_PG_DATABASE)
    pg.add_argument("--pg-user", default=SERVICE_ROLE)
    pg.add_argument(
        "--pg-password-env",
        default=DEFAULT_PG_PASSWORD_ENV,
        help="environment variable (or stack file env entry) with the password (default %(default)s)",
    )
    pg.add_argument("--sslmode", default="disable")
    mongo = p.add_argument_group("MongoDB (results-mongo)")
    mongo.add_argument("--mongo-host")
    mongo.add_argument("--mongo-port", type=int)
    mongo.add_argument("--mongo-database", default=DEFAULT_MONGO_DATABASE)
    mongo.add_argument("--mongo-user", help="default: JANE_MONGO_USER of the stack file")
    mongo.add_argument("--mongo-password-env", default=DEFAULT_MONGO_PASSWORD_ENV)
    return p


def load_stack_file(args: argparse.Namespace) -> dict[str, Any]:
    """The stack file, or ``{}`` when there is none (explicit options and environment must then suffice)."""
    path: Path = args.stack_file or Path(__file__).resolve().parents[1] / ".jane" / f"stack-{args.stack}.json"
    if not path.is_file():
        if args.stack_file is not None:
            raise ConfigError(f"stack file {path} not found")
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _secret(var: str, stack_env: Mapping[str, Any]) -> str | None:
    value = os.environ.get(var) or stack_env.get(var)
    return str(value) if value else None


def resolve_settings(args: argparse.Namespace) -> Settings:
    sources = SOURCES if args.source == "all" else (args.source,)
    if args.target_schema == args.source_schema and "legacy-pg" in sources:
        raise ConfigError("--target-schema must differ from --source-schema")
    stack = load_stack_file(args)
    services: Mapping[str, Any] = stack.get("services") or {}
    env: Mapping[str, Any] = stack.get("env") or {}
    need_pg = "legacy-pg" in sources or not args.dry_run
    pg = mongo = None
    if need_pg:
        info = services.get("postgres") or {}
        host, port = args.pg_host or info.get("host"), args.pg_port or info.get("port")
        password = _secret(args.pg_password_env, env)
        if not host or not port:
            raise ConfigError("PostgreSQL address unknown: no stack file entry, pass --pg-host/--pg-port")
        if password is None:
            raise ConfigError(
                f"PostgreSQL password: set {args.pg_password_env} (environment or stack file env)"
            )
        pg = Endpoint(str(host), int(port), args.pg_database, args.pg_user, password)
    if "mongo" in sources:
        info = services.get("mongodb") or {}
        host, port = args.mongo_host or info.get("host"), args.mongo_port or info.get("port")
        user = args.mongo_user or env.get("JANE_MONGO_USER") or info.get("user")
        password = _secret(args.mongo_password_env, env)
        if not host or not port or not user:
            raise ConfigError(
                "MongoDB address/user unknown: no stack file entry, pass --mongo-host/--mongo-port/--mongo-user"
            )
        if password is None:
            raise ConfigError(
                f"MongoDB password: set {args.mongo_password_env} (environment or stack file env)"
            )
        mongo = Endpoint(str(host), int(port), args.mongo_database, str(user), password)
    return Settings(pg=pg, mongo=mongo, sources=sources, types=tuple(args.types))


def pg_connection(
    ep: Endpoint, schema: str, *, connection_id: str, sslmode: str, layout: str | None = None
) -> ResolvedConnection:
    params: dict[str, Any] = {
        "host": ep.host,
        "port": ep.port,
        "database": ep.database,
        "schema": schema,
        "sslmode": sslmode,
    }
    if layout is not None:
        params["layout"] = layout
    return ResolvedConnection(
        connection_id=connection_id,
        kind="postgresql",
        params=params,
        secrets={"username": ep.user, "password": ep.password},
    )


def mongo_connection(ep: Endpoint) -> ResolvedConnection:
    return ResolvedConnection(
        connection_id=MONGO_CONNECTION_ID,
        kind="mongodb",
        params={"host": ep.host, "port": ep.port, "database": ep.database, "auth_source": "admin"},
        secrets={"username": ep.user, "password": ep.password},
    )


# ----------------------------------------------------------------------------- main
async def run(args: argparse.Namespace, cfg: Settings) -> int:
    pool = {"pool_min_size": 1, "pool_max_size": args.concurrency}
    opened: list[StorageAdapter] = []
    try:
        sources: dict[str, StorageAdapter] = {}
        if "legacy-pg" in cfg.sources:
            assert cfg.pg is not None
            legacy = PostgresAdapter()
            await legacy.open(
                pg_connection(
                    cfg.pg, args.source_schema, connection_id=LEGACY_CONNECTION_ID, sslmode=args.sslmode
                ),
                pool,
            )
            opened.append(legacy)
            sources["legacy-pg"] = legacy
        if "mongo" in cfg.sources:
            assert cfg.mongo is not None
            mongo = MongoAdapter()
            await mongo.open(mongo_connection(cfg.mongo), {"pool_max_size": args.concurrency})
            opened.append(mongo)
            sources["mongo"] = mongo
        where = f"types {','.join(cfg.types)}; sources {','.join(sources)}"
        if args.dry_run:
            print(f"dry run ({where}): nothing is written", flush=True)
            rows = await survey(sources, cfg.types, args.batch_size)
            print(format_survey(rows, list(sources)))
            return 0
        assert cfg.pg is not None
        target = PostgresAdapter()
        await target.open(
            pg_connection(
                cfg.pg,
                args.target_schema,
                connection_id=TARGET_CONNECTION_ID,
                sslmode=args.sslmode,
                layout=TARGET_LAYOUT,
            ),
            pool,
        )
        opened.append(target)
        target_name = f"{cfg.pg.database}.{args.target_schema} (layout {TARGET_LAYOUT})"
        if args.verify:
            print(f"verify ({where}; target {target_name}): nothing is written", flush=True)
            checker = (
                None
                if args.skip_projection
                else postgres_projection_checker(target, args.target_schema, args.examples)
            )
            report = await verify(
                sources,
                target,
                types=cfg.types,
                batch_size=args.batch_size,
                concurrency=args.concurrency,
                projection=checker,
            )
            print(format_verify(report, args.examples))
            return 0 if report.ok else 1
        problem = await schema_owner_problem(target, args.target_schema, args.service_role)
        if problem:
            print(f"error: {problem}", file=sys.stderr)
            return 2
        print(f"migrate ({where}; target {target_name})", flush=True)
        result = await migrate(
            sources,
            target,
            types=cfg.types,
            batch_size=args.batch_size,
            concurrency=args.concurrency,
            progress_every=args.progress_every,
            max_failures=args.max_failures,
            out=lambda line: print(line, flush=True),
        )
        problem = await schema_owner_problem(target, args.target_schema, args.service_role)
        if problem:
            print(f"error: {problem}", file=sys.stderr)
            return 2
        print(format_migration(result, args.examples))
        return 0 if result.ok else 1
    except AdapterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        for adapter in reversed(opened):
            await adapter.close()


async def amain(argv: Sequence[str] | None = None) -> int:
    """The command line in a running event loop; exit code 0 ok, 1 failures/discrepancies, 2 settings."""
    args = build_parser().parse_args(argv)
    try:
        cfg = resolve_settings(args)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return await run(args, cfg)


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    return asyncio.run(amain(argv))


if __name__ == "__main__":
    sys.exit(main())
