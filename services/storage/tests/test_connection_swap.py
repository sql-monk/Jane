"""PUT /v1/connections while writes run (WP-19, found by WP-21 in e2e).

Before the fix every PUT closed the connection's adapter, also when the definition did not change, and a write in
progress failed with ``execution_error`` "adapter is not open" (``retryable: false``) - 2-6 of 15 writes when the
orchestrator re-synced its connections. Now an unchanged definition keeps the adapter and a changed one retires
it: new writes open a new adapter, writes in progress finish on the old one, which is closed afterwards.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from jane_storage.app import build_app
from jane_storage.settings import Settings


def connection(storage_dir: Path, **labels: str) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "connection_id": "raw-files",
        "kind": "filesystem",
        "params": {"base_path": str(storage_dir)},
    }
    if labels:
        doc["labels"] = labels
    return doc


def test_unchanged_put_keeps_the_open_adapter(
    settings: Settings, storage_dir: Path, h: SimpleNamespace
) -> None:
    with TestClient(build_app(settings)) as client:
        material = {"kind": "material", "material": h.material()}
        assert h.post(client, h.invocation([material], "keep-1")).json()["status"] == "success"
        pool = client.app.state.pool  # type: ignore[attr-defined]
        before = list(pool._open.values())
        body = json.loads(client.get("/v1/connections/raw-files").content)
        assert client.put("/v1/connections/raw-files", json=body).status_code == 200
        assert list(pool._open.values()) == before  # the same adapter object, not reopened
        assert client.put("/v1/connections/raw-files", json={**body, "labels": {"v": "2"}}).status_code == 200
        assert pool._open == {}  # a changed definition retires it (nobody held it: closed at once)


def test_puts_during_writes_do_not_fail_them(
    settings: Settings, storage_dir: Path, h: SimpleNamespace
) -> None:
    """Every write runs next to a PUT of a changed definition of its connection: none of them fails."""
    with TestClient(build_app(settings)) as client:
        results: list[dict[str, Any]] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def write(n: int) -> None:
            try:
                material = h.material(observation_id=f"obs_swap{n:04d}", material_id=f"web:swap{n:04d}")
                body = h.invocation([{"kind": "material", "material": material}], f"swap-{n}")
                result = h.post(client, body).json()
                with lock:
                    results.append(result)
            except BaseException as exc:  # pragma: no cover - reported below
                with lock:
                    errors.append(exc)

        def put(n: int) -> None:
            response = client.put("/v1/connections/raw-files", json=connection(storage_dir, round=str(n)))
            assert response.status_code in (200, 201), response.text

        for n in range(30):
            threads = [threading.Thread(target=write, args=(n,)), threading.Thread(target=put, args=(n,))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(60)
        assert errors == []
        failed = [r for r in results if r.get("status") != "success"]
        assert len(results) == 30 and failed == [], failed
        pool = client.app.state.pool  # type: ignore[attr-defined]
        assert pool._retired == {} and pool._users == {}  # every retired adapter was closed after its writes
        listed = client.get("/v1/objects", params={"connection_id": "raw-files", "limit": 100}).json()[
            "items"
        ]
        assert len(listed) == 30
