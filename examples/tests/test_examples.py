"""Offline checks of the WP-14 examples: packages, their tests, digests and documents against contracts/.

Run: ``uv run --all-packages pytest examples -q`` (no Docker, no services). The end-to-end run against a
stack is ``examples/jane_examples.py demo`` (see examples/README.md).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

import jane_examples as ex
from jane_extractor_sdk.testing import assert_package_tests_pass, run_local
from jane_registry.archive import ArchiveLimits, is_canonical
from jane_testsite import serve_in_thread  # type: ignore[import-untyped]

EXTRACTORS = ("examples.testsite-catalog-extractor", "examples.testsite-price-extractor")
CATALOG, PRICE = EXTRACTORS


@pytest.fixture(scope="module")
def testsite() -> Iterator[str]:
    with serve_in_thread() as base:
        yield base


def _expected_urls() -> dict[str, Any]:
    data: dict[str, Any] = ex.read_json(ex.ROOT / "tests" / "fixtures" / "testsite" / "expected_urls.json")
    return data


def test_offline_check_has_no_problems() -> None:
    """Manifests and rules vs contract schemas, package tests, lock digests, documents pinned to the lock."""
    assert ex.check_offline() == []


@pytest.mark.parametrize("package_id", EXTRACTORS)
def test_manifest_tests_pass_in_process(package_id: str) -> None:
    assert_package_tests_pass(ex.PACKAGES_DIR / package_id)


@pytest.mark.parametrize("package_id", [*ex.LOCAL_PACKAGES, *ex.STORAGE_PACKAGES])
def test_archive_is_the_registry_canonical_form_and_matches_the_lock(package_id: str) -> None:
    archive = ex.canonical_archive(package_id)
    assert archive == ex.canonical_archive(package_id)
    assert is_canonical(archive, ArchiveLimits(20 * 2**20, 50 * 2**20, 2000))
    lock = ex.read_json(ex.LOCK_FILE)["packages"][package_id]
    assert ex.digest_of(archive) == lock["digest"]


def test_test_pages_are_current_testsite_renderings(testsite: str) -> None:
    for package_id, cases in ex.SNAPSHOTS.items():
        for case, path in cases.items():
            stored = (ex.PACKAGES_DIR / package_id / "tests" / case / "page.html").read_bytes()
            assert stored == ex.render_page(testsite, path), (
                f"{package_id}/{case}: run `jane_examples.py snapshot`"
            )


def test_every_testsite_product_full_card_and_price_update_agree(testsite: str, tmp_path: Path) -> None:
    """All 19 products: the catalog gives a full card, the price check exactly sku/price/availability."""
    products = sorted(p for p, kind in _expected_urls()["page_types"].items() if kind == "product")
    assert len(products) == 19
    for path in products:
        page = tmp_path / "page.html"
        page.write_bytes(ex.render_page(testsite, path))
        url = f"http://{ex.TESTSITE_HOST}{path}"
        full = run_local(ex.PACKAGES_DIR / CATALOG, file=page, media_type="text/html", url=url)
        price = run_local(ex.PACKAGES_DIR / PRICE, file=page, media_type="text/html", url=url)
        assert full["status"] == price["status"] == "success", (path, full, price)
        (card,) = full["output"]["entities"]
        (update,) = price["output"]["entities"]
        assert card["completeness"] == "full" and update["completeness"] == "partial"
        assert set(card["fields"]) == {"sku", "title", "price", "availability", "category", "url"}
        assert set(update["fields"]) == ex.PRICE_FIELDS
        assert {k: card["fields"][k] for k in ex.PRICE_FIELDS} == update["fields"]
        assert card["key"] == update["key"]


@pytest.mark.parametrize("path", ["/catalog/phones/", "/pages/faq", "/news/2026/launch-alpha", "/about"])
def test_non_product_pages_are_empty_for_both_extractors(testsite: str, tmp_path: Path, path: str) -> None:
    page = tmp_path / "page.html"
    page.write_bytes(ex.render_page(testsite, path))
    for package_id in EXTRACTORS:
        result = run_local(
            ex.PACKAGES_DIR / package_id, file=page, media_type="text/html", url=f"http://x{path}"
        )
        assert result["status"] == "empty", (package_id, path, result)


def test_price_check_urls_are_catalog_products_inside_the_rules_scope() -> None:
    task = ex.read_json(ex.DOCUMENTS_DIR / ex.PRICE_DOC)
    rules = ex.read_json(ex.PACKAGES_DIR / "examples.testsite-web-rules" / "rules.json")
    catalog = set(_expected_urls()["sets"]["categories"])
    for url in task["input"]["urls"]:
        parts = urlsplit(url)
        assert parts.netloc == ex.TESTSITE_HOST
        assert parts.path in catalog, url
        assert any(parts.path.startswith(prefix) for prefix in rules["scope"]["path_prefixes"])


def test_tasks_are_independent_and_differ_only_where_the_spec_says() -> None:
    """TZ §6: separate tasks; the price check reads given URLs and stores a partial update, on a schedule."""
    catalog = ex.read_json(ex.DOCUMENTS_DIR / ex.CATALOG_DOC)
    price = ex.read_json(ex.DOCUMENTS_DIR / ex.PRICE_DOC)
    assert catalog["task_id"] != price["task_id"]
    assert catalog["input"]["source_id"] == price["input"]["source_id"]  # same entity key scope
    assert "urls" not in catalog["input"] and price["input"]["urls"]
    assert price["schedule"]["type"] in {"interval", "cron"}
    extract = {s["stage_id"]: s for s in price["stages"]}["extract-price"]
    assert extract["handler"]["package_id"] == PRICE
    stored = {s["stage_id"]: s for s in catalog["stages"]}
    assert stored["extract-products"]["handler"]["package_id"] == CATALOG
    assert stored["store-raw"]["connections"]["target"] == "raw-files"


def test_documents_hold_no_secret_values() -> None:
    for path in ex.DOCUMENTS_DIR.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        doc = json.loads(text)
        for conn in doc.get("connections", []):
            for ref in (conn.get("secret_refs") or {}).values():
                assert ref.startswith("env:JANE_SECRET_"), (path.name, ref)
        assert "password" not in json.dumps([c.get("params") for c in doc.get("connections", [])]).lower()
