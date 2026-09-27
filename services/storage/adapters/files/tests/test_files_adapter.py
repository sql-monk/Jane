"""Filesystem-specific guarantees: several processes, crash recovery, stale and held locks, jsonl."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from jane_contracts.storage_adapter import AdapterError, DeliveryRecord, ResolvedConnection
from jane_storage.codec import delivery_to_json, dumps, utcnow
from jane_storage.engine import StorageEngine
from jane_storage.keys import canonical_key, key_digest
from jane_storage_files import FilesystemAdapter


def conn(base: Path) -> ResolvedConnection:
    return ResolvedConnection(connection_id="t", kind="filesystem", params={"base_path": str(base)})


def rec(field: str, value: object, minute: int, obs: str) -> dict[str, object]:
    return {
        "entity_type": "product",
        "key": {"scope": "s", "natural": {"sku": "A"}},
        "fields": {field: value},
        "observation": {"observation_id": obs, "observed_at": f"2026-09-27T10:{minute:02d}:00Z"},
    }


KEY = canonical_key({"scope": "s", "natural": {"sku": "A"}})


async def open_adapter(base: Path, **options: object) -> FilesystemAdapter:
    adapter = FilesystemAdapter()
    await adapter.open(conn(base), options)
    await adapter.ensure_schema(["product"])
    return adapter


WORKER = textwrap.dedent(
    """
    import asyncio, sys
    from jane_contracts.storage_adapter import ResolvedConnection
    from jane_kit.clients import RetryPolicy
    from jane_storage.engine import StorageEngine
    from jane_storage_files import FilesystemAdapter

    async def main(base, worker, count):
        adapter = FilesystemAdapter()
        await adapter.open(ResolvedConnection("t", "filesystem", {"base_path": base}), {})
        await adapter.ensure_schema(["product"])
        engine = StorageEngine(adapter, retries=RetryPolicy(max_attempts=200, initial_backoff_ms=1, max_backoff_ms=20))
        for i in range(count):
            record = {
                "entity_type": "product",
                "key": {"scope": "s", "natural": {"sku": "A"}},
                "fields": {f"w{worker}": i},
                "observation": {"observation_id": f"o{worker}-{i:04d}", "observed_at": f"2026-09-27T10:00:{i:02d}Z"},
            }
            ack = await engine.store_entity(record, f"dk-{worker}-{i}#0")
            assert ack["status"] == "written", ack

    asyncio.run(main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])))
    """
)


def spawn(base: Path, worker: int, count: int) -> subprocess.Popen[bytes]:
    return subprocess.Popen([sys.executable, "-c", WORKER, str(base), str(worker), str(count)])


async def test_several_processes_update_one_entity(tmp_path: Path) -> None:
    workers, count = 4, 8
    procs = [spawn(tmp_path, w, count) for w in range(workers)]
    assert [p.wait(timeout=120) for p in procs] == [0] * workers
    adapter = await open_adapter(tmp_path)
    snap = await adapter.read_entity("product", KEY)
    assert snap is not None
    assert snap.version == workers * count
    assert dict(snap.fields) == {f"w{w}": count - 1 for w in range(workers)}
    history, cursor = await adapter.list_history("product", KEY, limit=1000)
    assert cursor is None
    assert len(history) == workers * count
    assert not list((tmp_path / "locks").rglob("*.lock"))


async def test_delivery_record_left_by_a_crash_is_redone(tmp_path: Path) -> None:
    adapter = await open_adapter(tmp_path)
    engine = StorageEngine(adapter)
    assert (await engine.store_entity(rec("price", 1, 0, "o0"), "dk-0#0"))["status"] == "written"
    # a writer crashed after writing the delivery record of version 2, before history and snapshot
    ghost = DeliveryRecord(
        delivery_key="dk-1#0",
        recorded_at=utcnow(),
        acks=[
            {
                "entity": {"entity_type": "product", "canonical_key": KEY, "version": 2},
                "delivery_key": "dk-1#0",
            }
        ],
    )
    (tmp_path / "deliveries" / f"{key_digest('dk-1#0')}.json").write_bytes(dumps(delivery_to_json(ghost)))
    assert await adapter.get_delivery("dk-1#0") is None
    ack = await engine.store_entity(rec("price", 2, 5, "o1"), "dk-1#0")
    assert ack["status"] == "written"
    snap = await adapter.read_entity("product", KEY)
    assert snap is not None and snap.fields["price"] == 2
    assert (await engine.store_entity(rec("price", 2, 5, "o1"), "dk-1#0"))["status"] == "duplicate"


async def test_torn_history_line_is_ignored_in_jsonl(tmp_path: Path) -> None:
    adapter = await open_adapter(tmp_path, entities_format="jsonl")
    engine = StorageEngine(adapter)
    await engine.store_entity(rec("price", 1, 0, "o0"), "dk-0#0")
    path = tmp_path / "history" / "product" / f"{key_digest(KEY)}.jsonl"
    with open(path, "ab") as fh:  # noqa: ASYNC230
        fh.write(b'{"version": 2, "trunc')  # crash in the middle of an append
    await engine.store_entity(rec("price", 2, 1, "o1"), "dk-1#0")
    history, _ = await adapter.list_history("product", KEY, limit=10)
    assert [h.delivery_key for h in history] == ["dk-1#0", "dk-0#0"]
    lines = path.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[-1])["version"] == 2


async def test_stale_lock_is_broken_and_held_lock_times_out(tmp_path: Path) -> None:
    adapter = await open_adapter(tmp_path, lock_timeout_ms=300, lock_stale_ms=60_000)
    engine = StorageEngine(adapter)
    lock = tmp_path / "locks" / "entities" / "product" / f"{key_digest(KEY)}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text("other-host:1 0\n", encoding="utf-8")
    with pytest.raises(AdapterError) as err:
        await engine.store_entity(rec("price", 1, 0, "o0"), "dk-0#0")
    assert err.value.retryable is True
    old = time.time() - 3600
    os.utime(lock, (old, old))
    assert (await engine.store_entity(rec("price", 1, 0, "o0"), "dk-0#0"))["status"] == "written"
    assert not lock.exists()


async def test_prefix_and_invalid_options(tmp_path: Path) -> None:
    adapter = FilesystemAdapter()
    with pytest.raises(AdapterError):
        await adapter.open(conn(tmp_path), {"prefix": "../escape"})
    with pytest.raises(AdapterError):
        await adapter.open(ResolvedConnection("t", "filesystem", {}), {})
    adapter = await open_adapter(tmp_path, prefix="tenant/a")
    await StorageEngine(adapter).store_entity(rec("price", 1, 0, "o0"), "dk#0")
    assert (tmp_path / "tenant" / "a" / "entities" / "product" / f"{key_digest(KEY)}.json").is_file()
