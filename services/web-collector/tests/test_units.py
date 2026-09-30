"""Unit tests: URL normalization and patterns, scope, robots.txt, limits from configuration, per-host limits,
retries, service basics (health, info, metrics)."""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_kit.config import LimitLayer
from jane_web_collector.app import build_app
from jane_web_collector.robots import parse_robots
from jane_web_collector.settings import ServiceLimits, resolve_service_limits, to_contract
from jane_web_collector.testing import FAST_LIMITS, Site, drain, errors, make_settings, start, web_rules
from jane_web_collector.urls import Normalizer, Scope, UrlPattern, material_id


def test_normalization() -> None:
    n = Normalizer(strip_query_params=("utm_*", "sessionid"))
    assert (
        n.normalize("HTTP://Example.TEST:80/a/./b/../c?b=2&a=1&utm_source=x#frag")
        == "http://example.test/a/c?a=1&b=2"
    )
    assert n.normalize("https://example.test:443") == "https://example.test/"
    assert n.normalize("/x y", "https://example.test/dir/") == "https://example.test/x%20y"
    assert n.normalize("%7euser", "https://example.test/") == "https://example.test/~user"
    for bad in ("mailto:a@b.c", "tel:+1", "javascript:void(0)", "ftp://x.test/", ""):
        assert n.normalize(bad, "https://example.test/") is None
    assert Normalizer(trailing_slash="remove").normalize("https://e.test/a/") == "https://e.test/a"
    assert Normalizer(trailing_slash="add").normalize("https://e.test/a") == "https://e.test/a/"
    assert Normalizer(sort_query=False).normalize("https://e.test/?b=1&a=2") == "https://e.test/?b=1&a=2"
    assert material_id("https://e.test/") == material_id("https://e.test/")
    assert material_id("https://e.test/").startswith("web:") and len(material_id("https://e.test/")) == 36


def test_patterns_and_scope() -> None:
    glob = UrlPattern.from_rule({"value": "shop.test/product/*"})
    assert glob.matches("https://shop.test/product/a")
    assert not glob.matches("https://shop.test/product/a/b")
    assert UrlPattern.from_rule({"value": "shop.test/**"}).matches("https://shop.test/a/b?c=1")
    assert UrlPattern.from_rule({"type": "regex", "value": r"/news/\d+"}).matches("https://shop.test/news/12")
    scope = Scope.from_rules(
        {
            "scope": {
                "allowed_domains": ["shop.test"],
                "include_subdomains": True,
                "path_prefixes": ["/catalog", "/product"],
                "exclude": [{"value": "**/private/**"}],
                "allowed_schemes": ["https"],
            }
        }
    )
    assert scope is not None
    assert scope.check("https://shop.test/catalog/x") is None
    assert scope.check("https://m.shop.test/product/y") is None
    assert scope.check("http://shop.test/catalog/x") is not None
    assert scope.check("https://evilshop.test/catalog/x") is not None
    assert scope.check("https://shop.test/about") is not None
    assert scope.check("https://shop.test/catalog/private/1") is not None


def test_robots_parsing() -> None:
    text = """
    User-agent: *
    Disallow: /private/
    Allow: /private/public$
    Crawl-delay: 2

    User-agent: JaneBot
    User-agent: OtherBot
    Disallow: /nojane
    Disallow: /*.pdf$

    Sitemap: https://e.test/sitemap.xml
    """
    jane = parse_robots(text, "JaneBot")
    assert not jane.allowed("https://e.test/nojane/x")
    assert not jane.allowed("https://e.test/files/a.pdf")
    assert jane.allowed("https://e.test/files/a.pdf?x=1")
    assert jane.allowed("https://e.test/private/x")  # the specific group replaces "*"
    anyone = parse_robots(text, "Somebody")
    assert not anyone.allowed("https://e.test/private/x")
    assert anyone.allowed("https://e.test/private/public")  # longest match wins
    assert anyone.crawl_delay == 2
    assert anyone.sitemaps == ["https://e.test/sitemap.xml"]
    assert parse_robots("", "JaneBot").allowed("https://e.test/anything")


def test_limits_from_configuration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    profile = tmp_path / "limits.json"
    profile.write_text(
        '{"profile": "test", "defaults": {"crawl": {"max_depth": 3}, "sandbox": {"memory_mb": 64}},'
        ' "hard_caps": {"concurrency": {"max_parallel_fetches": 6}}}',
        encoding="utf-8",
    )
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS_FILE", str(profile))
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__RATE__MIN_DELAY_MS_PER_HOST", "250")
    settings = make_settings(tmp_path)
    resolved = resolve_service_limits(settings)
    assert resolved.limits.crawl.max_depth == 3  # file; the unrelated sandbox group is ignored
    assert resolved.limits.rate.min_delay_ms_per_host == 250  # env
    request = resolve_service_limits(
        settings,
        LimitLayer(
            "request",
            {"concurrency": {"max_parallel_fetches": 50}, "llm": {"max_requests_per_minute": 1}},
        ),
    )
    assert request.limits.concurrency.max_parallel_fetches == 6  # min(request, hard cap)
    assert request.provenance()["concurrency.max_parallel_fetches"] == "hard_cap"
    doc = to_contract(ServiceLimits())
    assert set(doc) == {"concurrency", "rate", "crawl", "timeouts", "retries", "queue", "transfer"}
    with TestClient(build_app(settings)) as client:
        info = client.get("/v1/info").json()
    assert info["limits"]["profile"] == "test"
    assert info["limits"]["defaults"]["crawl"]["max_depth"] == 3
    assert info["limits"]["hard_caps"] == {"concurrency": {"max_parallel_fetches": 6}}


def test_health_metrics_and_logs(client: TestClient) -> None:
    health = client.get("/v1/health").json()
    assert health == {"status": "ok", "checks": {"state_store": {"status": "ok"}}}
    client.get("/v1/info")
    assert 'route="/v1/info"' in client.get("/metrics").text


def test_per_host_rate_limit_is_applied(client: TestClient, site: Site) -> None:
    urls = [site.url(f"/product/{s}") for s in ("phone-alpha", "phone-beta", "phone-gamma", "phone-delta")]
    limits = {**FAST_LIMITS, "rate": {"requests_per_second_per_host": 5, "min_delay_ms_per_host": 0}}
    began = time.monotonic()
    cid = start(client, {"source_kind": "web", "rules": web_rules(site), "urls": urls, "limits": limits})
    assert len(drain(client, cid)) == 4
    # robots.txt + 4 pages = 5 requests at 5 rps on one host: at least 4 intervals of 0.2 s
    assert time.monotonic() - began >= 0.8


class _Flaky(BaseHTTPRequestHandler):
    hits: dict[str, int] = {}  # noqa: RUF012

    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        n = self.hits[self.path] = self.hits.get(self.path, 0) + 1
        if self.path == "/robots.txt":
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        status = 200 if (self.path == "/flaky" and n >= 3) else 503
        body = b"<html><title>ok</title></html>" if status == 200 else b""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def flaky() -> Iterator[str]:
    _Flaky.hits = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Flaky)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_retries_follow_the_retry_policy(client: TestClient, flaky: str) -> None:
    rules = {
        "collector": "web",
        "scope": {"allowed_domains": ["127.0.0.1"]},
        "strategies": [{"type": "seed_list", "urls": [flaky + "/flaky", flaky + "/down"]}],
    }
    limits = {**FAST_LIMITS, "retries": {"max_attempts": 3, "initial_backoff_ms": 10, "max_backoff_ms": 20}}
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": limits})
    materials = drain(client, cid)
    assert [m["locator"]["canonical_url"] for m in materials] == [flaky + "/flaky"]
    assert _Flaky.hits["/flaky"] == 3 and _Flaky.hits["/down"] == 3
    [err] = errors(client, cid)
    assert err["code"] == "source_unavailable" and err["http_status"] == 503 and err["attempts"] == 3
