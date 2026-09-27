"""Contract tests: responses of the real app against ``contracts/openapi/handler.v1.yaml`` (+ common.yaml)."""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_handler_runtime.app import build_app
from jane_handler_runtime.settings import Settings
from jane_kit.contracts import ContractClient, OpenAPISpec, contracts_dir

pytestmark = pytest.mark.contract

CONTRACTS = contracts_dir(Path(__file__).parent)


@pytest.fixture
def api(subprocess_settings: Settings) -> Iterator[ContractClient]:
    if CONTRACTS is None:
        pytest.skip("contracts/ not available")
    with TestClient(build_app(subprocess_settings)) as c:
        yield ContractClient(OpenAPISpec.load(CONTRACTS / "openapi" / "handler.v1.yaml"), c)


def test_handler_protocol_matches_contract(api: ContractClient, h: Any) -> None:
    api.get("/v1/health")
    api.get("/v1/info")
    body = h.invocation(h.example, h.product_material(), key="c-1")
    ok = api.post("/v1/invocations", json=body, headers={"Idempotency-Key": "c-1"})
    assert ok.status_code == 200
    replay = api.post("/v1/invocations", json=body, headers={"Idempotency-Key": "c-1"})
    assert replay.json()["duplicate"] is True
    api.get(f"/v1/invocations/{ok.json()['invocation_id']}")
    assert api.get("/v1/invocations/inv_missing").status_code == 404
    failed = h.invocation(h.probe, h.product_material(), key="c-2", params={"mode": "bad_entity"})
    assert (
        api.post("/v1/invocations", json=failed, headers={"Idempotency-Key": "c-2"}).json()["status"]
        == "failed"
    )
    bad = {**body, "params": {"default_currency": 5}, "delivery": {"delivery_key": "c-3"}}
    assert api.post("/v1/invocations", json=bad, headers={"Idempotency-Key": "c-3"}).status_code == 422
    digest = {
        **body,
        "handler": {**body["handler"], "digest": "sha256:" + "1" * 64},
        "delivery": {"delivery_key": "c-4"},
    }
    assert api.post("/v1/invocations", json=digest, headers={"Idempotency-Key": "c-4"}).status_code == 422
    job = api.post(
        "/v1/invocations",
        json={**body, "mode": "async", "delivery": {"delivery_key": "c-5"}},
        headers={"Idempotency-Key": "c-5"},
    )
    assert job.status_code == 202
    for _ in range(600):
        state = api.get(f"/v1/jobs/{job.json()['job_id']}").json()
        if state["status"] == "succeeded":
            break
        time.sleep(0.05)
    assert state["status"] == "succeeded"
    run = api.post(
        "/v1/test-runs",
        json={
            "handler": body["handler"],
            "package_archive": body["package_archive"],
            "tests": ["product-phone-alpha"],
        },
        headers={"Idempotency-Key": "c-6"},
    )
    assert run.status_code == 202
    assert api.post("/v1/jobs/job_missing/cancel").status_code == 404
    listed = api.get("/v1/connections")
    assert listed.json() == {"items": [], "next_cursor": None}
    put = api.put(
        "/v1/connections/results-pg",
        json={"connection_id": "results-pg", "kind": "postgresql", "params": {"host": "db"}},
        headers={"Idempotency-Key": "c-7"},
    )
    assert put.status_code == 501 and put.json()["code"] == "not_implemented"
    assert api.get("/v1/connections/results-pg").status_code == 404
    assert api.delete("/v1/connections/results-pg").status_code == 404
    assert api.post("/v1/connections/results-pg/test").status_code == 404
    assert api.uncovered() == []
