"""Public RIA.com catalog cards; each price stays attached to its advertisement."""

from __future__ import annotations

import math
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

_VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
_PATH = re.compile(r"/uk/[^/]+-(\d+)\.html$")
_PRICE = re.compile(r"^(\d[\d\s\u00a0]*(?:[.,]\d+)?)\s*(грн\.?|UAH|USD|EUR|\$|€)$", re.IGNORECASE)
_CURRENCIES = {"грн": "UAH", "грн.": "UAH", "uah": "UAH", "usd": "USD", "$": "USD", "eur": "EUR", "€": "EUR"}


def _clean(text: str) -> str:
    return " ".join(text.split())


class _Cards(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.stack: list[tuple[str, set[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        identifier = attributes.get("id") or ""
        if self.current is None:
            if tag != "div" or "ticket-clean" not in classes or not identifier.startswith("adv_"):
                return
            self.current = {"id": identifier.removeprefix("adv_"), "title": [], "price": [], "location": []}
        captures: set[str] = set()
        if "ticket-title" in classes and tag == "a":
            self.current["url"] = attributes.get("href") or ""
            captures.add("title")
        if "price" in classes and "js-price" in classes:
            captures.add("price")
        if "address" in classes and "js-state-city" in classes:
            captures.add("location")
        if tag not in _VOID:
            self.stack.append((tag, captures))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        if not self.stack:
            self.cards.append(self.current)
            self.current = None

    def handle_data(self, data: str) -> None:
        if self.current is None:
            return
        captures = set().union(*(flags for _, flags in self.stack))
        for field in captures:
            self.current[field].append(data)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    parser = _Cards()
    parser.feed(ctx.text())
    parser.close()
    page_url = str((material.get("locator") or {}).get("url") or "https://www.ria.com/uk/")
    found: dict[str, dict[str, Any]] = {}
    for card in parser.cards:
        listing_id = card["id"]
        title = _clean(" ".join(card["title"]))
        url = urljoin(page_url, card.get("url") or "")
        parsed = urlsplit(url)
        match = _PATH.fullmatch(parsed.path)
        if not (
            listing_id.isdigit()
            and title
            and match
            and match.group(1) == listing_id
            and parsed.scheme == "https"
            and parsed.hostname in {"www.ria.com", "ria.com"}
        ):
            continue
        fields: dict[str, Any] = {"site": "ria.com", "listing_id": listing_id, "title": title, "url": url}
        price = _clean(" ".join(card["price"]))
        if price_match := _PRICE.fullmatch(price):
            amount = float(re.sub(r"\s", "", price_match.group(1)).replace(",", "."))
            currency = _CURRENCIES.get(price_match.group(2).lower())
            if math.isfinite(amount) and amount >= 0 and currency:
                fields["price"] = {"amount": amount, "currency": currency}
        if location := _clean(" ".join(card["location"])):
            fields["location"] = location
        found.setdefault(listing_id, fields)
    if not found:
        return (
            unrecognized("Catalog cards have no valid id, title or URL", signature="ria:invalid-cards")
            if parser.cards
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
