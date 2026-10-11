"""``news.analysis`` output (LLM data) -> entities ``news_item``, ``news_event``, ``news_mention``.

The LLM stage receives entities (``article`` / ``post``) and returns data only, so this transform builds the
entity keys and observations itself: the key of an item is its URL (the post URL for Telegram), the key of an
event is the deterministic ``event_key`` of :mod:`normalize`, shared by all sources; the observation is the one
of the analysed entity, copied by the LLM into ``ref`` and checked here (an invalid copy falls back to a
deterministic observation derived from the URL and the publication time).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from jane_extractor_sdk import Context, ExtractResult, empty, success, unrecognized

from .normalize import (
    actor_slug,
    country_code,
    event_key,
    kyiv_date,
    norm_name,
    parse_timestamp,
    region_code,
    valid_id,
)

SENTIMENTS = ("positive", "neutral", "negative")
TOPICS = (
    "war",
    "politics",
    "international",
    "economy",
    "energy",
    "society",
    "crime",
    "incidents",
    "health",
    "education",
    "culture",
    "sports",
    "science_tech",
    "weather",
    "other",
)
MENTION_TYPES = ("person", "organization", "country", "location", "other")
ROLES = ("subject", "object", "mentioned")
SOURCE_KINDS = ("official", "expert", "media", "eyewitness", "document", "social_media", "anonymous", "other")
SIGNALS = (
    "emotional_language",
    "sensational_headline",
    "unverified_claims",
    "one_sided",
    "missing_source",
    "propaganda_narrative",
    "hate_speech",
)


def _text(value: Any, limit: int) -> str:
    return " ".join(str(value).split())[:limit] if isinstance(value, str | int | float) else ""


def _enum(value: Any, allowed: tuple[str, ...], default: str) -> str:
    return value if isinstance(value, str) and value in allowed else default


def _strings(values: Any, limit: int, size: int) -> list[str]:
    out: list[str] = []
    for v in values if isinstance(values, list) else []:
        t = _text(v, size)
        if t and t not in out:
            out.append(t)
    return out[:limit]


def _outputs(data: Any) -> list[Mapping[str, Any]]:
    """The LLM output of one input, or of several (``{"results": [...]}``)."""
    if isinstance(data, Mapping) and isinstance(data.get("results"), list):
        return [d for d in data["results"] if isinstance(d, Mapping)]
    return [data] if isinstance(data, Mapping) else []


def _tonality(raw: Any) -> dict[str, Any]:
    raw = raw if isinstance(raw, Mapping) else {}
    score = raw.get("score")
    score = max(-1.0, min(1.0, float(score))) if isinstance(score, int | float) else 0.0
    label = raw.get("label")
    if label not in SENTIMENTS:
        label = "negative" if score < -0.2 else "positive" if score > 0.2 else "neutral"
    return {"label": label, "score": round(score, 3)}


def _mentions(raw: Any, max_mentions: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in raw if isinstance(raw, list) else []:
        if not isinstance(m, Mapping):
            continue
        canonical = _text(m.get("canonical_name"), 200) or _text(m.get("name"), 200)
        if not canonical or norm_name(canonical) in seen:
            continue
        seen.add(norm_name(canonical))
        mtype = _enum(m.get("type"), MENTION_TYPES, "other")
        item = {
            "name": _text(m.get("name"), 200) or canonical,
            "canonical_name": canonical,
            "entity_key": actor_slug(canonical, mtype) or "unknown",
            "type": mtype,
            "role": _enum(m.get("role"), ROLES, "mentioned"),
            "sentiment": _enum(m.get("sentiment"), SENTIMENTS, "neutral"),
        }
        evidence = _text(m.get("evidence"), 300)
        if evidence:
            item["evidence"] = evidence
        out.append(item)
    return out[:max_mentions]


def _observation(ref: Mapping[str, Any], url: str, published: str | None) -> tuple[dict[str, Any], bool]:
    obs_id = valid_id(ref.get("observation_id"))
    observed = parse_timestamp(str(ref.get("observed_at") or ""))
    if obs_id and observed is not None:
        return {"observation_id": obs_id, "observed_at": str(ref["observed_at"])}, True
    digest = hashlib.sha256(f"{url}|{published or ''}".encode()).hexdigest()[:32]
    return {
        "observation_id": f"news-analysis.{digest}",
        "observed_at": published or "1970-01-01T00:00:00Z",
    }, False


def _event_fields(event: Mapping[str, Any], key: str) -> dict[str, Any]:
    day, _, anchor = key.split(":", 2)
    fields: dict[str, Any] = {
        "event_key": key,
        "type": str(event.get("type")),
        "date": day,
        "anchor": anchor,
        "title": _text(event.get("title"), 200),
        "description": _text(event.get("description"), 500),
    }
    country = country_code(_text(event.get("country"), 60))
    if country:
        fields["country"] = country.upper()
    region = _text(event.get("region"), 120)
    settlement = _text(event.get("settlement"), 120)
    matched = region_code(region, settlement)
    if matched and fields.get("country", "UA") == "UA":
        fields["region_code"], fields["region"] = matched
    elif region:
        fields["region"] = region
    if settlement:
        fields["settlement"] = settlement
    for name in ("actor", "counterpart"):
        value = _text(event.get(name), 200)
        if value:
            fields[name] = value
    parties = sorted(
        {c.upper() for c in (country_code(_text(p, 60)) for p in event.get("parties") or []) if c}
    )
    if parties:
        fields["parties"] = parties
    participants = _strings(event.get("participants"), 6, 200)
    if participants:
        fields["participants"] = participants
    return {k: v for k, v in fields.items() if v not in ("", [], None)}


def _item(raw: Mapping[str, Any], params: Mapping[str, Any], ctx: Context) -> list[dict[str, Any]]:
    ref = raw.get("ref") if isinstance(raw.get("ref"), Mapping) else {}
    assert isinstance(ref, Mapping)
    kind = "telegram" if ref.get("entity_type") == "post" else "web"
    channel = _text(ref.get("channel"), 100)
    message_id = ref.get("message_id")
    url = _text(ref.get("url"), 2000)
    if not url and kind == "telegram" and channel and isinstance(message_id, int):
        url = f"https://t.me/{channel}/{message_id}"
    if not url.startswith(("http://", "https://")):
        ctx.log.warning("item without a valid URL skipped", code="news.invalid_ref")
        return []
    published_dt = parse_timestamp(str(ref.get("published_at") or ""))
    published = str(ref["published_at"]) if published_dt is not None else None
    observation, copied = _observation(ref, url, published)
    if not copied:
        ctx.log.warning(
            "observation of the analysed entity not copied; derived from the URL", code="news.observation"
        )
    observed_dt = parse_timestamp(observation["observed_at"])
    moment = published_dt or observed_dt
    fallback_day = kyiv_date(moment) if moment is not None else "1970-01-01"

    title = _text(raw.get("title"), 300)
    item: dict[str, Any] = {
        "url": url,
        "source": _text(ref.get("source"), 200) or (channel if kind == "telegram" else ""),
        "source_kind": kind,
        "title": title or url,
        "summary": _text(raw.get("summary"), 1200),
        "language": _text(raw.get("language"), 8).lower(),
        "content_type": _enum(
            raw.get("content_type"),
            ("news", "opinion", "analysis", "interview", "advertisement", "announcement", "other"),
            "other",
        ),
        "topics": [t for t in _strings(raw.get("topics"), 3, 40) if t in TOPICS],
        "countries": sorted(
            {c.upper() for c in (country_code(_text(x, 60)) for x in raw.get("countries") or []) if c}
        )[:5],
        "places": _strings(raw.get("places"), 5, 120),
        "tonality": _tonality(raw.get("tonality")),
        "key_facts": _strings(raw.get("key_facts"), 5, 300),
        "fact_or_opinion": _enum(raw.get("fact_or_opinion"), ("fact", "opinion", "mixed"), "fact"),
        "importance": _enum(raw.get("importance"), ("low", "medium", "high"), "medium"),
    }
    if kind == "telegram" and channel:
        item["channel"] = channel
        if isinstance(message_id, int) and message_id >= 0:
            item["message_id"] = message_id
    if published:
        item["published_at"] = published
    mentions = _mentions(raw.get("mentions"), int(params.get("max_mentions", 12)))
    item["mentions"] = mentions
    quoted = []
    for q in raw.get("quoted_sources") or []:
        if isinstance(q, Mapping) and _text(q.get("name"), 200):
            quoted.append(
                {"name": _text(q.get("name"), 200), "kind": _enum(q.get("kind"), SOURCE_KINDS, "other")}
            )
    item["quoted_sources"] = quoted[:8]
    manipulation = raw.get("manipulation") if isinstance(raw.get("manipulation"), Mapping) else {}
    assert isinstance(manipulation, Mapping)
    item["manipulation"] = {
        "clickbait": bool(manipulation.get("clickbait")),
        "signals": [s for s in _strings(manipulation.get("signals"), 7, 40) if s in SIGNALS],
    }

    event = raw.get("event") if isinstance(raw.get("event"), Mapping) else {}
    assert isinstance(event, Mapping)
    kinds = {norm_name(m["canonical_name"]): m["type"] for m in mentions}
    key = event_key(event, fallback_day, kinds=kinds, max_lag_days=int(params.get("max_event_lag_days", 3)))
    out: list[dict[str, Any]] = []
    if key is not None:
        ev = _event_fields(event, key)
        item.update(
            event_key=key, event_type=ev["type"], event_date=ev["date"], event_title=ev.get("title") or title
        )
        ev.setdefault("title", title)
        ev.update(last_url=url, last_source=item["source"])
        out.append(_record("news_event", ev, {"event_key": key}, params["event_scope"], observation))
    item = {k: v for k, v in item.items() if v not in ("", None)}
    out.insert(0, _record("news_item", item, {"url": url}, params["item_scope"], observation))
    if params.get("emit_mentions", True):
        for m in mentions:
            row = {
                "url": url,
                "canonical_name": m["canonical_name"],
                "entity_key": m["entity_key"],
                "name": m["name"],
                "type": m["type"],
                "role": m["role"],
                "sentiment": m["sentiment"],
                "source": item["source"],
                "source_kind": kind,
            }
            for name in ("evidence",):
                if name in m:
                    row[name] = m[name]
            for name in ("published_at", "event_key"):
                if name in item:
                    row[name] = item[name]
            natural = {"url": url, "canonical_name": m["canonical_name"]}
            out.append(_record("news_mention", row, natural, params["item_scope"], observation))
    return out


def _record(
    entity_type: str,
    fields: dict[str, Any],
    natural: dict[str, Any],
    scope: str,
    observation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "entity_type": entity_type,
        "key": {"scope": scope, "natural": natural},
        "fields": fields,
        "observation": dict(observation),
    }


def transform(material: Any, params: dict[str, Any], ctx: Context) -> ExtractResult:
    """Entry point (``kind: transform``); ``material`` is the ``DataInput`` of the LLM stage."""
    data = material.get("data") if isinstance(material, Mapping) else None
    raw_items = [i for out in _outputs(data) for i in (out.get("items") or []) if isinstance(i, Mapping)]
    if not raw_items:
        return empty()
    entities: list[dict[str, Any]] = []
    for raw in raw_items:
        entities.extend(_item(raw, params, ctx))
    if not entities:
        return unrecognized("no analysed item has a valid URL", signature="news.invalid_ref")
    return success(entities)  # type: ignore[arg-type]
