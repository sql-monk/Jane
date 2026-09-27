"""HTTP API of the orchestrator (``contracts/openapi/orchestrator.v1.yaml``).

``/v1/health``, ``/v1/info`` and ``/metrics`` come from jane-kit; everything else is implemented here.
Request bodies are validated against the contract schemas; responses follow the contract (checked by
``tests/test_contract.py``). Worker threads (feed, items, schedules, connection sync) start with the app
unless ``JANE_ORCHESTRATOR_RUN_WORKERS=false`` (then run ``python -m jane_orchestrator worker``).
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, TypeVar

from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from jane_kit.errors import BadRequest, NotFound
from jane_kit.idempotency import IDEMPOTENCY_HEADER, StoredResponse, idempotent
from jane_kit.pagination import clamp_limit
from jane_kit.service import create_app

from . import __version__
from .auth import Principal, authenticate
from .common import etag
from .core import Core
from .engine import Engine, Worker
from .idempotency import PgIdempotencyStore
from .service import Admin
from .settings import Settings, resolve_service_limits

log = logging.getLogger(__name__)
T = TypeVar("T")

READ, WRITE, ADMIN = "orchestrator:read", "orchestrator:write", "orchestrator:admin"


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    holder: dict[str, Any] = {}

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        core = Core(settings, limits, getattr(app.state, "metrics", None))
        await run_in_threadpool(core.open)
        engine = Engine(core)
        workers: list[Worker] = []
        if settings.run_workers:
            for i in range(limits.engine.workers):
                w = Worker(engine, f"{settings.instance_id}-w{i}", scheduler=settings.scheduler_enabled)
                w.start()
                workers.append(w)
        holder.update(core=core, admin=Admin(core), engine=engine, idem=PgIdempotencyStore(core.db))
        app.state.core = core
        app.state.engine = engine
        log.info("orchestrator started", extra={"limits": resolved.effective(), "workers": len(workers)})
        try:
            yield
        finally:
            for w in workers:
                w.stop()
            await run_in_threadpool(core.close)

    app = create_app(
        settings,
        title="Jane Orchestrator",
        version=__version__,
        lifespan=lifespan,
        capabilities=lambda: {
            "executors": [e.executor for e in settings.all_executors()],
            "queue": "postgresql-skip-locked",
        },
        limits=resolved,
    )
    app.state.limits = resolved

    async def db_check() -> bool:
        core = holder.get("core")
        if core is None:
            raise RuntimeError("starting")
        return bool(await run_in_threadpool(core.db.ping))

    app.state.health.add("database", db_check)

    def admin() -> Admin:
        a: Admin = holder["admin"]
        return a

    def principal(request: Request, scope: str) -> Principal:
        p = authenticate(request, settings.auth_mode, settings.api_keys)
        p.require(scope)
        return p

    async def body_json(request: Request) -> Any:
        raw = await request.body()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise BadRequest("request body is not valid JSON") from exc

    async def threaded(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        return await run_in_threadpool(fn, *args, **kwargs)

    def page(items: list[Any], nxt: str | None) -> dict[str, Any]:
        return {"items": items, "next_cursor": nxt}

    def lim(value: int | None) -> int:
        return clamp_limit(value, limits.pages)

    def with_etag(
        body: Any, version: int, status: int = 200, extra: dict[str, str] | None = None
    ) -> JSONResponse:
        return JSONResponse(body, status_code=status, headers={"ETag": etag(version), **(extra or {})})

    async def idem(request: Request, fn: Callable[[], StoredResponse]) -> Response:
        async def handler() -> StoredResponse:
            return await run_in_threadpool(fn)

        return await idempotent(request, holder["idem"], handler, limits=limits.idempotency)

    def validate(method: str, path: str, body: Any) -> None:
        holder["core"].schemas.validate_request(method, path, body)

    # ------------------------------------------------------------------ sources
    @app.get("/v1/sources", tags=["sources"])
    async def list_sources(
        request: Request,
        kind: str | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(*await threaded(admin().list_sources, kind, cursor, lim(limit)))

    @app.post("/v1/sources", tags=["sources"], status_code=201)
    async def create_source(request: Request) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request)
        validate("POST", "/v1/sources", body)

        def run() -> StoredResponse:
            doc, version = admin().create_source(body, p.name)
            return StoredResponse(
                201, doc, {"ETag": etag(version), "Location": f"/v1/sources/{doc['source_id']}"}
            )

        return await idem(request, run)

    @app.get("/v1/sources/{source_id}", tags=["sources"])
    async def get_source(request: Request, source_id: str) -> Response:
        principal(request, READ)
        doc, version = await threaded(admin().get_source, source_id)
        return with_etag(doc, version)

    @app.put("/v1/sources/{source_id}", tags=["sources"])
    async def replace_source(request: Request, source_id: str) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request)
        validate("PUT", "/v1/sources/x", body)
        doc, version = await threaded(
            admin().replace_source, source_id, body, request.headers.get("if-match"), p.name
        )
        return with_etag(doc, version)

    @app.delete("/v1/sources/{source_id}", tags=["sources"], status_code=204)
    async def delete_source(request: Request, source_id: str) -> Response:
        p = principal(request, WRITE)
        await threaded(admin().delete_source, source_id, p.name)
        return Response(status_code=204)

    # ------------------------------------------------------------------ tasks
    @app.get("/v1/tasks", tags=["tasks"])
    async def list_tasks(
        request: Request,
        source_id: str | None = None,
        package_id: str | None = None,
        package_version: str | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(
            *await threaded(admin().list_tasks, source_id, package_id, package_version, cursor, lim(limit))
        )

    @app.post("/v1/tasks", tags=["tasks"], status_code=201)
    async def create_task(request: Request) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request)
        validate("POST", "/v1/tasks", body)

        def run() -> StoredResponse:
            doc, version = admin().create_task(body, p.name)
            return StoredResponse(
                201, doc, {"ETag": etag(version), "Location": f"/v1/tasks/{doc['task_id']}"}
            )

        return await idem(request, run)

    @app.get("/v1/tasks/{task_id}", tags=["tasks"])
    async def get_task(request: Request, task_id: str) -> Response:
        principal(request, READ)
        doc, version = await threaded(admin().get_task, task_id)
        return with_etag(doc, version)

    @app.put("/v1/tasks/{task_id}", tags=["tasks"])
    async def replace_task(request: Request, task_id: str) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request)
        validate("PUT", "/v1/tasks/x", body)
        doc, version = await threaded(
            admin().replace_task, task_id, body, request.headers.get("if-match"), p.name
        )
        return with_etag(doc, version)

    @app.delete("/v1/tasks/{task_id}", tags=["tasks"], status_code=204)
    async def delete_task(request: Request, task_id: str) -> Response:
        p = principal(request, WRITE)
        await threaded(admin().delete_task, task_id, p.name)
        return Response(status_code=204)

    @app.post("/v1/task-validations", tags=["tasks"])
    async def validate_task(request: Request) -> dict[str, Any]:
        principal(request, READ)
        body = await body_json(request)
        result: dict[str, Any] = await threaded(admin().validate_task, body)
        return result

    @app.post("/v1/tasks/{task_id}/runs", tags=["runs"], status_code=202)
    async def start_run(request: Request, task_id: str) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request) or {}
        validate("POST", "/v1/tasks/x/runs", body)
        key = request.headers.get(IDEMPOTENCY_HEADER)

        def run() -> StoredResponse:
            job = admin().start_run(task_id, body, p.name, key)
            return StoredResponse(202, job, {"Location": job["links"]["self"]})

        return await idem(request, run)

    @app.get("/v1/tasks/{task_id}/stages/{stage_id}/activations", tags=["tasks", "audit"])
    async def list_activations(
        request: Request,
        task_id: str,
        stage_id: str,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(*await threaded(admin().list_activations, task_id, stage_id, cursor, lim(limit)))

    @app.post("/v1/tasks/{task_id}/stages/{stage_id}/activations", tags=["tasks"])
    async def activate(request: Request, task_id: str, stage_id: str) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request)
        validate("POST", "/v1/tasks/x/stages/y/activations", body)

        def run() -> StoredResponse:
            return StoredResponse(200, admin().activate(task_id, stage_id, body, p.name))

        return await idem(request, run)

    # ------------------------------------------------------------------ runs
    @app.get("/v1/runs", tags=["runs"])
    async def list_runs(
        request: Request,
        task_id: str | None = None,
        status: str | None = None,
        since: datetime | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)

        def run() -> tuple[list[dict[str, Any]], str | None]:
            with holder["core"].db.conn() as conn:
                result: tuple[list[dict[str, Any]], str | None] = admin().runs.list_runs(
                    conn, task_id=task_id, status=status, since=since, cursor=cursor, limit=lim(limit)
                )
                return result

        return page(*await threaded(run))

    @app.get("/v1/runs/{run_id}", tags=["runs"])
    async def get_run(request: Request, run_id: str) -> dict[str, Any]:
        principal(request, READ)

        def run() -> dict[str, Any]:
            with holder["core"].db.conn() as conn:
                runs = admin().runs
                return runs.run_view(conn, runs.get_row(conn, run_id))

        return await threaded(run)

    async def cancel(request: Request, run_id: str) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request) or {}
        validate("POST", "/v1/runs/x/cancel", body)
        job, accepted = await threaded(admin().runs.request_cancel, run_id, p.name, body.get("reason"))
        return JSONResponse(job, status_code=202 if accepted else 200)

    @app.post("/v1/runs/{run_id}/cancel", tags=["runs"])
    async def cancel_run(request: Request, run_id: str) -> Response:
        return await cancel(request, run_id)

    @app.get("/v1/runs/{run_id}/items", tags=["runs", "traces"])
    async def list_run_items(
        request: Request,
        run_id: str,
        stage_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)

        def run() -> tuple[list[dict[str, Any]], str | None]:
            with holder["core"].db.conn() as conn:
                result: tuple[list[dict[str, Any]], str | None] = admin().runs.list_items(
                    conn, run_id, stage_id=stage_id, status=status, cursor=cursor, limit=lim(limit)
                )
                return result

        return page(*await threaded(run))

    @app.get("/v1/materials/{material_id}/trace", tags=["traces"])
    async def material_trace(request: Request, material_id: str) -> dict[str, Any]:
        principal(request, READ)

        def run() -> dict[str, Any]:
            with holder["core"].db.conn() as conn:
                result: dict[str, Any] = admin().runs.trace(conn, material_id)
                return result

        return await threaded(run)

    @app.get("/v1/jobs/{job_id}", tags=["jobs"])
    async def get_job(request: Request, job_id: str) -> dict[str, Any]:
        principal(request, READ)

        def run() -> dict[str, Any]:
            with holder["core"].db.conn() as conn:
                row = conn.execute("SELECT * FROM runs WHERE run_id = %s", (job_id,)).fetchone()
                if row is None:
                    raise NotFound(f"job '{job_id}' not found")
                result: dict[str, Any] = admin().runs.job_view(conn, row)
                return result

        return await threaded(run)

    @app.post("/v1/jobs/{job_id}/cancel", tags=["jobs"])
    async def cancel_job(request: Request, job_id: str) -> Response:
        return await cancel(request, job_id)

    @app.post("/v1/reprocessing", tags=["runs"], status_code=202)
    async def reprocess(request: Request) -> Response:
        p = principal(request, WRITE)
        body = await body_json(request)
        validate("POST", "/v1/reprocessing", body)
        key = request.headers.get(IDEMPOTENCY_HEADER)

        def run() -> StoredResponse:
            job = admin().start_reprocessing(body, p.name, key)
            return StoredResponse(202, job, {"Location": job["links"]["self"]})

        return await idem(request, run)

    # ------------------------------------------------------------------ problems
    @app.get("/v1/unknown-materials", tags=["problems"])
    async def list_unknown(
        request: Request,
        source_id: str | None = None,
        forwarded: bool | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(*await threaded(admin().list_unknown, source_id, forwarded, cursor, lim(limit)))

    @app.get("/v1/problem-groups", tags=["problems"])
    async def list_problem_groups(
        request: Request,
        source_id: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(*await threaded(admin().list_problem_groups, source_id, status, cursor, lim(limit)))

    @app.patch("/v1/problem-groups/{group_id}", tags=["problems"])
    async def update_problem_group(request: Request, group_id: str) -> dict[str, Any]:
        p = principal(request, WRITE)
        body = await body_json(request)
        holder["core"].schemas.validate_request(
            "PATCH", "/v1/problem-groups/x", body, "application/merge-patch+json"
        )
        result: dict[str, Any] = await threaded(admin().update_problem_group, group_id, body, p.name)
        return result

    # ------------------------------------------------------------------ connections
    @app.get("/v1/connections", tags=["connections"])
    async def list_connections(
        request: Request,
        kind: str | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(*await threaded(admin().list_connections, kind, cursor, lim(limit)))

    @app.get("/v1/connections/{connection_id}", tags=["connections"])
    async def get_connection(request: Request, connection_id: str) -> Response:
        principal(request, READ)
        doc, version = await threaded(admin().get_connection, connection_id)
        return with_etag(doc, version)

    @app.put("/v1/connections/{connection_id}", tags=["connections"])
    async def put_connection(request: Request, connection_id: str) -> Response:
        p = principal(request, ADMIN)
        body = await body_json(request)
        validate("PUT", "/v1/connections/x", body)
        doc, version = await threaded(
            admin().put_connection, connection_id, body, request.headers.get("if-match"), p.name
        )
        return with_etag(doc, version)

    @app.delete("/v1/connections/{connection_id}", tags=["connections"], status_code=204)
    async def delete_connection(request: Request, connection_id: str) -> Response:
        p = principal(request, ADMIN)
        await threaded(admin().delete_connection, connection_id, p.name)
        return Response(status_code=204)

    # ------------------------------------------------------------------ limits, executors, audit
    @app.get("/v1/limits/platform", tags=["limits"])
    async def get_platform_limits(request: Request) -> Response:
        principal(request, READ)
        doc, version = await threaded(admin().get_platform_limits)
        return with_etag(doc, version)

    @app.put("/v1/limits/platform", tags=["limits"])
    async def put_platform_limits(request: Request) -> Response:
        p = principal(request, ADMIN)
        body = await body_json(request)
        validate("PUT", "/v1/limits/platform", body)
        doc, version = await threaded(
            admin().put_platform_limits, body, request.headers.get("if-match"), p.name
        )
        return with_etag(doc, version)

    @app.get("/v1/limits/effective", tags=["limits"])
    async def effective_limits(
        request: Request,
        source_id: str | None = None,
        task_id: str | None = None,
        stage_id: str | None = None,
    ) -> dict[str, Any]:
        principal(request, READ)
        result: dict[str, Any] = await threaded(admin().effective_limits, source_id, task_id, stage_id)
        return result

    @app.get("/v1/executors", tags=["system"])
    async def list_executors(request: Request) -> dict[str, Any]:
        principal(request, READ)
        return {"items": await threaded(admin().list_executors)}

    @app.get("/v1/audit-events", tags=["audit"])
    async def list_audit(
        request: Request,
        subject_type: str | None = None,
        subject_id: str | None = None,
        cursor: str | None = None,
        limit: int | None = Query(None, ge=1),
    ) -> dict[str, Any]:
        principal(request, READ)
        return page(*await threaded(admin().list_audit, subject_type, subject_id, cursor, lim(limit)))

    return app
