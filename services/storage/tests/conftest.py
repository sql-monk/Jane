from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_storage.app import build_app
from jane_storage.settings import Settings

PAGE = b"<!doctype html><html><head><title>Kettle A-100</title></head><body><div class=price>1299 UAH</div></body></html>"


def material(
    content: bytes = PAGE,
    *,
    media_type: str = "text/html",
    observation_id: str = "obs_01J9ZQ4A0000000000000001",
    material_id: str = "web:3704326c60776c53169680099e2eed31",
    source_id: str | None = "shop-example",
) -> dict[str, Any]:
    source: dict[str, Any] = {"kind": "web"}
    if source_id:
        source["source_id"] = source_id
    digest = hashlib.sha256(content).hexdigest()
    return {
        "material_id": material_id,
        "observation_id": observation_id,
        "source": source,
        "locator": {"url": "https://shop.example.test/product/a-100"},
        "fetched_at": "2026-09-27T10:00:05Z",
        "format": {"media_type": media_type, "content_kind": "page"},
        "revision": {"content_sha256": digest},
        "content": {
            "kind": "inline",
            "media_type": media_type,
            "encoding": "base64",
            "data": base64.b64encode(content).decode(),
            "size_bytes": len(content),
            "sha256": digest,
        },
        "collector": {"name": "web-collector", "version": "0.1.0"},
    }


def entity(
    sku: str = "A-100",
    *,
    fields: dict[str, Any] | None = None,
    at: str = "2026-09-27T10:00:05Z",
    obs: str = "obs_1",
) -> dict[str, Any]:
    return {
        "entity_type": "product",
        "key": {"scope": "shop-example", "natural": {"sku": sku}},
        "fields": fields if fields is not None else {"sku": sku, "title": f"Kettle {sku}", "price": 1299.0},
        "observation": {"observation_id": obs, "observed_at": at},
    }


def invocation(
    inputs: list[dict[str, Any]],
    delivery_key: str,
    *,
    package: str = "jane.storage-files",
    target: str | None = "raw-files",
    **extra: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "handler": {"package_id": package, "version": "1.0.0"},
        "inputs": inputs,
        "delivery": {"delivery_key": delivery_key},
        **extra,
    }
    if target is not None:
        body["connections"] = {"target": target}
    return body


def post(client: TestClient, body: dict[str, Any]) -> Any:
    return client.post(
        "/v1/invocations", json=body, headers={"Idempotency-Key": body["delivery"]["delivery_key"]}
    )


@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    return tmp_path / "storage"


@pytest.fixture
def settings(tmp_path: Path, storage_dir: Path) -> Settings:
    conn_file = tmp_path / "connections.json"
    conn_file.write_text(
        json.dumps(
            {
                "connections": [
                    {
                        "connection_id": "raw-files",
                        "kind": "filesystem",
                        "params": {"base_path": str(storage_dir)},
                    },
                    {
                        "connection_id": "broken-files",
                        "kind": "filesystem",
                        "params": {"base_path": str(tmp_path / "blocker" / "x")},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "blocker").write_text("file", encoding="utf-8")
    return Settings(log_format="console", connections_file=conn_file)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(settings)) as c:
        yield c


@pytest.fixture
def h() -> SimpleNamespace:
    """Test helpers (importlib mode: tests cannot import conftest directly)."""
    return SimpleNamespace(material=material, entity=entity, invocation=invocation, post=post, PAGE=PAGE)
