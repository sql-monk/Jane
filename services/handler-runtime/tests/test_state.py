"""Several instances on the shared PostgreSQL state (``@pytest.mark.integration``).

PostgreSQL: ``JANE_WP06_STATE_DSN`` or the dev stack (``just up --project jane-wp06-state postgres`` and
``just integration --project jane-wp06-state``). Each test module uses its own schema and drops it afterwards.
The sandbox backend is the real subprocess backend wrapped with a run counter (to prove "no second run").
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import httpx
import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from pydantic import SecretStr

from jane_handler_runtime.app import build_app
from jane_handler_runtime.runtime import build_runtime
from jane_handler_runtime.sandbox import Bundle, SandboxOutcome, SubprocessSandbox
from jane_handler_runtime.settings import SandboxLimits, Settings
from jane_kit.devstack import load_stack

pytestmark = pytest.mark.integration


def _dsn() -> str | None:
    if env := os.environ.get("JANE_WP06_STATE_DSN"):
        return env
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        return None
    return str(stack.get("postgres", "dsn"))


class CountingSandbox(SubprocessSandbox):
    """The real subprocess backend; counts runs shared by all instances of a test."""

    runs = 0
    lock = threading.Lock()

    def run(
        self, image: str, bundle: Bundle, limits: SandboxLimits, labels: Mapping[str, str]
    ) -> SandboxOutcome:
        with CountingSandbox.lock:
            CountingSandbox.runs += 1
        return super().run(image, bundle, limits, labels)


@pytest.fixture(scope="module")
def dsn() -> Iterator[tuple[str, str]]:
    value = _dsn()
    if value is None:
        pytest.skip("no PostgreSQL: set JANE_WP06_STATE_DSN or run `just up --project <p> postgres`")
    schema = f"wp06_test_{uuid.uuid4().hex[:8]}"
    yield value, schema
    with psycopg.connect(value, autocommit=True) as conn:
        conn.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))


def instance(dsn: tuple[str, str], tmp_path: Path, name: str) -> TestClient:
    settings = Settings(
        log_format="console",
        sandbox_backend="subprocess",
        allow_unsafe_subprocess=True,
        package_cache_dir=tmp_path / f"cache-{name}",
        state_dsn=SecretStr(dsn[0]),
        state_schema=dsn[1],
        instance_id=name,
    )
    runtime = build_runtime(settings, backend=CountingSandbox(True))
    return TestClient(build_app(settings, runtime))


def post(client: TestClient, body: dict[str, Any]) -> httpx.Response:
    key = body["delivery"]["delivery_key"]
    response: httpx.Response = client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})
    return response


def wait_job(client: TestClient, job_id: str, statuses: set[str], timeout: float = 60) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    job: dict[str, Any] = {}
    while time.monotonic() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job.get("status") in statuses:
            break
        time.sleep(0.05)
    return job


def test_redelivery_to_another_instance_is_a_duplicate(dsn: tuple[str, str], tmp_path: Path, h: Any) -> None:
    body = h.invocation(h.example, h.product_material(), key=f"multi-{uuid.uuid4().hex}")
    CountingSandbox.runs = 0
    with instance(dsn, tmp_path, "a") as a, instance(dsn, tmp_path, "b") as b:
        assert b.get("/v1/health").json()["checks"]["state"]["status"] == "ok"
        assert b.get("/v1/info").json()["capabilities"]["state"] == "postgresql"
        first = post(a, body)
        assert first.status_code == 200 and first.json()["duplicate"] is False
        again = post(b, body)
        assert again.status_code == 200
        assert again.headers["Idempotency-Replayed"] == "true"
        assert again.json()["duplicate"] is True
        assert again.json()["invocation_id"] == first.json()["invocation_id"]
        assert CountingSandbox.runs == 1  # the sandbox ran once for both deliveries
        stored = b.get(f"/v1/invocations/{first.json()['invocation_id']}")
        assert stored.status_code == 200 and stored.json()["status"] == "success"
    with instance(dsn, tmp_path, "restarted") as c:  # after a restart (new process state)
        replay = post(c, body)
        assert replay.json()["duplicate"] is True
        assert replay.json()["invocation_id"] == first.json()["invocation_id"]
        assert c.get(f"/v1/invocations/{first.json()['invocation_id']}").status_code == 200
    assert CountingSandbox.runs == 1


def test_jobs_are_visible_on_every_instance(dsn: tuple[str, str], tmp_path: Path, h: Any) -> None:
    body = h.invocation(h.example, h.product_material(), key=f"job-{uuid.uuid4().hex}", mode="async")
    with instance(dsn, tmp_path, "a") as a, instance(dsn, tmp_path, "b") as b:
        accepted = post(a, body)
        assert accepted.status_code == 202
        job_id = accepted.json()["job_id"]
        job = wait_job(b, job_id, {"succeeded", "failed"})
        assert job["status"] == "succeeded"
        assert b.get(f"/v1/invocations/{job['result']['invocation_id']}").status_code == 200
        again = post(b, body)  # redelivery of an async call that has finished meanwhile
        assert again.status_code == 200 and again.json()["duplicate"] is True
    with instance(dsn, tmp_path, "restarted") as c:
        assert c.get(f"/v1/jobs/{job_id}").json()["status"] == "succeeded"


def test_in_progress_on_another_instance_is_409(dsn: tuple[str, str], tmp_path: Path, h: Any) -> None:
    body = h.invocation(
        h.probe, h.product_material(), key=f"busy-{uuid.uuid4().hex}", params={"mode": "sleep"},
        limits={"sandbox": {"wall_time_ms": 4000}},
    )  # fmt: skip
    with instance(dsn, tmp_path, "a") as a, instance(dsn, tmp_path, "b") as b:
        results: list[httpx.Response] = []
        worker = threading.Thread(target=lambda: results.append(post(a, body)))
        worker.start()
        time.sleep(1.5)
        busy = post(b, body)
        assert busy.status_code == 409
        assert busy.json()["code"] == "idempotency_in_progress"
        assert busy.json()["retryable"] is True
        worker.join(60)
        assert results[0].status_code == 200 and results[0].json()["failure"]["kind"] == "timeout"
        done = post(b, body)
        assert done.json()["duplicate"] is True


def test_cancel_from_another_instance(dsn: tuple[str, str], tmp_path: Path, h: Any) -> None:
    body = h.invocation(
        h.probe, h.product_material(), key=f"cancel-{uuid.uuid4().hex}", params={"mode": "sleep"},
        mode="async", limits={"sandbox": {"wall_time_ms": 3000}},
    )  # fmt: skip
    with instance(dsn, tmp_path, "a") as a, instance(dsn, tmp_path, "b") as b:
        job_id = post(a, body).json()["job_id"]
        wait_job(b, job_id, {"running"})
        assert b.post(f"/v1/jobs/{job_id}/cancel").status_code == 202
        assert wait_job(a, job_id, {"cancelled", "succeeded", "failed"})["status"] == "cancelled"
