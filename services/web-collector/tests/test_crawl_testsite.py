"""WP-02 «Готово, коли» against the real testsite: no cycles, no leaving the bounds, robots.txt obeyed.

Also: explicit URL list, depth limit on the infinite calendar, dedup of redirects/tracking/fragments,
revisits with conditional requests, backpressure, budgets.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

from jane_web_collector.testing import FAST_LIMITS, Site, drain, errors, start, wait_done, web_rules


def _paths(site: Site, materials: list[dict[str, Any]]) -> list[str]:
    return [m["locator"]["canonical_url"] for m in materials]


def test_recursive_crawl_has_no_cycles_and_stays_in_bounds(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    cid = start(
        client,
        {"source_kind": "web", "source_id": "testsite", "rules": web_rules(site), "limits": FAST_LIMITS},
    )
    materials = drain(client, cid)
    view = wait_done(client, cid)
    assert view["status"] == "succeeded", view

    canon = _paths(site, materials)
    # exactly the expected set of the testsite (recursive from "/", robots, normalization, no /calendar/)
    assert set(canon) == site.canonical(expected_sets["recursive"])
    # no cycles: every URL emitted once and fetched from the site at most once
    assert len(canon) == len(set(canon))
    repeated = {path: n for path, n in site.requests.items() if n > 1}
    assert repeated == {}, repeated
    # never outside the bounds: everything fetched is on the testsite host, nothing under /calendar/
    for m in materials:
        assert urlsplit(m["locator"]["final_url"]).hostname == site.host
    assert not [p for p in site.requests if p.startswith("/calendar/")]
    stats = view["stats"]
    assert stats["emitted"] == len(materials)
    assert stats["skipped_out_of_scope"] > 0  # external links, calendar, mailto/tel are filtered
    assert stats["duplicates"] > 0  # loops, self links, tracking/fragment variants


def test_robots_txt_is_respected(client: TestClient, site: Site, expected_sets: dict[str, set[str]]) -> None:
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "limits": FAST_LIMITS})
    drain(client, cid)
    view = wait_done(client, cid)
    # the private pages are linked from "/" but never requested
    for path in expected_sets["robots_disallowed"]:
        assert site.requests[path] == 0, path
    assert site.requests["/robots.txt"] == 1  # fetched once and cached
    denied = [e for e in errors(client, cid) if e["code"] == "access_denied_by_policy"]
    assert {urlsplit(e["url"]).path for e in denied} == expected_sets["robots_disallowed"]
    assert view["stats"]["skipped_robots"] == len(expected_sets["robots_disallowed"])


def test_robots_user_agent_group_is_matched(client: TestClient, site: Site) -> None:
    """testsite's robots.txt disallows everything for BadBot: a collector identifying as BadBot fetches nothing."""
    rules = web_rules(site, fetch={"user_agent": "BadBot/1.0"})
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
    assert drain(client, cid) == []
    assert set(site.requests) == {"/robots.txt"}
    assert "BadBot/1.0" in site.user_agents


def test_owner_policy_explicitly_overrides_robots(client: TestClient, site: Site) -> None:
    rules = web_rules(
        site,
        robots={
            "mode": "owner_policy",
            "owner_policy": {"confirmed_owner": True, "justification": "Our own test site, owner allows it."},
        },
    )
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
    canon = _paths(site, drain(client, cid))
    assert site.url("/private/admin") in canon
    assert site.requests["/robots.txt"] == 0


def test_depth_limit_stops_the_infinite_calendar(client: TestClient, site: Site) -> None:
    """Without the exclude rule the calendar is an endless chain; crawl.max_depth ends the crawl."""
    rules = web_rules(site, scope={"allowed_domains": [site.host]})
    limits = {**FAST_LIMITS, "crawl": {"max_depth": 4}}
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": limits})
    materials = drain(client, cid)
    assert wait_done(client, cid)["status"] == "succeeded"
    depths = [m["discovery"]["depth"] for m in materials]
    assert max(depths) <= 4
    calendar = [p for p in site.requests if p.startswith("/calendar/")]
    assert 0 < len(calendar) <= 4  # "/" -> calendar at depth 1 .. 4


def test_explicit_url_list_fetches_only_those(client: TestClient, site: Site) -> None:
    urls = [site.url("/product/phone-alpha"), site.url("/about"), site.url("/missing-page")]
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "urls": urls, "limits": FAST_LIMITS})
    materials = drain(client, cid)
    assert set(_paths(site, materials)) == {site.url("/product/phone-alpha"), site.url("/about")}
    assert all(m["discovery"]["strategy"] == "seed_list" for m in materials)
    errs = errors(client, cid)
    assert [(urlsplit(e["url"]).path, e["code"], e.get("http_status")) for e in errs] == [
        ("/missing-page", "not_found", 404)
    ]
    assert set(site.requests) == {"/robots.txt", "/product/phone-alpha", "/about", "/missing-page"}


def test_seed_list_home_page_only(client: TestClient, site: Site) -> None:
    rules = web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/")]}])
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
    materials = drain(client, cid)
    assert _paths(site, materials) == [site.url("/")]
    m = materials[0]
    assert m["material_id"].startswith("web:")
    assert m["content"]["kind"] == "inline"
    assert m["content"]["encoding"] == "utf-8"
    assert "Jane test shop" in m["content"]["data"]
    assert m["format"] == {"media_type": "text/html", "charset": "utf-8", "content_kind": "page"}


def test_redirects_are_followed_and_deduplicated(client: TestClient, site: Site) -> None:
    urls = [site.url("/old/catalog"), site.url("/catalog/"), site.url("/about/")]
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "urls": urls, "limits": FAST_LIMITS})
    materials = drain(client, cid)
    canon = _paths(site, materials)
    assert sorted(canon) == sorted({site.url("/catalog/"), site.url("/about")})
    redirected = [m for m in materials if m["http"].get("redirects")]
    assert redirected and all(m["locator"]["url"] != m["locator"]["final_url"] for m in redirected)


def test_max_pages_budget_stops_the_run(client: TestClient, site: Site) -> None:
    limits = {**FAST_LIMITS, "crawl": {"max_depth": 20, "max_pages_per_run": 5}}
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "limits": limits})
    materials = drain(client, cid)
    view = wait_done(client, cid)
    assert view["status"] == "succeeded"
    assert view["stats"]["fetched"] == 5
    assert len(materials) <= 5
    assert view["effective_limits"]["crawl"]["max_pages_per_run"] == 5


def test_backpressure_pauses_until_materials_are_pulled(client: TestClient, site: Site) -> None:
    limits = {**FAST_LIMITS, "queue": {"max_unacked_materials": 3}}
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "limits": limits})
    import time

    deadline = time.monotonic() + 10
    view: dict[str, Any] = {}
    while time.monotonic() < deadline:
        view = client.get(f"/v1/collections/{cid}").json()
        if view["paused_by_backpressure"]:
            break
        time.sleep(0.05)
    assert view["paused_by_backpressure"] is True
    assert view["stats"]["unacked"] <= 3 + FAST_LIMITS["concurrency"]["max_parallel_fetches"]
    fetched_while_paused = view["stats"]["fetched"]
    time.sleep(0.5)
    assert client.get(f"/v1/collections/{cid}").json()["stats"]["fetched"] <= fetched_while_paused + 4
    materials = drain(client, cid)  # pulling acknowledges and releases the crawl
    assert wait_done(client, cid)["status"] == "succeeded"
    assert len(materials) > 10


def test_unacked_materials_are_redelivered_with_same_observation(client: TestClient, site: Site) -> None:
    rules = web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/"), site.url("/about")]}])
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
    wait_done(client, cid)
    first = client.get(f"/v1/collections/{cid}/materials", params={"limit": 1}).json()
    again = client.get(f"/v1/collections/{cid}/materials", params={"limit": 1}).json()
    assert first["items"][0]["observation_id"] == again["items"][0]["observation_id"]  # not acked yet
    nxt = client.get(f"/v1/collections/{cid}/materials", params={"after": first["next_cursor"]}).json()
    assert [m["observation_id"] for m in nxt["items"]] != [first["items"][0]["observation_id"]]
    assert nxt["end_of_stream"] is True
    done = client.get(f"/v1/collections/{cid}/materials", params={"after": nxt["next_cursor"]}).json()
    assert done["items"] == [] and done["end_of_stream"] is True


def test_incremental_revisit_uses_conditional_requests(client: TestClient, site: Site) -> None:
    rules = web_rules(site, revisit={"mode": "if_changed"})
    body = {"source_kind": "web", "state_key": "revisit", "rules": rules, "limits": FAST_LIMITS}
    first = start(client, body)
    n_first = len(drain(client, first))
    wait_done(client, first)
    site.reset()
    second = start(client, {**body, "mode": "incremental"})
    materials = drain(client, second)
    view = wait_done(client, second)
    # every page answered 304 (ETag), nothing re-emitted, but the crawl still covered the site via stored links
    assert materials == []
    assert view["stats"]["not_modified"] == n_first
    state = client.get("/v1/states/revisit").json()
    assert state["known_urls"] >= n_first
    assert state["frontier_size"] == 0


def test_incremental_never_skips_known_urls(client: TestClient, site: Site) -> None:
    rules = web_rules(site, revisit={"mode": "never"})
    body = {"source_kind": "web", "state_key": "never", "rules": rules, "limits": FAST_LIMITS}
    first = start(client, body)
    drain(client, first)
    site.reset()
    second = start(client, {**body, "mode": "incremental"})
    assert drain(client, second) == []
    assert [p for p in site.requests if p != "/robots.txt"] == []


def test_full_mode_emits_new_observations(client: TestClient, site: Site) -> None:
    rules = web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/about")]}])
    body = {"source_kind": "web", "state_key": "full", "rules": rules, "limits": FAST_LIMITS}
    a = drain(client, start(client, body))
    b = drain(client, start(client, body))
    assert a[0]["material_id"] == b[0]["material_id"]
    assert a[0]["observation_id"] != b[0]["observation_id"]
    assert a[0]["revision"]["content_sha256"] == b[0]["revision"]["content_sha256"]


def test_sections_priorities_and_metadata(client: TestClient, site: Site) -> None:
    rules = web_rules(
        site,
        sections=[{"section_id": "products", "patterns": [{"value": "*/product/*"}]}],
        priorities=[{"pattern": {"value": "*/news/**"}, "priority": 50}],
    )
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
    materials = drain(client, cid)
    products = [m for m in materials if "/product/" in m["locator"]["canonical_url"]]
    assert products and all(m["discovery"]["section"] == "products" for m in products)
    news = [m for m in materials if "/news/2026/" in m["locator"]["canonical_url"]]
    assert news and all(m["discovery"]["priority"] == 50 for m in news)
    article = news[0]
    assert article["published_at"].endswith("Z") and article["edited_at"].endswith("Z")
    assert article["metadata"]["title"]


def test_large_material_without_blob_store_is_an_error(client: TestClient, site: Site) -> None:
    limits = {**FAST_LIMITS, "transfer": {"inline_max_bytes": 100}}
    urls = [site.url("/about")]
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "urls": urls, "limits": limits})
    assert drain(client, cid) == []
    assert [e["code"] for e in errors(client, cid)] == ["limit_exceeded"]
