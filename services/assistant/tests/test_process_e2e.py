"""Full lifecycle over real HTTP: the assistant runs as its own process (``python -m jane_assistant``),
neighbours are contract-bound fakes served by uvicorn on free ports, search is the ``static`` provider.

new source (by name) -> proposals -> accept + activate (source and task created) -> problem samples
-> new version (manual approval) -> admin approves and activates -> admin rolls back.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import uvicorn
from assistant_fakes.llm import FakeLlm
from assistant_fakes.registry import FakeRegistry
from assistant_fakes.services import FakeCollector, FakeHandler, FakeOrchestrator, FakeStorage
from assistant_fakes.site import material, product


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class _Server:
    def __init__(self, app: Any) -> None:
        self.port = _free_port()
        self.server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning", lifespan="off")
        )
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> _Server:
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("fake server did not start")
            time.sleep(0.02)
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


@pytest.fixture
def stack(contracts: Path, tmp_path: Path) -> Iterator[dict[str, Any]]:
    registry = FakeRegistry(contracts)
    fakes: dict[str, Any] = {
        "llm": FakeLlm(contracts),
        "registry": registry,
        "collector_web": FakeCollector(contracts, "collector-web"),
        "handler_runtime": FakeHandler(contracts, registry),
        "orchestrator": FakeOrchestrator(contracts, registry),
        "storage": FakeStorage(contracts),
    }
    catalogue = tmp_path / "sources.json"
    catalogue.write_text(
        json.dumps(
            [{"title": "Shop Example", "url": "https://shop.example.test/", "aliases": ["kettles", "store"]}]
        ),
        encoding="utf-8",
    )
    servers = {name: _Server(f.app) for name, f in fakes.items()}
    for s in servers.values():
        s.__enter__()
    port = _free_port()
    env = {
        **os.environ,
        "JANE_ASSISTANT_PORT": str(port),
        "JANE_ASSISTANT_LOG_FORMAT": "console",
        "JANE_ASSISTANT_CONTRACTS_DIR": str(contracts),
        "JANE_ASSISTANT_SEARCH_PROVIDER": "static",
        "JANE_ASSISTANT_SEARCH_STATIC_FILE": str(catalogue),
        "JANE_ASSISTANT_LIMITS__CLIENTS__JOB_POLL_INTERVAL_MS": "20",
    }
    for name, s in servers.items():
        env[f"JANE_ASSISTANT_{name.upper()}_URL"] = s.url
    log = (tmp_path / "assistant.log").open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "jane_assistant"], env=env, stdout=log, stderr=subprocess.STDOUT
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 30
        while True:
            try:
                if httpx.get(f"{base}/v1/health", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            if proc.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError(
                    "assistant did not start: "
                    + (tmp_path / "assistant.log").read_text(encoding="utf-8")[-2000:]
                )
            time.sleep(0.1)
        yield {"base": base, "fakes": fakes, "servers": servers}
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()
        for s in servers.values():
            s.__exit__()
    assert [v for f in fakes.values() for v in f.app.violations] == []


def _wait(client: httpx.Client, job_id: str) -> dict[str, Any]:
    deadline = time.monotonic() + 30
    while True:
        job: dict[str, Any] = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            assert job["status"] == "succeeded", job
            return job
        assert time.monotonic() < deadline, job
        time.sleep(0.05)


def test_lifecycle_over_http(stack: dict[str, Any]) -> None:
    fakes = stack["fakes"]
    with httpx.Client(base_url=stack["base"], timeout=10) as c:
        info = c.get("/v1/info").json()
        assert info["capabilities"]["search_provider"] == "static"
        job = c.post(
            "/v1/onboarding-sessions",
            json={"query": "Shop Example store", "expected_entity_types": ["product"]},
            headers={"Idempotency-Key": "p-1"},
        ).json()
        session = _wait(c, job["job_id"])["result"]
        assert session["status"] == "proposals_ready", session
        sid = session["session_id"]
        acc = c.post(
            f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
            json={"activate": True, "source_id": "shop-example"},
            headers={"Idempotency-Key": "p-2"},
        ).json()
        accepted = _wait(c, acc["job_id"])["result"]
        assert accepted["activated"] is True
        ref = accepted["extractors"][0]["package"]
        orch: FakeOrchestrator = fakes["orchestrator"]
        task = orch.tasks["shop-example-collect"]
        stage_id = task["stages"][1]["stage_id"]
        assert orch.stage(task["task_id"], stage_id)["handler"] == ref
        assert orch.sources["shop-example"]["change_policy"] == {"llm_versions": "manual_approval"}

        storage: FakeStorage = fakes["storage"]
        storage.put(
            "obj_c300",
            material(
                "https://shop.example.test/product/c-300",
                product("C-300", "Kettle C-300", "899", "price-new"),
                "shop-example",
            ),
        )
        imp = c.post(
            "/v1/improvement-runs",
            headers={"Idempotency-Key": "p-3"},
            json={
                "package": {"package_id": ref["package_id"], "version": ref["version"]},
                "source_id": "shop-example",
                "problem_samples": [
                    {"material_ref": {"storage_connection_id": "raw-files", "object_id": "obj_c300"}}
                ],
                "policy": {"approval": "manual"},
            },
        ).json()
        improved = _wait(c, imp["job_id"])["result"]
        assert improved["outcome"] == "new_version" and improved["activated"] is False
        new = improved["version"]
        assert new["version"] == "1.0.1"
        assert [r["context"] for r in improved["test_reports"]] == [
            "tests",
            f"bindings:{task['task_id']}/{stage_id}",
        ]

    registry: FakeRegistry = fakes["registry"]
    with (
        httpx.Client(base_url=stack["servers"]["registry"].url) as reg,
        httpx.Client(base_url=stack["servers"]["orchestrator"].url) as admin,
    ):
        assert (
            reg.post(
                f"/v1/packages/{new['package_id']}/versions/{new['version']}/status",
                json={"status": "approved", "reason": "reviewed"},
                headers={"Idempotency-Key": "adm-1"},
            ).status_code
            == 200
        )
        path = f"/v1/tasks/{task['task_id']}/stages/{stage_id}/activations"
        act = admin.post(
            path,
            json={"kind": "activate", "package": new, "reason": "reviewed"},
            headers={"Idempotency-Key": "adm-2"},
        )
        assert act.status_code == 200 and act.json()["previous"]["version"] == ref["version"]
        rb = admin.post(
            path, json={"kind": "rollback", "reason": "regression"}, headers={"Idempotency-Key": "adm-3"}
        )
        assert rb.status_code == 200 and rb.json()["package"]["version"] == ref["version"]
    assert registry.versions[new["package_id"]][new["version"]]["test_status"] == "passed"
