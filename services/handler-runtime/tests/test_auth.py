"""ADR-0005 in handler-runtime: a token for every operation and the handler.v1 scope (jane_kit.auth_scopes)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from jane_handler_runtime.app import build_app
from jane_handler_runtime.settings import Settings
from jane_kit.auth import sha256_hex

KEYS = [
    {"name": "invoker", "sha256": sha256_hex("k-runtime-invoker"), "scopes": ["handler:invoke"]},
    {"name": "tester", "sha256": sha256_hex("k-runtime-tester"), "scopes": ["handler:test"]},
    {"name": "registry", "sha256": sha256_hex("k-runtime-registry"), "scopes": []},
]


def auth(token: str, **extra: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", **extra}


def test_runtime_needs_a_token_and_the_operation_scope(subprocess_settings: Settings) -> None:
    s = subprocess_settings.with_overrides(auth_mode="api_key", api_keys=KEYS)
    with TestClient(build_app(s)) as c:
        assert c.get("/v1/health").status_code == 200
        assert c.get("/v1/info").status_code == 401
        # the registry reads runtime profiles from /v1/info with its own key that has no runtime scope
        info = c.get("/v1/info", headers=auth("k-runtime-registry")).json()
        assert info["auth_mode"] == "api_key" and info["capabilities"]["runtime_profiles"]

        missing = c.post("/v1/test-runs", json={}, headers={"Idempotency-Key": "t-1"})
        assert missing.status_code == 401 and missing.json()["code"] == "unauthenticated"
        assert missing.headers["www-authenticate"] == "Bearer"
        denied = c.post(
            "/v1/test-runs", json={}, headers=auth("k-runtime-invoker", **{"Idempotency-Key": "t-2"})
        )
        assert denied.status_code == 403 and denied.json()["detail"] == "scope handler:test required"
        # invocations read RAW of every source through file:// (B1 ContentRef roots): never without handler:invoke
        anonymous = c.post("/v1/invocations", json={}, headers={"Idempotency-Key": "i-1"})
        assert anonymous.status_code == 401 and anonymous.json()["code"] == "unauthenticated"
        assert c.get("/v1/invocations/inv_x").status_code == 401
        tester = c.post(
            "/v1/invocations", json={}, headers=auth("k-runtime-tester", **{"Idempotency-Key": "i-2"})
        )
        assert tester.status_code == 403 and tester.json()["detail"] == "scope handler:invoke required"
        registry = c.post(
            "/v1/invocations", json={}, headers=auth("k-runtime-registry", **{"Idempotency-Key": "i-3"})
        )
        assert registry.status_code == 403
        assert c.get("/v1/invocations/inv_x", headers=auth("k-runtime-invoker")).status_code == 404
        assert c.get("/v1/jobs/job_x", headers=auth("k-runtime-tester")).status_code == 404
        assert c.get("/v1/jobs/job_x", headers=auth("k-runtime-registry")).status_code == 403
        assert c.get("/v1/connections", headers=auth("k-runtime-invoker")).status_code == 200
        assert c.put("/v1/connections/x", json={}, headers=auth("k-runtime-invoker")).status_code == 403
        assert c.get("/v1/invocations/inv_x", headers=auth("wrong-key")).status_code == 401
