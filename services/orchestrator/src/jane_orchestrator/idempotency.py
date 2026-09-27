"""``Idempotency-Key`` storage in the orchestrator DB (jane-kit ``IdempotencyStore`` protocol), so several
API instances share it."""

from __future__ import annotations

from datetime import timedelta

from starlette.concurrency import run_in_threadpool

from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_orchestrator.db import Database, Jsonb

__all__ = ["PgIdempotencyStore"]


class PgIdempotencyStore:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        with self.db.tx() as conn:
            conn.execute("DELETE FROM idempotency_keys WHERE key = %s AND expires_at <= now()", (key,))
            row = conn.execute(
                "INSERT INTO idempotency_keys (key, fingerprint, state, expires_at)"
                " VALUES (%s, %s, 'in_progress', now() + %s) ON CONFLICT (key) DO NOTHING RETURNING key",
                (key, fingerprint, timedelta(seconds=ttl_s)),
            ).fetchone()
            if row is not None:
                return None
            existing = conn.execute("SELECT * FROM idempotency_keys WHERE key = %s", (key,)).fetchone()
        if existing is None:  # expired and removed concurrently: treat as in progress, the client retries
            return IdempotencyRecord(key, fingerprint, "in_progress", 0.0)
        response = None
        if existing["state"] == "completed":
            response = StoredResponse(
                int(existing["status_code"]), existing["body"], dict(existing["headers"] or {})
            )
        return IdempotencyRecord(
            key, existing["fingerprint"], existing["state"], existing["expires_at"].timestamp(), response
        )

    def _complete(self, key: str, response: StoredResponse) -> None:
        with self.db.tx() as conn:
            conn.execute(
                "UPDATE idempotency_keys SET state = 'completed', status_code = %s, body = %s, headers = %s"
                " WHERE key = %s",
                (response.status_code, Jsonb(response.body), Jsonb(dict(response.headers)), key),
            )

    def _release(self, key: str) -> None:
        with self.db.tx() as conn:
            conn.execute("DELETE FROM idempotency_keys WHERE key = %s AND state = 'in_progress'", (key,))

    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        result: IdempotencyRecord | None = await run_in_threadpool(self._begin, key, fingerprint, ttl_s)
        return result

    async def complete(self, key: str, response: StoredResponse) -> None:
        await run_in_threadpool(self._complete, key, response)

    async def release(self, key: str) -> None:
        await run_in_threadpool(self._release, key)
