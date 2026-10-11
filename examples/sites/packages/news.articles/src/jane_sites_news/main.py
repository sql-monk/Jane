"""News articles: title, dates, author, section, tags, lead and the full clean text of a news page.

Metadata comes from schema.org JSON-LD (``NewsArticle``/``Article``/...), then ``og:``/``article:`` meta and
the page itself. The text is read from the site's article container (``sites.SITES`` or ``params.sites``) with
ads, embeds, captions and "read also" blocks removed; for an unknown site - the JSON-LD ``articleBody`` or the
element with the most paragraph text. One ``article`` entity per page, keyed by the canonical URL (no
tracking parameters, no fragment).

* a page without article markup (home page, listing, tag page) -> ``empty``;
* a paywalled article (``isAccessibleForFree: false``) -> ``empty`` with a warning: the full text is not there;
* an article without a title, a publication date or text -> ``unrecognized`` (signature names the gaps).
"""

from __future__ import annotations

import html
import json
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from datetime import UTC, datetime, tzinfo
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from dateutil import parser as date_parser  # type: ignore[import-untyped]
from dateutil import tz
from dateutil.zoneinfo import get_zonefile_instance  # type: ignore[import-untyped]
from lxml import html as lxml_html  # type: ignore[import-untyped]

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

from .sites import DROP_ALWAYS, REMOVE_ALWAYS, SITES, STOP_ALWAYS, SiteRule

ARTICLE_TYPES = frozenset(
    {
        "Article",
        "NewsArticle",
        "ReportageNewsArticle",
        "AnalysisNewsArticle",
        "OpinionNewsArticle",
        "BackgroundNewsArticle",
        "ReviewNewsArticle",
        "AskPublicNewsArticle",
        "SatiricalArticle",
        "BlogPosting",
        "LiveBlogPosting",
        "Report",
    }
)
BLOCK_TAGS = frozenset(
    {
        "address",
        "article",
        "aside",
        "blockquote",
        "dd",
        "details",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "summary",
        "table",
        "tbody",
        "tfoot",
        "thead",
        "tr",
        "ul",
    }
)
LANGUAGES = {"uk": "uk", "ua": "uk", "en": "en", "ru": "ru"}
PUBLISHED_META = ("article:published_time", "og:published_time", "datepublished", "pubdate")
MODIFIED_META = ("article:modified_time", "og:modified_time", "og:updated_time", "datemodified")
TRACKING_PARAM = re.compile(
    r"^(utm_\w*|fbclid|gclid|dclid|yclid|gbraid|wbraid|msclkid|mc_cid|mc_eid|_ga|_gl|igshid|ref_src|cmpid)$",
    re.I,
)
# Spaces (incl. no-break and typographic ones) and invisible characters (soft hyphen, zero-width, BOM).
_SPACE_CODES = (0x09, 0x0B, 0x0C, 0x0D, 0x20, 0xA0, 0x1680, *range(0x2000, 0x200B), 0x202F, 0x205F, 0x3000)
_SPACES = re.compile("[" + re.escape("".join(map(chr, _SPACE_CODES))) + "]+")
_INVISIBLE = re.compile(
    "[" + re.escape("".join(map(chr, (0xAD, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF)))) + "]"
)
_TAG = re.compile(r"<[^>]+>")
_XML_DECLARATION = re.compile(r"^\s*<\?xml[^>]*\?>", re.I)
_TRAILING_COMMA = re.compile(r",\s*([}\]])")
_TIME_ONLY = re.compile(r"^\d{1,2}:\d{2}$")
_CYRILLIC = re.compile(r"[а-яіїєґёыэъ]", re.I)
_LATIN = re.compile(r"[a-z]", re.I)


# --- text helpers -------------------------------------------------------------------------------------------


def _clean(value: Any) -> str | None:
    """One line of plain text: entities decoded (twice: some JSON-LD double-escapes), tags and spaces folded."""
    if not isinstance(value, str):
        return None
    text = html.unescape(html.unescape(value))
    text = _INVISIBLE.sub("", _TAG.sub(" ", text))
    text = _SPACES.sub(" ", text.replace("\n", " ")).strip()
    return text or None


def _clean_block(raw: str) -> str:
    lines = (_SPACES.sub(" ", _INVISIBLE.sub("", line)).strip() for line in raw.split("\n"))
    return "\n".join(line for line in lines if line)


def _blocks(root: Any) -> list[str]:
    """Text blocks of an element: paragraphs, headings, list items...; ``<br>`` is a line break inside a block."""
    out: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        text = _clean_block("".join(buf))
        buf.clear()
        if text:
            out.append(text)

    def walk(el: Any) -> None:
        if isinstance(el.tag, str):  # not a comment or a processing instruction
            block = el.tag in BLOCK_TAGS
            if block:
                flush()
            if el.tag == "br":
                buf.append("\n")
            elif el.tag in ("td", "th"):
                buf.append(" ")
            if el.text:
                buf.append(el.text)
            for child in el:
                walk(child)
            if block:
                flush()
        if el.tail:
            buf.append(el.tail)

    if root.text:
        buf.append(root.text)
    for child in root:
        walk(child)
    flush()
    return out


def _compile(patterns: Iterable[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.I) for p in patterns]


def _filter(
    blocks: Sequence[str], drop: Sequence[re.Pattern[str]], stop: Sequence[re.Pattern[str]]
) -> list[str]:
    out: list[str] = []
    for block in blocks:
        if any(p.search(block) for p in stop):
            break
        if any(p.search(block) for p in drop) or (out and out[-1] == block):
            continue
        if out and _TIME_ONLY.match(out[-1]):  # a live-blog entry: "21:03" + its text -> one block
            out[-1] = f"{out[-1]} {block}"
            continue
        out.append(block)
    return out


# --- page access --------------------------------------------------------------------------------------------


def _select(root: Any, css: str) -> list[Any]:
    """CSS matches under ``root``; an invalid selector (from params) matches nothing."""
    try:
        return list(root.cssselect(css))
    except Exception:  # cssselect raises several parser errors; a selector is data here, not code
        return []


class Page:
    def __init__(self, text: str) -> None:
        self.doc = lxml_html.document_fromstring(_XML_DECLARATION.sub("", text, count=1) or "<html></html>")

    def first_text(self, css: str | None) -> str | None:
        for el in _select(self.doc, css) if css else []:
            if text := _clean(el.text_content()):
                return text
        return None

    def all_texts(self, css: str) -> list[str]:
        return [t for el in _select(self.doc, css) if (t := _clean(el.text_content()))]

    def meta(self, *names: str) -> list[str]:
        """``content`` of ``<meta property|name|itemprop=...>`` for the names, in that order of names."""
        values: list[str] = []
        for name in names:
            for el in self.doc.iter("meta"):
                key = el.get("property") or el.get("name") or el.get("itemprop") or ""
                if key.strip().lower() == name and (value := _clean(el.get("content"))):
                    values.append(value)
        return values

    def meta1(self, *names: str) -> str | None:
        found = self.meta(*names)
        return found[0] if found else None

    def link(self, rel: str) -> str | None:
        for el in self.doc.iter("link"):
            if rel in (el.get("rel") or "").lower().split() and el.get("href"):
                return str(el.get("href")).strip()
        return None

    def json_ld(self) -> Iterator[Any]:
        for el in self.doc.iter("script"):
            if (el.get("type") or "").strip().lower() != "application/ld+json":
                continue
            raw = (el.text or "").strip()
            for candidate in (raw, _TRAILING_COMMA.sub(r"\1", raw)):
                try:
                    doc = json.loads(candidate, strict=False)
                except ValueError:
                    doc = None
                if doc is not None:
                    yield doc
                    break


def _nodes(doc: Any) -> Iterator[dict[str, Any]]:
    if isinstance(doc, dict):
        yield doc
        for value in doc.values():
            if isinstance(value, dict | list):
                yield from _nodes(value)
    elif isinstance(doc, list):
        for value in doc:
            yield from _nodes(value)


def _types(node: Mapping[str, Any]) -> set[str]:
    t = node.get("@type")
    values = t if isinstance(t, list) else [t]
    return {v.rsplit("/", 1)[-1] for v in values if isinstance(v, str)}


def _article_node(page: Page) -> dict[str, Any] | None:
    for doc in page.json_ld():
        for node in _nodes(doc):
            if _types(node) & ARTICLE_TYPES and (node.get("headline") or node.get("name")):
                return node
    return None


def _breadcrumb_section(page: Page, title: str) -> str | None:
    """The deepest JSON-LD breadcrumb above the article (``Укрінформ > Регіони > <title>`` -> ``Регіони``)."""
    for doc in page.json_ld():
        for node in _nodes(doc):
            if "BreadcrumbList" not in _types(node) or not isinstance(node.get("itemListElement"), list):
                continue
            names = []
            for el in node["itemListElement"]:
                item = el.get("item") if isinstance(el, dict) else None
                name = el.get("name") if isinstance(el, dict) else None
                if text := _clean(name or (item.get("name") if isinstance(item, dict) else None)):
                    names.append(text)
            names = [n for n in names[1:] if n != title]
            if names:
                return names[-1]
    return None


def _names(value: Any) -> list[str]:
    """Names of schema.org values: a string, ``{"name": ...}`` or a list of them."""
    out = []
    for item in value if isinstance(value, list) else [value]:
        if text := _clean(item.get("name") if isinstance(item, dict) else item):
            out.append(text)
    return out


def _url_of(value: Any) -> str | None:
    for item in value if isinstance(value, list) else [value]:
        url = (
            (item.get("url") or item.get("@id") or item.get("contentUrl")) if isinstance(item, dict) else item
        )
        if isinstance(url, str) and url.strip().startswith(("http://", "https://", "//")):
            return url.strip()
    return None


# --- field helpers ------------------------------------------------------------------------------------------


def _timezone(name: str) -> tzinfo:
    """dateutil's bundled tz database first: the result does not depend on the system zoneinfo."""
    zone: tzinfo | None = get_zonefile_instance().get(name) or tz.gettz(name)
    if zone is None:
        raise ValueError(f"unknown timezone {name!r}")
    return zone


def _date(value: Any, default_tz: tzinfo) -> str | None:
    """RFC 3339 in UTC (``Z``); a time without an offset is local time of ``default_tz``."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        if text.isdigit() and len(text) >= 9:
            moment = datetime.fromtimestamp(int(text), UTC)
        else:
            try:
                moment = date_parser.isoparse(text)
            except ValueError:
                moment = date_parser.parse(text, default=datetime(2000, 1, 1))
    except (ValueError, OverflowError):
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=default_tz)
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_date(values: Iterable[Any], default_tz: tzinfo) -> str | None:
    return next((d for v in values if (d := _date(v, default_tz))), None)


def _canonical(url: str | None, base: str = "") -> str | None:
    """Absolute http(s) URL without tracking parameters and fragment."""
    if not url:
        return None
    parts = urlsplit(urljoin(base, url.strip()))
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not TRACKING_PARAM.match(k)]
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path or "/", urlencode(query), ""))


def _host(url: str | None) -> str:
    return (urlsplit(url or "").hostname or "").lower()


def _within(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def _site_key(host: str, sites: Mapping[str, SiteRule]) -> str | None:
    matches = [d for d in sites if _within(host, d)]
    return max(matches, key=len) if matches else None


def _without_outlet(text: str | None, outlets: Sequence[str]) -> str | None:
    """``Title - ZAXID.NET`` -> ``Title``: the outlet name appended to a title or a description."""
    for name in outlets:
        for sep in (" - ", " – ", " — ", " | "):
            if text and text.casefold().endswith((sep + name).casefold()) and len(text) > len(sep + name):
                return text[: -len(sep + name)].rstrip() or text
    return text


def _norm_name(text: str) -> str:
    return re.sub(r"\W+", "", text.casefold())


def _language(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and (code := LANGUAGES.get(value.strip().lower().replace("_", "-")[:2])):
            return code
    return None


def _checked_language(declared: str | None, text: str) -> str | None:
    """The declared language unless the text contradicts its script (Crimean Tatar news of Suspilne say "uk")."""
    latin, cyrillic = len(_LATIN.findall(text)), len(_CYRILLIC.findall(text))
    if declared in ("uk", "ru") and latin > cyrillic:
        return None
    if declared == "en" and cyrillic > latin:
        return None
    return declared


def _keywords(value: Any) -> list[str]:
    items = value.split(",") if isinstance(value, str) else value if isinstance(value, list) else []
    return [t for v in items if (t := _clean(v))]


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for value in values:
        if value.casefold() not in seen:
            seen.add(value.casefold())
            out.append(value)
    return out


def _paywalled(node: Mapping[str, Any], page: Page) -> bool:
    free = node.get("isAccessibleForFree")
    if isinstance(free, str):
        free = free.strip().lower() not in ("false", "0", "no")
    return free is False or (page.meta1("article:content_tier") or "").lower() == "locked"


def _top_container(page: Page) -> Any | None:
    """The element whose direct ``<p>`` children hold the most text (fallback for unknown sites)."""
    best, best_len = None, 0
    for el in page.doc.iter():
        if not isinstance(el.tag, str) or el.tag in ("footer", "header", "nav", "aside"):
            continue
        size = sum(len(p.text_content()) for p in el if isinstance(p.tag, str) and p.tag == "p")
        if size > best_len:
            best, best_len = el, size
    return best


# --- extraction ---------------------------------------------------------------------------------------------


def _text(page: Page, rule: SiteRule, node: Mapping[str, Any], ctx: Context) -> str | None:
    drop = _compile([*DROP_ALWAYS, *rule.get("drop", [])])
    stop = _compile([*STOP_ALWAYS, *rule.get("stop", [])])
    containers: list[Any] = []
    for el in _select(page.doc, rule["body"]) if rule.get("body") else []:
        if not any(c in el.iterancestors() for c in containers):
            containers.append(el)
    if rule.get("body") and not containers:
        ctx.log.warning(
            "article container not found; generic text",
            code="extract.missing_selector",
            selector=rule["body"],
        )
    if not containers:
        body = node.get("articleBody")
        if isinstance(body, str) and body.strip():
            paragraphs = [_clean_block(html.unescape(p)) for p in re.split(r"\r?\n", body)]
            if text := "\n\n".join(_filter([p for p in paragraphs if p], drop, stop)):
                return text
        top = _top_container(page)
        containers = [top] if top is not None else []
    blocks: list[str] = []
    for container in containers:
        for css in [*REMOVE_ALWAYS, *rule.get("remove", [])]:
            for el in _select(container, css):
                if el is not container and el.getparent() is not None:
                    el.drop_tree()
        blocks += _blocks(container)
    return "\n\n".join(_filter(blocks, drop, stop)) or None


def _sites(params: Mapping[str, Any]) -> dict[str, SiteRule]:
    merged = {domain: dict(rule) for domain, rule in SITES.items()}
    for domain, rule in (params.get("sites") or {}).items():
        merged[str(domain).lower()] = {**merged.get(str(domain).lower(), {}), **rule}
    return merged


def _url(page: Page, ld: Mapping[str, Any], page_url: str, site: str) -> str | None:
    """The canonical URL of the article (rel=canonical, og:url, JSON-LD) if it is on the site, else the page URL."""
    for candidate in (
        page.link("canonical"),
        page.meta1("og:url"),
        _url_of(ld.get("url")),
        _url_of(ld.get("mainEntityOfPage")),
    ):
        url = _canonical(candidate, page_url)
        if url and _within(_host(url), site) and urlsplit(url).path not in ("", "/"):
            return url
    return _canonical(page_url)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    page = Page(ctx.text())
    locator = material.get("locator") or {}
    page_url = str(locator.get("final_url") or locator.get("url") or "")
    node = _article_node(page)
    if node is None and (
        (page.meta1("og:type") or "").lower() != "article" or not page.meta1(*PUBLISHED_META)
    ):  # og:type=article alone is not enough: listings of some sites (Radio Svoboda) declare it too
        return empty()
    ld: Mapping[str, Any] = node or {}
    if _paywalled(ld, page):
        ctx.log.warning("paywalled article: the full text is not on the page", code="extract.paywall")
        return empty()

    sites = _sites(params)
    default_tz = _timezone(str(params.get("default_timezone") or "Europe/Kyiv"))
    host = _host(page_url) or _host(_canonical(page.link("canonical")))
    key = _site_key(host, sites)
    rule: SiteRule = sites[key] if key else {}
    site = key or host.removeprefix("www.")

    url = _url(page, ld, page_url, site)
    outlet_names = [*page.meta("og:site_name"), *_names(ld.get("publisher"))]
    title = _without_outlet(
        page.first_text(rule.get("title"))
        or _clean(ld.get("headline"))
        or page.meta1("og:title")
        or page.first_text("h1")
        or _clean(page.doc.findtext(".//title")),
        outlet_names,
    )
    published = _first_date(
        [
            ld.get("datePublished"),
            *page.meta(*PUBLISHED_META),
        ],
        default_tz,
    )
    text = _text(page, rule, ld, ctx)
    min_text = int(params.get("min_text_chars") or 1)
    if not url or not title or not published or not text or len(text) < min_text:
        missing = [n for n, v in (("url", url), ("title", title), ("published_at", published)) if not v]
        missing += [] if text and len(text) >= min_text else ["text"]
        return unrecognized(
            f"article without {', '.join(missing)}",
            signature=f"news.articles:{site}:missing:{','.join(missing)}",
        )

    outlets = {_norm_name(n) for n in [site, site.split(".")[0], *outlet_names]}
    authors = (page.all_texts(rule["author"]) if rule.get("author") else []) or _names(ld.get("author"))
    authors = authors or page.meta("author")
    authors = [a.strip(" ,;:") for a in authors]
    authors = [a for a in _unique(authors) if _norm_name(a) and _norm_name(a) not in outlets]

    tags: list[str] = []
    if rule.get("tags") != "":  # "" - the site's keywords are categories, not tags
        tags = page.all_texts(rule["tags"]) if rule.get("tags") else []
        tags = tags or page.meta("article:tag") or _keywords(ld.get("keywords"))
        tags = tags or _keywords(page.meta1("news_keywords"))

    section = (
        page.first_text(rule.get("section"))
        or next(iter(_names(ld.get("articleSection"))), None)
        or page.meta1("article:section", "og:section")
        or _breadcrumb_section(page, title)
    )
    lead = _without_outlet(
        page.first_text(rule.get("lead"))
        or _clean(ld.get("description"))
        or page.meta1("og:description", "description"),
        outlet_names,
    )
    image = page.meta1("og:image") or _url_of(ld.get("image"))
    fields: dict[str, Any] = {
        "site": site,
        "url": url,
        "title": title,
        "published_at": published,
        "text": text,
        "modified_at": _first_date(
            [
                ld.get("dateModified"),
                *page.meta(*MODIFIED_META),
            ],
            default_tz,
        ),
        "author": ", ".join(authors) or None,
        "section": section,
        "lead": lead,
        "language": _checked_language(
            _language(ld.get("inLanguage"), page.doc.get("lang"), page.meta1("og:locale")), text
        ),
        "tags": _unique(tags) or None,
        "image": urljoin(page_url, image) if image else None,
    }
    return success([entity("article", fields)])
