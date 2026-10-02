"""HTTP client base for calling other Jane services (and base class of generated clients).

* timeouts, retries and pool size come from :class:`ClientLimits` (names follow ``limits.schema.json``:
  ``timeouts.*_ms``, ``retries`` = ``RetryPolicy``);
* retries only for safe methods or requests carrying ``Idempotency-Key``, and only for retryable
  failures (connection errors, 429/502/503/504, Problem ``retryable: true``); honours ``Retry-After``;
* propagates ``traceparent`` (W3C) and ``X-Request-ID`` from the log context;
* error responses become :class:`RemoteError` with the parsed :class:`~jane_kit.errors.Problem`;
* :meth:`ServiceClient.wait_for_job` polls a ``202`` job until it is terminal.
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

from jane_kit.config import Limits, contract_field
from jane_kit.errors import Problem
from jane_kit.idempotency import IDEMPOTENCY_HEADER
from jane_kit.logs import current_context
from jane_kit.tracing import TRACEPARENT, child_traceparent

__all__ = ["ClientLimits", "RemoteError", "RetryPolicy", "ServiceClient"]

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})
RETRY_STATUSES = frozenset({429, 502, 503, 504})
TERMINAL_JOB_STATUSES = frozenset({"succeeded", "failed", "cancelled"})


class RetryPolicy(Limits):
    """Contract ``limits.retries`` (``RetryPolicy``)."""

    max_attempts: int = Field(default=4, ge=1)
    """Total attempts including the first one."""
    initial_backoff_ms: int = Field(default=200, ge=0)
    max_backoff_ms: int = Field(default=10_000, ge=0)
    backoff_multiplier: float = Field(default=2.0, ge=1)
    jitter: bool = True


class ClientLimits(Limits):
    connect_timeout_ms: int = contract_field("timeouts.connect_timeout_ms", 5_000, ge=1)
    request_timeout_ms: int = contract_field("timeouts.request_timeout_ms", 30_000, ge=1)
    retries: RetryPolicy = contract_field("retries", RetryPolicy())
    max_connections: int = Field(default=20, ge=1)
    job_poll_interval_ms: int = Field(default=1_000, ge=1)
    job_wait_timeout_ms: int = Field(default=3_600_000, ge=1)


class RemoteError(Exception):
    def __init__(self, status: int, problem: Problem | None, body: str) -> None:
        self.status = status
        self.problem = problem
        self.body = body
        super().__init__(f"HTTP {status}: {problem.code if problem else body[:200]}")

    @property
    def retryable(self) -> bool:
        if self.problem is not None and self.problem.retryable is not None:
            return self.problem.retryable
        return self.status in RETRY_STATUSES or self.status >= 500


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
            timeout=httpx.Timeout(
                self.limits.request_timeout_ms / 1000, connect=self.limits.connect_timeout_ms / 1000
            ),
            limits=httpx.Limits(max_connections=self.limits.max_connections),
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _delay_s(self, attempt: int, response: httpx.Response | None) -> float:
        policy = self.limits.retries
        cap = policy.max_backoff_ms / 1000
        if response is not None and (ra := response.headers.get("retry-after")):
            try:
                return float(min(float(ra), cap))
            except ValueError:
                pass
        base = policy.initial_backoff_ms / 1000 * policy.backoff_multiplier**attempt
        if policy.jitter:
            base += random.uniform(0, base / 2)  # noqa: S311 - jitter, not crypto
        return float(min(base, cap))

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
        ctx = current_context()
        if (trace_id := ctx.get("trace_id")) and TRACEPARENT not in hdrs:
            hdrs[TRACEPARENT] = child_traceparent(str(trace_id))
        if (rid := ctx.get("request_id")) and "X-Request-ID" not in hdrs:
            hdrs["X-Request-ID"] = str(rid)
        if idempotency_key:
            hdrs[IDEMPOTENCY_HEADER] = idempotency_key
        may_retry = method in SAFE_METHODS or bool(idempotency_key)
        attempts = self.limits.retries.max_attempts
        attempt = 0
        while True:
            attempt += 1
            response: httpx.Response | None = None
            try:
                response = await self._client.request(method, url, json=json, params=params, headers=hdrs)
            except (httpx.ConnectError, httpx.ReadError, httpx.ReadTimeout, httpx.RemoteProtocolError):
                if not may_retry or attempt >= attempts:
                    raise
            else:
                if response.status_code < 400:
                    return response
                error = self._error(response)
                if not (may_retry and error.retryable and attempt < attempts):
                    raise error
            await asyncio.sleep(self._delay_s(attempt - 1, response))

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
        return str(uuid.uuid4())

    async def wait_for_job(self, job_url: str) -> dict[str, Any]:
        """Poll ``job_url`` (``Location`` of a 202) until the job is terminal; return the job body."""
        deadline = time.monotonic() + self.limits.job_wait_timeout_ms / 1000
        while True:
            job: dict[str, Any] = await self.get_json(job_url)
            if job.get("status") in TERMINAL_JOB_STATUSES:
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(f"job {job_url} not finished within {self.limits.job_wait_timeout_ms} ms")
            await asyncio.sleep(self.limits.job_poll_interval_ms / 1000)
