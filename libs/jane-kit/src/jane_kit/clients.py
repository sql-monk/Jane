"""HTTP client base for calling other Jane services (and base class of generated clients).

* timeouts, retries and connection pool size come from :class:`ClientLimits` (config, not code);
* retries only for safe methods or requests carrying ``Idempotency-Key``;
* honours ``Retry-After``; propagates ``X-Request-ID`` from the log context;
* error responses become :class:`RemoteError` carrying the parsed :class:`~jane_kit.errors.Problem`;
* :meth:`ServiceClient.wait_for_job` polls a ``202`` job until it reaches a terminal state.
"""

from __future__ import annotations

import asyncio
import random
import time
import uuid
from collections.abc import Mapping
from typing import Any, Self

import httpx
from pydantic import Field

from jane_kit.config import Limits
from jane_kit.errors import Problem
from jane_kit.idempotency import IDEMPOTENCY_HEADER
from jane_kit.logs import current_context

__all__ = ["ClientLimits", "RemoteError", "ServiceClient"]

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})
RETRY_STATUSES = frozenset({429, 502, 503, 504})
TERMINAL_JOB_STATES = frozenset({"succeeded", "failed", "cancelled"})


class ClientLimits(Limits):
    timeout_s: float = Field(default=30.0, gt=0)
    connect_timeout_s: float = Field(default=5.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    backoff_base_s: float = Field(default=0.2, ge=0)
    backoff_max_s: float = Field(default=10.0, ge=0)
    max_connections: int = Field(default=20, ge=1)
    job_poll_interval_s: float = Field(default=1.0, gt=0)
    job_wait_timeout_s: float = Field(default=3600.0, gt=0)


class RemoteError(Exception):
    def __init__(self, status: int, problem: Problem | None, body: str) -> None:
        self.status = status
        self.problem = problem
        self.body = body
        super().__init__(f"HTTP {status}: {problem.code if problem else body[:200]}")

    @property
    def retryable(self) -> bool:
        return bool(self.problem.retryable) if self.problem else self.status in RETRY_STATUSES


class ServiceClient:
    def __init__(
        self,
        base_url: str,
        limits: ClientLimits | None = None,
        *,
        headers: Mapping[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.limits = limits or ClientLimits()
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=dict(headers or {}),
            timeout=httpx.Timeout(self.limits.timeout_s, connect=self.limits.connect_timeout_s),
            limits=httpx.Limits(max_connections=self.limits.max_connections),
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _delay(self, attempt: int, response: httpx.Response | None) -> float:
        if response is not None and (ra := response.headers.get("retry-after")):
            try:
                return float(min(float(ra), self.limits.backoff_max_s))
            except ValueError:
                pass
        base = self.limits.backoff_base_s * (2**attempt)
        return float(min(base + random.uniform(0, base / 2), self.limits.backoff_max_s))  # noqa: S311

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: Any = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        idempotency_key: str | None = None,
    ) -> httpx.Response:
        method = method.upper()
        hdrs = dict(headers or {})
        if (rid := current_context().get("request_id")) and "X-Request-ID" not in hdrs:
            hdrs["X-Request-ID"] = str(rid)
        if idempotency_key:
            hdrs[IDEMPOTENCY_HEADER] = idempotency_key
        retryable = method in SAFE_METHODS or bool(idempotency_key)
        attempt = 0
        while True:
            response: httpx.Response | None = None
            try:
                response = await self._client.request(method, url, json=json, params=params, headers=hdrs)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError):
                if not retryable or attempt >= self.limits.max_retries:
                    raise
            else:
                if response.status_code < 400:
                    return response
                if not (
                    retryable and response.status_code in RETRY_STATUSES and attempt < self.limits.max_retries
                ):
                    raise self._error(response)
            await asyncio.sleep(self._delay(attempt, response))
            attempt += 1

    @staticmethod
    def _error(response: httpx.Response) -> RemoteError:
        problem = None
        if "json" in response.headers.get("content-type", ""):
            try:
                problem = Problem.model_validate(response.json())
            except ValueError:
                problem = None
        return RemoteError(response.status_code, problem, response.text)

    async def get_json(self, url: str, **kw: Any) -> Any:
        return (await self.request("GET", url, **kw)).json()

    async def post_json(self, url: str, json: Any, *, idempotency_key: str | None = None, **kw: Any) -> Any:
        return (await self.request("POST", url, json=json, idempotency_key=idempotency_key, **kw)).json()

    @staticmethod
    def new_idempotency_key() -> str:
        return uuid.uuid4().hex

    async def wait_for_job(self, job_url: str) -> dict[str, Any]:
        """Poll ``job_url`` (``Location`` of a 202) until the job is terminal; return the job body."""
        deadline = time.monotonic() + self.limits.job_wait_timeout_s
        while True:
            job: dict[str, Any] = await self.get_json(job_url)
            if job.get("state") in TERMINAL_JOB_STATES:
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(f"job {job_url} not finished within {self.limits.job_wait_timeout_s}s")
            await asyncio.sleep(self.limits.job_poll_interval_s)
