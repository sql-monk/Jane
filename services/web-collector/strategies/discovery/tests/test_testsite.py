"""WP-03 «Готово, коли»: every strategy alone and in combinations covers the expected URLs of the testsite.

Real testsite (WP-01) over HTTP, real collector core (WP-02) with this package registered as in production;
nothing is mocked. «Covers» = the emitted materials are exactly the expected set (canonical URLs), each URL
once, with navigation documents (sitemaps, feeds, API pages) not emitted.
"""

from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from jane_web_collector.testing import FAST_LIMITS, Site, drain, errors, start, wait_done, web_rules

ITEMS = {"value": "main li a"}
"""Item links of testsite category and search pages (the site navigation is outside ``<main>``)."""


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


# ------------------------------------------------------------------------------------------ alone
def test_sitemap_index_with_gzip_alone(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    materials, _ = collect(client, site, [sitemap(site)])
    assert_exactly(site, materials, expected_sets["sitemap"])
    assert by_strategy(materials) == {"sitemap": len(expected_sets["sitemap"])}
    # the index and every listed sitemap (the .gz one too) were read exactly once, none emitted as material
    for path in ["/sitemap.xml", "/sitemaps/products.xml", "/sitemaps/news.xml.gz", "/sitemaps/pages.xml"]:
        assert site.requests[path] == 1, path
    cursor = client.get("/v1/states/wp03").json()["cursors"]["sitemap"]["stats"]
    assert cursor["documents"] == 4 and cursor["gzip_documents"] == 1
    assert cursor["urls"] == len(expected_sets["sitemap"])


def test_sitemap_found_through_robots_txt(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    """No ``urls``: the ``Sitemap:`` line of robots.txt of the origin of the rules (here the seed list)."""
    strategies = [
        {"type": "sitemap", "strategy_id": "sitemap"},
        {"type": "seed_list", "urls": [site.url("/")]},
    ]
    materials, _ = collect(client, site, strategies)
    assert_exactly(site, materials, expected_sets["sitemap"])  # "/" is in the sitemap too
    assert site.requests["/sitemap.xml"] == 1
    assert site.requests["/sitemaps/news.xml.gz"] == 1


def test_sitemap_lastmod_since_skips_older_entries(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    # products.xml: lastmod 2026-09-01 (older, skipped); news.xml.gz: lastmod = modification time of each
    # article (09-02 .. 09-09); pages.xml: no lastmod (kept)
    materials, _ = collect(client, site, [sitemap(site, lastmod_since="2026-09-06T00:00:00Z")])
    news = {
        "/news/2026/price-drop-laptops",  # published 09-03, edited 09-06
        "/news/2026/review-headphones",
        "/news/2026/warranty-update",
        "/news/2026/recycling-program",
        "/news/2026/autumn-sale",
    }
    pages = {
        "/",
        "/about",
        "/catalog/",
        "/news/",
        "/pages/careers",
        "/pages/event-spring-meetup",
        "/pages/faq",
    }
    assert_exactly(site, materials, news | pages)


@pytest.mark.parametrize("path", ["/feeds/news.rss", "/feeds/news.atom"])
def test_feed_alone(client: TestClient, site: Site, expected_sets: dict[str, set[str]], path: str) -> None:
    materials, _ = collect(client, site, [{"type": "feed", "urls": [site.url(path)]}])
    assert_exactly(site, materials, expected_sets["feeds"])
    assert site.requests[path] == 1
    lastmods = {m["locator"]["canonical_url"] for m in materials}
    assert site.url("/news/2026/feed-only-announcement") in lastmods


def test_feed_autodiscovery_from_an_html_url(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    """An HTML page in ``urls``: its ``<link rel=alternate>`` feeds are read; the page itself is navigation."""
    materials, _ = collect(client, site, [{"type": "feed", "urls": [site.url("/about")]}])
    assert_exactly(site, materials, expected_sets["feeds"])
    assert site.requests["/feeds/news.rss"] == 1 and site.requests["/feeds/news.atom"] == 1


def test_feed_autodiscovery_on_seed_pages(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    """No ``urls``: feeds announced on the seed pages of other strategies (depth 0)."""
    strategies = [{"type": "seed_list", "urls": [site.url("/")]}, {"type": "feed", "strategy_id": "feed"}]
    materials, _ = collect(client, site, strategies)
    assert_exactly(site, materials, expected_sets["feeds"] | {"/"})
    assert by_strategy(materials) == {"seed_list": 1, "feed": len(expected_sets["feeds"])}


def test_listing_categories_with_rel_next(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    materials, _ = collect(client, site, [categories(site)])
    assert_exactly(site, materials, expected_sets["categories"])
    assert by_strategy(materials) == {"listing": len(expected_sets["categories"])}


def test_listing_categories_with_page_param(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    materials, view = collect(client, site, [categories(site, page_param={"name": "page"})])
    assert_exactly(site, materials, expected_sets["categories"])
    # the chains end at the first page past the end (404 on the testsite)
    not_found = {
        urlsplit(e["url"]).path + "?" + urlsplit(e["url"]).query
        for e in errors(client, view["collection_id"])
    }
    assert not_found == {
        "/catalog/phones/?page=4",
        "/catalog/laptops/?page=3",
        "/catalog/accessories/?page=3",
    }


def test_listing_search_pages(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
    materials, _ = collect(client, site, [search(site)])
    assert_exactly(site, materials, union(expected_sets, "search:phone", "search:cable"))


def test_url_template_stops_after_consecutive_misses(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    materials, _ = collect(client, site, [archive(site)])
    assert_exactly(site, materials, expected_sets["template:/archive/{n}"])
    assert site.requests["/archive/6"] == 1 and site.requests["/archive/7"] == 1  # two misses in a row
    assert not [p for p in site.requests if p.startswith("/archive/") and int(p.rsplit("/", 1)[1]) > 7]


def test_url_template_values_without_miss_detection(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    strategy = {
        "type": "url_template",
        "template": site.url("/archive/{n}"),
        "variables": {"n": {"values": [1, 2, 3, 4, 5]}},
    }
    materials, _ = collect(client, site, [strategy])
    assert_exactly(site, materials, expected_sets["template:/archive/{n}"])


@pytest.mark.parametrize(
    "pagination",
    [
        {"type": "next_url", "next_url_path": "$.next"},
        {"type": "page", "page_param": "page"},
    ],
    ids=["next_url", "page"],
)
def test_api_feed_alone(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]], pagination: dict[str, Any]
) -> None:
    materials, _ = collect(client, site, [api(site, **pagination)])
    assert_exactly(site, materials, expected_sets["api"])
    assert not [p for p in site.requests if p.startswith("/api/v1/products/")]  # detail endpoints not needed
    pages = sum(n for p, n in site.requests.items() if p.startswith("/api/v1/products"))
    assert pages == (4 if pagination["type"] == "next_url" else 5)  # "page" stops on the first empty page


# ------------------------------------------------------------------------------------------ combinations
@pytest.mark.parametrize(
    ("make", "sets"),
    [
        (sitemap, ("sitemap",)),
        (rss, ("feeds",)),
        (categories, ("categories",)),
        (search, ("search:phone", "search:cable")),
        (archive, ("template:/archive/{n}",)),
        (api, ("api",)),
    ],
    ids=["sitemap", "feed", "categories", "search", "url_template", "api_feed"],
)
def test_each_strategy_combined_with_recursion(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]], make: Any, sets: tuple[str, ...]
) -> None:
    materials, _ = collect(client, site, [*seeds_and_recursion(site), make(site)])
    assert_exactly(site, materials, union(expected_sets, "recursive", *sets))
    # the strategy contributes; which of two strategies that both propose a URL gets it is the core's dedup
    # (first candidate wins: items of a listing page are also links that recursion follows)
    assert by_strategy(materials)[make(site)["type"]] > 0
    repeated = {p: n for p, n in site.requests.items() if n > 1 and p != "/robots.txt"}
    assert repeated == {}, repeated


def test_all_strategies_together(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
    strategies = [
        *seeds_and_recursion(site),
        sitemap(site),
        rss(site),
        categories(site),
        search(site),
        archive(site),
        api(site),
    ]
    materials, _ = collect(client, site, strategies)
    names = ("recursive", "sitemap", "feeds", "categories", "search:phone", "search:cable", "api")
    assert_exactly(site, materials, union(expected_sets, *names, "template:/archive/{n}"))
    for only in ("only:sitemap", "only:api", "only:search", "only:feeds", "only:template"):
        assert site.canonical(expected_sets[only]) <= {m["locator"]["canonical_url"] for m in materials}
    assert set(by_strategy(materials)) == {
        "seed_list",
        "recursive",
        "sitemap",
        "feed",
        "listing",
        "url_template",
        "api_feed",
    }


def test_recursion_without_seeds_follows_sitemap_pages(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    """``recursive`` without ``seeds`` starts from the pages another strategy found (here: the sitemap)."""
    materials, _ = collect(client, site, [sitemap(site), {"type": "recursive"}])
    assert_exactly(site, materials, union(expected_sets, "sitemap", "recursive"))


def test_all_strategies_without_recursion(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    strategies = [sitemap(site), rss(site), categories(site), search(site), archive(site), api(site)]
    materials, _ = collect(client, site, strategies)
    names = ("sitemap", "feeds", "categories", "search:phone", "search:cable", "api", "template:/archive/{n}")
    assert_exactly(site, materials, union(expected_sets, *names))
    repeated = {p: n for p, n in site.requests.items() if n > 1}
    assert repeated == {}, repeated
