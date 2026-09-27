from __future__ import annotations

import asyncio
import io
import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from jane_kit.config import JaneSettings, LimitLayer, resolve_limits
from jane_kit.errors import JaneError, NotFound
from jane_kit.jobs import JobLimits
from jane_kit.logs import JsonFormatter, bind_context
from jane_kit.service import create_app

TRACEPARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


class Body(BaseModel):
    n: int


def make_app() -> FastAPI:
    app = create_app(
        JaneSettings(service_name="svc", instance_id="i-1"),
        configure_logs=False,
        capabilities={"strategies": ["recursive"]},
    )

    @app.get("/v1/things/{thing_id}")
    async def get_thing(thing_id: str) -> dict[str, str]:
        if thing_id == "missing":
            raise NotFound("no such thing")
        if thing_id == "limited":
            raise JaneError("slow down", code="rate_limited", retry_after_seconds=30)
        if thing_id == "boom":
            raise RuntimeError("secret internals")
        return {"id": thing_id}

    @app.post("/v1/things")
    async def post_thing(body: Body) -> Body:
        return body

    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(make_app(), raise_server_exceptions=False)


def test_health_and_info(client: TestClient) -> None:
    assert client.get("/v1/health").json() == {"status": "ok", "checks": {}}
    assert client.get("/v1/info").json() == {
        "service": "svc",
        "version": "0.1.0",
        "api_versions": ["v1"],
        "capabilities": {"strategies": ["recursive"]},
        "auth_mode": "none",
    }


def test_health_down_and_degraded() -> None:
    app = make_app()

    async def db_ok() -> bool:
        return True

    def cache_broken() -> bool:
        raise ConnectionError("cache down")

    app.state.health.add("db", db_ok)
    app.state.health.add("cache", cache_broken, critical=False)
    r = TestClient(app).get("/v1/health")
    assert r.status_code == 200
    assert r.json() == {
        "status": "degraded",
        "checks": {
            "db": {"status": "ok"},
            "cache": {"status": "degraded", "message": "ConnectionError: cache down"},
        },
    }

    app.state.health.add("queue", lambda: False)
    r = TestClient(app).get("/v1/health")
    assert r.status_code == 503
    assert r.json()["status"] == "down"


def test_health_check_timeout() -> None:
    app = create_app(JaneSettings(health_check_timeout_ms=50), configure_logs=False)

    async def slow() -> bool:
        await asyncio.sleep(1)
        return True

    app.state.health.add("slow", slow)
    r = TestClient(app).get("/v1/health")
    assert r.status_code == 503
    assert "timeout" in r.json()["checks"]["slow"]["message"]


def test_errors_are_problem_details_with_trace(client: TestClient) -> None:
    r = client.get("/v1/things/missing", headers={"traceparent": TRACEPARENT})
    assert r.status_code == 404
    assert r.headers["content-type"] == "application/problem+json"
    assert r.json() == {
        "type": "urn:jane:problem:not_found",
        "title": "Not found",
        "status": 404,
        "code": "not_found",
        "detail": "no such thing",
        "instance": "/v1/things/missing",
        "retryable": False,
        "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    }


def test_rate_limited_sets_retry_after(client: TestClient) -> None:
    r = client.get("/v1/things/limited")
    assert r.status_code == 429
    assert r.headers["Retry-After"] == "30"
    assert r.json()["retry_after_seconds"] == 30 and r.json()["retryable"] is True


def test_validation_and_unhandled_errors(client: TestClient) -> None:
    r = client.post("/v1/things", json={"n": "x"})
    assert r.status_code == 422
    assert r.json()["code"] == "validation_failed"
    assert r.json()["errors"][0]["pointer"] == "/n"
    r = client.post("/v1/things", content=b"{not json", headers={"content-type": "application/json"})
    assert r.status_code == 400 and r.json()["code"] == "bad_request"
    r = client.get("/v1/things/boom")
    assert r.status_code == 500
    assert r.json()["code"] == "internal_error" and r.json()["retryable"] is True
    assert "secret" not in r.text
    r = client.delete("/v1/things/x")
    assert r.status_code == 405 and r.json()["code"] == "method_not_allowed"


def test_metrics_use_route_templates(client: TestClient) -> None:
    client.get("/v1/things/a")
    client.get("/v1/things/b")
    text = client.get("/metrics").text
    assert 'jane_http_requests_total{method="GET",route="/v1/things/{thing_id}",status="200"} 2.0' in text
    assert 'jane_service_info{service="svc"} 1.0' in text
    assert "jane_http_request_duration_seconds_bucket" in text


def test_two_apps_have_independent_registries() -> None:
    a, b = TestClient(make_app()), TestClient(make_app())
    a.get("/v1/things/a")
    assert "/v1/things/{thing_id}" not in b.get("/metrics").text


def test_json_log_contains_context() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter("svc", "i-1"))
    log = logging.getLogger("jane.test.json")
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False
    with bind_context(trace_id="t-1", job_id="j-1"):
        log.info("hello %s", "світ", extra={"items": 3, "color_message": "ansi"})
    record = json.loads(stream.getvalue())
    assert record["msg"] == "hello світ"
    assert (record["service"], record["instance"], record["trace_id"], record["job_id"]) == (
        "svc",
        "i-1",
        "t-1",
        "j-1",
    )
    assert record["items"] == 3 and record["level"] == "info"
    assert "color_message" not in record


def test_health_check_timeout_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_HEALTH_CHECK_TIMEOUT_MS", "40")
    settings = JaneSettings()
    assert settings.health_check_timeout_ms == 40
    app = create_app(settings, configure_logs=False)
    assert app.state.health.check_timeout_s == 0.04

    async def slow() -> bool:
        await asyncio.sleep(1)
        return True

    app.state.health.add("slow", slow)
    body = TestClient(app).get("/v1/health").json()
    assert body["checks"]["slow"]["message"] == "timeout after 0.04s"


def test_info_publishes_platform_limits() -> None:
    resolved = resolve_limits(JobLimits, LimitLayer("platform", hard_caps={"job_retention_seconds": 3600}))
    app = create_app(JaneSettings(), configure_logs=False, limits=resolved)
    limits = TestClient(app).get("/v1/info").json()["limits"]
    # only contract fields; service-specific ones (max_concurrent_jobs...) stay internal
    assert limits == {
        "defaults": {"transfer": {"job_retention_seconds": 3600}},
        "hard_caps": {"transfer": {"job_retention_seconds": 3600}},
    }
