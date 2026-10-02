"""R-06: assistant replicas replay one onboarding request and share its job/session."""

from __future__ import annotations

import uuid

import pytest

from jane_e2e.assistant import assistant_flows
from jane_e2e.clients import JaneClient

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(8)]


def test_r_06_assistant_replay_and_session_are_shared_by_replicas() -> None:
    with assistant_flows("r06-assistant") as flows:
        flows.stack.scale("assistant", 2)
        first = JaneClient(flows.stack.url("assistant", 1))
        second = JaneClient(flows.stack.url("assistant", 2))
        try:
            headers = {"Idempotency-Key": uuid.uuid4().hex}
            body = {"query": "testsite"}
            started = first.api("assistant").post("/v1/onboarding-sessions", json=body, headers=headers)
            assert started.status_code == 202, started.text
            replayed = second.api("assistant").post("/v1/onboarding-sessions", json=body, headers=headers)
            assert replayed.status_code == 202, replayed.text
            assert replayed.headers["Idempotency-Replayed"] == "true"
            assert replayed.json() == started.json()

            changed = second.api("assistant").post(
                "/v1/onboarding-sessions", json={"query": "different-site"}, headers=headers
            )
            assert changed.status_code == 422, changed.text
            assert changed.json()["code"] == "idempotency_key_reused"

            job_id = started.json()["job_id"]
            job = second.wait_job("assistant", job_id, timeout_s=600)
            assert job["status"] == "succeeded", job
            session_id = started.json()["labels"]["session_id"]
            on_first = first.api("assistant").get(f"/v1/onboarding-sessions/{session_id}")
            on_second = second.api("assistant").get(f"/v1/onboarding-sessions/{session_id}")
            assert on_first.status_code == on_second.status_code == 200
            assert on_first.json() == on_second.json()
            assert on_second.json()["status"] == "needs_disambiguation"
        finally:
            first.close()
            second.close()
