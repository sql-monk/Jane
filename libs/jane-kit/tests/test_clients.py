from __future__ import annotations

import httpx
import pytest

from jane_kit.clients import ClientLimits, RemoteError, ServiceClient
from jane_kit.logs import bind_context

FAST = ClientLimits(max_retries=2, backoff_base_s=0, backoff_max_s=0, job_poll_interval_s=0.001)


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
        "type": "urn:jane:problem:unavailable",
        "title": "u",
        "status": 503,
        "code": "unavailable",
        "retryable": True,
    }
    t = transport(
        [httpx.Response(503, json=problem, headers={"content-type": "application/problem+json"})], seen
    )
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with pytest.raises(RemoteError) as info:
            await c.post_json("/v1/x", {})
    assert len(seen) == 1
    assert info.value.problem is not None and info.value.problem.code == "unavailable"
    assert info.value.retryable


async def test_post_with_idempotency_key_is_retried_and_headers_propagated() -> None:
    seen: list[httpx.Request] = []
    t = transport([httpx.Response(502), httpx.Response(201, json={"id": 1})], seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with bind_context(request_id="req-7"):
            assert await c.post_json("/v1/x", {"a": 1}, idempotency_key="k1") == {"id": 1}
    assert len(seen) == 2
    assert all(r.headers["Idempotency-Key"] == "k1" for r in seen)
    assert seen[0].headers["X-Request-ID"] == "req-7"


async def test_retries_exhausted_raises() -> None:
    seen: list[httpx.Request] = []
    t = transport([httpx.Response(503)] * 3, seen)
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        with pytest.raises(RemoteError):
            await c.get_json("/v1/x")
    assert len(seen) == 3  # 1 + max_retries


async def test_client_error_not_retried() -> None:
    seen: list[httpx.Request] = []
    t = transport(
        [
            httpx.Response(
                404,
                json={"title": "nf", "status": 404, "code": "not_found"},
                headers={"content-type": "application/problem+json"},
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
            httpx.Response(200, json={"job_id": "j", "state": "queued"}),
            httpx.Response(200, json={"job_id": "j", "state": "running"}),
            httpx.Response(200, json={"job_id": "j", "state": "succeeded", "result": 1}),
        ],
        seen,
    )
    async with ServiceClient("http://svc", FAST, transport=t) as c:
        job = await c.wait_for_job("/v1/jobs/j")
    assert job["result"] == 1 and len(seen) == 3


async def test_wait_for_job_timeout() -> None:
    limits = ClientLimits(job_poll_interval_s=0.001, job_wait_timeout_s=0.01)
    t = httpx.MockTransport(lambda r: httpx.Response(200, json={"state": "running"}))
    async with ServiceClient("http://svc", limits, transport=t) as c:
        with pytest.raises(TimeoutError):
            await c.wait_for_job("/v1/jobs/j")
