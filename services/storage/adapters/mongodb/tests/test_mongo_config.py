"""MongoDB adapter: registration and connection validation (no services needed, runs in `just check`)."""

from __future__ import annotations

from typing import Any

import pytest

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection
from jane_storage.adapters import adapter_class, create_adapter, package_dirs
from jane_storage.packages import load_package
from jane_storage_mongodb import MAX_CHUNK_BYTES, MongoAdapter


def test_registered_with_its_package() -> None:
    assert adapter_class("mongodb") is MongoAdapter
    pkg = load_package(package_dirs()["jane.storage-mongodb"])
    assert pkg.adapter == "mongodb"
    assert pkg.writes == "raw_and_entities"


@pytest.mark.parametrize(
    ("params", "options"),
    [
        ({"database": "bad name"}, {}),
        ({"database": "jane"}, {"prefix": "no-dashes"}),
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
        assert adapter._col("entities").name == "stage_entities"
        assert adapter._chunk == 1024
        assert adapter._client is not None
        assert adapter._client.options.pool_options.max_pool_size == 3
        assert adapter._client.options.server_selection_timeout == 1.5
    finally:
        await adapter.close()
