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

The entity type is the product group of the card's ``category_path`` (``CATEGORY_TYPES``: the longest table
prefix wins, an unknown section is ``product_other``); the price extractor of the shop uses the same table.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SPACES = re.compile(r"\s+")
OWN_FIELDS = {"countrymanufacturerforsite": "country", "pim_brand_id": "brand"}


# Catalog section (a prefix of ``category_path``) -> entity type, one MongoDB collection per type. The longest
# prefix in the table wins; a section that is not in the table is ``OTHER_TYPE`` (seasonal and promotional
# sections are only listed with their subsections). The card and the price extractor of the shop carry the same
# table and lookup - a price update must name the type of the card (examples/tests/test_sites.py compares them).
CATEGORY_TYPES: dict[tuple[str, ...], str] = {
    ("VARUS CAFE",): "product_food",
    ("Алкоголь",): "product_food",
    ("Бакалія",): "product_food",
    ("Вода, соки, напої",): "product_food",
    ("Гігієна та догляд",): "product_beauty",
    ("Гігієна та догляд", "Товари для здоров'я"): "product_health",
    ("Заморожені продукти",): "product_food",
    ("Здорове харчування та Еко товари",): "product_food",
    ("Здорове харчування та Еко товари", "БАДи (харчові добавки)"): "product_health",
    ("Ковбаси, сосиски, делікатеси",): "product_food",
    ("Кондитерські вироби та солодощі",): "product_food",
    ("Консервація та соління",): "product_food",
    ("Молочні продукти та яйця",): "product_food",
    ("М'ясо та напівфабрикати",): "product_food",
    ("Побутова хімія",): "product_household",
    ("Риба та морепродукти",): "product_food",
    ("Сири",): "product_food",
    ("Снеки",): "product_food",
    ("Товари для дітей",): "product_kids",
    ("Товари для дітей", "Шкільні товари"): "product_office",
    ("Товари для дому",): "product_home",
    ("Товари для дому", "Канцтовари"): "product_office",
    ("Товари для дому", "Одяг, взуття та аксесуари"): "product_clothing",
    ("Товари для дому", "Сад та город"): "product_garden",
    ("Товари для дому", "Спорт та розваги"): "product_sport",
    ("Товари для дому", "Товари для кемпінгу та відпочинку"): "product_sport",
    ("Товари для тварин",): "product_pet",
    ("Фрукти, овочі, горіхи",): "product_food",
    ("Хлібобулочні вироби",): "product_food",
    ("Чай, кава, гарячі напої",): "product_food",
}
OTHER_TYPE = "product_other"
APOSTROPHES = str.maketrans(dict.fromkeys("\u2019\u02bc`\u00b4\u2018", "'"))


def _section(name: str) -> str:
    """A section name compared without case, apostrophe variants and repeated spaces."""
    return " ".join(name.translate(APOSTROPHES).split()).casefold()


TYPES_BY_PREFIX = {tuple(_section(n) for n in prefix): kind for prefix, kind in CATEGORY_TYPES.items()}


def _mapped_type(path: Sequence[str]) -> str | None:
    """Type of the longest table prefix of ``path``; ``None`` when no prefix of it is in the table."""
    key = tuple(_section(n) for n in path)
    for size in range(len(key), 0, -1):
        kind = TYPES_BY_PREFIX.get(key[:size])
        if kind is not None:
            return kind
    return None


def _entity_type(path: Sequence[str] | None) -> str:
    """Type of a product with this ``category_path`` (no path or an unknown section - ``OTHER_TYPE``)."""
    return _mapped_type(path or []) or OTHER_TYPE


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
    return success([entity(_entity_type(path), fields, cleared=cleared, completeness="full")])
