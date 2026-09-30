"""S3 adapter: registration and connection validation (no services needed, runs in `just check`)."""

from __future__ import annotations

from typing import Any

import pytest

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection
from jane_storage.adapters import adapter_class, create_adapter, package_dirs
from jane_storage.packages import load_package
from jane_storage_s3 import DEFAULT_OPTIONS, S3Adapter

SECRETS = {"access_key": "AKIAEXAMPLE", "secret_key": "not-a-real-secret"}


def conn(params: dict[str, Any], secrets: dict[str, str] | None = None) -> ResolvedConnection:
    return ResolvedConnection("raw-s3", "s3", params, SECRETS if secrets is None else secrets)


def test_registered_with_its_package() -> None:
    assert adapter_class("s3") is S3Adapter
    pkg = load_package(package_dirs()["jane.storage-s3"])
    assert pkg.adapter == "s3"
    assert pkg.writes == "raw_and_entities"


@pytest.mark.parametrize(
    ("params", "secrets"),
    [
        ({}, None),  # no bucket
        ({"bucket": "Bad_Bucket"}, None),
        ({"bucket": "jane-raw", "prefix": "../escape"}, None),
        ({"bucket": "jane-raw", "addressing_style": "sideways"}, None),
        ({"bucket": "jane-raw", "sse": "rot13"}, None),
        ({"bucket": "jane-raw"}, {}),  # no credentials: never falls back to the environment
    ],
)
async def test_invalid_connection_is_not_retryable(
    params: dict[str, Any], secrets: dict[str, str] | None
) -> None:
    adapter = create_adapter("s3")
    with pytest.raises(AdapterError) as err:
        await adapter.open(conn(params, secrets), {})
    assert err.value.retryable is False


async def test_open_without_network_and_limits_from_options() -> None:
    adapter = S3Adapter()
    await adapter.open(
        conn({"bucket": "jane-raw", "region": "eu-central-1", "sse": "aws:kms", "sse_kms_key_id": "k-1"}),
        {"prefix": "stage/raw", "connect_timeout_ms": 1234, "pool_max_size": 3, "lock_stale_ms": 5000},
    )
    try:
        config = adapter.client.meta.config
        assert config.connect_timeout == 1.234
        assert config.max_pool_connections == 3
        assert config.retries["total_max_attempts"] == DEFAULT_OPTIONS["retry_max_attempts"]
        assert adapter._k("entities", "x.json") == "stage/raw/entities/x.json"
        assert adapter._put_extra == {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": "k-1"}
        assert adapter._stale.total_seconds() == 5
    finally:
        await adapter.close()


async def test_not_open_adapter_fails_cleanly() -> None:
    with pytest.raises(AdapterError):
        await S3Adapter().read_entity("product", "k")
