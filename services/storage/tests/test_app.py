"""The storage service over HTTP with the real filesystem adapter (no external services)."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import OpenAPISpec
from jane_storage.app import build_app
from jane_storage.packages import PackageCatalog, canonical_archive
from jane_storage.settings import Settings


def wait_job(client: TestClient, job_id: str) -> dict[str, Any]:
    deadline = time.monotonic() + 10
    job: dict[str, Any] = {}
    while time.monotonic() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            return job
        time.sleep(0.02)
    return job


def test_health_and_info(client: TestClient) -> None:
    assert client.get("/v1/health").json()["status"] == "ok"
    info = client.get("/v1/info").json()
    assert info["service"] == "storage"
    caps = info["capabilities"]
    assert {"filesystem", "postgresql"} <= set(caps["adapters"])
    assert {p["package_id"] for p in caps["packages"]} >= {"jane.storage-files", "jane.storage-postgresql"}
    assert info["limits"]["defaults"]["retries"]["max_attempts"] == 4
    assert info["limits"]["defaults"]["timeouts"]["sync_response_max_ms"] == 30000


def test_raw_html_is_stored_as_html_file(client: TestClient, h: SimpleNamespace, storage_dir: Path) -> None:
    r = h.post(client, h.invocation([{"kind": "material", "material": h.material()}], "dk-raw-1"))
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["status"] == "success"
    assert result["handler_kind"] == "storage"
    assert result["handler"]["digest"].startswith("sha256:")
    assert result["inputs"][0]["material_id"] == "web:3704326c60776c53169680099e2eed31"
    (ack,) = result["output"]["writes"]
    assert ack["status"] == "written"
    assert ack["target"] == {"adapter": "filesystem", "connection_id": "raw-files"}
    path = storage_dir / ack["object"]["locator"]["path"]
    assert path.suffix == ".html"
    assert path.read_bytes() == h.PAGE
    assert ack["object"]["locator"]["path"] == (
        "objects/shop-example/2026/09/27/web_3704326c60776c53169680099e2eed31/obs_01J9ZQ4A0000000000000001.html"
    )
    assert client.get(f"/v1/invocations/{result['invocation_id']}").json() == result


def test_format_override_json(client: TestClient, h: SimpleNamespace, storage_dir: Path) -> None:
    body = h.invocation(
        [{"kind": "material", "material": h.material()}], "dk-raw-json", params={"format": {"raw": "json"}}
    )
    ack = h.post(client, body).json()["output"]["writes"][0]
    path = storage_dir / ack["object"]["locator"]["path"]
    assert path.suffix == ".json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["content"]["data"] == h.PAGE.decode()
    assert doc["material_id"] == "web:3704326c60776c53169680099e2eed31"


def test_redelivery_is_duplicate_and_attempt_does_not_matter(client: TestClient, h: SimpleNamespace) -> None:
    body = h.invocation([{"kind": "entities", "entities": [h.entity(), h.entity("B-2")]}], "dk-ent-1")
    first = h.post(client, body).json()
    assert [w["status"] for w in first["output"]["writes"]] == ["written", "written"]
    assert first["duplicate"] is False
    retry = {**body, "context": {"attempt": 2}}
    r = h.post(client, retry)
    assert r.status_code == 200
    assert r.headers["Idempotency-Replayed"] == "true"
    again = r.json()
    assert again["duplicate"] is True
    assert [w["status"] for w in again["output"]["writes"]] == ["duplicate", "duplicate"]
    assert again["output"]["writes"][0]["entity"] == first["output"]["writes"][0]["entity"]
    history = client.get(
        "/v1/entity-history",
        params={
            "connection_id": "raw-files",
            "entity_type": "product",
            "key": 'shop-example|{"sku":"A-100"}',
        },
    ).json()
    assert len(history["items"]) == 1


def test_redelivery_after_restart_is_duplicate(settings: Settings, h: SimpleNamespace) -> None:
    body = h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-restart")
    with TestClient(build_app(settings)) as c:
        assert h.post(c, body).json()["output"]["writes"][0]["status"] == "written"
    with TestClient(build_app(settings)) as c:  # new process: nothing in memory
        again = h.post(c, body)
        assert "Idempotency-Replayed" not in again.headers
        assert again.json()["duplicate"] is True


def test_same_key_other_body_is_rejected(client: TestClient, h: SimpleNamespace) -> None:
    h.post(client, h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-reuse"))
    r = h.post(client, h.invocation([{"kind": "entities", "entities": [h.entity("Z-9")]}], "dk-reuse"))
    assert r.status_code == 422
    assert r.json()["code"] == "idempotency_key_reused"


def test_new_observation_partial_clear_and_stale(client: TestClient, h: SimpleNamespace) -> None:
    h.post(
        client, h.invocation([{"kind": "entities", "entities": [h.entity(at="2026-09-27T10:00:00Z")]}], "o1")
    )
    price = h.entity(fields={"price": 999.0}, at="2026-09-27T12:00:00Z", obs="obs_2")
    assert h.post(client, h.invocation([{"kind": "entities", "entities": [price]}], "o2")).json()["output"][
        "writes"
    ][0]["status"] == ("written")
    clear = {**h.entity(fields={}, at="2026-09-27T13:00:00Z", obs="obs_3"), "cleared": ["title"]}
    h.post(client, h.invocation([{"kind": "entities", "entities": [clear]}], "o3"))
    late = h.entity(fields={"price": 1.0, "title": "late"}, at="2026-09-27T11:00:00Z", obs="obs_0")
    ack = h.post(client, h.invocation([{"kind": "entities", "entities": [late]}], "o4")).json()["output"][
        "writes"
    ][0]
    assert ack["status"] == "stale"
    state = client.get(
        "/v1/entities",
        params={
            "connection_id": "raw-files",
            "entity_type": "product",
            "key": 'shop-example|{"sku":"A-100"}',
        },
    ).json()["items"][0]
    assert state["fields"] == {"sku": "A-100", "price": 999.0}
    assert state["cleared_fields"] == ["title"]
    assert state["version"] == 4


def test_test_mode_writes_nothing(client: TestClient, h: SimpleNamespace, storage_dir: Path) -> None:
    body = h.invocation(
        [{"kind": "entities", "entities": [h.entity()]}, {"kind": "material", "material": h.material()}],
        "dk-test",
        context={"test_mode": True},
    )
    result = h.post(client, body).json()
    assert result["test_mode"] is True
    assert {w["status"] for w in result["output"]["writes"]} == {"simulated"}
    assert not (storage_dir / "entities").exists()


def test_unavailable_storage_is_failed_result(client: TestClient, h: SimpleNamespace) -> None:
    result = h.post(
        client,
        h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-down", target="broken-files"),
    ).json()
    assert result["status"] == "failed"
    assert result["failure"]["kind"] == "connection_error"
    assert result["failure"]["retryable"] is True


@pytest.mark.parametrize(
    ("mutate", "status", "code"),
    [
        (
            lambda b: b.update(handler={"package_id": "jane.storage-files", "version": "9.9.9"}),
            404,
            "not_found",
        ),
        (lambda b: b["handler"].update(digest="sha256:" + "0" * 64), 422, "digest_mismatch"),
        (lambda b: b.update(connections={"target": "nope"}), 404, "not_found"),
        (lambda b: b.update(params={"unknown": 1}), 422, "validation_failed"),
        (lambda b: b.update(inputs=[{"kind": "data", "data": {}}]), 422, "validation_failed"),
        (lambda b: b["inputs"][0]["entities"][0]["fields"].update(price=None), 422, "validation_failed"),
        (lambda b: b.pop("connections"), 422, "validation_failed"),
    ],
)
def test_invalid_invocations(
    client: TestClient, h: SimpleNamespace, mutate: Any, status: int, code: str
) -> None:
    body = h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-bad")
    mutate(body)
    r = h.post(client, body)
    assert r.status_code == status, r.text
    assert r.json()["code"] == code


def test_idempotency_key_must_equal_delivery_key(client: TestClient, h: SimpleNamespace) -> None:
    body = h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-1")
    r = client.post("/v1/invocations", json=body, headers={"Idempotency-Key": "other"})
    assert r.status_code == 422
    assert client.post("/v1/invocations", json=body).status_code == 422


def test_body_limit_and_async_mode(
    settings: Settings, h: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_STORAGE_LIMITS__TRANSFER__MAX_REQUEST_BODY_BYTES", "2000")
    with TestClient(build_app(settings)) as c:
        big = h.invocation(
            [{"kind": "material", "material": h.material(b"<html>" + b"x" * 4000 + b"</html>")}], "k"
        )
        assert h.post(c, big).status_code == 413
        body = h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-async", mode="async")
        r = h.post(c, body)
        assert r.status_code == 202
        job = wait_job(c, r.json()["job_id"])
        assert job["status"] == "succeeded"
        assert job["result"]["output"]["writes"][0]["status"] == "written"


def test_request_limits_apply_within_hard_caps(
    settings: Settings, h: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_STORAGE_LIMITS__HARD_CAPS__RETRIES__MAX_ATTEMPTS", "3")
    with TestClient(build_app(settings)) as c:
        body = h.invocation(
            [{"kind": "entities", "entities": [h.entity()]}],
            "dk-lim",
            limits={"retries": {"max_attempts": 50}},
        )
        assert h.post(c, body).status_code == 200


def test_reads_objects_and_content_range(client: TestClient, h: SimpleNamespace) -> None:
    ack = h.post(client, h.invocation([{"kind": "material", "material": h.material()}], "dk-read")).json()[
        "output"
    ]["writes"][0]
    object_id = ack["object"]["object_id"]
    page = client.get(
        "/v1/objects", params={"connection_id": "raw-files", "source_id": "shop-example"}
    ).json()
    assert [i["object"]["object_id"] for i in page["items"]] == [object_id]
    assert page["items"][0]["material"]["url"] == "https://shop.example.test/product/a-100"
    detail = client.get(f"/v1/objects/{object_id}", params={"connection_id": "raw-files"}).json()
    assert detail["material"]["content"]["kind"] == "blob"
    assert detail["material"]["content"]["uri"].startswith("file://")
    assert detail["material"]["format"]["media_type"] == "text/html"
    full = client.get(f"/v1/objects/{object_id}/content", params={"connection_id": "raw-files"})
    assert full.content == h.PAGE
    assert full.headers["content-type"].startswith("text/html")
    part = client.get(
        f"/v1/objects/{object_id}/content",
        params={"connection_id": "raw-files"},
        headers={"Range": "bytes=0-8"},
    )
    assert part.status_code == 206
    assert part.content == h.PAGE[:9]
    assert client.get("/v1/objects/obj_none", params={"connection_id": "raw-files"}).status_code == 404
    assert client.get("/v1/objects", params={"connection_id": "unknown"}).status_code == 404


def test_entities_pagination_over_http(client: TestClient, h: SimpleNamespace) -> None:
    entities = [h.entity(f"S-{i}") for i in range(5)]
    h.post(client, h.invocation([{"kind": "entities", "entities": entities}], "dk-pages"))
    seen: list[str] = []
    cursor = None
    while True:
        params: dict[str, Any] = {"connection_id": "raw-files", "entity_type": "product", "limit": 2}
        if cursor:
            params["cursor"] = cursor
        page = client.get("/v1/entities", params=params).json()
        seen += [i["canonical_key"] for i in page["items"]]
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert len(seen) == len(set(seen)) == 5


def test_connections_api(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = {
        "connection_id": "results-files",
        "kind": "filesystem",
        "params": {"base_path": str(tmp_path / "r")},
        "secret_refs": {"token": "env:WP07_TEST_TOKEN"},
    }
    created = client.put("/v1/connections/results-files", json=body)
    assert created.status_code == 201
    etag = created.headers["ETag"]
    assert client.get("/v1/connections/results-files").json() == body
    stale = client.put("/v1/connections/results-files", json=body, headers={"If-Match": '"nope"'})
    assert stale.status_code == 412
    assert (
        client.put("/v1/connections/results-files", json=body, headers={"If-Match": etag}).status_code == 200
    )
    missing = client.post("/v1/connections/results-files/test").json()
    assert missing == {**missing, "ok": False, "secrets_resolved": {"token": False}}
    monkeypatch.setenv("WP07_TEST_TOKEN", "x")
    assert client.post("/v1/connections/results-files/test").json()["ok"] is True
    leaked = {**body, "params": {"base_path": "/x", "password": "hunter2"}}
    r = client.put("/v1/connections/results-files", json=leaked)
    assert r.status_code == 422
    assert r.json()["code"] == "secret_detected"
    ids = [c["connection_id"] for c in client.get("/v1/connections").json()["items"]]
    assert ids == ["broken-files", "raw-files", "results-files"]
    assert client.delete("/v1/connections/results-files").status_code == 204
    assert client.get("/v1/connections/results-files").status_code == 404


def test_test_run_of_package_tests(client: TestClient, storage_dir: Path) -> None:
    r = client.post(
        "/v1/test-runs",
        json={"handler": {"package_id": "jane.storage-files", "version": "1.0.0"}, "tests": "all"},
        headers={"Idempotency-Key": "tr-1"},
    )
    assert r.status_code == 202
    job = wait_job(client, r.json()["job_id"])
    report = job["result"]
    assert report["failed"] == 0
    assert report["passed"] == 2
    assert not (storage_dir / "entities").exists()


def test_package_archive_with_data_writes(client: TestClient, h: SimpleNamespace, storage_dir: Path) -> None:
    files_pkg = next(p for p in PackageCatalog.discover().all() if p.package_id == "jane.storage-files")
    manifest = {
        **files_pkg.manifest,
        "package_id": "local.llm-results",
        "entry": {**files_pkg.entry, "writes": "data"},
        "input": {"accepts": ["data"]},
        "tests": [],
    }
    files = [(p, d) for p, d in files_pkg.files if p != "jane-package.json"]
    archive = canonical_archive([*files, ("jane-package.json", json.dumps(manifest).encode())])
    body = h.invocation(
        [{"kind": "data", "data": {"events": [{"title": "Подія"}]}}],
        "dk-data",
        package="local.llm-results",
        package_archive={
            "kind": "inline",
            "media_type": "application/zip",
            "encoding": "base64",
            "data": base64.b64encode(archive).decode(),
        },
    )
    body["handler"]["digest"] = "sha256:" + hashlib.sha256(archive).hexdigest()
    result = h.post(client, body).json()
    assert result["status"] == "success", result
    path = storage_dir / result["output"]["writes"][0]["object"]["locator"]["path"]
    assert json.loads(path.read_text(encoding="utf-8")) == {"events": [{"title": "Подія"}]}
    assert zipfile.ZipFile(io.BytesIO(archive)).namelist()[0] == "jane-package.json"


def test_metrics_count_writes(client: TestClient, h: SimpleNamespace) -> None:
    h.post(client, h.invocation([{"kind": "entities", "entities": [h.entity()]}], "dk-m"))
    body = client.get("/metrics").text
    assert 'jane_storage_writes_total{adapter="filesystem",status="written"} 1.0' in body


def test_default_raw_format_non_html_is_json_material(
    client: TestClient, h: SimpleNamespace, storage_dir: Path
) -> None:
    """TZ §5: without format.raw, RAW that is not a web page is stored as a JSON document of the Material."""
    contracts = Path(__file__).resolve().parents[3] / "contracts"
    material = json.loads(
        (contracts / "examples" / "schemas" / "material" / "telegram-message-edit.json").read_text(
            encoding="utf-8"
        )
    )
    result = h.post(client, h.invocation([{"kind": "material", "material": material}], "dk-tg")).json()
    assert result["status"] == "success", result
    obj = result["output"]["writes"][0]["object"]
    assert obj["media_type"] == "application/json"
    path = storage_dir / obj["locator"]["path"]
    assert path.suffix == ".json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["content"]["data"] == material["content"]["data"]
    assert doc["content"]["encoding"] == "utf-8"
    assert {k: v for k, v in doc.items() if k != "content"} == {
        k: v for k, v in material.items() if k != "content"
    }
    spec = OpenAPISpec.load(contracts / "openapi" / "handler.v1.yaml")
    spec.validate_at((contracts / "schemas" / "material.schema.json").resolve().as_uri(), doc, "Material")
    # an explicit override still wins
    body = h.invocation(
        [{"kind": "material", "material": material}], "dk-tg-orig", params={"format": {"raw": "original"}}
    )
    raw = h.post(client, body).json()["output"]["writes"][0]["object"]
    assert raw["locator"]["path"].endswith(".txt")


def test_history_false_package_is_rejected(client: TestClient, h: SimpleNamespace) -> None:
    files_pkg = next(p for p in PackageCatalog.discover().all() if p.package_id == "jane.storage-files")
    manifest = {
        **files_pkg.manifest,
        "package_id": "local.no-history",
        "entry": {**files_pkg.entry, "history": False},
    }
    files = [(p, d) for p, d in files_pkg.files if p != "jane-package.json"]
    archive = canonical_archive([*files, ("jane-package.json", json.dumps(manifest).encode())])
    body = h.invocation(
        [{"kind": "entities", "entities": [h.entity()]}],
        "dk-nohist",
        package="local.no-history",
        package_archive={
            "kind": "inline",
            "media_type": "application/zip",
            "encoding": "base64",
            "data": base64.b64encode(archive).decode(),
        },
    )
    r = h.post(client, body)
    assert r.status_code == 422
    assert "history" in r.text
