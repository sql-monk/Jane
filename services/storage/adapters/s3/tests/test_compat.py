"""Compatibility suite C-01…C-16 for the S3 adapter against SeaweedFS (an S3 implementation that is not MinIO).

Needs `just up --project <name> s3`, then `just integration --project <name> services/storage/adapters/s3`.
Every test gets its own bucket, emptied and removed afterwards. Real AWS S3 is not covered here.
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


class S3Target(CompatTarget):
    kind = "s3"

    def __init__(self, stack: StackInfo, service: str = "s3") -> None:
        self.info = stack.services[service]
        self.bucket = f"compat-{uuid.uuid4().hex[:16]}"

    def _conn(self, endpoint: str, cid: str) -> ResolvedConnection:
        return ResolvedConnection(
            connection_id=cid,
            kind=self.kind,
            params={
                "endpoint": endpoint,
                "region": self.info.get("region", "us-east-1"),
                "bucket": self.bucket,
                "addressing_style": "path",
                "create_bucket": True,
            },
            secrets={"access_key": self.info["access_key"], "secret_key": self.info["secret_key"]},
        )

    def connection(self) -> ResolvedConnection:
        return self._conn(self.info["endpoint"], f"compat-{self.kind}")

    def unavailable_connection(self) -> ResolvedConnection:
        return self._conn(f"http://127.0.0.1:{_free_port()}", f"compat-{self.kind}-down")

    def options(self) -> dict[str, Any]:
        return {"prefix": "compat", "connect_timeout_ms": 2000, "retry_max_attempts": 1}

    def client(self) -> Any:
        return boto3.client(
            "s3",
            endpoint_url=self.info["endpoint"],
            region_name=self.info.get("region", "us-east-1"),
            aws_access_key_id=self.info["access_key"],
            aws_secret_access_key=self.info["secret_key"],
            config=Config(s3={"addressing_style": "path"}),
        )

    def _read_json(self, key: str) -> Any:
        body = self.client().get_object(Bucket=self.bucket, Key=key)["Body"].read()
        return json.loads(body)

    async def native_object_path(self, rec: ObjectRecord) -> str | None:
        key = str(rec.locator["key"])
        head = await asyncio.to_thread(self.client().head_object, Bucket=self.bucket, Key=key)
        assert head["Metadata"]["sha256"] == rec.sha256
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
                    keys = [{"Key": o["Key"]} for o in resp.get("Contents", [])]
                    for key in keys:
                        client.delete_object(Bucket=self.bucket, Key=key["Key"])
                    if not resp.get("IsTruncated"):
                        break
                client.delete_bucket(Bucket=self.bucket)
            except client.exceptions.NoSuchBucket:
                pass

        await asyncio.to_thread(drop)


class TestS3Compat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        stack = load_stack()
        if stack is None or "s3" not in stack.services:
            pytest.skip("dev stack with s3 (SeaweedFS) is not running (just up s3)")
        return S3Target(stack)
