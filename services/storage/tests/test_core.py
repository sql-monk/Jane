"""Pure core: canonical keys, object keys, merge semantics, formats, retries."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from jane_contracts.storage_adapter import OrderKey
from jane_kit.clients import RetryPolicy
from jane_storage.codec import (
    format_ts,
    order_from_json,
    order_to_json,
    parse_ts,
    snapshot_from_json,
    snapshot_to_json,
)
from jane_storage.engine import backoff_ms
from jane_storage.formats import InvalidFormat, build_raw_object, extension_for
from jane_storage.keys import canonical_key, object_delivery_key, object_key, safe_segment
from jane_storage.merge import InvalidRecord, merge

NOW = datetime(2026, 9, 28, 6, 0, tzinfo=UTC)


def rec(
    fields: dict[str, Any], at: str, obs: str = "obs", seq: int | None = None, **extra: Any
) -> dict[str, Any]:
    observation: dict[str, Any] = {"observation_id": obs, "observed_at": at}
    if seq is not None:
        observation["sequence"] = seq
    return {
        "entity_type": "product",
        "key": {"scope": "shop", "natural": {"sku": "A-100"}},
        "fields": fields,
        "observation": observation,
        **extra,
    }


def test_canonical_key_matches_contract_example() -> None:
    assert (
        canonical_key({"scope": "shop-example", "natural": {"sku": "A-100"}})
        == 'shop-example|{"sku":"A-100"}'
    )
    assert canonical_key({"scope": "s", "natural": {"b": 1, "a": "ї"}}) == 's|{"a":"ї","b":1}'


def test_object_key_is_filesystem_safe() -> None:
    key = object_key(
        material_id="web:3704326c",
        observation_id="obs_1",
        source_id="shop-example",
        fetched_at=parse_ts("2026-09-27T23:30:00-03:00"),
        ext="html",
    )
    assert key == "shop-example/2026/09/28/web_3704326c/obs_1.html"
    assert safe_segment("con") == "_con"
    assert safe_segment('a<>:"|?*b') == "a_______b"
    assert object_delivery_key("dk", 0) == "dk"
    assert object_delivery_key("dk", 1) == "dk#raw1"


def test_merge_new_then_partial_then_clear_then_stale() -> None:
    first = merge(None, rec({"sku": "A-100", "price": 10.0, "title": "T"}, "2026-09-27T10:00:00Z"), now=NOW)
    assert first.status == "written"
    assert first.snapshot.version == 1
    partial = merge(first.snapshot, rec({"price": 9.0}, "2026-09-27T11:00:00Z", "o2"), now=NOW)
    assert dict(partial.snapshot.fields) == {"sku": "A-100", "price": 9.0, "title": "T"}
    assert partial.applied == ["price"]
    cleared = merge(partial.snapshot, rec({}, "2026-09-27T12:00:00Z", "o3", cleared=["title"]), now=NOW)
    assert "title" not in cleared.snapshot.fields
    assert cleared.snapshot.cleared_fields == frozenset({"title"})
    late = merge(cleared.snapshot, rec({"title": "old", "price": 1.0}, "2026-09-27T10:30:00Z", "o4"), now=NOW)
    assert late.status == "stale"
    assert late.stale == ["price", "title"]
    assert dict(late.snapshot.fields) == dict(cleared.snapshot.fields)
    assert late.snapshot.version == cleared.snapshot.version + 1


def test_merge_order_uses_sequence_then_observation_id() -> None:
    base = merge(None, rec({"text": "b"}, "2026-09-27T10:00:00Z", "obs_b", seq=5), now=NOW).snapshot
    assert merge(base, rec({"text": "a"}, "2026-09-27T10:00:00Z", "obs_a", seq=4), now=NOW).status == "stale"
    assert (
        merge(base, rec({"text": "c"}, "2026-09-27T10:00:00Z", "obs_c", seq=6), now=NOW).status == "written"
    )
    # no sequence ranks below any sequence at the same time; then observation_id decides
    assert merge(base, rec({"text": "z"}, "2026-09-27T10:00:00Z", "obs_z"), now=NOW).status == "stale"
    same = merge(base, rec({"text": "b2"}, "2026-09-27T10:00:00Z", "obs_c", seq=5), now=NOW)
    assert same.status == "written"
    # exactly the same order is not newer
    assert merge(base, rec({"text": "x"}, "2026-09-27T10:00:00Z", "obs_b", seq=5), now=NOW).status == "stale"


@pytest.mark.parametrize(
    ("record", "message"),
    [
        (rec({"price": None}, "2026-09-27T10:00:00Z"), "null"),
        (rec({"price": 1}, "2026-09-27T10:00:00Z", cleared=["price"]), "both"),
        ({**rec({}, "2026-09-27T10:00:00Z"), "key": {"scope": "", "natural": {}}}, "key"),
    ],
)
def test_merge_rejects_invalid_records(record: dict[str, Any], message: str) -> None:
    with pytest.raises(InvalidRecord, match=message):
        merge(None, record, now=NOW)


def test_codec_round_trip() -> None:
    snap = merge(
        None, rec({"a": {"b": [1, 2.5, True]}}, "2026-09-27T10:00:00.123456Z", seq=3), now=NOW
    ).snapshot
    assert snapshot_from_json(snapshot_to_json(snap)) == snap
    order = OrderKey(observed_at=NOW, observation_id="x", sequence=None)
    assert order_from_json(order_to_json(order)) == order
    assert format_ts(parse_ts("2026-09-27T10:00:05Z")) == "2026-09-27T10:00:05.000000Z"


def material(media_type: str, content: bytes) -> dict[str, Any]:
    return {
        "material_id": "web:1",
        "observation_id": "obs_1",
        "source": {"source_id": "shop", "kind": "web"},
        "fetched_at": "2026-09-27T10:00:05Z",
        "format": {"media_type": media_type},
        "content": {
            "kind": "inline",
            "media_type": media_type,
            "encoding": "utf-8",
            "data": content.decode(),
        },
    }


def test_raw_formats() -> None:
    html = build_raw_object(material("text/html; charset=utf-8", b"<html/>"), b"<html/>", "original")
    assert html.object_key.endswith(".html")
    assert html.media_type == "text/html"
    assert html.content == b"<html/>"
    assert "data" not in html.metadata["content"]
    as_json = build_raw_object(material("text/html", b"<html/>"), b"<html/>", "json")
    assert as_json.object_key.endswith(".json")
    assert as_json.media_type == "application/json"
    assert b'"data": "<html/>"' in as_json.content
    auto_html = build_raw_object(material("text/html", b"<html/>"), b"<html/>", "auto")
    assert (auto_html.object_key.endswith(".html"), auto_html.content) == (True, b"<html/>")
    auto_feed = build_raw_object(material("application/rss+xml", b"<rss/>"), b"<rss/>", "auto")
    assert (auto_feed.object_key.endswith(".json"), auto_feed.media_type) == (True, "application/json")
    feed = build_raw_object(material("application/rss+xml", b"<rss/>"), b"<rss/>", "original")
    assert feed.object_key.endswith(".xml")
    with pytest.raises(InvalidFormat):
        build_raw_object(material("application/json", b"{}"), b"{}", "html")
    assert extension_for("application/vnd.x+json") == "json"
    assert extension_for("application/octet-stream") == "bin"


def test_backoff_from_policy() -> None:
    policy = RetryPolicy(initial_backoff_ms=100, max_backoff_ms=250, backoff_multiplier=2.0, jitter=False)
    assert [backoff_ms(policy, n) for n in (1, 2, 3)] == [100, 200, 250]
    jittered = RetryPolicy(initial_backoff_ms=100, jitter=True)
    assert backoff_ms(jittered, 1, rnd=lambda: 0.5) == 50
