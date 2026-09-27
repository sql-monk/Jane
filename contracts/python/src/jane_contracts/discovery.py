"""Material discovery strategy contract for the Web Collector.

Owners: WP-02 implements the core (fetcher, scope, robots, normalization, frontier with dedup and
priorities, depth, revisit, per-host limits, state persistence) and the strategy registry plus the
``seed_list`` and ``recursive`` strategies. WP-03 implements ``sitemap``, ``feed``, ``listing``,
``url_template`` and ``api_feed`` against this protocol.

``llm_explore`` is NOT implemented by the collector in v1: the strategy registry reports it as unsupported
(``POST /v1/rules/validations`` answers ``supported: false``; a collection with it fails validation).
LLM-driven source exploration is done by the assistant's onboarding (WP-11, ``assistant.v1``), which
turns its findings into ordinary strategies (seed_list, sitemap, listing, …) in the proposed rules.

Division of responsibility (see contracts/docs/discovery-strategy.md):

* A strategy only *proposes* candidate URLs (:class:`DiscoveredUrl`). It never performs HTTP itself:
  all network access goes through :meth:`DiscoveryContext.fetch`, which applies scope, exclusions,
  robots.txt, rate limits, redirects, size limits and conditional requests.
* The core normalizes, checks scope and exclusions, deduplicates, enforces ``limits.crawl.max_depth``
  and ``max_frontier_size``, orders by priority and decides what is emitted as a Material.
* Strategies are configured with the validated strategy object from CollectorRules
  (``contracts/schemas/collector-rules.schema.json#/$defs/Strategy``); ``type_name`` equals its ``type``.
* Strategy state must be JSON-serialisable (:meth:`DiscoveryStrategy.snapshot`) so a killed
  collection resumes without re-emitting everything.

Registration: WP-03 exposes ``STRATEGIES: list[type[DiscoveryStrategy]]`` in its package
``strategies/discovery/__init__.py``; the WP-02 registry imports that list at start-up.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Literal, Protocol, runtime_checkable

UrlKind = Literal["material", "navigation"]
"""``material`` — candidate content page (emitted as Material if fetched successfully);
``navigation`` — fetched only to discover more URLs (sitemap, feed, listing page, API page)."""


@dataclass(frozen=True, slots=True)
class DiscoveredUrl:
    """A candidate URL proposed by a strategy. The core may drop it (scope, robots, dedup, depth)."""

    url: str
    strategy_id: str
    kind: UrlKind = "material"
    priority: int = 0
    depth: int = 0
    parent_url: str | None = None
    section: str | None = None
    lastmod: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FetchedResource:
    """A response obtained through :meth:`DiscoveryContext.fetch` (already within limits)."""

    url: str
    final_url: str
    status: int
    media_type: str
    headers: Mapping[str, str]
    body: bytes
    fetched_at: datetime
    depth: int
    strategy_id: str | None
    kind: UrlKind
    truncated: bool = False


@dataclass(frozen=True, slots=True)
class LinkSelector:
    """Mirrors CollectorRules ``$defs/Selector``."""

    value: str
    type: Literal["css", "xpath", "rel"] = "css"
    attribute: str = "href"


class FetchRejected(Exception):
    """Raised by :meth:`DiscoveryContext.fetch` when policy forbids the request.

    ``code`` is a Problem code: ``out_of_scope``, ``access_denied_by_policy``, ``limit_exceeded``
    or ``rate_limited`` (the latter only when the wait would exceed configured limits).
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class DiscoveryContext(Protocol):
    """Services the Web Collector core provides to a running strategy."""

    source_id: str | None
    collection_id: str
    rules: Mapping[str, Any]
    """The full validated WebRules document."""
    limits: Mapping[str, Any]
    """Effective Limits (read-only); strategy-level ``limits`` are already merged in."""
    log: logging.Logger

    async def fetch(self, url: str, *, kind: UrlKind = "navigation", conditional: bool = True) -> FetchedResource | None:
        """Fetch through the core. Returns ``None`` if not modified (conditional request) or
        filtered as a duplicate. Raises :class:`FetchRejected` on policy violations."""
        ...

    def normalize(self, url: str, base: str | None = None) -> str:
        """Resolve relative URLs and apply CollectorRules ``normalization``."""
        ...

    def in_scope(self, url: str) -> bool: ...

    def section_for(self, url: str) -> str | None: ...

    def extract_links(self, resource: FetchedResource, selector: LinkSelector | None = None) -> list[str]:
        """Links from an HTML resource (``a[href]`` by default), normalized and absolute."""
        ...

    def is_cancelled(self) -> bool: ...


@runtime_checkable
class DiscoveryStrategy(Protocol):
    """One material discovery mode. Instances live for one collection run."""

    type_name: ClassVar[str]
    """Equals the strategy ``type`` in CollectorRules, e.g. ``"sitemap"``."""

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        """``config`` is the validated strategy object; ``strategy_id`` is its id or a generated one."""
        ...

    def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        """Initial candidates. May fetch navigation documents (sitemaps, feeds, API pages)."""
        ...

    def on_fetched(self, resource: FetchedResource, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        """Called by the core for every successfully fetched resource (from any strategy), so
        strategies combine: e.g. ``recursive`` follows links from pages found by ``sitemap``.
        Strategies that do not react to other pages yield nothing."""
        ...

    def snapshot(self) -> Mapping[str, Any]:
        """JSON-serialisable progress state (cursor, page number, processed sitemap files)."""
        ...

    def restore(self, state: Mapping[str, Any]) -> None:
        """Restore state saved by :meth:`snapshot` after a restart."""
        ...


class StrategyRegistry(Protocol):
    """Registry owned by WP-02."""

    def register(self, strategy: type[DiscoveryStrategy]) -> None: ...

    def get(self, type_name: str) -> type[DiscoveryStrategy]:
        """Raises ``KeyError`` for unknown types (collector answers ``supported: false``)."""
        ...

    def types(self) -> Sequence[str]: ...
