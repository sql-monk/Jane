"""jane-kit ``JobStore`` and ``IdempotencyStore`` on the collector's own SQLite state (shared by instances)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_kit.jobs import Job

from .state import StateStore

__all__ = ["SqliteIdempotencyStore", "SqliteJobStore"]


class SqliteJobStore:
    def __init__(self, state: StateStore) -> None:
        self.state = state

    async def create(self, job: Job) -> None:
        existing = self.state.get_job(job.job_id)
        if existing is not None:  # resumed after a restart: keep the original creation data
            old = Job.model_validate_json(existing)
            job = job.model_copy(
                update={
                    "created_at": old.created_at,
                    "started_at": old.started_at,
                    "idempotency_key": old.idempotency_key,
                    "labels": old.labels,
                    "progress": old.progress,
                }
            )
        self.state.put_job(job.job_id, job.model_dump_json())

    async def get(self, job_id: str) -> Job | None:
        body = self.state.get_job(job_id)
        return Job.model_validate_json(body) if body else None

    async def save(self, job: Job) -> None:
        job = job.model_copy(update={"updated_at": datetime.now(UTC)})
        self.state.put_job(job.job_id, job.model_dump_json())


class SqliteIdempotencyStore:
    def __init__(self, state: StateStore) -> None:
        self.state = state

    async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
        row = self.state.idem_begin(key, fingerprint, ttl_s)
        if row is None:
            return None
        response = None
        if row["response"]:
            data = json.loads(row["response"])
            response = StoredResponse(data["status_code"], data["body"], data.get("headers") or {})
        return IdempotencyRecord(row["key"], row["fingerprint"], row["state"], row["expires_at"], response)

    async def complete(self, key: str, response: StoredResponse) -> None:
        self.state.idem_complete(
            key,
            json.dumps(
                {
                    "status_code": response.status_code,
                    "body": response.body,
                    "headers": dict(response.headers),
                }
            ),
        )

    async def release(self, key: str) -> None:
        self.state.idem_release(key)
