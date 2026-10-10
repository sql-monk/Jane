"""Status snapshots over the real filesystem adapter."""

from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from jane_kit.contracts import OpenAPISpec


def test_status_unknown_then_inventory(client: TestClient, h: SimpleNamespace) -> None:
    url = "/v1/storage-status?connection_id=raw-files"
    before = client.get(url).json()
    assert before["availability"] == "unknown"
    assert before["statistics"]["object_count"] is None
    assert client.post("/v1/connections/raw-files/test").json()["ok"] is True
    empty = client.get(url).json()
    assert empty["statistics"]["object_count"] == 0
    assert empty["statistics"]["total_size_bytes"] == 0
    result = h.post(client, h.invocation([{"kind": "material", "material": h.material()}], "status-raw"))
    assert result.json()["status"] == "success"
    # A render does not rescan the backend: only an explicit test refreshes metadata counts.
    assert client.get(url).json() == empty
    assert client.post("/v1/connections/raw-files/test").json()["ok"] is True
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
    assert client.post("/v1/connections/bad-files/test").json()["ok"] is False
    snapshot = client.get("/v1/storage-status?connection_id=bad-files").json()
    assert snapshot["availability"] == "unavailable"
    assert snapshot["statistics"]["object_count"] is None
    assert snapshot["statistics"]["unavailable_reason"] == "check_failed"
    assert client.post("/v1/connections/raw-files/test").json()["ok"] is True
    assert client.get("/v1/storage-status?connection_id=raw-files").json()["availability"] == "available"


def test_failed_fresh_inventory_replaces_success(
    client: TestClient, h: SimpleNamespace, storage_dir: Path
) -> None:
    result = h.post(client, h.invocation([{"kind": "material", "material": h.material()}], "status-broken"))
    assert result.json()["status"] == "success"
    assert client.post("/v1/connections/raw-files/test").json()["ok"] is True
    # Broken stored metadata must not become an invented zero count.
    payload = storage_dir / result.json()["output"]["writes"][0]["object"]["locator"]["path"]
    payload.with_name(payload.name + ".meta.json").unlink()
    assert client.post("/v1/connections/raw-files/test").json()["ok"] is False
    state = client.get("/v1/storage-status?connection_id=raw-files").json()
    assert state["availability"] == "unavailable"
    assert state["statistics"]["object_count"] is None
