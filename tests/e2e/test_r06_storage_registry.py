"""R-06: two storage and registry replicas observe the same durable state."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import fetch_page, standin_web_material
from jane_e2e.registry import FILES_DIR, archive, key, package_files, publish_body
from jane_e2e.stack import E2EStack
from jane_e2e.steps import store
from jane_e2e.verify import objects_by_source

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(8)]


def test_r_06_storage_replica_deduplicates_delivery(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    require("testsite", "storage")
    stack.scale("storage", 2)
    material = standin_web_material(
        fetch_page(f"{stack.url('testsite')}/product/phone-alpha"),
        source_id=f"r06-{run_id}",
        observation_id=f"obs_r06_{run_id}",
    )
    first_client, second_client = client("storage", 1), client("storage", 2)
    body, first = store(
        first_client,
        package_id="jane.storage-files",
        connection="raw-files",
        inputs=[{"kind": "material", "material": material}],
        run_id=run_id,
        stage_id="store-raw",
        key_part=material["observation_id"],
    )
    assert first["status"] == "success", first
    assert first["output"]["writes"][0]["status"] == "written", first

    _, replay = second_client.invoke(body)
    assert replay["status"] == "success", replay
    assert replay["duplicate"] is True, replay
    assert replay["output"]["writes"][0]["status"] == "duplicate", replay
    objects = objects_by_source(second_client, "raw-files", f"r06-{run_id}")
    assert len(objects) == 1, objects
    assert objects[0]["material"]["material_id"] == material["material_id"]


def test_r_06_registry_replica_reads_published_archive(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient]
) -> None:
    require("registry")
    stack.scale("registry", 2)
    first_client, second_client = client("registry", 1), client("registry", 2)
    manifest, files = package_files(FILES_DIR)
    package_id = manifest["package_id"]
    create_body = {"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]}
    create_headers = {"Idempotency-Key": key()}
    created = first_client.api("registry").post(
        "/v1/packages",
        json=create_body,
        headers=create_headers,
    )
    assert created.status_code == 201, created.text
    replay_created = second_client.api("registry").post(
        "/v1/packages", json=create_body, headers=create_headers
    )
    assert replay_created.status_code == 201, replay_created.text
    assert replay_created.headers["Idempotency-Replayed"] == "true"
    assert replay_created.json() == created.json()

    version_body = publish_body(manifest, files)
    version_headers = {"Idempotency-Key": key()}
    published = first_client.api("registry").post(
        f"/v1/packages/{package_id}/versions",
        json=version_body,
        headers=version_headers,
    )
    assert published.status_code == 201, published.text
    replay_published = second_client.api("registry").post(
        f"/v1/packages/{package_id}/versions", json=version_body, headers=version_headers
    )
    assert replay_published.status_code == 201, replay_published.text
    assert replay_published.headers["Idempotency-Replayed"] == "true"
    assert replay_published.json() == published.json()
    version: dict[str, Any] = published.json()

    read = second_client.api("registry").get(f"/v1/packages/{package_id}/versions/{manifest['version']}")
    assert read.status_code == 200, read.text
    assert read.json() == version
    assert archive(second_client, package_id, manifest["version"], version["digest"]) == archive(
        first_client, package_id, manifest["version"], version["digest"]
    )


def test_r_02_registry_restart_replays_package_and_version(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    require("registry")
    registry = client("registry")
    manifest, files = package_files(FILES_DIR)
    package_id = f"e2e.registry-restart-{run_id}"
    manifest = {**manifest, "package_id": package_id}
    create_body = {"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]}
    create_headers = {"Idempotency-Key": key()}
    created = registry.api("registry").post("/v1/packages", json=create_body, headers=create_headers)
    assert created.status_code == 201, created.text

    version_body = publish_body(manifest, files)
    version_headers = {"Idempotency-Key": key()}
    version_path = f"/v1/packages/{package_id}/versions"
    published = registry.api("registry").post(version_path, json=version_body, headers=version_headers)
    assert published.status_code == 201, published.text
    before = archive(registry, package_id, manifest["version"], published.json()["digest"])

    stack.kill("registry")
    stack.restart("registry")
    restarted = client("registry")
    replay_created = restarted.api("registry").post("/v1/packages", json=create_body, headers=create_headers)
    assert replay_created.status_code == 201, replay_created.text
    assert replay_created.headers["Idempotency-Replayed"] == "true"
    assert replay_created.json() == created.json()
    replay_published = restarted.api("registry").post(
        version_path, json=version_body, headers=version_headers
    )
    assert replay_published.status_code == 201, replay_published.text
    assert replay_published.headers["Idempotency-Replayed"] == "true"
    assert replay_published.json() == published.json()
    mismatch = restarted.api("registry").post(
        version_path, json={**version_body, "files": {}}, headers=version_headers
    )
    assert mismatch.status_code == 422, mismatch.text
    assert mismatch.json()["code"] == "idempotency_key_reused"
    read = restarted.api("registry").get(f"{version_path}/{manifest['version']}")
    assert read.status_code == 200, read.text
    assert read.json() == published.json()
    assert archive(restarted, package_id, manifest["version"], published.json()["digest"]) == before
