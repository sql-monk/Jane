"""Managed connections: secret reference policy and resolution, secret-like value detection (ADR-0006).

Secret values are resolved only here, in the service's own environment, and are never returned by the
API, stored in the database or written to logs.

Because a connection decides *where* a resolved secret is sent (``params.api_base``), a connection must not
be able to reference arbitrary process state or ship a secret to an arbitrary host. :class:`ConnectionPolicy`
(from :class:`~jane_llm.settings.Settings`) restricts:

* ``env:`` references to variables with a configured prefix (default ``JANE_SECRET_``);
* ``file:`` references to files inside a configured directory (default ``/run/secrets``);
* ``params.api_base`` to a configured allowlist of origins (default the official provider hosts).

The policy is enforced when a connection is stored (422) **and** when it is resolved for a call.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

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
FAKE_SCRIPTS_KEY = "responses"
"""Scripts of the ``fake`` provider may contain arbitrary text; exempt only when ``params.provider == "fake"``."""


def origin(url: str) -> str:
    parts = urlsplit(url.strip())
    port = f":{parts.port}" if parts.port else ""
    return f"{parts.scheme.lower()}://{(parts.hostname or '').lower()}{port}"


@dataclass(frozen=True)
class ConnectionPolicy:
    env_prefix: str = "JANE_SECRET_"
    files_dir: Path | None = Path("/run/secrets")
    api_base_allowlist: tuple[str, ...] = ("https://api.anthropic.com",)
    _origins: frozenset[str] = field(init=False, repr=False, default=frozenset())

    def __post_init__(self) -> None:
        object.__setattr__(self, "_origins", frozenset(origin(u) for u in self.api_base_allowlist))

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

    def api_base_error(self, api_base: Any) -> str | None:
        if api_base is None:
            return None
        if not isinstance(api_base, str) or origin(api_base) not in self._origins:
            return f"api_base must be one of the allowed origins {sorted(self._origins)}"
        return None

    def violations(self, doc: dict[str, Any]) -> list[FieldError]:
        errors = []
        for name, ref in (doc.get("secret_refs") or {}).items():
            if msg := self.ref_error(str(ref)):
                errors.append(
                    FieldError(pointer=f"/secret_refs/{name}", code="secret_ref_not_allowed", message=msg)
                )
        params = doc.get("params") or {}
        if msg := self.api_base_error(params.get("api_base")):
            errors.append(FieldError(pointer="/params/api_base", code="api_base_not_allowed", message=msg))
        return errors


def resolve_ref(ref: str, policy: ConnectionPolicy) -> str | None:
    """Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing or not allowed."""
    if policy.ref_error(ref) is not None:
        return None
    if ref.startswith("env:"):
        return os.environ.get(ref[4:]) or None
    if ref.startswith("file:"):
        try:
            return Path(ref[5:]).read_text(encoding="utf-8").strip() or None
        except OSError:
            return None
    return None


def find_secret_like(params: dict[str, Any], prefix: str = "/params") -> list[FieldError]:
    """Pointers to values in ``params`` that look like secrets (they belong in ``secret_refs``)."""
    found: list[FieldError] = []
    exempt = {FAKE_SCRIPTS_KEY} if params.get("provider") == "fake" else set()

    def walk(value: Any, pointer: str, key: str | None, depth: int) -> None:
        if depth == 1 and key in exempt:
            return
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, f"{pointer}/{str(k).replace('~', '~0').replace('/', '~1')}", str(k), depth + 1)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f"{pointer}/{i}", key, depth)
        elif isinstance(value, str):
            if key is not None and _SECRET_KEY_RE.search(key) and value:
                found.append(FieldError(pointer=pointer, code="secret_key", message="use secret_refs"))
            elif any(r.search(value) for r in _SECRET_VALUE_RES):
                found.append(
                    FieldError(pointer=pointer, code="secret_value", message="value looks like a secret")
                )

    walk(params, prefix, None, 0)
    return found


def resolve_connection(
    doc: dict[str, Any], policy: ConnectionPolicy
) -> tuple[ResolvedConnection, dict[str, bool]]:
    """Resolve ``secret_refs`` of a stored connection under ``policy``. Returns the connection and, per
    secret, whether it was resolved (for ``POST /v1/connections/{id}/test``). A connection whose
    ``api_base`` is not allowed gets no secrets at all."""
    values: dict[str, str] = {}
    resolved: dict[str, bool] = {}
    api_base_ok = policy.api_base_error((doc.get("params") or {}).get("api_base")) is None
    for name, ref in (doc.get("secret_refs") or {}).items():
        value = resolve_ref(str(ref), policy) if api_base_ok else None
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
