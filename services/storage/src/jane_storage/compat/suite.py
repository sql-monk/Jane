"""Scenarios C-01…C-16 as a pytest base class (see :mod:`jane_storage.compat`)."""

# ruff: noqa: PT018

from __future__ import annotations

import asyncio
import base64
import contextlib
import hashlib
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, ClassVar

import pytest

from jane_contracts.storage_adapter import (
    AdapterError,
    CommitOutcome,
    DeliveryRecord,
    EntitySnapshot,
    HistoryEvent,
    ObjectRecord,
    OrderKey,
    RawObject,
    ResolvedConnection,
    StorageAdapter,
)
from jane_kit.clients import RetryPolicy

from ..adapters import REQUIRED_CAPABILITIES, adapter_class, create_adapter
from ..codec import entity_ack
from ..connections import AdapterPool, ConnectionRegistry
from ..content import ContentReader
from ..engine import StorageEngine
from ..handler import StorageHandler
from ..keys import canonical_key, object_id_for
from ..merge import merge
from ..packages import PackageCatalog, StoragePackage

__all__ = ["SCENARIOS", "AdapterCompatSuite", "CompatEnv", "CompatTarget"]

SCENARIOS = {
    "C-01": "new entity",
    "C-02": "repeated delivery after adapter restart",
    "C-03": "new observation with new values",
    "C-04": "partial update",
    "C-05": "explicit clear",
    "C-06": "late observation",
    "C-07": "mixed: one field newer, another not",
    "C-08": "same observed_at, different sequence",
    "C-09": "concurrent commits with one expected_version",
    "C-10": "put_object with the same key and sha256",
    "C-11": "put_object with the same key, different sha256",
    "C-12": "RAW HTML round trip",
    "C-13": "entities as JSON documents; entities format override",
    "C-14": "unicode, special characters and a long key",
    "C-15": "pagination of entities, history and objects",
    "C-16": "unavailable storage",
}

T0 = datetime(2026, 9, 27, 10, 0, 0, tzinfo=UTC)
ENTITY = "product"
SCOPE = "compat-shop"
COMPAT_RETRIES = RetryPolicy(max_attempts=20, initial_backoff_ms=1, max_backoff_ms=20, jitter=True)
"""Retry policy of the core on ``CONFLICT`` in the suite (the service reads it from ``limits.conflict_retries``)."""
PAGE_LIMITS = (1, 2, 3)


def ts(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def record(
    sku: str = "A-100",
    *,
    fields: Mapping[str, Any] | None = None,
    cleared: Sequence[str] = (),
    at: float = 0,
    obs: str | None = None,
    sequence: int | None = None,
    scope: str = SCOPE,
    natural: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "observation_id": obs or f"obs_{int(at * 60):08d}",
        "observed_at": ts(at).isoformat().replace("+00:00", "Z"),
    }
    if sequence is not None:
        observation["sequence"] = sequence
    rec: dict[str, Any] = {
        "entity_type": ENTITY,
        "key": {"scope": scope, "natural": dict(natural or {"sku": sku})},
        "fields": dict(
            fields if fields is not None else {"sku": sku, "title": f"Kettle {sku}", "price": 1299.0}
        ),
        "observation": observation,
    }
    if cleared:
        rec["cleared"] = list(cleared)
    return rec


def raw_object(
    key: str, content: bytes, *, material: str = "web:compat", media_type: str = "text/html"
) -> RawObject:
    return RawObject(
        object_key=key,
        material_id=material,
        observation_id=key.rsplit("/", 1)[-1].split(".", 1)[0],
        source_id=SCOPE,
        media_type=media_type,
        format="original",
        content=content,
        sha256=hashlib.sha256(content).hexdigest(),
        metadata={"material_id": material, "source": {"source_id": SCOPE, "kind": "web"}},
    )


class CompatTarget(ABC):
    """What an adapter package provides to the suite. One instance = one isolated namespace."""

    kind: ClassVar[str]
    entity_formats: ClassVar[tuple[str, ...]] = ("json",)
    """Values of ``options["entities_format"]`` the adapter supports (filesystem: json and jsonl)."""

    @abstractmethod
    def connection(self) -> ResolvedConnection:
        """Connection to an empty namespace of a reachable storage (same one on every call)."""

    @abstractmethod
    def unavailable_connection(self) -> ResolvedConnection:
        """Connection of the same kind whose storage is not reachable (C-16)."""

    def options(self) -> dict[str, Any]:
        """Base ``adapter.open`` options (e.g. prefix); the suite adds ``entities_format``."""
        return {}

    async def cleanup(self) -> None:  # noqa: B027 - optional hook
        """Drop the namespace after the test (optional)."""

    async def native_object_path(self, rec: ObjectRecord) -> str | None:
        """Adapter-native name of a stored object (filesystem: relative path) — C-12; None if n/a."""
        return None

    async def native_entity_document(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> Any | None:
        """The stored entity document as the adapter keeps it (parsed JSON) — C-13; None if n/a."""
        return None

    async def native_history_documents(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> list[Any] | None:
        """Stored history documents in the adapter's native layout — C-13 format override; None if n/a."""
        return None


class CompatEnv:
    """Opened adapters, engines and the handler over one :class:`CompatTarget`."""

    def __init__(self, target: CompatTarget) -> None:
        self.target = target
        self._opened: list[StorageAdapter] = []

    async def adapter(
        self, *, connection: ResolvedConnection | None = None, **options: Any
    ) -> StorageAdapter:
        adapter = create_adapter(self.target.kind)
        await adapter.open(connection or self.target.connection(), {**self.target.options(), **options})
        self._opened.append(adapter)
        await adapter.ensure_schema([ENTITY])
        return adapter

    async def restart(self, adapter: StorageAdapter, **options: Any) -> StorageAdapter:
        await adapter.close()
        self._opened.remove(adapter)
        return await self.adapter(**options)

    def engine(self, adapter: StorageAdapter) -> StorageEngine:
        return StorageEngine(
            adapter, connection_id=self.target.connection().connection_id, retries=COMPAT_RETRIES
        )

    def package(self) -> StoragePackage:
        catalog = PackageCatalog.discover()
        for pkg in catalog.all():
            if pkg.adapter == self.target.kind and pkg.writes == "raw_and_entities":
                return pkg
        raise AssertionError(
            f"no storage package with adapter={self.target.kind!r} and writes=raw_and_entities is registered "
            "in the 'jane.storage.packages' entry point group"
        )

    def handler(self, connection: ResolvedConnection) -> tuple[StorageHandler, AdapterPool]:
        registry = ConnectionRegistry()
        registry.add_resolved(connection)
        pool = AdapterPool(registry, self.target.options())
        reader = ContentReader(max_bytes=16 * 1024 * 1024, request_timeout_ms=5_000)
        handler = StorageHandler(PackageCatalog([self.package()]), pool, reader, retries=COMPAT_RETRIES)
        return handler, pool

    async def close(self) -> None:
        for adapter in self._opened:
            with contextlib.suppress(Exception):  # best-effort cleanup
                await adapter.close()
        self._opened.clear()
        await self.target.cleanup()


async def collect_entities(
    adapter: StorageAdapter, limit: int, scope: str | None = None
) -> list[EntitySnapshot]:
    items: list[EntitySnapshot] = []
    cursor: str | None = None
    for _ in range(1000):
        page, cursor = await adapter.list_entities(ENTITY, scope=scope, cursor=cursor, limit=limit)
        assert len(page) <= limit
        items.extend(page)
        if cursor is None:
            return items
    raise AssertionError("list_entities did not finish")


async def collect_history(adapter: StorageAdapter, key: str, limit: int) -> list[HistoryEvent]:
    items: list[HistoryEvent] = []
    cursor: str | None = None
    for _ in range(1000):
        page, cursor = await adapter.list_history(ENTITY, key, cursor=cursor, limit=limit)
        assert len(page) <= limit
        items.extend(page)
        if cursor is None:
            return items
    raise AssertionError("list_history did not finish")


async def collect_objects(adapter: StorageAdapter, limit: int, **filters: Any) -> list[ObjectRecord]:
    items: list[ObjectRecord] = []
    cursor: str | None = None
    for _ in range(1000):
        page, cursor = await adapter.list_objects(cursor=cursor, limit=limit, **filters)
        assert len(page) <= limit
        items.extend(page)
        if cursor is None:
            return items
    raise AssertionError("list_objects did not finish")


def _order(rec: Mapping[str, Any]) -> OrderKey:
    obs = rec["observation"]
    return OrderKey(
        observed_at=datetime.fromisoformat(obs["observed_at"].replace("Z", "+00:00")),
        observation_id=obs["observation_id"],
        sequence=obs.get("sequence"),
    )


def _event(
    rec: Mapping[str, Any], dk: str, applied: Sequence[str], stale: Sequence[str] = ()
) -> HistoryEvent:
    return HistoryEvent(
        entity_type=ENTITY,
        canonical_key=canonical_key(rec["key"]),
        record=dict(rec),
        delivery_key=dk,
        received_at=datetime.now(UTC),
        applied_fields=list(applied),
        stale_fields=list(stale),
    )


class AdapterCompatSuite:
    """Base class; subclasses provide the ``compat_target`` fixture. Test names carry the scenario id."""

    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        raise NotImplementedError("override the compat_target fixture in the adapter's test class")

    @pytest.fixture
    async def env(self, compat_target: CompatTarget) -> AsyncIterator[CompatEnv]:
        env = CompatEnv(compat_target)
        try:
            yield env
        finally:
            await env.close()

    # ---------------------------------------------------------------------------------- basics
    async def test_registered_with_required_capabilities(self, env: CompatEnv) -> None:
        cls = adapter_class(env.target.kind)
        assert cls.kind == env.target.kind
        assert frozenset(cls.capabilities) == REQUIRED_CAPABILITIES
        adapter = await env.adapter()
        assert isinstance(adapter, StorageAdapter)
        assert await adapter.health() is True
        await adapter.ensure_schema([ENTITY, "event"])  # idempotent
        assert env.package().adapter == env.target.kind

    # ---------------------------------------------------------------------------------- C-01
    async def test_c01_new_entity(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        rec = record(at=0)
        key = canonical_key(rec["key"])
        assert await adapter.read_entity(ENTITY, key) is None
        merged = merge(None, rec, now=datetime.now(UTC))
        event = _event(rec, "c01-dk#0", merged.applied)
        result = await adapter.commit_entity(new=merged.snapshot, expected_version=None, event=event)
        assert result.outcome is CommitOutcome.COMMITTED
        assert result.snapshot is not None and result.snapshot.version == 1
        snap = await adapter.read_entity(ENTITY, key)
        assert snap is not None
        assert snap.version == 1
        assert dict(snap.fields) == rec["fields"]
        assert dict(snap.key) == rec["key"]
        assert snap.canonical_key == key
        assert snap.field_orders["price"] == _order(rec)
        history = await collect_history(adapter, key, 10)
        assert len(history) == 1
        assert history[0].delivery_key == "c01-dk#0"
        assert sorted(history[0].applied_fields) == ["price", "sku", "title"]
        delivery = await adapter.get_delivery("c01-dk#0")
        assert delivery is not None
        assert [dict(a) for a in delivery.acks] == [entity_ack(merged.snapshot, event)]
        # through the core
        ack = await env.engine(adapter).store_entity(record("B-200", at=0), "c01-core#0")
        assert ack["status"] == "written"
        assert ack["entity"]["version"] == 1
        assert ack["target"]["adapter"] == env.target.kind

    # ---------------------------------------------------------------------------------- C-02
    async def test_c02_redelivery_after_restart_is_duplicate(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        rec = record(at=0)
        key = canonical_key(rec["key"])
        first = await env.engine(adapter).store_entity(rec, "c02-dk#0")
        assert first["status"] == "written"
        before = await adapter.read_entity(ENTITY, key)
        adapter = await env.restart(adapter)
        again = await env.engine(adapter).store_entity(rec, "c02-dk#0")
        assert again["status"] == "duplicate"
        assert again["entity"] == first["entity"]
        assert again["applied_fields"] == first["applied_fields"]
        assert await adapter.read_entity(ENTITY, key) == before
        assert len(await collect_history(adapter, key, 10)) == 1
        # the adapter itself refuses the same delivery key atomically
        assert before is not None
        merged = merge(before, rec, now=datetime.now(UTC))
        dup = await adapter.commit_entity(
            new=merged.snapshot,
            expected_version=before.version,
            event=_event(rec, "c02-dk#0", merged.applied),
        )
        assert dup.outcome is CommitOutcome.DUPLICATE
        assert await adapter.read_entity(ENTITY, key) == before
        assert len(await collect_history(adapter, key, 10)) == 1

    # ---------------------------------------------------------------------------------- C-03
    async def test_c03_new_observation_updates(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        await engine.store_entity(record(at=0), "c03-a#0")
        rec2 = record(fields={"sku": "A-100", "title": "Kettle A-100 v2", "price": 1199.0}, at=10)
        ack = await engine.store_entity(rec2, "c03-b#0")
        assert ack["status"] == "written"
        assert ack["entity"]["version"] == 2
        snap = await adapter.read_entity(ENTITY, canonical_key(rec2["key"]))
        assert snap is not None
        assert dict(snap.fields) == rec2["fields"]
        assert snap.version == 2
        history = await collect_history(adapter, snap.canonical_key, 10)
        assert [h.delivery_key for h in history] == ["c03-b#0", "c03-a#0"]  # newest first

    # ---------------------------------------------------------------------------------- C-04
    async def test_c04_partial_update_keeps_other_fields(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        await engine.store_entity(record(at=0), "c04-a#0")
        ack = await engine.store_entity(record(fields={"price": 999.0}, at=5), "c04-b#0")
        assert ack["status"] == "written"
        assert ack["applied_fields"] == ["price"]
        snap = await adapter.read_entity(ENTITY, canonical_key(record()["key"]))
        assert snap is not None
        assert dict(snap.fields) == {"sku": "A-100", "title": "Kettle A-100", "price": 999.0}
        assert snap.field_orders["title"] == _order(record(at=0))
        assert snap.field_orders["price"] == _order(record(at=5))

    # ---------------------------------------------------------------------------------- C-05
    async def test_c05_explicit_clear(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        await engine.store_entity(record(at=0), "c05-a#0")
        clear = record(fields={}, cleared=["price"], at=7)
        ack = await engine.store_entity(clear, "c05-b#0")
        assert ack["status"] == "written"
        assert ack["applied_fields"] == ["price"]
        snap = await adapter.read_entity(ENTITY, canonical_key(clear["key"]))
        assert snap is not None
        assert "price" not in snap.fields
        assert "price" in snap.cleared_fields
        assert snap.field_orders["price"] == _order(clear)
        assert dict(snap.fields) == {"sku": "A-100", "title": "Kettle A-100"}
        # a later value brings the field back and removes it from cleared_fields
        await engine.store_entity(record(fields={"price": 1.5}, at=8), "c05-c#0")
        snap = await adapter.read_entity(ENTITY, canonical_key(clear["key"]))
        assert snap is not None
        assert snap.fields["price"] == 1.5
        assert "price" not in snap.cleared_fields

    # ---------------------------------------------------------------------------------- C-06
    async def test_c06_late_observation_is_stale(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        await engine.store_entity(record(at=10), "c06-a#0")
        key = canonical_key(record()["key"])
        before = await adapter.read_entity(ENTITY, key)
        late = record(fields={"price": 1399.0, "title": "old"}, at=1)
        ack = await engine.store_entity(late, "c06-b#0")
        assert ack["status"] == "stale"
        assert ack["applied_fields"] == []
        assert ack["stale_fields"] == ["price", "title"]
        snap = await adapter.read_entity(ENTITY, key)
        assert snap is not None and before is not None
        assert dict(snap.fields) == dict(before.fields)
        assert dict(snap.field_orders) == dict(before.field_orders)
        history = await collect_history(adapter, key, 10)
        assert len(history) == 2
        assert history[0].delivery_key == "c06-b#0"
        assert list(history[0].stale_fields) == ["price", "title"]
        assert list(history[0].applied_fields) == []
        assert history[0].record["fields"] == late["fields"]

    # ---------------------------------------------------------------------------------- C-07
    async def test_c07_mixed_partially_stale(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        await engine.store_entity(record(at=0), "c07-a#0")
        await engine.store_entity(record(fields={"price": 1000.0}, at=30), "c07-b#0")
        mixed = record(fields={"price": 500.0, "title": "Kettle new title"}, at=20)
        ack = await engine.store_entity(mixed, "c07-c#0")
        assert ack["status"] == "partially_stale"
        assert ack["applied_fields"] == ["title"]
        assert ack["stale_fields"] == ["price"]
        snap = await adapter.read_entity(ENTITY, canonical_key(mixed["key"]))
        assert snap is not None
        assert snap.fields["price"] == 1000.0
        assert snap.fields["title"] == "Kettle new title"

    # ---------------------------------------------------------------------------------- C-08
    async def test_c08_same_time_higher_sequence_wins(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        v2 = record(fields={"text": "edited"}, at=0, obs="obs_edit", sequence=1727431300)
        v1 = record(fields={"text": "original"}, at=0, obs="obs_orig", sequence=1727431200)
        assert (await engine.store_entity(v2, "c08-a#0"))["status"] == "written"
        assert (await engine.store_entity(v1, "c08-b#0"))["status"] == "stale"
        snap = await adapter.read_entity(ENTITY, canonical_key(v2["key"]))
        assert snap is not None
        assert snap.fields["text"] == "edited"
        assert snap.field_orders["text"].sequence == 1727431300
        v3 = record(fields={"text": "edited again"}, at=0, obs="obs_edit2", sequence=1727431400)
        assert (await engine.store_entity(v3, "c08-c#0"))["status"] == "written"
        snap = await adapter.read_entity(ENTITY, canonical_key(v2["key"]))
        assert snap is not None and snap.fields["text"] == "edited again"

    # ---------------------------------------------------------------------------------- C-09
    async def test_c09_concurrent_commits(self, env: CompatEnv) -> None:
        first = await env.adapter()
        second = await env.adapter()  # a separate instance, as another worker/process would have
        await env.engine(first).store_entity(record(at=0), "c09-base#0")
        key = canonical_key(record()["key"])
        current = await first.read_entity(ENTITY, key)
        assert current is not None and current.version == 1
        a = record(fields={"price": 10.0}, at=5, obs="obs_a")
        b = record(fields={"title": "B"}, at=6, obs="obs_b")
        ma, mb = merge(current, a, now=datetime.now(UTC)), merge(current, b, now=datetime.now(UTC))
        results = await asyncio.gather(
            first.commit_entity(new=ma.snapshot, expected_version=1, event=_event(a, "c09-a#0", ma.applied)),
            second.commit_entity(new=mb.snapshot, expected_version=1, event=_event(b, "c09-b#0", mb.applied)),
        )
        outcomes = sorted(r.outcome.value for r in results)
        assert outcomes == ["committed", "conflict"]
        loser = "c09-b#0" if results[0].outcome is CommitOutcome.COMMITTED else "c09-a#0"
        assert await first.get_delivery(loser) is None, (
            "a conflicting commit must not leave its delivery record"
        )
        snap = await first.read_entity(ENTITY, key)
        assert snap is not None and snap.version == 2
        assert len(await collect_history(first, key, 10)) == 2
        # the core retries on CONFLICT: both concurrent updates end up applied
        c = record(fields={"price": 20.0}, at=7, obs="obs_c")
        d = record(fields={"availability": "in_stock"}, at=8, obs="obs_d")
        acks = await asyncio.gather(
            env.engine(first).store_entity(c, "c09-c#0"), env.engine(second).store_entity(d, "c09-d#0")
        )
        assert sorted(ack["status"] for ack in acks) == ["written", "written"]
        snap = await second.read_entity(ENTITY, key)
        assert snap is not None
        assert snap.version == 4
        assert snap.fields["price"] == 20.0
        assert snap.fields["availability"] == "in_stock"
        assert len(await collect_history(second, key, 10)) == 4

    # ---------------------------------------------------------------------------------- C-10
    async def test_c10_put_object_is_idempotent(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        obj = raw_object(
            f"{SCOPE}/2026/09/27/web_c10/obs_1.html", b"<html><h1>C-10</h1></html>", material="web:c10"
        )
        first = await adapter.put_object(obj)
        assert first.object_id == object_id_for(obj.object_key)
        assert first.sha256 == obj.sha256
        assert first.size_bytes == len(obj.content)
        adapter = await env.restart(adapter)
        again = await adapter.put_object(obj)
        assert again.object_id == first.object_id
        assert again.sha256 == first.sha256
        assert again.object_key == first.object_key
        listed = await collect_objects(adapter, 10, material_id="web:c10")
        assert [o.object_id for o in listed] == [first.object_id]
        fetched = await adapter.get_object(first.object_id)
        assert fetched is not None and fetched.object_key == obj.object_key
        assert await adapter.get_object("obj_does_not_exist") is None
        # object deliveries: record_delivery is insert-if-absent
        rec = DeliveryRecord(
            delivery_key="c10-dk", recorded_at=datetime.now(UTC), acks=[{"object": {"x": 1}}]
        )
        assert await adapter.record_delivery(rec) is True
        assert await adapter.record_delivery(rec) is False
        stored = await adapter.get_delivery("c10-dk")
        assert stored is not None and [dict(a) for a in stored.acks] == [{"object": {"x": 1}}]

    # ---------------------------------------------------------------------------------- C-11
    async def test_c11_same_key_other_content_is_rejected(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        key = f"{SCOPE}/2026/09/27/web_c11/obs_1.html"
        await adapter.put_object(raw_object(key, b"<html>one</html>"))
        with pytest.raises(AdapterError) as err:
            await adapter.put_object(raw_object(key, b"<html>two</html>"))
        assert err.value.retryable is False
        stored = await collect_objects(adapter, 10, material_id="web:compat")
        assert len(stored) == 1
        assert await adapter.read_object_content(stored[0].object_id) == b"<html>one</html>"

    # ---------------------------------------------------------------------------------- C-12
    async def test_c12_raw_html_round_trip(self, env: CompatEnv) -> None:
        page = "<!doctype html><html><head><meta charset=utf-8><title>Чайник</title></head><body>€ 1299</body></html>"
        content = page.encode("utf-8")
        handler, pool = env.handler(env.target.connection())
        pkg = env.package()
        invocation = {
            "handler": {"package_id": pkg.package_id, "version": pkg.version},
            "inputs": [
                {
                    "kind": "material",
                    "material": {
                        "material_id": "web:c12c12c12c12c12c12c12c12c12c12c1",
                        "observation_id": "obs_c12",
                        "source": {"source_id": SCOPE, "kind": "web"},
                        "locator": {"url": "https://shop.example.test/p/c12"},
                        "fetched_at": "2026-09-27T10:00:05Z",
                        "format": {"media_type": "text/html; charset=utf-8", "content_kind": "page"},
                        "revision": {"content_sha256": hashlib.sha256(content).hexdigest()},
                        "content": {
                            "kind": "inline",
                            "media_type": "text/html",
                            "encoding": "base64",
                            "data": base64.b64encode(content).decode(),
                            "sha256": hashlib.sha256(content).hexdigest(),
                        },
                        "collector": {"name": "web-collector", "version": "0.1.0"},
                    },
                }
            ],
            "connections": {"target": env.target.connection().connection_id},
            "delivery": {"delivery_key": "c12-dk"},
        }
        try:
            result = await handler.invoke(invocation)
            assert result["status"] == "success", result
            (ack,) = result["output"]["writes"]
            assert ack["status"] == "written"
            obj = ack["object"]
            assert obj["media_type"] == "text/html"
            adapter = await env.adapter()
            assert await adapter.read_object_content(obj["object_id"]) == content
            rec = await adapter.get_object(obj["object_id"])
            assert rec is not None
            assert rec.media_type == "text/html"
            assert rec.object_key.endswith(".html")
            assert rec.metadata.get("material_id") == "web:c12c12c12c12c12c12c12c12c12c12c1"
            native = await env.target.native_object_path(rec)
            if native is not None:
                assert native.endswith(".html")
            again = await handler.invoke(invocation)
            assert again["duplicate"] is True
            assert again["output"]["writes"][0]["status"] == "duplicate"
            assert again["output"]["writes"][0]["object"]["object_id"] == obj["object_id"]
        finally:
            await pool.close()

    # ---------------------------------------------------------------------------------- C-13
    async def test_c13_entities_are_json_documents(self, env: CompatEnv) -> None:
        fields = {
            "sku": "J-1",
            "price": {"amount": 1299.5, "currency": "UAH"},
            "tags": ["kettle", "steel", 3, True],
            "stock": 0,
            "discount": False,
            "title": "Чайник «J-1» — 1,7 л",
        }
        for fmt in env.target.entity_formats:
            adapter = await env.adapter(entities_format=fmt)
            engine = env.engine(adapter)
            rec = record(fields=fields, at=0, natural={"sku": f"J-1-{fmt}"})
            await engine.store_entity(rec, f"c13-{fmt}-a#0")
            await engine.store_entity(
                record(fields={"stock": 5}, at=1, natural={"sku": f"J-1-{fmt}"}), f"c13-{fmt}-b#0"
            )
            key = canonical_key(rec["key"])
            snap = await adapter.read_entity(ENTITY, key)
            assert snap is not None
            assert dict(snap.fields) == {**fields, "stock": 5}
            assert isinstance(snap.fields["price"]["amount"], float)
            assert snap.fields["tags"][3] is True
            history = await collect_history(adapter, key, 10)
            assert [h.record["fields"] for h in history] == [{"stock": 5}, fields]
            options = {**env.target.options(), "entities_format": fmt}
            doc = await env.target.native_entity_document(ENTITY, key, options)
            if doc is not None:
                assert doc["fields"] == {**fields, "stock": 5}
                assert doc["canonical_key"] == key
            native_history = await env.target.native_history_documents(ENTITY, key, options)
            if native_history is not None:
                assert len(native_history) == 2
            adapter = await env.restart(adapter, entities_format=fmt)
            assert await adapter.read_entity(ENTITY, key) == snap

    # ---------------------------------------------------------------------------------- C-14
    async def test_c14_unicode_and_long_keys(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        natural = {"sku": "A/1 ?#", "назва": "Чайник 🫖 \\ \" ' % * : < > |", "long": "x" * 300, "n": 7}
        rec = record(fields={"title": "ключ"}, at=0, scope="scope|ua", natural=natural)
        key = canonical_key(rec["key"])
        assert key.startswith('scope|ua|{"long":"')
        ack = await engine.store_entity(rec, "c14-dk/ ?#ї#0")
        assert ack["status"] == "written"
        snap = await adapter.read_entity(ENTITY, key)
        assert snap is not None
        assert snap.canonical_key == key
        assert dict(snap.key) == rec["key"]
        assert snap.fields["title"] == "ключ"
        assert [s.canonical_key for s in await collect_entities(adapter, 10, scope="scope|ua")] == [key]
        history = await collect_history(adapter, key, 10)
        assert [h.delivery_key for h in history] == ["c14-dk/ ?#ї#0"]
        assert await adapter.get_delivery("c14-dk/ ?#ї#0") is not None
        again = await engine.store_entity(rec, "c14-dk/ ?#ї#0")
        assert again["status"] == "duplicate"
        other = record(fields={"title": "other"}, at=0, scope="scope|ua", natural={**natural, "n": 8})
        await engine.store_entity(other, "c14-other#0")
        snap = await adapter.read_entity(ENTITY, key)
        assert snap is not None and snap.fields["title"] == "ключ"

    # ---------------------------------------------------------------------------------- C-15
    async def test_c15_pagination(self, env: CompatEnv) -> None:
        adapter = await env.adapter()
        engine = env.engine(adapter)
        skus = [f"P-{i:02d}" for i in range(7)]
        for i, sku in enumerate(skus):
            await engine.store_entity(record(sku, at=i), f"c15-e{i}#0")
        await engine.store_entity(record("OTHER", at=0, scope="compat-other"), "c15-other#0")
        for i in range(1, 5):
            await engine.store_entity(record("P-00", fields={"price": float(i)}, at=10 + i), f"c15-h{i}#0")
        key0 = canonical_key(record("P-00")["key"])
        for i in range(5):
            content = f"<html>{i}</html>".encode()
            await adapter.put_object(
                raw_object(f"{SCOPE}/2026/09/27/web_c15/obs_{i}.html", content, material="web:c15")
            )
        await adapter.put_object(
            raw_object(f"{SCOPE}/2026/09/27/web_x/obs_x.html", b"<html>x</html>", material="web:x")
        )
        for limit in PAGE_LIMITS:
            entities = await collect_entities(adapter, limit, scope=SCOPE)
            keys = [e.canonical_key for e in entities]
            assert len(keys) == len(set(keys)) == 7, (limit, keys)
            assert {e.fields["sku"] for e in entities} == set(skus)
            everything = await collect_entities(adapter, limit)
            assert len({e.canonical_key for e in everything}) == len(everything) == 8
            history = await collect_history(adapter, key0, limit)
            assert [h.delivery_key for h in history] == [f"c15-h{i}#0" for i in (4, 3, 2, 1)] + ["c15-e0#0"]
            objects = await collect_objects(adapter, limit, material_id="web:c15")
            ids = [o.object_id for o in objects]
            assert len(ids) == len(set(ids)) == 5, (limit, ids)
            assert len(await collect_objects(adapter, limit)) == 6
            assert len(await collect_objects(adapter, limit, source_id=SCOPE)) == 6
        past = await collect_objects(adapter, 10, until=datetime(2000, 1, 1, tzinfo=UTC))
        assert past == []
        recent = await collect_objects(adapter, 10, since=datetime(2000, 1, 1, tzinfo=UTC))
        assert len(recent) == 6
        updated = await adapter.list_entities(
            ENTITY, updated_since=datetime.now(UTC) + timedelta(hours=1), limit=10
        )
        assert list(updated[0]) == []

    # ---------------------------------------------------------------------------------- C-16
    async def test_c16_unavailable_storage(self, env: CompatEnv) -> None:
        conn = env.target.unavailable_connection()
        adapter = create_adapter(env.target.kind)
        opened: AdapterError | None = None
        try:
            await adapter.open(conn, env.target.options())
        except AdapterError as exc:
            opened = exc
        if opened is not None:
            assert opened.retryable is True
        else:
            try:
                assert await adapter.health() is False
                with pytest.raises(AdapterError) as err:
                    await adapter.ensure_schema([ENTITY])
                assert err.value.retryable is True
                obj = raw_object(f"{SCOPE}/2026/09/27/web_c16/obs.html", b"<html/>")
                with pytest.raises(AdapterError) as err:
                    await adapter.put_object(obj)
                assert err.value.retryable is True
            finally:
                await adapter.close()
        handler, pool = env.handler(conn)
        pkg = env.package()
        try:
            result = await handler.invoke(
                {
                    "handler": {"package_id": pkg.package_id, "version": pkg.version},
                    "inputs": [{"kind": "entities", "entities": [record(at=0)]}],
                    "connections": {"target": conn.connection_id},
                    "delivery": {"delivery_key": "c16-dk"},
                }
            )
        finally:
            await pool.close()
        assert result["status"] == "failed"
        assert result["failure"]["kind"] == "connection_error"
        assert result["failure"]["retryable"] is True
        assert result["handler_kind"] == "storage"
