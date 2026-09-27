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


def wait_status(client: TestClient, job_id: str, wanted: str) -> dict[str, object]:
    deadline = time.monotonic() + 5
    job: dict[str, object] = {}
    while time.monotonic() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] == wanted:
            break
        time.sleep(0.02)
    return job


def test_health_and_info(client: TestClient) -> None:
    health = client.get("/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "checks": {}}
    info = client.get("/v1/info").json()
    assert info["service"] == "template-service"
    assert info["api_versions"] == ["v1"]


def test_metrics_exposed(client: TestClient) -> None:
    client.get("/v1/info")
    body = client.get("/metrics").text
    assert 'jane_http_requests_total{method="GET",route="/v1/info",status="200"}' in body


def test_limits_come_from_config(client: TestClient) -> None:
    resolved = client.app.state.limits  # type: ignore[attr-defined]
    assert resolved.limits.jobs.max_concurrent_jobs == 2
    provenance = resolved.provenance()
    assert provenance["jobs.max_concurrent_jobs"] == "platform"
    assert resolved.origin["jobs.max_concurrent_jobs"] == "platform:env"


def test_unknown_route_is_problem(client: TestClient) -> None:
    r = client.get(
        "/v1/nope", headers={"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}
    )
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["code"] == "not_found"
    assert r.json()["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"


def test_example_job_is_idempotent_and_finishes(client: TestClient) -> None:
    headers = {"Idempotency-Key": "k-1"}
    first = client.post("/v1/examples/jobs", json={"steps": 2}, headers=headers)
    assert first.status_code == 202
    job_id = first.json()["job_id"]
    assert first.headers["Location"] == f"/v1/jobs/{job_id}"
    again = client.post("/v1/examples/jobs", json={"steps": 2}, headers=headers)
    assert again.json()["job_id"] == job_id
    assert again.headers["Idempotency-Replayed"] == "true"
    reused = client.post("/v1/examples/jobs", json={"steps": 3}, headers=headers)
    assert reused.status_code == 422
    assert reused.json()["code"] == "idempotency_key_reused"
    job = wait_status(client, job_id, "succeeded")
    assert job["status"] == "succeeded"
    assert job["result"] == {"steps_done": 2}
    assert job["progress"]["completed"] == 2  # type: ignore[index]


def test_example_job_can_be_cancelled(client: TestClient) -> None:
    r = client.post(
        "/v1/examples/jobs", json={"steps": 1000, "step_delay_ms": 50}, headers={"Idempotency-Key": "k-2"}
    )
    job_id = r.json()["job_id"]
    cancel = client.post(f"/v1/jobs/{job_id}/cancel", json={"reason": "test"})
    assert cancel.status_code == 202
    assert cancel.json()["status"] in {"cancelling", "cancelled"}
    assert wait_status(client, job_id, "cancelled")["status"] == "cancelled"
    assert client.post(f"/v1/jobs/{job_id}/cancel").status_code == 200  # already terminal


def test_missing_idempotency_key_rejected(client: TestClient) -> None:
    r = client.post("/v1/examples/jobs", json={})
    assert r.status_code == 422
    assert r.json()["errors"][0]["parameter"] == "Idempotency-Key"
