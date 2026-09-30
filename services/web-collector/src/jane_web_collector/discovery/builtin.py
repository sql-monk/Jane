"""Built-in discovery strategies of the core: ``seed_list`` (explicit list / home page) and ``recursive``."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any, ClassVar

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource

from ..urls import compile_patterns, patterns_match
from .links import is_html

__all__ = ["RecursiveStrategy", "SeedListStrategy"]


class SeedListStrategy:
    """Explicit list of URLs (or just the home page). Seeds have ``depth=0``; no reaction to other pages."""

    type_name: ClassVar[str] = "seed_list"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.urls: list[str] = list(config.get("urls") or [])
        self.priority = int(config.get("priority", 0))

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for url in self.urls:
            yield DiscoveredUrl(url=url, strategy_id=self.strategy_id, kind="material", depth=0)

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        return
        yield  # pragma: no cover - makes this an async generator

    def snapshot(self) -> Mapping[str, Any]:
        return {}

    def restore(self, state: Mapping[str, Any]) -> None:
        return None


class RecursiveStrategy:
    """Follows links from every fetched HTML page (from any strategy, or from its own ``seeds``).

    ``link_sources`` chooses which links count (``a_href`` by default); ``follow`` additionally narrows
    them to matching URLs. Scope, exclusions, robots, dedup, depth and frontier size are the core's job.
    """

    type_name: ClassVar[str] = "recursive"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.seed_urls: list[str] = list(config.get("seeds") or [])
        self.follow = compile_patterns(config.get("follow"))
        self.link_sources: tuple[str, ...] = tuple(config.get("link_sources") or ("a_href",))

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for url in self.seed_urls:
            yield DiscoveredUrl(url=url, strategy_id=self.strategy_id, kind="material", depth=0)

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        if not is_html(resource.media_type) or not 200 <= resource.status < 300:
            return
        extract = getattr(ctx, "extract_links_from", None)
        links = (
            extract(resource, sources=self.link_sources) if callable(extract) else ctx.extract_links(resource)
        )
        for link in links:
            if self.follow and not patterns_match(self.follow, link):
                continue
            yield DiscoveredUrl(
                url=link,
                strategy_id=self.strategy_id,
                kind="material",
                depth=resource.depth + 1,
                parent_url=resource.final_url,
            )

    def snapshot(self) -> Mapping[str, Any]:
        return {}

    def restore(self, state: Mapping[str, Any]) -> None:
        return None
