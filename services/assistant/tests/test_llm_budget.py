"""R13/R14 (WP-15): the assistant's LLM budget and long model calls.

* The assistant sends the whole ``limits.llm.budget`` with ``scope.run_id`` = its run; the **real** LLM gateway
  (``jane_llm``, fake provider, memory store) counts a ``period: run`` budget across every call of the run -
  also from another job or instance of the same onboarding session - and refuses the call that no longer fits.
* ``amount: 0`` stops the assistant before any call, exactly as the gateway refuses it.
* ``mode=async`` waits for the gateway's job; a job failed on the budget is the same ``BudgetExhausted``.
* A model call longer than the neighbours' ``clients.request_timeout_ms`` finishes within
  ``llm_call.request_timeout_ms`` (real HTTP: a contract fake of the gateway on uvicorn).
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import httpx
import pytest
from assistant_fakes import WAIT_S
from assistant_fakes.llm import FakeLlm
from assistant_fakes.server import Server
from assistant_fakes.site import material, page
from fastapi.testclient import TestClient

from jane_assistant.app import build_app
from jane_assistant.clients import LlmClient
from jane_assistant.llm import BudgetExhausted, LlmSession, part
from jane_assistant.settings import LlmLimits, Settings
from jane_kit.clients import ClientLimits, ServiceClient
from jane_llm.app import build_app as build_llm_app
from jane_llm.providers import ADAPTERS, FakeProvider, ProviderRequest, ProviderResponse, ResolvedConnection
from jane_llm.settings import ServiceLimits as LlmServiceLimits
from jane_llm.settings import Settings as LlmSettings
from jane_llm.store import MemoryStore

SCHEMA = {"type": "object", "required": ["ok"], "properties": {"ok": {"type": "boolean"}}}
PRICED = {  # 1000 USD per million tokens: one call costs tenths of a dollar
    "provider_id": "fake",
    "kind": "fake",
    "enabled": True,
    "models": [
        {
            "model_id": "fake-deterministic-1",
            "max_context_tokens": 128000,
            "supports_structured_output": True,
            "pricing": {"input_per_mtok": 1000, "output_per_mtok": 1000, "currency": "USD"},
        }
    ],
}


class CountingProvider(FakeProvider):
    """The gateway's real fake provider plus a call counter (the provider is the gateway's neighbour)."""

    def __init__(self) -> None:
        self.calls = 0

    async def complete(
        self, request: ProviderRequest, connection: ResolvedConnection | None, limits: LlmServiceLimits
    ) -> ProviderResponse:
        self.calls += 1
        return await super().complete(request, connection, limits)


class RecordingClient(LlmClient):
    """The assistant's real gateway client; keeps every result to read the gateway's ``BudgetStatus``."""

    def __init__(self, client: ServiceClient) -> None:
        super().__init__(client)
        self.results: list[dict[str, Any]] = []

    async def complete(self, request: Mapping[str, Any], key: str) -> dict[str, Any]:
        result = await super().complete(request, key)
        self.results.append(result)
        return result


@contextmanager
def gateway(*, priced: bool = True) -> Iterator[tuple[TestClient, httpx.ASGITransport, CountingProvider]]:
    """The real LLM service in process: admin calls through ``TestClient``, the assistant's calls through an
    ASGI transport (all of one test in one event loop)."""
    provider = CountingProvider()
    app = build_llm_app(
        LlmSettings(log_format="console", store="memory"),
        store=MemoryStore(),
        adapters={**ADAPTERS, "fake": provider},
    )
    with TestClient(app) as admin:
        if priced:
            assert admin.put("/v1/providers/fake", json=PRICED).status_code == 200
        yield admin, httpx.ASGITransport(app=app), provider


def budget(amount: float, period: str = "run") -> dict[str, Any]:
    return {"amount": amount, "currency": "USD", "period": period}


def session(client: LlmClient, job: str, run: str, amount: float, mode: str = "sync") -> LlmSession:
    limits = LlmLimits(max_output_tokens_per_request=50, budget=budget(amount))
    return LlmSession(client, limits, "onboarding", job, run_id=run, mode=mode)


def run_spent(result: dict[str, Any]) -> float:
    status = next(b for b in result["budget"] if b["limit"]["period"] == "run")
    assert status["scope_type"] == "platform"  # onboarding has no source/task: the most specific scope
    return float(status["spent"]["amount"])


def ask(llm: LlmSession, text: str = "page") -> Any:
    return llm.ask("probe", "Answer with the schema.", [part("page", text)], SCHEMA, model="default")


def test_the_gateway_counts_the_run_budget_across_sessions_of_one_run() -> None:
    with gateway() as (_, transport, provider):

        async def scenario() -> None:
            client = RecordingClient(ServiceClient("http://llm.test", transport=transport))
            a = session(client, "job-a", "onb_1", 100)
            await ask(a)
            b = session(
                client, "job-b", "onb_1", 100
            )  # e.g. the job after candidate selection, another instance
            await ask(b, "another page")
            c = session(client, "job-c", "onb_2", 100)
            await ask(c)
            spent = [run_spent(r) for r in client.results]
            assert spent[0] == pytest.approx(a.spent) and a.spent > 0
            assert spent[1] == pytest.approx(a.spent + b.spent)  # one window for the run, not per session
            assert spent[2] == pytest.approx(c.spent)  # another run has its own window
            # The run spent its budget: a fresh session of the same run (local spent 0) is refused by the gateway.
            d = session(client, "job-d", "onb_1", spent[1])
            with pytest.raises(BudgetExhausted) as exc:
                await ask(d)
            assert exc.value.details is not None and exc.value.details["period"] == "run"
            assert d.calls == 1 and d.spent == 0
            await client.aclose()

        asyncio.run(scenario())
        assert provider.calls == 3  # the refused call never reached the provider


def test_zero_budget_means_no_call_in_the_assistant_and_in_the_gateway() -> None:
    with gateway(priced=False) as (admin, transport, provider):  # the free model: cost 0

        async def scenario() -> None:
            client = RecordingClient(ServiceClient("http://llm.test", transport=transport))
            off = session(client, "job-0", "onb_0", 0)
            with pytest.raises(BudgetExhausted):
                await ask(off)
            assert off.calls == 0 and client.results == []  # stopped before any request
            free = session(client, "job-1", "onb_1", 0.01)
            assert set(await ask(free)) == {"ok"}  # a positive budget lets the free model through
            assert free.spent == 0
            await client.aclose()

        asyncio.run(scenario())
        assert provider.calls == 1
        same = {
            "model": "default",
            "instructions": "Answer with the schema.",
            "data": [{"name": "page", "text": "page"}],
            "output_schema": SCHEMA,
            "scope": {"purpose": "onboarding", "run_id": "onb_0"},
            "limits": {"budget": budget(0)},
        }
        refused = admin.post("/v1/completions", json=same, headers={"Idempotency-Key": "zero-1"})
        assert refused.status_code == 429 and refused.json()["code"] == "budget_exhausted"
        assert provider.calls == 1


def test_async_mode_waits_for_the_gateway_job_and_reports_its_budget_failure() -> None:
    with gateway() as (_, transport, provider):

        async def scenario() -> None:
            limits = ClientLimits(job_poll_interval_ms=10)
            client = RecordingClient(ServiceClient("http://llm.test", limits, transport=transport))
            first = session(client, "job-a", "imp_1", 100, mode="async")
            assert set(await ask(first)) == {"ok"}
            assert first.spent > 0 and run_spent(client.results[0]) == pytest.approx(first.spent)
            tight = session(client, "job-b", "imp_1", first.spent, mode="async")
            with pytest.raises(BudgetExhausted):  # the gateway's job failed with budget_exhausted
                await ask(tight)
            await client.aclose()

        asyncio.run(scenario())
        assert provider.calls == 1


def _unknown(client: TestClient) -> dict[str, Any]:
    body = {
        "source_id": "shop-example",
        "forward_unknown_to_llm": True,
        "material": material(
            "https://shop.example.test/events/1", page("event", "Concert", ""), "shop-example"
        ),
    }
    r = client.post("/v1/unknown-materials", json=body, headers={"Idempotency-Key": "slow-llm-1"})
    assert r.status_code == 202, r.text
    deadline = time.monotonic() + WAIT_S
    while True:
        job: dict[str, Any] = client.get(f"/v1/jobs/{r.json()['job_id']}").json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            return job
        assert time.monotonic() < deadline, job
        time.sleep(0.02)


@pytest.mark.parametrize("own_timeout", [True, False])
def test_a_model_call_longer_than_the_neighbour_timeout_finishes_within_its_own(
    contracts: Path, monkeypatch: pytest.MonkeyPatch, own_timeout: bool
) -> None:
    """``clients.request_timeout_ms`` (the profile's web/service timeout) no longer cuts a model call; the control
    with ``llm_call.request_timeout_ms`` as short as it shows the call really outlasts it."""
    llm = FakeLlm(contracts)
    llm.knobs.delay_s = 1.0
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__CLIENTS__REQUEST_TIMEOUT_MS", "300")
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__CLIENTS__RETRIES__MAX_ATTEMPTS", "1")
    if not own_timeout:
        monkeypatch.setenv("JANE_ASSISTANT_LIMITS__LLM_CALL__REQUEST_TIMEOUT_MS", "300")
    with Server(llm.app) as server:
        settings = Settings(log_format="console", contracts_dir=contracts, llm_url=server.url)
        with TestClient(build_app(settings)) as client:
            job = _unknown(client)
    assert llm.app.violations == []
    if own_timeout:
        assert job["status"] == "succeeded", job
        assert job["result"]["classification"]["material_type"] == "event"
    else:
        assert job["status"] == "failed" and "Timeout" in job["error"]["detail"], job
