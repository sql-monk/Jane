"""S3 adapter of the Jane storage handler (``kind: s3``); also the base of the MinIO adapter.

Layout in the connection bucket under ``<prefix>/`` (contracts/docs/storage-adapter.md, "Object stores"):

| Key | Content |
|---|---|
| ``entities/<entity_type>/<sha256(canonical_key)>.json`` | ``EntitySnapshot`` (+ ``pending``: the history event of its version until it is rolled forward) |
| ``history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json`` | ``HistoryEvent`` |
| ``deliveries/<sha256(delivery_key)>.json`` | ``DeliveryRecord`` (+ ``claimed_at``) |
| ``objects/<object_key>`` + ``objects/<object_key>.meta.json`` | bytes (``x-amz-meta-sha256``) + ``ObjectRecord`` |
| ``index/objects/<object_id>.json`` | ``ObjectRecord`` (lookup by ``object_id``, listing) |

Atomicity uses only conditional ``PutObject`` (``If-None-Match: *`` to create, ``If-Match: <ETag>`` to
replace), which AWS S3, MinIO and SeaweedFS implement. ``commit_entity``:

1. claim the delivery key: ``PUT deliveries/<h>.json`` with ``If-None-Match: *``. A 412 means the key
   exists: a complete delivery → ``DUPLICATE``; a claim of a commit still in flight → ``CONFLICT`` (the
   core retries); a dead claim (its commit lost the race or crashed more than ``lock_stale_ms`` ago) is
   removed and the claim repeated;
2. compare-and-swap the snapshot: ``PUT entities/…json`` with ``If-Match`` of the snapshot read at
   ``expected_version`` (``If-None-Match: *`` for a new entity). The new snapshot carries its history
   event in ``pending``, so the snapshot write is the single commit point: the version, the state and
   the event become visible together. A 412 → the claim is deleted (compensation) → ``CONFLICT``;
3. roll forward: ``PUT history/…/<version>.json`` and drop ``pending`` (``If-Match``). A crash here loses
   nothing: readers and the next commit roll a pending event forward first.

History versions are contiguous (``1..snapshot.version``), so history pages are read by key without
listing. ETags are content hashes; a snapshot document always contains its ``version``, so a replaced
document never gets the ETag of an older one.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import re
import uuid
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, ClassVar, TypeVar

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import (  # type: ignore[import-untyped]
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    ParamValidationError,
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
    dumps,
    entity_ack,
    event_from_json,
    event_to_json,
    format_ts,
    loads,
    object_record_from_json,
    object_record_to_json,
    parse_ts,
    snapshot_from_json,
    snapshot_to_json,
    utcnow,
)
from jane_storage.keys import key_digest, object_id_for, safe_segment

__all__ = ["DEFAULT_OPTIONS", "S3Adapter", "S3Profile", "package_dir"]

T = TypeVar("T")

DEFAULT_OPTIONS: dict[str, int] = {
    "connect_timeout_ms": 10_000,
    "command_timeout_ms": 30_000,
    "pool_max_size": 10,
    "lock_stale_ms": 120_000,
    "retry_max_attempts": 3,
    "claim_attempts": 3,
}
"""Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``lock_stale_ms`` — age after which a delivery claim without its snapshot is a leftover of a crash;
``claim_attempts`` — how many times a dead claim is removed and the delivery key claimed again."""

_BUCKET = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
_PREFIX = re.compile(r"^(?!.*(^|/)\.\.(/|$))[A-Za-z0-9._/-]{1,200}$")
_OBJECT_ID = re.compile(r"^[A-Za-z0-9_]{1,128}$")
_PRECONDITION = {"PreconditionFailed", "ConditionalRequestConflict", "NoSuchKey", "412", "409", "404"}
_MISSING = {"NoSuchKey", "404", "NotFound"}
_RETRYABLE_CODES = {
    "SlowDown",
    "RequestTimeout",
    "RequestTimeoutException",
    "ServiceUnavailable",
    "InternalError",
    "Throttling",
    "ThrottlingException",
    "RequestLimitExceeded",
    "OperationAborted",
}


def package_dir() -> Path:
    """Directory of the ``jane.storage-s3`` storage package (entry point ``jane.storage.packages``)."""
    return Path(__file__).parent / "package"


def _cursor(value: Any) -> str:
    return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")


def _uncursor(cursor: str) -> Any:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    except ValueError as exc:
        raise AdapterError(f"invalid cursor: {exc}", retryable=False) from exc


def _code(exc: ClientError) -> tuple[str, int]:
    error = exc.response.get("Error", {}) or {}
    status = int((exc.response.get("ResponseMetadata", {}) or {}).get("HTTPStatusCode") or 0)
    return str(error.get("Code", "")), status


@dataclass(frozen=True, slots=True)
class S3Profile:
    """What differs between S3-compatible services; the protocol (and the code) is the same."""

    addressing_style: str
    """Default ``addressing_style``: ``auto`` (AWS: virtual-hosted), ``path`` (MinIO, most self-hosted)."""
    endpoint_required: bool
    """AWS S3 derives the endpoint from ``region``; a self-hosted service needs ``params.endpoint``."""
    create_bucket: bool
    """Default of ``params.create_bucket`` (``ensure_schema`` creates a missing bucket)."""
    server_side_encryption: bool
    """``params.sse`` (``AES256`` | ``aws:kms``) and ``params.sse_kms_key_id`` are accepted."""


class S3Adapter:
    """``StorageAdapter`` over an S3 bucket (connection ``params.bucket``; secrets ``access_key``, ``secret_key``)."""

    kind: ClassVar[str] = "s3"
    capabilities: ClassVar[frozenset[str]] = frozenset({"objects", "entities", "history"})
    profile: ClassVar[S3Profile] = S3Profile(
        addressing_style="auto", endpoint_required=False, create_bucket=False, server_side_encryption=True
    )

    def __init__(self) -> None:
        self._client: Any = None
        self._bucket = ""
        self._prefix = ""
        self._create_bucket = False
        self._stale = timedelta(milliseconds=DEFAULT_OPTIONS["lock_stale_ms"])
        self._claim_attempts = DEFAULT_OPTIONS["claim_attempts"]
        self._put_extra: dict[str, str] = {}

    # ------------------------------------------------------------------ lifecycle
    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
        params = dict(connection.params)
        merged = dict(DEFAULT_OPTIONS)
        for name in DEFAULT_OPTIONS:
            for layer in (params, options):
                if name in layer:
                    merged[name] = int(layer[name])
        bucket = params.get("bucket")
        if not isinstance(bucket, str) or not _BUCKET.match(bucket):
            raise AdapterError(f"{self.kind} connection needs a valid params.bucket", retryable=False)
        endpoint = params.get("endpoint")
        if endpoint is not None and not isinstance(endpoint, str):
            raise AdapterError("params.endpoint must be a URL string", retryable=False)
        if self.profile.endpoint_required and not endpoint:
            raise AdapterError(f"{self.kind} connection needs params.endpoint", retryable=False)
        addressing = str(params.get("addressing_style", self.profile.addressing_style))
        if addressing not in {"auto", "path", "virtual"}:
            raise AdapterError(f"invalid addressing_style {addressing!r}", retryable=False)
        prefix = str(options.get("prefix") or params.get("prefix") or "").strip("/")
        if prefix and not _PREFIX.match(prefix):
            raise AdapterError(f"invalid prefix {prefix!r}", retryable=False)
        access_key, secret_key = connection.secrets.get("access_key"), connection.secrets.get("secret_key")
        if not access_key or not secret_key:
            raise AdapterError(
                f"{self.kind} connection needs secrets access_key and secret_key", retryable=False
            )
        put_extra: dict[str, str] = {}
        sse = params.get("sse")
        if sse is not None:
            if not self.profile.server_side_encryption or sse not in {"AES256", "aws:kms"}:
                raise AdapterError(f"{self.kind}: unsupported params.sse {sse!r}", retryable=False)
            put_extra["ServerSideEncryption"] = str(sse)
            if params.get("sse_kms_key_id"):
                put_extra["SSEKMSKeyId"] = str(params["sse_kms_key_id"])
        verify = params.get("verify_tls", True)
        timeout_connect = merged["connect_timeout_ms"] / 1000
        timeout_read = merged["command_timeout_ms"] / 1000
        try:
            self._client = boto3.session.Session().client(
                "s3",
                endpoint_url=endpoint or None,
                region_name=str(params.get("region") or "us-east-1"),
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=connection.secrets.get("session_token") or None,
                verify=verify if isinstance(verify, bool | str) else True,
                config=Config(
                    connect_timeout=timeout_connect,
                    read_timeout=timeout_read,
                    retries={"total_max_attempts": max(1, merged["retry_max_attempts"]), "mode": "standard"},
                    max_pool_connections=max(1, merged["pool_max_size"]),
                    s3={"addressing_style": addressing},
                ),
            )
        except (BotoCoreError, ValueError) as exc:
            raise AdapterError(f"{self.kind}: {exc}", retryable=False) from exc
        self._bucket = bucket
        self._prefix = prefix
        self._region = str(params.get("region") or "us-east-1")
        self._create_bucket = bool(params.get("create_bucket", self.profile.create_bucket))
        self._stale = timedelta(milliseconds=merged["lock_stale_ms"])
        self._claim_attempts = max(1, merged["claim_attempts"])
        self._put_extra = put_extra

    async def close(self) -> None:
        client, self._client = self._client, None
        if client is not None:
            await asyncio.to_thread(client.close)

    @property
    def client(self) -> Any:
        if self._client is None:
            raise AdapterError("adapter is not open", retryable=False)
        return self._client

    async def _run(self, fn: Callable[..., T], *args: Any) -> T:
        self.client  # noqa: B018 - raises if the adapter is not open
        try:
            return await asyncio.to_thread(fn, *args)
        except AdapterError:
            raise
        except ClientError as exc:
            code, status = _code(exc)
            retryable = status >= 500 or code in _RETRYABLE_CODES
            raise AdapterError(f"{self.kind}: {code or status}: {exc}", retryable=retryable) from exc
        except (NoCredentialsError, ParamValidationError) as exc:
            raise AdapterError(f"{self.kind}: {exc}", retryable=False) from exc
        except (BotoCoreError, OSError) as exc:  # connection refused/reset, timeouts
            raise AdapterError(f"{self.kind}: {type(exc).__name__}: {exc}", retryable=True) from exc

    # ------------------------------------------------------------------ primitive operations (sync)
    def _k(self, *parts: str) -> str:
        return "/".join(p for p in (self._prefix, *parts) if p)

    def _get(self, key: str) -> tuple[bytes, str] | None:
        try:
            resp = self.client.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if _code(exc)[0] in _MISSING:
                return None
            raise
        return bytes(resp["Body"].read()), str(resp["ETag"])

    def _get_json(self, key: str) -> tuple[dict[str, Any], str] | None:
        got = self._get(key)
        if got is None:
            return None
        try:
            doc = loads(got[0])
        except ValueError as exc:
            raise AdapterError(f"{self.kind}: {key} is not JSON: {exc}", retryable=False) from exc
        return doc, got[1]

    def _put(
        self,
        key: str,
        body: bytes,
        *,
        create: bool = False,
        if_match: str | None = None,
        content_type: str = "application/json",
        metadata: Mapping[str, str] | None = None,
    ) -> str | None:
        """PutObject; returns the new ETag or None if the precondition failed."""
        kwargs: dict[str, Any] = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": body,
            "ContentType": content_type,
            **self._put_extra,
        }
        if metadata:
            kwargs["Metadata"] = dict(metadata)
        if create:
            kwargs["IfNoneMatch"] = "*"
        if if_match is not None:
            kwargs["IfMatch"] = if_match
        try:
            resp = self.client.put_object(**kwargs)
        except ClientError as exc:
            code, status = _code(exc)
            if (create or if_match is not None) and (code in _PRECONDITION or status in {404, 409, 412}):
                return None
            raise
        return str(resp["ETag"])

    def _delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self._bucket, Key=key)

    def _delete_if(self, key: str, etag: str) -> None:
        """Delete ``key`` only while its ETag is ``etag`` (``If-Match`` on DeleteObject). A 412 means the
        document was replaced by another writer: it is left alone. Servers without conditional deletes
        either ignore the header (MinIO) or reject it — then the delete is unconditional (a narrow race,
        see README "Обмеження")."""
        try:
            self.client.delete_object(Bucket=self._bucket, Key=key, IfMatch=etag)
        except ClientError as exc:
            code, status = _code(exc)
            if code in _MISSING or status in {404, 412} or code == "PreconditionFailed":
                return
            if status in {400, 501} or code in {"NotImplemented", "InvalidArgument", "InvalidRequest"}:
                self._delete(key)
                return
            raise

    def _delete_own_claim(self, key: str, claim_id: str) -> None:
        """Compensation: remove the delivery claim only if it is still the one this call wrote."""
        got = self._get_json(key)
        if got is not None and got[0].get("claim_id") == claim_id:
            self._delete_if(key, got[1])

    def _keys(self, prefix: str, start_after: str | None) -> Iterator[str]:
        kwargs: dict[str, Any] = {"Bucket": self._bucket, "Prefix": prefix}
        if start_after:
            kwargs["StartAfter"] = start_after
        while True:
            resp = self.client.list_objects_v2(**kwargs)
            for item in resp.get("Contents", []) or []:
                key = str(item["Key"])
                if start_after is None or key > start_after:
                    yield key
            token = resp.get("NextContinuationToken")
            if not resp.get("IsTruncated") or not token:
                return
            kwargs.pop("StartAfter", None)
            kwargs["ContinuationToken"] = token

    # ------------------------------------------------------------------ schema, health
    def _head_bucket(self) -> bool:
        """True if the bucket exists; False if it does not."""
        try:
            self.client.head_bucket(Bucket=self._bucket)
        except ClientError as exc:
            code, status = _code(exc)
            if status == 404 or code in {"NoSuchBucket", "NotFound", "404"}:
                return False
            raise
        return True

    def _ensure_bucket(self) -> None:
        if self._head_bucket():
            return
        if not self._create_bucket:
            raise AdapterError(
                f"{self.kind}: bucket {self._bucket!r} does not exist (params.create_bucket is false)",
                retryable=False,
            )
        kwargs: dict[str, Any] = {"Bucket": self._bucket}
        if self._region != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": self._region}
        try:
            self.client.create_bucket(**kwargs)
        except ClientError as exc:
            if _code(exc)[0] not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise
            if not self._head_bucket():
                raise

    async def health(self) -> bool:
        try:
            exists = await self._run(self._head_bucket)
        except AdapterError:
            return False
        return exists or self._create_bucket

    async def ensure_schema(self, entity_types: Sequence[str]) -> None:
        # Keys need no directories; only the bucket has to exist.
        await self._run(self._ensure_bucket)

    # ------------------------------------------------------------------ objects
    def content_uri(self, rec: ObjectRecord) -> str | None:
        """Persistent ``s3://`` URI of a stored object (``ContentRef`` blob)."""
        return f"s3://{self._bucket}/{rec.locator['key']}"

    def _index_key(self, object_id: str) -> str:
        return self._k("index", "objects", f"{object_id}.json")

    def _put_object(self, obj: RawObject) -> ObjectRecord:
        object_id = object_id_for(obj.object_key)
        key = self._k("objects", obj.object_key)
        meta_key = f"{key}.meta.json"
        existing = self._get_json(meta_key)
        if existing is None:
            if (
                self._put(
                    key,
                    obj.content,
                    create=True,
                    content_type=obj.media_type,
                    metadata={"sha256": obj.sha256},
                )
                is None
            ):
                # the bytes are already there: a crashed or concurrent writer of the same key
                head = self.client.head_object(Bucket=self._bucket, Key=key)
                stored = str((head.get("Metadata") or {}).get("sha256", ""))
                if stored != obj.sha256:
                    raise AdapterError(
                        f"object {obj.object_key!r} already stored with sha256 {stored}", retryable=False
                    )
            rec = ObjectRecord(
                object_id=object_id,
                object_key=obj.object_key,
                locator={"bucket": self._bucket, "key": key},
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
            if self._put(meta_key, dumps(object_record_to_json(rec)), create=True) is None:
                existing = self._get_json(meta_key)
                if existing is None:
                    raise AdapterError(f"{self.kind}: object meta {meta_key} vanished", retryable=True)
        if existing is not None:
            rec = object_record_from_json(existing[0])
        if rec.sha256 != obj.sha256:
            raise AdapterError(
                f"object {obj.object_key!r} already stored with sha256 {rec.sha256}", retryable=False
            )
        # the index copy is derived from the winning meta document: every writer puts the same bytes
        self._put(self._index_key(object_id), dumps(object_record_to_json(rec)))
        return rec

    async def put_object(self, obj: RawObject) -> ObjectRecord:
        return await self._run(self._put_object, obj)

    def _get_object(self, object_id: str) -> ObjectRecord | None:
        if not _OBJECT_ID.match(object_id):
            return None
        got = self._get_json(self._index_key(object_id))
        return None if got is None else object_record_from_json(got[0])

    async def get_object(self, object_id: str) -> ObjectRecord | None:
        return await self._run(self._get_object, object_id)

    def _read_content(self, object_id: str) -> bytes:
        rec = self._get_object(object_id)
        got = None if rec is None else self._get(str(rec.locator["key"]))
        if got is None:
            raise AdapterError(f"object {object_id} not found", retryable=False)
        return got[0]

    async def read_object_content(self, object_id: str) -> bytes:
        return await self._run(self._read_content, object_id)

    def _list_objects(
        self,
        source_id: str | None,
        material_id: str | None,
        since: datetime | None,
        until: datetime | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[ObjectRecord], str | None]:
        prefix = self._k("index", "objects") + "/"
        found: list[tuple[str, ObjectRecord]] = []
        for key in self._keys(prefix, str(_uncursor(cursor)) if cursor else None):
            got = self._get_json(key)
            if got is None:
                continue
            rec = object_record_from_json(got[0])
            meta = rec.metadata
            if source_id is not None and meta.get("source_id") != source_id:
                continue
            if material_id is not None and meta.get("material_id") != material_id:
                continue
            if since is not None and rec.stored_at < since:
                continue
            if until is not None and rec.stored_at >= until:
                continue
            found.append((key, rec))
            if len(found) > limit:
                break
        page = found[:limit]
        next_cursor = _cursor(page[-1][0]) if len(found) > limit and page else None
        return [rec for _, rec in page], next_cursor

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
        return await self._run(self._list_objects, source_id, material_id, since, until, cursor, limit)

    # ------------------------------------------------------------------ entities
    def _snap_key(self, entity_type: str, canonical_key: str) -> str:
        return self._k("entities", safe_segment(entity_type), f"{key_digest(canonical_key)}.json")

    def _hist_key(self, entity_type: str, canonical_key: str, version: int) -> str:
        return self._k(
            "history", safe_segment(entity_type), key_digest(canonical_key), f"{version:012d}.json"
        )

    def _delivery_key(self, delivery_key: str) -> str:
        return self._k("deliveries", f"{key_digest(delivery_key)}.json")

    def _roll_forward(self, doc: Mapping[str, Any], etag: str) -> str | None:
        """Write the pending history event of a snapshot and drop ``pending``; returns the new ETag
        (None if another writer replaced the snapshot meanwhile — it rolled the event forward itself)."""
        pending = doc.get("pending")
        if not isinstance(pending, Mapping):
            return etag
        key = self._hist_key(str(doc["entity_type"]), str(doc["canonical_key"]), int(pending["version"]))
        self._put(key, dumps(dict(pending)))
        clean = {k: v for k, v in doc.items() if k != "pending"}
        return self._put(
            self._snap_key(str(doc["entity_type"]), str(doc["canonical_key"])), dumps(clean), if_match=etag
        )

    def _read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
        got = self._get_json(self._snap_key(entity_type, canonical_key))
        return None if got is None else snapshot_from_json(got[0])

    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
        return await self._run(self._read_entity, entity_type, canonical_key)

    def _delivery_state(self, key: str) -> tuple[str, DeliveryRecord | None]:
        """``missing`` | ``complete`` | ``in_flight`` (a commit may still finish) | ``dead`` (never will)."""
        state, record, _ = self._claim_state(key)
        return state, record

    def _claim_state(self, key: str) -> tuple[str, DeliveryRecord | None, tuple[dict[str, Any], str] | None]:
        """:meth:`_delivery_state` plus the claim document and its ETag."""
        got = self._get_json(key)
        if got is None:
            return "missing", None, None
        state, record = self._judge_claim(got[0])
        return state, record, got

    def _judge_claim(self, doc: Mapping[str, Any]) -> tuple[str, DeliveryRecord | None]:
        try:
            record = delivery_from_json(doc)
        except (KeyError, TypeError, ValueError):
            return "dead", None
        ack = dict(record.acks[0]) if record.acks else {}
        entity = ack.get("entity")
        if isinstance(entity, Mapping) and "version" in entity:
            version = int(entity["version"])
            etype, ckey = str(entity["entity_type"]), str(entity["canonical_key"])
            snap = self._get_json(self._snap_key(etype, ckey))
            current = int(snap[0]["version"]) if snap is not None else 0
            if current >= version:
                assert snap is not None
                pending = snap[0].get("pending")
                if isinstance(pending, Mapping) and int(pending["version"]) == version:
                    ok = pending.get("delivery_key") == record.delivery_key
                else:
                    event = self._get_json(self._hist_key(etype, ckey, version))
                    ok = event is not None and event[0].get("delivery_key") == record.delivery_key
                return ("complete", record) if ok else ("dead", record)
            claimed = parse_ts(str(doc.get("claimed_at") or doc["recorded_at"]))
            return ("in_flight", record) if utcnow() - claimed < self._stale else ("dead", record)
        obj = ack.get("object")
        if (
            isinstance(obj, Mapping)
            and "object_id" in obj
            and self._get_object(str(obj["object_id"])) is None
        ):
            return "dead", record
        return "complete", record

    def _applied(self, new: EntitySnapshot, event: HistoryEvent) -> bool:
        """Whether the snapshot CAS of this very commit already took effect (its response may have been
        lost and botocore retried the conditional PUT, which then fails with 412 against our own write)."""
        got = self._get_json(self._snap_key(new.entity_type, new.canonical_key))
        if got is None or int(got[0]["version"]) < new.version:
            return False
        pending = got[0].get("pending")
        if isinstance(pending, Mapping) and int(pending["version"]) == new.version:
            return bool(pending.get("delivery_key") == event.delivery_key)
        hist = self._get_json(self._hist_key(new.entity_type, new.canonical_key, new.version))
        return hist is not None and hist[0].get("delivery_key") == event.delivery_key

    def _claim(self, dkey: str, claim: dict[str, Any]) -> CommitOutcome | None:
        """Claim the delivery key; None = claimed by this call, otherwise DUPLICATE / CONFLICT."""
        for _ in range(self._claim_attempts):
            if self._put(dkey, dumps(claim), create=True) is not None:
                return None
            state, _, got = self._claim_state(dkey)
            if got is not None and got[0].get("claim_id") == claim["claim_id"]:
                return None  # our own PUT was applied, its response lost and the request retried
            if state == "complete":
                return CommitOutcome.DUPLICATE
            if state == "in_flight":
                return CommitOutcome.CONFLICT
            if state == "dead" and got is not None:
                self._delete_if(dkey, got[1])
        return CommitOutcome.CONFLICT

    def _commit(self, new: EntitySnapshot, expected: int | None, event: HistoryEvent) -> CommitResult:
        dkey = self._delivery_key(event.delivery_key)
        claim = delivery_to_json(
            DeliveryRecord(
                delivery_key=event.delivery_key, recorded_at=event.received_at, acks=[entity_ack(new, event)]
            )
        )
        claim["claimed_at"] = format_ts(utcnow())
        claim["claim_id"] = uuid.uuid4().hex
        refused = self._claim(dkey, claim)
        if refused is not None:
            return CommitResult(refused, self._read_entity(new.entity_type, new.canonical_key))

        def conflict() -> CommitResult:
            self._delete_own_claim(dkey, claim["claim_id"])  # compensation: nothing else was written
            return CommitResult(CommitOutcome.CONFLICT, self._read_entity(new.entity_type, new.canonical_key))

        skey = self._snap_key(new.entity_type, new.canonical_key)
        current = self._get_json(skey)
        etag: str | None = None
        if current is not None and int(current[0]["version"]) == expected:
            etag = self._roll_forward(*current)
        if (current is None) != (expected is None) or (current is not None and etag is None):
            return conflict()
        doc = snapshot_to_json(new)
        doc["pending"] = event_to_json(event, new.version)
        body = dumps(doc)
        written = (
            self._put(skey, body, if_match=etag) if etag is not None else self._put(skey, body, create=True)
        )
        if written is None:
            if not self._applied(new, event):
                return conflict()
            # Our CAS took effect (the 412 answered botocore's retry of it): committed, keep the claim.
            # Roll forward only the stored document of *our* version, with *its* ETag. If the snapshot is
            # already newer, another commit replaced ours and rolled our event forward itself: writing
            # anything here would roll that newer, acknowledged snapshot back.
            got = self._get_json(skey)
            if got is not None and int(got[0]["version"]) == new.version:
                with contextlib.suppress(ClientError, BotoCoreError, OSError):
                    self._roll_forward(*got)
            return CommitResult(CommitOutcome.COMMITTED, new)
        with contextlib.suppress(ClientError, BotoCoreError, OSError):
            # committed; rolling forward now only saves readers the work
            self._roll_forward(doc, written)  # our document with the ETag of our own write
        return CommitResult(CommitOutcome.COMMITTED, new)

    async def commit_entity(
        self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent
    ) -> CommitResult:
        return await self._run(self._commit, new, expected_version, event)

    def _list_entities(
        self,
        entity_type: str,
        scope: str | None,
        updated_since: datetime | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[EntitySnapshot], str | None]:
        prefix = self._k("entities", safe_segment(entity_type)) + "/"
        found: list[tuple[str, EntitySnapshot]] = []
        for key in self._keys(prefix, str(_uncursor(cursor)) if cursor else None):
            got = self._get_json(key)
            if got is None:
                continue
            snap = snapshot_from_json(got[0])
            if snap.entity_type != entity_type:
                continue
            if scope is not None and snap.key.get("scope") != scope:
                continue
            if updated_since is not None and snap.updated_at < updated_since:
                continue
            found.append((key, snap))
            if len(found) > limit:
                break
        page = found[:limit]
        next_cursor = _cursor(page[-1][0]) if len(found) > limit and page else None
        return [snap for _, snap in page], next_cursor

    async def list_entities(
        self,
        entity_type: str,
        *,
        scope: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int,
    ) -> tuple[Sequence[EntitySnapshot], str | None]:
        return await self._run(self._list_entities, entity_type, scope, updated_since, cursor, limit)

    def _list_history(
        self, entity_type: str, canonical_key: str, cursor: str | None, limit: int
    ) -> tuple[list[HistoryEvent], str | None]:
        current = self._get_json(self._snap_key(entity_type, canonical_key))
        if current is None:
            return [], None
        doc = current[0]
        pending = doc.get("pending")
        if isinstance(pending, Mapping):
            with contextlib.suppress(ClientError, BotoCoreError, OSError):
                self._roll_forward(*current)  # if it fails, the pending event is served from the snapshot
        top = int(doc["version"]) if cursor is None else int(_uncursor(cursor)) - 1
        versions = list(range(top, max(0, top - limit), -1))
        events: list[HistoryEvent] = []
        for version in versions:
            if isinstance(pending, Mapping) and int(pending["version"]) == version:
                events.append(event_from_json(pending))
                continue
            got = self._get_json(self._hist_key(entity_type, canonical_key, version))
            if got is not None:
                events.append(event_from_json(got[0]))
        next_cursor = _cursor(versions[-1]) if versions and versions[-1] > 1 else None
        return events, next_cursor

    async def list_history(
        self, entity_type: str, canonical_key: str, *, cursor: str | None = None, limit: int
    ) -> tuple[Sequence[HistoryEvent], str | None]:
        return await self._run(self._list_history, entity_type, canonical_key, cursor, limit)

    # ------------------------------------------------------------------ deliveries
    def _get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        state, record = self._delivery_state(self._delivery_key(delivery_key))
        if state != "complete" or record is None or record.delivery_key != delivery_key:
            return None
        return record

    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
        return await self._run(self._get_delivery, delivery_key)

    def _record_delivery(self, record: DeliveryRecord) -> bool:
        key = self._delivery_key(record.delivery_key)
        doc = delivery_to_json(record)
        doc["claimed_at"] = format_ts(utcnow())
        doc["claim_id"] = uuid.uuid4().hex
        for _ in range(self._claim_attempts):
            if self._put(key, dumps(doc), create=True) is not None:
                return True
            state, _, got = self._claim_state(key)
            if got is not None and got[0].get("claim_id") == doc["claim_id"]:
                return True  # our PUT was applied, the response lost and the request retried
            if state in {"complete", "in_flight"}:
                return False
            if state == "dead" and got is not None:
                self._delete_if(key, got[1])
        return False

    async def record_delivery(self, record: DeliveryRecord) -> bool:
        return await self._run(self._record_delivery, record)
