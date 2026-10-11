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
"""

from __future__ import annotations

import re
from typing import Any

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


def _clean(value: Any) -> str:
    return " ".join(str(value).split()) if value is not None else ""


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
    cards = lxml_html.fromstring(text).xpath(CARDS)
    if not cards:
        return empty()  # a product page or another page of the site

    entities: list[EntityOut] = []
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
        entities.append(entity("product", fields, cleared=cleared, completeness="partial"))
    if without_code:
        ctx.log.warning(
            f"{without_code} card(s) without a product code skipped",
            code="extract.missing_selector",
            selector=".product-code__category__text",
        )
    if not entities:
        return unrecognized(
            "category cards without a product code or a price",
            signature="missing-selector:.product-code__category__text",
        )
    return success(entities)
