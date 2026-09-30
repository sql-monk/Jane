"""TZ §12 criterion 3: changing the storage needs no change in the collector or extractor.

The collector's output (``Material``) and the extractor's output (``EntityRecord`` list) are taken as
they are from the WP-00 contract examples. The storage stage of ``task-config/catalog-full.json`` is
turned into a ``HandlerInvocation`` exactly as the orchestrator does (``handler`` + ``connections`` +
inputs). Swapping the storage = editing only ``handler.package_id`` and ``connections.target`` of the
stage; the collector/extractor data stay byte-for-byte identical and the stored result is the same.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import contracts_dir
from jane_kit.devstack import load_stack
from jane_storage.app import build_app
from jane_storage.settings import Settings

CONTRACTS = contracts_dir(Path(__file__).parent)


def example(rel: str) -> Any:
    if CONTRACTS is None:
        pytest.skip("contracts not available")
    return json.loads((CONTRACTS / "examples" / rel).read_text(encoding="utf-8"))


def stage(task: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return copy.deepcopy(next(s for s in task["stages"] if s["stage_id"] == stage_id))


def invocation_for(stage_cfg: dict[str, Any], inputs: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    """What the orchestrator sends for one item of a storage stage (ADR-0008 delivery key)."""
    handler = {
        k: v for k, v in stage_cfg["handler"].items() if k != "digest"
    }  # digest comes from the registry
    delivery_key = hashlib.sha256(f"{run_id}|{stage_cfg['stage_id']}|item-1".encode()).hexdigest()
    return {
        "handler": handler,
        "params": stage_cfg.get("params", {}),
        "connections": stage_cfg["connections"],
        "inputs": inputs,
        "delivery": {"delivery_key": delivery_key},
    }


def swap(stage_cfg: dict[str, Any], package_id: str, target: str) -> dict[str, Any]:
    """The whole storage change: package and connection of the stage."""
    return {
        **stage_cfg,
        "handler": {**stage_cfg["handler"], "package_id": package_id},
        "connections": {"target": target},
    }


def run(client: TestClient, body: dict[str, Any]) -> dict[str, Any]:
    r = client.post(
        "/v1/invocations", json=body, headers={"Idempotency-Key": body["delivery"]["delivery_key"]}
    )
    assert r.status_code == 200, r.text
    result: dict[str, Any] = r.json()
    assert result["status"] == "success", result
    return result


def state(client: TestClient, connection_id: str) -> dict[str, Any]:
    items = client.get(
        "/v1/entities",
        params={
            "connection_id": connection_id,
            "entity_type": "product",
            "key": 'shop-example|{"sku":"A-100"}',
        },
    ).json()["items"]
    assert len(items) == 1
    return dict(items[0]["fields"])


def check_swap(client: TestClient, variants: list[tuple[str, str]]) -> None:
    task = example("schemas/task-config/catalog-full.json")
    material = example("schemas/material/web-product-page.json")
    entities = example("openapi/result-extractor-success.json")["value"]["output"]["entities"]
    frozen = json.dumps([material, entities], sort_keys=True)
    raw_stage, products_stage = stage(task, "store-raw"), stage(task, "store-products")
    fields = []
    for i, (package_id, target) in enumerate(variants):
        raw = run(
            client,
            invocation_for(
                swap(raw_stage, package_id, target), [{"kind": "material", "material": material}], f"r{i}"
            ),
        )
        obj = raw["output"]["writes"][0]["object"]
        assert obj["media_type"] == "text/html"
        content = client.get(f"/v1/objects/{obj['object_id']}/content", params={"connection_id": target})
        assert content.content == material["content"]["data"].encode()
        stored = run(
            client,
            invocation_for(
                swap(products_stage, package_id, target),
                [{"kind": "entities", "entities": entities}],
                f"p{i}",
            ),
        )
        assert stored["output"]["writes"][0]["status"] == "written"
        assert stored["output"]["writes"][0]["target"]["adapter"] == (
            "filesystem" if "files" in package_id else "postgresql"
        )
        fields.append(state(client, target))
    assert all(f == fields[0] for f in fields)
    assert fields[0]["price"] == {"amount": 1299.0, "currency": "UAH"}
    assert json.dumps([material, entities], sort_keys=True) == frozen  # collector/extractor data untouched


def test_swap_between_two_filesystem_storages(tmp_path: Path) -> None:
    conns = tmp_path / "c.json"
    conns.write_text(
        json.dumps(
            {
                "connections": [
                    {
                        "connection_id": "raw-files",
                        "kind": "filesystem",
                        "params": {"base_path": str(tmp_path / "a")},
                    },
                    {
                        "connection_id": "files-b",
                        "kind": "filesystem",
                        "params": {"base_path": str(tmp_path / "b")},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    with TestClient(build_app(Settings(log_format="console", connections_file=conns))) as client:
        check_swap(client, [("jane.storage-files", "raw-files"), ("jane.storage-files", "files-b")])


@pytest.fixture
def pg_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        pytest.skip("dev stack with postgres is not running (just up postgres)")
    pg = stack.services["postgres"]
    monkeypatch.setenv("JANE_SECRET_WP07_SWAP_PG_USER", pg["user"])
    monkeypatch.setenv("JANE_SECRET_WP07_SWAP_PG_PASSWORD", pg["password"])
    schema = f"swap_{hashlib.sha256(str(tmp_path).encode()).hexdigest()[:10]}"
    conns = tmp_path / "c.json"
    conns.write_text(
        json.dumps(
            {
                "connections": [
                    {
                        "connection_id": "raw-files",
                        "kind": "filesystem",
                        "params": {"base_path": str(tmp_path / "f")},
                    },
                    {
                        "connection_id": "results-pg",
                        "kind": "postgresql",
                        "params": {
                            "host": pg["host"],
                            "port": pg["port"],
                            "database": pg["database"],
                            "schema": schema,
                            "sslmode": "disable",
                        },
                        "secret_refs": {
                            "username": "env:JANE_SECRET_WP07_SWAP_PG_USER",
                            "password": "env:JANE_SECRET_WP07_SWAP_PG_PASSWORD",
                        },
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    settings = Settings(
        log_format="console",
        connections_file=conns,
        connection_host_allowlist=[f"{pg['host']}:{pg['port']}"],
    )
    with TestClient(build_app(settings)) as client:
        yield client
    import asyncio

    import asyncpg  # type: ignore[import-untyped]

    async def drop() -> None:
        con = await asyncpg.connect(pg["dsn"])
        try:
            await con.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        finally:
            await con.close()

    asyncio.run(drop())


@pytest.mark.integration
def test_swap_postgresql_and_filesystem(pg_client: TestClient) -> None:
    check_swap(pg_client, [("jane.storage-postgresql", "results-pg"), ("jane.storage-files", "raw-files")])
