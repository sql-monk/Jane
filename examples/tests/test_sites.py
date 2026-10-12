"""Sites of examples/sites (real catalogs, ads, news, Telegram): documents, manifests and package tests, no services."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any, cast

import pytest

SITES = Path(__file__).resolve().parents[1] / "sites"
sys.path.insert(0, str(SITES))

import setup_sites  # noqa: E402


@pytest.mark.parametrize("site", [p.stem for p in sorted((SITES / "sites").glob("*.json"))])
def test_site_documents_and_packages(site: str) -> None:
    problems = setup_sites.check_site(SITES / "sites" / f"{site}.json", setup_sites.package_dirs(), set())
    assert problems == []


def read(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


CATALOGS = [p.stem for p in sorted((SITES / "sites").glob("*.json")) if read(p)["group"] == "catalog"]


@pytest.mark.parametrize("site", CATALOGS)
def test_catalog_card_and_price_extractors_share_the_category_table(site: str) -> None:
    """The price task must write the product type the card task wrote: one table and lookup per shop."""
    config = read(SITES / "sites" / f"{site}.json")
    dirs = setup_sites.package_dirs()
    extractors = [
        pid for s in config["sources"] for pid in setup_sites.source_extractors(config, dirs, s["source_id"])
    ]
    assert extractors and all(setup_sites.category_code(dirs[pid]) for pid in extractors)
    assert setup_sites.category_problems(site, config, dirs) == []


def test_category_check_detects_a_diverging_price_table(tmp_path: Path) -> None:
    config = read(SITES / "sites" / "epicentrk.json")
    dirs = dict(setup_sites.package_dirs())
    copy = tmp_path / "catalog.epicentrk-prices"
    shutil.copytree(dirs["catalog.epicentrk-prices"], copy)
    module = next(copy.glob("src/*/main.py"))
    text = module.read_text(encoding="utf-8")
    module.write_text(
        text.replace('("Сад та город",): "product_garden"', '("Сад та город",): "product_home"'),
        encoding="utf-8",
    )
    dirs["catalog.epicentrk-prices"] = copy
    problems = setup_sites.category_problems("epicentrk", config, dirs)
    assert any("differs from catalog.epicentrk-products" in p for p in problems), problems
