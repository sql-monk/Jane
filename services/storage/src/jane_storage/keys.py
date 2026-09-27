"""Deterministic keys built by the storage core (contracts/docs/storage-adapter.md).

* canonical entity key: ``scope + '|' + natural`` serialized as JSON with sorted keys, no spaces
  (``entity.schema.json#/$defs/EntityKey``);
* object key of a RAW/result document:
  ``<source_id>/<yyyy>/<mm>/<dd>/<material_id>/<observation_id>.<ext>`` — filesystem safe on Windows
  and Linux (every character outside ``[A-Za-z0-9._-]`` becomes ``_``);
* delivery keys of the parts of one invocation.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

__all__ = [
    "NO_SOURCE",
    "canonical_key",
    "entity_delivery_key",
    "key_digest",
    "object_delivery_key",
    "object_id_for",
    "object_key",
    "safe_segment",
]

NO_SOURCE = "_standalone"
"""Source segment of object keys for materials without ``source.source_id`` (standalone use)."""

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]")
_WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def canonical_key(key: Mapping[str, Any]) -> str:
    """``shop-example|{"sku":"A-100"}`` for ``{"scope": "shop-example", "natural": {"sku": "A-100"}}``."""
    natural = json.dumps(key["natural"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{key['scope']}|{natural}"


def key_digest(value: str) -> str:
    """sha256 hex of a key; used for file/object names that must not depend on key characters."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_segment(value: str) -> str:
    """One path segment that is valid on Windows and Linux."""
    out = _UNSAFE.sub("_", value).strip(".") or "_"
    if out.split(".", 1)[0].lower() in _WINDOWS_RESERVED:
        out = f"_{out}"
    return out


def object_key(
    *, material_id: str, observation_id: str, source_id: str | None, fetched_at: datetime, ext: str
) -> str:
    ts = fetched_at.astimezone(UTC)
    return "/".join(
        (
            safe_segment(source_id or NO_SOURCE),
            f"{ts:%Y}",
            f"{ts:%m}",
            f"{ts:%d}",
            safe_segment(material_id),
            f"{safe_segment(observation_id)}.{ext}",
        )
    )


def object_id_for(object_key_: str) -> str:
    """Deterministic ``object_id`` (``Id`` pattern) of an object key; the same in every adapter."""
    return f"obj_{key_digest(object_key_)[:32]}"


def entity_delivery_key(delivery_key: str, index: int) -> str:
    """Delivery key of the ``index``-th entity (0-based, across all inputs) of an invocation."""
    return f"{delivery_key}#{index}"


def object_delivery_key(delivery_key: str, index: int, kind: str = "raw") -> str:
    """Delivery key of the ``index``-th object write: the first RAW uses the invocation key itself."""
    if kind == "raw" and index == 0:
        return delivery_key
    return f"{delivery_key}#{kind}{index}"
