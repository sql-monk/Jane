"""Crash recovery and races of the MongoDB commit protocol, driven deterministically (hooks, not timing):

* a snapshot whose ``pending`` event and delivery record were never rolled forward (the writer died, or lost the
  response, right after the compare-and-swap): ``_deliveries`` holds only the intent of the key;
* an intent whose commit died before the compare-and-swap: the key is not delivered, the next attempt commits;
* two instances with the same delivery key: the other instance commits between the two reads of
  ``commit_entity`` (snapshot first, then ``_deliveries``), or finishes its roll-forward between the reads of
  ``get_delivery`` (intent, then the snapshot it names).
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from pymongo import AsyncMongoClient

from jane_contracts.storage_adapter import CommitOutcome, HistoryEvent, ResolvedConnection
from jane_kit.devstack import load_stack
from jane_storage.codec import entity_ack
from jane_storage.compat.suite import COMPAT_RETRIES, record
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key, key_digest
from jane_storage.merge import merge
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


def _intent(delivery_key: str, key: str) -> dict[str, Any]:
    """The ``_deliveries`` document of an entity commit that is not rolled forward (yet)."""
    return {
        "_id": key_digest(delivery_key),
        "delivery_key": delivery_key,
        "intent": {"entity_type": "product", "entity_id": key_digest(key)},
    }


async def test_pending_event_and_delivery_are_rolled_forward(mongo: tuple[dict[str, Any], str]) -> None:
    info, database = mongo
    adapter = await _open(info, database)
    engine = StorageEngine(adapter, connection_id="recovery-mongo", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "m-a#0")
    await engine.store_entity(record(fields={"price": 2.0}, at=1), "m-b#0")
    key = canonical_key(record()["key"])
    eid, hid = key_digest(key), f"{key_digest(key)}|{2:012d}"
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(info["uri"], tz_aware=True)
    db = client[database]
    try:
        # state after a crash between the compare-and-swap and the roll-forward of version 2
        event = await db["product.history"].find_one({"_id": hid}, {"_id": 0, "key_hash": 0})
        assert event is not None
        snap = await adapter.read_entity("product", key)
        assert snap is not None
        history, _ = await adapter.list_history("product", key, limit=1)
        pending = {"version": 2, "delivery_key": "m-b#0", "event": event, "ack": entity_ack(snap, history[0])}
        await db["product"].update_one({"_id": eid}, {"$set": {"pending": pending}})
        await db["product.history"].delete_one({"_id": hid})
        await db["_deliveries"].replace_one({"_id": key_digest("m-b#0")}, _intent("m-b#0", key))

        # the redelivery is recognised through the intent and the pending key, and rolled forward
        again = await engine.store_entity(record(fields={"price": 2.0}, at=1), "m-b#0")
        assert again["status"] == "duplicate"
        assert again["entity"]["version"] == 2
        delivery = await db["_deliveries"].find_one({"_id": key_digest("m-b#0")})
        assert (
            delivery is not None
            and "intent" not in delivery
            and delivery["acks"][0]["entity"]["version"] == 2
        )
        assert await db["product.history"].find_one({"_id": hid}) is not None
        doc = await db["product"].find_one({"_id": eid})
        assert doc is not None and "pending" not in doc
        history, _ = await adapter.list_history("product", key, limit=10)
        assert [h.delivery_key for h in history] == ["m-b#0", "m-a#0"]
        ack = await engine.store_entity(record(fields={"price": 3.0}, at=2), "m-c#0")
        assert ack["entity"]["version"] == 3
    finally:
        await client.close()
        await adapter.close()


async def test_intent_without_a_commit_does_not_block_the_key(mongo: tuple[dict[str, Any], str]) -> None:
    """The writer died after its intent, before the compare-and-swap: nothing is delivered, and the next attempt
    with the key replaces the intent and commits."""
    info, database = mongo
    adapter = await _open(info, database)
    engine = StorageEngine(adapter, connection_id="recovery-mongo", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "base#0")
    key = canonical_key(record()["key"])
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(info["uri"], tz_aware=True)
    try:
        await client[database]["_deliveries"].insert_one(_intent("K#0", key))
        assert await adapter.get_delivery("K#0") is None
        ack = await engine.store_entity(record(fields={"price": 7.0}, at=5), "K#0")
        assert ack["status"] == "written" and ack["entity"]["version"] == 2
        found = await adapter.get_delivery("K#0")
        assert found is not None and found.acks[0]["entity"]["version"] == 2
        doc = await client[database]["_deliveries"].find_one({"_id": key_digest("K#0")})
        assert doc is not None and "intent" not in doc
        assert await _history(adapter, key) == ["K#0", "base#0"]
    finally:
        await client.close()
        await adapter.close()


# ------------------------------------------------------------------------ same key, two instances
class Hooked(MongoAdapter):
    """Runs ``hook`` once right before, and ``after_hook`` once right after, this instance first reads the
    document of a delivery key in ``_deliveries`` — i.e. after ``commit_entity`` has read the snapshot, and
    before ``get_delivery`` follows an intent to its snapshot."""

    hook: Callable[[], Awaitable[None]] | None = None
    after_hook: Callable[[], Awaitable[None]] | None = None

    async def _delivery_doc(self, delivery_key: str) -> dict[str, Any] | None:
        hook, self.hook = self.hook, None
        if hook is not None:
            await hook()
        doc = await super()._delivery_doc(delivery_key)
        after, self.after_hook = self.after_hook, None
        if after is not None:
            await after()
        return doc


async def _open(info: dict[str, Any], database: str, adapter: MongoAdapter | None = None) -> MongoAdapter:
    adapter = adapter or MongoAdapter()
    conn = ResolvedConnection(
        "recovery-mongo",
        "mongodb",
        {"host": info["host"], "port": int(info["port"]), "database": database},
        {"username": info["user"], "password": info["password"]},
    )
    await adapter.open(conn, {"connect_timeout_ms": 3000})
    await adapter.ensure_schema(["product"])
    return adapter


async def _history(adapter: MongoAdapter, key: str) -> list[str]:
    events, _ = await adapter.list_history("product", key, limit=100)
    return [e.delivery_key for e in events]


async def _no_roll_forward(doc: Any) -> None:
    return None


@pytest.mark.parametrize("a_progress", ["committed", "cas_only", "delivery_inserted"])
async def test_same_key_commit_between_the_two_reads(
    mongo: tuple[dict[str, Any], str], a_progress: str
) -> None:
    """B reads the snapshot (K is nowhere yet), then A commits K — fully, only intent + CAS (crash before the
    roll-forward) or intent + CAS + delivery record with ``pending`` still set — and only then B reads
    ``_deliveries``. B answers DUPLICATE or CONFLICT (then DUPLICATE on the core's retry); K is applied once."""
    info, database = mongo
    a = await _open(info, database)
    engine = StorageEngine(a, connection_id="recovery-mongo", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "base#0")
    key = canonical_key(record()["key"])
    eid = key_digest(key)
    rec = record(fields={"price": 7.0}, at=5)
    current = await a.read_entity("product", key)
    assert current is not None
    merged = merge(current, rec, now=datetime.now(UTC))
    event = HistoryEvent("product", key, rec, "K#0", datetime.now(UTC), merged.applied, [])
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(info["uri"], tz_aware=True)
    db = client[database]

    ran: list[bool] = []

    async def a_commits() -> None:
        ran.append(True)
        if a_progress != "committed":
            a._roll_forward = _no_roll_forward  # type: ignore[method-assign]
        result = await a.commit_entity(new=merged.snapshot, expected_version=1, event=event)
        assert result.outcome is CommitOutcome.COMMITTED
        intent = await db["_deliveries"].find_one({"_id": key_digest("K#0")})
        assert intent is not None and ("intent" in intent) is (a_progress != "committed")
        if a_progress == "delivery_inserted":  # first half of the roll-forward: delivery record, pending kept
            doc = await db["product"].find_one({"_id": eid})
            assert doc is not None and doc["pending"]["delivery_key"] == "K#0"
            await db["_deliveries"].replace_one(
                {"_id": key_digest("K#0")},
                {
                    "delivery_key": "K#0",
                    "recorded_at": doc["pending"]["event"]["received_at"],
                    "acks": [doc["pending"]["ack"]],
                },
            )

    b = Hooked()
    b.hook = a_commits
    try:
        await _open(info, database, b)
        result = await b.commit_entity(new=merged.snapshot, expected_version=1, event=event)
        assert ran == [True]  # the hook ran between B's two reads
        assert result.outcome in {CommitOutcome.DUPLICATE, CommitOutcome.CONFLICT}
        again = await StorageEngine(b, connection_id="recovery-mongo", retries=COMPAT_RETRIES).store_entity(
            rec, "K#0"
        )  # the core's retry of B
        assert again["status"] == "duplicate"
        assert await _history(b, key) == ["K#0", "base#0"]
    finally:
        await b.close()
        await client.close()
        await a.close()


async def test_get_delivery_while_the_other_instance_commits(mongo: tuple[dict[str, Any], str]) -> None:
    """B is about to read ``_deliveries`` (K is not there: A has not committed yet), A commits and rolls forward,
    then B reads: B finds K."""
    info, database = mongo
    a = await _open(info, database)
    engine = StorageEngine(a, connection_id="recovery-mongo", retries=COMPAT_RETRIES)
    await engine.store_entity(record(at=0), "base#0")

    ran: list[bool] = []

    async def a_commits() -> None:
        ran.append(True)
        ack = await engine.store_entity(record(fields={"price": 7.0}, at=5), "K#0")
        assert ack["status"] == "written"

    b = Hooked()
    b.hook = a_commits
    try:
        await _open(info, database, b)
        found = await b.get_delivery("K#0")
        assert ran == [True]
        assert found is not None and found.delivery_key == "K#0"
    finally:
        await b.close()
        await a.close()


async def test_get_delivery_while_the_other_instance_rolls_forward(mongo: tuple[dict[str, Any], str]) -> None:
    """A committed K (intent + CAS) without rolling forward. B reads the intent; then A finishes the roll-forward
    (delivery record, ``pending`` dropped) before B reads the snapshot the intent names. B finds no ``pending``
    there and must re-read ``_deliveries``: it finds K."""
    info, database = mongo
    a = await _open(info, database)
    await StorageEngine(a, connection_id="recovery-mongo", retries=COMPAT_RETRIES).store_entity(
        record(at=0), "base#0"
    )
    key = canonical_key(record()["key"])
    crashed = await _open(info, database)  # A's commit of K: intent + CAS, then the roll-forward is lost
    crashed._roll_forward = _no_roll_forward  # type: ignore[method-assign]
    ack = await StorageEngine(crashed, connection_id="recovery-mongo", retries=COMPAT_RETRIES).store_entity(
        record(fields={"price": 7.0}, at=5), "K#0"
    )
    assert ack["status"] == "written"
    await crashed.close()

    ran: list[bool] = []

    async def a_rolls_forward() -> None:
        ran.append(True)
        client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(info["uri"], tz_aware=True)
        try:
            doc = await client[database]["product"].find_one({"_id": key_digest(key)})
            assert doc is not None and doc["pending"]["delivery_key"] == "K#0"
            await a._roll_forward(doc)
            doc = await client[database]["product"].find_one({"_id": key_digest(key)})
            assert doc is not None and "pending" not in doc
        finally:
            await client.close()

    b = Hooked()
    b.after_hook = a_rolls_forward
    try:
        await _open(info, database, b)
        found = await b.get_delivery("K#0")
        assert ran == [True]
        assert found is not None and found.acks[0]["entity"]["version"] == 2
        assert await _history(b, key) == ["K#0", "base#0"]
    finally:
        await b.close()
        await a.close()
