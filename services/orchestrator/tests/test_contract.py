"""Contract tests: every operation of ``orchestrator.v1.yaml`` is called on the real service and each
response is validated against the contract (``ContractClient``). Needs PostgreSQL (see conftest)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from orch_support import SPECS, Neighbours, catalog_task, price_task, source_doc, wait_until

from jane_kit.contracts import ContractClient

pytestmark = pytest.mark.contract


def test_every_operation_matches_contract(make_client: Any, neighbours: Neighbours) -> None:
    neighbours.registry.add("shop-example.product-extractor", "1.2.0")
    neighbours.registry.add("shop-example.product-extractor", "1.3.0")
    api = ContractClient(SPECS["orchestrator"], make_client())
    k = iter(range(1000))

    def idem() -> dict[str, str]:
        return {"Idempotency-Key": f"c-{next(k)}"}

    api.get("/v1/health")
    api.get("/v1/info")
    assert api.post("/v1/sources", json=source_doc(), headers=idem()).status_code == 201
    assert api.post("/v1/sources", json=source_doc(), headers=idem()).status_code == 409
    api.get("/v1/sources?kind=web&limit=1")
    src = api.get("/v1/sources/shop-example")
    api.put("/v1/sources/shop-example", json=source_doc(), headers={"If-Match": src.headers["etag"]})
    assert (
        api.put("/v1/sources/shop-example", json=source_doc(), headers={"If-Match": '"v0"'}).status_code
        == 412
    )
    assert api.get("/v1/sources/nope").status_code == 404
    assert api.post("/v1/tasks", json=catalog_task(), headers=idem()).status_code == 201
    assert api.post("/v1/tasks", json=price_task(), headers=idem()).status_code == 201
    bad = catalog_task(task_id="bad")
    bad["stages"][1]["inputs"] = [{"from": "missing"}]
    assert api.post("/v1/tasks", json=bad, headers=idem()).status_code == 422
    api.get("/v1/tasks")
    api.get("/v1/tasks?package_id=shop-example.product-extractor&package_version=1.2.0")
    task = api.get("/v1/tasks/shop-price-check")
    api.put("/v1/tasks/shop-price-check", json=price_task(), headers={"If-Match": task.headers["etag"]})
    api.post("/v1/task-validations", json=catalog_task())
    api.post("/v1/task-validations", json=bad)
    run = api.post("/v1/tasks/shop-catalog/runs", json={"reason": "contract"}, headers=idem())
    assert run.status_code == 202 and run.headers["location"] == f"/v1/jobs/{run.json()['job_id']}"
    run_id = run.json()["job_id"]
    assert api.post("/v1/tasks/shop-catalog/runs", json={}, headers=idem()).status_code == 409  # overlap skip
    wait_until(lambda: api.get(f"/v1/jobs/{run_id}").json()["status"] == "succeeded")
    api.get(f"/v1/runs/{run_id}")
    api.get("/v1/runs?task_id=shop-catalog&status=succeeded&since=2020-01-01T00:00:00Z")
    items = api.get(f"/v1/runs/{run_id}/items?stage_id=extract-products&status=completed").json()["items"]
    api.get(f"/v1/materials/{items[0]['material_id']}/trace")
    assert api.get("/v1/materials/web:none/trace").status_code == 404
    assert api.post(f"/v1/runs/{run_id}/cancel", json={"reason": "late"}).status_code == 200
    assert api.post(f"/v1/jobs/{run_id}/cancel").status_code == 200
    run2 = api.post("/v1/tasks/shop-price-check/runs", json={"test_mode": True}, headers=idem()).json()[
        "job_id"
    ]
    assert api.post(f"/v1/runs/{run2}/cancel", json={"reason": "stop"}).status_code in {200, 202}
    assert api.get("/v1/runs/nope").status_code == 404
    api.get("/v1/unknown-materials?source_id=shop-example&forwarded=false")
    api.get("/v1/problem-groups?source_id=shop-example&status=open")
    rep = api.post(
        "/v1/reprocessing",
        json={
            "task_id": "shop-catalog",
            "stored_materials": {"storage_connection_id": "raw-files"},
            "from_stage": "extract-products",
        },
        headers=idem(),
    )
    assert rep.status_code == 202
    url = "/v1/tasks/shop-catalog/stages/extract-products/activations"
    act = api.post(
        url,
        json={
            "kind": "activate",
            "package": {"package_id": "shop-example.product-extractor", "version": "1.3.0"},
        },
        headers=idem(),
    )
    assert act.status_code == 200
    deny = api.post(
        url,
        json={
            "kind": "auto_activate",
            "package": {"package_id": "shop-example.product-extractor", "version": "1.2.0"},
        },
        headers=idem(),
    )
    assert deny.status_code == 403
    api.get(url)
    conn = {"connection_id": "raw-files", "kind": "filesystem", "params": {"base_path": "/data/raw"}}
    put = api.put("/v1/connections/raw-files", json=conn)
    api.put("/v1/connections/raw-files", json=conn, headers={"If-Match": put.headers["etag"]})
    api.get("/v1/connections?kind=filesystem")
    api.get("/v1/connections/raw-files")
    assert api.put("/v1/connections/raw-files", json={**conn, "params": {"token": "x"}}).status_code == 422
    assert api.delete("/v1/connections/raw-files").status_code == 409
    api.put("/v1/connections/tmp", json={"connection_id": "tmp", "kind": "filesystem"})
    assert api.delete("/v1/connections/tmp").status_code == 204
    lim = api.get("/v1/limits/platform")
    api.put("/v1/limits/platform", json=lim.json(), headers={"If-Match": lim.headers["etag"]})
    api.get("/v1/limits/effective?task_id=shop-catalog&stage_id=extract-products")
    api.get("/v1/limits/effective?source_id=shop-example")
    assert api.get("/v1/limits/effective?task_id=nope").status_code == 404
    api.get("/v1/executors")
    api.get("/v1/audit-events?subject_type=stage")
    wait_until(
        lambda: api.get(f"/v1/jobs/{rep.json()['job_id']}").json()["status"] in {"succeeded", "failed"}
    )
    merge = {"Content-Type": "application/merge-patch+json"}
    groups = api.get("/v1/problem-groups").json()["items"]
    assert groups, "the unrecognized gift-card page should form a problem group"
    patch = {"status": "ignored", "note": "x"}
    SPECS["orchestrator"].validate_request(
        "PATCH", "/v1/problem-groups/x", patch, "application/merge-patch+json"
    )
    assert (
        api.patch(
            f"/v1/problem-groups/{groups[0]['group_id']}", content=json.dumps(patch), headers=merge
        ).status_code
        == 200
    )
    assert (
        api.patch("/v1/problem-groups/pg_none", content=json.dumps(patch), headers=merge).status_code == 404
    )
    api.get("/v1/jobs/nope")
    assert api.delete("/v1/sources/shop-example").status_code == 409
    wait_until(lambda: api.get(f"/v1/jobs/{run2}").json()["status"] in {"cancelled", "succeeded"})
    assert api.delete("/v1/tasks/shop-price-check").status_code == 204
    assert api.delete("/v1/tasks/shop-catalog").status_code == 204
    assert api.delete("/v1/sources/shop-example").status_code == 204
    missing = [op for op in api.uncovered()]
    assert missing == [], f"operations not exercised: {missing}"
    assert neighbours.all_violations() == []


def test_requests_to_neighbours_match_their_contracts(make_client: Any, neighbours: Neighbours) -> None:
    """Fakes validate every request the orchestrator sends (collector.v1, handler.v1, storage.v1)."""
    client = make_client()
    client.post("/v1/sources", json=source_doc(forward_unknown=True), headers={"Idempotency-Key": "n-1"})
    client.post("/v1/tasks", json=catalog_task(), headers={"Idempotency-Key": "n-2"})
    run_id = client.post("/v1/tasks/shop-catalog/runs", json={}, headers={"Idempotency-Key": "n-3"}).json()[
        "job_id"
    ]
    wait_until(lambda: client.get(f"/v1/runs/{run_id}").json()["status"] == "succeeded")
    assert neighbours.llm.effects  # unknown page forwarded (flag on)
    assert neighbours.all_violations() == []
    assert {p for _, p, _ in neighbours.collector.requests} >= {"/v1/collections"}
