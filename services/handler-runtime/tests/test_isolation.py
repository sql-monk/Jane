"""Sandbox isolation on a real container engine (``@pytest.mark.isolation``; CI job ``isolation``, Linux).

No sandbox mocks: every test runs the probe package through the Docker backend in a fresh container of the
``python-extractor@1`` image. The image is built once per session (tag from ``JANE_WP06_SANDBOX_IMAGE``,
default ``jane-wp06/python-extractor:1-test``); containers carry a per-session label and are removed.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_handler_runtime.app import build_app
from jane_handler_runtime.cli import build_context
from jane_handler_runtime.docker_sandbox import SANDBOX_LABEL, DockerSandbox
from jane_handler_runtime.settings import Settings

pytestmark = pytest.mark.isolation

IMAGE = os.environ.get("JANE_WP06_SANDBOX_IMAGE", "jane-wp06/python-extractor:1-test")
SESSION_LABEL = "io.jane.test-session"
SESSION = f"wp06-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def engine() -> Iterator[DockerSandbox]:
    sandbox = DockerSandbox(extra_labels={SESSION_LABEL: SESSION})
    try:
        sandbox.ping()
    except Exception as exc:  # pragma: no cover - no engine on this machine
        pytest.skip(f"no container engine: {exc}")
    if not sandbox.has_image(IMAGE):
        context, dockerfile = build_context("python-extractor@1")
        for chunk in sandbox.api.build(
            fileobj=io.BytesIO(context),
            custom_context=True,
            dockerfile=dockerfile,
            tag=IMAGE,
            rm=True,
            decode=True,
        ):
            assert "error" not in chunk, chunk
    yield sandbox
    sandbox.cleanup({SESSION_LABEL: SESSION})
    leftovers = sandbox.api.containers(all=True, filters={"label": [f"{SESSION_LABEL}={SESSION}"]})
    assert leftovers == [], "sandbox containers were left behind"


@pytest.fixture
def settings(engine: DockerSandbox, tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("JANE_WP06_FAKE_SECRET", "must-not-leak")
    return Settings(
        log_format="console",
        sandbox_backend="docker",
        profile_images={"python-extractor@1": IMAGE},
        sandbox_labels={SESSION_LABEL: SESSION},
        package_cache_dir=tmp_path / "cache",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(settings)) as c:
        yield c


def invoke(
    client: TestClient, h: Any, key: str, params: dict[str, Any], limits: dict[str, Any] | None = None
) -> dict[str, Any]:
    body = h.invocation(h.probe, h.product_material(), key=key, params=params)
    if limits:
        body["limits"] = limits
    r = client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 200, r.text
    result: dict[str, Any] = r.json()
    return result


def running_sandboxes(engine: DockerSandbox, invocation_id: str) -> list[Any]:
    return list(
        engine.api.containers(all=True, filters={"label": [f"io.jane.invocation-id={invocation_id}"]})
    )


def test_hang_is_killed_at_wall_time(client: TestClient, engine: DockerSandbox, h: Any) -> None:
    started = time.monotonic()
    result = invoke(client, h, f"hang-{SESSION}", {"mode": "hang"}, {"sandbox": {"wall_time_ms": 3000}})
    elapsed = time.monotonic() - started
    assert result["status"] == "failed"
    assert result["failure"]["kind"] == "timeout"
    assert result["failure"]["retryable"] is False
    assert result["failure"]["details"]["wall_time_ms"] == 3000
    assert 3 <= elapsed < 30, elapsed
    assert running_sandboxes(engine, result["invocation_id"]) == []


def test_network_access_is_blocked(client: TestClient, engine: DockerSandbox, h: Any) -> None:
    """A server that a normal container *can* reach is unreachable from the sandbox."""
    api = engine.api
    server = api.create_container(
        IMAGE,
        command=["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"],
        labels={SANDBOX_LABEL: "1", SESSION_LABEL: SESSION},
        host_config=api.create_host_config(network_mode="bridge"),
    )
    try:
        api.start(server)
        ip = ""
        for _ in range(50):
            ip = api.inspect_container(server)["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
            if ip:
                break
            time.sleep(0.1)
        probe = (
            "import socket, time\n"
            "for _ in range(50):\n"
            "    try:\n"
            f"        socket.create_connection(('{ip}', 8000), timeout=2).close(); print('reachable'); break\n"
            "    except OSError:\n"
            "        time.sleep(0.2)\n"
        )
        control = api.create_container(
            IMAGE, command=["python", "-c", probe], labels={SESSION_LABEL: SESSION},
            host_config=api.create_host_config(network_mode="bridge"),
        )  # fmt: skip
        try:
            api.start(control)
            api.wait(control, timeout=60)
            assert b"reachable" in api.logs(control), "control container could not reach the server"
        finally:
            api.remove_container(control, force=True, v=True)

        result = invoke(client, h, f"net-{SESSION}", {"mode": "network", "host": ip, "port": 8000})
        assert result["status"] == "failed"
        assert result["failure"]["kind"] == "sandbox_violation"
        error = result["failure"]["details"]["error"]
        assert error["type"] == "OSError"
        assert "unreachable" in error["message"].lower()  # ENETUNREACH from the kernel: no network interface
        assert any(m["code"] == "sandbox.network_blocked" for m in result["diagnostics"]["messages"])
    finally:
        api.remove_container(server, force=True, v=True)


def test_cancel_kills_the_sandbox_container(client: TestClient, engine: DockerSandbox, h: Any) -> None:
    key = f"cancel-{SESSION}"
    body = h.invocation(h.probe, h.product_material(), key=key, params={"mode": "sleep"}, mode="async")
    body["limits"] = {"sandbox": {"wall_time_ms": 120_000}}
    accepted = client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})
    assert accepted.status_code == 202
    job_id = accepted.json()["job_id"]
    invocation_id = accepted.json()["labels"]["invocation_id"]
    deadline = time.monotonic() + 60
    while not [c for c in running_sandboxes(engine, invocation_id) if c["State"] == "running"]:
        assert time.monotonic() < deadline, "sandbox container did not start"
        time.sleep(0.1)
    started = time.monotonic()
    assert client.post(f"/v1/jobs/{job_id}/cancel", json={"reason": "isolation test"}).status_code == 202
    while client.get(f"/v1/jobs/{job_id}").json()["status"] not in {"cancelled", "succeeded", "failed"}:
        assert time.monotonic() - started < 30
        time.sleep(0.1)
    assert client.get(f"/v1/jobs/{job_id}").json()["status"] == "cancelled"
    while running_sandboxes(engine, invocation_id):
        assert time.monotonic() - started < 30, "sandbox container still exists after cancel"
        time.sleep(0.1)
    assert time.monotonic() - started < 30  # far below wall_time_ms = 120 s


def test_memory_limit_kills_the_sandbox(client: TestClient, h: Any) -> None:
    result = invoke(
        client, h, f"mem-{SESSION}", {"mode": "memory", "mb": 512}, {"sandbox": {"memory_mb": 64}}
    )
    assert result["status"] == "failed"
    assert result["failure"]["kind"] == "resource_exceeded"
    assert result["failure"]["details"]["memory_mb"] == 64


def test_read_only_fs_non_root_no_secrets_no_network_interfaces(client: TestClient, h: Any) -> None:
    result = invoke(client, h, f"env-{SESSION}", {"mode": "environment"})
    assert result["status"] == "success", result
    data = result["output"]["data"]
    assert data["uid"] == 65534
    assert data["write_root"].startswith("denied")
    assert data["write_package"].startswith("denied")
    assert data["write_work"].startswith("denied")
    assert data["write_tmp"] == "written"
    assert "JANE_WP06_FAKE_SECRET" not in data["env"]
    assert not [k for k in data["env"] if k.startswith("JANE_")]
    assert data["interfaces"] == ["lo"]


def test_example_package_tests_pass_through_cli(engine: DockerSandbox, h: Any) -> None:
    """The CLI runs the package tests on the Docker backend without any other Jane service."""
    env = {
        **os.environ,
        "JANE_HANDLER_RUNTIME_SANDBOX_BACKEND": "docker",
        "JANE_HANDLER_RUNTIME_SANDBOX_LABELS": json.dumps({SESSION_LABEL: SESSION}),
    }
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "jane_handler_runtime.cli",
            "test",
            str(h.example),
            "--image",
            IMAGE,
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["failed"] == 0 and report["passed"] == 5
    assert {c["actual_status"] for c in report["cases"]} == {"success", "empty", "unrecognized"}


def test_profile_libraries_are_installed_in_the_image(engine: DockerSandbox) -> None:
    from jane_handler_runtime.profiles import load_profiles

    libraries = dict(load_profiles()["python-extractor@1"].libraries)
    script = "import json,importlib.metadata as m,sys;print(json.dumps({d:m.version(d) for d in json.loads(sys.argv[1])}))"
    container = engine.api.create_container(
        IMAGE,
        command=["python", "-I", "-c", script, json.dumps(sorted(libraries))],
        labels={SESSION_LABEL: SESSION},
    )
    try:
        engine.api.start(container)
        assert engine.api.wait(container, timeout=60)["StatusCode"] == 0
        installed = json.loads(engine.api.logs(container, stderr=False))
    finally:
        engine.api.remove_container(container, force=True, v=True)
    assert installed == libraries
