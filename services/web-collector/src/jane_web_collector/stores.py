"""jane-kit ``JobStore`` and ``IdempotencyStore`` on the collector's own SQLite state (shared by instances)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from jane_kit.idempotency import IdempotencyRecord, StoredResponse
from jane_kit.jobs import Job, JobStatus

from .state import StateStore

__all__ = ["SqliteIdempotencyStore", "SqliteJobStore"]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


TERMINAL = frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED})


class SqliteJobStore:
    """Jobs of collections are shared by all instances on the state file.

    * Only the instance holding a collection's lease writes its job; others may only request cancellation.
    * A terminal job status is stored only when the collection itself already has that status (written by
      the run's final lease-fenced transaction or by the owner on failure/cancellation). A run that stopped
      without finishing (lease lost, graceful shutdown) therefore never makes the job look finished.
    """

    def __init__(self, state: StateStore, instance_id: str) -> None:
        self.state = state
        self.instance_id = instance_id

    def _foreign(self, job: Job) -> bool:
        # the owner column changes only by claiming the lease, so any other writer is a run that lost it
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
                }
            )
        self.state.put_job(job.job_id, job.model_dump_json())

    async def get(self, job_id: str) -> Job | None:
        body = self.state.get_job(job_id)
        return Job.model_validate_json(body) if body else None

    async def save(self, job: Job) -> None:
        collection = self.state.get_status(job.job_id)
        if collection is not None:
            if job.status != JobStatus.CANCELLING and self._foreign(job):
                return  # a run that lost its lease must not overwrite the new owner's job
            if job.status in TERMINAL and job.status.value != collection:
                if job.status == JobStatus.CANCELLED and collection == "queued":
                    # cancelled before it started: nothing ran, the collection ends here as well
                    self.state.set_status(job.job_id, "cancelled", finished_at=_now_iso())
                else:
                    return  # the collection is not finished: keep the job non-terminal (it will be resumed)
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
