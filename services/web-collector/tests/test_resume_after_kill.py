"""WP-02 «Готово, коли»: after a hard kill of the collector process the crawl continues where it stopped.

The collector runs as a separate OS process against the real testsite; it is killed with SIGKILL /
TerminateProcess (no graceful shutdown), then a new process is started on the same state directory.
"""

from __future__ import annotations

import contextlib
import sqlite3
import time
from typing import Any

import httpx

from jane_web_collector.testing import ServiceFactory, Site, drain, start, wait_done, web_rules

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
    # The collection lease in service_factory is 3 s. The host lease must also fit this bounded
    # crash scenario: its production default is 120 s, so slots left by a killed request would
    # correctly outlive drain(timeout=90). Keep the shared limiter enabled and its expiry real.
    lease_settings = {"JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__SHARED_HOST_TTL_SECONDS": "3"}
    first = service_factory(**lease_settings)
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
    with contextlib.closing(sqlite3.connect(first.state_dir / "state.db")) as db:
        dead_owner = db.execute("SELECT owner FROM collections WHERE collection_id = ?", (cid,)).fetchone()[0]
        dead_slots = db.execute(
            "SELECT token, expires_at FROM host_slots WHERE instance_id = ?", (dead_owner,)
        ).fetchall()
    print(
        f"crash host leases: owner={dead_owner}, killed_at={time.time()}, ttl_seconds=3, slots={dead_slots}"
    )
    fetched_before = view["stats"]["fetched"]
    assert view["status"] == "running"
    requests_before = sum(site.requests.values())

    second = service_factory(state_dir=first.state_dir, **lease_settings)
    second.start()
    with httpx.Client(base_url=second.base, timeout=10) as api:
        rest = drain(api, cid, timeout=90)
        done = wait_done(api, cid, timeout=30)
    assert done["status"] == "succeeded", done
    with contextlib.closing(sqlite3.connect(first.state_dir / "state.db")) as db:
        left = db.execute("SELECT COUNT(*) FROM host_slots WHERE instance_id = ?", (dead_owner,)).fetchone()[
            0
        ]
    print(f"crash host leases after recovery: owner={dead_owner}, observed_at={time.time()}, slots={left}")
    assert left == 0  # the dead instance's slots expired; nothing deleted them on its behalf

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
