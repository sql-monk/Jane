"""Long-running operations per WP-00 ``schemas/common/job.schema.json`` and ``common.yaml`` pathItems.

* ``202 Accepted`` + ``Job`` body + ``Location: /v1/jobs/{job_id}`` (:func:`accepted`);
* ``GET /v1/jobs/{job_id}``; ``POST /v1/jobs/{job_id}/cancel`` -> 202 (``cancelling``) or 200 if
  the job is already terminal (:func:`jobs_router`);
* statuses ``queued -> running -> succeeded|failed``; ``queued|running -> cancelling -> cancelled``.

:class:`InMemoryJobStore` is for a single instance and tests. For several instances use the shared stores of
:mod:`jane_kit.stores` (PostgreSQL / SQLite, with leases and fencing) on the service's own database;
:class:`JobRunner` works with any store. Every store follows the same write rules (:func:`decide_save`):

* a terminal job (``succeeded|failed|cancelled``) never changes again;
* any instance may request cancellation (``cancelling``) of a live job; every other write comes only from the
  instance that owns the job and only while its lease is live (fencing: a run that lost the lease cannot
  overwrite the job);
* a cancellation committed first is kept: progress of the run keeps ``cancelling``, a later success or failure
  of a stale snapshot ends the job ``cancelled``;
* a job whose owner stopped renewing its lease ends ``failed`` (``service_unavailable``, retryable) - or
  ``cancelled`` if cancellation had already been requested (:func:`orphaned`).
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable, Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from jane_kit.config import Limits, contract_field
from jane_kit.errors import JaneError, NotFound, Problem, ServiceUnavailable, Timeout
from jane_kit.logs import bind_context

__all__ = [
    "TERMINAL_STATUSES",
    "InMemoryJobStore",
    "Job",
    "JobCancelRequest",
    "JobCancellation",
    "JobCancelledError",
    "JobContext",
    "JobLimits",
    "JobPosition",
    "JobProgress",
    "JobRunner",
    "JobStatus",
    "JobStore",
    "accepted",
    "decide_save",
    "jobs_router",
    "orphaned",
    "resumed",
]

log = logging.getLogger(__name__)


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    CANCELLING = "cancelling"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATUSES = frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED})


def _now() -> datetime:
    return datetime.now(UTC)


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow")


class JobProgress(_Model):
    completed: int | None = Field(default=None, ge=0)
    total: int | None = Field(default=None, ge=0)
    unit: str | None = None
    message: str | None = None
    counters: dict[str, int] | None = None
    updated_at: datetime | None = None


class JobCancellation(_Model):
    requested_at: datetime
    requested_by: str | None = None
    reason: str | None = None


class JobCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = Field(default=None, max_length=1000)


class Job(_Model):
    job_id: str
    kind: str = Field(pattern=r"^[a-z][a-z0-9_]{1,63}$")
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    progress: JobProgress | None = None
    result: dict[str, Any] | None = None
    result_ref: dict[str, Any] | None = None
    """``ContentRef`` of a large result (passed by reference, not inline)."""
    error: Problem | None = None
    cancellation: JobCancellation | None = None
    idempotency_key: str | None = Field(default=None, max_length=255)
    links: dict[str, str] | None = None
    labels: dict[str, str] | None = None

    def wire(self) -> dict[str, Any]:
        """JSON body as in the contract (``None`` fields omitted)."""
        return self.model_dump(mode="json", exclude_none=True)


class JobLimits(Limits):
    max_concurrent_jobs: int = Field(default=4, ge=1)
    """Jobs executing at the same time in one instance; the rest wait in ``queued``."""
    max_queued_jobs: int = Field(default=1000, ge=0)
    """Beyond this, submit fails with 503 ``service_unavailable`` (backpressure, retryable)."""
    job_timeout_ms: int = Field(default=3_600_000, ge=1)
    """Wall-clock limit per job; exceeded -> ``failed`` with code ``timeout``."""
    job_retention_seconds: int = contract_field("transfer.job_retention_seconds", 86_400, ge=60)
    """Contract ``limits.transfer.job_retention_seconds``: finished jobs are kept at least this long."""
    queue_full_retry_after_seconds: int = Field(default=1, ge=0)
    """``Retry-After`` sent with 503 when the job queue is full."""


class JobCancelledError(Exception):
    """Raised inside a job by :meth:`JobContext.check_cancelled`."""


class JobStore(Protocol):
    async def create(self, job: Job) -> None: ...
    async def get(self, job_id: str) -> Job | None: ...
    async def save(self, job: Job) -> None: ...


def decide_save(current: Job | None, new: Job, *, mine: bool, live: bool) -> Job | None:
    """The document a save of ``new`` writes over ``current`` (``None``: write nothing).

    ``mine`` - the saving instance owns the job; ``live`` - the owner's lease has not expired.
    """
    if current is None or not live or current.status in TERMINAL_STATUSES:
        return None
    now = _now()
    if new.status == JobStatus.CANCELLING:
        if current.status == JobStatus.CANCELLING:
            return None
        cancellation = new.cancellation or JobCancellation(requested_at=now)
        return current.model_copy(
            update={"status": JobStatus.CANCELLING, "cancellation": cancellation, "updated_at": now}
        )
    if not mine:
        return None
    if current.status == JobStatus.CANCELLING:
        if new.status in TERMINAL_STATUSES:
            # the cancellation was committed first: a success or failure of an older snapshot cannot erase it
            return new.model_copy(
                update={
                    "status": JobStatus.CANCELLED,
                    "cancellation": current.cancellation,
                    "finished_at": new.finished_at or now,
                    "result": None,
                    "error": None,
                    "updated_at": now,
                }
            )
        return new.model_copy(
            update={"status": JobStatus.CANCELLING, "cancellation": current.cancellation, "updated_at": now}
        )
    if new.status in TERMINAL_STATUSES and new.finished_at is None:
        return new.model_copy(update={"finished_at": now, "updated_at": now})
    return new.model_copy(update={"updated_at": now})


def orphaned(job: Job, owner: str | None) -> Job:
    """Terminal state of a job whose owner stopped renewing its lease (killed, hung or partitioned)."""
    now = _now()
    if job.status == JobStatus.CANCELLING:
        return job.model_copy(update={"status": JobStatus.CANCELLED, "finished_at": now, "updated_at": now})
    error = JaneError(
        f"instance {owner or 'unknown'} stopped while the job was {job.status} (job lease expired); "
        "retry the request",
        code="service_unavailable",
        retryable=True,
    )
    return job.model_copy(
        update={
            "status": JobStatus.FAILED,
            "finished_at": now,
            "updated_at": now,
            "error": error.to_problem(),
        }
    )


def resumed(existing: Job, new: Job) -> Job:
    """``new`` (a resubmission of the same ``job_id``) keeping what the existing job already recorded."""
    return new.model_copy(
        update={
            "created_at": existing.created_at,
            "started_at": existing.started_at,
            "idempotency_key": existing.idempotency_key,
            "labels": existing.labels,
            "progress": existing.progress,
            "cancellation": existing.cancellation,
            "status": JobStatus.CANCELLING if existing.status == JobStatus.CANCELLING else new.status,
            "updated_at": _now(),
        }
    )


JobPosition = tuple[datetime, str]
"""Cursor position in a job listing: ``(created_at, job_id)``, newest first."""


class InMemoryJobStore:
    """Single-instance store; drops finished jobs older than ``job_retention_seconds``.

    Writes follow :func:`decide_save` (this process owns every job and its lease never expires): a terminal job
    never changes, a committed cancellation is kept.
    """

    def __init__(self, limits: JobLimits | None = None) -> None:
        self.limits = limits or JobLimits()
        self._jobs: dict[str, Job] = {}

    def _gc(self) -> None:
        now = _now()
        for job_id, job in list(self._jobs.items()):
            if (
                job.finished_at
                and (now - job.finished_at).total_seconds() > self.limits.job_retention_seconds
            ):
                del self._jobs[job_id]

    async def create(self, job: Job) -> None:
        self._gc()
        existing = self._jobs.get(job.job_id)
        self._jobs[job.job_id] = (resumed(existing, job) if existing is not None else job).model_copy(
            deep=True
        )

    async def get(self, job_id: str) -> Job | None:
        job = self._jobs.get(job_id)
        return job.model_copy(deep=True) if job else None

    async def save(self, job: Job) -> None:
        saved = decide_save(self._jobs.get(job.job_id), job, mine=True, live=True)
        if saved is not None:
            self._jobs[job.job_id] = saved.model_copy(deep=True)

    async def page(
        self,
        kind: str,
        *,
        labels: Mapping[str, str],
        statuses: Iterable[str] | None,
        after: JobPosition | None,
        limit: int,
    ) -> list[Job]:
        """Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly
        after ``after`` (the same listing as :meth:`jane_kit.stores.PgJobStore.page`)."""
        self._gc()
        wanted = set(statuses or ())
        found = [
            job.model_copy(deep=True)
            for job in self._jobs.values()
            if job.kind == kind
            and all((job.labels or {}).get(k) == v for k, v in labels.items())
            and (not wanted or str(job.status) in wanted)
            and (after is None or (job.created_at, job.job_id) < after)
        ]
        found.sort(key=lambda j: (j.created_at, j.job_id), reverse=True)
        return found[:limit]


class JobContext:
    """Handle given to a running job for progress reporting and cooperative cancellation."""

    def __init__(self, runner: JobRunner, job_id: str) -> None:
        self._runner = runner
        self.job_id = job_id

    async def progress(
        self,
        completed: int | None = None,
        total: int | None = None,
        *,
        unit: str | None = None,
        message: str | None = None,
        counters: Mapping[str, int] | None = None,
    ) -> None:
        job = await self._runner.store.get(self.job_id)
        if job is None:
            return
        current = job.progress or JobProgress()
        update = {
            k: v
            for k, v in {
                "completed": completed,
                "total": total,
                "unit": unit,
                "message": message,
                "counters": dict(counters) if counters is not None else None,
            }.items()
            if v is not None
        }
        job.progress = current.model_copy(update={**update, "updated_at": _now()})
        await self._runner.store.save(job)

    async def cancelled(self) -> bool:
        job = await self._runner.store.get(self.job_id)
        return bool(job and job.status == JobStatus.CANCELLING)

    async def check_cancelled(self) -> None:
        if await self.cancelled():
            raise JobCancelledError(self.job_id)


JobFn = Callable[[JobContext], Awaitable[dict[str, Any] | None]]


class JobRunner:
    """Runs job coroutines in the current event loop with limits from config."""

    def __init__(
        self, store: JobStore | None = None, limits: JobLimits | None = None, jobs_path: str = "/v1/jobs"
    ) -> None:
        self.limits = limits or JobLimits()
        self.store: JobStore = store or InMemoryJobStore(self.limits)
        self.jobs_path = jobs_path.rstrip("/")
        self._slots = asyncio.Semaphore(self.limits.max_concurrent_jobs)
        self._tasks: dict[str, asyncio.Task[None]] = {}

    @property
    def active(self) -> int:
        return len(self._tasks)

    def location(self, job_id: str) -> str:
        return f"{self.jobs_path}/{job_id}"

    async def submit(
        self,
        kind: str,
        fn: JobFn,
        *,
        job_id: str | None = None,
        idempotency_key: str | None = None,
        labels: Mapping[str, str] | None = None,
    ) -> Job:
        if len(self._tasks) >= self.limits.max_concurrent_jobs + self.limits.max_queued_jobs:
            raise ServiceUnavailable(
                "job queue is full",
                retry_after_seconds=self.limits.queue_full_retry_after_seconds,
                details={"limit": self.limits.max_queued_jobs, "path": "max_queued_jobs"},
            )
        job_id = job_id or f"job_{uuid.uuid4().hex}"
        job = Job(
            job_id=job_id,
            kind=kind,
            idempotency_key=idempotency_key,
            labels=dict(labels) if labels else None,
            links={"self": self.location(job_id), "cancel": f"{self.location(job_id)}/cancel"},
        )
        await self.store.create(job)
        self._tasks[job.job_id] = asyncio.create_task(self._run(job.job_id, fn), name=f"job-{job.job_id}")
        return job

    async def _update(self, job_id: str, **update: Any) -> Job | None:
        job = await self.store.get(job_id)
        if job is None:
            return None
        job = job.model_copy(update=update)
        await self.store.save(job)
        return job

    async def _finish(self, job_id: str, status: JobStatus, **update: Any) -> None:
        await self._update(job_id, status=status, finished_at=_now(), **update)

    async def _run(self, job_id: str, fn: JobFn) -> None:
        ctx = JobContext(self, job_id)
        with bind_context(job_id=job_id):
            try:
                async with self._slots:
                    job = await self.store.get(job_id)
                    if job is None:
                        return
                    if job.status == JobStatus.CANCELLING:
                        await self._finish(job_id, JobStatus.CANCELLED)
                        return
                    await self._update(job_id, status=JobStatus.RUNNING, started_at=_now())
                    async with asyncio.timeout(self.limits.job_timeout_ms / 1000):
                        result = await fn(ctx)
                await self._finish(job_id, JobStatus.SUCCEEDED, result=result)
            except (asyncio.CancelledError, JobCancelledError):
                await self._finish(job_id, JobStatus.CANCELLED)
            except TimeoutError:
                err = Timeout(f"job exceeded job_timeout_ms={self.limits.job_timeout_ms}", retryable=False)
                await self._finish(job_id, JobStatus.FAILED, error=err.to_problem())
            except JaneError as exc:
                await self._finish(job_id, JobStatus.FAILED, error=exc.to_problem())
            except Exception as exc:
                log.exception("job failed")
                await self._finish(
                    job_id, JobStatus.FAILED, error=JaneError(f"{type(exc).__name__}: {exc}").to_problem()
                )
            finally:
                self._tasks.pop(job_id, None)

    async def get(self, job_id: str) -> Job:
        job = await self.store.get(job_id)
        if job is None:
            raise NotFound(f"job {job_id} not found")
        return job

    async def cancel(self, job_id: str, reason: str | None = None, requested_by: str | None = None) -> Job:
        """Request cancellation. Terminal jobs are returned unchanged (HTTP 200 in the contract)."""
        job = await self.get(job_id)
        if job.status in TERMINAL_STATUSES or job.status == JobStatus.CANCELLING:
            return job
        cancellation = JobCancellation(requested_at=_now(), requested_by=requested_by, reason=reason)
        job = await self._update(job_id, status=JobStatus.CANCELLING, cancellation=cancellation) or job
        task = self._tasks.get(job_id)
        if task is not None:
            task.cancel()  # queued: stops waiting for a slot; running: interrupts at the next await
        return job

    async def wait(self, job_id: str) -> Job:
        task = self._tasks.get(job_id)
        if task is not None:
            await asyncio.gather(task, return_exceptions=True)
        return await self.get(job_id)

    async def shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)


def accepted(job: Job, location: str | None = None, headers: Mapping[str, str] | None = None) -> JSONResponse:
    """``202 Accepted`` with the Job body and ``Location`` of the job resource."""
    loc = location or (job.links or {}).get("self") or f"/v1/jobs/{job.job_id}"
    return JSONResponse(job.wire(), status_code=202, headers={"Location": loc, **dict(headers or {})})


def jobs_router(runner: JobRunner) -> APIRouter:
    """``GET {jobs_path}/{job_id}`` and ``POST {jobs_path}/{job_id}/cancel`` (common.yaml Job, JobCancel)."""
    router = APIRouter(prefix=runner.jobs_path, tags=["jobs"])

    @router.get("/{job_id}", response_model=None, operation_id="getJob")
    async def get_job(job_id: str) -> JSONResponse:
        return JSONResponse((await runner.get(job_id)).wire())

    @router.post("/{job_id}/cancel", response_model=None, operation_id="cancelJob")
    async def cancel_job(job_id: str, body: JobCancelRequest | None = Body(default=None)) -> JSONResponse:  # noqa: B008
        before = await runner.get(job_id)
        if before.status in TERMINAL_STATUSES:
            return JSONResponse(before.wire(), status_code=200)
        job = await runner.cancel(job_id, reason=body.reason if body else None)
        return JSONResponse(job.wire(), status_code=202)

    return router
