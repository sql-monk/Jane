"""WP-16 (post-M3) on the real core with this package, against real HTTP sites.

* R22 - ``api_feed``: ``emit_items_as_materials`` (every JSON item is a Material, the item URLs are not fetched)
  and ``method: POST`` with a JSON ``body`` (``DiscoveryContext`` 1.1), on the testsite fixture; POST is served by
  a test subclass of the unmodified testsite handler that answers a POST of the API like its GET.
* R23 - incremental runs: listing pages are re-read in full every run (new items on known pages are found, also
  with ``revisit.mode=if_changed``), a ``lastmod`` later than the last fetch forces a revisit and an older one
  never prevents one. A tiny site whose content the test changes between runs.
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from jane_testsite import server as testsite  # type: ignore[import-untyped]
from jane_web_collector.testing import FAST_LIMITS, REPO_ROOT, Site, drain, start, wait_done, web_rules

from .helpers import api, collect, seeds_and_recursion

SCHEMAS = REPO_ROOT / "contracts" / "schemas"


@pytest.fixture(scope="module")
def material_validator() -> Draft202012Validator:
    resources = [
        (path.resolve().as_uri(), Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
        for path in SCHEMAS.rglob("*.schema.json")
    ]
    registry: Registry[Any] = Registry().with_resources(resources)
    uri = (SCHEMAS / "material.schema.json").resolve().as_uri()
    return Draft202012Validator(
        {"$ref": uri}, registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER
    )


def _paths(materials: list[dict[str, Any]]) -> list[str]:
    out = []
    for m in materials:
        parts = urlsplit(m["locator"]["canonical_url"])
        out.append(parts.path + (f"?{parts.query}" if parts.query else ""))
    return out


# ============================================================================================== R22: api_feed
def test_api_feed_emits_json_items_as_materials(
    client: TestClient,
    site: Site,
    expected_sets: dict[str, set[str]],
    material_validator: Draft202012Validator,
) -> None:
    strategy = {**api(site), "emit_items_as_materials": True, "lastmod_path": "$.missing"}
    report = client.post("/v1/rules/validations", json=web_rules(site, strategies=[strategy])).json()
    assert report == {"valid": True, "supported": True, "errors": [], "warnings": []}
    materials, view = collect(client, site, [strategy])
    assert sorted(_paths(materials)) == sorted(expected_sets["api"])  # one material per item, each once
    assert not [p for p in site.requests if p.startswith("/product/")]  # item URLs are not fetched
    assert view["stats"]["emitted"] == len(expected_sets["api"]) and view["stats"]["by_strategy"] == {
        "api": len(expected_sets["api"])
    }
    for m in materials:
        assert not list(material_validator.iter_errors(m))
        assert m["format"] == {"media_type": "application/json", "content_kind": "json", "charset": "utf-8"}
        item = json.loads(m["content"]["data"])
        assert item["url"] == m["locator"]["url"] == m["locator"]["canonical_url"]
        assert m["revision"]["content_sha256"] == hashlib.sha256(m["content"]["data"].encode()).hexdigest()
        assert m["discovery"]["strategy"] == "api_feed"
        assert urlsplit(m["discovery"]["parent_url"]).path == "/api/v1/products"
        assert "http" not in m and "final_url" not in m["locator"]


def test_api_feed_items_combine_with_recursion_once_per_url(
    client: TestClient, site: Site, expected_sets: dict[str, set[str]]
) -> None:
    strategy = {**api(site), "emit_items_as_materials": True}
    materials, _ = collect(client, site, [strategy, *seeds_and_recursion(site)])
    canon = [m["locator"]["canonical_url"] for m in materials]
    assert len(canon) == len(set(canon))  # the item claims its URL: recursion does not fetch it again
    assert set(canon) == site.canonical(expected_sets["recursive"] | expected_sets["api"])
    json_items = {
        m["locator"]["canonical_url"] for m in materials if m["format"]["media_type"] == "application/json"
    }
    assert json_items == site.canonical(expected_sets["api"])
    assert not [p for p in site.requests if p in expected_sets["api"]]


def test_api_feed_items_in_incremental_runs_follow_revisit(client: TestClient, site: Site) -> None:
    strategy = {**api(site), "emit_items_as_materials": True}
    rules = web_rules(site, strategies=[strategy], revisit={"mode": "if_changed"})
    body = {"source_kind": "web", "source_id": "api-items", "rules": rules, "limits": FAST_LIMITS}
    first = drain(client, start(client, body))
    item = json.loads(
        next(m for m in first if m["locator"]["url"].endswith("/product/phone-alpha"))["content"]["data"]
    )
    control = site.url("/_e2e/products/phone-alpha")
    try:
        assert httpx.put(control, json={"price": "1.00"}, timeout=10).status_code == 200
        changed = drain(client, start(client, {**body, "mode": "incremental"}))
        assert _paths(changed) == ["/product/phone-alpha"]  # if_changed: only the item whose content changed
        assert json.loads(changed[0]["content"]["data"])["price"] == "1.00"
        never = {**body, "rules": web_rules(site, strategies=[strategy]), "mode": "incremental"}
        assert drain(client, start(client, never)) == []  # revisit.mode=never: known items rest
    finally:
        httpx.put(control, json={"price": item["price"]}, timeout=10)


class PostingSite(Site):
    """``Site`` that also logs POST requests: ``(path, content-type, body)``."""

    posts: list[tuple[str, str, bytes]]


@pytest.fixture
def post_site() -> Iterator[PostingSite]:
    holder = PostingSite(base="")
    holder.posts = []

    class Handler(testsite.TestSiteHandler):  # type: ignore[misc]
        """The unmodified testsite answers a POST of its API like the GET (with the query of the URL); a POST to
        ``/old-api`` is redirected with 307 (the method and body must be kept) and to ``/moved-api`` with 303."""

        def do_GET(self) -> None:
            with holder.lock:
                holder.requests[self.path] += 1
            super().do_GET()

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length") or "0")
            with holder.lock:
                holder.posts.append(
                    (self.path, self.headers.get("Content-Type", ""), self.rfile.read(length))
                )
            path = urlsplit(self.path).path
            if path in {"/old-api", "/moved-api"}:
                status = 307 if path == "/old-api" else 303
                self.send_response(status)
                query = urlsplit(self.path).query
                self.send_header("Location", "/api/v1/products" + (f"?{query}" if query else ""))
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            super().do_GET()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    holder.base = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield holder
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("pagination", ["next_url", "page"])
def test_api_feed_post_queries_every_page_with_the_json_body(
    client: TestClient, post_site: PostingSite, expected_sets: dict[str, set[str]], pagination: str
) -> None:
    query = {"filter": {"category": "all"}, "lang": "uk"}
    paging = (
        {"type": "next_url", "next_url_path": "$.next"}
        if pagination == "next_url"
        else {"type": "page", "page_param": "page"}
    )
    strategy = {**api(post_site, **paging), "method": "POST", "body": query}
    materials, _ = collect(client, post_site, [strategy])
    assert sorted(_paths(materials)) == sorted(expected_sets["api"])
    api_posts = [p for p in post_site.posts if p[0].startswith("/api/")]
    assert {urlsplit(p[0]).query for p in api_posts} >= {"page=2", "page=3", "page=4"}
    assert all(ctype == "application/json" and json.loads(body) == query for _, ctype, body in api_posts)
    assert not [p for p in post_site.requests if p.startswith("/api/")]  # no API page was read with GET


def test_api_feed_post_follows_redirects_by_their_method_rules(
    client: TestClient, post_site: PostingSite, expected_sets: dict[str, set[str]]
) -> None:
    query = {"q": "all"}
    kept = {
        **api(post_site),
        "strategy_id": "kept",
        "url": post_site.url("/old-api"),
        "method": "POST",
        "body": query,
    }
    materials, _ = collect(client, post_site, [kept])
    assert sorted(_paths(materials)) == sorted(expected_sets["api"])
    first = [p for p in post_site.posts if p[0] in {"/old-api", "/api/v1/products"}]
    assert [p[0] for p in first] == [
        "/old-api",
        "/api/v1/products",
    ]  # 307: the POST is repeated with its body
    assert all(json.loads(body) == query for _, _, body in first)
    post_site.posts.clear()
    post_site.reset()
    moved = {**kept, "strategy_id": "moved", "url": post_site.url("/moved-api")}
    rules = web_rules(post_site, strategies=[moved])
    cid = start(client, {"source_kind": "web", "source_id": "moved", "rules": rules, "limits": FAST_LIMITS})
    assert len(drain(client, cid)) == len(expected_sets["api"])
    posted = [p[0] for p in post_site.posts]
    assert posted[0] == "/moved-api" and "/api/v1/products" not in posted  # 303: not repeated as POST
    assert post_site.requests["/api/v1/products"] == 1  # ... but continued with GET, without the body
    assert {urlsplit(p).query for p in posted[1:]} == {"page=2", "page=3", "page=4"}  # next pages: POST again


# ============================================================================================== R23: incremental
@dataclass
class ChangingSite:
    """A site the test changes between runs: a paginated list (two items per page, ``rel=next``), item pages, a
    sitemap with ``lastmod``. Every page has an ``ETag`` and answers 304 to a matching ``If-None-Match``."""

    base: str = ""
    items: list[int] = field(default_factory=lambda: [1, 2, 3])
    lastmod: dict[str, datetime] = field(default_factory=dict)
    log: list[tuple[str, str | None]] = field(default_factory=list)
    """(path, If-None-Match) of every request."""
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def host(self) -> str:
        return self.base.split("://", 1)[1].split(":")[0]

    def url(self, path: str) -> str:
        return self.base + path

    def fetched(self, path: str) -> int:
        with self.lock:
            return sum(1 for p, _ in self.log if p == path)

    def conditional(self, path: str) -> list[str | None]:
        with self.lock:
            return [inm for p, inm in self.log if p == path]

    def clear(self) -> None:
        with self.lock:
            self.log.clear()

    def page(self, path: str, query: dict[str, list[str]]) -> tuple[int, str, str]:
        if path == "/robots.txt":
            return 200, "text/plain", "User-agent: *\nAllow: /\n"
        if path == "/list":
            n = int(query.get("page", ["1"])[0])
            chunk = self.items[(n - 1) * 2 : n * 2]
            links = "".join(f'<li><a href="/item/{i}">item {i}</a></li>' for i in chunk)
            more = f'<a rel="next" href="/list?page={n + 1}">next</a>' if len(self.items) > n * 2 else ""
            return 200, "text/html", f"<html><body><main><ul>{links}</ul></main>{more}</body></html>"
        if path.startswith("/item/") or path.startswith("/doc/"):
            return 200, "text/html", f"<html><head><title>{path}</title></head><body>{path}</body></html>"
        if path == "/sitemap.xml":
            rows = "".join(
                f"<url><loc>{self.base}{p}</loc><lastmod>{t.isoformat(timespec='seconds')}</lastmod></url>"
                for p, t in sorted(self.lastmod.items())
            )
            return (
                200,
                "application/xml",
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>',
            )
        return 404, "text/html", "<html><body>no</body></html>"


@pytest.fixture
def changing() -> Iterator[ChangingSite]:
    site = ChangingSite()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            parts = urlsplit(self.path)
            with site.lock:
                site.log.append((self.path, self.headers.get("If-None-Match")))
                status, ctype, text = site.page(parts.path, parse_qs(parts.query))
            body = text.encode()
            etag = '"' + hashlib.sha256(body).hexdigest()[:16] + '"'
            if status == 200 and self.headers.get("If-None-Match") == etag:
                self.send_response(304)
                self.send_header("ETag", etag)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("ETag", etag)
            self.end_headers()
            self.wfile.write(body)

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


def _rules(
    site: ChangingSite, strategies: list[dict[str, Any]], revisit: str, **extra: Any
) -> dict[str, Any]:
    return {
        "collector": "web",
        "scope": {"allowed_domains": [site.host]},
        "strategies": strategies,
        "revisit": {"mode": revisit},
        **extra,
    }


def _run(
    client: TestClient,
    site: ChangingSite,
    rules: dict[str, Any],
    mode: str,
    limits: dict[str, Any] | None = None,
) -> list[str]:
    body = {
        "source_kind": "web",
        "source_id": "changing",
        "rules": rules,
        "mode": mode,
        "limits": {**FAST_LIMITS, **(limits or {})},
    }
    cid = start(client, body)
    materials = drain(client, cid)
    assert wait_done(client, cid)["status"] == "succeeded"
    return sorted(_paths(materials))


@pytest.mark.parametrize("revisit", ["never", "if_changed"])
def test_listing_pages_are_reread_and_find_new_items(
    client: TestClient, changing: ChangingSite, revisit: str
) -> None:
    """A new item on the second page of a known category: before R23 an incremental run skipped the first page
    (``never``) or got 304 for it (``if_changed``), never learnt the next page and missed the item."""
    listing = {
        "type": "listing",
        "strategy_id": "category",
        "start_urls": [changing.url("/list?page=1")],
        "item_links": {"value": "main li a"},
    }
    rules = _rules(changing, [listing], revisit)
    assert _run(client, changing, rules, "full") == [
        "/item/1",
        "/item/2",
        "/item/3",
        "/list?page=1",
        "/list?page=2",
    ]
    changing.items.append(4)  # the second page gets a new item, the first one stays the same
    changing.clear()
    assert _run(client, changing, rules, "incremental") == ["/item/4", "/list?page=1", "/list?page=2"]
    assert changing.conditional("/list?page=1") == [None]  # read in full, never a conditional request
    assert changing.conditional("/list?page=2") == [None]
    # the known items follow revisit: not fetched (never) or answered 304 and not emitted (if_changed)
    assert changing.fetched("/item/1") == (0 if revisit == "never" else 1)


def test_lastmod_newer_than_the_last_fetch_forces_a_revisit(
    client: TestClient, changing: ChangingSite
) -> None:
    old = datetime(2026, 1, 1, tzinfo=UTC)
    changing.lastmod = {"/doc/a": old, "/doc/b": old}
    sitemap = {"type": "sitemap", "strategy_id": "sitemap", "urls": [changing.url("/sitemap.xml")]}
    never = _rules(changing, [sitemap], "never")
    assert _run(client, changing, never, "full") == ["/doc/a", "/doc/b"]
    changing.lastmod["/doc/b"] = datetime.now(UTC) + timedelta(seconds=5)  # changed after the last fetch
    changing.clear()
    assert _run(client, changing, never, "incremental") == ["/doc/b"]
    assert changing.fetched("/doc/a") == 0
    # without use_lastmod_for_revisit the sitemap passes no lastmod: revisit=never keeps both at rest
    changing.clear()
    quiet = _rules(changing, [{**sitemap, "use_lastmod_for_revisit": False}], "never")
    assert _run(client, changing, quiet, "incremental") == []
    # an older lastmod never prevents a revisit the rules allow (interval of 0 s: everything is due)
    changing.clear()
    interval = _rules(changing, [sitemap], "interval")
    assert _run(client, changing, interval, "incremental", {"crawl": {"revisit_interval_seconds": 0}}) == [
        "/doc/a",
        "/doc/b",
    ]
