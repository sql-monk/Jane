"""Prices and availability of prostor.ua products from category pages - the "update prices" task.

Every product tile of a category page (``ol.product-items > li.product-item``) has the Magento product id
(``data-id``, also ``data-product-id`` of its price box), the current price (``[data-price-type=finalPrice]
[data-price-amount]``), the price before a discount (``[data-price-type=oldPrice]``) and the stock flag of the
wish-list button (``data-post`` JSON ``data.is_in_stock``). Each tile becomes a partial ``product`` entity
(``completeness: partial``) with only ``shop``, ``product_id``, ``price``, ``currency``, ``availability`` and
``old_price`` - the key fields of the full card of ``catalog.prostor-product-extractor``, so storage updates
these fields of the same entity and keeps the rest (TZ §6: a missing field is not a deletion). A tile without a
discount clears ``old_price`` explicitly (``cleared``), so an ended discount does not linger.

An out-of-stock tile without a price updates availability only and preserves the last observed price and
discount. States (TZ §9): ``success`` - a category with priced or known out-of-stock tiles; ``empty`` - no
product tiles; ``unrecognized`` - tiles without prices or a known out-of-stock status (the markup changed), or
a section of an unknown type.

The entity type is the product group of the category page (``CATEGORY_TYPES``, the same table as the card
extractor's): the page's ``BreadcrumbList`` JSON-LD without the home page and with the page's own category is
the ``category_path`` its products show on their own pages. A page whose section is not in the table (seasonal
and gift sections list products of any group), has subsections of different types or has no breadcrumbs is
``unrecognized`` and writes nothing: the price update must not create a product in another type's collection.
"""

from __future__ import annotations

import html
import json
from collections.abc import Sequence
from html.parser import HTMLParser
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

# Catalog section (a prefix of ``category_path``) -> entity type, one MongoDB collection per type. The longest
# prefix in the table wins; a section that is not in the table is ``OTHER_TYPE`` (seasonal and promotional
# sections are only listed with their subsections). The card and the price extractor of the shop carry the same
# table and lookup - a price update must name the type of the card (examples/tests/test_sites.py compares them).
CATEGORY_TYPES: dict[tuple[str, ...], str] = {
    ("Великдень", "Кондитерський декор"): "product_food",
    ("Волосся",): "product_beauty",
    ("Галантерея",): "product_clothing",
    ("Дім",): "product_home",
    ("Дім", "Зоотовари"): "product_pet",
    ("Дім", "Продукти"): "product_food",
    ("Дім", "Спортивні товари"): "product_sport",
    ("Дітям",): "product_kids",
    ("Здоров`я",): "product_health",
    ("Косметика",): "product_beauty",
    ("Обличчя",): "product_beauty",
    ("Парфуми",): "product_beauty",
    ("Побутова хімія",): "product_household",
    ("Продукти",): "product_food",
    ("Святий Миколай", "Дитяча косметика"): "product_beauty",
    ("Тіло",): "product_beauty",
    ("Чоловікам", "Спідня білизна"): "product_clothing",
    ("Чоловікам", "Чоловічі засоби для стайлінгу"): "product_beauty",
    ("Чоловікам", "Чоловічі шкарпетки"): "product_clothing",
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


def _listing_type(path: Sequence[str]) -> str | None:
    """Type of the products of a category page with this ``path``: the table type when no deeper section of the
    table under the page has another type. ``None`` - it cannot be told: no table prefix (a seasonal, promotional
    or new section may list products of any section) or subsections of the page have different types."""
    kind = _mapped_type(path)
    key = tuple(_section(n) for n in path)
    deeper = {
        t for prefix, t in TYPES_BY_PREFIX.items() if len(prefix) > len(key) and prefix[: len(key)] == key
    }
    return kind if kind is not None and deeper <= {kind} else None


def _number(value: Any) -> float | None:
    try:
        number = float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


class _Tiles(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tiles: list[dict[str, Any]] = []
        self.ld_json: list[str] = []
        self._in_ld = False
        self._list_depth = 0  # nesting of <ol> inside the product list; 0 - outside it

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        classes = a.get("class", "").split()
        if tag == "script":
            self._in_ld = a.get("type") == "application/ld+json"
            if self._in_ld:
                self.ld_json.append("")
            return
        if tag == "ol":
            if self._list_depth:
                self._list_depth += 1
            elif "product-items" in classes:
                self._list_depth = 1
            return
        if not self._list_depth:
            return
        if tag == "li" and "product-item" in classes:
            self.tiles.append({"id": a.get("data-id") or None})
            return
        if not self.tiles:
            return
        tile = self.tiles[-1]
        if a.get("data-role") == "priceBox" and a.get("data-product-id"):
            tile.setdefault("box_id", a["data-product-id"])
        price_type = a.get("data-price-type")
        if price_type in ("finalPrice", "oldPrice") and a.get("data-price-amount"):
            tile.setdefault(price_type, a["data-price-amount"])
        if a.get("data-action") == "add-to-wishlist" and a.get("data-post"):
            try:
                post = json.loads(a["data-post"])
            except ValueError:
                post = {}
            stock = (post.get("data") or {}).get("is_in_stock") if isinstance(post, dict) else None
            if stock is not None:
                tile.setdefault("in_stock", str(stock))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_ld = False
        elif tag == "ol" and self._list_depth:
            self._list_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_ld:
            self.ld_json[-1] += data


def _category_path(page: _Tiles, ctx: Context) -> list[str]:
    """Names of the ``BreadcrumbList`` items after the home page, the page's own category (no link) included."""
    for raw in page.ld_json:
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for block in doc if isinstance(doc, list) else [doc]:
            if not isinstance(block, dict) or block.get("@type") != "BreadcrumbList":
                continue
            items = sorted(
                (e for e in block.get("itemListElement") or [] if isinstance(e, dict)),
                key=lambda e: int(e.get("position") or 0),
            )
            names = []
            for element in items[1:]:  # position 1 is the home page
                item = element.get("item")
                name = item.get("name") if isinstance(item, dict) else element.get("name")
                if isinstance(name, str) and name.strip():
                    names.append(" ".join(html.unescape(name).split()))
            return names
    return []


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = _Tiles()
    page.feed(ctx.text())
    page.close()
    if not page.tiles:
        return empty()

    path = _category_path(page, ctx)
    kind = _listing_type(path)
    found: list[tuple[dict[str, Any], list[str] | None]] = []
    seen: set[str] = set()
    unpriced = 0
    for tile in page.tiles:
        product_id = tile.get("box_id") or tile.get("id")
        price = _number(tile.get("finalPrice"))
        stock = tile.get("in_stock")
        availability = {"1": "in_stock", "0": "out_of_stock"}.get(stock) if stock is not None else None
        if not product_id or (price is None and availability != "out_of_stock"):
            unpriced += 1
            continue
        if product_id in seen:
            continue
        seen.add(product_id)
        if price is None:
            found.append(
                ({"shop": params["shop"], "product_id": product_id, "availability": availability}, None)
            )
            continue
        old_price = _number(tile.get("oldPrice"))
        if old_price is not None and old_price <= price:
            old_price = None
        fields = {
            "shop": params["shop"],
            "product_id": product_id,
            "price": price,
            "currency": params["default_currency"],
            "availability": availability,
            "old_price": old_price,
        }
        cleared = ["old_price"] if old_price is None else None
        found.append((fields, cleared))
    if unpriced:
        ctx.log.warning(
            f"{unpriced} product tile(s) without an id or a price skipped",
            code="extract.missing_selector",
            selector="[data-price-type=finalPrice]",
        )
    if not found:
        return unrecognized(
            "category page with product tiles but without prices",
            signature="missing-selector:[data-price-type=finalPrice]",
        )
    if kind is None:
        section = " > ".join(path) or "no breadcrumbs"
        ctx.log.warning(f"category page of an unmapped section: {section}", code="extract.unmapped_category")
        return unrecognized(
            f"the product type of category page {section!r} is not known: no prices are written",
            signature=f"unmapped-category:{path[0] if path else 'none'}",
        )
    return success([entity(kind, f, cleared=c, completeness="partial") for f, c in found])
