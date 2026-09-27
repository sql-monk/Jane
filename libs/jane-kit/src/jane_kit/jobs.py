"""Long-running operations: ``202 Accepted`` + ``job_id``, state, progress, result, cancellation.

CONNECTION POINT (WP-00): the job resource schema, state names and the cancel endpoint come from
``contracts/``. Defaults here: states ``queued|running|succeeded|failed|cancelled``,
``GET {prefix}/{job_id}``, ``POST {prefix}/{job_id}/cancel``, ``Location`` header on 202.

:class:`InMemoryJobStore` is for a single instance and tests. For several instances a service
implements :class:`JobStore` on its own database; :class:`JobRunner` works with any store.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from jane_kit.config import Limits
from jane_kit.errors import Conflict, JaneError, LimitExceeded, NotFound, Problem
from jane_kit.logs import bind_context

__all__ = [
    "TERMINAL_STATES",
    "InMemoryJobStore",
    "Job",
    "JobCancelledError",
    "JobContext",
    "JobLimits",
    "JobRunner",
    "JobState",
    "JobStore",
    "accepted",
    "jobs_router",
]

log = logging.getLogger(__name__)


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATES = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})


def _now() -> datetime:
    return datetime.now(UTC)


class Job(BaseModel):
    job_id: str
    kind: str
    state: JobState = JobState.QUEUED
    progress: float | None = Field(default=None, ge=0.0, le=1.0)
    message: str | None = None
    result: Any = None
    result_ref: str | None = None
    """Link to a large result in blob storage (large payloads are passed by reference)."""
    error: Problem | None = None
    cancel_requested: bool = False
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class JobLimits(Limits):
    max_concurrent_jobs: int = Field(default=4, ge=1)
    """Jobs executing at the same time in one instance; the rest wait in ``queued``."""
    max_queued_jobs: int = Field(default=1000, ge=0)
    """Submitting beyond this returns 429 (backpressure) instead of growing memory."""
    job_timeout_s: float | None = Field(default=3600.0, gt=0)
    """Wall-clock limit per job; ``None`` disables it (only with an external watchdog)."""


class JobCancelledError(Exception):
    """Raised inside a job by :meth:`JobContext.check_cancelled`."""


class JobStore(Protocol):
    async def create(self, job: Job) -> None: ...
    async def get(self, job_id: str) -> Job | None: ...
    async def save(self, job: Job) -> None: ...


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    async def create(self, job: Job) -> None:
        self._jobs[job.job_id] = job.model_copy()

    async def get(self, job_id: str) -> Job | None:
        job = self._jobs.get(job_id)
        return job.model_copy() if job else None

    async def save(self, job: Job) -> None:
        self._jobs[job.job_id] = job.model_copy(update={"updated_at": _now()})


class JobContext:
    """Handle given to a running job for progress reporting and cooperative cancellation."""

    def __init__(self, runner: JobRunner, job_id: str) -> None:
        self._runner = runner
        self.job_id = job_id

    async def progress(self, fraction: float | None = None, message: str | None = None) -> None:
        job = await self._runner.store.get(self.job_id)
        if job is None:
            return
        update: dict[str, Any] = {}
        if fraction is not None:
            update["progress"] = max(0.0, min(1.0, fraction))
        if message is not None:
            update["message"] = message
        await self._runner.store.save(job.model_copy(update=update))

    async def cancelled(self) -> bool:
        job = await self._runner.store.get(self.job_id)
        return bool(job and job.cancel_requested)

    async def check_cancelled(self) -> None:
        if await self.cancelled():
            raise JobCancelledError(self.job_id)


JobFn = Callable[[JobContext], Awaitable[Any]]


class JobRunner:
    """Runs job coroutines in the current event loop with a concurrency limit from config."""

    def __init__(self, store: JobStore | None = None, limits: JobLimits | None = None) -> None:
        self.store: JobStore = store or InMemoryJobStore()
        self.limits = limits or JobLimits()
        self._slots = asyncio.Semaphore(self.limits.max_concurrent_jobs)
        self._tasks: dict[str, asyncio.Task[None]] = {}

    @property
    def active(self) -> int:
        return len(self._tasks)

    async def submit(self, kind: str, fn: JobFn, *, job_id: str | None = None) -> Job:
        if len(self._tasks) >= self.limits.max_concurrent_jobs + self.limits.max_queued_jobs:
            raise LimitExceeded("job queue is full", code="job_queue_full")
        job = Job(job_id=job_id or uuid.uuid4().hex, kind=kind)
        await self.store.create(job)
        self._tasks[job.job_id] = asyncio.create_task(self._run(job.job_id, fn), name=f"job-{job.job_id}")
        return job

    async def _set(self, job_id: str, **update: Any) -> Job | None:
        job = await self.store.get(job_id)
        if job is None:
            return None
        job = job.model_copy(update=update)
        await self.store.save(job)
        return job

    async def _run(self, job_id: str, fn: JobFn) -> None:
        ctx = JobContext(self, job_id)
        with bind_context(job_id=job_id):
            try:
                async with self._slots:
                    job = await self.store.get(job_id)
                    if job is None or job.cancel_requested:
                        await self._set(job_id, state=JobState.CANCELLED)
                        return
                    await self._set(job_id, state=JobState.RUNNING)
                    async with asyncio.timeout(self.limits.job_timeout_s):
                        result = await fn(ctx)
                await self._set(job_id, state=JobState.SUCCEEDED, result=result, progress=1.0)
            except (asyncio.CancelledError, JobCancelledError):
                await self._set(job_id, state=JobState.CANCELLED)
            except TimeoutError:
                err = LimitExceeded(
                    f"job exceeded job_timeout_s={self.limits.job_timeout_s}",
                    code="job_timeout",
                    retryable=False,
                )
                await self._set(job_id, state=JobState.FAILED, error=err.to_problem())
            except JaneError as exc:
                await self._set(job_id, state=JobState.FAILED, error=exc.to_problem())
            except Exception as exc:
                log.exception("job failed")
                await self._set(
                    job_id,
                    state=JobState.FAILED,
                    error=JaneError(f"{type(exc).__name__}: {exc}").to_problem(),
                )
            finally:
                self._tasks.pop(job_id, None)

    async def get(self, job_id: str) -> Job:
        job = await self.store.get(job_id)
        if job is None:
            raise NotFound(f"job {job_id} not found", code="job_not_found")
        return job

    async def cancel(self, job_id: str) -> Job:
        job = await self.get(job_id)
        if job.state in TERMINAL_STATES:
            if job.state == JobState.CANCELLED:
                return job
            raise Conflict(f"job {job_id} is already {job.state}", code="job_already_finished")
        job = await self._set(job_id, cancel_requested=True) or job
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


def accepted(job: Job, location: str) -> JSONResponse:
    """``202 Accepted`` with ``Location`` of the job resource."""
    return JSONResponse(job.model_dump(mode="json"), status_code=202, headers={"Location": location})


def jobs_router(runner: JobRunner, prefix: str = "/v1/jobs") -> APIRouter:
    router = APIRouter(prefix=prefix, tags=["jobs"])

    @router.get("/{job_id}", response_model=Job)
    async def get_job(job_id: str) -> Job:
        return await runner.get(job_id)

    @router.post("/{job_id}/cancel", response_model=Job, status_code=202)
    async def cancel_job(job_id: str) -> Job:
        return await runner.cancel(job_id)

    return router
