"""Replay actual RST catalog RAW through the collector's navigation and admission.

Run: ``uv run --all-packages pytest examples/tests/test_automarket_navigation.py -q``.
The fixture is the stored RAW of the successful incremental run described by its
metadata. No website or deployed service is called by these tests.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_contracts.discovery import FetchedResource
from jane_kit.config import LimitLayer, ResolvedLimits, resolve_limits
from jane_web_collector.crawler import CrawlRun, RunDeps, StrategyContext
from jane_web_collector.discovery import Registry
from jane_web_collector.host_limits import HostLimiter
from jane_web_collector.settings import ServiceLimits, contract_layer, to_contract
from jane_web_collector.state import StateStore

EXAMPLES = Path(__file__).resolve().parents[1]
REPO = EXAMPLES.parent
FIXTURE = EXAMPLES / "automarket/evidence/fixtures/rst-index.html"
METADATA = FIXTURE.with_suffix(".json")
RULES = EXAMPLES / "sites/packages/autos.rst-rules/rules.json"


def _resolve(source: dict[str, Any] | None, request: dict[str, Any] | None) -> ResolvedLimits[ServiceLimits]:
    return resolve_limits(
        ServiceLimits,
        contract_layer(LimitLayer("source", source or {})),
        contract_layer(LimitLayer("request", request or {})),
    )


@asynccontextmanager
async def _run(
    tmp_path: Path, *, max_depth: int = 5, revisit_interval_seconds: int = 21600
) -> AsyncIterator[CrawlRun]:
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    limits = {"crawl": {"max_depth": max_depth, "revisit_interval_seconds": revisit_interval_seconds}}
    registry = Registry.default(REPO / "services/web-collector/strategies/discovery", use_entry_points=False)
    assert registry.load_errors == []
    state = StateStore(tmp_path / "state.db")
    try:
        async with httpx.AsyncClient() as client:
            deps = RunDeps(
                state=state,
                registry=registry,
                client=client,
                resolve=_resolve,
                transit=None,
                instance_id="rst-navigation-test",
                lease_seconds=30,
                heartbeat_seconds=5,
                user_agent="JaneBot/0.1",
                version="test",
                host_limiter=HostLimiter(_resolve(None, limits).limits),
            )
            yield CrawlRun(
                deps,
                {
                    "collection_id": "rst-navigation-test",
                    "state_key": "autos-rst",
                    "request": {"source_id": "autos-rst", "mode": "incremental", "limits": limits},
                    "rules": rules,
                },
            )
    finally:
        state.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("max_depth", [1, 5])
async def test_rst_raw_discovers_twenty_ads_in_scope_and_catalog_pagination(
    tmp_path: Path, max_depth: int
) -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    body = FIXTURE.read_bytes()
    assert hashlib.sha256(body).hexdigest() == metadata["sha256"]
    assert len(body) == metadata["size_bytes"]
    assert metadata["locator"]["url"] == metadata["locator"]["final_url"]
    async with _run(tmp_path, max_depth=max_depth) as run:
        config = run.rules["strategies"][0]
        sid = config["strategy_id"]
        strategy = run.deps.registry.get(config["type"])(config, sid)
        ctx = StrategyContext(run, sid, to_contract(run.limits))
        run.strategies.append((sid, strategy, ctx, max_depth))
        seeds = [candidate async for candidate in strategy.seeds(ctx)]
        assert [seed.url for seed in seeds] == [metadata["locator"]["url"]]
        assert run.admit(seeds, None)[0].section == "catalog"
        resource = FetchedResource(
            url=seeds[0].url,
            final_url=metadata["locator"]["final_url"],
            status=metadata["http_status"],
            media_type="text/html",
            headers={"content-type": metadata["content_type"]},
            body=body,
            fetched_at=datetime.fromisoformat(metadata["fetched_at"]),
            depth=0,
            strategy_id=sid,
            kind="material",
        )
        candidates = [candidate async for candidate in strategy.on_fetched(resource, ctx)]
        rows = run.admit(candidates, resource.depth)
        ads = [row for row in rows if row.section == "ad"]
        assert len(ads) == 20
        assert [row.url for row in ads] == metadata["expected_ad_urls"]
        assert all(row.depth == 1 and row.priority == 50 for row in ads)
        assert all(run.scope_reason(row.url) is None for row in rows)
        assert run.stats["skipped_out_of_scope"] == 0
        pagination = [row for row in rows if row.section == "catalog"]
        assert [row.url for row in pagination] == ([metadata["expected_next_page"]] if max_depth >= 2 else [])
        assert len(rows) == 20 + len(pagination)
        assert all(row.priority < ads[0].priority for row in pagination)


@pytest.mark.asyncio
@pytest.mark.parametrize(("interval", "skipped"), [(21600, True), (0, False)])
async def test_rst_recent_ads_are_revisited_by_one_run_zero_interval(
    tmp_path: Path, interval: int, skipped: bool
) -> None:
    """The observed zero-entity run was revisit suppression, not failed discovery."""
    async with _run(tmp_path, revisit_interval_seconds=interval) as run:
        previous = {"status": 200, "fetched_at": time.time() - 3600}
        assert run._revisit_skip(previous) is skipped
        run.mode = "full"
        assert run._revisit_skip(previous) is False
