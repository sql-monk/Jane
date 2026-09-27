"""Storage formats (TZ §5): RAW web pages as HTML by default, other results as JSON; overridable.

Format of a RAW material = ``params.format.raw`` → ``manifest.entry.format.raw`` → ``original``:

* ``original`` — bytes as received; the extension follows the media type (``text/html`` → ``.html``),
  so a web page is stored as HTML by default;
* ``html`` — the page as ``text/html`` (only for HTML materials);
* ``json`` — the Material document with its content embedded (``content.encoding`` utf-8/base64).

Entities are JSON documents; ``format.entities: jsonl`` is passed to the adapter
(``options["entities_format"]``), which may keep history as JSON Lines (filesystem adapter).
Other result documents (``writes: data``) are JSON.
"""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from jane_contracts.storage_adapter import RawFormat, RawObject

from .codec import parse_ts
from .keys import NO_SOURCE, object_key, safe_segment

__all__ = [
    "InvalidFormat",
    "build_data_object",
    "build_raw_object",
    "entities_format",
    "extension_for",
    "material_metadata",
    "raw_format",
]

HTML_TYPES = frozenset({"text/html", "application/xhtml+xml"})
RAW_FORMATS: frozenset[str] = frozenset({"original", "html", "json"})
_EXTENSIONS = {
    "text/html": "html",
    "application/xhtml+xml": "html",
    "application/json": "json",
    "application/ld+json": "json",
    "application/feed+json": "json",
    "text/plain": "txt",
    "text/xml": "xml",
    "application/xml": "xml",
    "application/rss+xml": "xml",
    "application/atom+xml": "xml",
    "text/csv": "csv",
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "application/gzip": "gz",
}


class InvalidFormat(ValueError):
    pass


def _bare(media_type: str) -> str:
    return media_type.split(";", 1)[0].strip().lower()


def extension_for(media_type: str) -> str:
    bare = _bare(media_type)
    if bare in _EXTENSIONS:
        return _EXTENSIONS[bare]
    if bare.endswith("+json"):
        return "json"
    if bare.endswith("+xml"):
        return "xml"
    return "bin"


def raw_format(params: Mapping[str, Any], entry: Mapping[str, Any]) -> str:
    fmt = (params.get("format") or {}).get("raw") or (entry.get("format") or {}).get("raw") or "original"
    return str(fmt)


def entities_format(params: Mapping[str, Any], entry: Mapping[str, Any]) -> str:
    fmt = (
        (params.get("format") or {}).get("entities") or (entry.get("format") or {}).get("entities") or "json"
    )
    return str(fmt)


def material_metadata(material: Mapping[str, Any]) -> dict[str, Any]:
    """Material without inline content data (kept next to the object for reprocessing)."""
    meta: dict[str, Any] = json.loads(json.dumps(material))
    content = meta.get("content")
    if isinstance(content, dict):
        content.pop("data", None)
    return meta


def build_raw_object(material: Mapping[str, Any], content: bytes, fmt: str) -> RawObject:
    media_type = _bare(str(material["format"]["media_type"]))
    stored_format: RawFormat
    if fmt == "original":
        stored_type, data, stored_format = media_type, content, "original"
    elif fmt == "html":
        if media_type not in HTML_TYPES:
            raise InvalidFormat(f"format.raw=html requires an HTML material, got {media_type}")
        stored_type, data, stored_format = "text/html", content, "html"
    elif fmt == "json":
        doc = material_metadata(material)
        base = dict(doc.get("content") or {})
        try:
            doc["content"] = {**base, "encoding": "utf-8", "data": content.decode("utf-8")}
        except UnicodeDecodeError:
            doc["content"] = {**base, "encoding": "base64", "data": base64.b64encode(content).decode("ascii")}
        stored_type, stored_format = "application/json", "json"
        data = json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    else:
        raise InvalidFormat(f"unknown raw format {fmt!r}")
    source = material.get("source") or {}
    key = object_key(
        material_id=str(material["material_id"]),
        observation_id=str(material["observation_id"]),
        source_id=source.get("source_id"),
        fetched_at=parse_ts(material["fetched_at"]),
        ext=extension_for(stored_type),
    )
    return RawObject(
        object_key=key,
        material_id=str(material["material_id"]),
        observation_id=str(material["observation_id"]),
        source_id=source.get("source_id"),
        media_type=stored_type,
        format=stored_format,
        content=data,
        sha256=hashlib.sha256(data).hexdigest(),
        metadata=material_metadata(material),
    )


def build_data_object(data: Any, *, delivery_key_digest: str, index: int, source_id: str | None) -> RawObject:
    """JSON result document of ``writes: data`` (e.g. an LLM output); the key depends only on the delivery."""
    body = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    material_id = f"data_{delivery_key_digest[:32]}"
    observation_id = f"part{index}"
    key = f"data/{safe_segment(source_id or NO_SOURCE)}/{material_id}/{observation_id}.json"
    return RawObject(
        object_key=key,
        material_id=material_id,
        observation_id=observation_id,
        source_id=source_id,
        media_type="application/json",
        format="json",
        content=body,
        sha256=hashlib.sha256(body).hexdigest(),
        metadata={"kind": "data"},
    )
