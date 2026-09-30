"""Price and availability of a Jane test site product - the scheduled "check prices" task.

Returns only ``sku``, ``price`` and ``availability`` with ``completeness: partial``: storage updates just
these fields of the product already collected by the catalog task and keeps the rest (TZ §6: a missing
field is not a deletion). ``empty`` for pages that are not products, ``unrecognized`` for a product page
without an identifier or a price.
"""

from __future__ import annotations

import json
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

AVAILABILITY = {"InStock": "in_stock", "OutOfStock": "out_of_stock", "PreOrder": "preorder"}


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page_type: str | None = None
        self.ld_json: list[str] = []
        self.itemprops: dict[str, str] = {}
        self.availability = ""
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "meta" and a.get("name") == "jane:page-type":
            self.page_type = a.get("content")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._capture = "ld"
            self.ld_json.append("")
        elif "itemprop" in a:
            if a.get("content"):
                self.itemprops[a["itemprop"]] = a["content"]
        elif "availability" in a.get("class", "").split():
            self._capture = "availability"

    def handle_endtag(self, tag: str) -> None:
        self._capture = None

    def handle_data(self, data: str) -> None:
        if self._capture == "ld":
            self.ld_json[-1] += data
        elif self._capture == "availability":
            self.availability += data


def _price(amount: Any, currency: Any) -> dict[str, Any] | None:
    try:
        return {"amount": float(amount), "currency": str(currency)}
    except (TypeError, ValueError):
        return None


def _availability(value: Any) -> str:
    return AVAILABILITY.get(str(value or "").strip().rsplit("/", 1)[-1], "unknown")


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = _Page()
    page.feed(ctx.text())
    offers: dict[str, Any] | None = None
    sku: Any = None
    for raw in page.ld_json:
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        if isinstance(doc, dict) and doc.get("@type") == "Product":
            offers, sku = doc.get("offers") or {}, doc.get("sku")
            break
    if offers is not None:
        price = _price(offers.get("price"), offers.get("priceCurrency") or params["default_currency"])
        availability = _availability(offers.get("availability"))
    elif page.page_type == "product":
        page_url = (material.get("locator") or {}).get("url")
        sku = urlsplit(page_url).path.rstrip("/").rsplit("/", 1)[-1] if page_url else None
        price = _price(page.itemprops.get("price"), params["default_currency"])
        availability = _availability(page.availability)
    else:
        return empty()

    if not sku:
        return unrecognized("product page without an identifier", signature="missing-field:sku")
    if price is None:
        ctx.log.warning("price not found", code="extract.missing_selector", selector="[itemprop=price]")
        return unrecognized("product page without a price", signature="missing-selector:[itemprop=price]")
    fields = {"sku": sku, "price": price, "availability": availability}
    return success([entity("product", fields, completeness="partial")])
