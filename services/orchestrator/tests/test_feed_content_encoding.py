"""Real PostgreSQL feed persistence of valid inline content containing a NUL byte."""

from __future__ import annotations

import asyncio
from typing import Any

import psycopg
import pytest
from orch_support import Neighbours, Page, catalog_task, items_by_stage, source_doc
from test_pipeline import post

from jane_kit.content import ContentReader

pytestmark = pytest.mark.integration


def test_nul_inline_content_survives_feed_cursor_and_worker_reload(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    pages = [
        Page("https://shop.example.test/product/nul", "<h1>Лосьйон\x00</h1>\\u0000", "products"),
        Page("https://shop.example.test/product/plain", "<h1>Мило</h1>\\u0000", "products"),
    ]
    neighbours.collector.site = pages
    api = make_client(run_workers=False)
    engine = api.app.state.engine
    assert post(api, "/v1/sources", source_doc()).status_code == 201
    assert post(api, "/v1/tasks", catalog_task()).status_code == 201
    response = post(api, "/v1/tasks/shop-catalog/runs", {})
    assert response.status_code == 202
    run_id = response.json()["job_id"]

    feed = engine.claim_feed("before-reload")
    assert feed is not None
    assert engine.process_feed(feed, "before-reload") == "fed:4"
    collection = next(iter(neighbours.collector.collections.values()))
    original = {m["observation_id"]: m for m in collection.materials}
    with psycopg.connect(db_dsn, row_factory=psycopg.rows.dict_row) as conn:
        row = conn.execute("SELECT feed_cursor, feed_done FROM runs WHERE run_id = %s", (run_id,)).fetchone()
        queued = conn.execute(
            "SELECT payload FROM items WHERE run_id = %s AND status = 'queued' ORDER BY seq", (run_id,)
        ).fetchall()
    assert row == {"feed_cursor": "c_0000000001", "feed_done": False}
    assert collection.acked == 0  # Acceptance is durable; the next pull acknowledges it.
    assert len(queued) == 4
    reader = ContentReader(timeout_ms=1000)
    for item in queued:
        material = item["payload"][0]["material"]
        before = original[material["observation_id"]]
        content = material["content"]
        assert {k: v for k, v in material.items() if k != "content"} == {
            k: v for k, v in before.items() if k != "content"
        }
        assert {k: v for k, v in content.items() if k not in {"encoding", "data"}} == {
            k: v for k, v in before["content"].items() if k not in {"encoding", "data"}
        }
        assert asyncio.run(reader.read(content, max_bytes=1000)) == before["content"]["data"].encode()
        if "\x00" in before["content"]["data"]:
            assert content["encoding"] == "base64"
        else:
            assert content == before["content"]  # A literal escape is ordinary text.
    assert original[collection.materials[0]["observation_id"]]["content"]["encoding"] == "utf-8"

    # Another app/worker reads only the durable state and performs the existing empty-EOF ACK.
    reloaded_api = make_client(run_workers=False)
    reloaded = reloaded_api.app.state.engine
    feed = reloaded.claim_feed("after-reload")
    assert feed is not None
    assert reloaded.process_feed(feed, "after-reload") == "fed:0"
    assert collection.acked == len(pages)
    assert collection.pulls == 2
    with psycopg.connect(db_dsn) as conn:
        assert conn.execute(
            "SELECT feed_cursor, feed_done FROM runs WHERE run_id = %s", (run_id,)
        ).fetchone() == ("c_0000000001", True)

    processed = 0
    while item := reloaded.claim_item("after-reload"):
        assert reloaded.process_item(item, "after-reload") == "success"
        processed += 1
    assert processed == 6
    run = reloaded_api.get(f"/v1/runs/{run_id}").json()
    assert run["status"] == "succeeded", run
    items = items_by_stage(db_dsn, run_id)
    assert {stage: len(rows) for stage, rows in items.items()} == {
        "collect": 2,
        "store-raw": 2,
        "extract-products": 2,
        "store-products": 2,
    }
    assert all(i["status"] == "completed" for rows in items.values() for i in rows)
    for fake in (neighbours.runtime, neighbours.storage):
        invocations = [
            b for method, path, b in fake.requests if method == "POST" and path == "/v1/invocations"
        ]
        for body in invocations:
            material = body["inputs"][0].get("material")
            if material:
                assert (
                    asyncio.run(reader.read(material["content"], max_bytes=1000))
                    == original[material["observation_id"]]["content"]["data"].encode()
                )
        assert set(fake.effects.values()) == {1}
        assert not fake.key_mismatch
    assert not neighbours.collector.cancelled
    assert neighbours.all_violations() == []
