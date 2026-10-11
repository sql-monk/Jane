"""DIM.RIA catalog advertisements from its public server-rendered page state."""

from __future__ import annotations

import json
import math
import re
from typing import Any
from urllib.parse import urljoin, urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

_STATE = re.compile(r"window\.__INITIAL_STATE__\s*=\s*")
_AD_PATH = re.compile(r"/uk/realty-[^/]+-(\d+)\.html$")
_CURRENCIES = {"$": "USD", "€": "EUR", "грн": "UAH"}
_CURRENCY_IDS = {1: "USD", 2: "EUR", 3: "UAH"}


def _text(value: Any) -> str:
    return " ".join(value.split()) if isinstance(value, str) else ""


def _amount(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        number = float(str(value).replace(" ", "").replace("\u00a0", "").replace(",", "."))
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = ctx.text()
    mark = _STATE.search(page)
    if mark is None:
        return empty()
    try:
        state, _ = json.JSONDecoder().raw_decode(page, mark.end())
    except ValueError:
        return unrecognized("DIM.RIA state is not JSON", signature="dimria:invalid-state")
    if not isinstance(state, dict):
        return unrecognized("DIM.RIA state is not an object", signature="dimria:invalid-state")
    catalog = state.get("catalog")
    items = catalog.get("realtyForCatalog") if isinstance(catalog, dict) else None
    ads = (
        [item for item in items if isinstance(item, dict) and item.get("realty_id")]
        if isinstance(items, list)
        else []
    )
    found: dict[str, dict[str, Any]] = {}
    for ad in ads:
        listing_id = str(ad.get("realty_id") or "")
        path = _text(ad.get("beautiful_url"))
        link = urljoin("https://dom.ria.com/uk/", path)
        parsed = urlsplit(link)
        match = _AD_PATH.fullmatch(parsed.path)
        title = _text(ad.get("imgSeoALT"))
        if not (
            listing_id.isdigit()
            and match
            and match.group(1) == listing_id
            and title
            and parsed.scheme == "https"
            and parsed.hostname == "dom.ria.com"
        ):
            continue
        fields: dict[str, Any] = {
            "site": "dom.ria.com",
            "listing_id": listing_id,
            "title": title,
            "url": link,
        }
        amount = _amount(ad.get("price"))
        currency = _CURRENCIES.get(_text(ad.get("currency_type")))
        if not currency:
            currency = _CURRENCY_IDS.get(ad.get("currencyId"))
        if amount is not None and currency:
            fields["price"] = {"amount": amount, "currency": currency}
        if location := _text(ad.get("city_name_uk")):
            fields["location"] = location
        found.setdefault(listing_id, fields)
    if not found:
        return (
            unrecognized("Catalog ads have no valid id, title or URL", signature="dimria:invalid-cards")
            if ads
            else empty()
        )
    scope = str((material.get("source") or {}).get("source_id") or "local")
    return success(
        [
            entity(
                "classified_ad",
                fields,
                key={
                    "scope": scope,
                    "natural": {"site": fields["site"], "listing_id": fields["listing_id"]},
                },
            )
            for fields in found.values()
        ]
    )
