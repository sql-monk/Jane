"""Car ads of Avtobazar InfoCar (``avtobazar.infocar.ua``): passenger car ad cards -> ``ad_car``.

A card (``/car/<region>/<city>/<make>/<model>/<body>-<year>-<id>.html``) gives the title (``h1``), the year,
the price in "у.о." (US dollars) with the site's UAH conversion (``abbr#priceabbr`` title), the mileage, the
engine volume and fuel, gearbox, drive, body type, colour, the "updated" date, the region, city, make and
model (breadcrumbs), the main photo and the seller's text (``p#text``: the free text after the equipment
sections; the "Стан" section tells a damaged car). "Приватне оголошення про продаж б.у. автомобіля" in the
page description means a private seller and a used car. ``div#deleted`` marks an ad that is no longer active:
"вже продано" - ``sold``, otherwise ``unknown``. Other pages (category pages, lorries, motorbikes) are
``empty``, so the entity type is fixed: every extracted ad is ``ad_car``.

The seller's name, phone images and QR card (``#author``) are never read; phone numbers and e-mails in the text
are hidden. Fuel, gearbox, drive and body type are normalized to the short English codes of the ``ad_car``
schema. Pages are windows-1251: the charset of the material is used, else the ``<meta charset>`` of the page.
"""

from __future__ import annotations

import codecs
import re
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SITE = "avtobazar.infocar.ua"
BASE_URL = "https://avtobazar.infocar.ua/"
AD_PATH = re.compile(r"^/car/(?:[^/]+/){4}[^/]*?-(\d+)\.html$")
META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?\s*([A-Za-z0-9_.:-]+)""", re.IGNORECASE)
PHONE = re.compile(r"(?<![\d+])(?:\+?\s?3\s?8[\s.-]?)?\(?0\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

FUEL = (  # (prefix of the lower-cased text, code); combined fuels first
    ("бензин + гбо", "petrol_gas"),
    ("бензин+гбо", "petrol_gas"),
    ("газ/бенз", "petrol_gas"),
    ("бензин/газ", "petrol_gas"),
    ("електро/", "hybrid"),
    ("гібрид", "hybrid"),
    ("бенз", "petrol"),
    ("диз", "diesel"),
    ("газ", "gas"),
    ("електро", "electric"),
)
GEARBOX = (
    ("механ", "manual"),
    ("ручн", "manual"),
    ("автомат", "automatic"),
    ("типтронік", "automatic"),
    ("планетарн", "automatic"),
    ("варіатор", "cvt"),
    ("робот", "robot"),
)
DRIVE = (("перед", "front"), ("зад", "rear"), ("повн", "awd"))
BODY = {
    "седан": "sedan",
    "хетчбек": "hatchback",
    "універсал": "wagon",
    "позашляховик": "suv",
    "кросовер": "crossover",
    "мінівен": "minivan",
    "купе": "coupe",
    "кабріолет": "convertible",
    "пікап": "pickup",
    "ліфтбек": "liftback",
    "фургон": "van",
    "мікроавтобус": "minibus",
}
DAMAGED = {"битий", "після дтп", "аварійний", "не на ходу", "потребує ремонту", "на запчастини"}
BREADCRUMB_LEVELS = {1: "region", 2: "city", 3: "make", 4: "model"}  # depth of /car/<1>/<2>/<3>/<4>/


# ---------------------------------------------------------------------------------------------------- helpers
def _page_text(material: Material, ctx: Context) -> str:
    content = material.get("content") or {}
    declared = content.get("charset") or (material.get("format") or {}).get("charset")
    if declared or (content.get("kind") == "inline" and content.get("encoding") == "utf-8"):
        return ctx.text()
    raw = ctx.bytes()
    found = META_CHARSET.search(raw[:4096])
    charset = found.group(1).decode("ascii") if found else "utf-8"
    try:
        codecs.lookup(charset)
    except LookupError:
        charset = "utf-8"
    return raw.decode(charset, errors="replace")


def _clean(text: str | None) -> str:
    return " ".join((text or "").replace("\xa0", " ").split())


def _first(nodes: list[Any]) -> Any | None:
    return nodes[0] if nodes else None


def _digits(text: str) -> int | None:
    value = re.sub(r"[^\d]", "", text)
    return int(value) if value else None


def _amount_before(text: str, unit: str) -> int | None:
    """``348.130 грн.`` -> 348130 (dots and spaces are thousands separators on this site)."""
    match = re.search(r"(\d[\d.\s\xa0]*)\s*" + re.escape(unit), text)
    return _digits(match.group(1)) if match else None


def _code(text: str, table: tuple[tuple[str, str], ...]) -> str | None:
    value = _clean(text).lower()
    if not value:
        return None
    return next((code for prefix, code in table if value.startswith(prefix)), value)


def _engine(text: str) -> tuple[float | None, str | None]:
    """``2.5 л,   бензин + ГБО`` -> (2.5, ``petrol_gas``); ``електро`` -> (None, ``electric``)."""
    value = _clean(text)
    volume: float | None = None
    match = re.match(r"^(\d+(?:[.,]\d+)?)\s*л\b[^,]*,?\s*(.*)$", value)
    if match:
        volume = float(match.group(1).replace(",", "."))
        value = match.group(2)
    return (volume if volume else None), _code(value, FUEL)


def _mileage(text: str) -> int | None:
    match = re.search(r"(\d[\d.\s\xa0]*)\s*(км|km|миль|mi)", text, re.IGNORECASE)
    if not match:
        return None
    value = _digits(match.group(1))
    if value is None:
        return None
    return round(value * 1.609344) if match.group(2).lower() in {"mi", "миль"} else value


def _date(text: str) -> str | None:
    match = re.search(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", text)
    return f"{match.group(3)}-{match.group(2)}-{match.group(1)}" if match else None


def _masked(text: str, limit: int) -> str | None:
    value = _clean(EMAIL.sub("[e-mail]", PHONE.sub("[телефон]", text.replace("\xa0", " "))))
    if not value or limit <= 0:
        return None
    if len(value) > limit:
        value = value[: limit - 1].rstrip() + "…"
    return value


def _seller_text(paragraph: Any) -> tuple[dict[str, str], str]:
    """``p#text`` -> ({section: values}, free text). A line is ended by ``<br>``; a line that starts with
    ``<strong>Name:</strong>`` is an equipment section; the site's fraud warning (``<span>``) is skipped."""
    lines: list[tuple[str | None, list[str]]] = [(None, [])]
    if paragraph.text:
        lines[-1][1].append(paragraph.text)
    for child in paragraph:
        tag = child.tag if isinstance(child.tag, str) else ""
        if tag == "br":
            lines.append((None, []))
        elif tag == "strong" and not _clean("".join(lines[-1][1])):
            lines[-1] = (_clean(child.text_content()).rstrip(":"), [])
        elif tag != "span":
            lines[-1][1].append(child.text_content())
        if child.tail:
            lines[-1][1].append(child.tail)
    sections: dict[str, str] = {}
    free: list[str] = []
    for name, parts in lines:
        text = _clean("".join(parts))
        if name:
            sections[name] = text.rstrip(",").strip()
        elif text:
            free.append(text)
    return sections, " ".join(free)


def _status(doc: Any) -> str:
    deleted = _first(doc.xpath("//div[@id='deleted']"))
    if deleted is None:
        return "active"
    return "sold" if "продано" in _clean(deleted.text_content()).lower() else "unknown"


# ---------------------------------------------------------------------------------------------------- card
def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    text = _page_text(material, ctx)
    if not text.strip():
        return empty()
    doc = lxml_html.fromstring(text)
    page_url = str((material.get("locator") or {}).get("url") or BASE_URL)
    url = urljoin(BASE_URL, _first(doc.xpath("//link[@rel='canonical']/@href")) or page_url)
    path = AD_PATH.match(urlsplit(url).path)
    info = _first(doc.xpath("//div[@id='infocol']/div[@id='info']"))
    if path is None or info is None:
        return empty()  # not a passenger car card
    heading = _first(info.xpath("./h1"))
    price_node = _first(info.xpath(".//abbr[@id='priceabbr']"))
    title = _clean(heading.text_content()) if heading is not None else ""
    price_text = _clean(price_node.text_content()) if price_node is not None else ""
    amount = _digits(price_text)
    if "грн" in price_text:
        currency = "UAH"
    elif "€" in price_text or "євро" in price_text.lower():
        currency = "EUR"
    elif "у.о." in price_text or "$" in price_text:
        currency = "USD"
    else:
        currency = ""
    if not title or amount is None or not currency:
        ctx.log.warning(
            "ad card without a title or a price",
            code="extract.missing_selector",
            selector="h1|abbr#priceabbr",
        )
        return unrecognized(
            "ad card without a title or a price", signature="missing-selector:h1|abbr#priceabbr"
        )
    fields: dict[str, Any] = {
        "site": SITE,
        "ad_id": path.group(1),
        "url": url,
        "title": title,
        "price": amount,
        "currency": currency,
        "status": _status(doc),
    }
    rates = price_node.get("title", "") if price_node is not None else ""
    fields["price_usd"] = amount if currency == "USD" else _amount_before(rates, "$")
    fields["price_uah"] = amount if currency == "UAH" else _amount_before(rates, "грн")
    year = _first(info.xpath("./span[1]"))
    if year is not None and re.fullmatch(r"(19|20)\d{2}", _clean(year.text_content())):
        fields["year"] = int(_clean(year.text_content()))
    mileage = _first(info.xpath(".//div[@id='price']/strong"))
    if mileage is not None:
        fields["mileage_km"] = _mileage(mileage.text_content())
    for row in info.xpath(".//tr[td[@class='name']]"):
        cells = row.xpath("./td")
        if len(cells) < 2:
            continue
        name, value = _clean(cells[0].text_content()).rstrip(":"), _clean(cells[1].text_content())
        if name == "Двигун":
            fields["engine_l"], fields["fuel"] = _engine(value)
        elif name == "Коробка":
            fields["transmission"] = _code(value, GEARBOX)
        elif name == "Привід":
            fields["drive"] = _code(value, DRIVE)
        elif name == "Кузов":
            body = value.split(",", 1)[0].strip().lower()
            fields["body_type"] = BODY.get(body, body) or None
        elif name == "Колір":
            fields["color"] = value.lower() or None
        elif name == "Оновлено":
            fields["updated_at"] = _date(value)
    for link in doc.xpath("//div[@id='breadcramps']//a[@itemprop='item'][@href]"):
        parts = [p for p in urlsplit(link.get("href", "")).path.split("/") if p]
        level = BREADCRUMB_LEVELS.get(len(parts) - 1) if parts[:1] == ["car"] else None
        if level:
            fields[level] = _clean(link.text_content()) or None
    image = _first(doc.xpath("//a[@id='bigfoto']/img/@src"))
    if image:
        absolute = urljoin(BASE_URL, image.strip())
        fields["image"] = absolute if absolute.startswith("https://") else None
    summary = _clean(_first(doc.xpath("//meta[@name='description']/@content")) or "").lower()
    if summary.startswith("приватне оголошення"):
        fields["seller_type"] = "private"
    if "б.у." in summary or "вживан" in summary:
        fields["condition"] = "used"
    paragraph = _first(doc.xpath("//p[@id='text']"))
    if paragraph is not None:
        sections, free = _seller_text(paragraph)
        state = {item.strip().lower() for item in sections.get("Стан", "").split(",")}
        if state & DAMAGED:
            fields["condition"] = "damaged"
        fields["description"] = _masked(free, int(params.get("description_max_chars", 500)))
    return success([entity("ad_car", fields)])
