"""WP-17 (post-M3 requests) against contract fakes: real orchestrator, real PostgreSQL.

R02 executors without managed connections, R05 ProblemGroup.note and collector-rules activations, R06 exact
selection of stored RAW, R25 attempt history, WP-05 aggregated test status of auto activation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from orch_support import SPECS, Neighbours, catalog_task, items_by_stage, source_doc, wait_until

pytestmark = pytest.mark.integration

ORCH = SPECS["orchestrator"]
_N = 0


def post(client: TestClient, url: str, body: Any = None) -> Any:
    global _N
    _N += 1
    return client.post(url, json=body, headers={"Idempotency-Key": f"m3-{_N}"})


def wait_run(client: TestClient, run_id: str, timeout: float = 60) -> dict[str, Any]:
    run: dict[str, Any] = wait_until(
        lambda: (
            (r := client.get(f"/v1/runs/{run_id}").json())["status"] in {"succeeded", "failed", "cancelled"}
            and r
        ),
        timeout,
    )
    return run


def setup(client: TestClient, task: dict[str, Any] | None = None, **source: Any) -> None:
    assert post(client, "/v1/sources", source_doc(**source)).status_code == 201
    r = post(client, "/v1/tasks", task or catalog_task())
    assert r.status_code == 201, r.text


def run_catalog(client: TestClient) -> dict[str, Any]:
    r = post(client, "/v1/tasks/shop-catalog/runs", {})
    assert r.status_code == 202, r.text
    run = wait_run(client, r.json()["job_id"])
    assert run["status"] == "succeeded", run
    return run


def reprocess(client: TestClient, **stored: Any) -> Any:
    return post(
        client,
        "/v1/reprocessing",
        {
            "task_id": "shop-catalog",
            "stored_materials": {"storage_connection_id": "raw-files", **stored},
            "from_stage": "extract-products",
            "reason": "WP-17",
        },
    )


def at(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# ------------------------------------------------------------------ R06: exact choice of stored RAW
def test_reprocessing_exact_object_ids(make_client: Any, neighbours: Neighbours, db_dsn: str) -> None:
    client = make_client()
    setup(client)
    run_catalog(client)
    storage = neighbours.storage
    chosen = [storage.object_order[3], storage.object_order[0]]
    expected_obs = [storage.stored_objects[oid]["material"]["observation_id"] for oid in chosen]
    listings = len(storage.list_queries)
    r = reprocess(client, object_ids=chosen)
    assert r.status_code == 202, r.text
    run = wait_run(client, r.json()["job_id"])
    assert run["status"] == "succeeded", run
    items = items_by_stage(db_dsn, run["run_id"])
    assert [i["observation_id"] for i in items["collect"]] == expected_obs  # exactly these, in order
    assert {i["stored_object_id"] for i in items["collect"]} == set(chosen)  # the exact RAW is recorded
    assert len(items["extract-products"]) == 2
    assert len(storage.list_queries) == listings  # read by id, no listing of the whole source
    assert storage.object_reads[-2:] == chosen
    # since/until still apply to the chosen objects (stored_at of the fake: 2026-09-27T10:00:06Z)
    later = reprocess(client, object_ids=chosen, since="2026-09-28T00:00:00Z")
    assert wait_run(client, later.json()["job_id"])["status"] == "succeeded"
    assert items_by_stage(db_dsn, later.json()["job_id"])["collect"] == []
    # a missing object fails the run instead of silently reprocessing nothing
    missing = reprocess(client, object_ids=["obj_missing"])
    failed = wait_run(client, missing.json()["job_id"])
    assert failed["status"] == "failed" and failed["error"]["code"] == "not_found", failed
    assert neighbours.all_violations() == []


def test_reprocessing_by_observation_and_material_ids(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client()
    setup(client)
    run_catalog(client)
    storage = neighbours.storage
    mats = [storage.stored_objects[oid]["material"] for oid in storage.object_order]
    by_obs = reprocess(client, observation_ids=[mats[1]["observation_id"], mats[4]["observation_id"]])
    run = wait_run(client, by_obs.json()["job_id"])
    assert run["status"] == "succeeded", run
    collected = items_by_stage(db_dsn, run["run_id"])["collect"]
    assert sorted(i["observation_id"] for i in collected) == sorted(
        [mats[1]["observation_id"], mats[4]["observation_id"]]
    )
    # material_ids reach storage as the multi-value filter (storage.v1 material_ids)
    by_mat = reprocess(client, material_ids=[mats[2]["material_id"], mats[0]["material_id"]])
    run = wait_run(client, by_mat.json()["job_id"])
    assert run["status"] == "succeeded", run
    sent = [v for k, v in storage.list_queries[-1] if k == "material_ids"]
    assert sorted(sent) == sorted([mats[2]["material_id"], mats[0]["material_id"]])
    assert len(items_by_stage(db_dsn, run["run_id"])["collect"]) == 2
    assert neighbours.all_violations() == []


def test_reprocessing_selection_size_is_capped_by_configuration(
    make_client: Any, neighbours: Neighbours, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__STORED_SELECTION_MAX_IDS", "2")
    client = make_client()
    setup(client)
    r = reprocess(client, object_ids=["obj_a", "obj_b", "obj_c"])
    assert r.status_code == 422 and r.json()["code"] == "limit_exceeded", r.text
    assert r.json()["details"]["limit"] == "engine.stored_selection_max_ids"


def test_many_material_ids_are_filtered_here_not_sent_to_storage(
    make_client: Any, neighbours: Neighbours, monkeypatch: pytest.MonkeyPatch, db_dsn: str
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__STORED_MATERIAL_IDS_PER_REQUEST", "1")
    client = make_client()
    setup(client)
    run_catalog(client)
    storage = neighbours.storage
    mats = [storage.stored_objects[oid]["material"] for oid in storage.object_order]
    r = reprocess(client, material_ids=[mats[0]["material_id"], mats[1]["material_id"]])
    run = wait_run(client, r.json()["job_id"])
    assert run["status"] == "succeeded", run
    assert all(k != "material_ids" for k, _ in storage.list_queries[-1])
    assert len(items_by_stage(db_dsn, run["run_id"])["collect"]) == 2


# ------------------------------------------------------------------ R25: attempt history in items and traces
def test_attempt_history_shows_that_a_retry_waited_for_its_backoff(
    make_client: Any, neighbours: Neighbours
) -> None:
    neighbours.runtime.fail_retryable["shop-example.product-extractor"] = 1
    client = make_client()
    setup(
        client,
        task=catalog_task(
            retries={"max_attempts": 3, "initial_backoff_ms": 400, "backoff_multiplier": 1, "jitter": False}
        ),
    )
    run = run_catalog(client)
    page = client.get(f"/v1/runs/{run['run_id']}/items", params={"stage_id": "extract-products"})
    ORCH.validate_response("get", f"/v1/runs/{run['run_id']}/items", 200, page.json(), "application/json")
    retried = [i for i in page.json()["items"] if i["attempts"] == 2]
    assert len(retried) == 1, page.json()
    item = retried[0]
    events = item["attempt_history"]
    assert [e["event"] for e in events] == ["claimed", "retry_scheduled", "claimed", "completed"]
    assert [e["attempt"] for e in events] == [1, 1, 2, 2]
    retry = events[1]
    assert retry["delay_ms"] == 400 and retry["code"] == "upstream_unavailable"
    assert at(retry["available_at"]) >= at(retry["at"])
    assert at(events[2]["at"]) >= at(retry["available_at"])  # the next claim did not start before the backoff
    assert "available_at" not in item  # only for queued/retrying items
    trace = client.get(f"/v1/materials/{item['material_id']}/trace")
    ORCH.validate_response(
        "get", f"/v1/materials/{item['material_id']}/trace", 200, trace.json(), "application/json"
    )
    stage = next(s for s in trace.json()["observations"][0]["stages"] if s["stage_id"] == "extract-products")
    assert stage["item_id"] == item["item_id"] and stage["status"] == "completed" and stage["attempts"] == 2
    assert stage["attempt_history"] == events
    once = next(i for i in page.json()["items"] if i["attempts"] == 1)
    assert [e["event"] for e in once["attempt_history"]] == ["claimed", "completed"]


def test_attempt_history_is_bounded_by_configuration(
    make_client: Any, neighbours: Neighbours, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ATTEMPT_HISTORY_MAX", "0")
    client = make_client()
    setup(client)
    run = run_catalog(client)
    items = client.get(f"/v1/runs/{run['run_id']}/items", params={"stage_id": "extract-products"}).json()
    assert items["items"] and all("attempt_history" not in i for i in items["items"])


# ------------------------------------------------------------------ R05: ProblemGroup.note
def test_problem_group_note_is_kept_and_returned(make_client: Any, neighbours: Neighbours) -> None:
    from orch_support import base_result

    def unrecognized(body: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
        r = base_result(body, "unrecognized", "extractor")
        r["unrecognized"] = {"partial": False, "signature": "missing-selector:.price"}
        return r

    neighbours.runtime.behaviors["shop-example.product-extractor"] = unrecognized
    client = make_client()
    setup(client)
    run_catalog(client)
    group = client.get("/v1/problem-groups").json()["items"][0]
    assert "note" not in group
    url = f"/v1/problem-groups/{group['group_id']}"
    patch = {
        "status": "in_progress",
        "assistant_job_id": "job_01J9ZX0000000000000000IMP",
        "note": "awaits approval",
    }
    r = client.patch(url, json=patch, headers={"Content-Type": "application/merge-patch+json"})
    assert r.status_code == 200, r.text
    ORCH.validate_response("patch", url, 200, r.json(), "application/json")
    assert r.json()["note"] == "awaits approval" and r.json()["status"] == "in_progress"
    again = client.patch(
        url, json={"status": "resolved"}, headers={"Content-Type": "application/merge-patch+json"}
    )
    assert again.json()["note"] == "awaits approval"  # a PATCH without note keeps it
    listed = client.get("/v1/problem-groups").json()["items"][0]
    assert listed["note"] == "awaits approval" and listed["status"] == "resolved"


# ------------------------------------------------------------------ R05: activations of collector rules
def test_collect_stage_activation_switches_collector_rules(make_client: Any, neighbours: Neighbours) -> None:
    reg = neighbours.registry
    reg.add("shop-example.web-rules", "1.0.0", kind="collector-rules")
    reg.add("shop-example.web-rules", "1.1.0", kind="collector-rules")
    reg.add("shop-example.product-extractor", "1.2.0")
    client = make_client()
    setup(client)  # the collect stage has no own rules: the source gives shop-example.web-rules@1.0.0
    url = "/v1/tasks/shop-catalog/stages/collect/activations"
    body = {"kind": "activate", "package": {"package_id": "shop-example.web-rules", "version": "1.1.0"}}
    r = post(client, url, body)
    assert r.status_code == 200, r.text
    ORCH.validate_response("post", url, 200, r.json(), "application/json")
    assert r.json()["previous"] == {"package_id": "shop-example.web-rules", "version": "1.0.0"}
    collect = client.get("/v1/tasks/shop-catalog").json()["stages"][0]
    assert collect["collector"]["rules"]["version"] == "1.1.0"
    assert collect["collector"]["rules"]["digest"].startswith("sha256:")
    run_catalog(client)
    assert neighbours.collector.collections, "no collection started"
    request = next(iter(neighbours.collector.collections.values())).request
    assert request["rules_ref"]["version"] == "1.1.0"  # the activated rules are used by the next run
    rb = post(client, url, {"kind": "rollback", "reason": "regression"})
    assert rb.status_code == 200 and rb.json()["package"]["version"] == "1.0.0", rb.text
    history = client.get(url).json()["items"]
    assert [a["kind"] for a in history] == ["rollback", "activate"]
    # an extractor is not collector rules
    wrong = post(
        client,
        url,
        {"kind": "activate", "package": {"package_id": "shop-example.product-extractor", "version": "1.2.0"}},
    )
    assert wrong.status_code == 422, wrong.text
    events = client.get("/v1/audit-events", params={"subject_type": "stage"}).json()["items"]
    assert {e["action"] for e in events} >= {"stage.activate", "stage.rollback"}


# ------------------------------------------------------------------ WP-05: tests passed on every binding
def test_auto_activate_requires_tests_passed_on_every_context(
    make_client: Any, neighbours: Neighbours
) -> None:
    reg = neighbours.registry
    reg.add("shop-example.product-extractor", "1.2.0")
    failing_binding = {
        "status": "failed",
        "contexts": [
            {"context": "bindings:shop-catalog/extract-products", "test_status": "failed", "reports": 1},
            {"context": "bindings:other/extract-products", "test_status": "passed", "reports": 1},
        ],
    }
    reg.add("shop-example.product-extractor", "1.3.0", test_status="passed", test_summary=failing_binding)
    all_passed = {**failing_binding, "status": "passed"}
    reg.add("shop-example.product-extractor", "1.4.0", test_status="passed", test_summary=all_passed)
    client = make_client()
    setup(client, change_policy={"llm_versions": "auto_after_checks"})
    url = "/v1/tasks/shop-catalog/stages/extract-products/activations"
    pkg = {"package_id": "shop-example.product-extractor"}
    refused = post(client, url, {"kind": "auto_activate", "package": {**pkg, "version": "1.3.0"}})
    assert refused.status_code == 403, refused.text
    assert refused.json()["details"]["reason"] == "tests_not_passed"  # last report passed, a binding did not
    ok = post(client, url, {"kind": "auto_activate", "package": {**pkg, "version": "1.4.0"}})
    assert ok.status_code == 200, ok.text


# ------------------------------------------------------------------ R02: executors without connections
@pytest.mark.parametrize("status", [501, 404])
def test_executor_without_managed_connections_is_not_required(
    make_client: Any, neighbours: Neighbours, status: int
) -> None:
    neighbours.runtime.connections_unsupported = status  # handler-runtime: PUT -> 501 (or no such path)
    client = make_client()
    conn = {"connection_id": "results-pg", "kind": "postgresql", "params": {"host": "postgres", "port": 5432}}
    assert client.put("/v1/connections/results-pg", json=conn).status_code == 200
    view = wait_until(
        lambda: (
            (v := client.get("/v1/connections/results-pg").json())
            and all(e["sync_status"] == "synced" for e in v["executors"])
            and "handler-runtime" not in {e["executor"] for e in v["executors"]}
            and v
        )
    )
    assert {e["executor"] for e in view["executors"]} == {"web-collector", "storage", "llm"}
    assert any(m == "PUT" for m, _, _ in neighbours.runtime.requests)  # it was asked once, not required
    assert "results-pg" not in neighbours.runtime.connections
    setup(client)
    run = run_catalog(client)  # extraction on the runtime works without its connections
    assert run["status"] == "succeeded"
