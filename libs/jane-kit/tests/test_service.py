from __future__ import annotations

import io
import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from jane_kit.config import JaneSettings
from jane_kit.errors import NotFound
from jane_kit.logs import JsonFormatter, bind_context
from jane_kit.service import create_app


class Body(BaseModel):
    n: int


def make_app() -> FastAPI:
    app = create_app(JaneSettings(service_name="svc", instance_id="i-1"), configure_logs=False)

    @app.get("/v1/things/{thing_id}")
    async def get_thing(thing_id: str) -> dict[str, str]:
        if thing_id == "missing":
            raise NotFound("no such thing", code="thing_not_found")
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


def test_health_endpoints(client: TestClient) -> None:
    assert client.get("/health/live").json() == {
        "status": "ok",
        "service": "svc",
        "instance": "i-1",
        "version": "0.1.0",
        "checks": {},
    }
    assert client.get("/health/ready").status_code == 200


def test_readiness_fails_when_check_fails() -> None:
    app = make_app()

    async def db_ok() -> bool:
        return True

    def broken() -> bool:
        raise ConnectionError("db down")

    app.state.health.add("db", db_ok)
    app.state.health.add("cache", broken)
    r = TestClient(app).get("/health/ready")
    assert r.status_code == 503
    body = r.json()
    assert body["checks"]["db"]["status"] == "ok"
    assert body["checks"]["cache"] == {
        "status": "fail",
        "duration_ms": body["checks"]["cache"]["duration_ms"],
        "error": "ConnectionError: db down",
    }


def test_readiness_check_timeout() -> None:
    import asyncio

    app = create_app(JaneSettings(), configure_logs=False, health_check_timeout_s=0.05)

    async def slow() -> bool:
        await asyncio.sleep(1)
        return True

    app.state.health.add("slow", slow)
    r = TestClient(app).get("/health/ready")
    assert r.status_code == 503
    assert "timeout" in r.json()["checks"]["slow"]["error"]


def test_errors_are_problem_details(client: TestClient) -> None:
    r = client.get("/v1/things/missing", headers={"X-Request-ID": "req-42"})
    assert r.status_code == 404
    assert r.headers["content-type"] == "application/problem+json"
    assert r.headers["X-Request-ID"] == "req-42"
    body = r.json()
    assert body["code"] == "thing_not_found"
    assert body["type"] == "urn:jane:problem:thing_not_found"
    assert body["detail"] == "no such thing"
    assert body["request_id"] == "req-42"
    assert body["instance"] == "/v1/things/missing"


def test_validation_and_unhandled_errors(client: TestClient) -> None:
    r = client.post("/v1/things", json={"n": "x"})
    assert r.status_code == 422
    assert r.json()["code"] == "validation_failed"
    assert r.json()["errors"][0]["loc"] == ["body", "n"]
    r = client.get("/v1/things/boom")
    assert r.status_code == 500
    assert r.json()["code"] == "internal_error"
    assert "secret" not in r.text
    r = client.delete("/v1/things/x")
    assert r.status_code == 405
    assert r.json()["code"] == "method_not_allowed"


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
    with bind_context(request_id="r-1", job_id="j-1"):
        log.info("hello %s", "світ", extra={"items": 3})
    record = json.loads(stream.getvalue())
    assert record["msg"] == "hello світ"
    assert record["service"] == "svc"
    assert record["instance"] == "i-1"
    assert record["request_id"] == "r-1"
    assert record["job_id"] == "j-1"
    assert record["items"] == 3
    assert record["level"] == "info"
