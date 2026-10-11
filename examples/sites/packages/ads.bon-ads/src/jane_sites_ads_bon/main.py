"""Classified ads of BON.ua (formerly besplatka.ua): ad cards and category listing pages.

* An ad card (``/obyavlenie/<slug>``) gives a complete ``classified_ad``: the schema.org ``Product`` JSON-LD
  (ad number ``sku``, title, price, currency, city, photos, description) plus the card markup - breadcrumbs
  (category path, region), the properties table (condition and the other parameters), the location card
  (district), the "placed" date and the seller kind (a shop link - ``business``, an author link - ``private``).
* A category page (``/<category>``, ``/<category>/page/N``) gives a partial ``classified_ad`` per listed ad
  (number, URL, title, price, currency, city, date and the page's top category): the scheduled scan refreshes
  these fields of known ads every run, while a card is fetched once and then on ``revisit``.

Both use the same key (site + the ad number), so a card and the category pages update one entity. Personal
data stay out: no seller name, phone or profile id; phone numbers and e-mails in the description are masked;
the coordinates of the location card are not read. Pages that are neither (the home page, other sections)
are ``empty``; a card or a category page that does not yield its ads is ``unrecognized``.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SITE = "bon.ua"
BASE_URL = "https://bon.ua/"
CURRENCIES = {"грн": "UAH", "uah": "UAH", "$": "USD", "usd": "USD", "€": "EUR", "eur": "EUR", "євро": "EUR"}
_DATE = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")
_PHONE = re.compile(
    r"(?<![\w+])(?:\+?\s?3\s?8[\s\-.]*)?\(?0\d{2}\)?[\s\-.]*\d{3}[\s\-.]*\d{2}[\s\-.]*\d{2}(?!\w)"
)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_SPACES = re.compile(r"\s+")


def _text(value: Any) -> str | None:
    text = _SPACES.sub(" ", value).strip() if isinstance(value, str) else ""
    return text or None


def _node_text(nodes: list[Any]) -> str | None:
    return _text(nodes[0].text_content()) if nodes else None


def _classes(name: str) -> str:
    return f'contains(concat(" ", normalize-space(@class), " "), " {name} ")'


def _iso_date(value: str | None) -> str | None:
    m = _DATE.search(value or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def _amount(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        amount = float(str(value).replace(" ", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return None
    return amount if amount >= 0 else None


def _currency(value: str | None) -> str | None:
    key = (value or "").strip().rstrip(".").lower()
    return CURRENCIES.get(key) or (key.upper() if re.fullmatch(r"[a-z]{3}", key) else None)


def _description(value: Any, limit: int) -> str | None:
    text = _text(value)
    if not text:
        return None
    text = _EMAIL.sub("[email приховано]", _PHONE.sub("[телефон приховано]", text))
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _ld_blocks(doc: Any) -> list[Any]:
    blocks = []
    for raw in doc.xpath('//script[@type="application/ld+json"]/text()'):
        try:
            blocks.append(json.loads(raw))
        except ValueError:
            continue
    return blocks


def _ld_of_type(blocks: list[Any], type_name: str) -> dict[str, Any] | None:
    for block in blocks:
        for node in block if isinstance(block, list) else [block]:
            if isinstance(node, dict) and node.get("@type") == type_name:
                return node
    return None


def _deal_type(title: str, path: list[str], price: float | None) -> str:
    words = " ".join([title, *path]).lower()
    if re.search(r"\bкуплю\b", words):
        return "unknown"  # a wanted ad, not an offer
    if price == 0 or re.search(r"\b(віддам|отдам) (безкоштовно|даром|бесплатно)\b", words):
        return "free"
    if re.search(r"\b(обмін|обмен)\b", title.lower()):
        return "exchange"
    return "sale"


# ---------------------------------------------------------------------------------------------- ad card
def _card(doc: Any, product: dict[str, Any], page_url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    ad_id = str(product.get("sku") or "").strip()
    if not ad_id.isdigit():
        number = _node_text(doc.xpath(f"//ul[{_classes('card-info')}]/li[1]"))
        ad_id = re.sub(r"\D", "", number or "")
    title = _text(product.get("name"))
    url = _text(product.get("url")) or page_url
    names = doc.xpath(
        '//nav[@id="message-breadcrumbs"]//li[@itemprop="itemListElement"]//*[@itemprop="name"]/text()'
    )
    crumbs: list[str] = [c for c in (_text(t) for t in names[1:]) if c]  # without "Головна"
    path = [c for c in crumbs if " - " not in c]
    places = [c.split(" - ", 1)[1].strip() for c in crumbs if " - " in c]
    if not ad_id or not title or not url or not path:
        return None
    offers = product.get("offers")
    offer: dict[str, Any] = offers if isinstance(offers, dict) else {}
    price = _amount(offer.get("price"))
    served = offer.get("areaServed")
    city = _text(served.get("name")) if isinstance(served, dict) else None
    city = city or _node_text(doc.xpath(f"//*[{_classes('ms-location-card__primary')}]"))
    secondary = _node_text(doc.xpath(f"//*[{_classes('ms-location-card__secondary')}]"))
    region = next((p for p in places if "обл" in p.lower()), None)
    if region is None and secondary and "обл" in secondary.lower():
        region = secondary
    district = (
        secondary if secondary and ("район" in secondary.lower() or "р-н" in secondary.lower()) else None
    )
    properties: dict[str, str] = {}
    for prop in doc.xpath(f"//div[{_classes('card-properties')}]/div[{_classes('property')}]"):
        key = _node_text(prop.xpath(f"./*[{_classes('key')}]"))
        value = _node_text(prop.xpath(f"./*[{_classes('value')}]"))
        if key and value:
            properties.setdefault(key, value)
    seller_links = " ".join(doc.xpath(f"//a[{_classes('btn-all-messages')}]/@href"))
    seller = (
        "business" if "/shop/" in seller_links else "private" if "/author/" in seller_links else "unknown"
    )
    placed = _iso_date(" ".join(doc.xpath(f"//ul[{_classes('card-info')}]/li[2]//text()")))
    images = product.get("image")
    image = images[0] if isinstance(images, list) and images else images
    return {
        "site": SITE,
        "ad_id": ad_id,
        "url": url,
        "title": title,
        "category": path[0],
        "category_path": path,
        "price": price,
        "currency": _currency(offer.get("priceCurrency")) if price is not None else None,
        "is_free": price == 0 if price is not None else None,
        "deal_type": _deal_type(title, path, price),
        "city": city,
        "region": region,
        "district": district,
        "published_at": placed,
        "seller_type": seller,
        "condition": properties.get("Стан") or properties.get("Состояние"),
        "params": properties or None,
        "image": image if isinstance(image, str) and image.startswith(("https://", "http://")) else None,
        "description": _description(product.get("description"), int(params["description_max_chars"])),
    }


# ---------------------------------------------------------------------------------------- category page
def _listing(doc: Any, blocks: list[Any], page_url: str) -> tuple[list[dict[str, Any]], int]:
    """Partial ads of a category page and the number of listed items that could not be read."""
    trail = _ld_of_type(blocks, "BreadcrumbList") or {}
    names = [
        _text(i.get("name"))
        for i in sorted(
            (i for i in trail.get("itemListElement") or [] if isinstance(i, dict)),
            key=lambda i: int(i.get("position") or 0),
        )
    ]
    category = names[1] if len(names) > 1 else None
    items = doc.xpath(f"//div[{_classes('msg-one')}]")
    if not category or not items:
        return [], 0
    found: dict[str, dict[str, Any]] = {}
    broken = 0
    for item in items:
        ad_id = "".join(item.xpath(f".//*[{_classes('add_favorite')}]/@data-id")[:1]).strip()
        link = item.xpath(f".//a[{_classes('m-title')}]")
        href = link[0].get("href") if link else None
        title = _text(link[0].text_content()) if link else None
        if not ad_id.isdigit() or not href or not title:
            broken += 1
            continue
        wrap = item.xpath(f".//*[{_classes('m-price-wrap')}]")
        price = currency = None
        if wrap:
            sign = _node_text(wrap[0].xpath(f".//*[{_classes('m-currency')}]"))
            number = (wrap[0].text_content() or "").replace(sign or "", "")
            price = _amount(re.sub(r"[^\d.,]", "", number))
            currency = _currency(sign) if price is not None else None
        found.setdefault(
            ad_id,
            {
                "site": SITE,
                "ad_id": ad_id,
                "url": urljoin(page_url or BASE_URL, href),
                "title": title,
                "category": category,
                "price": price,
                "currency": currency,
                "city": _node_text(item.xpath(f".//*[{_classes('m-region')}]")),
                "published_at": _iso_date(_node_text(item.xpath(f".//*[{_classes('m-date')}]"))),
            },
        )
    return list(found.values()), broken


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    text = ctx.text()
    if not text.strip():
        return empty()
    doc = lxml_html.fromstring(text)
    page_url = str((material.get("locator") or {}).get("url") or "")
    blocks = _ld_blocks(doc)
    product = _ld_of_type(blocks, "Product")
    is_card = urlsplit(page_url).path.startswith("/obyavlenie/") or bool(
        doc.xpath(f"//ul[{_classes('card-info')}]")
    )
    if is_card and product is not None and isinstance(product.get("offers"), dict):
        fields = _card(doc, product, page_url, params)
        if fields is None:
            ctx.log.warning("ad card without a number, title or category", code="extract.missing_field")
            return unrecognized("ad card without a number, title or category", signature="bon:card-fields")
        return success([entity("classified_ad", fields, completeness="full")])
    ads, broken = _listing(doc, blocks, page_url)
    if broken:
        ctx.log.warning(
            f"{broken} listed item(s) without a number, link or title", code="extract.missing_field"
        )
    if ads:
        return success([entity("classified_ad", f, completeness="partial") for f in ads])
    if broken:
        return unrecognized("category page items could not be read", signature="bon:listing-items")
    if is_card:
        return unrecognized("ad card without schema.org Product data", signature="bon:card-no-product")
    return empty()
