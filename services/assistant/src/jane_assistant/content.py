"""Material content helpers: read ``ContentRef`` (inline / blob) under the ContentRef policy, URL shapes,
truncation.

Material content is untrusted data. It is only ever placed in ``data`` parts of LLM requests
(``llm.v1`` ``DataPart``) and in package test fixtures, never in instructions.

Reading (WP-01h) goes through ``jane_kit.content.ContentReader``: ``file://`` only inside
``JANE_ASSISTANT_BLOB_ROOTS``, ``download_url`` only to ``JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST`` hosts (both empty
by default), no redirects, size and timeouts from ``limits.content``. The app installs its
:class:`MaterialContent` with :class:`MaterialContentScope` for every request, so the jobs a request starts
(onboarding sampling, improvement samples, unknown materials) read with it; outside an app (or without a scope)
:func:`material_bytes` reads inline content only.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from starlette.types import ASGIApp, Receive, Scope, Send

from jane_kit.content import ContentReader
from jane_kit.errors import ValidationFailed

from .settings import ContentLimits, ServiceLimits, Settings

__all__ = [
    "MaterialContent",
    "MaterialContentScope",
    "decode_text",
    "host_of",
    "material_bytes",
    "material_label",
    "truncate",
    "url_shape",
]

_NUMERIC = re.compile(r"^\d+$")
_HEXISH = re.compile(r"^[0-9a-f]{8,}$", re.I)
_SLUGGY = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)+$", re.I)


@dataclass(frozen=True)
class MaterialContent:
    """Reads ``material.content`` with the assistant's ContentRef policy and ``limits.content``."""

    reader: ContentReader
    max_bytes: int

    @classmethod
    def from_settings(cls, settings: Settings, limits: ServiceLimits) -> MaterialContent:
        return cls(
            ContentReader(
                timeout_ms=limits.content.fetch_timeout_ms,
                connect_timeout_ms=limits.content.connect_timeout_ms,
                blob_roots=settings.blob_roots,
                download_host_allowlist=settings.download_host_allowlist,
                settings_prefix="JANE_ASSISTANT_",
            ),
            limits.content.max_material_bytes,
        )

    async def read(self, material: Mapping[str, Any]) -> bytes:
        content = material.get("content")
        if not isinstance(content, Mapping) or not content:
            raise ValidationFailed("material has no content")
        return await self.reader.read(content, max_bytes=self.max_bytes, limit="content.max_material_bytes")


_INLINE_ONLY = MaterialContent(
    ContentReader(timeout_ms=ContentLimits().fetch_timeout_ms), ContentLimits().max_material_bytes
)
_current: ContextVar[MaterialContent] = ContextVar("jane_assistant_material_content", default=_INLINE_ONLY)


class MaterialContentScope:
    """ASGI middleware: a request of the app, and every job it starts (tasks copy the context), reads material
    content with ``content``."""

    def __init__(self, app: ASGIApp, content: MaterialContent) -> None:
        self.app = app
        self.content = content

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        token = _current.set(self.content)
        try:
            await self.app(scope, receive, send)
        finally:
            _current.reset(token)


async def material_bytes(material: Mapping[str, Any], content: MaterialContent | None = None) -> bytes:
    """Bytes of ``material.content`` (``sha256`` verified when present). ``content`` defaults to the reader of
    the current app (:class:`MaterialContentScope`), else inline only."""
    return await (content or _current.get()).read(material)


def decode_text(raw: bytes, charset: str | None = None) -> str:
    try:
        return raw.decode(charset or "utf-8")
    except (UnicodeDecodeError, LookupError):
        return raw.decode("utf-8", errors="replace")


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n[... truncated {len(text) - max_chars} characters]"


def host_of(url: str | None) -> str | None:
    if not url:
        return None
    host = urlsplit(url).hostname
    return host.lower() if host else None


def url_shape(material: dict[str, Any]) -> str:
    """Structural signature of a material's URL (``host/product/*``) used to diversify samples:
    variable path segments (numbers, hashes, slugs) collapse to ``*``."""
    locator = material.get("locator") or {}
    if "telegram" in locator:
        text_len = len(str((material.get("content") or {}).get("data", "")))
        return f"telegram/{min(text_len // 500, 4)}"
    url = locator.get("canonical_url") or locator.get("final_url") or locator.get("url") or ""
    parts = urlsplit(url)
    segments = []
    for seg in parts.path.split("/"):
        if not seg:
            continue
        if _NUMERIC.match(seg) or _HEXISH.match(seg) or _SLUGGY.match(seg):
            segments.append("*")
        else:
            segments.append(seg.lower())
    query = "?q" if parts.query else ""
    return f"{(parts.hostname or '').lower()}/{'/'.join(segments)}{query}"


def material_label(material: dict[str, Any]) -> str:
    locator = material.get("locator") or {}
    if "telegram" in locator:
        tg = locator["telegram"]
        return f"telegram:{tg.get('channel_username') or tg.get('channel_id')}/{tg.get('message_id')}"
    return str(locator.get("canonical_url") or locator.get("url") or material.get("material_id"))
