"""Orchestrator-side steps (orchestrator.v1): connections, source, M1 task, runs, items, traces.

The M1 task of plan.md §6 is ``collect`` -> (``store-raw`` || ``extract-products`` -> ``store-products``):
RAW of every page into files, extraction by a local package (bound to product URLs) into PostgreSQL.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from jane_e2e.clients import JaneClient

__all__ = [
    "CONNECTIONS",
    "RULES_REF",
    "TESTSITE",
    "connections_synced",
    "create_source",
    "create_task",
    "list_items",
    "m1_task",
    "put_connections",
    "start_run",
    "wait_run",
]

TESTSITE = "http://testsite:8080"  # the test site as seen by the services inside the compose network
RULES_REF = {"package_id": "testsite.web-rules", "version": "1.0.0"}  # tests/e2e/config/rules (local)
TERMINAL = frozenset({"succeeded", "failed", "cancelled"})

# Same documents as tests/e2e/config/storage-connections.json: the orchestrator's registry is the source of
# truth for stages (ADR-0006) and pushes them to storage (PUT /v1/connections/{id}).
CONNECTIONS_FILE = Path(__file__).resolve().parents[1] / "config" / "storage-connections.json"
CONNECTIONS: list[dict[str, Any]] = json.loads(CONNECTIONS_FILE.read_text(encoding="utf-8"))["connections"]


def _key() -> str:
    return uuid.uuid4().hex


def put_connections(orch: JaneClient) -> None:
    for conn in CONNECTIONS:
        r = orch.api("orchestrator").put(f"/v1/connections/{conn['connection_id']}", json=conn)
        assert r.status_code in (200, 201), r.text


def connections_synced(orch: JaneClient, executor: str) -> bool | None:
    """True when no registered connection waits to be pushed to ``executor`` (``PlatformConnection``), else None.

    Every ``PUT /v1/connections/{id}`` (also with an unchanged document) makes the orchestrator push the
    connection to its executors again. R-03 waits for these pushes before partitioning storage so a pending
    connection delivery cannot occupy the worker needed to measure invocation retry backoff. Direct storage
    writes need no such wait: WP-19 fixed adapter lifetime during connection updates."""
    for conn in CONNECTIONS:
        r = orch.api("orchestrator").get(f"/v1/connections/{conn['connection_id']}")
        assert r.status_code == 200, r.text
        if any(
            e["executor"] == executor and e["sync_status"] == "pending" for e in r.json().get("executors", [])
        ):
            return None
    return True


def create_source(orch: JaneClient, source_id: str, **extra: Any) -> dict[str, Any]:
    body = {
        "source_id": source_id,
        "kind": "web",
        "title": f"e2e test site {source_id}",
        "locator": {"url": f"{TESTSITE}/"},
        "collector_rules": RULES_REF,
        **extra,
    }
    r = orch.api("orchestrator").post("/v1/sources", json=body, headers={"Idempotency-Key": _key()})
    assert r.status_code in (200, 201), r.text
    return dict(r.json())


def m1_task(
    task_id: str,
    source_id: str,
    urls: list[str],
    extractor: dict[str, Any],
    *,
    limits: dict[str, Any] | None = None,
    raw_package: str = "jane.storage-files",
    raw_connection: str = "raw-files",
    entities_package: str = "jane.storage-postgresql",
    entities_connection: str = "results-pg",
) -> dict[str, Any]:
    task: dict[str, Any] = {
        "task_id": task_id,
        "title": f"e2e M1 {task_id}",
        "input": {"source_id": source_id, "urls": urls},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}},
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": {"package_id": raw_package, "version": "1.0.0"},
                "connections": {"target": raw_connection},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "extract-products",
                "kind": "handler",
                "handler": extractor,
                "inputs": [
                    {
                        "from": "collect",
                        "when": {"field": "material.format.media_type", "op": "eq", "value": "text/html"},
                    }
                ],
                "bindings": [{"url_patterns": [{"value": "*/product/*"}]}],
            },
            {
                "stage_id": "store-products",
                "kind": "handler",
                "handler": {"package_id": entities_package, "version": "1.0.0"},
                "connections": {"target": entities_connection},
                "inputs": [
                    {
                        "from": "extract-products",
                        "select": "output",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
            },
        ],
    }
    if limits:
        task["limits"] = limits
    return task


def create_task(orch: JaneClient, task: dict[str, Any]) -> dict[str, Any]:
    r = orch.api("orchestrator").post("/v1/tasks", json=task, headers={"Idempotency-Key": _key()})
    assert r.status_code in (200, 201), r.text
    return dict(r.json())


def start_run(
    orch: JaneClient, task_id: str, key: str | None = None, body: dict[str, Any] | None = None
) -> str:
    r = orch.api("orchestrator").post(
        f"/v1/tasks/{task_id}/runs",
        json=body or {"reason": "e2e"},
        headers={"Idempotency-Key": key or _key()},
    )
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def wait_run(orch: JaneClient, run_id: str, timeout_s: float = 600.0, poll_s: float = 1.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    while True:
        run: dict[str, Any] = orch.api("orchestrator").get(f"/v1/runs/{run_id}").json()
        if run["status"] in TERMINAL:
            return run
        if time.monotonic() > deadline:
            raise TimeoutError(f"run {run_id} still {run['status']} after {timeout_s}s: {run.get('stages')}")
        time.sleep(poll_s)


def list_items(orch: JaneClient, run_id: str, stage_id: str | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        params: dict[str, Any] = {"limit": 500}
        if stage_id:
            params["stage_id"] = stage_id
        if cursor:
            params["cursor"] = cursor
        page = orch.api("orchestrator").get(f"/v1/runs/{run_id}/items", params=params).json()
        items.extend(page["items"])
        cursor = page.get("next_cursor")
        if not cursor:
            return items
