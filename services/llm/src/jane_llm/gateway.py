"""LLM gateway core: model resolution, prompt assembly, budgets and rates, provider call, schema validation.

Budget semantics (``llm.v1``: platform -> source -> task):

* the platform budget is the stored ``BudgetDefinition`` ``platform/platform`` or, if none, the configured
  ``limits.llm.budget``; source and task budgets exist only when defined (``PUT /v1/budgets``);
  ``limits.llm.budget`` of a request narrows the most specific scope of the request (``min`` with a stored one);
* every applicable budget is checked before **each** provider call with a worst-case reservation
  (estimated input tokens + ``max_output_tokens`` at the model's price): the call happens only if
  ``spent + reserved + estimate <= limit`` for every budget, atomically in the shared store; after the
  call the reservation is replaced by the actual cost. So concurrent requests on any number of instances
  never overspend a budget, and an exhausted budget stops calls (429 ``budget_exhausted``, no provider call);
* ``max_requests_per_minute`` is enforced per scope (platform, source, task and provider) the same way.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from jane_kit.config import LimitLayer, ResolvedLimits
from jane_kit.errors import (
    JaneError,
    LimitExceeded,
    NotFound,
    RateLimited,
    UpstreamUnavailable,
    ValidationFailed,
)
from jane_llm.connections import resolve_connection
from jane_llm.models import Budget, BudgetDefinition, CompletionRequest, LlmLimitsIn, ModelInfo, Provider
from jane_llm.prompt import DataBlock, NonceFactory, build_prompt, new_nonce, retry_hint
from jane_llm.providers import ADAPTERS, ProviderAdapter, ProviderError, ProviderRequest, ResolvedConnection
from jane_llm.settings import ServiceLimits, Settings, resolve_service_limits
from jane_llm.store import (
    BudgetCheck,
    BudgetExceeded,
    CounterKey,
    RateCheck,
    RateExceeded,
    Store,
    UsageRecord,
)

log = logging.getLogger(__name__)


class BudgetExhausted(JaneError):
    code = "budget_exhausted"


def budget_key(scope_type: str, scope_id: str) -> str:
    return f"{scope_type}:{scope_id}"


def window(period: str, now: datetime, run_id: str | None) -> tuple[str, datetime | None] | None:
    """Counter window of a budget period and when it resets (``None`` for ``total`` and ``run``)."""
    now = now.astimezone(UTC)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "day":
        return f"day:{now:%Y-%m-%d}", midnight + timedelta(days=1)
    if period == "week":
        iso = now.isocalendar()
        return f"week:{iso.year}-W{iso.week:02d}", midnight + timedelta(days=7 - now.weekday())
    if period == "month":
        nxt = (midnight.replace(day=1) + timedelta(days=32)).replace(day=1)
        return f"month:{now:%Y-%m}", nxt
    if period == "total":
        return "total", None
    if period == "run":
        return (f"run:{run_id}", None) if run_id else None
    raise ValueError(f"unknown budget period {period!r}")


@dataclass(frozen=True)
class Scope:
    source_id: str | None
    task_id: str | None
    run_id: str | None
    purpose: str

    def levels(self) -> list[tuple[str, str]]:
        out = [("platform", "platform")]
        if self.source_id:
            out.append(("source", self.source_id))
        if self.task_id:
            out.append(("task", self.task_id))
        return out


@dataclass(frozen=True)
class ResolvedModel:
    provider: Provider
    model: ModelInfo
    adapter: ProviderAdapter
    connection: ResolvedConnection | None


def _strip_fences(text: str) -> str:
    m = re.match(r"^\s*```(?:json)?\s*\n(.*?)\n\s*```\s*$", text, re.DOTALL)
    return m.group(1) if m else text


def validate_output(
    schema: dict[str, Any], text: str
) -> tuple[Any, list[dict[str, str]], list[tuple[str, str]]]:
    """Parse and validate model output.

    Returns ``(output, errors for the caller, hints)``. Errors for the caller carry instance pointers; the
    hints for a schema retry go to the trusted channel, so they are built **only from the schema**
    (``schema_path`` and the violated keyword) — instance paths may contain keys chosen by the model or
    the data (``additionalProperties``, ``patternProperties``) and must never reach the system prompt.
    """
    try:
        output = json.loads(_strip_fences(text))
    except json.JSONDecodeError as exc:
        return None, [{"pointer": "", "message": f"output is not valid JSON: {exc.msg}"}], [("", "json")]
    errors = sorted(Draft202012Validator(schema).iter_errors(output), key=lambda e: list(e.absolute_path))
    pointer = ["/" + "/".join(str(p) for p in e.absolute_path) if e.absolute_path else "" for e in errors]
    report = [{"pointer": p, "message": e.message[:500]} for p, e in zip(pointer, errors, strict=True)]
    hints = [
        ("#/" + "/".join(str(seg) for seg in list(e.schema_path)[:-1]), str(e.validator)) for e in errors
    ]
    return output, report, hints


class Gateway:
    def __init__(
        self,
        store: Store,
        settings: Settings,
        limits: ResolvedLimits[ServiceLimits],
        *,
        adapters: dict[str, ProviderAdapter] | None = None,
        nonce_factory: NonceFactory = new_nonce,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        metrics: Any = None,
    ) -> None:
        self.store = store
        self.settings = settings
        self.resolved = limits
        self.adapters = adapters or ADAPTERS
        self.nonce_factory = nonce_factory
        self.clock = clock
        self.metrics = metrics

    @property
    def limits(self) -> ServiceLimits:
        return self.resolved.limits

    # ------------------------------------------------------------------ helpers
    async def _call(self, fn: Callable[..., Any], *args: Any) -> Any:
        return await asyncio.to_thread(fn, *args)

    async def resolve_model(self, name: str | None) -> ResolvedModel:
        name = name or "default"
        if "/" in name:
            provider_id, model_id = name.split("/", 1)
        else:
            alias = await self._call(self.store.get_doc, "alias", name)
            if alias is None:
                raise NotFound(f"model alias {name!r} is not configured")
            provider_id, model_id = alias["provider_id"], alias["model_id"]
        doc = await self._call(self.store.get_doc, "provider", provider_id)
        if doc is None:
            raise NotFound(f"provider {provider_id!r} is not configured")
        provider = Provider.model_validate(doc)
        if not provider.enabled:
            raise ValidationFailed(f"provider {provider_id!r} is disabled")
        model = provider.model(model_id)
        if model is None:
            raise NotFound(f"model {model_id!r} is not configured for provider {provider_id!r}")
        adapter = self.adapters.get(provider.kind)
        if adapter is None:
            raise ValidationFailed(f"provider kind {provider.kind!r} is not supported by this service")
        connection = None
        if provider.connection_id:
            cdoc = await self._call(self.store.get_doc, "connection", provider.connection_id)
            if cdoc is None:
                raise ValidationFailed(
                    f"connection {provider.connection_id!r} of provider {provider_id!r} is unknown"
                )
            connection, _ = resolve_connection(cdoc, self.settings.connection_policy())
            if err := self.settings.connection_policy().api_base_error(connection.params.get("api_base")):
                raise ValidationFailed(f"connection {provider.connection_id!r}: {err}")
        return ResolvedModel(provider, model, adapter, connection)

    async def budget_definitions(self, scope: Scope) -> list[tuple[str, str, BudgetDefinition | None]]:
        out = []
        for st, sid in scope.levels():
            doc = await self._call(self.store.get_doc, "budget", budget_key(st, sid))
            out.append((st, sid, BudgetDefinition.model_validate(doc) if doc else None))
        return out

    def _plan(
        self,
        scope: Scope,
        defs: list[tuple[str, str, BudgetDefinition | None]],
        request_limits: LlmLimitsIn | None,
        provider: Provider,
        now: datetime,
    ) -> tuple[list[BudgetCheck], list[RateCheck]]:
        budgets: dict[tuple[str, str], Budget] = {}
        rates: dict[tuple[str, str], int] = {}
        for st, sid, d in defs:
            if d and d.budget:
                budgets[(st, sid)] = d.budget
            if d and d.max_requests_per_minute:
                rates[(st, sid)] = d.max_requests_per_minute
        platform = self.limits.llm
        budgets.setdefault(
            ("platform", "platform"),
            Budget(
                amount=platform.budget.amount,
                currency=platform.budget.currency,
                period=platform.budget.period,
            ),
        )
        rates.setdefault(("platform", "platform"), platform.max_requests_per_minute)
        st, sid = scope.levels()[-1]
        if request_limits and request_limits.budget:
            rb, current = request_limits.budget, budgets.get((st, sid))
            same = current and current.currency == rb.currency and current.period == rb.period
            budgets[(st, sid)] = rb if not current or not same or rb.amount < current.amount else current
        if request_limits and request_limits.max_requests_per_minute:
            rates[(st, sid)] = min(rates.get((st, sid), 10**9), request_limits.max_requests_per_minute)
        if provider.limits and provider.limits.max_requests_per_minute:
            rates[("provider", provider.provider_id)] = provider.limits.max_requests_per_minute

        checks = []
        for (bst, bsid), b in budgets.items():
            w = window(b.period, now, scope.run_id)
            if w is None:
                log.warning("budget with period=run skipped: request has no run_id", extra={"scope": bst})
                continue
            checks.append(
                BudgetCheck(
                    CounterKey(bst, bsid, f"{b.currency}:{w[0]}"), b.amount, b.currency, b.period, w[1]
                )
            )
        minute = f"rpm:{now:%Y%m%d%H%M}"
        rate_checks = [
            RateCheck(CounterKey(rst, rsid, minute), limit, max(1, 60 - now.second))
            for (rst, rsid), limit in rates.items()
        ]
        return checks, rate_checks

    async def budget_status(self, checks: list[BudgetCheck]) -> list[dict[str, Any]]:
        out = []
        for c in checks:
            if c.key.scope_type not in {"platform", "source", "task"}:
                continue
            spent, _ = await self._call(self.store.counter, c.key)
            status: dict[str, Any] = {
                "scope_type": c.key.scope_type,
                "scope_id": c.key.scope_id,
                "spent": {"amount": round(spent, 10), "currency": c.currency},
                "limit": {"amount": c.limit, "currency": c.currency, "period": c.period},
                "exhausted": spent >= c.limit,
            }
            if c.resets_at:
                status["resets_at"] = c.resets_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            out.append(status)
        return out

    def effective_limits(self, request_limits: LlmLimitsIn | None) -> ServiceLimits:
        """Request limits over the platform ones, bounded by hard caps (budget and rpm handled separately)."""
        if not request_limits:
            return self.limits
        values = request_limits.model_dump(
            exclude_none=True, include={"max_input_tokens_per_request", "max_output_tokens_per_request"}
        )
        if not values:
            return self.limits
        return resolve_service_limits(self.settings, LimitLayer("request", {"llm": values})).limits

    # ------------------------------------------------------------------ completion
    async def complete(
        self, req: CompletionRequest, *, extra_data: list[DataBlock] | None = None
    ) -> dict[str, Any]:
        started = self.clock()
        if req.output_schema is not None:
            try:
                Draft202012Validator.check_schema(req.output_schema)
            except SchemaError as exc:
                raise ValidationFailed(f"output_schema is not a valid JSON Schema: {exc.message}") from exc
        limits = self.effective_limits(req.limits)
        gw = limits.gateway
        rm = await self.resolve_model(req.model)
        pricing = rm.model.pricing
        if pricing is None:
            raise ValidationFailed(
                f"model {rm.provider.provider_id}/{rm.model.model_id} has no pricing; budgets cannot be enforced"
            )
        scope = Scope(req.scope.source_id, req.scope.task_id, req.scope.run_id, req.scope.purpose)
        test_mode = bool(req.test_mode)

        blocks = [
            DataBlock(p.name, p.media_type, p.text if p.text is not None else json.dumps(p.content or {}))
            for p in req.data
        ] + list(extra_data or [])
        structured = req.output_schema is not None
        prompt = build_prompt(
            req.instructions, blocks, structured=structured, nonce_factory=self.nonce_factory
        )
        max_out = min(
            req.max_output_tokens or gw.default_max_output_tokens, limits.llm.max_output_tokens_per_request
        )
        retries = min(
            req.max_schema_retries if req.max_schema_retries is not None else gw.max_schema_retries,
            gw.max_schema_retries,
        )
        completion_id = f"cmp_{uuid.uuid4().hex}"
        system = prompt.system
        total_in = total_out = 0
        total_cost = 0.0
        output: Any = None
        text = ""
        report: list[dict[str, str]] = []
        finish = "stop"
        valid = False
        checks: list[BudgetCheck] = []

        for attempt in range(retries + 1):
            est_in = math.ceil((len(system) + len(prompt.user)) / gw.chars_per_token_estimate)
            if est_in > limits.llm.max_input_tokens_per_request:
                raise LimitExceeded(
                    f"estimated input tokens {est_in} exceed llm.max_input_tokens_per_request="
                    f"{limits.llm.max_input_tokens_per_request}",
                    details={
                        "path": "llm.max_input_tokens_per_request",
                        "limit": limits.llm.max_input_tokens_per_request,
                    },
                )
            if rm.model.max_context_tokens and est_in + max_out > rm.model.max_context_tokens:
                raise LimitExceeded(
                    f"estimated prompt ({est_in}) + max_output_tokens ({max_out}) exceed the model context "
                    f"({rm.model.max_context_tokens})"
                )
            estimate = (est_in * pricing.input_per_mtok + max_out * pricing.output_per_mtok) / 1_000_000
            now = self.clock()
            defs = await self.budget_definitions(scope)
            checks, rate_checks = self._plan(scope, defs, req.limits, rm.provider, now)
            mismatched = [c for c in checks if c.currency != pricing.currency]
            if mismatched:
                raise ValidationFailed(
                    f"budget currency {mismatched[0].currency} differs from model pricing currency {pricing.currency}"
                )
            reservation = f"res_{uuid.uuid4().hex}"
            try:
                await self._call(
                    self.store.reserve,
                    reservation,
                    estimate,
                    checks,
                    rate_checks,
                    now,
                    timedelta(seconds=gw.reservation_ttl_seconds),
                )
            except BudgetExceeded as exc:
                self._count("budget_rejections_total", scope_type=exc.check.key.scope_type)
                if attempt > 0:
                    report.append({"pointer": "", "message": "schema retries stopped: budget exhausted"})
                    break
                raise self._budget_error(exc, now) from exc
            except RateExceeded as exc:
                if attempt > 0:
                    report.append({"pointer": "", "message": "schema retries stopped: rate limit"})
                    break
                raise RateLimited(
                    f"max_requests_per_minute reached for {exc.check.key.scope_type}/{exc.check.key.scope_id}",
                    retry_after_seconds=exc.check.retry_after_seconds,
                    details={"scope_type": exc.check.key.scope_type, "scope_id": exc.check.key.scope_id},
                ) from exc
            preq = ProviderRequest(
                model_id=rm.model.model_id,
                system=system,
                user=prompt.user,
                max_output_tokens=max_out,
                output_schema=req.output_schema,
                temperature=req.temperature,
                structured_output=bool(rm.model.supports_structured_output),
            )
            try:
                resp = await rm.adapter.complete(preq, rm.connection, limits)
            except ProviderError as exc:
                await self._call(self.store.release, reservation)
                self._count(
                    "requests_total",
                    provider=rm.provider.provider_id,
                    model=rm.model.model_id,
                    outcome="error",
                )
                raise UpstreamUnavailable(str(exc), retryable=exc.retryable) from exc
            except BaseException:
                await self._call(self.store.release, reservation)
                raise
            cost = (
                resp.input_tokens * pricing.input_per_mtok + resp.output_tokens * pricing.output_per_mtok
            ) / 1_000_000
            total_in += resp.input_tokens
            total_out += resp.output_tokens
            total_cost += cost
            text, finish = resp.text, resp.finish_reason
            if structured:
                assert req.output_schema is not None
                output, report, hints = validate_output(req.output_schema, text)
                valid = not report
            else:
                output, report, hints, valid = None, [], [], True
            await self._call(
                self.store.settle,
                reservation,
                cost,
                UsageRecord(
                    completion_id=completion_id,
                    created_at=now,
                    provider_id=rm.provider.provider_id,
                    model_id=rm.model.model_id,
                    purpose=scope.purpose,
                    source_id=scope.source_id,
                    task_id=scope.task_id,
                    run_id=scope.run_id,
                    input_tokens=resp.input_tokens,
                    output_tokens=resp.output_tokens,
                    cost=cost,
                    currency=pricing.currency,
                    test_mode=test_mode,
                    outcome="ok" if valid else "invalid_output",
                ),
            )
            self._count(
                "requests_total",
                provider=rm.provider.provider_id,
                model=rm.model.model_id,
                outcome="ok" if valid else "invalid_output",
            )
            if valid:
                break
            system = prompt.system + retry_hint(hints)

        result: dict[str, Any] = {
            "completion_id": completion_id,
            "model": {"provider_id": rm.provider.provider_id, "model_id": rm.model.model_id},
            "valid": valid,
            "validation_errors": report,
            "finish_reason": finish,
            "usage": {
                "input_tokens": total_in,
                "output_tokens": total_out,
                "cost": {"amount": round(total_cost, 10), "currency": pricing.currency},
            },
            "budget": await self.budget_status(checks),
        }
        if structured and output is not None and valid:
            result["output"] = output
        else:
            result["output_text"] = text
        log.info(
            "completion",
            extra={
                "completion_id": completion_id,
                "provider": rm.provider.provider_id,
                "model": rm.model.model_id,
                "purpose": scope.purpose,
                "valid": valid,
                "input_tokens": total_in,
                "output_tokens": total_out,
                "cost": total_cost,
                "test_mode": test_mode,
                "duration_ms": int((self.clock() - started).total_seconds() * 1000),
            },
        )
        return result

    def _budget_error(self, exc: BudgetExceeded, now: datetime) -> BudgetExhausted:
        c = exc.check
        details: dict[str, Any] = {
            "scope_type": c.key.scope_type,
            "scope_id": c.key.scope_id,
            "period": c.period,
            "spent": {"amount": round(exc.spent, 10), "currency": c.currency},
            "limit": {"amount": c.limit, "currency": c.currency, "period": c.period},
            "requested_estimate": {"amount": round(exc.requested, 10), "currency": c.currency},
        }
        retry_after = None
        if c.resets_at:
            details["period_resets_at"] = c.resets_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            retry_after = max(1, int((c.resets_at - now).total_seconds()))
        return BudgetExhausted(
            f"LLM budget of {c.key.scope_type} {c.key.scope_id!r} is exhausted "
            f"(spent {exc.spent:.6f} + reserved {exc.reserved:.6f} + estimate {exc.requested:.6f} > {c.limit} {c.currency})",
            title="LLM budget exhausted",
            details=details,
            retry_after_seconds=retry_after,
        )

    def _count(self, name: str, **labels: str) -> None:
        if self.metrics is not None:
            counter = self.metrics.get(name)
            if counter is not None:
                counter.labels(**labels).inc()
