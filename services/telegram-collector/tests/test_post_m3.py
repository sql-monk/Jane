"""WP-16 (post-M3) on the real collector app against recorded channels.

* R30: a service message of the channel (``MessageService``: channel created, message pinned...) is emitted
  like any message, with its action in ``metadata.service_action``; a continued history read is
  ``telegram_history`` (see ``test_collect.test_budget_stops_the_run_and_the_next_run_continues``).
* R04: a state file of the previous format (``revision.sequence`` = epoch seconds in ``tg_seen``) is migrated,
  so known revisions stay known; a state store held by another instance answers 503 ``service_unavailable``
  with ``Retry-After`` (documented in ``collector.v1``), validated against the contract.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from jane_kit.contracts import ContractClient, OpenAPISpec
from jane_telegram_collector.app import build_app
from jane_telegram_collector.state import SCHEMA_VERSION, StateFileTooNew
from jane_telegram_collector.testing import (
    CHANNEL_ID,
    REPO_ROOT,
    T0,
    USERNAME,
    Recording,
    drain,
    make_settings,
    start,
    telegram_rules,
    wait_done,
)

SPEC = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "collector.v1.yaml")


def _collect(
    client: TestClient, mode: str = "full", **extra: Any
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    body: dict[str, Any] = {
        "source_kind": "telegram",
        "rules": telegram_rules(USERNAME),
        "mode": mode,
        "state_key": "news-tg",
        **extra,
    }
    cid = start(client, body)
    items = drain(client, cid)
    return wait_done(client, cid), items


def test_service_messages_are_emitted_and_marked_in_metadata(
    client: TestClient, channel: Recording, material_validator: Draft202012Validator
) -> None:
    channel.post("", date=T0 + timedelta(hours=1), service="pin_message")
    channel.post("A post after the pin", date=T0 + timedelta(hours=1, minutes=1))
    _, items = _collect(client)
    service, post = items[-2], items[-1]
    assert service["locator"]["telegram"]["message_id"] == 26
    assert service["metadata"]["service_action"] == "pin_message"
    assert service["content"]["data"] == "" and service["format"]["content_kind"] == "message"
    assert not list(material_validator.iter_errors(service))
    assert "service_action" not in post.get("metadata", {})
    assert all("service_action" not in m.get("metadata", {}) for m in items[:-2])
    # a service message posted later comes through the updates, marked the same way
    channel.post("", date=T0 + timedelta(hours=2), service="chat_edit_title")
    _, items = _collect(client, mode="incremental")
    assert [(m["metadata"].get("service_action"), m["discovery"]["strategy"]) for m in items] == [
        ("chat_edit_title", "telegram_updates")
    ]


def test_state_file_of_the_previous_format_is_migrated(tmp_path: Path, channel: Recording) -> None:
    settings = make_settings(tmp_path)
    with TestClient(build_app(settings)) as client:
        _, first = _collect(client)
    original = next(m for m in first if m["locator"]["telegram"]["message_id"] == 7)
    # what a collector before R04 left: sequences in epoch seconds and no schema version
    db = sqlite3.connect(settings.state_dir / "state.db")
    with db:
        db.execute("UPDATE tg_seen SET sequence = sequence / 1000")
        db.execute("PRAGMA user_version = 0")
    seconds = db.execute(
        "SELECT sequence FROM tg_seen WHERE material_id = ?", (f"tg:{CHANNEL_ID}:7",)
    ).fetchone()[0]
    db.close()
    assert seconds == int(T0.timestamp()) + 6 * 60

    with TestClient(build_app(settings)) as client:
        assert client.app.state.store.schema_version() == SCHEMA_VERSION  # type: ignore[attr-defined]
        channel.redeliver(7)  # the known revision again: still a duplicate after the migration
        view, items = _collect(client, mode="incremental")
        assert items == [] and view["stats"]["duplicates"] == 1
        channel.edit(7, "Event 7: moved", edit_date=T0 + timedelta(days=1))
        _, items = _collect(client, mode="incremental")
    assert len(items) == 1 and items[0]["revision"]["sequence"] > original["revision"]["sequence"]


@pytest.fixture
def busy_client(tmp_path: Path) -> Iterator[TestClient]:
    """The app with a short lock wait, so a held SQLite lock turns into 503 quickly."""
    with TestClient(build_app(make_settings(tmp_path, state_busy_timeout_ms=200))) as client:
        yield client


def test_busy_state_store_answers_503_with_retry_after(
    busy_client: TestClient, channel: Recording, tmp_path: Path
) -> None:
    api = ContractClient(SPEC, busy_client)
    cid = start(
        busy_client, {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": "busy"}
    )
    wait_done(busy_client, cid)
    page = api.get(f"/v1/collections/{cid}/materials", params={"limit": 5}).json()
    # another instance holds the write lock of the shared state file (here: a plain SQLite connection)
    other = sqlite3.connect(tmp_path / "state" / "state.db", isolation_level=None)
    other.execute("BEGIN IMMEDIATE")
    try:
        ack = api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"]})
        assert ack.status_code == 503, ack.text
        problem = ack.json()
        assert problem["code"] == "service_unavailable" and problem["retryable"] is True
        assert int(ack.headers["Retry-After"]) >= 1
        reset = api.delete("/v1/states/busy")
        assert reset.status_code == 503 and reset.json()["code"] == "service_unavailable"
    finally:
        other.execute("ROLLBACK")
        other.close()
    # the same requests succeed once the lock is free (nothing was half-written)
    assert (
        api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"]}).status_code == 200
    )
    assert api.delete("/v1/states/busy").status_code == 204


def test_one_shot_fetch_numbers_revisions_like_collections(client: TestClient, channel: Recording) -> None:
    """Review 1 of WP-16: a one-shot fetch takes the revision number from the revisions the collector already
    emitted, so another text within the same second does not get the sequence of an earlier revision."""
    edit_date = T0 + timedelta(days=1)
    seconds = int(edit_date.timestamp())
    channel.edit(7, "Event 7: moved to 20:00", edit_date=edit_date)
    _, items = _collect(client)
    first = next(m for m in items if m["locator"]["telegram"]["message_id"] == 7)
    assert first["revision"]["sequence"] == seconds * 1000
    channel.edit(7, "Event 7: moved to 21:00", edit_date=edit_date)  # the same second, another text
    body = {"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 7}}
    one = client.post("/v1/fetches", json=body).json()
    assert one["revision"]["sequence"] == seconds * 1000 + 1
    assert client.post("/v1/fetches", json=body).json()["revision"] == one["revision"]  # nothing written
    _, items = _collect(client, mode="incremental")
    assert [m["revision"]["sequence"] for m in items] == [one["revision"]["sequence"]]  # numbered alike


def test_state_file_of_a_newer_version_is_refused(tmp_path: Path, channel: Recording) -> None:
    settings = make_settings(tmp_path)
    with TestClient(build_app(settings)):
        pass
    db = sqlite3.connect(settings.state_dir / "state.db")
    db.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
    db.close()
    with pytest.raises(StateFileTooNew, match="newer than this collector supports"):
        build_app(settings)
