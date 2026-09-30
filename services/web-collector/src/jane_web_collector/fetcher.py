"""HTTP fetching with per-host limits, retries, manual redirects, size limits and conditional requests.

Every hop of a redirect chain goes through ``check_hop`` (scope, exclusions, robots.txt), so a redirect
cannot lead the crawler out of bounds. All numbers come from :class:`~.settings.ServiceLimits`.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit

import httpx

from jane_kit.errors import FieldError, ValidationFailed

from .connections import ConnectionPolicy, header_name_safe, header_value_safe, is_safe_rule_header
from .settings import ServiceLimits, Timeouts

__all__ = ["FetchError", "Fetcher", "HostLimiter", "HttpResult", "build_client"]

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
# Response headers copied into Material.http.headers (never Set-Cookie or auth headers).
KEPT_HEADERS = (
    "content-type",
    "content-length",
    "etag",
    "last-modified",
    "cache-control",
    "content-language",
)


class FetchError(Exception):
    """A URL could not be fetched (network, HTTP error after retries, policy)."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        http_status: int | None = None,
        attempts: int = 1,
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.attempts = attempts
        self.retry_after_seconds = retry_after_seconds


@dataclass
class HttpResult:
    url: str
    final_url: str
    status: int
    headers: dict[str, str]
    body: bytes
    fetched_at: datetime
    truncated: bool = False
    redirects: list[str] = field(default_factory=list)
    attempts: int = 1

    @property
    def media_type(self) -> str:
        return self.headers.get("content-type", "application/octet-stream").split(";", 1)[0].strip().lower()

    @property
    def charset(self) -> str | None:
        for part in self.headers.get("content-type", "").split(";")[1:]:
            key, _, value = part.strip().partition("=")
            if key.lower() == "charset" and value:
                return value.strip("\"'").lower()
        return None


def build_client(limits: ServiceLimits) -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        limits.timeouts.request_timeout_ms / 1000, connect=limits.timeouts.connect_timeout_ms / 1000
    )
    pool = httpx.Limits(max_connections=limits.concurrency.max_parallel_fetches * 2)
    return httpx.AsyncClient(timeout=timeout, limits=pool, follow_redirects=False, trust_env=False)


class HostLimiter:
    """Politeness per host: at most ``max_parallel_fetches_per_host`` requests at once and a minimum
    interval between request starts = max(1/rps, min_delay, robots Crawl-delay)."""

    def __init__(self, limits: ServiceLimits) -> None:
        self.limits = limits
        self._sems: dict[str, asyncio.Semaphore] = {}
        self._next: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def interval(self, crawl_delay: float | None) -> float:
        rate = self.limits.rate
        interval = max(1.0 / rate.requests_per_second_per_host, rate.min_delay_ms_per_host / 1000)
        if rate.respect_crawl_delay and crawl_delay:
            interval = max(interval, crawl_delay)
        return interval

    def semaphore(self, host: str) -> asyncio.Semaphore:
        if host not in self._sems:
            self._sems[host] = asyncio.Semaphore(self.limits.concurrency.max_parallel_fetches_per_host)
            self._locks[host] = asyncio.Lock()
        return self._sems[host]

    async def wait_turn(self, host: str, crawl_delay: float | None) -> None:
        self.semaphore(host)
        async with self._locks[host]:
            now = time.monotonic()
            start = max(now, self._next.get(host, 0.0))
            self._next[host] = start + self.interval(crawl_delay)
        if start > now:
            await asyncio.sleep(start - now)

    def push_back(self, host: str, seconds: float) -> None:
        """A source asked to slow down (Retry-After): no request to this host before that."""
        self._next[host] = max(self._next.get(host, 0.0), time.monotonic() + seconds)


HopCheck = Callable[[str], Awaitable[None]]
DelayFor = Callable[[str], Awaitable[float | None]]


def _retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            when = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, (when - datetime.now(UTC)).total_seconds())


class Fetcher:
    def __init__(
        self,
        client: httpx.AsyncClient,
        limits: ServiceLimits,
        limiter: HostLimiter,
        *,
        user_agent: str,
        headers: Mapping[str, str] | None = None,
        auth_headers: Mapping[str, str] | None = None,
        connection_policy: ConnectionPolicy | None = None,
        crawl_delay_for: DelayFor | None = None,
    ) -> None:
        self.client = client
        self.limits = limits
        self.limiter = limiter
        source_headers = dict(headers or {})
        invalid = [name for name in source_headers if not is_safe_rule_header(name)]
        if invalid:
            raise ValidationFailed(
                "source rules contain headers outside the allowlist",
                errors=[
                    FieldError(pointer=f"/fetch/headers/{name}", message="header is not allowed")
                    for name in invalid
                ],
            )
        self.headers = {"User-Agent": user_agent, **source_headers}
        self.auth_headers = dict(auth_headers or {})
        self.connection_policy = connection_policy or ConnectionPolicy()
        self.crawl_delay_for = crawl_delay_for

    def _backoff(self, attempt: int) -> float:
        r = self.limits.retries
        delay = min(r.max_backoff_ms, r.initial_backoff_ms * r.backoff_multiplier ** (attempt - 1)) / 1000
        if r.jitter:
            delay *= 0.5 + random.random() / 2  # noqa: S311 - jitter, not cryptography
        return delay

    def _timeout(self, timeouts: Timeouts | None) -> httpx.Timeout:
        """Per-request timeouts from the run's (or strategy's) effective limits, not the client defaults."""
        t = timeouts or self.limits.timeouts
        return httpx.Timeout(t.request_timeout_ms / 1000, connect=t.connect_timeout_ms / 1000)

    async def _one_request(
        self, url: str, headers: Mapping[str, str], max_bytes: int, timeouts: Timeouts | None = None
    ) -> tuple[int, dict[str, str], bytes, bool]:
        if any(not header_name_safe(name) or not header_value_safe(value) for name, value in headers.items()):
            raise FetchError("access_denied_by_policy", "HTTP request header rejected by policy")
        host = urlsplit(url).netloc
        delay = await self.crawl_delay_for(url) if self.crawl_delay_for else None
        if (
            delay
            and self.limits.rate.respect_crawl_delay
            and delay > self.limits.collector.max_retry_after_seconds
        ):
            raise FetchError(
                "rate_limited", f"robots.txt Crawl-delay {delay}s exceeds the configured maximum wait"
            )
        async with self.limiter.semaphore(host):
            await self.limiter.wait_turn(host, delay)
            async with self.client.stream(
                "GET", url, headers=headers, timeout=self._timeout(timeouts)
            ) as resp:
                chunks: list[bytes] = []
                size = 0
                truncated = False
                async for chunk in resp.aiter_bytes():
                    if size + len(chunk) > max_bytes:
                        chunks.append(chunk[: max_bytes - size])
                        size = max_bytes
                        truncated = True
                        break
                    chunks.append(chunk)
                    size += len(chunk)
                hdrs = {k.lower(): v for k, v in resp.headers.items()}
                return resp.status_code, hdrs, b"".join(chunks), truncated

    async def get(
        self,
        url: str,
        *,
        check_hop: HopCheck | None = None,
        conditional: Mapping[str, str] | None = None,
        max_bytes: int | None = None,
        timeouts: Timeouts | None = None,
    ) -> HttpResult:
        """GET with retries and redirects. Raises :class:`FetchError`; policy callbacks may raise their own."""
        max_bytes = max_bytes if max_bytes is not None else self.limits.crawl.max_material_bytes
        redirects: list[str] = []
        current = url
        total_attempts = 0
        while True:
            headers = {**self.headers, **self.auth_headers_for(current, url), **dict(conditional or {})}
            status, hdrs, body, truncated, attempts = await self._with_retries(
                current, headers, max_bytes, timeouts
            )
            total_attempts += attempts
            if status in REDIRECT_STATUSES and "location" in hdrs:
                if len(redirects) >= self.limits.crawl.max_redirects:
                    raise FetchError(
                        "limit_exceeded",
                        f"more than crawl.max_redirects={self.limits.crawl.max_redirects} redirects",
                        http_status=status,
                        attempts=total_attempts,
                    )
                target = urljoin(current, hdrs["location"])
                if check_hop is not None:
                    await check_hop(target)
                redirects.append(target)
                current = target
                conditional = None
                continue
            return HttpResult(
                url=url,
                final_url=current,
                status=status,
                headers={k: v for k, v in hdrs.items() if k in KEPT_HEADERS},
                body=body,
                fetched_at=datetime.now(UTC),
                truncated=truncated,
                redirects=redirects,
                attempts=total_attempts,
            )

    def auth_headers_for(self, current: str, original: str) -> dict[str, str]:
        """Credentials only for the original host (never leak them to a redirect target on another host)."""
        if not self.auth_headers:
            return {}
        if not self.connection_policy.origin_allowed(original):
            raise FetchError("access_denied_by_policy", "authenticated origin is not in the allowlist")
        start = urlsplit(original)
        target = urlsplit(current)
        if (
            start.scheme.lower() == target.scheme.lower()
            and start.hostname == target.hostname
            and (start.port or (443 if start.scheme.lower() == "https" else 80))
            == (target.port or (443 if target.scheme.lower() == "https" else 80))
        ):
            return self.auth_headers
        return {}

    async def _with_retries(
        self, url: str, headers: Mapping[str, str], max_bytes: int, timeouts: Timeouts | None = None
    ) -> tuple[int, dict[str, str], bytes, bool, int]:
        max_attempts = self.limits.retries.max_attempts
        last_error = ""
        last_status: int | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                status, hdrs, body, truncated = await self._one_request(url, headers, max_bytes, timeouts)
            except httpx.TimeoutException:
                last_error = "HTTP Timeout"
                last_status = None
            except httpx.TransportError:
                # httpx can include raw header values (including credentials) in LocalProtocolError text.
                last_error = "HTTP transport failed"
                last_status = None
            else:
                if status not in RETRY_STATUSES:
                    return status, hdrs, body, truncated, attempt
                last_status = status
                last_error = f"HTTP {status}"
                wait = _retry_after(hdrs.get("retry-after"))
                if wait is not None:
                    if wait > self.limits.collector.max_retry_after_seconds:
                        raise FetchError(
                            "rate_limited",
                            f"source asks to retry after {wait:.0f}s (above the configured maximum)",
                            http_status=status,
                            attempts=attempt,
                            retry_after_seconds=int(wait),
                        )
                    self.limiter.push_back(urlsplit(url).netloc, wait)
            if attempt < max_attempts:
                await asyncio.sleep(self._backoff(attempt))
        code = "rate_limited" if last_status == 429 else "source_unavailable"
        raise FetchError(code, last_error or "request failed", http_status=last_status, attempts=max_attempts)
