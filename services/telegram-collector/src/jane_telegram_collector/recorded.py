"""Recorded Telegram backend: channels replayed from JSON recordings (tests, demos, offline replays).

A recording ``<recordings_dir>/<username or channel_id>.json``::

    {
      "channel": {"channel_id": "-1001234567890", "username": "city_events_example", "title": "City events"},
      "required_secrets": ["session"],          # optional: the account must resolve these secret_refs
      "messages": [{"id": 1, "date": "2026-09-01T10:00:00Z", "text": "...", "edit_date": null,
                    "views": 10, "grouped_id": null, "author": null,
                    "media": [{"kind": "photo", "name": "p.jpg", "media_type": "image/jpeg", "data_base64": "..."}]}],
      "events": [{"pts": 1, "message": {...message as it was after this update...}}],
      "min_pts": 0,                             # updates before this pts are gone -> difference too long
      "faults": [{"method": "history", "flood_wait": 3, "count": 1},
                 {"method": "changes", "delay_ms": 500, "count": 1},
                 {"method": "resolve", "unavailable": true, "count": 1}]
    }

The file is re-read on every call, so another process (a test) may post and edit messages while the
collector runs. Consumed faults are counted in ``<file>.faults.json`` next to the recording.
:class:`Recording` writes the format (new message -> ``messages`` + event, edit -> updated message + event).
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .client import (
    AccountUnauthorized,
    ChangeBatch,
    ChannelInfo,
    ChannelUnavailable,
    ClientUnavailable,
    FloodWait,
    ResolvedAccount,
    TelegramClient,
    TgMedia,
    TgMessage,
)

__all__ = ["RecordedClient", "RecordedClientFactory", "Recording"]


_FILE_RETRIES = 50
_FILE_RETRY_DELAY_S = 0.02
"""Recorded backend only: a recording rewritten by another process may be locked for a moment on Windows
(``os.replace`` / read); up to 1 s of retries. Not an operational limit of the collector."""


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _ts(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_json(path: Path, data: Any) -> None:
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    for _ in range(_FILE_RETRIES):  # Windows: the reader may hold the file for a moment
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(_FILE_RETRY_DELAY_S)
    os.replace(tmp, path)


def _read_json(path: Path) -> dict[str, Any]:
    for _ in range(_FILE_RETRIES):
        try:
            data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
            return data
        except (PermissionError, json.JSONDecodeError):
            time.sleep(_FILE_RETRY_DELAY_S)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


class RecordedClientFactory:
    name = "recorded"

    def __init__(self, recordings_dir: Path | None) -> None:
        self.recordings_dir = recordings_dir

    def requires_account(self) -> bool:
        return False

    async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient:
        if self.recordings_dir is None:
            raise ClientUnavailable("recorded backend: JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR is not set")
        return RecordedClient(self.recordings_dir, account)


class RecordedClient:
    def __init__(self, root: Path, account: ResolvedAccount) -> None:
        self.root = root
        self.account = account

    # ------------------------------------------------------------------ files
    def _files(self) -> list[Path]:
        if not self.root.is_dir():
            return []
        return sorted(p for p in self.root.glob("*.json") if not p.name.endswith(".faults.json"))

    def _find(self, *, username: str | None, channel_id: str | None) -> Path:
        for key in (username, channel_id):
            if key and (self.root / f"{key}.json").is_file():
                return self.root / f"{key}.json"
        for path in self._files():
            channel = _read_json(path).get("channel") or {}
            if (channel_id and channel.get("channel_id") == channel_id) or (
                username and str(channel.get("username", "")).lower() == username.lower()
            ):
                return path
        raise ChannelUnavailable(f"channel {username or channel_id} not found")

    def _load(self, channel: ChannelInfo) -> tuple[Path, dict[str, Any]]:
        path = self._find(username=channel.username, channel_id=channel.channel_id)
        return path, _read_json(path)

    async def _faults(self, path: Path, data: Mapping[str, Any], method: str) -> None:
        faults = data.get("faults") or []
        if not faults:
            return
        used_path = path.with_name(path.stem + ".faults.json")
        used: dict[str, int] = _read_json(used_path) if used_path.is_file() else {}
        for i, fault in enumerate(faults):
            if fault.get("method") not in (method, "*"):
                continue
            if used.get(str(i), 0) >= int(fault.get("count", 1)):
                continue
            used[str(i)] = used.get(str(i), 0) + 1
            _write_json(used_path, used)
            if fault.get("delay_ms"):
                await asyncio.sleep(int(fault["delay_ms"]) / 1000)
            if fault.get("flood_wait") is not None:
                raise FloodWait(int(fault["flood_wait"]))
            if fault.get("unavailable"):
                raise ClientUnavailable(f"recorded fault in {method}")
            return

    def _check_account(self, data: Mapping[str, Any]) -> None:
        missing = [s for s in data.get("required_secrets") or [] if not self.account.secrets.get(s)]
        if missing:
            raise AccountUnauthorized(f"account session is not authorized (missing secrets {missing})")

    def _message(self, channel_id: str, raw: Mapping[str, Any]) -> TgMessage:
        media = tuple(
            TgMedia(
                kind=str(m.get("kind", "document")),
                name=str(m.get("name", f"media-{i}")),
                media_type=str(m.get("media_type", "application/octet-stream")),
                size_bytes=len(base64.b64decode(m["data_base64"]))
                if m.get("data_base64")
                else m.get("size_bytes"),
                ref=f"{raw['id']}:{i}",
            )
            for i, m in enumerate(raw.get("media") or [])
        )
        date = _parse_ts(raw.get("date"))
        if date is None:
            raise ValueError(f"message {raw.get('id')} has no date")
        return TgMessage(
            channel_id=channel_id,
            message_id=int(raw["id"]),
            date=date,
            text=str(raw.get("text") or ""),
            edit_date=_parse_ts(raw.get("edit_date")),
            grouped_id=str(raw["grouped_id"]) if raw.get("grouped_id") else None,
            views=raw.get("views"),
            author=raw.get("author"),
            media=media,
        )

    @staticmethod
    def _pts(data: Mapping[str, Any]) -> int:
        events = data.get("events") or []
        return max([int(e["pts"]) for e in events] + [int(data.get("pts", 0))])

    # ------------------------------------------------------------------ TelegramClient
    async def resolve(self, *, username: str | None = None, channel_id: str | None = None) -> ChannelInfo:
        path = self._find(username=username, channel_id=channel_id)
        data = _read_json(path)
        self._check_account(data)
        await self._faults(path, data, "resolve")
        ch = data.get("channel") or {}
        messages = data.get("messages") or []
        return ChannelInfo(
            channel_id=str(ch["channel_id"]),
            username=ch.get("username"),
            title=ch.get("title"),
            top_message_id=max([int(m["id"]) for m in messages] + [0]),
            pts=self._pts(data),
        )

    async def history(
        self, channel: ChannelInfo, *, after_id: int, limit: int, since: datetime | None = None
    ) -> list[TgMessage]:
        path, data = self._load(channel)
        self._check_account(data)
        await self._faults(path, data, "history")
        out = [
            self._message(channel.channel_id, m)
            for m in sorted(data.get("messages") or [], key=lambda m: int(m["id"]))
            if int(m["id"]) > after_id
        ]
        if since is not None:
            out = [m for m in out if m.date >= since]
        return out[:limit]

    async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None:
        path, data = self._load(channel)
        self._check_account(data)
        await self._faults(path, data, "get_message")
        for m in data.get("messages") or []:
            if int(m["id"]) == message_id:
                return self._message(channel.channel_id, m)
        return None

    async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch:
        path, data = self._load(channel)
        self._check_account(data)
        await self._faults(path, data, "changes")
        current = self._pts(data)
        if pts < int(data.get("min_pts", 0)):
            return ChangeBatch(messages=[], pts=current, final=True, too_long=True)
        events = sorted(
            (e for e in data.get("events") or [] if int(e["pts"]) > pts), key=lambda e: int(e["pts"])
        )
        batch = events[:limit]
        return ChangeBatch(
            messages=[self._message(channel.channel_id, e["message"]) for e in batch],
            pts=int(batch[-1]["pts"]) if batch else max(pts, current),
            final=len(events) <= limit,
        )

    async def download_media(self, channel: ChannelInfo, media: TgMedia, *, max_bytes: int) -> bytes:
        path, data = self._load(channel)
        await self._faults(path, data, "download_media")
        message_id, _, index = media.ref.partition(":")
        for m in data.get("messages") or []:
            if str(m["id"]) == message_id:
                raw = base64.b64decode((m.get("media") or [])[int(index)].get("data_base64") or "")
                if len(raw) > max_bytes:
                    raise ValueError(f"media {media.name}: {len(raw)} bytes > {max_bytes}")
                return raw
        raise ChannelUnavailable(f"message {message_id} not found")

    async def close(self) -> None:
        return None


@dataclass
class Recording:
    """Writer of a recording file (for tests and hand-made demos)."""

    path: Path
    channel_id: str
    username: str | None = None
    title: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls, root: Path, *, channel_id: str, username: str | None = None, title: str | None = None
    ) -> Recording:
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{username or channel_id}.json"
        rec = cls(path, channel_id, username, title)
        rec.data = {
            "channel": {
                k: v for k, v in {"channel_id": channel_id, "username": username, "title": title}.items() if v
            },
            "messages": [],
            "events": [],
        }
        rec.save()
        return rec

    def save(self) -> None:
        _write_json(self.path, self.data)

    def reload(self) -> None:
        self.data = _read_json(self.path)

    def _event(self, message: Mapping[str, Any]) -> None:
        pts = RecordedClient._pts(self.data) + 1
        self.data.setdefault("events", []).append({"pts": pts, "message": dict(message)})

    def post(
        self,
        text: str,
        *,
        date: datetime | None = None,
        media: list[dict[str, Any]] | None = None,
        save: bool = True,
        **extra: Any,
    ) -> int:
        messages = self.data.setdefault("messages", [])
        message_id = max([int(m["id"]) for m in messages] + [0]) + 1
        msg: dict[str, Any] = {
            "id": message_id,
            "date": _ts(date or datetime.now(UTC)),
            "text": text,
            **extra,
        }
        if media:
            msg["media"] = media
        messages.append(msg)
        self._event(msg)
        if save:
            self.save()
        return message_id

    def edit(
        self, message_id: int, text: str, *, edit_date: datetime | None = None, save: bool = True
    ) -> None:
        for msg in self.data["messages"]:
            if int(msg["id"]) == message_id:
                msg["text"] = text
                msg["edit_date"] = _ts(edit_date or datetime.now(UTC))
                self._event(msg)
                break
        else:
            raise KeyError(message_id)
        if save:
            self.save()

    def redeliver(self, message_id: int) -> None:
        """Append an update carrying the current (unchanged) state of a message again."""
        msg = next(m for m in self.data["messages"] if int(m["id"]) == message_id)
        self._event(msg)
        self.save()

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()
