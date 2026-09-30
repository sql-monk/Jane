"""Collection run: one :class:`TelegramRun` per collection (history, new messages, edits, cursors).

Per channel the run keeps a *progress* record (``channel_progress``, per collection) and the persistent
*cursor* (``tg_cursors``, per ``state_key``):

* ``mode=full`` (or no cursor yet): read the history (``history.since`` / ``from_message_id``) oldest first;
  every message is a new observation. The channel ``pts`` at the start is remembered, so the next
  incremental run also sees the edits made while the history was read.
* ``mode=incremental`` with a cursor: ``getChannelDifference`` from the cursor's ``pts`` gives new and edited
  messages. If Telegram answers "difference too long", new messages are read from the history after
  ``last_message_id`` and an error entry says that edits in the gap are unavailable.

An edit is emitted as a new observation of the same ``material_id`` with a larger ``revision.sequence``
(``edit_date``) and ``is_edit: true``. A repeated delivery of a revision already emitted for the ``state_key``
(same sequence and text; e.g. an update replayed after a restart) is not emitted again (``stats.duplicates``).

Every emitted message is committed in one lease-fenced transaction with the run progress, the cursor, the
seen revision and the stats, so a killed instance's successor continues exactly after the last emitted
message. Flood-waits up to ``telegram.max_flood_wait_seconds`` are waited out; longer ones stop the run with
``rate_limited`` (progress kept, the next collection continues from the cursor).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import random
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, TypeVar

from jane_kit.config import ResolvedLimits
from jane_kit.errors import JaneError
from jane_kit.jobs import JobCancelledError, JobContext

from .client import (
    AccountUnauthorized,
    ChannelInfo,
    ChannelUnavailable,
    ClientFactory,
    ClientUnavailable,
    FloodWait,
    ResolvedAccount,
    TelegramClient,
    TgMedia,
    TgMessage,
)
from .materials import (
    ContentTooLarge,
    Delivery,
    TransitStore,
    build_material,
    material_id,
    message_sequence,
    message_sha,
    new_observation_id,
    rfc3339,
)
from .settings import ServiceLimits
from .state import LeaseLost, StateStore

__all__ = ["LeaseLost", "RunDeps", "TelegramRun", "channel_key", "new_stats"]

log = logging.getLogger(__name__)

T = TypeVar("T")

STAT_KEYS = (
    "discovered",
    "fetched",
    "emitted",
    "acknowledged",
    "unacked",
    "duplicates",
    "skipped_out_of_scope",
    "skipped_robots",
    "not_modified",
    "errors",
    "frontier_size",
    "bytes_fetched",
)
HISTORY = "telegram_history"
UPDATES = "telegram_updates"


def new_stats() -> dict[str, Any]:
    return {**dict.fromkeys(STAT_KEYS, 0), "by_strategy": {}}


def channel_key(spec: Mapping[str, Any]) -> str:
    return str(spec["channel_id"]) if spec.get("channel_id") else "@" + str(spec["username"]).lower()


def _now() -> datetime:
    return datetime.now(UTC)


def _parse(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


class RateLimitedStop(Exception):
    def __init__(self, seconds: int, what: str) -> None:
        super().__init__(f"{what}: Telegram asks to wait {seconds}s")
        self.seconds = seconds
        self.what = what


class TransientFailure(Exception):
    def __init__(self, what: str, attempts: int, cause: BaseException) -> None:
        super().__init__(f"{what}: {type(cause).__name__}: {cause} after {attempts} attempt(s)")
        self.attempts = attempts


@dataclass
class RunDeps:
    """Service-level dependencies shared by all runs."""

    state: StateStore
    factory: ClientFactory
    resolve: Callable[..., ResolvedLimits[ServiceLimits]]
    transit: TransitStore | None
    instance_id: str
    lease_seconds: float
    heartbeat_seconds: float
    version: str
    ack_events: dict[str, asyncio.Event] = field(default_factory=dict)


class TelegramRun:
    def __init__(self, deps: RunDeps, record: Mapping[str, Any], account: ResolvedAccount) -> None:
        self.deps = deps
        self.state = deps.state
        self.account = account
        self.collection_id: str = record["collection_id"]
        self.state_key: str = record["state_key"]
        self.request: dict[str, Any] = record["request"]
        self.rules: dict[str, Any] = record["rules"]
        self.rules_ref: dict[str, Any] | None = record.get("rules_ref")
        self.source_id: str | None = self.request.get("source_id")
        self.mode: str = self.request.get("mode", "full")
        self.stats: dict[str, Any] = {**new_stats(), **(record.get("stats") or {})}
        self.resolved = deps.resolve(self.rules.get("limits"), self.request.get("limits"))
        self.limits: ServiceLimits = self.resolved.limits
        self.delivery = Delivery(
            mode=self.request.get("content_delivery", "auto"),
            inline_max_bytes=self.limits.transfer.inline_max_bytes,
            transit_ttl_seconds=self.limits.transfer.transit_ttl_seconds,
            store=deps.transit,
        )
        updates = self.rules.get("updates") or {}
        self.new_on = bool(updates.get("new_messages", True))
        self.edits_on = bool(updates.get("edits", True))
        media = self.rules.get("media") or {}
        self.media_on = bool(media.get("download", False))
        self.media_kinds = set(media.get("kinds") or ())
        self.fence = (self.collection_id, deps.instance_id)
        self.cancelled = False
        self.stop_reason: str | None = None
        self.flood_waits = 0
        self.channels: dict[str, Any] = {}
        self._job: JobContext | None = None
        self._stop_exc: BaseException | None = None
        self._last_call = 0.0
        self._cursors: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------ Telegram calls
    async def _pace(self) -> None:
        delay = self.limits.rate.min_delay_ms_per_host / 1000
        loop = asyncio.get_running_loop()
        wait = self._last_call + delay - loop.time()
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_call = loop.time()

    def _backoff(self, attempt: int) -> float:
        r = self.limits.retries
        ms = min(r.max_backoff_ms, r.initial_backoff_ms * r.backoff_multiplier ** (attempt - 1))
        if r.jitter:
            ms = random.uniform(0, ms)  # noqa: S311 - jitter, not cryptography
        return ms / 1000

    async def call(self, what: str, fn: Callable[[], Awaitable[T]]) -> T:
        """One Telegram API call: pacing, per-call timeout, retries of transient errors, flood-wait."""
        attempts = 0
        while True:
            await self._pace()
            try:
                async with asyncio.timeout(self.limits.timeouts.request_timeout_ms / 1000):
                    return await fn()
            except FloodWait as exc:
                self.flood_waits += 1
                if exc.seconds > self.limits.telegram.max_flood_wait_seconds:
                    raise RateLimitedStop(exc.seconds, what) from exc
                log.info(
                    "telegram flood wait", extra={"collection_id": self.collection_id, "seconds": exc.seconds}
                )
                await asyncio.sleep(exc.seconds)
            except (ClientUnavailable, TimeoutError) as exc:
                attempts += 1
                if attempts >= self.limits.retries.max_attempts:
                    raise TransientFailure(what, attempts, exc) from exc
                await asyncio.sleep(self._backoff(attempts))

    async def _open(self) -> TelegramClient:
        attempts = 0
        timeout = self.limits.timeouts.connect_timeout_ms / 1000
        while True:
            try:
                async with asyncio.timeout(timeout):
                    return await self.deps.factory.open(self.account, connect_timeout_s=timeout)
            except (ClientUnavailable, TimeoutError) as exc:
                attempts += 1
                if attempts >= self.limits.retries.max_attempts:
                    raise TransientFailure("connect", attempts, exc) from exc
                await asyncio.sleep(self._backoff(attempts))

    # ------------------------------------------------------------------ persistence helpers
    def _tx(self) -> Any:
        """Transaction fenced by this run's lease: a run that lost its lease cannot write anything."""
        return self.state.tx(self.fence)

    def _error(
        self, db: Any, code: str, message: str, *, where: str | None = None, attempts: int | None = None
    ) -> None:
        err: dict[str, Any] = {"code": code, "message": message, "at": rfc3339(_now())}
        if where:
            err["telegram_message"] = where
        if attempts:
            err["attempts"] = attempts
        self.state.add_error(db, self.collection_id, err)
        self.stats["errors"] += 1

    def _cursor(self, channel_id: str) -> dict[str, Any]:
        if channel_id not in self._cursors:
            self._cursors[channel_id] = dict(self.state.get_cursor(self.state_key, channel_id) or {})
        return self._cursors[channel_id]

    def _commit(self, db: Any, key: str, channel: ChannelInfo, progress: Mapping[str, Any]) -> None:
        self.state.put_progress(db, self.collection_id, key, progress)
        cursor = self._cursor(channel.channel_id)
        if channel.username:
            cursor["username"] = channel.username
        self.state.put_cursor(db, self.state_key, channel.channel_id, cursor, rfc3339(_now()))
        self.state.save_stats(db, self.collection_id, self.stats)

    def _budget(self) -> str | None:
        if self.stats["fetched"] >= self.limits.telegram.max_messages_per_run:
            return "telegram.max_messages_per_run"
        return None

    async def _wait_backpressure(self) -> None:
        limit = self.limits.queue.max_unacked_materials
        if self.state.unacked_count(self.collection_id) < limit:
            return
        # the flag belongs to the lease holder: a run that lost its lease must not touch the new owner's flag
        self.state.set_paused(self.collection_id, True, self.fence)
        event = self.deps.ack_events.setdefault(self.collection_id, asyncio.Event())
        try:
            while self.state.unacked_count(self.collection_id) >= limit and not self.cancelled:
                event.clear()
                with contextlib.suppress(TimeoutError):  # an ack may come through another instance
                    await asyncio.wait_for(
                        event.wait(), timeout=self.limits.collector.backpressure_poll_ms / 1000
                    )
        except BaseException:
            # interrupted (lease lost, cancelled, shutdown): clear the flag only while still the owner
            with contextlib.suppress(LeaseLost):
                self.state.set_paused(self.collection_id, False, self.fence)
            raise
        self.state.set_paused(self.collection_id, False, self.fence)  # LeaseLost here stops the run

    # ------------------------------------------------------------------ heartbeat
    async def _beat(self) -> None:
        """Renew the lease; detect cancellation requested through another instance; report progress."""
        if not self.state.claim(self.collection_id, self.deps.instance_id, self.deps.lease_seconds):
            raise LeaseLost(self.collection_id)
        job = self.state.get_job(self.collection_id)
        if job is not None and '"status":"cancelling"' in job.replace(" ", ""):
            self.cancelled = True
            raise JobCancelledError(self.collection_id)
        if self._job is not None:
            counters = {k: int(v) for k, v in self.stats.items() if isinstance(v, int)}
            counters["flood_waits"] = self.flood_waits
            await self._job.progress(int(self.stats["emitted"]), None, unit="messages", counters=counters)

    async def _heartbeat_loop(self, main: asyncio.Task[Any]) -> None:
        while True:
            await asyncio.sleep(self.deps.heartbeat_seconds)
            try:
                await self._beat()
            except (LeaseLost, JobCancelledError) as exc:
                self._stop_exc = exc
                main.cancel()
                return
            except Exception:
                log.exception("heartbeat failed", extra={"collection_id": self.collection_id})

    async def execute(self, job: JobContext | None = None) -> dict[str, Any]:
        self._job = job
        main = asyncio.current_task()
        if main is None:
            raise RuntimeError("execute() must run inside a task")
        await self._beat()
        heartbeat = asyncio.create_task(self._heartbeat_loop(main), name=f"heartbeat {self.collection_id}")
        try:
            return await self._execute()
        except asyncio.CancelledError:
            if self._stop_exc is not None:
                main.uncancel()
                raise self._stop_exc from None
            raise
        finally:
            heartbeat.cancel()
            await asyncio.gather(heartbeat, return_exceptions=True)

    # ------------------------------------------------------------------ the run
    def _result(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "collection_id": self.collection_id,
            "stats": self.stats,
            "channels": self.channels,
            "flood_waits": self.flood_waits,
        }
        if self.stop_reason:
            result["stopped_by"] = self.stop_reason
        return result

    def _fail(self, exc: JaneError, where: str | None, attempts: int | None = None) -> JaneError:
        """Record the error and mark the collection failed in one fenced transaction."""
        with self._tx() as db:
            self._error(db, exc.error_code, str(exc.detail), where=where, attempts=attempts)
            self.state.save_stats(db, self.collection_id, self.stats)
            result = {**self._result(), "error": exc.to_problem().model_dump(mode="json", exclude_none=True)}
            self.state.finish(db, self.collection_id, "failed", rfc3339(_now()), result)
        return exc

    async def _execute(self) -> dict[str, Any]:
        where: str | None = None
        # a previous owner killed while paused leaves the flag set; the new owner decides it anew
        self.state.set_paused(self.collection_id, False, self.fence)
        try:
            client = await self._open()
            try:
                for spec in self.rules["channels"]:
                    if self.stop_reason is not None:
                        break
                    where = channel_key(spec)
                    await self._channel(client, spec)
            finally:
                with contextlib.suppress(Exception):
                    await client.close()
        except RateLimitedStop as exc:
            raise self._fail(
                JaneError(
                    f"{exc}; more than telegram.max_flood_wait_seconds={self.limits.telegram.max_flood_wait_seconds}",
                    code="rate_limited",
                    retry_after_seconds=exc.seconds,
                    details={"retry_after_seconds": exc.seconds, "path": "telegram.max_flood_wait_seconds"},
                ),
                where,
            ) from exc
        except AccountUnauthorized as exc:
            raise self._fail(
                JaneError(
                    f"telegram account: {exc}",
                    code="source_unavailable",
                    retryable=False,
                    details={"reason": "account_unauthorized", "connection_id": self.account.connection_id},
                ),
                where,
            ) from exc
        except TransientFailure as exc:
            raise self._fail(
                JaneError(str(exc), code="source_unavailable", retryable=True), where, attempts=exc.attempts
            ) from exc
        result = self._result()
        with self._tx() as db:
            self.state.save_stats(db, self.collection_id, self.stats)
            self.state.finish(db, self.collection_id, "succeeded", rfc3339(_now()), result)
        return result

    def _plan(self, channel: ChannelInfo) -> dict[str, Any]:
        cursor = self._cursor(channel.channel_id)
        history = self.rules.get("history") or {}
        base: dict[str, Any] = {"channel_id": channel.channel_id, "pts_final": channel.pts}
        if self.mode == "full" or not cursor:
            dedup = self.mode == "incremental"
            if history.get("enabled", True):
                first = int(history.get("from_message_id") or 0)
                return {
                    **base,
                    "phase": "history",
                    "after_id": max(first - 1, 0),
                    "since": history.get("since"),
                    "strategy": HISTORY,
                    "dedup": dedup,
                    "known_max": 0,
                }
            # no history: start watching from the current top of the channel
            cursor["last_message_id"] = max(int(cursor.get("last_message_id", 0)), channel.top_message_id)
            return {**base, "phase": "finish", "known_max": channel.top_message_id}
        known = int(cursor.get("last_message_id", 0))
        if not self.new_on and not self.edits_on:
            return {
                **base,
                "phase": "finish",
                "pts_final": cursor.get("pts", channel.pts),
                "known_max": known,
            }
        if cursor.get("pts") is not None:
            return {**base, "phase": "changes", "pts": int(cursor["pts"]), "known_max": known, "dedup": True}
        if not self.new_on:  # edits wanted but no pts yet: nothing to diff against, start from now
            return {**base, "phase": "finish", "known_max": known}
        return {
            **base,
            "phase": "history",
            "after_id": known,
            "since": None,
            "strategy": UPDATES,
            "dedup": True,
            "known_max": known,
        }

    async def _channel(self, client: TelegramClient, spec: Mapping[str, Any]) -> None:
        key = channel_key(spec)
        progress = self.state.get_progress(self.collection_id, key)
        if progress is not None and progress.get("phase") == "done":
            self.channels[key] = progress.get("summary", {})
            return
        try:
            channel = await self.call(
                "resolve",
                lambda: client.resolve(username=spec.get("username"), channel_id=spec.get("channel_id")),
            )
        except ChannelUnavailable as exc:
            with self._tx() as db:
                self._error(db, "not_found", str(exc), where=key)
                done = {"phase": "done", "summary": {"error": "not_found"}}
                self.state.put_progress(db, self.collection_id, key, done)
                self.state.save_stats(db, self.collection_id, self.stats)
            self.channels[key] = done["summary"]
            return
        if progress is None:
            progress = self._plan(channel)
            with self._tx() as db:
                self._commit(db, key, channel, progress)
        emitted_before = int(self.stats["emitted"])
        while progress["phase"] != "finish":
            if progress["phase"] == "history":
                await self._history(client, key, channel, progress)
            elif progress["phase"] == "changes":
                await self._changes(client, key, channel, progress)
            else:
                raise RuntimeError(f"unknown phase {progress['phase']}")
            if self.stop_reason is not None:
                return
        cursor = self._cursor(channel.channel_id)
        cursor["pts"] = int(progress["pts_final"])
        summary = {
            "channel_id": channel.channel_id,
            "emitted": int(self.stats["emitted"]) - emitted_before,
            "last_message_id": int(cursor.get("last_message_id", 0)),
            "pts": cursor["pts"],
        }
        progress = {"phase": "done", "summary": summary}
        with self._tx() as db:
            self._commit(db, key, channel, progress)
        self.channels[key] = summary

    async def _history(
        self, client: TelegramClient, key: str, channel: ChannelInfo, progress: dict[str, Any]
    ) -> None:
        since = _parse(progress.get("since"))
        page = self.limits.collector.history_page_size
        while True:
            if (reason := self._budget()) is not None:
                self.stop_reason = reason
                return
            after = int(progress["after_id"])
            batch = await self.call(
                "history",
                lambda: client.history(channel, after_id=after, limit=min(page, self._left()), since=since),  # noqa: B023
            )
            if not batch:
                break
            for msg in batch:
                await self._emit(
                    client, key, channel, msg, progress, progress["strategy"], bool(progress["dedup"])
                )
                progress["after_id"] = max(int(progress["after_id"]), msg.message_id)
                if (reason := self._budget()) is not None:
                    with self._tx() as db:
                        self._commit(db, key, channel, progress)
                    self.stop_reason = reason
                    return
        progress["phase"] = "finish"
        with self._tx() as db:
            self._commit(db, key, channel, progress)

    def _left(self) -> int:
        return max(1, self.limits.telegram.max_messages_per_run - int(self.stats["fetched"]))

    async def _changes(
        self, client: TelegramClient, key: str, channel: ChannelInfo, progress: dict[str, Any]
    ) -> None:
        page = self.limits.collector.changes_page_size
        while True:
            if (reason := self._budget()) is not None:
                self.stop_reason = reason
                return
            pts = int(progress["pts"])
            batch = await self.call(
                "changes",
                lambda: client.changes(channel, pts=pts, limit=min(page, self._left())),  # noqa: B023
            )
            if batch.too_long:
                progress.update(
                    phase="history" if self.new_on else "finish",
                    after_id=int(progress["known_max"]),
                    since=None,
                    strategy=UPDATES,
                    dedup=True,
                    pts_final=batch.pts,
                )
                with self._tx() as db:
                    self._error(
                        db,
                        "source_unavailable",
                        "channel difference too long: edits made in the gap are not available; "
                        "new messages are read from the history",
                        where=key,
                    )
                    self._commit(db, key, channel, progress)
                return
            for msg in batch.messages:
                is_new = msg.message_id > int(progress["known_max"])
                if (is_new and not self.new_on) or (not is_new and not self.edits_on):
                    progress["known_max"] = max(int(progress["known_max"]), msg.message_id)
                    continue
                await self._emit(client, key, channel, msg, progress, UPDATES, True)
                progress["known_max"] = max(int(progress["known_max"]), msg.message_id)
            progress["pts"] = batch.pts
            progress["pts_final"] = batch.pts
            self._cursor(channel.channel_id)["pts"] = batch.pts
            with self._tx() as db:
                self._commit(db, key, channel, progress)
            if batch.final:
                break
        progress["phase"] = "finish"
        with self._tx() as db:
            self._commit(db, key, channel, progress)

    async def _media(
        self, client: TelegramClient, channel: ChannelInfo, msg: TgMessage, observation_id: str
    ) -> tuple[list[tuple[TgMedia, dict[str, Any]]], list[dict[str, Any]]]:
        attachments: list[tuple[TgMedia, dict[str, Any]]] = []
        diagnostics: list[dict[str, Any]] = []
        if not self.media_on:
            return attachments, diagnostics
        cap = self.limits.telegram.max_media_bytes
        for i, media in enumerate(msg.media):
            if self.media_kinds and media.kind not in self.media_kinds:
                continue
            if media.size_bytes is not None and media.size_bytes > cap:
                diagnostics.append(
                    {
                        "level": "warning",
                        "code": "media_too_large",
                        "message": f"{media.name}: {media.size_bytes} bytes > telegram.max_media_bytes={cap}",
                    }
                )
                continue
            try:
                data = await self.call(
                    "download_media",
                    lambda: client.download_media(channel, media, max_bytes=cap),  # noqa: B023
                )
                ref = self.delivery.content_ref(
                    data, media.media_type, f"{observation_id}-{i}", _now(), text=False
                )
            except (ValueError, ContentTooLarge) as exc:
                diagnostics.append({"level": "warning", "code": "media_skipped", "message": str(exc)})
                continue
            self.stats["bytes_fetched"] += len(data)
            attachments.append((media, ref))
        return attachments, diagnostics

    async def _emit(
        self,
        client: TelegramClient,
        key: str,
        channel: ChannelInfo,
        msg: TgMessage,
        progress: dict[str, Any],
        strategy: str,
        dedup: bool,
    ) -> None:
        self.stats["discovered"] += 1
        self.stats["fetched"] += 1
        self.stats["bytes_fetched"] += len(msg.text.encode("utf-8"))
        mid = material_id(channel.channel_id, msg.message_id)
        sequence = message_sequence(msg)
        sha = message_sha(msg)
        cursor = self._cursor(channel.channel_id)
        if dedup:
            seen = self.state.seen(self.state_key, mid)
            if seen is not None and (seen[0] > sequence or (seen[0] == sequence and seen[1] == sha)):
                self.stats["duplicates"] += 1
                return
        await self._wait_backpressure()
        observation_id = new_observation_id()
        attachments, diagnostics = await self._media(client, channel, msg, observation_id)
        try:
            material = build_material(
                msg,
                channel,
                observation_id=observation_id,
                delivery=self.delivery,
                collector_version=self.deps.version,
                source_id=self.source_id,
                strategy=strategy,
                rules_ref=self.rules_ref,
                collection_id=self.collection_id,
                attachments=attachments,
                diagnostics=diagnostics,
            )
        except ContentTooLarge as exc:
            with self._tx() as db:
                self._error(db, "limit_exceeded", str(exc), where=f"{key}/{msg.message_id}")
                self._commit(db, key, channel, progress)
            return
        cursor["last_message_id"] = max(int(cursor.get("last_message_id", 0)), msg.message_id)
        if msg.edit_date is not None:
            edited = rfc3339(msg.edit_date)
            cursor["last_edit_date"] = max(str(cursor.get("last_edit_date", "")), edited)
        progress["after_id"] = max(int(progress.get("after_id", 0)), msg.message_id)
        self.stats["emitted"] += 1
        by = self.stats["by_strategy"]
        by[strategy] = by.get(strategy, 0) + 1
        with self._tx() as db:
            self.state.append_material(db, self.collection_id, observation_id, material)
            self.state.put_seen(db, self.state_key, mid, sequence, sha)
            self._commit(db, key, channel, progress)
