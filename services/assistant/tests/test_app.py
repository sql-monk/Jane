from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from jane_assistant.app import build_app
from jane_assistant.settings import Settings


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__JOBS__MAX_CONCURRENT_JOBS", "2")
    with TestClient(build_app(Settings(log_format="console"))) as c:
        yield c


def test_health_and_info(client: TestClient) -> None:
    health = client.get("/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "checks": {}}
    info = client.get("/v1/info").json()
    assert info["service"] == "assistant"
    assert info["api_versions"] == ["v1"]
    caps = info["capabilities"]
    assert caps["operations"] == ["onboarding", "improvement", "unknown_materials"]
    assert caps["neighbours"]["llm"] is False  # nothing configured: honest capabilities
    assert info["limits"]["defaults"]["llm"]["max_improvement_attempts"] == 3


def test_metrics_exposed(client: TestClient) -> None:
    client.get("/v1/info")
    body = client.get("/metrics").text
    assert 'jane_http_requests_total{method="GET",route="/v1/info",status="200"}' in body


def test_limits_come_from_config(client: TestClient) -> None:
    resolved = client.app.state.limits  # type: ignore[attr-defined]
    assert resolved.limits.jobs.max_concurrent_jobs == 2
    assert resolved.provenance()["jobs.max_concurrent_jobs"] == "platform"
    assert resolved.origin["jobs.max_concurrent_jobs"] == "platform:env"


def test_info_limits_and_health_timeout_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_ASSISTANT_HEALTH_CHECK_TIMEOUT_MS", "150")
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__LLM__MAX_ONBOARDING_SAMPLES", "25")
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__HARD_CAPS__LLM__MAX_IMPROVEMENT_ATTEMPTS", "2")
    app = build_app(Settings(log_format="console"))
    assert app.state.health.check_timeout_s == 0.15
    with TestClient(app) as c:
        limits = c.get("/v1/info").json()["limits"]
    assert limits["defaults"]["llm"]["max_onboarding_samples"] == 25
    assert limits["hard_caps"] == {"llm": {"max_improvement_attempts": 2}}


def test_unknown_route_is_problem(client: TestClient) -> None:
    r = client.get(
        "/v1/nope", headers={"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}
    )
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["code"] == "not_found"
    assert r.json()["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"


def test_without_neighbours_jobs_fail_with_upstream_unavailable(client: TestClient) -> None:
    r = client.post(
        "/v1/onboarding-sessions",
        json={"query": "https://shop.example.test/"},
        headers={"Idempotency-Key": "k"},
    )
    assert r.status_code == 202
    job_id = r.json()["job_id"]
    for _ in range(200):
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"failed", "succeeded"}:
            break
    assert job["status"] == "failed"
    assert job["error"]["code"] == "upstream_unavailable"
    session = client.get(f"/v1/onboarding-sessions/{r.json()['labels']['session_id']}").json()
    assert session["status"] == "failed" and session["error"]["code"] == "upstream_unavailable"


def test_name_without_search_provider_fails_clearly(client: TestClient) -> None:
    r = client.post(
        "/v1/onboarding-sessions", json={"query": "Shop Example"}, headers={"Idempotency-Key": "k2"}
    )
    job_id = r.json()["job_id"]
    for _ in range(200):
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"failed", "succeeded"}:
            break
    assert job["status"] == "failed" and "search provider" in job["error"]["detail"]


def test_missing_idempotency_key_rejected(client: TestClient) -> None:
    r = client.post("/v1/onboarding-sessions", json={"query": "x"})
    assert r.status_code == 422
    assert r.json()["errors"][0]["parameter"] == "Idempotency-Key"
