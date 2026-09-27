"""HTTP API of the service.

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit. The
``/v1/examples/*`` endpoint shows the patterns (Idempotency-Key, 202 + Job, progress, cancellation):
replace it with the API from ``contracts/openapi/<service>.v1.yaml`` and delete it.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field

from jane_kit.idempotency import IDEMPOTENCY_HEADER, InMemoryIdempotencyStore, StoredResponse, idempotent
from jane_kit.jobs import JobContext, JobRunner, jobs_router
from jane_kit.service import create_app

from . import __version__
from .settings import Settings, resolve_service_limits

log = logging.getLogger(__name__)


class ExampleJobRequest(BaseModel):
    """EXAMPLE - delete together with the /v1/examples endpoint.

    The bounds below validate the demo payload only; they are not operational limits of the service
    (those live in ``ServiceLimits`` and come from configuration).
    """

    steps: int = Field(default=3, ge=1, le=1000)
    step_delay_ms: int = Field(default=10, ge=0, le=60_000)


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    runner = JobRunner(limits=limits.jobs)
    idem_store = InMemoryIdempotencyStore(limits.idempotency)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        log.info("configured limits", extra={"limits": resolved.effective()})
        yield
        await runner.shutdown()

    app = create_app(
        settings,
        title="Registry",
        version=__version__,
        lifespan=lifespan,
        capabilities={"examples": ["jobs"]},
        limits=resolved,  # published in /v1/info as PlatformLimits (WP-00 ServiceInfo.limits)
    )
    app.state.limits = resolved
    app.include_router(jobs_router(runner))

    @app.post("/v1/examples/jobs", status_code=202, tags=["examples"])
    async def start_example_job(body: ExampleJobRequest, request: Request) -> Response:  # EXAMPLE
        async def handler() -> StoredResponse:
            async def work(ctx: JobContext) -> dict[str, Any]:
                for i in range(body.steps):
                    await ctx.check_cancelled()
                    await asyncio.sleep(body.step_delay_ms / 1000)
                    await ctx.progress(i + 1, body.steps, unit="steps")
                return {"steps_done": body.steps}

            job = await runner.submit(
                "example", work, idempotency_key=request.headers.get(IDEMPOTENCY_HEADER)
            )
            return StoredResponse(202, job.wire(), {"Location": runner.location(job.job_id)})

        return await idempotent(request, idem_store, handler, limits=limits.idempotency)

    return app
