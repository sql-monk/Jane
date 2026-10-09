"""Material documents (``material.schema.json``) and content delivery (inline / transit blob, ADR-0004)."""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .fetcher import HttpResult
from .urls import material_id

__all__ = [
    "MaterialTooLarge",
    "TransitStore",
    "build_item_material",
    "build_material",
    "content_kind",
    "new_observation_id",
    "rfc3339",
]

TEXT_TYPES = frozenset(
    {
        "application/json",
        "application/xml",
        "application/xhtml+xml",
        "application/rss+xml",
        "application/atom+xml",
        "application/javascript",
        "application/ld+json",
    }
)
UTF8_NAMES = frozenset({None, "utf-8", "utf8", "us-ascii", "ascii"})
EXTENSIONS = {
    "text/html": ".html",
    "application/json": ".json",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
}


class MaterialTooLarge(Exception):
    """Content above ``transfer.inline_max_bytes`` and no blob store configured (``limit_exceeded``)."""


def rfc3339(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


_last_ms = 0
_counter = 0


def new_observation_id() -> str:
    """``obs_`` + 12 hex of epoch ms + 4 hex counter + 8 hex random: sortable, monotonic within a process."""
    global _last_ms, _counter
    ms = int(time.time() * 1000)
    if ms <= _last_ms:
        _counter += 1
        ms = _last_ms
    else:
        _counter = 0
    _last_ms = ms
    return f"obs_{ms:012x}{_counter & 0xFFFF:04x}{secrets.token_hex(4)}"


def is_text(media_type: str) -> bool:
    return (
        media_type.startswith("text/") or media_type in TEXT_TYPES or media_type.endswith(("+xml", "+json"))
    )


def content_kind(media_type: str, url: str) -> str:
    lower = url.lower()
    if media_type in {"text/html", "application/xhtml+xml"}:
        return "page"
    if media_type in {"application/rss+xml", "application/atom+xml"}:
        return "feed"
    if "sitemap" in lower and (
        media_type.endswith("xml") or media_type in {"application/gzip", "application/x-gzip"}
    ):
        return "sitemap"
    if media_type == "application/json" or media_type.endswith("+json"):
        return "json"
    return "file"


class TransitStore:
    """Transit blobs on a local/shared directory (``file://`` URIs, single node or shared volume)."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def put(self, observation_id: str, body: bytes, media_type: str, now: datetime) -> Path:
        folder = self.root / "web-collector" / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{observation_id}{EXTENSIONS.get(media_type, '.bin')}"
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(body)
        os.replace(tmp, path)
        return path

    def cleanup(self, ttl_seconds: int) -> int:
        """Remove transit files older than their TTL (the producer's cleaner, ADR-0004)."""
        cutoff = time.time() - ttl_seconds
        removed = 0
        base = self.root / "web-collector"
        if not base.is_dir():
            return 0
        for path in base.rglob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
        return removed


@dataclass
class Delivery:
    mode: str  # auto | inline | blob
    inline_max_bytes: int
    transit_ttl_seconds: int
    store: TransitStore | None


def _content_ref(
    body: bytes,
    media_type: str,
    charset: str | None,
    observation_id: str,
    fetched_at: datetime,
    delivery: Delivery,
) -> dict[str, Any]:
    digest = hashlib.sha256(body).hexdigest()
    use_blob = delivery.mode == "blob" or (delivery.mode == "auto" and len(body) > delivery.inline_max_bytes)
    if use_blob:
        if delivery.store is None:
            raise MaterialTooLarge(
                f"{len(body)} bytes > transfer.inline_max_bytes={delivery.inline_max_bytes} and no blob store configured"
                if delivery.mode == "auto"
                else "content_delivery=blob but no blob store configured"
            )
        path = delivery.store.put(observation_id, body, media_type, fetched_at)
        ref: dict[str, Any] = {
            "kind": "blob",
            "uri": path.as_uri(),
            "media_type": media_type,
            "size_bytes": len(body),
            "sha256": digest,
            "store": "transit",
            "expires_at": rfc3339(fetched_at + timedelta(seconds=delivery.transit_ttl_seconds)),
        }
        if charset:
            ref["charset"] = charset
        return ref
    if delivery.mode == "inline" and len(body) > delivery.inline_max_bytes:
        raise MaterialTooLarge(f"{len(body)} bytes > transfer.inline_max_bytes={delivery.inline_max_bytes}")
    ref = {"kind": "inline", "media_type": media_type, "size_bytes": len(body), "sha256": digest}
    if charset:
        ref["charset"] = charset
    text: str | None = None
    if is_text(media_type) and charset in UTF8_NAMES:
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            text = None
    if text is not None:
        ref.update(encoding="utf-8", data=text)
    else:
        ref.update(encoding="base64", data=base64.b64encode(body).decode("ascii"))
    return ref


def build_material(
    result: HttpResult,
    *,
    canonical_url: str,
    observation_id: str,
    source_id: str | None,
    delivery: Delivery,
    collector_version: str,
    collection_id: str | None = None,
    rules_ref: Mapping[str, Any] | None = None,
    discovery: Mapping[str, Any] | None = None,
    html_meta: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    media_type = result.media_type
    material: dict[str, Any] = {
        "material_id": material_id(canonical_url),
        "observation_id": observation_id,
        "source": {"kind": "web", **({"source_id": source_id} if source_id else {})},
        "locator": {"url": result.url, "final_url": result.final_url, "canonical_url": canonical_url},
        "fetched_at": rfc3339(result.fetched_at),
        "format": {"media_type": media_type, "content_kind": content_kind(media_type, result.final_url)},
        "revision": {"content_sha256": hashlib.sha256(result.body).hexdigest()},
        "content": _content_ref(
            result.body, media_type, result.charset, observation_id, result.fetched_at, delivery
        ),
        "http": {"status": result.status, "headers": dict(result.headers)},
        "collector": {"name": "web-collector", "version": collector_version},
    }
    if result.charset:
        material["format"]["charset"] = result.charset
    if language := result.headers.get("content-language"):
        material["format"]["language"] = language.split(",")[0].strip()
    source_revision = result.headers.get("etag") or result.headers.get("last-modified")
    if source_revision:
        material["revision"]["source_revision"] = source_revision
    if result.redirects:
        material["http"]["redirects"] = list(result.redirects)
    if collection_id:
        material["collector"]["collection_id"] = collection_id
    if rules_ref:
        material["collector"]["rules"] = dict(rules_ref)
    if discovery:
        material["discovery"] = {k: v for k, v in discovery.items() if v is not None}
    meta = dict(html_meta or {})
    for prop, field in (("article:published_time", "published_at"), ("article:modified_time", "edited_at")):
        if prop in meta:
            try:
                material[field] = rfc3339(datetime.fromisoformat(meta.pop(prop).replace("Z", "+00:00")))
            except ValueError:
                meta.pop(prop, None)
    if meta.get("title"):
        material["metadata"] = {"title": meta["title"]}
    if result.truncated:
        material["diagnostics"] = [
            {
                "level": "warning",
                "code": "truncated",
                "message": "content cut at limits.crawl.max_material_bytes",
            }
        ]
    return material


def build_item_material(
    body: bytes,
    *,
    media_type: str,
    url: str,
    canonical_url: str,
    fetched_at: datetime,
    observation_id: str,
    source_id: str | None,
    delivery: Delivery,
    collector_version: str,
    collection_id: str | None = None,
    rules_ref: Mapping[str, Any] | None = None,
    discovery: Mapping[str, Any] | None = None,
    edited_at: datetime | None = None,
) -> dict[str, Any]:
    """Material of content a strategy already has (``api_feed`` JSON item, ``DiscoveryContext.emit_material``).

    The same document as for a fetched page, except that nothing was fetched at ``url``: no ``http`` and no
    ``locator.final_url``; ``fetched_at`` is when the API page with the item was fetched (its URL is
    ``discovery.parent_url``); ``edited_at`` is the item's ``lastmod``, if the strategy has one."""
    charset = "utf-8" if is_text(media_type) else None
    material: dict[str, Any] = {
        "material_id": material_id(canonical_url),
        "observation_id": observation_id,
        "source": {"kind": "web", **({"source_id": source_id} if source_id else {})},
        "locator": {"url": url, "canonical_url": canonical_url},
        "fetched_at": rfc3339(fetched_at),
        "format": {"media_type": media_type, "content_kind": content_kind(media_type, canonical_url)},
        "revision": {"content_sha256": hashlib.sha256(body).hexdigest()},
        "content": _content_ref(body, media_type, charset, observation_id, fetched_at, delivery),
        "collector": {"name": "web-collector", "version": collector_version},
    }
    if charset:
        material["format"]["charset"] = charset
    if edited_at is not None:
        material["edited_at"] = rfc3339(edited_at)
    if collection_id:
        material["collector"]["collection_id"] = collection_id
    if rules_ref:
        material["collector"]["rules"] = dict(rules_ref)
    if discovery:
        material["discovery"] = {k: v for k, v in discovery.items() if v is not None}
    return material
