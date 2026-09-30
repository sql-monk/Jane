"""MongoDB adapter of the Jane storage handler (``kind: mongodb``, PyMongo ``AsyncMongoClient``).

Collections in ``params.database`` with ``<prefix>`` (default ``jane_``):

| Collection | Content |
|---|---|
| ``<p>entities`` | ``_id = <entity_type>|<sha256(canonical_key)>``, the ``EntitySnapshot`` document (+ ``pending``) |
| ``<p>entity_history`` | one ``HistoryEvent`` document per version (``_id = <entity_type>|<hash>|<version:012d>``) |
| ``<p>deliveries`` | ``_id = sha256(delivery_key)``, the ``DeliveryRecord`` document — kept forever |
| ``<p>objects`` | ``_id = object_id``, the ``ObjectRecord`` document (commit marker of an object) |
| ``<p>object_chunks`` | RAW bytes in chunks of ``chunk_bytes`` (``_id = <object_id>:<sha256>:<n>``) |

Multi-document transactions need a replica set; the adapter does not, so a standalone ``mongod`` works.
Atomicity of ``commit_entity`` comes from single-document operations:

1. the stored snapshot has the key in ``pending``, or ``deliveries`` has it → ``DUPLICATE`` (read in this
   order: the roll-forward inserts the delivery record before it drops ``pending``);
2. compare-and-swap of the snapshot document — ``replace_one({_id, version: expected})`` or
   ``insert_one`` for a new entity (duplicate ``_id`` → ``CONFLICT``). The replacement carries the
   history event and the delivery acknowledgement in ``pending``, so the snapshot write is the single
   commit point: state, version, history event and delivery key become visible together;
3. roll forward: insert the history event and the delivery record, then ``$unset`` ``pending``. A crash
   here loses nothing — ``get_delivery`` finds keys in ``pending`` (indexed), readers and the next commit
   roll a pending event forward first (all steps are idempotent).

Connection parameters: ``host``, ``port``, ``database``, ``auth_source`` (``admin``), ``tls``,
``replica_set``, ``direct_connection``, ``chunk_bytes``; secrets ``username``, ``password``.
"""

from __future__ import annotations

import base64
import contextlib
import json
import re
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from bson.errors import BSONError, InvalidDocument
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    ExecutionTimeout,
    OperationFailure,
    PyMongoError,
    WTimeoutError,
)

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
    entity_ack,
    event_from_json,
    event_to_json,
    format_ts,
    object_record_from_json,
    object_record_to_json,
    parse_ts,
    snapshot_from_json,
    snapshot_to_json,
    utcnow,
)
from jane_storage.keys import key_digest, object_id_for

__all__ = ["DEFAULT_OPTIONS", "MongoAdapter", "package_dir"]

DEFAULT_OPTIONS: dict[str, int] = {
    "pool_min_size": 0,
    "pool_max_size": 10,
    "connect_timeout_ms": 10_000,
    "command_timeout_ms": 30_000,
    "chunk_bytes": 4 * 1024 * 1024,
}
"""Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``chunk_bytes`` — size of one RAW chunk document (BSON documents are limited to 16 MiB)."""

MAX_CHUNK_BYTES = 15 * 1024 * 1024
_PREFIX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,40}$|^$")
_DATABASE = re.compile(r"^[A-Za-z0-9_-]{1,63}$")
_ENTITY_FIELDS = {"_id": 0, "pending": 0}
_AUTH_FAILED = 18
_NOT_RETRYABLE_CODES = {
    2,
    13,
    18,
    26,
    73,
}  # BadValue, Unauthorized, AuthenticationFailed, NamespaceNotFound, InvalidNamespace


def package_dir() -> Path:
    """Directory of the ``jane.storage-mongodb`` storage package (entry point ``jane.storage.packages``)."""
    return Path(__file__).parent / "package"


def _cursor(value: Any) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def _uncursor(cursor: str) -> Any:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    except ValueError as exc:
        raise AdapterError(f"invalid cursor: {exc}", retryable=False) from exc


@contextmanager
def _errors() -> Iterator[None]:
    """Map driver errors to ``AdapterError`` (``retryable`` for network, timeouts, transient server errors)."""
    try:
        yield
    except AdapterError:
        raise
    except (ConnectionFailure, ExecutionTimeout, WTimeoutError) as exc:
        raise AdapterError(f"mongodb: {type(exc).__name__}: {exc}", retryable=True) from exc
    except OperationFailure as exc:
        retryable = exc.code not in _NOT_RETRYABLE_CODES and (
            exc.has_error_label("RetryableWriteError") or exc.has_error_label("TransientTransactionError")
        )
        raise AdapterError(f"mongodb: {exc.code}: {exc}", retryable=retryable) from exc
    except (PyMongoError, BSONError, InvalidDocument, OverflowError) as exc:
        raise AdapterError(f"mongodb: {type(exc).__name__}: {exc}", retryable=False) from exc


class MongoAdapter:
    kind: ClassVar[str] = "mongodb"
    capabilities: ClassVar[frozenset[str]] = frozenset({"objects", "entities", "history"})

    def __init__(self) -> None:
        self._client: AsyncMongoClient[dict[str, Any]] | None = None
        self._db_name = "jane"
        self._prefix = "jane_"
        self._chunk = DEFAULT_OPTIONS["chunk_bytes"]

    # ------------------------------------------------------------------ helpers
    def _col(self, name: str) -> AsyncCollection[dict[str, Any]]:
        if self._client is None:
            raise AdapterError("adapter is not open", retryable=False)
        return self._client[self._db_name][f"{self._prefix}{name}"]

    @staticmethod
    def _entity_id(entity_type: str, canonical_key: str) -> str:
        return f"{entity_type}|{key_digest(canonical_key)}"

    @staticmethod
    def _history_id(entity_type: str, canonical_key: str, version: int) -> str:
        return f"{entity_type}|{key_digest(canonical_key)}|{version:012d}"

    # ------------------------------------------------------------------ lifecycle
    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        params = dict(connection.params)
        merged = dict(DEFAULT_OPTIONS)
        for name in DEFAULT_OPTIONS:
            for layer in (params, options):
                if name in layer:
                    merged[name] = int(layer[name])
        database = str(params.get("database") or "jane")
        prefix = str(options.get("prefix", params.get("prefix", "jane_")))
        if not _DATABASE.match(database) or not _PREFIX.match(prefix):
            raise AdapterError(f"invalid database {database!r} or prefix {prefix!r}", retryable=False)
        if not 1 <= merged["chunk_bytes"] <= MAX_CHUNK_BYTES:
            raise AdapterError(f"chunk_bytes must be 1..{MAX_CHUNK_BYTES}", retryable=False)
        kwargs: dict[str, Any] = {
            "host": str(params.get("host", "localhost")),
            "port": int(params.get("port", 27017)),
            "tz_aware": True,
            "appname": "jane-storage",
            "serverSelectionTimeoutMS": merged["connect_timeout_ms"],
            "connectTimeoutMS": merged["connect_timeout_ms"],
            "socketTimeoutMS": merged["command_timeout_ms"],
            "maxPoolSize": max(1, merged["pool_max_size"]),
            "minPoolSize": max(0, merged["pool_min_size"]),
            "tls": bool(params.get("tls", False)),
        }
        if connection.secrets.get("username"):
            kwargs["username"] = connection.secrets["username"]
            kwargs["password"] = connection.secrets.get("password", "")
            kwargs["authSource"] = str(params.get("auth_source", "admin"))
        if params.get("replica_set"):
            kwargs["replicaSet"] = str(params["replica_set"])
        if "direct_connection" in params:
            kwargs["directConnection"] = bool(params["direct_connection"])
        with _errors():
            self._client = AsyncMongoClient(**kwargs)
        self._db_name, self._prefix, self._chunk = database, prefix, merged["chunk_bytes"]

    async def close(self) -> None:
        client, self._client = self._client, None
        if client is not None:
            await client.close()

    async def health(self) -> bool:
        if self._client is None:
            return False
        try:
            with _errors():
                reply = await self._client.admin.command("ping")
        except AdapterError:
            return False
        return bool(reply.get("ok"))

    async def ensure_schema(self, entity_types: Sequence[str]) -> None:
        with _errors():
            await self._col("entities").create_index([("entity_type", ASCENDING), ("_id", ASCENDING)])
            await self._col("entities").create_index(
                [("entity_type", ASCENDING), ("key.scope", ASCENDING), ("_id", ASCENDING)]
            )
            await self._col("entities").create_index(
                [("pending.delivery_key", ASCENDING)], partialFilterExpression={"pending": {"$exists": True}}
            )
            await self._col("entity_history").create_index(
                [("entity_type", ASCENDING), ("key_hash", ASCENDING), ("version", DESCENDING)], unique=True
            )
            await self._col("objects").create_index([("stored_at", ASCENDING), ("_id", ASCENDING)])
            await self._col("object_chunks").create_index(
                [("object_id", ASCENDING), ("sha256", ASCENDING), ("n", ASCENDING)]
            )

    # ------------------------------------------------------------------ objects
    def _chunk_id(self, object_id: str, sha256: str, n: int) -> str:
        return f"{object_id}:{sha256}:{n:08d}"

    async def put_object(self, obj: RawObject) -> ObjectRecord:
        object_id = object_id_for(obj.object_key)
        objects, chunks = self._col("objects"), self._col("object_chunks")
        with _errors():
            existing = await objects.find_one({"_id": object_id})
            if existing is None:
                parts = [
                    obj.content[i : i + self._chunk] for i in range(0, len(obj.content), self._chunk)
                ] or [b""]
                for n, part in enumerate(parts):
                    chunk_id = self._chunk_id(object_id, obj.sha256, n)
                    doc = {
                        "_id": chunk_id,
                        "object_id": object_id,
                        "sha256": obj.sha256,
                        "n": n,
                        "data": part,
                    }
                    await chunks.replace_one({"_id": chunk_id}, doc, upsert=True)
                rec = ObjectRecord(
                    object_id=object_id,
                    object_key=obj.object_key,
                    locator={"collection": f"{self._prefix}objects", "id": object_id},
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
                try:
                    await objects.insert_one(
                        {"_id": object_id, **object_record_to_json(rec), "chunks": len(parts)}
                    )
                    return rec
                except DuplicateKeyError:  # a concurrent writer of the same key won
                    existing = await objects.find_one({"_id": object_id})
                    if existing is None:
                        raise AdapterError(f"object {object_id} vanished", retryable=True) from None
                    if existing["sha256"] != obj.sha256:
                        await chunks.delete_many({"object_id": object_id, "sha256": obj.sha256})
        rec = object_record_from_json(existing)
        if rec.sha256 != obj.sha256:
            raise AdapterError(
                f"object {obj.object_key!r} already stored with sha256 {rec.sha256}", retryable=False
            )
        return rec

    async def get_object(self, object_id: str) -> ObjectRecord | None:
        with _errors():
            doc = await self._col("objects").find_one({"_id": object_id})
        return None if doc is None else object_record_from_json(doc)

    async def read_object_content(self, object_id: str) -> bytes:
        with _errors():
            doc = await self._col("objects").find_one({"_id": object_id})
            if doc is None:
                raise AdapterError(f"object {object_id} not found", retryable=False)
            parts = [
                bytes(c["data"])
                async for c in self._col("object_chunks")
                .find({"object_id": object_id, "sha256": doc["sha256"]})
                .sort("n", ASCENDING)
            ]
        if len(parts) != int(doc.get("chunks", len(parts))):
            raise AdapterError(
                f"object {object_id}: {len(parts)} of {doc['chunks']} chunks found", retryable=False
            )
        return b"".join(parts)

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
        query: dict[str, Any] = {}
        if source_id is not None:
            query["metadata.source_id"] = source_id
        if material_id is not None:
            query["metadata.material_id"] = material_id
        stored: dict[str, str] = {}
        if since is not None:
            stored["$gte"] = format_ts(since)
        if until is not None:
            stored["$lt"] = format_ts(until)
        if stored:
            query["stored_at"] = stored
        if cursor is not None:
            at, oid = _uncursor(cursor)
            query["$or"] = [{"stored_at": {"$gt": at}}, {"stored_at": at, "_id": {"$gt": oid}}]
        with _errors():
            docs = (
                await self._col("objects")
                .find(query)
                .sort([("stored_at", ASCENDING), ("_id", ASCENDING)])
                .limit(limit + 1)
                .to_list()
            )
        items = [object_record_from_json(d) for d in docs[:limit]]
        next_cursor = (
            _cursor([docs[limit - 1]["stored_at"], docs[limit - 1]["_id"]])
            if len(docs) > limit and limit > 0
            else None
        )
        return items, next_cursor

    # ------------------------------------------------------------------ entities
    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
        with _errors():
            doc = await self._col("entities").find_one(
                {"_id": self._entity_id(entity_type, canonical_key)}, _ENTITY_FIELDS
            )
        return None if doc is None else snapshot_from_json(doc)

    async def _roll_forward(self, doc: Mapping[str, Any]) -> None:
        """Make the pending history event and delivery record of a snapshot durable; idempotent."""
        pending = doc.get("pending")
        if not isinstance(pending, Mapping):
            return
        event, ack = dict(pending["event"]), dict(pending["ack"])
        version = int(pending["version"])
        etype, ckey = str(doc["entity_type"]), str(doc["canonical_key"])
        with contextlib.suppress(DuplicateKeyError):
            await self._col("entity_history").insert_one(
                {"_id": self._history_id(etype, ckey, version), "key_hash": key_digest(ckey), **event}
            )
        record = DeliveryRecord(
            delivery_key=str(pending["delivery_key"]), recorded_at=parse_ts(event["received_at"]), acks=[ack]
        )
        with contextlib.suppress(DuplicateKeyError):
            await self._col("deliveries").insert_one(
                {"_id": key_digest(record.delivery_key), **delivery_to_json(record)}
            )
        await self._col("entities").update_one(
            {"_id": doc["_id"], "version": version, "pending.delivery_key": record.delivery_key},
            {"$unset": {"pending": ""}},
        )

    async def _delivery_doc(self, delivery_key: str) -> dict[str, Any] | None:
        doc = await self._col("deliveries").find_one({"_id": key_digest(delivery_key)})
        return doc if doc is not None and doc.get("delivery_key") == delivery_key else None

    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        entities = self._col("entities")
        eid = self._entity_id(new.entity_type, new.canonical_key)
        with _errors():
            # Order matters: the snapshot first, then ``deliveries``. The roll-forward inserts the delivery
            # record before it drops ``pending``, so a key committed by another instance is always seen in
            # one of the two reads (the reverse order has a window where it is in neither).
            current = await entities.find_one({"_id": eid})
            pending = None if current is None else current.get("pending")
            if isinstance(pending, Mapping) and pending.get("delivery_key") == event.delivery_key:
                assert current is not None
                return CommitResult(CommitOutcome.DUPLICATE, snapshot_from_json(current))
            if await self._delivery_doc(event.delivery_key) is not None:
                return CommitResult(
                    CommitOutcome.DUPLICATE, await self.read_entity(new.entity_type, new.canonical_key)
                )
            if current is not None and isinstance(current.get("pending"), Mapping):
                await self._roll_forward(current)
            current_version = None if current is None else int(current["version"])
            if current_version != expected_version:
                return CommitResult(
                    CommitOutcome.CONFLICT, None if current is None else snapshot_from_json(current)
                )
            doc = {
                "_id": eid,
                **snapshot_to_json(new),
                "pending": {
                    "version": new.version,
                    "delivery_key": event.delivery_key,
                    "event": event_to_json(event, new.version),
                    "ack": entity_ack(new, event),
                },
            }
            if expected_version is None:
                try:
                    await entities.insert_one(doc)
                except DuplicateKeyError:
                    return CommitResult(
                        CommitOutcome.CONFLICT, await self.read_entity(new.entity_type, new.canonical_key)
                    )
            else:
                result = await entities.replace_one({"_id": eid, "version": expected_version}, doc)
                if result.matched_count == 0:
                    return CommitResult(
                        CommitOutcome.CONFLICT, await self.read_entity(new.entity_type, new.canonical_key)
                    )
        with contextlib.suppress(AdapterError), _errors():
            await self._roll_forward(doc)  # committed; rolling forward now only saves readers the work
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
        query: dict[str, Any] = {"entity_type": entity_type}
        if scope is not None:
            query["key.scope"] = scope
        if updated_since is not None:
            query["updated_at"] = {"$gte": format_ts(updated_since)}
        if cursor is not None:
            query["_id"] = {"$gt": str(_uncursor(cursor))}
        with _errors():
            docs = (
                await self._col("entities")
                .find(query, {"pending": 0})
                .sort("_id", ASCENDING)
                .limit(limit + 1)
                .to_list()
            )
        items = [snapshot_from_json(d) for d in docs[:limit]]
        next_cursor = _cursor(docs[limit - 1]["_id"]) if len(docs) > limit and limit > 0 else None
        return items, next_cursor

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]:
        with _errors():
            current = await self._col("entities").find_one(
                {"_id": self._entity_id(entity_type, canonical_key)}
            )
            if current is None:
                return [], None
            await self._roll_forward(current)
            version: dict[str, int] = {"$lte": int(current["version"])}
            if cursor is not None:
                version["$lt"] = int(_uncursor(cursor))
            docs = (
                await self._col("entity_history")
                .find({"entity_type": entity_type, "key_hash": key_digest(canonical_key), "version": version})
                .sort("version", DESCENDING)
                .limit(limit + 1)
                .to_list()
            )
        items = [event_from_json(d) for d in docs[:limit]]
        next_cursor = _cursor(int(docs[limit - 1]["version"])) if len(docs) > limit and limit > 0 else None
        return items, next_cursor

    # ------------------------------------------------------------------ deliveries
    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        with _errors():
            # pending first, then deliveries: see the comment in commit_entity
            pending = await self._col("entities").find_one({"pending.delivery_key": delivery_key})
            if pending is None:
                doc = await self._delivery_doc(delivery_key)
                return None if doc is None else delivery_from_json(doc)
        with contextlib.suppress(AdapterError), _errors():
            await self._roll_forward(
                pending
            )  # committed, not rolled forward yet (crash or commit in progress)
        event = pending["pending"]["event"]
        return DeliveryRecord(
            delivery_key=delivery_key,
            recorded_at=parse_ts(event["received_at"]),
            acks=[pending["pending"]["ack"]],
        )

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        with _errors():
            try:
                await self._col("deliveries").insert_one(
                    {"_id": key_digest(record.delivery_key), **delivery_to_json(record)}
                )
            except DuplicateKeyError:
                return False
        return True
