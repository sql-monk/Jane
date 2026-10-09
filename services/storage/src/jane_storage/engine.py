"""Storage core: applies one entity record or one object to an adapter (contracts/docs/storage-adapter.md).

Algorithm for one ``EntityRecord`` (delivery key ``<invocation delivery_key>#<n>``):

1. ``get_delivery`` — already recorded → the stored ack with ``status: duplicate``;
2. ``read_entity`` → :func:`jane_storage.merge.merge` (pure) → ``commit_entity`` with the read version;
3. ``CONFLICT`` → re-read and retry (bounded by ``limits.conflict_retries``); ``DUPLICATE`` → as in step 1;
   ``COMMITTED`` → ``WriteAck`` ``written | partially_stale | stale``.

Objects: ``get_delivery`` → ``put_object`` (idempotent by key) → ``record_delivery`` (insert-if-absent).
The engine never interprets storage-specific errors: ``AdapterError`` propagates to the handler, which
turns it into ``HandlerResult.failed``.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime
from typing import Any

from jane_contracts.storage_adapter import (
    AdapterError,
    CommitOutcome,
    DeliveryRecord,
    HistoryEvent,
    ObjectRecord,
    RawObject,
    StorageAdapter,
)
from jane_kit.clients import RetryPolicy

from .codec import utcnow
from .keys import canonical_key
from .merge import merge

__all__ = ["ConflictRetriesExhausted", "StorageEngine", "backoff_ms", "stored_object_ref"]


class ConflictRetriesExhausted(AdapterError):
    """Concurrent writers kept winning for longer than ``limits.conflict_retries.max_attempts``."""

    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=True)


def backoff_ms(policy: RetryPolicy, attempt: int, rnd: Callable[[], float] = random.random) -> float:
    """Delay before attempt ``attempt + 1`` (``attempt`` >= 1)."""
    delay = min(policy.initial_backoff_ms * policy.backoff_multiplier ** (attempt - 1), policy.max_backoff_ms)
    return delay * rnd() if policy.jitter else delay


def stored_object_ref(rec: ObjectRecord, adapter_kind: str, connection_id: str | None) -> dict[str, Any]:
    """``StoredObjectRef`` of an object record."""
    ref: dict[str, Any] = {
        "object_id": rec.object_id,
        "adapter": adapter_kind,
        "locator": dict(rec.locator),
        "media_type": rec.media_type,
        "size_bytes": rec.size_bytes,
        "sha256": rec.sha256,
    }
    if connection_id:
        ref["connection_id"] = connection_id
    return ref


class StorageEngine:
    """Core semantics over one opened adapter (one connection)."""

    def __init__(
        self,
        adapter: StorageAdapter,
        *,
        connection_id: str | None = None,
        retries: RetryPolicy | None = None,
        clock: Callable[[], datetime] = utcnow,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.adapter = adapter
        self.connection_id = connection_id
        self.retries = retries or RetryPolicy()
        self._clock = clock
        self._sleep = sleep

    @property
    def target(self) -> dict[str, Any]:
        target: dict[str, Any] = {"adapter": self.adapter.kind}
        if self.connection_id:
            target["connection_id"] = self.connection_id
        return target

    def _duplicate(self, prior: DeliveryRecord, delivery_key: str) -> dict[str, Any]:
        stored = dict(prior.acks[0]) if prior.acks else {}
        stored.pop("status", None)
        stored.pop("target", None)
        return {"status": "duplicate", "target": self.target, **stored, "delivery_key": delivery_key}

    async def store_entity(self, record: Mapping[str, Any], delivery_key: str) -> dict[str, Any]:
        """Apply one EntityRecord; returns a ``WriteAck``."""
        prior = await self.adapter.get_delivery(delivery_key)
        if prior is not None:
            return self._duplicate(prior, delivery_key)
        entity_type = str(record["entity_type"])
        key = canonical_key(record["key"])
        attempt = 0
        while True:
            attempt += 1
            current = await self.adapter.read_entity(entity_type, key)
            now = self._clock()
            result = merge(current, record, now=now)
            event = HistoryEvent(
                entity_type=entity_type,
                canonical_key=key,
                record=dict(record),
                delivery_key=delivery_key,
                received_at=now,
                applied_fields=result.applied,
                stale_fields=result.stale,
            )
            outcome = await self.adapter.commit_entity(
                new=result.snapshot, expected_version=current.version if current else None, event=event
            )
            if outcome.outcome is CommitOutcome.COMMITTED:
                version = outcome.snapshot.version if outcome.snapshot else result.snapshot.version
                return {
                    "status": result.status,
                    "target": self.target,
                    "entity": {"entity_type": entity_type, "canonical_key": key, "version": version},
                    "applied_fields": result.applied,
                    "stale_fields": result.stale,
                    "delivery_key": delivery_key,
                }
            if outcome.outcome is CommitOutcome.DUPLICATE:
                prior = await self.adapter.get_delivery(delivery_key)
                if prior is None:  # recorded by a commit that is still being finished; treat as duplicate
                    prior = DeliveryRecord(delivery_key=delivery_key, recorded_at=now, acks=[])
                return self._duplicate(prior, delivery_key)
            if attempt >= self.retries.max_attempts:
                raise ConflictRetriesExhausted(
                    f"entity {entity_type} {key!r}: version conflict after {attempt} attempt(s)"
                )
            await self._sleep(backoff_ms(self.retries, attempt) / 1000)

    async def store_object(self, obj: RawObject, delivery_key: str) -> dict[str, Any]:
        """Persist one object (RAW or result document); returns a ``WriteAck``."""
        prior = await self.adapter.get_delivery(delivery_key)
        if prior is not None:
            return self._duplicate(prior, delivery_key)
        rec = await self.adapter.put_object(obj)
        ack = {
            "status": "written",
            "target": self.target,
            "object": stored_object_ref(rec, self.adapter.kind, self.connection_id),
            "delivery_key": delivery_key,
        }
        stored = {k: v for k, v in ack.items() if k not in {"status", "target"}}
        recorded = await self.adapter.record_delivery(
            DeliveryRecord(delivery_key=delivery_key, recorded_at=self._clock(), acks=[stored])
        )
        if not recorded:
            prior = await self.adapter.get_delivery(delivery_key)
            if prior is not None:
                return self._duplicate(prior, delivery_key)
        return ack
