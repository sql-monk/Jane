"""plan.md §5 WP-09 «Готово, коли» — one test per condition:

1. after a worker is killed the chain completes without double effects;
2. several workers do not duplicate work;
3. the full-collection task and the price-check task are independent;
4. changing limits needs no code change.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from typing import Any

import psycopg
import pytest
from fastapi.testclient import TestClient
from orch_support import (
    CONTRACTS,
    Neighbours,
    catalog_task,
    default_site,
    items_by_stage,
    price_task,
    source_doc,
    wait_until,
)

pytestmark = pytest.mark.integration

_N = 0


def post(client: TestClient, url: str, body: Any = None) -> Any:
    global _N
    _N += 1
    return client.post(url, json=body, headers={"Idempotency-Key": f"dw-{_N}"})


def start(client: TestClient, task_id: str, body: Any = None) -> str:
    r = post(client, f"/v1/tasks/{task_id}/runs", body or {})
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def wait_run(client: TestClient, run_id: str, timeout: float = 60) -> Any:
    return wait_until(
        lambda: (
            (r := client.get(f"/v1/runs/{run_id}").json())["status"] in {"succeeded", "failed", "cancelled"}
            and r
        ),
        timeout,
    )


def worker_process(
    db_dsn: str, neighbours: Neighbours, fast_engine: dict[str, str], name: str
) -> subprocess.Popen[bytes]:
    env = {
        **os.environ,
        **fast_engine,
        "JANE_ORCHESTRATOR_DATABASE_URL": db_dsn,
        "JANE_ORCHESTRATOR_EXECUTORS": json.dumps(neighbours.executors()),
        "JANE_ORCHESTRATOR_CONTRACTS_DIR": str(CONTRACTS),
        "JANE_ORCHESTRATOR_INSTANCE_ID": name,
        "JANE_ORCHESTRATOR_SCHEDULER_ENABLED": "false",
        "JANE_ORCHESTRATOR_LOG_LEVEL": "WARNING",
        "JANE_ORCHESTRATOR_LIMITS__ENGINE__WORKERS": "1",
        "JANE_ORCHESTRATOR_LIMITS__ENGINE__LEASE_MS": "1500",
        "JANE_ORCHESTRATOR_LIMITS__ENGINE__HEARTBEAT_MS": "300",
    }
    return subprocess.Popen([sys.executable, "-m", "jane_orchestrator", "worker"], env=env)


def test_worker_killed_mid_chain_completes_without_double_effects(
    make_client: Any, neighbours: Neighbours, db_dsn: str, fast_engine: dict[str, str]
) -> None:
    api = make_client(run_workers=False)  # API only; work is done by worker processes
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task()).status_code == 201
    # The storage executor performs the first write, then never answers: the worker is killed mid-call,
    # after the effect happened but before the orchestrator recorded the result.
    neighbours.storage.hang_after_effect = threading.Event()
    run_id = start(api, "shop-catalog")
    first = worker_process(db_dsn, neighbours, fast_engine, "victim")
    try:
        assert neighbours.storage.hung.wait(60), "worker never reached the storage executor"
        first.kill()  # SIGKILL / TerminateProcess: no cleanup, lease stays until it expires
        first.wait(30)
        second = worker_process(db_dsn, neighbours, fast_engine, "survivor")
        try:
            run = wait_run(api, run_id, 90)
        finally:
            second.kill()
            second.wait(30)
    finally:
        if first.poll() is None:
            first.kill()
    assert run["status"] == "succeeded", run
    items = items_by_stage(db_dsn, run_id)
    assert all(i["status"] == "completed" for stage in items.values() for i in stage)
    assert len(items["store-raw"]) == 6 and len(items["store-products"]) == 5
    # no double effects: every delivery executed exactly once in every executor ...
    for fake in (neighbours.runtime, neighbours.storage):
        assert set(fake.effects.values()) == {1}, fake.effects
    assert sum(neighbours.storage.effects.values()) == 6 + 5
    assert len(neighbours.storage.stored_objects) == 6
    # ... and the interrupted delivery was retried with the same key and answered as a duplicate
    replayed = [k for k, n in neighbours.storage.duplicates.items() if n]
    assert replayed, "the killed delivery was not re-delivered"
    retried = [i for s in items.values() for i in s if i["delivery_key"] in replayed]
    assert retried and all(i["attempts"] >= 2 for i in retried)
    assert neighbours.all_violations() == []


def test_several_workers_do_not_duplicate_work(make_client: Any, neighbours: Neighbours, db_dsn: str) -> None:
    neighbours.collector.site = default_site(40, 0)
    neighbours.runtime.delay_s = 0.03
    neighbours.storage.delay_s = 0.01
    # two orchestrator instances on the same DB, each with 3 worker threads
    a = make_client()
    make_client()
    for c in (a,):
        c.app.state.core  # noqa: B018 - app started
    assert post(a, "/v1/sources", source_doc()).status_code == 201
    task = catalog_task(limits={"concurrency": {"max_parallel_stage_items": 8}})
    assert post(a, "/v1/tasks", task).status_code == 201
    run = wait_run(a, start(a, "shop-catalog"), 90)
    assert run["status"] == "succeeded"
    items = items_by_stage(db_dsn, run["run_id"])
    assert len(items["extract-products"]) == 40 and len(items["store-products"]) == 40
    for fake in (neighbours.runtime, neighbours.storage):
        assert set(fake.calls.values()) == {1}, "a delivery key was invoked more than once"
        assert set(fake.effects.values()) == {1}
        assert not fake.duplicates
    assert neighbours.runtime.max_concurrent >= 2, "work was not spread over several workers"
    assert all(i["attempts"] == 1 for s in items.values() for i in s if s is not items["collect"])


def test_full_collection_and_price_check_tasks_are_independent(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", catalog_task()).status_code == 201
    assert post(client, "/v1/tasks", price_task()).status_code == 201
    neighbours.runtime.delay_s = 0.05
    catalog_run = start(client, "shop-catalog")
    price_run = start(client, "shop-price-check")
    # cancelling one task's run does not touch the other
    second_price = None
    cancel = client.post(f"/v1/runs/{price_run}/cancel", json={"reason": "independence check"})
    assert cancel.status_code in {200, 202}
    wait_run(client, price_run)
    second_price = start(client, "shop-price-check")
    runs = {rid: wait_run(client, rid) for rid in (catalog_run, second_price)}
    assert runs[catalog_run]["status"] == "succeeded"
    assert runs[second_price]["status"] == "succeeded"
    # separate collections: price check only asked for its explicit URLs
    reqs = [c.request for c in neighbours.collector.collections.values()]
    assert any("urls" not in r for r in reqs)
    assert any(r.get("urls") == price_task()["input"]["urls"] for r in reqs)
    cat_items = items_by_stage(db_dsn, catalog_run)
    price_items = items_by_stage(db_dsn, second_price)
    assert set(price_items) == {"collect", "extract-price", "store-price"}
    assert len(price_items["collect"]) == 2 and len(cat_items["collect"]) == 6
    assert {i["handler"]["package_id"] for i in price_items["extract-price"]} == {
        "shop-example.price-extractor"
    }
    keys_cat = {i["delivery_key"] for s in cat_items.values() for i in s if i["delivery_key"]}
    keys_price = {i["delivery_key"] for s in price_items.values() for i in s if i["delivery_key"]}
    assert keys_cat and keys_price and not keys_cat & keys_price
    # own schedules: the price task has its interval schedule, the catalog task none
    tasks = {t["task_id"]: t for t in client.get("/v1/tasks").json()["items"]}
    assert "next_run_at" in tasks["shop-price-check"] and "next_run_at" not in tasks["shop-catalog"]
    # changing the price task does not change the catalog task or its runs
    doc = client.get("/v1/tasks/shop-price-check")
    changed = {**doc.json(), "title": "Price check v2"}
    r = client.put("/v1/tasks/shop-price-check", json=changed, headers={"If-Match": doc.headers["etag"]})
    assert r.status_code == 200
    assert client.get("/v1/tasks/shop-catalog").json() == catalog_task()
    assert client.get(f"/v1/runs/{catalog_run}").json()["task_etag"] == '"v1"'


def test_changing_limits_needs_no_code_change(make_client: Any, neighbours: Neighbours, db_dsn: str) -> None:
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", catalog_task()).status_code == 201
    neighbours.runtime.fail_retryable["shop-example.product-extractor"] = 10_000  # always a retryable failure

    def attempts_of(run_id: str) -> set[int]:
        return {i["attempts"] for i in items_by_stage(db_dsn, run_id)["extract-products"]}

    # platform level via the API
    limits = client.get("/v1/limits/platform")
    doc = limits.json()
    doc["defaults"]["retries"] = {
        **doc["defaults"].get("retries", {}),
        "max_attempts": 2,
        "initial_backoff_ms": 5,
        "max_backoff_ms": 20,
    }
    r = client.put("/v1/limits/platform", json=doc, headers={"If-Match": limits.headers["etag"]})
    assert r.status_code == 200, r.text
    run1 = wait_run(client, start(client, "shop-catalog"))
    assert attempts_of(run1["run_id"]) == {2}
    eff = client.get(
        "/v1/limits/effective", params={"task_id": "shop-catalog", "stage_id": "extract-products"}
    ).json()
    assert (
        eff["limits"]["retries"]["max_attempts"] == 2
        and eff["provenance"]["retries.max_attempts"] == "platform"
    )

    # task level via the task configuration
    task = client.get("/v1/tasks/shop-catalog")
    body = {**task.json(), "retries": {"max_attempts": 3, "initial_backoff_ms": 5}}
    assert (
        client.put(
            "/v1/tasks/shop-catalog", json=body, headers={"If-Match": task.headers["etag"]}
        ).status_code
        == 200
    )
    run2 = wait_run(client, start(client, "shop-catalog"))
    assert attempts_of(run2["run_id"]) == {3}
    eff = client.get(
        "/v1/limits/effective", params={"task_id": "shop-catalog", "stage_id": "extract-products"}
    ).json()
    assert eff["provenance"]["retries.max_attempts"] == "task"

    # request level (RunRequest.limits) and hard caps: a cap wins over a lower level
    doc = client.get("/v1/limits/platform")
    capped = {**doc.json(), "hard_caps": {"retries": {"max_attempts": 1}}}
    assert (
        client.put("/v1/limits/platform", json=capped, headers={"If-Match": doc.headers["etag"]}).status_code
        == 200
    )
    run3 = wait_run(client, start(client, "shop-catalog", {"limits": {"retries": {"max_attempts": 5}}}))
    assert attempts_of(run3["run_id"]) == {1}
    # the runs finished (failures were recorded as problems, on_failure=continue)
    assert {run1["status"], run2["status"], run3["status"]} == {"succeeded"}
    groups = client.get("/v1/problem-groups").json()["items"]
    assert groups and groups[0]["problem"] == "failed"
    # audit trail of the limit changes
    events = client.get("/v1/audit-events", params={"subject_type": "limits"}).json()["items"]
    assert len(events) == 2

    # engine knobs come from the environment (JANE_ORCHESTRATOR_LIMITS__ENGINE__*), see conftest FAST_ENGINE
    assert client.app.state.core.engine.poll_interval_ms == 20


def test_backpressure_bounded_queue_holds_back_collection(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    neighbours.collector.site = default_site(30, 0)
    neighbours.runtime.delay_s = 0.05
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    task = catalog_task(limits={"queue": {"max_inflight_materials": 3, "max_unacked_materials": 4}})
    assert post(client, "/v1/tasks", task).status_code == 201
    run_id = start(client, "shop-catalog")
    peak = {"inflight": 0, "backpressure": False}
    stop = threading.Event()

    def sample() -> None:
        with psycopg.connect(db_dsn) as conn:
            while not stop.is_set():
                row = conn.execute(
                    "SELECT count(DISTINCT observation_id) FROM items WHERE run_id = %s"
                    " AND status IN ('queued','retrying','leased','running')",
                    (run_id,),
                ).fetchone()
                bp = conn.execute("SELECT backpressure FROM runs WHERE run_id = %s", (run_id,)).fetchone()
                peak["inflight"] = max(peak["inflight"], int(row[0]) if row else 0)
                peak["backpressure"] = peak["backpressure"] or bool(bp and bp[0])
                time.sleep(0.01)

    t = threading.Thread(target=sample, daemon=True)
    t.start()
    run = wait_run(client, run_id, 90)
    stop.set()
    t.join(5)
    assert run["status"] == "succeeded"
    assert peak["inflight"] <= 3, peak
    assert peak["backpressure"], "the feed was never held back"
    col = next(iter(neighbours.collector.collections.values()))
    assert col.request["limits"]["queue"]["max_unacked_materials"] == 4
    assert col.max_unacked_seen <= 4  # the collector buffer bounded what it emitted
    assert len(items_by_stage(db_dsn, run_id)["collect"]) == 30
