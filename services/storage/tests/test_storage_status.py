"""Status snapshots over the real filesystem adapter."""

import time
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from jane_kit.contracts import OpenAPISpec


def inventory(client: TestClient, connection_id: str = "raw-files") -> dict:
    response = client.post(
        "/v1/storage-status/checks",
        json={"connection_id": connection_id},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 202, response.text
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        job = client.get(response.headers["Location"]).json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            assert job["status"] == "succeeded", job
            return job["result"]
        time.sleep(0.01)
    raise AssertionError("status job did not complete")


def test_status_unknown_then_inventory(client: TestClient, h: SimpleNamespace) -> None:
    url = "/v1/storage-status?connection_id=raw-files"
    before = client.get(url).json()
    assert before["availability"] == "unknown"
    assert before["statistics"]["object_count"] is None
    assert inventory(client)["availability"] == "available"
    empty = client.get(url).json()
    assert empty["statistics"]["object_count"] == 0
    assert empty["statistics"]["total_size_bytes"] == 0
    result = h.post(client, h.invocation([{"kind": "material", "material": h.material()}], "status-raw"))
    assert result.json()["status"] == "success"
    # A render does not rescan the backend: only an explicit test refreshes metadata counts.
    assert client.get(url).json() == empty
    assert inventory(client)["availability"] == "available"
    snapshot = client.get(url).json()
    assert snapshot["availability"] == "available"
    assert snapshot["checked_at"] is not None
    assert snapshot["statistics"]["object_count"] == 1
    assert snapshot["statistics"]["total_size_bytes"] == len(h.PAGE)
    assert snapshot["statistics"]["unavailable_reason"] is None
    OpenAPISpec.load(
        Path(__file__).resolve().parents[3] / "contracts/openapi/storage.v1.yaml"
    ).validate_response("GET", "/v1/storage-status", 200, snapshot)


def test_snapshot_invalidates_on_put_and_delete(client: TestClient) -> None:
    url = "/v1/storage-status?connection_id=raw-files"
    assert client.post("/v1/connections/raw-files/test").json()["ok"]
    doc = client.get("/v1/connections/raw-files").json()
    doc["title"] = "Updated definition"
    assert client.put("/v1/connections/raw-files", json=doc).status_code == 200
    assert client.get(url).json()["availability"] == "unknown"
    assert client.delete("/v1/connections/raw-files").status_code == 204
    assert client.get(url).status_code == 404
    assert client.put("/v1/connections/raw-files", json=doc).status_code == 201
    assert client.get(url).json()["statistics"]["object_count"] is None


def test_failure_is_visible_and_does_not_hide_other_connections(client: TestClient) -> None:
    doc = {"connection_id": "bad-files", "kind": "filesystem", "params": {}}
    assert client.put("/v1/connections/bad-files", json=doc).status_code == 201
    assert inventory(client, "bad-files")["availability"] == "unavailable"
    snapshot = client.get("/v1/storage-status?connection_id=bad-files").json()
    assert snapshot["availability"] == "unavailable"
    assert snapshot["statistics"]["object_count"] is None
    assert snapshot["statistics"]["unavailable_reason"] == "check_failed"
    assert inventory(client)["availability"] == "available"
    assert client.get("/v1/storage-status?connection_id=raw-files").json()["availability"] == "available"


def test_failed_fresh_inventory_replaces_success(
    client: TestClient, h: SimpleNamespace, storage_dir: Path
) -> None:
    result = h.post(client, h.invocation([{"kind": "material", "material": h.material()}], "status-broken"))
    assert result.json()["status"] == "success"
    assert inventory(client)["availability"] == "available"
    # Broken stored metadata must not become an invented zero count.
    payload = storage_dir / result.json()["output"]["writes"][0]["object"]["locator"]["path"]
    payload.with_name(payload.name + ".meta.json").unlink()
    assert inventory(client)["availability"] == "available"
    state = client.get("/v1/storage-status?connection_id=raw-files").json()
    assert state["availability"] == "available"
    assert state["statistics"]["object_count"] is None

    assert state["statistics"]["unavailable_reason"] == "statistics_check_failed"
    # The original endpoint remains a health check even with damaged inventory.
    assert client.post("/v1/connections/raw-files/test").json()["ok"] is True


def test_idempotent_status_jobs_and_unknown_connection(client: TestClient) -> None:
    body = {"connection_id": "raw-files"}
    headers = {"Idempotency-Key": "status-replay"}
    first = client.post("/v1/storage-status/checks", json=body, headers=headers)
    assert first.status_code == 202
    again = client.post("/v1/storage-status/checks", json=body, headers=headers)
    assert again.status_code == 202
    assert again.json()["job_id"] == first.json()["job_id"]
    assert again.headers["Idempotency-Replayed"] == "true"
    changed = client.post(
        "/v1/storage-status/checks", json={"connection_id": "broken-files"}, headers=headers
    )
    assert changed.status_code == 422
    assert changed.json()["code"] == "idempotency_key_reused"
    assert (
        client.post(
            "/v1/storage-status/checks", json={"connection_id": "unknown"}, headers=headers
        ).status_code
        == 404
    )
    assert client.post("/v1/storage-status/checks", json=body).status_code == 422


def test_slow_inventory_is_background(settings, monkeypatch, tmp_path: Path) -> None:
    import asyncio
    import json
    import threading

    from jane_storage.app import build_app
    from jane_storage_files import FilesystemAdapter

    original = FilesystemAdapter.object_statistics
    entered = threading.Event()
    release = asyncio.Event()

    async def delayed_real_inventory(self):
        # Gate only execution time; after release run the actual filesystem inventory.
        entered.set()
        await release.wait()
        return await original(self)

    monkeypatch.setattr(FilesystemAdapter, "object_statistics", delayed_real_inventory)
    limits_file = tmp_path / "status-limits.json"
    limits_file.write_text(
        json.dumps({"defaults": {"timeouts": {"sync_response_max_ms": 1, "request_timeout_ms": 5000}}}),
        encoding="utf-8",
    )
    settings = settings.with_overrides(limits_file=limits_file)
    with TestClient(build_app(settings)) as client:
        actual = client.get("/v1/info").json()["limits"]["defaults"]["timeouts"]
        assert actual["sync_response_max_ms"] == 1
        assert actual["request_timeout_ms"] == 5000
        try:
            response = client.post(
                "/v1/storage-status/checks",
                json={"connection_id": "raw-files"},
                headers={"Idempotency-Key": "slow-status"},
            )
            assert response.status_code == 202
            job_id = response.json()["job_id"]
            location = response.headers["Location"]
            assert entered.wait(timeout=1), "original submitted job did not start inventory"
            # HTTP acceptance arrived while the actual inventory remains blocked at its gate.
            pending = client.get(location).json()
            assert pending["job_id"] == job_id
            assert pending["status"] == "running"
            assert pending.get("result") is None
            assert not release.is_set()
            # Existing synchronous connection health check is independent of the gated inventory.
            assert client.post("/v1/connections/raw-files/test").json()["ok"] is True
        finally:
            client.portal.call(release.set)
        deadline = time.monotonic() + actual["request_timeout_ms"] / 1000
        while time.monotonic() < deadline:
            completed = client.get(location).json()
            assert completed["job_id"] == job_id
            if completed["status"] in {"succeeded", "failed", "cancelled"}:
                break
            time.sleep(0.01)
        assert completed["status"] == "succeeded", completed
        assert completed["result"]["statistics"]["object_count"] == 0
