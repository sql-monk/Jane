"""Cursor pagination per WP-00 conventions: ``?limit=&cursor=`` -> ``{"items": [...], "next_cursor": ... | null}``.

``limit`` above the service maximum is clamped (not rejected); there is no offset/page. Cursors are
opaque to clients: :func:`encode_cursor` wraps any JSON-serialisable position (e.g. the last sort
key) in URL-safe base64.
"""

from __future__ import annotations

import base64
import binascii
import json
from typing import Any

from pydantic import BaseModel, Field

from jane_kit.config import Limits
from jane_kit.errors import FieldError, ValidationFailed

__all__ = ["Page", "PageLimits", "clamp_limit", "decode_cursor", "encode_cursor"]


class PageLimits(Limits):
    default_page_size: int = Field(default=50, ge=1)
    max_page_size: int = Field(default=500, ge=1)


class Page[T](BaseModel):
    items: list[T]
    next_cursor: str | None = None


def clamp_limit(requested: int | None, limits: PageLimits | None = None) -> int:
    limits = limits or PageLimits()
    if requested is None:
        return min(limits.default_page_size, limits.max_page_size)
    return max(1, min(requested, limits.max_page_size))


def encode_cursor(position: Any) -> str:
    raw = json.dumps(position, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str) -> Any:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode()))
    except (binascii.Error, ValueError) as exc:
        raise ValidationFailed(
            "invalid cursor", errors=[FieldError(parameter="cursor", message="invalid cursor")]
        ) from exc
