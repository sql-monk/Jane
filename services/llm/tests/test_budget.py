"""«Перевищення бюджету зупиняє виклики» — on the real service (fake provider), memory and PostgreSQL stores."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient


def _setup(client: TestClient, h: Any, *, task_budget: float | None = 0.5) -> None:
    assert client.put("/v1/providers/fake", json=h.priced_fake).status_code == 200
    if task_budget is not None:
        r = client.put(
            "/v1/budgets/task/shop-catalog",
            json={
                "scope_type": "task",
                "scope_id": "shop-catalog",
                "budget": {"amount": task_budget, "currency": "USD", "period": "day"},
            },
        )
        assert r.status_code == 200, r.text


def _task_call(client: TestClient, h: Any, **kw: Any) -> Any:
    body = h.completion(scope={"purpose": "handler", "task_id": "shop-catalog", "source_id": "shop"}, **kw)
    return client.post("/v1/completions", json=body, headers=h.idem())


def test_exhausted_task_budget_stops_provider_calls(client: TestClient, fake: Any, h: Any) -> None:
    _setup(client, h)
    ok = 0
    for _ in range(100):
        r = _task_call(client, h)
        if r.status_code != 200:
            break
        ok += 1
        assert r.json()["valid"] is True
    assert 0 < ok < 100
    assert r.status_code == 429
    problem = r.json()
    assert problem["code"] == "budget_exhausted"
    assert problem["retryable"] is False
    assert problem["details"]["scope_type"] == "task"
    assert problem["details"]["scope_id"] == "shop-catalog"
    assert "Retry-After" in r.headers

    calls_at_stop = len(fake.calls)
    assert calls_at_stop == ok  # the rejected request never reached the provider
    for _ in range(3):
        again = _task_call(client, h)
        assert again.status_code == 429
    assert len(fake.calls) == calls_at_stop

    usage = client.get("/v1/usage", params={"scope_type": "task", "scope_id": "shop-catalog"}).json()
    assert usage["totals"]["requests"] == ok
    assert usage["totals"]["cost"]["amount"] <= 0.5  # never overspent
    budgets = {(b["scope_type"], b["scope_id"]): b for b in client.get("/v1/budgets").json()["items"]}
    status = budgets[("task", "shop-catalog")]["status"]
    assert status["spent"]["amount"] <= 0.5
    assert status["spent"]["amount"] == pytest.approx(usage["totals"]["cost"]["amount"])

    # Another task without its own budget is limited only by the platform budget and still works.
    other = client.post(
        "/v1/completions",
        json=h.completion(scope={"purpose": "handler", "task_id": "other-task"}),
        headers=h.idem(),
    )
    assert other.status_code == 200
    assert len(fake.calls) == calls_at_stop + 1


def test_raising_the_budget_resumes_calls(client: TestClient, fake: Any, h: Any) -> None:
    _setup(client, h, task_budget=0.2)
    while _task_call(client, h).status_code == 200:
        pass
    assert _task_call(client, h).status_code == 429
    _setup(client, h, task_budget=5)
    assert _task_call(client, h).status_code == 200


def test_platform_budget_from_configuration(
    make_client: Callable[..., TestClient], fake: Any, h: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JANE_LLM_LIMITS__LLM__BUDGET__AMOUNT", "1.5")
    client = make_client()
    _setup(client, h, task_budget=None)
    codes = [
        client.post("/v1/completions", json=h.completion(), headers=h.idem()).status_code for _ in range(40)
    ]
    assert 200 in codes and codes[-1] == 429
    assert codes.index(429) == len(fake.calls)
    info = client.get("/v1/info").json()
    assert info["limits"]["defaults"]["llm"]["budget"] == {"amount": 1.5, "currency": "USD", "period": "day"}
    platform = next(b for b in client.get("/v1/budgets").json()["items"] if b["scope_type"] == "platform")
    assert platform["status"]["spent"]["amount"] <= 1.5


def test_request_budget_only_narrows(client: TestClient, fake: Any, h: Any) -> None:
    _setup(client, h, task_budget=5)
    tight = {"budget": {"amount": 0.6, "currency": "USD", "period": "day"}}
    first = _task_call(client, h, limits=tight)
    assert first.status_code == 200
    # 0.6 USD fits one call only (estimate ~0.41, actual ~0.27)
    assert _task_call(client, h, limits=tight).status_code == 429
    loose = {"budget": {"amount": 1000, "currency": "USD", "period": "day"}}
    assert _task_call(client, h, limits=loose).status_code == 200  # stored 5 USD still applies (min)


def test_idempotent_replay_does_not_spend_twice(client: TestClient, fake: Any, h: Any) -> None:
    _setup(client, h)
    headers = h.idem()
    body = h.completion(scope={"purpose": "handler", "task_id": "shop-catalog"})
    first = client.post("/v1/completions", json=body, headers=headers)
    second = client.post("/v1/completions", json=body, headers=headers)
    assert first.status_code == second.status_code == 200
    assert second.headers["Idempotency-Replayed"] == "true"
    assert second.json() == first.json()
    assert len(fake.calls) == 1
    usage = client.get("/v1/usage", params={"scope_type": "task", "scope_id": "shop-catalog"}).json()
    assert usage["totals"]["requests"] == 1


def test_handler_budget_failure_is_not_replayed_after_budget_increase(
    client: TestClient, fake: Any, h: Any
) -> None:
    _setup(client, h, task_budget=0.001)
    material_inv = {
        "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
        "inputs": [{"kind": "material", "material": _material("Концерт у суботу")}],
        "context": {"trace": {"task_id": "shop-catalog"}},
        "delivery": {"delivery_key": "budget-2"},
    }
    first = client.post("/v1/invocations", json=material_inv, headers={"Idempotency-Key": "budget-2"})
    assert first.json()["status"] == "failed"
    assert first.json()["failure"]["kind"] == "budget_exhausted"
    assert fake.calls == []
    _setup(client, h, task_budget=5)
    second = client.post("/v1/invocations", json=material_inv, headers={"Idempotency-Key": "budget-2"})
    assert second.json()["status"] in {"success", "empty"}
    assert "Idempotency-Replayed" not in second.headers
    assert len(fake.calls) == 1


def _material(text: str) -> dict[str, Any]:
    return {
        "material_id": "tg:-100:1",
        "observation_id": "obs_1",
        "source": {"source_id": "news-tg", "kind": "telegram"},
        "locator": {},
        "fetched_at": "2026-09-27T12:30:00Z",
        "format": {"media_type": "text/plain"},
        "revision": {"content_sha256": "0" * 64},
        "content": {"kind": "inline", "media_type": "text/plain", "encoding": "utf-8", "data": text},
        "collector": {"name": "telegram-collector", "version": "0.1.0"},
    }
