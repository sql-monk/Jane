"""Backpressure status remains owned by the current collection lease."""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from types import SimpleNamespace
from typing import cast

from jane_web_collector.crawler import CrawlRun
from jane_web_collector.state import StateStore


async def _until_paused(state: StateStore, collection_id: str) -> None:
    for _ in range(100):
        record = state.get_collection(collection_id)
        assert record is not None
        if record["paused"]:
            return
        await asyncio.sleep(0.01)
    raise AssertionError("collection did not pause")


async def test_old_lease_holder_cannot_clear_new_backpressure_pause(tmp_path: Path) -> None:
    state = StateStore(tmp_path / "state.db")
    collection_id = "lease-handoff"
    state.create_collection(
        collection_id,
        state_key=collection_id,
        status="running",
        request={},
        rules={},
        rules_ref=None,
        created_at="2026-09-30T00:00:00Z",
        effective_limits={},
    )
    with state.tx() as db:
        for seq in (1, 2):
            state.append_material(db, collection_id, f"observation-{seq}", {})

    def waiter(owner: str) -> CrawlRun:
        return cast(
            CrawlRun,
            SimpleNamespace(
                state=state,
                collection_id=collection_id,
                fence=(collection_id, owner),
                limits=SimpleNamespace(
                    queue=SimpleNamespace(max_unacked_materials=2),
                    collector=SimpleNamespace(backpressure_poll_ms=1000),
                ),
                deps=SimpleNamespace(ack_events={}),
                cancelled=False,
                _backpressure_waiters=0,
            ),
        )

    assert state.claim(collection_id, "owner-a", 10)
    owner_a = waiter("owner-a")
    task_a = asyncio.create_task(CrawlRun._wait_backpressure(owner_a))
    task_b: asyncio.Task[None] | None = None
    try:
        await _until_paused(state, collection_id)
        state.release(collection_id, "owner-a")
        assert state.claim(collection_id, "owner-b", 10)
        owner_b = waiter("owner-b")
        task_b = asyncio.create_task(CrawlRun._wait_backpressure(owner_b))
        for _ in range(100):
            if owner_b._backpressure_waiters:
                break
            await asyncio.sleep(0.01)
        assert owner_b._backpressure_waiters == 1
        record = state.get_collection(collection_id)
        assert record is not None and record["paused"] == 1

        task_a.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task_a
        assert not task_b.done()
        assert state.unacked_count(collection_id) == 2
        record = state.get_collection(collection_id)
        assert record is not None and record["paused"] == 1

        assert state.ack(collection_id, 1) == 1
        owner_b.deps.ack_events[collection_id].set()
        await asyncio.wait_for(task_b, timeout=1)
        record = state.get_collection(collection_id)
        assert record is not None and record["paused"] == 0
    finally:
        for task in (task_a, task_b):
            if task is not None and not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
        state.close()
