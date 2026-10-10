"""Packages of examples/shops (real shops' laptop prices): manifest tests and rule documents, without services."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import jane_examples as ex
from jane_extractor_sdk.testing import assert_package_tests_pass

SHOPS = Path(__file__).resolve().parents[1] / "shops" / "packages"


def test_jsonld_offers_extractor_manifest_tests_pass() -> None:
    assert_package_tests_pass(SHOPS / "shops.jsonld-offers")


@pytest.mark.parametrize("package", sorted(p.name for p in SHOPS.glob("shops.*-notebooks-rules")))
def test_shop_rules_are_valid_and_polite(package: str) -> None:
    rules: dict[str, Any] = json.loads((SHOPS / package / "rules.json").read_text(encoding="utf-8"))
    assert ex.validate("collector-rules.schema.json", rules) == []
    assert rules["robots"] == {"mode": "respect"}
    assert [s["type"] for s in rules["strategies"]] == ["seed_list"]  # category pages only, no link following
    assert len(rules["strategies"][0]["urls"]) <= 5
    assert rules["dedup"]["use_link_rel_canonical"] is False  # pages 2-5 point rel=canonical at page 1
