"""HTTP API of the source assistant (``contracts/openapi/assistant.v1.yaml``).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit. Every long
operation is ``202`` + Job; POSTs with side effects honour ``Idempotency-Key``.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

from jane_kit.auth_scopes import ASSISTANT
from jane_kit.config import LimitError
from jane_kit.errors import ValidationFailed
from jane_kit.idempotency import IDEMPOTENCY_HEADER, StoredResponse, idempotent
from jane_kit.jobs import JobContext, JobRunner, jobs_router
from jane_kit.service import create_app

from . import __version__
from .clients import Neighbours
from .content import MaterialContent, MaterialContentScope
from .guards import SchemaValidator
from .improvement import run_improvement
from .onboarding import OnboardingService
from .search import HttpJsonSearchProvider, NoSearchProvider, SearchProvider, StaticSearchProvider
from .settings import ServiceLimits, Settings, request_layer, resolve_service_limits
from .state import InMemoryState, PostgresState, ServiceState
from .unknown import FlagOff, run_unknown

log = logging.getLogger(__name__)

SLUG = r"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"
SEMVER = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OnboardingRequest(_Strict):
    query: str = Field(min_length=1, max_length=2000)
    source_kind: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_-]{1,31}$")
    expected_entity_types: list[str] | None = None
    crawl_hints: dict[str, Any] | None = None
    limits: dict[str, Any] | None = None
    auto_activation: bool = False


class CandidateSelection(_Strict):
    candidate_id: str


class AcceptanceRequest(_Strict):
    activate: bool = False
    source_id: str | None = Field(default=None, pattern=SLUG)


class PackageRef(_Strict):
    package_id: str = Field(pattern=SLUG)
    version: str = Field(pattern=SEMVER)
    digest: str | None = Field(default=None, pattern=r"^sha256:[a-f0-9]{64}$")


class MaterialRef(_Strict):
    storage_connection_id: str
    object_id: str


class ProblemSample(_Strict):
    material: dict[str, Any] | None = None
    material_ref: MaterialRef | None = None
    result: dict[str, Any] | None = None
    diagnostics: list[dict[str, Any]] | None = None

    @model_validator(mode="after")
    def _one_source(self) -> ProblemSample:
        if self.material is None and self.material_ref is None:
            raise ValueError("material or material_ref is required")
        return self


class BindingRef(_Strict):
    task_id: str
    stage_id: str


class Policy(_Strict):
    approval: Literal["manual", "auto_after_checks"] = "manual"
    allow_fork: bool = True


class ImprovementRequest(_Strict):
    package: PackageRef
    source_id: str | None = None
    problem_group_id: str | None = None
    problem_samples: list[ProblemSample] = Field(min_length=1)
    successful_examples: list[ProblemSample] | None = None
    bindings: list[BindingRef] | None = None
    policy: Policy | None = None
    limits: dict[str, Any] | None = None


class UnknownMaterialRequest(_Strict):
    source_id: str
    task_id: str | None = None
    forward_unknown_to_llm: bool
    material: dict[str, Any]
    limits: dict[str, Any] | None = None


@dataclass
class Dependencies:
    """Replaceable collaborators (tests pass ASGI transports of contract fakes and a fake search)."""

    transports: Mapping[str, httpx.AsyncBaseTransport] | None = None
    search: SearchProvider | None = None
    state: ServiceState | None = None


def build_state(settings: Settings, limits: ServiceLimits) -> ServiceState:
    """PostgreSQL state when ``state_dsn`` is set (several instances), else in-memory (one instance)."""
    if settings.state_dsn is not None:
        return PostgresState(
            settings.state_dsn.get_secret_value(), settings.state_schema, limits, settings.instance_id
        )
    return InMemoryState(limits)


def build_search(settings: Settings, limits: ServiceLimits) -> SearchProvider:
    if settings.search_provider == "static":
        if settings.search_static_file is None:
            raise ValueError("search_provider=static needs JANE_ASSISTANT_SEARCH_STATIC_FILE")
        return StaticSearchProvider.from_file(settings.search_static_file)
    if settings.search_provider == "http_json":
        if not settings.search_url_template:
            raise ValueError("search_provider=http_json needs JANE_ASSISTANT_SEARCH_URL_TEMPLATE")
        return HttpJsonSearchProvider(
            settings.search_url_template,
            items_path=settings.search_items_path,
            title_field=settings.search_title_field,
            url_field=settings.search_url_field,
            description_field=settings.search_description_field,
            limits=limits.search,
        )
    return NoSearchProvider()


def _limits(settings: Settings, llm_limits: dict[str, Any] | None) -> ServiceLimits:
    try:
        return resolve_service_limits(settings, *request_layer(llm_limits)).limits
    except LimitError as exc:
        raise ValidationFailed(f"invalid limits: {exc}") from exc


def _body(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude_none=True)


def build_app(settings: Settings | None = None, deps: Dependencies | None = None) -> FastAPI:
    settings = settings or Settings()
    deps = deps or Dependencies()
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    state = deps.state or build_state(settings, limits)
    runner = JobRunner(store=state.jobs, limits=limits.jobs)
    idem_store = state.idempotency
    neighbours = Neighbours.from_settings(
        settings, limits.clients, deps.transports, llm_limits=limits.llm_call.client_limits(limits.clients)
    )
    validator = SchemaValidator.locate(settings.contracts_dir)
    search = deps.search or build_search(settings, limits)
    onboarding = OnboardingService(
        settings=settings,
        neighbours=neighbours,
        search=search,
        runner=runner,
        store=state.sessions,
        validator=validator,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        log.info(
            "configured limits",
            extra={"limits": resolved.effective(), "contracts_schemas": str(validator.schemas_dir)},
        )
        await state.open()

        async def heartbeat() -> None:
            while True:
                await asyncio.sleep(limits.state.heartbeat_interval_ms / 1000)
                try:
                    await state.heartbeat()
                except Exception:
                    log.warning("state heartbeat failed", exc_info=True)

        beat = asyncio.create_task(heartbeat(), name="state-heartbeat")
        try:
            yield
        finally:
            beat.cancel()
            await runner.shutdown()
            await state.release_owned(f"instance {settings.instance_id} shut down")
            await state.close()
            await neighbours.aclose()

    def capabilities() -> dict[str, Any]:
        return {
            "operations": ["onboarding", "improvement", "unknown_materials"],
            "search_provider": settings.search_provider if deps.search is None else "custom",
            "neighbours": {
                "llm": neighbours.llm.configured,
                "registry": neighbours.registry.configured,
                "collector_web": neighbours.collector("web").configured,
                "collector_telegram": neighbours.collector("telegram").configured,
                "handler_runtime": neighbours.handler.configured,
                "orchestrator": neighbours.orchestrator.configured,
                "storage": neighbours.storage.configured,
            },
            "local_schema_validation": validator.available,
            "state": state.name,
        }

    app = create_app(
        settings,
        title="Jane Source Assistant",
        version=__version__,
        lifespan=lifespan,
        capabilities=capabilities,
        limits=resolved,
        auth_scopes=ASSISTANT,  # ADR-0005 scopes per operation
    )
    app.state.limits = resolved
    app.state.runner = runner
    app.state.service_state = state
    app.state.health.add("state", state.ping)
    app.state.onboarding = onboarding
    app.state.neighbours = neighbours
    # Material content of requests and of the jobs they start: JANE_ASSISTANT_BLOB_ROOTS / _DOWNLOAD_HOST_ALLOWLIST.
    app.add_middleware(MaterialContentScope, content=MaterialContent.from_settings(settings, limits))
    app.include_router(jobs_router(runner))

    def accepted(job: dict[str, Any], extra: dict[str, str] | None = None) -> StoredResponse:
        return StoredResponse(202, job, {"Location": runner.location(job["job_id"]), **(extra or {})})

    @app.post("/v1/onboarding-sessions", status_code=202, tags=["onboarding"], operation_id="startOnboarding")
    async def start_onboarding(body: OnboardingRequest, request: Request) -> Response:
        payload = _body(body)
        _limits(settings, payload.get("limits"))

        async def handler() -> StoredResponse:
            job, _session_id = await onboarding.start(payload, request.headers.get(IDEMPOTENCY_HEADER))
            return accepted(job)

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    @app.get("/v1/onboarding-sessions/{session_id}", tags=["onboarding"], operation_id="getOnboardingSession")
    async def get_session(session_id: str) -> JSONResponse:
        return JSONResponse((await onboarding.get(session_id)).wire())

    @app.post(
        "/v1/onboarding-sessions/{session_id}/candidate-selection",
        tags=["onboarding"],
        operation_id="selectCandidate",
    )
    async def select_candidate(session_id: str, body: CandidateSelection) -> JSONResponse:
        return JSONResponse((await onboarding.select(session_id, body.candidate_id)).wire())

    @app.post(
        "/v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance",
        status_code=202,
        tags=["onboarding"],
        operation_id="acceptProposal",
    )
    async def accept_proposal(
        session_id: str, proposal_id: str, body: AcceptanceRequest, request: Request
    ) -> Response:
        async def handler() -> StoredResponse:
            job = await onboarding.accept(
                session_id,
                proposal_id,
                body.activate,
                body.source_id,
                request.headers.get(IDEMPOTENCY_HEADER),
            )
            return accepted(job)

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    @app.post("/v1/improvement-runs", status_code=202, tags=["improvement"], operation_id="startImprovement")
    async def start_improvement(body: ImprovementRequest, request: Request) -> Response:
        payload = _body(body)
        run_limits = _limits(settings, payload.get("limits"))

        async def handler() -> StoredResponse:
            async def work(ctx: JobContext) -> dict[str, Any]:
                async def progress(done: int, message: str) -> None:
                    await ctx.progress(done, 4, unit="steps", message=message)

                return await run_improvement(
                    nb=neighbours,
                    req=payload,
                    settings=settings,
                    limits=run_limits,
                    validator=validator,
                    job_id=ctx.job_id,
                    progress=progress,
                )

            # Labels identify the run for the admin UI and the improvement-runs list (filters).
            labels = {"package_id": body.package.package_id}
            if body.source_id:
                labels["source_id"] = body.source_id[:256]
            if body.problem_group_id:
                labels["problem_group_id"] = body.problem_group_id[:256]
            job = await runner.submit(
                "improvement", work, idempotency_key=request.headers.get(IDEMPOTENCY_HEADER), labels=labels
            )
            return accepted(job.wire())

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    @app.post(
        "/v1/unknown-materials", status_code=202, tags=["unknown"], operation_id="analyzeUnknownMaterial"
    )
    async def analyze_unknown(body: UnknownMaterialRequest, request: Request) -> Response:
        if not body.forward_unknown_to_llm:
            raise FlagOff(
                "forward_unknown_to_llm is off: unknown materials are not sent to the LLM",
                title="Forwarding unknown pages to LLM is disabled",
            )
        payload = _body(body)
        errors = validator.errors("material.schema.json", payload["material"])
        if errors:
            raise ValidationFailed(f"material does not match material.schema.json: {errors[:3]}")
        run_limits = _limits(settings, payload.get("limits"))

        async def handler() -> StoredResponse:
            async def work(ctx: JobContext) -> dict[str, Any]:
                return await run_unknown(
                    nb=neighbours, req=payload, settings=settings, limits=run_limits, job_id=ctx.job_id
                )

            job = await runner.submit(
                "unknown_material",
                work,
                idempotency_key=request.headers.get(IDEMPOTENCY_HEADER),
                labels={"source_id": body.source_id[:256]},
            )
            return accepted(job.wire())

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    return app
