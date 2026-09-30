"""The strategies stay inside the core's policy (robots.txt, scope, budgets) and take every bound from limits:
pagination depth, entries per document, generated URLs. Navigation documents are re-read on an incremental
run while materials follow the core's revisit rules. Real testsite, real core."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from jane_web_collector.testing import FAST_LIMITS, Site, drain, errors, start, wait_done, web_rules

from .helpers import api, assert_exactly, categories, collect, cursor_stats, rss, sitemap


def test_robots_txt_applies_to_strategy_urls(client: TestClient, site: Site) -> None:
    """Disallowed URLs are refused by the core both as candidates and through ``ctx.fetch``."""
    template = site.url("/private/{page}")
    strategies: list[dict[str, Any]] = [
        {
            "type": "url_template",
            "strategy_id": "queued",
            "template": template,
            "variables": {"page": {"values": ["admin"]}},
        },
        {
            "type": "url_template",
            "strategy_id": "fetched",
            "template": template,
            "variables": {"page": {"values": ["reports", "admin"]}},
            "stop_after_consecutive_misses": 1,
        },
    ]
    materials, view = collect(client, site, strategies)
    assert materials == []
    assert not [p for p in site.requests if p.startswith("/private/")]
    denied = {
        urlsplit(e["url"]).path
        for e in errors(client, view["collection_id"])
        if e["code"] == "access_denied_by_policy"
    }
    assert denied == {"/private/admin", "/private/reports"}
    assert cursor_stats(client, "wp03", "fetched")["refused"] == 2


def test_urls_outside_the_scope_are_never_requested(client: TestClient, site: Site) -> None:
    strategies: list[dict[str, Any]] = [
        {
            "type": "url_template",
            "template": "https://external.example.org/p/{n}",
            "variables": {"n": {"range": {"start": 1, "end": 3}}},
        },
        {
            "type": "url_template",
            "template": "https://external.example.org/q/{n}",
            "variables": {"n": {"range": {"start": 1, "end": 3}}},
            "stop_after_consecutive_misses": 1,
        },
        {"type": "sitemap", "urls": ["https://external.example.org/sitemap.xml"]},
        {"type": "feed", "urls": ["https://cdn.external.example.net/feed.xml"]},
    ]
    materials, view = collect(client, site, strategies)
    assert materials == []
    assert view["stats"]["skipped_out_of_scope"] >= 3 + 3 + 1 + 1
    # nothing was attempted on the network: a request would have failed as source_unavailable
    assert [e for e in errors(client, view["collection_id"]) if e["code"] != "out_of_scope"] == []


def test_sitemap_entries_per_document_come_from_limits(client: TestClient, site: Site) -> None:
    materials, _ = collect(client, site, [sitemap(site, limits={"crawl": {"max_links_per_page": 3}})])
    by_file: dict[str, int] = {}
    for m in materials:
        path = urlsplit(m["locator"]["canonical_url"]).path
        kind = (
            "product"
            if path.startswith("/product/")
            else "news"
            if path.startswith("/news/2026/")
            else "page"
        )
        by_file[kind] = by_file.get(kind, 0) + 1
    assert by_file == {"product": 3, "news": 3, "page": 3}
    # products.xml has 17 entries, news.xml.gz 8, pages.xml 7: the rest is dropped and counted
    assert cursor_stats(client, "wp03", "sitemap")["entries_over_limit"] == (17 - 3) + (8 - 3) + (7 - 3)


def test_listing_pagination_depth_comes_from_strategy_limits(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    materials, _ = collect(client, site, [categories(site, limits={"crawl": {"max_depth": 2}})])
    # phones has 3 pages: page 3 (and its only product) is 2 steps away, its items would be at depth 3
    assert_exactly(
        site, materials, expected_sets["categories"] - {"/catalog/phones/?page=3", "/product/phone-eta"}
    )
    assert site.requests["/catalog/phones/?page=3"] == 0
    assert cursor_stats(client, "wp03", "categories")["chains_ended_by_depth"] == 1


def test_api_pagination_depth_comes_from_strategy_limits(client: TestClient, site: Site) -> None:
    strategy = {**api(site), "limits": {"crawl": {"max_depth": 2}}}
    materials, _ = collect(client, site, [strategy])
    assert len(materials) == 10  # two pages of five items
    assert site.requests["/api/v1/products?page=3"] == 0
    assert cursor_stats(client, "wp03", "api")["stopped_by_depth"] == 1


def test_url_template_size_comes_from_max_seed_urls(client: TestClient, site: Site) -> None:
    strategy = {
        "type": "url_template",
        "strategy_id": "archive",
        "template": site.url("/archive/{n}"),
        "variables": {"n": {"range": {"start": 1, "end": 1_000_000_000}}},
        "limits": {"crawl": {"max_seed_urls": 3}},
    }
    materials, _ = collect(client, site, [strategy])
    assert_exactly(site, materials, {"/archive/1", "/archive/2", "/archive/3"})
    assert cursor_stats(client, "wp03", "archive")["stopped_by_max_seed_urls"] == 1


def test_page_budget_stops_the_strategies(client: TestClient, site: Site) -> None:
    limits = {**FAST_LIMITS, "crawl": {"max_depth": 20, "max_pages_per_run": 3}}
    materials, view = collect(client, site, [sitemap(site), api(site)], limits=limits)
    assert materials == []  # the budget went to navigation documents
    fetched = sum(n for p, n in site.requests.items() if p != "/robots.txt")
    assert fetched == 3 and view["stats"]["fetched"] == 3


def test_incremental_run_rereads_navigation_documents_only(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    rules = web_rules(site, strategies=[sitemap(site), rss(site), api(site)])
    body = {"source_kind": "web", "source_id": "shop", "rules": rules, "limits": FAST_LIMITS}
    first = drain(client, start(client, body))
    assert_exactly(site, first, expected_sets["sitemap"] | expected_sets["feeds"] | expected_sets["api"])
    site.reset()
    cid = start(client, {**body, "mode": "incremental"})
    assert drain(client, cid) == []  # revisit.mode=never: every listed material is known
    assert wait_done(client, cid)["status"] == "succeeded"
    navigation = {
        p
        for p in site.requests
        if not p.startswith(("/product/", "/news/", "/pages/", "/about", "/catalog/"))
    }
    assert navigation - {"/", "/robots.txt"} == {
        "/sitemap.xml",
        "/sitemaps/products.xml",
        "/sitemaps/news.xml.gz",
        "/sitemaps/pages.xml",
        "/feeds/news.rss",
        "/api/v1/products",
        "/api/v1/products?page=2",
        "/api/v1/products?page=3",
        "/api/v1/products?page=4",
    }
    assert not [p for p in site.requests if p.startswith(("/product/", "/news/2026/"))]


@pytest.mark.parametrize(
    ("options", "pointers"),
    [
        ({"method": "POST", "body": {"q": "phones"}}, ["/strategies/0/method"]),
        ({"emit_items_as_materials": True}, ["/strategies/0/emit_items_as_materials"]),
        (
            {"method": "POST", "body": {}, "emit_items_as_materials": True},
            ["/strategies/0/method", "/strategies/0/emit_items_as_materials"],
        ),
    ],
    ids=["post", "json-materials", "both"],
)
def test_schema_valid_api_feed_options_are_rejected_before_job(
    client: TestClient, site: Site, options: dict[str, Any], pointers: list[str]
) -> None:
    strategy = {**api(site), **options}
    rules = web_rules(site, strategies=[strategy])
    report = client.post("/v1/rules/validations", json=rules).json()
    assert report["valid"] is True and report["supported"] is False, report
    assert report["errors"] == []
    assert [(w["pointer"], w["code"]) for w in report["warnings"]] == [
        (pointer, "unsupported_strategy") for pointer in pointers
    ]
    response = client.post(
        "/v1/collections",
        json={"source_kind": "web", "rules": rules, "limits": FAST_LIMITS},
        headers={"Idempotency-Key": "api-feed-unsupported"},
    )
    assert response.status_code == 422, response.text
    problem = response.json()
    assert problem["code"] == "validation_failed"
    assert [(e["pointer"], e["code"]) for e in problem["errors"]] == [
        ("/rules" + pointer, "unsupported_strategy") for pointer in pointers
    ]
    assert site.requests == {}
