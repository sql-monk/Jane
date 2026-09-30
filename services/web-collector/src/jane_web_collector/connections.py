"""Managed connections (``/v1/connections``, ADR-0006) for sites that need HTTP authentication.

Only ``kind=http`` is used by the web collector. Secret values never pass the API: ``secret_refs`` point to
``env:VAR`` or ``file:<path>`` in this service's environment (``vault:`` has no provider in v1 and is reported
as unresolved). How the resolved secrets are applied (service convention for ``params``, documented in README):

* ``params.auth_scheme = "bearer"`` + ``secret_refs.token`` -> ``Authorization: Bearer <token>``;
* ``params.auth_scheme = "basic"`` + ``secret_refs.username`` / ``secret_refs.password``;
* ``params.auth_scheme = "header"`` + ``params.header_name`` + ``secret_refs.value``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError, JaneError, ValidationFailed

__all__ = ["SUPPORTED_KINDS", "auth_headers", "check_params", "connection_etag", "resolve_secret"]

SUPPORTED_KINDS = frozenset({"http"})
_SECRET_KEY = re.compile(
    r"(pass(word|wd)?|secret|token|api[_-]?key|authorization|cookie|private[_-]?key|credential)", re.I
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
    """Reject non-http kinds and secret-looking values in ``params`` (``secret_detected``)."""
    if body.get("kind") not in SUPPORTED_KINDS:
        raise ValidationFailed(
            "web-collector uses only connections of kind http",
            errors=[FieldError(pointer="/kind", message="supported kinds: http")],
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
        return os.environ.get(target)
    if scheme == "file":
        path = Path(target)
        try:
            return path.read_text(encoding="utf-8").strip() if path.is_file() else None
        except OSError:
            return None
    return None  # vault: no provider configured in v1


def auth_headers(connection: Mapping[str, Any]) -> dict[str, str]:
    params = connection.get("params") or {}
    refs = connection.get("secret_refs") or {}
    scheme = str(params.get("auth_scheme", "")).lower()

    def secret(name: str) -> str:
        value = resolve_secret(refs[name]) if name in refs else None
        if value is None:
            raise ValidationFailed(
                f"connection {connection.get('connection_id')}: secret {name} is not resolvable",
                errors=[FieldError(pointer=f"/secret_refs/{name}", message="unresolved")],
            )
        return value

    if scheme == "bearer":
        return {"Authorization": f"Bearer {secret('token')}"}
    if scheme == "basic":
        pair = f"{secret('username')}:{secret('password')}".encode()
        return {"Authorization": "Basic " + base64.b64encode(pair).decode()}
    if scheme == "header" and params.get("header_name"):
        return {str(params["header_name"]): secret("value")}
    return {}
