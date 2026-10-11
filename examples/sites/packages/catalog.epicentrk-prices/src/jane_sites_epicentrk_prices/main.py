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

A page without product tiles is ``empty``; tiles without product links are ``unrecognized``.
"""

from __future__ import annotations

import math
import re
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SLUG = re.compile(r"/(?:[a-z]{2}/)?shop/([^/]+)\.html")
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


def _text(value: str | None) -> str:
    return " ".join((value or "").split())


def _number(value: str | None) -> float | None:
    raw = (value or "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        number = float(raw)
    except ValueError:
        return None
    return number if math.isfinite(number) and number >= 0 else None


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
    skipped = len(cards) - len(found)
    if skipped:
        ctx.log.info(f"{skipped} tile(s) without a product link or repeated", code="extract.skipped_tiles")
    return success(
        [
            entity("product", fields, cleared=cleared, completeness="partial")
            for fields, cleared in found.values()
        ]
    )
