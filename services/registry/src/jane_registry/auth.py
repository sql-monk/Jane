"""Authentication and scopes (ADR-0005): ``Authorization: Bearer <token>``, implemented by ``jane_kit.auth``.

* ``auth_mode=none`` - every caller has every scope (local tests on loopback; the service logs a warning);
* ``auth_mode=api_key`` - keys from ``JANE_REGISTRY_API_KEYS`` (JSON) and/or ``JANE_REGISTRY_API_KEYS_FILE``:
  ``[{"name", "sha256" | "secret_ref", "scopes", "actor"}]`` - only hashes are kept (``secret_ref`` =
  ``env:VAR``/``file:/path`` is resolved once at start and hashed);
* ``auth_mode=jwt`` - RS256/ES256 tokens of an identity provider (``JANE_REGISTRY_JWT_*``); scopes from the
  ``scope`` claim, the actor from the ``actor`` claim (``human`` when absent).

Scopes (``jane_kit.auth_scopes.REGISTRY``, checked for every route): ``registry:read`` (GET),
``registry:write`` (create, publish, fork, test results, upstream ports, package settings),
``registry:approve`` (``POST .../status``).
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from fastapi import Request

from jane_kit.auth import AuthSettings, load_api_keys, principal_of
from jane_kit.errors import Forbidden

__all__ = ["ACTORS", "ALL_SCOPES", "Authenticator", "Principal", "check_actors"]

ALL_SCOPES = frozenset({"registry:read", "registry:write", "registry:approve"})
ACTORS = frozenset({"human", "llm", "import"})


@dataclass(frozen=True)
class Principal:
    name: str
    scopes: frozenset[str]
    actor: str = "human"
    """``provenance.created_by`` of what this caller creates: ``human`` (default), ``llm`` (the assistant's
    key) or ``import``. An ``llm`` caller can only publish ``created_by: llm`` versions."""


def check_actors(settings: AuthSettings) -> None:
    """Start-up check: ``actor`` of every configured key is one of :data:`ACTORS`."""
    if settings.auth_mode != "api_key":
        return
    for key in load_api_keys(settings):
        actor = key.attributes.get("actor", "human")
        if actor not in ACTORS:
            raise ValueError(f"api key {key.name!r}: actor must be one of {sorted(ACTORS)}")


class Authenticator:
    """Scope dependencies of the routes; authentication itself is jane-kit's middleware (``create_app``)."""

    def __init__(self, settings: AuthSettings) -> None:
        check_actors(settings)
        self.mode = settings.auth_mode

    @staticmethod
    def principal(request: Request) -> Principal:
        p = principal_of(request)
        actor = str(p.attributes.get("actor") or "human") if p.method != "none" else "human"
        if actor not in ACTORS:
            raise Forbidden(f"actor {actor!r} is not one of {sorted(ACTORS)}")
        scopes = ALL_SCOPES if p.method == "none" else p.scopes
        return Principal(p.name, frozenset(scopes), actor)

    def require(self, scope: str) -> Callable[[Request], Coroutine[Any, Any, Principal]]:
        async def dependency(request: Request) -> Principal:
            principal = self.principal(request)
            if scope not in principal.scopes:
                raise Forbidden(f"scope {scope} required")
            return principal

        return dependency
