"""ADR-0005 in the web-collector: a token for every operation and the collector.v1 scope (jane_kit.auth_scopes)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from jane_kit.auth import sha256_hex
from jane_web_collector.app import build_app
from jane_web_collector.settings import Settings

KEYS = [
    {"name": "viewer", "sha256": sha256_hex("k-collector-viewer"), "scopes": ["collector:read"]},
    {"name": "runner", "sha256": sha256_hex("k-collector-runner"), "scopes": ["collector:run"]},
    {"name": "nobody", "sha256": sha256_hex("k-collector-nobody"), "scopes": []},
]


def auth(token: str, **extra: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", **extra}


def test_collector_needs_a_token_and_the_operation_scope(settings: Settings) -> None:
    s = settings.with_overrides(auth_mode="api_key", api_keys=KEYS)
    with TestClient(build_app(s)) as c:
        assert c.get("/v1/health").status_code == 200
        assert c.get("/v1/info").status_code == 401
        assert c.get("/v1/info", headers=auth("k-collector-nobody")).json()["auth_mode"] == "api_key"

        missing = c.post("/v1/collections", json={}, headers={"Idempotency-Key": "c-1"})
        assert missing.status_code == 401 and missing.json()["code"] == "unauthenticated"
        denied = c.post(
            "/v1/collections", json={}, headers=auth("k-collector-viewer", **{"Idempotency-Key": "c-2"})
        )
        assert denied.status_code == 403 and denied.json()["detail"] == "scope collector:run required"
        assert c.post("/v1/fetches", json={}, headers=auth("k-collector-viewer")).status_code == 403
        assert c.get("/v1/collections/col_x", headers=auth("k-collector-viewer")).status_code == 404
        assert c.get("/v1/collections/col_x", headers=auth("k-collector-runner")).status_code == 403
        assert c.delete("/v1/states/s-1", headers=auth("k-collector-viewer")).status_code == 403
        assert c.get("/v1/jobs/col_x", headers=auth("k-collector-nobody")).status_code == 403
        assert c.get("/v1/connections", headers=auth("k-collector-viewer")).status_code == 200
        assert c.put("/v1/connections/x", json={}, headers=auth("k-collector-runner")).status_code == 403
        assert c.post("/v1/connections/x/test", headers=auth("k-collector-viewer")).status_code == 403
