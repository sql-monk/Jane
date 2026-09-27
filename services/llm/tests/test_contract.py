"""Contract tests: every operation of ``llm.v1.yaml`` and ``handler.v1.yaml`` on the real app.

Requests and responses are validated by :class:`jane_kit.contracts.ContractClient` (skipped until
``contracts/`` exists in the checkout).
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import ContractClient, OpenAPISpec, contracts_dir
from jane_llm.packages import build_archive, read_dir

pytestmark = pytest.mark.contract

CONTRACTS = contracts_dir(Path(__file__).parent)
PACKAGE_DIR = Path(__file__).resolve().parents[1] / "packages" / "jane.llm-event-extractor"


def _spec(name: str) -> OpenAPISpec:
    if CONTRACTS is None or not (CONTRACTS / "openapi" / name).is_file():
        pytest.skip(f"contracts/openapi/{name} not available")
    return OpenAPISpec.load(CONTRACTS / "openapi" / name)


def _wait(api: ContractClient, job_id: str) -> dict[str, Any]:
    for _ in range(200):
        job = api.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            return dict(job)
        time.sleep(0.02)
    raise AssertionError("job did not finish")


def test_llm_api_matches_contract(client: TestClient, h: Any) -> None:
    api = ContractClient(_spec("llm.v1.yaml"), client)
    api.get("/v1/health")
    api.get("/v1/info")
    assert api.get("/v1/providers").json()["items"]
    api.get("/v1/providers/fake")
    assert api.get("/v1/providers/nope").status_code == 404
    api.put("/v1/providers/fake", json=h.priced_fake)
    assert client.put("/v1/providers/fake", json={"provider_id": "fake"}).status_code == 422
    assert (
        api.put("/v1/providers/fake", json=h.priced_fake, headers={"If-Match": '"stale"'}).status_code == 412
    )
    spare = {**h.priced_fake, "provider_id": "spare"}
    api.put("/v1/providers/spare", json=spare)
    api.get("/v1/model-aliases")
    api.put(
        "/v1/model-aliases/cheap",
        json={"alias": "cheap", "provider_id": "spare", "model_id": "fake-deterministic-1"},
    )
    assert (
        api.put(
            "/v1/model-aliases/bad", json={"alias": "bad", "provider_id": "x", "model_id": "y"}
        ).status_code
        == 422
    )
    assert api.delete("/v1/providers/spare").status_code == 409  # used by alias "cheap"
    api.put(
        "/v1/model-aliases/cheap",
        json={"alias": "cheap", "provider_id": "fake", "model_id": "fake-deterministic-1"},
    )
    assert api.delete("/v1/providers/spare").status_code == 204

    body = h.completion(scope={"purpose": "handler", "task_id": "t1", "source_id": "s1", "run_id": "run_1"})
    ok = api.post("/v1/completions", json=body, headers=h.idem())
    assert ok.status_code == 200 and ok.json()["valid"] is True
    text = api.post(
        "/v1/completions",
        json={k: v for k, v in body.items() if k != "output_schema"},
        headers=h.idem(),
    )
    assert "output_text" in text.json()
    job = api.post("/v1/completions", json={**body, "mode": "async"}, headers=h.idem())
    assert job.status_code == 202
    assert _wait(api, job.json()["job_id"])["status"] == "succeeded"
    assert api.post("/v1/completions", json={**body, "model": "nope"}, headers=h.idem()).status_code == 404
    assert api.post("/v1/completions", json=body).status_code == 422  # Idempotency-Key required
    assert client.post(
        "/v1/completions", content=b"{", headers={**h.idem(), "content-type": "application/json"}
    ).status_code in {400, 422}

    api.get("/v1/budgets")
    task = {
        "scope_type": "task",
        "scope_id": "t1",
        "budget": {"amount": 0.3, "currency": "USD", "period": "day"},
    }
    api.put("/v1/budgets/task/t1", json=task)
    assert client.put("/v1/budgets/task/t1", json={"scope_type": "task"}).status_code == 422
    exhausted = api.post("/v1/completions", json=body, headers=h.idem())
    assert exhausted.status_code == 429 and exhausted.json()["code"] == "budget_exhausted"
    assert api.delete("/v1/budgets/task/t1").status_code == 204
    assert api.delete("/v1/budgets/task/t1").status_code == 404
    for group in ("day", "model", "purpose", "scope"):
        api.get("/v1/usage", params={"group_by": group})
    api.get("/v1/usage", params={"scope_type": "task", "scope_id": "t1", "since": "2026-01-01T00:00:00Z"})
    assert api.get(f"/v1/jobs/{job.json()['job_id']}").status_code == 200
    assert api.post(f"/v1/jobs/{job.json()['job_id']}/cancel").status_code == 200  # already finished
    assert api.get("/v1/jobs/unknown").status_code == 404
    assert not [op for op in api.uncovered() if "cancel" not in op], api.uncovered()


def test_handler_api_matches_contract(client: TestClient, h: Any) -> None:
    api = ContractClient(_spec("handler.v1.yaml"), client)
    api.get("/v1/health")
    api.get("/v1/info")
    conn = {
        "connection_id": "llm-main",
        "kind": "llm_provider",
        "params": {"api_base": "http://llm.test"},
        "secret_refs": {"api_key": "env:JANE_TEST_UNSET_KEY"},
    }
    assert api.put("/v1/connections/llm-main", json=conn).status_code == 201
    assert api.put("/v1/connections/llm-main", json=conn).status_code == 200
    leak = {**conn, "params": {"api_key": "plain-value"}}
    bad = api.put("/v1/connections/llm-main", json=leak)
    assert bad.status_code == 422 and bad.json()["code"] == "secret_detected"
    assert api.get("/v1/connections").json()["items"][0]["connection_id"] == "llm-main"
    etag = api.get("/v1/connections/llm-main").headers["ETag"]
    assert api.put("/v1/connections/llm-main", json=conn, headers={"If-Match": etag}).status_code == 200
    tested = api.post("/v1/connections/llm-main/test").json()
    assert tested == {**tested, "ok": False, "secrets_resolved": {"api_key": False}}
    assert api.get("/v1/connections/nope").status_code == 404

    material = PACKAGE_DIR / "tests" / "concert" / "material.json"
    inv = {
        "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
        "inputs": [
            {"kind": "material", "material": json.loads(material.read_text(encoding="utf-8"))}
        ],
        "context": {"trace": {"source_id": "news-tg", "task_id": "events"}, "test_mode": True},
        "delivery": {"delivery_key": "c-1"},
    }
    r = api.post("/v1/invocations", json=inv, headers={"Idempotency-Key": "c-1"})
    assert r.status_code == 200
    result = r.json()
    replay = api.post("/v1/invocations", json=inv, headers={"Idempotency-Key": "c-1"})
    assert replay.json()["duplicate"] is True and replay.headers["Idempotency-Replayed"] == "true"
    api.get(f"/v1/invocations/{result['invocation_id']}")
    assert api.get("/v1/invocations/inv_missing").status_code == 404
    missing = {
        **inv,
        "handler": {"package_id": "jane.nope", "version": "1.0.0"},
        "delivery": {"delivery_key": "c-2"},
    }
    assert api.post("/v1/invocations", json=missing, headers={"Idempotency-Key": "c-2"}).status_code == 404
    digest = {
        **inv,
        "handler": {**inv["handler"], "digest": "sha256:" + "0" * 64},
        "delivery": {"delivery_key": "c-3"},
    }
    r = api.post("/v1/invocations", json=digest, headers={"Idempotency-Key": "c-3"})
    assert r.status_code == 422 and r.json()["code"] == "digest_mismatch"
    archive = build_archive(read_dir(PACKAGE_DIR))
    packed = {
        **inv,
        "package_archive": {
            "kind": "inline",
            "media_type": "application/zip",
            "encoding": "base64",
            "data": base64.b64encode(archive).decode(),
        },
        "delivery": {"delivery_key": "c-4"},
        "mode": "async",
    }
    job = api.post("/v1/invocations", json=packed, headers={"Idempotency-Key": "c-4"})
    assert job.status_code == 202
    assert _wait(api, job.json()["job_id"])["result"]["handler_kind"] == "llm"

    run = api.post("/v1/test-runs", json={"handler": inv["handler"], "tests": "all"}, headers=h.idem())
    assert run.status_code == 202
    report = _wait(api, run.json()["job_id"])["result"]
    assert report["passed"] + report["failed"] == 2
    assert api.delete("/v1/connections/llm-main").status_code == 204
    assert api.delete("/v1/connections/llm-main").status_code == 404
    assert not [op for op in api.uncovered() if "cancel" not in op], api.uncovered()
