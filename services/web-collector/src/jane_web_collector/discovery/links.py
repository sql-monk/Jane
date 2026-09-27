"""Link extraction from HTML (lxml): ``a[href]`` by default, CSS / XPath / ``rel`` selectors, ``<base href>``."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import lxml.html  # type: ignore[import-untyped]
from lxml import etree

__all__ = ["HTML_TYPES", "LINK_SOURCES", "extract_hrefs", "html_meta", "is_html", "parse_html"]

HTML_TYPES = frozenset({"text/html", "application/xhtml+xml"})
# rel values of <link> that point to resources, not to pages worth crawling.
_RESOURCE_RELS = frozenset(
    {
        "stylesheet",
        "icon",
        "shortcut",
        "apple-touch-icon",
        "preload",
        "prefetch",
        "preconnect",
        "dns-prefetch",
        "manifest",
        "modulepreload",
    }
)


def is_html(media_type: str) -> bool:
    return media_type in HTML_TYPES


def parse_html(body: bytes) -> Any | None:
    if not body.strip():
        return None
    try:
        return lxml.html.document_fromstring(body)
    except (etree.ParserError, ValueError):
        return None


def _rels(el: Any) -> set[str]:
    return {r.lower() for r in (el.get("rel") or "").split()}


def _a_href(doc: Any) -> Iterable[str]:
    for el in doc.iter("a", "area"):
        if el.get("href"):
            yield el.get("href")


def _link_rel(doc: Any) -> Iterable[str]:
    for el in doc.iter("link"):
        if el.get("href") and not (_rels(el) & _RESOURCE_RELS):
            yield el.get("href")


def _canonical(doc: Any) -> Iterable[str]:
    for el in doc.iter("link"):
        if el.get("href") and "canonical" in _rels(el):
            yield el.get("href")


def _pagination_rel(doc: Any) -> Iterable[str]:
    for el in doc.iter("a", "link"):
        if el.get("href") and _rels(el) & {"next", "prev", "previous"}:
            yield el.get("href")


LINK_SOURCES: dict[str, Callable[[Any], Iterable[str]]] = {
    "a_href": _a_href,
    "link_rel": _link_rel,
    "canonical": _canonical,
    "pagination_rel": _pagination_rel,
}


def base_href(doc: Any, url: str) -> str:
    for el in doc.iter("base"):
        if el.get("href"):
            return str(el.get("href"))
    return url


def extract_hrefs(
    doc: Any,
    *,
    selector_type: str | None = None,
    selector: str | None = None,
    attribute: str = "href",
    sources: Iterable[str] = ("a_href",),
) -> list[str]:
    """Raw (not yet resolved) link values in document order."""
    if selector is not None:
        if selector_type == "xpath":
            found = doc.xpath(selector)
        elif selector_type == "rel":
            wanted = selector.lower()
            found = [el for el in doc.iter("a", "link", "area") if wanted in _rels(el)]
        else:
            found = doc.cssselect(selector)
        out: list[str] = []
        for item in found:
            if isinstance(item, str):
                out.append(item)
            elif hasattr(item, "get") and item.get(attribute):
                out.append(item.get(attribute))
        return out
    hrefs: list[str] = []
    for source in sources:
        hrefs.extend(LINK_SOURCES[source](doc))
    return hrefs


def html_meta(doc: Any) -> dict[str, str]:
    """``title``, ``article:published_time``, ``article:modified_time`` if present."""
    out: dict[str, str] = {}
    title = doc.find(".//title")
    if title is not None and title.text_content().strip():
        out["title"] = title.text_content().strip()
    for el in doc.iter("meta"):
        prop = el.get("property") or el.get("name")
        if prop in {"article:published_time", "article:modified_time"} and el.get("content"):
            out[prop] = el.get("content")
    return out
