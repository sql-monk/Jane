"""Relational layout ``news`` of the PostgreSQL adapter (connection parameter ``params.layout = "news"``).

The engine state (``<prefix>entities``, ``<prefix>entity_history``, ``<prefix>deliveries``,
``<prefix>objects``) stays the source of truth. On top of it ``commit_entity`` lays the snapshots of
``article``, ``post``, ``news_article`` and ``news_event`` out into normalized tables of the same schema
**in the same transaction**, right after a successful compare-and-swap, so the projection always matches
the state (design: ``docs/delivery/news-pg.md``, sections 2-3; reference: ``docs/components/storage/adapters.md``).

Public API (used by the adapter, the data transfer script and the CLI):

* :func:`map_snapshot` — pure mapping of a snapshot to rows (:class:`EntityRows`), no database;
* :func:`ensure_layout` — applies the numbered migrations (:data:`MIGRATIONS`) inside the caller's
  transaction and records them in ``<schema>.jane_layout_migrations``;
* :func:`write_projection` — writes the rows of one snapshot (inside the caller's transaction);
* :func:`rebuild` — clears the projection and lays every stored snapshot of the four types out again;
* CLI ``python -m jane_storage_postgres.news_layout rebuild …`` (see ``__main__``).

Write rules: the parent row is upserted by ``canonical_key``; child rows are deleted and inserted again;
dictionaries (``tag``, ``topic``, ``named_entity``) get ``INSERT … ON CONFLICT DO NOTHING`` in a fixed order
followed by a lookup, which is race-free under READ COMMITTED (the insert waits for a concurrent inserter of
the same name) and holds no row lock on the dictionary row until commit. ``source`` is inserted if absent before
the parent row (foreign key) and updated last, so the row lock on a source is held for the shortest time: the
newest snapshot (by ``updated_at``) sets the attributes it has, an older one only fills gaps, ``NULL`` never
overwrites a value, ``first_seen_at`` / ``last_seen_at`` only widen.
"""

# ruff: noqa: S608 - table names are fixed identifiers and the schema is validated by the adapter; values are bound

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import asyncpg  # type: ignore[import-untyped]

from jane_contracts.storage_adapter import AdapterError, EntitySnapshot
from jane_storage.codec import order_from_json

from .ddl import MIGRATIONS, MIGRATIONS_TABLE, PROJECTION_TABLES, VIEWS, migrations_table_sql
from .mapping import (
    PROJECTED_TYPES,
    EntityRows,
    EvidenceRow,
    MentionRow,
    SourceRow,
    map_snapshot,
    parse_timestamp,
)

__all__ = [
    "DEFAULT_REBUILD_BATCH_SIZE",
    "LAYOUT",
    "MIGRATIONS",
    "MIGRATIONS_TABLE",
    "PROJECTED_TYPES",
    "PROJECTION_TABLES",
    "SOURCE_TYPES",
    "VIEWS",
    "EntityRows",
    "EvidenceRow",
    "MentionRow",
    "SourceRow",
    "ensure_layout",
    "latest_version",
    "map_snapshot",
    "parse_timestamp",
    "rebuild",
    "write_projection",
]

LAYOUT = "news"
SOURCE_TYPES: tuple[str, ...] = ("article", "post", "news_article")
"""Types whose snapshots update ``source`` (``news_event.scope`` does not refer to a source)."""
DEFAULT_REBUILD_BATCH_SIZE = 500
"""Snapshots read per query by :func:`rebuild` (override: argument / CLI ``--batch-size``)."""


def latest_version() -> int:
    return MIGRATIONS[-1][0]


def _q(schema: str) -> str:
    return f'"{schema}"'


# ---------------------------------------------------------------------------------------------- migrations
async def ensure_layout(con: asyncpg.Connection, schema: str) -> list[int]:
    """Apply the missing migrations in the caller's transaction; returns the versions applied now.

    Serialized per schema by an advisory transaction lock (two adapters with different ``table_prefix``
    in one schema share the projection). A schema migrated by a newer adapter is refused.
    """
    await con.execute("SELECT pg_advisory_xact_lock(hashtext($1))", f"{schema}.jane_layout")
    await con.execute(migrations_table_sql(schema))
    rows = await con.fetch(f"SELECT version FROM {_q(schema)}.{MIGRATIONS_TABLE} WHERE layout = $1", LAYOUT)
    applied = {int(r["version"]) for r in rows}
    if applied and max(applied) > latest_version():
        raise AdapterError(
            f"postgresql: layout {LAYOUT!r} of schema {schema!r} is at version {max(applied)}, "
            f"this adapter knows versions up to {latest_version()}",
            retryable=False,
        )
    done: list[int] = []
    for version, statements in MIGRATIONS:
        if version in applied:
            continue
        await con.execute(statements.format(s=_q(schema)))
        await con.execute(
            f"INSERT INTO {_q(schema)}.{MIGRATIONS_TABLE} (layout, version, applied_at) VALUES ($1, $2, clock_timestamp())",
            LAYOUT,
            version,
        )
        done.append(version)
    return done


# ---------------------------------------------------------------------------------------------- writing
async def write_projection(con: asyncpg.Connection, schema: str, snapshot: EntitySnapshot) -> bool:
    """Lay ``snapshot`` out in the caller's transaction; ``False`` for a type the layout does not project."""
    rows = map_snapshot(snapshot)
    if rows is None:
        return False
    await _write(con, _q(schema), rows)
    return True


async def _write(con: asyncpg.Connection, s: str, rows: EntityRows) -> None:
    if rows.source is not None:
        await con.execute(
            f"""INSERT INTO {s}.source (source_id, kind, name, site, channel, first_seen_at, last_seen_at)
                VALUES ($1, $2, $3, $4, $5, $6, $6) ON CONFLICT (source_id) DO NOTHING""",
            *_source_args(rows.source),
        )
    parent_id, inserted = await _upsert_parent(con, s, rows)
    if rows.entity_type == "article":
        if not inserted:
            await con.execute(f"DELETE FROM {s}.article_tag WHERE article_id = $1", parent_id)
        await _dictionary_children(con, s, "article_tag", "article_id", parent_id, "tag", "tag_id", rows.tags)
    elif rows.entity_type == "post":
        if not inserted:
            await con.execute(f"DELETE FROM {s}.post_link WHERE post_id = $1", parent_id)
        if rows.links:
            await con.execute(
                f"""INSERT INTO {s}.post_link (post_id, position, url)
                    SELECT $1, p, u FROM unnest($2::integer[], $3::text[]) AS t(p, u)""",
                parent_id,
                [p for p, _ in rows.links],
                [u for _, u in rows.links],
            )
    elif rows.entity_type == "news_article":
        await _news_article_children(con, s, parent_id, inserted, rows)
    if rows.source is not None:
        await con.execute(_SOURCE_UPDATE.format(s=s), *_source_args(rows.source))


_SOURCE_UPDATE = """UPDATE {s}.source SET
    kind = CASE WHEN last_seen_at IS NULL OR $6 >= last_seen_at THEN COALESCE($2, kind) ELSE COALESCE(kind, $2) END,
    name = CASE WHEN last_seen_at IS NULL OR $6 >= last_seen_at THEN COALESCE($3, name) ELSE COALESCE(name, $3) END,
    site = CASE WHEN last_seen_at IS NULL OR $6 >= last_seen_at THEN COALESCE($4, site) ELSE COALESCE(site, $4) END,
    channel = CASE WHEN last_seen_at IS NULL OR $6 >= last_seen_at
        THEN COALESCE($5, channel) ELSE COALESCE(channel, $5) END,
    first_seen_at = LEAST(first_seen_at, $6),
    last_seen_at = GREATEST(last_seen_at, $6)
WHERE source_id = $1"""
"""Attributes of the source: the snapshot that is newest so far (``$6 = updated_at`` not older than
``last_seen_at``) sets every attribute it has; an older snapshot only fills an attribute that is still ``NULL``.
``NULL`` never overwrites a value. The expressions read the locked row, so under READ COMMITTED a concurrent
update makes PostgreSQL re-evaluate them on the newer row version: commits that finish out of clock order end
with the same values as commits in clock order (and as :func:`rebuild`, which lays snapshots out by
``updated_at``)."""


def _source_args(src: SourceRow) -> tuple[Any, ...]:
    return (src.source_id, src.kind, src.name, src.site, src.channel, src.seen_at)


async def _upsert_parent(con: asyncpg.Connection, s: str, rows: EntityRows) -> tuple[int, bool]:
    names = list(rows.columns)
    placeholders = ", ".join(f"${i}" for i in range(1, len(names) + 1))
    updates = ", ".join(f"{n} = EXCLUDED.{n}" for n in names if n != "canonical_key")
    row = await con.fetchrow(
        f"""INSERT INTO {s}.{rows.table} ({", ".join(names)}) VALUES ({placeholders})
            ON CONFLICT (canonical_key) DO UPDATE SET {updates}
            RETURNING {rows.id_column} AS id, (xmax = 0) AS inserted""",
        *rows.columns.values(),
    )
    assert row is not None
    return int(row["id"]), bool(row["inserted"])


async def _dictionary_ids(
    con: asyncpg.Connection, s: str, table: str, id_column: str, names: Sequence[str]
) -> dict[str, int]:
    """Ids of ``names`` in ``tag`` / ``topic``, inserting the missing ones (sorted: one lock order for all)."""
    wanted = sorted(set(names))
    if not wanted:
        return {}
    await con.execute(
        f"""INSERT INTO {s}.{table} (name) SELECT n FROM unnest($1::text[]) WITH ORDINALITY AS t(n, i)
            ORDER BY i ON CONFLICT (name) DO NOTHING""",
        wanted,
    )
    found = await con.fetch(
        f"SELECT {id_column} AS id, name FROM {s}.{table} WHERE name = ANY($1::text[])", wanted
    )
    ids = {r["name"]: int(r["id"]) for r in found}
    _check_found(table, wanted, ids)
    return ids


def _check_found(table: str, wanted: Sequence[Any], ids: dict[Any, int]) -> None:
    missing = [w for w in wanted if w not in ids]
    if missing:  # only possible if a row vanished between the insert and the lookup (a concurrent rebuild)
        raise AdapterError(
            f"postgresql: layout {LAYOUT!r}: {table} rows {missing[:3]!r} not found after insert",
            retryable=True,
        )


async def _dictionary_children(
    con: asyncpg.Connection,
    s: str,
    child: str,
    parent_column: str,
    parent_id: int,
    table: str,
    id_column: str,
    items: Sequence[tuple[int, str]],
) -> None:
    if not items:
        return
    ids = await _dictionary_ids(con, s, table, id_column, [name for _, name in items])
    await con.execute(
        f"""INSERT INTO {s}.{child} ({parent_column}, position, {id_column})
            SELECT $1, p, d FROM unnest($2::integer[], $3::bigint[]) AS t(p, d)""",
        parent_id,
        [p for p, _ in items],
        [ids[name] for _, name in items],
    )


_EVENT_COLUMNS = (
    "summary",
    "identity_confidence",
    "identity_specificity",
    "identity_kind",
    "event_date",
    "event_time",
    "primary_actor",
    "action",
    "object",
    "location",
    "country",
    "date_resolution_method",
    "date_resolution_quote",
    "date_resolution_reference_published_at",
)


async def _news_article_children(
    con: asyncpg.Connection, s: str, article_id: int, inserted: bool, rows: EntityRows
) -> None:
    if not inserted:
        for child in ("evidence", "news_article_mention", "news_article_topic", "news_article_location"):
            await con.execute(f"DELETE FROM {s}.{child} WHERE news_article_id = $1", article_id)
        await con.execute(f"DELETE FROM {s}.news_article_event WHERE news_article_id = $1", article_id)
    await _dictionary_children(
        con, s, "news_article_topic", "news_article_id", article_id, "topic", "topic_id", rows.topics
    )
    if rows.locations:
        await con.execute(
            f"""INSERT INTO {s}.news_article_location (news_article_id, position, name)
                SELECT $1, p, n FROM unnest($2::integer[], $3::text[]) AS t(p, n)""",
            article_id,
            [p for p, _ in rows.locations],
            [n for _, n in rows.locations],
        )
    if rows.event is not None:
        values = [rows.event[c] for c in _EVENT_COLUMNS]
        placeholders = ", ".join(f"${i}" for i in range(2, len(values) + 2))
        await con.execute(
            f"""INSERT INTO {s}.news_article_event (news_article_id, {", ".join(_EVENT_COLUMNS)})
                VALUES ($1, {placeholders})""",
            article_id,
            *values,
        )
    mention_ids = await _mentions(con, s, article_id, rows.mentions)
    if rows.evidence:
        await con.execute(
            f"""INSERT INTO {s}.evidence (news_article_id, subject, mention_id, position, quote, reason, attribution)
                SELECT $1, sub, m, p, q, r, a
                FROM unnest($2::text[], $3::bigint[], $4::integer[], $5::text[], $6::text[], $7::text[])
                    AS t(sub, m, p, q, r, a)""",
            article_id,
            [e.subject for e in rows.evidence],
            [None if e.mention_position is None else mention_ids[e.mention_position] for e in rows.evidence],
            [e.position for e in rows.evidence],
            [e.quote for e in rows.evidence],
            [e.reason for e in rows.evidence],
            [e.attribution for e in rows.evidence],
        )


async def _mentions(
    con: asyncpg.Connection, s: str, article_id: int, mentions: Sequence[MentionRow]
) -> dict[int, int]:
    """Insert the mentions; returns ``position -> mention_id``."""
    if not mentions:
        return {}
    keys = sorted(
        {(m.canonical_name, m.entity_kind) for m in mentions if m.canonical_name is not None},
        key=lambda k: (k[0], k[1] is None, k[1] or ""),
    )
    entity_ids: dict[tuple[str | None, str | None], int] = {}
    if keys:
        names, kinds = [k[0] for k in keys], [k[1] for k in keys]
        await con.execute(
            f"""INSERT INTO {s}.named_entity (canonical_name, entity_kind)
                SELECT c, k FROM unnest($1::text[], $2::text[]) WITH ORDINALITY AS t(c, k, i)
                ORDER BY i ON CONFLICT (canonical_name, entity_kind) DO NOTHING""",
            names,
            kinds,
        )
        found = await con.fetch(
            f"""SELECT n.named_entity_id AS id, n.canonical_name, n.entity_kind
                FROM {s}.named_entity AS n
                JOIN unnest($1::text[], $2::text[]) AS t(c, k)
                    ON n.canonical_name = t.c AND n.entity_kind IS NOT DISTINCT FROM t.k""",
            names,
            kinds,
        )
        entity_ids = {(r["canonical_name"], r["entity_kind"]): int(r["id"]) for r in found}
        _check_found("named_entity", keys, entity_ids)
    rows = await con.fetch(
        f"""INSERT INTO {s}.news_article_mention (news_article_id, position, named_entity_id, name, role, attitude,
                attitude_confidence, factual_impact)
            SELECT $1, p, e, n, r, a, c, f
            FROM unnest($2::integer[], $3::bigint[], $4::text[], $5::text[], $6::text[], $7::float8[], $8::text[])
                AS t(p, e, n, r, a, c, f)
            RETURNING position, mention_id""",
        article_id,
        [m.position for m in mentions],
        [
            None if m.canonical_name is None else entity_ids[(m.canonical_name, m.entity_kind)]
            for m in mentions
        ],
        [m.name for m in mentions],
        [m.role for m in mentions],
        [m.attitude for m in mentions],
        [m.attitude_confidence for m in mentions],
        [m.factual_impact for m in mentions],
    )
    return {int(r["position"]): int(r["mention_id"]) for r in rows}


# ---------------------------------------------------------------------------------------------- rebuild
async def rebuild(
    con: asyncpg.Connection,
    *,
    schema: str,
    table_prefix: str = "jane_",
    batch_size: int = DEFAULT_REBUILD_BATCH_SIZE,
) -> dict[str, int]:
    """Clear the projection and lay out every stored snapshot of the four types again; one transaction.

    Applies missing migrations first. Concurrent commits wait on the projection tables (``TRUNCATE``) and
    project their newer snapshots after this transaction. Snapshots are laid out in the order of
    ``(updated_at, entity_type, canonical_key)`` — the order in which the live projection saw them last — so
    the attributes of ``source`` come from the newest snapshot, as in the live projection. ``first_seen_at`` /
    ``last_seen_at`` are widened from the history (``received_at`` of a version = ``updated_at`` of its
    snapshot). ``batch_size`` is the cursor prefetch. Returns the number of snapshots per type.

    The result equals the live projection of the same writes except for: new surrogate ids; dictionary rows
    nothing refers to are gone; an attribute of ``source`` (``name``, ``kind``, ``site``, ``channel``) that
    only an *earlier version* of some entity had — its current snapshot no longer has the field (cleared,
    or a wrong type) — keeps that old value live but is taken from the newest current snapshot that has it
    (or is ``NULL``) after a rebuild, because a rebuild sees current snapshots only.
    """
    if batch_size < 1:
        raise AdapterError(f"rebuild batch_size must be >= 1, got {batch_size}", retryable=False)
    s = _q(schema)
    entities = f'{s}."{table_prefix}entities"'
    history = f'{s}."{table_prefix}entity_history"'
    counts = dict.fromkeys(sorted(PROJECTED_TYPES), 0)
    async with con.transaction():
        await con.execute("SELECT pg_advisory_xact_lock(hashtext($1))", f"{schema}.{table_prefix}")
        await ensure_layout(con, schema)
        await con.execute(f"TRUNCATE {', '.join(f'{s}.{t}' for t in PROJECTION_TABLES)} RESTART IDENTITY")
        snapshots = con.cursor(
            f"""SELECT entity_type, canonical_key, key, fields, field_orders, cleared_fields, version, updated_at
                FROM {entities} WHERE entity_type = ANY($1::text[])
                ORDER BY updated_at, entity_type, canonical_key""",
            sorted(PROJECTED_TYPES),
            prefetch=batch_size,
        )
        async for row in snapshots:
            snapshot = _snapshot(row)
            if await write_projection(con, schema, snapshot):
                counts[snapshot.entity_type] += 1
        await con.execute(
            f"""UPDATE {s}.source AS src
                SET first_seen_at = LEAST(src.first_seen_at, seen.first_seen),
                    last_seen_at = GREATEST(src.last_seen_at, seen.last_seen)
                FROM (
                    SELECT e.scope, min(h.received_at) AS first_seen, max(h.received_at) AS last_seen
                    FROM {history} AS h
                    JOIN {entities} AS e USING (entity_type, canonical_key)
                    WHERE h.entity_type = ANY($1::text[])
                    GROUP BY e.scope
                ) AS seen
                WHERE src.source_id = seen.scope""",
            list(SOURCE_TYPES),
        )
    return counts


def _snapshot(row: Any) -> EntitySnapshot:
    return EntitySnapshot(
        entity_type=row["entity_type"],
        canonical_key=row["canonical_key"],
        key=dict(row["key"]),
        fields=dict(row["fields"]),
        field_orders={k: order_from_json(v) for k, v in dict(row["field_orders"]).items()},
        cleared_fields=frozenset(row["cleared_fields"]),
        version=int(row["version"]),
        updated_at=row["updated_at"],
    )
