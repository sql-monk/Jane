"""ADR-0005 in the LLM gateway: a token for every operation, llm.v1 + handler.v1 scopes (jane_kit.auth_scopes)."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient

from jane_kit.auth import sha256_hex

KEYS = [
    {"name": "assistant", "sha256": sha256_hex("k-llm-assistant"), "scopes": ["llm:invoke"]},
    {"name": "admin", "sha256": sha256_hex("k-llm-admin"), "scopes": ["llm:admin"]},
    {"name": "nobody", "sha256": sha256_hex("k-llm-nobody"), "scopes": []},
]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_llm_needs_a_token_and_the_operation_scope(make_client: Callable[..., TestClient]) -> None:
    c = make_client(settings={"auth_mode": "api_key", "api_keys": KEYS})
    assert c.get("/v1/health").status_code == 200
    assert c.get("/v1/info").status_code == 401
    assert c.get("/v1/info", headers=auth("k-llm-nobody")).json()["auth_mode"] == "api_key"

    missing = c.post("/v1/completions", json={}, headers={"Idempotency-Key": "c-1"})
    assert missing.status_code == 401 and missing.json()["code"] == "unauthenticated"
    denied = c.post("/v1/completions", json={}, headers={**auth("k-llm-admin"), "Idempotency-Key": "c-2"})
    assert denied.status_code == 403 and denied.json()["detail"] == "scope llm:invoke required"
    assert c.get("/v1/providers", headers=auth("k-llm-assistant")).status_code == 200
    assert c.get("/v1/providers", headers=auth("k-llm-nobody")).status_code == 403
    assert c.get("/v1/budgets", headers=auth("k-llm-assistant")).status_code == 403
    assert c.get("/v1/budgets", headers=auth("k-llm-admin")).status_code == 200
    assert c.put("/v1/providers/x", json={}, headers=auth("k-llm-assistant")).status_code == 403
    assert c.post("/v1/invocations", json={}, headers=auth("k-llm-assistant")).status_code == 403
    assert c.get("/v1/jobs/job_x", headers=auth("k-llm-assistant")).status_code == 404
