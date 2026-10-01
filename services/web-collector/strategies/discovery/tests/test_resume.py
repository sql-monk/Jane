"""A collection with the WP-03 strategies survives a hard kill of the collector (contracts/docs/discovery-strategy.md
rule 6): the collector runs as a separate OS process with this package (``JANE_WEB_COLLECTOR_DISCOVERY_PATH``),
is killed with SIGKILL / TerminateProcess, and a new process on the same state finishes the collection.

Killed while the strategies read their navigation documents (``seeds``: sitemaps, the URL template walk, API
pages) or later, while listing chains are followed from the saved strategy state — in both cases the result is
exactly the expected union, every URL once, acknowledged materials are not delivered again.

The kill inside ``seeds`` is placed by holding a sitemap request on the test site until the process is dead
(:class:`.helpers.Hold`), not by polling ``stats.fetched``: the sitemap strategy finishes about 70 ms after its
third fetch at 15 req/s, so on a loaded machine a poll-then-kill landed after it.
"""

from __future__ import annotations

import time
from collections import Counter
from typing import Any

import httpx
import pytest

from jane_web_collector.testing import ServiceFactory, drain, start, wait_done, web_rules

from .helpers import WAIT_S, HoldingSite, api, archive, categories, sitemap, union

SLOW_LIMITS: dict[str, Any] = {
    # slow enough that the kill lands where the test wants it (~60 requests at 15 req/s)
    "rate": {"requests_per_second_per_host": 15, "min_delay_ms_per_host": 0},
    "concurrency": {"max_parallel_fetches": 2, "max_parallel_fetches_per_host": 2},
    "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
    "crawl": {"max_depth": 20},
}
SEED_FETCHES = 4 + 7 + 4  # sitemap index + 3 sitemaps, /archive/1..7, 4 API pages: all read in seeds()
NAVIGATION_PREFIXES = ("/sitemap", "/api/", "/robots.txt")
TEMPLATE_MISSES = {"/archive/6", "/archive/7"}  # 404s: a restarted URL template walk checks them again
SEEDS_HOLD = "/sitemaps/pages.xml"
"""The last child sitemap (4th fetch of seeds()): held until the kill, so the sitemap strategy is unfinished."""


@pytest.mark.parametrize("kill_after", [None, 30], ids=["during-seeds", "during-crawl"])
def test_strategies_resume_after_kill(
    service_factory: ServiceFactory,
    site: HoldingSite,
    expected_sets: dict[str, set[str]],
    kill_after: int | None,
) -> None:
    rules = web_rules(site, strategies=[sitemap(site), archive(site), api(site), categories(site)])
    body = {"source_kind": "web", "source_id": "resume", "rules": rules, "limits": SLOW_LIMITS}
    hold = site.hold(SEEDS_HOLD) if kill_after is None else None
    first = service_factory()
    first.start()
    acked: list[dict[str, Any]] = []
    with httpx.Client(base_url=first.base, timeout=10) as client:
        cid = start(client, body)
        view: dict[str, Any] = {}
        if hold is not None:  # seeds() waits for the held sitemap: nothing moves until the kill
            hold.wait_arrived()
            view = client.get(f"/v1/collections/{cid}").json()
        else:
            deadline = time.monotonic() + WAIT_S
            while time.monotonic() < deadline:
                view = client.get(f"/v1/collections/{cid}").json()
                if view["stats"]["fetched"] >= kill_after:
                    break
                time.sleep(0.02)
        page = client.get(f"/v1/collections/{cid}/materials", params={"limit": 5}).json()
        if page["items"]:  # the consumer took and acknowledged a first page before the crash
            acked = page["items"]
            client.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"], "limit": 1})
    first.kill()
    if hold is not None:
        hold.release()  # the handler answers the dead connection; the next request of the path is not held
    assert view["status"] == "running", view
    fetched_before = view["stats"]["fetched"]

    second = service_factory(state_dir=first.state_dir)
    second.start()
    with httpx.Client(base_url=second.base, timeout=10) as client:
        rest = drain(client, cid, timeout=120)
        done = wait_done(client, cid, timeout=30)
    assert done["status"] == "succeeded", done
    assert done["stats"]["fetched"] > fetched_before

    urls = [m["locator"]["canonical_url"] for m in acked + rest]
    assert {u: n for u, n in Counter(urls).items() if n > 1} == {}
    want = union(expected_sets, "sitemap", "categories", "template:/archive/{n}", "api")
    assert set(urls) == site.canonical(want)
    assert not {m["observation_id"] for m in acked} & {m["observation_id"] for m in rest}
    # materials are fetched again only if they were in flight at the kill (navigation documents and misses of
    # an unfinished seeds() step are re-read by design)
    refetched = {
        p: n
        for p, n in site.requests.items()
        if n > 1 and not p.startswith(NAVIGATION_PREFIXES) and p not in TEMPLATE_MISSES
    }
    assert len(refetched) <= SLOW_LIMITS["concurrency"]["max_parallel_fetches"], refetched
    if hold is not None:
        # killed inside seeds() of the sitemap strategy: the new process re-read the sitemaps
        assert fetched_before < SEED_FETCHES, view
        assert site.requests["/sitemap.xml"] == 2
        assert site.requests[SEEDS_HOLD] == 2, dict(site.requests)
    else:  # killed in the crawl: seeds() was complete and is not repeated, listing chains continued
        navigation = [p for p in site.requests if p.startswith(NAVIGATION_PREFIXES) and p != "/robots.txt"]
        assert navigation and all(site.requests[p] == 1 for p in navigation), dict(site.requests)
        assert all(n == 1 for p, n in site.requests.items() if p.startswith("/catalog/")), dict(site.requests)
