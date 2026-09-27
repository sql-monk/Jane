"""Crash recovery of the MongoDB commit protocol: a snapshot whose ``pending`` event and delivery record
were never rolled forward (the writer died right after the compare-and-swap)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

import pytest
from pymongo import AsyncMongoClient

from jane_contracts.storage_adapter import ResolvedConnection
from jane_kit.devstack import load_stack
from jane_storage.codec import entity_ack
from jane_storage.compat.suite import COMPAT_RETRIES, record
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key, key_digest
from jane_storage_mongodb import MongoAdapter

pytestmark = pytest.mark.integration


@pytest.fixture
async def mongo() -> AsyncIterator[tuple[dict[str, Any], str]]:
    stack = load_stack()
    if stack is None or "mongodb" not in stack.services:
        pytest.skip("dev stack with mongodb is not running (just up mongodb)")
    info, database = stack.services["mongodb"], f"recovery_{uuid.uuid4().hex[:12]}"
    yield info, database
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(info["uri"])
    await client.drop_database(database)
    await client.close()


async def test_pending_event_and_delivery_are_rolled_forward(mongo: tuple[dict[str, Any], str]) -> None:
    info, database = mongo
    adapter = MongoAdapter()
    conn = ResolvedConnection(
        "recovery-mongo",
        "mongodb",
        {"host": info["host"], "port": int(info["port"]), "database": database},
        {"username": info["user"], "password": info["password"]},
    )
    await adapter.open(conn, {"connect_timeout_ms": 3000})
    await adapter.ensure_schema(["product"])
    engine = StorageEngine(adapter, connection_id="recovery-mongo", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "m-a#0")
    await engine.store_entity(record(fields={"price": 2.0}, at=1), "m-b#0")
    key = canonical_key(record()["key"])
    eid, hid = f"product|{key_digest(key)}", f"product|{key_digest(key)}|{2:012d}"
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(info["uri"], tz_aware=True)
    db = client[database]
    try:
        # state after a crash between the compare-and-swap and the roll-forward of version 2
        event = await db["jane_entity_history"].find_one({"_id": hid}, {"_id": 0, "key_hash": 0})
        assert event is not None
        snap = await adapter.read_entity("product", key)
        assert snap is not None
        history, _ = await adapter.list_history("product", key, limit=1)
        pending = {"version": 2, "delivery_key": "m-b#0", "event": event, "ack": entity_ack(snap, history[0])}
        await db["jane_entities"].update_one({"_id": eid}, {"$set": {"pending": pending}})
        await db["jane_entity_history"].delete_one({"_id": hid})
        await db["jane_deliveries"].delete_one({"_id": key_digest("m-b#0")})

        # the redelivery is recognised through the indexed pending key and rolled forward
        again = await engine.store_entity(record(fields={"price": 2.0}, at=1), "m-b#0")
        assert again["status"] == "duplicate"
        assert await db["jane_deliveries"].find_one({"_id": key_digest("m-b#0")}) is not None
        assert await db["jane_entity_history"].find_one({"_id": hid}) is not None
        doc = await db["jane_entities"].find_one({"_id": eid})
        assert doc is not None and "pending" not in doc
        history, _ = await adapter.list_history("product", key, limit=10)
        assert [h.delivery_key for h in history] == ["m-b#0", "m-a#0"]
        ack = await engine.store_entity(record(fields={"price": 3.0}, at=2), "m-c#0")
        assert ack["entity"]["version"] == 3
    finally:
        await client.close()
        await adapter.close()
