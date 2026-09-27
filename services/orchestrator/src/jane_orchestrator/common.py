"""Small helpers shared by the orchestrator modules: ids, time, hashing, JSON pointers."""

from __future__ import annotations

import hashlib
import os
import time
from datetime import UTC, datetime
from typing import Any

__all__ = ["delivery_key", "etag", "get_path", "new_id", "now", "parse_etag", "rfc3339"]

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_id(prefix: str) -> str:
    """Time-ordered opaque id (ULID layout: 48-bit ms timestamp + 80 random bits), e.g. ``run_01J9...``."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    chars = []
    for _ in range(26):
        chars.append(_CROCKFORD[value & 31])
        value >>= 5
    return f"{prefix}_{''.join(reversed(chars))}"


def now() -> datetime:
    return datetime.now(UTC)


def rfc3339(value: datetime | None) -> str | None:
    """RFC 3339 UTC with ``Z`` (contract convention)."""
    if value is None:
        return None
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def delivery_key(run_id: str, stage_id: str, item_key: str) -> str:
    """Deterministic delivery key (handler-invocation.schema.json ``Delivery``, ADR-0008 §5):
    ``sha256(run_id | stage_id | item_key)``. A retry of the same delivery has the same key."""
    return hashlib.sha256(f"{run_id}|{stage_id}|{item_key}".encode()).hexdigest()


def etag(version: int) -> str:
    return f'"v{version}"'


def parse_etag(value: str | None) -> int | None:
    """``"v7"`` / ``W/"v7"`` / ``v7`` -> 7; anything else -> None (never matches)."""
    if value is None:
        return None
    raw = value.strip()
    if raw.startswith("W/"):
        raw = raw[2:]
    raw = raw.strip('"')
    if raw.startswith("v") and raw[1:].isdigit():
        return int(raw[1:])
    return -1


def get_path(doc: Any, dotted: str) -> tuple[bool, Any]:
    """``(found, value)`` for a dotted path in nested dicts (``format.media_type``)."""
    node = doc
    for part in dotted.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return False, None
    return True, node
