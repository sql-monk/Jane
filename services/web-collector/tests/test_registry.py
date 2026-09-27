"""Strategy registry: built-ins, the WP-03 package directory plug-in point, llm_explore unsupported (ADR-0010)."""

from __future__ import annotations

import sys
import textwrap
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_contracts.discovery import DiscoveryStrategy
from jane_web_collector.app import build_app
from jane_web_collector.discovery import RecursiveStrategy, Registry, SeedListStrategy
from jane_web_collector.discovery.registry import DISCOVERY_MODULE
from jane_web_collector.testing import FAST_LIMITS, Site, drain, make_settings, start, web_rules

# A stand-in for WP-03's services/web-collector/strategies/discovery/ package, written to a temp dir.
# It only uses the public DiscoveryContext (ctx.fetch for a navigation document, then proposes URLs).
PLUGIN = """
from collections.abc import AsyncIterator, Mapping
from typing import Any, ClassVar

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource

from .helpers import parse_urlset


class FakeSitemap:
    type_name: ClassVar[str] = "sitemap"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.urls = list(config.get("urls") or [])
        self.strategy_id = strategy_id
        self.done: list[str] = []

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for url in self.urls:
            if url in self.done:
                continue
            res = await ctx.fetch(url, kind="navigation")
            self.done.append(url)
            if res is None:
                continue
            for loc in parse_urlset(res.body):
                yield DiscoveredUrl(url=loc, strategy_id=self.strategy_id, kind="navigation" if loc.endswith(".xml") else "material")

    async def on_fetched(self, resource: FetchedResource, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        if resource.strategy_id == self.strategy_id and resource.url.endswith(".xml"):
            for loc in parse_urlset(resource.body):
                yield DiscoveredUrl(url=loc, strategy_id=self.strategy_id, kind="material", depth=resource.depth)

    def snapshot(self) -> Mapping[str, Any]:
        return {"done": self.done}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.done = list(state.get("done", []))


STRATEGIES = [FakeSitemap]
"""
HELPERS = """
import re


def parse_urlset(body: bytes) -> list[str]:
    return re.findall(r"<loc>([^<]+)</loc>", body.decode("utf-8", "replace"))
"""


@pytest.fixture
def plugin_dir(tmp_path: Path) -> Iterator[Path]:
    path = tmp_path / "strategies" / "discovery"
    path.mkdir(parents=True)
    (path / "__init__.py").write_text(textwrap.dedent(PLUGIN), encoding="utf-8")
    (path / "helpers.py").write_text(textwrap.dedent(HELPERS), encoding="utf-8")
    yield path
    sys.modules.pop(DISCOVERY_MODULE, None)
    sys.modules.pop(f"{DISCOVERY_MODULE}.helpers", None)


def test_builtins_follow_the_protocol() -> None:
    reg = Registry.default(Path("does-not-exist"), use_entry_points=False)
    assert list(reg.types()) == ["recursive", "seed_list"]
    for cls in (SeedListStrategy, RecursiveStrategy):
        assert isinstance(cls({"type": cls.type_name, "urls": ["http://x.test/"]}, "s"), DiscoveryStrategy)
    assert not reg.supported("llm_explore")
    with pytest.raises(ValueError, match="reserved"):
        reg.register(type("Llm", (SeedListStrategy,), {"type_name": "llm_explore"}))
    with pytest.raises(ValueError, match="already registered"):
        reg.register(type("Other", (SeedListStrategy,), {"type_name": "recursive"}))


def test_discovery_package_is_loaded_and_combines_with_recursion(
    tmp_path: Path, plugin_dir: Path, site: Site
) -> None:
    reg = Registry.default(plugin_dir, use_entry_points=False)
    assert "sitemap" in reg.types()
    assert reg.origins["sitemap"].startswith("package:")
    with TestClient(build_app(make_settings(tmp_path, discovery_path=plugin_dir))) as client:
        assert "sitemap" in client.get("/v1/info").json()["capabilities"]["strategies"]
        rules = web_rules(
            site,
            strategies=[
                {"type": "sitemap", "strategy_id": "sm", "urls": [site.url("/sitemaps/products.xml")]},
                {"type": "recursive", "link_sources": ["a_href"]},
            ],
        )
        materials = drain(
            client, start(client, {"source_kind": "web", "rules": rules, "limits": FAST_LIMITS})
        )
    urls = {m["locator"]["canonical_url"] for m in materials}
    # the sitemap-only product (no links point to it) comes from the plug-in; recursion adds linked pages
    assert site.url("/product/sitemap-only-widget") in urls
    assert site.url("/news/") in urls
    assert site.url("/sitemaps/products.xml") not in urls  # navigation documents are not materials
    by = {m["discovery"]["strategy"] for m in materials}
    assert by == {"sitemap", "recursive"}


def test_broken_discovery_package_does_not_break_the_service(tmp_path: Path) -> None:
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "__init__.py").write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    reg = Registry.default(bad, use_entry_points=False)
    assert list(reg.types()) == ["recursive", "seed_list"]
    assert reg.load_errors and "boom" in reg.load_errors[0]
    sys.modules.pop(DISCOVERY_MODULE, None)


def test_llm_explore_is_valid_but_unsupported(client: TestClient, site: Site) -> None:
    rules = web_rules(site, strategies=[{"type": "llm_explore", "goal": "product pages"}])
    check = client.post("/v1/rules/validations", json=rules).json()
    assert check["valid"] is True
    assert check["supported"] is False
    assert check["warnings"][0]["pointer"] == "/strategies/0"
    r = client.post(
        "/v1/collections", json={"source_kind": "web", "rules": rules}, headers={"Idempotency-Key": "llm"}
    )
    assert r.status_code == 422
    assert r.json()["code"] == "validation_failed"
    assert r.json()["errors"][0]["pointer"] == "/rules/strategies/0"


def test_strategy_without_implementation_is_unsupported(client: TestClient, site: Site) -> None:
    rules = web_rules(site, strategies=[{"type": "feed", "urls": [site.url("/feeds/news.rss")]}])
    check = client.post("/v1/rules/validations", json=rules).json()
    assert check == {**check, "valid": True, "supported": False}
