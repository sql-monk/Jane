"""Regression tests for review round 1 (based on the reviewer's reproductions)."""

from __future__ import annotations

import threading
import time
from typing import Any

import psycopg
import pytest
from orch_support import Neighbours, catalog_task, items_by_stage, source_doc, wait_until
from test_done_when import post, start, wait_run, worker_process

pytestmark = pytest.mark.integration


def _feed_done(db_dsn: str, run_id: str) -> bool:
    with psycopg.connect(db_dsn) as c:
        r = c.execute("SELECT feed_done FROM runs WHERE run_id = %s", (run_id,)).fetchone()
        return bool(r and r[0])


def test_cancel_then_worker_killed_run_becomes_cancelled(
    make_client: Any, neighbours: Neighbours, db_dsn: str, fast_engine: dict[str, str]
) -> None:
    api = make_client(run_workers=False)
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task()).status_code == 201
    neighbours.storage.hang_after_effect = threading.Event()
    run_id = start(api, "shop-catalog")
    victim = worker_process(db_dsn, neighbours, fast_engine, "victim")
    try:
        assert neighbours.storage.hung.wait(60)
        wait_until(lambda: _feed_done(db_dsn, run_id), 30)
        assert api.post(f"/v1/runs/{run_id}/cancel", json={"reason": "x"}).json()["status"] == "cancelling"
        victim.kill()
        victim.wait(30)
        survivor = worker_process(db_dsn, neighbours, fast_engine, "survivor")
        try:
            run = wait_run(api, run_id, 60)
        finally:
            survivor.kill()
            survivor.wait(30)
    finally:
        if victim.poll() is None:
            victim.kill()
    assert run["status"] == "cancelled", run
    active = [
        i for s in items_by_stage(db_dsn, run_id).values() for i in s if i["status"] in {"queued", "running"}
    ]
    assert active == []
    # the task is not blocked (overlap: skip): a new run can start
    assert post(api, "/v1/tasks/shop-catalog/runs", {}).status_code == 202


def test_worker_kill_does_not_spend_retry_attempts(
    make_client: Any, neighbours: Neighbours, db_dsn: str, fast_engine: dict[str, str]
) -> None:
    api = make_client(run_workers=False)
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task(retries={"max_attempts": 1})).status_code == 201
    neighbours.storage.hang_after_effect = threading.Event()
    run_id = start(api, "shop-catalog")
    victim = worker_process(db_dsn, neighbours, fast_engine, "victim")
    try:
        assert neighbours.storage.hung.wait(60)
        victim.kill()
        victim.wait(30)
        survivor = worker_process(db_dsn, neighbours, fast_engine, "survivor")
        try:
            run = wait_run(api, run_id, 60)
        finally:
            survivor.kill()
            survivor.wait(30)
    finally:
        if victim.poll() is None:
            victim.kill()
    assert run["status"] == "succeeded", run
    items = [i for s in items_by_stage(db_dsn, run_id).values() for i in s]
    assert all(i["status"] == "completed" for i in items)
    taken_over = [i for i in items if i["lease_reclaims"]]
    assert taken_over and all(i["attempts"] == 1 for i in taken_over)
    assert set(neighbours.storage.effects.values()) == {1}


def test_poison_item_fails_after_configured_lease_takeovers(
    make_client: Any, neighbours: Neighbours, db_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__MAX_LEASE_RECLAIMS", "2")
    api = make_client(run_workers=False)
    engine = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task()).status_code == 201
    run_id = start(api, "shop-catalog")
    feed = engine.claim_feed("w")
    engine.process_feed(feed, "w")
    item = engine.claim_item("w")
    with psycopg.connect(db_dsn) as c:  # simulate: workers died on it twice already
        c.execute(
            "UPDATE items SET lease_expires_at = now() - interval '1 second', lease_reclaims = 2 WHERE item_id = %s",
            (item["item_id"],),
        )
    again = engine.claim_item("w2")
    assert again["item_id"] == item["item_id"] and again["lease_reclaims"] == 3 and again["attempts"] == 1
    assert engine.process_item(again, "w2") == "failed"
    failed = next(
        i for s in items_by_stage(db_dsn, run_id).values() for i in s if i["item_id"] == item["item_id"]
    )
    assert failed["status"] == "failed" and "max_lease_reclaims" in failed["error"]["detail"]


@pytest.mark.parametrize(("overlap", "allowed"), [("queue", 1), ("allow", 2)])
def test_parallel_runs_limit_holds_with_many_workers(
    make_client: Any,
    neighbours: Neighbours,
    db_dsn: str,
    monkeypatch: pytest.MonkeyPatch,
    overlap: str,
    allowed: int,
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__WORKERS", "6")
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__POLL_INTERVAL_MS", "10")
    neighbours.runtime.delay_s = 0.05
    client = make_client()
    make_client()  # a second instance with 6 more workers
    task = catalog_task(
        schedule={"type": "manual", "overlap": overlap},
        limits={"concurrency": {"max_parallel_runs_per_task": 2}},
    )
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", task).status_code == 201
    peak = {"n": 0}
    stop = threading.Event()

    def sample() -> None:
        with psycopg.connect(db_dsn) as conn:
            while not stop.is_set():
                row = conn.execute(
                    "SELECT count(*) FROM runs WHERE status IN ('running', 'cancelling')"
                ).fetchone()
                peak["n"] = max(peak["n"], int(row[0]) if row else 0)
                time.sleep(0.002)

    t = threading.Thread(target=sample, daemon=True)
    t.start()
    for _ in range(6):
        ids = [start(client, "shop-catalog") for _ in range(4)]
        for rid in ids:
            assert wait_run(client, rid, 90)["status"] == "succeeded"
    stop.set()
    t.join(5)
    with psycopg.connect(db_dsn) as conn:
        rows = conn.execute("SELECT started_at, finished_at FROM runs ORDER BY started_at").fetchall()
    concurrent = max(sum(1 for s, f in rows if s <= start_ and f > start_) for start_, _ in rows)
    assert peak["n"] <= allowed, peak
    assert concurrent <= allowed
    if overlap == "queue":
        with psycopg.connect(db_dsn) as conn:
            order = conn.execute("SELECT run_id FROM runs ORDER BY seq").fetchall()
            by_start = conn.execute("SELECT run_id FROM runs ORDER BY started_at").fetchall()
        assert order == by_start  # FIFO


def test_run_timeout_after_feed_is_done(make_client: Any, neighbours: Neighbours, db_dsn: str) -> None:
    neighbours.storage.hang_after_effect = threading.Event()  # one storage call never returns
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert (
        post(client, "/v1/tasks", catalog_task(limits={"timeouts": {"run_timeout_ms": 2000}})).status_code
        == 201
    )
    run_id = start(client, "shop-catalog")
    wait_until(lambda: _feed_done(db_dsn, run_id), 30)
    run = wait_run(client, run_id, 30)
    assert run["status"] == "failed" and run["error"]["code"] == "timeout"


def test_llm_budgets_of_sources_and_tasks_are_synced(make_client: Any, neighbours: Neighbours) -> None:
    client = make_client()
    budget = {"amount": 5, "currency": "USD", "period": "day"}
    src = source_doc(limits={"llm": {"budget": budget, "max_requests_per_minute": 10}})
    assert post(client, "/v1/sources", src).status_code == 201
    task = catalog_task(limits={"llm": {"budget": {"amount": 1, "currency": "USD", "period": "run"}}})
    assert post(client, "/v1/tasks", task).status_code == 201
    llm = neighbours.llm
    wait_until(lambda: ("source", "shop-example") in llm.budgets and ("task", "shop-catalog") in llm.budgets)
    assert llm.budgets[("source", "shop-example")] == {
        "scope_type": "source",
        "scope_id": "shop-example",
        "budget": budget,
        "max_requests_per_minute": 10,
    }
    assert llm.budgets[("task", "shop-catalog")]["budget"]["period"] == "run"
    # removing the budget from the source deletes it in the gateway (the inherited one applies)
    cur = client.get("/v1/sources/shop-example")
    assert (
        client.put(
            "/v1/sources/shop-example", json=source_doc(), headers={"If-Match": cur.headers["etag"]}
        ).status_code
        == 200
    )
    wait_until(lambda: ("source", "shop-example") not in llm.budgets)
    # deleting the task deletes its budget
    assert client.delete("/v1/tasks/shop-catalog").status_code == 204
    wait_until(lambda: ("task", "shop-catalog") not in llm.budgets)
    assert neighbours.all_violations() == []


def test_activation_does_not_hold_task_lock_during_registry_calls(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    neighbours.registry.add("shop-example.product-extractor", "1.3.0")
    neighbours.registry.delay_s = 1.0
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", catalog_task()).status_code == 201
    url = "/v1/tasks/shop-catalog/stages/extract-products/activations"
    body = {
        "kind": "activate",
        "package": {"package_id": "shop-example.product-extractor", "version": "1.3.0"},
    }
    result: dict[str, Any] = {}
    t = threading.Thread(target=lambda: result.update(r=post(client, url, body)))
    t.start()
    wait_until(lambda: any(p.endswith("/1.3.0") for _, p, _ in neighbours.registry.requests), 10)
    # while the registry call is in flight the task row is free, and a concurrent change commits
    with psycopg.connect(db_dsn) as conn:
        conn.execute("SELECT 1 FROM tasks WHERE task_id = 'shop-catalog' FOR UPDATE NOWAIT")
        conn.execute("UPDATE tasks SET version = version + 1 WHERE task_id = 'shop-catalog'")
    t.join(10)
    assert result["r"].status_code == 409  # the task changed meanwhile: activation is not applied blindly
    assert result["r"].json()["retryable"] is True
    again = post(client, url, body)
    assert again.status_code == 200


def test_rate_limited_collection_restarts_after_retry_after(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    col = neighbours.collector
    col.rate_limit_after = 2  # the first collection hits rate_limited after two materials
    col.retry_after_seconds = 1
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert (
        post(
            client, "/v1/tasks", catalog_task(retries={"max_attempts": 3, "initial_backoff_ms": 10})
        ).status_code
        == 201
    )
    run = wait_run(client, start(client, "shop-catalog"), 60)
    assert run["status"] == "succeeded", run
    first, second = sorted(col.collections.values(), key=lambda c: c.started)
    assert first.request.get("mode", "full") == "full" and second.request["mode"] == "incremental"
    assert second.started - first.ended >= 1.0  # not earlier than retry_after_seconds
    assert len(items_by_stage(db_dsn, run["run_id"])["collect"]) == 6  # nothing lost, nothing duplicated
    assert neighbours.all_violations() == []


def test_rate_limited_collection_without_retries_fails_the_run(
    make_client: Any, neighbours: Neighbours
) -> None:
    neighbours.collector.rate_limit_after = 2
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", catalog_task(retries={"max_attempts": 1})).status_code == 201
    run = wait_run(client, start(client, "shop-catalog"), 60)
    assert run["status"] == "failed" and run["error"]["code"] == "rate_limited"
    assert len(neighbours.collector.collections) == 1


def test_collection_waits_for_its_connections_to_reach_the_collector(
    make_client: Any, neighbours: Neighbours, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__SCHEDULER_INTERVAL_MS", "700")  # sync runs late
    client = make_client()
    account = {
        "connection_id": "tg-main",
        "kind": "telegram_account",
        "secret_refs": {"session": "env:TG_SESSION"},
    }
    assert post(client, "/v1/sources", source_doc(connections={"account": "tg-main"})).status_code == 201
    assert post(client, "/v1/tasks", catalog_task()).status_code == 201
    assert client.put("/v1/connections/tg-main", json=account).status_code == 200
    run = wait_run(client, start(client, "shop-catalog"), 60)
    assert run["status"] == "succeeded"
    paths = [p for _, p, _ in neighbours.collector.requests]
    assert paths.index("/v1/connections/tg-main") < paths.index("/v1/collections")
    assert neighbours.collector.connections["tg-main"] == account  # only secret_refs, never values


# ---------------------------------------------------------------- WP-09a: reaper races and fairness
def _metric(client: Any, status: str) -> float:
    import re

    text = client.get("/metrics").text
    pattern = r"jane_orchestrator_runs_total\{status=\"" + re.escape(status) + r"\"\} ([0-9.]+)"
    m = re.search(pattern, text)
    return float(m.group(1)) if m else 0.0


def _drive_feeds(engine: Any, db_dsn: str, run_ids: list[str]) -> None:
    def done() -> bool:
        feed = engine.claim_feed("driver")
        if feed is not None:
            engine.process_feed(feed, "driver")
        with psycopg.connect(db_dsn) as c:
            n = c.execute(
                "SELECT count(*) FROM runs WHERE run_id = ANY(%s) AND feed_done", (run_ids,)
            ).fetchone()
            return bool(n and n[0] == len(run_ids))

    wait_until(done, 60)


def _race(engine: Any, n: int = 8) -> list[int]:
    barrier = threading.Barrier(n)
    out: list[int] = []
    lock = threading.Lock()

    def go() -> None:
        barrier.wait()
        r = engine.reap()
        with lock:
            out.append(r)

    threads = [threading.Thread(target=go) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(30)
    return out


def test_concurrent_reapers_fail_timed_out_run_once(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client(run_workers=False)
    engine = client.app.state.engine
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    task = catalog_task(limits={"timeouts": {"run_timeout_ms": 1000}})
    assert post(client, "/v1/tasks", task).status_code == 201
    run_id = start(client, "shop-catalog")
    _drive_feeds(engine, db_dsn, [run_id])
    with psycopg.connect(db_dsn, autocommit=True) as c:  # a collection still to cancel
        c.execute("UPDATE runs SET collector_cancelled = false WHERE run_id = %s", (run_id,))
    time.sleep(1.5)
    before_failed = _metric(client, "failed")
    before_cancel = len(neighbours.collector.cancelled)
    results = _race(engine)
    assert client.get(f"/v1/runs/{run_id}").json()["status"] == "failed"
    assert _metric(client, "failed") - before_failed == 1
    assert len(neighbours.collector.cancelled) - before_cancel == 1
    assert sum(results) == 1
    with psycopg.connect(db_dsn) as c:
        active = c.execute(
            "SELECT count(*) FROM items WHERE run_id = %s AND status IN ('queued','retrying','running')",
            (run_id,),
        ).fetchone()
    assert active is not None and active[0] == 0


def test_concurrent_reapers_close_cancelling_run_once(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client(run_workers=False)
    engine = client.app.state.engine
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", catalog_task()).status_code == 201
    run_id = start(client, "shop-catalog")
    _drive_feeds(engine, db_dsn, [run_id])
    with psycopg.connect(db_dsn, autocommit=True) as c:  # a worker holds one item, then dies
        c.execute(
            "UPDATE items SET status = 'running', lease_owner = 'dead', lease_expires_at = now() + interval '1 hour'"
            " WHERE item_id = (SELECT item_id FROM items WHERE run_id = %s AND status = 'queued' ORDER BY seq LIMIT 1)",
            (run_id,),
        )
    assert client.post(f"/v1/runs/{run_id}/cancel", json={"reason": "x"}).json()["status"] == "cancelling"
    with psycopg.connect(db_dsn, autocommit=True) as c:
        c.execute(
            "UPDATE items SET lease_expires_at = now() - interval '1 second' WHERE run_id = %s AND status = 'running'",
            (run_id,),
        )
    before = _metric(client, "cancelled")
    results = _race(engine)
    assert client.get(f"/v1/runs/{run_id}").json()["status"] == "cancelled"
    assert _metric(client, "cancelled") - before == 1
    assert sum(results) == 1


def test_reaper_reaches_orphaned_runs_beyond_batch_of_busy_runs(
    make_client: Any, neighbours: Neighbours, db_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__REAP_BATCH", "2")
    client = make_client(run_workers=False)
    engine = client.app.state.engine
    assert engine.core.engine.reap_batch == 2
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    task = catalog_task(
        schedule={"type": "manual", "overlap": "allow"},
        limits={"concurrency": {"max_parallel_runs_per_task": 10}},
    )
    assert post(client, "/v1/tasks", task).status_code == 201
    runs = [start(client, "shop-catalog") for _ in range(8)]
    _drive_feeds(engine, db_dsn, runs)
    busy, orphaned = runs[:5], runs[5:]
    with psycopg.connect(db_dsn, autocommit=True) as c:
        for run_id in runs:  # every run: one item held by a worker
            c.execute(
                "UPDATE items SET status = 'running', lease_owner = 'w', lease_expires_at = now() + interval '1 hour'"
                " WHERE item_id = (SELECT item_id FROM items WHERE run_id = %s AND status = 'queued'"
                " ORDER BY seq LIMIT 1)",
                (run_id,),
            )
    for run_id in runs:  # busy runs cancelled first: their updated_at is the oldest
        assert client.post(f"/v1/runs/{run_id}/cancel", json={}).json()["status"] == "cancelling"
    with psycopg.connect(db_dsn, autocommit=True) as c:  # the workers of the orphaned runs died
        c.execute(
            "UPDATE items SET lease_expires_at = now() - interval '1 second' WHERE run_id = ANY(%s)"
            " AND status = 'running'",
            (orphaned,),
        )
    for _ in range(3):
        engine.reap()
    status = {r: client.get(f"/v1/runs/{r}").json()["status"] for r in runs}
    assert all(status[r] == "cancelled" for r in orphaned), status
    assert all(status[r] == "cancelling" for r in busy), status  # live leases: left to their workers
