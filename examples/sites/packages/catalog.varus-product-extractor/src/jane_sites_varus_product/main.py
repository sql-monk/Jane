"""Full product card of varus.ua from one item of the site's catalog API (``completeness: full``).

The collector rules ``catalog.varus-catalog-rules`` read the product lists of the categories through the API the
category pages of the site use themselves (``POST https://varus.ua/api/graphql``) with the ``api_feed`` strategy
and emit every product item as a JSON material (``emit_items_as_materials``). One item is one ``product`` entity
keyed by ``shop`` + ``product_id`` (the shop's SKU, the same as ``sku`` in the JSON-LD of the product page).

Prices are the regional ones the site shows to a visitor who has not chosen a shop (``regionalPriceInfo``): a
special price below the regular one is ``price`` and the regular price is then ``old_price``; without a discount
``old_price`` is cleared. An item without a price (``price: 0`` - out of stock in the region) sends no ``price``
(the last known one stays, a missing field is not a deletion) and ``availability: out_of_stock``.

States (TZ §9): ``success`` - a product item; ``empty`` - JSON that is not a product item (an API error document);
``unrecognized`` - a product item without a SKU, a name or a URL key, or in stock without a price.
"""

from __future__ import annotations

import json
import re
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SPACES = re.compile(r"\s+")
OWN_FIELDS = {"countrymanufacturerforsite": "country", "pim_brand_id": "brand"}


def _clean(value: Any) -> str | None:
    if value is None or isinstance(value, bool | dict | list):
        return None
    text = SPACES.sub(" ", str(value)).strip()
    return text or None


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _positive(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if value > 0 else None


def _prices(info: Any) -> tuple[float | None, float | None]:
    """``(price, old_price)`` of ``regionalPriceInfo``: a special price below the regular one is the price."""
    if not isinstance(info, dict):
        return None, None
    regular, special = _positive(info.get("price")), _positive(info.get("specialPrice"))
    if regular is not None and special is not None and special < regular:
        return special, regular
    return regular if regular is not None else special, None


def _availability(value: Any) -> str:
    if not isinstance(value, dict) or not isinstance(value.get("inStock"), bool):
        return "unknown"
    return "in_stock" if value["inStock"] else "out_of_stock"


def _attribute_value(attr: dict[str, Any]) -> str | None:
    if "textValue" in attr:
        return _clean(attr["textValue"])
    number = attr.get("numberValue")
    if isinstance(number, int | float) and not isinstance(number, bool):
        return f"{number:g}"
    option = attr.get("option")
    if isinstance(option, dict):
        return _clean(option.get("label"))
    options = attr.get("options")
    if isinstance(options, list):
        labels = [_clean(o.get("label")) for o in options if isinstance(o, dict)]
        return ", ".join(label for label in labels if label) or None
    if isinstance(attr.get("boolValue"), bool):
        return "так" if attr["boolValue"] else "ні"
    return None


def _attributes(item: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    """``(attributes by label, own fields)``: the country and the brand become fields of their own."""
    attributes: dict[str, str] = {}
    own: dict[str, str] = {}
    for attr in item.get("attributes") or []:
        if not isinstance(attr, dict):
            continue
        value = _attribute_value(attr)
        code, label = str(attr.get("code") or ""), _clean(attr.get("label"))
        if value is None:
            continue
        if code in OWN_FIELDS:
            own.setdefault(OWN_FIELDS[code], value)
        elif label:
            attributes.setdefault(label, value)
    return attributes, own


def _category_path(item: dict[str, Any]) -> list[str]:
    """Product categories from level 2 down to the primary category (one per level, the API order)."""
    primary = _obj(item.get("primaryCategory"))
    primary_name = _clean(primary.get("name"))
    tree = [
        c
        for c in item.get("categories") or []
        if isinstance(c, dict)
        and c.get("isProductCategory") is True
        and isinstance(c.get("level"), int)
        and c["level"] >= 2
        and _clean(c.get("name"))
    ]
    primary_level = next((c["level"] for c in tree if c.get("urlKey") == primary.get("urlKey")), None)
    path: dict[int, str] = {}
    for c in sorted(tree, key=lambda c: c["level"]):
        if primary_level is not None and c["level"] >= primary_level:
            break
        path.setdefault(c["level"], str(_clean(c["name"])))
    names = list(path.values())
    if primary_name:
        names.append(primary_name)
    return names


def _size(value: Any, unit: str) -> str | None:
    try:
        amount = float(str(value).replace(",", "."))
    except ValueError:
        return None
    return f"{amount:g} {unit}" if amount > 0 else None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    try:
        item = json.loads(ctx.text())
    except ValueError:
        ctx.log.warning("material is not JSON", code="extract.bad_json")
        return empty()
    if not isinstance(item, dict) or not ({"sku", "urlKey"} & item.keys()):
        return empty()  # not a product item of the catalog API (an error document, another object)

    sku, title, url_key = _clean(item.get("sku")), _clean(item.get("name")), _clean(item.get("urlKey"))
    for name, value in (("sku", sku), ("name", title), ("urlKey", url_key)):
        if not value:
            ctx.log.warning(f"product item without {name}", code="extract.missing_field", selector=name)
            return unrecognized(f"product item without {name}", signature=f"missing-field:{name}")

    price, old_price = _prices(item.get("regionalPriceInfo"))
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

    attributes, own = _attributes(item)
    brand, gallery, step = _obj(item.get("brand")), _obj(item.get("gallery")), _obj(item.get("qtyStep"))
    path = _category_path(item)
    fields: dict[str, Any] = {
        "shop": params["shop"],
        "product_id": sku,
        "title": title,
        "url": str(params["product_url"]).format(url_key=url_key),
        "price": price,
        "currency": params["currency"],
        "old_price": old_price,
        "availability": availability,
        "brand": _clean(brand.get("name")) or own.get("brand"),
        "category": path[-1] if path else None,
        "category_path": path or None,
        "image": str(params["image_url"]).format(sku=sku) if gallery.get("mainImageTimestamp") else None,
        "sku": sku,
        "unit": "кг" if step.get("isDecimal") is True else "шт",
        "weight": _size(item.get("weight"), "г"),
        "volume": _size(item.get("volume"), "мл"),
        "country": own.get("country"),
        "attributes": attributes or None,
        "completeness": "full",
    }
    cleared = ["old_price"] if price is not None and old_price is None else None
    return success([entity("product", fields, cleared=cleared, completeness="full")])
