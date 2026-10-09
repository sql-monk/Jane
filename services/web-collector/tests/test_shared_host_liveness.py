"""R15, review 1 of WP-16: rows of the shared per-host schedule live exactly as long as their instance does.

Two instances are two :class:`SharedHosts` on two connections to one state file (as two replicas with one
``STATE_DIR``), with a short ``shared_host_ttl_seconds`` so that every wait below is longer than the TTL:

* a ``Retry-After``, a long download and a strict interval (``Crawl-delay``) longer than the TTL must not let the
  other instance exceed ``max_parallel_fetches_per_host`` or the interval: a live instance renews what it holds,
  and a slot is taken only when the request may start at once (before the review a slot was held while sleeping
  until the start and expired meanwhile);
* an instance that died (it neither releases nor renews) blocks the host until the TTL and not after it.

Nothing is mocked: the real state store and the real shared limiter, times measured on the wall clock.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_web_collector.app import build_app
from jane_web_collector.shared_hosts import SharedHosts, check_ttl
from jane_web_collector.state import StateStore
from jane_web_collector.testing import make_settings

TTL = 1.0
"""``shared_host_ttl_seconds`` of these tests: every wait below is longer."""
POLL = 0.02
HOST = "site.test"
SLACK = 0.05
"""Clock and scheduling slack for lower bounds (a bound is only ever late under load, never early)."""


@dataclass
class Host:
    """What the source would see: requests in flight and their starts."""

    in_flight: int = 0
    max_in_flight: int = 0
    starts: dict[str, float] = field(default_factory=dict)
    ends: dict[str, float] = field(default_factory=dict)

    async def request(self, shared: SharedHosts, name: str, hold: float, *, interval: float = 0.05) -> None:
        token = await shared.start(HOST, interval=interval, parallel=1)
        self.starts[name] = time.time()
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        try:
            await asyncio.sleep(hold)
        finally:
            self.in_flight -= 1
            self.ends[name] = time.time()
            shared.release(HOST, token)


@pytest.fixture
def instances(tmp_path: Path) -> Iterator[tuple[SharedHosts, SharedHosts]]:
    a_store, b_store = StateStore(tmp_path / "state.db"), StateStore(tmp_path / "state.db")
    try:
        yield (
            SharedHosts(a_store, "instance-a", poll_s=POLL, ttl_s=TTL),
            SharedHosts(b_store, "instance-b", poll_s=POLL, ttl_s=TTL),
        )
    finally:
        a_store.close()
        b_store.close()


def test_retry_after_longer_than_the_ttl_keeps_one_request_in_flight(
    instances: tuple[SharedHosts, SharedHosts],
) -> None:
    a, b = instances
    host = Host()

    async def scenario() -> float:
        began = time.time()
        a.push_back(HOST, 2.5 * TTL)  # A got 429 with Retry-After longer than the TTL
        await asyncio.gather(host.request(b, "b", 0.3), host.request(a, "a", 0.3))
        await asyncio.gather(a.aclose(), b.aclose())
        return began

    began = asyncio.run(scenario())
    assert host.max_in_flight == 1, host
    assert min(host.starts.values()) >= began + 2.5 * TTL - SLACK  # nobody started before Retry-After


def test_a_download_longer_than_the_ttl_keeps_its_slot(instances: tuple[SharedHosts, SharedHosts]) -> None:
    a, b = instances
    host = Host()

    async def scenario() -> None:
        long = asyncio.create_task(host.request(a, "a", 3 * TTL))
        await asyncio.sleep(TTL / 2)
        await host.request(b, "b", 0.1)
        await long
        await asyncio.gather(a.aclose(), b.aclose())

    asyncio.run(scenario())
    assert host.max_in_flight == 1, host
    assert host.starts["b"] >= host.ends["a"] - SLACK  # B waited for the whole download of A


def test_an_interval_longer_than_the_ttl_keeps_applying(instances: tuple[SharedHosts, SharedHosts]) -> None:
    """A Crawl-delay of 3 TTL on A's side: B, allowed 0.05 s, still waits 3 TTL after A's request starts."""
    a, b = instances
    host = Host()

    async def scenario() -> None:
        await host.request(a, "a", 0.0, interval=3 * TTL)  # A stays registered on the host (no leave)
        await host.request(b, "b", 0.0)
        await asyncio.gather(a.aclose(), b.aclose())

    asyncio.run(scenario())
    assert host.starts["b"] - host.starts["a"] >= 3 * TTL - SLACK, host


def test_a_dead_instance_blocks_the_host_until_the_ttl_only(
    instances: tuple[SharedHosts, SharedHosts],
) -> None:
    """A takes the only slot with a very strict interval and dies: no release, no leave, no renewal. B waits
    for its slot and registration to expire - about one TTL - and not for A's interval (10 TTL)."""
    a, b = instances
    host = Host()

    async def scenario() -> tuple[float, float]:
        await a.start(HOST, interval=10 * TTL, parallel=1)
        died = time.time()
        await a.aclose()  # killed: whatever it holds is never renewed or given back
        await asyncio.wait_for(host.request(b, "b", 0.0), timeout=5 * TTL)
        await b.aclose()
        return died, host.starts["b"]

    died, started = asyncio.run(scenario())
    waited = started - died
    assert waited >= TTL - SLACK, f"B started {waited:.2f} s after A died, before A's slot expired"
    assert waited < 3 * TTL, (
        f"B waited {waited:.2f} s: A's registration (interval {10 * TTL} s) outlived the TTL"
    )


def test_ttl_must_outlast_a_renewal_that_waited_a_full_lock_wait(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    check_ttl(120, 10_000)  # defaults
    with pytest.raises(ValueError, match="shared_host_ttl_seconds"):
        check_ttl(3, 2_000)  # renewed every 1 s, may wait 2 s for the lock: 3 s is too short
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_TTL_SECONDS", "3")
    with pytest.raises(ValueError, match="shared_host_ttl_seconds"):
        build_app(make_settings(tmp_path, state_busy_timeout_ms=2_000))
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_LIMITS", "false")
    with TestClient(build_app(make_settings(tmp_path, state_busy_timeout_ms=2_000))) as client:
        assert client.get("/v1/health").status_code == 200  # no coordination, no rule
