"""HTTP API of the LLM service: ``llm.v1`` (gateway) + ``handler.v1`` (LLM handler).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from fastapi import Body, FastAPI, Header, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from jane_kit.auth_scopes import HANDLER, LLM, merge
from jane_kit.errors import (
    Conflict,
    FieldError,
    JaneError,
    NotFound,
    ValidationFailed,
)
from jane_kit.idempotency import (
    IDEMPOTENCY_HEADER,
    REPLAY_HEADER,
    StoredResponse,
    fingerprint,
    idempotent,
    run_idempotent,
)
from jane_kit.jobs import JobContext, JobRunner, jobs_router
from jane_kit.pagination import PageLimits, clamp_limit, decode_cursor, encode_cursor
from jane_kit.service import create_app
from jane_llm import __version__
from jane_llm.connections import find_secret_like, resolve_connection
from jane_llm.gateway import Gateway, Scope, budget_key
from jane_llm.handler import LlmHandler
from jane_llm.models import BudgetDefinition, CompletionRequest, Connection, ModelAlias, Provider
from jane_llm.packages import PackageLoader
from jane_llm.prompt import NonceFactory, new_nonce
from jane_llm.providers import ADAPTERS, ProviderAdapter
from jane_llm.providers.fake import FAKE_MODEL_ID, FAKE_PROVIDER_ID
from jane_llm.settings import Settings, resolve_service_limits
from jane_llm.store import MemoryStore, PostgresStore, Store, StoreIdempotency, StoreJobs, UsageQuery
from jane_llm.testing import run_tests

log = logging.getLogger(__name__)

JSON_BODY = Body(...)
IF_MATCH = Header(default=None, alias="If-Match")
BUILTIN_PACKAGES = Path(__file__).resolve().parents[2] / "packages"

FAKE_PROVIDER = {
    "provider_id": FAKE_PROVIDER_ID,
    "kind": "fake",
    "enabled": True,
    "models": [
        {
            "model_id": FAKE_MODEL_ID,
            "max_context_tokens": 128_000,
            "supports_structured_output": True,
            "pricing": {"input_per_mtok": 0, "output_per_mtok": 0, "currency": "USD"},
        }
    ],
}


def make_store(settings: Settings) -> Store:
    if settings.store == "memory":
        log.warning(
            "store=memory: budgets and usage are per process; use store=postgres for several instances"
        )
        return MemoryStore()
    if not settings.database_url:
        raise RuntimeError(
            "JANE_LLM_DATABASE_URL is required for store=postgres (or set JANE_LLM_STORE=memory)"
        )
    return PostgresStore(
        settings.database_url,
        settings.db_schema,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
    )


def etag(doc: dict[str, Any]) -> str:
    return '"' + hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()[:32] + '"'


def _parse[M](model: type[M], body: Any) -> M:
    try:
        return model.model_validate(body)  # type: ignore[attr-defined,no-any-return]
    except ValidationError as exc:
        errors = [
            FieldError(pointer="/" + "/".join(str(p) for p in e["loc"]), code=e["type"], message=e["msg"])
            for e in exc.errors()
        ]
        raise ValidationFailed("request does not match the API contract", errors=errors) from exc


def seed(store: Store, settings: Settings) -> None:
    if settings.seed_file is not None:
        text = settings.seed_file.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        for c in data.get("connections") or []:
            conn = _parse(Connection, c)
            if bad := settings.connection_policy().violations(conn.model_dump(exclude_none=True)):
                raise RuntimeError(
                    f"seed connection {conn.connection_id}: {bad[0].pointer}: {bad[0].message}"
                )
            if leaks := find_secret_like(conn.params or {}):
                raise RuntimeError(
                    f"seed connection {conn.connection_id}: secret-like params {leaks[0].pointer}"
                )
            store.seed_doc("connection", conn.connection_id, conn.model_dump(exclude_none=True))
        for p in data.get("providers") or []:
            prov = _parse(Provider, p)
            store.seed_doc("provider", prov.provider_id, prov.model_dump(exclude_none=True))
        for a in data.get("model_aliases") or []:
            alias = _parse(ModelAlias, a)
            store.seed_doc("alias", alias.alias, alias.model_dump())
        for b in data.get("budgets") or []:
            bd = _parse(BudgetDefinition, b)
            store.seed_doc(
                "budget",
                budget_key(bd.scope_type, bd.scope_id),
                bd.model_dump(exclude_none=True, exclude={"status"}),
            )
    if settings.fake_provider_enabled:
        store.seed_doc("provider", FAKE_PROVIDER_ID, FAKE_PROVIDER)
        store.seed_doc(
            "alias",
            "default",
            {"alias": "default", "provider_id": FAKE_PROVIDER_ID, "model_id": FAKE_MODEL_ID},
        )


def build_app(
    settings: Settings | None = None,
    *,
    store: Store | None = None,
    adapters: dict[str, ProviderAdapter] | None = None,
    nonce_factory: NonceFactory = new_nonce,
    clock: Callable[[], datetime] | None = None,
) -> FastAPI:
    settings = settings or Settings()
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    store = store or make_store(settings)
    policy = settings.connection_policy()
    idem_store = StoreIdempotency(store)
    runner = JobRunner(store=StoreJobs(store), limits=limits.jobs)
    adapters = adapters or ADAPTERS
    packages_dir = settings.packages_dir or (BUILTIN_PACKAGES if BUILTIN_PACKAGES.is_dir() else None)
    loader = PackageLoader(
        packages_dir,
        settings.registry_url,
        limits.registry.client_limits(),
        settings.registry_token.get_secret_value() if settings.registry_token else None,
        limits=limits.gateway,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        await asyncio.to_thread(store.migrate)
        await asyncio.to_thread(seed, store, settings)
        log.info("configured limits", extra={"limits": resolved.effective(), "store": settings.store})
        yield
        await runner.shutdown()
        await asyncio.to_thread(store.close)

    def capabilities() -> dict[str, Any]:
        return {
            "handler_kinds": ["llm"],
            "provider_kinds": sorted(adapters),
            "connections": ["llm_provider"],
            "structured_output": True,
            "store": settings.store,
        }

    app = create_app(
        settings,
        title="Jane LLM Gateway",
        version=__version__,
        lifespan=lifespan,
        capabilities=capabilities,
        limits=resolved,
        auth_scopes=merge(HANDLER, LLM),  # ADR-0005 scopes per operation
    )
    metrics: dict[str, Any] = {}
    if settings.metrics_enabled:
        m = app.state.metrics
        metrics = {
            "requests_total": m.counter(
                "llm_requests_total", "Provider calls", ["provider", "model", "outcome"]
            ),
            "budget_rejections_total": m.counter(
                "llm_budget_rejections_total", "Calls stopped by budget", ["scope_type"]
            ),
        }
    gateway = Gateway(
        store,
        settings,
        resolved,
        adapters=adapters,
        nonce_factory=nonce_factory,
        metrics=metrics,
        **({"clock": clock} if clock else {}),
    )
    handler = LlmHandler(gateway, loader)
    app.state.limits = resolved
    app.state.store = store
    app.state.gateway = gateway
    app.include_router(jobs_router(runner))
    app.state.health.add("store", lambda: asyncio.to_thread(store.ping))

    async def call(fn: Callable[..., Any], *args: Any) -> Any:
        return await asyncio.to_thread(fn, *args)

    # ------------------------------------------------------------------ providers
    @app.get("/v1/providers", tags=["providers"])
    async def list_providers() -> dict[str, Any]:
        return {"items": await call(store.list_docs, "provider")}

    @app.get("/v1/providers/{provider_id}", tags=["providers"])
    async def get_provider(provider_id: str) -> Response:
        doc = await call(store.get_doc, "provider", provider_id)
        if doc is None:
            raise NotFound(f"provider {provider_id} not found")
        return JSONResponse(doc, headers={"ETag": etag(doc)})

    @app.put("/v1/providers/{provider_id}", tags=["providers"])
    async def put_provider(
        provider_id: str,
        body: Any = JSON_BODY,
        if_match: str | None = IF_MATCH,
    ) -> Response:
        prov = _parse(Provider, body)
        if prov.provider_id != provider_id:
            raise ValidationFailed("provider_id in the body differs from the path")
        if prov.kind not in adapters:
            raise ValidationFailed(f"provider kind {prov.kind!r} is not supported (have {sorted(adapters)})")
        await _check_if_match("provider", provider_id, if_match)
        if prov.connection_id and await call(store.get_doc, "connection", prov.connection_id) is None:
            raise ValidationFailed(f"connection {prov.connection_id!r} is unknown; PUT /v1/connections first")
        doc = prov.model_dump(exclude_none=True)
        await call(store.put_doc, "provider", provider_id, doc)
        return JSONResponse(doc, headers={"ETag": etag(doc)})

    @app.delete("/v1/providers/{provider_id}", status_code=204, tags=["providers"])
    async def delete_provider(provider_id: str) -> Response:
        aliases = [
            a["alias"] for a in await call(store.list_docs, "alias") if a["provider_id"] == provider_id
        ]
        if aliases:
            raise Conflict(f"provider {provider_id} is used by model aliases {aliases}")
        await call(store.delete_doc, "provider", provider_id)
        return Response(status_code=204)

    async def _check_if_match(kind: Any, key: str, if_match: str | None) -> None:
        if if_match is None:
            return
        current = await call(store.get_doc, kind, key)
        if current is None or etag(current) != if_match:
            raise JaneError("the resource was changed (ETag mismatch)", code="precondition_failed")

    # ------------------------------------------------------------------ aliases
    @app.get("/v1/model-aliases", tags=["providers"])
    async def list_aliases() -> dict[str, Any]:
        return {"items": await call(store.list_docs, "alias")}

    @app.put("/v1/model-aliases/{alias}", tags=["providers"])
    async def put_alias(alias: str, body: Any = JSON_BODY) -> dict[str, Any]:
        a = _parse(ModelAlias, body)
        if a.alias != alias:
            raise ValidationFailed("alias in the body differs from the path")
        pdoc = await call(store.get_doc, "provider", a.provider_id)
        if pdoc is None or Provider.model_validate(pdoc).model(a.model_id) is None:
            raise ValidationFailed(f"model {a.provider_id}/{a.model_id} is not configured")
        await call(store.put_doc, "alias", alias, a.model_dump())
        return a.model_dump()

    # ------------------------------------------------------------------ completions
    @app.post("/v1/completions", tags=["completions"], response_model=None)
    async def create_completion(request: Request, body: Any = JSON_BODY) -> Response:
        req = _parse(CompletionRequest, body)

        async def run() -> StoredResponse:
            if req.mode == "async":

                async def work(ctx: JobContext) -> dict[str, Any]:
                    return await gateway.complete(req)

                job = await runner.submit(
                    "llm_completion", work, idempotency_key=request.headers.get(IDEMPOTENCY_HEADER)
                )
                return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})
            return StoredResponse(200, await gateway.complete(req))

        return await idempotent(request, idem_store, run, limits=limits.idempotency)

    # ------------------------------------------------------------------ budgets & usage
    async def _with_status(bd: BudgetDefinition) -> dict[str, Any]:
        doc = bd.model_dump(exclude_none=True, exclude={"status"})
        scope = Scope(
            bd.scope_id if bd.scope_type == "source" else None,
            bd.scope_id if bd.scope_type == "task" else None,
            None,
            "other",
        )
        defs: list[tuple[str, str, BudgetDefinition | None]] = [(bd.scope_type, bd.scope_id, bd)]
        checks, _ = gateway._plan(
            scope,
            defs,
            None,
            Provider(provider_id="x", kind="fake", enabled=True, models=[]),
            datetime.now(UTC),
        )
        statuses = [
            s
            for s in await gateway.budget_status(checks)
            if s["scope_type"] == bd.scope_type and s["scope_id"] == bd.scope_id
        ]
        if statuses:
            doc["status"] = statuses[0]
        return doc

    @app.get("/v1/budgets", tags=["budgets"])
    async def list_budgets() -> dict[str, Any]:
        docs = {(d["scope_type"], d["scope_id"]): d for d in await call(store.list_docs, "budget")}
        if ("platform", "platform") not in docs:
            b = limits.llm.budget
            docs[("platform", "platform")] = {
                "scope_type": "platform",
                "scope_id": "platform",
                "budget": {"amount": b.amount, "currency": b.currency, "period": b.period},
                "max_requests_per_minute": limits.llm.max_requests_per_minute,
            }
        items = [await _with_status(BudgetDefinition.model_validate(d)) for _, d in sorted(docs.items())]
        return {"items": items}

    @app.put("/v1/budgets/{scope_type}/{scope_id}", tags=["budgets"])
    async def put_budget(scope_type: str, scope_id: str, body: Any = JSON_BODY) -> dict[str, Any]:
        bd = _parse(BudgetDefinition, body)
        if (bd.scope_type, bd.scope_id) != (scope_type, scope_id):
            raise ValidationFailed("scope in the body differs from the path")
        if scope_type == "platform" and scope_id != "platform":
            raise ValidationFailed("the platform scope id is 'platform'")
        await call(
            store.put_doc,
            "budget",
            budget_key(scope_type, scope_id),
            bd.model_dump(exclude_none=True, exclude={"status"}),
        )
        return await _with_status(bd)

    @app.delete("/v1/budgets/{scope_type}/{scope_id}", status_code=204, tags=["budgets"])
    async def delete_budget(scope_type: str, scope_id: str) -> Response:
        if not await call(store.delete_doc, "budget", budget_key(scope_type, scope_id)):
            raise NotFound(f"budget {scope_type}/{scope_id} not found")
        return Response(status_code=204)

    @app.get("/v1/usage", tags=["usage"])
    async def get_usage(
        scope_type: str | None = Query(default=None, pattern="^(platform|source|task)$"),
        scope_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        group_by: str = Query(default="day", pattern="^(day|model|purpose|scope)$"),
    ) -> dict[str, Any]:
        if scope_type in {"source", "task"} and not scope_id:
            raise ValidationFailed("scope_id is required for scope_type source/task")
        rows = await call(store.usage, UsageQuery(scope_type, scope_id, since, until, group_by))
        items = []
        totals = {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": {"amount": 0.0, "currency": limits.llm.budget.currency},
        }
        for r in rows:
            item: dict[str, Any] = {
                "requests": r.requests,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "cost": {"amount": round(r.cost, 10), "currency": r.currency},
                "test_mode": bool(r.test_mode),
            }
            if r.period_start is not None:
                item["period_start"] = r.period_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            for k in ("scope_type", "scope_id", "model", "purpose"):
                if getattr(r, k) is not None:
                    item[k] = getattr(r, k)
            items.append(item)
            totals["requests"] += r.requests
            totals["input_tokens"] += r.input_tokens
            totals["output_tokens"] += r.output_tokens
            totals["cost"]["amount"] = round(totals["cost"]["amount"] + r.cost, 10)  # type: ignore[index]
            totals["cost"]["currency"] = r.currency  # type: ignore[index]
        return {"items": items, "totals": totals}

    # ------------------------------------------------------------------ handler.v1
    @app.post("/v1/invocations", tags=["invocations"], response_model=None)
    async def invoke(request: Request, body: Any = JSON_BODY) -> Response:
        if not isinstance(body, dict) or not {"handler", "inputs", "delivery"} <= set(body):
            raise ValidationFailed("HandlerInvocation needs handler, inputs and delivery")
        if not body["inputs"]:
            raise ValidationFailed("inputs must not be empty")
        key = request.headers.get(IDEMPOTENCY_HEADER) or str(
            (body.get("delivery") or {}).get("delivery_key") or ""
        )
        if not key:
            raise ValidationFailed(
                "Idempotency-Key (= delivery.delivery_key) is required",
                errors=[FieldError(parameter=IDEMPOTENCY_HEADER, message="required")],
            )

        class _NoStore(Exception):
            def __init__(self, response: StoredResponse) -> None:
                self.response = response

        async def execute() -> dict[str, Any]:
            result = await handler.invoke(body)
            await call(store.save_invocation, result["invocation_id"], result)
            return result

        async def run() -> StoredResponse:
            if body.get("mode") == "async":

                async def work(ctx: JobContext) -> dict[str, Any]:
                    return await execute()

                job = await runner.submit("llm_invocation", work, idempotency_key=key)
                return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})
            result = await execute()
            if (
                result.get("status") == "failed"
                and (result.get("failure") or {}).get("kind") == "budget_exhausted"
            ):
                raise _NoStore(
                    StoredResponse(200, result)
                )  # re-delivery after a budget change must run again
            return StoredResponse(200, result)

        fp = fingerprint(request.method, request.url.path, await request.body())
        try:
            stored, replayed = await run_idempotent(idem_store, key, fp, run, limits.idempotency)
        except _NoStore as ns:
            return JSONResponse(ns.response.body, status_code=ns.response.status_code)
        headers = dict(stored.headers)
        payload = stored.body
        if replayed:
            headers[REPLAY_HEADER] = "true"
            if stored.status_code == 200 and isinstance(payload, dict):
                payload = {**payload, "duplicate": True}
        return JSONResponse(payload, status_code=stored.status_code, headers=headers)

    @app.get("/v1/invocations/{invocation_id}", tags=["invocations"])
    async def get_invocation(invocation_id: str) -> dict[str, Any]:
        doc = await call(store.get_invocation, invocation_id)
        if doc is None:
            raise NotFound(f"invocation {invocation_id} not found")
        return doc  # type: ignore[no-any-return]

    @app.post("/v1/test-runs", status_code=202, tags=["tests"], response_model=None)
    async def start_test_run(request: Request, body: Any = JSON_BODY) -> Response:
        if not isinstance(body, dict) or "handler" not in body:
            raise ValidationFailed("TestRunRequest needs handler")

        async def run() -> StoredResponse:
            async def work(ctx: JobContext) -> dict[str, Any]:
                return await run_tests(handler, body)

            job = await runner.submit(
                "llm_test_run", work, idempotency_key=request.headers.get(IDEMPOTENCY_HEADER)
            )
            return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})

        return await idempotent(request, idem_store, run, limits=limits.idempotency)

    # ------------------------------------------------------------------ connections
    page_limits = PageLimits()

    @app.get("/v1/connections", tags=["connections"])
    async def list_connections(
        limit: int | None = Query(default=None, ge=1), cursor: str | None = None
    ) -> dict[str, Any]:
        docs = await call(store.list_docs, "connection")
        after = decode_cursor(cursor) if cursor else None
        if after is not None:
            docs = [d for d in docs if d["connection_id"] > after]
        n = clamp_limit(limit, page_limits)
        page = docs[:n]
        nxt = encode_cursor(page[-1]["connection_id"]) if len(docs) > n else None
        return {"items": page, "next_cursor": nxt}

    @app.get("/v1/connections/{connection_id}", tags=["connections"])
    async def get_connection(connection_id: str) -> Response:
        doc = await call(store.get_doc, "connection", connection_id)
        if doc is None:
            raise NotFound(f"connection {connection_id} not found")
        return JSONResponse(doc, headers={"ETag": etag(doc)})

    @app.put("/v1/connections/{connection_id}", tags=["connections"])
    async def put_connection(
        connection_id: str,
        body: Any = JSON_BODY,
        if_match: str | None = IF_MATCH,
    ) -> Response:
        conn = _parse(Connection, body)
        if conn.connection_id != connection_id:
            raise ValidationFailed("connection_id in the body differs from the path")
        if leaks := find_secret_like(conn.params or {}):
            raise JaneError(
                "params contain secret-like values; use secret_refs", code="secret_detected", errors=leaks
            )
        doc = conn.model_dump(exclude_none=True)
        if violations := policy.violations(doc):
            raise ValidationFailed(
                "connection violates the secret policy of this service (allowed env prefix, secrets "
                "directory, provider api_base allowlist)",
                errors=violations,
            )
        await _check_if_match("connection", connection_id, if_match)
        created = await call(store.put_doc, "connection", connection_id, doc)
        return JSONResponse(doc, status_code=201 if created else 200, headers={"ETag": etag(doc)})

    @app.delete("/v1/connections/{connection_id}", status_code=204, tags=["connections"])
    async def delete_connection(connection_id: str) -> Response:
        if not await call(store.delete_doc, "connection", connection_id):
            raise NotFound(f"connection {connection_id} not found")
        return Response(status_code=204)

    @app.post("/v1/connections/{connection_id}/test", tags=["connections"])
    async def test_connection(connection_id: str) -> dict[str, Any]:
        doc = await call(store.get_doc, "connection", connection_id)
        if doc is None:
            raise NotFound(f"connection {connection_id} not found")
        started = datetime.now(UTC)
        _, resolved_refs = resolve_connection(doc, policy)
        missing = [k for k, ok in resolved_refs.items() if not ok]
        result: dict[str, Any] = {
            "ok": not missing,
            "checked_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "latency_ms": int((datetime.now(UTC) - started).total_seconds() * 1000),
            "secrets_resolved": resolved_refs,
        }
        if missing:
            result["message"] = f"secret reference(s) not resolvable in this service's environment: {missing}"
        return result

    return app
