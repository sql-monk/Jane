"""Material content helpers: decode ``ContentRef`` (inline / blob), URL shapes, truncation.

Material content is untrusted data. It is only ever placed in ``data`` parts of LLM requests
(``llm.v1`` ``DataPart``) and in package test fixtures, never in instructions.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit
from urllib.request import url2pathname

import httpx

from jane_kit.errors import JaneError

__all__ = [
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


async def material_bytes(material: dict[str, Any], http: httpx.AsyncClient | None = None) -> bytes:
    """Bytes of ``material.content``: inline (utf-8/base64) or blob via ``download_url`` or
    ``file://``. ``sha256`` is checked when present (contract: every consumer verifies it)."""
    content = material.get("content") or {}
    kind = content.get("kind")
    if kind == "inline":
        data = str(content.get("data", ""))
        raw = base64.b64decode(data) if content.get("encoding") == "base64" else data.encode("utf-8")
    elif kind == "blob":
        if content.get("download_url"):
            client = http or httpx.AsyncClient()
            try:
                r = await client.get(str(content["download_url"]))
                r.raise_for_status()
                raw = r.content
            finally:
                if http is None:
                    await client.aclose()
        elif str(content.get("uri", "")).startswith("file://"):
            path = Path(url2pathname(unquote(urlsplit(str(content["uri"])).path)))
            raw = await asyncio.to_thread(path.read_bytes)
        else:
            raise JaneError(
                f"blob {content.get('uri')} has no download_url; the assistant reads blobs only via "
                "download_url or file://",
                code="not_implemented",
            )
    else:
        raise JaneError("material has no content", code="validation_failed")
    expected = content.get("sha256")
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise JaneError(f"content sha256 mismatch for {material.get('material_id')}", code="digest_mismatch")
    return raw


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
