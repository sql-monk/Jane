"""MTProto backend on Telethon (optional extra ``telethon``: ``uv sync --package jane-telegram-collector --extra telethon``).

NOT verified against the real Telegram service (no test account in the project): the adapter follows the
Telethon 1.x API and is covered only by the shared collector tests through the recorded backend.

The ``telegram_account`` connection (ADR-0006, README "Підключення"):

* ``params.api_id`` — application id from my.telegram.org (not a secret);
* ``secret_refs.api_hash`` — application hash;
* ``secret_refs.session`` — Telethon ``StringSession`` of an already authorized account (created offline,
  interactive login is not part of the service).
"""

from __future__ import annotations

import asyncio
import importlib
import re
from datetime import UTC, datetime
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

__all__ = ["TelethonClientFactory"]


def _telethon() -> Any:
    try:
        return importlib.import_module("telethon")
    except ImportError as exc:  # pragma: no cover - depends on the optional extra
        raise ClientUnavailable(
            "telethon backend: install the 'telethon' extra of jane-telegram-collector"
        ) from exc


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def service_action(action: Any) -> str:
    """``MessageActionChannelCreate`` -> ``channel_create`` (the action of a ``MessageService``)."""
    name = type(action).__name__
    return _snake(name.removeprefix("MessageAction") or name)


def _utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class TelethonClientFactory:
    name = "telethon"

    def requires_account(self) -> bool:
        return True

    async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient:
        telethon = _telethon()
        sessions = importlib.import_module("telethon.sessions")
        api_id = account.params.get("api_id")
        api_hash = account.secrets.get("api_hash")
        session = account.secrets.get("session")
        if not api_id or not api_hash or not session:
            raise AccountUnauthorized(
                "telegram_account needs params.api_id, secret_refs.api_hash and secret_refs.session"
            )
        client = telethon.TelegramClient(
            sessions.StringSession(session), int(str(api_id)), api_hash, timeout=connect_timeout_s
        )
        try:
            async with asyncio.timeout(connect_timeout_s):
                await client.connect()
                if not await client.is_user_authorized():
                    raise AccountUnauthorized("telegram session is not authorized")
        except TimeoutError as exc:
            await client.disconnect()
            raise ClientUnavailable("telegram connect timed out") from exc
        return TelethonClient(client)


class TelethonClient:
    def __init__(self, client: Any) -> None:
        self.client = client
        self.errors = importlib.import_module("telethon.errors")
        self.functions = importlib.import_module("telethon.functions")
        self.types = importlib.import_module("telethon.types")
        self._entities: dict[str, Any] = {}

    async def _call(self, coro: Any) -> Any:
        try:
            return await coro
        except self.errors.FloodWaitError as exc:
            raise FloodWait(int(exc.seconds)) from exc
        except (self.errors.AuthKeyError, self.errors.UnauthorizedError) as exc:
            raise AccountUnauthorized(str(exc)) from exc
        except (ValueError, self.errors.ChannelPrivateError, self.errors.UsernameNotOccupiedError) as exc:
            raise ChannelUnavailable(str(exc)) from exc
        except (ConnectionError, self.errors.ServerError, self.errors.RPCError) as exc:
            raise ClientUnavailable(str(exc)) from exc

    def _message(self, channel_id: str, msg: Any) -> TgMessage:
        media: list[TgMedia] = []
        if getattr(msg, "media", None) is not None:
            kind = "photo" if msg.photo else "video" if msg.video else "audio" if msg.audio else "document"
            file = msg.file
            media.append(
                TgMedia(
                    kind=kind,
                    name=(file.name if file and file.name else f"{kind}-{msg.id}{file.ext if file else ''}"),
                    media_type=(file.mime_type if file and file.mime_type else "application/octet-stream"),
                    size_bytes=file.size if file else None,
                    ref=str(msg.id),
                )
            )
        date = _utc(msg.date)
        if date is None:
            raise ClientUnavailable(f"message {msg.id} without date")
        action = getattr(msg, "action", None) if isinstance(msg, self.types.MessageService) else None
        return TgMessage(
            channel_id=channel_id,
            message_id=int(msg.id),
            date=date,
            text=getattr(msg, "message", None) or "",
            edit_date=_utc(getattr(msg, "edit_date", None)),
            grouped_id=str(msg.grouped_id) if getattr(msg, "grouped_id", None) else None,
            views=getattr(msg, "views", None),
            author=getattr(msg, "post_author", None),
            media=tuple(media),
            service_action=service_action(action) if action is not None else None,
        )

    async def resolve(self, *, username: str | None = None, channel_id: str | None = None) -> ChannelInfo:
        target: Any = username
        if target is None and channel_id is not None:
            raw = int(channel_id)
            target = self.types.PeerChannel(int(str(raw)[4:]) if str(raw).startswith("-100") else abs(raw))
        entity = await self._call(self.client.get_entity(target))
        full = await self._call(self.client(self.functions.channels.GetFullChannelRequest(entity)))
        top = await self._call(self.client.get_messages(entity, limit=1))
        cid = f"-100{entity.id}"
        self._entities[cid] = entity
        return ChannelInfo(
            channel_id=cid,
            username=getattr(entity, "username", None),
            title=getattr(entity, "title", None),
            top_message_id=int(top[0].id) if top else 0,
            pts=int(full.full_chat.pts),
        )

    async def _entity(self, channel: ChannelInfo) -> Any:
        if channel.channel_id not in self._entities:
            await self.resolve(username=channel.username, channel_id=channel.channel_id)
        return self._entities[channel.channel_id]

    async def history(
        self, channel: ChannelInfo, *, after_id: int, limit: int, since: datetime | None = None
    ) -> list[TgMessage]:
        entity = await self._entity(channel)
        kwargs: dict[str, Any] = {"min_id": after_id, "limit": limit, "reverse": True}
        if since is not None and after_id == 0:
            kwargs["offset_date"] = since
        msgs = await self._call(self.client.get_messages(entity, **kwargs))
        out = [self._message(channel.channel_id, m) for m in msgs if m is not None and m.id > after_id]
        if since is not None:
            out = [m for m in out if m.date >= since]
        return sorted(out, key=lambda m: m.message_id)

    async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None:
        entity = await self._entity(channel)
        msg = await self._call(self.client.get_messages(entity, ids=message_id))
        return self._message(channel.channel_id, msg) if msg is not None else None

    async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch:
        entity = await self._entity(channel)
        request = self.functions.updates.GetChannelDifferenceRequest(
            channel=entity,
            filter=self.types.ChannelMessagesFilterEmpty(),
            pts=pts,
            limit=limit,
            force=True,
        )
        diff = await self._call(self.client(request))
        if isinstance(diff, self.types.updates.ChannelDifferenceEmpty):
            return ChangeBatch(messages=[], pts=int(diff.pts), final=bool(diff.final))
        if isinstance(diff, self.types.updates.ChannelDifferenceTooLong):
            full = await self._call(self.client(self.functions.channels.GetFullChannelRequest(entity)))
            return ChangeBatch(messages=[], pts=int(full.full_chat.pts), final=True, too_long=True)
        # service messages (pinned, title changed...) are emitted too, marked in metadata (R30)
        messages = [
            m for m in diff.new_messages if isinstance(m, self.types.Message | self.types.MessageService)
        ]
        for update in diff.other_updates:
            if isinstance(update, self.types.UpdateEditChannelMessage) and isinstance(
                update.message, self.types.Message
            ):
                messages.append(update.message)
        return ChangeBatch(
            messages=[self._message(channel.channel_id, m) for m in messages],
            pts=int(diff.pts),
            final=bool(diff.final),
        )

    async def download_media(self, channel: ChannelInfo, media: TgMedia, *, max_bytes: int) -> bytes:
        if media.size_bytes is not None and media.size_bytes > max_bytes:
            raise ValueError(f"media {media.name}: {media.size_bytes} bytes > {max_bytes}")
        entity = await self._entity(channel)
        msg = await self._call(self.client.get_messages(entity, ids=int(media.ref)))
        if msg is None:
            raise ChannelUnavailable(f"message {media.ref} not found")
        data = await self._call(self.client.download_media(msg, file=bytes))
        if not isinstance(data, bytes):
            raise ClientUnavailable("media download returned no bytes")
        if len(data) > max_bytes:
            raise ValueError(f"media {media.name}: {len(data)} bytes > {max_bytes}")
        return data

    async def close(self) -> None:
        await self.client.disconnect()
