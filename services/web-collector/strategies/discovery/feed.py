"""``feed`` strategy: RSS 2.0, RSS 1.0 (RDF) and Atom feeds (``collector-rules.schema.json#/$defs/FeedStrategy``).

* ``urls`` are fetched as navigation documents; every entry link becomes a material candidate (``lastmod`` from
  ``atom:updated`` / ``dc:date`` / ``pubDate`` for RSS, ``updated`` / ``published`` for Atom).
* ``autodiscover`` (default ``true``): ``<link rel="alternate" type="application/rss+xml|atom+xml|rdf+xml">``
  is looked up on seed pages — an HTML page among ``urls`` and every HTML page with depth 0 fetched by other
  strategies (for example ``seed_list``); the feeds found there are read in the same step.

Feeds are re-read on every run (navigation documents are fetched with ``conditional=False``); entries go
through scope, robots, dedup and revisit rules of the core.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar
from urllib.parse import urljoin

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource, LinkSelector

from ._common import (
    BudgetExhausted,
    UnsafeDocument,
    bump,
    children,
    fetch_document,
    is_html,
    is_success,
    limit,
    localname,
    maybe_gunzip,
    parse_datetime,
    parse_xml,
    safe_normalize,
    text_of,
)

__all__ = ["FEED_AUTODISCOVERY_XPATH", "FeedEntry", "FeedStrategy", "parse_feed", "parse_feed_bytes"]

_LOWER = "translate({}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
_TYPE = _LOWER.format("normalize-space(@type)")
FEED_AUTODISCOVERY_XPATH = (
    "//link[@href]"
    f"[contains(concat(' ', {_LOWER.format('normalize-space(@rel)')}, ' '), ' alternate ')]"
    f"[starts-with({_TYPE}, 'application/rss+xml') or starts-with({_TYPE}, 'application/atom+xml')"
    f" or starts-with({_TYPE}, 'application/rdf+xml')]/@href"
)
"""``<link rel="alternate">`` elements of RSS/Atom/RDF type (case-insensitive); yields their ``href``."""


@dataclass(frozen=True, slots=True)
class FeedEntry:
    link: str
    lastmod: datetime | None


def _rss_link(item: Any) -> str | None:
    link = text_of(item, ["link"])
    if link:
        return link
    for guid in children(item, "guid"):
        if (guid.get("isPermaLink") or "true").strip().lower() != "false" and guid.text and guid.text.strip():
            return str(guid.text.strip())
    about = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
    return str(about) if about else None


def _atom_link(entry: Any, base: str) -> str | None:
    fallback: str | None = None
    for link in children(entry, "link"):
        href = link.get("href")
        if not href:
            continue
        rel = (link.get("rel") or "alternate").strip().lower()
        resolved = str(urljoin(link.base or base, href.strip()))
        if rel == "alternate":
            return resolved
        fallback = fallback or (resolved if rel in {"related", "via"} else None)
    return fallback


def parse_feed(root: Any, base: str, max_entries: int) -> tuple[list[FeedEntry], int]:
    """Entries of an RSS/RDF/Atom document (already parsed); returns ``(entries, dropped_over_limit)``."""
    name = localname(root)
    entries: list[FeedEntry] = []
    dropped = 0
    if name == "feed":
        items = [
            (e, _atom_link(e, base), text_of(e, ["updated", "published"])) for e in children(root, "entry")
        ]
    elif name in {"rss", "RDF"}:
        channel = next(children(root, "channel"), None)
        containers = [root] if channel is None else [channel, root]
        items = [
            (i, _rss_link(i), text_of(i, ["updated", "modified", "date", "pubDate"]))
            for container in containers
            for i in children(container, "item")
        ]
    else:
        return [], 0
    for _, link, stamp in items:
        if not link:
            continue
        if len(entries) >= max_entries:
            dropped += 1
            continue
        entries.append(FeedEntry(urljoin(base, link), parse_datetime(stamp)))
    return entries, dropped


def parse_feed_bytes(
    body: bytes, base: str, *, max_bytes: int, max_entries: int
) -> tuple[list[FeedEntry], int]:
    """Decode (gzip up to ``max_bytes``) and parse a feed; ``([], 0)`` if the body is not a feed."""
    decoded = maybe_gunzip(body, max_bytes)
    root = parse_xml(decoded.data, base_url=base)
    if root is None:
        return [], 0
    return parse_feed(root, base, max_entries)


class FeedStrategy:
    """RSS/Atom feeds (``urls``) plus feed autodiscovery on seed pages."""

    type_name: ClassVar[str] = "feed"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.urls: list[str] = [u for u in config.get("urls") or [] if isinstance(u, str)]
        self.autodiscover = bool(config.get("autodiscover", True))
        self.stats: dict[str, int] = {}
        self._seen: set[str] = set()  # feeds (and HTML seed pages) handled by this process

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        self.stats = {}  # seeds are re-run from scratch after a restart
        try:
            for url in self.urls:
                if ctx.is_cancelled():
                    return
                async for cand in self._read(ctx, url, level=0, html_allowed=self.autodiscover):
                    yield cand
        except BudgetExhausted as exc:
            ctx.log.warning("feed strategy stopped: budget exhausted", extra={"reason": str(exc)})

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        """Autodiscovery on seed pages found by other strategies (HTML, depth 0)."""
        if (
            not self.autodiscover
            or resource.depth != 0
            or not is_success(resource)
            or not is_html(resource.media_type)
        ):
            return
        try:
            for feed_url in self._discover(ctx, resource):
                async for cand in self._read(ctx, feed_url, level=1, html_allowed=False):
                    yield cand
        except BudgetExhausted as exc:
            ctx.log.warning("feed autodiscovery stopped: budget exhausted", extra={"reason": str(exc)})

    def _discover(self, ctx: DiscoveryContext, page: FetchedResource) -> list[str]:
        found = ctx.extract_links(page, LinkSelector(value=FEED_AUTODISCOVERY_XPATH, type="xpath"))
        fresh = [u for u in found if u not in self._seen]
        if fresh:
            bump(self.stats, "feeds_discovered", len(fresh))
            ctx.log.info("feeds discovered", extra={"page": page.final_url, "feeds": fresh})
        return fresh

    async def _read(
        self, ctx: DiscoveryContext, url: str, *, level: int, html_allowed: bool
    ) -> AsyncIterator[DiscoveredUrl]:
        normalized = safe_normalize(ctx, url)
        if normalized is None or normalized in self._seen:
            return
        self._seen.add(normalized)
        resource = await fetch_document(ctx, normalized)
        if resource is None or not is_success(resource):
            return
        if is_html(resource.media_type):
            if html_allowed:
                for feed_url in self._discover(ctx, resource):
                    async for cand in self._read(ctx, feed_url, level=level + 1, html_allowed=False):
                        yield cand
            return
        max_entries = limit(ctx, "crawl.max_links_per_page")
        try:
            entries, dropped = parse_feed_bytes(
                resource.body,
                resource.final_url,
                max_bytes=limit(ctx, "crawl.max_material_bytes"),
                max_entries=max_entries,
            )
        except UnsafeDocument as exc:
            bump(self.stats, "documents_refused")
            ctx.log.warning("feed refused", extra={"url": resource.final_url, "reason": str(exc)})
            return
        bump(self.stats, "feeds_read")
        if dropped:
            bump(self.stats, "entries_over_limit", dropped)
            ctx.log.warning(
                "feed entries over crawl.max_links_per_page dropped",
                extra={"url": resource.final_url, "dropped": dropped, "limit": max_entries},
            )
        if not entries:
            ctx.log.info(
                "no feed entries", extra={"url": resource.final_url, "media_type": resource.media_type}
            )
        for entry in entries:
            bump(self.stats, "entries")
            yield DiscoveredUrl(
                url=entry.link,
                strategy_id=self.strategy_id,
                kind="material",
                depth=level + 1,
                parent_url=resource.final_url,
                lastmod=entry.lastmod,
            )

    def snapshot(self) -> Mapping[str, Any]:
        return {"stats": dict(self.stats)} if self.stats else {}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.stats = dict(state.get("stats") or {})
