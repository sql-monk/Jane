"""WP-02c: the process-wide per-host limiter (``host_limits``) on its own, with real asyncio time.

The integration side (collections and ``POST /v1/fetches`` against a real HTTP server) is in
``test_shared_host_limit.py``. Timing checks are lower bounds (load only makes them easier) or upper bounds
with a wide margin against the value the opposite behaviour would give.
"""

from __future__ import annotations

import asyncio
import gc
import itertools
import time

import pytest

from jane_web_collector.host_limits import HostLimiter, HostSession
from jane_web_collector.settings import Concurrency, Rate, ServiceLimits


def _limits(rps: float, parallel: int = 2, *, respect_crawl_delay: bool = True) -> ServiceLimits:
    return ServiceLimits(
        rate=Rate(
            requests_per_second_per_host=rps, min_delay_ms_per_host=0, respect_crawl_delay=respect_crawl_delay
        ),
        concurrency=Concurrency(max_parallel_fetches_per_host=parallel),
    )


async def _requests(
    session: HostSession, host: str, n: int, starts: list[float], hold_s: float = 0.0
) -> None:
    for _ in range(n):
        async with session.slot(host):
            starts.append(time.monotonic())
            if hold_s:
                await asyncio.sleep(hold_s)


def _span(starts: list[float]) -> float:
    ordered = sorted(starts)
    return ordered[-1] - ordered[0]


async def test_sessions_share_one_schedule_per_host() -> None:
    limiter = HostLimiter(ServiceLimits())
    interval = 0.05
    first, second = limiter.session(_limits(1 / interval)), limiter.session(_limits(1 / interval))
    starts: list[float] = []
    await asyncio.gather(_requests(first, "a.test", 5, starts), _requests(second, "a.test", 5, starts))
    # 10 starts at least one interval apart, whichever session made them
    assert _span(starts) >= 0.75 * 9 * interval
    # other hosts have their own schedule
    a: list[float] = []
    b: list[float] = []
    await asyncio.gather(_requests(first, "a.test", 3, a), _requests(second, "b.test", 3, b))
    merged = sorted(a + b)
    assert min(y - x for x, y in itertools.pairwise(merged)) < interval / 2


async def test_the_strictest_interval_of_active_sessions_applies() -> None:
    limiter = HostLimiter(ServiceLimits())
    slow, fast = limiter.session(_limits(1 / 0.3)), limiter.session(_limits(1000))
    starts: list[float] = []
    await _requests(slow, "h.test", 1, starts)  # the slow session is now active on the host
    await _requests(fast, "h.test", 4, starts)
    assert _span(starts) >= 0.75 * 4 * 0.3
    assert limiter.stats("h.test") == {
        "sessions": 2,
        "in_flight": 0,
        "waiting": 0,
        "interval_s": pytest.approx(0.3),
        "parallel": 2,
        "last_start": pytest.approx(max(starts)),
    }
    slow.close()  # its limits stop applying
    began = time.monotonic()
    await _requests(fast, "h.test", 10, [])
    assert time.monotonic() - began < 0.5 * 10 * 0.3  # ~0.3 s at most at 0.3 s from the last start
    fast.close()


async def test_the_smallest_parallelism_of_active_sessions_applies() -> None:
    limiter = HostLimiter(ServiceLimits())
    one, three = limiter.session(_limits(1000, parallel=1)), limiter.session(_limits(1000, parallel=3))
    in_flight = peak = 0

    async def hold(session: HostSession) -> None:
        nonlocal in_flight, peak
        async with session.slot("p.test"):
            in_flight += 1
            peak = max(peak, in_flight)
            await asyncio.sleep(0.05)
            in_flight -= 1

    await hold(one)  # registers parallelism 1 on the host
    await asyncio.gather(*(hold(three) for _ in range(3)), hold(one))
    assert peak == 1
    one.close()
    peak = 0
    await asyncio.gather(*(hold(three) for _ in range(3)))
    assert peak == 3
    three.close()


async def test_cancelled_waits_leave_no_trace() -> None:
    limiter = HostLimiter(ServiceLimits())
    slow = limiter.session(_limits(1.0, parallel=2))  # 1 s between starts
    async with slow.slot("c.test"):
        pass
    stats = limiter.stats("c.test")
    assert stats is not None
    first_start = stats["last_start"]

    async def one_request() -> None:
        async with slow.slot("c.test"):
            raise AssertionError("must not start: cancelled before its turn")

    turn = asyncio.create_task(one_request())  # sleeps until its turn (1 s after the first start)
    queued = asyncio.create_task(one_request())  # waits behind it for the turn
    await asyncio.sleep(0.05)
    assert limiter.stats("c.test") == {**stats, "in_flight": 2}
    for task in (turn, queued):
        task.cancel()
    results = await asyncio.wait_for(asyncio.gather(turn, queued, return_exceptions=True), timeout=0.5)
    assert all(isinstance(r, asyncio.CancelledError) for r in results)
    assert limiter.stats("c.test") == {**stats, "in_flight": 0, "last_start": first_start}

    # waiting for a slot (parallelism 1) is cancellable too and frees nothing it did not take
    single = limiter.session(_limits(1000, parallel=1))
    release = asyncio.Event()

    async def holder() -> None:
        async with single.slot("s.test"):
            await release.wait()

    holding = asyncio.create_task(holder())
    await asyncio.sleep(0.01)
    waiting = asyncio.create_task(one_request_on(single, "s.test"))
    await asyncio.sleep(0.01)
    assert (limiter.stats("s.test") or {})["waiting"] == 1
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting
    release.set()
    await holding
    after = limiter.stats("s.test") or {}
    assert (after["sessions"], after["in_flight"], after["waiting"], after["parallel"]) == (1, 0, 0, 1)
    async with single.slot("s.test"):  # the slot is free again
        pass


async def one_request_on(session: HostSession, host: str) -> None:
    async with session.slot(host):
        pass


async def test_retry_after_delays_every_session_of_the_host() -> None:
    limiter = HostLimiter(ServiceLimits())
    first, other = limiter.session(_limits(1000)), limiter.session(_limits(1000))
    began = time.monotonic()
    first.push_back("r.test", 0.3)
    async with other.slot("r.test"):
        waited = time.monotonic() - began
    assert waited >= 0.3 * 0.9


async def test_crawl_delay_counts_until_the_session_closes() -> None:
    limiter = HostLimiter(ServiceLimits())
    polite = limiter.session(_limits(1000))
    async with polite.slot("d.test", crawl_delay=0.2):
        pass
    async with polite.slot("d.test"):  # e.g. robots.txt itself: no Crawl-delay, does not lower it
        pass
    assert (limiter.stats("d.test") or {})["interval_s"] == pytest.approx(0.2)
    ignoring = limiter.session(_limits(1000, respect_crawl_delay=False))
    async with ignoring.slot("e.test", crawl_delay=5):
        pass
    assert (limiter.stats("e.test") or {})["interval_s"] == pytest.approx(0.001)


async def test_state_of_unused_hosts_is_dropped() -> None:
    limiter = HostLimiter(ServiceLimits())
    session = limiter.session(_limits(1000))
    for i in range(50):
        async with session.slot(f"host-{i}.test"):
            pass
    assert len(limiter) == 50
    assert limiter.prune(time.monotonic() + 60) == 0  # the session is still open: its hosts stay
    session.close()
    session.close()  # idempotent
    limiter.prune(time.monotonic() + 60)
    assert len(limiter) == 0

    # a session that is never closed stops counting once it is garbage collected
    forgotten = limiter.session(_limits(1 / 0.5))
    async with forgotten.slot("g.test"):
        pass
    assert (limiter.stats("g.test") or {})["sessions"] == 1
    del forgotten
    gc.collect()
    assert (limiter.stats("g.test") or {})["sessions"] == 0
    assert limiter.prune(time.monotonic() + 60) == 1
