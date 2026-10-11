"""Catalog, server-side search and inventories against the real filesystem adapter."""

import asyncio
import json
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import OpenAPISpec
from jane_storage.app import build_app
from jane_storage.settings import Settings


def seed(client: TestClient, h: SimpleNamespace) -> None:
    records = [
        h.entity(f"A-{i}", fields={"title": title, "nested": {"tags": ["ноутбук"]}})
        for i, title in enumerate(["first", "Needle 100%_ match", "Needle other", "last"])
    ]
    another = h.entity("article-1", fields={"title": "Article"})
    another["entity_type"] = "article"
    another["key"]["scope"] = "another-scope"
    records.append(another)
    response = h.post(client, h.invocation([{"kind": "entities", "entities": records}], "discovery-seed"))
    assert response.json()["status"] == "success", response.text


def test_actual_catalog_empty_scoped_and_paginated(client: TestClient, h: SimpleNamespace) -> None:
    params = {"connection_id": "raw-files", "limit": 1}
    empty = client.get("/v1/entity-types", params=params)
    assert empty.json() == {"items": [], "next_cursor": None, "search_supported": True}
    seed(client, h)
    first = client.get("/v1/entity-types", params=params)
    assert first.json()["items"] == [{"entity_type": "article", "entity_count": 1}]
    second = client.get("/v1/entity-types", params={**params, "cursor": first.json()["next_cursor"]})
    assert second.json()["items"] == [{"entity_type": "product", "entity_count": 4}]
    assert second.json()["next_cursor"] is None
    scoped = client.get("/v1/entity-types", params={**params, "scope": "shop-example"}).json()
    assert scoped["items"] == [{"entity_type": "product", "entity_count": 4}]
    OpenAPISpec.load(
        Path(__file__).resolve().parents[3] / "contracts/openapi/storage.v1.yaml"
    ).validate_response("GET", "/v1/entity-types", 200, first.json())


def test_search_before_pagination_not_only_first_page(client: TestClient, h: SimpleNamespace) -> None:
    seed(client, h)
    params = {"connection_id": "raw-files", "entity_type": "product", "limit": 1}
    first = client.get("/v1/entities", params=params).json()
    assert first["items"][0]["fields"]["title"] == "first"
    found = client.get("/v1/entities", params={**params, "search": "needle"}).json()
    assert found["items"][0]["fields"]["title"] == "Needle 100%_ match"
    assert found["next_cursor"]
    after = client.get(
        "/v1/entities", params={**params, "search": "NEEDLE", "cursor": found["next_cursor"]}
    ).json()
    assert after["items"][0]["fields"]["title"] == "Needle other"
    assert after["next_cursor"] is None
    literal = client.get("/v1/entities", params={**params, "search": "%_"}).json()
    assert literal["items"][0]["fields"]["title"] == "Needle 100%_ match"
    assert literal["next_cursor"] is None
    assert client.get("/v1/entities", params={**params, "search": "ноутбук"}).json()["items"]
    assert not client.get(
        "/v1/entities", params={**params, "search": "needle", "scope": "another-scope"}
    ).json()["items"]
    key = found["items"][0]["canonical_key"]
    assert (
        client.get("/v1/entities", params={**params, "key": key, "search": "missing"}).json()["items"] == []
    )


def test_optional_catalog_unavailable_and_failure_not_empty(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from jane_storage_files import FilesystemAdapter

    monkeypatch.setattr(FilesystemAdapter, "list_entity_types", None)
    response = client.get("/v1/entity-types", params={"connection_id": "raw-files"})
    assert response.status_code == 501
    assert response.json()["code"] == "not_implemented"
    monkeypatch.setattr(FilesystemAdapter, "search_entities", None)
    response = client.get(
        "/v1/entities", params={"connection_id": "raw-files", "entity_type": "product", "search": "needle"}
    )
    assert response.status_code == 501
    assert client.get("/v1/entity-types", params={"connection_id": "broken-files"}).status_code == 502


@pytest.mark.parametrize(
    ("method", "path", "query"),
    [
        ("list_entity_types", "/v1/entity-types", {}),
        ("list_entities", "/v1/entities", {"entity_type": "product"}),
        ("search_entities", "/v1/entities", {"entity_type": "product", "search": "private-query"}),
        (
            "read_entity",
            "/v1/entities",
            {"entity_type": "product", "key": "private-key", "search": "private-query"},
        ),
    ],
)
def test_configured_read_deadline_returns_safe_problem(
    method: str,
    path: str,
    query: dict[str, str],
    settings: Settings,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jane_storage_files import FilesystemAdapter

    original = getattr(FilesystemAdapter, method)
    cancelled = threading.Event()

    async def delayed_real_read(self: FilesystemAdapter, *args: Any, **kwargs: Any) -> Any:
        try:
            await asyncio.sleep(0.1)
            return await original(self, *args, **kwargs)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    monkeypatch.setattr(FilesystemAdapter, method, delayed_real_read)
    limits_file = tmp_path / "read-deadline.json"
    limits_file.write_text(
        json.dumps({"defaults": {"timeouts": {"request_timeout_ms": 5}}}), encoding="utf-8"
    )
    spec = OpenAPISpec.load(Path(__file__).resolve().parents[3] / "contracts/openapi/storage.v1.yaml")
    with TestClient(build_app(settings.with_overrides(limits_file=limits_file))) as client:
        assert client.get("/v1/info").json()["limits"]["defaults"]["timeouts"]["request_timeout_ms"] == 5

        # Warm the real connection so this regression measures cancellation of the operation,
        # rather than timing out during first-time schema initialization.
        async def warm_connection() -> None:
            async with client.app.state.pool.lease("raw-files", "filesystem", {}):
                pass

        assert client.portal is not None
        client.portal.call(warm_connection)
        response = client.get(path, params={"connection_id": "raw-files", **query})
    assert response.status_code == 504, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "timeout"
    assert response.json()["retryable"] is True
    assert cancelled.is_set(), "the actual adapter operation was not cancelled"
    assert "private-query" not in response.text and "private-key" not in response.text
    assert str(tmp_path) not in response.text
    spec.validate_response("GET", path, 504, response.json(), response.headers["content-type"])
