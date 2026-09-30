"""Shared helpers of the WP-03 discovery strategies.

* limits: every number comes from ``ctx.limits`` (effective limits of the strategy, ``strategies[].limits``
  already merged in by the core); a missing or invalid value is a configuration error;
* safe decoding of navigation documents: bounded gzip decompression and an XML parser that never resolves
  entities, never touches the network and rejects documents that declare DTD entities;
* dates (W3C Datetime / RFC 3339 / RFC 822), URL helpers and the navigation fetch wrapper around
  ``ctx.fetch`` (all network access of the strategies goes through the core).
"""

from __future__ import annotations

import re
import zlib
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from lxml import etree  # type: ignore[import-untyped]

from jane_contracts.discovery import DiscoveryContext, FetchedResource, FetchRejected

__all__ = [
    "HTML_TYPES",
    "BudgetExhausted",
    "Decoded",
    "UnsafeDocument",
    "bump",
    "children",
    "fetch_document",
    "is_html",
    "is_success",
    "limit",
    "localname",
    "maybe_gunzip",
    "origin_of",
    "parse_datetime",
    "parse_xml",
    "query_param",
    "rule_origins",
    "safe_normalize",
    "set_query_param",
    "text_of",
]

HTML_TYPES = frozenset({"text/html", "application/xhtml+xml"})
GZIP_MAGIC = b"\x1f\x8b"


class BudgetExhausted(Exception):
    """``ctx.fetch`` refused because a run budget or the configured maximum wait is exhausted."""


class UnsafeDocument(ValueError):
    """A navigation document that is refused on purpose (DTD entity declarations)."""


def limit(ctx: DiscoveryContext, path: str) -> int:
    """Require an effective ``group.name`` limit supplied by the core for this strategy."""
    group, _, name = path.partition(".")
    section = ctx.limits.get(group) if isinstance(ctx.limits, Mapping) else None
    value = section.get(name) if isinstance(section, Mapping) else None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise ValueError(f"missing or invalid effective limit: {path}")


def bump(stats: dict[str, int], key: str, by: int = 1) -> None:
    stats[key] = stats.get(key, 0) + by


def is_html(media_type: str) -> bool:
    return media_type in HTML_TYPES


def is_success(resource: FetchedResource) -> bool:
    return 200 <= resource.status < 300


async def fetch_document(ctx: DiscoveryContext, url: str) -> FetchedResource | None:
    """Fetch a navigation document through the core, always with a body (``conditional=False``).

    Navigation documents (sitemaps, feeds, API pages) are re-read on every run: only the materials they
    list go through the revisit rules of the core. ``None``: already fetched in this process, or the fetch
    failed (the core records the error). Policy refusals of one URL are skipped; an exhausted budget raises
    :class:`BudgetExhausted` so the strategy stops.
    """
    try:
        return await ctx.fetch(url, kind="navigation", conditional=False)
    except FetchRejected as exc:
        if exc.code in {"limit_exceeded", "rate_limited"}:
            raise BudgetExhausted(f"{exc.code}: {exc}") from exc
        ctx.log.info("navigation document skipped", extra={"url": url, "code": exc.code})
        return None


def safe_normalize(ctx: DiscoveryContext, url: str, base: str | None = None) -> str | None:
    """``ctx.normalize`` that returns ``None`` for non-HTTP(S) or malformed URLs instead of raising."""
    if not isinstance(url, str) or not url.strip():
        return None
    try:
        return ctx.normalize(url.strip(), base)
    except ValueError:
        return None


def origin_of(url: str) -> str | None:
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if parts.scheme not in {"http", "https"} or not parts.netloc or "{" in parts.netloc:
        return None
    return f"{parts.scheme}://{parts.netloc}"


_URL_FIELDS: dict[str, tuple[str, ...]] = {
    "seed_list": ("urls",),
    "recursive": ("seeds",),
    "sitemap": ("urls",),
    "feed": ("urls",),
    "listing": ("start_urls",),
    "api_feed": ("url",),
    "url_template": ("template",),
}


def _rule_urls(strategy: Mapping[str, Any]) -> Iterator[str]:
    for name in _URL_FIELDS.get(str(strategy.get("type")), ()):
        value = strategy.get(name)
        values = value if isinstance(value, list) else [value]
        yield from (v for v in values if isinstance(v, str))
    search = strategy.get("search")
    if isinstance(search, Mapping) and isinstance(search.get("url_template"), str):
        yield search["url_template"]


def rule_origins(rules: Mapping[str, Any]) -> list[str]:
    """Origins (``scheme://host[:port]``) of explicit URLs in the rules, in order of appearance.

    If there are none, ``scope.allowed_domains`` with the first allowed scheme (``https`` by default).
    """
    seen: list[str] = []
    for strategy in rules.get("strategies") or []:
        if not isinstance(strategy, Mapping):
            continue
        for url in _rule_urls(strategy):
            origin = origin_of(url)
            if origin and origin not in seen:
                seen.append(origin)
    if seen:
        return seen
    scope = rules.get("scope") or {}
    schemes = scope.get("allowed_schemes") or ["https", "http"]
    return [f"{schemes[0]}://{domain}" for domain in scope.get("allowed_domains") or []]


def query_param(url: str, name: str) -> str | None:
    for key, value in parse_qsl(urlsplit(url).query, keep_blank_values=True):
        if key == name:
            return value
    return None


def set_query_param(url: str, name: str, value: str) -> str:
    parts = urlsplit(url)
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != name]
    pairs.append((name, value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment))


# ---------------------------------------------------------------------------------------------- dates
_YEAR_MONTH = re.compile(r"(\d{4})(?:-(\d{2}))?")


def parse_datetime(value: Any) -> datetime | None:
    """W3C Datetime (sitemaps: ``YYYY``, ``YYYY-MM``, ``YYYY-MM-DD``, with time), RFC 3339, RFC 822 (RSS)
    or a Unix timestamp. Naive values are taken as UTC. ``None`` if unparseable."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        try:
            return datetime.fromtimestamp(float(value), UTC)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        match = _YEAR_MONTH.fullmatch(text)
        if match:
            try:
                parsed = datetime(int(match.group(1)), int(match.group(2) or 1), 1)
            except ValueError:
                return None
        else:
            try:
                parsed = parsedate_to_datetime(text)
            except (TypeError, ValueError, IndexError):
                return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


# ---------------------------------------------------------------------------------------------- gzip
@dataclass(frozen=True, slots=True)
class Decoded:
    data: bytes
    compressed: bool
    truncated: bool


def maybe_gunzip(body: bytes, max_bytes: int) -> Decoded:
    """Decompress a gzip body (``.gz`` sitemaps are served as ``application/gzip``, not Content-Encoding).

    The output never exceeds ``max_bytes`` (``crawl.max_material_bytes``): a gzip bomb is cut there and
    reported as truncated instead of being inflated in memory. Multi-member files are supported; a corrupt or
    cut stream yields what was decoded so far (``truncated=True``). Non-gzip bodies are returned as they are.
    """
    if not body.startswith(GZIP_MAGIC):
        return Decoded(body, compressed=False, truncated=False)
    out = bytearray()
    data = body
    truncated = False
    while data:
        inflater = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
        pending = data
        try:
            while pending and len(out) <= max_bytes:
                out += inflater.decompress(pending, max_bytes - len(out) + 1)
                pending = inflater.unconsumed_tail
        except zlib.error:
            truncated = True
            break
        if len(out) > max_bytes:
            del out[max_bytes:]
            truncated = True
            break
        if not inflater.eof:
            truncated = True
            break
        data = inflater.unused_data
        if data and not data.startswith(GZIP_MAGIC):
            break  # trailing garbage after the last member
    return Decoded(bytes(out), compressed=True, truncated=truncated)


# ---------------------------------------------------------------------------------------------- XML
def _parser() -> etree.XMLParser:
    return etree.XMLParser(
        resolve_entities=False,  # no entity expansion: no "billion laughs", no external entities (XXE)
        no_network=True,
        load_dtd=False,
        dtd_validation=False,
        huge_tree=False,  # libxml2's own depth/size safety limits stay on
        recover=True,  # a document cut at crawl.max_material_bytes still yields its complete entries
        remove_comments=True,
        remove_pis=True,
        collect_ids=False,
    )


def parse_xml(data: bytes, base_url: str | None = None) -> Any | None:
    """Parse a navigation document safely. ``None`` if it is not XML at all.

    Raises :class:`UnsafeDocument` for documents that declare DTD entities: sitemaps and feeds never need
    them, and refusing them outright closes entity-expansion and external-entity attacks.
    """
    text = data.lstrip()
    if text.startswith(b"\xef\xbb\xbf"):
        text = text[3:].lstrip()
    if not text.startswith(b"<"):
        return None
    try:
        root = etree.fromstring(text, _parser(), base_url=base_url)
    except (etree.XMLSyntaxError, ValueError):
        return None
    if root is None:
        return None
    dtd = root.getroottree().docinfo.internalDTD
    if dtd is not None and any(True for _ in dtd.iterentities()):
        raise UnsafeDocument("the document declares DTD entities")
    return root


def localname(el: Any) -> str:
    tag = getattr(el, "tag", None)
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def children(el: Any, name: str) -> Iterator[Any]:
    for child in el:
        if localname(child) == name:
            yield child


def text_of(el: Any, names: Iterable[str]) -> str | None:
    """Stripped text of the first direct child whose local name is in ``names`` (in the given order)."""
    wanted = list(names)
    found: dict[str, str] = {}
    for child in el:
        name = localname(child)
        if name in wanted and name not in found and child.text and child.text.strip():
            found[name] = child.text.strip()
    for name in wanted:
        if name in found:
            return found[name]
    return None
