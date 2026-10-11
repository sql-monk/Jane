"""A dedicated consumer isolates its tasks without changing shared leases or default FIFO."""

from __future__ import annotations

import json
from typing import Any

import psycopg
import pytest
from orch_support import Neighbours, catalog_task, items_by_stage, source_doc
from test_done_when import post, start

from jane_kit.config import LimitError
from jane_orchestrator.settings import Settings, resolve_service_limits


@pytest.mark.parametrize("raw", ['["ads-autoria", "ads-rst"]', "ads-autoria, ads-rst", "[]"])
def test_task_allowlist_from_environment(raw: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS", raw)
    resolved = resolve_service_limits(Settings())
    assert resolved.limits.engine.task_ids == ([] if raw == "[]" else ["ads-autoria", "ads-rst"])
    assert "task_ids" not in resolved.platform_limits()["defaults"]


@pytest.mark.parametrize("raw", ["", "ads-autoria,", '[" "]', '["ads-rst", 12]', "[invalid"])
def test_invalid_allowlist_cannot_silently_enable_all_tasks(
    raw: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS", raw)
    with pytest.raises((LimitError, ValueError)):
        resolve_service_limits(Settings())


def _collect_and_store(task_id: str, **extra: Any) -> dict[str, Any]:
    doc = catalog_task(task_id)
    return {**doc, "stages": doc["stages"][:2], **extra}


def _feed_items(engine: Any, db_dsn: str, run_id: str, worker: str) -> None:
    for _ in range(10):
        feed = engine.claim_feed(worker)
        if feed is not None:
            assert feed["run_id"] == run_id
            engine.process_feed(feed, worker)
        if items_by_stage(db_dsn, run_id).get("store-raw"):
            return
    pytest.fail("collector did not produce stage items")


@pytest.mark.integration
def test_targeted_claims_bypass_older_task_and_keep_leases_and_delivery_key(
    make_client: Any, db_dsn: str, neighbours: Neighbours, monkeypatch: pytest.MonkeyPatch
) -> None:
    general_api = make_client(run_workers=False)
    general = general_api.app.state.engine
    assert post(general_api, "/v1/sources", source_doc()).status_code == 201
    assert post(general_api, "/v1/tasks", _collect_and_store("other-catalog")).status_code == 201
    older = start(general_api, "other-catalog")
    _feed_items(general, db_dsn, older, "general-feed")

    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS", '["ads-autoria", "ads-rst"]')
    targeted = make_client(run_workers=False).app.state.engine
    assert targeted.claim_item("target") is None
    assert targeted.claim_feed("target") is None
    assert post(general_api, "/v1/tasks", _collect_and_store("ads-autoria")).status_code == 201
    selected = start(general_api, "ads-autoria")
    feed = targeted.claim_feed("target-feed")
    assert feed is not None and feed["run_id"] == selected
    assert targeted.claim_feed("second-target") is None  # live feed lease cannot be duplicated
    targeted.process_feed(feed, "target-feed")
    if not items_by_stage(db_dsn, selected).get("store-raw"):
        _feed_items(targeted, db_dsn, selected, "target-feed")

    item = targeted.claim_item("target")
    assert item is not None and item["run_id"] == selected
    older_item = general.claim_item("general")
    assert older_item is not None and older_item["run_id"] == older  # default FIFO

    with psycopg.connect(db_dsn) as conn:  # simulate a stopped worker in this isolated test DB
        conn.execute(
            "UPDATE items SET lease_expires_at = now() - interval '1 second' WHERE item_id = %s",
            (item["item_id"],),
        )
    reclaimed = targeted.claim_item("replacement")
    assert reclaimed is not None and reclaimed["item_id"] == item["item_id"]
    assert reclaimed["delivery_key"] == item["delivery_key"]
    assert reclaimed["attempts"] == item["attempts"]
    assert reclaimed["lease_reclaims"] == item["lease_reclaims"] + 1
    assert targeted.process_item(item, "target") == "lease_lost"
    assert targeted.process_item(reclaimed, "replacement") == "success"
    assert neighbours.storage.effects[item["delivery_key"]] == 1
    assert neighbours.storage.duplicates[item["delivery_key"]] == 1
    assert neighbours.storage.key_mismatch == []
    assert general.process_item(older_item, "general") == "success"

    # A general consumer can still claim the selected task from the same queue.
    while (next_item := general.claim_item("general")) is not None:
        if next_item["run_id"] == selected:
            break
        general.process_item(next_item, "general")
    assert next_item is not None and next_item["run_id"] == selected


@pytest.mark.integration
def test_targeted_scheduler_and_housekeeping_leave_other_tasks_for_general_worker(
    make_client: Any, db_dsn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = make_client(run_workers=False)
    general = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    schedule = {"type": "interval", "interval_seconds": 21600, "overlap": "queue"}
    for task_id in ("other-catalog", "ads-rst"):
        assert post(api, "/v1/tasks", _collect_and_store(task_id, schedule=schedule)).status_code == 201
    with psycopg.connect(db_dsn) as conn:
        conn.execute("UPDATE tasks SET next_run_at = now() - interval '1 second'")
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__TASK_IDS", json.dumps(["ads-rst"]))
    targeted = make_client(run_workers=False).app.state.engine
    assert targeted.schedule_due() == 1
    assert targeted.schedule_due() == 0
    assert general.schedule_due() == 1

    with psycopg.connect(db_dsn) as conn:
        conn.execute("UPDATE runs SET status = 'running', feed_done = true")
    assert targeted.reap() == 1
    with psycopg.connect(db_dsn) as conn:
        rows: dict[str, str] = dict(conn.execute("SELECT task_id, status FROM runs").fetchall())
    assert rows == {"other-catalog": "running", "ads-rst": "succeeded"}
    assert general.reap() == 1
