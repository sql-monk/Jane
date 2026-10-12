"""Prices and availability from yakaboo.ua category pages - the price task every 4 hours (``prices-yakaboo``).

A category (section) page lists up to 55 books as server-rendered cards ``div.category-card``: the product code
in ``id`` and in ``.product-code__category__text`` ("Код товару", the key of the catalog task too), the shown
price ``#product-price``, the old price of a discount ``#product-price-old`` and the stock status
``ui-shipment-status available | supplier | pending | not-available`` (e-books have none).

Every card becomes a ``product`` entity with only these fields and ``completeness: partial``: storage updates the
price of the book the catalog task collected and keeps its other fields (TZ §6: a missing field is not a
deletion). A card with a price and without an old price clears ``old_price`` (the discount is over); a card
without a price (out of stock) updates the availability only; without a status the availability is not sent.
``empty`` for pages without cards (a product page), ``unrecognized`` when cards are present but none has a code.

The entity type is the product group of the category page (``CATEGORY_TYPES``, the same table as the book
extractor's): the page's ``BreadcrumbList`` JSON-LD without the home page and with the page's own section is the
``category_path`` its books show on their own pages. A page whose section is not in the table (a collection such
as «Часто шукають» lists products of any group) or has subsections of different types is ``unrecognized`` and
writes nothing: the price update must not create a product in another type's collection.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from html import unescape
from typing import Any
from urllib.parse import urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import (
    Context,
    EntityOut,
    ExtractResult,
    Material,
    empty,
    entity,
    success,
    unrecognized,
)

SHOWN_STATUS = {
    "available": "in_stock",
    "supplier": "in_stock",  # "Доставка з UK N днів": orderable now, delivered from the supplier
    "pending": "preorder",  # "Очікується з DD.MM.YY"
    "not-available": "out_of_stock",
}
CARDS = '//div[contains(concat(" ", normalize-space(@class), " "), " category-card ")]'
MONEY = re.compile(r"\d+(?:[.,]\d+)?")
SPACES = re.compile(r"[\s  ]+")


# Catalog section (a prefix of ``category_path``) -> entity type, one MongoDB collection per type. The longest
# prefix in the table wins; a section that is not in the table is ``OTHER_TYPE`` (seasonal and promotional
# sections are only listed with their subsections). The card and the price extractor of the shop carry the same
# table and lookup - a price update must name the type of the card (examples/tests/test_sites.py compares them).
CATEGORY_TYPES: dict[tuple[str, ...], str] = {
    ("Ігри та творчість",): "product_kids",
    ("Книжки",): "product_book",
    ("Кольорові олівці",): "product_office",
    ("Настільні ігри",): "product_kids",
    ("Рюкзаки, сумки шкільні",): "product_office",
    ("Шкільні зошити",): "product_office",
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


def _clean(value: Any) -> str:
    return " ".join(str(value).split()) if value is not None else ""


def _ld_objects(doc: Any, ctx: Context) -> Iterator[dict[str, Any]]:
    """Top-level JSON-LD objects of the page (lists and ``@graph`` unfolded)."""
    for raw in doc.xpath('//script[@type="application/ld+json"]/text()'):
        if not str(raw).strip():
            continue
        try:
            data = json.loads(str(raw))
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict):
                graph = item.get("@graph")
                yield from (g for g in graph if isinstance(g, dict)) if isinstance(graph, list) else [item]


def _category_path(doc: Any, ctx: Context) -> list[str]:
    """Names of the ``BreadcrumbList`` items after the home page; the page's own section is the last one."""
    for obj in _ld_objects(doc, ctx):
        kind = obj.get("@type")
        if "BreadcrumbList" not in ([kind] if isinstance(kind, str) else kind or []):
            continue
        elements = [e for e in obj.get("itemListElement") or [] if isinstance(e, dict)]
        elements.sort(key=lambda e: e["position"] if isinstance(e.get("position"), int) else 0)
        path: list[str] = []
        for element in elements:
            item = element.get("item")
            target = item.get("@id") if isinstance(item, dict) else item
            name = item.get("name") if isinstance(item, dict) else element.get("name")
            text = _clean(unescape(str(name))) if isinstance(name, str) else ""
            if text and urlsplit(str(target or "")).path not in ("", "/"):  # skip the home page
                path.append(text)
        return path
    return []


def _money(card: Any, xpath: str) -> float | None:
    for el in card.xpath(xpath):
        match = MONEY.search(SPACES.sub("", str(el.text_content())))
        if match:
            return float(match.group().replace(",", "."))
    return None


def _availability(card: Any) -> str | None:
    for classes in card.xpath('.//div[contains(@class, "ui-shipment-status")]/@class'):
        for token in str(classes).split():
            if token in SHOWN_STATUS:
                return SHOWN_STATUS[token]
    return None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    text = ctx.text()
    if not text.strip():
        return empty()
    doc = lxml_html.fromstring(text)
    cards = doc.xpath(CARDS)
    if not cards:
        return empty()  # a product page or another page of the site

    priced: list[tuple[dict[str, Any], list[str]]] = []
    seen: set[str] = set()
    without_code = 0
    for card in cards:
        code = _clean(
            " ".join(
                str(t) for t in card.xpath('.//*[contains(@class, "product-code__category__text")]//text()')
            )
        )
        code = code or _clean(card.get("id"))
        if not code:
            without_code += 1
            continue
        if code in seen:
            continue
        seen.add(code)
        price = _money(card, './/span[@id="product-price"]')
        old_price = _money(card, './/span[@id="product-price-old"]')
        if old_price is not None and (price is None or old_price <= price):
            old_price = None
        availability = _availability(card)
        if price is None and availability is None:
            continue  # nothing to update
        fields = {
            "shop": params["shop"],
            "product_id": code,
            "price": price,
            "currency": params["currency"] if price is not None else None,
            "old_price": old_price,
            "availability": availability,
        }
        cleared = ["old_price"] if price is not None and old_price is None else []
        priced.append((fields, cleared))
    if without_code:
        ctx.log.warning(
            f"{without_code} card(s) without a product code skipped",
            code="extract.missing_selector",
            selector=".product-code__category__text",
        )
    if not priced:
        return unrecognized(
            "category cards without a product code or a price",
            signature="missing-selector:.product-code__category__text",
        )
    path = _category_path(doc, ctx)
    kind = _listing_type(path)
    if kind is None:
        section = " > ".join(path) or "no breadcrumbs"
        ctx.log.warning(f"category page of an unmapped section: {section}", code="extract.unmapped_category")
        return unrecognized(
            f"the product type of category page {section!r} is not known: no prices are written",
            signature=f"unmapped-category:{path[0] if path else 'none'}",
        )
    entities: list[EntityOut] = [
        entity(kind, fields, cleared=cleared, completeness="partial") for fields, cleared in priced
    ]
    return success(entities)
