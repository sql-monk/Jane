"""Product offers from ``product-card`` elements of shop category pages (data attributes).

Foxtrot and Moyo render each product of a category page as ``<div class="product-card" data-price=...>`` with
the product data in attributes (Foxtrot: ``data-code``, ``data-title``, ``data-brand``, ``data-variant``;
Moyo: ``data-product_id``, ``data-name``, ``data-brand``, ``data-status-product``, ``data-img`` and the
product URL base64-encoded in ``data-async``); without a URL attribute the first ``.html`` link inside the card
is the product page. Every card with an id, a title, a price and a URL becomes an entity - the same entity
types and schema as ``shops.jsonld-offers``, keyed by the shop and the shop's product id.

The entity type is the required stage parameter ``entity_type`` - a ``product_*`` type of the taxonomy that
the task chooses for the one category it collects (laptops: ``product_electronics``); the extractor does not
guess it from the page.
"""

from __future__ import annotations

import base64
import binascii
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

ID_ATTRS = ("data-code", "data-product_id", "data-product-id", "data-sku", "data-id")
TITLE_ATTRS = ("data-title", "data-name")
AVAILABILITY = {
    "instock": "in_stock",
    "в наличии": "in_stock",
    "в наявності": "in_stock",
    "outofstock": "out_of_stock",
    "нет в наличии": "out_of_stock",
    "немає в наявності": "out_of_stock",
    "закінчився": "out_of_stock",
    "preorder": "preorder",
    "передзамовлення": "preorder",
}


class _Cards(HTMLParser):
    def __init__(self, card_class: str) -> None:
        super().__init__(convert_charrefs=True)
        self.card_class = card_class
        self.cards: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "div" and self.card_class in a.get("class", "").split() and a.get("data-price"):
            self.cards.append(a)
        elif tag == "a" and self.cards and "href" not in self.cards[-1]:
            href = a.get("href", "")
            if urlsplit(href).path.endswith(".html"):
                self.cards[-1]["href"] = href


def _first(card: dict[str, str], names: tuple[str, ...]) -> str | None:
    return next((card[n].strip() for n in names if card.get(n, "").strip()), None)


def _url(card: dict[str, str], page_url: str) -> str | None:
    encoded = card.get("data-async", "")
    if encoded:
        try:
            decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            decoded = ""
        if decoded.startswith(("https://", "http://")):
            return decoded
    href = card.get("href")
    if href and page_url:
        absolute = urljoin(page_url, href)
        return absolute if absolute.startswith(("https://", "http://")) else None
    return None


def _availability(card: dict[str, str]) -> str:
    raw = _first(card, ("data-variant", "data-status-product", "data-availability")) or ""
    return AVAILABILITY.get(raw.casefold(), "unknown")


def _entity_type(params: dict[str, Any]) -> str:
    """The ``product_*`` type of the stage; the runtime checks it against the params schema (enum)."""
    value = params.get("entity_type")
    if not isinstance(value, str) or not value.startswith("product_"):
        raise ValueError(f"params.entity_type must be a product_* type, got {value!r}")
    return value


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    entity_type = _entity_type(params)
    page = _Cards(str(params.get("card_class") or "product-card"))
    page.feed(ctx.text())
    page_url = str((material.get("locator") or {}).get("url") or "")
    shop = (urlsplit(page_url).hostname or "").lower().removeprefix("www.")
    currency = str(params.get("currency") or "UAH")
    found: dict[str, dict[str, Any]] = {}
    for card in page.cards:
        product_id, title, url = _first(card, ID_ATTRS), _first(card, TITLE_ATTRS), _url(card, page_url)
        try:
            amount = float(card["data-price"].replace(" ", "").replace(",", "."))
        except ValueError:
            continue
        if not (product_id and title and url and shop) or amount < 0:
            continue
        fields: dict[str, Any] = {
            "shop": shop,
            "product_id": product_id,
            "title": title,
            "url": url,
            "price": {"amount": amount, "currency": currency},
            "availability": _availability(card),
        }
        if brand := _first(card, ("data-brand",)):
            fields["brand"] = brand
        image = card.get("data-img", "")
        if image.startswith(("https://", "http://")):
            fields["image"] = image
        found.setdefault(product_id, fields)
    if not found:
        return empty()
    return success([entity(entity_type, fields) for fields in found.values()])
