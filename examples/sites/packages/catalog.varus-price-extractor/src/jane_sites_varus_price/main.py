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

The entity type is the product group of the item's own categories (``primaryCategory`` and ``categories``, which
the short query of ``catalog.varus-prices-rules`` 2.x requests for this purpose): the same ``category_path`` and
the same table (``CATEGORY_TYPES``) as the card extractor, so the price update names the card's type. An item
without categories (an older short query) is ``unrecognized`` and writes nothing instead of guessing a type.

States (TZ §9): ``success`` - a product item; ``empty`` - JSON that is not a product item (an API error document);
``unrecognized`` - a product item without a SKU, without ``regionalPriceInfo`` or without categories, or in stock
without a price.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SPACES = re.compile(r"\s+")

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

    path = _category_path(item)
    if not path:
        ctx.log.warning(
            "product item without categories", code="extract.missing_field", selector="primaryCategory"
        )
        return unrecognized(
            "product item without categories: the product type is not known, no price is written",
            signature="missing-field:primaryCategory",
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
    return success([entity(_entity_type(path), fields, cleared=cleared, completeness="partial")])
