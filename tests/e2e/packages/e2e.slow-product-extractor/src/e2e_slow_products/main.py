"""Parse a testsite product after an optional, task-configured delay (``params.delay_seconds``).

The delay keeps one invocation in flight long enough for the reliability scenarios: R-01 lets an
orchestrator lease expire while the call is still running, R-03 partitions storage while the extraction
still holds the next storage stage back.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

_LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    delay = float(params.get("delay_seconds", 0))
    if delay > 0:
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
