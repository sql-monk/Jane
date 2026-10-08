"""Delay of the deterministic ``fake`` provider: ``params.delay_ms`` and ``params.responses[].delay_ms``, bounded
by ``limits.fake.max_delay_ms`` (README, "Провайдери й підключення" / "Ліміти").

The provider is the real one; tests that check *which* delay applies only record it instead of waiting
(:meth:`FakeProvider._hold`), the others wait for real."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_llm.prompt import DataBlock, build_prompt
from jane_llm.providers import FakeProvider, ProviderError, ProviderRequest, ResolvedConnection
from jane_llm.providers.fake import HOLD_LOG_MESSAGE
from jane_llm.settings import FakeProviderLimits, ServiceLimits, Settings, resolve_service_limits


class RecordingFake(FakeProvider):
    """The real fake provider; the delay is recorded instead of waited for."""

    def __init__(self) -> None:
        self.held: list[float] = []

    async def _hold(self, seconds: float) -> None:
        self.held.append(seconds)


class HeldFake(FakeProvider):
    """The real fake provider (real waiting); ``started`` is set when a delay begins."""

    def __init__(self) -> None:
        self.started = threading.Event()
        self.calls = 0

    async def complete(self, request: Any, connection: Any, limits: Any) -> Any:
        self.calls += 1
        return await super().complete(request, connection, limits)

    async def _hold(self, seconds: float) -> None:
        self.started.set()
        await super()._hold(seconds)


def ask(
    fake: FakeProvider, params: dict[str, Any] | None, data: str, limits: ServiceLimits | None = None
) -> str:
    prompt = build_prompt("Classify.", [DataBlock("page", None, data)], structured=False)
    conn = None if params is None else ResolvedConnection("slow", "llm_provider", params)
    response = asyncio.run(
        fake.complete(ProviderRequest("m", prompt.system, prompt.user, 200), conn, limits or ServiceLimits())
    )
    return response.text


def test_connection_delay_applies_to_every_call() -> None:
    fake = RecordingFake()
    assert ask(fake, {"provider": "fake", "delay_ms": 1500}, "page one").startswith("fake:")
    assert ask(fake, {"provider": "fake", "delay_ms": 1500}, "page two").startswith("fake:")
    assert fake.held == [1.5, 1.5]
    assert ask(fake, {"provider": "fake"}, "no delay") and fake.held == [1.5, 1.5]  # absent: none
    assert ask(fake, None, "no connection") and fake.held == [1.5, 1.5]


def test_script_delay_overrides_and_a_delay_only_script_keeps_matching() -> None:
    params = {
        "provider": "fake",
        "delay_ms": 100,
        "responses": [
            {"when_data_contains": "slow", "delay_ms": 2000},  # no answer: sets the delay only
            {"when_data_contains": "other", "delay_ms": 3000},  # does not match "slow page"
            {"when_data_contains": "page", "output_text": "answered", "delay_ms": 4000},
            {"when_data_contains": "fast", "output_text": "at once", "delay_ms": 0},
        ],
    }
    fake = RecordingFake()
    assert ask(fake, params, "slow page") == "answered"  # the first matching delay wins, the answer follows
    assert ask(fake, params, "a page") == "answered"  # the answering script's own delay
    assert ask(fake, params, "fast") == "at once"  # 0 overrides the connection delay
    assert ask(fake, params, "unmatched").startswith("fake:")  # no script: the connection delay
    assert fake.held == [2.0, 4.0, 0.1]


def test_delay_is_bounded_by_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    assert ServiceLimits().fake.max_delay_ms == 30_000  # documented default
    fake = RecordingFake()
    params = {"provider": "fake", "delay_ms": 600_000}
    ask(fake, params, "x")
    assert fake.held == [30.0]
    ask(fake, params, "x", ServiceLimits(fake=FakeProviderLimits(max_delay_ms=250)))
    assert fake.held == [30.0, 0.25]
    ask(fake, params, "x", ServiceLimits(fake=FakeProviderLimits(max_delay_ms=0)))  # 0: delays are off
    assert fake.held == [30.0, 0.25]

    monkeypatch.setenv("JANE_LLM_LIMITS__FAKE__MAX_DELAY_MS", "1200")
    configured = resolve_service_limits(Settings(log_format="console", store="memory")).limits
    assert configured.fake.max_delay_ms == 1200
    ask(fake, params, "x", configured)
    assert fake.held[-1] == 1.2


@pytest.mark.parametrize("bad", [-1, 1.5, "1000", True, None])
def test_invalid_delay_fails_the_call(bad: Any) -> None:
    for params in (
        {"provider": "fake", "delay_ms": bad},
        {"provider": "fake", "responses": [{"when_data_contains": "x", "delay_ms": bad}]},
    ):
        with pytest.raises(ProviderError) as exc:
            ask(RecordingFake(), params, "x")
        assert exc.value.retryable is False
        assert "delay_ms must be a non-negative integer" in str(exc.value)


def test_scripted_error_comes_after_the_delay() -> None:
    fake = RecordingFake()
    params = {
        "provider": "fake",
        "responses": [{"when_data_contains": "boom", "error": "unavailable", "delay_ms": 700}],
    }
    with pytest.raises(ProviderError) as exc:
        ask(fake, params, "boom")
    assert exc.value.retryable is True
    assert fake.held == [0.7]


def test_real_wait_is_logged_before_it_starts(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="jane_llm.providers.fake")
    started = time.monotonic()
    ask(FakeProvider(), {"provider": "fake", "delay_ms": 200}, "x")
    assert time.monotonic() - started >= 0.2
    [record] = [r for r in caplog.records if r.getMessage() == HOLD_LOG_MESSAGE]
    assert (record.connection_id, record.delay_ms, record.requested_delay_ms) == ("slow", 200, 200)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------- through the gateway
@pytest.fixture
def fake() -> HeldFake:
    """Replaces the conftest ``fake`` adapter for the app of this module (``make_client``)."""
    return HeldFake()


def slow_provider(client: TestClient, delay_ms: int) -> None:
    conn = {
        "connection_id": "slow",
        "kind": "llm_provider",
        "params": {"provider": "fake", "delay_ms": delay_ms},
    }
    assert client.put("/v1/connections/slow", json=conn).status_code == 201
    provider = {
        "provider_id": "slow",
        "kind": "fake",
        "connection_id": "slow",
        "enabled": True,
        "models": [
            {
                "model_id": "fake-deterministic-1",
                "pricing": {"input_per_mtok": 1, "output_per_mtok": 1, "currency": "USD"},
            }
        ],
    }
    assert client.put("/v1/providers/slow", json=provider).status_code == 200


def test_completion_in_flight_holds_its_idempotency_key(
    make_client: Callable[..., TestClient], fake: HeldFake, h: Any
) -> None:
    """R-04 on the service: while a held synchronous completion runs, the same key and body get 409
    ``idempotency_in_progress``, another body 422; afterwards the stored result. One provider call."""
    client = make_client()
    slow_provider(client, 1500)
    body = h.completion(model="slow/fake-deterministic-1", scope={"purpose": "other", "task_id": "t-held"})
    headers = h.idem()
    with ThreadPoolExecutor(1) as pool:
        pending = pool.submit(client.post, "/v1/completions", json=body, headers=headers)
        assert fake.started.wait(30), "the provider call never started its delay"
        busy = client.post("/v1/completions", json=body, headers=headers)
        assert busy.status_code == 409 and busy.json()["code"] == "idempotency_in_progress", busy.text
        assert busy.json()["retryable"] is True
        other = client.post("/v1/completions", json={**body, "instructions": "Other."}, headers=headers)
        assert other.status_code == 422 and other.json()["code"] == "idempotency_key_reused", other.text
        assert not pending.done()
        first = pending.result(timeout=30)
    assert first.status_code == 200, first.text
    again = client.post("/v1/completions", json=body, headers=headers)
    assert again.status_code == 200 and again.headers["Idempotency-Replayed"] == "true"
    assert again.json() == first.json()
    assert fake.calls == 1
    usage = client.get("/v1/usage", params={"scope_type": "task", "scope_id": "t-held"}).json()
    assert usage["totals"]["requests"] == 1, json.dumps(usage)
