"""Contract tests: every collector.v1 operation of the real app, responses validated by ContractClient."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import ContractClient, OpenAPISpec
from jane_telegram_collector.testing import FAST_LIMITS, REPO_ROOT, USERNAME, Recording, telegram_rules

pytestmark = pytest.mark.contract

SPEC = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "collector.v1.yaml")
COMMON = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "common.yaml")


def test_every_operation_matches_the_contract(
    client: TestClient, channel: Recording, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = ContractClient(SPEC, client)
    COMMON.validate_component("Health", api.get("/v1/health").json())
    COMMON.validate_component("ServiceInfo", api.get("/v1/info").json())

    # fetch: 200, 429 (flood-wait), 502 (missing message), 422 (not telegram), 400 (bad JSON)
    one = {"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 1}}
    assert api.post("/v1/fetches", json=one).status_code == 200
    channel.set("faults", [{"method": "get_message", "flood_wait": 30, "count": 1}])
    assert api.post("/v1/fetches", json=one).status_code == 429
    channel.set("faults", [])
    missing = {"source_kind": "telegram", "telegram": {"channel_username": USERNAME, "message_id": 404}}
    assert api.post("/v1/fetches", json=missing).status_code == 502
    assert (
        api.post("/v1/fetches", json={"source_kind": "web", "url": "https://example.test/"}).status_code
        == 422
    )
    bad = api.request("POST", "/v1/fetches", content=b"{", headers={"content-type": "application/json"})
    assert bad.status_code == 400

    # rules validation: telegram (supported), web (valid, not supported), invalid
    rules = telegram_rules(USERNAME)
    assert api.post("/v1/rules/validations", json=rules).json() == {
        "valid": True,
        "supported": True,
        "errors": [],
        "warnings": [],
    }
    web = api.post(
        "/v1/rules/validations",
        json={
            "collector": "web",
            "scope": {"allowed_domains": ["example.test"]},
            "strategies": [{"type": "recursive"}],
        },
    ).json()
    assert web["valid"] is True and web["supported"] is False
    raw = client.post("/v1/rules/validations", json={"collector": "telegram", "channels": []})
    SPEC.validate_response("POST", "/v1/rules/validations", raw.status_code, raw.json())
    invalid = raw.json()
    assert invalid["valid"] is False and invalid["errors"][0]["pointer"] == "/channels"

    # collections: 202, replay, 409 (state_key busy), 422, get, materials, errors
    body = {
        "source_kind": "telegram",
        "source_id": "contract",
        "rules": rules,
        "limits": {**FAST_LIMITS, "queue": {"max_unacked_materials": 3}},
    }
    first = api.post("/v1/collections", json=body, headers={"Idempotency-Key": "c-1"})
    assert first.status_code == 202
    cid = first.json()["job_id"]
    replay = api.post("/v1/collections", json=body, headers={"Idempotency-Key": "c-1"})
    assert replay.json()["job_id"] == cid and replay.headers["Idempotency-Replayed"] == "true"
    assert api.post("/v1/collections", json=body, headers={"Idempotency-Key": "c-2"}).status_code == 409
    no_rules = client.post(
        "/v1/collections", json={"source_kind": "telegram"}, headers={"Idempotency-Key": "c-3"}
    )
    SPEC.validate_response(
        "POST", "/v1/collections", no_rules.status_code, no_rules.json(), no_rules.headers["content-type"]
    )
    assert no_rules.status_code == 422
    web_kind = api.post(
        "/v1/collections", json={"source_kind": "web", "rules": rules}, headers={"Idempotency-Key": "c-4"}
    )
    assert web_kind.status_code == 422
    api.get(f"/v1/collections/{cid}")
    api.get(f"/v1/jobs/{cid}")
    page = api.get(f"/v1/collections/{cid}/materials", params={"limit": 2, "wait_ms": 2000}).json()
    assert page["items"]
    api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"], "limit": 2})
    api.get(f"/v1/collections/{cid}/errors", params={"limit": 1})
    assert api.get("/v1/collections/job_nope").status_code == 404
    assert api.get("/v1/collections/job_nope/materials").status_code == 404
    assert api.get("/v1/collections/job_nope/errors").status_code == 404

    # state while running -> DELETE conflicts; cancel the job; then state reads and resets
    assert api.delete("/v1/states/contract").status_code == 409
    assert api.post(f"/v1/jobs/{cid}/cancel", json={"reason": "contract test"}).status_code == 202
    deadline = time.monotonic() + 10
    while api.get(f"/v1/jobs/{cid}").json()["status"] != "cancelled" and time.monotonic() < deadline:
        time.sleep(0.05)
    assert api.get(f"/v1/collections/{cid}").json()["status"] == "cancelled"
    assert api.post(f"/v1/jobs/{cid}/cancel").status_code == 200
    assert api.get("/v1/jobs/job_nope").status_code == 404
    assert api.post("/v1/jobs/job_nope/cancel").status_code == 404
    state = api.get("/v1/states/contract").json()
    assert state["collector"] == "telegram" and state["cursors"]["-1001234567890"]["last_message_id"] >= 1
    assert api.delete("/v1/states/contract").status_code == 204
    assert api.get("/v1/states/never-used").status_code == 404

    # connections
    monkeypatch.setenv("JANE_TEST_TG_SESSION", "x")
    conn = {
        "connection_id": "tg-main",
        "kind": "telegram_account",
        "params": {"api_id": 12345},
        "secret_refs": {"session": "env:JANE_TEST_TG_SESSION"},
    }
    created = api.put("/v1/connections/tg-main", json=conn)
    assert created.status_code == 201
    etag = created.headers["ETag"]
    assert api.put("/v1/connections/tg-main", json=conn, headers={"If-Match": etag}).status_code == 200
    assert api.put("/v1/connections/tg-main", json=conn, headers={"If-Match": '"stale"'}).status_code == 412
    leaked = api.put("/v1/connections/tg-main", json={**conn, "params": {"api_hash": "0123abcd"}})
    assert leaked.status_code == 422 and leaked.json()["code"] == "secret_detected"
    assert api.get("/v1/connections").json()["items"][0]["connection_id"] == "tg-main"
    assert api.get("/v1/connections/tg-main").headers["ETag"] == etag
    tested = api.post("/v1/connections/tg-main/test").json()
    assert tested["ok"] is True and tested["secrets_resolved"] == {"session": True}
    assert api.delete("/v1/connections/tg-main").status_code == 204
    assert api.get("/v1/connections/tg-main").status_code == 404
    assert api.delete("/v1/connections/tg-main").status_code == 404
    assert api.post("/v1/connections/tg-main/test").status_code == 404

    assert api.uncovered() == []
