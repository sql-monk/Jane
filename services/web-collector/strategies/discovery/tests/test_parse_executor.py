"""The actual sitemap parser keeps its configured slot through queued and running cancellation."""

from __future__ import annotations

import asyncio
import threading
from types import FrameType, ModuleType
from typing import Any

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("unsafe", [False, True], ids=["running-cancel", "late-unsafe-error"])
async def test_cancellation_keeps_actual_parse_worker_bound(discovery: ModuleType, unsafe: bool) -> None:
    parser = discovery.sitemap
    executor = parser._ParseExecutor(1)
    entered, release = threading.Event(), threading.Event()
    starts: list[bytes] = []
    finishes: list[bytes] = []
    valid = b"<urlset><url><loc>https://store.test/a</loc></url></urlset>"
    body = b'<!DOCTYPE urlset [<!ENTITY hidden "x">]><urlset/>' if unsafe else valid
    code = parser.parse_sitemap.__code__

    def profile(frame: FrameType, event: str, arg: Any) -> None:
        if frame.f_code == code:
            if event == "call":
                starts.append(frame.f_locals["body"])
                entered.set()
                assert release.wait(timeout=10)
            elif event == "return":
                finishes.append(frame.f_locals["body"])

    loop = asyncio.get_running_loop()
    errors: list[dict[str, Any]] = []
    old_handler = loop.get_exception_handler()
    old_profile = threading.getprofile()
    loop.set_exception_handler(lambda loop, context: errors.append(context))
    threading.setprofile(profile)
    tasks: list[asyncio.Task[Any]] = []
    try:
        running = asyncio.create_task(
            executor.parse(body, "https://store.test", max_bytes=4096, max_entries=10)
        )
        tasks.append(running)
        assert await asyncio.to_thread(entered.wait, 5)
        queued = asyncio.create_task(
            executor.parse(valid, "https://store.test", max_bytes=4096, max_entries=10)
        )
        tasks.append(queued)
        await asyncio.sleep(0)
        queued.cancel()
        with pytest.raises(asyncio.CancelledError):
            await queued
        running.cancel()
        with pytest.raises(asyncio.CancelledError):
            await running
        replacement = asyncio.create_task(
            executor.parse(valid, "https://store.test", max_bytes=4096, max_entries=10)
        )
        tasks.append(replacement)
        await asyncio.sleep(0)
        assert starts == [body] and not finishes
        assert executor._available == 0 and len(executor._waiters) == 1
        release.set()
        result = await asyncio.wait_for(replacement, timeout=10)
        assert [entry.loc for entry in result.urls] == ["https://store.test/a"]
        assert starts == [body, valid] and finishes == [body, valid]
        assert executor._available == 1 and not executor._waiters
        await asyncio.sleep(0)
        assert errors == []  # late UnsafeDocument is observed even after its original job was cancelled
    finally:
        release.set()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        executor._executor.shutdown(wait=True)
        threading.setprofile(old_profile)
        loop.set_exception_handler(old_handler)


def test_parse_worker_limit_is_positive(discovery: ModuleType) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        discovery.sitemap._ParseExecutor(0)


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["complete", "error", "cancel"])
async def test_completed_parse_holds_slot_until_consumer_closes(discovery: ModuleType, outcome: str) -> None:
    executor = discovery.sitemap._ParseExecutor(1)
    body = b"<urlset><url><loc>https://store.test/a</loc></url></urlset>"
    entered, release = asyncio.Event(), asyncio.Event()

    async def consume() -> None:
        async with executor.document(body, "https://store.test", max_bytes=4096, max_entries=10) as doc:
            assert [entry.loc for entry in doc.urls] == ["https://store.test/a"]
            entered.set()
            await release.wait()
            if outcome == "error":
                raise ValueError("consumer failed")

    consumer = asyncio.create_task(consume())
    replacement: asyncio.Task[Any] | None = None
    try:
        await asyncio.wait_for(entered.wait(), timeout=5)
        replacement = asyncio.create_task(
            executor.parse(body, "https://store.test", max_bytes=4096, max_entries=10)
        )
        await asyncio.sleep(0)
        assert executor._available == 0 and len(executor._waiters) == 1
        assert not replacement.done()  # the first CPU task ended, but its real document is still owned
        if outcome == "cancel":
            consumer.cancel()
            with pytest.raises(asyncio.CancelledError):
                await consumer
        else:
            release.set()
            if outcome == "error":
                with pytest.raises(ValueError, match="consumer failed"):
                    await consumer
            else:
                await consumer
        result = await asyncio.wait_for(replacement, timeout=5)
        assert [entry.loc for entry in result.urls] == ["https://store.test/a"]
        assert executor._available == 1 and not executor._waiters
    finally:
        release.set()
        consumer.cancel()
        await asyncio.gather(consumer, return_exceptions=True)
        if replacement is not None:
            replacement.cancel()
            await asyncio.gather(replacement, return_exceptions=True)
        executor._executor.shutdown(wait=True)
