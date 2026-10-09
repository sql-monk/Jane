"""Caller-context claim tokens, separate from the process-wide heartbeat registry."""

from __future__ import annotations

import threading
from collections.abc import Mapping
from contextvars import ContextVar


class ClaimTokens:
    def __init__(self) -> None:
        self._context: ContextVar[Mapping[str, str] | None] = ContextVar("idempotency_claims", default=None)
        self._active: set[str] = set()
        self._lock = threading.Lock()

    def bind(self, key: str, token: str) -> None:
        # Contexts inherit values. Copy on every change so child requests cannot mutate a parent's claims.
        claims = dict(self._context.get() or {})
        claims[key] = token
        self._context.set(claims)
        with self._lock:
            self._active.add(token)

    def take(self, key: str) -> str | None:
        """Capture the caller's token before dispatching a DB write to a worker thread."""
        claims = dict(self._context.get() or {})
        token = claims.pop(key, None)
        self._context.set(claims)
        if token is not None:
            with self._lock:
                self._active.discard(token)
        return token

    def active(self) -> list[str]:
        """A background heartbeat must see every live request, regardless of its own context."""
        with self._lock:
            return list(self._active)
