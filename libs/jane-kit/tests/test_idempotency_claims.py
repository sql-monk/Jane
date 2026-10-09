"""Real shared-store regressions: request TTL, same-process takeover and async claim fencing."""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import Request, Response
from psycopg import sql
from psycopg.rows import dict_row

from jane_kit.config import JaneSettings
from jane_kit.devstack import load_stack
from jane_kit.idempotency import (
    IdempotencyInProgress,
    StoredResponse,
    fingerprint,
    idempotent,
    run_idempotent,
)
from jane_kit.service import create_app
from jane_kit.stores.postgres import PgDatabase, PgIdempotencyStore, migrate
from jane_kit.stores.sqlite import SqliteDatabase, SqliteIdempotencyStore


@dataclass
class Claims:
    db: SqliteDatabase | PgDatabase
    store: SqliteIdempotencyStore | PgIdempotencyStore
    schema: str | None = None

    def row(self, key: str = "k") -> dict[str, Any]:
        if isinstance(self.db, SqliteDatabase):
            with self.db.tx() as db:
                sqlite_row = db.execute("SELECT * FROM idempotency WHERE key = ?", (key,)).fetchone()
                assert sqlite_row is not None, "the current claim must not be deleted by a stale request"
                return dict(sqlite_row)
        assert self.schema is not None
        with self.db.tx() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                sql.SQL("SELECT * FROM {} WHERE key = %s").format(sql.Identifier(self.schema, "idempotency")),
                (key,),
            )
            pg_row = cur.fetchone()
            assert pg_row is not None, "the current claim must not be deleted by a stale request"
            row = dict(pg_row)
        for column in ("expires_at", "lease_until"):
            if row[column] is not None:
                row[column] = row[column].timestamp()
        return row

    def expire(self, column: str = "lease_until") -> None:
        assert column in {"lease_until", "expires_at"}
        if isinstance(self.db, SqliteDatabase):
            with self.db.tx() as db:
                db.execute(f"UPDATE idempotency SET {column} = ?", (time.time() - 1,))
        else:
            assert self.schema is not None
            with self.db.tx() as db:
                db.execute(
                    sql.SQL("UPDATE {} SET {} = clock_timestamp() - interval '1 second'").format(
                        sql.Identifier(self.schema, "idempotency"), sql.Identifier(column)
                    )
                )

    def legacy_claim(self) -> None:
        if isinstance(self.db, SqliteDatabase):
            with self.db.tx() as db:
                db.execute("UPDATE idempotency SET lease_until = NULL, owner = NULL, token = NULL")
        else:
            assert self.schema is not None
            with self.db.tx() as conn:
                conn.execute(
                    sql.SQL("UPDATE {} SET lease_until = NULL, owner = NULL, token = NULL").format(
                        sql.Identifier(self.schema, "idempotency")
                    )
                )


@pytest.fixture(
    params=[
        "sqlite",
        pytest.param("split", marks=pytest.mark.integration),
        pytest.param("json", marks=pytest.mark.integration),
    ]
)
def claims(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[Claims]:
    if request.param == "sqlite":
        sqlite = SqliteDatabase(tmp_path / "claims.sqlite", busy_timeout_ms=5_000)
        store = SqliteIdempotencyStore(sqlite, owner="one-service", in_progress_lease_s=60)
        store.migrate()
        try:
            yield Claims(sqlite, store)
        finally:
            sqlite.close()
        return
    stack = load_stack()
    dsn = os.environ.get("JANE_KIT_PG_DSN") or (stack.get("postgres", "dsn") if stack else None)
    if dsn is None:
        pytest.skip("no PostgreSQL: set JANE_KIT_PG_DSN or run just up --project <p> postgres")
    pg = PgDatabase(dsn, max_size=8, connect_timeout_ms=10_000)
    pg.open()
    schema = "claims_" + uuid.uuid4().hex[:10]
    pg_store = PgIdempotencyStore(
        pg.tx, owner="one-service", in_progress_lease_s=60, schema=schema, layout=request.param
    )
    try:
        migrate(pg.tx, schema, pg_store, schema=schema)
        yield Claims(pg, pg_store, schema)
    finally:
        with pg.tx() as db:
            db.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))
        pg.close()


async def test_lease_expiry_keeps_fingerprint_until_key_ttl_at_http_boundary(claims: Claims) -> None:
    app = create_app(JaneSettings(), configure_logs=False)
    calls = 0

    @app.post("/v1/orders")
    async def create_order(request: Request) -> Response:
        async def handler() -> StoredResponse:
            nonlocal calls
            calls += 1
            return StoredResponse(201, {"order": calls}, {"Location": f"/v1/orders/{calls}"})

        return await idempotent(request, claims.store, handler)

    original = b'{"a":1}'
    assert await claims.store.begin("k", fingerprint("POST", "/v1/orders", original), 86_400) is None
    before = claims.row()
    claims.expire()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Idempotency-Key": "k", "Content-Type": "application/json"}
        rejected = await client.post("/v1/orders", content=b'{"a":2}', headers=headers)
        assert rejected.status_code == 422 and rejected.json()["code"] == "idempotency_key_reused"
        assert calls == 0
        after_reject = claims.row()
        assert (after_reject["token"], after_reject["fingerprint"], after_reject["expires_at"]) == (
            before["token"],
            before["fingerprint"],
            before["expires_at"],
        )
        recovered = await client.post("/v1/orders", content=original, headers=headers)
        assert recovered.status_code == 201 and calls == 1
        assert claims.row()["expires_at"] == before["expires_at"]
        assert claims.row()["token"] != before["token"]
        replay = await client.post("/v1/orders", content=original, headers=headers)
        assert replay.json() == recovered.json() and replay.headers["Idempotency-Replayed"] == "true"
        assert replay.headers["Location"] == "/v1/orders/1" and calls == 1
        claims.expire("expires_at")
        reused = await client.post("/v1/orders", content=b'{"a":2}', headers=headers)
        assert reused.status_code == 201 and reused.json() == {"order": 2} and calls == 2


@pytest.mark.parametrize("old_action", ["complete", "release"])
@pytest.mark.parametrize("expiry", ["lease_until", "expires_at"])
async def test_same_store_concurrent_requests_fence_old_claim_and_keep_new_heartbeat(
    claims: Claims, old_action: str, expiry: str
) -> None:
    store = claims.store
    old_entered, new_entered = asyncio.Event(), asyncio.Event()
    old_finish, new_finish = asyncio.Event(), asyncio.Event()
    captured: dict[str, dict[str, Any]] = {}

    async def old_handler() -> StoredResponse:
        captured["old"] = claims.row()
        old_entered.set()
        await old_finish.wait()
        if old_action == "release":
            raise RuntimeError("old request failed after takeover")
        return StoredResponse(202, {"from": "stale-request"})

    async def new_handler() -> StoredResponse:
        captured["new"] = claims.row()
        new_entered.set()
        await new_finish.wait()
        return StoredResponse(202, {"from": "current-request"}, {"Location": "/v1/jobs/current"})

    # Both adapters really await to_thread; each handler must retain its own immutable token.
    old = asyncio.create_task(run_idempotent(store, "k", "original-body", old_handler))
    new = None
    try:
        await asyncio.wait_for(old_entered.wait(), 5)
        claims.expire(expiry)
        new_fp = "original-body" if expiry == "lease_until" else "changed-after-key-ttl"
        new = asyncio.create_task(run_idempotent(store, "k", new_fp, new_handler))
        await asyncio.wait_for(new_entered.wait(), 5)
        assert captured["old"]["token"] != captured["new"]["token"]
        if expiry == "lease_until":
            assert captured["old"]["expires_at"] == captured["new"]["expires_at"]
        old_finish.set()
        if old_action == "release":
            with pytest.raises(RuntimeError, match="old request failed after takeover"):
                await old
        else:
            await old
        current = claims.row()
        assert current["state"] == "in_progress" and current["token"] == captured["new"]["token"]
        assert await store.heartbeat() == 1  # stale completion/release must not unregister the new token
        assert claims.row()["lease_until"] >= current["lease_until"]
        new_finish.set()
        current_response, replayed = await new
        assert not replayed and current_response.body == {"from": "current-request"}

        async def must_not_run() -> StoredResponse:
            raise AssertionError("a completed response must replay")

        response, replayed = await run_idempotent(store, "k", new_fp, must_not_run)
        assert replayed and response == current_response
        assert await store.heartbeat() == 0
    finally:
        old_finish.set()
        new_finish.set()
        await asyncio.gather(*(task for task in (old, new) if task is not None), return_exceptions=True)


async def test_same_body_takeover_is_atomic_between_request_contexts(claims: Claims) -> None:
    assert await claims.store.begin("k", "fp", 86_400) is None
    before = claims.row()
    claims.expire()
    entered, finish = asyncio.Event(), asyncio.Event()
    calls = 0

    async def handler() -> StoredResponse:
        nonlocal calls
        calls += 1
        entered.set()
        await finish.wait()
        return StoredResponse(200, {"calls": calls})

    tasks = [asyncio.create_task(run_idempotent(claims.store, "k", "fp", handler)) for _ in range(6)]
    try:
        await asyncio.wait_for(entered.wait(), 5)
        # Wait until every contender has either reached the handler or returned 409.
        while sum(task.done() for task in tasks) < 5:
            await asyncio.wait_for(
                asyncio.wait(
                    [task for task in tasks if not task.done()], return_when=asyncio.FIRST_COMPLETED
                ),
                5,
            )
        assert calls == 1 and claims.row()["expires_at"] == before["expires_at"]
        # The parent context still holds the OLD token inherited by child tasks. Its release is fenced.
        await claims.store.release("k")
        assert claims.row()["state"] == "in_progress" and await claims.store.heartbeat() == 1
        finish.set()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        assert sum(isinstance(result, IdempotencyInProgress) for result in results) == 5
        assert sum(isinstance(result, tuple) for result in results) == 1
    finally:
        finish.set()
        await asyncio.gather(*tasks, return_exceptions=True)


async def test_legacy_null_lease_keeps_fingerprint_and_key_ttl(claims: Claims) -> None:
    assert await claims.store.begin("k", "fp", 86_400) is None
    claims.legacy_claim()
    before = claims.row()
    record = await claims.store.begin("k", "other", 86_400)
    assert record is not None and record.fingerprint == "fp" and record.state == "in_progress"
    assert claims.row() == before


def test_sync_adapter_claim_complete_and_release(claims: Claims) -> None:
    store = claims.store
    assert store.begin_sync("k", "fp", 86_400) is None
    response = StoredResponse(202, {"job_id": "current"}, {"Location": "/v1/jobs/current"})
    store.complete_sync("k", response)
    replay = store.begin_sync("k", "fp", 86_400)
    assert replay is not None and replay.response == response
    assert store.begin_sync("retry", "fp", 86_400) is None
    store.release_sync("retry")
    assert store.begin_sync("retry", "fp", 86_400) is None
