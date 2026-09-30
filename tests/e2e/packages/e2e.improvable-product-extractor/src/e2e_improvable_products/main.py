"""E2E fixture extractor (WP-13, S-M2-07): product cards of the test site with in-stock offers only.

A human-written extractor with a known gap, so that a real run produces problem results that the source
assistant improves (ТЗ §9):

* JSON-LD ``Product`` whose offer availability is ``InStock`` -> ``success`` (full card);
* any other availability (``OutOfStock``, ``PreOrder`` ...) -> ``unrecognized`` with a partial card and
  the signature ``unknown-availability``;
* no JSON-LD ``Product`` -> ``empty``.
"""

from __future__ import annotations

import json
import re
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

_LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


def _product(html: str) -> dict[str, Any] | None:
    for block in _LD_JSON.findall(html):
        try:
            doc = json.loads(block)
        except ValueError:
            continue
        if isinstance(doc, dict) and doc.get("@type") == "Product":
            return doc
    return None


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    ld = _product(ctx.text())
    if ld is None:
        return empty()
    offers = ld.get("offers") or {}
    fields: dict[str, Any] = {"sku": ld.get("sku"), "title": ld.get("name")}
    try:
        fields["price"] = {"amount": float(offers["price"]), "currency": str(offers["priceCurrency"])}
    except (KeyError, TypeError, ValueError):
        fields["price"] = None
    availability = str(offers.get("availability", "")).rsplit("/", 1)[-1]
    if availability != "InStock":
        ctx.log.warning("offer availability is not handled", code="extract.unknown_availability")
        return unrecognized(
            "offer availability is not handled by this extractor",
            signature="unknown-availability",
            entities=[entity("product", fields, completeness="partial")],
        )
    fields["availability"] = "in_stock"
    return success([entity("product", fields, completeness="full")])
