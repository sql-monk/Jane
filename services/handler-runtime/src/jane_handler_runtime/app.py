"""HTTP API: handler protocol ``contracts/openapi/handler.v1.yaml`` for Python extractors.

``POST /v1/invocations`` (sync / async, ``Idempotency-Key`` = ``delivery.delivery_key``),
``GET /v1/invocations/{id}``, ``POST /v1/test-runs`` (always ``test_mode``), ``/v1/jobs/*``; ``/v1/health``,
``/v1/info``, ``/metrics`` come from jane-kit.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import cached_property
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from jane_kit.auth_scopes import HANDLER
from jane_kit.contracts import ContractViolation, OpenAPISpec
from jane_kit.errors import (
    BadRequest,
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
    run_idempotent,
)
from jane_kit.jobs import TERMINAL_STATUSES, Job, JobContext, JobRunner, JobStatus, jobs_router
from jane_kit.service import create_app

from . import __version__
from .profiles import load_profiles
from .runtime import Runtime, build_runtime
from .settings import Settings, request_layer, resolve_service_limits
from .state import InMemoryState, PostgresState, ServiceState
from .testrun import run_tests, select_cases

log = logging.getLogger(__name__)


class _Contracts:
    def __init__(self, runtime: Runtime) -> None:
        self.runtime = runtime

    @cached_property
    def handler_spec(self) -> OpenAPISpec:
        return OpenAPISpec.load(self.runtime.schemas.root.parent / "openapi" / "handler.v1.yaml")


async def _json_body(request: Request) -> dict[str, Any]:
    try:
        body = json.loads(await request.body())
    except ValueError as exc:
        raise BadRequest(f"request body is not JSON: {exc}") from exc
    if not isinstance(body, dict):
        raise BadRequest("request body must be a JSON object")
    return body


def _problem_error(job: Job) -> JaneError:
    problem = job.error
    if problem is None:
        return JaneError("job failed without an error")
    return JaneError(
        problem.detail,
        code=problem.code,
        status=problem.status,
        retryable=problem.retryable,
        title=problem.title,
        details=problem.details,
        retry_after_seconds=problem.retry_after_seconds,
    )


def build_state(settings: Settings, runtime: Runtime) -> ServiceState:
    """PostgreSQL state when ``state_dsn`` is set (several instances), else in-memory (one instance)."""
    if settings.state_dsn is not None:
        return PostgresState(
            settings.state_dsn.get_secret_value(),
            settings.state_schema,
            runtime.limits.limits,
            settings.instance_id,
        )
    return InMemoryState(runtime.limits.limits)


def build_app(
    settings: Settings | None = None, runtime: Runtime | None = None, state: ServiceState | None = None
) -> FastAPI:
    settings = settings or Settings()
    runtime = runtime or build_runtime(settings)
    resolved = runtime.limits
    limits = resolved.limits
    state = state or build_state(settings, runtime)
    runner = JobRunner(store=state.jobs, limits=limits.jobs)
    idem_store = state.idempotency
    results = state.results
    contracts = _Contracts(runtime)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        log.info(
            "configured limits",
            extra={
                "limits": resolved.effective(),
                "backend": runtime.backend.name,
                "images": settings.profile_images,
                "state": state.name,
            },
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
            await asyncio.gather(beat, return_exceptions=True)
            await runner.shutdown()
            await state.close()
            runtime.close()

    def capabilities() -> dict[str, Any]:
        return {
            "handler_kinds": ["extractor", "transform"],
            "runtimes": ["python"],
            "runtime_profiles": {name: dict(p.document) for name, p in load_profiles().items()},
            "sandbox": {"backend": runtime.backend.name, "network": ["none"]},
            "package_sources": ["package_archive", "registry"]
            if settings.registry_url
            else ["package_archive"],
            "connections": False,
            "state": state.name,
            "test_runs": True,
        }

    app = create_app(
        settings,
        title="Handler Runtime",
        version=__version__,
        lifespan=lifespan,
        capabilities=capabilities,
        limits=resolved,
        auth_scopes=HANDLER,  # ADR-0005 scopes per operation
    )
    app.state.limits = resolved
    app.state.runtime = runtime
    app.state.results = results
    app.state.service_state = state
    app.state.runner = runner

    @app.post("/v1/jobs/{job_id}/cancel", tags=["jobs"], operation_id="cancelJob", response_model=None)
    async def cancel_job(job_id: str, request: Request) -> JSONResponse:
        """jane-kit cancel + stop the sandbox container of the invocation (by label, on this engine)."""
        before = await runner.get(job_id)
        if before.status in TERMINAL_STATUSES:
            return JSONResponse(before.wire(), status_code=200)
        raw = await request.body()
        reason = None
        if raw:
            payload = json.loads(raw)
            reason = payload.get("reason") if isinstance(payload, dict) else None
        job = await runner.cancel(job_id, reason=reason)
        invocation_id = (before.labels or {}).get("invocation_id")
        if invocation_id:
            killed = await asyncio.to_thread(runtime.backend.kill, invocation_id)
            log.info(
                "job cancelled", extra={"job_id": job_id, "invocation_id": invocation_id, "killed": killed}
            )
        return JSONResponse(job.wire(), status_code=202)

    app.include_router(jobs_router(runner))

    @app.get("/v1/connections", tags=["connections"], operation_id="listConnections")
    async def list_connections() -> JSONResponse:
        """handler-runtime holds no connections: extractors get no credentials (TZ §7, §11)."""
        return JSONResponse({"items": [], "next_cursor": None})

    @app.put("/v1/connections/{connection_id}", tags=["connections"], operation_id="putConnection")
    async def put_connection(connection_id: str) -> JSONResponse:
        raise JaneError(
            "handler-runtime does not use managed connections (extractors run without credentials)",
            code="not_implemented",
        )

    @app.get("/v1/connections/{connection_id}", tags=["connections"], operation_id="getConnection")
    async def get_connection(connection_id: str) -> JSONResponse:
        raise NotFound(f"connection {connection_id} not found")

    @app.delete("/v1/connections/{connection_id}", tags=["connections"], operation_id="deleteConnection")
    async def delete_connection(connection_id: str) -> JSONResponse:
        raise NotFound(f"connection {connection_id} not found")

    @app.post("/v1/connections/{connection_id}/test", tags=["connections"], operation_id="testConnection")
    async def test_connection(connection_id: str) -> JSONResponse:
        raise NotFound(f"connection {connection_id} not found")

    async def sandbox_check() -> bool:
        await asyncio.to_thread(runtime.backend.ping)
        return True

    app.state.health.add("sandbox", sandbox_check)
    app.state.health.add("state", state.ping)

    async def idempotent_call(request: Request, handler: Any) -> tuple[StoredResponse, bool]:
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if key is None:
            raise ValidationFailed(
                f"{IDEMPOTENCY_HEADER} header is required",
                errors=[FieldError(parameter=IDEMPOTENCY_HEADER, message="required")],
            )
        fp = fingerprint(request.method, request.url.path, await request.body())
        return await run_idempotent(idem_store, key, fp, handler, limits.idempotency)

    @app.post("/v1/invocations", tags=["invocations"], operation_id="invokeHandler", response_model=None)
    async def invoke(request: Request) -> Response:
        body = await _json_body(request)
        errors = runtime.schemas.errors("handler-invocation.schema.json", body)
        if errors:
            raise ValidationFailed(
                "request does not match HandlerInvocation",
                errors=[FieldError(pointer=e["pointer"] or "/", message=e["message"]) for e in errors[:20]],
            )
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if key is not None and key != body["delivery"]["delivery_key"]:
            raise ValidationFailed(
                "Idempotency-Key must equal delivery.delivery_key",
                errors=[
                    FieldError(parameter=IDEMPOTENCY_HEADER, message="differs from delivery.delivery_key")
                ],
            )

        async def handler() -> StoredResponse:
            prep = await runtime.executor.prepare(body)

            async def work(ctx: JobContext) -> dict[str, Any]:
                result = await runtime.executor.run(prep)
                await ctx.check_cancelled()  # cancelled meanwhile (possibly from another instance)
                await results.put(result)
                return result

            job = await runner.submit(
                "invocation", work, idempotency_key=key, labels={"invocation_id": prep.invocation_id}
            )
            if body.get("mode", "sync") == "sync":
                wait_s = prep.limits.timeouts.sync_response_max_ms / 1000
                try:
                    done = await asyncio.wait_for(asyncio.shield(runner.wait(job.job_id)), timeout=wait_s)
                except TimeoutError:
                    done = None
                if done is not None and done.status == JobStatus.SUCCEEDED and done.result is not None:
                    return StoredResponse(200, done.result)
                if done is not None and done.status == JobStatus.FAILED:
                    raise _problem_error(done)
            current = await runner.get(job.job_id)
            return StoredResponse(202, current.wire(), {"Location": runner.location(job.job_id)})

        stored, replayed = await idempotent_call(request, handler)
        status, payload, headers = stored.status_code, stored.body, dict(stored.headers)
        if replayed:
            headers[REPLAY_HEADER] = "true"
            if status == 202:
                job = await runner.get(payload["job_id"])
                if job.status == JobStatus.SUCCEEDED and job.result is not None:
                    status, payload = 200, job.result
                    headers.pop("Location", None)
            if status == 200:
                payload = {**payload, "duplicate": True}
        return JSONResponse(payload, status_code=status, headers=headers)

    @app.get("/v1/invocations/{invocation_id}", tags=["invocations"], operation_id="getInvocation")
    async def get_invocation(invocation_id: str) -> JSONResponse:
        result = await results.get(invocation_id)
        if result is None:
            raise NotFound(f"invocation {invocation_id} not found")
        return JSONResponse(result)

    @app.post("/v1/test-runs", tags=["tests"], operation_id="startTestRun", response_model=None)
    async def start_test_run(request: Request) -> Response:
        body = await _json_body(request)
        try:
            contracts.handler_spec.validate_component("TestRunRequest", body)
        except ContractViolation as exc:
            raise ValidationFailed(str(exc)[:2000]) from exc
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if body.get("limits"):
            try:
                resolve_service_limits(settings, request_layer(body["limits"]))
            except ValueError as exc:
                raise ValidationFailed(f"invalid limits: {exc}") from exc

        async def handler() -> StoredResponse:
            package = await runtime.store.load(body["handler"], body.get("package_archive"))
            await asyncio.to_thread(runtime.executor.check_package, package)
            cases = select_cases(package, body.get("tests", "all"), body.get("extra_cases") or [])

            async def work(ctx: JobContext) -> dict[str, Any]:
                return await run_tests(
                    runtime.executor, package, cases, params=body.get("params"), limits=body.get("limits")
                )

            job = await runner.submit("test_run", work, idempotency_key=key)
            return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})

        stored, replayed = await idempotent_call(request, handler)
        headers = dict(stored.headers)
        if replayed:
            headers[REPLAY_HEADER] = "true"
        return JSONResponse(stored.body, status_code=stored.status_code, headers=headers)

    return app
