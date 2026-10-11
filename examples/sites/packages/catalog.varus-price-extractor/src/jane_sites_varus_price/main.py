"""Price and availability of a varus.ua product from one item of the site's catalog API (``completeness: partial``).

The collector rules ``catalog.varus-prices-rules`` read the same category product lists as the catalog task
(``POST https://varus.ua/api/graphql``) with a short query - SKU, URL key, regional prices and availability - and
emit every item as a JSON material. One item is one partial ``product`` entity with only ``shop``,
``product_id``, ``price``, ``currency``, ``old_price`` and ``availability``: storage updates these fields of the
product the catalog task collected under the same key and keeps the rest (a missing field is not a deletion).

Prices are the regional ones the site shows to a visitor who has not chosen a shop (``regionalPriceInfo``): a
special price below the regular one is ``price`` and the regular price is ``old_price``; without a discount
``old_price`` is cleared. An item without a price (``price: 0`` - out of stock in the region) updates only
``availability`` (the last known price stays).

States (TZ §9): ``success`` - a product item; ``empty`` - JSON that is not a product item (an API error document);
``unrecognized`` - a product item without a SKU or without ``regionalPriceInfo``, or in stock without a price.
"""

from __future__ import annotations

import json
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized


def _positive(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if value > 0 else None


def _availability(value: Any) -> str:
    if not isinstance(value, dict) or not isinstance(value.get("inStock"), bool):
        return "unknown"
    return "in_stock" if value["inStock"] else "out_of_stock"


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    try:
        item = json.loads(ctx.text())
    except ValueError:
        ctx.log.warning("material is not JSON", code="extract.bad_json")
        return empty()
    if not isinstance(item, dict) or not ({"sku", "urlKey"} & item.keys()):
        return empty()  # not a product item of the catalog API (an error document, another object)

    sku = str(item.get("sku") or "").strip()
    if not sku:
        ctx.log.warning("product item without sku", code="extract.missing_field", selector="sku")
        return unrecognized("product item without sku", signature="missing-field:sku")
    info = item.get("regionalPriceInfo")
    if not isinstance(info, dict):
        ctx.log.warning(
            "product item without prices", code="extract.missing_field", selector="regionalPriceInfo"
        )
        return unrecognized("product item without prices", signature="missing-field:regionalPriceInfo")

    regular, special = _positive(info.get("price")), _positive(info.get("specialPrice"))
    price: float | None
    old_price: float | None
    if regular is not None and special is not None and special < regular:
        price, old_price = special, regular
    else:
        price, old_price = (regular if regular is not None else special), None
    availability = _availability(item.get("regionalAvailability"))
    if price is None and availability == "in_stock":
        ctx.log.warning(
            "product in stock without a price",
            code="extract.missing_field",
            selector="regionalPriceInfo.price",
        )
        return unrecognized(
            "product in stock without a price", signature="missing-field:regionalPriceInfo.price"
        )

    fields: dict[str, Any] = {
        "shop": params["shop"],
        "product_id": sku,
        "price": price,
        "currency": params["currency"] if price is not None else None,
        "old_price": old_price,
        "availability": availability,
    }
    cleared = ["old_price"] if price is not None and old_price is None else None
    return success([entity("product", fields, cleared=cleared, completeness="partial")])
