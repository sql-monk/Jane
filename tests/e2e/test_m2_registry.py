"""S-M2-01: real registry packages, immutable archives, runtime loading and fork lifecycle."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import delivery_key
from jane_e2e.orchestration import (
    TESTSITE,
    create_source,
    create_task,
    m1_task,
    put_connections,
    start_run,
    wait_run,
)
from jane_e2e.registry import (
    FILES_DIR,
    LLM_DIR,
    POSTGRES_DIR,
    RULES_DIR,
    archive,
    archive_file,
    key,
    package_files,
    publish,
    publish_body,
    publish_storage_packages,
    publish_version,
    run_stage_handler,
)
from jane_e2e.registry import registry_stack as registry_stack_of
from jane_e2e.stack import E2EStack
from jane_e2e.steps import EXTRACTOR_DIR, collector_fetch, sandbox_limits

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(7, 9)]


@pytest.fixture
def registry_stack() -> Iterator[E2EStack]:
    """An isolated stack whose runtime fetches archives from the real registry."""
    services = ("registry", "handler-runtime", "orchestrator", "storage", "web-collector")
    with registry_stack_of("registry", services) as stack:
        yield stack


def test_registry_packages_runtime_and_fork(registry_stack: E2EStack, run_id: str) -> None:
    stack = registry_stack
    stack.ensure("registry", "handler-runtime", "storage", "web-collector", "orchestrator")
    registry = JaneClient(stack.url("registry"))
    runtime = JaneClient(stack.url("handler-runtime"))
    collector = JaneClient(stack.url("web-collector"))
    orch = JaneClient(stack.url("orchestrator"))
    try:
        storage_publish = publish_storage_packages(stack.url("registry"))
        assert "jane.storage-files@1.0.0" in storage_publish
        assert "jane.storage-postgresql@1.0.0" in storage_publish

        packages = [EXTRACTOR_DIR, FILES_DIR, POSTGRES_DIR, LLM_DIR, RULES_DIR]
        published: dict[str, dict[str, Any]] = {}
        manifests: dict[str, dict[str, Any]] = {}
        files_by_id: dict[str, dict[str, bytes]] = {}
        for directory in packages:
            manifest, files = package_files(directory)
            package_id = manifest["package_id"]
            manifests[package_id], files_by_id[package_id] = manifest, files
            if manifest["kind"] == "storage":
                response = registry.api("registry").get(f"/v1/packages/{package_id}/versions/1.0.0")
                assert response.status_code == 200, response.text
                version = dict(response.json())
            else:
                version = publish(registry, manifest, files)
            assert version["manifest"]["kind"] == manifest["kind"]
            archive(registry, package_id, manifest["version"], version["digest"])
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
            f"/v1/packages/{parent_id}/forks", json=fork_request, headers={"Idempotency-Key": key()}
        )
        assert forked.status_code == 201, forked.text
        fork_ref = forked.json()["fork_of"]
        assert fork_ref == {"package_id": parent_id, "version": "1.0.0", "digest": parent_v1["digest"]}
        fork_v1 = registry.api("registry").get(f"/v1/packages/{fork_id}/versions/1.0.0").json()
        fork_archive = archive(registry, fork_id, "1.0.0", fork_v1["digest"])
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
        parent_v2 = publish_version(registry, parent_v2_manifest, parent_v2_files)
        assert parent_v2["digest"] != parent_v1["digest"]
        parent_v2_archive = archive(registry, parent_id, "1.1.0", parent_v2["digest"])
        marker = b"# Registry upstream acceptance marker."
        assert marker in archive_file(parent_v2_archive, source)
        assert marker not in archive_file(fork_archive, source)

        # The runtime refuses a registry archive whose digest differs from the pinned one.
        wrong_key = delivery_key(run_id, "registry-wrong-digest", material["observation_id"])
        wrong_pin: dict[str, Any] = dict(invocation)
        wrong_pin["handler"] = {**handler, "digest": parent_v2["digest"]}
        wrong_pin["delivery"] = {"delivery_key": wrong_key}
        mismatch = runtime.api("handler").post(
            "/v1/invocations",
            json=wrong_pin,
            headers={"Idempotency-Key": wrong_key},
        )
        assert mismatch.status_code == 422, mismatch.text
        assert mismatch.json()["code"] == "digest_mismatch", mismatch.text

        assert archive(registry, fork_id, "1.0.0", fork_v1["digest"]) == fork_archive
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
        fork_pin = {"package_id": fork_id, "version": "1.0.0", "digest": fork_v1["digest"]}
        assert run_stage_handler(orch, run["run_id"], "extract-products") == fork_pin

        port_request = {"parent_version": "1.1.0", "new_version": "1.1.0"}
        started = registry.api("registry").post(
            f"/v1/packages/{fork_id}/upstream-ports",
            json=port_request,
            headers={"Idempotency-Key": key()},
        )
        assert started.status_code == 202, started.text
        job = registry.wait_job("registry", started.json()["job_id"])
        assert job["status"] == "succeeded", job
        ported = job["result"]
        assert ported["version"] == "1.1.0" and ported["digest"] != fork_v1["digest"]
        assert ported["manifest"]["fork_of"] == fork_ref
        # The port carries the parent's 1.1.0 change; the fork's 1.0.0 stays without it.
        ported_archive = archive(registry, fork_id, "1.1.0", ported["digest"])
        assert archive_file(ported_archive, source) == archive_file(parent_v2_archive, source)
        assert marker in archive_file(ported_archive, source)
        assert archive(registry, fork_id, "1.0.0", fork_v1["digest"]) == fork_archive
        assert marker not in archive_file(fork_archive, source)
        ported_vs_parent = (
            registry.api("registry")
            .get(f"/v1/packages/{fork_id}/diff", params={"from": "1.1.0", "to": "parent:1.1.0"})
            .json()
        )
        source_status = [f["status"] for f in ported_vs_parent["files"] if f["path"] == source]
        assert source_status == ["unchanged"], ported_vs_parent
        assert (
            registry.api("registry").get(f"/v1/packages/{fork_id}/upstream").json()["newer_parent_versions"]
            == []
        )

        # With fork 1.1.0 published, the task pinned to fork 1.0.0 still executes exactly that version.
        pinned_run = wait_run(orch, start_run(orch, task_id))
        assert pinned_run["status"] == "succeeded", pinned_run
        pinned = run_stage_handler(orch, pinned_run["run_id"], "extract-products")
        assert pinned == fork_pin, pinned
        assert pinned["digest"] != ported["digest"]

        # A storage package (parent and fork alike) only declares required_connections; concrete
        # connection IDs such as raw-files live in task configuration, never in the package.
        storage_id = "jane.storage-files"
        storage_version = published[storage_id]
        required = storage_version["manifest"]["required_connections"]
        assert required and all("name" in c and "kind" in c for c in required), required
        assert "raw-files" not in json.dumps(storage_version["manifest"])
        storage_fork_id = f"jane.storage-files-{run_id}"
        storage_fork = registry.api("registry").post(
            f"/v1/packages/{storage_id}/forks",
            json={"new_package_id": storage_fork_id, "from_version": "1.0.0"},
            headers={"Idempotency-Key": key()},
        )
        assert storage_fork.status_code == 201, storage_fork.text
        assert storage_fork.json()["fork_of"] == {
            "package_id": storage_id,
            "version": "1.0.0",
            "digest": storage_version["digest"],
        }
        storage_fork_manifest = (
            registry.api("registry").get(f"/v1/packages/{storage_fork_id}/versions/1.0.0").json()["manifest"]
        )
        assert storage_fork_manifest["kind"] == "storage"
        assert storage_fork_manifest["required_connections"] == required
        assert "connections" not in storage_fork_manifest
        assert "raw-files" not in json.dumps(storage_fork_manifest)

        secret_file = dict(files_by_id[parent_id])
        secret_file[".env"] = b"TOKEN=dummy\n"
        rejected_manifest = json.loads(json.dumps(parent))
        rejected_manifest["version"] = "1.2.0"
        rejected = registry.api("registry").post(
            f"/v1/packages/{parent_id}/versions",
            json=publish_body(rejected_manifest, secret_file),
            headers={"Idempotency-Key": key()},
        )
        assert rejected.status_code == 422 and rejected.json()["code"] == "secret_detected"
        assert registry.api("registry").get(f"/v1/packages/{parent_id}/versions/1.2.0").status_code == 404
    finally:
        for client in (registry, runtime, collector, orch):
            client.close()
