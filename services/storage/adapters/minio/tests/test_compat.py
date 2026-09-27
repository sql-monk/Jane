"""Compatibility suite C-01…C-16 for the MinIO adapter against the MinIO server of the dev stack.

Needs `just up --project <name> minio`, then `just integration --project <name> services/storage/adapters/minio`.
Every test gets its own bucket (created by the adapter: ``create_bucket`` defaults to true for MinIO),
emptied and removed afterwards.
"""

from __future__ import annotations

import asyncio
import json
import socket
import uuid
from collections.abc import Mapping
from typing import Any

import boto3  # type: ignore[import-untyped]
import pytest
from botocore.config import Config  # type: ignore[import-untyped]

from jane_contracts.storage_adapter import ObjectRecord, ResolvedConnection
from jane_kit.devstack import StackInfo, load_stack
from jane_storage.compat import AdapterCompatSuite, CompatTarget
from jane_storage.keys import key_digest

pytestmark = pytest.mark.integration


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class MinioTarget(CompatTarget):
    kind = "minio"

    def __init__(self, stack: StackInfo) -> None:
        self.info = stack.services["minio"]
        self.bucket = f"compat-{uuid.uuid4().hex[:16]}"

    def _conn(self, endpoint: str, cid: str) -> ResolvedConnection:
        # MinIO profile: path-style addressing and bucket creation are the defaults
        return ResolvedConnection(
            connection_id=cid,
            kind="minio",
            params={"endpoint": endpoint, "bucket": self.bucket},
            secrets={"access_key": self.info["access_key"], "secret_key": self.info["secret_key"]},
        )

    def connection(self) -> ResolvedConnection:
        return self._conn(self.info["endpoint"], "compat-minio")

    def unavailable_connection(self) -> ResolvedConnection:
        return self._conn(f"http://127.0.0.1:{_free_port()}", "compat-minio-down")

    def options(self) -> dict[str, Any]:
        return {"prefix": "compat", "connect_timeout_ms": 2000, "retry_max_attempts": 1}

    def client(self) -> Any:
        return boto3.client(
            "s3",
            endpoint_url=self.info["endpoint"],
            region_name="us-east-1",
            aws_access_key_id=self.info["access_key"],
            aws_secret_access_key=self.info["secret_key"],
            config=Config(s3={"addressing_style": "path"}),
        )

    def _read_json(self, key: str) -> Any:
        return json.loads(self.client().get_object(Bucket=self.bucket, Key=key)["Body"].read())

    async def native_object_path(self, rec: ObjectRecord) -> str | None:
        key = str(rec.locator["key"])
        head = await asyncio.to_thread(self.client().head_object, Bucket=self.bucket, Key=key)
        assert head["Metadata"]["sha256"] == rec.sha256
        assert head["ContentType"].startswith(rec.media_type)
        return key

    async def native_entity_document(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> Any | None:
        key = f"{options['prefix']}/entities/{entity_type}/{key_digest(canonical_key)}.json"
        return await asyncio.to_thread(self._read_json, key)

    async def native_history_documents(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> list[Any] | None:
        prefix = f"{options['prefix']}/history/{entity_type}/{key_digest(canonical_key)}/"

        def read() -> list[Any]:
            resp = self.client().list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            return [self._read_json(o["Key"]) for o in resp.get("Contents", [])]

        return await asyncio.to_thread(read)

    async def cleanup(self) -> None:
        def drop() -> None:
            client = self.client()
            try:
                while True:
                    resp = client.list_objects_v2(Bucket=self.bucket)
                    for obj in resp.get("Contents", []):
                        client.delete_object(Bucket=self.bucket, Key=obj["Key"])
                    if not resp.get("IsTruncated"):
                        break
                client.delete_bucket(Bucket=self.bucket)
            except client.exceptions.NoSuchBucket:
                pass

        await asyncio.to_thread(drop)


class TestMinioCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        stack = load_stack()
        if stack is None or "minio" not in stack.services:
            pytest.skip("dev stack with minio is not running (just up minio)")
        return MinioTarget(stack)
