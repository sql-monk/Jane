"""Material documents for Telegram messages (``material.schema.json``) and content delivery (ADR-0004).

* ``material_id`` = ``tg:<channel_id>:<message_id>`` — the same for every observation of the message;
* ``observation_id`` — new for every read from Telegram (history, update, edit, one-shot fetch);
* ``revision.sequence`` = ``edit_date`` (or ``date`` for an unedited message) as epoch seconds,
  ``revision.is_edit`` = Telegram marked the message as edited, ``revision.content_sha256`` = sha256 of the text;
* content: the message text (``text/plain``, UTF-8) inline, or a transit blob (``file://``) if asked or larger
  than ``transfer.inline_max_bytes``; downloaded media go to ``attachments`` the same way.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .client import ChannelInfo, TgMedia, TgMessage

__all__ = [
    "ContentTooLarge",
    "Delivery",
    "TransitStore",
    "build_material",
    "message_sequence",
    "message_sha",
    "new_observation_id",
    "rfc3339",
]

EXTENSIONS = {"text/plain": ".txt", "image/jpeg": ".jpg", "image/png": ".png", "video/mp4": ".mp4"}


class ContentTooLarge(Exception):
    """Content above ``transfer.inline_max_bytes`` and no blob store (or ``content_delivery=inline``)."""


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


def material_id(channel_id: str, message_id: int) -> str:
    return f"tg:{channel_id}:{message_id}"


def message_sequence(msg: TgMessage) -> int:
    return int((msg.edit_date or msg.date).timestamp())


def message_sha(msg: TgMessage) -> str:
    return hashlib.sha256(msg.text.encode("utf-8")).hexdigest()


class TransitStore:
    """Transit blobs on a local/shared directory (``file://`` URIs, single node or shared volume)."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    @property
    def base(self) -> Path:
        return self.root / "telegram-collector"

    def put(self, name: str, body: bytes, media_type: str, now: datetime) -> Path:
        folder = self.base / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}{EXTENSIONS.get(media_type, '.bin')}"
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(body)
        os.replace(tmp, path)
        return path

    def cleanup(self, ttl_seconds: int) -> int:
        """Remove transit files older than their TTL (the producer's cleaner, ADR-0004)."""
        cutoff = time.time() - ttl_seconds
        removed = 0
        if not self.base.is_dir():
            return 0
        for path in self.base.rglob("*"):
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

    def content_ref(
        self, body: bytes, media_type: str, name: str, now: datetime, *, text: bool
    ) -> dict[str, Any]:
        digest = hashlib.sha256(body).hexdigest()
        too_big = len(body) > self.inline_max_bytes
        if self.mode == "inline" and too_big:
            raise ContentTooLarge(
                f"{len(body)} bytes > transfer.inline_max_bytes={self.inline_max_bytes} (content_delivery=inline)"
            )
        if self.mode == "blob" or (self.mode == "auto" and too_big):
            if self.store is None:
                raise ContentTooLarge(
                    f"{len(body)} bytes > transfer.inline_max_bytes={self.inline_max_bytes} and no blob store configured"
                    if self.mode == "auto"
                    else "content_delivery=blob but no blob store configured"
                )
            path = self.store.put(name, body, media_type, now)
            ref: dict[str, Any] = {
                "kind": "blob",
                "uri": path.as_uri(),
                "media_type": media_type,
                "size_bytes": len(body),
                "sha256": digest,
                "store": "transit",
                "expires_at": rfc3339(now + timedelta(seconds=self.transit_ttl_seconds)),
            }
            if text:
                ref["charset"] = "utf-8"
            return ref
        if text:
            return {
                "kind": "inline",
                "media_type": media_type,
                "charset": "utf-8",
                "encoding": "utf-8",
                "data": body.decode("utf-8"),
                "size_bytes": len(body),
                "sha256": digest,
            }
        return {
            "kind": "inline",
            "media_type": media_type,
            "encoding": "base64",
            "data": base64.b64encode(body).decode("ascii"),
            "size_bytes": len(body),
            "sha256": digest,
        }


def message_url(channel: ChannelInfo, message_id: int) -> str:
    if channel.username:
        return f"https://t.me/{channel.username}/{message_id}"
    internal = (
        channel.channel_id[4:] if channel.channel_id.startswith("-100") else channel.channel_id.lstrip("-")
    )
    return f"https://t.me/c/{internal}/{message_id}"


def build_material(
    msg: TgMessage,
    channel: ChannelInfo,
    *,
    observation_id: str,
    delivery: Delivery,
    collector_version: str,
    source_id: str | None = None,
    strategy: str | None = None,
    rules_ref: Mapping[str, Any] | None = None,
    collection_id: str | None = None,
    attachments: Sequence[tuple[TgMedia, dict[str, Any]]] = (),
    diagnostics: Sequence[Mapping[str, Any]] = (),
    now: datetime | None = None,
) -> dict[str, Any]:
    fetched = now or datetime.now(UTC)
    body = msg.text.encode("utf-8")
    sequence = message_sequence(msg)
    telegram: dict[str, Any] = {"channel_id": channel.channel_id, "message_id": msg.message_id}
    if channel.username:
        telegram["channel_username"] = channel.username
    if msg.grouped_id:
        telegram["grouped_id"] = msg.grouped_id
    source: dict[str, Any] = {"kind": "telegram"}
    if source_id:
        source["source_id"] = source_id
    if channel.title:
        source["name"] = channel.title
    collector: dict[str, Any] = {"name": "telegram-collector", "version": collector_version}
    if rules_ref:
        collector["rules"] = dict(rules_ref)
    if collection_id:
        collector["collection_id"] = collection_id
    material: dict[str, Any] = {
        "material_id": material_id(channel.channel_id, msg.message_id),
        "observation_id": observation_id,
        "source": source,
        "locator": {"url": message_url(channel, msg.message_id), "telegram": telegram},
        "fetched_at": rfc3339(fetched),
        "published_at": rfc3339(msg.date),
        "format": {"media_type": "text/plain", "charset": "utf-8", "content_kind": "message"},
        "revision": {
            "content_sha256": hashlib.sha256(body).hexdigest(),
            "source_revision": str(sequence),
            "sequence": sequence,
            "is_edit": msg.edit_date is not None,
        },
        "content": delivery.content_ref(body, "text/plain", observation_id, fetched, text=True),
        "collector": collector,
    }
    if msg.edit_date is not None:
        material["edited_at"] = rfc3339(msg.edit_date)
    if strategy:
        material["discovery"] = {"strategy": strategy}
    if attachments:
        material["attachments"] = [{"name": m.name, "role": m.kind, "content": ref} for m, ref in attachments]
    if diagnostics:
        material["diagnostics"] = [dict(d) for d in diagnostics]
    metadata: dict[str, Any] = {}
    if msg.views is not None:
        metadata["views"] = msg.views
    if msg.author:
        metadata["author"] = msg.author
    if msg.media:
        metadata["media"] = [
            {
                k: v
                for k, v in {
                    "kind": m.kind,
                    "name": m.name,
                    "media_type": m.media_type,
                    "size_bytes": m.size_bytes,
                }.items()
                if v is not None
            }
            for m in msg.media
        ]
    if metadata:
        material["metadata"] = metadata
    return material
