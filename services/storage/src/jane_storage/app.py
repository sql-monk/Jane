"""HTTP API of the storage service.

* ``handler.v1`` (write path): ``POST /v1/invocations``, ``GET /v1/invocations/{id}``,
  ``POST /v1/test-runs``, ``/v1/connections*``, ``/v1/jobs/*``;
* ``storage.v1`` (read path): ``/v1/entities``, ``/v1/entity-history``, ``/v1/objects*``;
* ``/v1/health``, ``/v1/info``, ``/metrics`` from jane-kit.

Idempotency: ``Idempotency-Key`` must equal ``delivery.delivery_key``. The durable deduplication is the
delivery record kept by the adapter together with the data (works across instances and restarts);
the in-memory key store only rejects a reused key with a different body (422) and a concurrent
duplicate (409). A repeated delivery is executed again and returns the stored acks with
``duplicate: true`` (``Idempotency-Replayed: true`` if this instance saw the key).
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import re
from collections import OrderedDict
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from jsonschema import Draft202012Validator

from jane_contracts.storage_adapter import AdapterError, EntitySnapshot, HistoryEvent, ObjectRecord
from jane_kit.config import LimitError, LimitLayer
from jane_kit.contracts import ContractViolation, OpenAPISpec, contracts_dir
from jane_kit.errors import FieldError, JaneError, NotFound, ValidationFailed
from jane_kit.idempotency import (
    IDEMPOTENCY_HEADER,
    REPLAY_HEADER,
    IdempotencyInProgress,
    IdempotencyKeyReused,
    InMemoryIdempotencyStore,
    StoredResponse,
)
from jane_kit.jobs import JobContext, JobRunner, accepted, jobs_router
from jane_kit.pagination import clamp_limit
from jane_kit.service import create_app

from . import __version__
from .adapters import available_adapters
from .codec import format_ts, snapshot_to_json
from .connections import AdapterPool, ConnectionRegistry
from .content import ContentReader
from .handler import StorageHandler
from .packages import PackageCatalog, StoragePackage
from .settings import ServiceLimits, Settings, resolve_service_limits

log = logging.getLogger(__name__)

REQUEST_LIMIT_PATHS = {
    "retries",
    "timeouts.sync_response_max_ms",
    "timeouts.request_timeout_ms",
}
"""Parts of ``HandlerInvocation.limits`` this executor applies (min with its own hard caps)."""


def _request_layer(limits: Mapping[str, Any] | None) -> LimitLayer | None:
    if not limits:
        return None
    picked: dict[str, Any] = {}
    if isinstance(limits.get("retries"), Mapping):
        picked["retries"] = dict(limits["retries"])
    timeouts = {
        k: v for k, v in dict(limits.get("timeouts") or {}).items() if f"timeouts.{k}" in REQUEST_LIMIT_PATHS
    }
    if timeouts:
        picked["timeouts"] = timeouts
    return LimitLayer("request", picked, name="invocation") if picked else None


def _fingerprint(body: Mapping[str, Any]) -> str:
    """Request identity for the idempotency key: everything but ``context`` (attempt, trace)."""
    stable = {k: v for k, v in body.items() if k != "context"}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def entity_state(snap: EntitySnapshot) -> dict[str, Any]:
    doc = snapshot_to_json(snap)
    doc["updated_at"] = format_ts(snap.updated_at)
    return doc


def history_entry(event: HistoryEvent) -> dict[str, Any]:
    return {
        "record": dict(event.record),
        "received_at": format_ts(event.received_at),
        "delivery_key": event.delivery_key,
        "applied_fields": list(event.applied_fields),
        "stale_fields": list(event.stale_fields),
    }


class InvocationResults:
    """Recent HandlerResults of this instance (``GET /v1/invocations/{id}``)."""

    def __init__(self, max_entries: int) -> None:
        self.max_entries = max_entries
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def put(self, result: dict[str, Any]) -> None:
        self._items[result["invocation_id"]] = result
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    def get(self, invocation_id: str) -> dict[str, Any]:
        try:
            return self._items[invocation_id]
        except KeyError:
            raise NotFound(f"invocation {invocation_id} not found on this instance") from None


def _request_validator(root: Path | None) -> Any:
    if root is None or not (root / "openapi" / "handler.v1.yaml").is_file():
        log.warning("contracts not found: HandlerInvocation is validated by the core checks only")
        return None
    spec = OpenAPISpec.load(root / "openapi" / "handler.v1.yaml")

    def validate(body: dict[str, Any]) -> list[FieldError]:
        try:
            spec.validate_request("post", "/v1/invocations", body)
        except ContractViolation as exc:
            return [FieldError(pointer="/", message=str(exc)[:2000])]
        return []

    return validate


def _connection_validator(root: Path | None) -> Any:
    if root is None or not (root / "schemas" / "common" / "connection.schema.json").is_file():
        return None
    schema = json.loads((root / "schemas" / "common" / "connection.schema.json").read_text(encoding="utf-8"))
    schema.pop("$defs", None)
    schema["properties"]["kind"] = {"type": "string", "pattern": "^[a-z][a-z0-9_]{1,31}$"}
    schema["properties"]["secret_refs"] = {
        "type": "object",
        "additionalProperties": {
            "type": "string",
            "pattern": "^(env:[A-Z_][A-Z0-9_]{0,127}|file:.{1,512}|vault:[^#]{1,512}#[A-Za-z0-9_.-]{1,128})$",
        },
    }
    schema["properties"]["connection_id"] = {
        "type": "string",
        "pattern": "^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$",
    }
    schema["properties"]["labels"] = {"type": "object"}
    return Draft202012Validator(schema)


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    resolved = resolve_service_limits(settings)
    limits: ServiceLimits = resolved.limits
    runner = JobRunner(limits=limits.jobs)
    keys = InMemoryIdempotencyStore(limits.idempotency)
    root = contracts_dir(Path(__file__).parent) if settings.validate_requests else None
    registry = ConnectionRegistry(validator=_connection_validator(root), policy=settings.connection_policy())
    if settings.connections_file is not None:
        registry.load_file(settings.connections_file)
    pool = AdapterPool(registry, limits.adapters.model_dump())
    catalog = PackageCatalog.discover(settings.package_dirs)

    async def transit() -> Any:
        if settings.transit_connection_id is None:
            return None
        return registry.resolve(settings.transit_connection_id)

    def handler_for(lim: ServiceLimits) -> StorageHandler:
        reader = ContentReader(
            max_bytes=lim.objects.max_object_bytes,
            request_timeout_ms=lim.timeouts.request_timeout_ms,
            transit=transit,
        )
        return StorageHandler(
            catalog, pool, reader, retries=lim.retries, request_validator=_request_validator(root)
        )

    default_handler = handler_for(limits)
    results = InvocationResults(limits.invocations.max_results_in_memory)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        log.info("configured limits", extra={"limits": resolved.effective()})
        log.info(
            "storage ready",
            extra={
                "adapters": sorted(available_adapters()),
                "packages": [f"{p.package_id}@{p.version}" for p in catalog.all()],
                "connections": [c.connection_id for c in registry.list()],
            },
        )
        yield
        await runner.shutdown()
        await pool.close()

    def capabilities() -> dict[str, Any]:
        return {
            "handler_kinds": ["storage"],
            "adapters": sorted(available_adapters()),
            "packages": [p.ref for p in catalog.all()],
            "connections": True,
            "test_mode": True,
        }

    app = create_app(
        settings,
        title="Storage",
        version=__version__,
        lifespan=lifespan,
        capabilities=capabilities,
        limits=resolved,
    )
    app.state.limits = resolved
    app.state.registry = registry
    app.state.pool = pool
    app.state.catalog = catalog
    app.include_router(jobs_router(runner))
    writes_total = (
        app.state.metrics.counter(
            "storage_writes_total", "WriteAcks by adapter and status", ["adapter", "status"]
        )
        if settings.metrics_enabled
        else None
    )
    failures_total = (
        app.state.metrics.counter("storage_failed_invocations_total", "Failed invocations by kind", ["kind"])
        if settings.metrics_enabled
        else None
    )

    def observe(result: Mapping[str, Any]) -> None:
        results.put(dict(result))
        if writes_total is not None:
            for ack in (result.get("output") or {}).get("writes") or ():
                writes_total.labels(ack["target"]["adapter"], ack["status"]).inc()
        if failures_total is not None and result["status"] == "failed":
            failures_total.labels(result["failure"]["kind"]).inc()

    async def read_body(request: Request) -> Any:
        declared = request.headers.get("content-length")
        cap = limits.transfer.max_request_body_bytes
        if declared is not None and declared.isdigit() and int(declared) > cap:
            raise JaneError(f"body exceeds transfer.max_request_body_bytes={cap}", code="payload_too_large")
        raw = await request.body()
        if len(raw) > cap:
            raise JaneError(f"body exceeds transfer.max_request_body_bytes={cap}", code="payload_too_large")
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise JaneError("request body is not valid JSON", code="bad_request") from exc

    # ------------------------------------------------------------------ handler.v1
    @app.post("/v1/invocations", tags=["invocations"])
    async def invoke(request: Request) -> Response:
        body = await read_body(request)
        if not isinstance(body, dict):
            raise ValidationFailed(
                "HandlerInvocation must be an object", errors=[FieldError(pointer="/", message="object")]
            )
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if key is None:
            raise ValidationFailed(
                f"{IDEMPOTENCY_HEADER} header is required",
                errors=[FieldError(parameter=IDEMPOTENCY_HEADER, message="required")],
            )
        delivery_key = (body.get("delivery") or {}).get("delivery_key")
        if delivery_key is not None and key != delivery_key:
            raise ValidationFailed(
                f"{IDEMPOTENCY_HEADER} must equal delivery.delivery_key",
                errors=[
                    FieldError(parameter=IDEMPOTENCY_HEADER, message="differs from delivery.delivery_key")
                ],
            )
        try:
            layer = _request_layer(body.get("limits"))
            lim = resolve_service_limits(settings, layer).limits if layer else limits
        except LimitError as exc:
            raise ValidationFailed(
                str(exc), errors=[FieldError(pointer="/limits", message=str(exc))]
            ) from exc
        handler = handler_for(lim) if layer else default_handler
        prepared = await handler.prepare(body)

        fp = _fingerprint(body)
        existing = await keys.begin(key, fp, float(limits.idempotency.idempotency_ttl_seconds))
        replayed = False
        if existing is not None:
            if existing.fingerprint != fp:
                raise IdempotencyKeyReused("the key was used with a different request")
            if existing.state != "completed":
                raise IdempotencyInProgress("a request with this key is still running")
            replayed = True
        headers = {REPLAY_HEADER: "true"} if replayed else {}

        async def work(ctx: JobContext) -> dict[str, Any]:
            try:
                result = await handler.execute(prepared)
            except BaseException:
                if not replayed:
                    await keys.release(key)
                raise
            observe(result)
            if not replayed:
                await keys.complete(key, StoredResponse(200, {"invocation_id": result["invocation_id"]}))
            return result

        job = await runner.submit("storage_invocation", work, idempotency_key=key)
        if body.get("mode") == "async":
            return accepted(job, runner.location(job.job_id), headers)
        timeout = lim.timeouts.sync_response_max_ms / 1000
        try:
            done = await asyncio.wait_for(asyncio.shield(runner.wait(job.job_id)), timeout)
        except TimeoutError:
            return accepted(await runner.get(job.job_id), runner.location(job.job_id), headers)
        if done.result is None:
            if done.error is not None:
                raise JaneError(done.error.detail or done.error.title, code=done.error.code)
            raise JaneError("invocation did not produce a result")
        return JSONResponse(done.result, headers=headers)

    @app.get("/v1/invocations/{invocation_id}", tags=["invocations"])
    async def get_invocation(invocation_id: str) -> JSONResponse:
        return JSONResponse(results.get(invocation_id))

    @app.post("/v1/test-runs", status_code=202, tags=["tests"])
    async def test_run(request: Request) -> Response:
        body = await read_body(request)
        if request.headers.get(IDEMPOTENCY_HEADER) is None:
            raise ValidationFailed(
                f"{IDEMPOTENCY_HEADER} header is required",
                errors=[FieldError(parameter=IDEMPOTENCY_HEADER, message="required")],
            )
        ref = body.get("handler") or {}
        pkg = catalog.get(str(ref.get("package_id")), str(ref.get("version")))
        if pkg is None:
            raise NotFound(f"{ref.get('package_id')}@{ref.get('version')}")
        cases = manifest_test_cases(pkg, body)

        async def work(ctx: JobContext) -> dict[str, Any]:
            report = []
            started = format_ts(datetime.now().astimezone())
            for i, (name, invocation, expected) in enumerate(cases):
                await ctx.check_cancelled()
                try:
                    result = await default_handler.invoke(invocation)
                except JaneError as exc:
                    report.append(
                        {
                            "name": name,
                            "passed": False,
                            "expected_status": expected,
                            "differences": [{"pointer": "/", "expected": expected, "actual": exc.error_code}],
                        }
                    )
                    continue
                passed = result["status"] == expected
                report.append(
                    {
                        "name": name,
                        "passed": passed,
                        "expected_status": expected,
                        "actual_status": result["status"],
                        "result": result,
                    }
                )
                await ctx.progress(i + 1, len(cases), unit="cases")
            return {
                "package": pkg.ref,
                "passed": sum(1 for r in report if r["passed"]),
                "failed": sum(1 for r in report if not r["passed"]),
                "cases": report,
                "started_at": started,
                "finished_at": format_ts(datetime.now().astimezone()),
            }

        job = await runner.submit(
            "storage_test_run", work, idempotency_key=request.headers.get(IDEMPOTENCY_HEADER)
        )
        return accepted(job, runner.location(job.job_id))

    # ------------------------------------------------------------------ connections
    def connection_body(doc: Mapping[str, Any]) -> dict[str, Any]:
        return {
            k: v
            for k, v in doc.items()
            if k in {"connection_id", "kind", "title", "params", "secret_refs", "labels"}
        }

    @app.get("/v1/connections", tags=["connections"])
    async def list_connections(limit: int | None = None, cursor: str | None = None) -> JSONResponse:
        items = registry.list()
        if cursor:
            items = [c for c in items if c.connection_id > cursor]
        size = clamp_limit(limit, limits.pages)
        page = items[:size]
        next_cursor = page[-1].connection_id if len(items) > size and page else None
        return JSONResponse(
            {"items": [connection_body(c.document) for c in page], "next_cursor": next_cursor}
        )

    @app.get("/v1/connections/{connection_id}", tags=["connections"])
    async def get_connection(connection_id: str) -> JSONResponse:
        stored = registry.get(connection_id)
        return JSONResponse(connection_body(stored.document), headers={"ETag": stored.etag})

    @app.put("/v1/connections/{connection_id}", tags=["connections"])
    async def put_connection(connection_id: str, request: Request) -> JSONResponse:
        body = await read_body(request)
        if not isinstance(body, dict) or body.get("connection_id") != connection_id:
            raise ValidationFailed(
                "connection_id in the body must match the path",
                errors=[FieldError(pointer="/connection_id", message="must match the path")],
            )
        if_match = request.headers.get("if-match")
        if if_match is not None:
            try:
                current = registry.get(connection_id).etag
            except NotFound:
                current = None
            if if_match != "*" and if_match != current:
                raise JaneError("ETag does not match", code="precondition_failed")
        stored, created = registry.put(body)
        await pool.forget(connection_id)
        return JSONResponse(
            connection_body(stored.document),
            status_code=201 if created else 200,
            headers={"ETag": stored.etag},
        )

    @app.delete("/v1/connections/{connection_id}", status_code=204, tags=["connections"])
    async def delete_connection(connection_id: str) -> Response:
        registry.delete(connection_id)
        await pool.forget(connection_id)
        return Response(status_code=204)

    @app.post("/v1/connections/{connection_id}/test", tags=["connections"])
    async def test_connection(connection_id: str) -> JSONResponse:
        stored = registry.get(connection_id)
        started = asyncio.get_running_loop().time()
        resolved_secrets = registry.secrets_resolved(connection_id)
        out: dict[str, Any] = {
            "ok": False,
            "checked_at": format_ts(datetime.now().astimezone()),
            "secrets_resolved": resolved_secrets,
        }
        violations = registry.policy_errors(connection_id)
        if violations:
            # config file / bypassing the API: no secret is read and the adapter is not opened
            out["message"] = "connection violates the secret policy of this executor: " + "; ".join(
                f"{v.pointer} ({v.code}): {v.message}" for v in violations
            )
            return JSONResponse(out)
        if not all(resolved_secrets.values()):
            missing = sorted(k for k, v in resolved_secrets.items() if not v)
            out["message"] = f"secret(s) not resolvable in this executor: {missing}"
            return JSONResponse(out)
        try:
            adapter = await pool.adapter_for(connection_id, stored.kind, {})
            out["ok"] = await adapter.health()
        except (AdapterError, JaneError) as exc:
            out["message"] = str(exc)[:1000]
        out["latency_ms"] = int((asyncio.get_running_loop().time() - started) * 1000)
        return JSONResponse(out)

    # ------------------------------------------------------------------ storage.v1
    async def reader(connection_id: str) -> Any:
        stored = registry.get(connection_id)
        registry.ensure_allowed(connection_id, parameter="connection_id")
        try:
            return await pool.adapter_for(connection_id, stored.kind, {})
        except AdapterError as exc:
            raise JaneError(str(exc), code="upstream_unavailable", retryable=exc.retryable) from exc

    async def call(coro: Any) -> Any:
        try:
            return await coro
        except AdapterError as exc:
            if exc.retryable:
                raise JaneError(str(exc), code="upstream_unavailable", retryable=True) from exc
            raise ValidationFailed(
                str(exc), errors=[FieldError(parameter="cursor", message=str(exc))]
            ) from exc

    @app.get("/v1/entities", tags=["entities"])
    async def list_entities(
        connection_id: str,
        entity_type: str,
        scope: str | None = None,
        key: str | None = None,
        updated_since: datetime | None = None,
        cursor: str | None = None,
        limit: int | None = Query(default=None, ge=1),
    ) -> JSONResponse:
        adapter = await reader(connection_id)
        if key is not None:
            snap = await call(adapter.read_entity(entity_type, key))
            items = [snap] if snap is not None and (scope is None or snap.key.get("scope") == scope) else []
            return JSONResponse({"items": [entity_state(s) for s in items], "next_cursor": None})
        page, next_cursor = await call(
            adapter.list_entities(
                entity_type,
                scope=scope,
                updated_since=updated_since,
                cursor=cursor,
                limit=clamp_limit(limit, limits.pages),
            )
        )
        return JSONResponse({"items": [entity_state(s) for s in page], "next_cursor": next_cursor})

    @app.get("/v1/entity-history", tags=["entities"])
    async def list_history(
        connection_id: str,
        entity_type: str,
        key: str,
        cursor: str | None = None,
        limit: int | None = Query(default=None, ge=1),
    ) -> JSONResponse:
        adapter = await reader(connection_id)
        if await call(adapter.read_entity(entity_type, key)) is None:
            raise NotFound(f"entity {entity_type} {key!r} not found")
        page, next_cursor = await call(
            adapter.list_history(entity_type, key, cursor=cursor, limit=clamp_limit(limit, limits.pages))
        )
        return JSONResponse({"items": [history_entry(e) for e in page], "next_cursor": next_cursor})

    def object_ref(rec: ObjectRecord, adapter_kind: str, connection_id: str) -> dict[str, Any]:
        return {
            "object_id": rec.object_id,
            "adapter": adapter_kind,
            "connection_id": connection_id,
            "locator": dict(rec.locator),
            "media_type": rec.media_type,
            "size_bytes": rec.size_bytes,
            "sha256": rec.sha256,
        }

    def material_summary(meta: Mapping[str, Any]) -> dict[str, Any]:
        out = {
            "material_id": meta.get("material_id"),
            "observation_id": meta.get("observation_id"),
            "source_id": meta.get("source_id") or (meta.get("source") or {}).get("source_id"),
            "url": (meta.get("locator") or {}).get("url"),
            "fetched_at": meta.get("fetched_at"),
        }
        return {k: v for k, v in out.items() if v is not None}

    @app.get("/v1/objects", tags=["objects"])
    async def list_objects(
        connection_id: str,
        source_id: str | None = None,
        material_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        cursor: str | None = None,
        limit: int | None = Query(default=None, ge=1),
    ) -> JSONResponse:
        adapter = await reader(connection_id)
        page, next_cursor = await call(
            adapter.list_objects(
                source_id=source_id,
                material_id=material_id,
                since=since,
                until=until,
                cursor=cursor,
                limit=clamp_limit(limit, limits.pages),
            )
        )
        items = [
            {
                "object": object_ref(rec, adapter.kind, connection_id),
                "material": material_summary(rec.metadata),
                "stored_at": format_ts(rec.stored_at),
            }
            for rec in page
        ]
        return JSONResponse({"items": items, "next_cursor": next_cursor})

    async def get_record(adapter: Any, object_id: str) -> ObjectRecord:
        rec: ObjectRecord | None = await call(adapter.get_object(object_id))
        if rec is None:
            raise NotFound(f"object {object_id} not found")
        return rec

    @app.get("/v1/objects/{object_id}", tags=["objects"])
    async def get_object(object_id: str, connection_id: str) -> JSONResponse:
        adapter = await reader(connection_id)
        rec = await get_record(adapter, object_id)
        out: dict[str, Any] = {
            "object": object_ref(rec, adapter.kind, connection_id),
            "stored_at": format_ts(rec.stored_at),
        }
        meta = dict(rec.metadata)
        if "material_id" in meta and "fetched_at" in meta and isinstance(meta.get("content"), Mapping):
            material = {k: v for k, v in meta.items() if k not in {"source_id", "stored_format", "format"}}
            material["format"] = (
                meta.get("format")
                if isinstance(meta.get("format"), Mapping)
                else {"media_type": rec.media_type}
            )
            content_uri = getattr(adapter, "content_uri", None)
            uri = content_uri(rec) if callable(content_uri) else None
            if uri is not None:
                material["content"] = {
                    "kind": "blob",
                    "uri": uri,
                    "media_type": rec.media_type,
                    "size_bytes": rec.size_bytes,
                    "sha256": rec.sha256,
                    "store": "persistent",
                    "expires_at": None,
                }
            elif rec.size_bytes <= limits.transfer.inline_max_bytes:
                data = await call(adapter.read_object_content(object_id))
                try:
                    inline = {"encoding": "utf-8", "data": data.decode("utf-8")}
                except UnicodeDecodeError:
                    inline = {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
                material["content"] = {
                    "kind": "inline",
                    "media_type": rec.media_type,
                    **inline,
                    "size_bytes": rec.size_bytes,
                    "sha256": rec.sha256,
                }
            else:
                material = {}
            if material:
                out["material"] = material
        return JSONResponse(out)

    @app.get("/v1/objects/{object_id}/content", tags=["objects"])
    async def get_object_content(object_id: str, connection_id: str, request: Request) -> Response:
        adapter = await reader(connection_id)
        rec = await get_record(adapter, object_id)
        data: bytes = await call(adapter.read_object_content(object_id))
        rng = request.headers.get("range")
        if rng and (m := re.fullmatch(r"bytes=(\d*)-(\d*)", rng.strip())):
            start_s, end_s = m.groups()
            if start_s:
                start, end = int(start_s), int(end_s) if end_s else len(data) - 1
            else:
                start, end = max(0, len(data) - int(end_s or 0)), len(data) - 1
            end = min(end, len(data) - 1)
            if start > end:
                return Response(status_code=416, headers={"Content-Range": f"bytes */{len(data)}"})
            return Response(
                data[start : end + 1],
                status_code=206,
                media_type=rec.media_type,
                headers={"Content-Range": f"bytes {start}-{end}/{len(data)}", "Accept-Ranges": "bytes"},
            )
        return Response(data, media_type=rec.media_type, headers={"Accept-Ranges": "bytes"})

    return app


def manifest_test_cases(
    pkg: StoragePackage, body: Mapping[str, Any]
) -> list[tuple[str, dict[str, Any], str]]:
    """Invocations (``test_mode``) for the package's manifest tests and extra cases of a test run."""
    selected = body.get("tests", "all")
    cases: list[tuple[str, dict[str, Any], str]] = []
    base = {"handler": {"package_id": pkg.package_id, "version": pkg.version}, "context": {"test_mode": True}}
    if selected != "none":
        for test in pkg.manifest.get("tests") or ():
            if isinstance(selected, list) and test["name"] not in selected:
                continue
            spec = test["input"]
            if "entities" in spec:
                item: dict[str, Any] = {
                    "kind": "entities",
                    "entities": json.loads(pkg.file(spec["entities"])),
                }
            elif "material" in spec:
                item = {"kind": "material", "material": json.loads(pkg.file(spec["material"]))}
            else:
                data = pkg.file(spec["file"])
                item = {
                    "kind": "material",
                    "material": {
                        "material_id": f"test:{test['name']}",
                        "observation_id": f"obs_{test['name']}",
                        "source": {"kind": "web"},
                        "locator": {"url": spec.get("url", "https://example.test/")},
                        "fetched_at": "2026-01-01T00:00:00Z",
                        "format": {"media_type": spec.get("media_type", "application/octet-stream")},
                        "revision": {"content_sha256": hashlib.sha256(data).hexdigest()},
                        "content": {
                            "kind": "inline",
                            "media_type": spec.get("media_type", "application/octet-stream"),
                            "encoding": "base64",
                            "data": base64.b64encode(data).decode("ascii"),
                        },
                        "collector": {"name": "test", "version": "0"},
                    },
                }
            invocation = {
                **base,
                "params": dict(test.get("params") or {}),
                "inputs": [item],
                "delivery": {"delivery_key": f"test-run:{test['name']}"},
            }
            cases.append((test["name"], invocation, test["expected_status"]))
    for extra in body.get("extra_cases") or ():
        invocation = {
            **base,
            "params": dict(extra.get("params") or body.get("params") or {}),
            "inputs": [extra["input"]],
            "delivery": {"delivery_key": f"test-run:{extra['name']}"},
        }
        cases.append((extra["name"], invocation, extra["expected_status"]))
    return cases
