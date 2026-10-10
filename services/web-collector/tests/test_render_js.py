"""``fetch.render_js``: pages built by scripts are rendered in headless Chromium (``render.py``).

The collector is the real app, or the real :class:`Renderer` / :class:`EgressProxy`, against the real testsite;
only DNS answers are replaced (a resolver function) where a test needs a name that resolves to a chosen address.
Tests with the ``chromium`` fixture need the browser (``uv run playwright install chromium``): skipped without it
on a developer machine, failing in CI.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient

from jane_testsite import site as testsite  # type: ignore[import-untyped]
from jane_web_collector.app import build_app
from jane_web_collector.egress import EgressPolicy
from jane_web_collector.fetcher import HttpResult
from jane_web_collector.render import EgressProxy, Renderer, RenderOptions
from jane_web_collector.settings import ServiceLimits, Settings
from jane_web_collector.testing import FAST_LIMITS, Site, drain, errors, make_settings, start, wait_done

PRICE = f"{testsite.JS_OFFER.price} {testsite.JS_OFFER.currency}"  # written by the page's script only
MARKER = f'data-marker="{testsite.JS_MARKER}"'
RENDER_UA = "JaneRenderBot/2.0 (+https://example.test/bot)"


def rules(site: Site, *paths: str, render_js: bool = True, **fetch: Any) -> dict[str, Any]:
    return {
        "collector": "web",
        "scope": {"allowed_domains": [site.host]},
        "strategies": [{"type": "seed_list", "urls": [site.url(p) for p in paths]}],
        "fetch": {"render_js": render_js, **fetch},
    }


def collect(client: TestClient, body: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cid = start(client, {"source_kind": "web", "limits": FAST_LIMITS, **body})
    materials = drain(client, cid)
    assert wait_done(client, cid)["status"] == "succeeded"
    return materials, errors(client, cid)


def diagnostics(material: dict[str, Any]) -> dict[str, str]:
    return {d["code"]: d["message"] for d in material.get("diagnostics", [])}


# ---------------------------------------------------------------- without a browser


def test_without_render_js_the_scripted_content_is_missing(client: TestClient, site: Site) -> None:
    materials, errs = collect(client, {"rules": rules(site, testsite.JS_PRICE_PAGE, render_js=False)})
    assert errs == []
    [m] = materials
    html = m["content"]["data"]
    assert testsite.JS_OFFER.name in html and 'data-state="loading"' in html
    assert PRICE not in html and MARKER not in html and testsite.JS_OFFER.price not in html
    assert "rendered" not in diagnostics(m)
    assert site.requests[testsite.JS_PRICE_DATA] == 0  # no script ran


def test_render_unavailable_fails_the_url_and_the_collection_goes_on(tmp_path: Path, site: Site) -> None:
    settings = make_settings(tmp_path, render_enabled=False)
    with TestClient(build_app(settings)) as client:
        info = client.get("/v1/info").json()["capabilities"]
        assert info["render_js"] is False and "disabled" in info["render_js_unavailable"]
        body = {"rules": rules(site, testsite.JS_PRICE_PAGE, "/api/v1/products")}
        materials, errs = collect(client, body)
        # the JSON page is not HTML: nothing to render, it is collected; the HTML page fails, never a plain fetch
        assert [urlsplit(m["locator"]["url"]).path for m in materials] == ["/api/v1/products"]
        [err] = errs
        assert err["url"] == site.url(testsite.JS_PRICE_PAGE) and err["code"] == "not_implemented"
        assert "fetch.render_js" in err["message"] and "RENDER_ENABLED=false" in err["message"]
        one = client.post(
            "/v1/fetches",
            json={"source_kind": "web", "url": site.url(testsite.JS_PRICE_PAGE), "rules": body["rules"]},
        )
        assert one.status_code == 501 and one.json()["code"] == "not_implemented", one.text


def test_missing_browser_is_diagnosed(tmp_path: Path, site: Site) -> None:
    missing = tmp_path / "no-such-chromium"
    with TestClient(build_app(make_settings(tmp_path, render_browser_executable=missing))) as client:
        materials, errs = collect(client, {"rules": rules(site, testsite.JS_PRICE_PAGE)})
        assert materials == []
        [err] = errs
        assert err["code"] == "not_implemented"
        assert "could not start" in err["message"] and "playwright install chromium" in err["message"]
        info = client.get("/v1/info").json()["capabilities"]
        assert info["render_js"] is False and "could not start" in info["render_js_unavailable"]
    assert site.requests[testsite.JS_PRICE_DATA] == 0


def test_render_settings_come_from_the_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    defaults = Settings()
    assert defaults.render_enabled is True and defaults.render_wait_until == "networkidle"
    assert defaults.render_block_resource_types == ["image", "media", "font"]
    limits = ServiceLimits().collector
    assert (limits.render_timeout_ms, limits.render_extra_wait_ms, limits.render_max_pages) == (30_000, 0, 2)
    assert limits.render_max_transfer_bytes == 50 * 1024**2
    monkeypatch.setenv("JANE_WEB_COLLECTOR_RENDER_WAIT_UNTIL", "load")
    monkeypatch.setenv("JANE_WEB_COLLECTOR_RENDER_BLOCK_RESOURCE_TYPES", '["image", "stylesheet"]')
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__RENDER_TIMEOUT_MS", "5000")
    settings = make_settings(tmp_path)
    assert settings.render_wait_until == "load"
    assert settings.render_block_resource_types == ["image", "stylesheet"]
    with TestClient(build_app(settings)) as client:
        assert client.app.state.limits.limits.collector.render_timeout_ms == 5000  # type: ignore[attr-defined]


async def test_proxy_checks_every_connection(site: Site) -> None:
    """The egress proxy alone (no browser): plain HTTP and CONNECT, a denied name, the transfer budget."""
    port = int(site.base.rsplit(":", 1)[1])
    dns = fake_dns({"shop.example.test": ["127.0.0.1"], "metadata.example.test": ["169.254.169.254"]})
    proxy = EgressProxy(EgressPolicy(), resolver=dns, connect_timeout_s=5, max_bytes=10_000)
    await proxy.start()
    try:
        status, raw = await through(
            proxy, f"GET http://shop.example.test:{port}{testsite.JS_PRICE_DATA} HTTP/1.1"
        )
        assert status.startswith("HTTP/1.0 200") or status.startswith("HTTP/1.1 200"), status
        assert b"\r\nConnection: close\r\n" in raw and json.loads(raw.split(b"\r\n\r\n", 1)[1])["price"]
        assert site.requests[testsite.JS_PRICE_DATA] == 1 and proxy.connections == 1
        # plain HTTP to a denied address: no answer at all (a network error for the browser, not a page)
        status, raw = await through(proxy, "GET http://metadata.example.test/latest/meta-data/ HTTP/1.1")
        assert raw == b""
        status, _ = await through(proxy, "CONNECT metadata.example.test:443 HTTP/1.1")
        assert status.startswith("HTTP/1.1 403")
        assert len(proxy.denied) == 2 and all("169.254.169.254" in d for d in proxy.denied)
        assert await proxy.precheck("https://metadata.example.test/x") is not None
        assert await proxy.precheck(site.url("/")) is None
        # past the budget the page's connections are cut and no new one is opened
        proxy.max_bytes = 10
        await through(proxy, f"GET http://shop.example.test:{port}{testsite.JS_PRICE_DATA} HTTP/1.1")
        assert proxy.budget_exceeded
        status, _ = await through(proxy, f"CONNECT shop.example.test:{port} HTTP/1.1")
        assert status.startswith("HTTP/1.1 403") and proxy.connections == 2
    finally:
        await proxy.aclose()


# ---------------------------------------------------------------- with the browser


@pytest.mark.usefixtures("chromium")
def test_render_js_material_is_the_rendered_dom(client: TestClient, site: Site) -> None:
    body = {"rules": rules(site, testsite.JS_PRICE_PAGE, user_agent=RENDER_UA)}
    materials, errs = collect(client, body)
    assert errs == []
    [m] = materials
    html = m["content"]["data"]
    assert PRICE in html and MARKER in html and 'data-state="ready"' in html
    offer = '"offers":{"@type":"Offer","price":"1499.00","priceCurrency":"UAH"'  # JSON-LD added by the script
    assert offer in html
    assert m["format"]["media_type"] == "text/html" and m["format"]["charset"] == "utf-8"
    assert m["http"]["status"] == 200 and "etag" not in m["http"]["headers"]
    assert "rendered" in diagnostics(m) and "render_egress_denied" not in diagnostics(m)
    # the browser did not request the page again; its script asked the site for the data, as the collector
    assert site.requests[testsite.JS_PRICE_PAGE] == 1 and site.requests["/robots.txt"] == 1
    assert site.requests[testsite.JS_PRICE_DATA] == 1
    assert site.user_agents == {RENDER_UA}


@pytest.mark.usefixtures("chromium")
def test_render_js_subrequest_to_a_denied_address_is_refused(client: TestClient, site: Site) -> None:
    materials, errs = collect(client, {"rules": rules(site, testsite.JS_PROBE_PAGE)})
    assert errs == []
    [m] = materials
    html = m["content"]["data"]
    assert PRICE in html and "metadata: unreachable" in html
    denied = diagnostics(m)["render_egress_denied"]
    assert testsite.METADATA_PROBE_URL in denied and "169.254.169.254" in denied and "egress policy" in denied


@pytest.mark.usefixtures("chromium")
def test_rendered_dom_is_cut_at_max_material_bytes(client: TestClient, site: Site) -> None:
    raw = httpx.get(site.url(testsite.JS_PRICE_PAGE)).content
    limit = len(raw) + 40  # the document fits, the rendered DOM (JSON-LD, price, marker) does not
    limits = {**FAST_LIMITS, "crawl": {**FAST_LIMITS["crawl"], "max_material_bytes": limit}}
    materials, _ = collect(client, {"rules": rules(site, testsite.JS_PRICE_PAGE), "limits": limits})
    [m] = materials
    assert "truncated" in diagnostics(m) and "rendered" in diagnostics(m)
    assert len(m["content"]["data"].encode("utf-8")) <= limit


@pytest.mark.usefixtures("chromium")
def test_fetch_renders_as_well(client: TestClient, site: Site) -> None:
    url = site.url(testsite.JS_PRICE_PAGE)
    r = client.post(
        "/v1/fetches",
        json={"source_kind": "web", "url": url, "rules": rules(site, testsite.JS_PRICE_PAGE)},
    )
    assert r.status_code == 200, r.text
    assert PRICE in r.json()["content"]["data"] and "rendered" in diagnostics(r.json())
    assert client.get("/v1/info").json()["capabilities"]["render_js"] is True


@pytest.mark.usefixtures("chromium")
async def test_loopback_subrequests_go_through_the_proxy(site: Site) -> None:
    """With private addresses denied, the page's request to the site on 127.0.0.1 never reaches it: the browser
    has no way out except the egress proxy (Playwright proxies loopback too)."""
    page = await fetched(site, site.url(testsite.JS_PRICE_PAGE))
    renderer = Renderer(RenderOptions(), EgressPolicy(deny_private=True), max_pages=1)
    try:
        out = await renderer.render(page, user_agent=RENDER_UA, limits=ServiceLimits())
    finally:
        await renderer.aclose()
    html = out.body.decode("utf-8")
    assert MARKER in html and PRICE not in html and 'data-state="failed"' in html
    assert site.requests[testsite.JS_PRICE_DATA] == 0
    assert (
        "127.0.0.1" in out.diagnostics[-1]["message"]
        and out.diagnostics[-1]["code"] == "render_egress_denied"
    )


@pytest.mark.usefixtures("chromium")
async def test_browser_names_are_resolved_by_the_collector(site: Site) -> None:
    """``shop.example.test`` exists only in the collector's resolver: the browser reaches the site through it."""
    port = int(site.base.rsplit(":", 1)[1])
    page = await fetched(site, site.url(testsite.JS_PRICE_PAGE))
    page.url = page.final_url = f"http://shop.example.test:{port}{testsite.JS_PRICE_PAGE}"
    renderer = Renderer(
        RenderOptions(), EgressPolicy(), max_pages=1, resolver=fake_dns({"shop.example.test": ["127.0.0.1"]})
    )
    try:
        out = await renderer.render(page, user_agent=RENDER_UA, limits=ServiceLimits())
    finally:
        await renderer.aclose()
    assert PRICE in out.body.decode("utf-8") and site.requests[testsite.JS_PRICE_DATA] == 1


@pytest.mark.usefixtures("chromium")
async def test_dns_rebinding_is_caught_by_the_proxy(site: Site) -> None:
    """The router's check sees an allowed address, the connection would go to a denied one: the proxy checks the
    address it connects to, so nothing reaches either."""
    port = int(site.base.rsplit(":", 1)[1])
    answers = iter([["127.0.0.1"]])

    async def rebinding(host: str, port: int) -> list[str]:
        if host != "shop.example.test":
            raise OSError(f"unknown host {host}")
        return next(answers, ["169.254.169.254"])

    page = await fetched(site, site.url(testsite.JS_PRICE_PAGE))
    page.url = page.final_url = f"http://shop.example.test:{port}{testsite.JS_PRICE_PAGE}"
    renderer = Renderer(RenderOptions(), EgressPolicy(), max_pages=1, resolver=rebinding)
    try:
        out = await renderer.render(page, user_agent=RENDER_UA, limits=ServiceLimits())
    finally:
        await renderer.aclose()
    assert PRICE not in out.body.decode("utf-8") and site.requests[testsite.JS_PRICE_DATA] == 0
    denied = {d["code"]: d["message"] for d in out.diagnostics}["render_egress_denied"]
    assert "shop.example.test resolves to 169.254.169.254" in denied


# ---------------------------------------------------------------- helpers


def fake_dns(answers: dict[str, list[str]]) -> Callable[[str, int], Awaitable[list[str]]]:
    async def resolve(host: str, port: int) -> list[str]:
        if host not in answers:
            raise OSError(f"unknown host {host}")
        return answers[host]

    return resolve


async def fetched(site: Site, url: str) -> HttpResult:
    """The page as the fetcher hands it to the renderer (status, kept headers, body)."""
    async with httpx.AsyncClient() as http:
        r = await http.get(url)
    return HttpResult(
        url=url,
        final_url=url,
        status=r.status_code,
        headers={"content-type": r.headers["content-type"]},
        body=r.content,
        fetched_at=datetime.now(UTC),
    )


async def through(proxy: EgressProxy, request_line: str) -> tuple[str, bytes]:
    """Send one request to the proxy; returns the status line (``""`` if it closed without one) and all bytes."""
    reader, writer = await asyncio.open_connection("127.0.0.1", int(proxy.url.rsplit(":", 1)[1]))
    try:
        writer.write(f"{request_line}\r\nHost: x\r\n\r\n".encode())
        await writer.drain()
        if request_line.startswith("CONNECT"):
            raw = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 10)
        else:
            raw = await asyncio.wait_for(reader.read(-1), 10)
    except asyncio.IncompleteReadError as exc:
        raw = exc.partial
    finally:
        writer.close()
    return raw.split(b"\r\n", 1)[0].decode("latin-1") if raw else "", raw
