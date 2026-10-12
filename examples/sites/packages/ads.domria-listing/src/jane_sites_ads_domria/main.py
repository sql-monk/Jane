"""Classified ads from the catalog pages of DIM.RIA (dom.ria.com): flats for rent and for sale.

A catalog page (``/uk/arenda-kvartir/kiev/``, ``?page=N``) is rendered on the server together with the page
state ``window.__INITIAL_STATE__``; ``catalog.realtyForCatalog`` holds the ads of the page (20 plus promoted
ones) with every field of the ad card, so the cards themselves are not fetched. Each ad becomes a complete
``ad_realty`` (DIM.RIA lists real estate only, so the type is fixed) keyed by the site and ``realty_id``;
newbuild promo blocks of the list (no ``realty_id``) are skipped.

No personal data: the seller (name, phones, avatar, user id), the street, house and flat numbers, the
coordinates and the free-text description (owners write addresses and phones there) are left out.

A page without the catalog state (or with an empty list) is ``empty``; a catalog whose ads lack an id, a URL
or a price is ``unrecognized``.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from dateutil.zoneinfo import get_zonefile_instance  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

SITE = "dom.ria.com"
ENTITY_TYPE = "ad_realty"  # the only type of output.entities: the site lists real estate only
BASE_URL = "https://dom.ria.com/uk/"
PHOTO_BASE = "https://cdn.riastatic.com/photos/"
STATE_MARK = "window.__INITIAL_STATE__="
# The site's timestamps ("2026-10-09 13:05:42") are Kyiv local time; dateutil's bundled tz database
# keeps the result independent of the system zoneinfo of the sandbox.
SITE_TZ = get_zonefile_instance().get("Europe/Kyiv") or get_zonefile_instance().get("Europe/Kiev")
CURRENCY_SIGNS = {"$": "USD", "грн": "UAH", "€": "EUR"}
CURRENCY_IDS = {1: "USD", 2: "EUR", 3: "UAH"}


class _BadState(ValueError):
    pass


def _state(text: str) -> dict[str, Any] | None:
    start = text.find(STATE_MARK)
    if start < 0:
        return None
    try:
        state, _ = json.JSONDecoder().raw_decode(text, start + len(STATE_MARK))
    except ValueError as exc:
        raise _BadState(str(exc)) from None
    if not isinstance(state, dict):
        raise _BadState("the page state is not an object")
    return state


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        number = float(str(value).replace(",", ".").replace(" ", ""))
    except ValueError:
        return None
    return number


def _int(value: Any) -> int | None:
    number = _num(value)
    return int(number) if number is not None and number == int(number) else None


def _text(value: Any) -> str | None:
    text = " ".join(value.split()) if isinstance(value, str) else ""
    return text or None


def _number_text(value: Any) -> str | None:
    number = _num(value)
    if number is None or number <= 0:
        return None
    return str(int(number)) if number == int(number) else str(number)


def _local_time(value: Any) -> str | None:
    """'2026-10-09 13:05:42' (Kyiv time) -> '2026-10-09T13:05:42+03:00'."""
    try:
        moment = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return moment.replace(tzinfo=SITE_TZ).isoformat()


def _currency(ad: dict[str, Any]) -> str | None:
    sign = _text(ad.get("currency_type"))
    if sign in CURRENCY_SIGNS:
        return CURRENCY_SIGNS[sign]
    return CURRENCY_IDS.get(_int(ad.get("currencyId")) or 0)


def _deal_type(advert_type: str | None) -> str:
    name = (advert_type or "").lower()
    if "оренд" in name:
        return "rent"
    if "продаж" in name:
        return "sale"
    if "обмін" in name:
        return "exchange"
    return "unknown"


def _region(state_name: str | None) -> str | None:
    if not state_name:
        return None
    return state_name if "обл" in state_name.lower() else f"{state_name} область"


def _image(ad: dict[str, Any]) -> str | None:
    photo = ad.get("mainPhoto")
    if isinstance(photo, str) and photo.startswith("https://"):
        return photo
    path = _text(ad.get("main_photo"))
    return PHOTO_BASE + path.lstrip("/") if path else None


def _params(ad: dict[str, Any]) -> dict[str, str]:
    params = {
        "Тип нерухомості": _text(ad.get("realty_type_name_uk")),
        "Житлова площа, м²": _number_text(ad.get("living_square_meters")),
        "Площа кухні, м²": _number_text(ad.get("kitchen_square_meters")),
        "Метро": _text(ad.get("metro_station_name_uk")),
        "Тип стін": _text(ad.get("wall_type")),
        "Новобудова": _text(ad.get("user_newbuild_name_uk")),
    }
    return {k: v for k, v in params.items() if v}


def _fields(ad: dict[str, Any]) -> dict[str, Any] | None:
    ad_id = _int(ad.get("realty_id"))
    path = _text(ad.get("beautiful_url"))
    price = _num(ad.get("price"))
    currency = _currency(ad)
    if not ad_id or not path or price is None or price < 0 or not currency:
        return None
    realty_type = _text(ad.get("realty_type_name_uk"))
    advert_type = _text(ad.get("advert_type_name_uk"))
    city = _text(ad.get("city_name_uk"))
    rooms = _int(ad.get("rooms_count"))
    area = _num(ad.get("total_square_meters"))
    title = _text(ad.get("imgSeoALT")) or ", ".join(
        p
        for p in (
            advert_type,
            realty_type,
            f"{rooms}-кімн." if rooms else None,
            f"{_number_text(area)} м²" if area else None,
            city,
        )
        if p
    )
    floors = _int(ad.get("floors_count"))
    per_m2 = _num(ad.get("price_item"))
    agency = _int(ad.get("agency_id")) or 0
    category_path = [p for p in (_text(ad.get("realty_type_parent_name_uk")), realty_type, advert_type) if p]
    return {
        "site": SITE,
        "ad_id": str(ad_id),
        "url": BASE_URL + path.lstrip("/"),
        "title": title,
        "category": ", ".join(p for p in (realty_type, advert_type) if p) or "Нерухомість",
        "category_path": category_path or None,
        "price": price,
        "currency": currency,
        "deal_type": _deal_type(advert_type),
        "city": city,
        "region": _region(_text(ad.get("state_name_uk"))),
        "district": _text(ad.get("district_name_uk")),
        "published_at": _local_time(ad.get("publishing_date")),
        "refreshed_at": _local_time(ad.get("actualized_at")),
        "seller_type": "business" if agency > 0 else "unknown",
        "params": _params(ad) or None,
        "image": _image(ad),
        "area_m2": area if area and area > 0 else None,
        "rooms": rooms,
        "floor": _int(ad.get("floor")),
        "floors_total": floors if floors else None,
        "price_per_m2": per_m2 if per_m2 and per_m2 > 0 else None,
    }


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    try:
        state = _state(ctx.text())
    except _BadState as exc:
        ctx.log.warning(f"page state is not JSON: {exc}", code="extract.bad_state")
        return unrecognized("window.__INITIAL_STATE__ is not JSON", signature="domria:bad-state")
    catalog = (state or {}).get("catalog")
    items = catalog.get("realtyForCatalog") if isinstance(catalog, dict) else None
    ads = [i for i in items if isinstance(i, dict) and i.get("realty_id")] if isinstance(items, list) else []
    if not ads:
        return empty()
    found: dict[str, dict[str, Any]] = {}
    skipped = 0
    for ad in ads:
        fields = _fields(ad)
        if fields is None:
            skipped += 1
            continue
        found.setdefault(fields["ad_id"], fields)
    if skipped:
        ctx.log.warning(f"{skipped} ad(s) without an id, a URL or a price", code="extract.missing_field")
    if not found:
        return unrecognized("catalog ads without an id, a URL or a price", signature="domria:missing-fields")
    return success([entity(ENTITY_TYPE, f, completeness="full") for f in found.values()])
