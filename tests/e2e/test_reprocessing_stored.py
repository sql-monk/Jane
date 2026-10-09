"""Reprocessing of stored RAW (TZ §10 "повторно обробляти збережені матеріали") after M3 - WP-17 backlog:

* S-M3-01 (R06): ``stored_materials.object_ids`` selects exactly the given stored RAW objects, in the given order,
  although the same materials have other stored observations (``material_ids`` would take them all); a missing
  object id fails the run with ``not_found``.
* S-M3-02 (R01): a Telegram message is stored as a JSON RAW document (the TZ §5 default for a RAW that is not a web
  page). storage.v1 ``GET /v1/objects/{id}`` restores the original message - text, media type, size and sha256 of
  the collector's material, not of the JSON document - and reprocessing that stored RAW into a stage that keeps the
  original bytes (``format.raw: original``) stores an object with the collector's sha256.

Real services: orchestrator, storage, web-collector, handler-runtime, registry (archives of the extractor),
telegram-collector, testsite and PostgreSQL. Substitute (**З**): the recorded Telegram backend of the collector.
Everything is read through the public contracts (orchestrator.v1, storage.v1, collector.v1).
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import (
    TESTSITE,
    create_source,
    create_task,
    list_items,
    m1_task,
    put_connections,
    start_run,
    wait_run,
)
from jane_e2e.stack import E2EStack
from jane_e2e.steps import store
from jane_e2e.verify import entities, history, objects_by_source, site_paths
from jane_telegram_collector.recorded import Recording  # type: ignore[import-untyped]

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M3")]

RAW = "raw-files"
STORAGE_FILES = {"package_id": "jane.storage-files", "version": "1.0.0"}


def reprocess(orch: JaneClient, task_id: str, stored: dict[str, Any], from_stage: str, reason: str) -> str:
    """``POST /v1/reprocessing`` of stored RAW of the connection ``raw-files``; returns the run id."""
    body = {
        "task_id": task_id,
        "stored_materials": {"storage_connection_id": RAW, **stored},
        "from_stage": from_stage,
        "reason": reason,
    }
    r = orch.api("orchestrator").post(
        "/v1/reprocessing", json=body, headers={"Idempotency-Key": uuid.uuid4().hex}
    )
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def stored_object(storage: JaneClient, object_id: str) -> dict[str, Any]:
    r = storage.api("storage").get(f"/v1/objects/{object_id}", params={"connection_id": RAW})
    assert r.status_code == 200, r.text
    return dict(r.json())


def stored_content(storage: JaneClient, object_id: str) -> bytes:
    r = storage.api("storage").get(f"/v1/objects/{object_id}/content", params={"connection_id": RAW})
    assert r.status_code == 200, r.text
    return bytes(r.content)


def stored_text(storage: JaneClient, object_id: str, media_type: str) -> bytes:
    """Read original RAW bytes through storage.v1 ``getObjectContent`` and check their exact media type."""
    r = storage.api("storage").get(f"/v1/objects/{object_id}/content", params={"connection_id": RAW})
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].split(";", 1)[0].strip() == media_type, r.headers
    return bytes(r.content)


def inline_bytes(content: dict[str, Any]) -> bytes:
    assert content["kind"] == "inline", content
    if content["encoding"] == "utf-8":
        return str(content["data"]).encode("utf-8")
    return base64.b64decode(content["data"])


# ---------------------------------------------------------------------------- S-M3-01 (R06)
@pytest.mark.criteria(6)
def test_s_m3_01_reprocessing_takes_exactly_the_given_stored_objects(
    orchestrated: JaneClient, client: Callable[..., JaneClient], extractor: dict[str, Any], run_id: str
) -> None:
    """Two runs of an M1 task store two RAW observations of each of two product pages. Reprocessing with
    ``object_ids`` = [the run-1 RAW of product B, the run-2 RAW of product A] extracts exactly these two stored
    observations in this order (not the other two RAW of the same materials), stores one more history event of
    each product from exactly that observation and writes no RAW. A missing object id fails the run."""
    orch, storage = orchestrated, client("storage")
    source_id = task_id = f"e2e-{run_id}-exact"
    paths = site_paths("product")[:2]
    create_source(orch, source_id)
    create_task(orch, m1_task(task_id, source_id, [TESTSITE + p for p in paths], extractor))
    runs = [start_run(orch, task_id, key=uuid.uuid4().hex)]
    assert wait_run(orch, runs[0])["status"] == "succeeded"
    runs.append(start_run(orch, task_id, key=uuid.uuid4().hex))
    assert wait_run(orch, runs[1])["status"] == "succeeded"

    # observation of every (run, material) and the RAW object that stores it
    observation = {
        (n, i["material_id"]): i["observation_id"]
        for n, run in enumerate(runs)
        for i in list_items(orch, run, "store-raw")
    }
    objects = objects_by_source(storage, RAW, source_id)
    object_of = {o["material"]["observation_id"]: o["object"]["object_id"] for o in objects}
    materials = sorted({material for _, material in observation})
    assert len(materials) == len(paths) and len(objects) == len(observation) == 2 * len(paths), objects
    a, b = materials
    chosen = [observation[(0, b)], observation[(1, a)]]  # one stored observation of each material, B first
    others = sorted(set(observation.values()) - set(chosen))

    rerun = reprocess(
        orch,
        task_id,
        {"object_ids": [object_of[obs] for obs in chosen]},
        "extract-products",
        "e2e: exact stored objects (R06)",
    )
    final = wait_run(orch, rerun)
    extracted = list_items(orch, rerun, "extract-products")
    stored = list_items(orch, rerun, "store-products")
    print(
        f"\nS-M3-01: runs={runs} reprocessing={rerun} chosen={chosen} others={others}"
        f"\nS-M3-01: extracted={[(i['observation_id'], i['status'], i.get('result_status')) for i in extracted]}"
    )
    assert final["status"] == "succeeded", final
    assert final["counters"]["materials"] == len(chosen), final
    # exactly the chosen observations, in the order of object_ids; nothing of the other stored RAW
    assert [i["observation_id"] for i in extracted] == chosen, extracted
    assert all(i["status"] == "completed" and i["result_status"] == "success" for i in extracted), extracted
    assert sorted(i["observation_id"] for i in stored) == sorted(chosen), stored
    assert all(i["status"] == "completed" and i["result_status"] == "success" for i in stored), stored
    # reprocessing starts at the extractor: no RAW is written again
    assert list_items(orch, rerun, "store-raw") == []
    assert len(objects_by_source(storage, RAW, source_id)) == len(objects)
    # each product got one history event from the reprocessing run, made from the chosen observation
    chosen_of = {observation[(0, b)]: b, observation[(1, a)]: a}
    products = entities(storage, "results-pg", source_id)
    assert len(products) == len(paths), products
    from_rerun = {}
    for product in products:
        events = history(storage, "results-pg", product["canonical_key"])
        assert len(events) == 3, (product["canonical_key"], events)  # two runs and the reprocessing
        mine = [e for e in events if (e["record"].get("provenance") or {}).get("run_id") == rerun]
        assert len(mine) == 1, (product["canonical_key"], events)
        from_rerun[product["canonical_key"]] = mine[0]["record"]["observation"]
    assert sorted(o["observation_id"] for o in from_rerun.values()) == sorted(chosen), from_rerun
    assert {o["observation_id"]: o["material_id"] for o in from_rerun.values()} == chosen_of, from_rerun

    # a stored object that does not exist: the run fails with not_found (no silent partial selection)
    missing = wait_run(
        orch,
        reprocess(
            orch,
            task_id,
            {"object_ids": [object_of[chosen[0]], f"obj_missing_{run_id}"]},
            "extract-products",
            "e2e: missing stored object (R06)",
        ),
    )
    assert missing["status"] == "failed", missing
    assert (missing.get("error") or {}).get("code") == "not_found", missing


# ---------------------------------------------------------------------------- S-M3-02 (R01)
def _collect_telegram(
    collector: JaneClient, body: dict[str, Any], timeout_s: float = 120
) -> list[dict[str, Any]]:
    """A Telegram collection (collector.v1) drained with cursor acknowledgement."""
    r = collector.api("collector").post(
        "/v1/collections", json=body, headers={"Idempotency-Key": uuid.uuid4().hex}
    )
    assert r.status_code == 202, r.text
    cid = r.json()["job_id"]
    out: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        params: dict[str, Any] = {"wait_ms": 2000, **({"after": after} if after else {})}
        page = collector.api("collector").get(f"/v1/collections/{cid}/materials", params=params)
        assert page.status_code == 200, page.text
        out.extend(page.json()["items"])
        after = page.json().get("next_cursor") or after
        if page.json()["end_of_stream"]:
            return out
    raise TimeoutError(f"Telegram collection {cid} did not finish in {timeout_s}s")


@pytest.mark.criteria(1, 12)
def test_s_m3_02_telegram_json_raw_is_restored_and_reprocessed_with_its_sha256(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """Telegram messages from the real collector (recorded backend) are stored by storage as JSON RAW documents.
    ``GET /v1/objects/{id}`` gives back each original message inline (text, ``text/plain``, size and sha256 of the
    collector's material), although the stored object is the JSON document with another sha256. Reprocessing those
    stored objects (``object_ids``) into a stage with ``format.raw: original`` stores the message bytes again - with
    the collector's sha256 - which the JSON document itself would not give."""
    require("telegram-collector", "storage", "orchestrator")
    collector, storage, orch = client("telegram-collector"), client("storage"), client("orchestrator")
    put_connections(orch)
    username = f"tg_raw_{run_id}"
    rec = Recording.create(
        stack.telegram_recordings_dir, channel_id="-1009876543210", username=username, title="RAW restore"
    )
    t0 = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    texts = ["Квитки на концерт: 250 грн", "Event 2: exhibition at 19:00"]  # non-ASCII: bytes != characters
    for n, text in enumerate(texts):
        rec.post(text, date=t0 + timedelta(minutes=n))
    source_id = task_id = f"e2e-tg-raw-{run_id}"
    messages = _collect_telegram(
        collector,
        {
            "source_kind": "telegram",
            "source_id": source_id,
            "state_key": source_id,
            "mode": "full",
            "rules": {"collector": "telegram", "channels": [{"username": username}]},
            "limits": {"rate": {"min_delay_ms_per_host": 0}},
        },
    )
    assert [m["content"]["data"] for m in messages] == texts, messages
    original = {m["observation_id"]: m for m in messages}

    # 1. the RAW goes to storage as a third-party application would send it (no format.raw: JSON document)
    for m in messages:
        _, result = store(
            storage,
            package_id=STORAGE_FILES["package_id"],
            connection=RAW,
            inputs=[{"kind": "material", "material": m}],
            run_id=run_id,
            stage_id="store-telegram-json",
            key_part=m["observation_id"],
        )
        assert result["status"] == "success", json.dumps(result)[:2000]
    documents = objects_by_source(storage, RAW, source_id)
    assert len(documents) == len(messages), documents
    for doc in documents:
        m = original[doc["material"]["observation_id"]]
        body = m["content"]["data"].encode("utf-8")
        assert doc["object"]["media_type"] == "application/json", doc
        # the stored object is the JSON document of the Material with the message embedded
        document = stored_content(storage, doc["object"]["object_id"])
        assert doc["object"]["sha256"] == hashlib.sha256(document).hexdigest() != m["content"]["sha256"], doc
        assert json.loads(document)["content"]["data"] == m["content"]["data"], document
        # storage.v1 restores the original message, not the document that wraps it (R01)
        restored = stored_object(storage, doc["object"]["object_id"])["material"]
        content = restored["content"]
        assert inline_bytes(content) == body, content
        assert content["media_type"] == "text/plain", content
        assert content["size_bytes"] == len(body) == m["content"]["size_bytes"], content
        assert content["sha256"] == hashlib.sha256(body).hexdigest() == m["content"]["sha256"], content
        assert content["sha256"] == m["revision"]["content_sha256"], (content, m["revision"])
        assert (restored["material_id"], restored["observation_id"]) == (
            m["material_id"],
            m["observation_id"],
        )

    # 2. reprocessing of exactly these stored objects into a stage that keeps the original bytes
    r = orch.api("orchestrator").post(
        "/v1/sources",
        json={
            "source_id": source_id,
            "kind": "telegram",
            "title": f"e2e Telegram RAW {run_id}",
            "locator": {"telegram_username": username},
        },
        headers={"Idempotency-Key": uuid.uuid4().hex},
    )
    assert r.status_code in (200, 201), r.text
    store_stage = {"kind": "handler", "handler": STORAGE_FILES, "connections": {"target": RAW}}
    create_task(
        orch,
        {
            "task_id": task_id,
            "title": f"e2e Telegram RAW {task_id}",
            "input": {"source_id": source_id},
            "stages": [
                {"stage_id": "collect", "kind": "collect", "collector": {"collector": "telegram"}},
                # how the task stores RAW itself: the TZ §5 default (JSON document), as in step 1
                {"stage_id": "store-raw", **store_stage, "inputs": [{"from": "collect"}]},
                {
                    "stage_id": "store-original",
                    **store_stage,
                    "params": {"format": {"raw": "original"}},
                    "inputs": [{"from": "collect"}],
                },
            ],
        },
    )
    chosen = sorted(documents, key=lambda d: d["material"]["observation_id"], reverse=True)
    rerun = reprocess(
        orch,
        task_id,
        {"object_ids": [d["object"]["object_id"] for d in chosen]},
        "store-original",
        "e2e: Telegram JSON RAW again as original bytes (R01)",
    )
    final = wait_run(orch, rerun)
    items = list_items(orch, rerun, "store-original")
    copies = [
        o
        for o in objects_by_source(storage, RAW, source_id)
        if o["object"]["object_id"] not in {d["object"]["object_id"] for d in documents}
    ]
    print(
        f"\nS-M3-02: documents={[(d['object']['object_id'], d['object']['sha256'][:12]) for d in documents]}"
        f"\nS-M3-02: reprocessing={rerun} {final['status']} items={[(i['observation_id'], i['status']) for i in items]}"
        f"\nS-M3-02: copies={[(o['object']['media_type'], o['object']['sha256'][:12], o['object']['size_bytes']) for o in copies]}"
        f"\nS-M3-02: collector sha256={sorted(m['content']['sha256'][:12] for m in messages)}"
    )
    assert final["status"] == "succeeded", final
    assert [i["observation_id"] for i in items] == [d["material"]["observation_id"] for d in chosen], items
    assert all(i["status"] == "completed" and i["result_status"] == "success" for i in items), items
    assert list_items(orch, rerun, "store-raw") == []  # reprocessing started at store-original
    assert len(copies) == len(messages), copies
    for copy in copies:
        m = original[copy["material"]["observation_id"]]
        body = m["content"]["data"].encode("utf-8")
        assert copy["object"]["media_type"] == "text/plain", copy
        assert copy["object"]["sha256"] == m["content"]["sha256"], (copy, m["content"])
        assert copy["object"]["size_bytes"] == len(body), copy
        assert stored_text(storage, copy["object"]["object_id"], "text/plain") == body
