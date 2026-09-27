"""M1 - first end-to-end slice (plan.md §6): Web -> RAW in files and, in parallel, extraction by a local
package -> results in PostgreSQL. Scenarios S-M1-* of docs/acceptance/scenarios.md.

S-M1-01 runs now against what is merged into main (storage WP-07, handler-runtime WP-06, testsite WP-01);
the Web Collector (WP-02) is replaced by an explicitly labelled stand-in (jane_e2e.materials). S-M1-02 is
the same chain with the real collector, S-M1-03 the same chain driven by the orchestrator (WP-09); both
skip until those WPs are merged.
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import STANDIN_COLLECTOR, delivery_key, fetch_page, standin_web_material
from jane_e2e.stack import E2EStack
from jane_extractor_sdk.package import build_archive

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M1")]

ROOT = Path(__file__).resolve().parents[2]
EXTRACTOR_DIR = ROOT / "libs" / "extractor-sdk" / "examples" / "testsite-product-extractor"
PRODUCT_PATH = "/product/phone-alpha"
# Expected card of this product: the package's own test case (same page model as the test site).
EXPECTED_FIELDS = {
    "sku": "phone-alpha",
    "title": "Phone Alpha",
    "price": {"amount": 299.0, "currency": "UAH"},
    "availability": "in_stock",
}


def _extractor_ref() -> tuple[dict[str, Any], dict[str, Any]]:
    """Local package (not from the registry): handler ref + inline ContentRef of its canonical archive."""
    archive = build_archive(EXTRACTOR_DIR)
    sha = hashlib.sha256(archive).hexdigest()
    handler = {"package_id": "testsite.product-extractor", "version": "1.0.0", "digest": f"sha256:{sha}"}
    content = {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(archive).decode("ascii"),
        "size_bytes": len(archive),
        "sha256": sha,
    }
    return handler, content


def run_m1_chain(
    stack: E2EStack, storage: JaneClient, runtime: JaneClient, material: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """The M1 chain for one material: store-raw (files) || extract (runtime) -> store-products (PostgreSQL).

    Every step is checked through the public APIs (handler.v1 / storage.v1) of the real services, plus the
    RAW file on the storage volume. Returns ids for further checks.
    """
    source_id = material["source"]["source_id"]
    raw_bytes = (
        material["content"]["data"].encode("utf-8")
        if material["content"]["encoding"] == "utf-8"
        else base64.b64decode(material["content"]["data"])
    )

    # --- branch 1: RAW -> filesystem adapter (default format for a web page: HTML, TZ §5)
    store_raw = {
        "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
        "connections": {"target": "raw-files"},
        "inputs": [{"kind": "material", "material": material}],
        "context": {"trace": {"run_id": f"run_{run_id}", "stage_id": "store-raw", "source_id": source_id}},
        "delivery": {"delivery_key": delivery_key(run_id, "store-raw", material["observation_id"])},
    }
    _, raw_result = storage.invoke(store_raw)
    assert raw_result["status"] == "success", raw_result
    (raw_ack,) = raw_result["output"]["writes"]
    assert raw_ack["status"] == "written", raw_ack
    obj = raw_ack["object"]
    assert obj["locator"]["path"].endswith(".html"), obj
    assert obj["sha256"] == hashlib.sha256(raw_bytes).hexdigest()

    # the file itself on the storage volume: byte-for-byte the fetched page
    on_disk = stack.exec("storage", "cat", f"/var/lib/jane/storage/{obj['locator']['path']}")
    assert on_disk == raw_bytes

    # storage.v1 read API: listed for the material, content retrievable
    listed = storage.api("storage").get(
        "/v1/objects", params={"connection_id": "raw-files", "material_id": material["material_id"]}
    )
    assert listed.status_code == 200
    mine = [i for i in listed.json()["items"] if i["object"]["object_id"] == obj["object_id"]]
    assert len(mine) == 1, listed.json()
    assert mine[0]["material"]["observation_id"] == material["observation_id"]
    content = storage.api("storage").get(
        f"/v1/objects/{obj['object_id']}/content", params={"connection_id": "raw-files"}
    )
    assert content.status_code == 200
    assert content.content == raw_bytes

    # technical redelivery of the same result: duplicate, no second record (TZ §11)
    _, raw_again = storage.invoke(store_raw)
    assert raw_again["duplicate"] is True
    assert raw_again["output"]["writes"][0]["status"] == "duplicate"
    listed_again = storage.api("storage").get(
        "/v1/objects", params={"connection_id": "raw-files", "material_id": material["material_id"]}
    )
    same_obs = [
        i
        for i in listed_again.json()["items"]
        if i["material"]["observation_id"] == material["observation_id"]
    ]
    assert len(same_obs) == 1

    # --- branch 2: extraction by a local package in the sandbox runtime
    handler, archive = _extractor_ref()
    extract = {
        "handler": handler,
        "package_archive": archive,
        "inputs": [{"kind": "material", "material": material}],
        "context": {
            "trace": {"run_id": f"run_{run_id}", "stage_id": "extract-products", "source_id": source_id}
        },
        "delivery": {"delivery_key": delivery_key(run_id, "extract-products", material["observation_id"])},
        "mode": "sync",
    }
    _, extracted = runtime.invoke(extract)
    assert extracted["status"] == "success", extracted
    (entity,) = extracted["output"]["entities"]
    assert entity["entity_type"] == "product"
    assert entity["key"] == {"scope": source_id, "natural": {"sku": EXPECTED_FIELDS["sku"]}}
    for name, value in EXPECTED_FIELDS.items():
        assert entity["fields"][name] == value, (name, entity["fields"])
    assert entity["observation"]["observation_id"] == material["observation_id"]
    assert entity["provenance"]["package"]["digest"] == handler["digest"]

    # --- results -> PostgreSQL adapter
    store_products = {
        "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
        "connections": {"target": "results-pg"},
        "inputs": [
            {
                "kind": "entities",
                "entities": extracted["output"]["entities"],
                "from_invocation_id": extracted["invocation_id"],
            }
        ],
        "context": {
            "trace": {"run_id": f"run_{run_id}", "stage_id": "store-products", "source_id": source_id}
        },
        "delivery": {"delivery_key": delivery_key(run_id, "store-products", extracted["invocation_id"])},
    }
    _, stored = storage.invoke(store_products)
    assert stored["status"] == "success", stored
    (ack,) = stored["output"]["writes"]
    assert ack["status"] == "written", ack

    _, stored_again = storage.invoke(store_products)
    assert stored_again["duplicate"] is True
    assert stored_again["output"]["writes"][0]["status"] == "duplicate"

    entities = storage.api("storage").get(
        "/v1/entities", params={"connection_id": "results-pg", "entity_type": "product", "scope": source_id}
    )
    assert entities.status_code == 200
    (state,) = entities.json()["items"]
    assert state["version"] == 1, state  # redelivery did not create a new version
    for name, value in EXPECTED_FIELDS.items():
        assert state["fields"][name] == value
    history = storage.api("storage").get(
        "/v1/entity-history",
        params={
            "connection_id": "results-pg",
            "entity_type": "product",
            "key": state["canonical_key"],
        },
    )
    assert history.status_code == 200
    assert len(history.json()["items"]) == 1
    return {"object": obj, "entity": state, "extracted": extracted}


@pytest.mark.criteria(1, 2, 8, 12)
def test_s_m1_01_raw_to_files_and_extraction_to_postgres_standin_collector(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-01: testsite page -> (stand-in collector) -> RAW HTML in files || local extractor -> PostgreSQL."""
    require("testsite", "storage", "handler-runtime")
    page = fetch_page(stack.url("testsite") + PRODUCT_PATH)
    material = standin_web_material(
        page, source_id=f"e2e-{run_id}", observation_id=f"obs_e2e_{run_id}", section="products"
    )
    assert material["collector"]["name"] == STANDIN_COLLECTOR
    run_m1_chain(stack, client("storage"), client("handler-runtime"), material, run_id)


@pytest.mark.criteria(1, 2, 12)
def test_s_m1_02_raw_and_extraction_with_real_web_collector(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-02: the same chain, the material comes from the real Web Collector (collector.v1 fetchMaterial)."""
    require("testsite", "web-collector", "storage", "handler-runtime")
    collector = client("web-collector")
    r = collector.api("collector").post(
        "/v1/fetches",
        json={
            "source_kind": "web",
            "source_id": f"e2e-{run_id}",
            "url": f"http://testsite:8080{PRODUCT_PATH}",
        },
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
