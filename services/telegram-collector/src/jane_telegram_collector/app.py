"""HTTP API ``collector.v1`` of the Telegram Collector (``contracts/openapi/collector.v1.yaml``).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit; the rest is here. The
service is autonomous: rules inline, from a local package or from the registry; materials are pulled with
a cursor; nothing calls the orchestrator.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sqlite3
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Header, Query, Request, Response
from fastapi.responses import JSONResponse

from jane_kit.errors import FieldError, JaneError, NotFound, ValidationFailed, problem_response
from jane_kit.idempotency import StoredResponse, idempotent
from jane_kit.jobs import JobRunner, jobs_router
from jane_kit.pagination import clamp_limit, decode_cursor, encode_cursor
from jane_kit.service import create_app

from . import __version__
from .client import load_factory
from .connections import check_params, connection_etag, resolved_map
from .engine import Engine
from .materials import rfc3339
from .rules import ContractSchemas, validate_rules
from .settings import Settings, resolve_service_limits
from .state import StateStore
from .stores import SqliteIdempotencyStore, SqliteJobStore

log = logging.getLogger(__name__)

CURSOR_RE = re.compile(r"^c_(\d{1,18})$")
TERMINAL = {"succeeded", "failed", "cancelled"}


def _cursor(seq: int) -> str:
    return f"c_{seq:016d}"


def _parse_after(after: str | None) -> int | None:
    if after is None:
        return None
    m = CURSOR_RE.match(after)
    if not m:
        raise ValidationFailed(
            "invalid cursor", errors=[FieldError(parameter="after", message="invalid cursor")]
        )
    return int(m.group(1))


def _now() -> str:
    return rfc3339(datetime.now(UTC))


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    state = StateStore(settings.state_dir / "state.db", busy_timeout_ms=settings.state_busy_timeout_ms)
    schemas = ContractSchemas.locate(settings.contracts_dir)
    factory = load_factory(settings)
    policy = settings.connection_policy()
    runner = JobRunner(store=SqliteJobStore(state, settings.instance_id), limits=limits.jobs)
    idem_store = SqliteIdempotencyStore(state)
    engine = Engine(settings, resolved, state, factory, schemas, runner)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        log.info(
            "configured limits",
            extra={"limits": resolved.effective(), "client_backend": factory.name, "state": str(state.path)},
        )
        await engine.resume_pending()
        await engine.start()
        yield
        await engine.stop()
        state.close()

    app = create_app(
        settings,
        title="Jane Telegram Collector",
        version=__version__,
        lifespan=lifespan,
        capabilities=engine.capabilities,
        limits=resolved,
    )
    app.state.limits = resolved
    app.state.engine = engine
    app.state.store = state

    async def state_check() -> tuple[str, str | None]:
        state.ping()
        return "ok", None

    app.state.health.add("state_store", state_check)

    async def state_busy(request: Request, exc: Exception) -> JSONResponse:
        # another instance held the SQLite lock longer than state_busy_timeout_ms: retryable, not a 500
        log.warning("state store busy", extra={"path": request.url.path, "error": str(exc)})
        err = JaneError("state store is busy, retry", code="service_unavailable", retry_after_seconds=1)
        return problem_response(err.to_problem(instance=request.url.path), err.headers)

    app.add_exception_handler(sqlite3.OperationalError, state_busy)
    app.include_router(jobs_router(runner))

    async def json_body(request: Request) -> Any:
        raw = await request.body()
        try:
            return json.loads(raw) if raw else None
        except ValueError as exc:
            raise JaneError("request body is not valid JSON", code="bad_request") from exc

    # ------------------------------------------------------------------ fetch
    @app.post("/v1/fetches", tags=["fetch"], response_model=None)
    async def fetch_material(request: Request) -> JSONResponse:
        return JSONResponse(await engine.fetch_one(await json_body(request)))

    # ------------------------------------------------------------------ collections
    @app.post("/v1/collections", status_code=202, tags=["collections"], response_model=None)
    async def start_collection(request: Request) -> Response:
        payload = await json_body(request)

        async def handler() -> StoredResponse:
            job = await engine.start_collection(payload)
            return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    def _record(collection_id: str) -> dict[str, Any]:
        record = state.get_collection(collection_id)
        if record is None:
            raise NotFound(f"collection {collection_id} not found")
        if record.get("expired"):
            raise JaneError(
                "collection expired after job_retention_seconds",
                code="not_found",
                status=410,
                title="Collection expired",
            )
        return record

    @app.get("/v1/collections/{collection_id}", tags=["collections"], response_model=None)
    async def get_collection(collection_id: str) -> JSONResponse:
        _record(collection_id)
        return JSONResponse(engine.collection_view(collection_id))

    @app.get("/v1/collections/{collection_id}/materials", tags=["collections"], response_model=None)
    async def list_materials(
        collection_id: str,
        after: str | None = Query(default=None, max_length=2048),
        limit: int | None = Query(default=None, ge=1),
        wait_ms: int | None = Query(default=None, ge=0),
    ) -> JSONResponse:
        record = _record(collection_id)
        page_size = clamp_limit(limit, limits.page)
        after_seq = _parse_after(after)
        if after_seq is not None and after_seq > state.emitted_count(collection_id):
            # a cursor that was never issued would silently acknowledge materials nobody has seen
            raise ValidationFailed(
                "cursor is ahead of the last delivered material",
                errors=[FieldError(parameter="after", message="unknown cursor")],
            )
        if after_seq is not None and after_seq > int(record["acked_seq"]):
            state.ack(collection_id, after_seq)
            engine.acked(collection_id)
        start = max(after_seq or 0, int(record["acked_seq"]))
        deadline = time.monotonic() + min(wait_ms or 0, limits.collector.max_wait_ms) / 1000
        while True:
            items = state.materials_after(collection_id, start, page_size + 1)
            status = engine.collection_view(collection_id)["status"]
            if items or status in TERMINAL or time.monotonic() >= deadline:
                break
            await asyncio.sleep(limits.collector.long_poll_interval_ms / 1000)
        more = len(items) > page_size
        items = items[:page_size]
        if items:
            next_cursor: str | None = _cursor(items[-1][0])
        elif after is not None:
            next_cursor = after
        else:
            next_cursor = _cursor(start) if start else None
        if status not in TERMINAL:  # re-read after listing: the run may have finished meanwhile
            status = engine.collection_view(collection_id)["status"]
            more = more or bool(state.materials_after(collection_id, items[-1][0] if items else start, 1))
        return JSONResponse(
            {
                "items": [m for _, m in items],
                "next_cursor": next_cursor,
                "end_of_stream": status in TERMINAL and not more,
                "collection_status": status,
            }
        )

    @app.get("/v1/collections/{collection_id}/errors", tags=["collections"], response_model=None)
    async def list_errors(
        collection_id: str,
        cursor: str | None = Query(default=None, max_length=2048),
        limit: int | None = Query(default=None, ge=1),
    ) -> JSONResponse:
        _record(collection_id)
        page_size = clamp_limit(limit, limits.page)
        try:
            after = int(decode_cursor(cursor)) if cursor else 0
        except (ValueError, TypeError) as exc:
            raise ValidationFailed(
                "invalid cursor", errors=[FieldError(parameter="cursor", message="invalid cursor")]
            ) from exc
        rows = state.errors_after(collection_id, after, page_size + 1)
        more = len(rows) > page_size
        rows = rows[:page_size]
        return JSONResponse(
            {
                "items": [e for _, e in rows],
                "next_cursor": encode_cursor(rows[-1][0]) if more and rows else None,
            }
        )

    # ------------------------------------------------------------------ rules
    @app.post("/v1/rules/validations", tags=["rules"], response_model=None)
    async def validate(request: Request) -> JSONResponse:
        return JSONResponse(validate_rules(schemas, await json_body(request)).wire())

    # ------------------------------------------------------------------ state
    @app.get("/v1/states/{state_key}", tags=["state"], response_model=None)
    async def get_state(state_key: str) -> JSONResponse:
        summary = state.state_summary(state_key)
        if summary is None:
            raise NotFound(f"no state for {state_key}")
        return JSONResponse(
            {
                "state_key": state_key,
                "collector": "telegram",
                "updated_at": summary["updated_at"],
                "cursors": summary["cursors"],
            }
        )

    @app.delete("/v1/states/{state_key}", status_code=204, tags=["state"], response_model=None)
    async def reset_state(state_key: str) -> Response:
        if state.active_for_state_key(state_key):
            raise JaneError(f"state {state_key} is used by a running collection", code="conflict")
        state.delete_state(state_key)
        return Response(status_code=204)

    # ------------------------------------------------------------------ connections
    @app.get("/v1/connections", tags=["connections"], response_model=None)
    async def list_connections(
        cursor: str | None = Query(default=None, max_length=2048),
        limit: int | None = Query(default=None, ge=1),
    ) -> JSONResponse:
        page_size = clamp_limit(limit, limits.page)
        after = str(decode_cursor(cursor)) if cursor else None
        items = state.list_connections(after, page_size + 1)
        more = len(items) > page_size
        items = items[:page_size]
        return JSONResponse(
            {
                "items": items,
                "next_cursor": encode_cursor(items[-1]["connection_id"]) if more and items else None,
            }
        )

    @app.get("/v1/connections/{connection_id}", tags=["connections"], response_model=None)
    async def get_connection(connection_id: str) -> JSONResponse:
        found = state.get_connection(connection_id)
        if found is None:
            raise NotFound(f"connection {connection_id} not found")
        return JSONResponse(found[0], headers={"ETag": found[1]})

    @app.put("/v1/connections/{connection_id}", tags=["connections"], response_model=None)
    async def put_connection(
        connection_id: str,
        request: Request,
        if_match: str | None = Header(default=None, alias="If-Match"),
    ) -> JSONResponse:
        payload = await json_body(request)
        errors = schemas.errors(
            f"{schemas.root.resolve().as_uri()}/schemas/common/connection.schema.json", payload
        )
        if errors:
            raise ValidationFailed("connection does not match the contract", errors=errors)
        if payload["connection_id"] != connection_id:
            raise ValidationFailed(
                "connection_id in the body differs from the path",
                errors=[FieldError(pointer="/connection_id", message="must equal the path parameter")],
            )
        check_params(payload, policy)
        current = state.get_connection(connection_id)
        if if_match is not None and (current is None or current[1] != if_match):
            raise JaneError("If-Match does not match the current ETag", code="precondition_failed")
        etag = connection_etag(payload)
        created = state.put_connection(connection_id, payload, etag)
        return JSONResponse(payload, status_code=201 if created else 200, headers={"ETag": etag})

    @app.delete("/v1/connections/{connection_id}", status_code=204, tags=["connections"], response_model=None)
    async def delete_connection(connection_id: str) -> Response:
        if not state.delete_connection(connection_id):
            raise NotFound(f"connection {connection_id} not found")
        return Response(status_code=204)

    @app.post("/v1/connections/{connection_id}/test", tags=["connections"], response_model=None)
    async def test_connection(connection_id: str) -> JSONResponse:
        found = state.get_connection(connection_id)
        if found is None:
            raise NotFound(f"connection {connection_id} not found")
        started = time.perf_counter()
        secrets = resolved_map(found[0], policy)
        ok = all(secrets.values())
        body: dict[str, Any] = {
            "ok": ok,
            "checked_at": _now(),
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "secrets_resolved": secrets,
        }
        if not ok:
            body["message"] = "some secret_refs are not resolvable in this collector's environment"
        return JSONResponse(body)

    return app
