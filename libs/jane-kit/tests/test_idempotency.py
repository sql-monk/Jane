from __future__ import annotations

import asyncio

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient

from jane_kit.config import JaneSettings
from jane_kit.errors import ValidationFailed
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
    with pytest.raises(IdempotencyKeyReused) as info:
        await run_idempotent(store, "k", "fp2", handler)
    assert (info.value.status, info.value.retryable) == (422, False)


async def test_concurrent_duplicate_gets_in_progress() -> None:
    store = InMemoryIdempotencyStore()
    gate = asyncio.Event()

    async def slow() -> StoredResponse:
        await gate.wait()
        return StoredResponse(200, {"ok": True})

    first = asyncio.create_task(run_idempotent(store, "k", "fp", slow))
    await asyncio.sleep(0)
    with pytest.raises(IdempotencyInProgress) as info:
        await run_idempotent(store, "k", "fp", slow)
    assert (info.value.status, info.value.retryable) == (409, True)
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
    limits = IdempotencyLimits(idempotency_ttl_seconds=60, in_memory_max_entries=2)
    store = InMemoryIdempotencyStore(limits, clock=lambda: now[0])
    counter = 0

    async def handler() -> StoredResponse:
        nonlocal counter
        counter += 1
        return StoredResponse(200, counter)

    await run_idempotent(store, "a", "fp", handler, limits)
    now[0] = 61
    response, replayed = await run_idempotent(store, "a", "fp", handler, limits)
    assert response.body == 2 and not replayed
    for key in ("b", "c", "d"):
        await run_idempotent(store, key, "fp", handler, limits)
    assert len(store) <= 2


@pytest.mark.parametrize("key", ["", "x" * 256, "has space", "кирилиця"])
async def test_key_format_from_contract(key: str) -> None:
    async def handler() -> StoredResponse:
        return StoredResponse(200, None)

    with pytest.raises(ValidationFailed):
        await run_idempotent(InMemoryIdempotencyStore(), key, "fp", handler)


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
    assert "Idempotency-Replayed" not in r1.headers
    assert r2.headers["Idempotency-Replayed"] == "true"
    assert r2.headers["Location"] == "/v1/orders/1"
    assert r3.status_code == 422 and r3.json()["code"] == "idempotency_key_reused"
    assert r4.status_code == 422 and r4.json()["errors"] == [
        {"parameter": "Idempotency-Key", "message": "required"}
    ]
    assert len(created) == 1
