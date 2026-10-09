"""``jane_kit.content`` writing (R18, ADR-0004 producer part): inline refs, transit blobs, the producer's cleaner."""

from __future__ import annotations

import base64
import hashlib
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from jane_kit.content import ContentReader, ContentTooLarge, ContentWriter, FileTransitStore, inline_ref
from jane_kit.errors import JaneError

NOW = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)


def test_inline_ref_text_and_binary() -> None:
    text = inline_ref("ціна 1299".encode(), "text/plain", text=True, charset="utf-8")
    assert text["encoding"] == "utf-8" and text["data"] == "ціна 1299" and text["charset"] == "utf-8"
    assert (
        text["size_bytes"] == len("ціна 1299".encode())
        and text["sha256"] == hashlib.sha256("ціна 1299".encode()).hexdigest()
    )
    raw = b"\xff\xfe\x00"
    binary = inline_ref(raw, "text/plain", text=True)  # not UTF-8: base64 although text was asked
    assert (
        binary["encoding"] == "base64" and base64.b64decode(binary["data"]) == raw and "charset" not in binary
    )


async def test_writer_modes_and_round_trip_through_the_reader(tmp_path: Path) -> None:
    store = FileTransitStore(tmp_path / "transit", "web-collector")
    auto = ContentWriter("auto", inline_max_bytes=8, transit_ttl_seconds=3600, store=store)
    small = auto.ref(b"tiny", "text/html", "obs_1", NOW, text=True)
    assert small["kind"] == "inline"
    big_body = b"<html>" + b"x" * 100 + b"</html>"
    big = auto.ref(big_body, "text/html", "obs_2", NOW, text=True, charset="utf-8")
    assert big["kind"] == "blob" and big["store"] == "transit" and big["expires_at"] == "2026-10-09T13:00:00Z"
    assert big["uri"].startswith("file://") and big["charset"] == "utf-8"
    path = tmp_path / "transit" / "web-collector" / "2026" / "10" / "09" / "obs_2.html"
    assert path.read_bytes() == big_body
    reader = ContentReader(timeout_ms=1000, blob_roots=[tmp_path / "transit"])
    assert await reader.read(big, max_bytes=1000) == big_body  # the consumer's checks pass (size, sha256)
    assert ContentWriter("blob", 8, 60, store).ref(b"tiny", "text/plain", "obs_3", NOW)["kind"] == "blob"
    with pytest.raises(ContentTooLarge) as exc:
        ContentWriter("inline", 8, 60, store).ref(big_body, "text/html", "obs_4", NOW)
    assert exc.value.error_code == "limit_exceeded" and exc.value.details == {
        "path": "transfer.inline_max_bytes",
        "limit": 8,
    }
    with pytest.raises(ContentTooLarge, match="no blob store configured"):
        ContentWriter("auto", 8, 60, None).ref(big_body, "text/html", "obs_5", NOW)
    with pytest.raises(ContentTooLarge, match="content_delivery=blob"):
        ContentWriter("blob", 8, 60, None).ref(b"tiny", "text/html", "obs_6", NOW)


def test_names_are_checked_and_reuse_is_explicit(tmp_path: Path) -> None:
    store = FileTransitStore(tmp_path, "storage")
    for bad in ("../x", "a/b", "a\\b", "c:x", "", ".hidden"):
        with pytest.raises(ValueError, match="name"):
            store.put(bad, b"x", "text/plain", NOW)
    with pytest.raises(ValueError, match="producer"):
        FileTransitStore(tmp_path, "../other")
    first = store.put("obj-abc", b"one", "text/plain", NOW, reuse=True)
    old = time.time() - 1000
    os.utime(first, (old, old))
    again = store.put("obj-abc", b"one", "text/plain", NOW, reuse=True)
    assert again == first and first.stat().st_mtime > old + 500  # kept, its TTL restarts
    replaced = store.put("obj-abc", b"two", "text/plain", NOW)
    assert replaced.read_bytes() == b"two"
    assert not list(first.parent.glob(".*.tmp"))


def test_cleanup_removes_only_old_files_of_this_producer(tmp_path: Path) -> None:
    mine = FileTransitStore(tmp_path, "telegram-collector")
    other = FileTransitStore(tmp_path, "web-collector")
    old_file = mine.put("obs_old", b"a", "text/plain", NOW)
    new_file = mine.put("obs_new", b"b", "text/plain", NOW)
    foreign = other.put("obs_x", b"c", "text/plain", NOW)
    stale = time.time() - 7200
    os.utime(old_file, (stale, stale))
    os.utime(foreign, (stale, stale))
    assert mine.cleanup(3600) == 1
    assert not old_file.exists() and new_file.exists() and foreign.exists()
    assert FileTransitStore(tmp_path / "missing", "x").cleanup(1) == 0


async def test_reader_refuses_a_transit_blob_outside_its_roots(tmp_path: Path) -> None:
    ref = ContentWriter("blob", 8, 60, FileTransitStore(tmp_path / "t", "assistant")).ref(
        b"data", "text/plain", "n1", NOW
    )
    with pytest.raises(JaneError, match="outside the allowed roots"):
        await ContentReader(timeout_ms=1000, blob_roots=[tmp_path / "elsewhere"]).read(ref, max_bytes=100)
