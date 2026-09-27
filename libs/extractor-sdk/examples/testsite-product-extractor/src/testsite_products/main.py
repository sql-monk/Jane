"""Example extractor: product cards of the Jane test site (tests/fixtures/testsite).

Reads schema.org JSON-LD first and falls back to microdata. Shows the four states of TZ §9:
``success`` (product found), ``empty`` (not a product page), ``unrecognized`` (product page without a
price), ``failed`` (an exception - handled by the runtime).
"""

from __future__ import annotations

import json
from html.parser import HTMLParser
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

AVAILABILITY = {"InStock": "in_stock", "OutOfStock": "out_of_stock"}


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page_type: str | None = None
        self.ld_json: list[str] = []
        self.h1 = ""
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
        elif tag == "h1":
            self._capture = "h1"
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
        elif self._capture == "h1":
            self.h1 += data
        elif self._capture == "availability":
            self.availability += data
        elif self._capture and self._capture.startswith("itemprop:"):
            name = self._capture.split(":", 1)[1]
            self.itemprops[name] = self.itemprops.get(name, "") + data


def _ld_products(page: _Page, ctx: Context) -> list[dict[str, Any]]:
    products = []
    for raw in page.ld_json:
        try:
            doc = json.loads(raw)
        except ValueError:
            ctx.log.warning("invalid JSON-LD block skipped", code="extract.bad_json_ld")
            continue
        if isinstance(doc, dict) and doc.get("@type") == "Product":
            products.append(doc)
    return products


def _price(amount: Any, currency: Any) -> dict[str, Any] | None:
    try:
        return {"amount": float(amount), "currency": str(currency)}
    except (TypeError, ValueError):
        return None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = _Page()
    page.feed(ctx.text())
    page_url = (material.get("locator") or {}).get("url")
    url = page_url if params.get("include_url", True) else None
    products = _ld_products(page, ctx)

    if products:
        ld = products[0]
        offers = ld.get("offers") or {}
        availability = str(offers.get("availability", "")).rsplit("/", 1)[-1]
        fields = {
            "sku": ld.get("sku"),
            "title": ld.get("name"),
            "price": _price(offers.get("price"), offers.get("priceCurrency") or params["default_currency"]),
            "availability": AVAILABILITY.get(availability, "unknown"),
            "url": url,
        }
    elif page.page_type == "product":
        ctx.log.info("no JSON-LD, using microdata", code="extract.microdata_fallback")
        fields = {
            "sku": page_url.rstrip("/").rsplit("/", 1)[-1] if page_url else None,
            "title": page.itemprops.get("name") or page.h1.strip() or None,
            "price": _price(page.itemprops.get("price"), params["default_currency"]),
            "availability": AVAILABILITY.get(page.availability.strip(), "unknown"),
            "url": url,
        }
    else:
        return empty()

    if not fields["sku"]:
        return unrecognized("product page without an identifier", signature="missing-field:sku")
    if fields["price"] is None:
        ctx.log.warning("price not found", code="extract.missing_selector", selector="[itemprop=price]")
        return unrecognized(
            "product page without a price",
            signature="missing-selector:[itemprop=price]",
            entities=[entity("product", fields, completeness="partial")],
        )
    return success([entity("product", fields, completeness="full")])
