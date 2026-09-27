"""jane-kit ``JobStore`` and ``IdempotencyStore`` on the collector's own SQLite state (shared by instances)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_kit.jobs import TERMINAL_STATUSES, Job, JobStatus

from .state import StateStore

__all__ = ["SqliteIdempotencyStore", "SqliteJobStore"]


class SqliteJobStore:
    """Jobs of collections, shared by all instances on the state file.

    The collection row (written in lease-fenced transactions) is the source of truth; the job mirrors it:

    * only the instance holding a collection's lease writes its job; others may only request ``cancelling``;
    * a terminal job status is stored only if the collection already has that status. A run interrupted by
      a graceful shutdown (the runner reports ``cancelled``) leaves the collection ``running`` and
      resumable by another instance, so such a report is ignored.
    """

    def __init__(self, state: StateStore, instance_id: str) -> None:
        self.state = state
        self.instance_id = instance_id

    def _foreign(self, job: Job) -> bool:
        owner, _ = self.state.lease(job.job_id)
        return owner is not None and owner != self.instance_id

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
                    "cancellation": old.cancellation,
                    "status": JobStatus.CANCELLING if old.status == JobStatus.CANCELLING else job.status,
                }
            )
        self.state.put_job(job.job_id, job.model_dump_json())

    async def get(self, job_id: str) -> Job | None:
        body = self.state.get_job(job_id)
        return Job.model_validate_json(body) if body else None

    async def save(self, job: Job) -> None:
        if job.status != JobStatus.CANCELLING and self._foreign(job):
            return  # a run that lost its lease must not overwrite the new owner's job
        if job.status in TERMINAL_STATUSES:
            collection = self.state.get_status(job.job_id)
            if collection is not None and collection != job.status.value:
                if collection not in {s.value for s in TERMINAL_STATUSES}:
                    return
                job = job.model_copy(update={"status": JobStatus(collection)})
        elif job.status != JobStatus.CANCELLING:
            current = await self.get(job.job_id)
            if current is not None and current.status == JobStatus.CANCELLING:
                # progress of a run whose cancellation was requested elsewhere keeps the cancellation visible
                job = job.model_copy(
                    update={"status": JobStatus.CANCELLING, "cancellation": current.cancellation}
                )
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
