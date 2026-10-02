"""R-06: two storage and registry replicas observe the same durable state."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import fetch_page, standin_web_material
from jane_e2e.registry import archive, key, package_files, publish_body
from jane_e2e.stack import E2EStack
from jane_e2e.steps import EXTRACTOR_DIR, store
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
    manifest, files = package_files(EXTRACTOR_DIR)
    package_id = manifest["package_id"]
    created = first_client.api("registry").post(
        "/v1/packages",
        json={"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]},
        headers={"Idempotency-Key": key()},
    )
    assert created.status_code == 201, created.text
    published = first_client.api("registry").post(
        f"/v1/packages/{package_id}/versions",
        json=publish_body(manifest, files),
        headers={"Idempotency-Key": key()},
    )
    assert published.status_code == 201, published.text
    version: dict[str, Any] = published.json()

    read = second_client.api("registry").get(f"/v1/packages/{package_id}/versions/{manifest['version']}")
    assert read.status_code == 200, read.text
    assert read.json() == version
    assert archive(second_client, package_id, manifest["version"], version["digest"]) == archive(
        first_client, package_id, manifest["version"], version["digest"]
    )
