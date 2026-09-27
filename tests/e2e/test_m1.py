"""M1 - first end-to-end slice (plan.md §6): Web -> RAW in files and, in parallel, extraction by a local
package -> results in PostgreSQL. Scenarios S-M1-* of docs/acceptance/scenarios.md.

S-M1-01 and S-M1-05 run now against what is merged into main (storage WP-07, handler-runtime WP-06,
testsite WP-01); the Web Collector (WP-02) is replaced by an explicitly labelled stand-in
(jane_e2e.materials). S-M1-02 is the same chain with the real collector, S-M1-03 the chain driven by the
orchestrator (WP-09); both skip until those WPs are merged.
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Callable
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import STANDIN_COLLECTOR, fetch_page, standin_web_material
from jane_e2e.stack import E2EStack
from jane_e2e.steps import extract, store

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M1")]

PRODUCT_PATH = "/product/phone-alpha"
# Expected card of this product: the package's own test case (same page model as the test site).
EXPECTED_FIELDS = {
    "sku": "phone-alpha",
    "title": "Phone Alpha",
    "price": {"amount": 299.0, "currency": "UAH"},
    "availability": "in_stock",
}


def _raw_bytes(material: dict[str, Any]) -> bytes:
    content = material["content"]
    if content["encoding"] == "utf-8":
        return str(content["data"]).encode("utf-8")
    return base64.b64decode(content["data"])


def _objects_of(storage: JaneClient, connection: str, material: dict[str, Any]) -> list[dict[str, Any]]:
    r = storage.api("storage").get(
        "/v1/objects", params={"connection_id": connection, "material_id": material["material_id"]}
    )
    assert r.status_code == 200, r.text
    return [i for i in r.json()["items"] if i["material"]["observation_id"] == material["observation_id"]]


def _entities(storage: JaneClient, connection: str, scope: str) -> list[dict[str, Any]]:
    r = storage.api("storage").get(
        "/v1/entities", params={"connection_id": connection, "entity_type": "product", "scope": scope}
    )
    assert r.status_code == 200, r.text
    return list(r.json()["items"])


def store_raw_in_files(
    stack: E2EStack, storage: JaneClient, material: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """Branch 1: RAW -> filesystem adapter (default format of a web page: HTML, TZ §5) + redelivery."""
    raw = _raw_bytes(material)
    inputs = [{"kind": "material", "material": material}]
    kw: dict[str, Any] = {"run_id": run_id, "stage_id": "store-raw", "key_part": material["observation_id"]}
    body, result = store(
        storage, package_id="jane.storage-files", connection="raw-files", inputs=inputs, **kw
    )
    assert result["status"] == "success", result
    (ack,) = result["output"]["writes"]
    assert ack["status"] == "written", ack
    obj = ack["object"]
    assert obj["locator"]["path"].endswith(".html"), obj
    assert obj["sha256"] == hashlib.sha256(raw).hexdigest()

    # the file itself on the storage volume: byte-for-byte the fetched page
    assert stack.exec("storage", "cat", f"/var/lib/jane/storage/{obj['locator']['path']}") == raw

    # storage.v1 read API: listed for the material, content retrievable
    (listed,) = _objects_of(storage, "raw-files", material)
    assert listed["object"]["object_id"] == obj["object_id"]
    content = storage.api("storage").get(
        f"/v1/objects/{obj['object_id']}/content", params={"connection_id": "raw-files"}
    )
    assert content.status_code == 200
    assert content.content == raw

    # technical redelivery of the same result: duplicate, no second record (TZ §11)
    _, again = storage.invoke(body)
    assert again["duplicate"] is True
    assert again["output"]["writes"][0]["status"] == "duplicate"
    assert len(_objects_of(storage, "raw-files", material)) == 1
    return dict(obj)


def extract_products(runtime: JaneClient, material: dict[str, Any], run_id: str) -> dict[str, Any]:
    """Branch 2: extraction by a local package in the sandbox runtime."""
    _, result = extract(runtime, material, run_id)
    assert result["status"] == "success", result
    (entity,) = result["output"]["entities"]
    assert entity["entity_type"] == "product"
    assert entity["key"] == {
        "scope": material["source"]["source_id"],
        "natural": {"sku": EXPECTED_FIELDS["sku"]},
    }
    for name, value in EXPECTED_FIELDS.items():
        assert entity["fields"][name] == value, (name, entity["fields"])
    assert entity["observation"]["observation_id"] == material["observation_id"]
    assert entity["provenance"]["package"]["digest"] == result["handler"]["digest"]
    return result


def store_entities(
    storage: JaneClient, package_id: str, connection: str, extracted: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """Results -> storage adapter, redelivery is a duplicate; returns the entity state from storage.v1."""
    inputs = [
        {
            "kind": "entities",
            "entities": extracted["output"]["entities"],
            "from_invocation_id": extracted["invocation_id"],
        }
    ]
    kw: dict[str, Any] = {
        "run_id": run_id,
        "stage_id": f"store-{connection}",
        "key_part": extracted["invocation_id"],
    }
    body, result = store(storage, package_id=package_id, connection=connection, inputs=inputs, **kw)
    assert result["status"] == "success", result
    assert result["output"]["writes"][0]["status"] == "written", result
    _, again = storage.invoke(body)
    assert again["duplicate"] is True
    assert again["output"]["writes"][0]["status"] == "duplicate"

    scope = extracted["output"]["entities"][0]["key"]["scope"]
    (state,) = _entities(storage, connection, scope)
    assert state["version"] == 1, state  # redelivery did not create a new version
    for name, value in EXPECTED_FIELDS.items():
        assert state["fields"][name] == value
    history = storage.api("storage").get(
        "/v1/entity-history",
        params={"connection_id": connection, "entity_type": "product", "key": state["canonical_key"]},
    )
    assert history.status_code == 200
    assert len(history.json()["items"]) == 1
    return dict(state)


def run_m1_chain(
    stack: E2EStack, storage: JaneClient, runtime: JaneClient, material: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """The M1 chain for one material: store-raw (files) || extract (runtime) -> store-products (PostgreSQL)."""
    obj = store_raw_in_files(stack, storage, material, run_id)
    extracted = extract_products(runtime, material, run_id)
    state = store_entities(storage, "jane.storage-postgresql", "results-pg", extracted, run_id)
    return {"object": obj, "extracted": extracted, "state": state}


def _standin_material(stack: E2EStack, run_id: str) -> dict[str, Any]:
    page = fetch_page(stack.url("testsite") + PRODUCT_PATH)
    material = standin_web_material(
        page, source_id=f"e2e-{run_id}", observation_id=f"obs_e2e_{run_id}", section="products"
    )
    assert material["collector"]["name"] == STANDIN_COLLECTOR
    return material


@pytest.mark.criteria(1, 2, 8, 12)
def test_s_m1_01_raw_to_files_and_extraction_to_postgres_standin_collector(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-01: testsite page -> (stand-in collector) -> RAW HTML in files || local extractor -> PostgreSQL."""
    require("testsite", "storage", "handler-runtime")
    material = _standin_material(stack, run_id)
    run_m1_chain(stack, client("storage"), client("handler-runtime"), material, run_id)


@pytest.mark.criteria(1, 2, 12)
def test_s_m1_02_raw_and_extraction_with_real_web_collector(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-02: the same chain, the material comes from the real Web Collector (collector.v1 fetchMaterial)."""
    require("testsite", "web-collector", "storage", "handler-runtime")
    r = (
        client("web-collector")
        .api("collector")
        .post(
            "/v1/fetches",
            json={
                "source_kind": "web",
                "source_id": f"e2e-{run_id}",
                "url": f"http://testsite:8080{PRODUCT_PATH}",
            },
        )
    )
    assert r.status_code == 200, r.text
    material = r.json()
    assert material["collector"]["name"] != STANDIN_COLLECTOR
    run_m1_chain(stack, client("storage"), client("handler-runtime"), material, run_id)


@pytest.mark.criteria(2)
def test_s_m1_03_orchestrated_task_web_to_files_and_postgres(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-03: the M1 task (collect -> store-raw || extract -> store-products) run by the orchestrator."""
    require("testsite", "web-collector", "orchestrator", "storage", "handler-runtime")
    pytest.skip("сценарій реалізується у фазі M1 WP-13, коли WP-02 і WP-09 будуть у main")


@pytest.mark.criteria(3)
def test_s_m1_05_storage_swap_is_configuration_only(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-05: the same extractor output is stored in PostgreSQL and in files; only the storage package and
    connection differ, the collector material and the extractor call are byte-for-byte the same."""
    require("testsite", "storage", "handler-runtime")
    storage, runtime = client("storage"), client("handler-runtime")
    material = _standin_material(stack, run_id)
    extracted = extract_products(runtime, material, run_id)
    in_pg = store_entities(storage, "jane.storage-postgresql", "results-pg", extracted, run_id)
    in_files = store_entities(storage, "jane.storage-files", "raw-files", extracted, run_id)
    assert in_files["canonical_key"] == in_pg["canonical_key"]
    assert in_files["fields"] == in_pg["fields"]
