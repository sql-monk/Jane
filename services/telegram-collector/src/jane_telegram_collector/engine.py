"""Service core: collections (start, resume after restart or takeover, cancellation), one-shot fetch, housekeeping."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from jane_kit.config import LimitError, LimitLayer, ResolvedLimits, resolve_limits
from jane_kit.errors import FieldError, JaneError, NotFound, ValidationFailed
from jane_kit.jobs import Job, JobCancelledError, JobContext, JobRunner, JobStatus

from . import __version__
from .client import (
    AccountUnauthorized,
    ChannelUnavailable,
    ClientFactory,
    ClientUnavailable,
    FloodWait,
    ResolvedAccount,
)
from .collector import LeaseLost, RunDeps, TelegramRun, new_stats
from .connections import resolve_account
from .materials import (
    ContentTooLarge,
    Delivery,
    TransitStore,
    build_material,
    material_id,
    message_sha,
    new_observation_id,
    revision_sequence,
    rfc3339,
)
from .rules import ContractSchemas, RulesLoader, validate_rules
from .settings import ServiceLimits, Settings, contract_layer, platform_layers, to_contract
from .state import StateStore

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
        factory: ClientFactory,
        schemas: ContractSchemas,
        runner: JobRunner,
    ) -> None:
        self.settings = settings
        self.base = base_limits
        self.limits = base_limits.limits
        self.state = state
        self.factory = factory
        self.schemas = schemas
        self.runner = runner
        self.platform = platform_layers(settings)
        self.transit = TransitStore(settings.transit_dir) if settings.transit_dir else None
        self.policy = settings.connection_policy()
        self.rules_loader = RulesLoader(
            rules_dir=settings.rules_dir,
            registry_url=settings.registry_url,
            registry_token_env=settings.registry_token_env,
            timeout_s=self.limits.timeouts.request_timeout_ms / 1000,
        )
        self.deps = RunDeps(
            state=state,
            factory=factory,
            resolve=self.resolve,
            transit=self.transit,
            instance_id=settings.instance_id,
            lease_seconds=settings.lease_seconds,
            heartbeat_seconds=settings.heartbeat_interval_ms / 1000,
            version=__version__,
        )
        self.local: set[str] = set()
        self.shutting_down = False
        self._tasks: list[asyncio.Task[None]] = []

    # ------------------------------------------------------------------ limits
    def resolve(
        self, source: Mapping[str, Any] | None = None, request: Mapping[str, Any] | None = None
    ) -> ResolvedLimits[ServiceLimits]:
        layers = []
        if source:
            layers.append(LimitLayer("source", source, name="rules"))
        if request:
            layers.append(LimitLayer("request", request, name="request"))
        try:
            return resolve_limits(ServiceLimits, *self.platform, *(contract_layer(la) for la in layers))
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

    async def _resume_loop(self) -> None:
        # an expired lease is taken over at most one heartbeat interval later (JANE_TELEGRAM_COLLECTOR_HEARTBEAT_INTERVAL_MS)
        interval = self.settings.heartbeat_interval_ms / 1000
        while True:
            try:
                await self.resume_pending()
            except Exception:
                log.exception("resume loop failed")
            await asyncio.sleep(interval)

    async def resume_pending(self) -> list[str]:
        """Take over non-terminal collections whose lease expired (after a crash/kill) and continue them."""
        resumed = []
        me = self.settings.instance_id
        for cid in self.state.resumable(me):
            if cid in self.local or not self.state.claim(cid, me, self.settings.lease_seconds):
                continue
            job = self.state.get_job(cid)
            if job is not None and Job.model_validate_json(job).status == JobStatus.CANCELLING:
                if self.state.finish_if_owner(cid, me, "cancelled", _now()):
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

    def _telegram_only(self, payload: Mapping[str, Any]) -> None:
        if payload.get("source_kind") != "telegram":
            raise ValidationFailed(
                "telegram-collector collects only source_kind=telegram",
                errors=[FieldError(pointer="/source_kind", message="expected telegram")],
            )

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
        report = validate_rules(self.schemas, rules)
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
            ]
            raise ValidationFailed("collector rules are not telegram rules", errors=errors)

    def account(self, rules: Mapping[str, Any], pointer: str) -> ResolvedAccount:
        """The ``telegram_account`` connection named by the rules (or the configured default), secrets resolved."""
        conn_id = rules.get("account_connection_id") or self.settings.default_account_connection_id
        where = f"{pointer}/account_connection_id"
        if not conn_id:
            if self.factory.requires_account():
                raise ValidationFailed(
                    f"the {self.factory.name} client needs a telegram_account connection",
                    errors=[
                        FieldError(
                            pointer=where,
                            message="required (or JANE_TELEGRAM_COLLECTOR_DEFAULT_ACCOUNT_CONNECTION_ID)",
                        )
                    ],
                )
            return ResolvedAccount(connection_id=None, params={})
        found = self.state.get_connection(str(conn_id))
        if found is None:
            raise ValidationFailed(
                f"connection {conn_id} is not known to this collector",
                errors=[FieldError(pointer=where, message="unknown connection (PUT /v1/connections/{id})")],
            )
        return resolve_account(found[0], where, self.policy)

    # ------------------------------------------------------------------ collections
    async def start_collection(self, payload: dict[str, Any]) -> Job:
        self._schema_errors("CollectionRequest", payload)
        self._telegram_only(payload)
        if payload.get("urls"):
            raise ValidationFailed(
                "urls are for web collections",
                errors=[FieldError(pointer="/urls", message="not used for telegram")],
            )
        rules, rules_ref, pointer = await self._rules_for(payload)
        self._check_rules(rules, pointer)
        resolved = self.resolve(rules.get("limits"), payload.get("limits"))
        if payload.get("content_delivery") == "blob" and self.transit is None:
            raise ValidationFailed(
                "content_delivery=blob needs a blob store (JANE_TELEGRAM_COLLECTOR_TRANSIT_DIR)",
                errors=[FieldError(pointer="/content_delivery", message="no blob store configured")],
            )
        self.account(rules, pointer)  # fail fast: unknown connection or unresolvable secrets
        cid = f"job_{uuid.uuid4().hex}"
        state_key = payload.get("state_key") or payload.get("source_id") or cid
        created = self.state.create_collection(
            cid,
            state_key=state_key,
            request=payload,
            rules=rules,
            rules_ref=rules_ref,
            created_at=_now(),
            effective_limits=to_contract(resolved.limits),
            owner=self.settings.instance_id,
            lease_seconds=self.settings.lease_seconds,
        )
        if not created:
            raise JaneError(
                f"state_key {state_key} is used by a running collection",
                code="conflict",
                details={"state_key": state_key},
            )
        return await self._submit(cid, labels=payload.get("labels"))

    async def _submit(self, cid: str, labels: Mapping[str, str] | None = None) -> Job:
        self.local.add(cid)

        async def work(ctx: JobContext) -> dict[str, Any]:
            me = self.settings.instance_id
            try:
                record = self.state.get_collection(cid)
                if record is None:
                    raise JaneError(f"collection {cid} disappeared")
                with self.state.tx((cid, me)) as db:
                    self.state.set_running(db, cid)
                pointer = (
                    "/rules_ref"
                    if record.get("rules_ref") and not record["request"].get("rules")
                    else "/rules"
                )
                run = TelegramRun(self.deps, record, self.account(record["rules"], pointer))
                # the run writes its terminal status itself, in its last lease-fenced transaction
                return await run.execute(ctx)
            except LeaseLost:
                # another instance holds the lease now; this run wrote nothing after losing it, and the job
                # store ignores this instance's job updates for a collection it does not own
                log.warning("lease lost, another instance continues", extra={"collection_id": cid})
                return {"collection_id": cid, "handed_over": True}
            except (asyncio.CancelledError, JobCancelledError) as exc:
                if self.shutting_down:  # graceful stop: stays resumable by this or another instance
                    self.state.release(cid, me)
                else:
                    job = self.state.get_job(cid)
                    requested = isinstance(exc, JobCancelledError) or (
                        job is not None and Job.model_validate_json(job).status == JobStatus.CANCELLING
                    )
                    # not requested: the runner's job_timeout_ms interrupted the run
                    self.state.finish_if_owner(cid, me, "cancelled" if requested else "failed", _now())
                raise
            except BaseException as exc:
                problem = exc.to_problem() if isinstance(exc, JaneError) else JaneError(str(exc)).to_problem()
                self.state.finish_if_owner(
                    cid, me, "failed", _now(), {"error": problem.model_dump(mode="json", exclude_none=True)}
                )
                raise
            finally:
                self.local.discard(cid)

        return await self.runner.submit("collection", work, job_id=cid, labels=labels)

    def collection_view(self, cid: str) -> dict[str, Any]:
        record = self.state.get_collection(cid)
        if record is None:
            raise NotFound(f"collection {cid} not found")
        stats = {**new_stats(), **(record.get("stats") or {})}
        stats["unacked"] = self.state.unacked_count(cid)
        stats["acknowledged"] = max(0, self.state.emitted_count(cid) - stats["unacked"])
        stats["frontier_size"] = 0
        request = record.get("request") or {}
        view: dict[str, Any] = {
            "collection_id": cid,
            "status": self._status(cid, record),
            "paused_by_backpressure": bool(record.get("paused")),
            "source_kind": "telegram",
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
        status = str(record["status"])
        if status in TERMINAL:
            return status
        job = self.state.get_job(cid)
        if job is not None and Job.model_validate_json(job).status == JobStatus.CANCELLING:
            return "cancelling"
        return status

    def acked(self, cid: str) -> None:
        event = self.deps.ack_events.get(cid)
        if event is not None:
            event.set()

    # ------------------------------------------------------------------ one-shot fetch
    async def fetch_one(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._schema_errors("FetchRequest", payload)
        self._telegram_only(payload)
        target = payload.get("telegram")
        if not target or not (target.get("channel_username") or target.get("channel_id")):
            raise ValidationFailed(
                "telegram.channel_username or telegram.channel_id and telegram.message_id are required",
                errors=[FieldError(pointer="/telegram", message="channel and message_id required")],
            )
        rules: dict[str, Any] = {}
        rules_ref = None
        pointer = "/rules"
        if payload.get("rules") is not None or payload.get("rules_ref") is not None:
            rules, rules_ref, pointer = await self._rules_for(payload)
            self._check_rules(rules, pointer)
        limits = self.resolve(rules.get("limits"), payload.get("limits")).limits
        if payload.get("content_delivery") == "blob" and self.transit is None:
            raise ValidationFailed(
                "content_delivery=blob needs a blob store (JANE_TELEGRAM_COLLECTOR_TRANSIT_DIR)",
                errors=[FieldError(pointer="/content_delivery", message="no blob store configured")],
            )
        account = self.account(rules, pointer)
        timeout = limits.timeouts.request_timeout_ms / 1000
        connect = limits.timeouts.connect_timeout_ms / 1000
        try:
            async with asyncio.timeout(connect):
                client = await self.factory.open(account, connect_timeout_s=connect)
            try:
                async with asyncio.timeout(timeout):
                    channel = await client.resolve(
                        username=target.get("channel_username"), channel_id=target.get("channel_id")
                    )
                async with asyncio.timeout(timeout):
                    msg = await client.get_message(channel, int(target["message_id"]))
            finally:
                await client.close()
        except FloodWait as exc:
            # a synchronous call never blocks on a flood-wait: the caller retries after Retry-After
            raise JaneError(
                f"Telegram asks to wait {exc.seconds}s",
                code="rate_limited",
                retry_after_seconds=exc.seconds,
                details={"retry_after_seconds": exc.seconds},
            ) from exc
        except ChannelUnavailable as exc:
            raise JaneError(
                str(exc),
                code="source_unavailable",
                retryable=False,
                details={"reason": "channel_unavailable"},
            ) from exc
        except AccountUnauthorized as exc:
            raise JaneError(
                f"telegram account: {exc}",
                code="source_unavailable",
                retryable=False,
                details={"reason": "account_unauthorized"},
            ) from exc
        except (ClientUnavailable, TimeoutError) as exc:
            raise JaneError(
                f"telegram unavailable: {exc!r}", code="source_unavailable", retryable=True
            ) from exc
        if msg is None:
            # the source says the material does not exist: 404 not_found (collector.v1, R04), not a source error
            raise JaneError(
                f"message {target['message_id']} not found in {channel.username or channel.channel_id}",
                code="not_found",
                details={"reason": "message_not_found"},
            )
        delivery = Delivery(
            mode=payload.get("content_delivery", "auto"),
            inline_max_bytes=limits.transfer.inline_max_bytes,
            transit_ttl_seconds=limits.transfer.transit_ttl_seconds,
            store=self.transit,
        )
        # the revision number from the revisions this collector already emitted (any state_key, nothing written):
        # the same text keeps its sequence, another text in the same second gets the next one (review 1, R04)
        seen = self.state.latest_seen(material_id(channel.channel_id, msg.message_id))
        try:
            return build_material(
                msg,
                channel,
                observation_id=new_observation_id(),
                delivery=delivery,
                collector_version=__version__,
                source_id=payload.get("source_id"),
                rules_ref=rules_ref,
                sequence=revision_sequence(msg, message_sha(msg), seen),
            )
        except ContentTooLarge as exc:
            raise JaneError(
                str(exc), code="limit_exceeded", details={"path": "transfer.inline_max_bytes"}
            ) from exc

    def capabilities(self) -> dict[str, Any]:
        return {
            "source_kinds": ["telegram"],
            "client_backend": self.factory.name,
            "strategies": ["telegram_history", "telegram_updates"],
            "modes": ["full", "incremental"],
            "content_delivery": ["auto", "inline", "blob"] if self.transit else ["auto", "inline"],
            "rules_sources": self.rules_loader.sources(),
            "connection_kinds": ["telegram_account"],
        }
