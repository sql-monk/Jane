"""S-M2-03: discovery strategies through the real Docker Web Collector HTTP API."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import TESTSITE

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(10)]

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ROOT / "tests" / "fixtures" / "testsite" / "expected_urls.json"
RULES = Path(__file__).parent / "config" / "rules" / "testsite.web-rules" / "1.0.0" / "rules.json"
ITEMS = {"value": "main li a"}


def _url(path: str) -> str:
    return TESTSITE + path


def _strategies() -> dict[str, list[dict[str, Any]]]:
    return {
        "recursive": [{"type": "seed_list", "urls": [_url("/")]}, {"type": "recursive"}],
        "sitemap": [{"type": "sitemap", "urls": [_url("/sitemap.xml")]}],
        "feeds": [{"type": "feed", "urls": [_url("/feeds/news.rss")]}],
        "categories": [
            {
                "type": "listing",
                "start_urls": [_url(f"/catalog/{c}/") for c in ("phones", "laptops", "accessories")],
                "item_links": ITEMS,
            }
        ],
        "search": [
            {
                "type": "listing",
                "start_urls": [_url("/search?q=phone")],
                "search": {"url_template": _url("/search?q={query}"), "queries": ["cable"]},
                "item_links": ITEMS,
            }
        ],
        "api": [
            {
                "type": "api_feed",
                "url": _url("/api/v1/products"),
                "items_path": "$.items",
                "url_path": "$.url",
                "pagination": {"type": "next_url", "next_url_path": "$.next"},
            }
        ],
        "template": [
            {
                "type": "url_template",
                "template": _url("/archive/{n}"),
                "variables": {"n": {"range": {"start": 1, "end": 50}}},
                "stop_after_consecutive_misses": 2,
            }
        ],
    }


def _path(url: str) -> str:
    parsed = urlsplit(url)
    query = "&".join(sorted(parsed.query.split("&"))) if parsed.query else ""
    return parsed.path + (f"?{query}" if query else "")


def _expected(*names: str) -> set[str]:
    sets = json.loads(EXPECTED.read_text(encoding="utf-8"))["sets"]
    return {_path(path) for name in names for path in sets[name]}


def _collect(
    collector: JaneClient, run_id: str, strategies: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    rules["strategies"] = strategies
    response = collector.api("collector").post(
        "/v1/collections",
        json={"source_kind": "web", "source_id": f"m2-{run_id}", "rules": rules},
        headers={"Idempotency-Key": f"m2-discovery-{run_id}"},
    )
    assert response.status_code == 202, response.text
    collection_id = response.json()["job_id"]
    materials: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        params: dict[str, Any] = {"wait_ms": 2000, **({"after": after} if after else {})}
        page_response = collector.api("collector").get(
            f"/v1/collections/{collection_id}/materials", params=params
        )
        assert page_response.status_code == 200, page_response.text
        page = page_response.json()
        materials.extend(page["items"])
        after = page.get("next_cursor") or after
        if page["end_of_stream"]:
            view_response = collector.api("collector").get(f"/v1/collections/{collection_id}")
            assert view_response.status_code == 200, view_response.text
            view = view_response.json()
            assert view["status"] == "succeeded", view
            return materials, view
    raise TimeoutError(f"collection {collection_id} did not finish")


def _errors(collector: JaneClient, collection_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        params = {"limit": 200, **({"cursor": cursor} if cursor else {})}
        response = collector.api("collector").get(f"/v1/collections/{collection_id}/errors", params=params)
        assert response.status_code == 200, response.text
        page = response.json()
        items.extend(page["items"])
        cursor = page.get("next_cursor")
        if not cursor:
            return items


def _assert_paths(materials: list[dict[str, Any]], expected: set[str]) -> None:
    canonical = [m["locator"]["canonical_url"] for m in materials]
    paths = [_path(url) for url in canonical]
    assert len(paths) == len(set(paths)), "duplicate canonical URL"
    assert set(paths) == expected, {
        "missing": sorted(expected - set(paths)),
        "unexpected": sorted(set(paths) - expected),
    }
    fixture = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert not set(paths) & set(fixture["sets"]["robots_disallowed"])
    assert all(not path.startswith(fixture["trap_prefix"]) for path in paths)
    assert all(urlsplit(url).hostname == "testsite" for url in canonical)
    assert all(urlsplit(m["locator"]["final_url"]).hostname == "testsite" for m in materials)
    assert not set(canonical) & set(fixture["external_links"])
    assert not set(paths) & set(fixture["redirects"])


@pytest.mark.parametrize(
    ("strategy", "expected_names"),
    [
        ("recursive", ("recursive",)),
        ("sitemap", ("sitemap",)),
        ("feeds", ("feeds",)),
        ("categories", ("categories",)),
        ("search", ("search:phone", "search:cable")),
        ("api", ("api",)),
        ("template", ("template:/archive/{n}",)),
    ],
)
def test_s_m2_03_each_strategy(
    require: Callable[..., None],
    client: Callable[..., JaneClient],
    run_id: str,
    strategy: str,
    expected_names: tuple[str, ...],
) -> None:
    require("testsite", "web-collector")
    collector = client("web-collector")
    materials, view = _collect(collector, run_id, _strategies()[strategy])
    _assert_paths(materials, _expected(*expected_names))
    if strategy == "recursive":
        fixture = json.loads(EXPECTED.read_text(encoding="utf-8"))
        assert view["stats"]["skipped_robots"] == len(fixture["sets"]["robots_disallowed"])
        assert view["stats"]["skipped_out_of_scope"] > 0  # external links and the calendar trap
        denied = {
            _path(error["url"])
            for error in _errors(collector, view["collection_id"])
            if error["code"] == "access_denied_by_policy"
        }
        assert denied == set(fixture["sets"]["robots_disallowed"])


@pytest.mark.parametrize(
    ("strategies", "expected_names", "only_names"),
    [
        (("sitemap", "recursive"), ("sitemap", "recursive"), ("only:sitemap",)),
        (("api", "recursive"), ("api", "recursive"), ("only:api",)),
        (("feeds", "template"), ("feeds", "template:/archive/{n}"), ("only:feeds", "only:template")),
    ],
)
def test_s_m2_03_strategy_combinations(
    require: Callable[..., None],
    client: Callable[..., JaneClient],
    run_id: str,
    strategies: tuple[str, ...],
    expected_names: tuple[str, ...],
    only_names: tuple[str, ...],
) -> None:
    require("testsite", "web-collector")
    selected = [part for name in strategies for part in _strategies()[name]]
    materials, _ = _collect(client("web-collector"), run_id, selected)
    _assert_paths(materials, _expected(*expected_names))
    paths = {_path(m["locator"]["canonical_url"]) for m in materials}
    assert _expected(*only_names) <= paths
