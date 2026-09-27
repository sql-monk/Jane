"""Contract tests: every operation of ``contracts/openapi/assistant.v1.yaml`` on the real app.

Responses go through ``ContractClient`` (status + schema); job results are validated against the
result schemas of the contract (``OnboardingSession``, ``AcceptanceResult``, ``ImprovementResult``,
``UnknownMaterialResult``). Neighbours are contract-bound fakes (see ``assistant_fakes``).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from assistant_fakes import World
from fastapi.testclient import TestClient

from jane_assistant.app import build_app
from jane_assistant.settings import Settings
from jane_kit.contracts import OpenAPISpec

pytestmark = pytest.mark.contract


def test_common_resources_match_contract(contracts: Path) -> None:
    common = OpenAPISpec.load(contracts / "openapi" / "common.yaml")
    with TestClient(build_app(Settings(log_format="console"))) as client:
        common.validate_component("Health", client.get("/v1/health").json())
        common.validate_component("ServiceInfo", client.get("/v1/info").json())
        common.validate_component("Problem", client.get("/v1/jobs/unknown").json())
        r = client.post(
            "/v1/onboarding-sessions",
            json={"query": "https://x.example.test/"},
            headers={"Idempotency-Key": "c"},
        )
        common.validate_component("Job", r.json())
        for _ in range(100):
            body = client.get(f"/v1/jobs/{r.json()['job_id']}").json()
            common.validate_component("Job", body)
            if body["status"] in {"failed", "succeeded"}:
                break
            time.sleep(0.01)


def test_every_operation_is_covered(w: World) -> None:
    api = w.api
    api.get("/v1/health")
    api.get("/v1/info")
    r = api.post(
        "/v1/onboarding-sessions",
        json={"query": "Shop Example kettles", "expected_entity_types": ["product"]},
        headers={"Idempotency-Key": "a"},
    )
    sid = r.json()["labels"]["session_id"]
    w.result(r.json()["job_id"], "OnboardingSession")
    sel = api.post(f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"})
    w.result(sel.json()["job_id"], "OnboardingSession")
    api.get(f"/v1/onboarding-sessions/{sid}")
    api.get("/v1/onboarding-sessions/onb_nope")
    api.post(f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_2"})  # 409
    acc = api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
        json={"activate": False},
        headers={"Idempotency-Key": "b"},
    )
    w.result(acc.json()["job_id"], "AcceptanceResult")
    api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p9/acceptance", json={}, headers={"Idempotency-Key": "b2"}
    )  # 409 completed
    api.post(
        "/v1/improvement-runs",
        json={
            "package": {"package_id": "nope.pkg", "version": "1.0.0"},
            "problem_samples": [{"material_ref": {"storage_connection_id": "raw", "object_id": "o"}}],
        },
        headers={"Idempotency-Key": "c"},
    )
    bad = w.client.post(
        "/v1/improvement-runs",
        json={"package": {"package_id": "x", "version": "1"}, "problem_samples": []},
        headers={"Idempotency-Key": "d"},
    )
    w.spec.validate_response("POST", "/v1/improvement-runs", bad.status_code, bad.json(), bad.headers["content-type"])
    mat = w.collector._items({"collector": "web", "scope": {"allowed_domains": ["shop.example.test"]}}, "s")[0]
    api.post(
        "/v1/unknown-materials",
        json={"source_id": "s", "forward_unknown_to_llm": False, "material": mat},
        headers={"Idempotency-Key": "e"},
    )  # 403
    job = api.post(
        "/v1/unknown-materials",
        json={"source_id": "s", "forward_unknown_to_llm": True, "material": mat},
        headers={"Idempotency-Key": "f"},
    )
    w.result(job.json()["job_id"], "UnknownMaterialResult")
    api.get(f"/v1/jobs/{job.json()['job_id']}")
    api.post(f"/v1/jobs/{job.json()['job_id']}/cancel", json={"reason": "done already"})  # 200 terminal
    assert api.uncovered() == []
