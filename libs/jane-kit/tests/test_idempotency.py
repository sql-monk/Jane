from __future__ import annotations

import asyncio

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient

from jane_kit.config import JaneSettings
from jane_kit.errors import BadRequest
from jane_kit.idempotency import (
    IdempotencyInProgress,
    IdempotencyKeyReused,
    IdempotencyLimits,
    InMemoryIdempotencyStore,
    StoredResponse,
    idempotent,
    run_idempotent,
)
from jane_kit.service import create_app


async def test_second_call_replays_without_running_handler() -> None:
    store = InMemoryIdempotencyStore()
    calls = 0

    async def handler() -> StoredResponse:
        nonlocal calls
        calls += 1
        return StoredResponse(201, {"n": calls})

    r1, replayed1 = await run_idempotent(store, "k", "fp", handler)
    r2, replayed2 = await run_idempotent(store, "k", "fp", handler)
    assert (r1.body, replayed1) == ({"n": 1}, False)
    assert (r2.body, replayed2) == ({"n": 1}, True)
    assert calls == 1


async def test_reuse_with_different_request_rejected() -> None:
    store = InMemoryIdempotencyStore()

    async def handler() -> StoredResponse:
        return StoredResponse(200, {})

    await run_idempotent(store, "k", "fp1", handler)
    with pytest.raises(IdempotencyKeyReused):
        await run_idempotent(store, "k", "fp2", handler)


async def test_concurrent_duplicate_gets_in_progress() -> None:
    store = InMemoryIdempotencyStore()
    gate = asyncio.Event()

    async def slow() -> StoredResponse:
        await gate.wait()
        return StoredResponse(200, {"ok": True})

    first = asyncio.create_task(run_idempotent(store, "k", "fp", slow))
    await asyncio.sleep(0)
    with pytest.raises(IdempotencyInProgress):
        await run_idempotent(store, "k", "fp", slow)
    gate.set()
    assert (await first)[0].body == {"ok": True}


async def test_failed_handler_releases_key() -> None:
    store = InMemoryIdempotencyStore()

    async def failing() -> StoredResponse:
        raise RuntimeError("transient")

    async def ok() -> StoredResponse:
        return StoredResponse(200, {"ok": True})

    with pytest.raises(RuntimeError):
        await run_idempotent(store, "k", "fp", failing)
    response, replayed = await run_idempotent(store, "k", "fp", ok)
    assert response.body == {"ok": True} and not replayed


async def test_ttl_expiry_and_eviction_from_limits() -> None:
    now = [0.0]
    store = InMemoryIdempotencyStore(
        IdempotencyLimits(ttl_s=10, in_memory_max_entries=2), clock=lambda: now[0]
    )
    limits = store.limits
    counter = 0

    async def handler() -> StoredResponse:
        nonlocal counter
        counter += 1
        return StoredResponse(200, counter)

    await run_idempotent(store, "a", "fp", handler, limits)
    now[0] = 11
    response, replayed = await run_idempotent(store, "a", "fp", handler, limits)
    assert response.body == 2 and not replayed
    await run_idempotent(store, "b", "fp", handler, limits)
    await run_idempotent(store, "c", "fp", handler, limits)
    await run_idempotent(store, "d", "fp", handler, limits)
    assert len(store._records) <= 2


async def test_key_length_limit() -> None:
    store = InMemoryIdempotencyStore()

    async def handler() -> StoredResponse:
        return StoredResponse(200, None)

    with pytest.raises(BadRequest):
        await run_idempotent(store, "x" * 11, "fp", handler, IdempotencyLimits(max_key_length=10))


def test_fastapi_helper_end_to_end() -> None:
    app = create_app(JaneSettings(), configure_logs=False)
    store = InMemoryIdempotencyStore()
    created: list[int] = []

    @app.post("/v1/orders")
    async def create_order(request: Request) -> Response:
        async def handler() -> StoredResponse:
            created.append(1)
            return StoredResponse(201, {"order": len(created)}, {"Location": f"/v1/orders/{len(created)}"})

        return await idempotent(request, store, handler)

    c = TestClient(app)
    r1 = c.post("/v1/orders", json={"a": 1}, headers={"Idempotency-Key": "o-1"})
    r2 = c.post("/v1/orders", json={"a": 1}, headers={"Idempotency-Key": "o-1"})
    r3 = c.post("/v1/orders", json={"a": 2}, headers={"Idempotency-Key": "o-1"})
    r4 = c.post("/v1/orders", json={"a": 1})
    assert r1.status_code == r2.status_code == 201
    assert r1.json() == r2.json() == {"order": 1}
    assert r2.headers["Idempotent-Replayed"] == "true"
    assert r2.headers["Location"] == "/v1/orders/1"
    assert r3.status_code == 422 and r3.json()["code"] == "idempotency_key_reused"
    assert r4.status_code == 400 and r4.json()["code"] == "idempotency_key_missing"
    assert len(created) == 1
