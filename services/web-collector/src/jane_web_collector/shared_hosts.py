"""Per-host politeness shared by the instances of the Web Collector that share one state store (R15).

:mod:`.host_limits` keeps the per-host schedule of one process; several instances on one node with one
``STATE_DIR`` (one SQLite file) would still reach a host N times as often. :class:`SharedHosts` extends the
schedule of every host into the shared state store, so the host sees one polite client for the whole platform
(all collections and one-shot fetches of all those instances):

* **who uses the host** (``host_users``): every instance registers the strictest interval and the smallest
  parallelism of its own sessions on the host, from its first request there until the host becomes idle in the
  instance;
* **parallelism** (``host_slots``): at most the smallest registered ``max_parallel_fetches_per_host`` requests
  of all instances are in flight;
* **fairness** (``host_waiters``): requests that wait for a slot queue in arrival order across the instances; a
  waiting request re-checks every ``collector.shared_host_poll_ms`` and takes a slot only when no older waiter is
  ahead of it for the free slots, so a busy instance cannot starve another one;
* **request starts** (``host_schedule``): a request takes its slot only when it may start at once - the largest
  registered interval after the previous start of any instance has passed, and so has ``Retry-After``; the first
  request in line sleeps until then **without** a slot. A slot is held only while the request is in flight;
* ``Retry-After`` from the source delays every instance (``host_schedule.not_before``).

**Liveness** (review 1 of WP-16): while an instance holds a registration, a slot or a place in line, a renewal
task extends them every ``collector.shared_host_ttl_seconds / 3`` - also during a long download, a ``Retry-After``
of up to ``collector.max_retry_after_seconds`` or a ``Crawl-delay`` longer than the TTL. Only an instance that
died stops renewing: its rows expire ``collector.shared_host_ttl_seconds`` after its last renewal and stop limiting
the others. So the TTL does not have to exceed request durations or waits; it bounds how long a dead instance
blocks a host. The start-up rule ``shared_host_ttl_seconds * 2/3 > STATE_BUSY_TIMEOUT_MS`` keeps a renewal that
waited a full lock wait in time (:func:`check_ttl`).

Times are wall-clock (``time.time()``) because they are compared across processes. Instances with different
state stores do not coordinate (separate collectors, v1 is single node: ADR-0007). A busy store (another
process holding the SQLite lock longer than ``STATE_BUSY_TIMEOUT_MS``) never fails a request: the request waits
and tries again; the per-process limits keep applying meanwhile.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import sqlite3
import time
import uuid

from .state import StateStore

__all__ = ["RENEWALS_PER_TTL", "SharedHosts", "check_ttl"]

log = logging.getLogger(__name__)

RENEWALS_PER_TTL = 3
"""Renewals within one ``shared_host_ttl_seconds``: a live row is renewed every ``ttl / 3``."""


def check_ttl(ttl_s: float, busy_timeout_ms: int) -> None:
    """Start-up rule: a renewal that waited one full SQLite lock wait must still come before the TTL runs out
    (``ttl - ttl / 3 > busy timeout``); otherwise a live instance would lose its slot to another instance."""
    if ttl_s - ttl_s / RENEWALS_PER_TTL <= busy_timeout_ms / 1000:
        raise ValueError(
            f"collector.shared_host_ttl_seconds ({ttl_s:g}) * 2/3 must be greater than "
            f"STATE_BUSY_TIMEOUT_MS ({busy_timeout_ms} ms)"
        )


class SharedHosts:
    """Cross-instance part of the per-host limits, kept in the shared :class:`~.state.StateStore`."""

    def __init__(self, state: StateStore, instance_id: str, *, poll_s: float, ttl_s: float) -> None:
        self.state = state
        self.instance_id = instance_id
        self.poll_s = poll_s
        """``collector.shared_host_poll_ms`` / 1000: re-check of a host whose slots other instances hold."""
        self.ttl_s = ttl_s
        """``collector.shared_host_ttl_seconds``: rows nobody renews for this long expire (a dead instance)."""
        self._hosts: dict[str, tuple[float, int]] = {}
        """Hosts this instance is registered on: ``host -> (interval, parallel)`` of its last request there."""
        self._tokens: dict[str, str] = {}
        """Requests of this instance in line or in flight: ``token -> host``."""
        self._renewer: asyncio.Task[None] | None = None

    async def start(self, host: str, *, interval: float, parallel: int) -> str:
        """Register this instance's limits on ``host`` (its strictest ``interval`` and smallest ``parallel``), wait
        in line until the request may start (a free slot of the platform, the interval since the previous start of
        any instance, ``Retry-After``) and take the slot. Returns its token: give it back with :meth:`release`
        when the request is over."""
        token = uuid.uuid4().hex
        self._hosts[host] = (interval, parallel)
        self._tokens[token] = host
        self._ensure_renewer()
        try:
            while True:
                try:
                    taken, wait_s = self.state.host_take_slot(
                        host, self.instance_id, token, interval=interval, parallel=parallel, ttl=self.ttl_s
                    )
                except sqlite3.OperationalError:
                    log.warning("shared host limits: state store busy, retrying", extra={"host": host})
                    taken, wait_s = False, 0.0
                if taken:
                    return token
                await asyncio.sleep(wait_s if wait_s > 0 else self.poll_s)
        except BaseException:  # cancelled while waiting in line: leave the line
            self.release(host, token)
            raise

    def release(self, host: str, token: str) -> None:
        """Give back the slot (or the place in line) of ``token``."""
        self._tokens.pop(token, None)
        try:
            self.state.host_release_slot(host, token)
        except sqlite3.OperationalError:  # no longer renewed: the slot expires after ttl_s
            log.warning("shared host limits: slot not released, it expires", extra={"host": host})

    def push_back(self, host: str, seconds: float) -> None:
        """``Retry-After``: no instance starts a request to ``host`` before ``now + seconds``."""
        try:
            self.state.host_push_back(host, time.time() + seconds)
        except sqlite3.OperationalError:
            log.warning("shared host limits: Retry-After not shared", extra={"host": host})

    def leave(self, host: str) -> None:
        """This instance no longer uses ``host``: its limits stop applying to the other instances."""
        self._hosts.pop(host, None)
        try:
            self.state.host_leave(host, self.instance_id)
        except sqlite3.OperationalError:  # no longer renewed: the registration expires after ttl_s
            log.warning("shared host limits: registration not removed, it expires", extra={"host": host})

    # ------------------------------------------------------------------ liveness
    def _ensure_renewer(self) -> None:
        loop = asyncio.get_running_loop()
        if self._renewer is None or self._renewer.done() or self._renewer.get_loop() is not loop:
            self._renewer = loop.create_task(self._renew_loop(), name="shared-host-renewal")

    async def _renew_loop(self) -> None:
        """Renew this instance's registrations, slots and places in line while it has any."""
        period = self.ttl_s / RENEWALS_PER_TTL
        while self._hosts or self._tokens:
            await asyncio.sleep(period)
            self.renew()

    def renew(self) -> None:
        """One renewal of everything this instance holds (the renewal task calls it every ``ttl / 3``)."""
        if not self._hosts and not self._tokens:
            return
        try:
            self.state.host_renew(self.instance_id, dict(self._hosts), list(self._tokens), self.ttl_s)
        except sqlite3.OperationalError:
            log.warning("shared host limits: renewal postponed, state store busy")

    async def aclose(self) -> None:
        """Stop renewing (service shutdown). Rows still held expire after ``ttl_s`` like those of a dead instance."""
        if self._renewer is not None:
            self._renewer.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._renewer
            self._renewer = None
