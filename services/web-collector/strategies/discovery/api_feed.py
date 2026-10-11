"""``api_feed`` strategy: material URLs from a documented JSON API or JSON channel (``#/$defs/ApiFeedStrategy``).

``items_path`` selects the items of a page, ``url_path`` the material URL inside an item (relative URLs are
resolved against the page URL), ``lastmod_path`` an optional change time (ISO 8601 / RFC 822 / Unix time).

Pagination (``pagination.type``):

* ``none`` — only ``url``;
* ``next_url`` — ``next_url_path`` in the page gives the next page URL (absolute or relative);
* ``cursor`` — ``cursor_path`` gives a token, the next page is ``url`` with ``cursor_param=<token>``;
* ``page`` — ``page_param`` is incremented from its value in ``url`` (1 if absent) while pages have items.
  With POST, optional ``body_page_path`` also writes that page number to an existing JSON object field
  (for example ``$.variables.page``). Each request receives a separate copy of the body. If the URL has
  no page number, the positive integer at that body path supplies the first page number.

Pagination stops without a next page, on a repeated page URL or cursor, on a page with no new item URLs, on a
non-2xx or non-JSON page, and at the pagination depth: page N counts as N-1 steps from the first page, its
items as N, so pages are followed while their items fit into ``crawl.max_depth`` of the strategy. API pages are
navigation documents read in ``seeds()`` through ``ctx.fetch`` (re-read after a restart; the core dedups).

R22 (``DiscoveryContext`` 1.1):

* ``method: POST`` - every API page is requested with POST and ``body`` as JSON (``Content-Type:
  application/json``); pagination parameters (``cursor_param``, ``page_param``) stay query parameters of the
  URL, ``next_url`` gives the next URL. The body is unchanged unless ``body_page_path`` or ``partitions``
  explicitly select fields to update in a separate request copy. The query must be read-only:
  the core retries it like a GET;
* ``emit_items_as_materials: true`` - every item becomes a Material itself (``application/json``, the item
  serialized as JSON) through ``ctx.emit_material``: ``material_id`` from the item's ``url_path`` URL (the same
  object as the page at that URL), ``edited_at`` from ``lastmod_path``, ``discovery.parent_url`` - the API page.
  The item URLs are not fetched; the core claims them in the collection, so no other strategy fetches the same
  URL in that collection. Without the option the items' URLs are proposed to the core as before.
"""

from __future__ import annotations

import json
import re
from collections import deque
from collections.abc import AsyncIterator, Mapping
from copy import deepcopy
from typing import Any, ClassVar

from jane_contracts.discovery import DiscoveredMaterial, DiscoveredUrl, DiscoveryContext, FetchedResource

from ._common import (
    BudgetExhausted,
    bump,
    fetch_document,
    is_success,
    limit,
    parse_datetime,
    query_param,
    safe_normalize,
    set_query_param,
)
from .jsonpath import JsonPath

__all__ = ["ApiFeedStrategy", "UnsupportedConfig"]


class UnsupportedConfig(ValueError):
    """Valid by the schema, but not executable by this collector."""


def _as_page_number(value: str | None, default: int = 1) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def _body_keys(body: Any, path: str) -> tuple[list[str], Any]:
    if not re.fullmatch(r"\$\.[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", path):
        raise ValueError("body path must be a JSON object path, such as $.variables.page")
    keys = path[2:].split(".")
    value = body
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise ValueError("body path must reference an existing field in body")
        value = value[key]
    return keys, value


def _write_body(body: Any, keys: list[str], value: Any) -> None:
    target = body
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value


class ApiFeedStrategy:
    type_name: ClassVar[str] = "api_feed"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.method = str(config.get("method", "GET")).upper()
        if self.method not in {"GET", "POST"}:
            raise UnsupportedConfig(f"api_feed: method {self.method} is not supported (GET or POST)")
        self.body: Any = config.get("body")
        self.emit_items = bool(config.get("emit_items_as_materials", False))
        self.url: str = str(config["url"])
        self.item_url_base: str | None = str(config["item_url_base"]) if config.get("item_url_base") else None
        self.items_path = JsonPath(str(config["items_path"]))
        self.url_path = JsonPath(str(config["url_path"]))
        self.lastmod_path = JsonPath(str(config["lastmod_path"])) if config.get("lastmod_path") else None
        pagination: Mapping[str, Any] = config.get("pagination") or {}
        self.pagination = str(pagination.get("type", "none"))
        required = {
            "next_url": ("next_url_path",),
            "cursor": ("cursor_path", "cursor_param"),
            "page": ("page_param",),
        }
        missing = [name for name in required.get(self.pagination, ()) if not pagination.get(name)]
        if missing:
            raise ValueError(f"api_feed: pagination type {self.pagination!r} needs {', '.join(missing)}")
        self.next_url_path = JsonPath(pagination["next_url_path"]) if self.pagination == "next_url" else None
        self.cursor_path = JsonPath(pagination["cursor_path"]) if self.pagination == "cursor" else None
        self.cursor_param: str = str(pagination.get("cursor_param") or "")
        self.page_param: str = str(pagination.get("page_param") or "")
        self.body_page_path: str = str(pagination.get("body_page_path") or "")
        self._body_page_keys: list[str] = []
        if self.body_page_path:
            if self.method != "POST" or self.pagination != "page":
                raise UnsupportedConfig("body_page_path requires POST and page pagination")
            self._body_page_keys, value = _body_keys(self.body, self.body_page_path)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError("body page number must be a positive integer")
            initial_url_page = query_param(self.url, self.page_param)
            if initial_url_page is None:
                self.url = set_query_param(self.url, self.page_param, str(value))
            elif not initial_url_page.isdigit() or int(initial_url_page) < 1:
                raise ValueError("URL page number must be a positive integer")
        partitions = config.get("partitions") or {}
        self.partition_path = JsonPath(partitions["items_path"]) if partitions else None
        self.partition_param = str(partitions.get("url_param") or "")
        self._partition_body_keys: list[str] = []
        self._partition_root: Any = None
        if partitions:
            if self.method != "POST" or not self.partition_param:
                raise UnsupportedConfig("partitions require POST and a nonempty url_param")
            if self.partition_param in {self.page_param, self.cursor_param}:
                raise ValueError("partition url_param must differ from pagination parameters")
            self._partition_body_keys, self._partition_root = _body_keys(self.body, partitions["body_path"])
            if isinstance(self._partition_root, bool) or not isinstance(self._partition_root, str | int):
                raise ValueError("partition root must be a string or integer")
            if self._partition_body_keys == self._body_page_keys:
                raise ValueError("partition and page body paths must differ")
        self._active_partition: Any = self._partition_root
        self._partition_children: list[Any] = []
        self.stats: dict[str, int] = {}

    def page_body(self, url: str) -> Any:
        """A fresh request body; configuration and prior requests are never mutated."""
        if not self._body_page_keys and not self._partition_body_keys:
            return self.body
        body = deepcopy(self.body)
        if self._body_page_keys:
            _write_body(body, self._body_page_keys, _as_page_number(query_param(url, self.page_param)))
        if self._partition_body_keys:
            _write_body(body, self._partition_body_keys, self._active_partition)
        return body

    def items(self, document: Any) -> list[Any]:
        found = self.items_path.find(document)
        if len(found) == 1 and isinstance(found[0], list):
            return list(found[0])
        return found

    def next_page(self, document: Any, current: str, item_count: int, cursors: set[str]) -> str | None:
        """URL of the next page by the configured pagination, or ``None`` to stop."""
        if self.pagination == "next_url" and self.next_url_path is not None:
            target = self.next_url_path.first(document)
            return target if isinstance(target, str) and target.strip() else None
        if self.pagination == "cursor" and self.cursor_path is not None:
            cursor = self.cursor_path.first(document)
            if cursor is None or isinstance(cursor, bool | dict | list) or str(cursor) == "":
                return None
            token = str(cursor)
            if token in cursors:
                return None
            cursors.add(token)
            return set_query_param(self.url, self.cursor_param, token)
        if self.pagination == "page" and item_count:
            page = _as_page_number(query_param(current, self.page_param))
            return set_query_param(current, self.page_param, str(page + 1))
        return None

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        self.stats = {}  # seeds are re-run from scratch after a restart
        try:
            if self.partition_path is None:
                async for cand in self._pages(ctx):
                    yield cand
            else:
                pending = deque([(self._partition_root, 0)])
                known = {str(self._partition_root)}
                max_partitions = limit(ctx, "crawl.max_frontier_size")
                while pending:
                    value, depth = pending.popleft()
                    if ctx.is_cancelled():
                        return
                    if depth >= limit(ctx, "crawl.max_depth"):
                        bump(self.stats, "partitions_over_depth")
                        continue
                    self._active_partition = value
                    self._partition_children = []
                    async for cand in self._pages(ctx):
                        yield cand
                    bump(self.stats, "partitions")
                    for child in self._partition_children:
                        if isinstance(child, bool) or not isinstance(child, str | int) or str(child) in known:
                            continue
                        if len(known) >= max_partitions:
                            bump(self.stats, "partitions_over_limit")
                            continue
                        known.add(str(child))
                        pending.append((child, depth + 1))
        except BudgetExhausted as exc:
            ctx.log.warning("api_feed stopped: budget exhausted", extra={"reason": str(exc)})

    async def _pages(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        max_depth = limit(ctx, "crawl.max_depth")
        max_items = limit(ctx, "crawl.max_links_per_page")
        max_bytes = limit(ctx, "crawl.max_material_bytes")
        url: str | None = self.url
        if self.partition_path is not None:
            url = set_query_param(url, self.partition_param, str(self._active_partition))
        step = 0  # pagination steps from the first page; items of this page get depth step + 1
        pages_seen: set[str] = set()
        items_seen: set[str] = set()
        cursors: set[str] = set()
        while url is not None:
            if self.partition_path is not None:
                url = set_query_param(url, self.partition_param, str(self._active_partition))
            if ctx.is_cancelled():
                return
            if step + 1 > max_depth:
                bump(self.stats, "stopped_by_depth")
                ctx.log.warning(
                    "api_feed pagination stopped by crawl.max_depth",
                    extra={"next": url, "max_depth": max_depth},
                )
                return
            normalized = safe_normalize(ctx, url)
            if normalized is None or normalized in pages_seen:
                return
            pages_seen.add(normalized)
            resource = await fetch_document(
                ctx, normalized, method=self.method, body=self.page_body(normalized)
            )
            if resource is None or not is_success(resource):
                return
            document = self._json(ctx, resource, max_bytes)
            if document is None:
                return
            bump(self.stats, "pages")
            if self.partition_path is not None:
                self._partition_children.extend(self.partition_path.find(document))
            items = self.items(document)
            if len(items) > max_items:
                bump(self.stats, "items_over_limit", len(items) - max_items)
                ctx.log.warning(
                    "api_feed items over crawl.max_links_per_page dropped",
                    extra={"url": resource.final_url, "dropped": len(items) - max_items, "limit": max_items},
                )
            new = 0
            for item in items[:max_items]:
                link = self.url_path.first(item)
                target = (
                    safe_normalize(ctx, link, self.item_url_base or resource.final_url)
                    if isinstance(link, str)
                    else None
                )
                if target is None:
                    bump(self.stats, "items_without_url")
                    continue
                if target in items_seen:
                    continue
                items_seen.add(target)
                new += 1
                bump(self.stats, "items")
                lastmod = parse_datetime(self.lastmod_path.first(item)) if self.lastmod_path else None
                if self.emit_items:
                    emitted = await ctx.emit_material(
                        DiscoveredMaterial(
                            url=target,
                            strategy_id=self.strategy_id,
                            body=json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
                            fetched_at=resource.fetched_at,
                            depth=step + 1,
                            parent_url=resource.final_url,
                            lastmod=lastmod,
                        )
                    )
                    bump(self.stats, "items_emitted" if emitted else "items_not_emitted")
                    continue
                yield DiscoveredUrl(
                    url=target,
                    strategy_id=self.strategy_id,
                    kind="material",
                    depth=step + 1,
                    parent_url=resource.final_url,
                    lastmod=lastmod,
                )
            if step > 0 and new == 0:
                ctx.log.info(
                    "api_feed: page without new items, pagination stops", extra={"url": resource.final_url}
                )
                return
            following = self.next_page(document, resource.final_url, len(items), cursors)
            url = safe_normalize(ctx, following, resource.final_url) if following else None
            step += 1

    def _json(self, ctx: DiscoveryContext, resource: FetchedResource, max_bytes: int) -> Any | None:
        if resource.truncated:
            bump(self.stats, "truncated_pages")
            ctx.log.warning(
                "api_feed page cut at crawl.max_material_bytes, pagination stops",
                extra={"url": resource.final_url, "limit": max_bytes},
            )
            return None
        try:
            return json.loads(resource.body)
        except (ValueError, RecursionError) as exc:
            bump(self.stats, "invalid_pages")
            ctx.log.warning(
                "api_feed page is not JSON, pagination stops",
                extra={"url": resource.final_url, "media_type": resource.media_type, "error": str(exc)[:200]},
            )
            return None

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        return
        yield  # pragma: no cover - makes this an async generator

    def snapshot(self) -> Mapping[str, Any]:
        return {"stats": dict(self.stats)} if self.stats else {}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.stats = dict(state.get("stats") or {})
