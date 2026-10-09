"""«Перевищення бюджету зупиняє виклики» — on the real service (fake provider), memory and PostgreSQL stores."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient


def _setup(client: TestClient, h: Any, *, task_budget: float | None = 1.5) -> None:
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
    assert usage["totals"]["cost"]["amount"] <= 1.5  # never overspent
    budgets = {(b["scope_type"], b["scope_id"]): b for b in client.get("/v1/budgets").json()["items"]}
    status = budgets[("task", "shop-catalog")]["status"]
    assert status["spent"]["amount"] <= 1.5
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
    # 0.6 USD fits one call only (estimate ~0.58, actual ~0.27)
    assert _task_call(client, h, limits=tight).status_code == 429
    loose = {"budget": {"amount": 1000, "currency": "USD", "period": "day"}}
    assert _task_call(client, h, limits=loose).status_code == 200  # stored 5 USD still applies (min)


def test_request_budget_of_another_period_does_not_replace_the_stored_one(
    client: TestClient, fake: Any, h: Any
) -> None:
    """R07: the request budget is one more check of the most specific scope, never a replacement.

    Before WP-15 a request budget with another period replaced the stored task budget, and ``run`` without
    ``run_id`` was then skipped - the call went through with no task budget at all."""
    _setup(client, h, task_budget=0.6)  # 0.6 USD fits one call only (estimate ~0.58, actual ~0.27)
    loose_run = {"budget": {"amount": 1000, "currency": "USD", "period": "run"}}
    first = _task_call(client, h, limits=loose_run)
    assert first.status_code == 200
    statuses = {(b["limit"]["period"], b["scope_type"]) for b in first.json()["budget"]}
    assert {("day", "task"), ("run", "task"), ("day", "platform")} <= statuses
    second = _task_call(client, h, limits=loose_run)
    assert second.status_code == 429
    assert second.json()["details"]["scope_type"] == "task"
    assert second.json()["details"]["period"] == "day"  # the stored budget stopped it
    assert len(fake.calls) == 1


def test_request_budget_without_scope_ids_narrows_the_platform_budget(
    make_client: Callable[..., TestClient], fake: Any, h: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A request with no source/task (e.g. the assistant's onboarding) narrows the platform scope; the platform
    budget itself still applies even when the request budget has another period."""
    monkeypatch.setenv("JANE_LLM_LIMITS__LLM__BUDGET__AMOUNT", "0.6")
    client = make_client()
    _setup(client, h, task_budget=None)
    loose = {"budget": {"amount": 1000, "currency": "USD", "period": "run"}}
    assert (
        client.post("/v1/completions", json=h.completion(limits=loose), headers=h.idem()).status_code == 200
    )
    stopped = client.post("/v1/completions", json=h.completion(limits=loose), headers=h.idem())
    assert stopped.status_code == 429
    assert stopped.json()["details"]["scope_type"] == "platform"
    assert stopped.json()["details"]["period"] == "day"
    assert len(fake.calls) == 1


def test_run_budget_counts_per_run_id_or_per_request(client: TestClient, fake: Any, h: Any) -> None:
    """``period: run``: one window per ``scope.run_id``; without ``run_id`` the request itself is the run."""
    _setup(client, h, task_budget=None)
    per_run = {"budget": {"amount": 0.6, "currency": "USD", "period": "run"}}

    def call(run_id: str | None) -> Any:
        scope = {"purpose": "onboarding", "task_id": "shop-catalog"}
        if run_id:
            scope["run_id"] = run_id
        return client.post(
            "/v1/completions", json=h.completion(scope=scope, limits=per_run), headers=h.idem()
        )

    first = call("asst-run-1")
    assert first.status_code == 200
    run_status = next(b for b in first.json()["budget"] if b["limit"]["period"] == "run")
    assert run_status["scope_type"] == "task" and run_status["exhausted"] is False
    assert "resets_at" not in run_status
    over = call("asst-run-1")
    assert over.status_code == 429 and over.json()["details"]["period"] == "run"
    assert "Retry-After" not in over.headers  # a run window never resets by time
    assert call("asst-run-2").status_code == 200  # another run has its own window
    assert call(None).status_code == 200  # no run_id: this request is the run
    assert call(None).status_code == 200
    assert len(fake.calls) == 4
    # ... and it is enforced, not skipped: a call that does not fit the run budget of its own request is refused
    tiny = h.completion(
        scope={"purpose": "onboarding", "task_id": "shop-catalog"},
        limits={"budget": {"amount": 0.1, "currency": "USD", "period": "run"}},
    )
    refused = client.post("/v1/completions", json=tiny, headers=h.idem())
    assert refused.status_code == 429 and refused.json()["details"]["period"] == "run"
    assert len(fake.calls) == 4


@pytest.mark.parametrize(
    "where",
    ["platform-config", "task-definition", "request-run"],
)
def test_zero_budget_allows_no_call_even_for_a_free_model(
    make_client: Callable[..., TestClient], fake: Any, h: Any, monkeypatch: pytest.MonkeyPatch, where: str
) -> None:
    """R13: ``amount: 0`` means "LLM off" for that scope - the free ``fake`` model is refused too, without a
    provider call; ``exhausted`` is ``spent >= limit``. The same rule as the assistant's own check."""
    if where == "platform-config":
        monkeypatch.setenv("JANE_LLM_LIMITS__LLM__BUDGET__AMOUNT", "0")
    client = make_client()
    body = h.completion(scope={"purpose": "onboarding", "task_id": "t0", "run_id": "asst-run-0"})
    if where == "task-definition":
        zero = {
            "scope_type": "task",
            "scope_id": "t0",
            "budget": {"amount": 0, "currency": "USD", "period": "run"},
        }
        assert client.put("/v1/budgets/task/t0", json=zero).status_code == 200
    if where == "request-run":
        body["limits"] = {"budget": {"amount": 0, "currency": "USD", "period": "run"}}
    r = client.post("/v1/completions", json=body, headers=h.idem())
    assert r.status_code == 429 and r.json()["code"] == "budget_exhausted"
    assert r.json()["details"]["limit"]["amount"] == 0
    assert fake.calls == []
    budgets = {(b["scope_type"], b["scope_id"]): b for b in client.get("/v1/budgets").json()["items"]}
    if where == "platform-config":
        assert budgets[("platform", "platform")]["status"]["exhausted"] is True
    # a positive budget lets the same free call through
    ok = h.completion(scope={"purpose": "onboarding", "task_id": "t1", "run_id": "asst-run-0"})
    ok["limits"] = {"budget": {"amount": 0.01, "currency": "USD", "period": "run"}}
    expected = 429 if where == "platform-config" else 200
    assert client.post("/v1/completions", json=ok, headers=h.idem()).status_code == expected


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


def test_source_budget_stops_handler_calls(client: TestClient, fake: Any, h: Any) -> None:
    """A money budget on the ``source`` level applies to invocations whose ``context.trace.source_id`` matches."""
    assert client.put("/v1/providers/fake", json=h.priced_fake).status_code == 200
    budget = {
        "scope_type": "source",
        "scope_id": "news-tg",
        "budget": {"amount": 2, "currency": "USD", "period": "day"},
    }
    assert client.put("/v1/budgets/source/news-tg", json=budget).status_code == 200
    statuses = []
    for i in range(30):
        inv = {
            "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
            "inputs": [{"kind": "material", "material": _material(f"Концерт {i}")}],
            "context": {"trace": {"source_id": "news-tg", "task_id": f"task-{i}"}},
            "delivery": {"delivery_key": f"src-{i}"},
        }
        res = client.post("/v1/invocations", json=inv, headers={"Idempotency-Key": f"src-{i}"}).json()
        statuses.append(res["status"])
        if res["status"] == "failed":
            assert res["failure"]["kind"] == "budget_exhausted"
            assert res["failure"]["details"]["scope_type"] == "source"
            assert res["failure"]["details"]["scope_id"] == "news-tg"
            break
    assert statuses[-1] == "failed" and len(statuses) > 1
    calls = len(fake.calls)
    assert calls == len(statuses) - 1  # the stopped invocation made no provider call
    # Smaller completions for the same source still fit until the rest of the budget is used, then 429;
    # another source is not affected.
    for _ in range(10):
        same = client.post(
            "/v1/completions",
            json=h.completion(scope={"purpose": "other", "source_id": "news-tg"}),
            headers=h.idem(),
        )
        if same.status_code != 200:
            break
    assert same.status_code == 429 and same.json()["details"]["scope_type"] == "source"
    calls = len(fake.calls)
    other = client.post(
        "/v1/completions",
        json=h.completion(scope={"purpose": "other", "source_id": "shop"}),
        headers=h.idem(),
    )
    assert other.status_code == 200
    assert len(fake.calls) == calls + 1
    usage = client.get("/v1/usage", params={"scope_type": "source", "scope_id": "news-tg"}).json()
    assert usage["totals"]["cost"]["amount"] <= 2


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
