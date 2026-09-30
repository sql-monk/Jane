"""Flood-wait, per-call timeouts and retries from the limit levels, account connections and secrets, media."""

from __future__ import annotations

import base64
import time
from datetime import timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import url2pathname

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from jane_telegram_collector.app import build_app
from jane_telegram_collector.settings import Settings
from jane_telegram_collector.testing import (
    FAST_LIMITS,
    T0,
    USERNAME,
    Recording,
    drain,
    errors,
    make_settings,
    start,
    telegram_rules,
    wait_done,
)


def body(state_key: str, **extra: object) -> dict[str, object]:
    return {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": state_key, **extra}


# ---------------------------------------------------------------- flood-wait


def test_short_flood_wait_is_waited_out(client: TestClient, channel: Recording) -> None:
    channel.set("faults", [{"method": "history", "flood_wait": 2, "count": 1}])
    started = time.monotonic()
    cid = start(client, body("fw"))
    items = drain(client, cid)
    view = wait_done(client, cid)
    assert view["status"] == "succeeded"
    assert len(items) == 25
    assert time.monotonic() - started >= 2
    assert client.get(f"/v1/jobs/{cid}").json()["result"]["flood_waits"] == 1


def test_long_flood_wait_stops_with_rate_limited_and_the_next_run_continues(
    client: TestClient, channel: Recording
) -> None:
    cid = start(client, body("fw2", limits={"telegram": {"max_flood_wait_seconds": 5}}))
    first = drain(client, cid)
    assert len(first) == 25
    for i in range(5):
        channel.post(f"late {i}", date=T0 + timedelta(hours=1, minutes=i))
    channel.set("faults", [{"method": "changes", "flood_wait": 3600, "count": 1}])
    cid = start(client, body("fw2", mode="incremental", limits={"telegram": {"max_flood_wait_seconds": 5}}))
    assert drain(client, cid) == []
    view = wait_done(client, cid)
    assert view["status"] == "failed"
    job = client.get(f"/v1/jobs/{cid}").json()
    assert job["status"] == "failed"
    assert job["error"]["code"] == "rate_limited"
    assert job["error"]["retryable"] is True
    assert job["error"]["retry_after_seconds"] == 3600
    errs = errors(client, cid)
    assert [e["code"] for e in errs] == ["rate_limited"]
    # the flood is over: the next run continues from the saved cursor, nothing lost, nothing repeated
    cid = start(client, body("fw2", mode="incremental"))
    items = drain(client, cid)
    assert [m["locator"]["telegram"]["message_id"] for m in items] == [26, 27, 28, 29, 30]


def test_one_shot_fetch_does_not_block_on_flood_wait(client: TestClient, channel: Recording) -> None:
    channel.set("faults", [{"method": "get_message", "flood_wait": 42, "count": 1}])
    r = client.post(
        "/v1/fetches",
        json={"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 1}},
    )
    assert r.status_code == 429
    assert r.json()["code"] == "rate_limited"
    assert r.headers["Retry-After"] == "42"


# ---------------------------------------------------------------- timeouts and retries from the limit levels


def test_request_timeout_from_the_request_applies_to_each_call(
    client: TestClient, channel: Recording
) -> None:
    channel.set("faults", [{"method": "history", "delay_ms": 1500, "count": 5}])
    limits = {
        "timeouts": {"request_timeout_ms": 200},
        "retries": {"max_attempts": 2, "initial_backoff_ms": 0, "max_backoff_ms": 0},
    }
    cid = start(client, body("to", limits=limits))
    view = wait_done(client, cid)
    assert view["status"] == "failed"
    job = client.get(f"/v1/jobs/{cid}").json()
    assert job["error"]["code"] == "source_unavailable"
    assert "TimeoutError" in job["error"]["detail"]
    assert errors(client, cid)[0]["attempts"] == 2


def test_rules_level_timeout_and_transient_errors_are_retried(client: TestClient, channel: Recording) -> None:
    # two transient failures, three attempts from the source level (rules.limits): the run succeeds
    channel.set("faults", [{"method": "history", "unavailable": True, "count": 2}])
    rules = telegram_rules(
        USERNAME, limits={"retries": {"max_attempts": 3, "initial_backoff_ms": 0, "max_backoff_ms": 0}}
    )
    r = client.post(
        "/v1/collections",
        json={
            "source_kind": "telegram",
            "rules": rules,
            "state_key": "rt",
            "limits": {"rate": {"min_delay_ms_per_host": 0}},
        },
        headers={"Idempotency-Key": "rt-1"},
    )
    cid = r.json()["job_id"]
    assert len(drain(client, cid)) == 25
    assert wait_done(client, cid)["status"] == "succeeded"


def test_platform_limits_and_hard_caps_from_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, channel: Recording
) -> None:
    monkeypatch.setenv("JANE_TELEGRAM_COLLECTOR_LIMITS__TELEGRAM__MAX_FLOOD_WAIT_SECONDS", "60")
    monkeypatch.setenv("JANE_TELEGRAM_COLLECTOR_LIMITS__HARD_CAPS__QUEUE__MAX_UNACKED_MATERIALS", "7")
    settings = make_settings(tmp_path)
    with TestClient(build_app(settings)) as c:
        info = c.get("/v1/info").json()
        assert info["limits"]["defaults"]["telegram"]["max_flood_wait_seconds"] == 60
        assert info["limits"]["hard_caps"] == {"queue": {"max_unacked_materials": 7}}
        cid = start(c, body("caps", limits={**FAST_LIMITS, "queue": {"max_unacked_materials": 1000}}))
        view = c.get(f"/v1/collections/{cid}").json()
        assert view["effective_limits"]["queue"]["max_unacked_materials"] == 7  # min(request, hard cap)
        drain(c, cid)


def test_lease_configuration_is_validated(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must be less than lease_seconds"):
        make_settings(tmp_path, lease_seconds=3, heartbeat_interval_ms=1000, state_busy_timeout_ms=2000)


# ---------------------------------------------------------------- account connection and secrets


def account(conn_id: str = "tg-main", **secret_refs: str) -> dict[str, object]:
    return {
        "connection_id": conn_id,
        "kind": "telegram_account",
        "title": "Collector account",
        "params": {"api_id": 12345},
        "secret_refs": secret_refs
        or {"session": "env:JANE_SECRET_TEST_TG_SESSION", "api_hash": "env:JANE_SECRET_TEST_TG_API_HASH"},
    }


def test_account_secrets_are_resolved_only_in_the_collector(
    client: TestClient, channel: Recording, monkeypatch: pytest.MonkeyPatch
) -> None:
    channel.set("required_secrets", ["session", "api_hash"])
    monkeypatch.delenv("JANE_SECRET_TEST_TG_SESSION", raising=False)
    monkeypatch.setenv("JANE_SECRET_TEST_TG_API_HASH", "hash-value-not-a-real-secret")
    put = client.put("/v1/connections/tg-main", json=account())
    assert put.status_code == 201
    assert "hash-value" not in put.text
    test = client.post("/v1/connections/tg-main/test").json()
    assert test["ok"] is False and test["secrets_resolved"] == {"session": False, "api_hash": True}
    rules = telegram_rules(USERNAME, account_connection_id="tg-main")
    r = client.post(
        "/v1/collections",
        json={"source_kind": "telegram", "rules": rules, "state_key": "acc"},
        headers={"Idempotency-Key": "a-1"},
    )
    assert r.status_code == 422
    assert r.json()["errors"][0]["pointer"] == "/rules/account_connection_id"
    assert "session" in r.json()["errors"][0]["message"]

    monkeypatch.setenv("JANE_SECRET_TEST_TG_SESSION", "session-value-not-a-real-secret")
    assert client.post("/v1/connections/tg-main/test").json()["ok"] is True
    cid = start(client, {"source_kind": "telegram", "rules": rules, "state_key": "acc"})
    items = drain(client, cid)
    assert len(items) == 25
    for text in (client.get(f"/v1/collections/{cid}").text, client.get(f"/v1/jobs/{cid}").text, str(items)):
        assert "session-value" not in text and "hash-value" not in text


def test_session_rejected_by_telegram_fails_the_collection(
    client: TestClient, channel: Recording, monkeypatch: pytest.MonkeyPatch
) -> None:
    channel.set("required_secrets", ["session"])
    client.put("/v1/connections/tg-bad", json=account("tg-bad", api_hash="env:JANE_SECRET_TEST_TG_API_HASH"))
    monkeypatch.setenv("JANE_SECRET_TEST_TG_API_HASH", "x")
    cid = start(
        client,
        {
            "source_kind": "telegram",
            "rules": telegram_rules(USERNAME, account_connection_id="tg-bad"),
            "state_key": "bad",
        },
    )
    view = wait_done(client, cid)
    assert view["status"] == "failed"
    error = client.get(f"/v1/jobs/{cid}").json()["error"]
    assert error["code"] == "source_unavailable" and error["details"]["reason"] == "account_unauthorized"
    assert error["retryable"] is False


def test_connections_reject_secret_values_and_other_kinds(client: TestClient) -> None:
    leaked = {**account(), "params": {"api_id": 1, "session_string": "1BVtsOK..."}}
    r = client.put("/v1/connections/tg-main", json=leaked)
    assert r.status_code == 422 and r.json()["code"] == "secret_detected"
    r = client.put("/v1/connections/pg", json={"connection_id": "pg", "kind": "postgresql"})
    assert r.status_code == 422
    rules = telegram_rules(USERNAME, account_connection_id="nope")
    r = client.post(
        "/v1/collections",
        json={"source_kind": "telegram", "rules": rules},
        headers={"Idempotency-Key": "u-1"},
    )
    assert r.status_code == 422 and "unknown connection" in r.json()["errors"][0]["message"]


def test_telethon_backend_requires_an_account(tmp_path: Path) -> None:
    settings = make_settings(tmp_path, client_backend="telethon")
    with TestClient(build_app(settings)) as c:
        assert c.get("/v1/info").json()["capabilities"]["client_backend"] == "telethon"
        r = c.post(
            "/v1/collections",
            json={"source_kind": "telegram", "rules": telegram_rules(USERNAME)},
            headers={"Idempotency-Key": "t-1"},
        )
        assert r.status_code == 422
        assert r.json()["errors"][0]["pointer"] == "/rules/account_connection_id"


# ---------------------------------------------------------------- media and content delivery

PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 600).decode()
BIG = base64.b64encode(b"x" * 3000).decode()


def test_media_download_inline_blob_and_size_limit(
    tmp_path: Path, material_validator: Draft202012Validator
) -> None:
    settings: Settings = make_settings(tmp_path, transit_dir=tmp_path / "transit")
    assert settings.recordings_dir is not None
    rec = Recording.create(settings.recordings_dir, channel_id="-1009", username="media_chan", title="Media")
    rec.post(
        "photo",
        date=T0,
        media=[{"kind": "photo", "name": "p.png", "media_type": "image/png", "data_base64": PNG}],
    )
    rec.post(
        "doc",
        date=T0,
        media=[
            {
                "kind": "document",
                "name": "d.bin",
                "media_type": "application/octet-stream",
                "data_base64": BIG,
            }
        ],
    )
    rules = telegram_rules("media_chan", media={"download": True, "kinds": ["photo", "document"]})
    with TestClient(build_app(settings)) as c:
        limits = {
            **FAST_LIMITS,
            "transfer": {"inline_max_bytes": 1000},
            "telegram": {"max_media_bytes": 5000},
        }
        cid = start(c, {"source_kind": "telegram", "rules": rules, "state_key": "m", "limits": limits})
        items = drain(c, cid)
    for m in items:
        assert not list(material_validator.iter_errors(m))
    photo, doc = items
    assert photo["attachments"][0]["content"]["kind"] == "inline"
    assert photo["attachments"][0]["content"]["encoding"] == "base64"
    assert photo["attachments"][0]["role"] == "photo"
    blob = doc["attachments"][0]["content"]
    assert blob["kind"] == "blob" and blob["uri"].startswith("file://") and blob["store"] == "transit"
    assert blob["size_bytes"] == 3000
    # too large for telegram.max_media_bytes: skipped with a diagnostic, the message itself is emitted
    with TestClient(build_app(settings)) as c:
        limits = {**FAST_LIMITS, "telegram": {"max_media_bytes": 1000}}
        cid = start(c, {"source_kind": "telegram", "rules": rules, "state_key": "m2", "limits": limits})
        items = drain(c, cid)
    assert "attachments" in items[0] and "attachments" not in items[1]
    assert items[1]["diagnostics"][0]["code"] == "media_too_large"


def test_content_delivery_blob_and_inline(tmp_path: Path, channel: Recording) -> None:
    settings = make_settings(tmp_path, transit_dir=tmp_path / "transit")
    with TestClient(build_app(settings)) as c:
        cid = start(c, body("b", content_delivery="blob"))
        items = drain(c, cid)
        assert {m["content"]["kind"] for m in items} == {"blob"}
        uri = urlparse(items[0]["content"]["uri"])
        path = Path(url2pathname(uri.path))
        assert path.read_bytes() == b"Event 1: concert at 19:00"
        cid = start(c, body("i", content_delivery="inline"))
        assert {m["content"]["kind"] for m in drain(c, cid)} == {"inline"}
    with TestClient(build_app(make_settings(tmp_path / "noblob"))) as c:
        r = c.post(
            "/v1/collections", json=body("x", content_delivery="blob"), headers={"Idempotency-Key": "b-1"}
        )
        assert r.status_code == 422


# ---------------------------------------------------------------- cancellation


def test_cancel_a_running_collection(client: TestClient, channel: Recording) -> None:
    cid = start(client, body("c", limits={"queue": {"max_unacked_materials": 2}}))
    deadline = time.monotonic() + 10
    while (
        not client.get(f"/v1/collections/{cid}").json()["paused_by_backpressure"]
        and time.monotonic() < deadline
    ):
        time.sleep(0.05)
    r = client.post(f"/v1/jobs/{cid}/cancel", json={"reason": "test"})
    assert r.status_code == 202
    view = wait_done(client, cid)
    assert view["status"] == "cancelled"
    assert client.get(f"/v1/jobs/{cid}").json()["status"] == "cancelled"
    # the state_key is free again
    cid = start(client, body("c"))
    assert wait_done(client, cid)["status"] == "succeeded"


# ---------------------------------------------------------------- secret policy (coordinator decision, as WP-10)


def test_connection_policy_rejects_exfiltration(
    tmp_path: Path, channel: Recording, monkeypatch: pytest.MonkeyPatch
) -> None:
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "session").write_text("session-from-file", encoding="utf-8")
    (tmp_path / "outside").write_text("not-for-telegram", encoding="utf-8")
    monkeypatch.setenv("PGPASSWORD", "db-password-not-for-telegram")
    monkeypatch.setenv("JANE_SECRET_TG_SESSION", "session-from-env")
    settings = make_settings(
        tmp_path, secret_files_dir=secrets_dir, telegram_host_allowlist=["proxy.internal.test"]
    )
    rules = telegram_rules(USERNAME, account_connection_id="tg")

    def conn(**overrides: object) -> dict[str, object]:
        return {"connection_id": "tg", "kind": "telegram_account", "params": {"api_id": 1}, **overrides}

    rejected: list[tuple[dict[str, Any], str, str]] = [
        ({"secret_refs": {"session": "env:PGPASSWORD"}}, "/secret_refs/session", "secret_ref_not_allowed"),
        (
            {"secret_refs": {"session": f"file:{secrets_dir / '..' / 'outside'}"}},
            "/secret_refs/session",
            "secret_ref_not_allowed",
        ),
        (
            {"secret_refs": {"session": "vault:kv/tg#session"}},
            "/secret_refs/session",
            "secret_ref_not_allowed",
        ),
        (
            {"params": {"api_id": 1, "proxy_host": "evil.example.org"}},
            "/params/proxy_host",
            "host_not_allowed",
        ),
        (
            {"params": {"api_id": 1, "server": "https://evil.example.org:443"}},
            "/params/server",
            "host_not_allowed",
        ),
        # values that URL parsers read differently must not pass as the allow-listed host
        *(
            ({"params": {"api_id": 1, "proxy_host": value}}, "/params/proxy_host", "host_not_allowed")
            for value in (
                "evil.example.org\\@proxy.internal.test",
                "evil.example.org@proxy.internal.test",
                "http://evil.example.org\\@proxy.internal.test",
                "proxy.internal.test/../evil",
                "proxy.internal.test evil.example.org",
                "proxy.internal.test\t",
                "proxy.internal.test\x00.evil.example.org",
                "proxy.internal.test.",
                "proxy.internal.test:99999",
                "proxy.internal.test?x=1",
            )
        ),
    ]
    with TestClient(build_app(settings)) as c:
        for overrides, pointer, code in rejected:
            r = c.put("/v1/connections/tg", json=conn(**overrides))
            assert r.status_code == 422, (overrides, r.text)
            assert r.json()["errors"][0]["pointer"] == pointer
            assert r.json()["errors"][0]["code"] == code
        assert c.get("/v1/connections/tg").status_code == 404

        # allowed: prefixed env variable, file inside the secrets directory, allow-listed host
        ok = conn(
            params={"api_id": 1, "proxy_host": "proxy.internal.test"},
            secret_refs={
                "session": "env:JANE_SECRET_TG_SESSION",
                "api_hash": f"file:{secrets_dir / 'session'}",
            },
        )
        assert c.put("/v1/connections/tg", json=ok).status_code == 201
        assert c.post("/v1/connections/tg/test").json()["secrets_resolved"] == {
            "session": True,
            "api_hash": True,
        }
        cid = start(c, {"source_kind": "telegram", "rules": rules, "state_key": "pol"})
        assert len(drain(c, cid)) == 25

        # a connection stored bypassing the API gets no secrets and is rejected when used
        store = c.app.state.store  # type: ignore[attr-defined]
        store.put_connection("tg", conn(secret_refs={"session": "env:PGPASSWORD"}), '"x"')
        assert c.post("/v1/connections/tg/test").json()["secrets_resolved"] == {"session": False}
        r = c.post(
            "/v1/collections",
            json={"source_kind": "telegram", "rules": rules, "state_key": "pol2"},
            headers={"Idempotency-Key": "pol-2"},
        )
        assert r.status_code == 422
        assert r.json()["errors"][0]["code"] == "secret_ref_not_allowed"
        assert "db-password" not in r.text
        one = {
            "source_kind": "telegram",
            "rules": rules,
            "telegram": {"channel_username": USERNAME, "message_id": 1},
        }
        assert c.post("/v1/fetches", json=one).status_code == 422
