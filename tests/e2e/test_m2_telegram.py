"""S-M2-02: the real Telegram Collector against its recorded Telegram backend (external substitute)."""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.stack import E2EStack
from jane_e2e.steps import store
from jane_e2e.verify import objects_by_source
from jane_telegram_collector.recorded import Recording  # type: ignore[import-untyped]

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]


def _start(collector: JaneClient, body: dict[str, Any]) -> str:
    r = collector.api("collector").post(
        "/v1/collections", json=body, headers={"Idempotency-Key": uuid.uuid4().hex}
    )
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def _drain(collector: JaneClient, cid: str, timeout_s: float = 120) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        params: dict[str, Any] = {"wait_ms": 2000, **({"after": after} if after else {})}
        r = collector.api("collector").get(f"/v1/collections/{cid}/materials", params=params)
        assert r.status_code == 200, r.text
        page = r.json()
        out.extend(page["items"])
        after = page.get("next_cursor") or after
        if page["end_of_stream"]:
            return out
    raise TimeoutError(f"Telegram collection {cid} did not finish in {timeout_s}s")


@pytest.mark.criteria(1, 8, 12)
def test_s_m2_02_telegram_history_new_and_edit_to_raw_json(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """History, new message and edit are distinct observations; technical redelivery is not.

    Storage persists every observation as a JSON RAW object. Only the Telegram network is substituted
    by a recording; the HTTP collector and storage services are real.
    """
    require("telegram-collector", "storage")
    collector, storage = client("telegram-collector"), client("storage")
    username = f"city_events_{run_id}"
    rec = Recording.create(
        stack.telegram_recordings_dir, channel_id="-1001234567890", username=username, title="City events"
    )
    t0 = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    rec.post("Event 1: concert at 19:00", date=t0)
    rec.post("Event 2: exhibition", date=t0 + timedelta(minutes=1))

    source_id, state_key = f"e2e-tg-{run_id}", f"e2e-tg-{run_id}"
    rules = {"collector": "telegram", "channels": [{"username": username}]}
    base = {
        "source_kind": "telegram",
        "source_id": source_id,
        "state_key": state_key,
        "rules": rules,
        "limits": {"rate": {"min_delay_ms_per_host": 0}},
    }
    first_id = _start(collector, {**base, "mode": "full"})
    first_page = (
        collector.api("collector")
        .get(f"/v1/collections/{first_id}/materials", params={"wait_ms": 5000})
        .json()
    )
    assert first_page["items"], first_page
    redelivered = (
        collector.api("collector")
        .get(f"/v1/collections/{first_id}/materials", params={"wait_ms": 100})
        .json()
    )
    assert [m["observation_id"] for m in redelivered["items"]] == [
        m["observation_id"] for m in first_page["items"]
    ]
    history = _drain(collector, first_id)
    assert [m["locator"]["telegram"]["message_id"] for m in history] == [1, 2]

    rec.post("Event 3: lecture", date=t0 + timedelta(hours=1))
    rec.edit(1, "Event 1: moved to 20:00", edit_date=t0 + timedelta(days=1))
    changes = _drain(collector, _start(collector, {**base, "mode": "incremental"}))
    assert len(changes) == 2, changes
    original = history[0]
    edited = next(m for m in changes if m["locator"]["telegram"]["message_id"] == 1)
    assert edited["material_id"] == original["material_id"]
    assert edited["observation_id"] != original["observation_id"]
    assert edited["revision"]["is_edit"] is True
    assert edited["revision"]["sequence"] > original["revision"]["sequence"]
    assert next(m for m in changes if m["locator"]["telegram"]["message_id"] == 3)

    for material in [*history, *changes]:
        body, result = store(
            storage,
            package_id="jane.storage-files",
            connection="raw-files",
            inputs=[{"kind": "material", "material": material}],
            run_id=run_id,
            stage_id="store-telegram-raw",
            key_part=material["observation_id"],
        )
        assert result["status"] == "success", result
        _, duplicate = storage.invoke(body)
        assert duplicate["output"]["writes"][0]["status"] == "duplicate", duplicate

    objects = objects_by_source(storage, "raw-files", source_id)
    assert len(objects) == 4, objects
    assert len({o["material"]["observation_id"] for o in objects}) == 4
    for obj in objects:
        assert obj["object"]["locator"]["path"].endswith(".json"), obj
        r = storage.api("storage").get(
            f"/v1/objects/{obj['object']['object_id']}/content", params={"connection_id": "raw-files"}
        )
        assert r.status_code == 200, r.text
        stored = json.loads(r.content)
        assert stored["source"]["kind"] == "telegram"
        assert stored["observation_id"] == obj["material"]["observation_id"]
