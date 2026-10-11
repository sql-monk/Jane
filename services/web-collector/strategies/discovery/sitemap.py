"""``sitemap`` strategy: Sitemap and Sitemap Index, plain and ``.gz`` (``#/$defs/SitemapStrategy``).

* ``urls`` — sitemap or index URLs. Without ``urls``: ``Sitemap:`` lines of ``/robots.txt`` of every origin of
  the rules (``use_robots_txt``, default ``true``); if robots.txt lists none (or ``use_robots_txt=false``) —
  ``/sitemap.xml``. Origins are taken from explicit URLs of the strategies in the rules, otherwise from
  ``scope.allowed_domains`` with the first allowed scheme.
* Formats: ``<urlset>``, ``<sitemapindex>`` (nested indexes are followed), gzip (by magic bytes, e.g.
  ``application/gzip``), plain-text sitemaps (one URL per line) and RSS/Atom used as a sitemap.
* ``lastmod_since`` skips URL entries with an older ``lastmod`` (entries without ``lastmod`` are kept);
  ``use_lastmod_for_revisit`` passes ``lastmod`` to the core with the candidate.

Depth: a sitemap listed directly has level 0, a sitemap from an index at level L has level L+1; its URLs get
depth ``level + 1``. Index nesting stops where the URLs would exceed ``crawl.max_depth`` of the strategy.
Sitemap files are read in ``seeds()`` (re-read from scratch after a restart; the core dedups the URLs).
"""

from __future__ import annotations

import asyncio
import functools
import os
import re
import threading
from collections import deque
from collections.abc import AsyncGenerator, AsyncIterator, Mapping
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import AsyncExitStack, aclosing, asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar
from urllib.parse import urljoin

from jane_contracts.discovery import DiscoveredUrl, DiscoveryContext, FetchedResource

from ._common import (
    BudgetExhausted,
    UnsafeDocument,
    bump,
    children,
    fetch_document,
    is_success,
    limit,
    localname,
    maybe_gunzip,
    parse_datetime,
    parse_xml,
    rule_origins,
    safe_normalize,
    text_of,
)
from .feed import parse_feed

__all__ = ["SitemapDocument", "SitemapEntry", "SitemapStrategy", "parse_robots_sitemaps", "parse_sitemap"]

_ROBOTS_SITEMAP = re.compile(r"^\s*sitemap\s*:\s*(\S+)", re.IGNORECASE | re.MULTILINE)


@dataclass
class _ParseWaiter:
    loop: asyncio.AbstractEventLoop
    ready: asyncio.Future[None]
    granted: bool = False
    cancelled: bool = False


@dataclass
class _ParseLease:
    finished: bool = False
    closed: bool = False
    released: bool = False


class _ParseExecutor:
    """Bound document lifetimes across jobs and loops, retaining permits through consumption.

    Cancelling an await cannot stop a running thread. Releasing its slot then would allow cancelled
    jobs to accumulate unbounded work in the executor queue while new collections replace them.
    Holding the completed result also bounds unconsumed documents and prevents the next CPU parse
    competing for the GIL while the current consumer repeatedly enters SQLite.
    """

    def __init__(self, workers: int) -> None:
        if workers < 1:
            raise ValueError("JANE_WEB_COLLECTOR_SITEMAP_PARSE_WORKERS must be positive")
        self.workers = workers
        self._executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="sitemap-parse")
        self._available = workers
        self._lock = threading.Lock()
        self._waiters: deque[_ParseWaiter] = deque()

    @staticmethod
    def _grant(waiter: _ParseWaiter) -> None:
        if not waiter.cancelled and not waiter.ready.done():
            waiter.ready.set_result(None)

    def _release(self) -> None:
        with self._lock:
            while self._waiters:
                waiter = self._waiters.popleft()
                if waiter.cancelled or waiter.loop.is_closed():
                    continue
                waiter.granted = True
                try:
                    waiter.loop.call_soon_threadsafe(self._grant, waiter)
                except RuntimeError:  # the loop closed between the check and delivery
                    waiter.cancelled = True
                    continue
                return
            self._available += 1

    def _settle(self, lease: _ParseLease, *, finished: bool = False, closed: bool = False) -> None:
        with self._lock:
            lease.finished |= finished
            lease.closed |= closed
            release = lease.finished and lease.closed and not lease.released
            if release:
                lease.released = True
        if release:
            self._release()

    def _finished(self, future: Future[SitemapDocument], lease: _ParseLease) -> None:
        # Observe late errors; cancellation frees a slot only after its real CPU task has ended.
        if not future.cancelled():
            future.exception()
        self._settle(lease, finished=True)

    @asynccontextmanager
    async def document(
        self, body: bytes, base: str, *, max_bytes: int, max_entries: int
    ) -> AsyncIterator[SitemapDocument]:
        loop = asyncio.get_running_loop()
        waiter = _ParseWaiter(loop, loop.create_future())
        with self._lock:
            if self._available:
                self._available -= 1
                waiter.granted = True
                waiter.ready.set_result(None)
            else:
                self._waiters.append(waiter)
        lease = _ParseLease()
        try:
            await asyncio.shield(waiter.ready)
        except asyncio.CancelledError:
            with self._lock:
                waiter.cancelled = True
                if not waiter.granted:
                    self._waiters.remove(waiter)
            if waiter.granted:
                self._release()
            raise
        try:
            future = self._executor.submit(
                functools.partial(parse_sitemap, body, base, max_bytes=max_bytes, max_entries=max_entries)
            )
        except BaseException:
            self._release()
            raise
        future.add_done_callback(lambda done: self._finished(done, lease))
        try:
            wrapped = asyncio.wrap_future(future, loop=loop)
            # Consume a late parsing error after cancellation without touching strategy/context state.
            wrapped.add_done_callback(lambda done: done.exception() if not done.cancelled() else None)
            yield await asyncio.shield(wrapped)
        finally:
            self._settle(lease, closed=True)

    async def parse(self, body: bytes, base: str, *, max_bytes: int, max_entries: int) -> SitemapDocument:
        """Parse-only convenience; strategy consumption uses the longer document context."""
        async with self.document(body, base, max_bytes=max_bytes, max_entries=max_entries) as doc:
            return doc


_PARSE_EXECUTOR: _ParseExecutor | None = None
_PARSE_EXECUTOR_LOCK = threading.Lock()


def _parse_executor() -> _ParseExecutor:
    global _PARSE_EXECUTOR
    with _PARSE_EXECUTOR_LOCK:
        if _PARSE_EXECUTOR is None:
            # Private runtime setting, separate from parsing/document limits in the public contract.
            workers = int(os.environ.get("JANE_WEB_COLLECTOR_SITEMAP_PARSE_WORKERS", "1"))
            _PARSE_EXECUTOR = _ParseExecutor(workers)
        return _PARSE_EXECUTOR


@dataclass(frozen=True, slots=True)
class SitemapEntry:
    loc: str
    lastmod: datetime | None = None


@dataclass
class SitemapDocument:
    kind: str = "unknown"
    """``urlset``, ``sitemapindex``, ``text``, ``feed`` or ``unknown``."""
    urls: list[SitemapEntry] = field(default_factory=list)
    sitemaps: list[SitemapEntry] = field(default_factory=list)
    dropped: int = 0
    """Entries over ``crawl.max_links_per_page``."""
    compressed: bool = False
    truncated: bool = False
    """The body (or its decompressed form) was cut at ``crawl.max_material_bytes``."""


def parse_robots_sitemaps(text: str, base: str) -> list[str]:
    """``Sitemap:`` lines of a robots.txt (case-insensitive, anywhere in the file)."""
    out: list[str] = []
    for match in _ROBOTS_SITEMAP.finditer(text):
        url = urljoin(base, match.group(1))
        if url not in out:
            out.append(url)
    return out


def _entries(parent: Any, name: str, base: str) -> list[SitemapEntry]:
    out: list[SitemapEntry] = []
    for item in children(parent, name):
        loc = text_of(item, ["loc"])
        if loc:
            out.append(SitemapEntry(urljoin(base, loc), parse_datetime(text_of(item, ["lastmod"]))))
    return out


def parse_sitemap(body: bytes, base: str, *, max_bytes: int, max_entries: int) -> SitemapDocument:
    """Parse one sitemap file. Raises ``UnsafeDocument`` for XML with DTD entity declarations."""
    decoded = maybe_gunzip(body, max_bytes)
    doc = SitemapDocument(compressed=decoded.compressed, truncated=decoded.truncated)
    markup = decoded.data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<")
    root = parse_xml(decoded.data, base_url=base) if markup else None
    if root is not None:
        name = localname(root)
        if name == "urlset":
            doc.kind, doc.urls = "urlset", _entries(root, "url", base)
        elif name == "sitemapindex":
            doc.kind, doc.sitemaps = "sitemapindex", _entries(root, "sitemap", base)
        elif name in {"rss", "RDF", "feed"}:
            entries, doc.dropped = parse_feed(root, base, max_entries)
            doc.kind, doc.urls = "feed", [SitemapEntry(e.link, e.lastmod) for e in entries]
    elif not markup and decoded.data.strip():  # plain-text sitemap: one URL per line
        text = decoded.data.decode("utf-8", errors="replace")
        lines = [line.strip() for line in text.splitlines()]
        doc.kind = "text"
        doc.urls = [SitemapEntry(line) for line in lines if line.lower().startswith(("http://", "https://"))]
    for attr in ("urls", "sitemaps"):
        entries = getattr(doc, attr)
        if len(entries) > max_entries:
            doc.dropped += len(entries) - max_entries
            setattr(doc, attr, entries[:max_entries])
    return doc


class SitemapStrategy:
    """Reads sitemap files through ``ctx.fetch`` and proposes their URLs as material candidates."""

    type_name: ClassVar[str] = "sitemap"

    def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
        self.config = config
        self.strategy_id = strategy_id
        self.urls: list[str] = [u for u in config.get("urls") or [] if isinstance(u, str)]
        self.use_robots_txt = bool(config.get("use_robots_txt", True))
        self.lastmod_since = parse_datetime(config.get("lastmod_since"))
        if config.get("lastmod_since") and self.lastmod_since is None:
            raise ValueError(f"sitemap: lastmod_since {config.get('lastmod_since')!r} is not a timestamp")
        self.pass_lastmod = bool(config.get("use_lastmod_for_revisit", True))
        self.stats: dict[str, int] = {}

    # ------------------------------------------------------------------ discovery of sitemap files
    async def _start_documents(self, ctx: DiscoveryContext) -> list[str]:
        if self.urls:
            return list(self.urls)
        found: list[str] = []
        for origin in rule_origins(ctx.rules):
            if not ctx.in_scope(origin + "/"):
                continue
            from_robots: list[str] = []
            if self.use_robots_txt:
                robots = await fetch_document(ctx, origin + "/robots.txt")
                if robots is not None and is_success(robots):
                    text = robots.body.decode("utf-8", errors="replace")
                    from_robots = parse_robots_sitemaps(text, robots.final_url)
                    bump(self.stats, "robots_sitemaps", len(from_robots))
            found.extend(from_robots or [origin + "/sitemap.xml"])
        if not found:
            ctx.log.warning("sitemap: no origin in scope to look for sitemaps")
        return found

    async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
        self.stats = {}  # seeds are re-run from scratch after a restart
        try:
            async with aclosing(self._walk(ctx)) as walk:
                async for cand in walk:
                    yield cand
        except BudgetExhausted as exc:
            ctx.log.warning("sitemap strategy stopped: budget exhausted", extra={"reason": str(exc)})

    async def _walk(self, ctx: DiscoveryContext) -> AsyncGenerator[DiscoveredUrl, None]:
        max_depth = limit(ctx, "crawl.max_depth")
        max_entries = limit(ctx, "crawl.max_links_per_page")
        max_bytes = limit(ctx, "crawl.max_material_bytes")
        queue: deque[tuple[str, int]] = deque((u, 0) for u in await self._start_documents(ctx))
        seen: set[str] = set()
        while queue:
            if ctx.is_cancelled():
                return
            url, level = queue.popleft()
            normalized = safe_normalize(ctx, url)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            resource = await fetch_document(ctx, normalized)
            if resource is None or not is_success(resource):
                continue
            async with AsyncExitStack() as stack:
                doc = await self._parse(
                    ctx, resource, stack=stack, max_bytes=max_bytes, max_entries=max_entries
                )
                if doc is None:
                    continue
                for child in doc.sitemaps:
                    if level + 2 > max_depth:  # the child's URLs (depth level + 2) could not be admitted
                        bump(self.stats, "sitemaps_over_depth")
                        ctx.log.warning(
                            "sitemap index nesting stopped by crawl.max_depth",
                            extra={"index": resource.final_url, "sitemap": child.loc, "max_depth": max_depth},
                        )
                        continue
                    queue.append((child.loc, level + 1))
                for entry in doc.urls:
                    if self.lastmod_since and entry.lastmod and entry.lastmod < self.lastmod_since:
                        bump(self.stats, "skipped_lastmod")
                        continue
                    bump(self.stats, "urls")
                    yield DiscoveredUrl(
                        url=entry.loc,
                        strategy_id=self.strategy_id,
                        kind="material",
                        depth=level + 1,
                        parent_url=resource.final_url,
                        lastmod=entry.lastmod if self.pass_lastmod else None,
                    )

    async def _parse(
        self,
        ctx: DiscoveryContext,
        resource: FetchedResource,
        *,
        stack: AsyncExitStack,
        max_bytes: int,
        max_entries: int,
    ) -> SitemapDocument | None:
        try:
            doc = await stack.enter_async_context(
                _parse_executor().document(
                    resource.body, resource.final_url, max_bytes=max_bytes, max_entries=max_entries
                )
            )
        except UnsafeDocument as exc:
            bump(self.stats, "documents_refused")
            ctx.log.warning("sitemap refused", extra={"url": resource.final_url, "reason": str(exc)})
            return None
        bump(self.stats, "documents")
        if doc.compressed:
            bump(self.stats, "gzip_documents")
        if doc.truncated or resource.truncated:
            bump(self.stats, "truncated_documents")
            ctx.log.warning(
                "sitemap cut at crawl.max_material_bytes, only complete entries are used",
                extra={"url": resource.final_url, "limit": max_bytes},
            )
        if doc.dropped:
            bump(self.stats, "entries_over_limit", doc.dropped)
            ctx.log.warning(
                "sitemap entries over crawl.max_links_per_page dropped",
                extra={"url": resource.final_url, "dropped": doc.dropped, "limit": max_entries},
            )
        if doc.kind == "unknown":
            ctx.log.info(
                "not a sitemap", extra={"url": resource.final_url, "media_type": resource.media_type}
            )
        return doc

    async def on_fetched(
        self, resource: FetchedResource, ctx: DiscoveryContext
    ) -> AsyncIterator[DiscoveredUrl]:
        return
        yield  # pragma: no cover - makes this an async generator

    def snapshot(self) -> Mapping[str, Any]:
        return {"stats": dict(self.stats)} if self.stats else {}

    def restore(self, state: Mapping[str, Any]) -> None:
        self.stats = dict(state.get("stats") or {})
