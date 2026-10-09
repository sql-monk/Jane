"""Per-host politeness shared by the instances of the Web Collector that share one state store (R15).

:mod:`.host_limits` keeps the per-host schedule of one process; several instances on one node with one
``STATE_DIR`` (one SQLite file) would still reach a host N times as often. :class:`SharedHosts` extends the
schedule of every host into the shared state store, so the host sees one polite client for the whole platform
(all collections and one-shot fetches of all those instances):

* **who uses the host** (``host_users``): every instance registers the strictest interval and the smallest
  parallelism of its own sessions on the host; a registration expires ``collector.shared_host_ttl_seconds`` after
  its last request (a killed instance stops counting) and is removed when the host becomes idle in the instance;
* **parallelism** (``host_slots``): at most the smallest registered ``max_parallel_fetches_per_host`` requests
  of all instances are in flight; a slot of a killed instance expires after the same TTL;
* **fairness** (``host_waiters``): requests that wait for a slot queue in arrival order across the instances; a
  waiting request re-checks every ``collector.shared_host_poll_ms`` and takes a slot only when no older waiter is
  ahead of it for the free slots, so a busy instance cannot starve another one;
* **request starts** (``host_schedule``): together with the slot, a request reserves its start at
  ``max(now, last start + the largest registered interval, Retry-After)`` and sleeps until then (the slot is
  taken after the process' own interval, so it is held only for that short sleep and the request). A request
  cancelled while sleeping gives the slot back and leaves a gap (slower, never faster);
* ``Retry-After`` from the source delays every instance (``host_schedule.not_before``).

Times are wall-clock (``time.time()``) because they are compared across processes. Instances with different
state stores do not coordinate (separate collectors, v1 is single node: ADR-0007). A busy store (another
process holding the SQLite lock longer than ``STATE_BUSY_TIMEOUT_MS``) never fails a request: the request waits
and tries again; the per-process limits keep applying meanwhile.
"""

from __future__ import annotations

import asyncio
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass

from .state import StateStore

__all__ = ["SharedHosts"]

log = logging.getLogger(__name__)


@dataclass
class SharedHosts:
    """Cross-instance part of the per-host limits, kept in the shared :class:`~.state.StateStore`."""

    state: StateStore
    instance_id: str
    poll_s: float
    """``collector.shared_host_poll_ms`` / 1000: re-check of a host whose slots other instances hold."""
    ttl_s: float
    """``collector.shared_host_ttl_seconds``: a registration or slot not renewed or released for this long expires."""

    async def start(self, host: str, *, interval: float, parallel: int) -> str:
        """Register this instance's limits on ``host`` (its strictest ``interval`` and smallest ``parallel``), wait
        in line for a slot of the platform, reserve the next start and sleep until it. Returns the slot token:
        give it back with :meth:`release` when the request is over."""
        token = uuid.uuid4().hex
        try:
            while True:
                try:
                    start = self.state.host_take_slot(
                        host, self.instance_id, token, interval=interval, parallel=parallel, ttl=self.ttl_s
                    )
                except sqlite3.OperationalError:
                    log.warning("shared host limits: state store busy, retrying", extra={"host": host})
                    start = None
                if start is not None:
                    break
                await asyncio.sleep(self.poll_s)
            delay = start - time.time()
            if delay > 0:
                await asyncio.sleep(delay)
        except (
            BaseException
        ):  # cancelled while waiting in line or for the start: leave the line, free the slot
            self.release(host, token)
            raise
        return token

    def release(self, host: str, token: str) -> None:
        """Give back the slot (or the place in line) of ``token``."""
        try:
            self.state.host_release_slot(host, token)
        except sqlite3.OperationalError:  # the slot expires after ttl_s anyway
            log.warning("shared host limits: slot not released, it expires", extra={"host": host})

    def push_back(self, host: str, seconds: float) -> None:
        """``Retry-After``: no instance starts a request to ``host`` before ``now + seconds``."""
        try:
            self.state.host_push_back(host, time.time() + seconds)
        except sqlite3.OperationalError:
            log.warning("shared host limits: Retry-After not shared", extra={"host": host})

    def leave(self, host: str) -> None:
        """This instance no longer uses ``host``: its limits stop applying to the other instances."""
        try:
            self.state.host_leave(host, self.instance_id)
        except sqlite3.OperationalError:  # the registration expires after ttl_s anyway
            log.warning("shared host limits: registration not removed, it expires", extra={"host": host})
