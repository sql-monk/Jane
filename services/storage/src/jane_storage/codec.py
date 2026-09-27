"""Adapter kit: JSON documents for the dataclasses of ``jane_contracts.storage_adapter``.

Shared by every adapter that keeps snapshots, history events, delivery records and object metadata
as JSON (filesystem, MinIO, S3, MongoDB; SQL adapters use it for JSON columns). Using the same codec
guarantees that all adapters return identical values to the core (e.g. timestamps with microseconds
in UTC, ``field_orders`` with ``sequence``).

Document shapes follow ``entity.schema.json`` (``EntityState``, ``EntityHistoryEntry``) plus the
internal fields the core needs (``version`` of a history event, ``canonical_key``).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from jane_contracts.storage_adapter import (
    DeliveryRecord,
    EntitySnapshot,
    HistoryEvent,
    ObjectRecord,
    OrderKey,
)

__all__ = [
    "delivery_from_json",
    "delivery_to_json",
    "dumps",
    "entity_ack",
    "event_from_json",
    "event_to_json",
    "format_ts",
    "loads",
    "object_record_from_json",
    "object_record_to_json",
    "order_from_json",
    "order_to_json",
    "parse_ts",
    "snapshot_from_json",
    "snapshot_to_json",
    "utcnow",
]


def utcnow() -> datetime:
    return datetime.now(UTC)


def format_ts(value: datetime) -> str:
    """RFC 3339 UTC with microseconds: ``2026-09-27T10:00:05.000000Z``."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_ts(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).astimezone(UTC)


def dumps(document: Any) -> bytes:
    """Canonical UTF-8 JSON (sorted keys, no ASCII escaping)."""
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def loads(raw: bytes | str) -> Any:
    return json.loads(raw)


def order_to_json(order: OrderKey) -> dict[str, Any]:
    out: dict[str, Any] = {
        "observed_at": format_ts(order.observed_at),
        "observation_id": order.observation_id,
    }
    if order.sequence is not None:
        out["sequence"] = order.sequence
    return out


def order_from_json(doc: Mapping[str, Any]) -> OrderKey:
    seq = doc.get("sequence")
    return OrderKey(
        observed_at=parse_ts(doc["observed_at"]),
        observation_id=str(doc["observation_id"]),
        sequence=None if seq is None else int(seq),
    )


def snapshot_to_json(snap: EntitySnapshot) -> dict[str, Any]:
    return {
        "entity_type": snap.entity_type,
        "canonical_key": snap.canonical_key,
        "key": dict(snap.key),
        "fields": dict(snap.fields),
        "field_orders": {name: order_to_json(o) for name, o in snap.field_orders.items()},
        "cleared_fields": sorted(snap.cleared_fields),
        "version": snap.version,
        "updated_at": format_ts(snap.updated_at),
    }


def snapshot_from_json(doc: Mapping[str, Any]) -> EntitySnapshot:
    return EntitySnapshot(
        entity_type=str(doc["entity_type"]),
        canonical_key=str(doc["canonical_key"]),
        key=dict(doc["key"]),
        fields=dict(doc["fields"]),
        field_orders={name: order_from_json(o) for name, o in dict(doc.get("field_orders") or {}).items()},
        cleared_fields=frozenset(doc.get("cleared_fields") or ()),
        version=int(doc["version"]),
        updated_at=parse_ts(doc["updated_at"]),
    )


def event_to_json(event: HistoryEvent, version: int) -> dict[str, Any]:
    """History event document; ``version`` = snapshot version this event produced."""
    return {
        "entity_type": event.entity_type,
        "canonical_key": event.canonical_key,
        "version": version,
        "record": dict(event.record),
        "delivery_key": event.delivery_key,
        "received_at": format_ts(event.received_at),
        "applied_fields": list(event.applied_fields),
        "stale_fields": list(event.stale_fields),
    }


def event_from_json(doc: Mapping[str, Any]) -> HistoryEvent:
    return HistoryEvent(
        entity_type=str(doc["entity_type"]),
        canonical_key=str(doc["canonical_key"]),
        record=dict(doc["record"]),
        delivery_key=str(doc["delivery_key"]),
        received_at=parse_ts(doc["received_at"]),
        applied_fields=list(doc.get("applied_fields") or ()),
        stale_fields=list(doc.get("stale_fields") or ()),
    )


def delivery_to_json(record: DeliveryRecord) -> dict[str, Any]:
    return {
        "delivery_key": record.delivery_key,
        "recorded_at": format_ts(record.recorded_at),
        "acks": [dict(a) for a in record.acks],
    }


def delivery_from_json(doc: Mapping[str, Any]) -> DeliveryRecord:
    return DeliveryRecord(
        delivery_key=str(doc["delivery_key"]),
        recorded_at=parse_ts(doc["recorded_at"]),
        acks=[dict(a) for a in doc.get("acks") or ()],
    )


def object_record_to_json(rec: ObjectRecord) -> dict[str, Any]:
    return {
        "object_id": rec.object_id,
        "object_key": rec.object_key,
        "locator": dict(rec.locator),
        "media_type": rec.media_type,
        "size_bytes": rec.size_bytes,
        "sha256": rec.sha256,
        "stored_at": format_ts(rec.stored_at),
        "metadata": dict(rec.metadata),
    }


def object_record_from_json(doc: Mapping[str, Any]) -> ObjectRecord:
    return ObjectRecord(
        object_id=str(doc["object_id"]),
        object_key=str(doc["object_key"]),
        locator=dict(doc.get("locator") or {}),
        media_type=str(doc["media_type"]),
        size_bytes=int(doc["size_bytes"]),
        sha256=str(doc["sha256"]),
        stored_at=parse_ts(doc["stored_at"]),
        metadata=dict(doc.get("metadata") or {}),
    )


def entity_ack(new: EntitySnapshot, event: HistoryEvent) -> dict[str, Any]:
    """What ``commit_entity`` records as the only ack of the entity delivery (``DeliveryRecord.acks[0]``).

    The core turns it into a ``WriteAck`` with ``status: duplicate`` on a repeated delivery. Every
    adapter must record exactly this document so that duplicates look the same everywhere.
    """
    return {
        "entity": {
            "entity_type": new.entity_type,
            "canonical_key": new.canonical_key,
            "version": new.version,
        },
        "applied_fields": list(event.applied_fields),
        "stale_fields": list(event.stale_fields),
        "delivery_key": event.delivery_key,
    }
