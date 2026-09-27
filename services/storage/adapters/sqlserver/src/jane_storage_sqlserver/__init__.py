"""SQL Server adapter of the Jane storage handler (``kind: sqlserver``, pymssql / FreeTDS).

Tables in ``<schema>`` (default ``dbo``) with ``<table_prefix>`` (default ``jane_``):

| Table | Content |
|---|---|
| ``<p>entities`` | current state: PK ``(entity_type, key_hash)``, ``doc`` = ``EntitySnapshot`` JSON (nvarchar(max)), ``version`` |
| ``<p>entity_history`` | one row per accepted update (also stale): PK ``(entity_type, key_hash, version)`` |
| ``<p>deliveries`` | PK ``delivery_hash`` + ``delivery_key`` + acknowledged writes (JSON) — kept forever (ADR-0008) |
| ``<p>objects`` | RAW / result documents: ``content`` varbinary(max), ``meta`` = ``ObjectRecord`` JSON |

Keys (canonical key, delivery key, object key) have no length limit, so indexes use their sha256
(``key_hash``, ``delivery_hash``) — SQL Server index keys are limited to 900/1700 bytes. Timestamps are
stored as fixed-width RFC 3339 UTC strings (``jane_storage.codec.format_ts``): they sort chronologically
and keep microseconds on any TDS version.

``commit_entity`` is one T-SQL batch in one transaction (``XACT_ABORT ON``): insert the delivery row (a
duplicate key → ``DUPLICATE``), compare-and-swap of the snapshot (``UPDATE … WHERE version = @expected``
or ``INSERT`` for a new entity; nothing changed or a duplicate key → ``CONFLICT``) and the history insert
— all or nothing. A deadlock victim (1205) is reported as ``CONFLICT``: nothing was written and the
core retries. ``ensure_schema`` is idempotent and serialised with ``sp_getapplock``.

Connection parameters: ``host``, ``port``, ``database``, ``schema``, ``encryption`` (FreeTDS:
``off`` | ``request`` | ``require``), ``tds_version``; secrets ``username``, ``password``.
"""

# ruff: noqa: S608 - table names are built only from identifiers validated by _IDENT/_PREFIX; values are bound

from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, NoReturn, TypeVar

import pymssql

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
from jane_storage.codec import (
    delivery_from_json,
    delivery_to_json,
    dumps,
    entity_ack,
    event_from_json,
    event_to_json,
    format_ts,
    loads,
    object_record_from_json,
    object_record_to_json,
    snapshot_from_json,
    snapshot_to_json,
    utcnow,
)
from jane_storage.keys import key_digest, object_id_for

__all__ = ["DEFAULT_OPTIONS", "SqlServerAdapter", "package_dir"]

T = TypeVar("T")

DEFAULT_OPTIONS: dict[str, int] = {
    "pool_min_size": 1,
    "pool_max_size": 10,
    "connect_timeout_ms": 10_000,
    "command_timeout_ms": 30_000,
    "lock_timeout_ms": 30_000,
}
"""Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``lock_timeout_ms`` bounds the wait for the ``ensure_schema`` application lock."""

_IDENT = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
_PREFIX = re.compile(r"^[a-z_][a-z0-9_]{0,30}$|^$")
_DATABASE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_NOT_RETRYABLE = {
    18456,  # login failed
    4060,  # cannot open database
    229,  # permission denied
    262,  # permission denied in database
    208,  # invalid object name
}
_OUTCOMES = {0: CommitOutcome.COMMITTED, 1: CommitOutcome.DUPLICATE, 2: CommitOutcome.CONFLICT}


def package_dir() -> Path:
    """Directory of the ``jane.storage-sqlserver`` storage package (entry point ``jane.storage.packages``)."""
    return Path(__file__).parent / "package"


def _cursor(value: Any) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def _uncursor(cursor: str) -> Any:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    except ValueError as exc:
        raise AdapterError(f"invalid cursor: {exc}", retryable=False) from exc


def _error_number(exc: BaseException) -> int | None:
    args = exc.args
    first = args[0] if args else None
    if isinstance(first, tuple) and first:
        first = first[0]
    return first if isinstance(first, int) else None


def _fail(exc: BaseException) -> NoReturn:
    if isinstance(exc, AdapterError):
        raise exc
    number = _error_number(exc)
    retryable = isinstance(exc, pymssql.OperationalError | pymssql.InterfaceError | OSError | TimeoutError)
    if number in _NOT_RETRYABLE:
        retryable = False
    if number in {1205, -2}:  # deadlock victim, timeout
        retryable = True
    raise AdapterError(f"sqlserver: {type(exc).__name__}: {number}: {exc}", retryable=retryable) from exc


def _short(value: str) -> str:
    """A value for a hashed index column: sha256 of it."""
    return key_digest(value)


class _Pool:
    """A small pool of pymssql connections; every call runs in a worker thread (pymssql is blocking)."""

    def __init__(self, connect: Callable[[], Any], max_size: int) -> None:
        self._connect = connect
        self._idle: list[Any] = []
        self._slots = asyncio.Semaphore(max_size)

    async def warm(self, count: int) -> None:
        for _ in range(count):
            self._idle.append(await asyncio.to_thread(self._connect))

    async def run(self, fn: Callable[[Any], T]) -> T:
        async with self._slots:
            con = self._idle.pop() if self._idle else None
            try:
                if con is None:
                    con = await asyncio.to_thread(self._connect)
                result = await asyncio.to_thread(fn, con)
            except BaseException:
                if con is not None:  # the connection state is unknown after an error
                    with contextlib.suppress(Exception):
                        con.close()
                raise
            self._idle.append(con)
            return result

    def close(self) -> None:
        idle, self._idle = self._idle, []
        for con in idle:
            with contextlib.suppress(Exception):
                con.close()


class SqlServerAdapter:
    kind: ClassVar[str] = "sqlserver"
    capabilities: ClassVar[frozenset[str]] = frozenset({"objects", "entities", "history"})

    def __init__(self) -> None:
        self._pool: _Pool | None = None
        self._schema = "dbo"
        self._prefix = "jane_"
        self._lock_timeout_ms = DEFAULT_OPTIONS["lock_timeout_ms"]

    # ------------------------------------------------------------------ helpers
    def _t(self, name: str) -> str:
        return f"[{self._schema}].[{self._prefix}{name}]"

    async def _run(self, fn: Callable[[Any], T]) -> T:
        if self._pool is None:
            raise AdapterError("adapter is not open", retryable=False)
        try:
            return await self._pool.run(fn)
        except AdapterError:
            raise
        except (pymssql.Error, OSError, TimeoutError) as exc:
            _fail(exc)

    @staticmethod
    def _rows(con: Any, sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        with con.cursor(as_dict=True) as cur:
            cur.execute(sql, dict(params) if params else None)
            return list(cur.fetchall()) if cur.description else []

    # ------------------------------------------------------------------ lifecycle
    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        params = dict(connection.params)
        merged = dict(DEFAULT_OPTIONS)
        for name in DEFAULT_OPTIONS:
            for layer in (params, options):
                if name in layer:
                    merged[name] = int(layer[name])
        schema = str(options.get("schema") or params.get("schema") or "dbo")
        prefix = str(options.get("table_prefix", params.get("table_prefix", "jane_")))
        database = str(params.get("database") or "")
        if not _IDENT.match(schema) or not _PREFIX.match(prefix) or not _DATABASE.match(database):
            raise AdapterError(
                f"invalid database {database!r}, schema {schema!r} or table_prefix {prefix!r}",
                retryable=False,
            )
        kwargs: dict[str, Any] = {
            "server": str(params.get("host", "localhost")),
            "port": str(int(params.get("port", 1433))),
            "user": connection.secrets.get("username"),
            "password": connection.secrets.get("password"),
            "database": database,
            "login_timeout": max(1, round(merged["connect_timeout_ms"] / 1000)),
            "timeout": max(1, round(merged["command_timeout_ms"] / 1000)),
            "appname": "jane-storage",
            "charset": "UTF-8",
            "autocommit": True,
            "tds_version": str(params.get("tds_version", "7.4")),
        }
        if params.get("encryption"):
            kwargs["encryption"] = str(params["encryption"])

        def connect() -> Any:
            return pymssql.connect(**kwargs)

        self._schema, self._prefix = schema, prefix
        self._lock_timeout_ms = merged["lock_timeout_ms"]
        pool = _Pool(connect, max(1, merged["pool_max_size"]))
        try:
            await pool.warm(max(0, min(merged["pool_min_size"], merged["pool_max_size"])))
        except (pymssql.Error, OSError, TimeoutError) as exc:
            pool.close()
            _fail(exc)
        self._pool = pool

    async def close(self) -> None:
        pool, self._pool = self._pool, None
        if pool is not None:
            await asyncio.to_thread(pool.close)

    async def health(self) -> bool:
        try:
            rows = await self._run(lambda con: self._rows(con, "SELECT 1 AS ok"))
        except AdapterError:
            return False
        return bool(rows and rows[0]["ok"] == 1)

    async def ensure_schema(self, entity_types: Sequence[str]) -> None:
        s, p = self._schema, self._prefix
        bin2 = "COLLATE Latin1_General_100_BIN2"

        def table(name: str, ddl: str) -> str:
            return f"IF OBJECT_ID(N'{self._t(name)}', N'U') IS NULL CREATE TABLE {self._t(name)} ({ddl});\n"

        def index(name: str, tbl: str, columns: str) -> str:
            return (
                f"IF INDEXPROPERTY(OBJECT_ID(N'{self._t(tbl)}'), N'{name}', 'IndexID') IS NULL "
                f"CREATE INDEX [{name}] ON {self._t(tbl)} ({columns});\n"
            )

        sql = (
            "SET NOCOUNT ON; SET XACT_ABORT ON;\nBEGIN TRAN;\n"
            f"DECLARE @r int; EXEC @r = sp_getapplock @Resource = N'jane-storage:{s}.{p}', @LockMode = 'Exclusive', "
            f"@LockOwner = 'Transaction', @LockTimeout = {int(self._lock_timeout_ms)};\n"
            "IF @r < 0 THROW 50002, N'ensure_schema: application lock timeout', 1;\n"
            f"IF SCHEMA_ID(N'{s}') IS NULL EXEC(N'CREATE SCHEMA [{s}]');\n"
            + table(
                "entities",
                f"entity_type nvarchar(128) NOT NULL, key_hash char(64) {bin2} NOT NULL, "
                f"scope_hash char(64) {bin2} NOT NULL, canonical_key nvarchar(max) NOT NULL, version int NOT NULL, "
                f"updated_at char(27) {bin2} NOT NULL, doc nvarchar(max) NOT NULL, "
                f"CONSTRAINT [PK_{p}entities] PRIMARY KEY CLUSTERED (entity_type, key_hash)",
            )
            + index(f"IX_{p}entities_scope", "entities", "entity_type, scope_hash, key_hash")
            + table(
                "entity_history",
                f"entity_type nvarchar(128) NOT NULL, key_hash char(64) {bin2} NOT NULL, version int NOT NULL, "
                "delivery_key nvarchar(max) NOT NULL, doc nvarchar(max) NOT NULL, "
                f"CONSTRAINT [PK_{p}entity_history] PRIMARY KEY CLUSTERED (entity_type, key_hash, version)",
            )
            + table(
                "deliveries",
                f"delivery_hash char(64) {bin2} NOT NULL, delivery_key nvarchar(max) NOT NULL, "
                f"recorded_at char(27) {bin2} NOT NULL, doc nvarchar(max) NOT NULL, "
                f"CONSTRAINT [PK_{p}deliveries] PRIMARY KEY CLUSTERED (delivery_hash)",
            )
            + table(
                "objects",
                f"object_id varchar(64) {bin2} NOT NULL, object_key nvarchar(max) NOT NULL, "
                f"stored_at char(27) {bin2} NOT NULL, source_hash char(64) {bin2} NULL, "
                f"material_hash char(64) {bin2} NULL, sha256 char(64) {bin2} NOT NULL, size_bytes bigint NOT NULL, "
                "meta nvarchar(max) NOT NULL, content varbinary(max) NOT NULL, "
                f"CONSTRAINT [PK_{p}objects] PRIMARY KEY CLUSTERED (object_id)",
            )
            + index(f"IX_{p}objects_stored", "objects", "stored_at, object_id")
            + index(f"IX_{p}objects_material", "objects", "material_hash, stored_at, object_id")
            + "COMMIT TRAN;"
        )
        await self._run(lambda con: self._rows(con, sql))

    # ------------------------------------------------------------------ objects
    async def put_object(self, obj: RawObject) -> ObjectRecord:
        object_id = object_id_for(obj.object_key)
        select = f"SELECT meta FROM {self._t('objects')} WHERE object_id = %(id)s"

        def put(con: Any) -> dict[str, Any]:
            rows = self._rows(con, select, {"id": object_id})
            if rows:
                return dict(loads(rows[0]["meta"]))
            rec = ObjectRecord(
                object_id=object_id,
                object_key=obj.object_key,
                locator={"table": f"{self._schema}.{self._prefix}objects", "id": object_id},
                media_type=obj.media_type,
                size_bytes=len(obj.content),
                sha256=obj.sha256,
                stored_at=utcnow(),
                metadata={
                    **dict(obj.metadata),
                    "material_id": obj.material_id,
                    "observation_id": obj.observation_id,
                    "source_id": obj.source_id,
                    "stored_format": obj.format,
                },
            )
            doc = object_record_to_json(rec)
            sql = f"""SET NOCOUNT ON;
                BEGIN TRY
                    INSERT INTO {self._t("objects")} (object_id, object_key, stored_at, source_hash, material_hash,
                        sha256, size_bytes, meta, content)
                    VALUES (%(id)s, %(key)s, %(stored_at)s, %(source)s, %(material)s, %(sha)s, %(size)s, %(meta)s,
                        CONVERT(varbinary(max), %(content)s, 2));
                END TRY
                BEGIN CATCH
                    IF ERROR_NUMBER() NOT IN (2601, 2627) THROW;
                END CATCH
                {select};"""
            rows = self._rows(
                con,
                sql,
                {
                    "id": object_id,
                    "key": obj.object_key,
                    "stored_at": doc["stored_at"],
                    "source": None if obj.source_id is None else _short(obj.source_id),
                    "material": _short(obj.material_id),
                    "sha": obj.sha256,
                    "size": len(obj.content),
                    "meta": dumps(doc).decode("utf-8"),
                    "content": obj.content.hex(),  # pymssql binds bytes as a string literal
                },
            )
            return dict(loads(rows[0]["meta"]))

        rec = object_record_from_json(await self._run(put))
        if rec.sha256 != obj.sha256:
            raise AdapterError(
                f"object {obj.object_key!r} already stored with sha256 {rec.sha256}", retryable=False
            )
        return rec

    async def get_object(self, object_id: str) -> ObjectRecord | None:
        sql = f"SELECT meta FROM {self._t('objects')} WHERE object_id = %(id)s"
        rows = await self._run(lambda con: self._rows(con, sql, {"id": object_id}))
        return object_record_from_json(loads(rows[0]["meta"])) if rows else None

    async def read_object_content(self, object_id: str) -> bytes:
        sql = f"SELECT content FROM {self._t('objects')} WHERE object_id = %(id)s"
        rows = await self._run(lambda con: self._rows(con, sql, {"id": object_id}))
        if not rows:
            raise AdapterError(f"object {object_id} not found", retryable=False)
        return bytes(rows[0]["content"])

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
        where, args = ["1 = 1"], dict[str, Any](n=limit + 1)
        for column, op, name, value in (
            ("source_hash", "=", "source", None if source_id is None else _short(source_id)),
            ("material_hash", "=", "material", None if material_id is None else _short(material_id)),
            ("stored_at", ">=", "since", None if since is None else format_ts(since)),
            ("stored_at", "<", "until", None if until is None else format_ts(until)),
        ):
            if value is not None:
                args[name] = value
                where.append(f"{column} {op} %({name})s")
        if cursor is not None:
            args["c_at"], args["c_id"] = _uncursor(cursor)
            where.append("(stored_at > %(c_at)s OR (stored_at = %(c_at)s AND object_id > %(c_id)s))")
        sql = (
            f"SELECT TOP (%(n)s) meta FROM {self._t('objects')} WHERE {' AND '.join(where)} "
            "ORDER BY stored_at, object_id"
        )
        rows = await self._run(lambda con: self._rows(con, sql, args))
        records = [object_record_from_json(loads(r["meta"])) for r in rows]
        # hashed filters: confirm the values (a hash collision would only widen the scan)
        records = [
            r
            for r in records
            if (source_id is None or r.metadata.get("source_id") == source_id)
            and (material_id is None or r.metadata.get("material_id") == material_id)
        ]
        items = records[:limit]
        last = items[-1] if items else None
        more = len(rows) > limit
        next_cursor = _cursor([format_ts(last.stored_at), last.object_id]) if more and last else None
        return items, next_cursor

    # ------------------------------------------------------------------ entities
    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
        sql = f"SELECT doc FROM {self._t('entities')} WHERE entity_type = %(t)s AND key_hash = %(h)s"
        args = {"t": entity_type, "h": key_digest(canonical_key)}
        rows = await self._run(lambda con: self._rows(con, sql, args))
        return snapshot_from_json(loads(rows[0]["doc"])) if rows else None

    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        delivery = DeliveryRecord(
            delivery_key=event.delivery_key, recorded_at=event.received_at, acks=[entity_ack(new, event)]
        )
        snapshot = snapshot_to_json(new)
        args = {
            "dh": key_digest(event.delivery_key),
            "dk": event.delivery_key,
            "recorded": format_ts(event.received_at),
            "ddoc": dumps(delivery_to_json(delivery)).decode("utf-8"),
            "t": new.entity_type,
            "h": key_digest(new.canonical_key),
            "sh": _short(str(new.key.get("scope", ""))),
            "ck": new.canonical_key,
            "version": new.version,
            "expected": expected_version,
            "updated": snapshot["updated_at"],
            "doc": dumps(snapshot).decode("utf-8"),
            "hdoc": dumps(event_to_json(event, new.version)).decode("utf-8"),
        }
        entities, history, deliveries = self._t("entities"), self._t("entity_history"), self._t("deliveries")
        sql = f"""SET NOCOUNT ON; SET XACT_ABORT ON;
            DECLARE @stage int = 0, @err int;
            BEGIN TRY
                BEGIN TRAN;
                SET @stage = 1;
                INSERT INTO {deliveries} (delivery_hash, delivery_key, recorded_at, doc)
                    VALUES (%(dh)s, %(dk)s, %(recorded)s, %(ddoc)s);
                SET @stage = 2;
                IF %(expected)s IS NULL
                    INSERT INTO {entities} (entity_type, key_hash, scope_hash, canonical_key, version, updated_at, doc)
                        VALUES (%(t)s, %(h)s, %(sh)s, %(ck)s, %(version)s, %(updated)s, %(doc)s);
                ELSE
                BEGIN
                    UPDATE {entities} SET scope_hash = %(sh)s, canonical_key = %(ck)s, version = %(version)s,
                            updated_at = %(updated)s, doc = %(doc)s
                        WHERE entity_type = %(t)s AND key_hash = %(h)s AND version = %(expected)s;
                    IF @@ROWCOUNT = 0 THROW 50001, N'version conflict', 1;
                END
                SET @stage = 3;
                INSERT INTO {history} (entity_type, key_hash, version, delivery_key, doc)
                    VALUES (%(t)s, %(h)s, %(version)s, %(dk)s, %(hdoc)s);
                COMMIT TRAN;
                SELECT 0 AS outcome;
            END TRY
            BEGIN CATCH
                IF @@TRANCOUNT > 0 ROLLBACK TRAN;
                SET @err = ERROR_NUMBER();
                IF @err IN (2601, 2627) AND @stage = 1 SELECT 1 AS outcome;
                ELSE IF @err IN (2601, 2627, 50001, 1205) SELECT 2 AS outcome;
                ELSE THROW;
            END CATCH"""
        rows = await self._run(lambda con: self._rows(con, sql, args))
        outcome = _OUTCOMES[int(rows[0]["outcome"])]
        if outcome is CommitOutcome.COMMITTED:
            return CommitResult(outcome, new)
        return CommitResult(outcome, await self.read_entity(new.entity_type, new.canonical_key))

    async def list_entities(
        self,
        entity_type: str,
        *,
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]:
        where, args = ["entity_type = %(t)s"], dict[str, Any](t=entity_type, n=limit + 1)
        if scope is not None:
            args["sh"] = _short(scope)
            where.append("scope_hash = %(sh)s")
        if updated_since is not None:
            args["since"] = format_ts(updated_since)
            where.append("updated_at >= %(since)s")
        if cursor is not None:
            args["after"] = str(_uncursor(cursor))
            where.append("key_hash > %(after)s")
        sql = (
            f"SELECT TOP (%(n)s) key_hash, doc FROM {self._t('entities')} WHERE {' AND '.join(where)} "
            "ORDER BY key_hash"
        )
        rows = await self._run(lambda con: self._rows(con, sql, args))
        page = rows[:limit]
        items = [snapshot_from_json(loads(r["doc"])) for r in page]
        if scope is not None:
            items = [s for s in items if s.key.get("scope") == scope]
        next_cursor = _cursor(page[-1]["key_hash"]) if len(rows) > limit and page else None
        return items, next_cursor

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]:
        args: dict[str, Any] = {"t": entity_type, "h": key_digest(canonical_key), "n": limit + 1}
        where = "entity_type = %(t)s AND key_hash = %(h)s"
        if cursor is not None:
            args["before"] = int(_uncursor(cursor))
            where += " AND version < %(before)s"
        sql = f"SELECT TOP (%(n)s) version, doc FROM {self._t('entity_history')} WHERE {where} ORDER BY version DESC"
        rows = await self._run(lambda con: self._rows(con, sql, args))
        items = [event_from_json(loads(r["doc"])) for r in rows[:limit]]
        next_cursor = _cursor(int(rows[limit - 1]["version"])) if len(rows) > limit and limit > 0 else None
        return items, next_cursor

    # ------------------------------------------------------------------ deliveries
    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        sql = f"SELECT delivery_key, doc FROM {self._t('deliveries')} WHERE delivery_hash = %(dh)s"
        rows = await self._run(lambda con: self._rows(con, sql, {"dh": key_digest(delivery_key)}))
        if not rows or rows[0]["delivery_key"] != delivery_key:
            return None
        return delivery_from_json(loads(rows[0]["doc"]))

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        sql = f"""SET NOCOUNT ON;
            BEGIN TRY
                INSERT INTO {self._t("deliveries")} (delivery_hash, delivery_key, recorded_at, doc)
                    VALUES (%(dh)s, %(dk)s, %(recorded)s, %(doc)s);
                SELECT 1 AS inserted;
            END TRY
            BEGIN CATCH
                IF ERROR_NUMBER() NOT IN (2601, 2627) THROW;
                SELECT 0 AS inserted;
            END CATCH"""
        args = {
            "dh": key_digest(record.delivery_key),
            "dk": record.delivery_key,
            "recorded": format_ts(record.recorded_at),
            "doc": dumps(delivery_to_json(record)).decode("utf-8"),
        }
        rows = await self._run(lambda con: self._rows(con, sql, args))
        return bool(rows[0]["inserted"])
