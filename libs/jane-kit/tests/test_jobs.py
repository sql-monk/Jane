from __future__ import annotations

import asyncio
import time

import pytest
from fastapi import Response
from fastapi.testclient import TestClient

from jane_kit.config import JaneSettings
from jane_kit.errors import Conflict, LimitExceeded, NotFound, ValidationFailed
from jane_kit.jobs import JobContext, JobLimits, JobRunner, JobState, accepted, jobs_router
from jane_kit.service import create_app


async def test_job_success_with_progress() -> None:
    runner = JobRunner()

    async def work(ctx: JobContext) -> dict[str, int]:
        await ctx.progress(0.5, "half")
        return {"answer": 42}

    job = await runner.submit("demo", work)
    assert job.state == JobState.QUEUED
    done = await runner.wait(job.job_id)
    assert done.state == JobState.SUCCEEDED
    assert done.result == {"answer": 42}
    assert done.progress == 1.0
    assert done.message == "half"


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
    with pytest.raises(LimitExceeded):
        await runner.submit("demo", work)
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
    await runner.cancel(queued.job_id)
    await runner.cancel(running.job_id)
    assert (await runner.wait(running.job_id)).state == JobState.CANCELLED
    assert (await runner.wait(queued.job_id)).state == JobState.CANCELLED
    again = await runner.cancel(running.job_id)
    assert again.state == JobState.CANCELLED


async def test_cooperative_cancellation() -> None:
    runner = JobRunner()
    steps = 0

    async def work(ctx: JobContext) -> None:
        nonlocal steps
        while True:
            await ctx.check_cancelled()
            steps += 1
            await asyncio.sleep(0.005)

    job = await runner.submit("demo", work)
    await asyncio.sleep(0.03)
    await runner.cancel(job.job_id)
    assert (await runner.wait(job.job_id)).state == JobState.CANCELLED
    assert steps > 0


async def test_failures_and_timeout() -> None:
    runner = JobRunner(limits=JobLimits(job_timeout_s=0.05))

    async def invalid(ctx: JobContext) -> None:
        raise ValidationFailed("bad input", code="bad_input")

    async def crash(ctx: JobContext) -> None:
        raise RuntimeError("boom")

    async def slow(ctx: JobContext) -> None:
        await asyncio.sleep(10)

    j1, j2, j3 = [await runner.submit("demo", f) for f in (invalid, crash, slow)]
    r1, r2, r3 = [await runner.wait(j.job_id) for j in (j1, j2, j3)]
    assert r1.state == JobState.FAILED and r1.error and r1.error.code == "bad_input"
    assert r2.state == JobState.FAILED and r2.error and r2.error.code == "internal_error"
    assert r3.state == JobState.FAILED and r3.error and r3.error.code == "job_timeout"
    with pytest.raises(Conflict):
        await runner.cancel(j1.job_id)
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

        job = await runner.submit("work", work)
        return accepted(job, f"/v1/jobs/{job.job_id}")

    with TestClient(app) as c:
        r = c.post("/v1/work")
        assert r.status_code == 202
        job_id = r.json()["job_id"]
        assert r.headers["Location"] == f"/v1/jobs/{job_id}"
        assert c.get(f"/v1/jobs/{job_id}").json()["state"] in {"queued", "running"}
        assert c.post(f"/v1/jobs/{job_id}/cancel").status_code == 202
        for _ in range(100):
            if c.get(f"/v1/jobs/{job_id}").json()["state"] == "cancelled":
                break
            time.sleep(0.01)
        assert c.get(f"/v1/jobs/{job_id}").json()["state"] == "cancelled"
        missing = c.get("/v1/jobs/unknown")
        assert missing.status_code == 404 and missing.json()["code"] == "job_not_found"
