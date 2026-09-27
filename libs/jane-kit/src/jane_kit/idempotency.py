"""Idempotent request handling by ``Idempotency-Key`` (TZ §11: a repeated technical delivery is a duplicate).

Semantics of the WP-00 contract (``common.yaml#/components/parameters/IdempotencyKey``):

* first request with a key runs the handler; the response is stored for
  ``transfer.idempotency_ttl_seconds``;
* same key + same request -> stored response with ``Idempotency-Replayed: true``, no new effect;
* same key + different request -> 422 ``idempotency_key_reused``;
* same key while the first request still runs -> 409 ``idempotency_in_progress`` (retryable);
* the key is 1-255 printable ASCII characters;
* if the handler raises, the key is released so the client can retry.

:class:`InMemoryIdempotencyStore` suits one instance and tests. Services running several instances
implement :class:`IdempotencyStore` on their own database (e.g. PostgreSQL ``INSERT ... ON CONFLICT
DO NOTHING``).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from pydantic import Field

from jane_kit.config import Limits
from jane_kit.errors import FieldError, JaneError, ValidationFailed

__all__ = [
    "IDEMPOTENCY_HEADER",
    "REPLAY_HEADER",
    "IdempotencyInProgress",
    "IdempotencyKeyReused",
    "IdempotencyLimits",
    "IdempotencyRecord",
    "IdempotencyStore",
    "InMemoryIdempotencyStore",
    "StoredResponse",
    "fingerprint",
    "idempotent",
    "run_idempotent",
]

IDEMPOTENCY_HEADER = "Idempotency-Key"
REPLAY_HEADER = "Idempotency-Replayed"
KEY_RE = re.compile(r"^[\x21-\x7E]{1,255}$")


class IdempotencyLimits(Limits):
    idempotency_ttl_seconds: int = Field(default=86_400, ge=60)
    """Contract ``limits.transfer.idempotency_ttl_seconds``: how long a key is remembered."""
    in_memory_max_entries: int = Field(default=10_000, ge=1)
    """Only :class:`InMemoryIdempotencyStore`: the oldest entries are evicted beyond this."""


class IdempotencyKeyReused(JaneError):
    code = "idempotency_key_reused"


class IdempotencyInProgress(JaneError):
    code = "idempotency_in_progress"


@dataclass(frozen=True)
class StoredResponse:
    status_code: int
    body: Any
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass
class IdempotencyRecord:
    key: str
    fingerprint: str
    state: Literal["in_progress", "completed"]
    expires_at: float
    response: StoredResponse | None = None


class IdempotencyStore(Protocol):
    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        """Atomically claim ``key``. Return ``None`` if claimed now, else the existing record."""
        ...

    async def complete(self, key: str, response: StoredResponse) -> None: ...

    async def release(self, key: str) -> None:
        """Forget an in-progress key (the handler failed; a retry must be possible)."""
        ...


class InMemoryIdempotencyStore:
    def __init__(self, limits: IdempotencyLimits | None = None, clock: Callable[[], float] = time.monotonic):
        self.limits = limits or IdempotencyLimits()
        self._clock = clock
        self._records: OrderedDict[str, IdempotencyRecord] = OrderedDict()
        self._lock = asyncio.Lock()

    def __len__(self) -> int:
        return len(self._records)

    def _evict(self, now: float) -> None:
        for key in [k for k, r in self._records.items() if r.expires_at <= now]:
            del self._records[key]
        while len(self._records) > self.limits.in_memory_max_entries:
            self._records.popitem(last=False)

    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        async with self._lock:
            now = self._clock()
            self._evict(now)
            existing = self._records.get(key)
            if existing is not None:
                return existing
            self._records[key] = IdempotencyRecord(key, fingerprint, "in_progress", now + ttl_s)
            self._evict(now)
            return None

    async def complete(self, key: str, response: StoredResponse) -> None:
        async with self._lock:
            record = self._records.get(key)
            if record is not None:
                record.state = "completed"
                record.response = response

    async def release(self, key: str) -> None:
        async with self._lock:
            record = self._records.get(key)
            if record is not None and record.state == "in_progress":
                del self._records[key]


def fingerprint(method: str, path: str, body: bytes, extra: Mapping[str, str] | None = None) -> str:
    h = hashlib.sha256()
    h.update(method.upper().encode())
    h.update(b"\0" + path.encode())
    h.update(b"\0" + body)
    if extra:
        h.update(b"\0" + json.dumps(dict(extra), sort_keys=True).encode())
    return h.hexdigest()


async def run_idempotent(
    store: IdempotencyStore,
    key: str,
    fp: str,
    handler: Callable[[], Awaitable[StoredResponse]],
    limits: IdempotencyLimits | None = None,
) -> tuple[StoredResponse, bool]:
    """Run ``handler`` once per key. Returns ``(response, replayed)``."""
    limits = limits or IdempotencyLimits()
    if not KEY_RE.match(key):
        raise ValidationFailed(
            f"{IDEMPOTENCY_HEADER} must be 1-255 printable ASCII characters",
            errors=[FieldError(parameter=IDEMPOTENCY_HEADER, message="invalid format")],
        )
    existing = await store.begin(key, fp, float(limits.idempotency_ttl_seconds))
    if existing is not None:
        if existing.fingerprint != fp:
            raise IdempotencyKeyReused("the key was used with a different request")
        if existing.state != "completed" or existing.response is None:
            raise IdempotencyInProgress("a request with this key is still running")
        return existing.response, True
    try:
        response = await handler()
    except BaseException:
        await store.release(key)
        raise
    await store.complete(key, response)
    return response, False


async def idempotent(
    request: Request,
    store: IdempotencyStore,
    handler: Callable[[], Awaitable[StoredResponse]],
    *,
    required: bool = True,
    limits: IdempotencyLimits | None = None,
) -> Response:
    """FastAPI helper: wrap an endpoint body so it honours ``Idempotency-Key``.

    A missing header is ``422 validation_failed`` (the contract marks the header required);
    ``required=False`` runs the handler directly instead.
    """
    key = request.headers.get(IDEMPOTENCY_HEADER)
    if key is None:
        if required:
            raise ValidationFailed(
                f"{IDEMPOTENCY_HEADER} header is required",
                errors=[FieldError(parameter=IDEMPOTENCY_HEADER, message="required")],
            )
        stored = await handler()
        return JSONResponse(stored.body, status_code=stored.status_code, headers=dict(stored.headers))
    fp = fingerprint(request.method, request.url.path, await request.body())
    stored, replayed = await run_idempotent(store, key, fp, handler, limits)
    headers = dict(stored.headers)
    if replayed:
        headers[REPLAY_HEADER] = "true"
    return JSONResponse(stored.body, status_code=stored.status_code, headers=headers)
