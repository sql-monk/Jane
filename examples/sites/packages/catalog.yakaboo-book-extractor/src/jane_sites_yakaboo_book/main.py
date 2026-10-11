"""Full book cards of yakaboo.ua product pages - the nightly "full catalog" task (``catalog-yakaboo``).

A product page is rendered on the server:

* the schema.org ``Product`` JSON-LD block - product code (``sku``), title, price, currency, schema.org
  availability, image and rating (``aggregateRating``);
* the ``BreadcrumbList`` JSON-LD block - the category path (without the home page and the book itself);
* the "Характеристики" table (``div.product-chars div.char``: ``char__title`` / ``char__value``) - author,
  publisher, pages, year, language, cover, ISBN, format...; the "Код" row is the product code and is skipped;
* the price block of the page (``div.base-product__price``) - the old price of a discount
  (``#product-price-old``) and the stock status shown to the buyer (``div.base-product__status``,
  ``ui-shipment-status available | supplier | pending | not-available``). The shown status wins over the
  schema.org one (a book that is expected later is ``InStock`` in JSON-LD but ``pending`` on the page).

Key: ``shop`` + ``product_id`` - the shop's product code ("Код товару"), the same code the category cards of
the price task (``catalog.yakaboo-price-extractor``) show. The card is ``completeness: full`` (also the field
``completeness``: storage keeps fields, not record flags, so it tells a catalog card from a price-only entity);
without a discount ``old_price`` is cleared (the discount is over). A page without a ``Product`` block is
``empty`` (category and other pages); a ``Product`` block without a code or a title is ``unrecognized``;
without a price - ``unrecognized`` with the partial card. Reviews (``Review`` JSON-LD, buyers' names) are not read.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from html import unescape
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SHOWN_STATUS = {
    "available": "in_stock",
    "supplier": "in_stock",  # "Доставка з UK N днів": orderable now, delivered from the supplier
    "pending": "preorder",  # "Очікується з DD.MM.YY"
    "not-available": "out_of_stock",
}
SCHEMA_AVAILABILITY = {
    "instock": "in_stock",
    "onlineonly": "in_stock",
    "limitedavailability": "in_stock",
    "instoreonly": "in_stock",
    "outofstock": "out_of_stock",
    "soldout": "out_of_stock",
    "discontinued": "out_of_stock",
    "preorder": "preorder",
    "presale": "preorder",
    "backorder": "preorder",
}
PUBLISHER = "Видавництво"
ISBN = "ISBN"
SKIPPED_ATTRIBUTES = frozenset({"Код"})  # the product code: it is the key (product_id) and sku
MONEY = re.compile(r"\d+(?:[.,]\d+)?")
ISBN_TOKEN = re.compile(r"[0-9][0-9-]{8,16}[0-9Xx]")
SPACES = re.compile(r"[\s  ]+")

PRICE_BLOCK = '//div[contains(concat(" ", normalize-space(@class), " "), " base-product__price ")]'
STATUS_BLOCK = '//div[contains(concat(" ", normalize-space(@class), " "), " base-product__status ")]'
CHAR_ROWS = (
    '//div[contains(concat(" ", normalize-space(@class), " "), " product-chars ")]'
    '//div[contains(concat(" ", normalize-space(@class), " "), " char ")]'
)


def _clean(value: Any) -> str:
    return " ".join(str(value).split()) if value is not None else ""


def _ld_text(value: Any) -> str | None:
    """A JSON-LD string (the site escapes HTML entities in it: ``Зв&#x27;язки``)."""
    if isinstance(value, bool) or value is None:
        return None
    text = _clean(unescape(str(value)))
    return text or None


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return float(value) if value >= 0 else None
    match = MONEY.search(SPACES.sub("", str(value)))
    return float(match.group().replace(",", ".")) if match else None


def _types(obj: Mapping[str, Any]) -> set[str]:
    kind = obj.get("@type")
    if isinstance(kind, str):
        return {kind}
    return {str(k) for k in kind} if isinstance(kind, list) else set()


def _ld_objects(doc: Any, ctx: Context) -> list[dict[str, Any]]:
    """Top-level JSON-LD objects of the page (lists and ``@graph`` unfolded, nested objects not)."""
    out: list[dict[str, Any]] = []
    for raw in doc.xpath('//script[@type="application/ld+json"]/text()'):
        if not str(raw).strip():
            continue
        try:
            data = json.loads(str(raw))
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for item in data if isinstance(data, list) else [data]:
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            if isinstance(graph, list):
                out.extend(g for g in graph if isinstance(g, dict))
            else:
                out.append(item)
    return out


def _first_text(doc: Any, xpath: str) -> str | None:
    for el in doc.xpath(xpath):
        text = _clean(el.text_content())
        if text:
            return text
    return None


def _characteristics(doc: Any) -> dict[str, str]:
    """``char__title`` -> ``char__value`` of the "Характеристики" table; several values joined with ", "."""
    out: dict[str, str] = {}
    for row in doc.xpath(CHAR_ROWS):
        title = _clean(" ".join(str(t) for t in row.xpath('.//div[contains(@class, "char__title")]//text()')))
        cells = row.xpath('.//div[contains(@class, "char__value")]')
        if not title or not cells or title in out:
            continue
        values = [_clean(v) for v in cells[0].xpath(".//*[@value]/@value")]
        values = [v for v in dict.fromkeys(values) if v]
        if not values:  # "Формат": plain text and a "Порівняти розмір" button
            text = _clean(
                " ".join(
                    str(t) for t in cells[0].xpath('.//text()[not(ancestor::*[contains(@class, "compare")])]')
                )
            )
            values = [text] if text else []
        if values:
            out[title] = ", ".join(values)
    return out


def _category_path(objects: Iterable[Mapping[str, Any]], page_path: str) -> list[str]:
    crumbs = next((o for o in objects if "BreadcrumbList" in _types(o)), None)
    if crumbs is None:
        return []
    elements = [e for e in crumbs.get("itemListElement") or [] if isinstance(e, dict)]
    elements.sort(key=lambda e: e["position"] if isinstance(e.get("position"), int) else 0)
    path: list[str] = []
    for element in elements:
        item = element.get("item")
        target = item.get("@id") if isinstance(item, dict) else item
        name = _ld_text(item.get("name") if isinstance(item, dict) else element.get("name"))
        target_path = urlsplit(str(target)).path if isinstance(target, str) else ""
        if not name or target_path in ("", "/") or target_path == page_path:  # home page, the book itself
            continue
        path.append(name)
    return path


def _availability(doc: Any, offers: Mapping[str, Any]) -> str:
    for classes in doc.xpath(f'{STATUS_BLOCK}//div[contains(@class, "ui-shipment-status")]/@class'):
        for token in str(classes).split():
            if token in SHOWN_STATUS:
                return SHOWN_STATUS[token]
    schema = str(offers.get("availability") or "").strip().rsplit("/", 1)[-1].lower()
    return SCHEMA_AVAILABILITY.get(schema, "unknown")


def _image(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        value = value.get("url") or value.get("contentUrl")
    text = _ld_text(value)
    return text if text and text.startswith(("http://", "https://")) else None


def _barcode(isbn: str | None) -> str | None:
    """The first ISBN of the "ISBN" row without hyphens (ISBN-13 is the EAN-13 barcode of the book)."""
    match = ISBN_TOKEN.search(isbn or "")
    if not match:
        return None
    digits = match.group().replace("-", "").upper()
    return digits if len(digits) in (10, 13) else None


def _rating(product: Mapping[str, Any]) -> tuple[float | None, int | None]:
    aggregate = product.get("aggregateRating")
    if not isinstance(aggregate, dict):
        return None, None
    count = _number(aggregate.get("reviewCount") or aggregate.get("ratingCount"))
    value = _number(aggregate.get("ratingValue"))
    if not count or value is None or value > 5:
        return None, None
    return value, int(count)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    text = ctx.text()
    if not text.strip():
        return empty()
    doc = lxml_html.fromstring(text)
    objects = _ld_objects(doc, ctx)
    product = next((o for o in objects if "Product" in _types(o)), None)
    if product is None:
        return empty()  # a category page or another page of the site

    page_url = str((material.get("locator") or {}).get("url") or "")
    canonical = next((str(h) for h in doc.xpath('//link[@rel="canonical"]/@href') if str(h).strip()), None)
    url = urljoin(page_url, canonical.strip()) if canonical else page_url
    raw_offers = product.get("offers")
    if isinstance(raw_offers, list):
        raw_offers = raw_offers[0] if raw_offers else None
    offers: dict[str, Any] = raw_offers if isinstance(raw_offers, dict) else {}

    code = _ld_text(product.get("sku") or offers.get("sku"))
    title = _ld_text(product.get("name"))
    price = _number(offers.get("price"))
    if price is None:
        price = _number(_first_text(doc, f'{PRICE_BLOCK}//span[@id="product-price"]'))
    old_price = _number(_first_text(doc, f'{PRICE_BLOCK}//span[@id="product-price-old"]'))
    if old_price is not None and (price is None or old_price <= price):
        old_price = None
    attributes = {k: v for k, v in _characteristics(doc).items() if k not in SKIPPED_ATTRIBUTES}
    category_path = _category_path(objects, urlsplit(url).path)
    rating, reviews_count = _rating(product)

    fields: dict[str, Any] = {
        "shop": params["shop"],
        "product_id": code,
        "title": title,
        "price": price,
        "currency": _ld_text(offers.get("priceCurrency")) or params["default_currency"],
        "url": url or None,
        "brand": attributes.get(PUBLISHER),
        "category": category_path[-1] if category_path else None,
        "category_path": category_path or None,
        "old_price": old_price,
        "availability": _availability(doc, offers),
        "image": _image(product.get("image")),
        "sku": code,
        "barcode": _barcode(attributes.get(ISBN)),
        "rating": rating,
        "reviews_count": reviews_count,
        "attributes": attributes or None,
    }
    cleared = ["old_price"] if old_price is None else []
    if not code:
        return unrecognized("product page without a product code", signature="missing-field:product_id")
    if not title or not fields["url"]:
        return unrecognized("product page without a title or URL", signature="missing-field:title")
    if price is None:
        ctx.log.warning("price not found", code="extract.missing_selector", selector="offers.price")
        fields.pop("currency")
        return unrecognized(
            "product page without a price",
            signature="missing-field:price",
            entities=[entity("product", fields, completeness="partial")],
        )
    fields["completeness"] = "full"
    return success([entity("product", fields, cleared=cleared, completeness="full")])
