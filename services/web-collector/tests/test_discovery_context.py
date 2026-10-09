"""R03: what ``DiscoveryContext.fetch`` shares with the core, what it returns and who sees the resource.

The documented semantics (``contracts/python/src/jane_contracts/discovery.py``, ``contracts/docs/discovery-strategy.md``)
checked on the real core: a probe strategy asks ``ctx.fetch`` for URLs with known answers, an observer strategy
records what reaches ``on_fetched``. Both are stand-ins registered under schema types the WP-03 package would
normally provide (it is not loaded in these core tests); the core, its fetcher and limiter are the real ones.
"""

from __future__ import annotations

import threading
from collections.abc import AsyncIterator, Iterator, Mapping
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, ClassVar, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource, FetchRejected
from jane_web_collector.testing import drain, start, wait_done

OUTCOMES: list[tuple[str, str]] = []
"""(path, what ``ctx.fetch`` gave the probe: ``resource:<status>``, ``none`` or ``rejected:<code>``), in order."""
NOTHING: tuple[DiscoveredUrl, ...] = ()
SEEN: list[tuple[str, int, str | None]] = []
"""What reached the observer's ``on_fetched``: (path, status, strategy that asked for the URL)."""


def _path(url: str) -> str:
    return "/" + url.split("/", 3)[3]


class Probe:
    """Stand-in registered as ``sitemap``: fetches its ``urls`` through ``ctx.fetch`` in ``seeds()``."""

    type_name: ClassVar[str] = "sitemap"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.urls = list(config.get("urls") or [])
        self.strategy_id = strategy_id

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for url in self.urls:
            try:
                res = await ctx.fetch(url, kind="navigation", conditional=False)
            except FetchRejected as exc:
                OUTCOMES.append((_path(url), f"rejected:{exc.code}"))
                continue
            OUTCOMES.append((_path(url), "none" if res is None else f"resource:{res.status}"))
        for cand in NOTHING:  # proposes nothing; an async generator all the same
            yield cand

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        if resource.strategy_id == self.strategy_id:
            OUTCOMES.append((_path(resource.url), "on_fetched called for the caller"))
        for cand in NOTHING:
            yield cand

    def snapshot(self) -> Mapping[str, Any]:
        return {}

    def restore(self, state: Mapping[str, Any]) -> None:
        pass


class Observer:
    """Stand-in registered as ``feed``: records every resource the core passes to ``on_fetched``."""

    type_name: ClassVar[str] = "feed"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.strategy_id = strategy_id

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for cand in NOTHING:
            yield cand

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        SEEN.append((_path(resource.url), resource.status, resource.strategy_id))
        for cand in NOTHING:
            yield cand

    def snapshot(self) -> Mapping[str, Any]:
        return {}

    def restore(self, state: Mapping[str, Any]) -> None:
        pass


@dataclass
class AnswersSite:
    base: str = ""
    hits: dict[str, int] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def host(self) -> str:
        return self.base.split("://", 1)[1].split(":")[0]


ROUTES: dict[str, tuple[int, dict[str, str], bytes]] = {
    "/robots.txt": (200, {"Content-Type": "text/plain"}, b"User-agent: *\nDisallow: /private\n"),
    "/ok": (200, {"Content-Type": "text/html"}, b"<html><body><a href='/ok2'>x</a></body></html>"),
    "/missing": (404, {"Content-Type": "text/html"}, b"<html><body>no such page</body></html>"),
    "/gone": (410, {"Content-Type": "text/html"}, b"<html><body>gone</body></html>"),
    "/not-implemented": (501, {"Content-Type": "text/plain"}, b"nope"),
    "/boom": (500, {"Content-Type": "text/plain"}, b"error"),
    "/slow-down": (429, {"Content-Type": "text/plain", "Retry-After": "3600"}, b"later"),
}


@pytest.fixture
def answers() -> Iterator[AnswersSite]:
    site = AnswersSite()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            with site.lock:
                site.hits[self.path] = site.hits.get(self.path, 0) + 1
            status, headers, body = ROUTES.get(
                self.path, (200, {"Content-Type": "text/html"}, b"<html></html>")
            )
            self.send_response(status)
            for k, v in {**headers, "Content-Length": str(len(body))}.items():
                self.send_header(k, v)
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


def test_fetch_semantics_and_on_fetched_of_other_strategies(client: TestClient, answers: AnswersSite) -> None:
    OUTCOMES.clear()
    SEEN.clear()
    registry = cast(FastAPI, client.app).state.engine.deps.registry
    registry.register(Probe)
    registry.register(Observer)
    paths = ["/ok", "/missing", "/gone", "/not-implemented", "/boom", "/slow-down", "/private/x", "/ok"]
    rules = {
        "collector": "web",
        "scope": {"allowed_domains": [answers.host]},
        "strategies": [
            {"type": "sitemap", "strategy_id": "probe", "urls": [answers.base + p for p in paths]},
            {"type": "sitemap", "strategy_id": "outside", "urls": ["https://elsewhere.example.org/x"]},
            {"type": "feed", "strategy_id": "observer"},
        ],
    }
    limits = {
        "rate": {"requests_per_second_per_host": 500, "min_delay_ms_per_host": 0},
        "retries": {"max_attempts": 2, "initial_backoff_ms": 0, "max_backoff_ms": 0},
    }
    cid = start(client, {"source_kind": "web", "rules": rules, "limits": limits})
    assert drain(client, cid) == []  # navigation documents are never emitted
    assert wait_done(client, cid)["status"] == "succeeded"

    assert sorted(OUTCOMES) == sorted(
        [
            ("/ok", "resource:200"),
            (
                "/missing",
                "resource:404",
            ),  # any final status is a resource: url_template counts misses with it
            ("/gone", "resource:410"),
            ("/not-implemented", "resource:501"),  # not a retried status
            ("/boom", "none"),  # 500 stayed failing after the retries: None, recorded in /errors
            ("/slow-down", "rejected:rate_limited"),  # the source asks to wait longer than the maximum
            ("/private/x", "rejected:access_denied_by_policy"),  # robots.txt
            ("/ok", "none"),  # already fetched for this collection: not fetched again
            ("/x", "rejected:out_of_scope"),
        ]
    )
    # every resource fetched for the probe reached the other strategy, whatever its status; not the caller
    assert sorted(SEEN) == sorted(
        [
            ("/ok", 200, "probe"),
            ("/missing", 404, "probe"),
            ("/gone", 410, "probe"),
            ("/not-implemented", 501, "probe"),
        ]
    )
    # one request per URL per collection (the repeated /ok is not fetched again); /boom retried, robots honoured
    assert answers.hits["/ok"] == 1 and answers.hits["/boom"] == 2 and "/private/x" not in answers.hits
    errors = {
        e["url"].rsplit("/", 1)[-1]: e["code"]
        for e in client.get(f"/v1/collections/{cid}/errors").json()["items"]
    }
    assert errors["boom"] == "source_unavailable" and errors["slow-down"] == "rate_limited"
    assert errors["x"] == "access_denied_by_policy" and errors["missing"] == "not_found"
