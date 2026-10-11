"""A real indexed catalog remains reachable across bounded runs and retained-state GC."""

from __future__ import annotations

import contextlib
import sqlite3
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_web_collector.app import build_app
from jane_web_collector.state import SCHEMA, FrontierRow, LeaseLost, StateStore
from jane_web_collector.testing import FAST_LIMITS, REPO_ROOT, drain, make_settings, start, wait_done


@dataclass
class Catalog:
    base: str = ""
    shards: int = 1
    per_shard: int = 6
    extra: bool = False
    requests: list[str] = field(default_factory=list)
    hold_path: str | None = None
    entered: threading.Event = field(default_factory=threading.Event)
    release: threading.Event = field(default_factory=threading.Event)
    state_path: Path | None = None
    active_peak: int = 0

    def url(self, path: str) -> str:
        return self.base + path

    @property
    def products(self) -> set[str]:
        return {self.url(f"/product/{n}") for n in range(self.shards * self.per_shard)}


@pytest.fixture
def catalog() -> Iterator[Catalog]:
    catalog = Catalog()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            catalog.requests.append(self.path)
            if catalog.state_path is not None:
                with sqlite3.connect(catalog.state_path) as db:
                    counts = db.execute(
                        "SELECT COUNT(*) FROM frontier WHERE status IN ('pending', 'inflight') GROUP BY collection_id"
                    ).fetchall()
                    catalog.active_peak = max(
                        catalog.active_peak, max((count for (count,) in counts), default=0)
                    )
            if self.path == catalog.hold_path:
                catalog.entered.set()
                catalog.release.wait(timeout=20)
            if self.path == "/robots.txt":
                content, media_type = b"User-agent: *\nAllow: /\n", "text/plain"
            elif self.path == "/sitemap.xml":
                rows = "".join(
                    f"<sitemap><loc>{catalog.url(f'/shard-{n}.xml')}</loc></sitemap>"
                    for n in range(catalog.shards)
                )
                content, media_type = f"<sitemapindex>{rows}</sitemapindex>".encode(), "application/xml"
            elif self.path.startswith("/shard-"):
                shard = int(self.path.removeprefix("/shard-").removesuffix(".xml"))
                urls = [
                    catalog.url(f"/product/{n}")
                    for n in range(shard * catalog.per_shard, (shard + 1) * catalog.per_shard)
                ]
                if catalog.extra:
                    urls.append(catalog.url("/product/new"))
                rows = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
                content, media_type = f"<urlset>{rows}</urlset>".encode(), "application/xml"
            else:
                content, media_type = f"<html><h1>{self.path}</h1></html>".encode(), "text/html"
            if self.path.startswith("/product/") and self.headers.get("If-None-Match") == '"v1"':
                self.send_response(304)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", media_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("ETag", '"v1"')
            self.end_headers()
            with contextlib.suppress(BrokenPipeError, ConnectionResetError):
                self.wfile.write(content)

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    catalog.base = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield catalog
    finally:
        catalog.release.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _body(catalog: Catalog, budget: int) -> dict[str, Any]:
    return {
        "source_kind": "web",
        "source_id": "whole-catalog",
        "state_key": "catalog",
        "mode": "incremental",
        "rules": {
            "collector": "web",
            "scope": {"allowed_domains": ["127.0.0.1"]},
            "strategies": [
                {"type": "sitemap", "strategy_id": "catalog", "urls": [catalog.url("/sitemap.xml")]}
            ],
            "revisit": {"mode": "if_changed"},
        },
        "limits": {
            **FAST_LIMITS,
            "concurrency": {"max_parallel_fetches": 1, "max_parallel_fetches_per_host": 1},
            "crawl": {"max_depth": 20, "max_pages_per_run": budget},
        },
    }


def _run(client: TestClient, body: dict[str, Any]) -> tuple[str, set[str], dict[str, Any]]:
    cid = start(client, body)
    urls = {m["locator"]["canonical_url"] for m in drain(client, cid)}
    view = wait_done(client, cid)
    assert view["status"] == "succeeded", view
    assert view["stats"]["fetched"] <= body["limits"]["crawl"]["max_pages_per_run"]
    return cid, urls, view


def _settings(tmp_path: Path) -> Any:
    return make_settings(tmp_path, discovery_path=REPO_ROOT / "services/web-collector/strategies/discovery")


def test_three_bounded_runs_complete_the_catalog_without_revisiting(tmp_path: Path, catalog: Catalog) -> None:
    with TestClient(build_app(_settings(tmp_path))) as client:
        body = _body(catalog, 3)
        all_urls: set[str] = set()
        pending = []
        for _ in range(3):
            _, urls, view = _run(client, body)
            assert not all_urls & urls
            all_urls |= urls
            pending.append(view["stats"]["continuation_pending"])
            assert client.get("/v1/states/catalog").json()["frontier_size"] == pending[-1]
        assert all_urls == catalog.products
        assert pending == [5, 2, 0]
        assert catalog.requests.count("/sitemap.xml") == 1
        assert catalog.requests.count("/shard-0.xml") == 1
        assert all(catalog.requests.count(f"/product/{n}") == 1 for n in range(6))


def test_unfinished_index_survives_restart_and_retention_gc(tmp_path: Path, catalog: Catalog) -> None:
    catalog.shards, catalog.per_shard = 4, 2
    settings = _settings(tmp_path)
    body = _body(catalog, 2)
    with TestClient(build_app(settings)) as client:
        first, urls, view = _run(client, body)
        assert urls == set()
        assert view["stats"]["continuation_pending"] == 3
    state = StateStore(settings.state_dir / "state.db")
    assert state.expire_finished(time.time() + 1) == [first]
    assert state.get_collection(first)["expired"] == 1  # type: ignore[index]
    assert state.frontier_size_for_state_key("catalog") == 3
    with sqlite3.connect(state.path) as db:
        cached = db.execute("SELECT resource, LENGTH(body) FROM seed_navigation").fetchall()
        assert len(cached) == 2  # index + first shard, compressed and still replayable
        assert all(size > 0 for _, size in cached)
    state.close()
    with TestClient(build_app(settings)) as client:
        for _ in range(20):
            _, part, view = _run(client, body)
            urls |= part
            if not view["stats"]["continuation_pending"]:
                break
            state = StateStore(settings.state_dir / "state.db")
            state.expire_finished(time.time() + 1)
            state.close()
        assert urls == catalog.products
        assert view["stats"]["continuation_pending"] == 0
    assert catalog.requests.count("/sitemap.xml") == 1
    assert all(catalog.requests.count(f"/shard-{n}.xml") == 1 for n in range(4))
    assert all(catalog.requests.count(f"/product/{n}") == 1 for n in range(8))
    with sqlite3.connect(settings.state_dir / "state.db") as db:
        assert db.execute("SELECT COUNT(*) FROM seed_navigation").fetchone()[0] == 0


def test_changed_rules_do_not_adopt_the_old_queue(tmp_path: Path, catalog: Catalog) -> None:
    with TestClient(build_app(_settings(tmp_path))) as client:
        _, _, first = _run(client, _body(catalog, 3))
        assert first["stats"]["continuation_pending"] == 5
        body = _body(catalog, 3)
        body["rules"]["strategies"] = [
            {"type": "seed_list", "strategy_id": "chosen", "urls": [catalog.url("/product/5")]}
        ]
        _, urls, second = _run(client, body)
        assert urls == {catalog.url("/product/5")}
        assert second["stats"]["continuation_pending"] == 0


def test_new_urls_are_fetched_before_successful_revisits(tmp_path: Path, catalog: Catalog) -> None:
    with TestClient(build_app(_settings(tmp_path))) as client:
        body = _body(catalog, 20)
        body["rules"]["priorities"] = [{"pattern": {"value": catalog.url("/product/0")}, "priority": 50}]
        _, urls, first = _run(client, body)
        assert urls == catalog.products and first["stats"]["continuation_pending"] == 0
        catalog.extra = True
        catalog.requests.clear()
        body["limits"]["crawl"]["max_pages_per_run"] = 3
        body["limits"]["crawl"]["max_frontier_size"] = 2
        _, urls, _ = _run(client, body)
        assert urls == {catalog.url("/product/new")}
        assert [path for path in catalog.requests if path.startswith("/product/")] == ["/product/new"]


def test_queue_cap_spools_the_whole_catalog_across_four_runs(tmp_path: Path, catalog: Catalog) -> None:
    settings = _settings(tmp_path)
    body = _body(catalog, 3)
    body["limits"]["crawl"]["max_frontier_size"] = 2
    with TestClient(build_app(settings)) as client:
        catalog.state_path = settings.state_dir / "state.db"
        observed: set[str] = set()
        for _ in range(4):
            _, urls, view = _run(client, body)
            assert not observed & urls
            observed |= urls
            with sqlite3.connect(settings.state_dir / "state.db") as db:
                active = db.execute(
                    "SELECT COUNT(*) FROM frontier WHERE status IN ('pending', 'inflight') GROUP BY collection_id"
                ).fetchall()
                assert all(count <= 2 for (count,) in active)
            assert (
                client.get("/v1/states/catalog").json()["frontier_size"]
                == view["stats"]["continuation_pending"]
            )
        assert observed == catalog.products
        assert view["stats"]["continuation_pending"] == 0
        assert catalog.requests.count("/sitemap.xml") == 1
        assert catalog.active_peak <= 2


@pytest.mark.parametrize("terminal", ["cancelled", "failed"])
def test_unfinished_loans_return_after_terminal_borrower_and_gc(
    tmp_path: Path, catalog: Catalog, terminal: str
) -> None:
    settings = _settings(tmp_path)
    body = _body(catalog, 3)
    body["limits"]["crawl"]["max_frontier_size"] = 2
    with TestClient(build_app(settings)) as client:
        _, observed, _ = _run(client, body)
        catalog.hold_path = "/product/2"
        second_body = _body(catalog, 20)
        second_body["limits"]["crawl"]["max_frontier_size"] = 2
        borrower = start(client, second_body)
        assert catalog.entered.wait(timeout=10), catalog.requests
        assert client.post(f"/v1/jobs/{borrower}/cancel", json={"reason": "recovery test"}).status_code == 202
        assert wait_done(client, borrower)["status"] == "cancelled"
        completed = {m["locator"]["canonical_url"] for m in drain(client, borrower)}
        assert completed == {catalog.url("/product/1")}
        observed |= completed
        catalog.hold_path = None
        catalog.release.set()
        state = StateStore(settings.state_dir / "state.db")
        if terminal == "failed":
            # Exercise the failure terminal state with the exact same durable interrupted loan;
            # a core exception/timeout has the same recovery policy as this stored failure.
            state.set_status(borrower, "failed", finished_at="2026-10-11T00:00:00Z")
        state.expire_finished(time.time() + 1)
        state.close()
        for _ in range(3):
            _, urls, view = _run(client, second_body)
            assert not observed & urls
            observed |= urls
            if not view["stats"]["continuation_pending"]:
                break
        assert observed == catalog.products
        assert catalog.requests.count("/product/1") == 1
        with sqlite3.connect(settings.state_dir / "state.db") as db:
            assert db.execute("SELECT COUNT(*) FROM frontier_loans").fetchone()[0] == 0


def test_adoption_is_fenced_and_excludes_other_sources_and_cancelled_runs(tmp_path: Path) -> None:
    state = StateStore(tmp_path / "state.db")
    try:
        for cid in ("old", "new"):
            state.create_collection(
                cid,
                state_key="shared",
                status="running",
                request={},
                rules={},
                rules_ref=None,
                created_at="2026-10-11T00:00:00Z",
                effective_limits={},
            )
        assert state.claim("old", "writer", 30)
        with state.tx(("old", "writer")) as db:
            state.add_urls(db, "old", [FrontierRow("https://store.test/a", 0, 0, "material", "catalog")])
            state.defer_pending(db, "old", "shared", "source-and-rules", ["catalog"])
            state.set_status("old", "succeeded", finished_at="2026-10-11T00:00:01Z", db=db)
        assert state.claim("new", "writer", 30)
        with pytest.raises(LeaseLost), state.tx(("new", "stale-owner")) as db:
            state.adopt_deferred(db, "new", "shared", "source-and-rules", 1, lambda row: row)
        assert state.frontier_counts("old") == {"deferred": 1}
        with state.tx(("new", "writer")) as db:
            assert state.adopt_deferred(db, "new", "shared", "other-source", 1, lambda row: row)[0] == []
        state.set_status("old", "cancelled")
        with state.tx(("new", "writer")) as db:
            assert state.adopt_deferred(db, "new", "shared", "source-and-rules", 1, lambda row: row)[0] == []
    finally:
        state.close()


def test_gc_discards_cancelled_own_spool_without_stale_counters(tmp_path: Path) -> None:
    state = StateStore(tmp_path / "cancelled.db")
    try:
        state.create_collection(
            "cancelled",
            state_key="catalog",
            status="running",
            request={},
            rules={},
            rules_ref=None,
            created_at="2026-10-11T00:00:00Z",
            effective_limits={},
        )
        with state.tx() as db:
            state.add_overflow(
                db, "cancelled", FrontierRow("https://store.test/a", 0, 0, "material", "catalog")
            )
        state.set_status("cancelled", "cancelled", finished_at="2026-10-11T00:00:01Z")
        assert state.overflow_count("cancelled") == 1
        state.expire_finished(time.time() + 1)
        assert state.overflow_count("cancelled") == 0
        assert state.frontier_counts("cancelled") == {}
        with sqlite3.connect(state.path) as db:
            assert db.execute("SELECT COUNT(*) FROM frontier_overflow").fetchone()[0] == 0
    finally:
        state.close()


def test_large_unseen_frontier_keeps_known_selection_and_dequeue_indexed(tmp_path: Path) -> None:
    state = StateStore(tmp_path / "large.db")
    try:
        state.create_collection(
            "large",
            state_key="catalog",
            status="running",
            request={"mode": "incremental"},
            rules={},
            rules_ref=None,
            created_at="2026-10-11T00:00:00Z",
            effective_limits={},
        )
        known = "https://store.test/known"
        with state.tx() as db:
            db.execute(
                "INSERT INTO url_state(state_key, url, fetched_at, status) VALUES ('catalog', ?, ?, 200)",
                (known, time.time()),
            )
            state.add_urls(
                db,
                "large",
                (
                    FrontierRow(f"https://store.test/{n}", n % 17, 0, "material", "catalog")
                    for n in range(10_000)
                ),
            )
            state.add_urls(db, "large", [FrontierRow(known, 100, 0, "material", "catalog")])
            assert state.spool_known_pending(db, "large")
            assert state.frontier_row("large", known) is None
            assert not state.spool_known_pending(db, "large")
            known_plan = db.execute(
                "EXPLAIN QUERY PLAN SELECT * FROM frontier WHERE collection_id = ? AND status = 'pending' "
                "AND seen_before = 1 ORDER BY priority, seq DESC LIMIT 1",
                ("large",),
            ).fetchall()
            dequeue_plan = db.execute(
                "EXPLAIN QUERY PLAN SELECT * FROM frontier WHERE collection_id = ? AND status = 'pending' "
                "AND (? = 0 OR kind = 'material') ORDER BY seen_before, priority DESC, seq LIMIT ?",
                ("large", 0, 2),
            ).fetchall()
            for plan in (known_plan, dequeue_plan):
                details = " ".join(str(row[3]) for row in plan)
                assert "SEARCH frontier USING INDEX" in details, details
                assert "TEMP B-TREE" not in details, details
                print(details)
        assert state.overflow_count("large") == 1
        assert all(row.url != known for row in state.take_pending("large", 2))
    finally:
        state.close()


def test_legacy_frontier_backfills_the_indexed_marker_on_restart(tmp_path: Path) -> None:
    path = tmp_path / "legacy.db"
    known = "https://store.test/known"
    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA.replace("    seen_before INTEGER NOT NULL DEFAULT 0,\n", "", 1))
        db.execute(
            "INSERT INTO collections(collection_id, state_key, status, request, rules, created_at) "
            "VALUES ('legacy', 'catalog', 'running', '{}', '{}', '2026-10-11T00:00:00Z')"
        )
        db.execute(
            "INSERT INTO url_state(state_key, url, fetched_at, status) VALUES ('catalog', ?, ?, 200)",
            (known, time.time()),
        )
        db.execute(
            "INSERT INTO frontier(collection_id, url, status, priority, seq, depth, kind) "
            "VALUES ('legacy', ?, 'pending', 0, 1, 0, 'material')",
            (known,),
        )
    state = StateStore(path)
    try:
        with state.tx() as db:
            assert state.spool_known_pending(db, "legacy")
        assert state.overflow_count("legacy") == 1
    finally:
        state.close()
