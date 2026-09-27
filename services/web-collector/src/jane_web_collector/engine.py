"""Service core: collections (start, resume after restart, cancellation), the one-shot fetch and housekeeping."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from jane_kit.config import LimitError, LimitLayer, ResolvedLimits, resolve_limits
from jane_kit.errors import FieldError, Forbidden, JaneError, LimitExceeded, NotFound, ValidationFailed
from jane_kit.jobs import Job, JobCancelledError, JobContext, JobRunner, JobStatus

from . import __version__
from .connections import auth_headers
from .crawler import CrawlRun, LeaseLost, RunDeps, new_stats
from .discovery.links import html_meta, is_html, parse_html
from .discovery.registry import RESERVED_TYPES, Registry
from .fetcher import Fetcher, FetchError, HostLimiter, build_client
from .materials import Delivery, MaterialTooLarge, TransitStore, build_material, new_observation_id, rfc3339
from .robots import RobotsCache
from .rules import ContractSchemas, RulesLoader, validate_rules
from .settings import ServiceLimits, Settings, platform_layers, to_contract, translate_layer
from .state import StateStore
from .urls import Normalizer, Scope

__all__ = ["Engine"]

log = logging.getLogger(__name__)

TERMINAL = {"succeeded", "failed", "cancelled"}


def _now() -> str:
    return rfc3339(datetime.now(UTC))


class Engine:
    def __init__(
        self,
        settings: Settings,
        base_limits: ResolvedLimits[ServiceLimits],
        state: StateStore,
        registry: Registry,
        schemas: ContractSchemas,
        runner: JobRunner,
    ) -> None:
        self.settings = settings
        self.base = base_limits
        self.limits = base_limits.limits
        self.state = state
        self.registry = registry
        self.schemas = schemas
        self.runner = runner
        self.platform = platform_layers(settings)
        self.transit = TransitStore(settings.transit_dir) if settings.transit_dir else None
        self.rules_loader = RulesLoader(
            rules_dir=settings.rules_dir,
            registry_url=settings.registry_url,
            registry_token_env=settings.registry_token_env,
            timeout_s=self.limits.timeouts.request_timeout_ms / 1000,
        )
        self.client = build_client(self.limits)
        self.deps = RunDeps(
            state=state,
            registry=registry,
            client=self.client,
            resolve=self.resolve,
            transit=self.transit,
            instance_id=settings.instance_id,
            lease_seconds=settings.lease_seconds,
            heartbeat_seconds=settings.heartbeat_interval_ms / 1000,
            user_agent=settings.user_agent,
            version=__version__,
        )
        self.local: set[str] = set()
        self.shutting_down = False
        self._tasks: list[asyncio.Task[None]] = []
        self._fetch_limiter = HostLimiter(self.limits)

    # ------------------------------------------------------------------ limits
    def resolve(
        self,
        source: Mapping[str, Any] | None = None,
        request: Mapping[str, Any] | None = None,
        *extra: LimitLayer,
    ) -> ResolvedLimits[ServiceLimits]:
        layers = []
        if source:
            layers.append(LimitLayer("source", source, name="rules"))
        if request:
            layers.append(LimitLayer("request", request, name="request"))
        layers.extend(extra)
        try:
            return resolve_limits(
                ServiceLimits, *self.platform, *(translate_layer(la, contract_only=True) for la in layers)
            )
        except LimitError as exc:
            raise ValidationFailed(f"invalid limits: {exc}") from exc

    # ------------------------------------------------------------------ lifecycle
    async def start(self) -> None:
        self._tasks.append(asyncio.create_task(self._resume_loop(), name="resume-loop"))
        self._tasks.append(asyncio.create_task(self._gc_loop(), name="gc-loop"))

    async def stop(self) -> None:
        self.shutting_down = True
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.runner.shutdown()
        for cid in list(self.local):
            self.state.release(cid, self.settings.instance_id)
        await self.client.aclose()

    async def _resume_loop(self) -> None:
        interval = max(1.0, self.settings.lease_seconds / 3)
        while True:
            try:
                await self.resume_pending()
            except Exception:
                log.exception("resume loop failed")
            await asyncio.sleep(interval)

    async def resume_pending(self) -> list[str]:
        """Take over non-terminal collections whose lease expired (after a crash/kill) and continue them."""
        resumed = []
        for cid in self.state.resumable(self.settings.instance_id):
            if cid in self.local or not self.state.claim(
                cid, self.settings.instance_id, self.settings.lease_seconds
            ):
                continue
            job = self.state.get_job(cid)
            if job is not None and Job.model_validate_json(job).status == JobStatus.CANCELLING:
                self.state.set_status(cid, "cancelled", finished_at=_now())
                stored = Job.model_validate_json(job)
                await self.runner.store.save(
                    stored.model_copy(
                        update={"status": JobStatus.CANCELLED, "finished_at": datetime.now(UTC)}
                    )
                )
                continue
            log.info("resuming collection", extra={"collection_id": cid})
            await self._submit(cid)
            resumed.append(cid)
        return resumed

    async def _gc_loop(self) -> None:
        interval = min(self.limits.collector.gc_interval_seconds, self.limits.jobs.job_retention_seconds / 10)
        while True:
            await asyncio.sleep(interval)
            try:
                self.gc()
            except Exception:
                log.exception("gc failed")

    def gc(self) -> None:
        expired = self.state.expire_finished(time.time() - self.limits.jobs.job_retention_seconds)
        if expired:
            log.info("collections expired", extra={"count": len(expired)})
        if self.transit is not None:
            self.transit.cleanup(self.limits.transfer.transit_ttl_seconds)

    # ------------------------------------------------------------------ validation
    def _schema_errors(self, component: str, payload: Any) -> None:
        errors = self.schemas.errors(self.schemas.component(component), payload)
        if errors:
            raise ValidationFailed("request does not match the API contract", errors=errors)

    async def _rules_for(
        self, payload: Mapping[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any] | None, str]:
        """Rules document, rules_ref and the JSON pointer prefix for error messages."""
        ref: Mapping[str, Any] | None = payload.get("rules_ref")
        if payload.get("rules") is not None:
            return dict(payload["rules"]), dict(ref) if ref else None, "/rules"
        if ref is None:
            raise ValidationFailed("rules or rules_ref is required")
        rules = await self.rules_loader.load(ref)
        return rules, dict(ref), "/rules_ref"

    def _check_rules(self, rules: Mapping[str, Any], pointer: str) -> None:
        report = validate_rules(self.schemas, self.registry, rules)
        if not report.valid:
            errors = [
                FieldError(pointer=pointer + (e.pointer or ""), code=e.code, message=e.message)
                for e in report.errors
            ]
            raise ValidationFailed("collector rules are invalid", errors=errors)
        if not report.supported:
            errors = [
                FieldError(pointer=pointer + (w.pointer or ""), code=w.code, message=w.message)
                for w in report.warnings
                if w.code == "unsupported_strategy" or w.pointer == "/collector"
            ]
            raise ValidationFailed(
                "collector rules use features this collector does not execute", errors=errors
            )

    def _web_only(self, payload: Mapping[str, Any]) -> None:
        if payload.get("source_kind") != "web":
            raise ValidationFailed(
                "web-collector collects only source_kind=web",
                errors=[FieldError(pointer="/source_kind", message="expected web")],
            )

    # ------------------------------------------------------------------ collections
    async def start_collection(self, payload: dict[str, Any]) -> Job:
        self._schema_errors("CollectionRequest", payload)
        self._web_only(payload)
        rules, rules_ref, pointer = await self._rules_for(payload)
        self._check_rules(rules, pointer)
        resolved = self.resolve(rules.get("limits"), payload.get("limits"))
        urls = payload.get("urls") or []
        seed_total = len(urls) + sum(
            len(s.get("urls") or []) for s in rules.get("strategies") or [] if s.get("type") == "seed_list"
        )
        if seed_total > resolved.limits.crawl.max_seed_urls:
            raise LimitExceeded(
                f"{seed_total} seed URLs > crawl.max_seed_urls={resolved.limits.crawl.max_seed_urls}",
                details={"limit": resolved.limits.crawl.max_seed_urls, "path": "crawl.max_seed_urls"},
            )
        if payload.get("content_delivery") == "blob" and self.transit is None:
            raise ValidationFailed(
                "content_delivery=blob needs a blob store (JANE_WEB_COLLECTOR_TRANSIT_DIR)",
                errors=[FieldError(pointer="/content_delivery", message="no blob store configured")],
            )
        conn_id = (rules.get("fetch") or {}).get("connection_id")
        if conn_id:
            found = self.state.get_connection(conn_id)
            if found is None:
                raise ValidationFailed(
                    f"connection {conn_id} is not known to this collector",
                    errors=[
                        FieldError(pointer=f"{pointer}/fetch/connection_id", message="unknown connection")
                    ],
                )
            auth_headers(found[0])  # fail fast on unresolved secrets
        cid = f"job_{uuid.uuid4().hex}"
        state_key = payload.get("state_key") or payload.get("source_id") or cid
        if self.state.active_for_state_key(state_key):
            raise JaneError(
                f"state_key {state_key} is used by a running collection",
                code="conflict",
                details={"state_key": state_key},
            )
        self.state.create_collection(
            cid,
            state_key=state_key,
            status="queued",
            request=payload,
            rules=rules,
            rules_ref=rules_ref,
            created_at=_now(),
            effective_limits=to_contract(resolved.limits),
        )
        self.state.claim(cid, self.settings.instance_id, self.settings.lease_seconds)
        return await self._submit(cid, labels=payload.get("labels"))

    async def _submit(self, cid: str, labels: Mapping[str, str] | None = None) -> Job:
        self.local.add(cid)

        async def work(ctx: JobContext) -> dict[str, Any]:
            me = self.settings.instance_id
            record = self.state.get_collection(cid)
            if record is None:
                raise JaneError(f"collection {cid} disappeared")
            try:
                with self.state.tx((cid, me)) as db:
                    self.state.set_status(cid, "running", db=db)
                run = CrawlRun(self.deps, record)
                # the run marks the collection succeeded itself, in its last lease-fenced transaction
                return await run.execute(ctx)
            except LeaseLost:
                # another instance holds the lease now; this run wrote nothing after losing it, and the job
                # store ignores this instance's job updates for a collection it does not own
                log.warning("lease lost, another instance continues", extra={"collection_id": cid})
                return {"collection_id": cid, "handed_over": True}
            except (asyncio.CancelledError, JobCancelledError):
                if self.shutting_down:  # graceful stop: stays resumable
                    self.state.release(cid, me)
                else:
                    self.state.set_status_if_owner(cid, me, "cancelled", finished_at=_now())
                raise
            except BaseException:
                self.state.set_status_if_owner(cid, me, "failed", finished_at=_now())
                raise
            finally:
                self.local.discard(cid)

        return await self.runner.submit("collection", work, job_id=cid, labels=labels)

    def collection_view(self, cid: str) -> dict[str, Any]:
        record = self.state.get_collection(cid)
        if record is None:
            raise NotFound(f"collection {cid} not found")
        stats = {**new_stats(), **(record.get("stats") or {})}
        counts = self.state.frontier_counts(cid)
        stats["frontier_size"] = counts.get("pending", 0) + counts.get("inflight", 0)
        stats["unacked"] = self.state.unacked_count(cid)
        stats["acknowledged"] = max(0, self.state.emitted_count(cid) - stats["unacked"])
        request = record.get("request") or {}
        view: dict[str, Any] = {
            "collection_id": cid,
            "status": self._status(cid, record),
            "paused_by_backpressure": bool(record.get("paused")),
            "source_kind": "web",
            "mode": request.get("mode", "full"),
            "state_key": record["state_key"],
            "created_at": record["created_at"],
            "stats": stats,
        }
        if request.get("source_id"):
            view["source_id"] = request["source_id"]
        if record.get("rules_ref"):
            view["rules"] = record["rules_ref"]
        if record.get("finished_at"):
            view["finished_at"] = record["finished_at"]
        if record.get("effective_limits"):
            view["effective_limits"] = record["effective_limits"]
        return view

    def _status(self, cid: str, record: Mapping[str, Any]) -> str:
        """The collection's own status is the source of truth for "finished"; the job adds only
        ``queued``/``running``/``cancelling`` detail while the collection is not terminal."""
        own = str(record["status"])
        if own in TERMINAL:
            return own
        job = self.state.get_job(cid)
        if job is not None:
            status = Job.model_validate_json(job).status.value
            if status not in TERMINAL:
                return status
        return own

    def acked(self, cid: str) -> None:
        event = self.deps.ack_events.get(cid)
        if event is not None:
            event.set()

    # ------------------------------------------------------------------ one-shot fetch
    async def fetch_one(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._schema_errors("FetchRequest", payload)
        self._web_only(payload)
        if not payload.get("url"):
            raise ValidationFailed(
                "url is required for web", errors=[FieldError(pointer="/url", message="required")]
            )
        rules: dict[str, Any] = {}
        rules_ref = None
        if payload.get("rules") is not None or payload.get("rules_ref") is not None:
            rules, rules_ref, pointer = await self._rules_for(payload)
            self._check_rules(rules, pointer)
        resolved = self.resolve(rules.get("limits"), payload.get("limits"))
        limits = resolved.limits
        normalizer = Normalizer.from_rules(rules)
        canonical = normalizer.normalize(payload["url"])
        if canonical is None:
            raise ValidationFailed(
                "url must be http(s)", errors=[FieldError(pointer="/url", message="not http(s)")]
            )
        scope = Scope.from_rules(rules)
        if scope is not None and (reason := scope.check(canonical)):
            raise JaneError(f"{canonical}: {reason}", code="out_of_scope")
        robots_cfg = rules.get("robots") or {}
        fetch_cfg = rules.get("fetch") or {}
        user_agent = fetch_cfg.get("user_agent") or self.settings.user_agent
        token = robots_cfg.get("user_agent_token") or user_agent.split("/", 1)[0].split()[0]
        headers = dict(fetch_cfg.get("headers") or {})
        creds: dict[str, str] = {}
        if fetch_cfg.get("connection_id"):
            found = self.state.get_connection(fetch_cfg["connection_id"])
            if found is None:
                raise ValidationFailed(
                    "unknown connection",
                    errors=[FieldError(pointer="/rules/fetch/connection_id", message="unknown")],
                )
            creds = auth_headers(found[0])
        base_fetcher = Fetcher(
            self.client, limits, self._fetch_limiter, user_agent=user_agent, headers=headers
        )

        async def fetch_robots(url: str) -> tuple[int, str] | None:
            try:
                res = await base_fetcher.get(url, max_bytes=limits.collector.robots_max_bytes)
            except FetchError:
                return None
            return res.status, res.body.decode("utf-8", errors="replace")

        owner_policy = robots_cfg.get("mode") == "owner_policy"
        robots = RobotsCache(fetch_robots, token, limits.collector.robots_cache_ttl_seconds)

        async def check(url: str) -> None:
            target = normalizer.normalize(url)
            if target is None or (scope is not None and scope.check(target)):
                raise JaneError(f"redirect to {url} leaves the scope", code="out_of_scope")
            if not owner_policy and not await robots.allowed(target):
                raise Forbidden(
                    f"disallowed by robots.txt for user-agent {token}", code="access_denied_by_policy"
                )

        await check(canonical)

        async def crawl_delay(url: str) -> float | None:
            return None if owner_policy else (await robots.rules_for(url)).crawl_delay

        fetcher = Fetcher(
            self.client,
            limits,
            self._fetch_limiter,
            user_agent=user_agent,
            headers=headers,
            auth_headers=creds,
            crawl_delay_for=crawl_delay,
        )
        try:
            result = await fetcher.get(canonical, check_hop=check)
        except FetchError as exc:
            raise JaneError(
                exc.message,
                code=exc.code if exc.code in {"rate_limited", "limit_exceeded"} else "source_unavailable",
                details={
                    k: v for k, v in {"http_status": exc.http_status, "attempts": exc.attempts}.items() if v
                },
                retry_after_seconds=exc.retry_after_seconds,
            ) from exc
        if result.status >= 400:
            raise JaneError(
                f"source returned HTTP {result.status}",
                code="source_unavailable",
                details={"http_status": result.status},
            )
        delivery = Delivery(
            mode=payload.get("content_delivery", "auto"),
            inline_max_bytes=limits.transfer.inline_max_bytes,
            transit_ttl_seconds=limits.transfer.transit_ttl_seconds,
            store=self.transit,
        )
        doc = parse_html(result.body) if is_html(result.media_type) else None
        try:
            return build_material(
                result,
                canonical_url=normalizer.normalize(result.final_url) or canonical,
                observation_id=new_observation_id(),
                source_id=payload.get("source_id"),
                delivery=delivery,
                collector_version=__version__,
                rules_ref=rules_ref,
                html_meta=html_meta(doc) if doc is not None else None,
            )
        except MaterialTooLarge as exc:
            raise LimitExceeded(str(exc), details={"path": "transfer.inline_max_bytes"}) from exc

    def capabilities(self) -> dict[str, Any]:
        return {
            "source_kinds": ["web"],
            "strategies": list(self.registry.types()),
            "unsupported_strategies": sorted(RESERVED_TYPES),
            "content_delivery": ["auto", "inline", "blob"] if self.transit else ["auto", "inline"],
            "rules_sources": self.rules_loader.sources(),
            "connection_kinds": ["http"],
            "robots_policies": ["respect", "owner_policy"],
            **(
                {"strategy_load_errors": list(self.registry.load_errors)} if self.registry.load_errors else {}
            ),
        }
