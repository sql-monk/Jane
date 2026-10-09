"""Shared ``IdempotencyStore`` / ``JobStore`` implementations on a service's own database (R17).

* :mod:`jane_kit.stores.postgres` - :class:`~jane_kit.stores.postgres.PgIdempotencyStore`,
  :class:`~jane_kit.stores.postgres.PgJobStore` (needs ``psycopg``: ``jane-kit[postgres]``);
* :mod:`jane_kit.stores.sqlite` - :class:`~jane_kit.stores.sqlite.SqliteIdempotencyStore`,
  :class:`~jane_kit.stores.sqlite.SqliteJobStore`, :class:`~jane_kit.stores.sqlite.SqliteWorkJobStore`.

The in-memory stores stay in :mod:`jane_kit.idempotency` / :mod:`jane_kit.jobs` (one instance, tests). Every
store keeps the contract semantics (same key + same request -> stored response, other request -> 422, still
running -> 409; job statuses and cancellation) and the write rules of :func:`jane_kit.jobs.decide_save`.

Leases are renewed by the instance's heartbeat (:func:`heartbeat_loop` with :class:`LeaseLimits` or the
service's own lease settings); the data of each service stays in its own database (ADR-0009).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from pydantic import Field

from jane_kit.config import Limits

__all__ = ["LeaseLimits", "heartbeat_loop"]

log = logging.getLogger(__name__)


class LeaseLimits(Limits):
    """Leases of the shared stores (one group per service, e.g. ``limits.state``)."""

    in_progress_lease_ms: int = Field(default=900_000, ge=1_000)
    """An ``Idempotency-Key`` claim not renewed for this long (its instance stopped) can be claimed again."""
    job_lease_ms: int = Field(default=60_000, ge=1_000)
    """A job whose instance did not renew its lease for this long ends ``failed`` (retryable)."""
    heartbeat_interval_ms: int = Field(default=15_000, ge=100)
    """How often an instance renews its leases (keep well below both leases)."""


async def heartbeat_loop(
    beats: Iterable[Callable[[], Awaitable[Any]]], interval_s: float, *, name: str = "store"
) -> None:
    """Call every ``beat`` (``store.heartbeat``, ``store.gc``...) each ``interval_s`` until cancelled; a failed
    beat is logged and retried at the next tick (the lease covers a few missed beats)."""
    calls = list(beats)
    while True:
        await asyncio.sleep(interval_s)
        for beat in calls:
            try:
                await beat()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.warning("%s heartbeat failed", name, exc_info=True)
