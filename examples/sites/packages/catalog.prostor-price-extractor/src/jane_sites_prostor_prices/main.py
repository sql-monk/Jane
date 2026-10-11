"""Prices and availability of prostor.ua products from category pages - the "update prices" task.

Every product tile of a category page (``ol.product-items > li.product-item``) has the Magento product id
(``data-id``, also ``data-product-id`` of its price box), the current price (``[data-price-type=finalPrice]
[data-price-amount]``), the price before a discount (``[data-price-type=oldPrice]``) and the stock flag of the
wish-list button (``data-post`` JSON ``data.is_in_stock``). Each tile becomes a partial ``product`` entity
(``completeness: partial``) with only ``shop``, ``product_id``, ``price``, ``currency``, ``availability`` and
``old_price`` - the key fields of the full card of ``catalog.prostor-product-extractor``, so storage updates
these fields of the same entity and keeps the rest (TZ §6: a missing field is not a deletion). A tile without a
discount clears ``old_price`` explicitly (``cleared``), so an ended discount does not linger.

An out-of-stock tile without a price updates availability only and preserves the last observed price and
discount. States (TZ §9): ``success`` - a category with priced or known out-of-stock tiles; ``empty`` - no
product tiles; ``unrecognized`` - tiles without prices or a known out-of-stock status (the markup changed).
"""

from __future__ import annotations

import json
from html.parser import HTMLParser
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized


def _number(value: Any) -> float | None:
    try:
        number = float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


class _Tiles(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tiles: list[dict[str, Any]] = []
        self._list_depth = 0  # nesting of <ol> inside the product list; 0 - outside it

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        classes = a.get("class", "").split()
        if tag == "ol":
            if self._list_depth:
                self._list_depth += 1
            elif "product-items" in classes:
                self._list_depth = 1
            return
        if not self._list_depth:
            return
        if tag == "li" and "product-item" in classes:
            self.tiles.append({"id": a.get("data-id") or None})
            return
        if not self.tiles:
            return
        tile = self.tiles[-1]
        if a.get("data-role") == "priceBox" and a.get("data-product-id"):
            tile.setdefault("box_id", a["data-product-id"])
        price_type = a.get("data-price-type")
        if price_type in ("finalPrice", "oldPrice") and a.get("data-price-amount"):
            tile.setdefault(price_type, a["data-price-amount"])
        if a.get("data-action") == "add-to-wishlist" and a.get("data-post"):
            try:
                post = json.loads(a["data-post"])
            except ValueError:
                post = {}
            stock = (post.get("data") or {}).get("is_in_stock") if isinstance(post, dict) else None
            if stock is not None:
                tile.setdefault("in_stock", str(stock))

    def handle_endtag(self, tag: str) -> None:
        if tag == "ol" and self._list_depth:
            self._list_depth -= 1


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = _Tiles()
    page.feed(ctx.text())
    page.close()
    if not page.tiles:
        return empty()

    entities = []
    seen: set[str] = set()
    unpriced = 0
    for tile in page.tiles:
        product_id = tile.get("box_id") or tile.get("id")
        price = _number(tile.get("finalPrice"))
        stock = tile.get("in_stock")
        availability = {"1": "in_stock", "0": "out_of_stock"}.get(stock) if stock is not None else None
        if not product_id or (price is None and availability != "out_of_stock"):
            unpriced += 1
            continue
        if product_id in seen:
            continue
        seen.add(product_id)
        if price is None:
            entities.append(
                entity(
                    "product",
                    {"shop": params["shop"], "product_id": product_id, "availability": availability},
                    completeness="partial",
                )
            )
            continue
        old_price = _number(tile.get("oldPrice"))
        if old_price is not None and old_price <= price:
            old_price = None
        fields = {
            "shop": params["shop"],
            "product_id": product_id,
            "price": price,
            "currency": params["default_currency"],
            "availability": availability,
            "old_price": old_price,
        }
        cleared = ["old_price"] if old_price is None else None
        entities.append(entity("product", fields, cleared=cleared, completeness="partial"))
    if unpriced:
        ctx.log.warning(
            f"{unpriced} product tile(s) without an id or a price skipped",
            code="extract.missing_selector",
            selector="[data-price-type=finalPrice]",
        )
    if not entities:
        return unrecognized(
            "category page with product tiles but without prices",
            signature="missing-selector:[data-price-type=finalPrice]",
        )
    return success(entities)
