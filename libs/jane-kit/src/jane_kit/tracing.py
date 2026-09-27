"""W3C Trace Context (``traceparent``): continue the caller's trace, pass it on (skill jane-contracts §11)."""

from __future__ import annotations

import re
import secrets

__all__ = ["TRACEPARENT", "child_traceparent", "new_trace_id", "parse_traceparent"]

TRACEPARENT = "traceparent"
_RE = re.compile(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")


def new_trace_id() -> str:
    return secrets.token_hex(16)


def parse_traceparent(value: str | None) -> str | None:
    """Trace id from a valid ``traceparent`` header, else ``None``."""
    if not value:
        return None
    m = _RE.match(value.strip().lower())
    if not m or m.group(2) == "0" * 32 or m.group(3) == "0" * 16:
        return None
    return m.group(2)


def child_traceparent(trace_id: str) -> str:
    """``traceparent`` for an outgoing call within ``trace_id`` (new span id, sampled)."""
    return f"00-{trace_id}-{secrets.token_hex(8)}-01"
