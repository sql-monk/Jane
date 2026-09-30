"""Parse a testsite product after an optional, task-configured delay."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

_LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    delay = float(params["delay_seconds"])
    if delay:
        print("e2e-slow-extractor-started", flush=True)
    time.sleep(delay)
    for raw in _LD_JSON.findall(ctx.text()):
        try:
            product = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(product, dict) or product.get("@type") != "Product":
            continue
        offer = product.get("offers") or {}
        return success(
            [
                entity(
                    "product",
                    {
                        "sku": str(product["sku"]),
                        "title": str(product["name"]),
                        "price": {"amount": float(offer["price"]), "currency": str(offer["priceCurrency"])},
                    },
                    completeness="full",
                )
            ]
        )
    return empty()
