"""Events from messages of a Telegram channel - the "events from Telegram" example of WP-14.

A message announces an event with one line per event::

    Подія: <назва> | <YYYY-MM-DD> [HH:MM] | <місце>

Rule-based on purpose (deterministic, no LLM): the LLM path of the platform is ``jane.llm-event-extractor``
behind the LLM gateway. ``success`` - at least one event; ``empty`` - no announcement in the message;
``unrecognized`` - an announcement line that cannot be parsed. An edited message is a new observation of
the same material, so the stored event is updated, not duplicated (key: channel/message/line).
"""

from __future__ import annotations

import re
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, Material, empty, entity, success, unrecognized

LINE = re.compile(
    r"^\s*(?P<marker>[^:|]{1,40}):\s*(?P<title>[^|]+?)\s*\|\s*(?P<date>\d{4}-\d{2}-\d{2})"
    r"(?:\s+(?P<time>\d{2}:\d{2}))?\s*\|\s*(?P<place>.+?)\s*$"
)


def extract(material: Material, params: dict[str, Any], ctx: Context) -> ExtractResult:
    tg = (material.get("locator") or {}).get("telegram") or {}
    channel = str(tg.get("channel_username") or tg.get("channel_id") or "local")
    message_id = tg.get("message_id")
    markers = {m.casefold() for m in params["markers"]}
    events, broken = [], []
    for number, line in enumerate(ctx.text().splitlines(), start=1):
        head = line.split(":", 1)[0].strip().casefold()
        if head not in markers:
            continue
        match = LINE.match(line)
        if match is None:
            broken.append(number)
            continue
        fields = {
            "event_id": f"{channel}/{message_id}/{number}",
            "title": match["title"],
            "date": match["date"],
            "time": match["time"],
            "place": match["place"],
            "channel": channel,
            "message_id": message_id,
        }
        events.append(entity("event", fields, completeness="full"))
    if broken and not events:
        ctx.log.warning("announcement line not parsed", code="extract.bad_line", selector=f"line {broken[0]}")
        return unrecognized("event announcement without date or place", signature="bad-line:event")
    return success(events) if events else empty()
