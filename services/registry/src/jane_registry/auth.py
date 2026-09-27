"""Authentication and scopes (ADR-0005): ``Authorization: Bearer <token>``.

* ``auth_mode=none`` - every caller has every scope (local tests; the service logs a warning);
* ``auth_mode=api_key`` - keys from ``JANE_REGISTRY_API_KEYS_FILE``: ``[{"name", "sha256", "scopes"}]``
  where ``sha256`` is the hex digest of the key (the keys themselves are never stored);
* ``auth_mode=jwt`` - not implemented in this version (the service refuses to start).

Scopes: ``registry:read`` (GET), ``registry:write`` (create, publish, fork, test results, upstream
ports, package settings), ``registry:approve`` (``POST .../status``).
"""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import Request

from jane_kit.errors import Forbidden, Unauthenticated

__all__ = ["ALL_SCOPES", "ApiKey", "Authenticator", "Principal"]

ALL_SCOPES = frozenset({"registry:read", "registry:write", "registry:approve"})


@dataclass(frozen=True)
class Principal:
    name: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class ApiKey:
    name: str
    sha256: str
    scopes: frozenset[str]


def load_api_keys(path: Path) -> list[ApiKey]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return [ApiKey(str(k["name"]), str(k["sha256"]).lower(), frozenset(k.get("scopes") or [])) for k in doc]


class Authenticator:
    def __init__(self, mode: str, keys: list[ApiKey] | None = None) -> None:
        if mode == "jwt":
            raise ValueError("auth_mode=jwt is not implemented by the registry yet; use api_key")
        self.mode = mode
        self.keys = keys or []

    def principal(self, request: Request) -> Principal:
        if self.mode == "none":
            return Principal("anonymous", ALL_SCOPES)
        header = request.headers.get("authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise Unauthenticated("missing bearer token", headers={"WWW-Authenticate": "Bearer"})
        digest = hashlib.sha256(token.strip().encode()).hexdigest()
        for key in self.keys:
            if hmac.compare_digest(key.sha256, digest):
                return Principal(key.name, key.scopes)
        raise Unauthenticated("invalid token", headers={"WWW-Authenticate": "Bearer"})

    def require(self, scope: str) -> Callable[[Request], Coroutine[Any, Any, Principal]]:
        async def dependency(request: Request) -> Principal:
            principal = self.principal(request)
            if scope not in principal.scopes:
                raise Forbidden(f"scope {scope} is required")
            return principal

        return dependency
