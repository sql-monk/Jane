"""Managed connections (``/v1/connections``, ADR-0006): the Telegram account the collector works as.

Only ``kind=telegram_account`` is accepted. Secret values never pass the API: ``secret_refs`` point into this
service's environment and are resolved right before a client is opened (kept only in memory).

Secret policy (coordinator decision, same as WP-10 ``services/llm``): a connection decides *where* a resolved
secret goes, so the collector restricts it:

* ``env:VAR`` — only variables starting with ``JANE_TELEGRAM_COLLECTOR_SECRET_ENV_PREFIX`` (default ``JANE_SECRET_``);
* ``file:<path>`` — only inside ``JANE_TELEGRAM_COLLECTOR_SECRET_FILES_DIR`` (default ``/run/secrets``; the path is
  resolved first, so ``..`` does not escape); ``vault:`` is disabled;
* host-like ``params`` (``server``, ``host``, ``proxy_host``, ``proxy``, ``api_base``, ``dc_address``) — only hosts
  from ``JANE_TELEGRAM_COLLECTOR_TELEGRAM_HOST_ALLOWLIST`` (default empty: such params are rejected).

Violations: 422 on ``PUT /v1/connections``; a connection stored bypassing the API gets no secrets and is rejected
(422) when a collection or fetch would use it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jane_kit.errors import FieldError, JaneError, ValidationFailed

from .client import ResolvedAccount

__all__ = [
    "HOST_PARAMS",
    "SUPPORTED_KINDS",
    "ConnectionPolicy",
    "check_params",
    "connection_etag",
    "resolve_account",
    "resolved_map",
]

SUPPORTED_KINDS = frozenset({"telegram_account"})
HOST_PARAMS = ("server", "host", "proxy_host", "proxy", "api_base", "dc_address")
_SECRET_KEY = re.compile(
    r"(pass(word|wd)?|secret|token|api[_-]?(key|hash)|authorization|cookie|private[_-]?key|credential|session|phone_code)",
    re.I,
)
_SECRET_VALUE = re.compile(r"^(bearer|basic)\s+\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)


def _host(value: str) -> str:
    text = value.strip()
    parts = urlsplit(text if "://" in text else f"//{text}")
    return (parts.hostname or "").lower()


@dataclass(frozen=True)
class ConnectionPolicy:
    env_prefix: str = "JANE_SECRET_"
    files_dir: Path | None = Path("/run/secrets")
    host_allowlist: Sequence[str] = ()

    def ref_error(self, ref: str) -> str | None:
        """Why a secret reference is not allowed (``None`` if allowed)."""
        if ref.startswith("env:"):
            if not self.env_prefix or not ref[4:].startswith(self.env_prefix):
                return f"env: references must name variables starting with {self.env_prefix!r}"
            return None
        if ref.startswith("file:"):
            if self.files_dir is None:
                return "file: references are disabled"
            try:
                path = Path(ref[5:]).resolve()
                base = self.files_dir.resolve()
            except (OSError, RuntimeError):
                return "file: reference is not a valid path"
            if not path.is_relative_to(base):
                return f"file: references must point inside {self.files_dir}"
            return None
        if ref.startswith("vault:"):
            return "vault: references are not configured in this service"
        return "unknown secret reference scheme"

    def host_error(self, value: Any) -> str | None:
        allowed = {h.lower() for h in self.host_allowlist}
        if not isinstance(value, str) or _host(value) not in allowed:
            return f"host must be one of the allowed Telegram hosts {sorted(allowed)}"
        return None

    def violations(self, doc: Mapping[str, Any]) -> list[FieldError]:
        errors = []
        for name, ref in (doc.get("secret_refs") or {}).items():
            if msg := self.ref_error(str(ref)):
                errors.append(
                    FieldError(pointer=f"/secret_refs/{name}", code="secret_ref_not_allowed", message=msg)
                )
        params = doc.get("params") or {}
        for key in HOST_PARAMS:
            if key in params and (msg := self.host_error(params[key])):
                errors.append(FieldError(pointer=f"/params/{key}", code="host_not_allowed", message=msg))
        return errors

    def resolve(self, ref: str) -> str | None:
        """Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing or not allowed."""
        if self.ref_error(ref) is not None:
            return None
        if ref.startswith("env:"):
            return os.environ.get(ref[4:]) or None
        try:
            return Path(ref[5:]).read_text(encoding="utf-8").strip() or None
        except OSError:
            return None


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
    """Reject other kinds, secret-looking ``params`` (``secret_detected``) and policy violations (422)."""
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
    violations = policy.violations(body)
    if violations:
        raise ValidationFailed("connection violates the secret policy of this collector", errors=violations)


def resolved_map(connection: Mapping[str, Any], policy: ConnectionPolicy) -> dict[str, bool]:
    return {
        name: policy.resolve(ref) is not None for name, ref in (connection.get("secret_refs") or {}).items()
    }


def resolve_account(
    connection: Mapping[str, Any] | None, pointer: str, policy: ConnectionPolicy
) -> ResolvedAccount:
    """Resolve every ``secret_ref``; a policy violation or an unresolvable reference is a configuration error (422)."""
    if connection is None:
        return ResolvedAccount(connection_id=None, params={})
    violations = policy.violations(connection)
    if violations:
        raise ValidationFailed(
            f"connection {connection.get('connection_id')} violates the secret policy of this collector",
            errors=[
                FieldError(pointer=pointer, code=v.code, message=f"{v.pointer}: {v.message}")
                for v in violations
            ],
        )
    secrets: dict[str, str] = {}
    missing: list[str] = []
    for name, ref in (connection.get("secret_refs") or {}).items():
        value = policy.resolve(ref)
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
