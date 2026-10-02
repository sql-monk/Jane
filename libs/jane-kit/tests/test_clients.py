from __future__ import annotations

import httpx
import pytest

from jane_kit.clients import ClientLimits, RemoteError, RetryPolicy, ServiceClient
from jane_kit.logs import bind_context
from jane_kit.tracing import parse_traceparent

FAST = ClientLimits(
    retries=RetryPolicy(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0, jitter=False),
    job_poll_interval_ms=1,
)
PROBLEM = {"content-type": "application/problem+json"}


def transport(responses: list[httpx.Response], seen: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return responses.pop(0)

    return httpx.MockTransport(handler)


async def test_get_retries_on_503_then_succeeds() -> None:
    seen: list[httpx.Request] = []
    t = transport([httpx.Response(503), httpx.Response(200, json={"ok": True})], seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        assert await c.get_json("/v1/x") == {"ok": True}
    assert len(seen) == 2


async def test_post_without_idempotency_key_is_not_retried() -> None:
    seen: list[httpx.Request] = []
    problem = {
        "type": "urn:jane:problem:service_unavailable",
        "title": "u",
        "status": 503,
        "code": "service_unavailable",
        "retryable": True,
    }
    t = transport([httpx.Response(503, json=problem, headers=PROBLEM)], seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with pytest.raises(RemoteError) as info:
            await c.post_json("/v1/x", {})
    assert len(seen) == 1
    assert info.value.problem is not None and info.value.problem.code == "service_unavailable"
    assert info.value.retryable


async def test_post_with_idempotency_key_is_retried_and_context_propagated() -> None:
    seen: list[httpx.Request] = []
    t = transport([httpx.Response(502), httpx.Response(201, json={"id": 1})], seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with bind_context(trace_id="4bf92f3577b34da6a3ce929d0e0e4736", request_id="req-7"):
            assert await c.post_json("/v1/x", {"a": 1}, idempotency_key="k1") == {"id": 1}
    assert len(seen) == 2
    assert all(r.headers["Idempotency-Key"] == "k1" for r in seen)
    assert parse_traceparent(seen[0].headers["traceparent"]) == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert seen[0].headers["X-Request-ID"] == "req-7"


@pytest.mark.parametrize(
    ("method", "idempotency_key", "should_retry"),
    [("GET", None, True), ("POST", "delivery-1", True), ("POST", None, False)],
)
async def test_read_error_retries_only_safe_or_idempotent_requests(
    method: str, idempotency_key: str | None, should_retry: bool
) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if len(seen) == 1:
            raise httpx.ReadError("server closed an idle pooled connection", request=request)
        return httpx.Response(200, json={"ok": True})

    async with ServiceClient("http://svc", FAST, transport=httpx.MockTransport(handler)) as client:
        if should_retry:
            response = await client.request(
                method, "/v1/x", json={"a": 1} if method == "POST" else None, idempotency_key=idempotency_key
            )
            assert response.json() == {"ok": True}
        else:
            with pytest.raises(httpx.ReadError):
                await client.request(method, "/v1/x", json={"a": 1})
    assert len(seen) == (2 if should_retry else 1)
    if idempotency_key:
        assert all(request.headers["Idempotency-Key"] == idempotency_key for request in seen)
        assert seen[0].content == seen[1].content


async def test_non_retryable_problem_is_not_retried_even_with_key() -> None:
    seen: list[httpx.Request] = []
    body = {
        "type": "urn:jane:problem:budget_exhausted",
        "title": "b",
        "status": 429,
        "code": "budget_exhausted",
        "retryable": False,
    }
    t = transport([httpx.Response(429, json=body, headers=PROBLEM)], seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with pytest.raises(RemoteError):
            await c.post_json("/v1/x", {}, idempotency_key="k")
    assert len(seen) == 1


async def test_attempts_exhausted_raises() -> None:
    seen: list[httpx.Request] = []
    t = transport([httpx.Response(503)] * 3, seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with pytest.raises(RemoteError):
            await c.get_json("/v1/x")
    assert len(seen) == 3  # max_attempts


async def test_client_error_not_retried() -> None:
    seen: list[httpx.Request] = []
    t = transport(
        [
            httpx.Response(
                404,
                json={"type": "t", "title": "nf", "status": 404, "code": "not_found", "retryable": False},
                headers=PROBLEM,
            )
        ],
        seen,
    )
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with pytest.raises(RemoteError) as info:
            await c.get_json("/v1/x")
    assert info.value.status == 404 and not info.value.retryable and len(seen) == 1


async def test_wait_for_job_polls_until_terminal() -> None:
    seen: list[httpx.Request] = []
    t = transport(
        [
            httpx.Response(200, json={"job_id": "j", "status": "queued"}),
            httpx.Response(200, json={"job_id": "j", "status": "running"}),
            httpx.Response(200, json={"job_id": "j", "status": "succeeded", "result": {"n": 1}}),
        ],
        seen,
    )
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        job = await c.wait_for_job("/v1/jobs/j")
    assert job["result"] == {"n": 1} and len(seen) == 3


async def test_wait_for_job_timeout() -> None:
    limits = ClientLimits(job_poll_interval_ms=1, job_wait_timeout_ms=10)
    t = httpx.MockTransport(lambda r: httpx.Response(200, json={"status": "running"}))
    async with ServiceClient("http://svc", limits, transport=t) as c:
        with pytest.raises(TimeoutError):
            await c.wait_for_job("/v1/jobs/j")
