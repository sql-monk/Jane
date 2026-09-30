"""``listing`` strategy: category, pagination and search pages (``#/$defs/ListingStrategy``).

Every listing page (``start_urls``, pages of ``search.url_template`` for each of ``search.queries``, and the
next pages found from them) is proposed as a material candidate and processed in ``on_fetched`` when the core
has fetched it — by this or any other strategy, so ``listing`` also reacts to category pages found by
``recursive``. From each listing page:

* ``item_links`` (Selector) — links to materials; without it every ``a[href]`` of the page except pagination
  links and the page itself;
* the next page — ``page_param`` (``name``, ``start``, ``step``, ``stop_when_empty``) if set, otherwise
  ``next_page`` (Selector, default ``rel=next``).

Listing pages are proposed as ``material``: they are HTML pages of the site (categories, search results) and
the testsite's expected ``categories``/``search:*`` sets include them. As ``navigation`` they would also
suppress the same pages as materials when combined with ``recursive`` (the core keeps one kind per URL).

Pagination depth: page N is N-1 steps from its start page (the core gives candidates from ``on_fetched`` depth
``page depth + 1``); a next page is proposed only while its items still fit into ``crawl.max_depth`` of the
strategy. A chain also stops on a non-2xx page, with ``stop_when_empty`` on a page without items, and when a
page repeats the items of the previous one (a site that ignores the page parameter).

State (``snapshot``): the listing pages known to the strategy, saved by the core in the same transaction as
the candidates, so a killed collection resumes without losing a pagination chain.
"""

from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator, Mapping
from typing import Any, ClassVar
from urllib.parse import quote

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource, LinkSelector

from ._common import bump, is_html, is_success, limit, query_param, safe_normalize, set_query_param

__all__ = ["ListingStrategy"]

_PAGINATION_XPATH = (
    "//*[self::a or self::link][@href][contains(concat(' ', translate(normalize-space(@rel), "
    "'NEXTPRVIOU', 'nextprviou'), ' '), ' next ') or contains(concat(' ', translate(normalize-space(@rel), "
    "'NEXTPRVIOU', 'nextprviou'), ' '), ' prev ') or contains(concat(' ', translate(normalize-space(@rel), "
    "'NEXTPRVIOU', 'nextprviou'), ' '), ' previous ')]/@href"
)


def _selector(config: Mapping[str, Any] | None, default: LinkSelector | None = None) -> LinkSelector | None:
    if not config:
        return default
    return LinkSelector(
        value=str(config["value"]),
        type=config.get("type", "css"),
        attribute=str(config.get("attribute", "href")),
    )


def _digest(urls: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(urls)).encode()).hexdigest()[:32]


class ListingStrategy:
    type_name: ClassVar[str] = "listing"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.start_urls: list[str] = [u for u in config.get("start_urls") or [] if isinstance(u, str)]
        search: Mapping[str, Any] = config.get("search") or {}
        if search:
            template = str(search["url_template"])
            self.start_urls += [
                template.replace("{query}", quote(str(q), safe="")) for q in search["queries"]
            ]
        self.item_links = _selector(config.get("item_links"))
        self.next_link = _selector(config.get("next_page"), LinkSelector(value="next", type="rel"))
        page_param: Mapping[str, Any] = config.get("page_param") or {}
        self.page_param: str | None = str(page_param["name"]) if page_param else None
        self.page_start = int(page_param.get("start", 1))
        self.page_step = int(page_param.get("step", 1))
        self.stop_when_empty = bool(page_param.get("stop_when_empty", True))
        if self.page_param and self.page_step == 0:
            raise ValueError("listing: page_param.step must not be 0")
        self.pages: dict[str, dict[str, Any]] = {}
        """Normalized listing page URL -> {"n": page number, "prev": previous page URL, "digest": items digest}."""
        self.stats: dict[str, int] = {}

    # ------------------------------------------------------------------ seeds
    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        for url in self.start_urls:
            normalized = safe_normalize(ctx, url)
            if normalized is None:
                ctx.log.warning("listing: start URL is not an HTTP(S) URL", extra={"url": url})
                continue
            self.pages.setdefault(normalized, {"n": self._page_number(normalized), "prev": None})
            yield DiscoveredUrl(url=normalized, strategy_id=self.strategy_id, kind="material", depth=0)

    def _page_number(self, url: str) -> int:
        if not self.page_param:
            return 1
        value = query_param(url, self.page_param)
        try:
            return int(value) if value is not None else self.page_start
        except ValueError:
            return self.page_start

    # ------------------------------------------------------------------ listing pages
    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        page = self.pages.get(resource.url)
        if page is None:
            return
        if not is_success(resource) or not is_html(resource.media_type):
            bump(self.stats, "chains_ended_by_status")
            return
        bump(self.stats, "pages")
        items = self._items(ctx, resource)
        page["digest"] = _digest(items)
        previous = self.pages.get(page["prev"]) if page.get("prev") else None
        if previous is not None and previous.get("digest") == page["digest"] and items:
            bump(self.stats, "chains_ended_by_repeat")
            ctx.log.info("listing: page repeats the previous one, chain stops", extra={"url": resource.url})
            return
        for item in items:
            bump(self.stats, "items")
            yield DiscoveredUrl(
                url=item,
                strategy_id=self.strategy_id,
                kind="material",
                depth=resource.depth + 1,
                parent_url=resource.final_url,
            )
        following = self._next(ctx, resource, page, items)
        if following is None:
            return
        max_depth = limit(ctx, "crawl.max_depth")
        if resource.depth + 2 > max_depth:  # the next page's items (depth + 2) could not be admitted
            bump(self.stats, "chains_ended_by_depth")
            ctx.log.warning(
                "listing pagination stopped by crawl.max_depth",
                extra={"page": resource.url, "next": following, "max_depth": max_depth},
            )
            return
        if following not in self.pages:
            self.pages[following] = {"n": page["n"] + self.page_step, "prev": resource.url}
        yield DiscoveredUrl(
            url=following,
            strategy_id=self.strategy_id,
            kind="material",
            depth=resource.depth + 1,
            parent_url=resource.final_url,
        )

    def _items(self, ctx: DiscoveryContext, resource: FetchedResource) -> list[str]:
        own = {resource.url, safe_normalize(ctx, resource.final_url)}
        if self.item_links is not None:
            found = ctx.extract_links(resource, self.item_links)
        else:
            pagination = set(ctx.extract_links(resource, LinkSelector(value=_PAGINATION_XPATH, type="xpath")))
            found = [u for u in ctx.extract_links(resource) if u not in pagination]
        return [u for u in dict.fromkeys(found) if u not in own and u not in self.pages]

    def _next(
        self, ctx: DiscoveryContext, resource: FetchedResource, page: Mapping[str, Any], items: list[str]
    ) -> str | None:
        if self.page_param:
            if self.stop_when_empty and not items:
                bump(self.stats, "chains_ended_by_empty_page")
                return None
            target = set_query_param(resource.url, self.page_param, str(page["n"] + self.page_step))
            return safe_normalize(ctx, target)
        own = {resource.url, safe_normalize(ctx, resource.final_url)}
        for link in ctx.extract_links(resource, self.next_link):
            if link not in own:
                return link
        return None

    def snapshot(self) -> Mapping[str, Any]:
        if not self.pages and not self.stats:
            return {}
        return {"pages": {url: dict(info) for url, info in self.pages.items()}, "stats": dict(self.stats)}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.pages = {str(url): dict(info) for url, info in (state.get("pages") or {}).items()}
        self.stats = dict(state.get("stats") or {})
