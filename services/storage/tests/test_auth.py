"""ADR-0005 in storage: a token for every operation, the scope of handler.v1 + storage.v1 (jane_kit.auth_scopes)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from jane_kit.auth import sha256_hex
from jane_storage.app import build_app
from jane_storage.settings import Settings

KEYS = [
    {"name": "reader", "sha256": sha256_hex("k-storage-reader"), "scopes": ["storage:read"]},
    {
        "name": "orchestrator",
        "sha256": sha256_hex("k-storage-orchestrator"),
        "scopes": ["handler:invoke", "connections:write", "storage:read"],
    },
    {"name": "nobody", "sha256": sha256_hex("k-storage-nobody"), "scopes": []},
]


def auth(token: str, **extra: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", **extra}


def test_storage_needs_a_token_and_the_operation_scope(settings: Settings, h: SimpleNamespace) -> None:
    s = settings.with_overrides(auth_mode="api_key", api_keys=KEYS)
    with TestClient(build_app(s)) as c:
        assert c.get("/v1/health").status_code == 200
        info = c.get("/v1/info")
        assert info.status_code == 401 and info.json()["code"] == "unauthenticated"
        assert c.get("/v1/info", headers=auth("k-storage-nobody")).json()["auth_mode"] == "api_key"

        body: dict[str, Any] = h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-auth")
        idem = {"Idempotency-Key": "dk-auth"}
        assert c.post("/v1/invocations", json=body, headers=idem).status_code == 401
        denied = c.post("/v1/invocations", json=body, headers=auth("k-storage-reader", **idem))
        assert denied.status_code == 403 and denied.json()["code"] == "forbidden"
        assert "handler:invoke" in denied.json()["detail"]
        ok = c.post("/v1/invocations", json=body, headers=auth("k-storage-orchestrator", **idem))
        assert ok.status_code == 200 and ok.json()["status"] == "success"

        params = {"connection_id": "raw-files"}
        assert c.get("/v1/objects", params=params).status_code == 401
        assert c.get("/v1/objects", params=params, headers=auth("k-storage-nobody")).status_code == 403
        assert c.get("/v1/objects", params=params, headers=auth("k-storage-reader")).status_code == 200

        conn = {"connection_id": "raw-x", "kind": "filesystem", "params": {"base_path": "/tmp/x"}}
        put = c.put("/v1/connections/raw-x", json=conn, headers=auth("k-storage-reader"))
        assert put.status_code == 403
        assert c.get("/v1/connections", headers=auth("k-storage-reader")).status_code == 403
        assert c.get("/v1/connections", headers=auth("k-storage-orchestrator")).status_code == 200
        assert c.get("/v1/jobs/job_unknown", headers=auth("k-storage-reader")).status_code == 403
