"""AUTO.RIA (auto.ria.com) ad page ``/uk/auto_<make>_<model>_<id>.html`` -> one full ``ad_car`` entity.

The page is rendered on the server (no JavaScript needed) and carries two machine-readable sources:

* JSON-LD ``Vehicle``: make (``brand.name``), ``model``, year (``productionDate``), the seller's price and its
  currency (``offers``), availability (``SoldOut`` - sold), ``itemCondition``, colour, fuel and gearbox
  (fallbacks), description;
* the page state ``window.__PINIA__ = {...}`` (Vue/Pinia server state): ``page.structures[<path>]`` holds
  ``additionalParams`` (ad id, link, prices converted to USD/UAH, main photo, ``isActive``, whether the seller
  is a company) and the server-driven page templates, found by their ``id``: ``basicInfoTitle``,
  ``basicInfoTableMainInfo*`` (mileage, gearbox, fuel and engine - told apart by their icon),
  ``basicInfoTableMainInfoGeo`` (region and city), ``descCharacteristicsValue`` (body type),
  ``descDriveTypeDriveType``, ``descColorColor``, ``descTechStateValue``, ``advertStatisticPublicationData``,
  ``sellerInfoSegment``, ``bannerStatusText``.

Mileage, gearbox, fuel, photo and ``url`` (the fetched URL, i.e. the search page's link) are read the same way
as on the search results page (package ``autos.autoria-search-page``), so both packages write identical values
into the same ``ad_car``. No seller names, phones, VIN or plate numbers are returned; phone numbers, e-mails and
street addresses inside the description are masked, the seller kind is omitted when the page shows no seller
(sold or removed ad). ``empty`` for a page without an ad (neither a ``Vehicle`` nor an ad state),
``unrecognized`` for an ad without a price.

The entity type is fixed: the package reads only passenger-car ad pages of AUTO.RIA, so every ad is ``ad_car``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from typing import Any
from urllib.parse import urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

CURRENCIES = {"USD", "UAH", "EUR"}
CONDITIONS = {
    "UsedCondition": "used",
    "NewCondition": "new",
    "DamagedCondition": "damaged",
    "RefurbishedCondition": "used",
}
DAMAGE_MARKERS = ("не відремонтован", "не на ходу", "на запчастин", "після дтп")
DEALER_SEGMENTS = {"компанія", "автосалон", "автодилер", "офіційний дилер", "дилер"}
NOT_SPECIFIED = {"не вказано", "не указано"}
MILEAGE_ICONS = {"ic_16_speedometer"}
GEARBOX_ICONS = {"ic_16_automat", "ic_16_transmission"}
FUEL_ICONS = {"ic_16_fuel", "ic_16_battery", "ic_16_hybrid"}
TEMPLATE_IDS = {
    "basicInfoTitle",
    "basicInfoTableMainInfoGeo",
    "descCharacteristicsValue",
    "descDriveTypeDriveType",
    "descColorColor",
    "descTechStateValue",
    "advertStatisticPublicationData",
    "sellerInfoSegment",
    "bannerStatusText",
    "basicInfoGenerationBase",
    "descGenerationBaseValue",
    "descEngineEngine",
    "descEcoStandartEcoStandart",
    "descTechStateText",
    "descPaintConditionValue",
    "descStateValue",
    "descFuelRateValue",
}
EQUIPMENT_IDS = {
    "comfort": "descComfortValue",
    "safety": "descSecurityValue",
    "multimedia": "descMultimediaValue",
    "headlights": "descHeadlightsValue",
    "interior_materials": "descInteriorMaterialsValue",
    "interior_color": "descInteriorColorsValue",
    "seat_adjustment": "descSeatAdjustmentValue",
    "heated_seats": "descSeatHeatedValue",
    "seat_memory": "descMemorySeatModuleValue",
    "electric_windows": "descWindowLifterValue",
    "climate_control": "descConditionerTypeValue",
    "power_steering": "descPowerSteeringValue",
    "steering_adjustment": "descSteeringWheelAdjustmentValue",
    "spare_wheel": "descSpareWheelValue",
    "lighting": "descOpticsValue",
    "body_and_interior": "descSalonValue",
    "parking_assistance": "descParktronicValue",
    "airbags": "descAirbagValue",
}
TEMPLATE_IDS.update(EQUIPMENT_IDS.values())

_PINIA = re.compile(r"window\.__PINIA__\s*=\s*")
_LD_JSON = re.compile(
    r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL
)
_AD_URL = re.compile(r"/auto_[^/]*?_(\d+)\.html$")
_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\s*$")
_THOUSANDS = re.compile(r"(\d+(?:[.,]\d+)?)\s*тис")
_KM = re.compile(r"(\d[\d\s]*)\s*км")
_LITRES = re.compile(r"^(\d+(?:[.,]\d+)?)\s*л\b")
_DATE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
_CDN = re.compile(r"^https://cdn\d*\.riastatic\.com/")
_PHONE = re.compile(r"\+?\d(?:[\s\-().]*\d){9,}")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_STREET = re.compile(
    r"\b(?:вул\.|вулиця|просп\.|проспект|пр-т|бульв\.|бульвар|пров\.|провулок|пл\.)\s*[^,.;\n]{1,60}"
    r"(?:,\s*(?:буд\.\s*)?\d+[\w/-]*)?",
    re.IGNORECASE,
)
_SPACES = re.compile(r"\s+")
_DOORS = re.compile(r"\b(\d+)\s+двер")
_SEATS = re.compile(r"\b(\d+)\s+місц")
_POWER_HP = re.compile(r"(\d+(?:[.,]\d+)?)\s*к\.\s*с\.")
_POWER_KW = re.compile(r"(\d+(?:[.,]\d+)?)\s*кВт\b")
_CONSUMPTION = re.compile(r"(місто|траса|змішаний)\s+(\d+(?:[.,]\d+)?)")


def _pinia(html: str) -> dict[str, Any] | None:
    match = _PINIA.search(html)
    if match is None:
        return None
    try:
        doc, _ = json.JSONDecoder().raw_decode(html, match.end())
    except ValueError:
        return None
    return doc if isinstance(doc, dict) else None


def _vehicles(html: str, ctx: Context) -> Iterator[dict[str, Any]]:
    for raw in _LD_JSON.findall(html):
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        for item in doc if isinstance(doc, list) else [doc]:
            types = item.get("@type") if isinstance(item, dict) else None
            if types == "Vehicle" or (isinstance(types, list) and "Vehicle" in types):
                yield item


def _ad_structure(state: Mapping[str, Any] | None) -> dict[str, Any]:
    """The ``page.structures`` entry of the ad (the one with ``additionalParams.autoId``)."""
    structures = ((state or {}).get("page") or {}).get("structures") or {}
    for value in structures.values() if isinstance(structures, dict) else []:
        if not isinstance(value, dict):
            continue
        params = value.get("additionalParams")
        if isinstance(params, dict) and params.get("autoId"):
            return dict(value)
    return {}


def _templates(node: Any, found: dict[str, dict[str, Any]], basic: list[dict[str, Any]]) -> None:
    if isinstance(node, dict):
        tid = node.get("id")
        if isinstance(tid, str):
            if tid in TEMPLATE_IDS and tid not in found:
                found[tid] = node
            elif re.fullmatch(r"basicInfoTableMainInfo\d+", tid):
                basic.append(node)
        for value in node.values():
            if isinstance(value, (dict, list)):
                _templates(value, found, basic)
    elif isinstance(node, list):
        for value in node:
            _templates(value, found, basic)


def _text(node: Mapping[str, Any] | None) -> str:
    if not node:
        return ""
    parts = [str(e.get("content") or "") for e in node.get("elements") or [] if e.get("type") == "Text"]
    return _SPACES.sub(" ", "".join(parts)).strip()


def _icon(node: Mapping[str, Any]) -> str:
    return next((str(e.get("style")) for e in node.get("elements") or [] if e.get("type") == "Icon"), "")


def _str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return _SPACES.sub(" ", value).strip() or None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("\u00a0", "").replace(" ", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _int(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None and number == int(number) else None


def mileage_km(text: str) -> int | None:
    lowered = text.casefold()
    if "без пробігу" in lowered:
        return 0
    if match := _THOUSANDS.search(lowered):
        return round(float(match.group(1).replace(",", ".")) * 1000)
    if match := _KM.search(lowered):
        return _int(match.group(1))
    return None


def fuel_and_engine(text: str) -> tuple[str | None, float | None]:
    fuel, _, rest = text.partition(",")
    match = _LITRES.match(rest.strip())
    return (fuel.strip() or None), (float(match.group(1).replace(",", ".")) if match else None)


def gearbox(text: str) -> str | None:
    return text if text and text.casefold() not in NOT_SPECIFIED else None


def image(src: Any) -> str | None:
    """The photo URL on one CDN host: the page picks a random ``cdnN`` shard per render."""
    if not isinstance(src, str) or not src.startswith("https://"):
        return None
    return _CDN.sub("https://cdn0.riastatic.com/", src)


def description(text: Any, limit: int) -> str | None:
    if not isinstance(text, str) or limit <= 0:
        return None
    masked = _STREET.sub("[адреса]", _EMAIL.sub("[e-mail]", _PHONE.sub("[телефон]", text)))
    clean = _SPACES.sub(" ", masked).strip()
    if len(clean) > limit:
        clean = clean[: limit - 1].rstrip() + "…"
    return clean or None


def _items(text: str) -> list[str]:
    """Preserve site labels and order; repeated responsive layouts add no duplicate options."""
    return list(dict.fromkeys(part.strip() for part in text.split("•") if part.strip()))


def _power(text: str, pattern: re.Pattern[str]) -> float | None:
    match = pattern.search(text)
    return float(match.group(1).replace(",", ".")) if match else None


def _details(found: Mapping[str, dict[str, Any]], ctx: Context) -> dict[str, Any]:
    """Only structured seller/site claims: no specification inference from the model name."""
    fields: dict[str, Any] = {}
    characteristics = _text(found.get("descCharacteristicsValue"))
    for field, pattern in (("doors", _DOORS), ("seats", _SEATS)):
        if match := pattern.search(characteristics):
            fields[field] = int(match.group(1))

    generation = _items(_text(found.get("basicInfoGenerationBase")))
    if not generation:
        generation = [part.strip() for part in _text(found.get("descGenerationBaseValue")).split(",", 1)]
        generation = [part for part in generation if part]
    for name, value in zip(("generation", "modification", "trim"), generation, strict=False):
        fields[name] = value

    engine = _text(found.get("descEngineEngine"))
    engine_hp = _power(engine, _POWER_HP)
    modification_hp = _power(fields.get("modification", ""), _POWER_HP)
    if engine_hp is not None or modification_hp is not None:
        fields["power_hp"] = engine_hp if engine_hp is not None else modification_hp
    if modification_hp is not None:
        fields["modification_power_hp"] = modification_hp
    if (power_kw := _power(engine, _POWER_KW)) is not None:
        fields["power_kw"] = power_kw
    if engine_hp is not None and modification_hp is not None and engine_hp != modification_hp:
        ctx.log.warning(
            f"engine detail gives {engine_hp:g} hp; modification gives {modification_hp:g} hp",
            code="extract.conflicting_power",
        )

    for field, template_id in (
        ("emission_standard", "descEcoStandartEcoStandart"),
        ("technical_state", "descTechStateText"),
        ("paint_condition", "descPaintConditionValue"),
    ):
        if text := _text(found.get(template_id)):
            fields[field] = text
    if "готовий до перевірки на сто" in _text(found.get("descTechStateValue")).casefold():
        fields["inspection_ready"] = True
    if options := _items(_text(found.get("descStateValue"))):
        fields["condition_options"] = options

    consumption = {
        {"місто": "city", "траса": "highway", "змішаний": "combined"}[label]: float(value.replace(",", "."))
        for label, value in _CONSUMPTION.findall(_text(found.get("descFuelRateValue")))
    }
    if consumption:
        fields["fuel_consumption_l_per_100km"] = consumption
    equipment = {
        category: options
        for category, template_id in EQUIPMENT_IDS.items()
        if (options := _items(_text(found.get(template_id))))
    }
    if equipment:
        fields["equipment"] = equipment
    return fields


def _geo(text: str) -> tuple[str | None, str | None]:
    """``UA, Кіровоградська обл., Кропивницький (Кіровоград), 25002`` -> region, city (no postcode)."""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if parts and re.fullmatch(r"[A-Z]{2}", parts[0]):
        parts = parts[1:]
    if parts and parts[-1].isdigit():
        parts = parts[:-1]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, (parts[0] if parts else None)


def _seller_type(params: Mapping[str, Any], segment: str) -> str | None:
    """``dealer`` (a company or a salon), ``private`` or None: a removed or sold ad shows no seller, and an
    unknown value must not overwrite the one stored from the active ad (a missing field is not a change)."""
    phone = (params.get("phone") or {}).get("data") or []
    data = {str(p[0]): str(p[1] or "") for p in phone if isinstance(p, list) and len(p) == 2}
    if data.get("isCompany") == "1" or data.get("companyId") or data.get("salonId"):
        return "dealer"
    if segment.casefold() in DEALER_SEGMENTS:
        return "dealer"
    return "private" if segment or data else None


def _status(offers: Mapping[str, Any], params: Mapping[str, Any], banner: str) -> str:
    availability = str(offers.get("availability") or "").rsplit("/", 1)[-1]
    if availability == "SoldOut" or "продан" in banner.casefold():
        return "sold"
    if availability == "InStock" and params.get("isActive") is not False:
        return "active"
    return "active" if params.get("isActive") is True else "unknown"


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    html = ctx.text()
    page_url = str((material.get("locator") or {}).get("url") or "")
    vehicles = list(_vehicles(html, ctx))
    vehicle = next(
        (v for v in vehicles if v.get("offers") or v.get("brand")), vehicles[0] if vehicles else {}
    )
    structure = _ad_structure(_pinia(html))
    ad = structure.get("additionalParams") or {}
    if not vehicle and not ad:
        return empty()
    found: dict[str, dict[str, Any]] = {}
    basic: list[dict[str, Any]] = []
    _templates(structure.get("templates") or [], found, basic)

    canonical = str(ad.get("link") or vehicle.get("url") or page_url)
    url_match = _AD_URL.search(urlsplit(canonical).path)
    ad_id = str(ad.get("autoId") or (url_match.group(1) if url_match else ""))
    # The page's own link spells the slug with "_" (auto_vaz_lada_...), the search results with "-"
    # (auto_vaz-lada_...); both open the same ad. The fetched URL keeps ``url`` equal to the search page's link.
    fetched = _AD_URL.search(urlsplit(page_url).path)
    url = page_url if fetched and fetched.group(1) == ad_id else canonical
    title = _text(found.get("basicInfoTitle")) or str(ad.get("title") or vehicle.get("name") or "").strip()
    site = (urlsplit(url).hostname or "").removeprefix("www.")
    offers = vehicle.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price, currency = _number(offers.get("price")), str(offers.get("priceCurrency") or "")
    if not (ad_id.isdigit() and title and site):
        return unrecognized("no ad id or title", signature="autoria-ad:no-id-or-title")
    if price is None or currency not in CURRENCIES:
        ctx.log.warning(f"ad {ad_id} has no price in JSON-LD offers", code="extract.missing_price")
        return unrecognized("no price in JSON-LD offers", signature="autoria-ad:no-price")

    fields: dict[str, Any] = {
        "site": site,
        "ad_id": ad_id,
        "url": url,
        "title": title,
        "price": price,
        "currency": currency,
    }
    brand = vehicle.get("brand")
    fields["make"] = _str(brand.get("name") if isinstance(brand, dict) else brand)
    fields["model"] = _str(vehicle.get("model"))
    year = _int(vehicle.get("productionDate"))
    if year is None and (match := _YEAR.search(title)):
        year = int(match.group(1))
    fields["year"] = year
    prices = ad.get("prices") or {}
    fields["price_usd"] = _number(prices.get("USD"))
    fields["price_uah"] = _number(prices.get("UAH"))

    for node in basic:
        icon, text = _icon(node), _text(node)
        if icon in MILEAGE_ICONS:
            fields["mileage_km"] = mileage_km(text)
        elif icon in GEARBOX_ICONS:
            fields["transmission"] = gearbox(text)
        elif icon in FUEL_ICONS:
            fields["fuel"], fields["engine_l"] = fuel_and_engine(text)
    if fields.get("mileage_km") is None:
        odometer = vehicle.get("mileageFromOdometer") or {}
        fields["mileage_km"] = _int(odometer.get("value")) if odometer.get("unitCode") == "KMT" else None
    fields["fuel"] = fields.get("fuel") or _str(vehicle.get("fuelType"))
    fields["transmission"] = fields.get("transmission") or gearbox(
        str(vehicle.get("vehicleTransmission") or "")
    )

    characteristics = _text(found.get("descCharacteristicsValue"))
    fields["body_type"] = characteristics.split("•", 1)[0].strip() or None
    fields["drive"] = _text(found.get("descDriveTypeDriveType")) or None
    fields["color"] = _text(found.get("descColorColor")) or _str(vehicle.get("color"))
    fields["region"], fields["city"] = _geo(_text(found.get("basicInfoTableMainInfoGeo")))
    fields["seller_type"] = _seller_type(ad, _text(found.get("sellerInfoSegment")))

    condition = CONDITIONS.get(
        str(vehicle.get("itemCondition") or offers.get("itemCondition") or "").rsplit("/", 1)[-1]
    )
    tech_state = _text(found.get("descTechStateValue")).casefold()
    if any(marker in tech_state for marker in DAMAGE_MARKERS):
        condition = "damaged"
    fields["condition"] = condition
    if match := _DATE.search(_text(found.get("advertStatisticPublicationData"))):
        fields["published_at"] = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    fields["image"] = image((ad.get("mainPhoto") or {}).get("src")) or next(
        (image(p.get("contentUrl")) for v in vehicles for p in v.get("image") or [] if isinstance(p, dict)),
        None,
    )
    fields["status"] = _status(offers, ad, _text(found.get("bannerStatusText")))
    fields["description"] = description(vehicle.get("description"), int(params["description_max_chars"]))
    fields.update(_details(found, ctx))
    return success([entity("ad_car", fields, completeness="full")])
