"""HTTP API of the registry: ``contracts/openapi/registry.v1.yaml``.

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from jane_kit.auth import resolve_secret_ref
from jane_kit.auth_scopes import REGISTRY
from jane_kit.errors import FieldError, Forbidden, JaneError, ValidationFailed
from jane_kit.idempotency import IdempotencyStore, InMemoryIdempotencyStore, StoredResponse, idempotent
from jane_kit.jobs import (
    TERMINAL_STATUSES,
    InMemoryJobStore,
    JobCancelRequest,
    JobContext,
    JobRunner,
    JobStore,
    accepted,
)
from jane_kit.pagination import clamp_limit, decode_cursor, encode_cursor
from jane_kit.service import create_app

from . import __version__
from .auth import Authenticator, Principal
from .blobs import BlobStore, FileBlobStore, S3BlobStore
from .profiles import ProfileSource
from .service import RegistryService, package_etag, package_wire, version_wire
from .settings import ServiceLimits, Settings, resolve_service_limits
from .store import MemoryStore, MetadataStore, PackageFilter
from .validation import ContractSchemas, PackageValidator, find_contracts_dir

log = logging.getLogger(__name__)

SLUG = r"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"
SEMVER = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
KINDS = Literal["extractor", "storage", "llm", "transform", "collector-rules"]
STATUSES = Literal["draft", "approved", "rejected", "deprecated", "yanked"]
LABELS = dict[
    Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9._/-]{0,62}$")], Annotated[str, Field(max_length=256)]
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PackageCreate(_Strict):
    package_id: str = Field(pattern=SLUG)
    kind: KINDS
    title: str
    description: str | None = None
    auto_changes_allowed: bool = True
    labels: LABELS | None = Field(default=None, max_length=64)


class PackagePatch(_Strict):
    title: str | None = None
    description: str | None = None
    auto_changes_allowed: bool | None = None
    deprecated: bool | None = None
    labels: LABELS | None = Field(default=None, max_length=64)


class FileContent(_Strict):
    encoding: Literal["utf-8", "base64"]
    data: str


class PublishRequest(_Strict):
    manifest: dict[str, Any]
    files: dict[str, FileContent]


class StatusChange(_Strict):
    status: Literal["approved", "rejected", "deprecated", "yanked"]
    reason: str | None = Field(default=None, max_length=2000)


class TestResultsRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    runner: str | None = None
    context: str | None = None
    report: dict[str, Any]
    recorded_at: str | None = None


class ForkRequest(_Strict):
    new_package_id: str = Field(pattern=SLUG)
    from_version: str = Field(pattern=SEMVER)
    initial_version: str | None = Field(default=None, pattern=SEMVER)
    title: str | None = None
    auto_changes_allowed: bool = False


class UpstreamPortRequest(_Strict):
    parent_version: str = Field(pattern=SEMVER)
    base_version: str | None = Field(default=None, pattern=SEMVER)
    new_version: str = Field(pattern=SEMVER)


def _parse[M: BaseModel](model: type[M], data: Any) -> M:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        errors = [
            FieldError(
                pointer="/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in e["loc"]),
                code=str(e["type"]),
                message=str(e["msg"]),
            )
            for e in exc.errors()
        ]
        raise ValidationFailed("request body does not match the contract", errors=errors) from exc


async def _json_body(request: Request) -> Any:
    raw = await request.body()
    try:
        import json

        return json.loads(raw) if raw else None
    except ValueError as exc:
        raise JaneError(f"body is not valid JSON: {exc}", code="bad_request") from exc


@dataclass
class Components:
    store: MetadataStore
    blobs: BlobStore
    idempotency: IdempotencyStore
    jobs: JobStore


def build_components(settings: Settings, limits: ServiceLimits) -> Components:
    store: MetadataStore
    idem: IdempotencyStore
    jobs: JobStore
    if settings.db == "postgres":
        from .postgres import PostgresIdempotencyStore, PostgresJobStore, PostgresStore

        if settings.db_url is None:
            raise ValueError(
                "JANE_REGISTRY_DB_URL is required for db=postgres (or set JANE_REGISTRY_DB=memory)"
            )
        pg = PostgresStore(settings.db_url.get_secret_value(), settings.db_schema, limits.db)
        rec = limits.recovery
        store = pg
        idem = PostgresIdempotencyStore(pg, rec.in_progress_lease_ms / 1000)
        # the owner is unique per start: a restarted instance must not renew the jobs of its previous life
        owner = f"{settings.instance_id}-{uuid.uuid4().hex[:8]}"
        jobs = PostgresJobStore(pg, limits.jobs, owner, rec.job_lease_ms / 1000)
    else:
        store, idem, jobs = (
            MemoryStore(),
            InMemoryIdempotencyStore(limits.idempotency),
            InMemoryJobStore(limits.jobs),
        )
    blobs: BlobStore
    if settings.blob == "filesystem":
        if settings.blob_root is None:
            raise ValueError("JANE_REGISTRY_BLOB_ROOT is required for blob=filesystem")
        blobs = FileBlobStore(settings.blob_root, settings.blob_bucket, settings.blob_prefix)
    else:
        blobs = S3BlobStore(
            bucket=settings.blob_bucket,
            prefix=settings.blob_prefix,
            endpoint_url=settings.s3_endpoint_url,
            region=settings.s3_region,
            access_key=settings.s3_access_key.get_secret_value() if settings.s3_access_key else None,
            secret_key=settings.s3_secret_key.get_secret_value() if settings.s3_secret_key else None,
            connect_timeout_s=limits.blob.connect_timeout_ms / 1000,
            read_timeout_s=limits.blob.read_timeout_ms / 1000,
            max_attempts=limits.blob.max_attempts,
        )
    return Components(store, blobs, idem, jobs)


def build_app(settings: Settings | None = None, components: Components | None = None) -> FastAPI:
    settings = settings or Settings()
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    comp = components or build_components(settings, limits)
    auth = Authenticator(settings)
    schemas = ContractSchemas(find_contracts_dir(settings.contracts_dir))
    profiles = ProfileSource(
        settings.runtime_profiles,
        limits.profiles,
        token=resolve_secret_ref(settings.runtime_profiles_token_ref)
        if settings.runtime_profiles_token_ref
        else None,
    )
    service = RegistryService(
        comp.store,
        comp.blobs,
        PackageValidator(schemas, require_tests=settings.require_tests),
        profiles,
        limits,
    )
    runner = JobRunner(store=comp.jobs, limits=limits.jobs)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        await comp.store.open()
        if isinstance(comp.blobs, S3BlobStore) and settings.s3_create_bucket:
            await asyncio.to_thread(comp.blobs.ensure_bucket)
        heartbeat: asyncio.Task[None] | None = None
        sweep = getattr(comp.jobs, "sweep", None)
        if sweep is not None:
            reaped = await sweep()
            if reaped:
                log.warning("jobs of stopped instances marked failed", extra={"jobs": reaped})
            heartbeat = asyncio.create_task(_heartbeat(), name="registry-job-heartbeat")
        log.info(
            "registry started",
            extra={"limits": resolved.effective(), "store": comp.store.name, "blob": comp.blobs.name},
        )
        try:
            yield
        finally:
            if heartbeat is not None:
                heartbeat.cancel()
                await asyncio.gather(heartbeat, return_exceptions=True)
            await runner.shutdown()
            await comp.store.close()

    async def _heartbeat() -> None:
        beat = getattr(comp.jobs, "heartbeat", None)
        while beat is not None:
            await asyncio.sleep(limits.recovery.job_heartbeat_ms / 1000)
            try:
                await beat()
            except Exception:
                log.exception("job lease renewal failed")

    app = create_app(
        settings,
        title="Jane Handler Registry",
        version=__version__,
        lifespan=lifespan,
        capabilities=lambda: {
            "handler_kinds": ["extractor", "storage", "llm", "transform", "collector-rules"],
            "metadata_store": comp.store.name,
            "blob_store": comp.blobs.name,
            "archive": {"format": "zip", "compression": "stored", "digest": "sha256"},
            "runtime_profiles": profiles.known(),
            "upstream_ports": True,
        },
        limits=resolved,
        auth_scopes=REGISTRY,  # ADR-0005; the route dependencies below also give the caller's actor
    )
    app.state.limits = resolved
    app.state.service = service
    app.state.components = comp
    app.state.health.add("metadata_store", comp.store.check)
    app.state.health.add("blob_store", comp.blobs.check)
    publications = (
        app.state.metrics.counter("registry_publications_total", "Publish attempts by result", ["result"])
        if settings.metrics_enabled
        else None
    )

    read = Depends(auth.require("registry:read"))
    write = auth.require("registry:write")
    approve = auth.require("registry:approve")

    # /v1/jobs (common.yaml Job, JobCancel): reading needs registry:read, cancelling registry:write
    @app.get("/v1/jobs/{job_id}", tags=["jobs"], operation_id="getJob", dependencies=[read])
    async def get_job(job_id: str) -> JSONResponse:
        return JSONResponse((await runner.get(job_id)).wire())

    @app.post("/v1/jobs/{job_id}/cancel", tags=["jobs"], operation_id="cancelJob")
    async def cancel_job(
        job_id: str,
        request: Request,
        principal: Principal = Depends(write),  # noqa: B008
    ) -> JSONResponse:
        raw = await _json_body(request)
        body = _parse(JobCancelRequest, raw) if raw is not None else None
        before = await runner.get(job_id)
        if before.status in TERMINAL_STATUSES:
            return JSONResponse(before.wire(), status_code=200)
        job = await runner.cancel(job_id, reason=body.reason if body else None, requested_by=principal.name)
        return JSONResponse(job.wire(), status_code=202)

    @app.middleware("http")
    async def body_limit(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > limits.requests.max_request_body_bytes:
            err = JaneError(
                f"body is {length} bytes, limit transfer.max_request_body_bytes="
                f"{limits.requests.max_request_body_bytes}",
                code="payload_too_large",
                details={
                    "limit": limits.requests.max_request_body_bytes,
                    "path": "transfer.max_request_body_bytes",
                },
            )
            from jane_kit.errors import problem_response

            return problem_response(err.to_problem(instance=request.url.path))
        return await call_next(request)

    async def run(request: Request, handler: Callable[[], Awaitable[StoredResponse]]) -> Response:
        return await idempotent(request, comp.idempotency, handler, limits=limits.idempotency)

    # ------------------------------------------------------------------ packages
    @app.get("/v1/packages", tags=["packages"], operation_id="listPackages", dependencies=[read])
    async def list_packages(
        kind: KINDS | None = None,
        q: str | None = None,
        tag: str | None = None,
        entity_type: str | None = None,
        media_type: str | None = None,
        domain: str | None = None,
        fork_of: str | None = None,
        cursor: Annotated[str | None, Query(max_length=2048)] = None,
        limit: Annotated[int | None, Query(ge=1)] = None,
    ) -> JSONResponse:
        size = clamp_limit(limit, limits.pages)
        after = str(decode_cursor(cursor)) if cursor else None
        flt = PackageFilter(kind, q, tag, entity_type, media_type, domain, fork_of)
        items = await service.list_packages(flt, after, size + 1)
        page, more = items[:size], len(items) > size
        return JSONResponse(
            {
                "items": [package_wire(p) for p in page],
                "next_cursor": encode_cursor(page[-1].package_id) if more and page else None,
            }
        )

    @app.post("/v1/packages", tags=["packages"], operation_id="createPackage", status_code=201)
    async def create_package(request: Request, principal: Principal = Depends(write)) -> Response:  # noqa: B008
        async def handler() -> StoredResponse:
            body = _parse(PackageCreate, await _json_body(request))
            pkg = await service.create_package(body.model_dump(exclude_none=True), principal)
            return StoredResponse(
                201,
                package_wire(pkg, 0),
                {"Location": f"/v1/packages/{pkg.package_id}", "ETag": package_etag(pkg)},
            )

        return await run(request, handler)

    @app.get("/v1/packages/{package_id}", tags=["packages"], operation_id="getPackage", dependencies=[read])
    async def get_package(package_id: str) -> JSONResponse:
        pkg = await service.package(package_id)
        forks = await comp.store.count_forks(package_id)
        return JSONResponse(package_wire(pkg, forks), headers={"ETag": package_etag(pkg)})

    @app.patch("/v1/packages/{package_id}", tags=["packages"], operation_id="updatePackage")
    async def update_package(
        package_id: str,
        request: Request,
        principal: Principal = Depends(write),  # noqa: B008
    ) -> JSONResponse:
        body = await _json_body(request)
        if isinstance(body, dict) and any(v is None for v in body.values()):
            raise ValidationFailed(
                "null values are not supported in this merge patch",
                errors=[
                    FieldError(pointer=f"/{k}", message="must not be null")
                    for k, v in body.items()
                    if v is None
                ],
            )
        patch = _parse(PackagePatch, body)
        changes = patch.model_dump(exclude_unset=True)
        if changes.get("auto_changes_allowed") is True and "registry:approve" not in principal.scopes:
            current = await service.package(package_id)
            if not current.auto_changes_allowed:
                raise Forbidden(
                    "allowing automatic changes of a package needs the registry:approve scope",
                    title="Scope registry:approve is required",
                )
        if not changes:
            pkg = await service.package(package_id)
        else:
            pkg = await service.update_package(package_id, changes, request.headers.get("if-match"))
        forks = await comp.store.count_forks(package_id)
        return JSONResponse(package_wire(pkg, forks), headers={"ETag": package_etag(pkg)})

    # ------------------------------------------------------------------ versions
    @app.get(
        "/v1/packages/{package_id}/versions",
        tags=["versions"],
        operation_id="listPackageVersions",
        dependencies=[read],
    )
    async def list_versions(
        package_id: str,
        status: STATUSES | None = None,
        cursor: Annotated[str | None, Query(max_length=2048)] = None,
        limit: Annotated[int | None, Query(ge=1)] = None,
    ) -> JSONResponse:
        await service.package(package_id)
        size = clamp_limit(limit, limits.pages)
        before = decode_cursor(cursor) if cursor else None
        if before is not None and not isinstance(before, int):
            raise ValidationFailed(
                "invalid cursor", errors=[FieldError(parameter="cursor", message="invalid")]
            )
        items = await comp.store.list_versions(package_id, status, before, size + 1)
        page, more = items[:size], len(items) > size
        return JSONResponse(
            {
                "items": [version_wire(v, full=False) for v in page],
                "next_cursor": encode_cursor(page[-1].seq) if more and page else None,
            }
        )

    @app.post(
        "/v1/packages/{package_id}/versions",
        tags=["versions"],
        operation_id="publishPackageVersion",
        status_code=201,
    )
    async def publish(
        package_id: str,
        request: Request,
        principal: Principal = Depends(write),  # noqa: B008
    ) -> Response:
        async def handler() -> StoredResponse:
            raw = await request.body()
            if len(raw) > limits.requests.max_request_body_bytes:
                raise JaneError(
                    "body exceeds transfer.max_request_body_bytes",
                    code="payload_too_large",
                    details={"limit": limits.requests.max_request_body_bytes},
                )
            media = (request.headers.get("content-type") or "").split(";", 1)[0].strip().lower()
            pkg = await service.package(package_id)
            if media in {"application/zip", "application/x-zip-compressed"}:
                manifest, files = service.files_from_zip(raw)
                from_zip = True
            elif media == "application/json":
                body = _parse(PublishRequest, await _json_body(request))
                manifest, files = service.files_from_json(body.model_dump())
                from_zip = False
            else:
                raise JaneError(
                    f"unsupported content type {media!r}; use application/zip or application/json",
                    code="unsupported_media_type",
                )
            v = await service.publish(pkg, manifest, files, principal, from_zip=from_zip)
            return StoredResponse(
                201, version_wire(v), {"Location": f"/v1/packages/{package_id}/versions/{v.version}"}
            )

        try:
            response = await run(request, handler)
        except JaneError as exc:
            if publications is not None:
                publications.labels(result=exc.error_code).inc()
            raise
        if publications is not None:
            publications.labels(result="published" if response.status_code == 201 else "replayed").inc()
        return response

    @app.get(
        "/v1/packages/{package_id}/versions/{version}",
        tags=["versions"],
        operation_id="getPackageVersion",
        dependencies=[read],
    )
    async def get_version(package_id: str, version: str) -> JSONResponse:
        return JSONResponse(version_wire(await service.version(package_id, version)))

    @app.get(
        "/v1/packages/{package_id}/versions/{version}/archive",
        tags=["versions"],
        operation_id="downloadPackageArchive",
        dependencies=[read],
    )
    async def download_archive(package_id: str, version: str) -> Response:
        v = await service.version(package_id, version)
        data = await service.archive(v)
        filename = f"{package_id}-{version}.zip"
        return Response(
            data,
            media_type="application/zip",
            headers={
                "ETag": f'"{v.digest}"',
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Jane-Package-Digest": v.digest,
            },
        )

    @app.get(
        "/v1/packages/{package_id}/versions/{version}/file",
        tags=["versions"],
        operation_id="getPackageFile",
        dependencies=[read],
    )
    async def get_file(package_id: str, version: str, path: str) -> Response:
        v = await service.version(package_id, version)
        files = await service.files_of(v)
        if path not in files:
            from jane_kit.errors import NotFound

            raise NotFound(f"file {path!r} is not in {package_id}@{version}")
        data = files[path]
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return Response(data, media_type="application/octet-stream")
        if "\0" in text:
            return Response(data, media_type="application/octet-stream")
        return Response(text, media_type="text/plain; charset=utf-8")

    @app.post(
        "/v1/packages/{package_id}/versions/{version}/status",
        tags=["versions"],
        operation_id="setPackageVersionStatus",
    )
    async def set_status(
        package_id: str,
        version: str,
        request: Request,
        principal: Principal = Depends(approve),  # noqa: B008
    ) -> Response:
        async def handler() -> StoredResponse:
            body = _parse(StatusChange, await _json_body(request))
            v = await service.set_status(package_id, version, body.status, body.reason, principal)
            return StoredResponse(200, version_wire(v))

        return await run(request, handler)

    @app.post(
        "/v1/packages/{package_id}/versions/{version}/test-results",
        tags=["versions"],
        operation_id="recordTestResults",
    )
    async def record_tests(
        package_id: str,
        version: str,
        request: Request,
        principal: Principal = Depends(write),  # noqa: B008
    ) -> Response:
        async def handler() -> StoredResponse:
            body = _parse(TestResultsRecord, await _json_body(request))
            v = await service.record_test_results(package_id, version, body.model_dump(exclude_none=True))
            return StoredResponse(200, version_wire(v))

        return await run(request, handler)

    # ------------------------------------------------------------------ forks
    @app.post("/v1/packages/{package_id}/forks", tags=["forks"], operation_id="forkPackage", status_code=201)
    async def fork(
        package_id: str,
        request: Request,
        principal: Principal = Depends(write),  # noqa: B008
    ) -> Response:
        async def handler() -> StoredResponse:
            body = _parse(ForkRequest, await _json_body(request))
            pkg, _ = await service.fork(package_id, body.model_dump(exclude_none=True), principal)
            return StoredResponse(
                201,
                package_wire(pkg, 0),
                {"Location": f"/v1/packages/{pkg.package_id}", "ETag": package_etag(pkg)},
            )

        return await run(request, handler)

    @app.get(
        "/v1/packages/{package_id}/diff",
        tags=["versions", "forks"],
        operation_id="diffPackage",
        dependencies=[read],
    )
    async def diff(
        package_id: str,
        to: str,
        from_: Annotated[str | None, Query(alias="from")] = None,
        context_lines: Annotated[int, Query(ge=0)] = 3,
    ) -> JSONResponse:
        return JSONResponse(await service.diff(package_id, from_, to, context_lines))

    @app.get(
        "/v1/packages/{package_id}/upstream",
        tags=["forks"],
        operation_id="getUpstreamStatus",
        dependencies=[read],
    )
    async def upstream(package_id: str) -> JSONResponse:
        return JSONResponse(await service.upstream(package_id))

    @app.post(
        "/v1/packages/{package_id}/upstream-ports",
        tags=["forks"],
        operation_id="portUpstreamChanges",
        status_code=202,
    )
    async def port(
        package_id: str,
        request: Request,
        principal: Principal = Depends(write),  # noqa: B008
    ) -> Response:
        async def handler() -> StoredResponse:
            body = _parse(UpstreamPortRequest, await _json_body(request))
            plan = await service.plan_port(package_id, body.model_dump(exclude_none=True), principal)

            async def work(ctx: JobContext) -> dict[str, Any]:
                await ctx.progress(0, 2, unit="steps", message="merging")
                version = await service.port(plan, principal, before_publish=ctx.check_cancelled)
                await ctx.progress(2, 2, unit="steps", message=f"published {version.version}")
                return version_wire(version)

            job = await runner.submit(
                "upstream_port",
                work,
                idempotency_key=request.headers.get("idempotency-key"),
                labels={"package_id": package_id},
            )
            resp = accepted(job, runner.location(job.job_id))
            return StoredResponse(202, job.wire(), {"Location": resp.headers["location"]})

        return await run(request, handler)

    return app
