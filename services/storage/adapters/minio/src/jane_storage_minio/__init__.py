"""MinIO adapter of the Jane storage handler (``kind: minio``).

MinIO speaks the S3 API, so the storage protocol — key layout, conditional writes, the commit algorithm
and crash recovery — is the one of :mod:`jane_storage_s3` (tested against both MinIO and SeaweedFS).
Only the profile differs:

| | ``s3`` | ``minio`` |
|---|---|---|
| ``params.endpoint`` | optional (AWS derives it from ``region``) | required |
| ``addressing_style`` | ``auto`` (virtual-hosted on AWS) | ``path`` |
| ``create_bucket`` default | ``false`` (buckets are provisioned in AWS) | ``true`` |
| ``sse`` / ``sse_kms_key_id`` | accepted (SSE-S3 / SSE-KMS) | rejected (MinIO KMS is server configuration) |
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from jane_storage_s3 import S3Adapter, S3Profile

__all__ = ["MinioAdapter", "package_dir"]


def package_dir() -> Path:
    """Directory of the ``jane.storage-minio`` storage package (entry point ``jane.storage.packages``)."""
    return Path(__file__).parent / "package"


class MinioAdapter(S3Adapter):
    """``StorageAdapter`` over a MinIO bucket (``params.endpoint``, ``params.bucket``; secrets ``access_key``, ``secret_key``)."""

    kind: ClassVar[str] = "minio"
    profile: ClassVar[S3Profile] = S3Profile(
        addressing_style="path", endpoint_required=True, create_bucket=True, server_side_encryption=False
    )
