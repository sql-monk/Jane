"""Extract a product from a deterministic SKU|title input."""

from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    parts = ctx.text().strip().split("|", 1)
    if len(parts) != 2 or not all(parts):
        return empty()
    sku, title = parts
    return success([entity("product", {"sku": sku, "title": title})])
