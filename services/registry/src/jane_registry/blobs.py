"""Content-addressed archive storage (ADR-0002 §2): object ``<bucket>/<prefix><sha256 hex>``.

* :class:`S3BlobStore` - MinIO / S3 (``boto3``), the default;
* :class:`FileBlobStore` - a directory standing in for the bucket (single host, tests, air-gapped use).

Objects are immutable: ``put`` of an existing digest is a no-op (identical content deduplicates).
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Protocol

from .archive import digest_of

__all__ = ["BlobIntegrityError", "BlobStore", "FileBlobStore", "S3BlobStore"]


class BlobIntegrityError(RuntimeError):
    """Stored bytes do not match their digest."""


def _hex(digest: str) -> str:
    return digest.removeprefix("sha256:")


def _verify(digest: str, data: bytes) -> bytes:
    if digest_of(data) != digest:
        raise BlobIntegrityError(f"archive {digest} is corrupted in the blob store")
    return data


class BlobStore(Protocol):
    name: str

    async def put(self, digest: str, data: bytes) -> None: ...
    async def get(self, digest: str) -> bytes | None: ...
    async def exists(self, digest: str) -> bool: ...
    async def check(self) -> bool: ...
    def location(self, digest: str) -> str: ...


class FileBlobStore:
    name = "filesystem"

    def __init__(self, root: Path, bucket: str, prefix: str) -> None:
        self.base = root / bucket
        self.bucket = bucket
        self.prefix = prefix

    def _path(self, digest: str) -> Path:
        return self.base / f"{self.prefix}{_hex(digest)}"

    def location(self, digest: str) -> str:
        return self._path(digest).resolve().as_uri()

    def _put(self, digest: str, data: bytes) -> None:
        target = self._path(digest)
        if target.is_file():
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    async def put(self, digest: str, data: bytes) -> None:
        _verify(digest, data)
        await asyncio.to_thread(self._put, digest, data)

    async def get(self, digest: str) -> bytes | None:
        path = self._path(digest)
        try:
            data = await asyncio.to_thread(path.read_bytes)
        except FileNotFoundError:
            return None
        return _verify(digest, data)

    async def exists(self, digest: str) -> bool:
        return await asyncio.to_thread(self._path(digest).is_file)

    async def check(self) -> bool:
        await asyncio.to_thread(self.base.mkdir, parents=True, exist_ok=True)
        return True


class S3BlobStore:
    name = "s3"

    def __init__(
        self,
        *,
        bucket: str,
        prefix: str,
        endpoint_url: str | None,
        region: str,
        access_key: str | None,
        secret_key: str | None,
        connect_timeout_s: float,
        read_timeout_s: float,
        max_attempts: int,
    ) -> None:
        import boto3  # type: ignore[import-untyped]
        from botocore.config import Config  # type: ignore[import-untyped]

        self.bucket = bucket
        self.prefix = prefix
        self.client: Any = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(
                connect_timeout=connect_timeout_s,
                read_timeout=read_timeout_s,
                retries={"max_attempts": max_attempts, "mode": "standard"},
                s3={"addressing_style": "path"},
            ),
        )

    def _key(self, digest: str) -> str:
        return f"{self.prefix}{_hex(digest)}"

    def location(self, digest: str) -> str:
        return f"s3://{self.bucket}/{self._key(digest)}"

    def ensure_bucket(self) -> None:
        from botocore.exceptions import ClientError  # type: ignore[import-untyped]

        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)

    def _exists(self, digest: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self.client.head_object(Bucket=self.bucket, Key=self._key(digest))
        except ClientError as exc:
            if str(exc.response.get("Error", {}).get("Code")) in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
        return True

    def _put(self, digest: str, data: bytes) -> None:
        if self._exists(digest):
            return
        self.client.put_object(
            Bucket=self.bucket,
            Key=self._key(digest),
            Body=data,
            ContentType="application/zip",
            ChecksumSHA256=_b64_sha256(data),
        )

    def _get(self, digest: str) -> bytes | None:
        from botocore.exceptions import ClientError

        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self._key(digest))
        except ClientError as exc:
            if str(exc.response.get("Error", {}).get("Code")) in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise
        return bytes(obj["Body"].read())

    async def put(self, digest: str, data: bytes) -> None:
        _verify(digest, data)
        await asyncio.to_thread(self._put, digest, data)

    async def get(self, digest: str) -> bytes | None:
        data = await asyncio.to_thread(self._get, digest)
        return None if data is None else _verify(digest, data)

    async def exists(self, digest: str) -> bool:
        return await asyncio.to_thread(self._exists, digest)

    async def check(self) -> bool:
        await asyncio.to_thread(self.client.head_bucket, Bucket=self.bucket)
        return True


def _b64_sha256(data: bytes) -> str:
    import base64

    return base64.b64encode(hashlib.sha256(data).digest()).decode("ascii")
