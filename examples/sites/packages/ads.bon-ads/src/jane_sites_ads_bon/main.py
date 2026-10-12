"""Classified ads of BON.ua (formerly besplatka.ua): ad cards and category listing pages.

* An ad card (``/obyavlenie/<slug>``) gives a complete ad: the schema.org ``Product`` JSON-LD (ad number
  ``sku``, title, price, currency, city, photos, description) plus the card markup - breadcrumbs (category
  path, region), the properties table (condition and the other parameters), the location card (district),
  the "placed" date and the seller kind (a shop link - ``business``, an author link - ``private``).
* A category page (``/<category>``, ``/<category>/page/N``) gives a partial ad per listed ad (number, URL,
  title, price, currency, city, date and the page's top category): the scheduled scan refreshes these fields
  of known ads every run, while a card is fetched once and then on ``revisit``.

The entity type is that of the top-level section of the site (``SECTIONS``: the section's URL slug, else its
name) - ``ad_goods``, ``ad_realty``, ``ad_car``; a section missing from the table is ``ad_other``. A card and
a category page name the same top-level section in their breadcrumbs, so both produce the same type and the
same key (site + the ad number) and update one entity. A category page that lists ads but names no top-level
section is ``unrecognized``: its ads would land under a type the cards may not share.

Personal data stay out: no seller name, phone or profile id; phone numbers and e-mails in the description
are masked; the coordinates of the location card are not read. Pages that are neither (the home page, other
sections) are ``empty``; a card or a category page that does not yield its ads is ``unrecognized``.
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
_APOSTROPHES = re.compile(r"[`'’ʼ]")

# Top-level sections of bon.ua: URL slug -> (name on the site, entity type). Every type here is declared in
# output.entities of the manifest; ``ad_other`` also covers any section missing from the table.
OTHER = "ad_other"
SECTIONS: dict[str, tuple[str, str]] = {
    "nedvizhimost": ("Нерухомість", "ad_realty"),
    "transport": ("Транспорт", "ad_car"),
    "avtozapchasti": ("Запчастини для транспорту", "ad_goods"),
    "odezhda-obuv-aksessuary": ("Одяг, взуття, аксесуари", "ad_goods"),
    "detskiy-mir": ("Дитячий світ", "ad_goods"),
    "electronika-i-bitovaya-tehnika": ("Електроніка, побутова техніка", "ad_goods"),
    "mebel-interer-obihod": ("Дім та Дача", "ad_goods"),
    "stroitelstvo-i-remont": ("Будівництво та ремонт", "ad_goods"),
    "sport-otdyh": ("Спорт, відпочинок", "ad_goods"),
    "hobbi-muzika-iscustvo": ("Хобі, музика, мистецтво", "ad_goods"),
    "krasota-i-zdorove": ("Краса та здоров`я", "ad_goods"),
    "oborudovanie": ("Обладнання", "ad_goods"),
    "rabota": ("Робота в Україні", OTHER),
    "rabota-za-rubezhom": ("Робота за кордоном", OTHER),
    "rezume": ("Резюме | Шукаю роботу", OTHER),
    "uslugi": ("Послуги", OTHER),
    "zhivotnye-i-rasteniya": ("Тварини та рослини", OTHER),
}
_LANGUAGES = {"ru", "uk", "ua"}


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


def _name_key(name: str) -> str:
    return _SPACES.sub(" ", _APOSTROPHES.sub("'", name)).strip().casefold()


_TYPE_BY_NAME = {_name_key(name): entity_type for name, entity_type in SECTIONS.values()}


def _entity_type(section_url: str | None, section_name: str | None) -> str:
    """Type of the ads of a top-level section: by its URL slug, else by its name, else ``ad_other``."""
    parts = [p for p in urlsplit(section_url or "").path.split("/") if p]
    if parts and parts[0] in _LANGUAGES:
        parts = parts[1:]
    if parts and parts[0] in SECTIONS:
        return SECTIONS[parts[0]][1]
    return _TYPE_BY_NAME.get(_name_key(section_name or ""), OTHER)


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
def _card(
    doc: Any, product: dict[str, Any], page_url: str, params: dict[str, Any]
) -> tuple[str, dict[str, Any]] | None:
    """Entity type and complete fields of an ad card."""
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
    links = doc.xpath('//nav[@id="message-breadcrumbs"]//li[@itemprop="itemListElement"]//a/@href')
    section_url = next((h for h in links if urlsplit(h).path.strip("/") not in ("", *_LANGUAGES)), None)
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
    return _entity_type(section_url, path[0]), {
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
def _section(blocks: list[Any]) -> tuple[str | None, str | None]:
    """Name and URL of the top-level section in the BreadcrumbList of a category page (after "Головна")."""
    trail = _ld_of_type(blocks, "BreadcrumbList") or {}
    crumbs = sorted(
        (i for i in trail.get("itemListElement") or [] if isinstance(i, dict)),
        key=lambda i: int(i.get("position") or 0),
    )
    if len(crumbs) < 2:
        return None, None
    item = crumbs[1].get("item")
    url = item.get("@id") if isinstance(item, dict) else item
    return _text(crumbs[1].get("name")), url if isinstance(url, str) else None


def _listing(items: list[Any], category: str, page_url: str) -> tuple[list[dict[str, Any]], int]:
    """Partial ads of a category page and the number of listed items that could not be read."""
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
        card = _card(doc, product, page_url, params)
        if card is None:
            ctx.log.warning("ad card without a number, title or category", code="extract.missing_field")
            return unrecognized("ad card without a number, title or category", signature="bon:card-fields")
        entity_type, fields = card
        return success([entity(entity_type, fields, completeness="full")])
    items = doc.xpath(f"//div[{_classes('msg-one')}]")
    category, section_url = _section(blocks)
    if items and not category and not is_card:
        ctx.log.warning(
            f"category page lists {len(items)} item(s) but names no top-level section",
            code="extract.missing_field",
        )
        return unrecognized(
            "category page without a top-level section: the type of its ads is unknown",
            signature="bon:listing-section",
        )
    ads, broken = _listing(items, category, page_url) if items and category else ([], 0)
    if broken:
        ctx.log.warning(
            f"{broken} listed item(s) without a number, link or title", code="extract.missing_field"
        )
    if ads:
        entity_type = _entity_type(section_url, category)
        return success([entity(entity_type, f, completeness="partial") for f in ads])
    if broken:
        return unrecognized("category page items could not be read", signature="bon:listing-items")
    if is_card:
        return unrecognized("ad card without schema.org Product data", signature="bon:card-no-product")
    return empty()
