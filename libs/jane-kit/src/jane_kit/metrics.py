"""Prometheus metrics with a per-application registry (no global state between app instances)."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable, Sequence

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

__all__ = ["Metrics", "install_metrics"]


class Metrics:
    """Holds the registry and the standard HTTP metrics of one service instance."""

    def __init__(self, service: str, namespace: str = "jane") -> None:
        self.service = service
        self.namespace = namespace
        self.registry = CollectorRegistry(auto_describe=True)
        self.http_requests = Counter(
            "http_requests_total",
            "HTTP requests by route template and status",
            ["method", "route", "status"],
            namespace=namespace,
            registry=self.registry,
        )
        self.http_latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency by route template",
            ["method", "route"],
            namespace=namespace,
            registry=self.registry,
        )
        self.http_in_flight = Gauge(
            "http_requests_in_flight",
            "HTTP requests being processed",
            namespace=namespace,
            registry=self.registry,
        )
        self.info = Gauge(
            "service_info", "Static service info", ["service"], namespace=namespace, registry=self.registry
        )
        self.info.labels(service=service).set(1)

    def counter(self, name: str, doc: str, labels: Sequence[str] = ()) -> Counter:
        return Counter(name, doc, list(labels), namespace=self.namespace, registry=self.registry)

    def gauge(self, name: str, doc: str, labels: Sequence[str] = ()) -> Gauge:
        return Gauge(name, doc, list(labels), namespace=self.namespace, registry=self.registry)

    def histogram(self, name: str, doc: str, labels: Sequence[str] = ()) -> Histogram:
        return Histogram(name, doc, list(labels), namespace=self.namespace, registry=self.registry)

    def render(self) -> bytes:
        return generate_latest(self.registry)


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else "__unmatched__"


def install_metrics(app: FastAPI, metrics: Metrics, path: str = "/metrics") -> None:
    """Expose ``path`` and record request count/latency labelled by route *template*."""

    @app.middleware("http")
    async def _measure(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path == path:
            return await call_next(request)
        start = time.perf_counter()
        metrics.http_in_flight.inc()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            metrics.http_in_flight.dec()
            route = _route_template(request)
            metrics.http_requests.labels(request.method, route, str(status)).inc()
            metrics.http_latency.labels(request.method, route).observe(time.perf_counter() - start)

    @app.get(path, include_in_schema=False)
    async def _metrics() -> Response:
        return Response(metrics.render(), media_type=CONTENT_TYPE_LATEST)
