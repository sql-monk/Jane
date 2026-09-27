"""Several real service processes share budgets and usage through PostgreSQL (not process memory)."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx
import pytest

pytestmark = pytest.mark.integration

BUDGET = 3.0


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture
def instances(h: Any) -> Iterator[list[str]]:
    dsn = h.pg_dsn()
    if dsn is None:
        pytest.skip("dev stack PostgreSQL not running (just up --project jane-wp10 postgres)")
    schema = h.new_schema()
    procs: list[subprocess.Popen[bytes]] = []
    urls = []
    try:
        for _ in range(2):
            port = _free_port()
            env = {
                **os.environ,
                "JANE_LLM_PORT": str(port),
                "JANE_LLM_STORE": "postgres",
                "JANE_LLM_DATABASE_URL": dsn,
                "JANE_LLM_DB_SCHEMA": schema,
                "JANE_LLM_LOG_LEVEL": "WARNING",
                "JANE_LLM_LIMITS__LLM__MAX_REQUESTS_PER_MINUTE": "10000",
            }
            procs.append(
                subprocess.Popen(
                    [sys.executable, "-m", "jane_llm"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            urls.append(f"http://127.0.0.1:{port}")
        deadline = time.monotonic() + 60
        for url in urls:
            while True:
                try:
                    if httpx.get(f"{url}/v1/health", timeout=1).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                if time.monotonic() > deadline:
                    pytest.fail(f"instance {url} did not become healthy")
                time.sleep(0.2)
        yield urls
    finally:
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
        h.drop_schema(dsn, schema)


def test_budget_is_shared_between_instances(instances: list[str], h: Any) -> None:
    a, b = instances
    assert httpx.put(f"{a}/v1/providers/fake", json=h.priced_fake).status_code == 200
    budget = {
        "scope_type": "task",
        "scope_id": "shared",
        "budget": {"amount": BUDGET, "currency": "USD", "period": "day"},
    }
    assert httpx.put(f"{b}/v1/budgets/task/shared", json=budget).status_code == 200  # set on B, applies on A

    def worker(url: str) -> list[tuple[int, float]]:
        out = []
        with httpx.Client(base_url=url, timeout=30) as c:
            for _ in range(15):
                body = h.completion(scope={"purpose": "handler", "task_id": "shared"})
                r = c.post("/v1/completions", json=body, headers={"Idempotency-Key": uuid.uuid4().hex})
                cost = r.json()["usage"]["cost"]["amount"] if r.status_code == 200 else 0.0
                out.append((r.status_code, cost))
        return out

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = [x for f in [pool.submit(worker, u) for u in instances * 4] for x in f.result()]

    ok = [c for s, c in results if s == 200]
    rejected = [s for s, _ in results if s == 429]
    assert ok and rejected
    assert {s for s, _ in results} <= {200, 429}
    spent_by_responses = sum(ok)
    assert spent_by_responses <= BUDGET  # the two instances together never overspend

    for url in instances:  # both instances see the same ledger and counter
        usage = httpx.get(f"{url}/v1/usage", params={"scope_type": "task", "scope_id": "shared"}).json()
        assert usage["totals"]["requests"] == len(ok)
        assert usage["totals"]["cost"]["amount"] == pytest.approx(spent_by_responses)
        status = next(x for x in httpx.get(f"{url}/v1/budgets").json()["items"] if x["scope_id"] == "shared")
        assert status["status"]["spent"]["amount"] == pytest.approx(spent_by_responses)
        body = h.completion(scope={"purpose": "handler", "task_id": "shared"})
        r = httpx.post(f"{url}/v1/completions", json=body, headers={"Idempotency-Key": uuid.uuid4().hex})
        assert r.status_code == 429
        assert r.json()["code"] == "budget_exhausted"


def test_idempotency_is_shared_between_instances(instances: list[str], h: Any) -> None:
    a, b = instances
    assert httpx.put(f"{a}/v1/providers/fake", json=h.priced_fake).status_code == 200
    key = {"Idempotency-Key": uuid.uuid4().hex}
    body = h.completion(scope={"purpose": "other", "task_id": "idem"})
    first = httpx.post(f"{a}/v1/completions", json=body, headers=key)
    second = httpx.post(f"{b}/v1/completions", json=body, headers=key)
    assert first.status_code == second.status_code == 200
    assert second.headers.get("Idempotency-Replayed") == "true"
    assert second.json()["completion_id"] == first.json()["completion_id"]
    usage = httpx.get(f"{b}/v1/usage", params={"scope_type": "task", "scope_id": "idem"}).json()
    assert usage["totals"]["requests"] == 1
