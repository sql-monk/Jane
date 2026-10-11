"""Prostor price absence and discount clearing against the SDK and the actual storage merge."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError

from jane_contracts.storage_adapter import EntitySnapshot
from jane_extractor_sdk.testing import run_local
from jane_storage.merge import merge

FULL = Path(__file__).resolve().parents[1]
PRICES = FULL.parent / "catalog.prostor-price-extractor"
NOW = datetime(2026, 10, 11, tzinfo=UTC)


def _result(package: Path, case: str) -> dict[str, Any]:
    return run_local(
        package,
        file=package / "tests" / case / "page.html",
        media_type="text/html",
        url="https://prostor.ua/ua/product/example/",
    )


def _previous(record: dict[str, Any]) -> EntitySnapshot:
    seed = copy.deepcopy(record)
    seed.pop("cleared", None)
    seed["fields"].update(price=123.0, currency="UAH", old_price=150.0, availability="in_stock")
    seed["observation"].update(observed_at="2026-10-10T01:00:00Z", observation_id="old-price")
    return merge(None, seed, now=NOW).snapshot


def _newer(record: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(record)
    updated["observation"].update(observed_at="2026-10-11T01:00:00Z", observation_id="new-card")
    return updated


@pytest.mark.parametrize("package", [FULL, PRICES], ids=["full-card", "price-tile"])
def test_unpriced_out_of_stock_updates_availability_and_preserves_last_prices(package: Path) -> None:
    result = _result(package, "out-of-stock-without-price")
    assert result["status"] == "success"
    record = result["output"]["entities"][0]
    assert record["completeness"] == "partial"
    assert record["fields"]["availability"] == "out_of_stock"
    assert {"price", "currency", "old_price"}.isdisjoint(record["fields"])
    assert {"price", "old_price"}.isdisjoint(record.get("cleared", []))
    schema = json.loads((package / "schemas/product.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(record["fields"])
    if package == FULL:
        assert record["fields"]["product_id"] == "1723"
        assert record["fields"]["attributes"]["Brand"] == "Syoss"
        assert record["fields"]["volume"] == 200
    after = merge(_previous(record), _newer(record), now=NOW).snapshot
    assert after.fields["availability"] == "out_of_stock"
    assert after.fields["price"] == 123.0
    assert after.fields["old_price"] == 150.0


@pytest.mark.parametrize(
    ("package", "case"),
    [(FULL, "cream-loreal"), (PRICES, "laundry-page-1")],
    ids=["full-card", "price-tile"],
)
def test_priced_card_without_discount_clears_the_previous_discount(package: Path, case: str) -> None:
    result = _result(package, case)
    record = next(
        item
        for item in result["output"]["entities"]
        if "price" in item["fields"] and "old_price" not in item["fields"]
    )
    assert "old_price" in record["cleared"]
    after = merge(_previous(record), _newer(record), now=NOW).snapshot
    assert "old_price" not in after.fields
    assert after.fields["price"] == record["fields"]["price"]


def test_in_stock_card_missing_price_retains_metadata_but_stays_unrecognized() -> None:
    result = _result(FULL, "card-without-price")
    assert result["status"] == "unrecognized"
    assert result["unrecognized"]["partial"] is True
    record = result["output"]["entities"][0]
    assert record["fields"]["title"]
    assert "price" not in record["fields"]
    schema = Draft202012Validator(
        json.loads((FULL / "schemas/product.schema.json").read_text(encoding="utf-8"))
    )
    schema.validate(record["fields"])
    with pytest.raises(ValidationError):
        schema.validate({**record["fields"], "completeness": "full"})
