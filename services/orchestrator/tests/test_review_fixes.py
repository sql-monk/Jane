"""Regression tests for review round 1 (based on the reviewer's reproductions)."""

from __future__ import annotations

import threading
import time
from typing import Any

import psycopg
import pytest
from orch_support import Neighbours, catalog_task, items_by_stage, source_doc, wait_until
from test_done_when import post, start, wait_run, worker_process

from jane_orchestrator.runs import problem

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
        # A terminal material page still needs one cursor-confirming pull. With one worker
        # blocked in storage, cancellation must work even before that final acknowledgement.
        assert not _feed_done(db_dsn, run_id)
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


def test_retry_with_same_delivery_key_sends_identical_handler_body(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    """A retry must not turn the same Idempotency-Key into a different request (422)."""
    api = make_client()
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert (
        post(api, "/v1/tasks", catalog_task(retries={"max_attempts": 2, "initial_backoff_ms": 5})).status_code
        == 201
    )
    package_id = "shop-example.product-extractor"
    neighbours.runtime.fail_retryable[package_id] = 1
    run_id = start(api, "shop-catalog")
    run = wait_run(api, run_id, 60)
    assert run["status"] == "succeeded", run
    calls = [
        body
        for method, path, body in neighbours.runtime.requests
        if method == "POST" and path == "/v1/invocations" and body["handler"]["package_id"] == package_id
    ]
    by_key: dict[str, list[dict[str, Any]]] = {}
    for body in calls:
        by_key.setdefault(body["delivery"]["delivery_key"], []).append(body)
    retried = [bodies for bodies in by_key.values() if len(bodies) > 1]
    assert len(retried) == 1
    assert retried[0][0] == retried[0][1]
    assert "attempt" not in retried[0][0]["context"]
    assert any(i["attempts"] == 2 for i in items_by_stage(db_dsn, run_id)["extract-products"])


@pytest.mark.parametrize(
    ("max_wait_ms", "outcome"),
    [(5000, "success"), (300, "retrying")],
)
def test_reclaimed_in_progress_delivery_keeps_attempt_and_key(
    make_client: Any,
    neighbours: Neighbours,
    db_dsn: str,
    monkeypatch: pytest.MonkeyPatch,
    max_wait_ms: int,
    outcome: str,
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__IDEMPOTENCY_IN_PROGRESS_POLL_MS", "20")
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__IDEMPOTENCY_IN_PROGRESS_RETRY_MS", "20")
    monkeypatch.setenv(
        "JANE_ORCHESTRATOR_LIMITS__ENGINE__IDEMPOTENCY_IN_PROGRESS_MAX_WAIT_MS", str(max_wait_ms)
    )
    api = make_client(run_workers=False)
    engine = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task(retries={"max_attempts": 1})).status_code == 201
    run_id = start(api, "shop-catalog")
    for _ in range(10):
        feed = engine.claim_feed("feed")
        if feed is not None:
            engine.process_feed(feed, "feed")
        if items_by_stage(db_dsn, run_id).get("store-raw"):
            break
    first = engine.claim_item("first")
    assert first is not None and first["stage_id"] == "store-raw"
    key = first["delivery_key"]
    original_can_finish = threading.Event()
    neighbours.storage.pause_before_effect = original_can_finish
    neighbours.storage.in_progress_retryable_after_409 = outcome == "retrying"
    first_outcome: list[str] = []
    original = threading.Thread(
        target=lambda: first_outcome.append(engine.process_item(first, "first")), daemon=True
    )
    original.start()
    try:
        wait_until(lambda: key in neighbours.storage.in_flight, 5)
        with psycopg.connect(db_dsn) as conn:
            conn.execute(
                "UPDATE items SET lease_expires_at = now() - interval '1 second' WHERE item_id = %s",
                (first["item_id"],),
            )
        reclaimed = engine.claim_item("second")
        assert reclaimed is not None and reclaimed["item_id"] == first["item_id"]
        assert reclaimed["delivery_key"] == key and reclaimed["attempts"] == 1
        second_outcome: list[str] = []
        replay = threading.Thread(
            target=lambda: second_outcome.append(engine.process_item(reclaimed, "second")), daemon=True
        )
        replay.start()
        wait_until(lambda: neighbours.storage.calls[key] >= 2, 5)
        if outcome == "retrying":
            replay.join(5)
            parked = next(
                row
                for row in items_by_stage(db_dsn, run_id)["store-raw"]
                if row["item_id"] == first["item_id"]
            )
            assert parked["status"] == "retrying" and parked["attempts"] == 1
            assert parked["error"]["code"] == "idempotency_in_progress"
            assert neighbours.storage.effects[key] == 0
            assert neighbours.storage.in_progress_rejections[key] >= 2
        else:
            original_can_finish.set()
            replay.join(5)
        assert not replay.is_alive()
        assert second_outcome == [outcome]
    finally:
        original_can_finish.set()
        original.join(5)
    assert not original.is_alive()
    assert first_outcome == ["lease_lost"]
    if outcome == "retrying":
        # The original call finishes after the bounded wait; a later claim must still
        # retrieve its result with the same key even though max_attempts is only 1.
        time.sleep(0.05)
        third = engine.claim_item("third")
        assert third is not None and third["item_id"] == first["item_id"]
        assert third["attempts"] == 1 and third["delivery_key"] == key
        assert engine.process_item(third, "third") == "success"
    rows = items_by_stage(db_dsn, run_id)["store-raw"]
    item = next(row for row in rows if row["item_id"] == first["item_id"])
    assert item["status"] == "completed" and item["attempts"] == 1
    assert neighbours.storage.calls[key] >= 2
    assert neighbours.storage.key_mismatch == []
    assert neighbours.storage.effects[key] == 1
    assert neighbours.storage.calls[key] >= 3  # original, 409, then replayed result
    assert neighbours.storage.duplicates[key] >= 1


def test_final_collector_page_is_acknowledged_before_feed_done(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    api = make_client(run_workers=False)
    engine = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert (
        post(
            api,
            "/v1/tasks",
            catalog_task(limits={"queue": {"max_inflight_materials": 6}}),
        ).status_code
        == 201
    )
    run_id = start(api, "shop-catalog")
    feed = engine.claim_feed("first")
    assert feed is not None
    engine.process_feed(feed, "first")
    collection = next(iter(neighbours.collector.collections.values()))
    assert not _feed_done(db_dsn, run_id)
    assert collection.acked == 0
    with psycopg.connect(db_dsn, row_factory=psycopg.rows.dict_row) as conn:
        row = conn.execute("SELECT * FROM runs WHERE run_id = %s", (run_id,)).fetchone()
    assert row is not None
    assert engine._capacity(row, {"queue.max_queue_depth": 10000, "queue.max_inflight_materials": 6}) == 0
    second = make_client(run_workers=False).app.state.engine
    feed = second.claim_feed("second")
    assert feed is not None
    second.process_feed(feed, "second")
    assert _feed_done(db_dsn, run_id)
    assert collection.acked == len(collection.materials)
    assert collection.pulls >= 2


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


def test_queue_start_timestamp_is_after_prior_run_finished_while_waiting_for_lock(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    """A queued transition may begin its transaction before the previous run finishes.

    The advisory lock still serializes the statuses; started_at must record the actual transition,
    not the earlier transaction start, or the run intervals falsely overlap.
    """
    api = make_client(run_workers=False)
    engine = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert (
        post(api, "/v1/tasks", catalog_task(schedule={"type": "manual", "overlap": "queue"})).status_code
        == 201
    )
    first, second = start(api, "shop-catalog"), start(api, "shop-catalog")
    with psycopg.connect(db_dsn) as conn:
        conn.execute(
            "UPDATE runs SET status = 'running', started_at = clock_timestamp(), feed_done = true"
            " WHERE run_id = %s",
            (first,),
        )
    claimed = engine.claim_feed("timestamp-test")
    assert claimed is not None and claimed["run_id"] == second

    errors: list[BaseException] = []

    def begin_next() -> None:
        try:
            engine.process_feed(claimed, "timestamp-test")
        except BaseException as exc:
            errors.append(exc)

    lock_key = "jane-run-start:shop-catalog"
    with psycopg.connect(db_dsn, autocommit=True) as gate:
        gate.execute("SELECT pg_advisory_lock(hashtext(%s))", (lock_key,))
        thread = threading.Thread(target=begin_next, daemon=True)
        thread.start()
        try:

            def blocked_on_advisory_lock() -> bool:
                with psycopg.connect(db_dsn) as observer:
                    row = observer.execute(
                        "SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid"
                        " WHERE a.datname = current_database() AND l.locktype = 'advisory' AND NOT l.granted"
                    ).fetchone()
                    return bool(row and row[0])

            wait_until(blocked_on_advisory_lock, 10)
            with psycopg.connect(db_dsn) as conn:
                row = conn.execute(
                    "UPDATE runs SET status = 'succeeded', finished_at = clock_timestamp()"
                    " WHERE run_id = %s RETURNING finished_at",
                    (first,),
                ).fetchone()
                assert row is not None
                first_finished = row[0]
        finally:
            gate.execute("SELECT pg_advisory_unlock(hashtext(%s))", (lock_key,))
            thread.join(30)

    assert not thread.is_alive()
    assert not errors, errors
    with psycopg.connect(db_dsn) as conn:
        row = conn.execute("SELECT started_at FROM runs WHERE run_id = %s", (second,)).fetchone()
    assert row is not None and row[0] is not None
    assert row[0] > first_finished


@pytest.mark.parametrize("ending", ["success", "failure"])
def test_run_finish_timestamp_is_after_row_lock_wait(
    make_client: Any, neighbours: Neighbours, db_dsn: str, ending: str
) -> None:
    """A finish transaction can wait for a row lock before its terminal status becomes visible."""
    api = make_client(run_workers=False)
    engine = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task()).status_code == 201
    run_id = start(api, "shop-catalog")
    with psycopg.connect(db_dsn) as conn:
        conn.execute(
            "UPDATE runs SET status = 'running', started_at = clock_timestamp(), feed_done = true"
            " WHERE run_id = %s",
            (run_id,),
        )

    errors: list[BaseException] = []

    def finish() -> None:
        try:
            if ending == "success":
                assert engine.runs.maybe_finish(run_id) == "succeeded"
            else:
                with engine.core.db.tx() as conn:
                    assert engine.runs.fail_run(conn, run_id, problem("test_failure", "forced failure"))
        except BaseException as exc:
            errors.append(exc)

    with psycopg.connect(db_dsn) as gate:
        gate.execute("SELECT run_id FROM runs WHERE run_id = %s FOR UPDATE", (run_id,))
        thread = threading.Thread(target=finish, daemon=True)
        thread.start()
        try:

            def blocked_on_row_lock() -> bool:
                with psycopg.connect(db_dsn) as observer:
                    row = observer.execute(
                        "SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid"
                        " WHERE a.datname = current_database() AND NOT l.granted"
                        " AND l.locktype IN ('transactionid', 'tuple')"
                    ).fetchone()
                    return bool(row and row[0])

            wait_until(blocked_on_row_lock, 10)
            row = gate.execute("SELECT clock_timestamp()").fetchone()
            assert row is not None
            marker = row[0]
        finally:
            gate.commit()
            thread.join(30)

    assert not thread.is_alive()
    assert not errors, errors
    with psycopg.connect(db_dsn) as conn:
        row = conn.execute("SELECT status, finished_at FROM runs WHERE run_id = %s", (run_id,)).fetchone()
    assert row is not None and row[0] == ("succeeded" if ending == "success" else "failed")
    assert row[1] > marker


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


def test_rate_limited_page_is_acknowledged_before_collection_restart(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    col = neighbours.collector
    col.rate_limit_after = 2
    col.retry_after_seconds = 1
    api = make_client(run_workers=False)
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task(retries={"max_attempts": 3})).status_code == 201
    run_id = start(api, "shop-catalog")
    first_engine = api.app.state.engine
    feed = first_engine.claim_feed("first")
    assert feed is not None
    first_engine.process_feed(feed, "first")
    old_collection = next(iter(col.collections.values()))
    assert len(items_by_stage(db_dsn, run_id)["collect"]) == 2
    assert old_collection.acked == 0 and old_collection.pulls == 1
    with psycopg.connect(db_dsn, row_factory=psycopg.rows.dict_row) as conn:
        row = conn.execute(
            "SELECT collection_id, feed_cursor, collection_restarts FROM runs WHERE run_id = %s",
            (run_id,),
        ).fetchone()
    assert row is not None
    assert row["collection_id"] == old_collection.cid
    assert row["feed_cursor"] is not None and row["collection_restarts"] == 0

    second_engine = make_client(run_workers=False).app.state.engine
    feed = second_engine.claim_feed("second")
    assert feed is not None
    second_engine.process_feed(feed, "second")
    assert old_collection.acked == 2 and old_collection.pulls >= 2
    with psycopg.connect(db_dsn, row_factory=psycopg.rows.dict_row) as conn:
        row = conn.execute(
            "SELECT collection_id, feed_cursor, collection_restarts FROM runs WHERE run_id = %s",
            (run_id,),
        ).fetchone()
    assert row is not None
    assert row["collection_id"] is None and row["feed_cursor"] is None
    assert row["collection_restarts"] == 1


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
    assert first.acked == 2 and first.pulls >= 2
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
