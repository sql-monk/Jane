"""Crawl engine: one :class:`CrawlRun` per collection, implementing ``DiscoveryContext`` for strategies.

Pipeline for every URL (from the frontier or ``ctx.fetch``): scope/exclude (at admission) -> robots.txt
(or the explicit ``owner_policy``) -> revisit decision (URL history of the ``state_key``) -> fetch (per-host
limits, redirects re-checked hop by hop, size limit, conditional request) -> dedup of the final/canonical
URL -> Material (buffer) -> ``on_fetched`` of every strategy -> admission of new candidates (normalize,
scope, depth, frontier size, dedup by primary key) -> one transaction.
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import logging
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import httpx

from jane_contracts.discovery import (
    DiscoveredUrl,
    DiscoveryStrategy,
    FetchedResource,
    FetchRejected,
    LinkSelector,
    UrlKind,
)
from jane_kit.config import LimitLayer, ResolvedLimits
from jane_kit.jobs import JobCancelledError, JobContext

from .connections import auth_headers
from .discovery.links import extract_hrefs, html_meta, is_html, parse_html
from .discovery.registry import Registry
from .fetcher import Fetcher, FetchError, HostLimiter, HttpResult
from .materials import Delivery, MaterialTooLarge, TransitStore, build_material, new_observation_id, rfc3339
from .robots import RobotsCache
from .settings import ServiceLimits, to_contract
from .state import FrontierRow, LeaseLost, StateStore
from .urls import Normalizer, Scope, UrlPattern, compile_patterns, patterns_match

__all__ = ["CrawlRun", "LeaseLost", "RunDeps", "StrategyContext", "new_stats"]

log = logging.getLogger(__name__)

STAT_KEYS = (
    "discovered",
    "fetched",
    "emitted",
    "acknowledged",
    "unacked",
    "duplicates",
    "skipped_out_of_scope",
    "skipped_robots",
    "not_modified",
    "errors",
    "frontier_size",
    "bytes_fetched",
)


def new_stats() -> dict[str, Any]:
    return {**dict.fromkeys(STAT_KEYS, 0), "by_strategy": {}}


class RedirectDuplicate(Exception):
    """A redirect leads to a URL that is already in the frontier: stop before fetching it again."""

    def __init__(self, target: str) -> None:
        super().__init__(target)
        self.target = target


@dataclass
class RunDeps:
    """Service-level dependencies shared by all runs."""

    state: StateStore
    registry: Registry
    client: httpx.AsyncClient
    resolve: Callable[..., ResolvedLimits[ServiceLimits]]
    transit: TransitStore | None
    instance_id: str
    lease_seconds: float
    heartbeat_seconds: float
    user_agent: str
    version: str
    ack_events: dict[str, asyncio.Event] = field(default_factory=dict)


def _now_iso() -> str:
    return rfc3339(datetime.now(UTC))


class StrategyContext:
    """``DiscoveryContext`` given to one strategy (its own merged limits)."""

    def __init__(self, run: CrawlRun, strategy_id: str, limits: Mapping[str, Any]) -> None:
        self._run = run
        self.strategy_id = strategy_id
        self.source_id = run.source_id
        self.collection_id = run.collection_id
        self.rules: Mapping[str, Any] = run.rules
        self.limits: Mapping[str, Any] = limits
        self.log = logging.getLogger(f"jane_web_collector.strategy.{strategy_id}")

    async def fetch(
        self, url: str, *, kind: UrlKind = "navigation", conditional: bool = True
    ) -> FetchedResource | None:
        return await self._run.fetch_for_strategy(
            url, kind=kind, conditional=conditional, caller=self.strategy_id
        )

    def normalize(self, url: str, base: str | None = None) -> str:
        normalized = self._run.normalizer.normalize(url, base)
        if normalized is None:
            raise ValueError(f"not an HTTP(S) URL: {url!r}")
        return normalized

    def in_scope(self, url: str) -> bool:
        return self._run.scope_reason(url) is None

    def section_for(self, url: str) -> str | None:
        return self._run.section_for(url)

    def extract_links(self, resource: FetchedResource, selector: LinkSelector | None = None) -> list[str]:
        return self._run.extract_links(resource, selector)

    def extract_links_from(
        self, resource: FetchedResource, sources: Sequence[str] = ("a_href",)
    ) -> list[str]:
        return self._run.extract_links(resource, None, sources)

    def is_cancelled(self) -> bool:
        return self._run.cancelled


class CrawlRun:
    def __init__(self, deps: RunDeps, record: Mapping[str, Any]) -> None:
        self.deps = deps
        self.state = deps.state
        self.collection_id: str = record["collection_id"]
        self.state_key: str = record["state_key"]
        self.request: dict[str, Any] = record["request"]
        self.rules: dict[str, Any] = record["rules"]
        self.rules_ref: dict[str, Any] | None = record.get("rules_ref")
        self.source_id: str | None = self.request.get("source_id")
        self.mode: str = self.request.get("mode", "full")
        self.meta: dict[str, Any] = dict(record.get("meta") or {})
        self.stats: dict[str, Any] = {**new_stats(), **(record.get("stats") or {})}
        self.counters: dict[str, int] = dict(self.meta.get("counters") or {})
        self.resolved = deps.resolve(self.rules.get("limits"), self.request.get("limits"))
        self.limits: ServiceLimits = self.resolved.limits
        self.normalizer = Normalizer.from_rules(self.rules)
        self.scope = Scope.from_rules(self.rules)
        self.sections: list[tuple[str, tuple[UrlPattern, ...]]] = [
            (s["section_id"], compile_patterns(s["patterns"])) for s in self.rules.get("sections") or []
        ]
        self.priority_rules: list[tuple[UrlPattern, int]] = [
            (UrlPattern.from_rule(p["pattern"]), int(p["priority"]))
            for p in self.rules.get("priorities") or []
        ]
        robots_cfg = self.rules.get("robots") or {}
        self.owner_policy = robots_cfg.get("mode") == "owner_policy"
        fetch_cfg = self.rules.get("fetch") or {}
        user_agent = fetch_cfg.get("user_agent") or deps.user_agent
        token = robots_cfg.get("user_agent_token") or user_agent.split("/", 1)[0].split()[0]
        dedup = self.rules.get("dedup") or {}
        self.dedup_key = dedup.get("key", "canonical_url")
        self.use_link_canonical = bool(dedup.get("use_link_rel_canonical", True))
        self.revisit_mode = (self.rules.get("revisit") or {}).get("mode", "never")
        self.delivery = Delivery(
            mode=self.request.get("content_delivery", "auto"),
            inline_max_bytes=self.limits.transfer.inline_max_bytes,
            transit_ttl_seconds=self.limits.transfer.transit_ttl_seconds,
            store=deps.transit,
        )
        self.accept = fetch_cfg.get("accept_media_types")
        headers = dict(fetch_cfg.get("headers") or {})
        if self.accept:
            headers.setdefault("Accept", ", ".join(self.accept))
        creds: dict[str, str] = {}
        if fetch_cfg.get("connection_id"):
            found = self.state.get_connection(fetch_cfg["connection_id"])
            if found is not None:
                creds = auth_headers(found[0])
        self.limiter = HostLimiter(self.limits)
        self.robots_fetcher = Fetcher(
            deps.client, self.limits, self.limiter, user_agent=user_agent, headers=headers
        )
        self.robots = RobotsCache(self._fetch_robots, token, self.limits.collector.robots_cache_ttl_seconds)
        self.fetcher = Fetcher(
            deps.client,
            self.limits,
            self.limiter,
            user_agent=user_agent,
            headers=headers,
            auth_headers=creds,
            crawl_delay_for=None if self.owner_policy else self._crawl_delay,
        )
        self.strategies: list[tuple[str, DiscoveryStrategy, StrategyContext, int]] = []
        self.cancelled = False
        self.stop_reason: str | None = None
        self.fetched_here: set[str] = set()
        self._job: JobContext | None = None
        self.fence = (self.collection_id, deps.instance_id)
        self._stop_exc: BaseException | None = None
        self.strategy_limits: dict[str, ServiceLimits] = {}
        self._last_progress = 0.0

    # ------------------------------------------------------------------ helpers for strategies
    def _tx(self) -> Any:
        """Transaction fenced by this run's lease: a run that lost its lease cannot write anything."""
        return self.state.tx(self.fence)

    def scope_reason(self, url: str) -> str | None:
        if self.scope is None:
            return None
        return self.scope.check(url)

    def section_for(self, url: str) -> str | None:
        for section_id, patterns in self.sections:
            if patterns_match(patterns, url):
                return section_id
        return None

    def rule_priority(self, url: str) -> int:
        for pattern, priority in self.priority_rules:
            if pattern.matches(url):
                return priority
        return 0

    def extract_links(
        self,
        resource: FetchedResource,
        selector: LinkSelector | None = None,
        sources: Sequence[str] = ("a_href",),
    ) -> list[str]:
        if not is_html(resource.media_type):
            return []
        doc = parse_html(resource.body)
        if doc is None:
            return []
        base = resource.final_url
        for el in doc.iter("base"):
            if el.get("href"):
                base = self.normalizer.normalize(el.get("href"), resource.final_url) or base
                break
        raw = extract_hrefs(
            doc,
            selector_type=selector.type if selector else None,
            selector=selector.value if selector else None,
            attribute=selector.attribute if selector else "href",
            sources=sources,
        )
        out: list[str] = []
        seen: set[str] = set()
        cap = self.limits.crawl.max_links_per_page
        for href in raw:
            url = self.normalizer.normalize(href, base)
            if url and url not in seen:
                seen.add(url)
                out.append(url)
                if len(out) >= cap:
                    break
        return out

    # ------------------------------------------------------------------ robots
    async def _fetch_robots(self, url: str) -> tuple[int, str] | None:
        try:
            res = await self.robots_fetcher.get(url, max_bytes=self.limits.collector.robots_max_bytes)
        except FetchError:
            return None
        return res.status, res.body.decode("utf-8", errors="replace")

    async def _crawl_delay(self, url: str) -> float | None:
        return (await self.robots.rules_for(url)).crawl_delay

    async def robots_allowed(self, url: str) -> bool:
        return True if self.owner_policy else await self.robots.allowed(url)

    async def _check_hop(self, url: str) -> None:
        canonical = self.normalizer.normalize(url)
        if canonical is None:
            raise FetchRejected("out_of_scope", f"redirect to a non-HTTP URL {url}")
        reason = self.scope_reason(canonical)
        if reason:
            raise FetchRejected("out_of_scope", f"redirect to {canonical}: {reason}")
        if not await self.robots_allowed(canonical):
            raise FetchRejected(
                "access_denied_by_policy", f"redirect to {canonical}: disallowed by robots.txt"
            )

    # ------------------------------------------------------------------ admission
    def _strategy_depth(self, strategy_id: str | None) -> int:
        for sid, _, _, depth in self.strategies:
            if sid == strategy_id:
                return depth
        return self.limits.crawl.max_depth

    def _strategy_priority(self, strategy_id: str | None) -> tuple[int, str | None]:
        for sid, strategy, _, _ in self.strategies:
            if sid == strategy_id:
                cfg = getattr(strategy, "config", {}) or {}
                return int(cfg.get("priority", 0)), cfg.get("section")
        return 0, None

    def admit(self, candidates: Sequence[DiscoveredUrl], parent_depth: int | None) -> list[FrontierRow]:
        """Normalize and filter candidates (scope, depth, frontier size); dedup happens on insert."""
        rows: list[FrontierRow] = []
        pending = self.state.frontier_counts(self.collection_id).get("pending", 0)
        seen: set[str] = set()
        for cand in candidates:
            url = self.normalizer.normalize(cand.url, cand.parent_url)
            if url is None:
                continue
            if url in seen:
                self.stats["duplicates"] += 1
                continue
            seen.add(url)
            if self.scope_reason(url):
                self.stats["skipped_out_of_scope"] += 1
                continue
            depth = parent_depth + 1 if parent_depth is not None else cand.depth
            if depth > self._strategy_depth(cand.strategy_id):
                self.counters["skipped_depth"] = self.counters.get("skipped_depth", 0) + 1
                continue
            if pending + len(rows) >= self.limits.crawl.max_frontier_size:
                self.counters["dropped_frontier_full"] = self.counters.get("dropped_frontier_full", 0) + 1
                continue
            strat_priority, forced_section = self._strategy_priority(cand.strategy_id)
            rows.append(
                FrontierRow(
                    url=url,
                    priority=self.rule_priority(url) + strat_priority + cand.priority,
                    depth=depth,
                    kind=cand.kind,
                    strategy_id=cand.strategy_id,
                    parent_url=cand.parent_url,
                    section=forced_section or cand.section or self.section_for(url),
                    lastmod=cand.lastmod.isoformat() if cand.lastmod else None,
                )
            )
        return rows

    def insert_rows(self, db: Any, rows: Sequence[FrontierRow]) -> None:
        for row in rows:
            added = self.state.add_urls(db, self.collection_id, [row])
            if added:
                self.stats["discovered"] += 1
                by = self.stats["by_strategy"]
                key = row.strategy_id or "unknown"
                by[key] = by.get(key, 0) + 1
            else:
                self.stats["duplicates"] += 1

    # ------------------------------------------------------------------ errors and persistence
    def _error(
        self,
        db: Any,
        url: str,
        code: str,
        message: str,
        *,
        http_status: int | None = None,
        attempts: int | None = None,
    ) -> None:
        err: dict[str, Any] = {"url": url, "code": code, "message": message, "at": _now_iso()}
        if http_status is not None:
            err["http_status"] = http_status
        if attempts is not None:
            err["attempts"] = attempts
        self.state.add_error(db, self.collection_id, err)
        if code != "access_denied_by_policy":
            self.stats["errors"] += 1

    def _snapshot_all(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for sid, strategy, _, _ in self.strategies:
            try:
                out[sid] = dict(strategy.snapshot())
            except Exception:
                log.exception("strategy snapshot failed", extra={"strategy_id": sid})
        return out

    def _persist(self, db: Any) -> None:
        snapshots = self._snapshot_all()
        self.state.save_strategy_states(db, self.collection_id, snapshots)
        self.state.save_cursors(db, self.state_key, {k: v for k, v in snapshots.items() if v}, _now_iso())
        self.meta["counters"] = self.counters
        self.state.save_stats(db, self.collection_id, self.stats)
        db.execute(
            "UPDATE collections SET meta = ? WHERE collection_id = ?",
            (json.dumps(self.meta, sort_keys=True), self.collection_id),
        )

    # ------------------------------------------------------------------ fetching one URL
    def _budget_left(self) -> str | None:
        if self.stats["fetched"] >= self.limits.crawl.max_pages_per_run:
            return "crawl.max_pages_per_run"
        if self.stats["bytes_fetched"] >= self.limits.crawl.max_bytes_per_run:
            return "crawl.max_bytes_per_run"
        return None

    async def _wait_backpressure(self) -> None:
        limit = self.limits.queue.max_unacked_materials
        if self.state.unacked_count(self.collection_id) < limit:
            return
        self.state.set_paused(self.collection_id, True)
        event = self.deps.ack_events.setdefault(self.collection_id, asyncio.Event())
        try:
            while self.state.unacked_count(self.collection_id) >= limit and not self.cancelled:
                event.clear()
                with contextlib.suppress(TimeoutError):  # an ack may come through another instance
                    await asyncio.wait_for(
                        event.wait(), timeout=self.limits.collector.backpressure_poll_ms / 1000
                    )
        finally:
            self.state.set_paused(self.collection_id, False)

    def _stored_links_candidates(self, links: Sequence[str], parent: str) -> list[DiscoveredUrl]:
        out: list[DiscoveredUrl] = []
        for sid, strategy, _, _ in self.strategies:
            if getattr(strategy, "type_name", None) != "recursive":
                continue
            follow: tuple[UrlPattern, ...] = getattr(strategy, "follow", ())
            out.extend(
                DiscoveredUrl(url=link, strategy_id=sid, kind="material", parent_url=parent)
                for link in links
                if not follow or patterns_match(follow, link)
            )
        return out

    def _revisit_skip(self, prev: Mapping[str, Any] | None) -> bool:
        if self.mode != "incremental" or prev is None or not (prev.get("status") or 0) < 400:
            return False
        if self.revisit_mode == "never":
            return True
        if self.revisit_mode == "interval":
            return time.time() - float(prev["fetched_at"]) < self.limits.crawl.revisit_interval_seconds
        return False

    async def handle(
        self, row: FrontierRow, *, caller: str | None = None, conditional: bool = True
    ) -> FetchedResource | None:
        """Fetch and process one admitted URL. Returns the resource (for ``ctx.fetch``) or ``None``."""
        url = row.url
        with self._tx() as db:
            if self.state.known(self.collection_id, url):
                self.state.mark_url(db, self.collection_id, url, "inflight")
            else:
                self.state.add_urls(db, self.collection_id, [row], status="inflight")
        if not await self.robots_allowed(url):
            with self._tx() as db:
                self.stats["skipped_robots"] += 1
                self._error(db, url, "access_denied_by_policy", "disallowed by robots.txt")
                self.state.mark_url(db, self.collection_id, url, "skipped")
                self._persist(db)
            if caller is not None:
                raise FetchRejected("access_denied_by_policy", f"{url}: disallowed by robots.txt")
            return None
        prev = self.state.url_state(self.state_key, url)
        if caller is None and self._revisit_skip(prev):
            assert prev is not None
            with self._tx() as db:
                self.stats["not_modified"] += 1
                self.insert_rows(db, self.admit(self._stored_links_candidates(prev["links"], url), row.depth))
                self.state.mark_url(db, self.collection_id, url, "unchanged")
                self._persist(db)
            return None
        cond: dict[str, str] = {}
        if prev and conditional and (self.revisit_mode == "if_changed" or caller is not None):
            if prev.get("etag"):
                cond["If-None-Match"] = prev["etag"]
            if prev.get("last_modified"):
                cond["If-Modified-Since"] = prev["last_modified"]
        if row.kind == "material":
            await self._wait_backpressure()
        self.fetched_here.add(url)
        claimed: list[str] = []

        async def hop(target: str) -> None:
            await self._check_hop(target)
            canonical = self.normalizer.normalize(target) or target
            if canonical == url or canonical in claimed:
                return
            with self._tx() as db:
                added = self.state.add_urls(
                    db,
                    self.collection_id,
                    [
                        FrontierRow(
                            canonical, row.priority, row.depth, row.kind, row.strategy_id, url, row.section
                        )
                    ],
                    status="inflight",
                )
            if not added:  # the redirect target is already known: do not fetch it a second time
                raise RedirectDuplicate(canonical)
            claimed.append(canonical)

        try:
            timeouts = self.strategy_limits.get(row.strategy_id or "", self.limits).timeouts
            result = await self.fetcher.get(url, check_hop=hop, conditional=cond, timeouts=timeouts)
        except RedirectDuplicate as dup:
            with self._tx() as db:
                self.stats["fetched"] += 1
                self.stats["duplicates"] += 1
                for other in claimed:
                    self.state.mark_url(db, self.collection_id, other, "redirect")
                self.state.mark_url(db, self.collection_id, url, "redirect")
                # remembered for revisits: an incremental run follows the stored target without refetching
                self.state.put_url_state(
                    db,
                    self.state_key,
                    url,
                    status=None,
                    etag=None,
                    last_modified=None,
                    content_sha256=None,
                    links=[dup.target],
                )
                self._persist(db)
            log.debug("redirect to a known URL", extra={"url": url, "target": dup.target})
            return None
        except FetchRejected as exc:
            with self._tx() as db:
                for other in claimed:
                    self.state.mark_url(db, self.collection_id, other, "skipped")
                if exc.code == "access_denied_by_policy":
                    self.stats["skipped_robots"] += 1
                else:
                    self.stats["skipped_out_of_scope"] += 1
                self._error(db, url, exc.code, str(exc))
                self.state.mark_url(db, self.collection_id, url, "skipped")
                self._persist(db)
            if caller is not None:
                raise
            return None
        except FetchError as exc:
            with self._tx() as db:
                for other in claimed:
                    self.state.mark_url(db, self.collection_id, other, "failed")
                self.stats["fetched"] += 1
                self._error(
                    db, url, exc.code, exc.message, http_status=exc.http_status, attempts=exc.attempts
                )
                self.state.mark_url(db, self.collection_id, url, "failed")
                self._persist(db)
            return None
        return await self._process_result(row, result, prev, caller, claimed)

    async def _process_result(
        self,
        row: FrontierRow,
        result: HttpResult,
        prev: Mapping[str, Any] | None,
        caller: str | None,
        claimed: Sequence[str] = (),
    ) -> FetchedResource | None:
        url = row.url
        self.stats["fetched"] += 1
        self.stats["bytes_fetched"] += len(result.body)
        if result.status == 304:
            with self._tx() as db:
                self.stats["not_modified"] += 1
                self.state.put_url_state(
                    db,
                    self.state_key,
                    url,
                    status=304,
                    etag=None,
                    last_modified=None,
                    content_sha256=None,
                    links=None,
                )
                if prev and caller is None:
                    self.insert_rows(
                        db, self.admit(self._stored_links_candidates(prev["links"], url), row.depth)
                    )
                self.state.mark_url(db, self.collection_id, url, "unchanged")
                self._persist(db)
            return None
        resource = FetchedResource(
            url=url,
            final_url=result.final_url,
            status=result.status,
            media_type=result.media_type,
            headers=dict(result.headers),
            body=result.body,
            fetched_at=result.fetched_at,
            depth=row.depth,
            strategy_id=row.strategy_id,
            kind=row.kind,  # type: ignore[arg-type]
            truncated=result.truncated,
        )
        canonical = self.normalizer.normalize(result.final_url) or url
        duplicate_of: str | None = None
        extra_done: list[FrontierRow] = []
        doc = parse_html(result.body) if is_html(result.media_type) and result.status < 300 else None
        if canonical != url and canonical not in claimed:
            if self.state.known(self.collection_id, canonical):
                duplicate_of = canonical
            else:
                extra_done.append(
                    FrontierRow(
                        canonical, row.priority, row.depth, row.kind, row.strategy_id, url, row.section
                    )
                )
        if doc is not None and self.use_link_canonical and duplicate_of is None:
            for href in extract_hrefs(doc, sources=("canonical",))[:1]:
                target = self.normalizer.normalize(href, result.final_url)
                if target and target != canonical and self.scope_reason(target) is None:
                    if self.state.known(self.collection_id, target):
                        duplicate_of = target
                    else:
                        extra_done.append(
                            FrontierRow(
                                target, row.priority, row.depth, row.kind, row.strategy_id, url, row.section
                            )
                        )
                        canonical = target
        content_sha = resource_sha(result.body)
        material: dict[str, Any] | None = None
        error: tuple[str, str] | None = None
        if result.status >= 400:
            code = "not_found" if result.status in (404, 410) else "source_unavailable"
            error = (code, f"HTTP {result.status}")
        elif duplicate_of is None and row.kind == "material" and 200 <= result.status < 300:
            changed = prev is None or prev.get("content_sha256") != content_sha
            if self.dedup_key == "canonical_url" or changed:
                try:
                    material = build_material(
                        result,
                        canonical_url=canonical,
                        observation_id=new_observation_id(),
                        source_id=self.source_id,
                        delivery=self.delivery,
                        collector_version=self.deps.version,
                        collection_id=self.collection_id,
                        rules_ref=self.rules_ref,
                        discovery={
                            "strategy": self._strategy_type(row.strategy_id),
                            "parent_url": row.parent_url,
                            "depth": row.depth,
                            "section": row.section,
                            "priority": row.priority,
                        },
                        html_meta=html_meta(doc) if doc is not None else None,
                    )
                except MaterialTooLarge as exc:
                    error = ("limit_exceeded", str(exc))
            else:
                self.stats["not_modified"] += 1
        candidates: list[DiscoveredUrl] = []
        if duplicate_of is None:
            candidates = await self._on_fetched(resource, exclude=caller)
        links = self.extract_links(resource) if doc is not None else None
        with self._tx() as db:
            if duplicate_of is not None:
                self.stats["duplicates"] += 1
            self.state.add_urls(db, self.collection_id, extra_done, status="done")
            for other in claimed:  # redirect hops and the final URL were claimed while following redirects
                self.state.mark_url(
                    db, self.collection_id, other, "done" if other == canonical else "redirect"
                )
            self.insert_rows(db, self.admit(candidates, row.depth))
            if error is not None:
                self._error(
                    db,
                    url,
                    error[0],
                    error[1],
                    http_status=result.status if result.status >= 400 else None,
                    attempts=result.attempts,
                )
            if material is not None:
                self.state.append_material(db, self.collection_id, material["observation_id"], material)
                self.stats["emitted"] += 1
            self.state.put_url_state(
                db,
                self.state_key,
                url,
                status=result.status,
                etag=result.headers.get("etag"),
                last_modified=result.headers.get("last-modified"),
                content_sha256=content_sha if result.status < 300 else None,
                links=links,
            )
            self.state.mark_url(db, self.collection_id, url, "failed" if result.status >= 400 else "done")
            self._persist(db)
        return resource

    def _strategy_type(self, strategy_id: str | None) -> str | None:
        for sid, strategy, _, _ in self.strategies:
            if sid == strategy_id:
                return getattr(strategy, "type_name", None)
        return strategy_id

    async def _on_fetched(self, resource: FetchedResource, exclude: str | None) -> list[DiscoveredUrl]:
        out: list[DiscoveredUrl] = []
        cap = self.limits.crawl.max_links_per_page
        for sid, strategy, ctx, _ in self.strategies:
            if sid == exclude:
                continue
            count = 0
            try:
                async for cand in strategy.on_fetched(resource, ctx):
                    out.append(cand)
                    count += 1
                    if count >= cap:
                        break
            except Exception as exc:
                log.exception("strategy on_fetched failed", extra={"strategy_id": sid, "url": resource.url})
                with self._tx() as db:
                    self._error(
                        db,
                        resource.url,
                        "internal_error",
                        f"strategy {sid} failed: {type(exc).__name__}: {exc}",
                    )
        return out

    async def fetch_for_strategy(
        self, url: str, *, kind: UrlKind, conditional: bool, caller: str
    ) -> FetchedResource | None:
        canonical = self.normalizer.normalize(url)
        if canonical is None:
            raise FetchRejected("out_of_scope", f"not an HTTP(S) URL: {url}")
        reason = self.scope_reason(canonical)
        if reason:
            self.stats["skipped_out_of_scope"] += 1
            raise FetchRejected("out_of_scope", f"{canonical}: {reason}")
        if canonical in self.fetched_here:
            return None
        existing = self.state.frontier_row(self.collection_id, canonical)
        if (
            existing is not None
            and existing["kind"] == "material"
            and existing["status"] in ("done", "unchanged")
        ):
            return None
        if budget := self._budget_left():
            raise FetchRejected("limit_exceeded", f"{budget} reached")
        row = FrontierRow(canonical, 0, 0, kind, caller, None, self.section_for(canonical))
        return await self.handle(row, caller=caller, conditional=conditional)

    # ------------------------------------------------------------------ run
    def _build_strategies(self) -> None:
        configs: list[Mapping[str, Any]]
        if self.request.get("urls"):
            configs = [{"type": "seed_list", "urls": self.request["urls"], "strategy_id": "request-urls"}]
        else:
            configs = self.rules.get("strategies") or []
        saved = self.state.load_strategy_states(self.collection_id)
        for i, cfg in enumerate(configs):
            sid = cfg.get("strategy_id") or f"{cfg['type']}-{i}"
            cls = self.deps.registry.get(cfg["type"])
            strategy = cls(cfg, sid)
            if sid in saved:
                strategy.restore(saved[sid])
            if cfg.get("limits"):
                resolved = self.deps.resolve(
                    self.rules.get("limits"),
                    self.request.get("limits"),
                    LimitLayer("stage", cfg["limits"], name=f"strategy:{sid}"),
                )
                strat_limits = resolved.limits
            else:
                strat_limits = self.limits
            self.strategy_limits[sid] = strat_limits
            ctx = StrategyContext(self, sid, to_contract(strat_limits))
            self.strategies.append((sid, strategy, ctx, strat_limits.crawl.max_depth))

    async def _seed(self) -> None:
        seeded: list[str] = list(self.meta.get("seeded") or [])
        for sid, strategy, ctx, _ in self.strategies:
            if sid in seeded:
                continue
            batch: list[DiscoveredUrl] = []
            async for cand in strategy.seeds(ctx):
                batch.append(cand)
                if len(batch) >= max(1, self.limits.crawl.max_links_per_page):
                    self._commit_seeds(batch)
                    batch = []
                if self.cancelled:
                    return
            self._commit_seeds(batch)
            seeded.append(sid)
            self.meta["seeded"] = seeded
            with self._tx() as db:
                self._persist(db)

    def _commit_seeds(self, batch: Sequence[DiscoveredUrl]) -> None:
        if not batch:
            return
        rows = self.admit(batch, None)
        with self._tx() as db:
            self.insert_rows(db, rows)
            self._persist(db)

    async def _beat(self) -> None:
        """Renew the lease; detect cancellation requested through another instance; report progress."""
        if not self.state.claim(self.collection_id, self.deps.instance_id, self.deps.lease_seconds):
            raise LeaseLost(self.collection_id)
        job = self.state.get_job(self.collection_id)
        if job is not None and '"status":"cancelling"' in job.replace(" ", ""):
            self.cancelled = True
            raise JobCancelledError(self.collection_id)
        if self._job is not None:
            counts = self.state.frontier_counts(self.collection_id)
            done = sum(v for k, v in counts.items() if k not in ("pending", "inflight"))
            await self._job.progress(
                done,
                done + counts.get("pending", 0) + counts.get("inflight", 0),
                unit="urls",
                counters={k: int(v) for k, v in self.stats.items() if isinstance(v, int)} | self.counters,
            )

    async def _heartbeat_loop(self, main: asyncio.Task[Any]) -> None:
        """Runs beside the crawl (also during seeding and slow fetches); stops the run when the lease is
        lost or the job is cancelled elsewhere."""
        while True:
            await asyncio.sleep(self.deps.heartbeat_seconds)
            try:
                await self._beat()
            except (LeaseLost, JobCancelledError) as exc:
                self._stop_exc = exc
                main.cancel()
                return
            except Exception:
                log.exception("heartbeat failed", extra={"collection_id": self.collection_id})

    async def execute(self, job: JobContext | None = None) -> dict[str, Any]:
        self._job = job
        main = asyncio.current_task()
        if main is None:
            raise RuntimeError("execute() must run inside a task")
        await self._beat()
        heartbeat = asyncio.create_task(self._heartbeat_loop(main), name=f"heartbeat {self.collection_id}")
        try:
            return await self._execute()
        except asyncio.CancelledError:
            if self._stop_exc is not None:
                main.uncancel()
                raise self._stop_exc from None
            raise
        finally:
            heartbeat.cancel()
            await asyncio.gather(heartbeat, return_exceptions=True)

    async def _execute(self) -> dict[str, Any]:
        # URLs left in flight by a previous owner (killed or stalled instance) go back to the queue
        self.state.reset_inflight(self.collection_id, self.fence)
        self._build_strategies()
        await self._seed()
        while True:
            await self._loop()
            if self.stop_reason:
                dropped = self.state.drop_pending(self.collection_id, self.fence)
                self.counters["dropped_by_budget"] = self.counters.get("dropped_by_budget", 0) + dropped
                break
            counts = self.state.frontier_counts(self.collection_id)
            if not counts.get("pending") and not counts.get("inflight"):
                break
            # nothing of ours is running: whatever is still in flight is stale -> fetch it again
            self.state.reset_inflight(self.collection_id, self.fence)
        result: dict[str, Any] = {"collection_id": self.collection_id, "stats": self.stats}
        if self.stop_reason:
            result["stopped_by"] = self.stop_reason
        with self._tx() as db:
            open_rows = db.execute(
                "SELECT COUNT(*) FROM frontier WHERE collection_id = ? AND status IN ('pending', 'inflight')",
                (self.collection_id,),
            ).fetchone()[0]
            if open_rows:  # cannot happen after the loop above; never report success with open URLs
                raise RuntimeError(f"{open_rows} URLs still open at the end of the run")
            job_row = db.execute("SELECT body FROM jobs WHERE job_id = ?", (self.collection_id,)).fetchone()
            if job_row is not None and json.loads(job_row[0]).get("status") == "cancelling":
                self.cancelled = True
                raise JobCancelledError(self.collection_id)  # cancellation never ends as "succeeded"
            self._persist(db)
            self.state.set_status(self.collection_id, "succeeded", finished_at=_now_iso(), db=db)
            db.execute(
                "UPDATE collections SET lease_until = 0 WHERE collection_id = ?", (self.collection_id,)
            )
        return result

    async def _loop(self) -> None:
        running: set[asyncio.Task[Any]] = set()
        interval = self.deps.heartbeat_seconds
        try:
            while True:
                if self.stop_reason is None and (reason := self._budget_left()):
                    self.stop_reason = reason
                if self.stop_reason is None:
                    free = self.limits.concurrency.max_parallel_fetches - len(running)
                    free = min(
                        free, self.limits.crawl.max_pages_per_run - self.stats["fetched"] - len(running)
                    )
                    if free > 0:
                        for row in self.state.take_pending(self.collection_id, free, self.fence):
                            running.add(asyncio.create_task(self.handle(row), name=f"fetch {row.url}"))
                if not running:
                    if self.stop_reason is not None or not self.state.frontier_counts(self.collection_id).get(
                        "pending"
                    ):
                        return
                    continue
                done, running = await asyncio.wait(
                    running, timeout=interval, return_when=asyncio.FIRST_COMPLETED
                )
                for task in done:
                    if (exc := task.exception()) is not None:
                        raise exc
        finally:
            for task in running:
                task.cancel()
            if running:
                await asyncio.gather(*running, return_exceptions=True)


def resource_sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()
