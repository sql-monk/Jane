"""Full product cards of prostor.ua (Magento 2) - the nightly "collect the catalog" task.

A product page (``/ua/product/<slug>/``) carries a schema.org ``Product`` JSON-LD block (name, sku, brand,
image, offer price, list price, availability, aggregate rating), a ``BreadcrumbList`` (category path), the
add-to-cart form with the shop's product id (``form#product_addtocart_form input[name=product]``) and the
attribute table ``#product-attribute-specs-table``. The entity key is ``shop`` + ``product_id`` - the same
Magento product id the category pages show in ``li.product-item[data-id]``, so the price task updates the
same entities. Customer reviews (names of private persons) are not read.

States (TZ §9): ``success`` - a priced product card (``completeness: full``), or the known metadata of an
out-of-stock product without a price (``completeness: partial``); ``empty`` - not a product page. A missing
id or title is ``unrecognized``; an in-stock/unknown product missing its price is ``unrecognized`` with its
partial metadata. An absent price never clears the last observed price or discount in storage.

The entity type is the product group of the card's ``category_path`` (``CATEGORY_TYPES``: the longest table
prefix wins, an unknown section is ``product_other``); the price extractor of the shop uses the same table.
"""

from __future__ import annotations

import html
import json
import re
from collections.abc import Sequence
from html.parser import HTMLParser
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

AVAILABILITY = {
    "instock": "in_stock",
    "outofstock": "out_of_stock",
    "soldout": "out_of_stock",
    "discontinued": "out_of_stock",
    "preorder": "preorder",
    "presale": "preorder",
    "backorder": "preorder",
    "in stock": "in_stock",
    "out of stock": "out_of_stock",
}
VOLUME_LABELS = ("об'єм", "обʼєм", "об’єм", "вага", "маса")
AMOUNT = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*([^\d\s].*?)\s*$")
FORM_ID = "product_addtocart_form"


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


def _entity_type(path: Sequence[str] | None) -> str:
    """Type of a product with this ``category_path`` (no path or an unknown section - ``OTHER_TYPE``)."""
    return _mapped_type(path or []) or OTHER_TYPE


def _clean(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(html.unescape(value).split())
    return text or None


def _number(value: Any) -> float | None:
    try:
        number = float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


class _Card(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ld_json: list[str] = []
        self.canonical: str | None = None
        self.og_type: str | None = None
        self.meta_availability: str | None = None
        self.form_product_id: str | None = None
        self.box_product_id: str | None = None
        self.box_prices: dict[str, str] = {}
        self.h1 = ""
        self.attributes: list[tuple[str, str]] = []
        self._in_ld = False
        self._in_form = False
        self._in_h1 = False
        self._in_specs = False
        self._cell: str | None = None
        self._label = ""
        self._value = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "script":
            self._in_ld = a.get("type") == "application/ld+json"
            if self._in_ld:
                self.ld_json.append("")
        elif tag == "link" and a.get("rel") == "canonical" and self.canonical is None:
            self.canonical = a.get("href") or None
        elif tag == "meta":
            prop = a.get("property")
            if prop == "og:type":
                self.og_type = a.get("content")
            elif prop == "product:availability":
                self.meta_availability = a.get("content")
        elif tag == "form" and a.get("id") == FORM_ID:
            self._in_form = True
        elif tag == "input" and self._in_form and a.get("name") == "product" and self.form_product_id is None:
            self.form_product_id = a.get("value") or None
        elif tag == "h1":
            self._in_h1 = True
        elif tag == "table" and a.get("id") == "product-attribute-specs-table":
            self._in_specs = True
        elif self._in_specs and tag in ("th", "td"):
            self._cell = tag
            if tag == "th":
                self._label, self._value = "", ""
        if a.get("data-role") == "priceBox" and self.box_product_id is None:
            self.box_product_id = a.get("data-product-id") or None
        price_type = a.get("data-price-type")
        if price_type and a.get("data-price-amount") and price_type not in self.box_prices:
            self.box_prices[price_type] = a["data-price-amount"]

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_ld = False
        elif tag == "form":
            self._in_form = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "table" and self._in_specs:
            self._in_specs = False
        elif self._in_specs and tag == self._cell:
            self._cell = None
            if tag == "td":
                label, value = _clean(self._label), _clean(self._value)
                if label and value:
                    self.attributes.append((label, value))

    def handle_data(self, data: str) -> None:
        if self._in_ld:
            self.ld_json[-1] += data
        elif self._in_h1:
            self.h1 += data
        elif self._cell == "th":
            self._label += data
        elif self._cell == "td":
            self._value += data


def _ld_blocks(page: _Card, ctx: Context) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for raw in page.ld_json:
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for item in doc if isinstance(doc, list) else [doc]:
            if isinstance(item, dict):
                blocks.append(item)
    return blocks


def _first_of_type(blocks: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    return next((b for b in blocks if b.get("@type") == kind), None)


def _availability(value: Any) -> str | None:
    key = str(value or "").strip().rsplit("/", 1)[-1].casefold()
    return AVAILABILITY.get(key)


def _categories(breadcrumbs: dict[str, Any] | None) -> list[str]:
    """Names of the linked breadcrumb items between the home page and the product itself."""
    if not breadcrumbs:
        return []
    items = sorted(
        (e for e in breadcrumbs.get("itemListElement") or [] if isinstance(e, dict)),
        key=lambda e: int(e.get("position") or 0),
    )
    names: list[str] = []
    for element in items[1:]:  # position 1 is the home page
        item = element.get("item") or {}
        name = _clean(item.get("name") if isinstance(item, dict) else None)
        if name and isinstance(item, dict) and item.get("@id"):
            names.append(name)
    return names


def _list_price(offers: dict[str, Any]) -> float | None:
    for spec in offers.get("priceSpecification") or []:
        if isinstance(spec, dict) and str(spec.get("priceType", "")).endswith("/ListPrice"):
            return _number(spec.get("price"))
    return None


def _volume(attributes: dict[str, str]) -> tuple[float | None, str | None]:
    for label, value in attributes.items():
        if label.casefold() in VOLUME_LABELS:
            match = AMOUNT.match(value)
            if match:
                return _number(match.group(1)), match.group(2)
    return None, None


def _image(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        value = value.get("url")
    return value if isinstance(value, str) and value.startswith(("https://", "http://")) else None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = _Card()
    page.feed(ctx.text())
    page.close()
    blocks = _ld_blocks(page, ctx)
    product = _first_of_type(blocks, "Product")
    if product is None and page.og_type != "product" and page.form_product_id is None:
        return empty()

    product = product or {}
    offers = product.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    attributes = dict(page.attributes)
    category_path = _categories(_first_of_type(blocks, "BreadcrumbList"))
    price = _number(offers.get("price"))
    if price is None:
        price = _number(page.box_prices.get("finalPrice"))
    old_price = _list_price(offers)
    if old_price is None:
        old_price = _number(page.box_prices.get("oldPrice"))
    if old_price is not None and (price is None or old_price <= price):
        old_price = None
    volume, unit = _volume(attributes)
    rating = product.get("aggregateRating") or {}
    brand = product.get("brand")
    page_url = (material.get("locator") or {}).get("url")

    fields: dict[str, Any] = {
        "shop": params["shop"],
        "product_id": page.form_product_id or page.box_product_id,
        "title": _clean(product.get("name")) or _clean(page.h1),
        "price": price,
        "currency": _clean(offers.get("priceCurrency")) or params["default_currency"],
        "url": page.canonical or _clean(offers.get("url")) or page_url,
        "completeness": "full",
        "brand": _clean(brand.get("name") if isinstance(brand, dict) else brand) or attributes.get("Brand"),
        "category": category_path[-1] if category_path else None,
        "category_path": category_path or None,
        "old_price": old_price,
        "availability": _availability(offers.get("availability"))
        or _availability(page.meta_availability)
        or "unknown",
        "image": _image(product.get("image")),
        "sku": _clean(str(product["sku"])) if product.get("sku") is not None else None,
        "volume": volume,
        "unit": unit,
        "rating": _number(rating.get("ratingValue")) if isinstance(rating, dict) else None,
        "reviews_count": _count(rating.get("reviewCount") or rating.get("ratingCount"))
        if isinstance(rating, dict)
        else None,
        "attributes": attributes or None,
    }
    cleared = ["old_price"] if old_price is None and price is not None else None
    if not fields["product_id"]:
        ctx.log.warning(
            "product id not found",
            code="extract.missing_selector",
            selector=f"#{FORM_ID} input[name=product]",
        )
        return unrecognized(
            "product page without the shop's product id",
            signature=f"missing-selector:#{FORM_ID} input[name=product]",
        )
    if not fields["title"]:
        return unrecognized("product page without a title", signature="missing-field:title")
    if price is None:
        fields["completeness"] = "partial"
        fields.pop("currency")
        partial = entity(_entity_type(category_path), fields, completeness="partial")
        if fields["availability"] == "out_of_stock":
            return success([partial])
        ctx.log.warning("price not found", code="extract.missing_selector", selector="offers.price")
        return unrecognized(
            "product page without a price",
            signature="missing-field:offers.price",
            entities=[partial],
        )
    kind = _entity_type(category_path)
    return success([entity(kind, fields, cleared=cleared, completeness="full")])


def _count(value: Any) -> int | None:
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None
    return count if count >= 0 else None
