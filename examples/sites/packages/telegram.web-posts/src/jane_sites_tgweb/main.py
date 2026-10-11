"""Posts of public Telegram channels from the web preview ``https://t.me/s/<channel>`` as ``post`` entities.

The preview page lists the latest messages of a channel, each as ``<div class="tgme_widget_message"
data-post="<channel>/<message id>">`` with the text in ``div.js-message_text`` (line breaks as ``<br>``, emoji
as ``<i class="emoji"><b>…</b></i>``), the time in ``time[datetime]``, the views in
``span.tgme_widget_message_views`` (``934``, ``99.4K``, ``1.2M``), ``edited`` in the meta line and the source of a
forward in ``.tgme_widget_message_forwarded_from_name``.

Every message with text becomes a ``post`` entity keyed by channel and message id - the same entity, key and
required fields as ``channels.telegram-posts`` (the Telethon path): link ``https://t.me/<channel>/<id>``,
publication time (RFC 3339, UTC), title (the first line with letters or digits; a longer one is cut to its first
sentence or to ``title_max_chars``) and the full text; plus the views, the source of a forward, the external
links of the text and link preview (not Telegram's own hosts), whether the message has media and whether it
was edited. The page is read again on every run, so a stored post gets its new views and edits (same key).

Service messages (``Channel created``, ``Channel photo updated``) and messages without text (media only) are
skipped. A page with no message with text is ``empty``; an HTML page that is not a Telegram channel page at all
is ``unrecognized``.
"""

from __future__ import annotations

import html
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urljoin, urlsplit

from lxml import etree  # type: ignore[import-untyped]
from lxml import html as lxml_html

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

TELEGRAM = "https://t.me/"
MESSAGES = '//div[contains(concat(" ", normalize-space(@class), " "), " tgme_widget_message ")][@data-post]'
CHANNEL_PAGE = (
    '//*[contains(concat(" ", normalize-space(@class), " "), " tgme_channel_info ")'
    ' or contains(concat(" ", normalize-space(@class), " "), " tgme_channel_history ")'
    ' or contains(concat(" ", normalize-space(@class), " "), " tgme_page ")]'
)
POST_ID = re.compile(r"([A-Za-z][A-Za-z0-9_]{2,63})/([0-9]{1,18})")
TELEGRAM_HOSTS = ("t.me", "telegram.me", "telegram.org", "telegram.dog", "telesco.pe")
MEDIA = frozenset(
    {
        "tgme_widget_message_photo_wrap",
        "tgme_widget_message_video_player",
        "tgme_widget_message_roundvideo_player",
        "tgme_widget_message_grouped_wrap",
        "tgme_widget_message_document_wrap",
        "tgme_widget_message_voice_player",
        "tgme_widget_message_sticker_wrap",
        "tgme_widget_message_location_wrap",
    }
)
SUFFIX = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
SENTENCE_END = re.compile(r"[.!?…](?=\s|$)")
EDITED = re.compile(r"\bedited\b", re.IGNORECASE)


def _has_class(cls: str) -> str:
    return f'contains(concat(" ", normalize-space(@class), " "), " {cls} ")'


def _first(node: Any, cls: str) -> Any | None:
    found = node.xpath(f".//*[{_has_class(cls)}]")
    return found[0] if found else None


def _clean(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\r", "").replace("​", "").replace("﻿", "")
    lines = [line.rstrip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _text(node: Any) -> str:
    for br in node.iter("br"):
        br.tail = "\n" + (br.tail or "")
    return _clean(node.text_content())


def _title(text: str, limit: int) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    line = next((x for x in lines if any(ch.isalnum() for ch in x)), lines[0] if lines else "")
    if len(line) <= limit:
        return line
    end = SENTENCE_END.search(line)
    if end and end.end() <= limit:
        return line[: end.end()]
    cut = line[: limit - 1]
    if " " in cut[limit // 2 :]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:-–—") + "…"


def _views(raw: str) -> int | None:
    value = raw.strip().replace(" ", "").replace(",", "")
    if not value:
        return None
    factor = SUFFIX.get(value[-1].upper(), 1)
    if factor != 1:
        value = value[:-1]
    try:
        return int(Decimal(value) * factor)
    except InvalidOperation:
        return None


def _published(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        moment = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _external(href: str | None) -> str | None:
    url = urljoin(TELEGRAM, html.unescape((href or "").strip()))  # the preview escapes "&" twice
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme not in ("http", "https") or not host:
        return None
    if any(host == h or host.endswith("." + h) for h in TELEGRAM_HOSTS):
        return None
    return url


def _links(text_node: Any, message: Any) -> list[str]:
    anchors = list(text_node.iter("a"))
    anchors += message.xpath(f".//a[{_has_class('tgme_widget_message_link_preview')}]")
    found = (_external(a.get("href")) for a in anchors)
    return list(dict.fromkeys(url for url in found if url))


def _post(message: Any, limit: int) -> dict[str, Any] | None:
    if "service_message" in (message.get("class") or "").split():
        return None
    match = POST_ID.fullmatch(message.get("data-post") or "")
    text_node = _first(message, "js-message_text")
    if match is None or text_node is None:
        return None
    links = _links(text_node, message)
    text = _text(text_node)
    if not text:
        return None
    channel, message_id = match.group(1), int(match.group(2))
    stamp = message.xpath(f".//a[{_has_class('tgme_widget_message_date')}]//time/@datetime")
    views = _first(message, "tgme_widget_message_views")
    meta = _first(message, "tgme_widget_message_meta")
    forwarded = _first(message, "tgme_widget_message_forwarded_from_name")
    classes = set(" ".join(message.xpath(".//@class")).split())
    return {
        "channel": channel,
        "message_id": message_id,
        "url": f"{TELEGRAM}{channel}/{message_id}",
        "published_at": _published(stamp[0] if stamp else None),
        "title": _title(text, limit),
        "text": text,
        "views": _views(views.text_content()) if views is not None else None,
        "forwarded_from": (_clean(forwarded.text_content()) or None) if forwarded is not None else None,
        "links": links or None,
        "has_media": bool(classes & MEDIA),
        "edited": bool(meta is not None and EDITED.search(meta.text_content())),
    }


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    source = ctx.text()
    if not source.strip():
        return empty()
    try:
        page = lxml_html.fromstring(source)
    except (etree.ParserError, ValueError):
        return unrecognized("not an HTML page", signature="tgweb:not-html")
    messages = page.xpath(MESSAGES)
    if not messages:
        if page.xpath(CHANNEL_PAGE):
            return empty()  # a channel (info) page without public messages
        return unrecognized(
            "no Telegram channel messages on the page",
            signature="missing-selector:div.tgme_widget_message[data-post]",
        )
    limit = int(params.get("title_max_chars") or 200)
    posts: dict[tuple[str, int], dict[str, Any]] = {}
    for message in messages:
        fields = _post(message, limit)
        if fields is not None:
            posts.setdefault((fields["channel"], fields["message_id"]), fields)
    if not posts:
        return empty()
    return success([entity("post", fields) for fields in posts.values()])
