"""MinIO adapter: registration and the MinIO profile of the S3 protocol (no services needed)."""

from __future__ import annotations

import pytest

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection
from jane_storage.adapters import adapter_class, create_adapter, package_dirs
from jane_storage.packages import load_package
from jane_storage_minio import MinioAdapter
from jane_storage_s3 import S3Adapter

SECRETS = {"access_key": "minio", "secret_key": "not-a-real-secret"}


def test_registered_with_its_package() -> None:
    assert adapter_class("minio") is MinioAdapter
    assert issubclass(MinioAdapter, S3Adapter)
    pkg = load_package(package_dirs()["jane.storage-minio"])
    assert pkg.adapter == "minio"
    assert pkg.writes == "raw_and_entities"


async def test_endpoint_is_required() -> None:
    with pytest.raises(AdapterError) as err:
        await create_adapter("minio").open(
            ResolvedConnection("m", "minio", {"bucket": "jane-raw"}, SECRETS), {}
        )
    assert err.value.retryable is False


async def test_aws_server_side_encryption_is_rejected() -> None:
    params = {"bucket": "jane-raw", "endpoint": "http://minio:9000", "sse": "aws:kms"}
    with pytest.raises(AdapterError) as err:
        await create_adapter("minio").open(ResolvedConnection("m", "minio", params, SECRETS), {})
    assert err.value.retryable is False


async def test_profile_defaults() -> None:
    adapter = MinioAdapter()
    await adapter.open(
        ResolvedConnection("m", "minio", {"bucket": "jane-raw", "endpoint": "http://minio:9000"}, SECRETS), {}
    )
    try:
        assert adapter.client.meta.config.s3["addressing_style"] == "path"
        assert adapter._create_bucket is True
    finally:
        await adapter.close()
