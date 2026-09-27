from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient
from pydantic import BaseModel

from jane_kit.config import JaneSettings
from jane_kit.contracts import ContractClient, ContractViolation, OpenAPISpec, build_mock_app, find_specs
from jane_kit.errors import NotFound
from jane_kit.service import create_app

pytestmark = pytest.mark.contract

DATA = Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def spec() -> OpenAPISpec:
    return OpenAPISpec.load(DATA / "openapi.yaml")


def test_operations_and_lookup(spec: OpenAPISpec) -> None:
    ids = {o.operation_id for o in spec.operations}
    assert ids == {"createItem", "listItems", "getItem", "getJob"}
    assert spec.operation("GET", "/v1/items/abc").operation_id == "getItem"
    assert spec.operation("GET", "/v1/items?limit=1").operation_id == "listItems"
    with pytest.raises(ContractViolation, match="not described"):
        spec.operation("DELETE", "/v1/items/abc")


def test_response_validation(spec: OpenAPISpec) -> None:
    spec.validate_response("GET", "/v1/items/1", 200, {"id": "1", "name": "n", "tags": []})
    with pytest.raises(ContractViolation, match="'tags' is a required property"):
        spec.validate_response("GET", "/v1/items/1", 200, {"id": "1", "name": "n"})
    with pytest.raises(ContractViolation, match="status 500 is not documented"):
        spec.validate_response("GET", "/v1/items/1", 500, {})
    # $ref'd response object with problem+json content
    spec.validate_response(
        "GET",
        "/v1/items/1",
        404,
        {"type": "t", "title": "x", "status": 404, "code": "not_found"},
        "application/problem+json",
    )
    with pytest.raises(ContractViolation, match="content type"):
        spec.validate_response("GET", "/v1/items/1", 404, {}, "text/plain")


def test_cross_file_ref(spec: OpenAPISpec) -> None:
    spec.validate_response("GET", "/v1/jobs/j", 200, {"job_id": "j", "state": "running", "progress": None})
    with pytest.raises(ContractViolation):
        spec.validate_response("GET", "/v1/jobs/j", 200, {"job_id": "j", "state": "exploded"})


def test_request_validation(spec: OpenAPISpec) -> None:
    spec.validate_request("POST", "/v1/items", {"name": "a"})
    with pytest.raises(ContractViolation, match="Additional properties"):
        spec.validate_request("POST", "/v1/items", {"name": "a", "bogus": 1})


class ItemCreate(BaseModel):
    name: str
    tags: list[str] = []


def real_app(broken: bool = False) -> FastAPI:
    app = create_app(JaneSettings(), configure_logs=False)
    items: dict[str, dict[str, object]] = {}

    @app.post("/v1/items", status_code=201)
    async def create_item(body: ItemCreate, idempotency_key: str = Header()) -> dict[str, object]:
        item: dict[str, object] = {"id": f"i-{len(items) + 1}", "name": body.name}
        if not broken:
            item["tags"] = body.tags
        items[str(item["id"])] = item
        return item

    @app.get("/v1/items/{item_id}")
    async def get_item(item_id: str) -> dict[str, object]:
        if item_id not in items:
            raise NotFound()
        return items[item_id]

    return app


def test_contract_client_accepts_conforming_service(spec: OpenAPISpec) -> None:
    c = ContractClient(spec, TestClient(real_app()))
    r = c.post("/v1/items", json={"name": "x"}, headers={"Idempotency-Key": "1"})
    assert r.status_code == 201
    c.get(f"/v1/items/{r.json()['id']}")
    c.get("/v1/items/unknown")  # 404 problem+json matches the Problem schema
    assert "GET /v1/items" in c.uncovered()


def test_contract_client_catches_drift(spec: OpenAPISpec) -> None:
    c = ContractClient(spec, TestClient(real_app(broken=True)))
    with pytest.raises(ContractViolation, match="tags"):
        c.post("/v1/items", json={"name": "x"}, headers={"Idempotency-Key": "1"})


def test_mock_app_from_contract(spec: OpenAPISpec) -> None:
    mock = TestClient(build_mock_app(spec))
    r = mock.get("/v1/items/anything")
    assert r.status_code == 200 and r.json() == {"id": "i-1", "name": "first", "tags": ["a"]}
    assert mock.get("/v1/items/x", headers={"Prefer": "example=other"}).json()["id"] == "i-2"
    nf = mock.get("/v1/items/x", headers={"Prefer": "code=404"})
    assert nf.status_code == 404
    assert nf.headers["content-type"].startswith("application/problem+json")
    created = mock.post("/v1/items", json={"name": "n"})
    assert created.status_code == 201
    bad = mock.post("/v1/items", json={"bogus": True})
    assert bad.status_code == 422
    listing = mock.get("/v1/items").json()  # generated from schema, no example given
    assert listing == {"items": [{"id": "string", "name": "string", "tags": ["string"]}]}
    spec.validate_response("GET", "/v1/items", 200, listing)
    job = mock.get("/v1/jobs/j1").json()
    spec.validate_response("GET", "/v1/jobs/j1", 200, job)


def test_find_specs(tmp_path: Path) -> None:
    (tmp_path / "svc").mkdir()
    (tmp_path / "svc" / "openapi.yaml").write_text("openapi: 3.1.0\n", encoding="utf-8")
    (tmp_path / "svc" / "schema.json").write_text("{}", encoding="utf-8")
    assert [p.name for p in find_specs(tmp_path)] == ["openapi.yaml"]
    assert list(find_specs(tmp_path / "missing")) == []


def test_rejects_openapi_30(tmp_path: Path) -> None:
    f = tmp_path / "openapi.yaml"
    f.write_text("openapi: 3.0.3\ninfo: {title: x, version: '1'}\npaths: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"3.1"):
        OpenAPISpec.load(f)
