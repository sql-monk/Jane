"""MongoDB adapter of the Jane storage handler (``kind: mongodb``, PyMongo ``AsyncMongoClient``).

Layout in ``params.database`` with ``<prefix>`` (``params.prefix``, empty by default): one collection per entity
type, its history next to it, service collections apart.

* ``<prefix><entity_type>`` — current state: ``_id = sha256(canonical_key)``, the ``EntitySnapshot`` document,
  ``search_text`` (see search below) and ``pending`` while a commit is being rolled forward;
* ``<prefix><entity_type>.history`` — one ``HistoryEvent`` document per version
  (``_id = <sha256(canonical_key)>|<version:012d>``, ``key_hash``);
* ``<prefix>_deliveries`` — ``_id = sha256(delivery_key)``: the ``DeliveryRecord`` (kept forever, ADR-0008) or
  the intent of an entity commit (``intent = {entity_type, entity_id}``) until that commit is rolled forward;
* ``<prefix>_objects`` — ``_id = object_id``, the ``ObjectRecord`` document (commit marker of an object);
* ``<prefix>_object_chunks`` — RAW bytes in chunks of ``chunk_bytes`` (``_id = <object_id>:<sha256>:<n>``).

``entity_type`` matches ``^[a-z][a-z0-9_]{0,63}$``: it never starts with ``_`` and never contains ``.``, so with
any prefix a type collection collides neither with a service collection (``<prefix>_…``) nor with a history
collection (``<prefix>….history``). The namespace ``<prefix>*`` belongs to one connection: every collection
``<prefix><entity_type>`` is an entity type of the catalog. With the empty prefix that is the whole database;
connections may share a database only with prefixes none of which is the start of another one. The type
``system`` needs a non-empty prefix (MongoDB reserves ``system.*``, so ``system.history`` cannot exist).

Multi-document transactions need a replica set; the adapter does not, so a standalone ``mongod`` works.
Atomicity of ``commit_entity`` comes from single-document operations:

1. read the snapshot, then the delivery document of the key: the key in the snapshot's ``pending`` or a delivery
   record → ``DUPLICATE`` (in this order: the roll-forward writes the delivery record before it drops
   ``pending``, so a key committed by another instance is seen in one of the two reads);
2. roll forward a ``pending`` left by an earlier commit of the entity; ``version`` differs → ``CONFLICT``;
3. write the intent ``{_id: sha256(delivery_key), delivery_key, intent: {entity_type, entity_id}}`` to
   ``_deliveries``: inserted, or replacing another intent of the key (a crashed or concurrent attempt points to
   the same snapshot); a delivery record already there → ``DUPLICATE``. The intent commits nothing: it only names
   the one snapshot document that can hold the key in ``pending``;
4. compare-and-swap of the snapshot — ``replace_one({_id, version: expected})`` or ``insert_one`` for a new entity
   (duplicate ``_id`` → ``CONFLICT``). The document carries the history event and the delivery acknowledgement in
   ``pending``, so this write is the single commit point: state, version, history event and delivery key become
   visible together;
5. roll forward: insert the history event, replace the intent with the delivery record, ``$unset`` ``pending``.
   A crash here loses nothing: ``get_delivery``, readers of the history and the next commit of the entity
   finish the roll-forward first (every step is idempotent).

``get_delivery`` never scans the type collections: it reads ``_deliveries`` by ``_id``. A delivery record is the
answer. An intent leads to one snapshot: the key in its ``pending`` means committed (rolled forward on the spot);
otherwise the delivery document is read once more — a roll-forward may have replaced the intent between the two
reads — and an intent that is still there means "not committed": a commit in progress or one that crashed before
its compare-and-swap; the next attempt with the key replaces it.

Indexes of a type collection are created by its first write in the process (cached per adapter instance) and by
``ensure_schema`` for the types it is given: ``canonical_key`` (order and cursor of lists and search),
``key.scope`` + ``canonical_key``, ``updated_at``, ``pending.delivery_key`` (partial: commits not yet rolled
forward); history: unique ``key_hash`` + ``version``.

Catalog and search (``EntityDiscoveryAdapter``): types come from the collection names of the namespace, with exact
counts (``key.scope`` filter optional), types without entities are left out. Search is a literal, case-insensitive
substring match on the server, before pagination: ``search_text`` holds ``casefold()`` of the JSON of
``canonical_key``, ``key`` and ``fields`` (the same text the core matches for an exact key) and the filter is
``$indexOfBytes`` of the casefolded term as a ``$literal`` — there is no pattern language, so regex
metacharacters, ``%`` and ``_`` match only themselves.

Statistics (``StorageStatisticsAdapter``): objects — count and the sum of ``size_bytes`` of ``_objects``; entities —
exact counts per type and ``storageSize + totalIndexSize`` of the type collections (``$collStats``; history,
deliveries and objects excluded); each collection is counted at its own moment, without a common snapshot.

Connection parameters: ``host``, ``port``, ``database``, ``prefix``, ``auth_source`` (``admin``), ``tls``,
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
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient, IndexModel
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
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

__all__ = ["DEFAULT_OPTIONS", "SIZE_BASIS", "MongoAdapter", "package_dir"]

DEFAULT_OPTIONS: dict[str, int] = {
    "pool_min_size": 0,
    "pool_max_size": 10,
    "connect_timeout_ms": 10_000,
    "command_timeout_ms": 30_000,
    "chunk_bytes": 4 * 1024 * 1024,
}
"""Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``chunk_bytes`` — size of one RAW chunk document (BSON documents are limited to 16 MiB)."""

SIZE_BASIS = "mongodb_collections_with_indexes"
"""``entity_statistics().size_basis``: ``storageSize + totalIndexSize`` of the type collections (current states)."""

MAX_CHUNK_BYTES = 15 * 1024 * 1024
_PREFIX = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]{0,40})?")
_DATABASE = re.compile(r"[A-Za-z0-9_-]{1,63}")
_ENTITY_TYPE = re.compile(r"[a-z][a-z0-9_]{0,63}")
_ENTITY_FIELDS = {"_id": 0, "pending": 0, "search_text": 0}
_NO_SEARCH_TEXT = {"search_text": 0}
_NAMESPACE_NOT_FOUND = 26
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


def _search_text(snap: EntitySnapshot) -> str:
    """What ``search_entities`` matches: the text the core builds for an exact-key search, casefolded."""
    doc = {"canonical_key": snap.canonical_key, "key": dict(snap.key), "fields": dict(snap.fields)}
    return json.dumps(doc, ensure_ascii=False, default=str).casefold()


def _is_intent(doc: Mapping[str, Any]) -> bool:
    return isinstance(doc.get("intent"), Mapping)


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
    """Fixed by the contract; catalog, search and statistics are the optional protocols
    ``EntityDiscoveryAdapter`` and ``StorageStatisticsAdapter`` (detected by their methods)."""

    def __init__(self) -> None:
        self._client: AsyncMongoClient[dict[str, Any]] | None = None
        self._db_name = "jane"
        self._prefix = ""
        self._chunk = DEFAULT_OPTIONS["chunk_bytes"]
        self._indexed: set[str] = set()
        """Entity types whose collections got their indexes in this process."""

    # ------------------------------------------------------------------ helpers
    def _db(self) -> AsyncDatabase[dict[str, Any]]:
        if self._client is None:
            raise AdapterError("adapter is not open", retryable=False)
        return self._client[self._db_name]

    def _svc(self, name: str) -> AsyncCollection[dict[str, Any]]:
        """Service collection ``<prefix>_<name>`` (deliveries, objects, object_chunks)."""
        return self._db()[f"{self._prefix}_{name}"]

    def _usable_type(self, entity_type: str) -> bool:
        if not _ENTITY_TYPE.fullmatch(entity_type):
            return False
        return bool(self._prefix) or entity_type != "system"  # system.* is reserved by MongoDB

    def _require_type(self, entity_type: str) -> None:
        if not self._usable_type(entity_type):
            raise AdapterError(
                f"entity_type {entity_type!r} has no collection: it must match ^[a-z][a-z0-9_]{{0,63}}$ "
                "('system' only with a non-empty prefix)",
                retryable=False,
            )

    def _type_col(self, entity_type: str) -> AsyncCollection[dict[str, Any]]:
        self._require_type(entity_type)
        return self._db()[f"{self._prefix}{entity_type}"]

    def _history_col(self, entity_type: str) -> AsyncCollection[dict[str, Any]]:
        self._require_type(entity_type)
        return self._db()[f"{self._prefix}{entity_type}.history"]

    @staticmethod
    def _history_id(key_hash: str, version: int) -> str:
        return f"{key_hash}|{version:012d}"

    async def _ensure_type(self, entity_type: str) -> None:
        """Indexes of a type collection and its history; once per type and adapter instance."""
        if entity_type in self._indexed:
            return
        await self._type_col(entity_type).create_indexes(
            [
                IndexModel([("canonical_key", ASCENDING)]),
                IndexModel([("key.scope", ASCENDING), ("canonical_key", ASCENDING)]),
                IndexModel([("updated_at", ASCENDING)]),
                IndexModel(
                    [("pending.delivery_key", ASCENDING)],
                    partialFilterExpression={"pending": {"$exists": True}},
                ),
            ]
        )
        await self._history_col(entity_type).create_indexes(
            [IndexModel([("key_hash", ASCENDING), ("version", DESCENDING)], unique=True)]
        )
        self._indexed.add(entity_type)

    async def _type_names(self) -> list[str]:
        """Entity types of this namespace (type collections, without service and history ones), sorted."""
        prefix = self._prefix
        names = await self._db().list_collection_names(
            filter={"type": "collection", "name": {"$regex": f"^{re.escape(prefix)}[a-z]"}}
        )
        return sorted(
            name[len(prefix) :]
            for name in names
            if name.startswith(prefix) and self._usable_type(name[len(prefix) :])
        )

    # ------------------------------------------------------------------ lifecycle
    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        params = dict(connection.params)
        merged = dict(DEFAULT_OPTIONS)
        for name in DEFAULT_OPTIONS:
            for layer in (params, options):
                if name in layer:
                    merged[name] = int(layer[name])
        database = str(params.get("database") or "jane")
        prefix = str(options.get("prefix", params.get("prefix", "")))
        if not _DATABASE.fullmatch(database) or not _PREFIX.fullmatch(prefix):
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
        self._indexed = set()

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
        for entity_type in entity_types:
            self._require_type(entity_type)
        with _errors():
            await self._svc("objects").create_index([("stored_at", ASCENDING), ("_id", ASCENDING)])
            await self._svc("object_chunks").create_index(
                [("object_id", ASCENDING), ("sha256", ASCENDING), ("n", ASCENDING)]
            )
            for entity_type in entity_types:
                await self._ensure_type(entity_type)

    # ------------------------------------------------------------------ objects
    def _chunk_id(self, object_id: str, sha256: str, n: int) -> str:
        return f"{object_id}:{sha256}:{n:08d}"

    async def put_object(self, obj: RawObject) -> ObjectRecord:
        object_id = object_id_for(obj.object_key)
        objects, chunks = self._svc("objects"), self._svc("object_chunks")
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
                    locator={"collection": objects.name, "id": object_id},
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
            doc = await self._svc("objects").find_one({"_id": object_id})
        return None if doc is None else object_record_from_json(doc)

    async def read_object_content(self, object_id: str) -> bytes:
        with _errors():
            doc = await self._svc("objects").find_one({"_id": object_id})
            if doc is None:
                raise AdapterError(f"object {object_id} not found", retryable=False)
            parts = [
                bytes(c["data"])
                async for c in self._svc("object_chunks")
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
                await self._svc("objects")
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
        if not self._usable_type(entity_type):
            return None
        with _errors():
            doc = await self._type_col(entity_type).find_one(
                {"_id": key_digest(canonical_key)}, _ENTITY_FIELDS
            )
        return None if doc is None else snapshot_from_json(doc)

    async def _roll_forward(self, doc: Mapping[str, Any]) -> None:
        """Make the pending history event and delivery record of a snapshot durable; idempotent.

        Order matters: the delivery record replaces the intent before ``pending`` is dropped (see
        ``get_delivery`` and step 1 of ``commit_entity``)."""
        pending = doc.get("pending")
        if not isinstance(pending, Mapping):
            return
        event, ack = dict(pending["event"]), dict(pending["ack"])
        version = int(pending["version"])
        etype, key_hash = str(doc["entity_type"]), key_digest(str(doc["canonical_key"]))
        with contextlib.suppress(DuplicateKeyError):
            await self._history_col(etype).insert_one(
                {"_id": self._history_id(key_hash, version), "key_hash": key_hash, **event}
            )
        record = DeliveryRecord(
            delivery_key=str(pending["delivery_key"]), recorded_at=parse_ts(event["received_at"]), acks=[ack]
        )
        with contextlib.suppress(DuplicateKeyError):  # concurrent roll-forwards of the same pending event
            await self._svc("deliveries").replace_one(
                {"_id": key_digest(record.delivery_key)}, delivery_to_json(record), upsert=True
            )
        await self._type_col(etype).update_one(
            {"_id": doc["_id"], "version": version, "pending.delivery_key": record.delivery_key},
            {"$unset": {"pending": ""}},
        )

    async def _delivery_doc(self, delivery_key: str) -> dict[str, Any] | None:
        """The document of a delivery key in ``_deliveries``: a delivery record or an intent."""
        doc = await self._svc("deliveries").find_one({"_id": key_digest(delivery_key)})
        return doc if doc is not None and doc.get("delivery_key") == delivery_key else None

    async def _write_intent(self, delivery_key: str, entity_type: str, entity_id: str) -> bool:
        """Point the key at the snapshot about to hold it in ``pending``; False if the key is already recorded."""
        intent = {
            "delivery_key": delivery_key,
            "intent": {"entity_type": entity_type, "entity_id": entity_id},
        }
        try:
            await self._svc("deliveries").replace_one(
                {"_id": key_digest(delivery_key), "intent": {"$exists": True}}, intent, upsert=True
            )
        except DuplicateKeyError:  # a delivery record, or a concurrent first intent of the same key
            doc = await self._delivery_doc(delivery_key)
            return doc is None or _is_intent(doc)
        return True

    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        self._require_type(new.entity_type)
        entities = self._type_col(new.entity_type)
        eid = key_digest(new.canonical_key)
        with _errors():
            await self._ensure_type(new.entity_type)
            # Order matters: the snapshot first, then ``_deliveries``. The roll-forward writes the delivery
            # record before it drops ``pending``, so a key committed by another instance is always seen in one
            # of the two reads (the reverse order has a window where it is in neither).
            current = await entities.find_one({"_id": eid}, _NO_SEARCH_TEXT)
            pending = None if current is None else current.get("pending")
            if isinstance(pending, Mapping) and pending.get("delivery_key") == event.delivery_key:
                assert current is not None
                return CommitResult(CommitOutcome.DUPLICATE, snapshot_from_json(current))
            delivery = await self._delivery_doc(event.delivery_key)
            if delivery is not None and not _is_intent(delivery):
                return CommitResult(
                    CommitOutcome.DUPLICATE, await self.read_entity(new.entity_type, new.canonical_key)
                )
            if current is not None and isinstance(pending, Mapping):
                await self._roll_forward(current)
            current_version = None if current is None else int(current["version"])
            if current_version != expected_version:
                return CommitResult(
                    CommitOutcome.CONFLICT, None if current is None else snapshot_from_json(current)
                )
            if not await self._write_intent(event.delivery_key, new.entity_type, eid):
                return CommitResult(
                    CommitOutcome.DUPLICATE, await self.read_entity(new.entity_type, new.canonical_key)
                )
            doc = {
                "_id": eid,
                **snapshot_to_json(new),
                "search_text": _search_text(new),
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
        return await self._list_entities(
            entity_type, scope=scope, updated_since=updated_since, cursor=cursor, limit=limit
        )

    async def search_entities(
        self,
        entity_type: str,
        *,
        search: str,
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]:
        return await self._list_entities(
            entity_type, search=search, scope=scope, updated_since=updated_since, cursor=cursor, limit=limit
        )

    async def _list_entities(
        self,
        entity_type: str,
        *,
        search: str = "",
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]:
        """Entities of one type in ``canonical_key`` order (binary, like ``COLLATE "C"``), filtered on the server."""
        if not self._usable_type(entity_type):
            return [], None
        query: dict[str, Any] = {}
        if scope is not None:
            query["key.scope"] = scope
        if updated_since is not None:
            query["updated_at"] = {"$gte": format_ts(updated_since)}
        if cursor is not None:
            query["canonical_key"] = {"$gt": str(_uncursor(cursor))}
        if search:
            # $literal: a term starting with "$" must not become a field path; no regex, so nothing is a pattern
            needle = {"$literal": search.casefold()}
            query["$expr"] = {"$gte": [{"$indexOfBytes": ["$search_text", needle]}, 0]}
        with _errors():
            docs = (
                await self._type_col(entity_type)
                .find(query, _ENTITY_FIELDS)
                .sort("canonical_key", ASCENDING)
                .limit(limit + 1)
                .to_list()
            )
        items = [snapshot_from_json(d) for d in docs[:limit]]
        next_cursor = _cursor(items[-1].canonical_key) if len(docs) > limit and items else None
        return items, next_cursor

    async def list_entity_types(
        self, *, scope: str | None = None, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[Mapping[str, Any]], str | None]:
        after = None if cursor is None else str(_uncursor(cursor))
        query: dict[str, Any] = {} if scope is None else {"key.scope": scope}
        rows: list[dict[str, Any]] = []
        with _errors():
            for entity_type in await self._type_names():
                if after is not None and entity_type <= after:
                    continue
                count = await self._type_col(entity_type).count_documents(query)
                if count:
                    rows.append({"entity_type": entity_type, "entity_count": count})
                if len(rows) > limit:
                    break
        page = rows[:limit]
        return page, _cursor(page[-1]["entity_type"]) if len(rows) > limit and page else None

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]:
        if not self._usable_type(entity_type):
            return [], None
        key_hash = key_digest(canonical_key)
        with _errors():
            current = await self._type_col(entity_type).find_one({"_id": key_hash}, _NO_SEARCH_TEXT)
            if current is None:
                return [], None
            await self._roll_forward(current)
            version: dict[str, int] = {"$lte": int(current["version"])}
            if cursor is not None:
                version["$lt"] = int(_uncursor(cursor))
            docs = (
                await self._history_col(entity_type)
                .find({"key_hash": key_hash, "version": version})
                .sort("version", DESCENDING)
                .limit(limit + 1)
                .to_list()
            )
        items = [event_from_json(d) for d in docs[:limit]]
        next_cursor = _cursor(int(docs[limit - 1]["version"])) if len(docs) > limit and limit > 0 else None
        return items, next_cursor

    # ------------------------------------------------------------------ statistics
    async def object_statistics(self) -> dict[str, int]:
        with _errors():
            cursor = await self._svc("objects").aggregate(
                [
                    {
                        "$group": {
                            "_id": None,
                            "object_count": {"$sum": 1},
                            "total_size_bytes": {"$sum": "$size_bytes"},
                        }
                    }
                ]
            )
            rows = await cursor.to_list()
        row = rows[0] if rows else {"object_count": 0, "total_size_bytes": 0}
        return {name: int(row[name]) for name in ("object_count", "total_size_bytes")}

    async def entity_statistics(self) -> dict[str, Any]:
        types: list[dict[str, Any]] = []
        size = 0
        with _errors():
            for entity_type in await self._type_names():
                col = self._type_col(entity_type)
                try:
                    stats = await (await col.aggregate([{"$collStats": {"storageStats": {}}}])).to_list()
                except OperationFailure as exc:
                    if (
                        exc.code == _NAMESPACE_NOT_FOUND
                    ):  # dropped after the listing: no longer in the namespace
                        continue
                    raise
                for shard in stats:
                    storage = shard.get("storageStats") or {}
                    if "storageSize" not in storage or "totalIndexSize" not in storage:
                        # unknown is not zero: the core reports the whole entity statistics as unavailable
                        raise AdapterError(
                            f"mongodb: $collStats of {col.name!r} reports no storageSize/totalIndexSize",
                            retryable=False,
                        )
                    size += int(storage["storageSize"]) + int(storage["totalIndexSize"])
                count = await col.count_documents({})
                if count:
                    types.append({"entity_type": entity_type, "entity_count": count})
        return {
            "entity_count": sum(row["entity_count"] for row in types),
            "total_size_bytes": size,
            "size_basis": SIZE_BASIS,
            "types": types,
        }

    # ------------------------------------------------------------------ deliveries
    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        with _errors():
            doc = await self._delivery_doc(delivery_key)
            if doc is None:
                return None
            if not _is_intent(doc):
                return delivery_from_json(doc)
            intent = doc["intent"]
            entity_type = str(intent.get("entity_type", ""))
            snap = (
                await self._type_col(entity_type).find_one({"_id": intent.get("entity_id")}, _NO_SEARCH_TEXT)
                if self._usable_type(entity_type)
                else None
            )
            pending = None if snap is None else snap.get("pending")
            if not isinstance(pending, Mapping) or pending.get("delivery_key") != delivery_key:
                # not (or no longer) pending: a roll-forward may have replaced the intent after the first read
                doc = await self._delivery_doc(delivery_key)
                return None if doc is None or _is_intent(doc) else delivery_from_json(doc)
        assert snap is not None
        with contextlib.suppress(AdapterError), _errors():
            await self._roll_forward(snap)  # committed, not rolled forward yet (crash or commit in progress)
        return DeliveryRecord(
            delivery_key=delivery_key,
            recorded_at=parse_ts(pending["event"]["received_at"]),
            acks=[pending["ack"]],
        )

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        """Insert-if-absent (object writes; their keys never equal entity keys ``<key>#<n>``, which alone get
        intents)."""
        with _errors():
            try:
                await self._svc("deliveries").insert_one(
                    {"_id": key_digest(record.delivery_key), **delivery_to_json(record)}
                )
            except DuplicateKeyError:
                return False
        return True
