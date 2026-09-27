"""Merge of an ``EntityRecord`` into the current state — a pure function (no I/O).

Semantics (``entity.schema.json``, TZ §6, §11):

1. a field in ``fields`` sets the value;
2. a field absent from ``fields`` and ``cleared`` is left unchanged (omission is not deletion);
3. a field in ``cleared`` is removed from ``fields`` and remembered in ``cleared_fields``;
4. every field (also a cleared one) remembers the observation order of its last change; an update of a
   field applies only if the record's order is strictly newer (``order_tuple``), otherwise the field is
   reported in ``stale`` and only the history keeps it;
5. the new snapshot always has ``version + 1`` (also for a stale-only update, whose fields equal the
   current ones) — the adapter commits it with compare-and-swap on the old version.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from jane_contracts.storage_adapter import EntitySnapshot, OrderKey, order_tuple

from .codec import parse_ts
from .keys import canonical_key

__all__ = ["InvalidRecord", "MergeResult", "merge", "order_of", "validate_record"]


class InvalidRecord(ValueError):
    """The record violates EntityRecord semantics (null value, field both set and cleared...)."""


@dataclass(frozen=True, slots=True)
class MergeResult:
    snapshot: EntitySnapshot
    applied: list[str]
    stale: list[str]

    @property
    def status(self) -> str:
        """``WriteAck.status`` for this merge."""
        if self.stale and self.applied:
            return "partially_stale"
        if self.stale:
            return "stale"
        return "written"


def order_of(record: Mapping[str, Any]) -> OrderKey:
    obs = record["observation"]
    seq = obs.get("sequence")
    return OrderKey(
        observed_at=parse_ts(obs["observed_at"]),
        observation_id=str(obs["observation_id"]),
        sequence=None if seq is None else int(seq),
    )


def validate_record(record: Mapping[str, Any]) -> None:
    fields = record.get("fields")
    if not isinstance(fields, Mapping):
        raise InvalidRecord("fields must be an object")
    nulls = sorted(name for name, value in fields.items() if value is None)
    if nulls:
        raise InvalidRecord(f"null is not a value, use 'cleared' to clear: {nulls}")
    cleared = list(record.get("cleared") or ())
    both = sorted(set(cleared) & set(fields))
    if both:
        raise InvalidRecord(f"fields are both set and cleared: {both}")
    if len(set(cleared)) != len(cleared):
        raise InvalidRecord("cleared contains duplicates")
    key = record.get("key")
    if not isinstance(key, Mapping) or not key.get("scope") or not key.get("natural"):
        raise InvalidRecord("key.scope and key.natural are required")


def merge(current: EntitySnapshot | None, record: Mapping[str, Any], *, now: datetime) -> MergeResult:
    validate_record(record)
    order = order_of(record)
    rank = order_tuple(order)
    fields: dict[str, Any] = dict(current.fields) if current else {}
    orders: dict[str, OrderKey] = dict(current.field_orders) if current else {}
    cleared: set[str] = set(current.cleared_fields) if current else set()
    applied: list[str] = []
    stale: list[str] = []

    def newer(name: str) -> bool:
        previous = orders.get(name)
        return previous is None or rank > order_tuple(previous)

    for name, value in record["fields"].items():
        if newer(name):
            fields[name] = value
            orders[name] = order
            cleared.discard(name)
            applied.append(name)
        else:
            stale.append(name)
    for name in record.get("cleared") or ():
        if newer(name):
            fields.pop(name, None)
            orders[name] = order
            cleared.add(name)
            applied.append(name)
        else:
            stale.append(name)

    snapshot = EntitySnapshot(
        entity_type=str(record["entity_type"]),
        canonical_key=current.canonical_key if current else canonical_key(record["key"]),
        key=dict(current.key) if current else dict(record["key"]),
        fields=fields,
        field_orders=orders,
        cleared_fields=frozenset(cleared),
        version=(current.version + 1) if current else 1,
        updated_at=now,
    )
    return MergeResult(snapshot=snapshot, applied=sorted(applied), stale=sorted(stale))
