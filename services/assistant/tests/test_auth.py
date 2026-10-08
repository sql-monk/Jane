"""ADR-0005 in the assistant: a token with ``assistant:use`` for every operation (jane_kit.auth_scopes)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jane_assistant.app import build_app
from jane_assistant.clients import Neighbours
from jane_assistant.settings import Settings
from jane_kit.auth import SecretRefError, sha256_hex
from jane_kit.clients import ClientLimits

KEYS = [
    {"name": "admin", "sha256": sha256_hex("k-assistant-admin"), "scopes": ["assistant:use"]},
    {"name": "viewer", "sha256": sha256_hex("k-assistant-viewer"), "scopes": ["orchestrator:read"]},
]


def auth(token: str, **extra: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", **extra}


def test_assistant_needs_a_token_with_assistant_use() -> None:
    with TestClient(build_app(Settings(log_format="console", auth_mode="api_key", api_keys=KEYS))) as c:
        assert c.get("/v1/health").status_code == 200
        assert c.get("/v1/info").status_code == 401
        assert c.get("/v1/info", headers=auth("k-assistant-viewer")).json()["auth_mode"] == "api_key"
        body = {"source": {"kind": "web", "url": "https://shop.example.test/"}}
        missing = c.post("/v1/onboarding-sessions", json=body, headers={"Idempotency-Key": "o-1"})
        assert missing.status_code == 401 and missing.json()["code"] == "unauthenticated"
        denied = c.post(
            "/v1/onboarding-sessions",
            json=body,
            headers=auth("k-assistant-viewer", **{"Idempotency-Key": "o-2"}),
        )
        assert denied.status_code == 403 and denied.json()["detail"] == "scope assistant:use required"
        assert c.get("/v1/onboarding-sessions/ses_x", headers=auth("k-assistant-admin")).status_code == 404
        assert c.get("/v1/jobs/job_x", headers=auth("k-assistant-viewer")).status_code == 403
        assert c.get("/v1/jobs/job_x", headers=auth("k-assistant-admin")).status_code == 404


async def test_each_neighbour_gets_its_own_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_TEST_ASSISTANT_TOKEN", "own")
    monkeypatch.setenv("JANE_TEST_ASSISTANT_REGISTRY_TOKEN", "for-registry")
    s = Settings(
        llm_url="http://llm:8110",
        registry_url="http://registry:8000",
        storage_url="http://storage:8000",
        service_token_ref="env:JANE_TEST_ASSISTANT_TOKEN",
        registry_token_ref="env:JANE_TEST_ASSISTANT_REGISTRY_TOKEN",
    )
    nb = Neighbours.from_settings(s, ClientLimits())
    try:
        assert nb.registry.c._client.headers["authorization"] == "Bearer for-registry"
        assert nb.llm.c._client.headers["authorization"] == "Bearer own"
        assert nb.storage.c._client.headers["authorization"] == "Bearer own"
    finally:
        await nb.aclose()
    with pytest.raises(SecretRefError, match="JANE_TEST_ASSISTANT_UNSET"):
        Neighbours.from_settings(
            s.with_overrides(llm_token_ref="env:JANE_TEST_ASSISTANT_UNSET"), ClientLimits()
        )
