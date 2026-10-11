"""Car ads of RST.ua (``car_ad``): tiles of the used-car catalog pages and the ad cards.

* **Catalog page** (``/ukr/oldcars/``, ``/ukr/oldcars/N.html``): every ``article.car-i`` tile is an ad - title
  (make, model, trim), price in USD with the UAH equivalent, year, engine volume, fuel and gearbox, mileage,
  region or city, the photo. Tiles of dealers' new cars (``/ukr/new/...``) are ads too (``condition: new``,
  ``seller_type: dealer``).
* **Ad card** (``/ukr/oldcars/<make>/<model>/<slug>_<id>.html``, ``div#car-p-i``): the same fields plus the
  city, drive, body type, colour and the description. Similar ads shown on a card are not extracted from it.

Both kinds give the same key (``site`` + ``ad_id``) and the same normalized values, so a catalog run updates
the price of the ad a card run filled in. Fuel, gearbox, drive and body type are normalized to short English
codes; the gearbox only to ``manual``/``automatic`` because a catalog tile does not tell more. The seller's name
and phone are never read; phone numbers and e-mails in the description are hidden. Pages are windows-1251: the charset of
the material is used, else the ``<meta charset>`` of the page.
"""

from __future__ import annotations

import codecs
import re
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SITE = "rst.ua"
BASE_URL = "https://rst.ua/"
USED_AD_PATH = re.compile(r"^/(?:ukr/)?oldcars/([^/]+)/([^/]+)/[^/]*?_(\d+)\.html$")
NEW_AD_PATH = re.compile(r"^/(?:ukr/)?new/([^/]+)/[^/]*?_(\d+)/")
META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?\s*([A-Za-z0-9_.:-]+)""", re.IGNORECASE)
PHONE = re.compile(r"(?<![\d+])(?:\+?\s?3\s?8[\s.-]?)?\(?0\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
TILE_XPATH = "//article[contains(concat(' ', normalize-space(@class), ' '), ' car-i ')]"

FUEL = (  # (prefix of the lower-cased text, code); combined fuels first
    ("г/б", "petrol_gas"),
    ("газ/бенз", "petrol_gas"),
    ("бенз/газ", "petrol_gas"),
    ("газ / бенз", "petrol_gas"),
    ("бензин/газ", "petrol_gas"),
    ("гібрид", "hybrid"),
    ("бенз", "petrol"),
    ("диз", "diesel"),
    ("газ", "gas"),
    ("ел", "electric"),
)
GEARBOX = (
    ("мех", "manual"),
    ("руч", "manual"),
    ("авт", "automatic"),
    ("тип", "automatic"),
    ("роб", "automatic"),
    ("вар", "automatic"),
)
DRIVE = (("перед", "front"), ("зад", "rear"), ("повн", "awd"))
BODY = {
    "седан": "sedan",
    "хетчбек": "hatchback",
    "хетчбэк": "hatchback",
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
    "мікробус пасажир": "minibus",
    "мікробус вантаж": "van",
}
TRANSLIT = str.maketrans(
    {
        "а": "a", "б": "b", "в": "v", "г": "g", "ґ": "g", "д": "d", "е": "e", "є": "e", "ж": "zh", "з": "z",
        "и": "i", "і": "i", "ї": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
        "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
        "ы": "y", "э": "e", "ю": "yu", "я": "ya",
    }
)  # fmt: skip


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


def _own_text(element: Any) -> str:
    """Text nodes directly inside ``element`` (not inside its child elements)."""
    return _clean(" ".join(element.xpath("text()")))


def _first(nodes: list[Any]) -> Any | None:
    return nodes[0] if nodes else None


def _digits(text: str) -> int | None:
    value = re.sub(r"[^\d]", "", text)
    return int(value) if value else None


def _amount(text: str) -> int | None:
    """``$15'900`` / ``1'599'300 грн`` -> 15900 / 1599300."""
    match = re.search(r"\d[\d'\s\xa0]*", text)
    return _digits(match.group(0)) if match else None


def _code(text: str, table: tuple[tuple[str, str], ...]) -> str | None:
    value = _clean(text).lower()
    if not value:
        return None
    return next((code for prefix, code in table if value.startswith(prefix)), value)


def _body(text: str) -> str | None:
    value = _clean(text).lower()
    return BODY.get(value, value) or None


def _engine(text: str) -> float | None:
    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not match:
        return None
    value = float(match.group(0).replace(",", "."))
    if value > 30:  # cubic centimetres
        value = round(value / 1000, 1)
    return value if value > 0 else None


def _mileage(text: str) -> int | None:
    match = re.search(r"(\d[\d'\s\xa0]*)\s*(km|км|mi|миль)", text, re.IGNORECASE)
    if not match:
        return None
    value = _digits(match.group(1))
    if value is None:
        return None
    return round(value * 1.609344) if match.group(2).lower() in {"mi", "миль"} else value


def _region(text: str) -> tuple[str | None, str | None]:
    """``Харківська обл`` -> (``Харківська область``, None); ``Одеса`` -> (None, ``Одеса``)."""
    value = _clean(text)
    if not value:
        return None, None
    match = re.match(r"^(.*?)\s+обл\.?$", value)
    if match:
        return f"{match.group(1)} область", None
    return None, value


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower().translate(TRANSLIT))


def _make_model(name: str, make_slug: str) -> tuple[str | None, str | None]:
    """Split ``HYUNDAI Santa Fe`` by the make slug of the URL (``hyundai``); ``ГАЗ Газель`` matches ``gaz``."""
    words = name.split()
    if len(words) < 2:
        return (words[0] if words else None), None
    wanted = _slug(make_slug)
    for n in range(1, len(words)):
        if _slug(" ".join(words[:n])) == wanted:
            return " ".join(words[:n]), " ".join(words[n:])
    return words[0], " ".join(words[1:])


def _description(text: str, limit: int) -> str | None:
    value = _clean(EMAIL.sub("[e-mail]", PHONE.sub("[телефон]", text.replace("\xa0", " "))))
    if not value or limit <= 0:
        return None
    if len(value) > limit:
        value = value[: limit - 1].rstrip() + "…"
    return value


def _details(doc: Any, card: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Preserve observed detail text; equipment/history are source claims, not verification."""
    fields: dict[str, Any] = {}
    specs = {
        item.get("title"): _clean(" ".join(item.itertext()))
        for item in card.xpath(".//li[@title]")
        if _clean(" ".join(item.itertext()))
    }
    battery = _first(
        card.xpath(".//li[i[contains(concat(' ', normalize-space(@class), ' '), ' ri-en-bf ')]]")
    )
    driving_range = _first(
        card.xpath(".//li[i[contains(concat(' ', normalize-space(@class), ' '), ' ri-en-b ')]]")
    )
    for label, node in [("Батарея", battery), ("Запас ходу", driving_range)]:
        if node is not None:
            specs[label] = _clean(" ".join(node.itertext()))
    if specs:
        fields["raw_specs"] = specs
    trim = _clean(" ".join(card.xpath(".//h2/i[contains(@class, 'fs-3')]/text()")))
    if trim:
        fields["trim"] = trim

    description = _first(doc.xpath("//div[@id='oc-item-desc']/p"))
    if description is not None:
        raw = description.text_content()
        full = _description(raw, int(params.get("full_description_max_chars", 12000)))
        if full:
            fields["description_full"] = full
            vin = re.search(r"\bVIN\s*[:\-]?\s*([A-HJ-NPR-Z0-9]{17})\b", full, re.IGNORECASE)
            if vin:
                fields["vin"] = vin.group(1).upper()
            # Only a named, explicitly listed equipment section is interpreted as a list.
            parts = [_clean(part) for part in re.split(r"[•\n\r]+", full) if _clean(part)]
            equipment: list[str] = []
            active = False
            for part in parts:
                if re.match(
                    r"^(?:оснащення|обладнання|комплектація|оснащение|оборудование|комплектация)\b",
                    part,
                    re.IGNORECASE,
                ):
                    active = True
                    continue
                if active and re.match(
                    r"^(?:стан|состояние|історія|история|контакти|контакты|ціна|цена|обслуговування)\b",
                    part,
                    re.IGNORECASE,
                ):
                    break
                if active:
                    equipment.append(part)
            equipment = list(dict.fromkeys(equipment))[: int(params.get("equipment_max_items", 100))]
            if equipment:
                fields["equipment"] = equipment

    gallery = _first(doc.xpath("//div[@id='car-p-photo']"))
    if gallery is not None:
        template = gallery.get("data-url", "")
        photos = []
        if "{0}" in template:
            for index in gallery.get("data-i", "").split(","):
                if index.strip().isdigit():
                    photo = _image(template.replace("{0}", index.strip()))
                    if photo:
                        photos.append(photo)
        else:
            photos = [url for src in gallery.xpath(".//img/@src") if (url := _image(src))]
        photos = list(dict.fromkeys(photos))[: int(params.get("photos_max_items", 100))]
        if photos:
            fields["photos"] = photos
            fields["image"] = photos[0]

    visible_vin = _first(doc.xpath("//p[@title='VIN-код']/span"))
    if visible_vin is not None:
        value = _clean(visible_vin.text_content())
        if re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", value, re.IGNORECASE):
            fields["vin"] = value.upper()
        elif value:
            fields["vin_masked"] = value
    history = [
        _clean(" ".join(item.itertext()))
        for item in doc.xpath(
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' car-p-inf ')]/div/p[not(@title)]"
        )
    ]
    history = list(dict.fromkeys(value for value in history if value))
    if history:
        fields["registration_history"] = history

    engine = _first(card.xpath(".//li[@title='двигун']"))
    if engine is not None and engine.xpath(
        "./i[contains(concat(' ', normalize-space(@class), ' '), ' ri-en-e ')]"
    ):
        engine_text = _clean(" ".join(engine.itertext()))
        for name, pattern, source_text in [
            ("power_kw", r"(\d+(?:[.,]\d+)?)\s*кВт(?!\s*(?:[·*/]|год))", engine_text),
            ("battery_kwh", r"(\d+(?:[.,]\d+)?)\s*кВт\s*[·*/]?\s*год", specs.get("Батарея", engine_text)),
            ("range_km", r"(\d+(?:[.,]\d+)?)\s*км", specs.get("Запас ходу", engine_text)),
        ]:
            match = re.search(pattern, source_text, re.IGNORECASE)
            if match:
                fields[name] = float(match.group(1).replace(",", "."))
    return fields


def _image(src: str | None) -> str | None:
    if not src:
        return None
    url = urljoin(BASE_URL, src.strip())
    return url if url.startswith("https://") else None


def _price(block: Any) -> dict[str, Any] | None:
    """``<b>$15'900<i>= 716'300 грн</i></b>`` -> price, currency, price_usd, price_uah."""
    main = _clean(block.text)
    amount = _amount(main)
    if amount is None:
        return None
    if "$" in main:
        currency = "USD"
    elif "€" in main:
        currency = "EUR"
    elif "грн" in main:
        currency = "UAH"
    else:
        return None
    out: dict[str, Any] = {"price": amount, "currency": currency}
    if currency == "USD":
        out["price_usd"] = amount
    if currency == "UAH":
        out["price_uah"] = amount
    for extra in block.xpath("./i"):
        text = _clean(extra.text_content())
        if "грн" in text and "price_uah" not in out:
            out["price_uah"] = _amount(text)
        elif "$" in text and "price_usd" not in out:
            out["price_usd"] = _amount(text)
    return {k: v for k, v in out.items() if v is not None}


def _fuel_gearbox(text: str) -> tuple[str | None, str | None]:
    """`` Бенз (Авт)`` -> (``petrol``, ``automatic``)."""
    match = re.match(r"^\s*([^()]*?)\s*(?:\(([^)]*)\))?\s*$", text)
    if not match:
        return None, None
    return _code(match.group(1), FUEL), _code(match.group(2) or "", GEARBOX)


# ---------------------------------------------------------------------------------------------------- tiles
def _tile(article: Any, page_url: str) -> dict[str, Any] | None:
    link = _first(article.xpath(".//a[contains(concat(' ', normalize-space(@class), ' '), ' ai ')][@href]"))
    block = _first(article.xpath(".//div[contains(concat(' ', normalize-space(@class), ' '), ' pr ')]/b"))
    if link is None or block is None:
        return None
    url = urljoin(page_url or BASE_URL, link.get("href", "").strip())
    path = urlsplit(url).path
    used, new = USED_AD_PATH.match(path), NEW_AD_PATH.match(path)
    if urlsplit(url).hostname not in {"rst.ua", "www.rst.ua"}:
        return None
    if used is not None:
        make_slug, ad_id = used.group(1), used.group(3)
    elif new is not None:
        make_slug, ad_id = new.group(1), new.group(2)
    else:
        return None
    name = _clean(link.text)
    italics = link.xpath("./i")
    trim = _clean(italics[1].text_content()) if len(italics) > 1 else ""
    price = _price(block)
    if not name or price is None:
        return None
    make, model = _make_model(name, make_slug)
    fields: dict[str, Any] = {
        "site": SITE,
        "ad_id": ad_id,
        "url": url,
        "title": _clean(f"{name} {trim}"),
        **price,
        "make": make,
        "model": model,
        "status": "active",
        "condition": "used" if used else "new",
    }
    if new:
        fields["seller_type"] = "dealer"
    for item in article.xpath(".//div[contains(concat(' ', normalize-space(@class), ' '), ' ps ')]//li"):
        title, classes = item.get("title", ""), item.get("class", "")
        if title == "рік":
            year = re.search(r"\b(19|20)\d{2}\b", _own_text(item))
            fields["year"] = int(year.group(0)) if year else None
        elif title == "двигун" and "ri-en-e" in classes.split():  # electric: power and range, no volume
            fields["fuel"] = "electric"
        elif title == "двигун":
            fields["engine_l"] = _engine(_own_text(item))
            hint = _first(item.xpath("./i[@title='паливо кпп']"))
            if hint is not None:
                fields["fuel"], fields["transmission"] = _fuel_gearbox(hint.text_content())
        elif "ri-speed" in classes.split():
            fields["mileage_km"] = _mileage(item.text_content())
        elif title == "регіон":
            fields["region"], fields["city"] = _region(item.text_content())
    image = _first(
        article.xpath(
            ".//div[contains(concat(' ', normalize-space(@class), ' '), ' p ')]/img[not(contains(@class, 'wm'))]/@src"
        )
    )
    fields["image"] = _image(image)
    return fields


# ---------------------------------------------------------------------------------------------------- card
class _Unrecognized(Exception):
    def __init__(self, reason: str, signature: str) -> None:
        super().__init__(reason)
        self.reason, self.signature = reason, signature


def _card(doc: Any, card: Any, page_url: str, limit: int, params: dict[str, Any]) -> dict[str, Any]:
    head = _first(card.xpath(".//div[starts-with(@id, 'i-')]"))
    ad_id = (head.get("id", "")[2:] if head is not None else "").strip()
    if head is None or not ad_id.isdigit():
        raise _Unrecognized("ad card without a number", "missing-selector:div#car-p-i div[id^=i-]")
    links = head.xpath(".//h2/a")
    block = _first(head.xpath(".//div[contains(concat(' ', normalize-space(@class), ' '), ' pr ')]/b"))
    price = _price(block) if block is not None else None
    if len(links) < 2 or price is None:
        raise _Unrecognized("ad card without a make, model or price", "missing-selector:h2 a|div.pr b")
    make, model = _clean(links[0].text_content()), _clean(links[1].text_content())
    trim = _clean(" ".join(i.text_content() for i in head.xpath(".//h2/i[contains(@class, 'fs-3')]")))
    url = _first(doc.xpath("//link[@rel='alternate'][@hreflang='uk']/@href")) or page_url
    fields: dict[str, Any] = {
        "site": SITE,
        "ad_id": ad_id,
        "url": urljoin(BASE_URL, url),
        "title": _clean(f"{make} {model} {trim}"),
        **price,
        "make": make,
        "model": model,
        "status": "active",
        "condition": "used",
    }
    year = _first(card.xpath(".//li[@title='рік']"))
    if year is not None:
        found = re.search(r"\b(19|20)\d{2}\b", year.text_content())
        fields["year"] = int(found.group(0)) if found else None
    mileage = _first(
        card.xpath(".//li[i[contains(concat(' ', normalize-space(@class), ' '), ' ri-speed ')]]")
    )
    if mileage is not None:
        fields["mileage_km"] = _mileage(mileage.text_content())
    region = _first(card.xpath(".//a[@title='регіон']"))
    if region is not None:
        tail = _first(region.xpath("following-sibling::i[1]"))
        suffix = " обл" if tail is not None and _clean(tail.text_content()).startswith("обл") else ""
        fields["region"], city = _region(_clean(region.text_content()) + suffix)
        fields["city"] = city
    city = _first(card.xpath(".//a[@title='місто']"))
    if city is not None:
        fields["city"] = _clean(city.text_content()) or fields.get("city")
    engine = _first(card.xpath(".//li[@title='двигун']"))
    if engine is not None and engine.xpath(
        "./i[contains(concat(' ', normalize-space(@class), ' '), ' ri-en-e ')]"
    ):
        fields["fuel"] = "electric"  # power, battery and range instead of a volume
    elif engine is not None:
        fields["engine_l"] = _engine(_own_text(engine))
        fuel = _first(engine.xpath(".//i[@title='паливо']"))
        fields["fuel"] = _code(fuel.text_content(), FUEL) if fuel is not None else None
    gearbox = _first(card.xpath(".//li[@title='КПП']"))
    if gearbox is not None:
        fields["transmission"] = _code(_own_text(gearbox), GEARBOX)
    drive = _first(
        card.xpath(".//div[contains(concat(' ', normalize-space(@class), ' '), ' ps ')]//i[@title='привід']")
    )
    if drive is not None:
        fields["drive"] = _code(drive.text_content(), DRIVE)
    body = _first(card.xpath(".//li[@title='кузов']"))
    if body is not None:
        fields["body_type"] = _body(_own_text(body))
        color = _first(body.xpath(".//i[@title='колір']"))
        if color is not None:
            fields["color"] = _clean(color.text_content()).lower() or None
    text = _first(doc.xpath("//div[@id='oc-item-desc']/p"))
    if text is not None:
        fields["description"] = _description(text.text_content(), limit)
    if params.get("include_details", True):
        fields.update(_details(doc, card, params))
    return fields


# ---------------------------------------------------------------------------------------------------- entry
def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    text = _page_text(material, ctx)
    if not text.strip():
        return empty()
    doc = lxml_html.fromstring(text)
    page_url = str((material.get("locator") or {}).get("url") or BASE_URL)
    limit = int(params.get("description_max_chars", 500))
    card = _first(doc.xpath("//div[@id='car-p-i']"))
    if card is not None:
        try:
            return success([entity("car_ad", _card(doc, card, page_url, limit, params))])
        except _Unrecognized as exc:
            ctx.log.warning(exc.reason, code="extract.missing_selector", selector=exc.signature)
            return unrecognized(exc.reason, signature=exc.signature)
    ads: dict[str, dict[str, Any]] = {}
    for article in doc.xpath(TILE_XPATH):
        fields = _tile(article, page_url)
        if fields is not None:
            ads.setdefault(fields["ad_id"], fields)
    if not ads:
        return empty()
    return success([entity("car_ad", fields) for fields in ads.values()])
