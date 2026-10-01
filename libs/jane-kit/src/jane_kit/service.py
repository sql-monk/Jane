"""FastAPI application factory with the standard Jane wiring.

``create_app`` gives every service the same behaviour: JSON logs with ``trace_id``/``request_id``,
W3C ``traceparent`` continuation, access log, Problem-details errors, Prometheus ``/metrics``,
``/v1/health`` and ``/v1/info`` (WP-00 ``common.yaml``).
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, Response

from jane_kit.config import JaneSettings, ResolvedLimits
from jane_kit.errors import install_error_handlers
from jane_kit.health import HealthRegistry, ServiceInfo, install_health
from jane_kit.logs import bind_context, configure_logging
from jane_kit.metrics import Metrics, install_metrics
from jane_kit.tracing import TRACEPARENT, new_trace_id, parse_traceparent

__all__ = ["REQUEST_ID_HEADER", "create_app", "run"]

REQUEST_ID_HEADER = "X-Request-ID"
access_log = logging.getLogger("jane.access")

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]
_QUIET_PATHS = ("/v1/health", "/metrics")


def create_app(
    settings: JaneSettings,
    *,
    title: str | None = None,
    version: str = "0.1.0",
    api_versions: tuple[str, ...] = ("v1",),
    capabilities: Mapping[str, Any] | Callable[[], Mapping[str, Any]] | None = None,
    lifespan: Lifespan | None = None,
    limits: ResolvedLimits[Any] | None = None,
    configure_logs: bool = True,
    **fastapi_kwargs: Any,
) -> FastAPI:
    """Build a FastAPI app. ``app.state.health`` and ``app.state.metrics`` are ready to extend.

    ``limits`` (the service's resolved platform limits) is published in ``/v1/info`` as ``limits``
    (``PlatformLimits``: contract-mapped defaults and hard caps, WP-00 ``ServiceInfo``); limits of a shared
    platform profile that the service does not have (``ResolvedLimits.ignored``) are logged at start.
    """
    if configure_logs:
        configure_logging(
            settings.service_name, settings.log_level, settings.log_format, settings.instance_id
        )

    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
        logging.getLogger("jane.service").info(
            "service starting", extra={"version": version, "port": settings.port}
        )
        if limits is not None and (limits.ignored or limits.ignored_hard_caps):
            logging.getLogger("jane.service").info(
                "platform limits profile applied partially: limits this service does not have are ignored",
                extra={
                    "profile": limits.profile,
                    "ignored": sorted(limits.ignored),
                    "ignored_hard_caps": sorted(limits.ignored_hard_caps),
                },
            )
        if lifespan is None:
            yield
        else:
            async with lifespan(app):
                yield
        logging.getLogger("jane.service").info("service stopped")

    def info() -> ServiceInfo:
        caps = capabilities() if callable(capabilities) else capabilities
        return ServiceInfo(
            service=settings.service_name,
            version=version,
            api_versions=list(api_versions),
            capabilities=dict(caps or {}),
            auth_mode=settings.auth_mode,
            limits=limits.platform_limits() if limits is not None else None,
        )

    app = FastAPI(title=title or settings.service_name, version=version, lifespan=_lifespan, **fastapi_kwargs)
    app.state.settings = settings
    app.state.health = HealthRegistry(check_timeout_s=settings.health_check_timeout_ms / 1000)
    install_error_handlers(app)
    install_health(app, app.state.health, info)
    if settings.metrics_enabled:
        app.state.metrics = Metrics(settings.service_name)
        install_metrics(app, app.state.metrics)

    @app.middleware("http")
    async def _request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        trace_id = parse_traceparent(request.headers.get(TRACEPARENT)) or new_trace_id()
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        start = time.perf_counter()
        with bind_context(trace_id=trace_id, request_id=request_id):
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = request_id
            if not request.url.path.startswith(_QUIET_PATHS):
                access_log.info(
                    "request",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    },
                )
            return response

    return app


def run(app: FastAPI | str, settings: JaneSettings, **uvicorn_kwargs: Any) -> None:
    """Run with uvicorn using host/port from settings (logging stays ours)."""
    uvicorn.run(app, host=settings.host, port=settings.port, log_config=None, **uvicorn_kwargs)
