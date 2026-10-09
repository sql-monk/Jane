"""R17: jobs on jane-kit's shared SQLite store - a collection cancelled while its job waits for a runner slot."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_telegram_collector.app import build_app
from jane_telegram_collector.testing import (
    USERNAME,
    Recording,
    make_settings,
    start,
    telegram_rules,
    wait_done,
)


def test_collection_cancelled_before_its_run_started(
    tmp_path: Path, channel: Recording, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With one runner slot taken, the second collection is still ``queued`` when it is cancelled: the job and the
    collection end ``cancelled`` (before R17 the job stayed ``cancelling`` until the instance restarted)."""
    monkeypatch.setenv("JANE_TELEGRAM_COLLECTOR_LIMITS__JOBS__MAX_CONCURRENT_JOBS", "1")
    with TestClient(build_app(make_settings(tmp_path))) as client:
        busy = {"queue": {"max_unacked_materials": 3}}  # pauses on backpressure, keeps the only slot
        first = start(client, {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "limits": busy})
        deadline = time.monotonic() + 30
        while client.get(f"/v1/collections/{first}").json()["status"] != "running":
            assert time.monotonic() < deadline
            time.sleep(0.05)
        second = start(
            client,
            {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": "other-state"},
        )
        assert client.get(f"/v1/collections/{second}").json()["status"] == "queued"
        assert client.post(f"/v1/jobs/{second}/cancel", json={"reason": "test"}).status_code == 202
        view = wait_done(client, second, timeout=20)
        job = client.get(f"/v1/jobs/{second}").json()
        assert view["status"] == job["status"] == "cancelled", (view, job)
        assert job["cancellation"]["reason"] == "test"
        assert client.post(f"/v1/jobs/{first}/cancel").status_code == 202
        assert wait_done(client, first, timeout=20)["status"] == "cancelled"
