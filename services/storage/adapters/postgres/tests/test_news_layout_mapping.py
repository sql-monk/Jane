"""Mapping of snapshots to the rows of the ``news`` layout — no database (real snapshots from results-mongo)."""

from __future__ import annotations

import copy
import json
import socket
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any

import pytest

from jane_contracts.storage_adapter import AdapterError, EntitySnapshot, ResolvedConnection
from jane_storage.keys import canonical_key
from jane_storage_postgres import LAYOUTS, PostgresAdapter
from jane_storage_postgres.news_layout import (
    MIGRATIONS,
    PROJECTED_TYPES,
    EvidenceRow,
    MentionRow,
    SourceRow,
    map_snapshot,
    parse_timestamp,
)
from jane_storage_postgres.news_layout.ddl import PROJECTION_TABLES

SAMPLES: dict[str, Any] = json.loads(
    (Path(__file__).parent / "data" / "news_samples.json").read_text(encoding="utf-8")
)
UPDATED = datetime(2026, 10, 12, 10, 34, 4, 929509, tzinfo=UTC)


def snapshot(
    entity_type: str, *, fields: dict[str, Any] | None = None, cleared: frozenset[str] = frozenset()
) -> EntitySnapshot:
    sample = SAMPLES[entity_type]
    return EntitySnapshot(
        entity_type=entity_type,
        canonical_key=canonical_key(sample["key"]),
        key=copy.deepcopy(sample["key"]),
        fields=copy.deepcopy(sample["fields"]) if fields is None else fields,
        field_orders={},
        cleared_fields=cleared,
        version=3,
        updated_at=UPDATED,
    )


def with_fields(entity_type: str, **changes: Any) -> EntitySnapshot:
    fields = copy.deepcopy(SAMPLES[entity_type]["fields"])
    fields.update(changes)
    return snapshot(entity_type, fields=fields)


# ---------------------------------------------------------------------------------------------- types
def test_only_the_four_news_types_are_projected() -> None:
    assert frozenset({"article", "post", "news_article", "news_event"}) == PROJECTED_TYPES
    product = EntitySnapshot(
        entity_type="product",
        canonical_key="shop|{}",
        key={"scope": "shop", "natural": {"sku": "A"}},
        fields={"title": "Kettle"},
        field_orders={},
        cleared_fields=frozenset(),
        version=1,
        updated_at=UPDATED,
    )
    assert map_snapshot(product) is None


def test_article_sample() -> None:
    rows = map_snapshot(snapshot("article"))
    assert rows is not None
    fields = SAMPLES["article"]["fields"]
    assert (rows.table, rows.id_column) == ("article", "article_id")
    assert rows.columns == {
        "canonical_key": canonical_key(SAMPLES["article"]["key"]),
        "version": 3,
        "updated_at": UPDATED,
        "extra": {},
        "source_id": "news-suspilne",
        "url": fields["url"],
        "site": "suspilne.media",
        "title": fields["title"],
        "lead": fields["lead"],
        "body": fields["text"],
        "author": "Суспільне Культура",
        "section": "Культура",
        "language": "uk",
        "image": fields["image"],
        "published_at": datetime(2026, 10, 12, 10, 22, 42, tzinfo=UTC),
        "modified_at": datetime(2026, 10, 12, 10, 29, 55, tzinfo=UTC),
    }
    assert rows.tags == [(0, "Радіодиктант"), (1, "Українське Радіо")]
    assert rows.source == SourceRow("news-suspilne", "web", None, "suspilne.media", None, UPDATED)
    assert not (rows.links or rows.topics or rows.locations or rows.mentions or rows.evidence)
    assert rows.event is None


def test_article_from_other_packages_keeps_their_fields_in_extra() -> None:
    """``news.web-article`` / ``news.telegram-public-posts`` write ``article`` with more fields."""
    rows = map_snapshot(
        with_fields(
            "article",
            source_id="news-suspilne",
            source_name="Суспільне",
            source_kind="web",
            region="ukraine",
            transport="rss_article",
            channel="suspilne_news",
            message_id=17,
        )
    )
    assert rows is not None
    assert rows.extra == {
        "source_id": "news-suspilne",
        "source_name": "Суспільне",
        "source_kind": "web",
        "region": "ukraine",
        "transport": "rss_article",
        "channel": "suspilne_news",
        "message_id": 17,
    }
    assert rows.source is not None and rows.source.kind == "web"


def test_post_sample() -> None:
    rows = map_snapshot(snapshot("post"))
    assert rows is not None
    fields = SAMPLES["post"]["fields"]
    assert rows.columns["source_id"] == "tgweb-hromadske-ua"
    assert rows.columns["channel"] == "hromadske_ua"
    assert rows.columns["message_id"] == 89322
    assert rows.columns["views"] == 17100
    assert rows.columns["edited"] is True
    assert rows.columns["has_media"] is False
    assert rows.columns["forwarded_from"] is None
    assert rows.columns["body"] == fields["text"]
    assert rows.columns["published_at"] == datetime(2026, 10, 11, 20, 59, 28, tzinfo=UTC)
    assert rows.links == list(enumerate(fields["links"]))
    assert rows.source == SourceRow("tgweb-hromadske-ua", "telegram", None, None, "hromadske_ua", UPDATED)
    assert rows.extra == {}


def test_news_event_sample() -> None:
    rows = map_snapshot(snapshot("news_event"))
    assert rows is not None
    assert rows.source is None
    assert rows.columns == {
        "canonical_key": canonical_key(SAMPLES["news_event"]["key"]),
        "version": 3,
        "updated_at": UPDATED,
        "extra": {},
        "scope": "news-events",
        "event_id": "news-event-0bdb293049bcaf057eaa60a75c6141a8",
        "summary": SAMPLES["news_event"]["fields"]["summary"],
        "identity_kind": "incident",
        "grouping_method": "exact_canonical_identity",
        "identity_confidence": 0.8,
        "event_date": date(2026, 10, 12),
        "event_time": None,
        "primary_actor": None,
        "action": "crash",
        "object": "PAC MFI-17 Mushshak",
        "location": "Nawan Killi",
        "country": "Pakistan",
    }


def test_news_article_sample() -> None:
    rows = map_snapshot(snapshot("news_article"))
    assert rows is not None
    fields = SAMPLES["news_article"]["fields"]
    assert rows.extra == {}, "source_id equal to key.scope is the column, not extra"
    c = rows.columns
    assert c["source_id"] == "news-web-pravda"
    assert c["published_at"] == datetime(2026, 10, 12, 10, 25, tzinfo=UTC)  # +03:00 → UTC
    assert c["fetched_at"] == datetime(2026, 10, 12, 10, 32, 59, tzinfo=UTC)
    assert c["edited_at"] is None
    assert c["event_id"] is None
    assert (c["grouping_status"], c["grouping_method"], c["grouping_reason"]) == (
        "ungrouped",
        "exact_canonical_identity",
        "low_identity_confidence",
    )
    assert (c["sentiment_label"], c["sentiment_confidence"]) == ("neutral", 0.85)
    assert c["sentiment_explanation"] == fields["sentiment"]["explanation"]
    assert (c["region"], c["transport"], c["material_id"]) == (
        "ukraine",
        "rss_article",
        "web:188f95cf434a15a95549553fe846ca5f",
    )
    assert rows.source == SourceRow("news-web-pravda", "web", "Українська правда", None, None, UPDATED)
    assert rows.topics == list(enumerate(fields["topics"]))
    assert rows.locations == list(enumerate(fields["locations"]))
    assert rows.event == {
        "summary": fields["event"]["summary"],
        "identity_confidence": 0.35,
        "identity_specificity": "broad",
        "identity_kind": None,
        "event_date": None,
        "event_time": None,
        "primary_actor": None,
        "action": None,
        "object": None,
        "location": "Kyiv",
        "country": "Ukraine",
        "date_resolution_method": None,
        "date_resolution_quote": None,
        "date_resolution_reference_published_at": None,
    }
    assert rows.mentions == [
        MentionRow(0, "Vitali Klitschko", "person", "Віталій Кличко", "mentioned", "neutral", 0.9, "unknown"),
        MentionRow(1, "Kyiv", "place", "Київ", "object", "neutral", 0.9, "harmful"),
        MentionRow(2, "Russia", "country", "російських", "mentioned", "neutral", 0.8, "unknown"),
    ]
    assert [(e.subject, e.position, e.mention_position) for e in rows.evidence] == [
        ("sentiment", 0, None),
        ("mention", 0, 0),
        ("mention", 0, 1),
        ("mention", 0, 2),
        ("event", 0, None),
    ]
    assert rows.evidence[1] == EvidenceRow(
        "mention", 0, "мер Києва Віталій Кличко", fields["entities"][0]["evidence"][0]["reason"], "author", 0
    )


def test_news_article_incident_event_with_time_and_date_resolution() -> None:
    event = {
        "summary": "Удар по Харкову",
        "canonical": {"date": "2026-10-11", "time": "21:05", "primary_actor": "Russia", "action": "strike"},
        "identity_confidence": 0.9,
        "identity_specificity": "specific",
        "identity_kind": "incident",
        "evidence": [{"quote": "q1", "reason": "r1", "attribution": "author"}],
        "date_resolution": {
            "method": "publication_weekday",
            "quote": "у суботу",
            "reference_published_at": "2026-10-12T08:00:00+03:00",
        },
        "time_evidence": {"quote": "о 21:05", "reason": "час", "attribution": "quoted_source"},
    }
    rows = map_snapshot(with_fields("news_article", event=event, event_id="news-event-1"))
    assert rows is not None and rows.event is not None
    assert rows.columns["event_id"] == "news-event-1"
    assert rows.event["event_date"] == date(2026, 10, 11)
    assert rows.event["event_time"] == time(21, 5)
    assert rows.event["identity_kind"] == "incident"
    assert rows.event["date_resolution_method"] == "publication_weekday"
    assert rows.event["date_resolution_quote"] == "у суботу"
    assert rows.event["date_resolution_reference_published_at"] == datetime(2026, 10, 12, 5, tzinfo=UTC)
    assert [(e.subject, e.position, e.quote) for e in rows.evidence if e.subject.startswith("event")] == [
        ("event", 0, "q1"),
        ("event_time", 0, "о 21:05"),
    ]
    assert rows.extra == {}


# ---------------------------------------------------------------------------------------------- extra
def test_unknown_and_unfit_values_go_to_extra_and_the_column_is_null() -> None:
    fields = copy.deepcopy(SAMPLES["news_article"]["fields"])
    fields["published_at"] = "вчора ввечері"
    fields["fetched_at"] = "2026-10-12"  # a date is not a date-time
    fields["edited_at"] = "2026-10-12T10:00:00"  # no offset
    fields["headline"] = 42
    fields["brand_new"] = {"a": [1, 2]}
    fields["event"]["canonical"]["foo"] = "bar"
    fields["event"]["canonical"]["time"] = "25:00"
    fields["event"]["identity_confidence"] = "high"
    fields["event"]["new_flag"] = True
    fields["sentiment"]["confidence"] = True
    fields["entities"][1]["weight"] = 3
    fields["entities"][2]["evidence"][0]["page"] = 7
    fields["topics"] = ["війна", 5, None, "Київ"]
    fields["source_id"] = "other-source"
    rows = map_snapshot(snapshot("news_article", fields=fields))
    assert rows is not None
    assert rows.extra == {
        "published_at": "вчора ввечері",
        "fetched_at": "2026-10-12",
        "edited_at": "2026-10-12T10:00:00",
        "headline": 42,
        "brand_new": {"a": [1, 2]},
        "event.canonical.foo": "bar",
        "event.canonical.time": "25:00",
        "event.identity_confidence": "high",
        "event.new_flag": True,
        "sentiment.confidence": True,
        "entities[1].weight": 3,
        "entities[2].evidence[0].page": 7,
        "topics[1]": 5,
        "topics[2]": None,
        "source_id": "other-source",
    }
    c = rows.columns
    assert c["published_at"] is None and c["fetched_at"] is None and c["edited_at"] is None
    assert c["headline"] is None
    assert c["sentiment_confidence"] is None
    assert c["source_id"] == "news-web-pravda"
    assert rows.event is not None
    assert rows.event["event_time"] is None and rows.event["identity_confidence"] is None
    assert rows.topics == [(0, "війна"), (3, "Київ")], "positions keep the original index"


def test_wrong_shapes_go_to_extra_whole() -> None:
    rows = map_snapshot(
        with_fields("news_article", event="подія", sentiment=[1], entities={"x": 1}, locations="Київ")
    )
    assert rows is not None
    assert rows.extra == {"event": "подія", "sentiment": [1], "entities": {"x": 1}, "locations": "Київ"}
    assert rows.event is None
    assert rows.mentions == [] and rows.locations == []
    assert [e.subject for e in rows.evidence] == []
    post = map_snapshot(with_fields("post", views="17K", message_id=2**63, has_media="yes", links=[1, "u"]))
    assert post is not None
    assert post.extra == {"views": "17K", "message_id": 2**63, "has_media": "yes", "links[0]": 1}
    assert post.links == [(1, "u")]
    assert post.columns["views"] is None and post.columns["message_id"] is None


def test_mention_items_that_are_not_objects_and_missing_canonical_name() -> None:
    entities = [
        "Кличко",
        {
            "name": "Хтось",
            "role": "subject",
            "attitude": "neutral",
            "attitude_confidence": 1,
            "evidence": [None],
        },
    ]
    rows = map_snapshot(with_fields("news_article", entities=entities))
    assert rows is not None
    assert rows.mentions == [MentionRow(1, None, None, "Хтось", "subject", "neutral", 1.0, None)]
    assert rows.extra == {"entities[0]": "Кличко", "entities[1].evidence[0]": None}


def test_missing_and_cleared_fields_are_null_without_extra() -> None:
    fields = copy.deepcopy(SAMPLES["article"]["fields"])
    for name in ("lead", "tags", "modified_at", "author"):
        del fields[name]
    fields["image"] = None
    rows = map_snapshot(snapshot("article", fields=fields, cleared=frozenset({"lead"})))
    assert rows is not None
    assert rows.columns["lead"] is None and rows.columns["modified_at"] is None
    assert rows.columns["author"] is None and rows.columns["image"] is None
    assert rows.tags == []
    assert rows.extra == {}


def test_extra_of_news_event_canonical() -> None:
    fields = copy.deepcopy(SAMPLES["news_event"]["fields"])
    fields["canonical"]["foo"] = 1
    fields["canonical"]["date"] = "12.10.2026"
    fields["canonical"]["time"] = "07:30:15"
    rows = map_snapshot(snapshot("news_event", fields=fields))
    assert rows is not None
    assert rows.extra == {"canonical.foo": 1, "canonical.date": "12.10.2026"}
    assert rows.columns["event_date"] is None
    assert rows.columns["event_time"] == time(7, 30, 15)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026-10-12T10:22:42Z", datetime(2026, 10, 12, 10, 22, 42, tzinfo=UTC)),
        ("2026-10-12T13:25:00+03:00", datetime(2026, 10, 12, 10, 25, tzinfo=UTC)),
        ("2026-10-12t10:22:42.5z", datetime(2026, 10, 12, 10, 22, 42, 500000, tzinfo=UTC)),
        ("2026-10-12T10:22:42.123456000Z", datetime(2026, 10, 12, 10, 22, 42, 123456, tzinfo=UTC)),
        ("2026-10-12T10:22:42.1234567Z", None),  # sub-microsecond precision would be lost
        ("2026-10-12T10:22:42", None),
        ("2026-10-12 10:22:42Z", None),
        ("2026-10-12", None),
        ("2026-02-30T10:00:00Z", None),
        ("2026-10-12T10:00:60Z", None),
        ("Mon, 12 Oct 2026 10:22:42 GMT", None),
    ],
)
def test_parse_timestamp_is_strict_rfc3339(text: str, expected: datetime | None) -> None:
    assert parse_timestamp(text) == expected


# ---------------------------------------------------------------------------------------------- schema
def test_migrations_are_numbered_from_one_and_cover_every_table() -> None:
    versions = [v for v, _ in MIGRATIONS]
    assert versions == list(range(1, len(versions) + 1))
    ddl = "\n".join(sql for _, sql in MIGRATIONS).format(s='"news"')
    for table in PROJECTION_TABLES:
        assert f'CREATE TABLE "news".{table} (' in ddl
    assert "jane_" not in ddl, "projection tables carry no engine prefix"


async def test_unknown_layout_is_a_non_retryable_error() -> None:
    assert frozenset({"news"}) == LAYOUTS
    connection = ResolvedConnection(
        connection_id="x",
        kind="postgresql",
        params={"host": "127.0.0.1", "database": "x", "layout": "warehouse"},
        secrets={},
    )
    adapter = PostgresAdapter()
    with pytest.raises(AdapterError) as err:
        await adapter.open(connection, {})
    assert err.value.retryable is False
    assert "warehouse" in str(err.value)
    listed = ResolvedConnection(
        connection_id="x", kind="postgresql", params={**connection.params, "layout": ["news"]}, secrets={}
    )
    with pytest.raises(AdapterError) as err:
        await adapter.open(listed, {})
    assert err.value.retryable is False
    assert adapter.layout is None
    with pytest.raises(AdapterError) as err:
        await adapter.rebuild_layout()
    assert err.value.retryable is False


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.mark.parametrize(
    "stage",
    [
        {"table_prefix": "x_"},
        {"table_prefix": ""},
        {"schema": "public"},
        {"schema": "other", "table_prefix": "jane_"},
    ],
)
async def test_stage_may_not_move_the_tables_of_a_connection_with_layout(stage: dict[str, Any]) -> None:
    """``schema`` / ``table_prefix`` stage params would share the projection of the schema with other tables."""
    params = {"host": "127.0.0.1", "port": _free_port(), "database": "x", "schema": "news", "layout": "news"}
    connection = ResolvedConnection(
        connection_id="results-news", kind="postgresql", params=params, secrets={}
    )
    adapter = PostgresAdapter()
    with pytest.raises(AdapterError) as err:
        await adapter.open(connection, stage)
    assert err.value.retryable is False
    assert "results-news" in str(err.value) and "override" in str(err.value)
    assert adapter.layout is None


@pytest.mark.parametrize(
    ("params", "stage"),
    [
        ({"schema": "news"}, {"schema": "news", "table_prefix": "jane_"}),  # same values as the connection
        ({"schema": "news", "table_prefix": "n_"}, {"table_prefix": "n_"}),
        ({}, {"schema": "public"}),
        (
            {"schema": "news"},
            {"table_prefix": "x_", "layout": "news"},
        ),  # no layout on the connection: allowed
    ],
)
async def test_same_namespace_or_no_layout_passes_the_check(
    params: dict[str, Any], stage: dict[str, Any]
) -> None:
    layout = {} if "layout" in stage else {"layout": "news"}
    connection = ResolvedConnection(
        connection_id="c",
        kind="postgresql",
        params={"host": "127.0.0.1", "port": _free_port(), "database": "x", **params, **layout},
        secrets={},
    )
    adapter = PostgresAdapter()
    # nothing listens on the port: the namespace check passed and the connect failed
    with pytest.raises(AdapterError) as err:
        await adapter.open(connection, {**stage, "connect_timeout_ms": 2000})
    assert err.value.retryable is True
    assert adapter.layout == (None if "layout" in stage else "news")
