"""Per-host politeness shared by every collection and one-shot fetch of one service process.

The :class:`~.engine.Engine` owns one :class:`HostLimiter`. Each user of it - a collection run or one
``POST /v1/fetches`` - opens a :class:`HostSession` with its own effective limits. The limiter keeps one
schedule per host (``host[:port]`` of the URL), so the source sees one polite client however many
collections and fetches use it at the same time:

* request starts to a host are at least ``interval`` apart, ``interval = max(1 / rate.requests_per_second_per_host,
  rate.min_delay_ms_per_host)`` and robots.txt ``Crawl-delay`` when ``rate.respect_crawl_delay``;
* at most ``concurrency.max_parallel_fetches_per_host`` requests to a host are in flight at once;
* sessions with different values: the strictest value of the sessions active on the host applies to every
  request to it (the largest interval, the smallest parallelism). A session becomes active on a host with its
  first request there and stays active until it is closed (the collection finished, failed, was cancelled or
  handed over; the fetch returned). A Crawl-delay seen by a session keeps counting until it is closed;
* ``Retry-After`` from the source delays every user of the host.

Nothing is reserved ahead of time: requests that hold a slot take their start turn one by one (in arrival
order), sleep until the start the strictest interval allows and only then mark it as the host's last start.
A request cancelled while it waits (for a slot or for its turn) leaves no trace in the schedule.

The state of a host is dropped once no session uses it, nothing is in flight or waiting and its last interval
has passed: when a session closes and every ``collector.host_state_prune_interval_seconds``.

The limits are per process: instances of the service do not coordinate them (README, "Ліміти").
"""

from __future__ import annotations

import asyncio
import time
import weakref
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from .settings import ServiceLimits

__all__ = ["HostLimiter", "HostSession"]


@dataclass
class _Use:
    """What one session asks of one host."""

    interval: float
    parallel: int


class _Host:
    """Shared schedule of one host."""

    def __init__(self) -> None:
        # Weak keys: a session that is never closed stops counting once it is garbage collected.
        self.users: weakref.WeakKeyDictionary[HostSession, _Use] = weakref.WeakKeyDictionary()
        self.in_flight = 0
        self.waiters: list[asyncio.Future[None]] = []
        self.turn = asyncio.Lock()
        """Requests holding a slot take their start turns one by one, in arrival order."""
        self.last_start: float | None = None
        """When the latest request to the host was allowed to start (``time.monotonic()``)."""
        self.free_at = 0.0
        """``last_start`` plus the interval in force then."""
        self.not_before = 0.0
        """``Retry-After``: no request starts before this."""

    def interval(self) -> float:
        return max((use.interval for use in self.users.values()), default=0.0)

    def parallel(self) -> int:
        return min((use.parallel for use in self.users.values()), default=1)

    def next_start(self) -> float:
        """Earliest start of the next request under the strictest interval in force now."""
        start = self.not_before
        if self.last_start is not None:
            start = max(start, self.last_start + self.interval())
        return start

    def wake(self) -> None:
        """Let every waiter re-check the parallelism (a slot was freed or a strict session left)."""
        for waiter in self.waiters:
            if not waiter.done():
                waiter.set_result(None)

    def idle(self, now: float) -> bool:
        return (
            not self.users
            and not self.in_flight
            and not self.waiters
            and now >= max(self.free_at, self.not_before)
        )


class HostLimiter:
    """Per-host limits of one service process (see the module docstring)."""

    def __init__(self, limits: ServiceLimits) -> None:
        """``limits`` are the service's own (platform) limits; only housekeeping is read from them, the
        per-host limits come with every session."""
        self.prune_interval = float(limits.collector.host_state_prune_interval_seconds)
        self._hosts: dict[str, _Host] = {}
        self._pruned_at = time.monotonic()

    def session(self, limits: ServiceLimits) -> HostSession:
        """A new user of the limiter with its effective limits; close it when the work is done."""
        return HostSession(self, limits)

    def __len__(self) -> int:
        """Number of hosts with state (diagnostics, tests)."""
        return len(self._hosts)

    def stats(self, host: str) -> dict[str, Any] | None:
        """State of one host (diagnostics, tests): sessions active on it, requests in flight and waiting for
        a slot, the interval and parallelism in force; ``None`` when the host has no state."""
        state = self._hosts.get(host)
        if state is None:
            return None
        return {
            "sessions": len(state.users),
            "in_flight": state.in_flight,
            "waiting": len(state.waiters),
            "interval_s": state.interval(),
            "parallel": state.parallel() if state.users else None,
            "last_start": state.last_start,
        }

    def _host(self, name: str) -> _Host:
        now = time.monotonic()
        if now - self._pruned_at >= self.prune_interval:
            self.prune(now)
        state = self._hosts.get(name)
        if state is None:
            state = self._hosts[name] = _Host()
        return state

    def prune(self, now: float | None = None) -> int:
        """Drop the state of hosts nobody uses any more; returns how many were dropped."""
        now = time.monotonic() if now is None else now
        self._pruned_at = now
        idle = [name for name, state in self._hosts.items() if state.idle(now)]
        for name in idle:
            del self._hosts[name]
        return len(idle)

    def push_back(self, host: str, seconds: float) -> None:
        """The source asked to slow down (``Retry-After``): no request to this host from anyone before that."""
        state = self._host(host)
        state.not_before = max(state.not_before, time.monotonic() + seconds)

    def _leave(self, session: HostSession, host: str) -> None:
        state = self._hosts.get(host)
        if state is None:
            return
        state.users.pop(session, None)
        state.wake()
        if state.idle(time.monotonic()):
            del self._hosts[host]


class HostSession:
    """One user of the shared :class:`HostLimiter` (a collection run or a one-shot fetch) with its own
    effective limits."""

    def __init__(self, limiter: HostLimiter, limits: ServiceLimits) -> None:
        self.limiter = limiter
        self.limits = limits
        self._hosts: set[str] = set()

    def interval(self, crawl_delay: float | None = None) -> float:
        """Minimum interval between request starts to one host that this session's limits ask for."""
        rate = self.limits.rate
        interval = max(1.0 / rate.requests_per_second_per_host, rate.min_delay_ms_per_host / 1000)
        if rate.respect_crawl_delay and crawl_delay:
            interval = max(interval, crawl_delay)
        return interval

    def _join(self, host: str, crawl_delay: float | None) -> _Host:
        state = self.limiter._host(host)
        previous = state.users.get(self)
        interval = self.interval(crawl_delay)
        if previous is not None:  # requests without a Crawl-delay (robots.txt itself) do not lower it
            interval = max(interval, previous.interval)
        state.users[self] = _Use(interval, self.limits.concurrency.max_parallel_fetches_per_host)
        self._hosts.add(host)
        return state

    @asynccontextmanager
    async def slot(self, host: str, crawl_delay: float | None = None) -> AsyncIterator[None]:
        """Wait for a free per-host slot and for the next allowed start; the slot is held while the request
        is in flight. Cancellation interrupts any wait and frees everything taken."""
        state = self._join(host, crawl_delay)
        while state.in_flight >= state.parallel():
            waiter: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            state.waiters.append(waiter)
            try:
                await waiter
            finally:
                state.waiters.remove(waiter)
        state.in_flight += 1
        try:
            await self._wait_turn(state)
            yield
        finally:
            state.in_flight -= 1
            state.wake()

    async def _wait_turn(self, state: _Host) -> None:
        # Nothing is reserved ahead: a request cancelled while it waits leaves no trace in the schedule.
        async with state.turn:
            planned = state.next_start()
            while (now := time.monotonic()) < planned:
                await asyncio.sleep(planned - now)
                required = state.next_start()  # a stricter session or Retry-After may have come meanwhile
                if required <= planned:
                    break
                planned = required
            state.last_start = max(planned, time.monotonic())
            state.free_at = state.last_start + state.interval()

    def push_back(self, host: str, seconds: float) -> None:
        self.limiter.push_back(host, seconds)

    def close(self) -> None:
        """Stop taking part in the limits of every host this session used (idempotent)."""
        for host in self._hosts:
            self.limiter._leave(self, host)
        self._hosts.clear()
