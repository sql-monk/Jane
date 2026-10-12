"""Public AUTO.RIA catalog cards from the server-rendered Pinia state.

The USD price is the amount displayed in the catalog, which the site may convert
from the seller's currency. It is never inferred from a different advertisement.
The entity type is fixed (``ad_car``): the AUTO.RIA catalog lists vehicles only.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterator
from typing import Any
from urllib.parse import urljoin, urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

ENTITY_TYPE = "ad_car"
_STATE = re.compile(r"window\.__PINIA__\s*=\s*")
_AD_PATH = re.compile(r"/uk/auto_[^/]*_(\d+)\.html$")


def _cards(node: Any) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        if node.get("type") == "AdvertisementCardTemplate":
            component = node.get("component")
            ad = component.get("advertisementCard") if isinstance(component, dict) else None
            data = ad.get("data") if isinstance(ad, dict) else None
            if isinstance(data, dict):
                yield data
            return
        for value in node.values():
            yield from _cards(value)
    elif isinstance(node, list):
        for value in node:
            yield from _cards(value)


def _text(value: Any) -> str:
    return " ".join(value.split()) if isinstance(value, str) else ""


def _amount(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number >= 0 else None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = ctx.text()
    mark = _STATE.search(page)
    if mark is None:
        return empty()
    try:
        state, _ = json.JSONDecoder().raw_decode(page, mark.end())
    except ValueError:
        return unrecognized("AUTO.RIA state is not JSON", signature="autoria:invalid-state")
    if not isinstance(state, dict):
        return unrecognized("AUTO.RIA state is not an object", signature="autoria:invalid-state")
    listing = state.get("list")
    lists = listing.get("lists") if isinstance(listing, dict) else None
    items = lists.get("items") if isinstance(lists, dict) else None
    cards = list(_cards(items))
    page_url = str((material.get("locator") or {}).get("url") or "https://auto.ria.com/uk/")
    found: dict[str, dict[str, Any]] = {}
    for card in cards:
        listing_id = str(card.get("id") or "")
        link = urljoin(page_url, _text(card.get("link")))
        parsed = urlsplit(link)
        match = _AD_PATH.fullmatch(parsed.path)
        title_node = card.get("title")
        title = _text(title_node.get("content")) if isinstance(title_node, dict) else ""
        if not (
            match
            and listing_id.isdigit()
            and match.group(1) == listing_id
            and parsed.scheme == "https"
            and parsed.hostname == "auto.ria.com"
            and title
        ):
            continue
        fields: dict[str, Any] = {
            "site": "auto.ria.com",
            "listing_id": listing_id,
            "title": title,
            "url": link,
        }
        price = card.get("price")
        amount = _amount(price.get("USD")) if isinstance(price, dict) else None
        if amount is not None:
            fields["price"] = {"amount": amount, "currency": "USD"}
        for info in card.get("basicInfo") or []:
            if not isinstance(info, dict):
                continue
            icon = info.get("icon")
            data = icon.get("data") if isinstance(icon, dict) else None
            if (
                isinstance(data, dict)
                and data.get("style") == "ic_16_location"
                and (location := _text(info.get("content")))
            ):
                fields["location"] = location
        found.setdefault(listing_id, fields)
    if not found:
        return (
            unrecognized("Catalog cards have no valid id, title or URL", signature="autoria:invalid-cards")
            if cards
            else empty()
        )
    scope = str((material.get("source") or {}).get("source_id") or "local")
    return success(
        [
            entity(
                ENTITY_TYPE,
                fields,
                key={
                    "scope": scope,
                    "natural": {"site": fields["site"], "listing_id": fields["listing_id"]},
                },
            )
            for fields in found.values()
        ]
    )
