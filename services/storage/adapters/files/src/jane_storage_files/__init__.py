"""Filesystem adapter of the Jane storage handler (``kind: filesystem``).

Layout under ``<base_path>/<prefix>`` (contracts/docs/storage-adapter.md, object stores and files):

| Path | Content |
|---|---|
| ``entities/<entity_type>/<sha256(canonical_key)>.json`` | ``EntitySnapshot`` |
| ``history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json`` | ``HistoryEvent`` (``entities_format: json``) |
| ``history/<entity_type>/<sha256(canonical_key)>.jsonl`` | one event per line (``entities_format: jsonl``) |
| ``deliveries/<sha256(delivery_key)>.json`` | ``DeliveryRecord`` |
| ``objects/<object_key>`` + ``.meta.json`` | bytes + ``ObjectRecord`` (the meta file is the commit marker) |
| ``index/objects/<object_id>.json`` | ``object_id`` → ``object_key`` |
| ``locks/…/<name>.lock`` | lock files (``O_CREAT | O_EXCL``) |

Atomicity on Windows and Linux: every document is written to a temporary file in the same directory,
flushed with ``fsync`` and moved into place with ``os.replace`` (retried while Windows reports the
target as in use by a reader); exclusive creation uses ``os.link`` of a complete temporary file (falls
back to ``O_CREAT | O_EXCL`` where hard links are unavailable). ``commit_entity`` and ``put_object``
run under a per-key lock file created with ``O_CREAT | O_EXCL``; a lock older than ``lock_stale_ms``
(a crashed writer) is broken. Commit order: delivery record → history event → snapshot; a delivery
record whose snapshot/history does not confirm it is incomplete (crash) and is redone.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import errno
import json
import os
import socket
import time
import uuid
from collections.abc import Callable, Iterator, Mapping, Sequence
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar, TypeVar

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

__all__ = ["DEFAULT_OPTIONS", "FilesystemAdapter", "package_dir"]

T = TypeVar("T")

DEFAULT_OPTIONS: dict[str, int] = {
    "lock_timeout_ms": 30_000,
    "lock_stale_ms": 120_000,
    "lock_poll_ms": 10,
    "replace_retry_ms": 5_000,
}
"""Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``)."""


def package_dir() -> Path:
    """Directory of the ``jane.storage-files`` storage package (entry point ``jane.storage.packages``)."""
    return Path(__file__).parent / "package"


def _b64(value: Any) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def _unb64(cursor: str) -> Any:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    except ValueError as exc:
        raise AdapterError(f"invalid cursor: {exc}", retryable=False) from exc


def _safe_prefix(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise AdapterError(f"invalid prefix {value!r}", retryable=False)
    return path


class _Store:
    """Synchronous file operations; the adapter runs them in worker threads."""

    def __init__(self, base: Path, prefix: PurePosixPath | None, options: Mapping[str, Any]) -> None:
        self.base = base
        self.root = base.joinpath(*prefix.parts) if prefix else base
        self.jsonl = options.get("entities_format", "json") == "jsonl"
        self.lock_timeout = int(options["lock_timeout_ms"]) / 1000
        self.lock_stale = int(options["lock_stale_ms"]) / 1000
        self.lock_poll = int(options["lock_poll_ms"]) / 1000
        self.replace_retry = int(options["replace_retry_ms"]) / 1000
        self.owner = f"{socket.gethostname()}:{os.getpid()}"

    # ------------------------------------------------------------------ paths
    def snapshot_path(self, entity_type: str, key: str) -> Path:
        return self.root / "entities" / entity_type / f"{key_digest(key)}.json"

    def history_dir(self, entity_type: str, key: str) -> Path:
        return self.root / "history" / entity_type / key_digest(key)

    def history_jsonl(self, entity_type: str, key: str) -> Path:
        return self.root / "history" / entity_type / f"{key_digest(key)}.jsonl"

    def delivery_path(self, delivery_key: str) -> Path:
        return self.root / "deliveries" / f"{key_digest(delivery_key)}.json"

    def object_path(self, object_key: str) -> Path:
        return self.root.joinpath("objects", *_safe_prefix(object_key).parts)

    def index_path(self, object_id: str) -> Path:
        return self.root / "index" / "objects" / f"{object_id}.json"

    def lock_path(self, *parts: str) -> Path:
        return self.root.joinpath("locks", *parts[:-1], f"{parts[-1]}.lock")

    def locator(self, path: Path) -> str:
        return path.relative_to(self.base).as_posix()

    # ------------------------------------------------------------------ primitives
    def _retry_windows(self, fn: Callable[[], T]) -> T:
        """Windows refuses to replace/open a file another process has open; retry for a while."""
        deadline = time.monotonic() + self.replace_retry
        while True:
            try:
                return fn()
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(self.lock_poll)

    def read_bytes(self, path: Path) -> bytes | None:
        def read() -> bytes | None:
            try:
                return path.read_bytes()
            except FileNotFoundError:
                return None

        return self._retry_windows(read)

    def read_json(self, path: Path) -> Any | None:
        raw = self.read_bytes(path)
        if raw is None:
            return None
        try:
            return loads(raw)
        except ValueError as exc:
            raise AdapterError(f"corrupt document {self.locator(path)}: {exc}", retryable=False) from exc

    def _tmp(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        return path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")

    @staticmethod
    def _write_fsync(path: Path, data: bytes) -> None:
        with open(path, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())

    def write_atomic(self, path: Path, data: bytes) -> None:
        tmp = self._tmp(path)
        try:
            self._write_fsync(tmp, data)
            self._retry_windows(lambda: os.replace(tmp, path))
        finally:
            with contextlib.suppress(FileNotFoundError):
                tmp.unlink()

    def create_exclusive(self, path: Path, data: bytes) -> bool:
        """Create ``path`` with ``data`` only if absent, never exposing a partial file. False if it exists."""
        if path.exists():
            return False
        tmp = self._tmp(path)
        try:
            self._write_fsync(tmp, data)
            try:
                os.link(tmp, path)
                return True
            except FileExistsError:
                return False
            except OSError as exc:  # no hard links on this filesystem
                if exc.errno not in (
                    errno.EPERM,
                    errno.ENOTSUP,
                    errno.EXDEV,
                    errno.EOPNOTSUPP,
                ) and not isinstance(exc, NotImplementedError):
                    raise
            try:
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
            except FileExistsError:
                return False
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            return True
        finally:
            with contextlib.suppress(FileNotFoundError):
                tmp.unlink()

    def unlink(self, path: Path) -> None:
        with contextlib.suppress(FileNotFoundError):
            self._retry_windows(path.unlink)

    @contextlib.contextmanager
    def lock(self, path: Path) -> Iterator[None]:
        path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.lock_timeout
        while True:
            try:
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                self._break_if_stale(path)
                if time.monotonic() >= deadline:
                    raise AdapterError(
                        f"lock {self.locator(path)} held longer than lock_timeout_ms", retryable=True
                    ) from None
                time.sleep(self.lock_poll)
                continue
            except PermissionError:  # Windows: the lock file is being deleted by its owner
                if time.monotonic() >= deadline:
                    raise
                time.sleep(self.lock_poll)
                continue
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(f"{self.owner} {time.time():.3f}\n")
            break
        try:
            yield
        finally:
            self.unlink(path)

    def _break_if_stale(self, path: Path) -> None:
        try:
            age = time.time() - path.stat().st_mtime
        except FileNotFoundError:
            return
        if age > self.lock_stale:
            stale = path.with_name(f"{path.name}.{uuid.uuid4().hex}.stale")
            with contextlib.suppress(FileNotFoundError, PermissionError):
                os.rename(path, stale)
                stale.unlink()

    # ------------------------------------------------------------------ schema / health
    def ensure_schema(self, entity_types: Sequence[str]) -> None:
        for sub in ("entities", "history", "deliveries", "objects", "index/objects", "locks"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        for entity_type in entity_types:
            (self.root / "entities" / entity_type).mkdir(parents=True, exist_ok=True)

    def health(self) -> bool:
        target = self.root if self.root.is_dir() else self.base
        return target.is_dir() and os.access(target, os.W_OK)

    # ------------------------------------------------------------------ objects
    def put_object(self, obj: RawObject, now: datetime) -> ObjectRecord:
        object_id = object_id_for(obj.object_key)
        path = self.object_path(obj.object_key)
        meta_path = path.with_name(path.name + ".meta.json")
        with self.lock(self.lock_path("objects", object_id)):
            existing = self.read_json(meta_path)
            if existing is not None:
                rec = object_record_from_json(existing)
                if rec.sha256 != obj.sha256:
                    raise AdapterError(
                        f"object {obj.object_key!r} already stored with sha256 {rec.sha256}", retryable=False
                    )
                return rec
            self.write_atomic(path, obj.content)
            rec = ObjectRecord(
                object_id=object_id,
                object_key=obj.object_key,
                locator={"path": self.locator(path)},
                media_type=obj.media_type,
                size_bytes=len(obj.content),
                sha256=obj.sha256,
                stored_at=now,
                metadata={
                    **dict(obj.metadata),
                    "material_id": obj.material_id,
                    "observation_id": obj.observation_id,
                    "source_id": obj.source_id,
                    "format": obj.format,
                },
            )
            self.write_atomic(self.index_path(object_id), dumps({"object_key": obj.object_key}))
            self.write_atomic(meta_path, dumps(object_record_to_json(rec)))
            return rec

    def get_object(self, object_id: str) -> ObjectRecord | None:
        if not object_id.replace("_", "").isalnum():
            return None
        index = self.read_json(self.index_path(object_id))
        if index is None:
            return None
        path = self.object_path(str(index["object_key"]))
        meta = self.read_json(path.with_name(path.name + ".meta.json"))
        return None if meta is None else object_record_from_json(meta)

    def read_object_content(self, object_id: str) -> bytes:
        rec = self.get_object(object_id)
        data = None if rec is None else self.read_bytes(self.object_path(rec.object_key))
        if data is None:
            raise AdapterError(f"object {object_id} not found", retryable=False)
        return data

    def list_objects(
        self,
        source_id: str | None,
        material_id: str | None,
        since: datetime | None,
        until: datetime | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[ObjectRecord], str | None]:
        index_dir = self.root / "index" / "objects"
        records = []
        for entry in sorted(index_dir.glob("*.json")) if index_dir.is_dir() else []:
            rec = self.get_object(entry.stem)
            if rec is None:
                continue
            meta = rec.metadata
            if source_id is not None and meta.get("source_id") != source_id:
                continue
            if material_id is not None and meta.get("material_id") != material_id:
                continue
            if since is not None and rec.stored_at < since:
                continue
            if until is not None and rec.stored_at >= until:
                continue
            records.append(rec)
        records.sort(key=lambda r: (format_ts(r.stored_at), r.object_id))
        if cursor is not None:
            after = tuple(_unb64(cursor))
            records = [r for r in records if (format_ts(r.stored_at), r.object_id) > after]
        page = records[:limit]
        more = len(records) > limit
        next_cursor = _b64([format_ts(page[-1].stored_at), page[-1].object_id]) if more and page else None
        return page, next_cursor

    # ------------------------------------------------------------------ entities
    def read_entity(self, entity_type: str, key: str) -> EntitySnapshot | None:
        doc = self.read_json(self.snapshot_path(entity_type, key))
        return None if doc is None else snapshot_from_json(doc)

    def _history_docs(self, entity_type: str, key: str) -> dict[int, dict[str, Any]]:
        docs: dict[int, dict[str, Any]] = {}
        if self.jsonl:
            raw = self.read_bytes(self.history_jsonl(entity_type, key)) or b""
            for line in raw.splitlines():
                try:
                    doc = loads(line)
                except ValueError:
                    continue  # a torn last line after a crash
                docs[int(doc["version"])] = doc
        else:
            folder = self.history_dir(entity_type, key)
            for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
                doc = self.read_json(path)
                if doc is not None:
                    docs[int(doc["version"])] = doc
        return docs

    def history_event(self, entity_type: str, key: str, version: int) -> dict[str, Any] | None:
        if self.jsonl:
            return self._history_docs(entity_type, key).get(version)
        return self.read_json(self.history_dir(entity_type, key) / f"{version:012d}.json")

    def _append_history(self, event: HistoryEvent, version: int) -> None:
        doc = event_to_json(event, version)
        if self.jsonl:
            path = self.history_jsonl(event.entity_type, event.canonical_key)
            path.parent.mkdir(parents=True, exist_ok=True)

            def append() -> None:
                with open(path, "ab") as fh:
                    fh.write(dumps(doc) + b"\n")
                    fh.flush()
                    os.fsync(fh.fileno())

            self._retry_windows(append)
        else:
            path = self.history_dir(event.entity_type, event.canonical_key) / f"{version:012d}.json"
            self.write_atomic(path, dumps(doc))

    def list_history(
        self, entity_type: str, key: str, cursor: str | None, limit: int
    ) -> tuple[list[HistoryEvent], str | None]:
        snap = self.read_entity(entity_type, key)
        if snap is None:
            return [], None
        docs = self._history_docs(entity_type, key)
        versions = sorted((v for v in docs if v <= snap.version), reverse=True)
        if cursor is not None:
            before = int(_unb64(cursor))
            versions = [v for v in versions if v < before]
        page = versions[:limit]
        next_cursor = _b64(page[-1]) if len(versions) > limit and page else None
        return [event_from_json(docs[v]) for v in page], next_cursor

    def list_entities(
        self,
        entity_type: str,
        scope: str | None,
        updated_since: datetime | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[EntitySnapshot], str | None]:
        folder = self.root / "entities" / entity_type
        snaps = []
        for path in folder.glob("*.json") if folder.is_dir() else []:
            doc = self.read_json(path)
            if doc is None:
                continue
            snap = snapshot_from_json(doc)
            if scope is not None and snap.key.get("scope") != scope:
                continue
            if updated_since is not None and snap.updated_at < updated_since:
                continue
            snaps.append(snap)
        snaps.sort(key=lambda s: s.canonical_key)
        if cursor is not None:
            after = str(_unb64(cursor))
            snaps = [s for s in snaps if s.canonical_key > after]
        page = snaps[:limit]
        next_cursor = _b64(page[-1].canonical_key) if len(snaps) > limit and page else None
        return page, next_cursor

    def _delivery_complete(self, record: DeliveryRecord) -> bool:
        ack = dict(record.acks[0]) if record.acks else {}
        entity = ack.get("entity")
        if isinstance(entity, Mapping) and "version" in entity:
            snap = self.read_entity(str(entity["entity_type"]), str(entity["canonical_key"]))
            if snap is None or snap.version < int(entity["version"]):
                return False
            event = self.history_event(snap.entity_type, snap.canonical_key, int(entity["version"]))
            return event is not None and event.get("delivery_key") == record.delivery_key
        obj = ack.get("object")
        if isinstance(obj, Mapping) and "object_id" in obj:
            return self.get_object(str(obj["object_id"])) is not None
        return True

    def _read_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        path = self.delivery_path(delivery_key)
        raw = self.read_bytes(path)
        if raw is None:
            return None
        try:
            record = delivery_from_json(loads(raw))
        except (ValueError, KeyError):
            return None
        return record if record.delivery_key == delivery_key else None

    def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        record = self._read_delivery(delivery_key)
        return record if record is not None and self._delivery_complete(record) else None

    def record_delivery(self, record: DeliveryRecord) -> bool:
        path = self.delivery_path(record.delivery_key)
        if self.create_exclusive(path, dumps(delivery_to_json(record))):
            return True
        existing = self._read_delivery(record.delivery_key)
        if existing is None:  # unreadable leftover of a crash: replace it
            self.write_atomic(path, dumps(delivery_to_json(record)))
            return True
        return False

    def commit_entity(
        self, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        with self.lock(self.lock_path("entities", new.entity_type, key_digest(new.canonical_key))):
            delivery_path = self.delivery_path(event.delivery_key)
            prior = self._read_delivery(event.delivery_key)
            if prior is not None:
                if self._delivery_complete(prior):
                    return CommitResult(
                        CommitOutcome.DUPLICATE, self.read_entity(new.entity_type, new.canonical_key)
                    )
                self.unlink(delivery_path)  # left by a crashed commit: redo
            current = self.read_entity(new.entity_type, new.canonical_key)
            if (current.version if current else None) != expected_version:
                return CommitResult(CommitOutcome.CONFLICT, current)
            delivery = DeliveryRecord(
                delivery_key=event.delivery_key, recorded_at=event.received_at, acks=[entity_ack(new, event)]
            )
            self.write_atomic(delivery_path, dumps(delivery_to_json(delivery)))
            self._append_history(event, new.version)
            self.write_atomic(
                self.snapshot_path(new.entity_type, new.canonical_key), dumps(snapshot_to_json(new))
            )
            return CommitResult(CommitOutcome.COMMITTED, new)


class FilesystemAdapter:
    """``StorageAdapter`` over a local or mounted directory (connection ``params.base_path``)."""

    kind: ClassVar[str] = "filesystem"
    capabilities: ClassVar[frozenset[str]] = frozenset({"objects", "entities", "history"})

    def __init__(self) -> None:
        self._store: _Store | None = None

    @property
    def store(self) -> _Store:
        if self._store is None:
            raise AdapterError("adapter is not open", retryable=False)
        return self._store

    async def _run(self, fn: Callable[..., T], *args: Any) -> T:
        try:
            return await asyncio.to_thread(fn, *args)
        except AdapterError:
            raise
        except OSError as exc:
            raise AdapterError(f"filesystem error: {exc}", retryable=True) from exc

    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        params = dict(connection.params)
        base = params.get("base_path")
        if not isinstance(base, str) or not base:
            raise AdapterError("filesystem connection needs params.base_path", retryable=False)
        merged = {**DEFAULT_OPTIONS}
        for name in DEFAULT_OPTIONS:
            if name in params:
                merged[name] = int(params[name])
            if name in options:
                merged[name] = int(options[name])
        prefix_value = options.get("prefix") or params.get("prefix")
        prefix = _safe_prefix(str(prefix_value)) if prefix_value else None
        fmt = str(options.get("entities_format") or "json")
        if fmt not in {"json", "jsonl"}:
            raise AdapterError(f"unsupported entities_format {fmt!r}", retryable=False)
        self._store = _Store(Path(base), prefix, {**merged, "entities_format": fmt})

    async def close(self) -> None:
        self._store = None

    async def health(self) -> bool:
        try:
            return await asyncio.to_thread(self.store.health)
        except OSError:
            return False

    async def ensure_schema(self, entity_types: Sequence[str]) -> None:
        await self._run(self.store.ensure_schema, list(entity_types))

    async def put_object(self, obj: RawObject) -> ObjectRecord:
        return await self._run(self.store.put_object, obj, utcnow())

    async def get_object(self, object_id: str) -> ObjectRecord | None:
        return await self._run(self.store.get_object, object_id)

    async def read_object_content(self, object_id: str) -> bytes:
        return await self._run(self.store.read_object_content, object_id)

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
        return await self._run(self.store.list_objects, source_id, material_id, since, until, cursor, limit)

    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
        return await self._run(self.store.read_entity, entity_type, canonical_key)

    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        return await self._run(self.store.commit_entity, new, expected_version, event)

    async def list_entities(
        self,
        entity_type: str,
        *,
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]:
        return await self._run(self.store.list_entities, entity_type, scope, updated_since, cursor, limit)

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]:
        return await self._run(self.store.list_history, entity_type, canonical_key, cursor, limit)

    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        return await self._run(self.store.get_delivery, delivery_key)

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        return await self._run(self.store.record_delivery, record)
