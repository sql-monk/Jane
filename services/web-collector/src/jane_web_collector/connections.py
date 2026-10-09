"""Managed connections (``/v1/connections``, ADR-0006) for sites that need HTTP authentication.

Only ``kind=http`` is used by the web collector. Secret values never pass the API: ``secret_refs`` point to
``env:VAR`` or ``file:<path>`` within operator-configured bounds (``vault:`` has no provider in v1 and is
rejected). How the resolved secrets are applied (service convention for ``params``, documented in README):

* ``params.auth_scheme = "bearer"`` + ``secret_refs.token`` -> ``Authorization: Bearer <token>``;
* ``params.auth_scheme = "basic"`` + ``secret_refs.username`` / ``secret_refs.password``;
* ``params.auth_scheme = "header"`` + ``params.header_name`` + ``secret_refs.value``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from jane_kit.errors import FieldError, JaneError, ValidationFailed
from jane_kit.rules import header_value_safe
from jane_kit.secrets import OriginAllowlist, SecretPolicy

__all__ = [
    "SUPPORTED_KINDS",
    "ConnectionPolicy",
    "auth_headers",
    "check_params",
    "connection_etag",
    "header_name_safe",
    "header_value_safe",
    "is_safe_rule_header",
]

SUPPORTED_KINDS = frozenset({"http"})
_SECRET_KEY = re.compile(
    r"(pass(word|wd)?|secret|token|api[_-]?key|authorization|cookie|private[_-]?key|credential)", re.I
)
_SECRET_VALUE = re.compile(r"^(bearer|basic)\s+\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)
_FORBIDDEN_DESTINATION_HEADERS = frozenset({"host", "content-length", "transfer-encoding"})
_SAFE_RULE_HEADERS = frozenset({"accept", "accept-language", "cache-control"})
_HEADER_NAME = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")


def is_safe_rule_header(name: str) -> bool:
    """Only these non-credential headers may come from a source-controlled rules package."""
    return name.lower() in _SAFE_RULE_HEADERS


def header_name_safe(value: object) -> bool:
    return isinstance(value, str) and _HEADER_NAME.fullmatch(value) is not None


@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy):
    """Operator-controlled secret and authenticated destination boundaries: jane-kit's shared secret policy
    (R17: ``env:`` prefix, ``file:`` directory with pinned reading) and the exact origins a credential may go to."""

    origin_allowlist: tuple[str, ...] = ()
    _origins: OriginAllowlist = field(init=False, repr=False, default=OriginAllowlist())

    def __post_init__(self) -> None:
        try:
            origins = OriginAllowlist(tuple(self.origin_allowlist))
        except ValueError:
            raise ValueError("connection_origin_allowlist entries must be exact HTTP(S) origins") from None
        object.__setattr__(self, "_origins", origins)

    def origin_allowed(self, url: str) -> bool:
        return self._origins.allows(url)

    def validate_refs(self, body: Mapping[str, Any]) -> None:
        errors = self.violations(body.get("secret_refs"))
        if errors:
            raise ValidationFailed("secret reference is not allowed", errors=errors)


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


def check_params(body: Mapping[str, Any], policy: ConnectionPolicy) -> None:
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
    params = body.get("params") or {}
    header_name = params.get("header_name")
    if header_name is not None and (
        not header_name_safe(header_name) or header_name.lower() in _FORBIDDEN_DESTINATION_HEADERS
    ):
        raise ValidationFailed(
            "header_name cannot control the HTTP destination or message framing",
            errors=[FieldError(pointer="/params/header_name", message="header is not allowed")],
        )
    policy.validate_refs(body)


def auth_headers(connection: Mapping[str, Any], policy: ConnectionPolicy) -> dict[str, str]:
    policy.validate_refs(connection)  # also rejects unsafe records written before the policy existed
    params = connection.get("params") or {}
    refs = connection.get("secret_refs") or {}
    scheme = str(params.get("auth_scheme", "")).lower()

    def secret(name: str) -> str:
        value = policy.resolve(refs[name]) if name in refs else None
        if value is None:
            raise ValidationFailed(
                f"connection {connection.get('connection_id')}: secret {name} is not resolvable",
                errors=[FieldError(pointer=f"/secret_refs/{name}", message="unresolved")],
            )
        if not header_value_safe(value):
            raise ValidationFailed(
                "connection secret cannot be used as an HTTP header",
                errors=[FieldError(pointer=f"/secret_refs/{name}", message="invalid HTTP header value")],
            )
        return value

    if scheme == "bearer":
        return {"Authorization": f"Bearer {secret('token')}"}
    if scheme == "basic":
        pair = f"{secret('username')}:{secret('password')}".encode()
        return {"Authorization": "Basic " + base64.b64encode(pair).decode()}
    if scheme == "header" and params.get("header_name"):
        if (
            not header_name_safe(params["header_name"])
            or params["header_name"].lower() in _FORBIDDEN_DESTINATION_HEADERS
        ):
            raise ValidationFailed(
                "header_name cannot control the HTTP destination or message framing",
                errors=[FieldError(pointer="/params/header_name", message="header is not allowed")],
            )
        return {str(params["header_name"]): secret("value")}
    return {}
