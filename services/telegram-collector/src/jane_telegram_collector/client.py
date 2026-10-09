"""Telegram client abstraction: the collector talks to Telegram only through :class:`TelegramClient`.

Implementations: :mod:`.recorded` (JSON recordings: tests, demos, replays), :mod:`.telethon_client`
(MTProto via the optional ``telethon`` extra) or any ``<module>:<factory>`` (``JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND``).

Channel identifiers follow the Bot API convention (``-100<channel id>``), message ids are the channel's
monotonic message ids, ``pts`` is the channel's update sequence (``updates.getChannelDifference``).
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .settings import Settings

__all__ = [
    "AccountUnauthorized",
    "ChangeBatch",
    "ChannelInfo",
    "ChannelUnavailable",
    "ClientFactory",
    "ClientUnavailable",
    "FloodWait",
    "ResolvedAccount",
    "TelegramClient",
    "TelegramError",
    "TgMedia",
    "TgMessage",
    "load_factory",
]


class TelegramError(Exception):
    """Base class of client errors."""


class FloodWait(TelegramError):
    """Telegram asks to wait ``seconds`` before the next call (FLOOD_WAIT_X)."""

    def __init__(self, seconds: int) -> None:
        super().__init__(f"flood wait {seconds}s")
        self.seconds = seconds


class ClientUnavailable(TelegramError):
    """Transient failure (network, Telegram internal error): the call may be retried."""


class ChannelUnavailable(TelegramError):
    """The channel does not exist, is private or the account has no access (per-channel error)."""


class AccountUnauthorized(TelegramError):
    """The account session is missing, expired or rejected (the whole collection fails)."""


@dataclass(frozen=True)
class TgMedia:
    kind: str  # photo | document | video | audio
    name: str
    media_type: str
    size_bytes: int | None = None
    ref: str = ""
    """Opaque reference for :meth:`TelegramClient.download_media`."""


@dataclass(frozen=True)
class TgMessage:
    channel_id: str
    message_id: int
    date: datetime
    text: str = ""
    edit_date: datetime | None = None
    grouped_id: str | None = None
    views: int | None = None
    author: str | None = None
    media: Sequence[TgMedia] = field(default_factory=tuple)
    service_action: str | None = None
    """A service message of the channel (``MessageService``: channel created, message pinned, title or photo
    changed...): the action in snake case (``channel_create``, ``pin_message``); ``None`` for a post."""


@dataclass(frozen=True)
class ChannelInfo:
    channel_id: str
    username: str | None
    title: str | None
    top_message_id: int
    """Id of the newest message (0 for an empty channel)."""
    pts: int
    """Current update sequence of the channel."""


@dataclass(frozen=True)
class ChangeBatch:
    messages: Sequence[TgMessage]
    """New and edited messages after the requested ``pts`` (current state of each message)."""
    pts: int
    """``pts`` to continue from."""
    final: bool
    """No more changes after ``pts`` right now."""
    too_long: bool = False
    """The difference is too long (Telegram ``channelDifferenceTooLong``): edits in the gap are unavailable."""


@dataclass(frozen=True)
class ResolvedAccount:
    """A ``telegram_account`` connection with its secrets resolved in this service's environment."""

    connection_id: str | None
    params: Mapping[str, object]
    secrets: Mapping[str, str] = field(repr=False, default_factory=dict)


class TelegramClient(Protocol):
    async def resolve(self, *, username: str | None = None, channel_id: str | None = None) -> ChannelInfo:
        """Channel by ``username`` or ``channel_id``; :class:`ChannelUnavailable` if not accessible."""
        ...

    async def history(
        self, channel: ChannelInfo, *, after_id: int, limit: int, since: datetime | None = None
    ) -> list[TgMessage]:
        """Up to ``limit`` messages with ``message_id > after_id`` (and ``date >= since``), oldest first."""
        ...

    async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None: ...

    async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch: ...

    async def download_media(self, channel: ChannelInfo, media: TgMedia, *, max_bytes: int) -> bytes:
        """Media bytes; more than ``max_bytes`` raises :class:`ValueError`."""
        ...

    async def close(self) -> None: ...


class ClientFactory(Protocol):
    name: str

    async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient: ...

    def requires_account(self) -> bool:
        """True if a ``telegram_account`` connection is mandatory for this backend."""
        ...


def load_factory(settings: Settings) -> ClientFactory:
    backend = settings.client_backend
    if backend == "recorded":
        from .recorded import RecordedClientFactory

        return RecordedClientFactory(settings.recordings_dir)
    if backend == "telethon":
        from .telethon_client import TelethonClientFactory

        return TelethonClientFactory()
    module_name, _, attr = backend.partition(":")
    if not attr:
        raise ValueError(f"unknown client backend {backend!r}: use recorded, telethon or <module>:<factory>")
    factory = getattr(importlib.import_module(module_name), attr)
    made: ClientFactory = factory(settings) if callable(factory) else factory
    return made
