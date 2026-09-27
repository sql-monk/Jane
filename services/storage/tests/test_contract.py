"""Contract tests: every response of the real service against handler.v1 and storage.v1 (WP-00)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from jane_kit.contracts import ContractClient, OpenAPISpec, contracts_dir
from jane_storage.packages import PackageCatalog

pytestmark = pytest.mark.contract

CONTRACTS = contracts_dir(Path(__file__).parent)


def spec(name: str) -> OpenAPISpec:
    if CONTRACTS is None or not (CONTRACTS / "openapi" / name).is_file():
        pytest.skip(f"contracts/openapi/{name} not available")
    return OpenAPISpec.load(CONTRACTS / "openapi" / name)


def test_handler_api_matches_contract(client: TestClient, h: SimpleNamespace, tmp_path: Path) -> None:
    api = ContractClient(spec("handler.v1.yaml"), client)
    api.get("/v1/health")
    api.get("/v1/info")
    body = h.invocation(
        [{"kind": "material", "material": h.material()}, {"kind": "entities", "entities": [h.entity()]}],
        "c-dk-1",
    )
    first = api.post("/v1/invocations", json=body, headers={"Idempotency-Key": "c-dk-1"})
    assert first.status_code == 200
    dup = api.post("/v1/invocations", json=body, headers={"Idempotency-Key": "c-dk-1"})
    assert dup.json()["duplicate"] is True
    api.get(f"/v1/invocations/{first.json()['invocation_id']}")
    api.get("/v1/invocations/inv_unknown")
    stale = h.invocation(
        [
            {
                "kind": "entities",
                "entities": [h.entity(fields={"price": 1.0}, at="2020-01-01T00:00:00Z", obs="o0")],
            }
        ],
        "c-dk-stale",
    )
    assert (
        api.post("/v1/invocations", json=stale, headers={"Idempotency-Key": "c-dk-stale"}).json()["output"][
            "writes"
        ][0]["status"]
        == "stale"
    )
    failed = h.invocation([{"kind": "entities", "entities": [h.entity()]}], "c-dk-f", target="broken-files")
    assert (
        api.post("/v1/invocations", json=failed, headers={"Idempotency-Key": "c-dk-f"}).json()["status"]
        == "failed"
    )
    missing = {**body, "handler": {"package_id": "jane.storage-files", "version": "9.9.9"}}
    assert api.post("/v1/invocations", json=missing, headers={"Idempotency-Key": "c-dk-1"}).status_code == 404
    digest = {**body, "handler": {**body["handler"], "digest": "sha256:" + "0" * 64}}
    assert api.post("/v1/invocations", json=digest, headers={"Idempotency-Key": "c-dk-1"}).status_code == 422
    job = api.post(
        "/v1/invocations",
        json={**body, "mode": "async", "delivery": {"delivery_key": "c-a"}},
        headers={"Idempotency-Key": "c-a"},
    )
    assert job.status_code == 202
    for _ in range(200):
        if api.get(f"/v1/jobs/{job.json()['job_id']}").json()["status"] == "succeeded":
            break
        time.sleep(0.02)
    api.post(f"/v1/jobs/{job.json()['job_id']}/cancel", json={"reason": "done already"})
    run = api.post(
        "/v1/test-runs",
        json={"handler": {"package_id": "jane.storage-files", "version": "1.0.0"}, "tests": "all"},
        headers={"Idempotency-Key": "c-tr"},
    )
    assert run.status_code == 202
    conn = {"connection_id": "c-files", "kind": "filesystem", "params": {"base_path": str(tmp_path / "c")}}
    assert api.put("/v1/connections/c-files", json=conn).status_code == 201
    assert api.put("/v1/connections/c-files", json=conn).status_code == 200
    api.get("/v1/connections")
    api.get("/v1/connections/c-files")
    api.post("/v1/connections/c-files/test")
    assert api.delete("/v1/connections/c-files").status_code == 204
    api.get("/v1/connections/c-files")
    assert api.uncovered() == []


def test_storage_read_api_matches_contract(client: TestClient, h: SimpleNamespace) -> None:
    api = ContractClient(spec("storage.v1.yaml"), client)
    result = h.post(
        client,
        h.invocation(
            [{"kind": "material", "material": h.material()}, {"kind": "entities", "entities": [h.entity()]}],
            "r-dk",
        ),
    ).json()
    object_id = result["output"]["writes"][0]["object"]["object_id"]
    key = 'shop-example|{"sku":"A-100"}'
    api.get("/v1/health")
    api.get("/v1/info")
    api.get("/v1/entities", params={"connection_id": "raw-files", "entity_type": "product"})
    api.get("/v1/entities", params={"connection_id": "raw-files", "entity_type": "product", "key": key})
    api.get("/v1/entities", params={"connection_id": "nope", "entity_type": "product"})
    api.get("/v1/entity-history", params={"connection_id": "raw-files", "entity_type": "product", "key": key})
    api.get(
        "/v1/entity-history", params={"connection_id": "raw-files", "entity_type": "product", "key": "x|{}"}
    )
    api.get("/v1/objects", params={"connection_id": "raw-files"})
    api.get(f"/v1/objects/{object_id}", params={"connection_id": "raw-files"})
    api.get("/v1/objects/obj_missing", params={"connection_id": "raw-files"})
    content = api.get(f"/v1/objects/{object_id}/content", params={"connection_id": "raw-files"})
    assert content.content == h.PAGE
    assert api.uncovered() == []


def test_storage_packages_match_manifest_schema() -> None:
    if CONTRACTS is None:
        pytest.skip("contracts not available")
    schemas = CONTRACTS / "schemas"
    resources = [
        (p.resolve().as_uri(), Resource.from_contents(json.loads(p.read_text(encoding="utf-8"))))
        for p in schemas.rglob("*.schema.json")
    ]
    registry: Registry = Registry().with_resources(resources)
    manifest_uri = (schemas / "package-manifest.schema.json").resolve().as_uri()
    validator = Draft202012Validator({"$ref": manifest_uri}, registry=registry)
    packages = PackageCatalog.discover().all()
    assert {p.package_id for p in packages} >= {"jane.storage-files", "jane.storage-postgresql"}
    for pkg in packages:
        errors = [e.message for e in validator.iter_errors(pkg.manifest)]
        assert errors == [], (pkg.package_id, errors)
        Draft202012Validator.check_schema(pkg.params_schema or {})
