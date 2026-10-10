"""Posts of public Telegram channels as ``post`` entities.

One entity per message with text: channel, message id, link ``https://t.me/<channel>/<id>``, publication time,
title (the first non-empty line, cut to ``title_max_chars``) and the full text. An edited message is a new
observation of the same material, so the stored post is updated, not duplicated (key: channel + message id).
A message without text (service action, media only) is ``empty``.
"""

from __future__ import annotations

from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    tg = (material.get("locator") or {}).get("telegram") or {}
    text = ctx.text().strip()
    if not text:
        return empty()
    username = tg.get("channel_username")
    channel = str(username or tg.get("channel_id") or "unknown")
    message_id = tg.get("message_id")
    if message_id is None:
        return empty()
    title = next((line.strip() for line in text.splitlines() if line.strip()), "")
    limit = int(params.get("title_max_chars") or 200)
    if len(title) > limit:
        title = title[: limit - 1].rstrip() + "…"
    fields: dict[str, Any] = {
        "channel": channel,
        "message_id": int(message_id),
        "title": title,
        "text": text,
    }
    if username:
        fields["url"] = f"https://t.me/{username}/{message_id}"
    if published := material.get("published_at"):
        fields["published_at"] = str(published)
    return success([entity("post", fields)])
