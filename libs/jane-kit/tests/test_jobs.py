from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest
from fastapi import Response
from fastapi.testclient import TestClient

from jane_kit.config import JaneSettings
from jane_kit.errors import NotFound, ServiceUnavailable, ValidationFailed
from jane_kit.jobs import JobContext, JobLimits, JobRunner, JobStatus, accepted, jobs_router
from jane_kit.service import create_app


async def test_job_success_with_progress() -> None:
    runner = JobRunner()

    async def work(ctx: JobContext) -> dict[str, Any]:
        await ctx.progress(5, 10, unit="pages", counters={"fetched": 5})
        return {"answer": 42}

    job = await runner.submit("collection", work, idempotency_key="k1")
    assert job.status == JobStatus.QUEUED
    assert job.job_id.startswith("job_")
    assert job.links == {"self": f"/v1/jobs/{job.job_id}", "cancel": f"/v1/jobs/{job.job_id}/cancel"}
    done = await runner.wait(job.job_id)
    assert done.status == JobStatus.SUCCEEDED
    assert done.result == {"answer": 42}
    assert done.progress is not None and (done.progress.completed, done.progress.total) == (5, 10)
    assert done.started_at and done.finished_at and done.idempotency_key == "k1"


async def test_concurrency_limit_from_config() -> None:
    runner = JobRunner(limits=JobLimits(max_concurrent_jobs=2))
    running = 0
    peak = 0

    async def work(ctx: JobContext) -> None:
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.02)
        running -= 1

    jobs = [await runner.submit("demo", work) for _ in range(6)]
    await asyncio.gather(*(runner.wait(j.job_id) for j in jobs))
    assert peak == 2


async def test_queue_limit_backpressure() -> None:
    runner = JobRunner(limits=JobLimits(max_concurrent_jobs=1, max_queued_jobs=1))
    gate = asyncio.Event()

    async def work(ctx: JobContext) -> None:
        await gate.wait()

    await runner.submit("demo", work)
    await runner.submit("demo", work)
    with pytest.raises(ServiceUnavailable) as info:
        await runner.submit("demo", work)
    assert info.value.status == 503 and info.value.retryable
    gate.set()
    await runner.shutdown()


async def test_cancel_running_and_queued_jobs() -> None:
    runner = JobRunner(limits=JobLimits(max_concurrent_jobs=1))
    started = asyncio.Event()

    async def forever(ctx: JobContext) -> None:
        started.set()
        await asyncio.sleep(3600)

    running = await runner.submit("demo", forever)
    queued = await runner.submit("demo", forever)
    await started.wait()
    q = await runner.cancel(queued.job_id, reason="wrong scope")
    assert q.status == JobStatus.CANCELLING and q.cancellation and q.cancellation.reason == "wrong scope"
    await runner.cancel(running.job_id)
    assert (await runner.wait(running.job_id)).status == JobStatus.CANCELLED
    assert (await runner.wait(queued.job_id)).status == JobStatus.CANCELLED
    again = await runner.cancel(running.job_id)  # terminal: unchanged
    assert again.status == JobStatus.CANCELLED


async def test_cooperative_cancellation_check() -> None:
    runner = JobRunner()
    seen: list[bool] = []

    async def work(ctx: JobContext) -> None:
        seen.append(await ctx.cancelled())
        await ctx.check_cancelled()

    job = await runner.submit("demo", work)
    await runner.wait(job.job_id)
    assert seen == [False]


async def test_failures_and_timeout() -> None:
    runner = JobRunner(limits=JobLimits(job_timeout_ms=50))

    async def invalid(ctx: JobContext) -> None:
        raise ValidationFailed("bad input", code="schema_mismatch")

    async def crash(ctx: JobContext) -> None:
        raise RuntimeError("boom")

    async def slow(ctx: JobContext) -> None:
        await asyncio.sleep(10)

    j1, j2, j3 = [await runner.submit("demo", f) for f in (invalid, crash, slow)]
    r1, r2, r3 = [await runner.wait(j.job_id) for j in (j1, j2, j3)]
    assert r1.status == JobStatus.FAILED and r1.error and r1.error.code == "schema_mismatch"
    assert r2.status == JobStatus.FAILED and r2.error and r2.error.code == "internal_error"
    assert r3.status == JobStatus.FAILED and r3.error and r3.error.code == "timeout"
    assert (await runner.cancel(j1.job_id)).status == JobStatus.FAILED  # terminal: returned as is
    with pytest.raises(NotFound):
        await runner.get("nope")


def test_http_flow_202_poll_cancel() -> None:
    app = create_app(JaneSettings(), configure_logs=False)
    runner = JobRunner()
    app.include_router(jobs_router(runner))

    @app.post("/v1/work", status_code=202)
    async def start() -> Response:
        async def work(ctx: JobContext) -> None:
            await asyncio.sleep(3600)

        return accepted(await runner.submit("work", work))

    with TestClient(app) as c:
        r = c.post("/v1/work")
        assert r.status_code == 202
        job_id = r.json()["job_id"]
        assert r.headers["Location"] == f"/v1/jobs/{job_id}"
        assert c.get(f"/v1/jobs/{job_id}").json()["status"] in {"queued", "running"}
        cancel = c.post(f"/v1/jobs/{job_id}/cancel", json={"reason": "test"})
        assert cancel.status_code == 202 and cancel.json()["cancellation"]["reason"] == "test"
        for _ in range(100):
            if c.get(f"/v1/jobs/{job_id}").json()["status"] == "cancelled":
                break
            time.sleep(0.01)
        assert c.get(f"/v1/jobs/{job_id}").json()["status"] == "cancelled"
        assert c.post(f"/v1/jobs/{job_id}/cancel").status_code == 200
        missing = c.get("/v1/jobs/unknown")
        assert missing.status_code == 404 and missing.json()["code"] == "not_found"


async def test_memory_store_follows_the_shared_write_rules() -> None:
    """The in-memory store decides like the shared stores (R17): terminal is final, cancellation is kept."""
    from jane_kit.jobs import InMemoryJobStore, Job, JobCancellation, JobProgress

    store = InMemoryJobStore()
    job = Job(job_id="job_a", kind="demo", status=JobStatus.RUNNING)
    await store.create(job)
    await store.save(
        job.model_copy(
            update={
                "status": JobStatus.CANCELLING,
                "cancellation": JobCancellation(requested_at=job.created_at),
            }
        )
    )
    await store.save(job.model_copy(update={"progress": JobProgress(completed=2)}))  # an older snapshot
    current = await store.get("job_a")
    assert current is not None and current.status == JobStatus.CANCELLING and current.progress is not None
    await store.save(job.model_copy(update={"status": JobStatus.SUCCEEDED, "result": {"x": 1}}))
    done = await store.get("job_a")
    assert done is not None and done.status == JobStatus.CANCELLED and done.result is None
    assert done.finished_at is not None and done.cancellation is not None
    await store.save(done.model_copy(update={"status": JobStatus.FAILED}))
    assert (await store.get("job_a")) == done
    await store.save(Job(job_id="unknown", kind="demo"))  # never created: nothing is written
    assert await store.get("unknown") is None


async def test_memory_store_page() -> None:
    from jane_kit.jobs import InMemoryJobStore, Job

    store = InMemoryJobStore()
    jobs = [Job(job_id=f"job_{n}", kind="demo", labels={"s": "1" if n % 2 else "2"}) for n in range(4)]
    for job in jobs:
        await store.create(job)
    await store.save(jobs[0].model_copy(update={"status": JobStatus.SUCCEEDED}))
    page = await store.page("demo", labels={}, statuses=None, after=None, limit=2)
    assert [j.job_id for j in page] == ["job_3", "job_2"]
    rest = await store.page(
        "demo", labels={}, statuses=None, after=(page[-1].created_at, page[-1].job_id), limit=5
    )
    assert [j.job_id for j in rest] == ["job_1", "job_0"]
    assert [
        j.job_id for j in await store.page("demo", labels={"s": "1"}, statuses=None, after=None, limit=5)
    ] == [
        "job_3",
        "job_1",
    ]
    assert [
        j.job_id for j in await store.page("demo", labels={}, statuses=["succeeded"], after=None, limit=5)
    ] == ["job_0"]
    assert await store.page("other", labels={}, statuses=None, after=None, limit=5) == []
