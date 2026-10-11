"""MongoDB adapter: registration, connection validation and collection names (no services needed, runs in
`just check`)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import jsonschema
import pytest

from jane_contracts.storage_adapter import AdapterError, EntitySnapshot, HistoryEvent, ResolvedConnection
from jane_storage.adapters import adapter_class, create_adapter, package_dirs
from jane_storage.packages import load_package
from jane_storage_mongodb import MAX_CHUNK_BYTES, MongoAdapter


def test_registered_with_its_package() -> None:
    assert adapter_class("mongodb") is MongoAdapter
    pkg = load_package(package_dirs()["jane.storage-mongodb"])
    assert pkg.adapter == "mongodb"
    assert pkg.writes == "raw_and_entities"
    assert pkg.version.split(".")[0] == "2"  # collection per entity type: new major version
    assert pkg.params_schema is not None
    jsonschema.validate({"prefix": ""}, pkg.params_schema)  # the default (empty) prefix is a valid value
    jsonschema.validate({"prefix": "stage_"}, pkg.params_schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"prefix": "no-dashes"}, pkg.params_schema)


@pytest.mark.parametrize(
    ("params", "options"),
    [
        ({"database": "bad name"}, {}),
        ({"database": "jane"}, {"prefix": "no-dashes"}),
        ({"database": "jane"}, {"prefix": "jane_\n"}),
        ({"database": "jane"}, {"chunk_bytes": MAX_CHUNK_BYTES + 1}),
    ],
)
async def test_invalid_connection_is_not_retryable(params: dict[str, Any], options: dict[str, Any]) -> None:
    with pytest.raises(AdapterError) as err:
        await create_adapter("mongodb").open(ResolvedConnection("m", "mongodb", params), options)
    assert err.value.retryable is False


async def test_open_is_lazy_and_limits_come_from_options() -> None:
    adapter = MongoAdapter()
    await adapter.open(
        ResolvedConnection("m", "mongodb", {"host": "mongo.invalid", "database": "jane"}, {"username": "u"}),
        {"prefix": "stage_", "connect_timeout_ms": 1500, "pool_max_size": 3, "chunk_bytes": 1024},
    )
    try:
        assert adapter._type_col("product_book").name == "stage_product_book"
        assert adapter._history_col("product_book").name == "stage_product_book.history"
        assert adapter._svc("deliveries").name == "stage__deliveries"
        assert adapter._chunk == 1024
        assert adapter._client is not None
        assert adapter._client.options.pool_options.max_pool_size == 3
        assert adapter._client.options.server_selection_timeout == 1.5
    finally:
        await adapter.close()


async def test_collection_names_with_the_default_empty_prefix() -> None:
    adapter = MongoAdapter()
    await adapter.open(ResolvedConnection("m", "mongodb", {"host": "mongo.invalid", "database": "jane"}), {})
    try:
        assert adapter._type_col("product").name == "product"
        assert adapter._history_col("product").name == "product.history"
        assert {adapter._svc(n).name for n in ("deliveries", "objects", "object_chunks")} == {
            "_deliveries",
            "_objects",
            "_object_chunks",
        }
    finally:
        await adapter.close()


async def test_entity_types_without_a_collection() -> None:
    """Names outside ^[a-z][a-z0-9_]{0,63}$ (and ``system`` without a prefix: ``system.*`` is reserved by
    MongoDB) have no collection: reads find nothing, writes fail without retries — before any I/O."""
    adapter = MongoAdapter()
    await adapter.open(ResolvedConnection("m", "mongodb", {"host": "mongo.invalid", "database": "jane"}), {})
    now = datetime.now(UTC)
    try:
        for entity_type in ("system", "Product", "_deliveries", "product.history", "x" * 65):
            assert await adapter.read_entity(entity_type, "s|{}") is None
            assert await adapter.list_entities(entity_type, limit=10) == ([], None)
            assert await adapter.search_entities(entity_type, search="a", limit=10) == ([], None)
            assert await adapter.list_history(entity_type, "s|{}", limit=10) == ([], None)
            snap = EntitySnapshot(
                entity_type, "s|{}", {"scope": "s", "natural": {}}, {}, {}, frozenset(), 1, now
            )
            event = HistoryEvent(entity_type, "s|{}", {}, "d#0", now, [], [])
            with pytest.raises(AdapterError) as err:
                await adapter.commit_entity(new=snap, expected_version=None, event=event)
            assert err.value.retryable is False
    finally:
        await adapter.close()
    await adapter.open(
        ResolvedConnection("m", "mongodb", {"host": "mongo.invalid", "database": "jane"}), {"prefix": "p_"}
    )
    try:
        assert adapter._history_col("system").name == "p_system.history"
    finally:
        await adapter.close()
