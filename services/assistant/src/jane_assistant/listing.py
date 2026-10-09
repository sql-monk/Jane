"""Positions and cursors of the list operations (``listOnboardingSessions``, ``listImprovementRuns``).

A list is ordered newest first by ``(created_at, id)``; a cursor is the opaque form of the position of the last item
of a page (``jane_kit.pagination.encode_cursor``). Its time is always written and read in one fixed UTC format with
microseconds, so the position compares the same way in memory and in PostgreSQL (``timestamptz``); anything else -
garbage, a naive time, another format, an id that is no service id - is ``validation_failed`` (422), never a server
error.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from jane_kit.errors import FieldError, ValidationFailed
from jane_kit.pagination import decode_cursor, encode_cursor

__all__ = ["CURSOR_TIME", "Position", "decode_position", "encode_position", "now_text", "parse_time"]

Position = tuple[datetime, str]
CURSOR_TIME = "%Y-%m-%dT%H:%M:%S.%fZ"
"""The time of a cursor (UTC, microseconds) - also how sessions write their ``created_at``."""
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")  # contract ``Id``
_TIME_FORMATS = (CURSOR_TIME, "%Y-%m-%dT%H:%M:%SZ")  # stored sessions before WP-15 have whole seconds


def now_text() -> str:
    return datetime.now(UTC).strftime(CURSOR_TIME)


def parse_time(value: str) -> datetime:
    """A stored ``created_at`` (``...Z``, with or without microseconds) as an aware UTC time; ``ValueError`` else."""
    for fmt in _TIME_FORMATS:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    raise ValueError(f"not a UTC time {value!r}")


def encode_position(position: Position) -> str:
    return encode_cursor([position[0].astimezone(UTC).strftime(CURSOR_TIME), position[1]])


def decode_position(cursor: str | None) -> Position | None:
    if cursor is None:
        return None
    value = decode_cursor(cursor)  # not base64 JSON -> 422 already
    if isinstance(value, list) and len(value) == 2 and all(isinstance(v, str) for v in value):
        try:
            when = datetime.strptime(value[0], CURSOR_TIME).replace(tzinfo=UTC)
        except ValueError:
            when = None
        if when is not None and _ID.match(value[1]):
            return when, value[1]
    raise ValidationFailed(
        "invalid cursor", errors=[FieldError(parameter="cursor", message="invalid cursor")]
    )
