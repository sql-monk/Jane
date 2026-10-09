"""Managed connections: secret reference policy and resolution, secret-like value detection (ADR-0006).

Secret values are resolved only here, in the service's own environment, and are never returned by the
API, stored in the database or written to logs.

Because a connection decides *where* a resolved secret is sent (``params.api_base``), a connection must not
be able to reference arbitrary process state or ship a secret to an arbitrary host. :class:`ConnectionPolicy`
(from :class:`~jane_llm.settings.Settings`) restricts:

* ``env:`` references to variables with a configured prefix (default ``JANE_SECRET_``);
* ``file:`` references to files inside a configured directory (default ``/run/secrets``), read through pinned
  path components;
* ``params.api_base`` to a configured allowlist of exact origins (default the official provider hosts; no
  userinfo, backslashes or whitespace).

The secret part is jane-kit's shared :class:`jane_kit.secrets.SecretPolicy` (R17), the same as in storage and
the collectors.

The policy is enforced when a connection is stored (422) **and** when it is resolved for a call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from jane_kit.errors import FieldError
from jane_kit.secrets import OriginAllowlist, SecretPolicy
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


def _parsable(url: str) -> bool:
    try:
        urlsplit(url.strip()).port  # noqa: B018 - a bad port ("...:99999", "...:abc") or bracket raises
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class ConnectionPolicy(SecretPolicy):
    """jane-kit's secret policy plus the allowed origins of ``params.api_base``."""

    api_base_allowlist: tuple[str, ...] = ("https://api.anthropic.com",)
    _api_bases: OriginAllowlist = field(init=False, repr=False, default=OriginAllowlist())

    def __post_init__(self) -> None:
        object.__setattr__(self, "_api_bases", OriginAllowlist(tuple(self.api_base_allowlist)))

    def api_base_error(self, api_base: Any) -> str | None:
        if api_base is None:
            return None
        allowed = f"api_base must be one of the allowed origins {sorted(self.api_base_allowlist)}"
        if not isinstance(api_base, str):
            return allowed
        if not _parsable(api_base):  # a validation error, not a 500
            return f"api_base is not a valid URL; {allowed}"
        return None if self._api_bases.allows(api_base.strip()) else allowed

    def violations(self, doc: Any, pointer: str = "/secret_refs") -> list[FieldError]:
        """Violations of a Connection document: its ``secret_refs`` and ``params.api_base``."""
        errors = super().violations((doc or {}).get("secret_refs"), pointer)
        params = (doc or {}).get("params") or {}
        if msg := self.api_base_error(params.get("api_base")):
            errors.append(FieldError(pointer="/params/api_base", code="api_base_not_allowed", message=msg))
        return errors


def resolve_ref(ref: str, policy: ConnectionPolicy) -> str | None:
    """Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing or not allowed."""
    return policy.resolve(ref)


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
