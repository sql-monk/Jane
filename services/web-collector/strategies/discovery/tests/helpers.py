"""Shared helpers of the WP-03 tests: strategy configurations for the testsite and collection helpers."""

from __future__ import annotations

import os
import threading
from collections import Counter
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

from jane_web_collector.testing import FAST_LIMITS, Site, drain, start, wait_done, web_rules

ITEMS = {"value": "main li a"}
"""Item links of testsite category and search pages (the site navigation is outside ``<main>``)."""

WAIT_S = float(os.environ.get("JANE_DISCOVERY_TEST_WAIT_S", "30"))
"""How long a test waits for an event of the collector (a held request arriving) before it fails."""
HTTP_TIMEOUT_S = float(os.environ.get("JANE_DISCOVERY_TEST_HTTP_TIMEOUT_S", "60"))
"""Timeout of one HTTP request to a collector process (the first ``POST /v1/collections`` took 8-16 s on a loaded
machine, beyond the former 10 s)."""
DRAIN_S = float(os.environ.get("JANE_DISCOVERY_TEST_DRAIN_S", "300"))
"""How long a test reads materials of a collection run by a collector process until ``end_of_stream``."""
DONE_S = float(os.environ.get("JANE_DISCOVERY_TEST_DONE_S", "120"))
"""How long a test waits for such a collection to reach a final status after its stream ended."""


# ------------------------------------------------------------------------------------------ test site
@dataclass
class Hold:
    """From the first request of ``path`` on, every request to the site waits for :meth:`release` (afterwards
    requests are answered at once). The collector stands still at a known point while the test acts (kills
    it), instead of the test polling and racing with it."""

    path: str
    arrived: threading.Event = field(default_factory=threading.Event)
    released: threading.Event = field(default_factory=threading.Event)

    def wait_arrived(self, timeout: float = WAIT_S) -> None:
        assert self.arrived.wait(timeout), f"{self.path} was not requested within {timeout} s"

    def release(self) -> None:
        self.released.set()


@dataclass
class HoldingSite(Site):
    """:class:`Site` whose requests can be held (:meth:`hold`); the ``site`` fixture serves one."""

    holds: dict[str, Hold] = field(default_factory=dict)

    def hold(self, path: str) -> Hold:
        with self.lock:
            hold = self.holds[path] = Hold(path)
        return hold

    def take_hold(self, path: str) -> Hold | None:
        """The hold a request of ``path`` has to wait for, if any (called by the request handler)."""
        with self.lock:
            for held in self.holds.values():
                if held.arrived.is_set() and not held.released.is_set():
                    return held  # the site stands still: every request waits
            hold = self.holds.get(path)
            if hold is None or hold.arrived.is_set():
                return None
            hold.arrived.set()
            return hold

    def release_all(self) -> None:
        with self.lock:
            for hold in self.holds.values():
                hold.release()


# ------------------------------------------------------------------------------------------ strategies
def sitemap(site: Site, **extra: Any) -> dict[str, Any]:
    return {"type": "sitemap", "strategy_id": "sitemap", "urls": [site.url("/sitemap.xml")], **extra}


def rss(site: Site) -> dict[str, Any]:
    return {"type": "feed", "strategy_id": "feed", "urls": [site.url("/feeds/news.rss")]}


def categories(site: Site, **extra: Any) -> dict[str, Any]:
    starts = [site.url(f"/catalog/{c}/") for c in ("phones", "laptops", "accessories")]
    return {
        "type": "listing",
        "strategy_id": "categories",
        "start_urls": starts,
        "item_links": ITEMS,
        **extra,
    }


def search(site: Site) -> dict[str, Any]:
    return {
        "type": "listing",
        "strategy_id": "search",
        "start_urls": [site.url("/search?q=phone")],
        "search": {"url_template": site.url("/search?q={query}"), "queries": ["cable"]},
        "item_links": ITEMS,
    }


def archive(site: Site, **extra: Any) -> dict[str, Any]:
    return {
        "type": "url_template",
        "strategy_id": "archive",
        "template": site.url("/archive/{n}"),
        "variables": {"n": {"range": {"start": 1, "end": 50}}},
        "stop_after_consecutive_misses": 2,
        **extra,
    }


def api(site: Site, **pagination: Any) -> dict[str, Any]:
    return {
        "type": "api_feed",
        "strategy_id": "api",
        "url": site.url("/api/v1/products"),
        "items_path": "$.items",
        "url_path": "$.url",
        "pagination": pagination or {"type": "next_url", "next_url_path": "$.next"},
    }


def seeds_and_recursion(site: Site) -> list[dict[str, Any]]:
    return [{"type": "seed_list", "urls": [site.url("/")]}, {"type": "recursive"}]


# ------------------------------------------------------------------------------------------ helpers
def collect(
    client: TestClient, site: Site, strategies: list[dict[str, Any]], limits: dict[str, Any] | None = None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rules = web_rules(site, strategies=strategies)
    cid = start(
        client, {"source_kind": "web", "source_id": "wp03", "rules": rules, "limits": limits or FAST_LIMITS}
    )
    materials = drain(client, cid)
    view = wait_done(client, cid)
    assert view["status"] == "succeeded", view
    return materials, view


def assert_exactly(site: Site, materials: list[dict[str, Any]], paths: set[str]) -> None:
    canon = [m["locator"]["canonical_url"] for m in materials]
    duplicates = {u: n for u, n in Counter(canon).items() if n > 1}
    assert duplicates == {}, duplicates
    got, want = set(canon), site.canonical(paths)
    assert got == want, {"missing": sorted(want - got), "unexpected": sorted(got - want)}
    for m in materials:
        assert urlsplit(m["locator"]["final_url"]).hostname == site.host


def by_strategy(materials: list[dict[str, Any]]) -> Counter[str]:
    return Counter(m["discovery"]["strategy"] for m in materials)


def union(expected_sets: dict[str, set[str]], *names: str) -> set[str]:
    out: set[str] = set()
    for name in names:
        out |= expected_sets[name]
    return out


def cursor_stats(client: TestClient, state_key: str, strategy_id: str) -> dict[str, Any]:
    """Diagnostic counters a strategy keeps in its snapshot (``GET /v1/states/{state_key}`` -> ``cursors``)."""
    stats: dict[str, Any] = client.get(f"/v1/states/{state_key}").json()["cursors"][strategy_id]["stats"]
    return stats
