"""Managed connections (``/v1/connections``, ADR-0006): the Telegram account the collector works as.

Only ``kind=telegram_account`` is accepted. Secret values never pass the API: ``secret_refs`` point to
``env:VAR`` or ``file:<path>`` in this service's environment (``vault:`` has no provider in v1 and is
reported as unresolved). Secrets are resolved right before a client is opened and are kept only in memory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError, JaneError, ValidationFailed

from .client import ResolvedAccount

__all__ = [
    "SUPPORTED_KINDS",
    "check_params",
    "connection_etag",
    "resolve_account",
    "resolve_secret",
    "resolved_map",
]

SUPPORTED_KINDS = frozenset({"telegram_account"})
_SECRET_KEY = re.compile(
    r"(pass(word|wd)?|secret|token|api[_-]?(key|hash)|authorization|cookie|private[_-]?key|credential|session|phone_code)",
    re.I,
)
_SECRET_VALUE = re.compile(r"^(bearer|basic)\s+\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)


def connection_etag(body: Mapping[str, Any]) -> str:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return '"' + hashlib.sha256(raw).hexdigest()[:32] + '"'


def _walk(value: Any, pointer: str) -> list[str]:
    hits: list[str] = []
    if isinstance(value, Mapping):
        for k, v in value.items():
            p = f"{pointer}/{k}"
            if _SECRET_KEY.search(str(k)) and isinstance(v, str) and v:
                hits.append(p)
            hits.extend(_walk(v, p))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            hits.extend(_walk(v, f"{pointer}/{i}"))
    elif isinstance(value, str) and _SECRET_VALUE.search(value):
        hits.append(pointer)
    return hits


def check_params(body: Mapping[str, Any]) -> None:
    """Reject other kinds and secret-looking values in ``params`` (``secret_detected``)."""
    if body.get("kind") not in SUPPORTED_KINDS:
        raise ValidationFailed(
            "telegram-collector uses only connections of kind telegram_account",
            errors=[FieldError(pointer="/kind", message="supported kinds: telegram_account")],
        )
    hits = _walk(body.get("params") or {}, "/params")
    if hits:
        raise JaneError(
            "params look like secrets; pass secrets only via secret_refs",
            code="secret_detected",
            errors=[FieldError(pointer=p, message="secret-like value") for p in hits],
        )


def resolve_secret(ref: str) -> str | None:
    scheme, _, target = ref.partition(":")
    if scheme == "env":
        return os.environ.get(target) or None
    if scheme == "file":
        path = Path(target)
        try:
            return (path.read_text(encoding="utf-8").strip() or None) if path.is_file() else None
        except OSError:
            return None
    return None  # vault: no provider configured in v1


def resolved_map(connection: Mapping[str, Any]) -> dict[str, bool]:
    return {
        name: resolve_secret(ref) is not None for name, ref in (connection.get("secret_refs") or {}).items()
    }


def resolve_account(connection: Mapping[str, Any] | None, pointer: str) -> ResolvedAccount:
    """Resolve every ``secret_ref``; an unresolvable one is a configuration error (422)."""
    if connection is None:
        return ResolvedAccount(connection_id=None, params={})
    secrets: dict[str, str] = {}
    missing: list[str] = []
    for name, ref in (connection.get("secret_refs") or {}).items():
        value = resolve_secret(ref)
        if value is None:
            missing.append(name)
        else:
            secrets[name] = value
    if missing:
        raise ValidationFailed(
            f"connection {connection.get('connection_id')}: secrets not resolvable in this collector: {missing}",
            errors=[FieldError(pointer=pointer, message=f"unresolved secret_refs: {', '.join(missing)}")],
        )
    return ResolvedAccount(
        connection_id=str(connection.get("connection_id")),
        params=dict(connection.get("params") or {}),
        secrets=secrets,
    )
