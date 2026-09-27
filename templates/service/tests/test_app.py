from __future__ import annotations

import time
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from jane_template_service.app import build_app
from jane_template_service.settings import Settings


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("JANE_TEMPLATE_SERVICE_LIMITS__JOBS__MAX_CONCURRENT_JOBS", "2")
    with TestClient(build_app(Settings(log_format="console"))) as c:
        yield c


def test_health_live_and_ready(client: TestClient) -> None:
    live = client.get("/health/live")
    assert live.status_code == 200
    assert live.json()["status"] == "ok"
    assert live.json()["service"] == "template-service"
    ready = client.get("/health/ready")
    assert ready.status_code == 200


def test_metrics_exposed(client: TestClient) -> None:
    client.get("/v1/info")
    body = client.get("/metrics").text
    assert 'jane_http_requests_total{method="GET",route="/v1/info",status="200"}' in body


def test_limits_come_from_config(client: TestClient) -> None:
    rows = {r["path"]: r for r in client.get("/v1/info").json()["limits"]}
    assert rows["jobs.max_concurrent_jobs"]["value"] == 2
    assert rows["jobs.max_concurrent_jobs"]["origin"] == "platform:env"
    assert rows["idempotency.ttl_s"]["origin"] == "default"


def test_unknown_route_is_problem(client: TestClient) -> None:
    r = client.get("/v1/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["code"] == "not_found"
    assert r.headers["X-Request-ID"]


def test_example_job_is_idempotent_and_finishes(client: TestClient) -> None:
    headers = {"Idempotency-Key": "k-1"}
    first = client.post("/v1/examples/jobs", json={"steps": 2}, headers=headers)
    assert first.status_code == 202
    job_id = first.json()["job_id"]
    assert first.headers["Location"] == f"/v1/jobs/{job_id}"
    again = client.post("/v1/examples/jobs", json={"steps": 2}, headers=headers)
    assert again.json()["job_id"] == job_id
    assert again.headers["Idempotent-Replayed"] == "true"
    reused = client.post("/v1/examples/jobs", json={"steps": 3}, headers=headers)
    assert reused.status_code == 422
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = client.get(f"/v1/jobs/{job_id}").json()
        if state["state"] == "succeeded":
            break
        time.sleep(0.02)
    assert state["state"] == "succeeded"
    assert state["result"] == {"steps_done": 2}


def test_example_job_can_be_cancelled(client: TestClient) -> None:
    r = client.post(
        "/v1/examples/jobs", json={"steps": 1000, "step_delay_s": 0.05}, headers={"Idempotency-Key": "k-2"}
    )
    job_id = r.json()["job_id"]
    assert client.post(f"/v1/jobs/{job_id}/cancel").status_code == 202
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        state = client.get(f"/v1/jobs/{job_id}").json()["state"]
        if state == "cancelled":
            break
        time.sleep(0.02)
    assert state == "cancelled"


def test_missing_idempotency_key_rejected(client: TestClient) -> None:
    r = client.post("/v1/examples/jobs", json={})
    assert r.status_code == 400
    assert r.json()["code"] == "idempotency_key_missing"
