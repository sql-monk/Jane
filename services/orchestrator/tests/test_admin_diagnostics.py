"""WP-30: exact business outputs beyond trace caps, safe audit and sync diagnostics."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import psycopg
import pytest
from orch_support import Neighbours, base_result, catalog_task, product_extractor, wait_until

from jane_orchestrator.common import rfc3339
from jane_orchestrator.runs import canonical_scope
from jane_orchestrator.service import audit_changes

from .test_features import setup, start, wait_run


def test_canonical_scope_supports_pipes_inside_the_real_scope() -> None:
    assert canonical_scope('real|business|{"sku":"a|b"}') == "real|business"
    assert canonical_scope("incomplete-key") is None


def test_audit_changes_show_only_changed_values_and_redact_secrets() -> None:
    before = {"title": "Before", "unchanged": 1, "params": {"password": "old", "dsn": "old dsn"}}
    after = {
        "title": "After",
        "unchanged": 1,
        "params": {"password": "new", "dsn": "new dsn"},
        "url": "https://user:password@example.test/path",
        "request": "https://example.test/path?token=secret&search=public",
    }
    changes = audit_changes(before, after)
    assert changes["changed"] == ["params", "request", "title", "url"]
    assert changes["before"]["title"] == "Before" and changes["after"]["title"] == "After"
    assert "unchanged" not in changes["before"]
    assert changes["after"]["params"] == {"password": "[redacted]", "dsn": "[redacted]"}
    assert changes["after"]["url"] == "https://[redacted]@example.test/path"
    assert changes["after"]["request"] == "https://example.test/path?token=[redacted]&search=public"


@pytest.mark.integration
@pytest.mark.parametrize("test_mode", [False, True])
def test_summary_counts_unique_entities_beyond_trace_cap(
    make_client: Any, neighbours: Neighbours, monkeypatch: pytest.MonkeyPatch, db_dsn: str, test_mode: bool
) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__TRACE_OUTPUTS_MAX", "1")

    def extract(body: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        result = product_extractor(body, state)
        if not result.get("output"):
            return result
        entity = result["output"]["entities"][0]
        entities = []
        for number in range(3):
            copy = deepcopy(entity)
            copy["key"]["natural"] = {"sku": f"shared-{number}"}
            entities.append(copy)
        result["output"]["entities"] = [*entities, deepcopy(entities[0])]
        return result

    neighbours.runtime.behaviors["shop-example.product-extractor"] = extract
    client = make_client()
    setup(client)
    run = wait_run(client, start(client, body={"test_mode": test_mode}))
    assert run["status"] == "succeeded", run
    assert run["counters"]["materials"] == 6
    assert run["summary"]["complete"] is True
    assert run["summary"]["extracted_entities"] == 3
    assert run["summary"]["saved_records"] == (0 if test_mode else 3)
    groups = run["summary"]["result_groups"]
    assert groups == (
        []
        if test_mode
        else [{"connection_id": "results-pg", "entity_type": "product", "scope": "shop-example", "count": 3}]
    )
    if not test_mode:
        with psycopg.connect(db_dsn) as conn:
            conn.execute("UPDATE items SET outputs_complete = NULL WHERE run_id = %s", (run["run_id"],))
            conn.execute("DELETE FROM run_output_identities WHERE run_id = %s", (run["run_id"],))
        legacy = client.get(f"/v1/runs/{run['run_id']}").json()["summary"]
        assert legacy["complete"] is False
        assert legacy["legacy_trace"] is True
        assert "extracted_entities" not in legacy and "saved_records" not in legacy


@pytest.mark.integration
def test_audit_date_filters_and_real_configuration_differences(make_client: Any) -> None:
    client = make_client()
    setup(client)
    source = client.get("/v1/sources/shop-example")
    doc = {**source.json(), "title": "Updated title"}
    response = client.put("/v1/sources/shop-example", json=doc, headers={"If-Match": source.headers["etag"]})
    assert response.status_code == 200
    events = client.get("/v1/audit-events", params={"subject_type": "source"}).json()["items"]
    update = next(event for event in events if event["action"] == "source.update")
    assert update["details"]["changed"] == ["title"]
    assert update["details"]["after"] == {"title": "Updated title"}
    assert client.get("/v1/audit-events", params={"since": update["at"]}).json()["items"]
    older = client.get("/v1/audit-events", params={"until": update["at"]}).json()["items"]
    assert all(event["event_id"] != update["event_id"] for event in older)
    assert client.get("/v1/audit-events", params={"since": "2099-01-01T00:00:00Z"}).json()["items"] == []
    assert client.get("/v1/audit-events", params={"since": "2026-01-01T00:00:00"}).status_code == 400


@pytest.mark.integration
def test_problem_group_audit_redacts_whole_event_and_keeps_safe_changes(
    make_client: Any, neighbours: Neighbours
) -> None:
    def unrecognized(body: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
        result = base_result(body, "unrecognized", "extractor")
        result["unrecognized"] = {"partial": False, "signature": "missing-selector:.price"}
        return result

    neighbours.runtime.behaviors["shop-example.product-extractor"] = unrecognized
    client = make_client()
    setup(client)
    wait_run(client, start(client))
    group = client.get("/v1/problem-groups").json()["items"][0]
    url = f"/v1/problem-groups/{group['group_id']}"
    fake_secret = "audit-regression-fake-value"
    notes = ("awaits approval", f"Bearer {fake_secret}", "review completed")
    for note in notes:
        response = client.patch(
            url,
            json={"note": note, "status": "in_progress"},
            headers={"Content-Type": "application/merge-patch+json"},
        )
        assert response.status_code == 200
        assert response.json()["note"] == note and response.json()["status"] == "in_progress"

    audit = client.get(
        "/v1/audit-events", params={"subject_type": "problem_group", "subject_id": group["group_id"]}
    )
    assert audit.status_code == 200
    assert fake_secret not in audit.text  # Includes every event and its duplicated/top-level fields.
    events = [event for event in audit.json()["items"] if event["action"] == "problem_group.update"]
    assert len(events) == 3
    final, secret, initial = (event["details"] for event in events)
    assert initial["after"] == {"note": "awaits approval", "status": "in_progress"}
    assert secret["before"] == {"note": "awaits approval"}
    assert secret["after"] == {"note": "[redacted]"}
    assert final["before"] == {"note": "[redacted]"}
    assert final["after"] == {"note": "review completed"}
    assert all("note" not in event["details"] for event in events)


@pytest.mark.integration
def test_connection_unsupported_is_distinct_from_failed_sync(
    make_client: Any, neighbours: Neighbours
) -> None:
    neighbours.runtime.connections_unsupported = 501
    neighbours.storage.connections_unsupported = 404
    client = make_client()
    response = client.put(
        "/v1/connections/results-pg",
        json={"connection_id": "results-pg", "kind": "postgresql", "params": {"host": "postgres"}},
    )
    assert response.status_code == 200
    view = wait_until(
        lambda: (
            (v := client.get("/v1/connections/results-pg").json())
            and any(e["sync_status"] == "failed" for e in v["executors"])
            and v["unsupported_executors"]
            and v
        )
    )
    assert view["unsupported_executors"] == [
        {"executor": "handler-runtime", "reason": "managed_connections_not_supported"}
    ]
    failed = next(executor for executor in view["executors"] if executor["executor"] == "storage")
    assert failed["error"]["code"] == "not_found" and failed["error"]["status"] == 404
    assert failed["attempts"] == 1 and failed["error"]["retryable"] is False
    updated = client.put(
        "/v1/connections/results-pg",
        json={"connection_id": "results-pg", "kind": "postgresql", "params": {"host": "postgres"}},
        headers={"If-Match": response.headers["etag"]},
    )
    assert updated.status_code == 200 and updated.json()["unsupported_executors"] == []


@pytest.mark.integration
def test_failed_handler_retains_failure_kind_trace_and_exact_group_filter(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    def fail(body: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        result = base_result(body, "failed", "extractor")
        result["failure"] = {
            "kind": "schema_mismatch",
            "message": "Output did not match package schema",
            "retryable": False,
        }
        return result

    neighbours.runtime.behaviors["shop-example.product-extractor"] = fail
    task = catalog_task()
    next(stage for stage in task["stages"] if stage["stage_id"] == "extract-products")["on_failure"] = (
        "fail_run"
    )
    client = make_client()
    setup(client, task=task)
    run = wait_run(client, start(client))
    assert run["status"] == "failed" and run["error"]["code"] == "schema_mismatch"
    assert run["collector_kind"] == "web"
    assert run["error"]["details"] == {"stage_id": "extract-products", "failure_kind": "schema_mismatch"}
    assert len(run["error"]["trace_id"]) == 32
    # A handler can advance after the run row's most recent collector update.
    with psycopg.connect(db_dsn) as conn:
        conn.execute("UPDATE runs SET updated_at = created_at WHERE run_id = %s", (run["run_id"],))
        latest = conn.execute(
            "SELECT max(updated_at) FROM items WHERE run_id = %s", (run["run_id"],)
        ).fetchone()[0]
    refreshed = client.get(f"/v1/runs/{run['run_id']}").json()
    assert refreshed["updated_at"] == rfc3339(latest)
    groups = client.get("/v1/problem-groups").json()["items"]
    assert groups
    group_id = groups[0]["group_id"]
    exact = client.get("/v1/problem-groups", params={"group_id": group_id}).json()
    assert [group["group_id"] for group in exact["items"]] == [group_id] and exact["next_cursor"] is None
    assert client.get("/v1/problem-groups", params={"group_id": "missing-group"}).json()["items"] == []
