"""``GET /v1/health`` and ``GET /v1/info`` per WP-00 ``common.yaml`` (pathItems Health, Info).

Health: ``{"status": "ok"|"degraded"|"down", "checks": {name: {"status", "message"}}}``; HTTP 200 for
ok/degraded, 503 for down. A check returns ``True``/``False``, a status string, or raises; each check
is time-boxed by ``check_timeout_s`` (from config).
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

__all__ = ["CheckResult", "HealthRegistry", "HealthReport", "ServiceInfo", "install_health"]

Status = Literal["ok", "degraded", "down"]
CheckFn = Callable[[], bool | str | Awaitable[bool | str]]
_RANK = {"ok": 0, "degraded": 1, "down": 2}


class CheckResult(BaseModel):
    status: Status
    message: str | None = None


class HealthReport(BaseModel):
    status: Status
    checks: dict[str, CheckResult] = {}


class ServiceInfo(BaseModel):
    service: str
    version: str
    api_versions: list[str]
    capabilities: dict[str, Any] = {}
    auth_mode: Literal["none", "api_key", "jwt"] | None = None


class HealthRegistry:
    """Named health checks. ``critical=False`` checks can only make the service ``degraded``."""

    def __init__(self, check_timeout_s: float = 2.0) -> None:
        self.check_timeout_s = check_timeout_s
        self._checks: dict[str, tuple[CheckFn, bool]] = {}

    def add(self, name: str, check: CheckFn, *, critical: bool = True) -> None:
        self._checks[name] = (check, critical)

    async def _run(self, check: CheckFn, critical: bool) -> CheckResult:
        failed: Status = "down" if critical else "degraded"
        try:
            async with asyncio.timeout(self.check_timeout_s):
                result = check()
                if inspect.isawaitable(result):
                    result = await result
        except TimeoutError:
            return CheckResult(status=failed, message=f"timeout after {self.check_timeout_s}s")
        except Exception as exc:
            return CheckResult(status=failed, message=f"{type(exc).__name__}: {exc}")
        if isinstance(result, str) and result in _RANK:
            status: Status = result  # type: ignore[assignment]
            return CheckResult(status=status if critical or status != "down" else "degraded")
        return (
            CheckResult(status="ok") if result else CheckResult(status=failed, message="check returned false")
        )

    async def report(self) -> HealthReport:
        names = list(self._checks)
        results = await asyncio.gather(*(self._run(*self._checks[n]) for n in names))
        checks = dict(zip(names, results, strict=True))
        worst = max((r.status for r in results), key=_RANK.__getitem__, default="ok")
        return HealthReport(status=worst, checks=checks)


def install_health(
    app: FastAPI, registry: HealthRegistry, info: Callable[[], ServiceInfo], prefix: str = "/v1"
) -> None:
    @app.get(f"{prefix}/health", tags=["system"], operation_id="getHealth", response_model=None)
    async def health() -> JSONResponse:
        report = await registry.report()
        body = report.model_dump(mode="json", exclude_none=True)
        return JSONResponse(body, status_code=503 if report.status == "down" else 200)

    @app.get(f"{prefix}/info", tags=["system"], operation_id="getServiceInfo", response_model=None)
    async def service_info() -> JSONResponse:
        return JSONResponse(info().model_dump(mode="json", exclude_none=True))
