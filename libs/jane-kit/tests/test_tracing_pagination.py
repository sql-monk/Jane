from __future__ import annotations

import pytest

from jane_kit.errors import ValidationFailed
from jane_kit.pagination import Page, PageLimits, clamp_limit, decode_cursor, encode_cursor
from jane_kit.tracing import child_traceparent, new_trace_id, parse_traceparent


def test_traceparent_roundtrip() -> None:
    trace = new_trace_id()
    header = child_traceparent(trace)
    assert parse_traceparent(header) == trace
    assert (
        parse_traceparent("00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
        == "4bf92f3577b34da6a3ce929d0e0e4736"
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "",
        "garbage",
        "00-" + "0" * 32 + "-00f067aa0ba902b7-01",
        "00-4bf92f3577b34da6a3ce929d0e0e4736-" + "0" * 16 + "-01",
    ],
)
def test_invalid_traceparent_ignored(bad: str | None) -> None:
    assert parse_traceparent(bad) is None


def test_limit_is_clamped_not_rejected() -> None:
    limits = PageLimits(default_page_size=50, max_page_size=100)
    assert clamp_limit(None, limits) == 50
    assert clamp_limit(1000, limits) == 100
    assert clamp_limit(0, limits) == 1


def test_cursor_roundtrip_and_invalid() -> None:
    cursor = encode_cursor({"after": "mat_01", "ts": 3})
    assert decode_cursor(cursor) == {"after": "mat_01", "ts": 3}
    with pytest.raises(ValidationFailed):
        decode_cursor("%%%not-base64")


def test_page_shape() -> None:
    assert Page[int](items=[1, 2]).model_dump() == {"items": [1, 2], "next_cursor": None}
