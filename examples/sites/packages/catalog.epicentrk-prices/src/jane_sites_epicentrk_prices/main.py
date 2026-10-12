"""Prices and availability of epicentrk.ua products from a category page - the frequent price update.

Every product tile of a category page (``li[data-test-small-card]``, up to 60 per page) becomes a partial
``product`` entity (``completeness: partial``) with ``shop``, ``product_id``, ``price``, ``currency``,
``old_price`` and ``availability`` only: storage updates these fields of the full card collected by
``catalog.epicentrk-products`` and keeps the rest (a missing field is not a deletion). The key is the same:
``shop`` + ``product_id`` = the slug of the product link (``/ua/shop/<slug>.html``).

The tiles are read through stable ``data-*`` attributes and schema.org microdata, not the hashed CSS classes:
the link ``a[data-product-picture]``, the price ``[data-product-price-main]`` and the struck-through price
``[data-product-price-old]`` (``data@value``), ``itemprop=availability`` or the status text of the tile
(«Немає в наявності» …). An out-of-stock tile has no price: only ``availability`` is sent and the last known
price stays. A tile with a price and no struck-through price clears ``old_price``.

The entity type is the product group of the category page (``CATEGORY_TYPES``, the same table as the card
extractor's): the breadcrumbs of the page (``itemprop=breadcrumb``, without the home, catalog and brand-filter
crumbs, emoji removed) are the ``category_path`` its products show on their own pages. A page whose section is
not in the table, or has subsections of different types, is ``unrecognized`` and writes nothing: the price
update must not create a product in another type's collection.

A page without product tiles is ``empty``; tiles without product links are ``unrecognized``.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Sequence
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SLUG = re.compile(r"/(?:[a-z]{2}/)?shop/([^/]+)\.html")
NAVIGATION_PATHS = frozenset({"/", "/ua/", "/shop/", "/ua/shop/"})
CURRENCY = re.compile(r"[A-Z]{3}")
SCHEMA_AVAILABILITY = {
    "instock": "in_stock",
    "limitedavailability": "in_stock",
    "onlineonly": "in_stock",
    "outofstock": "out_of_stock",
    "soldout": "out_of_stock",
    "discontinued": "out_of_stock",
    "preorder": "preorder",
    "presale": "preorder",
    "backorder": "preorder",
}
TEXT_AVAILABILITY = {
    "в наявності": "in_stock",
    "готовий до відправки": "in_stock",
    "закінчується": "in_stock",
    "немає в наявності": "out_of_stock",
    "закінчився": "out_of_stock",
    "передзамовлення": "preorder",
    "під замовлення": "preorder",
}


# Catalog section (a prefix of ``category_path``) -> entity type, one MongoDB collection per type. The longest
# prefix in the table wins; a section that is not in the table is ``OTHER_TYPE`` (seasonal and promotional
# sections are only listed with their subsections). The card and the price extractor of the shop carry the same
# table and lookup - a price update must name the type of the card (examples/tests/test_sites.py compares them).
CATEGORY_TYPES: dict[tuple[str, ...], str] = {
    ("Автотовари",): "product_auto",
    ("Будівництво та ремонт",): "product_tools",
    ("Дитячі товари",): "product_kids",
    ("Дім та інтер'єр",): "product_home",
    ("Дім та інтер'єр", "Книги"): "product_book",
    ("Електроніка",): "product_electronics",
    ("Зоотовари",): "product_pet",
    ("Інструменти",): "product_tools",
    ("Краса та здоров'я",): "product_beauty",
    ("Меблі",): "product_home",
    ("Медичні товари",): "product_health",
    ("Одяг, взуття, аксесуари",): "product_clothing",
    ("Освітлення",): "product_tools",
    ("Офіс і канцтовари",): "product_office",
    ("Побутова техніка",): "product_appliance",
    ("Побутова хімія",): "product_household",
    ("Покриття для підлоги",): "product_tools",
    ("Продукти",): "product_food",
    ("Сад та город",): "product_garden",
    ("Сантехніка",): "product_tools",
    ("Спорттовари",): "product_sport",
    ("Туристичні товари",): "product_sport",
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


def _text(value: str | None) -> str:
    return " ".join((value or "").split())


def _number(value: str | None) -> float | None:
    raw = (value or "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        number = float(raw)
    except ValueError:
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _plain(value: str | None) -> str:
    """Text without pictographs (category names carry decorative emoji)."""
    kept = "".join(
        ch
        for ch in value or ""
        if unicodedata.category(ch) not in {"So", "Cs", "Co", "Cf"} and not 0xFE00 <= ord(ch) <= 0xFE0F
    )
    return _text(kept)


def _category_path(doc: Any) -> list[str]:
    """Breadcrumbs of the category page without the home, catalog and brand-filter crumbs; the last crumb (the
    category itself, without a link) is kept."""
    path: list[str] = []
    for item in doc.xpath('//*[@itemprop="breadcrumb"]//li'):
        href = next(iter(item.xpath("./a/@href")), None)
        link = urlsplit(str(href)).path if href else None
        if link is not None and (link in NAVIGATION_PATHS or "/fs/" in link or "/filter/" in link):
            continue
        name = _plain(item.get("data-breadcrumb") or item.text_content())
        if name:
            path.append(name)
    return path


def _slug(url: str) -> str | None:
    match = SLUG.fullmatch(urlsplit(url).path)
    return match.group(1) if match else None


def _block_price(block: Any) -> float | None:
    """``data@value`` of a price block: the ``itemprop=price`` one, else the first numeric one."""
    for data in block.xpath('.//data[@itemprop="price"]') + block.xpath(".//data[@value]"):
        number = _number(data.get("value") or data.get("content"))
        if number is not None:
            return number
    return None


def _availability(card: Any, has_price: bool) -> str:
    for value in card.xpath('.//*[@itemprop="availability"]/@content | .//*[@itemprop="availability"]/@href'):
        mapped = SCHEMA_AVAILABILITY.get(str(value).rstrip("/").rsplit("/", 1)[-1].casefold())
        if mapped:
            return mapped
    for value in card.itertext():
        mapped = TEXT_AVAILABILITY.get(_text(value).casefold())
        if mapped:
            return mapped
    if has_price and card.xpath('.//button[@data-testid="small-cart-item-buy-button"]'):
        return "in_stock"
    return "unknown"


def _tile(card: Any, page_url: str, params: dict[str, Any]) -> tuple[dict[str, Any], list[str]] | None:
    href = next(
        iter(card.xpath(".//a[@data-product-picture]/@href | .//*[@data-product-card-name]//a/@href")), None
    )
    product_id = _slug(urljoin(page_url, str(href))) if href else None
    if not product_id:
        return None
    main = next(iter(card.xpath(".//*[@data-product-price-main]")), None)
    old = next(iter(card.xpath(".//*[@data-product-price-old]")), None)
    price = _block_price(main) if main is not None else None
    old_price = _block_price(old) if old is not None else None
    if price is None or old_price is None or old_price <= price:
        old_price = None
    currency = None
    if main is not None:
        currency = next(
            (str(c) for c in main.xpath('.//*[@itemprop="priceCurrency"]/@content') if CURRENCY.fullmatch(c)),
            str(params["currency"]),
        )
    fields = {
        "shop": str(params["shop"]),
        "product_id": product_id,
        "price": price,
        "currency": currency if price is not None else None,
        "old_price": old_price,
        "availability": _availability(card, price is not None),
    }
    return fields, (["old_price"] if price is not None and old_price is None else [])


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    doc = lxml_html.document_fromstring(ctx.text())
    cards = doc.xpath("//li[@data-test-small-card]")
    if not cards:
        return empty()
    page_url = str((material.get("locator") or {}).get("url") or "")
    found: dict[str, tuple[dict[str, Any], list[str]]] = {}
    for card in cards:
        tile = _tile(card, page_url, params)
        if tile is not None:
            found.setdefault(tile[0]["product_id"], tile)
    if not found:
        ctx.log.warning(
            "product tiles without links", code="extract.missing_selector", selector="a[data-product-picture]"
        )
        return unrecognized(
            "product tiles without product links", signature="missing-selector:a[data-product-picture]"
        )
    path = _category_path(doc)
    kind = _listing_type(path)
    if kind is None:
        section = " > ".join(path) or "no breadcrumbs"
        ctx.log.warning(f"category page of an unmapped section: {section}", code="extract.unmapped_category")
        return unrecognized(
            f"the product type of category page {section!r} is not known: no prices are written",
            signature=f"unmapped-category:{path[0] if path else 'none'}",
        )
    skipped = len(cards) - len(found)
    if skipped:
        ctx.log.info(f"{skipped} tile(s) without a product link or repeated", code="extract.skipped_tiles")
    return success(
        [entity(kind, fields, cleared=cleared, completeness="partial") for fields, cleared in found.values()]
    )
