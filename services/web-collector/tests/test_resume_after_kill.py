"""WP-02 «Готово, коли»: after a hard kill of the collector process the crawl continues where it stopped.

The collector runs as a separate OS process against the real testsite; it is killed with SIGKILL /
TerminateProcess (no graceful shutdown), then a new process is started on the same state directory.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from jane_web_collector.testing import Site, drain, start, wait_done, web_rules

from .conftest import ServiceFactory

SLOW_LIMITS: dict[str, Any] = {
    # slow enough that the kill lands in the middle of the crawl (~50 pages at 15 req/s)
    "rate": {"requests_per_second_per_host": 15, "min_delay_ms_per_host": 0},
    "concurrency": {"max_parallel_fetches": 2, "max_parallel_fetches_per_host": 2},
    "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
    "crawl": {"max_depth": 20},
}


def test_crawl_resumes_after_kill(
    service_factory: ServiceFactory, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    first = service_factory()
    first.start()
    with httpx.Client(base_url=first.base, timeout=10) as api:
        cid = start(
            api,
            {"source_kind": "web", "source_id": "resume", "rules": web_rules(site), "limits": SLOW_LIMITS},
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            view = api.get(f"/v1/collections/{cid}").json()
            if view["stats"]["fetched"] >= 12:
                break
            time.sleep(0.05)
        # the consumer took and acknowledged a first page before the crash
        page = api.get(f"/v1/collections/{cid}/materials", params={"limit": 5}).json()
        acked = page["items"]
        assert len(acked) == 5
        api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"], "limit": 1})
    first.kill()
    fetched_before = view["stats"]["fetched"]
    assert view["status"] == "running"
    requests_before = sum(site.requests.values())

    second = service_factory(state_dir=first.state_dir)
    second.start()
    with httpx.Client(base_url=second.base, timeout=10) as api:
        rest = drain(api, cid, timeout=90)
        done = wait_done(api, cid, timeout=30)
    assert done["status"] == "succeeded", done

    got = {m["locator"]["canonical_url"] for m in acked} | {m["locator"]["canonical_url"] for m in rest}
    assert got == site.canonical(expected_sets["recursive"])
    # acknowledged materials are not delivered again
    assert not {m["observation_id"] for m in acked} & {m["observation_id"] for m in rest}
    # it continued rather than restarting: "/" was fetched once, re-fetches are limited to in-flight URLs
    assert site.requests["/"] == 1
    refetched = {p: n for p, n in site.requests.items() if n > 1 and p != "/robots.txt"}
    assert len(refetched) <= SLOW_LIMITS["concurrency"]["max_parallel_fetches"], refetched
    assert requests_before > 12 and fetched_before < done["stats"]["fetched"]
    # robots.txt at most once per process
    assert site.requests["/robots.txt"] <= 2
