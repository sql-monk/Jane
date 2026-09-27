"""Bearer authentication (ADR-0005): ``none`` (local tests) or ``api_key`` with scopes.

``api_key``: keys are configured as SHA-256 hashes (``JANE_ORCHESTRATOR_API_KEYS``); the key value is never
stored. Scopes: ``orchestrator:read`` (GET), ``orchestrator:write`` (changes, runs),
``orchestrator:admin`` (platform limits, connections). ``jwt`` is reported but not enforced here yet.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

from fastapi import Request

from jane_kit.errors import Forbidden, Unauthenticated

__all__ = ["Principal", "authenticate"]

ANONYMOUS = "anonymous"


@dataclass(frozen=True)
class Principal:
    name: str
    scopes: frozenset[str]

    def require(self, scope: str) -> None:
        if scope not in self.scopes and "orchestrator:admin" not in self.scopes:
            raise Forbidden(f"scope {scope} required")


ALL_SCOPES = frozenset({"orchestrator:read", "orchestrator:write", "orchestrator:admin"})


def authenticate(request: Request, mode: str, keys: list[dict[str, Any]]) -> Principal:
    if mode == "none":
        return Principal(ANONYMOUS, ALL_SCOPES)
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise Unauthenticated("bearer token required", headers={"WWW-Authenticate": "Bearer"})
    if mode == "api_key":
        digest = hashlib.sha256(token.strip().encode()).hexdigest()
        for key in keys:
            if hmac.compare_digest(str(key.get("sha256", "")).lower(), digest):
                return Principal(str(key.get("name", "api-key")), frozenset(key.get("scopes") or []))
        raise Unauthenticated("invalid API key", headers={"WWW-Authenticate": "Bearer"})
    raise Unauthenticated(f"auth mode {mode} is not supported by this build")
