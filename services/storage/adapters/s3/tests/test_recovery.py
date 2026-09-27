"""Crash recovery of the S3 commit protocol (shared by the MinIO adapter), against SeaweedFS.

Simulates the states a crashed writer leaves behind and checks that the adapter finishes or discards
them: a delivery claim without its snapshot (fresh → CONFLICT, stale → removed) and a snapshot whose
``pending`` history event was never rolled forward.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3  # type: ignore[import-untyped]
import pytest
from botocore.config import Config  # type: ignore[import-untyped]

from jane_contracts.storage_adapter import CommitOutcome, HistoryEvent, ResolvedConnection
from jane_kit.devstack import load_stack
from jane_storage.codec import dumps, format_ts
from jane_storage.compat.suite import COMPAT_RETRIES, record
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key, key_digest
from jane_storage.merge import merge
from jane_storage_s3 import S3Adapter

pytestmark = pytest.mark.integration

PREFIX = "recovery"


class Env:
    def __init__(self, info: dict[str, Any]) -> None:
        self.info = info
        self.bucket = f"recovery-{uuid.uuid4().hex[:12]}"
        self.client = boto3.client(
            "s3",
            endpoint_url=info["endpoint"],
            region_name=info.get("region", "us-east-1"),
            aws_access_key_id=info["access_key"],
            aws_secret_access_key=info["secret_key"],
            config=Config(s3={"addressing_style": "path"}),
        )

    async def adapter(self, **options: Any) -> S3Adapter:
        adapter = S3Adapter()
        conn = ResolvedConnection(
            "recovery-s3",
            "s3",
            {
                "endpoint": self.info["endpoint"],
                "bucket": self.bucket,
                "addressing_style": "path",
                "create_bucket": True,
            },
            {"access_key": self.info["access_key"], "secret_key": self.info["secret_key"]},
        )
        await adapter.open(conn, {"prefix": PREFIX, **options})
        await adapter.ensure_schema(["product"])
        return adapter

    def get(self, key: str) -> Any:
        return json.loads(self.client.get_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}")["Body"].read())

    def put(self, key: str, doc: Any) -> None:
        self.client.put_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}", Body=dumps(doc))

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=f"{PREFIX}/{key}")

    def drop(self) -> None:
        resp = self.client.list_objects_v2(Bucket=self.bucket)
        for obj in resp.get("Contents", []):
            self.client.delete_object(Bucket=self.bucket, Key=obj["Key"])
        self.client.delete_bucket(Bucket=self.bucket)


@pytest.fixture
async def env() -> AsyncIterator[Env]:
    stack = load_stack()
    if stack is None or "s3" not in stack.services:
        pytest.skip("dev stack with s3 (SeaweedFS) is not running (just up s3)")
    e = Env(stack.services["s3"])
    try:
        yield e
    finally:
        e.drop()


def claim(delivery_key: str, key: str, version: int, claimed_at: datetime) -> dict[str, Any]:
    return {
        "delivery_key": delivery_key,
        "recorded_at": format_ts(claimed_at),
        "claimed_at": format_ts(claimed_at),
        "acks": [{"entity": {"entity_type": "product", "canonical_key": key, "version": version}}],
    }


async def test_claim_of_a_commit_in_flight_conflicts_and_a_stale_one_is_removed(env: Env) -> None:
    adapter = await env.adapter(lock_stale_ms=60_000)
    rec = record(at=0)
    key = canonical_key(rec["key"])
    dkey = f"deliveries/{key_digest('crash-dk#0')}.json"
    env.put(dkey, claim("crash-dk#0", key, 1, datetime.now(UTC)))
    merged = merge(None, rec, now=datetime.now(UTC))
    event = HistoryEvent("product", key, rec, "crash-dk#0", datetime.now(UTC), merged.applied, [])
    # a fresh claim: its writer may still be committing → CONFLICT, nothing touched
    result = await adapter.commit_entity(new=merged.snapshot, expected_version=None, event=event)
    assert result.outcome is CommitOutcome.CONFLICT
    assert await adapter.get_delivery("crash-dk#0") is None
    assert await adapter.read_entity("product", key) is None
    # the same claim older than lock_stale_ms: a crashed writer → removed, the delivery is written
    env.put(dkey, claim("crash-dk#0", key, 1, datetime.now(UTC) - timedelta(minutes=5)))
    ack = await StorageEngine(adapter, connection_id="recovery-s3", retries=COMPAT_RETRIES).store_entity(
        rec, "crash-dk#0"
    )
    assert ack["status"] == "written"
    assert (await adapter.get_delivery("crash-dk#0")) is not None
    await adapter.close()


async def test_claim_that_lost_the_race_is_dead_at_once(env: Env) -> None:
    adapter = await env.adapter()
    engine = StorageEngine(adapter, connection_id="recovery-s3", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "winner#0")
    key = canonical_key(record()["key"])
    # a claim for version 1 by another key: the snapshot is at version 1 by "winner" → the claim is dead
    env.put(f"deliveries/{key_digest('loser#0')}.json", claim("loser#0", key, 1, datetime.now(UTC)))
    assert await adapter.get_delivery("loser#0") is None
    ack = await engine.store_entity(record(fields={"price": 1.0}, at=1), "loser#0")
    assert ack["status"] == "written"
    assert ack["entity"]["version"] == 2
    await adapter.close()


async def test_pending_history_event_is_rolled_forward(env: Env) -> None:
    adapter = await env.adapter()
    engine = StorageEngine(adapter, connection_id="recovery-s3", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "p-a#0")
    await engine.store_entity(record(fields={"price": 2.0}, at=1), "p-b#0")
    key = canonical_key(record()["key"])
    digest = key_digest(key)
    # state after a crash between the snapshot CAS and the roll-forward of version 2
    hist_key = f"history/product/{digest}/{2:012d}.json"
    snap = env.get(f"entities/product/{digest}.json")
    snap["pending"] = env.get(hist_key)
    env.put(f"entities/product/{digest}.json", snap)
    env.delete(hist_key)
    assert (await adapter.get_delivery("p-b#0")) is not None  # complete: the event is in the snapshot
    history, _ = await adapter.list_history("product", key, limit=10)
    assert [h.delivery_key for h in history] == ["p-b#0", "p-a#0"]
    assert env.get(hist_key)["delivery_key"] == "p-b#0"  # rolled forward by the reader
    assert "pending" not in env.get(f"entities/product/{digest}.json")
    # the next commit works on top of it
    ack = await engine.store_entity(record(fields={"price": 3.0}, at=2), "p-c#0")
    assert ack["entity"]["version"] == 3
    await adapter.close()
