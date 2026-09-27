"""PostgreSQL adapter of the Jane storage handler (``kind: postgresql``, asyncpg).

Tables in ``<schema>`` with ``<table_prefix>`` (default ``jane_``):

| Table | Content |
|---|---|
| ``<p>entities`` | current state: ``(entity_type, canonical_key)`` PK, ``fields``/``field_orders``/``cleared_fields`` jsonb, ``version`` |
| ``<p>entity_history`` | one row per accepted update (also stale): PK ``(entity_type, canonical_key, version)`` |
| ``<p>deliveries`` | ``delivery_key`` PK + acknowledged writes (jsonb) — kept forever (ADR-0008) |
| ``<p>objects`` | RAW / result documents: bytes in ``content`` (bytea), media type, sha256, Material metadata |

``commit_entity`` is one transaction: ``INSERT … ON CONFLICT DO NOTHING`` into deliveries (nothing
inserted → ``DUPLICATE``), compare-and-swap of the snapshot (``UPDATE … WHERE version = $expected`` or
``INSERT … ON CONFLICT DO NOTHING`` for a new entity; nothing changed → ``CONFLICT``) and the history
insert — all or nothing. Connection parameters: ``host``, ``port``, ``database``, ``schema``,
``sslmode``; secrets ``username``, ``password`` (resolved by the core).
"""

# ruff: noqa: S608 - table names are built only from identifiers validated by _IDENT/_PREFIX; values are bound

from __future__ import annotations

import asyncio
import base64
import json
import re
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, NoReturn

import asyncpg  # type: ignore[import-untyped]

from jane_contracts.storage_adapter import (
    AdapterError,
    CommitOutcome,
    CommitResult,
    DeliveryRecord,
    EntitySnapshot,
    HistoryEvent,
    ObjectRecord,
    RawObject,
    ResolvedConnection,
)
from jane_storage.codec import entity_ack, order_from_json, order_to_json, parse_ts, utcnow
from jane_storage.keys import object_id_for

__all__ = ["DEFAULT_OPTIONS", "PostgresAdapter", "package_dir"]

DEFAULT_OPTIONS: dict[str, int] = {
    "pool_min_size": 1,
    "pool_max_size": 10,
    "connect_timeout_ms": 10_000,
    "command_timeout_ms": 30_000,
}
"""Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``)."""

_IDENT = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
_PREFIX = re.compile(r"^[a-z_][a-z0-9_]{0,30}$|^$")
_RETRYABLE = (
    OSError,
    TimeoutError,
    asyncio.TimeoutError,
    asyncpg.PostgresConnectionError,
    asyncpg.InterfaceError,
    asyncpg.CannotConnectNowError,
    asyncpg.TooManyConnectionsError,
    asyncpg.SerializationError,
    asyncpg.DeadlockDetectedError,
    asyncpg.QueryCanceledError,
    asyncpg.AdminShutdownError,
)


def package_dir() -> Path:
    """Directory of the ``jane.storage-postgresql`` storage package (entry point ``jane.storage.packages``)."""
    return Path(__file__).parent / "package"


def _fail(exc: BaseException) -> NoReturn:
    if isinstance(exc, AdapterError):
        raise exc
    retryable = isinstance(exc, _RETRYABLE) and not isinstance(
        exc, asyncpg.InvalidAuthorizationSpecificationError | asyncpg.InvalidPasswordError
    )
    raise AdapterError(f"postgresql: {type(exc).__name__}: {exc}", retryable=retryable) from exc


def _cursor(value: Any) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def _uncursor(cursor: str) -> Any:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    except ValueError as exc:
        raise AdapterError(f"invalid cursor: {exc}", retryable=False) from exc


class _Outcome(Exception):
    def __init__(self, outcome: CommitOutcome) -> None:
        super().__init__(outcome.value)
        self.outcome = outcome


async def _init_connection(con: asyncpg.Connection) -> None:
    await con.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


class PostgresAdapter:
    kind: ClassVar[str] = "postgresql"
    capabilities: ClassVar[frozenset[str]] = frozenset({"objects", "entities", "history"})

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None
        self._schema = "public"
        self._prefix = "jane_"

    # ------------------------------------------------------------------ helpers
    def _t(self, name: str) -> str:
        return f'"{self._schema}"."{self._prefix}{name}"'

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise AdapterError("adapter is not open", retryable=False)
        return self._pool

    @asynccontextmanager
    async def _con(self) -> AsyncIterator[asyncpg.Connection]:
        try:
            async with self.pool.acquire() as con:
                yield con
        except (asyncpg.PostgresError, OSError, TimeoutError, asyncpg.InterfaceError) as exc:
            _fail(exc)

    # ------------------------------------------------------------------ lifecycle
    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        params = dict(connection.params)
        merged = dict(DEFAULT_OPTIONS)
        for name in DEFAULT_OPTIONS:
            if name in params:
                merged[name] = int(params[name])
            if name in options:
                merged[name] = int(options[name])
        schema = str(options.get("schema") or params.get("schema") or "public")
        prefix = str(options.get("table_prefix", params.get("table_prefix", "jane_")))
        if not _IDENT.match(schema) or not _PREFIX.match(prefix):
            raise AdapterError(f"invalid schema {schema!r} or table_prefix {prefix!r}", retryable=False)
        self._schema, self._prefix = schema, prefix
        ssl = params.get("sslmode", "prefer")
        try:
            self._pool = await asyncpg.create_pool(
                host=params.get("host", "localhost"),
                port=int(params.get("port", 5432)),
                database=params.get("database"),
                user=connection.secrets.get("username"),
                password=connection.secrets.get("password"),
                ssl=None if ssl == "disable" else ssl,
                min_size=merged["pool_min_size"],
                max_size=merged["pool_max_size"],
                timeout=merged["connect_timeout_ms"] / 1000,
                command_timeout=merged["command_timeout_ms"] / 1000,
                init=_init_connection,
            )
        except (asyncpg.PostgresError, OSError, TimeoutError, asyncpg.InterfaceError) as exc:
            _fail(exc)

    async def close(self) -> None:
        if self._pool is not None:
            pool, self._pool = self._pool, None
            await pool.close()

    async def health(self) -> bool:
        try:
            async with self._con() as con:
                return bool(await con.fetchval("SELECT 1") == 1)
        except AdapterError:
            return False

    async def ensure_schema(self, entity_types: Sequence[str]) -> None:
        async with self._con() as con, con.transaction():
            await con.execute("SELECT pg_advisory_xact_lock(hashtext($1))", f"{self._schema}.{self._prefix}")
            await con.execute(f'CREATE SCHEMA IF NOT EXISTS "{self._schema}"')
            await con.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self._t("entities")} (
                    entity_type text NOT NULL,
                    canonical_key text NOT NULL,
                    scope text NOT NULL,
                    key jsonb NOT NULL,
                    fields jsonb NOT NULL,
                    field_orders jsonb NOT NULL,
                    cleared_fields jsonb NOT NULL,
                    version integer NOT NULL,
                    updated_at timestamptz NOT NULL,
                    PRIMARY KEY (entity_type, canonical_key)
                );
                CREATE INDEX IF NOT EXISTS "{self._prefix}entities_scope"
                    ON {self._t("entities")} (entity_type, scope, canonical_key COLLATE "C");
                CREATE TABLE IF NOT EXISTS {self._t("entity_history")} (
                    entity_type text NOT NULL,
                    canonical_key text NOT NULL,
                    version integer NOT NULL,
                    record jsonb NOT NULL,
                    delivery_key text NOT NULL,
                    received_at timestamptz NOT NULL,
                    applied_fields jsonb NOT NULL,
                    stale_fields jsonb NOT NULL,
                    PRIMARY KEY (entity_type, canonical_key, version)
                );
                CREATE TABLE IF NOT EXISTS {self._t("deliveries")} (
                    delivery_key text PRIMARY KEY,
                    recorded_at timestamptz NOT NULL,
                    acks jsonb NOT NULL
                );
                CREATE TABLE IF NOT EXISTS {self._t("objects")} (
                    object_id text PRIMARY KEY,
                    object_key text NOT NULL UNIQUE,
                    media_type text NOT NULL,
                    size_bytes bigint NOT NULL,
                    sha256 text NOT NULL,
                    stored_at timestamptz NOT NULL,
                    source_id text,
                    material_id text,
                    observation_id text,
                    format text NOT NULL,
                    metadata jsonb NOT NULL,
                    content bytea NOT NULL
                );
                CREATE INDEX IF NOT EXISTS "{self._prefix}objects_stored"
                    ON {self._t("objects")} (stored_at, object_id);
                """
            )

    # ------------------------------------------------------------------ objects
    def _object(self, row: Mapping[str, Any]) -> ObjectRecord:
        return ObjectRecord(
            object_id=row["object_id"],
            object_key=row["object_key"],
            locator={"table": f"{self._schema}.{self._prefix}objects", "id": row["object_id"]},
            media_type=row["media_type"],
            size_bytes=int(row["size_bytes"]),
            sha256=row["sha256"],
            stored_at=row["stored_at"],
            metadata=dict(row["metadata"]),
        )

    _OBJECT_COLUMNS = "object_id, object_key, media_type, size_bytes, sha256, stored_at, metadata"

    async def put_object(self, obj: RawObject) -> ObjectRecord:
        object_id = object_id_for(obj.object_key)
        metadata = {
            **dict(obj.metadata),
            "material_id": obj.material_id,
            "observation_id": obj.observation_id,
            "source_id": obj.source_id,
            "format": obj.format,
        }
        async with self._con() as con:
            row = await con.fetchrow(
                f"""INSERT INTO {self._t("objects")} (object_id, object_key, media_type, size_bytes, sha256,
                        stored_at, source_id, material_id, observation_id, format, metadata, content)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (object_key) DO NOTHING
                    RETURNING {self._OBJECT_COLUMNS}""",
                object_id,
                obj.object_key,
                obj.media_type,
                len(obj.content),
                obj.sha256,
                utcnow(),
                obj.source_id,
                obj.material_id,
                obj.observation_id,
                obj.format,
                metadata,
                obj.content,
            )
            if row is None:
                row = await con.fetchrow(
                    f"SELECT {self._OBJECT_COLUMNS} FROM {self._t('objects')} WHERE object_key = $1",
                    obj.object_key,
                )
        assert row is not None
        rec = self._object(row)
        if rec.sha256 != obj.sha256:
            raise AdapterError(
                f"object {obj.object_key!r} already stored with sha256 {rec.sha256}", retryable=False
            )
        return rec

    async def get_object(self, object_id: str) -> ObjectRecord | None:
        async with self._con() as con:
            row = await con.fetchrow(
                f"SELECT {self._OBJECT_COLUMNS} FROM {self._t('objects')} WHERE object_id = $1", object_id
            )
        return None if row is None else self._object(row)

    async def read_object_content(self, object_id: str) -> bytes:
        async with self._con() as con:
            data = await con.fetchval(
                f"SELECT content FROM {self._t('objects')} WHERE object_id = $1", object_id
            )
        if data is None:
            raise AdapterError(f"object {object_id} not found", retryable=False)
        return bytes(data)

    async def list_objects(
        self,
        *,
        source_id: str | None = None,
        material_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[ObjectRecord], str | None]:
        where, args = ["TRUE"], list[Any]()
        for column, op, value in (
            ("source_id", "=", source_id),
            ("material_id", "=", material_id),
            ("stored_at", ">=", since),
            ("stored_at", "<", until),
        ):
            if value is not None:
                args.append(value)
                where.append(f"{column} {op} ${len(args)}")
        if cursor is not None:
            stored_at, object_id = _uncursor(cursor)
            args += [parse_ts(stored_at), object_id]
            where.append(f"(stored_at, object_id) > (${len(args) - 1}, ${len(args)})")
        args.append(limit + 1)
        async with self._con() as con:
            rows = await con.fetch(
                f"""SELECT {self._OBJECT_COLUMNS} FROM {self._t("objects")} WHERE {" AND ".join(where)}
                    ORDER BY stored_at, object_id LIMIT ${len(args)}""",
                *args,
            )
        items = [self._object(r) for r in rows[:limit]]
        more = len(rows) > limit
        last = items[-1] if items else None
        next_cursor = _cursor([last.stored_at.isoformat(), last.object_id]) if more and last else None
        return items, next_cursor

    # ------------------------------------------------------------------ entities
    @staticmethod
    def _snapshot(row: Mapping[str, Any]) -> EntitySnapshot:
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

    _ENTITY_COLUMNS = (
        "entity_type, canonical_key, key, fields, field_orders, cleared_fields, version, updated_at"
    )

    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
        async with self._con() as con:
            row = await con.fetchrow(
                f"SELECT {self._ENTITY_COLUMNS} FROM {self._t('entities')} "
                "WHERE entity_type = $1 AND canonical_key = $2",
                entity_type,
                canonical_key,
            )
        return None if row is None else self._snapshot(row)

    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        orders = {k: order_to_json(v) for k, v in new.field_orders.items()}
        state = (
            new.entity_type,
            new.canonical_key,
            str(new.key.get("scope", "")),
            dict(new.key),
            dict(new.fields),
            orders,
            sorted(new.cleared_fields),
            new.version,
            new.updated_at,
        )
        try:
            async with self._con() as con, con.transaction():
                inserted = await con.fetchval(
                    f"""INSERT INTO {self._t("deliveries")} (delivery_key, recorded_at, acks) VALUES ($1, $2, $3)
                        ON CONFLICT (delivery_key) DO NOTHING RETURNING 1""",
                    event.delivery_key,
                    event.received_at,
                    [entity_ack(new, event)],
                )
                if inserted is None:
                    raise _Outcome(CommitOutcome.DUPLICATE)
                if expected_version is None:
                    changed = await con.fetchval(
                        f"""INSERT INTO {self._t("entities")} (entity_type, canonical_key, scope, key, fields,
                                field_orders, cleared_fields, version, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                            ON CONFLICT (entity_type, canonical_key) DO NOTHING RETURNING version""",
                        *state,
                    )
                else:
                    changed = await con.fetchval(
                        f"""UPDATE {self._t("entities")} SET scope = $3, key = $4, fields = $5, field_orders = $6,
                                cleared_fields = $7, version = $8, updated_at = $9
                            WHERE entity_type = $1 AND canonical_key = $2 AND version = $10
                            RETURNING version""",
                        *state,
                        expected_version,
                    )
                if changed is None:
                    raise _Outcome(CommitOutcome.CONFLICT)
                await con.execute(
                    f"""INSERT INTO {self._t("entity_history")} (entity_type, canonical_key, version, record,
                            delivery_key, received_at, applied_fields, stale_fields)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                    new.entity_type,
                    new.canonical_key,
                    new.version,
                    dict(event.record),
                    event.delivery_key,
                    event.received_at,
                    list(event.applied_fields),
                    list(event.stale_fields),
                )
        except _Outcome as rolled_back:
            return CommitResult(
                rolled_back.outcome, await self.read_entity(new.entity_type, new.canonical_key)
            )
        except asyncpg.UniqueViolationError as exc:  # racing history insert of the same version
            if exc.table_name and exc.table_name.endswith("entity_history"):
                return CommitResult(
                    CommitOutcome.CONFLICT, await self.read_entity(new.entity_type, new.canonical_key)
                )
            _fail(exc)
        return CommitResult(CommitOutcome.COMMITTED, new)

    async def list_entities(
        self,
        entity_type: str,
        *,
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]:
        where, args = ["entity_type = $1"], list[Any]([entity_type])
        if scope is not None:
            args.append(scope)
            where.append(f"scope = ${len(args)}")
        if updated_since is not None:
            args.append(updated_since)
            where.append(f"updated_at >= ${len(args)}")
        if cursor is not None:
            args.append(str(_uncursor(cursor)))
            where.append(f'canonical_key COLLATE "C" > ${len(args)}')
        args.append(limit + 1)
        async with self._con() as con:
            rows = await con.fetch(
                f"""SELECT {self._ENTITY_COLUMNS} FROM {self._t("entities")} WHERE {" AND ".join(where)}
                    ORDER BY canonical_key COLLATE "C" LIMIT ${len(args)}""",
                *args,
            )
        items = [self._snapshot(r) for r in rows[:limit]]
        next_cursor = _cursor(items[-1].canonical_key) if len(rows) > limit and items else None
        return items, next_cursor

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]:
        args: list[Any] = [entity_type, canonical_key]
        where = "entity_type = $1 AND canonical_key = $2"
        if cursor is not None:
            args.append(int(_uncursor(cursor)))
            where += " AND version < $3"
        args.append(limit + 1)
        async with self._con() as con:
            rows = await con.fetch(
                f"""SELECT version, record, delivery_key, received_at, applied_fields, stale_fields
                    FROM {self._t("entity_history")} WHERE {where} ORDER BY version DESC LIMIT ${len(args)}""",
                *args,
            )
        items = [
            HistoryEvent(
                entity_type=entity_type,
                canonical_key=canonical_key,
                record=dict(r["record"]),
                delivery_key=r["delivery_key"],
                received_at=r["received_at"],
                applied_fields=list(r["applied_fields"]),
                stale_fields=list(r["stale_fields"]),
            )
            for r in rows[:limit]
        ]
        next_cursor = _cursor(int(rows[limit - 1]["version"])) if len(rows) > limit else None
        return items, next_cursor

    # ------------------------------------------------------------------ deliveries
    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        async with self._con() as con:
            row = await con.fetchrow(
                f"SELECT delivery_key, recorded_at, acks FROM {self._t('deliveries')} WHERE delivery_key = $1",
                delivery_key,
            )
        if row is None:
            return None
        return DeliveryRecord(
            delivery_key=row["delivery_key"], recorded_at=row["recorded_at"], acks=list(row["acks"])
        )

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        async with self._con() as con:
            inserted = await con.fetchval(
                f"""INSERT INTO {self._t("deliveries")} (delivery_key, recorded_at, acks) VALUES ($1, $2, $3)
                    ON CONFLICT (delivery_key) DO NOTHING RETURNING 1""",
                record.delivery_key,
                record.recorded_at,
                [dict(a) for a in record.acks],
            )
        return inserted is not None
