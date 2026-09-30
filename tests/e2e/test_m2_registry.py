"""S-M2-01: real registry packages, immutable archives, runtime loading and fork lifecycle."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import uuid
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import delivery_key
from jane_e2e.orchestration import (
    TESTSITE,
    create_source,
    create_task,
    list_items,
    m1_task,
    put_connections,
    start_run,
    wait_run,
)
from jane_e2e.stack import ROOT, E2EStack, default_project
from jane_e2e.steps import EXTRACTOR_DIR, collector_fetch, sandbox_limits

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(7, 9)]

LLM_DIR = ROOT / "services/llm/packages/jane.llm-event-extractor"
FILES_DIR = ROOT / "services/storage/adapters/files/src/jane_storage_files/package"
POSTGRES_DIR = ROOT / "services/storage/adapters/postgres/src/jane_storage_postgres/package"
RULES_DIR = ROOT / "tests/e2e/config/rules/testsite.web-rules/1.0.0"


@pytest.fixture
def registry_stack(monkeypatch: pytest.MonkeyPatch) -> Iterator[E2EStack]:
    """An isolated stack whose runtime fetches archives from the real registry."""
    monkeypatch.setenv("JANE_E2E_RUNTIME_REGISTRY_URL", "http://registry:8000")
    monkeypatch.setenv("JANE_E2E_REGISTRY_RUNTIME_PROFILES", '["http://handler-runtime:8000/v1/info"]')
    monkeypatch.setenv("JANE_E2E_COLLECTOR_RULES_DIR", "/cfg/registry-only")
    monkeypatch.setenv("JANE_E2E_COLLECTOR_REGISTRY_URL", "http://registry:8000")
    stack = E2EStack(project=f"{default_project()}-registry-{uuid.uuid4().hex[:6]}")
    try:
        missing = stack.missing(("registry", "handler-runtime", "orchestrator", "storage", "web-collector"))
        if missing:
            pytest.skip("; ".join(missing))
        yield stack
    finally:
        if os.environ.get("JANE_E2E_KEEP") != "1":
            stack.down(volumes=True)


def _key() -> str:
    return uuid.uuid4().hex


def _package_files(directory: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    manifest = json.loads((directory / "jane-package.json").read_text(encoding="utf-8"))
    files = {
        p.relative_to(directory).as_posix(): p.read_bytes()
        for p in directory.rglob("*")
        if p.is_file() and p.name != "jane-package.json"
    }
    return manifest, files


def _body(manifest: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]:
    encoded: dict[str, dict[str, str]] = {}
    for path, data in files.items():
        try:
            encoded[path] = {"encoding": "utf-8", "data": data.decode("utf-8")}
        except UnicodeDecodeError:
            encoded[path] = {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
    return {"manifest": manifest, "files": encoded}


def _publish(registry: JaneClient, manifest: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]:
    package_id = manifest["package_id"]
    created = registry.api("registry").post(
        "/v1/packages",
        json={"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]},
        headers={"Idempotency-Key": _key()},
    )
    assert created.status_code == 201, created.text
    published = _publish_version(registry, manifest, files)
    assert published["status"] == "draft"
    return published


def _publish_version(
    registry: JaneClient, manifest: dict[str, Any], files: dict[str, bytes]
) -> dict[str, Any]:
    response = registry.api("registry").post(
        f"/v1/packages/{manifest['package_id']}/versions",
        json=_body(manifest, files),
        headers={"Idempotency-Key": _key()},
    )
    assert response.status_code == 201, response.text
    return dict(response.json())


def _archive(registry: JaneClient, package_id: str, version: str, digest: str) -> bytes:
    response = registry.api("registry").get(f"/v1/packages/{package_id}/versions/{version}/archive")
    assert response.status_code == 200, response.text
    assert response.headers["etag"] == f'"{digest}"'
    assert "sha256:" + hashlib.sha256(response.content).hexdigest() == digest
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert "jane-package.json" in archive.namelist()
        assert json.loads(archive.read("jane-package.json"))["package_id"] == package_id
    return response.content


def test_registry_packages_runtime_and_fork(registry_stack: E2EStack, run_id: str) -> None:
    stack = registry_stack
    stack.ensure("registry", "handler-runtime", "storage", "web-collector", "orchestrator")
    registry = JaneClient(stack.url("registry"))
    runtime = JaneClient(stack.url("handler-runtime"))
    collector = JaneClient(stack.url("web-collector"))
    orch = JaneClient(stack.url("orchestrator"))
    try:
        storage_publish = subprocess.run(
            [sys.executable, "-m", "jane_storage.packages", "publish", "--registry", stack.url("registry")],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert storage_publish.returncode == 0, (storage_publish.stdout, storage_publish.stderr)
        assert "jane.storage-files@1.0.0" in storage_publish.stdout
        assert "jane.storage-postgresql@1.0.0" in storage_publish.stdout

        packages = [EXTRACTOR_DIR, FILES_DIR, POSTGRES_DIR, LLM_DIR, RULES_DIR]
        published: dict[str, dict[str, Any]] = {}
        manifests: dict[str, dict[str, Any]] = {}
        files_by_id: dict[str, dict[str, bytes]] = {}
        for directory in packages:
            manifest, files = _package_files(directory)
            package_id = manifest["package_id"]
            manifests[package_id], files_by_id[package_id] = manifest, files
            if manifest["kind"] == "storage":
                response = registry.api("registry").get(f"/v1/packages/{package_id}/versions/1.0.0")
                assert response.status_code == 200, response.text
                version = dict(response.json())
            else:
                version = _publish(registry, manifest, files)
            assert version["manifest"]["kind"] == manifest["kind"]
            _archive(registry, package_id, manifest["version"], version["digest"])
            published[package_id] = version
        assert {v["manifest"]["kind"] for v in published.values()} == {
            "extractor",
            "storage",
            "llm",
            "collector-rules",
        }

        parent = manifests["testsite.product-extractor"]
        parent_id = parent["package_id"]
        parent_v1 = published[parent_id]
        material = collector_fetch(collector, f"{TESTSITE}/product/phone-alpha", f"registry-{run_id}")
        handler = {"package_id": parent_id, "version": "1.0.0", "digest": parent_v1["digest"]}
        invocation = {
            "handler": handler,
            "inputs": [{"kind": "material", "material": material}],
            "context": {"trace": {"run_id": f"run_{run_id}", "stage_id": "registry-extract"}},
            "delivery": {
                "delivery_key": delivery_key(run_id, "registry-extract", material["observation_id"])
            },
            "mode": "sync",
            "limits": sandbox_limits(),
        }
        assert "package_archive" not in invocation
        _, result = runtime.invoke(invocation)
        assert result["status"] == "success", result
        assert result["handler"]["digest"] == parent_v1["digest"]
        assert result["output"]["entities"][0]["fields"]["sku"] == "phone-alpha"

        # A fork stores an immutable snapshot, including a separate canonical archive.
        fork_id = f"testsite.product-extractor-{run_id}"
        fork_request = {"new_package_id": fork_id, "from_version": "1.0.0"}
        forked = registry.api("registry").post(
            f"/v1/packages/{parent_id}/forks", json=fork_request, headers={"Idempotency-Key": _key()}
        )
        assert forked.status_code == 201, forked.text
        fork_ref = forked.json()["fork_of"]
        assert fork_ref == {"package_id": parent_id, "version": "1.0.0", "digest": parent_v1["digest"]}
        fork_v1 = registry.api("registry").get(f"/v1/packages/{fork_id}/versions/1.0.0").json()
        fork_archive = _archive(registry, fork_id, "1.0.0", fork_v1["digest"])
        assert fork_v1["manifest"]["fork_of"] == fork_ref

        parent_v2_manifest = json.loads(json.dumps(parent))
        parent_v2_manifest["version"] = "1.1.0"
        parent_v2_manifest["provenance"] = {
            "created_by": "human",
            "based_on": {"package_id": parent_id, "version": "1.0.0"},
            "change_summary": "Add source marker without changing product extraction.",
        }
        parent_v2_files = dict(files_by_id[parent_id])
        source = "src/testsite_products/main.py"
        parent_v2_files[source] += b"\n# Registry upstream acceptance marker.\n"
        parent_v2 = _publish_version(registry, parent_v2_manifest, parent_v2_files)
        assert parent_v2["digest"] != parent_v1["digest"]
        assert _archive(registry, fork_id, "1.0.0", fork_v1["digest"]) == fork_archive
        unchanged = registry.api("registry").get(f"/v1/packages/{fork_id}/versions/1.0.0").json()
        assert unchanged["digest"] == fork_v1["digest"] and unchanged["files"] == fork_v1["files"]
        upstream = registry.api("registry").get(f"/v1/packages/{fork_id}/upstream").json()
        assert upstream["newer_parent_versions"] == ["1.1.0"]
        diff = (
            registry.api("registry")
            .get(f"/v1/packages/{fork_id}/diff", params={"from": "1.0.0", "to": "parent:1.1.0"})
            .json()
        )
        assert any(f["path"] == source and f["status"] == "modified" for f in diff["files"])

        # The task remains pinned to the fork's old digest after the parent changed.
        put_connections(orch)
        source_id, task_id = f"registry-source-{run_id}", f"registry-task-{run_id}"
        create_source(
            orch,
            source_id,
            collector_rules={
                "package_id": "testsite.web-rules",
                "version": "1.0.0",
                "digest": published["testsite.web-rules"]["digest"],
            },
        )
        task = m1_task(
            task_id,
            source_id,
            [f"{TESTSITE}/product/phone-alpha"],
            {"package_id": fork_id, "version": "1.0.0", "digest": fork_v1["digest"]},
        )
        create_task(orch, task)
        run = wait_run(orch, start_run(orch, task_id))
        assert run["status"] == "succeeded", run
        extracted = list_items(orch, run["run_id"], "extract-products")
        assert len(extracted) == 1 and extracted[0]["status"] == "completed", extracted
        trace = orch.api("orchestrator").get(f"/v1/materials/{extracted[0]['material_id']}/trace").json()
        assert fork_v1["digest"] in json.dumps(trace), trace

        port_request = {"parent_version": "1.1.0", "new_version": "1.1.0"}
        started = registry.api("registry").post(
            f"/v1/packages/{fork_id}/upstream-ports",
            json=port_request,
            headers={"Idempotency-Key": _key()},
        )
        assert started.status_code == 202, started.text
        job = registry.wait_job("registry", started.json()["job_id"])
        assert job["status"] == "succeeded", job
        ported = job["result"]
        assert ported["version"] == "1.1.0" and ported["digest"] != fork_v1["digest"]
        assert ported["manifest"]["fork_of"] == fork_ref
        assert _archive(registry, fork_id, "1.1.0", ported["digest"])
        assert (
            registry.api("registry").get(f"/v1/packages/{fork_id}/upstream").json()["newer_parent_versions"]
            == []
        )

        # Registry records connection requirements, while actual connection IDs stay with tasks.
        storage_id = "jane.storage-files"
        storage_version = published[storage_id]
        storage_fork_id = f"jane.storage-files-{run_id}"
        storage_fork = registry.api("registry").post(
            f"/v1/packages/{storage_id}/forks",
            json={"new_package_id": storage_fork_id, "from_version": "1.0.0"},
            headers={"Idempotency-Key": _key()},
        )
        assert storage_fork.status_code == 201, storage_fork.text
        storage_fork_manifest = (
            registry.api("registry").get(f"/v1/packages/{storage_fork_id}/versions/1.0.0").json()["manifest"]
        )
        assert (
            storage_fork_manifest["required_connections"]
            == storage_version["manifest"]["required_connections"]
        )
        assert "connections" not in storage_fork_manifest
        assert "raw-files" not in json.dumps(storage_fork_manifest)

        secret_file = dict(files_by_id[parent_id])
        secret_file[".env"] = b"TOKEN=dummy\n"
        rejected_manifest = json.loads(json.dumps(parent))
        rejected_manifest["version"] = "1.2.0"
        rejected = registry.api("registry").post(
            f"/v1/packages/{parent_id}/versions",
            json=_body(rejected_manifest, secret_file),
            headers={"Idempotency-Key": _key()},
        )
        assert rejected.status_code == 422 and rejected.json()["code"] == "secret_detected"
        assert registry.api("registry").get(f"/v1/packages/{parent_id}/versions/1.2.0").status_code == 404
    finally:
        for client in (registry, runtime, collector, orch):
            client.close()
