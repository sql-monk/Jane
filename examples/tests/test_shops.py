"""Packages of examples/shops (real shops' laptop prices): manifest tests, rule documents and the task
documents of ``setup_shops.py``, without services."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

SHOPS_DIR = Path(__file__).resolve().parents[1] / "shops"
sys.path.insert(0, str(SHOPS_DIR))

import setup_shops  # noqa: E402

import jane_examples as ex  # noqa: E402
from jane_extractor_sdk.testing import assert_package_tests_pass, run_local  # noqa: E402

SHOPS = SHOPS_DIR / "packages"
EXTRACTORS = ["shops.jsonld-offers", "shops.product-cards"]


def manifest(package: str) -> dict[str, Any]:
    doc: dict[str, Any] = ex.read_json(SHOPS / package / "jane-package.json")
    return doc


@pytest.mark.parametrize("package", EXTRACTORS)
def test_offer_extractor_manifest_tests_pass(package: str) -> None:
    assert_package_tests_pass(SHOPS / package)


@pytest.mark.parametrize("package", EXTRACTORS)
def test_extractor_declares_every_product_type_with_one_schema(package: str) -> None:
    m = manifest(package)
    assert ex.validate("package-manifest.schema.json", m) == []
    assert ex.package_json_problems(SHOPS / package, m) == []
    declared = m["output"]["entities"]
    types = [e["entity_type"] for e in declared]
    assert all(t.startswith("product_") for t in types) and len(set(types)) == len(types)
    assert {"product_electronics", "product_other"} <= set(types)
    assert {(e["schema"], tuple(e["key_fields"])) for e in declared} == {
        ("schemas/product.schema.json", ("shop", "product_id"))
    }
    params = ex.read_json(SHOPS / package / m["params_schema"])
    # the stage must name the type: no default, only the declared types
    assert "entity_type" in params["required"]
    assert "default" not in params["properties"]["entity_type"]
    assert params["properties"]["entity_type"]["enum"] == types
    assert all(case["params"]["entity_type"] == "product_electronics" for case in m["tests"])


@pytest.mark.parametrize("package", EXTRACTORS)
def test_entity_type_comes_from_the_stage_parameter(package: str) -> None:
    case = next(c for c in manifest(package)["tests"] if c["expected_status"] == "success")
    page = dict(
        file=SHOPS / package / case["input"]["file"], media_type="text/html", url=case["input"]["url"]
    )
    other = run_local(SHOPS / package, params={"entity_type": "product_other"}, **page)
    assert other["status"] == "success"
    assert {e["entity_type"] for e in other["output"]["entities"]} == {"product_other"}
    assert run_local(SHOPS / package, **page)["status"] == "failed"  # no type given: nothing is guessed


def test_notebook_tasks_store_product_electronics_in_mongodb() -> None:
    dirs = setup_shops.package_dirs()
    assert set(setup_shops.STORAGE) <= set(dirs)
    refs = {
        pid: {
            "package_id": pid,
            "version": ex.read_json(d / "jane-package.json")["version"],
            "digest": "sha256:" + "0" * 64,
        }
        for pid, d in dirs.items()
    }
    assert refs["jane.storage-mongodb"]["version"].split(".")[0] == "2"  # a collection per entity type
    connections = {c["connection_id"]: c for c in setup_shops.connection_docs()}
    assert connections["results-mongo"]["kind"] == "mongodb"
    assert connections["raw-files"]["kind"] == "filesystem"
    for shop, (url, title, extractor) in setup_shops.SHOPS.items():
        source = setup_shops.source_doc(shop, url, title, refs)
        assert ex.validate("source.schema.json", source) == []
        assert source["expected_entity_types"] == ["product_electronics"]
        task = setup_shops.task_doc(shop, title, extractor, refs)
        assert ex.validate("task-config.schema.json", task) == []
        stages = {s["stage_id"]: s for s in task["stages"]}
        assert stages["extract-offers"]["params"] == {"entity_type": "product_electronics"}
        assert "product_electronics" in [e["entity_type"] for e in manifest(extractor)["output"]["entities"]]
        assert stages["store-offers"]["handler"]["package_id"] == "jane.storage-mongodb"
        assert stages["store-offers"]["connections"] == {"target": "results-mongo"}
        assert stages["store-raw"]["handler"]["package_id"] == "jane.storage-files"
        assert stages["store-raw"]["connections"] == {"target": "raw-files"}


@pytest.mark.parametrize("package", sorted(p.name for p in SHOPS.glob("shops.*-notebooks-rules")))
def test_shop_rules_are_valid_and_polite(package: str) -> None:
    rules: dict[str, Any] = json.loads((SHOPS / package / "rules.json").read_text(encoding="utf-8"))
    assert ex.validate("collector-rules.schema.json", rules) == []
    assert rules["robots"] == {"mode": "respect"}
    assert [s["type"] for s in rules["strategies"]] == ["seed_list"]  # category pages only, no link following
    assert len(rules["strategies"][0]["urls"]) <= 5
    assert rules["dedup"]["use_link_rel_canonical"] is False  # pages 2-5 point rel=canonical at page 1
