"""WP-02c: per-host limits are shared by every collection and one-shot fetch of one service process.

Found by the WP-14 limits harness (profile ``ci``, scenario L2): two concurrent collections of one host made
97 request starts in a 1 s window at a limit of 51, because every collection had its own per-host limiter.
Here the real application talks to a real HTTP server that records when each request arrives (server side,
like the harness). Nothing of the collector is mocked.

Timing checks are chosen so that machine load cannot make them fail falsely:

* the span of all request starts is a lower bound: reserved starts are at least one interval apart, so
  ``last - first >= (n - 1) * interval - delay of the first request``; load only adds delay later on;
* the busiest 1 s window gets one extra request of slack for event-loop/timer jitter.
"""

from __future__ import annotations

import bisect
import itertools
import json
import math
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_web_collector.app import build_app
from jane_web_collector.testing import drain, make_settings, start, wait_done

RPS = 5.0
"""Platform rate of these tests: a 0.2 s interval between request starts to one host."""
INTERVAL = 1 / RPS
SPAN_FRACTION = 0.75
"""Share of the nominal span (``(n - 1) * interval``) that must be observed; the rest is slack for the
delay of the first request. Without a shared limit the span is about half of the nominal one."""

PLATFORM_LIMITS: dict[str, Any] = {
    "rate": {"requests_per_second_per_host": RPS, "min_delay_ms_per_host": 0},
    "concurrency": {"max_parallel_fetches": 2, "max_parallel_fetches_per_host": 2},
    "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
}


@dataclass
class TimedSite:
    """A tiny site (robots.txt allows everything, every other path is a small HTML page) that records the
    arrival time of every request."""

    base: str = ""
    starts: list[tuple[float, str]] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def host(self) -> str:
        return self.base.split("://", 1)[1].split(":")[0]

    def requests(self, prefix: str = "/") -> list[float]:
        with self.lock:
            return sorted(t for t, path in self.starts if path.startswith(prefix))

    def wait_first_request(self, prefix: str, timeout: float = 30) -> None:
        deadline = time.monotonic() + timeout
        while not self.requests(prefix):
            if time.monotonic() > deadline:
                raise AssertionError(f"no request to {prefix} within {timeout} s")
            time.sleep(0.01)


def _handler(site: TimedSite) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            with site.lock:
                site.starts.append((time.monotonic(), self.path))
            if self.path == "/robots.txt":
                body, media_type = b"User-agent: *\nAllow: /\n", "text/plain"
            else:
                body = f"<html><head><title>{self.path}</title></head><body>page</body></html>".encode()
                media_type = "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", media_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


@pytest.fixture
def timed() -> Iterator[TimedSite]:
    site = TimedSite()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(site))
    server.daemon_threads = True
    site.base = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield site
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def api(tmp_path: Path) -> Iterator[TestClient]:
    """The collector with the per-host limits in the platform layer (as the WP-14 profiles set them)."""
    profile = tmp_path / "platform-limits.json"
    profile.write_text(json.dumps({"profile": "wp02c-test", "defaults": PLATFORM_LIMITS}), encoding="utf-8")
    with TestClient(build_app(make_settings(tmp_path, limits_file=profile))) as c:
        yield c


def _collection(site: TimedSite, prefix: str, n: int, limits: dict[str, Any] | None = None) -> dict[str, Any]:
    urls = [f"{site.base}/{prefix}/{i}" for i in range(n)]
    body: dict[str, Any] = {
        "source_kind": "web",
        "rules": {
            "collector": "web",
            "scope": {"allowed_domains": [site.host]},
            "strategies": [{"type": "seed_list", "strategy_id": "seeds", "urls": urls}],
        },
    }
    if limits is not None:
        body["limits"] = limits
    return body


def _fetch(api: TestClient, site: TimedSite, path: str, limits: dict[str, Any] | None = None) -> None:
    body: dict[str, Any] = {
        "source_kind": "web",
        "url": site.base + path,
    }
    if limits is not None:
        body["limits"] = limits
    r = api.post("/v1/fetches", json=body)
    assert r.status_code == 200, r.text


def _politeness(starts: list[float], interval: float) -> dict[str, Any]:
    gaps = [b - a for a, b in itertools.pairwise(starts)]
    return {
        "requests": len(starts),
        "interval_s": round(interval, 3),
        "span_s": round(starts[-1] - starts[0], 3),
        "min_span_s": round(SPAN_FRACTION * (len(starts) - 1) * interval, 3),
        "max_in_1s": max(bisect.bisect_left(starts, s + 1.0) - i for i, s in enumerate(starts)),
        "max_in_1s_allowed": math.ceil(1 / interval) + 2,
        "min_gap_s": round(min(gaps), 4),
    }


def _assert_polite(starts: list[float], interval: float) -> None:
    """All request starts to one host, from whichever collection or fetch, respect one shared interval."""
    m = _politeness(starts, interval)
    print(f"politeness: {m}")  # shown with -s / -rP: measured values for the report
    assert m["span_s"] >= m["min_span_s"], f"requests to one host came too fast: {m}"
    assert m["max_in_1s"] <= m["max_in_1s_allowed"], f"too many requests in one second: {m}"


def _overlap(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[-1], b[-1])


def test_two_collections_of_one_host_share_the_rate(api: TestClient, timed: TimedSite) -> None:
    """Scenario L2 of the WP-14 harness: two collections of one host at once."""
    n = 8
    first = start(api, _collection(timed, "a", n))
    second = start(api, _collection(timed, "b", n))
    assert len(drain(api, first)) == n
    assert len(drain(api, second)) == n
    assert wait_done(api, first)["status"] == "succeeded"
    assert wait_done(api, second)["status"] == "succeeded"
    a, b = timed.requests("/a/"), timed.requests("/b/")
    assert len(a) == len(b) == n
    assert _overlap(a, b), "the collections did not run at the same time"
    _assert_polite(timed.requests(), INTERVAL)  # both robots.txt + 2n pages


def test_collection_and_one_shot_fetches_share_the_rate(api: TestClient, timed: TimedSite) -> None:
    n, fetches = 8, 4
    cid = start(api, _collection(timed, "a", n))
    timed.wait_first_request("/")
    for i in range(fetches):
        _fetch(api, timed, f"/f/{i}")
    assert len(drain(api, cid)) == n
    assert wait_done(api, cid)["status"] == "succeeded"
    a, f = timed.requests("/a/"), timed.requests("/f/")
    assert len(a) == n and len(f) == fetches
    assert _overlap(a, f), "the fetches did not run during the collection"
    _assert_polite(timed.requests(), INTERVAL)  # robots.txt of the collection and of every fetch, too


def test_the_strictest_active_rate_applies_to_every_user_of_the_host(
    api: TestClient, timed: TimedSite
) -> None:
    """A collection limited to 2 rps by its request and one-shot fetches allowed 1000 rps: while the
    collection is active, the host sees at most 2 rps from the service as a whole."""
    slow = {"rate": {"requests_per_second_per_host": 2, "min_delay_ms_per_host": 0}}
    fast = {"rate": {"requests_per_second_per_host": 1000, "min_delay_ms_per_host": 0}}
    n, fetches = 5, 2
    cid = start(api, _collection(timed, "a", n, slow))
    timed.wait_first_request("/")
    for i in range(fetches):
        _fetch(api, timed, f"/f/{i}", fast)
    assert len(drain(api, cid)) == n
    assert wait_done(api, cid)["status"] == "succeeded"
    a, f = timed.requests("/a/"), timed.requests("/f/")
    assert _overlap(a, f), "the fetches did not run during the collection"
    _assert_polite(timed.requests(), 1 / 2)


def test_cancelled_collection_releases_the_host(api: TestClient, timed: TimedSite) -> None:
    """Waiting for a per-host slot does not delay cancellation, and a cancelled collection's (strict)
    limits stop applying to the host."""
    interval = 4.0
    slow = {"rate": {"requests_per_second_per_host": 1 / interval, "min_delay_ms_per_host": 0}}
    cid = start(api, _collection(timed, "a", 20, slow))
    timed.wait_first_request("/a/")  # robots.txt, then the first page one interval later
    began = time.monotonic()
    assert api.post(f"/v1/jobs/{cid}/cancel", json={"reason": "test"}).status_code == 202
    assert wait_done(api, cid)["status"] == "cancelled"
    cancel_s = time.monotonic() - began
    assert cancel_s < interval * 0.9, f"cancellation waited for the host limiter: {cancel_s:.2f} s"
    began = time.monotonic()
    _fetch(api, timed, "/after-cancel")  # platform limits (0.2 s): robots.txt + the page
    fetch_s = time.monotonic() - began
    assert fetch_s < interval * 0.6, f"the cancelled collection still limits the host: {fetch_s:.2f} s"
    assert len(timed.requests("/a/")) < 20
