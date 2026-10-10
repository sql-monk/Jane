"""Product offers from the schema.org JSON-LD of shop category pages.

One package for several shops. Rozetka and Citrus put an ``ItemList`` of ``Product`` items with an ``Offer``
on a category page; Allo puts a collection ``Product`` whose ``offers`` list holds one ``Offer`` per product.
Every product with a URL and a price becomes an ``offer`` entity keyed by the shop and the shop's product id
(``sku``, else the numeric id in the product URL, else the URL). A page without such JSON-LD is ``empty``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

AVAILABILITY = {
    "InStock": "in_stock",
    "InStoreOnly": "in_stock",
    "OnlineOnly": "in_stock",
    "LimitedAvailability": "in_stock",
    "OutOfStock": "out_of_stock",
    "SoldOut": "out_of_stock",
    "Discontinued": "out_of_stock",
    "PreOrder": "preorder",
    "PreSale": "preorder",
    "BackOrder": "preorder",
}
# /p621368348/ (Rozetka), ...-790214.html (Citrus)
_ID_IN_URL = re.compile(r"/p(\d+)/?$|-(\d+)\.html$")
_DECORATION = re.compile(r"^[^\w(\[«\"]+")


class _LdJson(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self._in_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._in_ld = True
            self.blocks.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_ld:
            self.blocks[-1] += data


def _types(node: dict[str, Any]) -> set[str]:
    t = node.get("@type")
    if isinstance(t, str):
        return {t}
    return {x for x in t if isinstance(x, str)} if isinstance(t, list) else set()


def _walk(node: Any) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _pairs(doc: Any) -> Iterator[tuple[dict[str, Any], dict[str, Any]]]:
    """(product-like node, its offer) for every priced product in a JSON-LD document."""
    for node in _walk(doc):
        if "Product" not in _types(node):
            continue
        offers = node.get("offers")
        if isinstance(offers, dict) and node.get("url"):
            yield node, offers
        elif isinstance(offers, list):  # a collection: each offer carries its own url and name
            for offer in offers:
                if isinstance(offer, dict) and offer.get("url"):
                    yield offer, offer


def _text(value: Any) -> str | None:
    """A name without leading decoration (Citrus prefixes titles with a check mark)."""
    if isinstance(value, dict):
        value = value.get("name")
    text = _DECORATION.sub("", value).strip() if isinstance(value, str) else ""
    return text or None


def _image(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    return value if isinstance(value, str) and value.startswith(("https://", "http://")) else None


def _amount(value: Any) -> float | None:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount if amount >= 0 else None


def _product_id(item: dict[str, Any], offer: dict[str, Any], url: str) -> str:
    sku = offer.get("sku") or item.get("sku")
    if sku not in (None, ""):
        return str(sku)
    m = _ID_IN_URL.search(urlsplit(url).path)
    return next((g for g in m.groups() if g), url) if m else url


def _shop(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    return host.removeprefix("www.")


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = _LdJson()
    page.feed(ctx.text())
    page_url = str((material.get("locator") or {}).get("url") or "")
    default_currency = str(params.get("default_currency") or "UAH")
    found: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in page.blocks:
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for item, offer in _pairs(doc):
            url = str(item.get("url") or "")
            amount = _amount(offer.get("price"))
            title = _text(item.get("name"))
            if not url.startswith(("https://", "http://")) or amount is None or title is None:
                continue
            fields: dict[str, Any] = {
                "shop": _shop(page_url or url),
                "product_id": _product_id(item, offer, url),
                "title": title,
                "url": url,
                "price": {"amount": amount, "currency": str(offer.get("priceCurrency") or default_currency)},
                "availability": AVAILABILITY.get(
                    str(offer.get("availability") or "").rsplit("/", 1)[-1], "unknown"
                ),
            }
            if brand := _text(item.get("brand")):
                fields["brand"] = brand
            if image := _image(item.get("image")):
                fields["image"] = image
            found.setdefault((fields["shop"], fields["product_id"]), fields)
    if not found:
        return empty()
    return success([entity("offer", fields) for fields in found.values()])
