"""Health endpoints: liveness (process is up) and readiness (dependencies are usable).

CONNECTION POINT (WP-00): paths and body follow the health convention of ``contracts/``;
defaults are ``GET /health/live`` and ``GET /health/ready``.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

__all__ = ["CheckResult", "HealthRegistry", "HealthReport", "install_health"]

CheckFn = Callable[[], bool | Awaitable[bool]]


class CheckResult(BaseModel):
    status: Literal["ok", "fail"]
    duration_ms: float
    error: str | None = None


class HealthReport(BaseModel):
    status: Literal["ok", "fail"]
    service: str
    instance: str | None = None
    version: str | None = None
    checks: dict[str, CheckResult] = {}


class HealthRegistry:
    """Named readiness checks. A check returns ``True``/``False`` or raises; it is time-boxed."""

    def __init__(
        self,
        service: str,
        *,
        instance: str | None = None,
        version: str | None = None,
        check_timeout_s: float = 2.0,
    ) -> None:
        self.service = service
        self.instance = instance
        self.version = version
        self.check_timeout_s = check_timeout_s
        self._checks: dict[str, CheckFn] = {}

    def add(self, name: str, check: CheckFn) -> None:
        self._checks[name] = check

    async def _run(self, check: CheckFn) -> CheckResult:
        start = time.perf_counter()
        try:
            async with asyncio.timeout(self.check_timeout_s):
                result = check()
                if inspect.isawaitable(result):
                    result = await result
            ok, error = bool(result), None if result else "check returned false"
        except TimeoutError:
            ok, error = False, f"timeout after {self.check_timeout_s}s"
        except Exception as exc:
            ok, error = False, f"{type(exc).__name__}: {exc}"
        return CheckResult(
            status="ok" if ok else "fail",
            duration_ms=round((time.perf_counter() - start) * 1000, 2),
            error=error,
        )

    async def readiness(self) -> HealthReport:
        names = list(self._checks)
        results = await asyncio.gather(*(self._run(self._checks[n]) for n in names))
        checks = dict(zip(names, results, strict=True))
        status: Literal["ok", "fail"] = "ok" if all(r.status == "ok" for r in results) else "fail"
        return HealthReport(
            status=status, service=self.service, instance=self.instance, version=self.version, checks=checks
        )

    def liveness(self) -> HealthReport:
        return HealthReport(status="ok", service=self.service, instance=self.instance, version=self.version)


def install_health(app: FastAPI, registry: HealthRegistry, prefix: str = "/health") -> None:
    @app.get(f"{prefix}/live", tags=["health"], response_model=HealthReport)
    async def live() -> HealthReport:
        return registry.liveness()

    @app.get(
        f"{prefix}/ready",
        tags=["health"],
        response_model=HealthReport,
        responses={503: {"model": HealthReport}},
    )
    async def ready() -> JSONResponse:
        report = await registry.readiness()
        return JSONResponse(report.model_dump(mode="json"), status_code=200 if report.status == "ok" else 503)
