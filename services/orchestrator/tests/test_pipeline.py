"""End-to-end runs through the real orchestrator (PostgreSQL queue, worker threads) against contract fakes."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from orch_support import Neighbours, catalog_task, items_by_stage, source_doc, wait_until

pytestmark = pytest.mark.integration

IDEM = 0


def post(client: TestClient, url: str, body: Any = None) -> Any:
    global IDEM
    IDEM += 1
    return client.post(url, json=body, headers={"Idempotency-Key": f"k-{IDEM}-{url}"})


def setup_catalog(client: TestClient, **task_extra: Any) -> None:
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    r = post(client, "/v1/tasks", catalog_task(**task_extra))
    assert r.status_code == 201, r.text


def run_and_wait(
    client: TestClient, task_id: str = "shop-catalog", body: Any = None, timeout: float = 30
) -> dict[str, Any]:
    r = post(client, f"/v1/tasks/{task_id}/runs", body or {})
    assert r.status_code == 202, r.text
    run_id = r.json()["job_id"]
    return wait_until(
        lambda: (
            (run := client.get(f"/v1/runs/{run_id}").json())["status"] in {"succeeded", "failed", "cancelled"}
            and run
        ),
        timeout,
    )


def test_m1_chain_web_to_raw_and_extraction_to_results(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client()
    setup_catalog(client)
    run = run_and_wait(client)
    assert run["status"] == "succeeded", run
    items = items_by_stage(db_dsn, run["run_id"])
    assert len(items["collect"]) == 6  # 5 products + 1 unknown page
    assert len(items["store-raw"]) == 6  # RAW of every material → files
    assert len(items["extract-products"]) == 5  # binding: section products only
    assert len(items["store-products"]) == 5  # success → PostgreSQL results
    assert "unknown-pages" not in items  # flag off: not forwarded to LLM
    assert all(i["status"] == "completed" for s in items.values() for i in s)
    # passing by reference: the material with its ContentRef reached the handlers unchanged
    req = next(b for m, p, b in neighbours.runtime.requests if p == "/v1/invocations")
    assert req["inputs"][0]["material"]["content"]["kind"] == "inline"
    assert req["delivery"]["delivery_key"] and req["context"]["trace"]["run_id"] == run["run_id"]
    # every delivery_key executed exactly once
    for fake in (neighbours.runtime, neighbours.storage):
        assert fake.effects and set(fake.effects.values()) == {1}
        assert not fake.key_mismatch
    assert neighbours.all_violations() == []
    assert neighbours.llm.effects == {}
