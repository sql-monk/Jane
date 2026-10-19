"""Products of bi.ua («Будинок іграшок»): a full card from a product page, prices from a category page.

Both page types carry schema.org JSON-LD, the extractor reads it first and the visible markup only for what
JSON-LD lacks. The entity key is the shop (``bi.ua``) and the shop's product code (``product_id``, JSON-LD
``sku``, the code in the product card id ``<code>/<position>`` of a category page). Every colour or set of a
product is a separate product of the shop with its own code, URL and price, so a variant is a separate entity.

* **Product page** (``/ukr/product/<slug>.html``, top-level JSON-LD ``Product`` with an ``Offer``): ``title``,
  ``url``, ``price`` / ``currency`` / ``availability`` (the offer), ``old_price`` (the struck-through price of
  the buy block), ``brand``, ``sku`` (the manufacturer's article, JSON-LD ``mpn``), ``image``, ``category`` /
  ``category_path`` (the breadcrumbs without the home page and the product), ``rating`` / ``reviews_count``
  (``aggregateRating``, else the counter of the reviews tab), ``attributes`` (the characteristics tables:
  name -> value) and ``weight`` / ``unit`` (the «Вага» characteristic). ``completeness: full``.
* **Category page** (JSON-LD ``ItemList`` of products): one partial update per product - ``price``,
  ``currency``, ``availability`` and ``old_price`` (the struck-through price of the product card) -
  ``completeness: partial``; storage changes only these fields of the full card. ``listing_prices: false``
  makes category pages plain navigation (``empty``) - the full-catalog task reads prices from product pages.

A product shown without a price (bi.ua gives ``price: 0`` to some products out of stock) gets no ``price``
(the last known price stays in storage; such a product page is ``completeness: partial``). A price without a
struck-through price clears ``old_price``. Other pages are ``empty``; a product page without a JSON-LD
``Product``, a category page with product cards but no ``ItemList``, and products without a code are
``unrecognized``. Reviews (they carry names of private persons) are not kept.

The entity type is the product group of the breadcrumbs (``CATEGORY_TYPES``: the longest table prefix wins).
A product page takes it from its own ``category_path`` (an unknown section is ``product_other``); a category
page from its own breadcrumbs, the section of all its products, and a category page of a section that is not
in the table is ``unrecognized`` (no partial update into another type's collection).
"""

from __future__ import annotations

import html
import json
import re
from collections.abc import Iterator, Sequence
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from lxml import etree  # type: ignore[import-untyped]
from lxml import html as lxml_html

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SHOP = "bi.ua"
AVAILABILITY = {
    "instock": "in_stock",
    "instoreonly": "in_stock",
    "onlineonly": "in_stock",
    "limitedavailability": "in_stock",
    "outofstock": "out_of_stock",
    "soldout": "out_of_stock",
    "discontinued": "out_of_stock",
    "preorder": "preorder",
    "presale": "preorder",
    "backorder": "preorder",
}
HOME = "https://bi.ua/"
PRODUCT_PATH = re.compile(r"/product/[^/]+\.html$")
SPACES = re.compile(r"[\s\u00a0\u200b\u200c\u200d\ufeff]+")
DIGITS = re.compile(r"\d+")
WEIGHT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(кг|г)(?!\w)")
GRAMS = {"кг": 1000.0, "г": 1.0}
WEIGHT_ATTRIBUTE = "Вага"
OLD_PRICE = "//div[contains(@class,'prodBuy')]//div[contains(@class,'priceWr')]/p[@class='old']"
REVIEWS_COUNTER = "//li[@id='reviews']//span[contains(@class,'counter')]"
CARD = "//a[contains(@class,'goodsItemLink')][@id]"


# Catalog section (a prefix of ``category_path``) -> entity type, one MongoDB collection per type. The longest
# prefix in the table wins; a section that is not in the table is ``OTHER_TYPE`` (seasonal and promotional
# sections are only listed with their subsections). The card and the price extractor of the shop carry the same
# table and lookup - a price update must name the type of the card (examples/tests/test_sites.py compares them).
CATEGORY_TYPES: dict[tuple[str, ...], str] = {
    ("Дитячий транспорт",): "product_kids",
    ("Колекційні та ігрові фігурки",): "product_kids",
    ("Конструктори",): "product_kids",
    ("Машинки, роботи, трансформери",): "product_kids",
    ("М'які та інтерактивні іграшки",): "product_kids",
    ("Для активного відпочинку",): "product_kids",
    ("Настільні ігри та пазли",): "product_kids",
    ("Сюжетно-рольові набори",): "product_kids",
    ("Творчість і розвиток",): "product_kids",
    ("Товари для школи",): "product_office",
    ("Подарунки",): "product_other",
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


def _text(value: Any) -> str | None:
    """Text without HTML entities, zero-width characters and repeated spaces."""
    if isinstance(value, dict):
        value = value.get("name")
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return None
    text = SPACES.sub(" ", html.unescape(str(value))).strip()
    return text or None


def _node_text(node: Any) -> str | None:
    return _text("".join(node.itertext())) if node is not None else None


def _price(value: Any) -> float | None:
    """A positive price; ``0`` and anything else that is not a number is no price."""
    if isinstance(value, bool):
        return None
    try:
        amount = float(str(value).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return None
    return amount if amount > 0 else None


def _money(text: str | None) -> float | None:
    """A price shown on the page: «1 659 ₴» -> 1659.0."""
    if not text:
        return None
    digits = "".join(DIGITS.findall(text))
    return _price(digits) if digits else None


def _availability(offer: dict[str, Any]) -> str:
    value = str(offer.get("availability") or "").rstrip("/").rsplit("/", 1)[-1].lower()
    return AVAILABILITY.get(value, "unknown")


def _types(node: dict[str, Any]) -> set[str]:
    t = node.get("@type")
    if isinstance(t, str):
        return {t}
    return {x for x in t if isinstance(x, str)} if isinstance(t, list) else set()


def _ld_nodes(doc: Any, ctx: Context) -> Iterator[dict[str, Any]]:
    """Top-level JSON-LD nodes of the page (``@graph`` members included)."""
    for raw in doc.xpath("//script[@type='application/ld+json']/text()"):
        try:
            data = json.loads(raw, strict=False)  # bi.ua leaves raw line breaks in descriptions
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for block in data if isinstance(data, list) else [data]:
            if not isinstance(block, dict):
                continue
            graph = block.get("@graph")
            members = graph if isinstance(graph, list) else [block]
            yield from (m for m in members if isinstance(m, dict))


def _offer(product: dict[str, Any]) -> dict[str, Any]:
    offers = product.get("offers")
    if isinstance(offers, list):
        offers = next((o for o in offers if isinstance(o, dict)), None)
    return offers if isinstance(offers, dict) else {}


def _product_id(product: dict[str, Any]) -> str | None:
    sku = product.get("sku")
    if isinstance(sku, bool) or not isinstance(sku, (str, int)):
        return None
    return _text(sku)


def _url(value: Any, fallback: str | None) -> str | None:
    text = _text(value) or fallback
    if not text or not text.startswith(("https://", "http://")):
        return None
    parts = urlsplit(text)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def _image(value: Any) -> str | None:
    if isinstance(value, list):
        value = next((v for v in value if isinstance(v, str)), None)
    return value if isinstance(value, str) and value.startswith(("https://", "http://")) else None


def _category_path(nodes: list[dict[str, Any]], *, current: bool = False) -> list[str]:
    """Breadcrumbs after the home page. The last crumb has no link: the product of a product page (skipped) or
    the category itself of a category page (kept with ``current``)."""
    for node in nodes:
        if "BreadcrumbList" not in _types(node):
            continue
        crumbs = sorted(
            (c for c in node.get("itemListElement") or [] if isinstance(c, dict)),
            key=lambda c: c["position"] if isinstance(c.get("position"), int) else 0,
        )
        path = []
        for crumb in crumbs:
            link = crumb.get("item")
            link = link.get("@id") if isinstance(link, dict) else link
            name = _text(crumb.get("name"))
            if link == HOME or name is None or (not link and not current):
                continue
            path.append(name)
        return path
    return []


def _attributes(doc: Any) -> dict[str, str]:
    """Characteristics tables of the description tab: name -> value (title rows skipped)."""
    out: dict[str, str] = {}
    for row in doc.xpath("//div[contains(@class,'DprodChar')]//table//tr[count(td)>=2]"):
        name = _node_text(next(iter(row.xpath("./td[1]//span[contains(@class,'txt2')]")), None))
        value = _node_text(row.xpath("./td[2]")[0])
        if name and value:
            out.setdefault(name, value.replace(" ,", ","))  # «Кошик , Триколісний»: a space before a link
    return out


def _weight(text: str | None) -> tuple[float | None, str | None]:
    """«5 кг» -> (5.0, "кг"); «300 г» -> (300.0, "г"); «4 кг 300 г» -> (4.3, "кг")."""
    parts = [(float(n.replace(",", ".")), u) for n, u in WEIGHT.findall(text or "")]
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0]
    grams = sum(n * GRAMS[u] for n, u in parts)
    return round(grams / 1000, 3), "кг"


def _rating(product: dict[str, Any], doc: Any) -> tuple[float | None, int | None]:
    aggregate = product.get("aggregateRating")
    aggregate = aggregate if isinstance(aggregate, dict) else {}
    rating: float | None = None
    count: int | None = None
    try:
        rating = float(aggregate["ratingValue"])
    except (KeyError, TypeError, ValueError):
        rating = None
    try:
        count = int(aggregate["reviewCount"])
    except (KeyError, TypeError, ValueError):
        count = None
    if count is None:
        counter = _node_text(next(iter(doc.xpath(REVIEWS_COUNTER)), None))
        count = int(counter) if counter and counter.isdigit() else None
    return rating, count


def _product_page(
    product: dict[str, Any],
    nodes: list[dict[str, Any]],
    doc: Any,
    page_url: str | None,
    params: dict[str, Any],
) -> ExtractResult:
    product_id = _product_id(product)
    if product_id is None:
        return unrecognized("product JSON-LD without sku", signature="missing-field:sku")
    offer = _offer(product)
    price = _price(offer.get("price"))
    old = _money(_node_text(next(iter(doc.xpath(OLD_PRICE)), None)))
    old_price = old if price is not None and old is not None and old > price else None
    path = _category_path(nodes)
    attributes = _attributes(doc)
    weight, unit = _weight(attributes.get(WEIGHT_ATTRIBUTE))
    rating, reviews_count = _rating(product, doc)
    fields: dict[str, Any] = {
        "shop": SHOP,
        "product_id": product_id,
        "title": _text(product.get("name")),
        "price": price,
        "currency": _text(offer.get("priceCurrency")) or params["default_currency"],
        "url": _url(product.get("url") or offer.get("url"), page_url),
        "availability": _availability(offer),
        "old_price": old_price,
        "brand": _text(product.get("brand")),
        "category": path[-1] if path else None,
        "category_path": path or None,
        "image": _image(product.get("image")),
        "sku": _text(product.get("mpn")),
        "weight": weight,
        "unit": unit,
        "rating": rating,
        "reviews_count": reviews_count,
        "attributes": attributes or None,
    }
    full = all(fields[f] is not None for f in ("title", "price", "url"))
    cleared = ["old_price"] if price is not None and old_price is None else None
    kind = _entity_type(path)
    return success([entity(kind, fields, cleared=cleared, completeness="full" if full else "partial")])


def _card_old_prices(doc: Any) -> dict[str, float]:
    """Product code -> struck-through price of the product cards of a category page."""
    out: dict[str, float] = {}
    for card in doc.xpath(CARD):
        code = card.get("id", "").split("/", 1)[0].strip()
        old = _money(_node_text(next(iter(card.xpath(".//p[@class='old']")), None)))
        if code and old is not None:
            out.setdefault(code, old)
    return out


def _category_page(
    item_list: dict[str, Any], nodes: list[dict[str, Any]], doc: Any, params: dict[str, Any], ctx: Context
) -> ExtractResult:
    products: list[dict[str, Any]] = []
    for element in item_list.get("itemListElement") or []:
        item = element.get("item", element) if isinstance(element, dict) else None
        if isinstance(item, dict) and "Product" in _types(item):
            products.append(item)
    if not products:
        return empty()
    path = _category_path(nodes, current=True)
    kind = _listing_type(path)
    if kind is None:
        section = " > ".join(path) or "no breadcrumbs"
        ctx.log.warning(f"category page of an unmapped section: {section}", code="extract.unmapped_category")
        return unrecognized(
            f"the product type of category page {section!r} is not known: no prices are written",
            signature=f"unmapped-category:{path[0] if path else 'none'}",
        )
    old_prices = _card_old_prices(doc)
    found: dict[str, Any] = {}
    for product in products:
        product_id = _product_id(product)
        if product_id is None or product_id in found:
            continue
        offer = _offer(product)
        price = _price(offer.get("price"))
        old = old_prices.get(product_id)
        old_price = old if price is not None and old is not None and old > price else None
        fields = {
            "shop": SHOP,
            "product_id": product_id,
            "price": price,
            "currency": _text(offer.get("priceCurrency")) or params["default_currency"],
            "availability": _availability(offer),
            "old_price": old_price,
        }
        cleared = ["old_price"] if price is not None and old_price is None else None
        found[product_id] = entity(kind, fields, cleared=cleared, completeness="partial")
    if not found:
        return unrecognized("category page products without sku", signature="missing-field:sku")
    return success(list(found.values()))


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    raw = ctx.bytes()
    if not raw.strip():
        return empty()
    try:
        doc = lxml_html.document_fromstring(raw, parser=lxml_html.HTMLParser(encoding=ctx.charset()))
    except (etree.ParserError, ValueError):
        return empty()
    locator = material.get("locator") or {}
    page_url = str(locator.get("final_url") or locator.get("url") or "") or None
    nodes = list(_ld_nodes(doc, ctx))
    product = next((n for n in nodes if "Product" in _types(n) and n.get("offers")), None)
    if product is not None:
        return _product_page(product, nodes, doc, page_url, params)
    item_list = next((n for n in nodes if "ItemList" in _types(n)), None)
    if item_list is not None:
        return _category_page(item_list, nodes, doc, params, ctx) if params["listing_prices"] else empty()
    if page_url and PRODUCT_PATH.search(urlsplit(page_url).path):
        ctx.log.warning("product page without JSON-LD Product", code="extract.missing_json_ld")
        return unrecognized("product page without JSON-LD Product", signature="missing-json-ld:Product")
    if doc.xpath(CARD) and doc.xpath("//div[contains(@class,'pagin')]"):
        ctx.log.warning("category page without JSON-LD ItemList", code="extract.missing_json_ld")
        return unrecognized("category page without JSON-LD ItemList", signature="missing-json-ld:ItemList")
    return empty()
