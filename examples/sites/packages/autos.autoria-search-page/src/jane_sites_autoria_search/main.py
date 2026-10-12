"""AUTO.RIA (auto.ria.com) search results page ``/uk/search/?...`` -> a partial ``ad_car`` per listed ad.

The search page is rendered on the server; its results are in the page state ``window.__PINIA__ = {...}``
(Vue/Pinia server state) at ``list.lists.items.items``: templates of type ``AdvertisementCardTemplate`` (also
nested, e.g. the "offer of the day" block) whose ``component.advertisementCard.data`` is one ad: ``id``,
``link``, ``title`` (``<make> <model> <year>``), ``price`` converted to USD and UAH, ``basicInfo`` (mileage,
gearbox, fuel and engine - told apart by their icon), the first photo (its ``alt`` starts with the body type),
the "VIN checked" badge and the "sold" badge.

The page does not show the seller's own price currency (an ad priced in EUR is listed in USD and UAH), so the
entity is a partial update (``completeness: partial``) without ``price``/``currency``: the full ad comes from the
ad page (package ``autos.autoria-ad-page``, same ``ad_car`` key ``site`` + ``ad_id``). Re-reading the search
pages every run refreshes the converted prices, mileage and status of the listed ads. Mileage, gearbox and fuel
are parsed from the same texts as on the ad page, so both packages write identical values. ``empty`` for a page
without search results.

The entity type is fixed to ``ad_car``, the type of the ad page package: the search covers passenger cars only
(``category=1``), so a partial update always lands on the same entity as the full card.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from typing import Any
from urllib.parse import urljoin, urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

NOT_SPECIFIED = {"не вказано", "не указано"}
MILEAGE_ICONS = {"ic_16_speedometer"}
GEARBOX_ICONS = {"ic_16_automat", "ic_16_transmission"}
FUEL_ICONS = {"ic_16_fuel", "ic_16_battery", "ic_16_hybrid"}
VIN_CHECKED = "перевірений vin"
SOLD = "продано"

_PINIA = re.compile(r"window\.__PINIA__\s*=\s*")
_AD_URL = re.compile(r"/auto_[^/]*?_(\d+)\.html$")
_YEAR = re.compile(r"\b(19\d{2}|20\d{2})\s*$")
_THOUSANDS = re.compile(r"(\d+(?:[.,]\d+)?)\s*тис")
_KM = re.compile(r"(\d[\d\s]*)\s*км")
_LITRES = re.compile(r"^(\d+(?:[.,]\d+)?)\s*л\b")
_CDN = re.compile(r"^https://cdn\d*\.riastatic\.com/")
_SPACES = re.compile(r"\s+")


def _pinia(html: str) -> dict[str, Any] | None:
    match = _PINIA.search(html)
    if match is None:
        return None
    try:
        doc, _ = json.JSONDecoder().raw_decode(html, match.end())
    except ValueError:
        return None
    return doc if isinstance(doc, dict) else None


def _cards(node: Any) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        if node.get("type") == "AdvertisementCardTemplate":
            data = ((node.get("component") or {}).get("advertisementCard") or {}).get("data")
            if isinstance(data, dict):
                yield data
            return
        for value in node.values():
            yield from _cards(value)
    elif isinstance(node, list):
        for value in node:
            yield from _cards(value)


def _clean(text: Any) -> str:
    return _SPACES.sub(" ", text).strip() if isinstance(text, str) else ""


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def mileage_km(text: str) -> int | None:
    lowered = text.casefold()
    if "без пробігу" in lowered:
        return 0
    if match := _THOUSANDS.search(lowered):
        return round(float(match.group(1).replace(",", ".")) * 1000)
    if match := _KM.search(lowered):
        digits = re.sub(r"\D", "", match.group(1))
        return int(digits) if digits else None
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


def _badges(container: Mapping[str, Any]) -> list[str]:
    texts = []
    for badge in container.get("badges") or []:
        if isinstance(badge, dict) and badge.get("type") == "BadgeTemplate":
            parts = [e.get("content") for e in badge.get("elements") or [] if e.get("type") == "Text"]
            texts.append(_clean(" ".join(str(p) for p in parts if p)).casefold())
    return texts


def _status(container: Mapping[str, Any]) -> str:
    center = container.get("centerBadge")
    if isinstance(center, dict) and SOLD in _clean(center.get("content")).casefold():
        return "sold"
    return "active" if container.get("active") is True else "unknown"


def _fields(card: Mapping[str, Any], page_url: str) -> dict[str, Any] | None:
    link = urljoin(page_url, str(card.get("link") or ""))
    match = _AD_URL.search(urlsplit(link).path)
    ad_id = str(card.get("id") or "")
    title = _clean((card.get("title") or {}).get("content"))
    site = (urlsplit(link).hostname or "").removeprefix("www.")
    if not (match and ad_id.isdigit() and match.group(1) == ad_id and title and site):
        return None
    fields: dict[str, Any] = {"site": site, "ad_id": ad_id, "url": link, "title": title}
    if year := _YEAR.search(title):
        fields["year"] = int(year.group(1))
    price = card.get("price") or {}
    fields["price_usd"] = _number(price.get("USD"))
    fields["price_uah"] = _number(price.get("UAH"))
    for info in card.get("basicInfo") or []:
        icon = str((((info.get("icon") or {}).get("data")) or {}).get("style") or "")
        text = _clean(info.get("content"))
        if icon in MILEAGE_ICONS:
            fields["mileage_km"] = mileage_km(text)
        elif icon in GEARBOX_ICONS:
            fields["transmission"] = gearbox(text)
        elif icon in FUEL_ICONS:
            fields["fuel"], fields["engine_l"] = fuel_and_engine(text)
    photos = [p for p in card.get("photos") or [] if isinstance(p, dict)]
    if photos:
        alt = _clean(photos[0].get("alt"))
        body, found, _ = alt.partition(f" {title} ")
        fields["body_type"] = body.strip() if found and body.strip() else None
        fields["image"] = image(photos[0].get("src"))
    container = card.get("photoContainer") or {}
    fields["vin_checked"] = VIN_CHECKED in _badges(container)
    fields["status"] = _status(container)
    return fields


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    state = _pinia(ctx.text())
    results = (((state or {}).get("list") or {}).get("lists") or {}).get("items") or {}
    page_url = str((material.get("locator") or {}).get("url") or "")
    found: dict[str, dict[str, Any]] = {}
    for card in _cards(results.get("items") or []):
        fields = _fields(card, page_url)
        if fields is None:
            ctx.log.warning("search result without an ad id, link or title skipped", code="extract.bad_card")
            continue
        found.setdefault(fields["ad_id"], fields)
    if not found:
        return empty()
    return success([entity("ad_car", fields, completeness="partial") for fields in found.values()])
