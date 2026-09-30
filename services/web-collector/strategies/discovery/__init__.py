"""WP-03 discovery strategies of the Web Collector (``jane_contracts.discovery.DiscoveryStrategy``).

The core (WP-02) imports this directory as the package ``jane_web_collector_discovery`` and registers
:data:`STRATEGIES`. Strategies only propose candidate URLs; every request goes through ``ctx.fetch`` of the
core (scope, robots.txt, per-host limits, redirects, sizes, time-outs, budgets). See README.md.
"""

from __future__ import annotations

from jane_contracts.discovery import DiscoveryStrategy

from .api_feed import ApiFeedStrategy
from .feed import FeedStrategy
from .listing import ListingStrategy
from .sitemap import SitemapStrategy
from .url_template import UrlTemplateStrategy

__all__ = [
    "STRATEGIES",
    "ApiFeedStrategy",
    "FeedStrategy",
    "ListingStrategy",
    "SitemapStrategy",
    "UrlTemplateStrategy",
]

STRATEGIES: list[type[DiscoveryStrategy]] = [
    SitemapStrategy,
    FeedStrategy,
    ListingStrategy,
    UrlTemplateStrategy,
    ApiFeedStrategy,
]
