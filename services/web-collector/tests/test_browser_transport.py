"""Browser document transport retains policies and returns the original response, without scripts."""

from __future__ import annotations

import contextlib
import threading
import time
from collections import Counter
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from jane_web_collector.app import build_app
from jane_web_collector.egress import EgressDenied, EgressPolicy
from jane_web_collector.fetcher import FetchError
from jane_web_collector.render import Renderer, RenderOptions
from jane_web_collector.settings import ServiceLimits
from jane_web_collector.testing import FAST_LIMITS, drain, errors, make_settings, start, wait_done

DOCUMENT_BODY = b'<html><body>original<script>fetch("/script-ran")</script><img src="/image"></body></html>'


@pytest.fixture
def browser_site() -> Iterator[tuple[str, Counter[str]]]:
    requests: Counter[str] = Counter()

    class Pages(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requests[self.path] += 1
            if self.path == "/no-content":
                self.send_response(204)
                self.end_headers()
                return
            if self.path == "/slow":
                time.sleep(0.5)
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "/target")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            body = b"User-agent: *\nDisallow: /private\n" if self.path == "/robots.txt" else DOCUMENT_BODY
            self.send_response(200)
            self.send_header("Content-Type", "text/plain" if self.path == "/robots.txt" else "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            with contextlib.suppress(BrokenPipeError, ConnectionResetError):
                self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Pages)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def browser_rules(base: str, path: str, *, exclude_target: bool = False) -> dict[str, Any]:
    return {
        "collector": "web",
        "scope": {
            "allowed_domains": ["127.0.0.1"],
            "exclude": [{"value": "**/target"}] if exclude_target else [],
        },
        "strategies": [{"type": "seed_list", "urls": [base + path]}],
        "robots": {"mode": "respect"},
        "fetch": {"transport": "browser"},
    }


@pytest.mark.usefixtures("chromium")
def test_browser_transport_collects_original_document_without_subrequests(
    tmp_path: Path, browser_site: tuple[str, Counter[str]]
) -> None:
    base, requests = browser_site
    with TestClient(build_app(make_settings(tmp_path))) as client:
        cid = start(
            client, {"source_kind": "web", "limits": FAST_LIMITS, "rules": browser_rules(base, "/document")}
        )
        materials = drain(client, cid)
        assert wait_done(client, cid)["status"] == "succeeded"
        assert errors(client, cid) == []
        [material] = materials
        assert '<script>fetch("/script-ran")</script>' in material["content"]["data"]
        assert any(item["code"] == "browser_transport" for item in material["diagnostics"])
    assert requests == {"/robots.txt": 1, "/document": 1}


@pytest.mark.usefixtures("chromium")
@pytest.mark.parametrize(("transport", "render_js"), [("browser", False), ("browser", True), ("http", False)])
def test_truncated_browser_download_is_charged_and_stops_at_run_budget(
    tmp_path: Path, browser_site: tuple[str, Counter[str]], transport: str, render_js: bool
) -> None:
    base, requests = browser_site
    config = browser_rules(base, "/document")
    config["fetch"]["transport"] = transport
    config["fetch"]["render_js"] = render_js
    config["strategies"][0]["urls"].append(base + "/second")
    limits = {
        **FAST_LIMITS,
        "crawl": {
            **FAST_LIMITS["crawl"],
            "max_material_bytes": 8,
            "max_bytes_per_run": len(DOCUMENT_BODY) - 1,
        },
        "concurrency": {"max_parallel_fetches": 1, "max_parallel_fetches_per_host": 1},
    }
    with TestClient(build_app(make_settings(tmp_path))) as client:
        cid = start(client, {"source_kind": "web", "limits": limits, "rules": config})
        materials = drain(client, cid)
        view = wait_done(client, cid)
        expected_pages = 1 if transport == "browser" else 2
        assert len(materials) == view["stats"]["fetched"] == expected_pages
        if render_js:
            assert all(len(material["content"]["data"].encode()) <= 8 for material in materials)
            assert all(
                any(item["code"] == "rendered" for item in material["diagnostics"]) for material in materials
            )
        else:
            assert all(material["content"]["data"] == DOCUMENT_BODY[:8].decode() for material in materials)
        assert all(
            any(item["code"] == "truncated" for item in material["diagnostics"]) for material in materials
        )
        if transport == "browser":
            assert view["stats"]["bytes_fetched"] >= len(DOCUMENT_BODY)
        else:
            assert view["stats"]["bytes_fetched"] == 16
    assert requests["/document"] == 1
    assert requests["/second"] == (0 if transport == "browser" else 1)
    assert requests["/script-ran"] == requests["/image"] == 0


@pytest.mark.usefixtures("chromium")
@pytest.mark.parametrize("exclude", [False, True])
def test_browser_transport_redirect_is_checked_before_requesting_target(
    tmp_path: Path, browser_site: tuple[str, Counter[str]], exclude: bool
) -> None:
    base, requests = browser_site
    with TestClient(build_app(make_settings(tmp_path))) as client:
        response = client.post(
            "/v1/fetches",
            json={
                "source_kind": "web",
                "url": base + "/redirect",
                "limits": FAST_LIMITS,
                "rules": browser_rules(base, "/redirect", exclude_target=exclude),
            },
        )
        if exclude:
            assert response.status_code == 422, response.text
            assert response.json()["code"] == "out_of_scope"
        else:
            assert response.status_code == 200, response.text
    assert requests["/redirect"] == 1
    assert requests["/target"] == (0 if exclude else 1)
    assert requests["/script-ran"] == requests["/image"] == 0


@pytest.mark.usefixtures("chromium")
def test_browser_transport_obeys_robots(tmp_path: Path, browser_site: tuple[str, Counter[str]]) -> None:
    base, requests = browser_site
    with TestClient(build_app(make_settings(tmp_path))) as client:
        response = client.post(
            "/v1/fetches",
            json={
                "source_kind": "web",
                "url": base + "/private",
                "limits": FAST_LIMITS,
                "rules": browser_rules(base, "/private"),
            },
        )
        assert response.status_code == 403, response.text
        assert response.json()["code"] == "access_denied_by_policy"
    assert requests == {"/robots.txt": 1}


@pytest.mark.usefixtures("chromium")
@pytest.mark.parametrize(
    ("path", "expected_status", "expected_body", "expected_truncated"),
    [("/document", 200, b"<html><b", True), ("/no-content", 204, b"", False)],
)
async def test_browser_transport_cuts_original_response_at_material_limit(
    browser_site: tuple[str, Counter[str]],
    path: str,
    expected_status: int,
    expected_body: bytes,
    expected_truncated: bool,
) -> None:
    base, requests = browser_site
    renderer = Renderer(RenderOptions(), EgressPolicy(), max_pages=ServiceLimits().collector.render_max_pages)
    try:
        status, headers, body, truncated, network_bytes = await renderer.fetch(
            base + path, headers={"User-Agent": "JaneTest/1.0"}, max_bytes=8, limits=ServiceLimits()
        )
        assert status == expected_status
        if expected_status == 200:
            assert headers["content-type"] == "text/html"
            assert network_bytes >= len(DOCUMENT_BODY)
        assert body == expected_body and truncated == expected_truncated
    finally:
        await renderer.aclose()
    assert requests == {path: 1}


async def test_browser_transport_unavailable_is_explicit() -> None:
    renderer = Renderer(
        RenderOptions(enabled=False), EgressPolicy(), max_pages=ServiceLimits().collector.render_max_pages
    )
    try:
        with pytest.raises(FetchError) as failure:
            await renderer.fetch("https://example.test/", headers={}, max_bytes=100, limits=ServiceLimits())
        assert failure.value.code == "not_implemented"
    finally:
        await renderer.aclose()


@pytest.mark.usefixtures("chromium")
async def test_browser_transport_honors_request_timeout(browser_site: tuple[str, Counter[str]]) -> None:
    base, _ = browser_site
    renderer = Renderer(RenderOptions(), EgressPolicy(), max_pages=ServiceLimits().collector.render_max_pages)
    limits = ServiceLimits()
    timeouts = limits.timeouts.model_copy(update={"request_timeout_ms": 50})
    try:
        with pytest.raises(httpx.TimeoutException):
            await renderer.fetch(base + "/slow", headers={}, max_bytes=1000, limits=limits, timeouts=timeouts)
    finally:
        await renderer.aclose()


@pytest.mark.usefixtures("chromium")
async def test_browser_transport_denies_metadata_egress() -> None:
    renderer = Renderer(RenderOptions(), EgressPolicy(), max_pages=ServiceLimits().collector.render_max_pages)
    try:
        with pytest.raises(EgressDenied):
            await renderer.fetch(
                "http://169.254.169.254/latest/meta-data/", headers={}, max_bytes=1000, limits=ServiceLimits()
            )
    finally:
        await renderer.aclose()


def test_browser_transport_unknown_value_is_rejected(
    tmp_path: Path, browser_site: tuple[str, Counter[str]]
) -> None:
    base, requests = browser_site
    config = browser_rules(base, "/document")
    config["fetch"]["transport"] = "unknown"
    with TestClient(build_app(make_settings(tmp_path))) as client:
        response = client.post(
            "/v1/fetches", json={"source_kind": "web", "url": base + "/document", "rules": config}
        )
        assert response.status_code == 422, response.text
    assert requests == {}


def test_browser_transport_managed_connection_is_rejected_before_network(
    tmp_path: Path, browser_site: tuple[str, Counter[str]]
) -> None:
    base, requests = browser_site
    config = browser_rules(base, "/document")
    config["fetch"]["connection_id"] = "unused-connection"
    with TestClient(build_app(make_settings(tmp_path))) as client:
        response = client.post(
            "/v1/fetches", json={"source_kind": "web", "url": base + "/document", "rules": config}
        )
        assert response.status_code == 422, response.text
        assert any(item["pointer"].endswith("/fetch/connection_id") for item in response.json()["errors"])
    assert requests == {}
