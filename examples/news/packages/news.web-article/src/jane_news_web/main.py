"""Source-backed HTML article extraction, without network access."""

from __future__ import annotations

import json
import re
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qsl, urljoin, urlsplit

SKIP = {"script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"}
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "wbr", "area", "base", "embed"}


def clean(value: str) -> str:
    return " ".join(unescape(value).split())


class ArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.meta: dict[str, str] = {}
        self.title: list[str] = []
        self.h1: list[str] = []
        self.text: list[str] = []
        self.article_text: list[str] = []
        self.main_text: list[str] = []
        self.scripts: list[str] = []
        self.ld: list[str] = []
        self.in_ld = False
        self.canonical = ""
        self.has_article = False
        self.primary_seen = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        in_head = any(item[0] == "head" for item in self.stack)
        parent_skip = self.stack[-1][1] if self.stack else False
        parent_article = self.stack[-1][2] if self.stack else False
        if tag == "meta" and in_head:
            name = values.get("property") or values.get("name") or values.get("itemprop")
            if name and values.get("content"):
                self.meta[str(name).lower()] = str(values["content"])
        if tag == "link" and in_head and values.get("rel") == "canonical":
            self.canonical = str(values.get("href") or "")
        if tag == "time" and parent_article and not parent_skip and values.get("datetime"):
            self.meta.setdefault("article:published_time", str(values["datetime"]))
        if tag == "script" and "ld+json" in str(values.get("type")):
            self.in_ld = True
            self.scripts = []
        if tag in VOID:
            return
        class_name = str(values.get("class") or "") + " " + str(values.get("id") or "")
        article = (
            tag == "article"
            or bool(
                re.search(r"(?:article|story|news)[_-]*(?:body|text|content)|body[_-]*text", class_name, re.I)
            )
            or values.get("itemprop") == "articleBody"
        )
        self.has_article = self.has_article or article
        foreign_article = article and not parent_article and self.primary_seen
        if article and not parent_article and not self.primary_seen:
            self.primary_seen = True
        self.stack.append(
            (
                tag,
                parent_skip or tag in SKIP or foreign_article,
                parent_article or (article and not foreign_article),
            )
        )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.in_ld:
            self.ld.append("".join(self.scripts))
            self.in_ld = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self.in_ld:
            self.scripts.append(data)
        if any(x[0] == "title" for x in self.stack):
            self.title.append(data)
        if any(x[0] == "h1" for x in self.stack) and (
            not self.primary_seen or (self.stack and self.stack[-1][2])
        ):
            self.h1.append(data)
        if self.stack and self.stack[-1][1]:
            return
        if clean(data):
            self.text.append(data)
            if self.stack and self.stack[-1][2]:
                self.article_text.append(data)
            if any(item[0] == "main" for item in self.stack):
                self.main_text.append(data)


def json_articles(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for node in value for item in json_articles(node)]
    if not isinstance(value, dict):
        return []
    result: list[dict[str, Any]] = []
    types = value.get("@type", [])
    types = [types] if isinstance(types, str) else types
    if any(t in {"NewsArticle", "Article", "ReportageNewsArticle", "BlogPosting"} for t in types):
        result.append(value)
    for key in ("@graph", "mainEntity", "itemListElement"):
        if key in value:
            result.extend(json_articles(value[key]))
    return result


def page_identity(value: str, base: str) -> tuple[str, str, tuple[tuple[str, str], ...]] | None:
    parsed = urlsplit(urljoin(base, value))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    return (
        parsed.netloc.casefold(),
        parsed.path.rstrip("/") or "/",
        tuple(sorted(parse_qsl(parsed.query, keep_blank_values=True))),
    )


def primary_article(nodes: list[dict[str, Any]], urls: list[str]) -> dict[str, Any]:
    """Bind body and metadata to this page; never select the largest unrelated article."""
    base = urls[0]
    identities = {page_identity(url, base) for url in urls}
    matched = []
    anonymous = []
    for node in nodes:
        references = []
        for key in ("url", "@id", "mainEntityOfPage"):
            value = node.get(key)
            if isinstance(value, dict):
                value = value.get("@id") or value.get("url")
            if isinstance(value, str) and (identity := page_identity(value, base)) is not None:
                references.append(identity)
        if references and any(identity in identities for identity in references):
            matched.append(node)
        elif not references:
            anonymous.append(node)
    if matched:
        return max(matched, key=lambda node: len(str(node.get("articleBody", ""))))
    return anonymous[0] if len(nodes) == 1 and len(anonymous) == 1 else {}


def extract(material: dict[str, Any], params: dict[str, Any], ctx: Any) -> dict[str, Any]:
    page = ctx.text()
    parser = ArticleParser()
    parser.feed(page)
    locator = material.get("locator") or {}
    url = str(locator.get("url") or locator.get("canonical_url") or "")
    urls = [url]
    for key in ("canonical_url", "final_url"):
        if locator.get(key):
            urls.append(str(locator[key]))
    canonical = urljoin(url, parser.canonical) if parser.canonical else ""
    if canonical and urlsplit(canonical).hostname == urlsplit(url).hostname:
        url = canonical
        urls.append(canonical)
    nodes = []
    for raw in parser.ld:
        try:
            nodes.extend(json_articles(json.loads(raw)))
        except (ValueError, TypeError):
            continue
    article = primary_article(nodes, urls)
    if article.get("isAccessibleForFree") is False or article.get("isAccessibleForFree") == "false":
        return {
            "status": "unrecognized",
            "entities": [],
            "unrecognized": {
                "partial": False,
                "reason": "Article is behind a paywall",
                "signature": "news:paywall",
            },
        }
    title = clean(str(article.get("headline") or parser.meta.get("og:title") or " ".join(parser.h1)))
    text = clean(str(article.get("articleBody") or " ".join(parser.article_text or parser.main_text)))
    if not parser.has_article and not article.get("articleBody"):
        text = clean(" ".join(parser.text))
    # A news listing is not an article. Open Graph/schema/article containers supply an independent signal.
    signal = bool(article or parser.has_article or parser.meta.get("article:published_time"))
    if not signal or not title or len(text) < int(params.get("min_text_chars", 160)):
        return {
            "status": "unrecognized",
            "entities": [],
            "unrecognized": {
                "partial": False,
                "reason": "No readable news article",
                "signature": "news:no-article",
            },
        }
    fields: dict[str, Any] = {
        "url": url,
        "title": title,
        "text": text[: int(params.get("max_text_chars", 16000))],
        "source_id": params.get("source_id") or (material.get("source") or {}).get("source_id", "local"),
        "source_name": params["source_name"],
        "source_kind": "web",
        "region": params["region"],
        "language": params["language"],
        "transport": "rss_article",
    }
    published = (
        article.get("datePublished")
        or parser.meta.get("article:published_time")
        or material.get("published_at")
    )
    if published:
        fields["published_at"] = str(published)
    author = article.get("author")
    if isinstance(author, dict) and isinstance(author.get("name"), str):
        fields["author"] = author["name"]
    return {
        "status": "success",
        "entities": [
            {
                "entity_type": "article",
                "key": {"scope": fields["source_id"], "natural": {"url": url}},
                "fields": fields,
            }
        ],
    }
