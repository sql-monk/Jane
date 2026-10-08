"""ADR-0005 in the orchestrator: jane-kit authentication, the scope table, and its own tokens for executors."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest

from jane_kit.auth import SecretRefError, sha256_hex
from jane_orchestrator.executors import Executors
from jane_orchestrator.settings import ExecutorConfig, Settings


def executor(name: str, **extra: Any) -> dict[str, Any]:
    return {"executor": name, "role": "handler", "base_url": f"http://{name}:8000", **extra}


def test_executor_tokens_come_from_secret_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("JANE_TEST_ORCH_TOKEN", "own-token")
    secret = tmp_path / "storage-token"
    secret.write_text("file-token\n", encoding="utf-8")
    settings = Settings(
        service_token_ref="env:JANE_TEST_ORCH_TOKEN",
        executors=[
            ExecutorConfig.model_validate(executor("runtime")),
            ExecutorConfig.model_validate(executor("storage", token_ref=f"file:{secret}")),
            ExecutorConfig.model_validate(executor("legacy", token="plain-token")),
        ],
    )
    with caplog.at_level(logging.WARNING):
        resolved = settings.all_executors()
        tokens = {e.executor: e.token.get_secret_value() for e in resolved if e.token}
        assert all("own-token" not in repr(e) for e in resolved)  # SecretStr: never in reprs or logs
    assert tokens == {"runtime": "own-token", "storage": "file-token", "legacy": "plain-token"}
    assert any("plain text" in r.getMessage() for r in caplog.records)
    assert all(e.token is None for e in settings.executor_configs() if e.executor != "legacy")
    clients = Executors(settings.all_executors(), connect_timeout_ms=1000, request_timeout_ms=1000)
    try:
        assert clients._client("runtime").headers["authorization"] == "Bearer own-token"
        assert clients._client("storage").headers["authorization"] == "Bearer file-token"
    finally:
        clients.close()


def test_unresolvable_or_double_tokens_are_refused() -> None:
    with pytest.raises(SecretRefError, match="JANE_TEST_ORCH_UNSET"):
        Settings(service_token_ref="env:JANE_TEST_ORCH_UNSET", executors=[executor("x")]).all_executors()
    with pytest.raises(ValueError, match="not both"):
        ExecutorConfig.model_validate(executor("x", token="a", token_ref="env:B"))


@pytest.mark.integration
def test_api_needs_a_token_and_the_operation_scope(make_client: Any) -> None:
    keys = [
        {"name": "viewer", "sha256": sha256_hex("k-orch-viewer"), "scopes": ["orchestrator:read"]},
        {"name": "admin", "sha256": sha256_hex("k-orch-admin"), "scopes": ["orchestrator:admin"]},
    ]
    c = make_client(auth_mode="api_key", api_keys=keys)
    viewer = {"Authorization": "Bearer k-orch-viewer"}
    admin = {"Authorization": "Bearer k-orch-admin"}
    assert c.get("/v1/health").status_code == 200
    assert c.get("/v1/info").status_code == 401
    assert c.get("/v1/info", headers=viewer).json()["auth_mode"] == "api_key"
    missing = c.get("/v1/sources")
    assert missing.status_code == 401 and missing.json()["code"] == "unauthenticated"
    assert c.get("/v1/sources", headers=viewer).status_code == 200
    denied = c.put("/v1/limits/platform", json={}, headers=viewer)
    assert denied.status_code == 403 and denied.json()["code"] == "forbidden"
    assert c.post("/v1/sources", json={}, headers={**viewer, "Idempotency-Key": "a-1"}).status_code == 403
    # admin implies read and write
    assert c.get("/v1/runs", headers=admin).status_code == 200
    created = c.post("/v1/sources", json={}, headers={**admin, "Idempotency-Key": "a-2"})
    assert created.status_code == 422  # authorized; the empty source is invalid
