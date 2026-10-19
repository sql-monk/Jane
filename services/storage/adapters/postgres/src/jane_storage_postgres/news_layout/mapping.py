"""Pure mapping of an entity snapshot to the rows of the ``news`` layout (no database).

Rules (``docs/delivery/news-pg.md``, section 3):

* a field missing from the snapshot (also a cleared one) gives ``NULL``;
* an unknown field — at the top level or inside a known object — and a value that does not fit the column
  type (a number in a text column, an unparsable time, …) go to ``extra`` under the field path
  (``published_at``, ``event.canonical.foo``, ``tags[2]``, ``entities[0].evidence[1].foo``); the column is
  then ``NULL``. JSON ``null`` is ``NULL`` without an ``extra`` entry. Values are never dropped;
* lists keep the original index as ``position``: an item that gives no row (wrong type, ``null``) goes to
  ``extra`` and leaves a gap instead of shifting the following items.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from jane_contracts.storage_adapter import EntitySnapshot
from jane_storage.codec import parse_ts

__all__ = [
    "PROJECTED_TYPES",
    "EntityRows",
    "EvidenceRow",
    "MentionRow",
    "SourceRow",
    "map_snapshot",
    "parse_date",
    "parse_time",
    "parse_timestamp",
]

PROJECTED_TYPES: frozenset[str] = frozenset({"article", "post", "news_article", "news_event"})

_INT64 = 2**63
_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.(?P<frac>\d+))?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$")


def parse_timestamp(value: str) -> datetime | None:
    """Strict RFC 3339 date-time with an offset → aware ``datetime`` (UTC); ``None`` when it does not fit.

    More than six fractional digits fit only when the extra digits are zeros (``timestamptz`` keeps
    microseconds).
    """
    m = _TIMESTAMP.match(value)
    if m is None:
        return None
    frac = m.group("frac")
    if frac and len(frac) > 6 and frac[6:].strip("0"):
        return None
    try:
        return parse_ts(value)
    except ValueError:
        return None


def parse_date(value: str) -> date | None:
    if not _DATE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_time(value: str) -> time | None:
    """``HH:MM`` or ``HH:MM:SS``."""
    return time.fromisoformat(value) if _TIME.match(value) else None


@dataclass(frozen=True)
class SourceRow:
    """Upsert of ``source``: ``None`` never overwrites a stored value; ``seen_at`` widens first/last seen."""

    source_id: str
    kind: str | None
    name: str | None
    site: str | None
    channel: str | None
    seen_at: datetime


@dataclass(frozen=True)
class MentionRow:
    position: int
    canonical_name: str | None
    entity_kind: str | None
    name: str | None
    role: str | None
    attitude: str | None
    attitude_confidence: float | None
    factual_impact: str | None


@dataclass(frozen=True)
class EvidenceRow:
    subject: str
    """``event``, ``event_time``, ``sentiment`` or ``mention``."""
    position: int
    quote: str | None
    reason: str | None
    attribution: str | None
    mention_position: int | None = None
    """Position of the mention in ``entities`` (``subject == "mention"``)."""


@dataclass(frozen=True)
class EntityRows:
    """Everything one snapshot gives to the projection."""

    entity_type: str
    table: str
    id_column: str
    columns: dict[str, Any]
    """Parent row without the surrogate id: ``canonical_key``, data columns, ``version``, ``updated_at``,
    ``extra``."""
    source: SourceRow | None = None
    tags: list[tuple[int, str]] = field(default_factory=list)
    links: list[tuple[int, str]] = field(default_factory=list)
    topics: list[tuple[int, str]] = field(default_factory=list)
    locations: list[tuple[int, str]] = field(default_factory=list)
    event: dict[str, Any] | None = None
    """``news_article_event`` row without ``news_article_id``; ``None`` when the snapshot has no ``event``."""
    mentions: list[MentionRow] = field(default_factory=list)
    evidence: list[EvidenceRow] = field(default_factory=list)

    @property
    def extra(self) -> dict[str, Any]:
        extra: dict[str, Any] = self.columns["extra"]
        return extra


def _join(prefix: str, key: str) -> str:
    return f"{prefix}.{key}" if prefix else key


class _Reader:
    """Reads typed values out of JSON objects; whatever does not fit lands in ``extra``."""

    def __init__(self) -> None:
        self.extra: dict[str, Any] = {}

    def _typed(self, obj: Mapping[str, Any], key: str, path: str, convert: Callable[[Any], Any]) -> Any:
        if key not in obj or obj[key] is None:
            return None
        value = obj[key]
        converted = convert(value)
        if converted is None:
            self.extra[path] = value
        return converted

    def text(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> str | None:
        result: str | None = self._typed(
            obj, key, _join(prefix, key), lambda v: v if isinstance(v, str) else None
        )
        return result

    def bigint(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> int | None:
        def convert(v: Any) -> int | None:
            ok = isinstance(v, int) and not isinstance(v, bool) and -_INT64 <= v < _INT64
            return v if ok else None

        result: int | None = self._typed(obj, key, _join(prefix, key), convert)
        return result

    def double(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> float | None:
        def convert(v: Any) -> float | None:
            if isinstance(v, bool) or not isinstance(v, int | float):
                return None
            try:
                number = float(v)
            except OverflowError:
                return None
            return number if math.isfinite(number) else None

        result: float | None = self._typed(obj, key, _join(prefix, key), convert)
        return result

    def boolean(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> bool | None:
        result: bool | None = self._typed(
            obj, key, _join(prefix, key), lambda v: v if isinstance(v, bool) else None
        )
        return result

    def timestamp(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> datetime | None:
        result: datetime | None = self._typed(
            obj, key, _join(prefix, key), lambda v: parse_timestamp(v) if isinstance(v, str) else None
        )
        return result

    def day(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> date | None:
        result: date | None = self._typed(
            obj, key, _join(prefix, key), lambda v: parse_date(v) if isinstance(v, str) else None
        )
        return result

    def clock(self, obj: Mapping[str, Any], key: str, prefix: str = "") -> time | None:
        result: time | None = self._typed(
            obj, key, _join(prefix, key), lambda v: parse_time(v) if isinstance(v, str) else None
        )
        return result

    def obj(self, parent: Mapping[str, Any], key: str, prefix: str = "") -> Mapping[str, Any] | None:
        """A nested object; ``None`` (and the value in ``extra``) when it is not an object."""
        if key not in parent or parent[key] is None:
            return None
        value = parent[key]
        if isinstance(value, Mapping):
            return value
        self.extra[_join(prefix, key)] = value
        return None

    def items(self, parent: Mapping[str, Any], key: str, prefix: str = "") -> list[tuple[int, Any, str]]:
        """``(index, item, path)`` of a list; a non-list value goes to ``extra`` whole."""
        if key not in parent or parent[key] is None:
            return []
        value = parent[key]
        path = _join(prefix, key)
        if not isinstance(value, list):
            self.extra[path] = value
            return []
        return [(i, item, f"{path}[{i}]") for i, item in enumerate(value)]

    def strings(self, parent: Mapping[str, Any], key: str, prefix: str = "") -> list[tuple[int, str]]:
        """``(position, text)`` of a list of strings; other items go to ``extra`` as ``key[i]``."""
        out: list[tuple[int, str]] = []
        for i, item, path in self.items(parent, key, prefix):
            if isinstance(item, str):
                out.append((i, item))
            else:
                self.extra[path] = item
        return out

    def unknown(self, obj: Mapping[str, Any], known: frozenset[str], prefix: str = "") -> None:
        for key, value in obj.items():
            if key not in known:
                self.extra[_join(prefix, key)] = value


def _canonical(r: _Reader, parent: Mapping[str, Any], prefix: str) -> dict[str, Any]:
    """``canonical`` object of an event (``news_event`` and ``news_article.event``)."""
    path = _join(prefix, "canonical")
    canonical = r.obj(parent, "canonical", prefix) or {}
    r.unknown(canonical, _CANONICAL_KEYS, path)
    return {
        "event_date": r.day(canonical, "date", path),
        "event_time": r.clock(canonical, "time", path),
        "primary_actor": r.text(canonical, "primary_actor", path),
        "action": r.text(canonical, "action", path),
        "object": r.text(canonical, "object", path),
        "location": r.text(canonical, "location", path),
        "country": r.text(canonical, "country", path),
    }


_CANONICAL_KEYS = frozenset({"date", "time", "primary_actor", "action", "object", "location", "country"})
_EVIDENCE_KEYS = frozenset({"quote", "reason", "attribution"})


def _evidence_item(
    r: _Reader, item: Any, path: str, subject: str, position: int, mention_position: int | None = None
) -> EvidenceRow | None:
    if not isinstance(item, Mapping):
        r.extra[path] = item
        return None
    r.unknown(item, _EVIDENCE_KEYS, path)
    return EvidenceRow(
        subject=subject,
        position=position,
        quote=r.text(item, "quote", path),
        reason=r.text(item, "reason", path),
        attribution=r.text(item, "attribution", path),
        mention_position=mention_position,
    )


def _evidence_list(
    r: _Reader, parent: Mapping[str, Any], key: str, prefix: str, subject: str, mention: int | None = None
) -> list[EvidenceRow]:
    rows = (
        _evidence_item(r, item, path, subject, i, mention) for i, item, path in r.items(parent, key, prefix)
    )
    return [row for row in rows if row is not None]


def _base(snapshot: EntitySnapshot, r: _Reader) -> dict[str, Any]:
    return {
        "canonical_key": snapshot.canonical_key,
        "version": snapshot.version,
        "updated_at": snapshot.updated_at,
        "extra": r.extra,
    }


def _scope(snapshot: EntitySnapshot) -> str:
    return str(snapshot.key.get("scope", ""))


# ---------------------------------------------------------------------------------------------- article
_ARTICLE_KEYS = frozenset(
    {
        "site",
        "url",
        "title",
        "lead",
        "text",
        "author",
        "section",
        "language",
        "image",
        "published_at",
        "modified_at",
        "tags",
    }
)


def _article(snapshot: EntitySnapshot) -> EntityRows:
    f, r = snapshot.fields, _Reader()
    r.unknown(f, _ARTICLE_KEYS)
    site = r.text(f, "site")
    columns = {
        **_base(snapshot, r),
        "source_id": _scope(snapshot),
        "url": r.text(f, "url"),
        "site": site,
        "title": r.text(f, "title"),
        "lead": r.text(f, "lead"),
        "body": r.text(f, "text"),
        "author": r.text(f, "author"),
        "section": r.text(f, "section"),
        "language": r.text(f, "language"),
        "image": r.text(f, "image"),
        "published_at": r.timestamp(f, "published_at"),
        "modified_at": r.timestamp(f, "modified_at"),
    }
    return EntityRows(
        entity_type="article",
        table="article",
        id_column="article_id",
        columns=columns,
        source=SourceRow(_scope(snapshot), "web", None, site, None, snapshot.updated_at),
        tags=r.strings(f, "tags"),
    )


# ---------------------------------------------------------------------------------------------- post
_POST_KEYS = frozenset(
    {
        "channel",
        "message_id",
        "url",
        "published_at",
        "title",
        "text",
        "views",
        "forwarded_from",
        "links",
        "has_media",
        "edited",
    }
)


def _post(snapshot: EntitySnapshot) -> EntityRows:
    f, r = snapshot.fields, _Reader()
    r.unknown(f, _POST_KEYS)
    channel = r.text(f, "channel")
    columns = {
        **_base(snapshot, r),
        "source_id": _scope(snapshot),
        "channel": channel,
        "message_id": r.bigint(f, "message_id"),
        "url": r.text(f, "url"),
        "title": r.text(f, "title"),
        "body": r.text(f, "text"),
        "views": r.bigint(f, "views"),
        "forwarded_from": r.text(f, "forwarded_from"),
        "has_media": r.boolean(f, "has_media"),
        "edited": r.boolean(f, "edited"),
        "published_at": r.timestamp(f, "published_at"),
    }
    return EntityRows(
        entity_type="post",
        table="post",
        id_column="post_id",
        columns=columns,
        source=SourceRow(_scope(snapshot), "telegram", None, None, channel, snapshot.updated_at),
        links=r.strings(f, "links"),
    )


# ---------------------------------------------------------------------------------------------- news_event
_NEWS_EVENT_KEYS = frozenset(
    {"event_id", "summary", "canonical", "identity_confidence", "grouping_method", "identity_kind"}
)


def _news_event(snapshot: EntitySnapshot) -> EntityRows:
    f, r = snapshot.fields, _Reader()
    r.unknown(f, _NEWS_EVENT_KEYS)
    columns = {
        **_base(snapshot, r),
        "scope": _scope(snapshot),
        "event_id": r.text(f, "event_id"),
        "summary": r.text(f, "summary"),
        "identity_kind": r.text(f, "identity_kind"),
        "grouping_method": r.text(f, "grouping_method"),
        "identity_confidence": r.double(f, "identity_confidence"),
        **_canonical(r, f, ""),
    }
    return EntityRows(
        entity_type="news_event", table="news_event", id_column="news_event_id", columns=columns
    )


# ---------------------------------------------------------------------------------------------- news_article
_NEWS_ARTICLE_KEYS = frozenset(
    {
        "material_id",
        "headline",
        "headline_ukrainian",
        "summary",
        "source_language",
        "reporting_kind",
        "topics",
        "locations",
        "sentiment",
        "entities",
        "event",
        "source_id",
        "source_name",
        "source_kind",
        "url",
        "published_at",
        "fetched_at",
        "edited_at",
        "content_sha256",
        "analysis_language",
        "evidence_validation",
        "event_id",
        "event_grouping",
        "transport",
        "region",
    }
)
_SENTIMENT_KEYS = frozenset({"label", "confidence", "explanation", "evidence"})
_GROUPING_KEYS = frozenset({"status", "method", "reason"})
_MENTION_KEYS = frozenset(
    {
        "name",
        "canonical_name",
        "type",
        "role",
        "attitude",
        "attitude_confidence",
        "evidence",
        "factual_impact",
    }
)
_EVENT_KEYS = frozenset(
    {
        "summary",
        "canonical",
        "identity_confidence",
        "evidence",
        "identity_specificity",
        "identity_kind",
        "date_resolution",
        "time_evidence",
    }
)
_DATE_RESOLUTION_KEYS = frozenset({"method", "quote", "reference_published_at"})


def _news_article(snapshot: EntitySnapshot) -> EntityRows:
    f, r = snapshot.fields, _Reader()
    r.unknown(f, _NEWS_ARTICLE_KEYS)
    scope = _scope(snapshot)
    if "source_id" in f and f["source_id"] is not None and f["source_id"] != scope:
        r.extra["source_id"] = f["source_id"]  # the column is key.scope; a different value is kept aside
    evidence: list[EvidenceRow] = []

    sentiment = r.obj(f, "sentiment") or {}
    r.unknown(sentiment, _SENTIMENT_KEYS, "sentiment")
    evidence += _evidence_list(r, sentiment, "evidence", "sentiment", "sentiment")

    grouping = r.obj(f, "event_grouping") or {}
    r.unknown(grouping, _GROUPING_KEYS, "event_grouping")

    mentions: list[MentionRow] = []
    for i, item, path in r.items(f, "entities"):
        if not isinstance(item, Mapping):
            r.extra[path] = item
            continue
        r.unknown(item, _MENTION_KEYS, path)
        mentions.append(
            MentionRow(
                position=i,
                canonical_name=r.text(item, "canonical_name", path),
                entity_kind=r.text(item, "type", path),
                name=r.text(item, "name", path),
                role=r.text(item, "role", path),
                attitude=r.text(item, "attitude", path),
                attitude_confidence=r.double(item, "attitude_confidence", path),
                factual_impact=r.text(item, "factual_impact", path),
            )
        )
        evidence += _evidence_list(r, item, "evidence", path, "mention", i)

    event_row: dict[str, Any] | None = None
    event = r.obj(f, "event")
    if event is not None:
        r.unknown(event, _EVENT_KEYS, "event")
        resolution = r.obj(event, "date_resolution", "event") or {}
        r.unknown(resolution, _DATE_RESOLUTION_KEYS, "event.date_resolution")
        event_row = {
            "summary": r.text(event, "summary", "event"),
            "identity_confidence": r.double(event, "identity_confidence", "event"),
            "identity_specificity": r.text(event, "identity_specificity", "event"),
            "identity_kind": r.text(event, "identity_kind", "event"),
            **_canonical(r, event, "event"),
            "date_resolution_method": r.text(resolution, "method", "event.date_resolution"),
            "date_resolution_quote": r.text(resolution, "quote", "event.date_resolution"),
            "date_resolution_reference_published_at": r.timestamp(
                resolution, "reference_published_at", "event.date_resolution"
            ),
        }
        evidence += _evidence_list(r, event, "evidence", "event", "event")
        if event.get("time_evidence") is not None:
            row = _evidence_item(r, event["time_evidence"], "event.time_evidence", "event_time", 0)
            if row is not None:
                evidence.append(row)

    columns = {
        **_base(snapshot, r),
        "source_id": scope,
        "url": r.text(f, "url"),
        "material_id": r.text(f, "material_id"),
        "content_sha256": r.text(f, "content_sha256"),
        "headline": r.text(f, "headline"),
        "headline_ukrainian": r.text(f, "headline_ukrainian"),
        "summary": r.text(f, "summary"),
        "source_language": r.text(f, "source_language"),
        "analysis_language": r.text(f, "analysis_language"),
        "reporting_kind": r.text(f, "reporting_kind"),
        "region": r.text(f, "region"),
        "transport": r.text(f, "transport"),
        "published_at": r.timestamp(f, "published_at"),
        "fetched_at": r.timestamp(f, "fetched_at"),
        "edited_at": r.timestamp(f, "edited_at"),
        "evidence_validation": r.text(f, "evidence_validation"),
        "event_id": r.text(f, "event_id"),
        "grouping_status": r.text(grouping, "status", "event_grouping"),
        "grouping_method": r.text(grouping, "method", "event_grouping"),
        "grouping_reason": r.text(grouping, "reason", "event_grouping"),
        "sentiment_label": r.text(sentiment, "label", "sentiment"),
        "sentiment_confidence": r.double(sentiment, "confidence", "sentiment"),
        "sentiment_explanation": r.text(sentiment, "explanation", "sentiment"),
    }
    source = SourceRow(
        scope, r.text(f, "source_kind"), r.text(f, "source_name"), None, None, snapshot.updated_at
    )
    return EntityRows(
        entity_type="news_article",
        table="news_article",
        id_column="news_article_id",
        columns=columns,
        source=source,
        topics=r.strings(f, "topics"),
        locations=r.strings(f, "locations"),
        event=event_row,
        mentions=mentions,
        evidence=evidence,
    )


_MAPPERS: dict[str, Callable[[EntitySnapshot], EntityRows]] = {
    "article": _article,
    "post": _post,
    "news_article": _news_article,
    "news_event": _news_event,
}


def map_snapshot(snapshot: EntitySnapshot) -> EntityRows | None:
    """Rows of the projection for ``snapshot``; ``None`` for a type the layout does not project."""
    mapper = _MAPPERS.get(snapshot.entity_type)
    return None if mapper is None else mapper(snapshot)
