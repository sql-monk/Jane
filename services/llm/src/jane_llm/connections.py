"""Managed connections: secret reference resolution and secret-like value detection (ADR-0006).

Secret values are resolved only here, in the service's own environment, and are never returned by the
API, stored in the database or written to logs.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError
from jane_llm.providers.base import ResolvedConnection

_SECRET_KEY_RE = re.compile(r"(?i)(pass(word|wd)?|secret|token|api[_-]?key|credential|private[_-]?key|auth)")
_SECRET_VALUE_RES = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{16,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]
_ALLOWED_KEYS = {"responses"}  # fake scripts may legitimately contain arbitrary text


def resolve_ref(ref: str) -> str | None:
    """Value of ``env:VAR`` / ``file:<path>``; ``None`` if missing. ``vault:`` is not configured in v1."""
    if ref.startswith("env:"):
        return os.environ.get(ref[4:]) or None
    if ref.startswith("file:"):
        path = Path(ref[5:])
        try:
            return path.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None
    return None


def find_secret_like(params: dict[str, Any], prefix: str = "/params") -> list[FieldError]:
    """Pointers to values in ``params`` that look like secrets (they belong in ``secret_refs``)."""
    found: list[FieldError] = []

    def walk(value: Any, pointer: str, key: str | None) -> None:
        if key in _ALLOWED_KEYS:
            return
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, f"{pointer}/{str(k).replace('~', '~0').replace('/', '~1')}", str(k))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f"{pointer}/{i}", key)
        elif isinstance(value, str):
            if key is not None and _SECRET_KEY_RE.search(key) and value:
                found.append(FieldError(pointer=pointer, code="secret_key", message="use secret_refs"))
            elif any(r.search(value) for r in _SECRET_VALUE_RES):
                found.append(
                    FieldError(pointer=pointer, code="secret_value", message="value looks like a secret")
                )

    walk(params, prefix, None)
    return found


def resolve_connection(doc: dict[str, Any]) -> tuple[ResolvedConnection, dict[str, bool]]:
    """Resolve ``secret_refs`` of a stored connection. Returns the connection and, per secret, whether
    it was resolved (for ``POST /v1/connections/{id}/test``)."""
    values: dict[str, str] = {}
    resolved: dict[str, bool] = {}
    for name, ref in (doc.get("secret_refs") or {}).items():
        value = resolve_ref(str(ref))
        resolved[name] = value is not None
        if value is not None:
            values[name] = value
    conn = ResolvedConnection(
        connection_id=str(doc["connection_id"]),
        kind=str(doc["kind"]),
        params=dict(doc.get("params") or {}),
        secrets=values,
    )
    return conn, resolved
