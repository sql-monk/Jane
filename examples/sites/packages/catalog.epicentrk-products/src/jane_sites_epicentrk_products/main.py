"""Full product card of epicentrk.ua: one ``product`` entity per product page (``completeness: full``).

The product page (``/ua/shop/<slug>.html``, rendered on the server by Nuxt) carries schema.org microdata and
stable ``data-*`` attributes; its hashed CSS classes change with every build of the site and are not used:

* ``product_id`` - the slug of the canonical product URL, the same slug the category pages link to, so the
  partial updates of the price task (``catalog.epicentrk-prices``) hit the same key; ``url`` - that URL;
* ``title`` - ``h1[data-product-name]``; ``sku`` - the shop's code («КОД»);
* ``price`` / ``old_price`` - ``[data-product-price-main]`` / ``[data-product-price-old]`` (``data@value``),
  ``currency`` - ``itemprop=priceCurrency``, ``unit`` - the price unit («₴/шт.» -> «шт.»);
* ``availability`` - ``itemprop=availability`` of the offer, else the status text next to the code;
* ``brand``, ``category`` / ``category_path`` (breadcrumbs without the home, catalog and brand-filter crumbs),
  ``image`` (``og:image``), ``rating`` / ``reviews_count`` (``aggregateRating``), ``seller`` (the shop or a
  marketplace merchant; a name of an individual entrepreneur - «ФОП …» - is not kept), ``attributes`` (the
  characteristics ``section`` without reviews: name -> value, list values joined with ", ").

An out-of-stock product shows no price: its entity has no ``price`` (a missing field is not a deletion, the
last known price stays in storage). A page with a price and no struck-through price clears ``old_price``.
Pages without ``h1[data-product-name]`` (category and other pages) are ``empty``; a product page without a
slug or a title, or in stock without a price, is ``unrecognized``.
"""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SLUG = re.compile(r"/(?:[a-z]{2}/)?shop/([^/]+)\.html")
CURRENCY = re.compile(r"[A-Z]{3}")
INDIVIDUAL = re.compile(r"(?:ФОП|ФО-П)(?:\s|\.|$)", re.IGNORECASE)
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
NAVIGATION_PATHS = frozenset({"/", "/ua/", "/shop/", "/ua/shop/"})
SKIP_ATTRIBUTES = frozenset({"Ціна"})


def _text(value: str | None) -> str:
    return " ".join((value or "").split())


def _plain(value: str | None) -> str:
    """Text without pictographs (category names carry decorative emoji)."""
    kept = "".join(
        ch
        for ch in value or ""
        if unicodedata.category(ch) not in {"So", "Cs", "Co", "Cf"} and not 0xFE00 <= ord(ch) <= 0xFE0F
    )
    return _text(kept)


def _first(values: list[Any]) -> Any:
    return values[0] if values else None


def _number(value: str | None) -> float | None:
    raw = (value or "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        number = float(raw)
    except ValueError:
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _slug(url: str | None) -> str | None:
    if not url:
        return None
    match = SLUG.fullmatch(urlsplit(url).path)
    return match.group(1) if match else None


def _block_price(block: Any) -> float | None:
    """``data@value`` of a price block: the ``itemprop=price`` one, else the first numeric one."""
    for data in block.xpath('.//data[@itemprop="price"]') + block.xpath(".//data[@value]"):
        number = _number(data.get("value") or data.get("content"))
        if number is not None:
            return number
    return None


def _availability(doc: Any, status: str | None) -> str:
    for value in doc.xpath(
        '//*[@itemprop="offers"]//*[@itemprop="availability"]/@href'
        ' | //*[@itemprop="offers"]//*[@itemprop="availability"]/@content'
    ):
        mapped = SCHEMA_AVAILABILITY.get(str(value).rstrip("/").rsplit("/", 1)[-1].casefold())
        if mapped:
            return mapped
    return TEXT_AVAILABILITY.get(_text(status).casefold(), "unknown")


def _code_and_status(doc: Any) -> tuple[str | None, str | None]:
    """The shop's code («КОД <span>…</span>») and the status text of the same block («В наявності» …)."""
    for div in doc.iter("div"):
        span = div.find("span")
        if _text(div.text) != "КОД" or span is None:
            continue
        code = _text(span.text_content()) or None
        block = div.getparent().getparent() if div.getparent() is not None else None
        texts = [_text(t) for t in block.itertext()] if block is not None else []
        status = next((t for t in texts if t and t not in {"КОД", code}), None)
        return code, status
    return None, None


def _category_path(doc: Any) -> list[str]:
    path: list[str] = []
    for item in doc.xpath('//*[@itemprop="breadcrumb"]//li'):
        href = _first(item.xpath("./a/@href"))
        if not href:  # the product itself
            continue
        link = urlsplit(str(href)).path
        if link in NAVIGATION_PATHS or "/fs/" in link or "/filter/" in link:  # home, catalog, brand filter
            continue
        name = _plain(item.get("data-breadcrumb") or item.text_content())
        if name:
            path.append(name)
    return path


def _attributes(doc: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    reviews = '@itemprop="review" or @itemprop="acceptedAnswer" or @itemprop="suggestedAnswer"'
    for row in doc.xpath(f"//section//dl[not(ancestor::*[{reviews}])]/div[dt and dd]"):
        name = _text(row.find("dt").text_content()).rstrip(":").strip()
        dd = row.find("dd")
        items = [_text(li.text_content()) for li in dd.iter("li")]
        if not items:
            items = [_text(line) for line in dd.text_content().splitlines()]
        value = ", ".join(i for i in items if i)
        if name and value and name not in SKIP_ATTRIBUTES and name not in out:
            out[name] = value
    return out


def _seller(doc: Any) -> str | None:
    name = _text(
        _first([e.text_content() for e in doc.xpath('//*[@itemprop="seller"]//*[@itemprop="name"]')])
    )
    if not name:
        name = _text(_first(doc.xpath('//a[contains(@href, "/merchant/")]/@title')))
    if not name or INDIVIDUAL.match(name):
        return None
    return name


def _rating(doc: Any) -> tuple[float | None, int | None]:
    block = _first(doc.xpath('//*[@itemprop="aggregateRating"]'))
    if block is None:
        return None, None
    value = _first(block.xpath('.//*[@itemprop="ratingValue"]'))
    count = _first(block.xpath('.//*[@itemprop="ratingCount"] | .//*[@itemprop="reviewCount"]'))
    rating = _number(value.get("content") or value.text_content()) if value is not None else None
    reviews = _number(count.get("content") or count.text_content()) if count is not None else None
    return (
        rating if rating is not None and rating <= 5 else None,
        int(reviews) if reviews is not None and reviews.is_integer() else None,
    )


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    doc = lxml_html.document_fromstring(ctx.text())
    heading = _first(doc.xpath("//h1[@data-product-name]"))
    if heading is None:
        return empty()
    page_url = str((material.get("locator") or {}).get("url") or "")
    url = slug = None
    for candidate in (
        _first(doc.xpath('//link[@rel="canonical"]/@href')),
        _first(doc.xpath('//meta[@property="og:url"]/@content')),
        page_url,
    ):
        if candidate and _slug(urljoin(page_url, str(candidate))):
            url = urljoin(page_url, str(candidate))
            slug = _slug(url)
            break
    title = _text(heading.text_content())
    if not slug or not url:
        return unrecognized("product page without a product URL", signature="missing-field:product_id")
    if not title:
        return unrecognized(
            "product page without a title", signature="missing-selector:h1[data-product-name]"
        )

    main = _first(doc.xpath("//*[@data-product-price-main]"))
    old = _first(doc.xpath("//*[@data-product-price-old]"))
    price = _block_price(main) if main is not None else None
    old_price = _block_price(old) if old is not None else None
    if price is None or old_price is None or old_price <= price:
        old_price = None
    currency = unit = None
    if main is not None:
        currency = next(
            (str(c) for c in main.xpath('.//*[@itemprop="priceCurrency"]/@content') if CURRENCY.fullmatch(c)),
            None,
        )
        label = _text(_first([e.text_content() for e in main.xpath('.//data[@itemprop="priceCurrency"]')]))
        if "/" in label:  # «₴/шт.»
            unit = label.split("/", 1)[1].strip() or None
    sku, status = _code_and_status(doc)
    availability = _availability(doc, status)
    if price is None and availability in {"in_stock", "preorder"}:
        ctx.log.warning(
            "price not found", code="extract.missing_selector", selector="[data-product-price-main]"
        )
        return unrecognized(
            "product on sale without a price", signature="missing-selector:[data-product-price-main]"
        )

    path = _category_path(doc)
    rating, reviews = _rating(doc)
    attributes = _attributes(doc)
    brand = _text(_first(doc.xpath('//*[@itemprop="brand"]//meta[@itemprop="name"]/@content')))
    image = _first(doc.xpath('//meta[@property="og:image"]/@content'))
    fields: dict[str, Any] = {
        "shop": str(params["shop"]),
        "product_id": slug,
        "title": title,
        "url": url,
        "price": price,
        "currency": (currency or str(params["currency"])) if price is not None else None,
        "old_price": old_price,
        "availability": availability,
        "brand": brand or attributes.get("Бренд") or None,
        "category": path[-1] if path else None,
        "category_path": path or None,
        "image": urljoin(page_url, str(image)) if image else None,
        "sku": sku,
        "unit": unit if price is not None else None,
        "rating": rating,
        "reviews_count": reviews,
        "seller": _seller(doc),
        "attributes": attributes or None,
    }
    cleared = ["old_price"] if price is not None and old_price is None else None
    return success([entity("product", fields, cleared=cleared, completeness="full")])
