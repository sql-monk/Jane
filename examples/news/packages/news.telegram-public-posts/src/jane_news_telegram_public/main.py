"""Prepare individual public Telegram messages for the news analysis stage."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success

_POST = re.compile(r"^([A-Za-z0-9_]+)/([0-9]+)$")
_EXCLUDED_CLASSES = frozenset(
    {
        "tgme_widget_message_reply",
        "js-message_reply_text",
        "tgme_widget_message_link_preview",
        "tgme_widget_message_footer",
        "tgme_widget_message_author",
        "tgme_widget_message_user",
    }
)
_VOID = frozenset(
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


class PublicFeed(HTMLParser):
    """Read message text, excluding footer, link previews and reply excerpts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.posts: list[dict[str, Any]] = []
        self._stack: list[str] = []
        self._post_depth: int | None = None
        self._text_depth: int | None = None
        self._post: dict[str, Any] | None = None
        self._parts: list[str] = []
        self._ignore_depth: int | None = None
        self._ignore_times = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag not in _VOID:
            self._stack.append(tag)
        depth = len(self._stack)
        if "tgme_widget_message" in classes:
            match = _POST.fullmatch(values.get("data-post") or "")
            if match:
                self._post = {"channel": match.group(1).casefold(), "message_id": int(match.group(2))}
                self._parts = []
                self._post_depth = depth
                self._text_depth = None
                self._ignore_depth = None
                self._ignore_times = False
        if self._post is None:
            return
        # Reply excerpts also carry message_text; ignore their whole subtree
        # before recognizing a body, including nested text and line breaks.
        if self._ignore_depth is None and (classes & _EXCLUDED_CLASSES or tag in {"script", "style"}):
            self._ignore_depth = depth
            self._ignore_times = "tgme_widget_message_footer" not in classes
        # The footer's timestamp belongs to this post; a reply's timestamp does not.
        if tag == "time" and values.get("datetime") and not self._ignore_times:
            try:
                stamp = datetime.fromisoformat(str(values["datetime"]).replace("Z", "+00:00"))
                if stamp.tzinfo is not None:
                    self._post["published_at"] = stamp.astimezone(UTC).isoformat().replace("+00:00", "Z")
            except ValueError:
                pass
        if self._ignore_depth is not None:
            return
        if "tgme_widget_message_text" in classes and self._text_depth is None:
            self._text_depth = depth
        if self._text_depth is not None and tag == "br":
            self._parts.append("\n")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag not in self._stack:
            return
        index = len(self._stack) - 1 - self._stack[::-1].index(tag)
        closing_depth = index + 1
        if self._ignore_depth is not None and closing_depth <= self._ignore_depth:
            self._ignore_depth = None
            self._ignore_times = False
        if self._text_depth is not None and closing_depth <= self._text_depth:
            self._text_depth = None
        if self._post_depth is not None and closing_depth <= self._post_depth:
            if self._post is not None:
                self._post["text"] = "\n".join(
                    " ".join(line.split()) for line in "".join(self._parts).splitlines() if line.strip()
                ).strip()
                if self._post["text"]:
                    self.posts.append(self._post)
            self._post = None
            self._post_depth = None
            self._text_depth = None
            self._ignore_depth = None
            self._ignore_times = False
        del self._stack[index:]

    def handle_data(self, data: str) -> None:
        if self._text_depth is not None and self._ignore_depth is None:
            self._parts.append(data)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    parser = PublicFeed()
    parser.feed(ctx.text())
    # Repeated embeds of the same post do not become separate articles.
    posts = {(post["channel"], post["message_id"]): post for post in parser.posts}
    maximum = int(params.get("max_posts", 3))
    selected = list(posts.values())[-maximum:]
    if not selected:
        return empty()
    source_id = str((material.get("source") or {}).get("source_id") or "telegram-public")
    output = []
    for post in selected:
        title = post["text"].splitlines()[0]
        title_max = int(params.get("title_max_chars", 300))
        fields = {
            **post,
            "url": f"https://t.me/{post['channel']}/{post['message_id']}",
            "title": title if len(title) <= title_max else title[:title_max].rstrip(),
            "source_id": source_id,
            "source_name": str(params.get("source_name") or post["channel"]),
            "source_kind": "telegram",
            "transport": "telegram_public_web",
            "region": str(params.get("region", "unknown")),
            "language": str(params.get("language", "und")),
        }
        output.append(entity("article", fields))
    return success(output)
