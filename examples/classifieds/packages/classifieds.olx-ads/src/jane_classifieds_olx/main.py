"""Extract directly present public OLX cards from original category HTML."""

from __future__ import annotations

import math
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

VOID = frozenset(
    {
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
)
LISTING_ID = re.compile(r"-ID([A-Za-z0-9]+)\.html$")
PRICE = re.compile(r"^([\d\s\u00a0\u202f]+(?:[.,]\d{1,2})?)\s*(грн\.?|UAH|USD|EUR|\$|€)$", re.I)
CURRENCIES = {"грн": "UAH", "грн.": "UAH", "uah": "UAH", "usd": "USD", "$": "USD", "eur": "EUR", "€": "EUR"}


class Node:
    def __init__(self, tag: str, attrs: dict[str, str] | None = None) -> None:
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list[Node | str] = []

    def text(self) -> str:
        return " ".join(
            child.text()
            if isinstance(child, Node) and child.tag not in {"style", "script", "svg"}
            else ""
            if isinstance(child, Node)
            else child
            for child in self.children
        ).strip()

    def descendants(self, tag: str) -> list[Node]:
        found: list[Node] = []
        for child in self.children:
            if isinstance(child, Node):
                if child.tag == tag:
                    found.append(child)
                found.extend(child.descendants(tag))
        return found


class Cards(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[Node] = [Node("root")]
        self.cards: list[Node] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if node.attrs.get("data-cy") == "l-card" or node.attrs.get("data-testid") == "l-card":
            self.cards.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page_url = str((material.get("locator") or {}).get("url") or "")
    if (urlsplit(page_url).hostname or "").lower().removeprefix("www.") != "olx.ua":
        return empty()
    page = Cards()
    page.feed(ctx.text())
    found: dict[str, dict[str, Any]] = {}
    for card in page.cards:
        title_links = [a for a in card.descendants("a") if a.attrs.get("data-testid") == "card-title-link"]
        if not title_links:
            continue
        anchor = title_links[0]
        absolute = urlsplit(urljoin(page_url, anchor.attrs.get("href", "")))
        match = LISTING_ID.search(absolute.path)
        title = " ".join((anchor.attrs.get("aria-label") or anchor.text()).split())
        if (
            not match
            or not title
            or absolute.hostname not in {"olx.ua", "www.olx.ua"}
            or absolute.scheme != "https"
        ):
            continue
        listing_id = card.attrs.get("id", "")
        if not listing_id.isdigit():
            listing_id = match.group(1)
        fields: dict[str, Any] = {
            "site": "olx",
            "listing_id": listing_id,
            "title": title,
            "url": urlunsplit((absolute.scheme, absolute.netloc, absolute.path, "", "")),
        }
        for p in card.descendants("p"):
            if p.attrs.get("data-testid") == "ad-price":
                price = re.match(
                    r"^([\d\s\u00a0\u202f]+(?:[.,]\d{1,2})?)\s*(грн\.?|UAH|USD|EUR|\$|€)",
                    " ".join(p.text().split()),
                    re.I,
                )
                if price:
                    amount = float(re.sub(r"\s", "", price.group(1)).replace(",", "."))
                    if math.isfinite(amount) and amount >= 0:
                        fields["price"] = {
                            "amount": amount,
                            "currency": CURRENCIES[price.group(2).casefold()],
                        }
            elif p.attrs.get("data-testid") == "location-date":
                location = " ".join(p.text().split()).partition(" - ")[0]
                if location:
                    fields["location"] = location
        found.setdefault(listing_id, fields)
    if not found:
        return empty()
    scope = str((material.get("source") or {}).get("source_id") or "local")
    return success(
        [
            entity(
                "classified_ad",
                fields,
                key={"scope": scope, "natural": {"site": "olx", "listing_id": fields["listing_id"]}},
            )
            for fields in found.values()
        ]
    )
