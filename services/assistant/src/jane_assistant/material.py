"""Large HTML materials: what the model sees and what tests run on.

Real pages are large (a shop category page is 0.5-3 MB) and their first kilobytes are usually scripts and
styles; the informative part - schema.org JSON-LD, microdata, head tags, visible text - is further down. So:

* :func:`reduce_material` - once a material is read, HTML above ``material.max_fixture_bytes`` is reduced:
  executable scripts, styles, SVG, ``noscript`` and comments are removed, then data scripts other than JSON-LD
  (largest first), then the end of the body (cut at a tag; JSON-LD blocks from the cut part are kept while they
  fit). The page is read as HTML is: a ``<script>``, ``<style>``, ``<svg>``, ``<noscript>`` element or a comment
  is one opaque block from its start to its end, the earliest first, so ``"<!--"`` or ``"<style"`` inside a script
  is just script text. What is kept is byte-identical to the page, but the reduced page is **not** the real page:
  the removed scripts and the cut end of the body are still there on the real one, so an extractor that searches
  the whole page text (a price pattern that a script also contains) can pass on the reduced page and fail on the
  real one. Extractors are told so, and a proposal names the risk when its extractor was tested on reduced pages.
  The reduced page is the material of the sample: the model sees it, extractors are tested on it and packages
  keep it as their test fixture (``content.sha256``/``size_bytes``/``revision.content_sha256`` describe the
  reduced content). The full page cannot be the fixture: it does not fit ``transfer.inline_max_bytes``.
* :func:`material_text` - the text of a material for the model: small or non-HTML content as is (cut to the
  budget); larger HTML as a *digest* of the same size: head tags, structured data (JSON-LD with long lists
  shortened to their first items and the number of the rest stated, microdata types), visible text and the
  start of the body markup, in shares of the budget (``material.*_share``).
* evidence helpers for proposals: the declared ``rel=canonical`` of a page, its links, link patterns and
  pagination-like URL templates (read outside scripts and comments).

Content is untrusted data: it only ever goes into ``data`` parts of model requests and into test fixtures.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import html as html_lib
import json
import re
from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

from .content import segment_shape
from .settings import MaterialLimits

__all__ = [
    "declared_canonical",
    "empty_shell",
    "html_digest",
    "inline_bytes",
    "inline_text",
    "is_html",
    "lean_html",
    "link_pattern",
    "material_text",
    "outside_blocks",
    "page_links",
    "pagination_templates",
    "reduce_material",
    "same_url",
    "with_content",
]

_BLOCK = re.compile(
    r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>"
    r"|<style\b[^>]*>.*?</style\s*>"
    r"|<svg\b[^>]*>.*?</svg\s*>"
    r"|<noscript\b[^>]*>.*?</noscript\s*>"
    r"|<!--.*?-->",
    re.S | re.I,
)
"""Opaque blocks of a page. A scan finds the earliest block and consumes it whole, as an HTML parser does: text
inside a script (``"<!--"``, ``"<style"``) or inside a comment (``<script>``) never starts another block."""
_TYPE_ATTR = re.compile(r"""\btype\s*=\s*["']?([^"'\s>]+)""", re.I)
_TITLE = re.compile(r"<title\b[^>]*>.*?</title\s*>", re.S | re.I)
_META = re.compile(r"<meta\b[^>]*>", re.I)
_LINK = re.compile(r"<link\b[^>]*>", re.I)
_A_HREF = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+))""", re.I | re.S)
_ATTR = r"""\b{name}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+))"""
_ITEMTYPE = re.compile(_ATTR.format(name="itemtype"), re.I)
_ITEMPROP = re.compile(_ATTR.format(name="itemprop"), re.I)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
_BODY = re.compile(r"<body\b", re.I)
_NUMBER = re.compile(r"(?<=[=/])(\d{1,5})(?=$|[/&;#?])")
"""Format, not a limit: a whole path segment or parameter value that is a number (``/page/2/``, ``page=2``)."""
_PAGINATION_START_MAX = 3
"""Format, not a limit: a numbered link family is pagination-like when its smallest number is at most this
(page 2 or 3 is linked from page 1; ids of articles or products are larger)."""
_HEAD_RELS = {"canonical", "next", "prev", "previous"}
_HEAD_META = re.compile(r"^(description|keywords|robots|author|title)$|:", re.I)
"""Informative meta names: description and the like, namespaced ones (``og:``, ``product:``, ``jane:``)."""
_CUT_BODY_TAIL = "\n</body></html>"
_SECTIONS = ("head", "structured", "text", "markup")


def is_html(media_type: str | None) -> bool:
    media = (media_type or "").split(";")[0].strip().lower()
    return media in {"text/html", "application/xhtml+xml"}


def _attr(tag: str, name: str) -> str | None:
    m = re.search(_ATTR.format(name=re.escape(name)), tag, re.I)
    if not m:
        return None
    return html_lib.unescape(next(g for g in m.groups() if g is not None))


def _kind(block: re.Match[str]) -> str:
    """``ld`` (JSON-LD script), ``data`` (other JSON script), ``code`` (any other script) or ``noise`` (style,
    SVG, noscript, comment)."""
    attrs = block.group("attrs")
    if attrs is None:
        return "noise"
    m = _TYPE_ATTR.search(attrs)
    kind = (m.group(1) if m else "").lower()
    if kind == "application/ld+json":
        return "ld"
    if kind == "application/json" or kind.endswith("+json"):
        return "data"
    return "code"


def _blocks(page: str, *kinds: str) -> Iterator[re.Match[str]]:
    return (m for m in _BLOCK.finditer(page) if _kind(m) in kinds)


def _keep_blocks(page: str, keep: Callable[[str], bool], replacement: str = "") -> str:
    return _BLOCK.sub(lambda m: m.group(0) if keep(_kind(m)) else replacement, page)


def outside_blocks(page: str) -> str:
    """``page`` without scripts, styles, SVG, noscript and comments (each replaced by a space): the markup a
    browser shows, where tags and links are read."""
    return _keep_blocks(page, lambda _: False, " ")


def _size(text: str) -> int:
    return len(text.encode("utf-8"))


# ---------------------------------------------------------------------------------------------- reduction
def lean_html(page: str, max_bytes: int) -> str:
    """``page`` reduced to about ``max_bytes`` UTF-8 bytes (see the module docstring); unchanged if it fits."""
    if _size(page) <= max_bytes:
        return page
    out = _keep_blocks(page, lambda kind: kind in {"ld", "data"})
    if _size(out) <= max_bytes:
        return out
    data = sorted(_blocks(out, "data"), key=lambda m: len(m.group(0)), reverse=True)
    drop: list[tuple[int, int]] = []
    excess = _size(out) - max_bytes
    for m in data:
        if excess <= 0:
            break
        drop.append(m.span())
        excess -= _size(m.group(0))
    for start, end in sorted(drop, reverse=True):
        out = out[:start] + out[end:]
    if _size(out) <= max_bytes:
        return out
    return _cut_body(out, max_bytes)


def _cut_body(page: str, max_bytes: int) -> str:
    """Longest prefix of ``page`` ending at a tag, plus the JSON-LD blocks after it, within ``max_bytes``."""
    ld = [m.span() for m in _blocks(page, "ld")]
    tail = _CUT_BODY_TAIL
    budget = max_bytes - _size(tail)

    def after(cut: int) -> list[tuple[int, int]]:
        return [span for span in ld if span[0] >= cut]

    def size(cut: int) -> int:
        return _size(page[:cut]) + sum(_size(page[s:e]) for s, e in after(cut))

    if size(0) > budget:  # JSON-LD alone is too large: whole blocks in order while they fit, the rest dropped
        used, drop = 0, []
        for s, e in ld:
            if used + _size(page[s:e]) <= budget:
                used += _size(page[s:e])
            else:
                drop.append((s, e))
        for s, e in reversed(drop):
            page = page[:s] + page[e:]
        return _cut_body(page, max_bytes)  # every remaining block fits now
    low, high = 0, len(page)  # size(low) <= budget < size(high)
    while high - low > 1:
        mid = (low + high) // 2
        if size(mid) <= budget:
            low = mid
        else:
            high = mid
    cut = low
    inside = next((s for s, e in ld if s < cut < e), None)
    if inside is not None:  # never cut a JSON-LD block: it moves to the kept tail as a whole
        cut = inside
    tag = page.rfind("<", 0, cut + 1)
    cut = tag if tag > 0 else cut
    return page[:cut] + "".join(page[s:e] for s, e in after(cut)) + tail


def inline_bytes(material: Mapping[str, Any]) -> bytes | None:
    """Bytes of an inline ``material.content`` (``None`` for blob content)."""
    content = material.get("content") or {}
    if content.get("kind") != "inline":
        return None
    data = str(content.get("data", ""))
    return base64.b64decode(data) if content.get("encoding") == "base64" else data.encode("utf-8")


def inline_text(material: Mapping[str, Any], fallback: str = "") -> str:
    """Text of an inline ``material.content`` (``fallback`` for content given by reference)."""
    raw = inline_bytes(material)
    if raw is None:
        return fallback
    charset = (material.get("content") or {}).get("charset") or (material.get("format") or {}).get("charset")
    if (material.get("content") or {}).get("encoding") == "utf-8":
        return raw.decode("utf-8", errors="replace")
    try:
        return raw.decode(charset or "utf-8")
    except (UnicodeDecodeError, LookupError):
        return raw.decode("utf-8", errors="replace")


def with_content(material: Mapping[str, Any], raw: bytes, *, text: str | None = None) -> dict[str, Any]:
    """Copy of ``material`` with ``raw`` as its inline content (``text`` - the same bytes decoded, if known)."""
    out = copy.deepcopy(dict(material))
    old = dict(out.get("content") or {})
    media = old.get("media_type") or (out.get("format") or {}).get("media_type") or "application/octet-stream"
    sha = hashlib.sha256(raw).hexdigest()
    content: dict[str, Any] = {"kind": "inline", "media_type": media, "sha256": sha, "size_bytes": len(raw)}
    if text is not None:
        content.update(encoding="utf-8", data=text)
    else:
        try:
            content.update(encoding="utf-8", data=raw.decode("utf-8"))
        except UnicodeDecodeError:
            content.update(encoding="base64", data=base64.b64encode(raw).decode("ascii"))
    if old.get("charset") and content["encoding"] == "utf-8":
        content["charset"] = old["charset"]
    out["content"] = content
    revision = dict(out.get("revision") or {})
    if revision.get("content_sha256") and revision["content_sha256"] != sha:
        revision["content_sha256"] = sha
        out["revision"] = revision
    return out


def empty_shell(material: Mapping[str, Any]) -> dict[str, Any]:
    """The same material as an empty page of its site: its ``<title>`` and an empty body - a negative example
    when a sample holds one material type only."""
    page = outside_blocks(inline_text(material))
    title = m.group(0) if (m := _TITLE.search(page)) else "<title></title>"
    shell = f'<!DOCTYPE html>\n<html><head><meta charset="utf-8">{title}</head><body></body></html>\n'
    out = with_content(material, shell.encode("utf-8"), text=shell)
    out["content"]["media_type"] = "text/html"
    revision = dict(out.get("revision") or {})
    revision["content_sha256"] = out["content"]["sha256"]
    out["revision"] = revision
    return out


def reduce_material(
    material: Mapping[str, Any], raw: bytes, text: str, limits: MaterialLimits, *, inline: bool = True
) -> dict[str, Any]:
    """The material of a sample (see the module docstring): HTML above ``max_fixture_bytes`` reduced; with
    ``inline`` content given by reference also becomes inline (so tests and fixtures need no further reads)."""
    media = (material.get("format") or {}).get("media_type") or (material.get("content") or {}).get(
        "media_type"
    )
    if is_html(media) and len(raw) > limits.max_fixture_bytes:
        lean = lean_html(text, limits.max_fixture_bytes)
        return with_content(material, lean.encode("utf-8"), text=lean)
    if not inline or (material.get("content") or {}).get("kind") == "inline":
        return copy.deepcopy(dict(material))
    return with_content(material, raw)


# ---------------------------------------------------------------------------------------------- digest
def _shrink(node: Any, items: int, chars: int) -> Any:
    if isinstance(node, list):
        kept = [_shrink(x, items, chars) for x in node[:items]]
        if len(node) > items:
            kept.append(f"... {len(node) - items} more item(s), {len(node)} in total on the page")
        return kept
    if isinstance(node, dict):
        return {k: _shrink(v, items, chars) for k, v in node.items()}
    if isinstance(node, str) and len(node) > chars:
        return f"{node[:chars]}...[+{len(node) - chars} chars]"
    return node


def _counts(pattern: re.Pattern[str], page: str, limit: int) -> list[tuple[str, int]]:
    found: dict[str, int] = {}
    for m in pattern.finditer(page):
        value = next(g for g in m.groups() if g is not None)
        found[value] = found.get(value, 0) + 1
    return sorted(found.items(), key=lambda kv: -kv[1])[:limit]


def _structured(page: str, items: int, chars: int, limits: MaterialLimits) -> str:
    blocks = []
    for m in _blocks(page, "ld"):
        body = m.group("body").strip()
        try:
            rendered = json.dumps(
                _shrink(json.loads(body), items, chars), ensure_ascii=False, separators=(",", ":")
            )
        except ValueError:
            rendered = body if len(body) <= chars else f"{body[:chars]}...[+{len(body) - chars} chars]"
        blocks.append(f"<script{m.group('attrs')}>{rendered}</script>")
    markup = outside_blocks(page)
    types = _counts(_ITEMTYPE, markup, limits.max_microdata_types)
    props = _counts(_ITEMPROP, markup, limits.max_microdata_props)
    out = []
    if blocks:
        out.append(f"## structured data: {len(blocks)} JSON-LD block(s) (long lists shortened)")
        out += blocks
    if types:
        out.append(f"## microdata itemtypes: {'; '.join(f'{t} x{n}' for t, n in types)}")
        if props:
            out.append(f"itemprops: {', '.join(f'{p} x{n}' for p, n in props)}")
    return "\n".join(out)


def _head(page: str, limits: MaterialLimits) -> str:
    markup = outside_blocks(page)
    tags: list[str] = []
    if m := _TITLE.search(markup):
        tags.append(_SPACE.sub(" ", m.group(0)))
    for m in _META.finditer(markup):
        tag = m.group(0)
        key = _attr(tag, "name") or _attr(tag, "property") or ""
        if _attr(tag, "content") is not None and (_HEAD_META.search(key) or _attr(tag, "itemprop")):
            tags.append(tag)
    for m in _LINK.finditer(markup):
        rel = (_attr(m.group(0), "rel") or "").lower().split()
        if _HEAD_RELS & set(rel):
            tags.append(m.group(0))
    tags = tags[: limits.max_head_tags]
    return "## head\n" + "\n".join(tags) if tags else ""


def _visible_text(page: str) -> str:
    text = html_lib.unescape(_TAG.sub(" ", outside_blocks(page)))
    text = _SPACE.sub(" ", text).strip()
    return f"## visible text\n{text}" if text else ""


def _markup(page: str) -> str:
    body = _BODY.search(page)
    markup = _keep_blocks(page[body.start() if body else 0 :], lambda _: False).strip()
    return f"## body markup (start)\n{markup}" if markup else ""


def _cut(text: str, size: int) -> str:
    if len(text) <= size:
        return text
    marker = f"\n[... {len(text) - size} more characters]"
    return text[: max(0, size - len(marker))] + marker if size > len(marker) else ""


def html_digest(page: str, max_chars: int, limits: MaterialLimits, *, size_bytes: int | None = None) -> str:
    """A digest of ``page`` of at most ``max_chars`` characters (see the module docstring)."""
    intro = (
        f"[HTML digest of a {size_bytes if size_bytes is not None else _size(page)}-byte page: head tags, "
        "structured data, visible text and the start of the body markup. Lists in structured data are "
        "shortened: the page holds them in full.]\n"
    )
    budget = max(0, max_chars - len(intro) - (len(_SECTIONS) - 1))  # newlines between the sections
    sections = {
        "head": _head(page, limits),
        "structured": _structured(page, limits.max_list_items, limits.max_string_chars, limits),
        "text": _visible_text(page),
        "markup": _markup(page),
    }
    shares = {
        "head": limits.head_share,
        "structured": limits.structured_share,
        "text": limits.text_share,
    }
    caps = {k: int(budget * v) for k, v in shares.items()}
    caps["markup"] = budget - sum(caps.values())
    if len(sections["structured"]) > caps["structured"]:  # first shorten lists and strings further
        short = min(limits.short_string_chars, limits.max_string_chars)
        sections["structured"] = _structured(page, 1, short, limits)
    alloc = {k: min(len(sections[k]), caps[k]) for k in sections}
    left = budget - sum(alloc.values())
    for k in ("structured", "head", "text", "markup"):
        extra = min(left, len(sections[k]) - alloc[k])
        alloc[k] += extra
        left -= extra
    parts = [_cut(sections[k], alloc[k]) for k in _SECTIONS]
    return (intro + "\n".join(p for p in parts if p))[: max(0, max_chars)]


def material_text(text: str, media_type: str | None, max_chars: int, limits: MaterialLimits) -> str:
    """Text of a material for the model, at most ``max_chars`` characters: as is when it fits; HTML as a digest;
    anything else cut (with a marker when there is room for it)."""
    if len(text) <= max_chars:
        return text
    if is_html(media_type):
        return html_digest(text, max_chars, limits)
    widest = f"\n[... truncated {len(text)} characters]"  # the marker is never longer than this
    if max_chars <= len(widest):
        return text[: max(0, max_chars)]
    keep = max_chars - len(widest)
    return text[:keep] + f"\n[... truncated {len(text) - keep} characters]"


# ---------------------------------------------------------------------------------------------- evidence
def same_url(a: str, b: str) -> bool:
    """URLs equal up to the host case, the fragment, a default port and a trailing slash."""

    def norm(u: str) -> tuple[str, str, str, str]:
        p = urlsplit(u)
        host = (p.hostname or "").lower()
        port = p.port
        if port and not ((p.scheme == "http" and port == 80) or (p.scheme == "https" and port == 443)):
            host = f"{host}:{port}"
        return p.scheme.lower(), host, p.path.rstrip("/") or "/", p.query

    return norm(a) == norm(b)


def declared_canonical(page: str, base_url: str) -> str | None:
    """Absolute URL of the first ``<link rel="canonical">`` of the page (outside scripts and comments)."""
    for m in _LINK.finditer(outside_blocks(page)):
        tag = m.group(0)
        if "canonical" in (_attr(tag, "rel") or "").lower().split():
            href = _attr(tag, "href")
            if href:
                return urlunsplit(urlsplit(urljoin(base_url, href.strip()))._replace(fragment=""))
    return None


def page_links(page: str, base_url: str, hosts: Iterable[str] | None = None) -> list[str]:
    """Absolute http(s) links of ``<a href>`` outside scripts and comments (unique, in page order), optionally
    only on ``hosts``."""
    allowed = {h.lower() for h in hosts} if hosts is not None else None
    out: dict[str, None] = {}
    for m in _A_HREF.finditer(outside_blocks(page)):
        href = html_lib.unescape(next(g for g in m.groups() if g is not None)).strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        parts = urlsplit(urljoin(base_url, href))
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            continue
        host = parts.hostname.lower()
        if allowed is not None and not any(host == a or host.endswith("." + a) for a in allowed):
            continue
        out[urlunsplit(parts._replace(fragment=""))] = None
    return list(out)


def link_pattern(url: str) -> str:
    """``host/path`` with variable parts as ``*``; ``key=value`` path segments and query parameters keep the key
    (``page=*``, ``?page=*``), so pagination and filter links stay apart."""
    parts = urlsplit(url)
    segments = []
    for seg in parts.path.split("/"):
        if not seg:
            continue
        if "=" in seg:
            segments.append(";".join(f"{kv.split('=', 1)[0]}=*" for kv in seg.split(";") if kv))
        else:
            segments.append(segment_shape(seg))
    query = ""
    if parts.query:
        keys = sorted({kv.split("=", 1)[0] for kv in parts.query.split("&") if kv})
        query = "?" + "&".join(f"{k}=*" for k in keys)
    return f"{(parts.hostname or '').lower()}/{'/'.join(segments)}{query}"


def pagination_templates(links: Iterable[str]) -> dict[str, list[int]]:
    """Pagination-like URL templates among ``links``: one number in the path or query replaced by ``{n}`` that
    takes at least two values, the smallest of them at most ``_PAGINATION_START_MAX`` (``.../page=2/``)."""
    found: dict[str, set[int]] = {}
    for url in links:
        parts = urlsplit(url)
        head = f"{parts.scheme}://{parts.netloc}"
        rest = parts.path + (f"?{parts.query}" if parts.query else "")
        for m in _NUMBER.finditer(rest):
            template = head + rest[: m.start()] + "{n}" + rest[m.end() :]
            found.setdefault(template, set()).add(int(m.group(1)))
    return {
        t: sorted(values)
        for t, values in found.items()
        if len(values) >= 2 and min(values) <= _PAGINATION_START_MAX
    }
