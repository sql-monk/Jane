"""Optional per-run fairness using the real claim engine and isolated PostgreSQL."""

from __future__ import annotations

import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any, cast

import psycopg
import pytest
from orch_support import Neighbours, Page, catalog_task, source_doc
from psycopg.types.json import Jsonb
from test_done_when import post, start

from jane_orchestrator.settings import EngineLimits, Settings, resolve_service_limits


def test_item_ordering_defaults_to_fifo_and_is_configurable(monkeypatch: pytest.MonkeyPatch) -> None:
    assert EngineLimits().item_queue_ordering == "fifo"
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING", "run_round_robin")
    assert resolve_service_limits(Settings()).limits.engine.item_queue_ordering == "run_round_robin"
    with pytest.raises(ValueError, match="item_queue_ordering"):
        EngineLimits.model_validate({"item_queue_ordering": "newest_first"})


def seed_runs(
    make_client: Any,
    neighbours: Neighbours,
    db_dsn: str,
    *,
    old_count: int = 64,
    new_count: int = 4,
    parallel_limit: int = 1,
) -> tuple[Any, Any, str, str]:
    """Valid API-created runs; queue data exists only in the fixture's disposable database."""
    api = make_client(run_workers=False, scheduler_enabled=False)
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    run_ids = []
    with psycopg.connect(db_dsn) as conn:
        for label, count in (("old", old_count), ("new", new_count)):
            task_id = f"queue-{label}"
            assert post(api, "/v1/tasks", catalog_task(task_id=task_id)).status_code == 201
            run_id = start(api, task_id)
            run_ids.append(run_id)
            conn.execute(
                "UPDATE runs SET status = 'running', feed_done = true,"
                " started_at = now(), updated_at = now() - %s::interval WHERE run_id = %s",
                ("1 hour" if label == "old" else "0 seconds", run_id),
            )
            material = neighbours.collector.material(
                f"queue-{label}",
                0,
                Page("https://shop.example.test/product/a-0", "<html>Product</html>"),
                "shop-example",
            )
            payload = Jsonb([{"kind": "material", "material": material}])
            conn.cursor().executemany(
                "INSERT INTO items(item_id, run_id, task_id, stage_id, item_key, status, payload,"
                " delivery_key, max_attempts, parallel_limit)"
                " VALUES (%s,%s,%s,'store-raw',%s,'queued',%s,%s,3,%s)",
                [
                    (
                        f"queue-{label}-{number}",
                        run_id,
                        task_id,
                        str(number),
                        payload,
                        f"queue-delivery-{label}-{number}",
                        parallel_limit,
                    )
                    for number in range(count)
                ],
            )
    return api, api.app.state.engine, run_ids[0], run_ids[1]


@pytest.mark.integration
@pytest.mark.parametrize("ordering", ["fifo", "run_round_robin"])
def test_old_backlog_and_new_run_both_progress_with_fair_ordering(
    make_client: Any,
    neighbours: Neighbours,
    db_dsn: str,
    monkeypatch: pytest.MonkeyPatch,
    ordering: str,
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING", ordering)
    _, engine, old_run, new_run = seed_runs(make_client, neighbours, db_dsn, old_count=1597)
    claimed = []
    for number in range(4):
        worker = f"progress-{number}"
        item = engine.claim_item(worker)
        assert item is not None
        claimed.append(item["run_id"])
        assert engine.process_item(item, worker) == "success"
    expected = [old_run] * 4 if ordering == "fifo" else [old_run, new_run, old_run, new_run]
    assert claimed == expected
    with psycopg.connect(db_dsn) as conn:
        completed = Counter(
            row[0] for row in conn.execute("SELECT run_id FROM items WHERE status='completed'").fetchall()
        )
    assert completed == Counter(expected)
    assert not neighbours.storage.violations


@pytest.mark.integration
@pytest.mark.parametrize("ordering", ["fifo", "run_round_robin"])
def test_task_allowlist_restricts_fair_run_selection_and_item_claims(
    make_client: Any,
    neighbours: Neighbours,
    db_dsn: str,
    monkeypatch: pytest.MonkeyPatch,
    ordering: str,
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING", ordering)
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS", '["queue-new"]')
    _, engine, old_run, new_run = seed_runs(make_client, neighbours, db_dsn)
    for number in range(4):
        worker = f"allowlisted-{number}"
        item = engine.claim_item(worker)
        # The older forbidden run must not shadow an eligible allowlisted run,
        # including during the first (run-selection) phase of a fair claim.
        assert item is not None and item["run_id"] == new_run
        assert engine.process_item(item, worker) == "success"
    assert engine.claim_item("allowed-drained") is None
    with psycopg.connect(db_dsn) as conn:
        touched = conn.execute(
            "SELECT count(*) FROM items WHERE run_id=%s AND attempts > 0", (old_run,)
        ).fetchone()
        assert touched is not None and touched[0] == 0


@pytest.mark.integration
@pytest.mark.parametrize("parallel_limit", [1, 2])
def test_concurrent_fair_claims_respect_parallel_stage_limit(
    make_client: Any,
    neighbours: Neighbours,
    db_dsn: str,
    monkeypatch: pytest.MonkeyPatch,
    parallel_limit: int,
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING", "run_round_robin")
    _, engine, old_run, _ = seed_runs(
        make_client, neighbours, db_dsn, old_count=64, new_count=0, parallel_limit=parallel_limit
    )
    with ThreadPoolExecutor(max_workers=8) as pool:
        for turn in range(6):
            barrier = threading.Barrier(8)

            def claim(
                number: int, barrier: threading.Barrier = barrier, turn: int = turn
            ) -> dict[str, Any] | None:
                barrier.wait(timeout=5)
                return cast(dict[str, Any] | None, engine.claim_item(f"parallel-{turn}-{number}"))

            items = [item for item in pool.map(claim, range(8)) if item is not None]
            assert 1 <= len(items) <= parallel_limit
            assert len({item["item_id"] for item in items}) == len(items)
            # A busy run lock can make concurrent callers skip it; once claims finish,
            # the configured spare execution capacity remains usable.
            while len(items) < parallel_limit:
                item = engine.claim_item(f"fill-{turn}-{len(items)}")
                assert item is not None
                items.append(item)
            assert engine.claim_item("over-cap") is None
            with psycopg.connect(db_dsn) as conn:
                running = conn.execute(
                    "SELECT count(*) FROM items WHERE run_id=%s AND status='running'", (old_run,)
                ).fetchone()
                assert running is not None and running[0] == parallel_limit
                conn.execute(
                    "UPDATE items SET status='completed' WHERE run_id=%s AND status='running'", (old_run,)
                )


@pytest.mark.integration
def test_fair_ordering_preserves_delayed_retry_and_expired_lease_semantics(
    make_client: Any, neighbours: Neighbours, db_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING", "run_round_robin")
    _, engine, old_run, _ = seed_runs(make_client, neighbours, db_dsn, old_count=1, new_count=0)
    with psycopg.connect(db_dsn) as conn:
        conn.execute(
            "UPDATE items SET status='retrying', attempts=1, error=%s, available_at=now()+interval '1 hour'"
            " WHERE run_id=%s",
            (Jsonb({"code": "idempotency_in_progress"}), old_run),
        )
    assert engine.claim_item("not-due") is None
    with psycopg.connect(db_dsn) as conn:
        conn.execute("UPDATE items SET available_at=now()-interval '1 second' WHERE run_id=%s", (old_run,))
    item = engine.claim_item("replay")
    assert item is not None and item["attempts"] == 1
    assert engine.claim_item("active-lease") is None
    with psycopg.connect(db_dsn) as conn:
        conn.execute(
            "UPDATE items SET lease_expires_at=now()-interval '1 second' WHERE run_id=%s", (old_run,)
        )
    reclaimed = engine.claim_item("reclaimed")
    assert reclaimed is not None and reclaimed["item_id"] == item["item_id"]
    assert reclaimed["delivery_key"] == item["delivery_key"]
    assert reclaimed["attempts"] == 1 and reclaimed["lease_reclaims"] == 1
    assert not engine._extend_item(item["item_id"], "replay")
    with psycopg.connect(db_dsn) as conn:
        conn.execute(
            "UPDATE items SET status='retrying', error=%s, lease_owner=NULL, lease_expires_at=NULL WHERE run_id=%s",
            (Jsonb({"code": "connection_error"}), old_run),
        )
    retry = engine.claim_item("ordinary-retry")
    assert retry is not None and retry["attempts"] == 2
    assert retry["delivery_key"] == item["delivery_key"]


@pytest.mark.integration
def test_fair_claim_skips_cancellation_run_lock_and_respects_cancelled_status(
    make_client: Any, neighbours: Neighbours, db_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING", "run_round_robin")
    _, engine, old_run, new_run = seed_runs(make_client, neighbours, db_dsn)
    with ThreadPoolExecutor(max_workers=1) as pool, psycopg.connect(db_dsn) as conn:
        conn.execute("SELECT run_id FROM runs WHERE run_id=%s FOR UPDATE", (old_run,))
        try:
            item = pool.submit(engine.claim_item, "skip-canceller").result(timeout=3)
            assert item is not None and item["run_id"] == new_run
            conn.execute("UPDATE runs SET status='cancelling' WHERE run_id=%s", (old_run,))
            conn.commit()
        finally:
            conn.rollback()
    # New run's only stage is at its cap; the old run cannot be claimed after cancellation.
    assert engine.claim_item("after-cancel") is None
