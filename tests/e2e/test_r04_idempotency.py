"""R-04: replay each collector and the LLM through their real Docker HTTP APIs."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import TESTSITE
from jane_e2e.stack import E2EStack
from jane_telegram_collector.recorded import Recording  # type: ignore[import-untyped]

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(8)]


def _collection_result(
    collector: JaneClient, collection_id: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    api = collector.api("collector")
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        view_response = api.get(f"/v1/collections/{collection_id}")
        assert view_response.status_code == 200, view_response.text
        view = view_response.json()
        if view["status"] in {"succeeded", "failed", "cancelled"}:
            assert view["status"] == "succeeded", view
            page_response = api.get(f"/v1/collections/{collection_id}/materials")
            assert page_response.status_code == 200, page_response.text
            page = page_response.json()
            assert page["end_of_stream"], page
            return view, page["items"]
        time.sleep(0.25)
    raise TimeoutError(f"collection {collection_id} did not finish")


@pytest.mark.parametrize("service", ["web-collector", "telegram-collector"])
@pytest.mark.parametrize("replay_location", ["same-instance", "other-instance", "after-restart"])
def test_r_04_collectors_replay_one_job_without_new_materials(
    stack: E2EStack,
    require: Callable[..., None],
    client: Callable[..., JaneClient],
    run_id: str,
    service: str,
    replay_location: str,
) -> None:
    if service == "web-collector":
        require("testsite", service)
        body: dict[str, Any] = {
            "source_kind": "web",
            "source_id": f"r04-web-{run_id}",
            "rules_ref": {"package_id": "testsite.web-rules", "version": "1.0.0"},
            "urls": [f"{TESTSITE}/product/phone-alpha"],
        }
    else:
        require(service)
        username = f"r04_tg_{run_id}"
        recording = Recording.create(
            stack.telegram_recordings_dir,
            channel_id="-1001234567890",
            username=username,
            title="R-04 events",
        )
        recording.post("R-04 event", date=datetime(2026, 9, 1, 10, 0, tzinfo=UTC))
        body = {
            "source_kind": "telegram",
            "source_id": f"r04-tg-{run_id}",
            "state_key": f"r04-tg-{run_id}",
            "rules": {"collector": "telegram", "channels": [{"username": username}]},
            "mode": "full",
            "limits": {"rate": {"min_delay_ms_per_host": 0}},
        }

    if replay_location == "other-instance":
        stack.scale(service, 2)
    replay_replica = 2 if replay_location == "other-instance" else 1
    collector = client(service, 1)
    replay_collector = client(service, replay_replica)
    api = collector.api("collector")
    replay_api = replay_collector.api("collector")
    headers = {"Idempotency-Key": f"r04-{service}-{run_id}"}
    first = api.post("/v1/collections", json=body, headers=headers)
    assert first.status_code == 202, first.text
    collection_id = first.json()["job_id"]
    view_before, materials_before = _collection_result(collector, collection_id)
    assert len(materials_before) == 1, materials_before

    if replay_location == "after-restart":
        stack.kill(service)
        stack.restart(service)
        replay_collector = client(service, 1)
        replay_api = replay_collector.api("collector")

    replay = replay_api.post("/v1/collections", json=body, headers=headers)
    assert replay.status_code == 202, replay.text
    assert replay.headers["Idempotency-Replayed"] == "true"
    assert replay.json() == first.json()
    assert replay.json()["job_id"] == collection_id

    changed = {**body, "mode": "incremental"}
    mismatch = replay_api.post("/v1/collections", json=changed, headers=headers)
    assert mismatch.status_code == 422, mismatch.text
    assert mismatch.json()["code"] == "idempotency_key_reused"

    view_after, materials_after = _collection_result(replay_collector, collection_id)
    assert view_after == view_before
    assert materials_after == materials_before


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("replay_location", ["same-instance", "other-instance", "after-restart"])
def test_r_04_llm_replay_does_not_spend_usage_twice(
    stack: E2EStack,
    require: Callable[..., None],
    client: Callable[..., JaneClient],
    run_id: str,
    mode: str,
    replay_location: str,
) -> None:
    require("llm")
    if replay_location == "other-instance":
        stack.scale("llm", 2)
    replay_replica = 2 if replay_location == "other-instance" else 1
    llm = client("llm", 1)
    replay_llm = client("llm", replay_replica)
    api = llm.api("llm")
    replay_api = replay_llm.api("llm")
    task_id = f"r04-{mode}-{run_id}"
    body = {
        "model": "default",
        "instructions": "Classify the page type.",
        "data": [{"name": "page", "media_type": "text/plain", "text": "R-04 product"}],
        "output_schema": {
            "type": "object",
            "required": ["page_type"],
            "properties": {"page_type": {"type": "string", "enum": ["product", "other"]}},
        },
        "scope": {"purpose": "other", "task_id": task_id},
        "mode": mode,
    }
    headers = {"Idempotency-Key": f"r04-llm-{mode}-{run_id}"}
    first = api.post("/v1/completions", json=body, headers=headers)
    assert first.status_code == (200 if mode == "sync" else 202), first.text
    if mode == "async":
        job_id = first.json()["job_id"]
        job = llm.wait_job("llm", job_id)
        assert job["status"] == "succeeded", job
        completion = job["result"]
    else:
        completion = first.json()
    assert completion["valid"] is True, completion
    completion_id = completion["completion_id"]

    def usage() -> dict[str, Any]:
        response = api.get("/v1/usage", params={"scope_type": "task", "scope_id": task_id})
        assert response.status_code == 200, response.text
        return dict(response.json())

    before = usage()
    assert before["totals"]["requests"] == 1, before
    if replay_location == "after-restart":
        stack.kill("llm")
        stack.restart("llm")
        llm = client("llm", 1)
        api = llm.api("llm")
        replay_llm = client("llm", 1)
        replay_api = replay_llm.api("llm")
    replay = replay_api.post("/v1/completions", json=body, headers=headers)
    assert replay.status_code == first.status_code, replay.text
    assert replay.headers["Idempotency-Replayed"] == "true"
    assert replay.json() == first.json()
    if mode == "async":
        assert replay.json()["job_id"] == job_id
        assert replay_llm.wait_job("llm", job_id)["result"]["completion_id"] == completion_id
    else:
        assert replay.json()["completion_id"] == completion_id

    mismatch = replay_api.post(
        "/v1/completions", json={**body, "instructions": "Summarize."}, headers=headers
    )
    assert mismatch.status_code == 422, mismatch.text
    assert mismatch.json()["code"] == "idempotency_key_reused"
    assert usage() == before
    assert replay_api.get("/v1/usage", params={"scope_type": "task", "scope_id": task_id}).json() == before
