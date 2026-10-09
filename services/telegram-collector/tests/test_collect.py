"""Collections on the real collector app against recorded channels: history, new messages, edits, cursors.

Every test drives the real service through its HTTP API (FastAPI TestClient); only Telegram is replaced
by a recording.
"""

from __future__ import annotations

import time
from datetime import timedelta
from typing import Any

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from jane_telegram_collector.testing import (
    CHANNEL_ID,
    T0,
    USERNAME,
    Recording,
    drain,
    page,
    start,
    telegram_rules,
    wait_done,
)


def collect(
    client: TestClient, mode: str = "full", **extra: object
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    body: dict[str, Any] = {
        "source_kind": "telegram",
        "source_id": "news-tg",
        "rules": telegram_rules(USERNAME),
        "mode": mode,
        "state_key": "news-tg",
        **extra,
    }
    cid = start(client, body)
    items = drain(client, cid)
    return wait_done(client, cid), items


def test_history_is_collected_as_valid_materials(
    client: TestClient, channel: Recording, material_validator: Draft202012Validator
) -> None:
    view, items = collect(client)
    assert view["status"] == "succeeded"
    assert [m["locator"]["telegram"]["message_id"] for m in items] == list(range(1, 26))
    for m in items:
        errors = sorted(material_validator.iter_errors(m), key=str)
        assert not errors, errors[0].message
    first = items[0]
    assert first["material_id"] == f"tg:{CHANNEL_ID}:1"
    assert first["source"] == {"kind": "telegram", "source_id": "news-tg", "name": "City events"}
    assert first["locator"]["url"] == f"https://t.me/{USERNAME}/1"
    assert first["published_at"] == "2026-09-01T10:00:00Z"
    assert first["content"]["kind"] == "inline"
    assert first["content"]["data"] == "Event 1: concert at 19:00"
    assert first["revision"] == {
        "content_sha256": first["content"]["sha256"],
        "source_revision": str(int(T0.timestamp())),
        "sequence": int(T0.timestamp()) * 1000,  # epoch seconds x 1000 + revision within the second
        "is_edit": False,
    }
    assert first["discovery"] == {"strategy": "telegram_history"}
    assert first["metadata"] == {"views": 0}
    assert len({m["observation_id"] for m in items}) == 25
    stats = view["stats"]
    assert stats["emitted"] == 25 and stats["acknowledged"] == 25 and stats["unacked"] == 0
    assert stats["by_strategy"] == {"telegram_history": 25}
    state = client.get("/v1/states/news-tg").json()
    assert state["collector"] == "telegram"
    assert state["cursors"][CHANNEL_ID]["last_message_id"] == 25
    assert state["cursors"][CHANNEL_ID]["pts"] == 25


def test_history_since_and_from_message_id(client: TestClient, channel: Recording) -> None:
    rules = telegram_rules(
        USERNAME, history={"since": (T0 + timedelta(minutes=20)).isoformat().replace("+00:00", "Z")}
    )
    _, items = collect(client, rules=rules)
    assert [m["locator"]["telegram"]["message_id"] for m in items] == [21, 22, 23, 24, 25]
    rules = telegram_rules(USERNAME, history={"from_message_id": 23})
    _, items = collect(client, rules=rules, state_key="other")
    assert [m["locator"]["telegram"]["message_id"] for m in items] == [23, 24, 25]


def test_incremental_collects_only_new_messages(client: TestClient, channel: Recording) -> None:
    collect(client)
    for i in range(3):
        channel.post(f"New {i}", date=T0 + timedelta(hours=1, minutes=i))
    view, items = collect(client, mode="incremental")
    assert [m["locator"]["telegram"]["message_id"] for m in items] == [26, 27, 28]
    assert {m["discovery"]["strategy"] for m in items} == {"telegram_updates"}
    assert view["stats"]["by_strategy"] == {"telegram_updates": 3}
    view, items = collect(client, mode="incremental")
    assert items == [] and view["status"] == "succeeded"


def test_first_incremental_without_cursor_reads_history(client: TestClient, channel: Recording) -> None:
    view, items = collect(client, mode="incremental")
    assert len(items) == 25
    assert view["stats"]["by_strategy"] == {"telegram_history": 25}


def test_edit_is_a_new_revision_and_repeated_delivery_is_not(client: TestClient, channel: Recording) -> None:
    _, first = collect(client)
    original = next(m for m in first if m["locator"]["telegram"]["message_id"] == 7)

    # the source delivers the same revision of message 7 again (an update replayed by Telegram)
    channel.redeliver(7)
    view, items = collect(client, mode="incremental")
    assert items == []
    assert view["stats"]["duplicates"] == 1

    # an edit: same material_id, new observation, larger sequence, is_edit, new content
    edit_date = T0 + timedelta(days=1)
    channel.edit(7, "Event 7: moved to 20:00", edit_date=edit_date)
    view, items = collect(client, mode="incremental")
    assert len(items) == 1
    edited = items[0]
    assert edited["material_id"] == original["material_id"]
    assert edited["observation_id"] != original["observation_id"]
    assert edited["revision"]["is_edit"] is True
    assert edited["revision"]["sequence"] == int(edit_date.timestamp()) * 1000
    assert edited["revision"]["source_revision"] == str(int(edit_date.timestamp()))
    assert edited["revision"]["sequence"] > original["revision"]["sequence"]
    assert edited["revision"]["content_sha256"] != original["revision"]["content_sha256"]
    assert edited["edited_at"] == "2026-09-02T10:00:00Z"
    assert edited["published_at"] == original["published_at"]
    assert edited["content"]["data"] == "Event 7: moved to 20:00"
    assert edited["discovery"] == {"strategy": "telegram_updates"}
    assert (
        client.get("/v1/states/news-tg").json()["cursors"][CHANNEL_ID]["last_edit_date"]
        == "2026-09-02T10:00:00Z"
    )

    # the edit delivered once more is again a repeated delivery, not a new revision
    channel.redeliver(7)
    view, items = collect(client, mode="incremental")
    assert items == [] and view["stats"]["duplicates"] == 1

    # a second edit within the same second but with other text is still a new revision, and its sequence is
    # strictly larger although Telegram's edit_date (seconds) is the same (R04)
    channel.edit(7, "Event 7: moved to 21:00", edit_date=edit_date)
    view, items = collect(client, mode="incremental")
    assert [m["content"]["data"] for m in items] == ["Event 7: moved to 21:00"]
    second = items[0]["revision"]
    assert second["source_revision"] == edited["revision"]["source_revision"]
    assert second["sequence"] == edited["revision"]["sequence"] + 1

    # a third one in the same second: +1 again; its repeated delivery is a duplicate with the same sequence
    channel.edit(7, "Event 7: moved to 22:00", edit_date=edit_date)
    _, items = collect(client, mode="incremental")
    assert [m["revision"]["sequence"] for m in items] == [second["sequence"] + 1]
    channel.redeliver(7)
    view, items = collect(client, mode="incremental")
    assert items == [] and view["stats"]["duplicates"] == 1


def test_technical_redelivery_keeps_the_observation(client: TestClient, channel: Recording) -> None:
    """Unacknowledged materials are delivered again with the same observation_id (at-least-once)."""
    cid = start(client, {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": "s1"})
    wait_done(client, cid)
    one = page(client, cid, limit=10)
    again = page(client, cid, limit=10)
    assert [m["observation_id"] for m in one["items"]] == [m["observation_id"] for m in again["items"]]
    acked = page(client, cid, one["next_cursor"], limit=10)
    assert acked["items"][0]["locator"]["telegram"]["message_id"] == 11
    replay = page(
        client, cid, one["next_cursor"], limit=10
    )  # the same cursor again: nothing new acknowledged
    assert [m["observation_id"] for m in replay["items"]] == [m["observation_id"] for m in acked["items"]]


def test_full_rerun_is_a_new_observation_of_the_same_revision(client: TestClient, channel: Recording) -> None:
    _, first = collect(client)
    _, second = collect(client)
    assert [m["material_id"] for m in first] == [m["material_id"] for m in second]
    assert all(a["observation_id"] != b["observation_id"] for a, b in zip(first, second, strict=True))
    assert [m["revision"] for m in first] == [m["revision"] for m in second]


def test_edits_and_new_messages_can_be_switched_off(client: TestClient, channel: Recording) -> None:
    collect(client)
    channel.post("New", date=T0 + timedelta(hours=2))
    channel.edit(3, "Edited 3", edit_date=T0 + timedelta(hours=3))
    rules = telegram_rules(USERNAME, updates={"new_messages": True, "edits": False})
    _, items = collect(client, mode="incremental", rules=rules)
    assert [(m["locator"]["telegram"]["message_id"], m["revision"]["is_edit"]) for m in items] == [
        (26, False)
    ]
    channel.post("Newer", date=T0 + timedelta(hours=4))
    channel.edit(4, "Edited 4", edit_date=T0 + timedelta(hours=4))
    rules = telegram_rules(USERNAME, updates={"new_messages": False, "edits": True})
    _, items = collect(client, mode="incremental", rules=rules)
    assert [(m["locator"]["telegram"]["message_id"], m["revision"]["is_edit"]) for m in items] == [(4, True)]


def test_difference_too_long_falls_back_to_history(client: TestClient, channel: Recording) -> None:
    collect(client)
    channel.post("After gap", date=T0 + timedelta(hours=5))
    channel.edit(2, "Edited in the gap", edit_date=T0 + timedelta(hours=5))
    channel.set("min_pts", 100)  # Telegram forgot the updates since the cursor
    cid = start(
        client,
        {
            "source_kind": "telegram",
            "rules": telegram_rules(USERNAME),
            "mode": "incremental",
            "state_key": "news-tg",
        },
    )
    items = drain(client, cid)
    assert [m["locator"]["telegram"]["message_id"] for m in items] == [26]
    errs = client.get(f"/v1/collections/{cid}/errors").json()["items"]
    assert [e["code"] for e in errs] == ["source_unavailable"]
    assert "too long" in errs[0]["message"]


def test_budget_stops_the_run_and_the_next_run_continues(client: TestClient, channel: Recording) -> None:
    limits = {"telegram": {"max_messages_per_run": 10}}
    cid = start(
        client,
        {
            "source_kind": "telegram",
            "rules": telegram_rules(USERNAME),
            "mode": "incremental",
            "state_key": "b",
            "limits": limits,
        },
    )
    items = drain(client, cid)
    assert len(items) == 10
    job = client.get(f"/v1/jobs/{cid}").json()
    assert job["result"]["stopped_by"] == "telegram.max_messages_per_run"
    assert "pts" not in client.get("/v1/states/b").json()["cursors"][CHANNEL_ID]  # history not finished
    ids: list[int] = [m["locator"]["telegram"]["message_id"] for m in items]
    for _ in range(2):
        cid = start(
            client,
            {
                "source_kind": "telegram",
                "rules": telegram_rules(USERNAME),
                "mode": "incremental",
                "state_key": "b",
                "limits": limits,
            },
        )
        more = drain(client, cid)
        ids += [m["locator"]["telegram"]["message_id"] for m in more]
        # the rest of the history is read from the history, and says so (R30)
        assert {m["discovery"]["strategy"] for m in more} == {"telegram_history"}
        assert wait_done(client, cid)["stats"]["by_strategy"] == {"telegram_history": len(more)}
    assert ids == list(range(1, 26))
    assert client.get("/v1/states/b").json()["cursors"][CHANNEL_ID]["pts"] == 25


def test_backpressure_limit_from_the_request(client: TestClient, channel: Recording) -> None:
    """WP-09: ``limits.queue.max_unacked_materials`` of the request pauses the run until materials are pulled."""
    limits = {"queue": {"max_unacked_materials": 3}}
    cid = start(
        client,
        {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": "bp", "limits": limits},
    )
    deadline = time.monotonic() + 10
    view = client.get(f"/v1/collections/{cid}").json()
    while not view["paused_by_backpressure"] and time.monotonic() < deadline:
        time.sleep(0.05)
        view = client.get(f"/v1/collections/{cid}").json()
    assert view["paused_by_backpressure"] is True
    assert view["status"] == "running"
    assert view["stats"]["unacked"] == 3
    assert view["effective_limits"]["queue"]["max_unacked_materials"] == 3
    items = drain(client, cid, limit=2)
    assert len(items) == 25
    assert wait_done(client, cid)["status"] == "succeeded"


def test_same_idempotency_key_returns_the_same_job(client: TestClient, channel: Recording) -> None:
    """WP-09: a repeated POST /v1/collections with the same key does not start a second collection."""
    body = {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": "idem"}
    first = client.post("/v1/collections", json=body, headers={"Idempotency-Key": "k-1"})
    second = client.post("/v1/collections", json=body, headers={"Idempotency-Key": "k-1"})
    assert first.status_code == second.status_code == 202
    assert first.json()["job_id"] == second.json()["job_id"]
    assert second.headers["Idempotency-Replayed"] == "true"
    other = client.post(
        "/v1/collections", json={**body, "mode": "incremental"}, headers={"Idempotency-Key": "k-1"}
    )
    assert other.status_code == 422 and other.json()["code"] == "idempotency_key_reused"
    busy = client.post("/v1/collections", json=body, headers={"Idempotency-Key": "k-2"})
    if busy.status_code == 409:  # the first collection still runs on the same state_key
        assert busy.json()["code"] == "conflict"
    wait_done(client, first.json()["job_id"])


def test_state_can_be_reset(client: TestClient, channel: Recording) -> None:
    collect(client)
    assert client.delete("/v1/states/news-tg").status_code == 204
    assert client.get("/v1/states/news-tg").json()["cursors"] == {}
    _, items = collect(client, mode="incremental")
    assert len(items) == 25  # from scratch again


def test_channel_by_id_and_unknown_channel(client: TestClient, channel: Recording) -> None:
    rules = telegram_rules(CHANNEL_ID, "no_such_channel")
    cid = start(client, {"source_kind": "telegram", "rules": rules, "state_key": "ids"})
    items = drain(client, cid)
    assert len(items) == 25
    view = wait_done(client, cid)
    assert view["status"] == "succeeded" and view["stats"]["errors"] == 1
    errs = client.get(f"/v1/collections/{cid}/errors").json()["items"]
    assert errs[0]["code"] == "not_found" and errs[0]["telegram_message"] == "@no_such_channel"


def test_one_shot_fetch(
    client: TestClient, channel: Recording, material_validator: Draft202012Validator
) -> None:
    r = client.post(
        "/v1/fetches",
        json={"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 5}},
    )
    assert r.status_code == 200, r.text
    m = r.json()
    assert not list(material_validator.iter_errors(m))
    assert m["material_id"] == f"tg:{CHANNEL_ID}:5" and m["content"]["data"] == "Event 5: concert at 19:00"
    again = client.post(
        "/v1/fetches",
        json={"source_kind": "telegram", "telegram": {"channel_id": CHANNEL_ID, "message_id": 5}},
    ).json()
    assert again["observation_id"] != m["observation_id"] and again["revision"] == m["revision"]
    missing = client.post(
        "/v1/fetches",
        json={"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 999}},
    )
    # the source says there is no such message: 404 not_found, not retryable (R04)
    assert missing.status_code == 404, missing.text
    assert missing.json()["code"] == "not_found" and missing.json()["retryable"] is False
    assert missing.json()["details"]["reason"] == "message_not_found"
    assert m["revision"]["sequence"] == int(m["revision"]["source_revision"]) * 1000
    web = client.post("/v1/fetches", json={"source_kind": "web", "url": "https://example.test/"})
    assert web.status_code == 422
