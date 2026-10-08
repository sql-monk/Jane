"""Bearer authentication (ADR-0005) of the orchestrator, implemented by ``jane_kit.auth``.

Modes ``none`` (local tests on loopback), ``api_key`` (``JANE_ORCHESTRATOR_API_KEYS`` /
``JANE_ORCHESTRATOR_API_KEYS_FILE``: ``[{"name", "sha256" | "secret_ref", "scopes"}]``, only hashes kept) and
``jwt`` (``JANE_ORCHESTRATOR_JWT_*``). jane-kit's middleware authenticates every request (401) and checks the
scope table ``jane_kit.auth_scopes.ORCHESTRATOR`` (403); the handlers call :func:`caller` for the principal's
name (audit, ``requested_by``). Scopes: ``orchestrator:read`` (GET), ``orchestrator:write`` (changes, runs),
``orchestrator:admin`` (platform limits, connections; also grants read and write).
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from jane_kit.auth import principal_of
from jane_kit.errors import Forbidden

__all__ = ["ADMIN", "ALL_SCOPES", "Principal", "caller"]

ADMIN = "orchestrator:admin"
ALL_SCOPES = frozenset({"orchestrator:read", "orchestrator:write", ADMIN})


@dataclass(frozen=True)
class Principal:
    name: str
    scopes: frozenset[str]

    def require(self, scope: str) -> None:
        if scope not in self.scopes and ADMIN not in self.scopes:
            raise Forbidden(f"scope {scope} required")


def caller(request: Request, scope: str) -> Principal:
    """The authenticated caller of this request with ``scope`` (or ``orchestrator:admin``)."""
    p = principal_of(request)
    principal = Principal(p.name, ALL_SCOPES if p.method == "none" else frozenset(p.scopes))
    principal.require(scope)
    return principal
