"""R15: per-host limits are shared by the instances of the Web Collector that share one state store.

WP-02c made the per-host limits common to all collections and fetches of one process; two instances with one
``STATE_DIR`` (R-02 runs several replicas on one volume) still reached a host twice as often. Here two
independent application objects - two engines, two limiters, two SQLite connections, one state file, as two
replicas - collect the same host at the same time from a real HTTP server that records when each request
arrives and how many are in flight (server side, like the WP-14 harness). Nothing of the collector is mocked.

The timing bounds are the ones of ``test_shared_host_limit.py`` (load can only lengthen the span).
"""

from __future__ import annotations

import bisect
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
"""Share of the nominal span ``(n - 1) * interval`` that must be observed (as in ``test_shared_host_limit.py``)."""
HOLD_S = 0.4
"""How long the parallelism site keeps every page request open."""


def _politeness(starts: list[float], interval: float) -> dict[str, Any]:
    return {
        "requests": len(starts),
        "interval_s": round(interval, 3),
        "span_s": round(starts[-1] - starts[0], 3),
        "min_span_s": round(SPAN_FRACTION * (len(starts) - 1) * interval, 3),
        "max_in_1s": max(bisect.bisect_left(starts, s + 1.0) - i for i, s in enumerate(starts)),
        "max_in_1s_allowed": math.ceil(1 / interval) + 2,
    }


def _assert_polite(starts: list[float], interval: float) -> None:
    """All request starts to one host, from whichever instance, respect one shared interval."""
    m = _politeness(starts, interval)
    print(f"politeness: {m}")  # shown with -s: measured values for the report
    assert m["span_s"] >= m["min_span_s"], f"requests to one host came too fast: {m}"
    assert m["max_in_1s"] <= m["max_in_1s_allowed"], f"too many requests in one second: {m}"


def _overlap(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[-1], b[-1])


@dataclass
class CountingSite:
    """Records the arrival of every request and the largest number in flight at once; pages can be held."""

    base: str = ""
    hold_s: float = 0.0
    starts: list[tuple[float, str]] = field(default_factory=list)
    in_flight: int = 0
    max_in_flight: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def host(self) -> str:
        return self.base.split("://", 1)[1].split(":")[0]

    def requests(self, prefix: str = "/") -> list[float]:
        with self.lock:
            return sorted(t for t, path in self.starts if path.startswith(prefix))


def _serve(site: CountingSite) -> Iterator[CountingSite]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            page = self.path != "/robots.txt"
            with site.lock:
                site.starts.append((time.monotonic(), self.path))
                if page:
                    site.in_flight += 1
                    site.max_in_flight = max(site.max_in_flight, site.in_flight)
            try:
                if page and site.hold_s:
                    time.sleep(site.hold_s)
                body = b"User-agent: *\nAllow: /\n" if not page else b"<html><body>page</body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/plain" if not page else "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            finally:
                if page:
                    with site.lock:
                        site.in_flight -= 1

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
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
def counting() -> Iterator[CountingSite]:
    yield from _serve(CountingSite())


def _profile(tmp_path: Path, defaults: dict[str, Any], **collector: Any) -> Path:
    profile = tmp_path / "platform-limits.json"
    profile.write_text(json.dumps({"profile": "r15-test", "defaults": defaults}), encoding="utf-8")
    return profile


@pytest.fixture
def replicas(tmp_path: Path) -> Iterator[tuple[TestClient, TestClient]]:
    """Two instances of the collector on one state directory (each its own engine and SQLite connection)."""
    profile = _profile(
        tmp_path,
        {
            "rate": {"requests_per_second_per_host": RPS, "min_delay_ms_per_host": 0},
            "concurrency": {"max_parallel_fetches": 2, "max_parallel_fetches_per_host": 2},
            "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
        },
    )
    # one Settings per instance: each process start gets its own instance_id (the lease and limiter owner)
    one, two = make_settings(tmp_path, limits_file=profile), make_settings(tmp_path, limits_file=profile)
    with TestClient(build_app(one)) as a, TestClient(build_app(two)) as b:
        assert a.app.state.engine.settings.instance_id != b.app.state.engine.settings.instance_id  # type: ignore[attr-defined]
        yield a, b


def _collection(
    base: str, host: str, prefix: str, n: int, limits: dict[str, Any] | None = None
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "source_kind": "web",
        "rules": {
            "collector": "web",
            "scope": {"allowed_domains": [host]},
            "strategies": [
                {
                    "type": "seed_list",
                    "strategy_id": "seeds",
                    "urls": [f"{base}/{prefix}/{i}" for i in range(n)],
                }
            ],
        },
    }
    if limits is not None:
        body["limits"] = limits
    return body


def test_two_instances_share_the_rate_of_one_host(
    replicas: tuple[TestClient, TestClient], counting: CountingSite
) -> None:
    a, b = replicas
    n = 8
    first = start(a, _collection(counting.base, counting.host, "a", n))
    second = start(b, _collection(counting.base, counting.host, "b", n))
    assert len(drain(a, first)) == n
    assert len(drain(b, second)) == n
    assert wait_done(a, first)["status"] == "succeeded" and wait_done(b, second)["status"] == "succeeded"
    on_a, on_b = counting.requests("/a/"), counting.requests("/b/")
    assert len(on_a) == len(on_b) == n
    assert _overlap(on_a, on_b), "the instances did not collect at the same time"
    _assert_polite(counting.requests(), INTERVAL)  # robots.txt of both + 2n pages: one rate for the host


def test_two_instances_share_the_parallelism_of_one_host(tmp_path: Path) -> None:
    site = CountingSite(hold_s=HOLD_S)
    for _ in _serve(site):
        profile = _profile(
            tmp_path,
            {
                "rate": {"requests_per_second_per_host": 1000, "min_delay_ms_per_host": 0},
                "concurrency": {"max_parallel_fetches": 4, "max_parallel_fetches_per_host": 1},
                "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
            },
        )
        one, two = make_settings(tmp_path, limits_file=profile), make_settings(tmp_path, limits_file=profile)
        with TestClient(build_app(one)) as a, TestClient(build_app(two)) as b:
            n = 4
            first = start(a, _collection(site.base, site.host, "a", n))
            second = start(b, _collection(site.base, site.host, "b", n))
            assert len(drain(a, first)) == n and len(drain(b, second)) == n
            assert _overlap(site.requests("/a/"), site.requests("/b/")), "the instances did not overlap"
        print(f"parallelism: max in flight {site.max_in_flight} (limit 1, two instances)")
        assert site.max_in_flight == 1  # one slot for the host across both instances


def test_the_strictest_instance_rate_applies_to_the_other(
    replicas: tuple[TestClient, TestClient], counting: CountingSite
) -> None:
    """Instance A collects with 2 rps from its request, B with 1000 rps: while A is active on the host, the
    host sees at most 2 rps from the platform as a whole (the rule of WP-02c across instances)."""
    a, b = replicas
    slow = {"rate": {"requests_per_second_per_host": 2, "min_delay_ms_per_host": 0}}
    fast = {"rate": {"requests_per_second_per_host": 1000, "min_delay_ms_per_host": 0}}
    cid_a = start(a, _collection(counting.base, counting.host, "a", 5, slow))
    deadline = time.monotonic() + 30
    while not counting.requests("/a/") and time.monotonic() < deadline:
        time.sleep(0.01)
    cid_b = start(b, _collection(counting.base, counting.host, "b", 3, fast))
    assert len(drain(a, cid_a)) == 5 and len(drain(b, cid_b)) == 3
    on_a, on_b = counting.requests("/a/"), counting.requests("/b/")
    assert _overlap(on_a, on_b), "B did not run while A was active"
    _assert_polite(counting.requests(), 1 / 2)
