"""Several assistant instances on the shared PostgreSQL state (``@pytest.mark.integration``).

PostgreSQL: ``JANE_WP11_STATE_DSN`` or the dev stack (``just up --project jane-wp11 postgres`` and
``just test assistant -m integration`` with ``JANE_STACK_FILE=.jane/stack-jane-wp11.json``). Each test
module uses its own schema and drops it afterwards. Neighbours are the same contract-bound fakes for all
instances of a test.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections.abc import Iterator
from typing import Any

import httpx
import psycopg
import pytest
from assistant_fakes import World
from fastapi.testclient import TestClient
from psycopg import sql
from pydantic import SecretStr

from jane_assistant.settings import Settings
from jane_kit.devstack import load_stack

pytestmark = pytest.mark.integration


def _dsn() -> str | None:
    if env := os.environ.get("JANE_WP11_STATE_DSN"):
        return env
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        return None
    return str(stack.get("postgres", "dsn"))


@pytest.fixture(scope="module")
def pg() -> Iterator[tuple[str, str]]:
    value = _dsn()
    if value is None:
        pytest.skip("no PostgreSQL: set JANE_WP11_STATE_DSN or run `just up --project jane-wp11 postgres`")
    schema = f"wp11_test_{uuid.uuid4().hex[:8]}"
    yield value, schema
    with psycopg.connect(value, autocommit=True) as conn:
        conn.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))


def settings(w: World, pg: tuple[str, str], name: str) -> Settings:
    return Settings(
        log_format="console",
        contracts_dir=w.contracts,
        state_dsn=SecretStr(pg[0]),
        state_schema=pg[1],
        instance_id=name,
    )


def wait(
    client: TestClient, job_id: str, statuses: set[str] | None = None, timeout: float = 30
) -> dict[str, Any]:
    wanted = statuses or {"succeeded", "failed", "cancelled"}
    deadline = time.monotonic() + timeout
    while True:
        job: dict[str, Any] = client.get(f"/v1/jobs/{job_id}").json()
        if job.get("status") in wanted:
            return job
        assert time.monotonic() < deadline, job
        time.sleep(0.05)


def start(client: TestClient, query: str, key: str) -> httpx.Response:
    r: httpx.Response = client.post(
        "/v1/onboarding-sessions",
        json={"query": query, "expected_entity_types": ["product"]},
        headers={"Idempotency-Key": key},
    )
    assert r.status_code == 202, r.text
    return r


def test_session_started_on_a_is_continued_on_b(w: World, pg: tuple[str, str]) -> None:
    with w.instance(settings(w, pg, "a")) as a, w.instance(settings(w, pg, "b")) as b:
        assert b.get("/v1/info").json()["capabilities"]["state"] == "postgresql"
        assert b.get("/v1/health").json()["checks"]["state"]["status"] == "ok"
        first = start(a, "Shop Example kettles", "multi-1")
        job_id, sid = first.json()["job_id"], first.json()["labels"]["session_id"]
        assert wait(b, job_id)["result"]["status"] == "needs_disambiguation"  # job of A read through B

        replay = start(b, "Shop Example kettles", "multi-1")  # same Idempotency-Key on another instance
        assert replay.headers["Idempotency-Replayed"] == "true"
        assert replay.json()["job_id"] == job_id
        reused = b.post(
            "/v1/onboarding-sessions", json={"query": "other"}, headers={"Idempotency-Key": "multi-1"}
        )
        assert reused.status_code == 422 and reused.json()["code"] == "idempotency_key_reused"

        assert b.get(f"/v1/onboarding-sessions/{sid}").json()["status"] == "needs_disambiguation"
        sel = b.post(f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"})
        assert sel.status_code == 200
        done = wait(a, sel.json()["job_id"])  # job of B read through A
        assert done["result"]["status"] == "proposals_ready"
        session = a.get(f"/v1/onboarding-sessions/{sid}").json()
        assert session["status"] == "proposals_ready" and len(session["proposals"]) == 2

        acc = a.post(
            f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
            json={"activate": False},
            headers={"Idempotency-Key": "multi-2"},
        )
        assert acc.status_code == 202
        result = wait(b, acc.json()["job_id"])
        assert result["status"] == "succeeded", result
        w.spec.validate_component("AcceptanceResult", result["result"])
        again = b.post(
            f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
            json={"activate": False},
            headers={"Idempotency-Key": "multi-2"},
        )
        assert (
            again.headers["Idempotency-Replayed"] == "true" and again.json()["job_id"] == acc.json()["job_id"]
        )
        assert b.get(f"/v1/onboarding-sessions/{sid}").json()["status"] == "completed"
    assert len(w.registry.versions["shop.example.test.product-extractor"]) == 1  # published once


def test_concurrent_selection_on_two_instances_is_serialized(w: World, pg: tuple[str, str]) -> None:
    with w.instance(settings(w, pg, "a")) as a, w.instance(settings(w, pg, "b")) as b:
        r = start(a, "Shop Example kettles", "race-1")
        sid = r.json()["labels"]["session_id"]
        wait(a, r.json()["job_id"])
        barrier = threading.Barrier(2)
        results: dict[str, httpx.Response] = {}

        def pick(name: str, client: TestClient, cand: str) -> None:
            barrier.wait()
            results[name] = client.post(
                f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": cand}
            )

        threads = [
            threading.Thread(target=pick, args=("a", a, "cand_1")),
            threading.Thread(target=pick, args=("b", b, "cand_2")),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        codes = sorted(r.status_code for r in results.values())
        assert codes == [200, 409], {k: v.text for k, v in results.items()}
        winner = next(r for r in results.values() if r.status_code == 200).json()
        final = wait(b, winner["job_id"])
        session = b.get(f"/v1/onboarding-sessions/{sid}").json()
        assert session["selected_candidate_id"] == winner["selected_candidate_id"]
        assert final["status"] == "succeeded"
        assert len(w.collector.app.called("startCollection")) == 1  # sampled once


def test_graceful_restart_cancels_running_job_with_reason(w: World, pg: tuple[str, str]) -> None:
    w.llm.knobs.delay_s = 1.0
    with w.instance(settings(w, pg, "a")) as a:
        r = start(a, "https://shop.example.test/", "restart-1")
        job_id, sid = r.json()["job_id"], r.json()["labels"]["session_id"]
        wait(a, job_id, {"running"})
    w.llm.knobs.delay_s = 0.0
    with w.instance(settings(w, pg, "c")) as c:  # after the restart
        job = c.get(f"/v1/jobs/{job_id}").json()
        assert job["status"] == "cancelled"
        assert job["cancellation"]["reason"] == "instance a shut down"
        session = c.get(f"/v1/onboarding-sessions/{sid}").json()
        assert session["status"] == "cancelled"
        assert "instance shutdown or restart" in session["error"]["detail"]
        w.spec.validate_component("OnboardingSession", session)
        # the session is still readable and a new one can be started on the restarted service
        assert start(c, "https://tiny.example.test/", "restart-2").status_code == 202


def test_killed_instance_job_is_failed_by_another_and_stays_failed(
    w: World, pg: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # A renews leases far too rarely: from B's point of view A is dead after 300 ms.
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__STATE__JOB_LEASE_MS", "300")
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__STATE__HEARTBEAT_INTERVAL_MS", "600000")
    a_settings = settings(w, pg, "a-killed")
    w.llm.knobs.delay_s = 0.5
    with w.instance(a_settings) as a:
        monkeypatch.delenv("JANE_ASSISTANT_LIMITS__STATE__JOB_LEASE_MS")
        monkeypatch.delenv("JANE_ASSISTANT_LIMITS__STATE__HEARTBEAT_INTERVAL_MS")
        with w.instance(settings(w, pg, "b")) as b:
            r = start(a, "https://shop.example.test/", "kill-1")
            job_id, sid = r.json()["job_id"], r.json()["labels"]["session_id"]
            time.sleep(0.8)
            job = b.get(f"/v1/jobs/{job_id}").json()
            assert job["status"] == "failed", job
            assert job["error"]["code"] == "service_unavailable"
            assert "instance a-killed stopped" in job["error"]["detail"]
            session = b.get(f"/v1/onboarding-sessions/{sid}").json()
            assert session["status"] == "failed" and "a-killed" in session["error"]["detail"]
            w.llm.knobs.delay_s = 0.0
            time.sleep(1.5)  # A's task goes on and tries to finish the job
            assert (
                b.get(f"/v1/jobs/{job_id}").json()["status"] == "failed"
            )  # terminal state is never overwritten


def test_state_survives_restart_for_finished_sessions(w: World, pg: tuple[str, str]) -> None:
    with w.instance(settings(w, pg, "a")) as a:
        r = start(a, "https://tiny.example.test/", "persist-1")
        job_id, sid = r.json()["job_id"], r.json()["labels"]["session_id"]
        wait(a, job_id)
    with w.instance(settings(w, pg, "a")) as a2:
        assert a2.get(f"/v1/onboarding-sessions/{sid}").json()["status"] == "insufficient_sample"
        job = a2.get(f"/v1/jobs/{job_id}").json()
        assert job["status"] == "succeeded" and job["result"]["session_id"] == sid
