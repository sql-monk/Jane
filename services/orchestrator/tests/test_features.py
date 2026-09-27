"""Feature tests of WP-09 against contract fakes (real orchestrator, real PostgreSQL)."""

from __future__ import annotations

import time
from typing import Any

import pytest
from fastapi.testclient import TestClient
from orch_support import Neighbours, catalog_task, items_by_stage, price_task, source_doc, wait_until

pytestmark = pytest.mark.integration

_N = 0


def post(client: TestClient, url: str, body: Any = None, key: str | None = None) -> Any:
    global _N
    _N += 1
    return client.post(url, json=body, headers={"Idempotency-Key": key or f"ft-{_N}"})


def start(client: TestClient, task_id: str = "shop-catalog", body: Any = None) -> str:
    r = post(client, f"/v1/tasks/{task_id}/runs", body or {})
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def wait_run(client: TestClient, run_id: str, timeout: float = 60) -> dict[str, Any]:
    return wait_until(
        lambda: (
            (r := client.get(f"/v1/runs/{run_id}").json())["status"] in {"succeeded", "failed", "cancelled"}
            and r
        ),
        timeout,
    )


def setup(
    client: TestClient, source: dict[str, Any] | None = None, task: dict[str, Any] | None = None
) -> None:
    assert post(client, "/v1/sources", source or source_doc()).status_code == 201
    r = post(client, "/v1/tasks", task or catalog_task())
    assert r.status_code == 201, r.text


def test_cancel_stops_collection_and_pending_items(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    from orch_support import default_site

    neighbours.collector.site = default_site(30, 0)
    neighbours.runtime.delay_s = 0.2
    client = make_client()
    setup(client, task=catalog_task(limits={"concurrency": {"max_parallel_stage_items": 1}, "queue": {"max_inflight_materials": 2}}))
    run_id = start(client)
    wait_until(lambda: sum(neighbours.runtime.calls.values()) >= 1)
    r = client.post(f"/v1/jobs/{run_id}/cancel", json={"reason": "wrong limits"})
    assert r.status_code == 202
    assert r.json()["status"] in {"cancelling", "cancelled"}
    assert r.json()["cancellation"]["reason"] == "wrong limits"
    run = wait_run(client, run_id)
    assert run["status"] == "cancelled"
    calls = sum(neighbours.runtime.calls.values())
    time.sleep(0.5)
    assert sum(neighbours.runtime.calls.values()) == calls, "invocations continued after cancellation"
    items = items_by_stage(db_dsn, run_id)
    assert any(i["status"] == "cancelled" for i in items["extract-products"])
    assert neighbours.collector.cancelled == [run["collection_id"]]
    again = client.post(f"/v1/runs/{run_id}/cancel")
    assert again.status_code == 200 and again.json()["status"] == "cancelled"


def test_material_trace_links_stages_results_and_versions(make_client: Any, neighbours: Neighbours) -> None:
    client = make_client()
    setup(client)
    run = wait_run(client, start(client))
    items = client.get(
        f"/v1/runs/{run['run_id']}/items", params={"stage_id": "extract-products", "limit": 1}
    ).json()
    assert items["next_cursor"] is not None and len(items["items"]) == 1
    material_id = items["items"][0]["material_id"]
    trace = client.get(f"/v1/materials/{material_id}/trace").json()
    assert trace["source_id"] == "shop-example" and trace["url"].startswith(
        "https://shop.example.test/product/"
    )
    obs = trace["observations"][0]
    assert obs["run_id"] == run["run_id"] and obs["task_id"] == "shop-catalog" and obs["content_sha256"]
    stages = {s["stage_id"]: s for s in obs["stages"]}
    assert set(stages) == {"store-raw", "extract-products", "store-products"}
    assert stages["extract-products"]["handler"]["version"] == "1.2.0"
    assert stages["extract-products"]["handler"]["digest"].startswith("sha256:")
    assert stages["extract-products"]["outputs"][0]["canonical_key"].startswith('shop-example|{"sku":')
    assert stages["store-raw"]["outputs"][0]["kind"] == "stored_object"
    assert stages["store-products"]["outputs"][0]["connection_id"] == "results-pg"
    assert client.get("/v1/materials/web:nope/trace").status_code == 404


def test_unknown_material_goes_to_llm_only_with_flag(make_client: Any, neighbours: Neighbours) -> None:
    client = make_client()
    setup(client)
    run1 = wait_run(client, start(client))
    assert run1["counters"]["unknown_materials"] == 1
    assert neighbours.llm.calls == {}, "LLM called although the flag is off"
    unknown = client.get("/v1/unknown-materials", params={"forwarded": "false"}).json()["items"]
    assert len(unknown) == 1 and unknown[0]["url"].endswith("/gift-cards/0")
    assert "forward_unknown_to_llm=false" in unknown[0]["reason"]
    # enable «Передавати в LLM невідомі сторінки» on the source (no code change)
    src = client.get("/v1/sources/shop-example")
    body = {**src.json(), "forward_unknown_to_llm": True}
    assert (
        client.put(
            "/v1/sources/shop-example", json=body, headers={"If-Match": src.headers["etag"]}
        ).status_code
        == 200
    )
    run2 = wait_run(client, start(client))
    assert run2["status"] == "succeeded"
    assert sum(neighbours.llm.effects.values()) == 1
    req = next(b for m, p, b in neighbours.llm.requests if p == "/v1/invocations")
    assert req["inputs"][0]["material"]["locator"]["url"].endswith("/gift-cards/0")
    forwarded = client.get("/v1/unknown-materials", params={"forwarded": "true"}).json()["items"]
    assert len(forwarded) == 1 and forwarded[0]["run_id"] == run2["run_id"]
    assert run2["costs"]["llm"] == {"amount": 0.01, "currency": "USD"}
    # the task level overrides the source (explicit false)
    v = client.post("/v1/task-validations", json=catalog_task(forward_unknown_to_llm=False)).json()
    assert v["valid"] and v["effective_forward_unknown_to_llm"] is False
    assert any(w["code"] == "unknown_flag_off" for w in v["warnings"])


def test_reprocessing_stored_raw(make_client: Any, neighbours: Neighbours, db_dsn: str) -> None:
    client = make_client()
    setup(client)
    wait_run(client, start(client))
    stored = len(neighbours.storage.stored_objects)
    assert stored == 6
    before = sum(neighbours.runtime.effects.values())
    r = post(
        client,
        "/v1/reprocessing",
        {
            "task_id": "shop-catalog",
            "stored_materials": {"storage_connection_id": "raw-files"},
            "from_stage": "extract-products",
            "reason": "fix",
        },
    )
    assert r.status_code == 202, r.text
    run = wait_run(client, r.json()["job_id"])
    assert run["status"] == "succeeded" and run["trigger"] == "reprocess"
    items = items_by_stage(db_dsn, run["run_id"])
    assert len(items["collect"]) == 6
    assert len(items["extract-products"]) == 6  # injected at from_stage, no new collection
    assert "store-raw" not in items
    assert len(items["store-products"]) == 5
    assert sum(neighbours.runtime.effects.values()) == before + 6
    assert len(neighbours.collector.collections) == 1


def test_activation_rollback_and_auto_activate_policy(make_client: Any, neighbours: Neighbours) -> None:
    reg = neighbours.registry
    reg.add("shop-example.product-extractor", "1.2.0")
    reg.add("shop-example.product-extractor", "1.3.0")
    reg.add("shop-example.product-extractor", "1.4.0-draft.1", status="draft", test_status="unknown")
    client = make_client()
    setup(client)
    url = "/v1/tasks/shop-catalog/stages/extract-products/activations"
    r = post(
        client,
        url,
        {
            "kind": "activate",
            "package": {"package_id": "shop-example.product-extractor", "version": "1.3.0"},
            "reason": "ok",
        },
    )
    assert r.status_code == 200, r.text
    act = r.json()
    assert act["previous"]["version"] == "1.2.0" and act["package"]["digest"].startswith("sha256:")
    task = client.get("/v1/tasks/shop-catalog").json()
    stage = next(s for s in task["stages"] if s["stage_id"] == "extract-products")
    assert stage["handler"]["version"] == "1.3.0"
    draft = post(
        client,
        url,
        {
            "kind": "activate",
            "package": {"package_id": "shop-example.product-extractor", "version": "1.4.0-draft.1"},
        },
    )
    assert draft.status_code == 409
    rb = post(client, url, {"kind": "rollback", "reason": "regression"})
    assert rb.status_code == 200 and rb.json()["package"]["version"] == "1.2.0"
    # auto_activate: source policy manual_approval → 403 source_policy
    auto = {
        "kind": "auto_activate",
        "package": {"package_id": "shop-example.product-extractor", "version": "1.3.0"},
    }
    r = post(client, url, auto)
    assert r.status_code == 403 and r.json()["details"]["reason"] == "source_policy"
    src = client.get("/v1/sources/shop-example")
    body = {**src.json(), "change_policy": {"llm_versions": "auto_after_checks"}}
    assert client.put("/v1/sources/shop-example", json=body).status_code == 200
    reg.packages["shop-example.product-extractor"]["auto_changes_allowed"] = False
    r = post(client, url, auto)
    assert r.status_code == 403 and r.json()["details"]["reason"] == "package_auto_changes_forbidden"
    reg.packages["shop-example.product-extractor"]["auto_changes_allowed"] = True
    reg.versions[("shop-example.product-extractor", "1.3.0")]["test_status"] = "failed"
    r = post(client, url, auto)
    assert r.status_code == 403 and r.json()["details"]["reason"] == "tests_not_passed"
    reg.versions[("shop-example.product-extractor", "1.3.0")]["test_status"] = "passed"
    r = post(client, url, auto)
    assert r.status_code == 200 and r.json()["kind"] == "auto_activate"
    history = client.get(url).json()["items"]
    assert [a["kind"] for a in history] == ["auto_activate", "rollback", "activate"]
    audit = client.get("/v1/audit-events", params={"subject_type": "stage"}).json()["items"]
    assert [e["action"] for e in audit] == ["stage.auto_activate", "stage.rollback", "stage.activate"]
    # listTasks?package_id= finds the bindings of a shared package
    tasks = client.get("/v1/tasks", params={"package_id": "shop-example.product-extractor"}).json()["items"]
    assert [t["task_id"] for t in tasks] == ["shop-catalog"]
    assert tasks[0]["package_stages"][0]["package"]["version"] == "1.3.0"
    assert (
        client.get(
            "/v1/tasks", params={"package_id": "shop-example.product-extractor", "package_version": "9.9.9"}
        ).json()["items"]
        == []
    )
    rules = client.get("/v1/tasks", params={"package_id": "shop-example.web-rules"}).json()["items"]
    assert rules[0]["package_stages"] == [
        {"stage_id": "collect", "package": {"package_id": "shop-example.web-rules", "version": "1.0.0"}}
    ]


def test_connections_registry_syncs_executors_without_secrets(
    make_client: Any, neighbours: Neighbours
) -> None:
    client = make_client()
    conn = {
        "connection_id": "results-pg",
        "kind": "postgresql",
        "params": {"host": "postgres", "port": 5432, "database": "jane_results"},
        "secret_refs": {"username": "env:RESULTS_PG_USER", "password": "env:RESULTS_PG_PASSWORD"},
    }
    r = client.put("/v1/connections/results-pg", json=conn)
    assert r.status_code == 200, r.text
    assert {e["sync_status"] for e in r.json()["executors"]} == {"pending"}
    view = wait_until(
        lambda: (
            (v := client.get("/v1/connections/results-pg").json())
            and all(e["sync_status"] == "synced" for e in v["executors"])
            and v
        )
    )
    assert {e["executor"] for e in view["executors"]} == {
        "web-collector",
        "handler-runtime",
        "storage",
        "llm",
    }
    assert neighbours.storage.connections["results-pg"] == conn
    assert neighbours.collector.connections["results-pg"] == conn
    bad = {**conn, "params": {"host": "x", "password": "hunter2"}}
    r = client.put("/v1/connections/results-pg", json=bad)
    assert r.status_code == 422 and r.json()["code"] == "secret_detected"
    stale = client.put("/v1/connections/results-pg", json=conn, headers={"If-Match": '"v99"'})
    assert stale.status_code == 412
    setup(client)
    assert client.delete("/v1/connections/results-pg").status_code == 409  # referenced by a stage
    assert client.delete("/v1/tasks/shop-catalog").status_code == 204
    assert client.delete("/v1/connections/results-pg").status_code == 204
    wait_until(lambda: "results-pg" not in neighbours.storage.connections)


def test_schedule_creates_runs_and_overlap_skip(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client()
    task = price_task()
    task["schedule"] = {"type": "interval", "interval_seconds": 1, "overlap": "skip"}
    setup(client, task=task)
    runs = wait_until(
        lambda: (
            (r := client.get("/v1/runs", params={"task_id": "shop-price-check"}).json()["items"])
            and len(r) >= 2
            and r
        ),
        30,
    )
    assert all(r["trigger"] == "schedule" for r in runs)
    # disable → no more runs
    doc = client.get("/v1/tasks/shop-price-check")
    body = {**doc.json(), "enabled": False}
    assert (
        client.put(
            "/v1/tasks/shop-price-check", json=body, headers={"If-Match": doc.headers["etag"]}
        ).status_code
        == 200
    )
    for r in client.get("/v1/runs", params={"task_id": "shop-price-check"}).json()["items"]:
        wait_run(client, r["run_id"])
    n = len(client.get("/v1/runs", params={"task_id": "shop-price-check"}).json()["items"])
    time.sleep(1.5)
    assert len(client.get("/v1/runs", params={"task_id": "shop-price-check"}).json()["items"]) == n


def test_test_mode_and_idempotent_start(make_client: Any, neighbours: Neighbours) -> None:
    client = make_client()
    setup(client)
    body = {
        "reason": "dry run",
        "test_mode": True,
        "input_override": {"urls": ["https://shop.example.test/product/a-1"]},
    }
    a = post(client, "/v1/tasks/shop-catalog/runs", body, key="same-key")
    b = post(client, "/v1/tasks/shop-catalog/runs", body, key="same-key")
    assert a.status_code == b.status_code == 202
    assert a.json()["job_id"] == b.json()["job_id"] and b.headers["idempotency-replayed"] == "true"
    other = post(client, "/v1/tasks/shop-catalog/runs", {"reason": "x"}, key="same-key")
    assert other.status_code == 422 and other.json()["code"] == "idempotency_key_reused"
    run = wait_run(client, a.json()["job_id"])
    assert run["test_mode"] is True and run["counters"]["materials"] == 1
    writes = [b for m, p, b in neighbours.storage.requests if p == "/v1/invocations"]
    assert writes and all(w["context"]["test_mode"] is True for w in writes)
    assert neighbours.storage.stored_objects == {}  # nothing written to working data


def test_invalid_task_rejected(make_client: Any) -> None:
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    task = catalog_task()
    task["stages"][1]["inputs"] = [{"from": "missing"}]
    r = post(client, "/v1/tasks", task)
    assert r.status_code == 422 and r.json()["errors"][0]["pointer"] == "/stages/1/inputs/0/from"
    cyc = catalog_task()
    cyc["stages"][2]["inputs"].append({"from": "store-products"})
    v = client.post("/v1/task-validations", json=cyc).json()
    assert v["valid"] is False and any(e["code"] == "cycle" for e in v["errors"])
    typo = {**catalog_task(), "stagez": []}
    assert post(client, "/v1/tasks", typo).status_code == 422
