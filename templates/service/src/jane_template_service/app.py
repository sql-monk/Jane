"""HTTP API of the service.

The ``/v1/examples/*`` endpoints show the jane-kit patterns (idempotency, 202 + job_id, progress,
cancellation). Replace them with the API from ``contracts/`` and delete the examples.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field

from jane_kit.idempotency import InMemoryIdempotencyStore, StoredResponse, idempotent
from jane_kit.jobs import JobContext, JobRunner, jobs_router
from jane_kit.service import create_app

from . import __version__
from .settings import Settings, platform_limits


class InfoResponse(BaseModel):
    service: str
    version: str
    instance: str
    limits: list[dict[str, Any]]


class ExampleJobRequest(BaseModel):  # EXAMPLE
    steps: int = Field(default=3, ge=1, le=1000)
    step_delay_s: float = Field(default=0.01, ge=0, le=60)


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    resolved = platform_limits(settings)
    limits = resolved.limits
    runner = JobRunner(limits=limits.jobs)
    idem_store = InMemoryIdempotencyStore(limits.idempotency)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        await runner.shutdown()

    app = create_app(settings, title="Template Service", version=__version__, lifespan=lifespan)
    app.state.limits = resolved
    app.include_router(jobs_router(runner))

    @app.get("/v1/info", response_model=InfoResponse, tags=["service"])
    async def info() -> InfoResponse:
        rows = [{"path": p, "value": v, "origin": o} for p, v, o in resolved.explain()]
        return InfoResponse(
            service=settings.service_name, version=__version__, instance=settings.instance_id, limits=rows
        )

    @app.post("/v1/examples/jobs", status_code=202, tags=["examples"])
    async def start_example_job(body: ExampleJobRequest, request: Request) -> Response:  # EXAMPLE
        async def handler() -> StoredResponse:
            async def work(ctx: JobContext) -> dict[str, int]:
                for i in range(body.steps):
                    await ctx.check_cancelled()
                    await asyncio.sleep(body.step_delay_s)
                    await ctx.progress((i + 1) / body.steps, f"step {i + 1}/{body.steps}")
                return {"steps_done": body.steps}

            job = await runner.submit("example", work)
            return StoredResponse(202, job.model_dump(mode="json"), {"Location": f"/v1/jobs/{job.job_id}"})

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    return app
