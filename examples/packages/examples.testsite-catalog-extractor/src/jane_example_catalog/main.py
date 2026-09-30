"""Full product cards of the Jane test site (tests/fixtures/testsite) - the "collect the catalog" task.

Reads the schema.org ``Product`` JSON-LD block (fallback: microdata) and the category link of a product
page. Returns every field the page has (``completeness: full``). States of TZ §9: ``success`` (a product
card), ``empty`` (not a product page), ``unrecognized`` (a product page without an identifier or price).
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

AVAILABILITY = {"InStock": "in_stock", "OutOfStock": "out_of_stock", "PreOrder": "preorder"}
CATEGORY_PATH = re.compile(r"/catalog/([a-z0-9-]+)/?$")


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page_type: str | None = None
        self.ld_json: list[str] = []
        self.itemprops: dict[str, str] = {}
        self.availability = ""
        self.category: str | None = None
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "meta" and a.get("name") == "jane:page-type":
            self.page_type = a.get("content")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._capture = "ld"
            self.ld_json.append("")
        elif tag == "a" and self.category is None:
            match = CATEGORY_PATH.search(urlsplit(a.get("href", "")).path)
            if match:
                self.category = match.group(1)
        elif "itemprop" in a:
            if a.get("content"):
                self.itemprops[a["itemprop"]] = a["content"]
            else:
                self._capture = "itemprop:" + a["itemprop"]
        elif "availability" in a.get("class", "").split():
            self._capture = "availability"

    def handle_endtag(self, tag: str) -> None:
        self._capture = None

    def handle_data(self, data: str) -> None:
        if self._capture == "ld":
            self.ld_json[-1] += data
        elif self._capture == "availability":
            self.availability += data
        elif self._capture and self._capture.startswith("itemprop:"):
            name = self._capture.split(":", 1)[1]
            self.itemprops[name] = self.itemprops.get(name, "") + data


def _json_ld_product(page: _Page, ctx: Context) -> dict[str, Any] | None:
    for raw in page.ld_json:
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        if isinstance(doc, dict) and doc.get("@type") == "Product":
            return doc
    return None


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
    page_url = (material.get("locator") or {}).get("url")
    ld = _json_ld_product(page, ctx)
    if ld is not None:
        offers = ld.get("offers") or {}
        sku = ld.get("sku")
        title = ld.get("name")
        price = _price(offers.get("price"), offers.get("priceCurrency") or params["default_currency"])
        availability = _availability(offers.get("availability"))
    elif page.page_type == "product":
        ctx.log.info("no JSON-LD, using microdata", code="extract.microdata_fallback")
        sku = urlsplit(page_url).path.rstrip("/").rsplit("/", 1)[-1] if page_url else None
        title = page.itemprops.get("name")
        price = _price(page.itemprops.get("price"), params["default_currency"])
        availability = _availability(page.availability)
    else:
        return empty()

    fields = {
        "sku": sku or None,
        "title": title or None,
        "price": price,
        "availability": availability,
        "category": page.category,
        "url": page_url if params["include_url"] else None,
    }
    if not fields["sku"]:
        return unrecognized("product page without an identifier", signature="missing-field:sku")
    if price is None:
        ctx.log.warning("price not found", code="extract.missing_selector", selector="[itemprop=price]")
        return unrecognized(
            "product page without a price",
            signature="missing-selector:[itemprop=price]",
            entities=[entity("product", fields, completeness="partial")],
        )
    return success([entity("product", fields, completeness="full")])
