"""Stored RAW and the task's source (real orchestrator, real PostgreSQL, contract fakes as neighbours).

* reprocessing (``POST /v1/reprocessing``) feeds only RAW of the task's own source, although one storage
  connection keeps RAW of several sources and the same URL (the same ``material_id``) is stored by each;
* problem samples and unknown materials name the stored RAW of their observation (``stored_object_id``).
"""

from __future__ import annotations

from threading import Event
from typing import Any

import psycopg
import pytest
from orch_support import (
    SPECS,
    Neighbours,
    base_result,
    catalog_task,
    items_by_stage,
    product_extractor,
    source_doc,
    wait_until,
)

from jane_orchestrator.db import MIGRATIONS, Database

pytestmark = pytest.mark.integration

_N = 0


def post(client: Any, url: str, body: Any) -> Any:
    global _N
    _N += 1
    return client.post(url, json=body, headers={"Idempotency-Key": f"raw-{_N}"})


def run_to_end(client: Any, job: Any) -> dict[str, Any]:
    assert job.status_code == 202, job.text
    run_id = job.json()["job_id"]
    run: dict[str, Any] = wait_until(
        lambda: (
            (r := client.get(f"/v1/runs/{run_id}").json())["status"] in {"succeeded", "failed", "cancelled"}
            and r
        ),
        60,
    )
    return run


def two_sources_with_the_same_pages(client: Any) -> None:
    """``shop-example`` and ``shop-mirror`` collect the same site and store RAW into ``raw-files``."""
    for source_id, task_id in (("shop-example", "shop-catalog"), ("shop-mirror", "mirror-catalog")):
        assert post(client, "/v1/sources", source_doc(source_id)).status_code == 201
        assert post(client, "/v1/tasks", catalog_task(task_id, source_id)).status_code == 201
        run = run_to_end(client, post(client, f"/v1/tasks/{task_id}/runs", {}))
        assert run["status"] == "succeeded", run


def reprocess(client: Any, **stored: Any) -> dict[str, Any]:
    body = {
        "task_id": "shop-catalog",
        "stored_materials": {"storage_connection_id": "raw-files", **stored},
        "from_stage": "extract-products",
        "reason": "extractor fix",
    }
    run = run_to_end(client, post(client, "/v1/reprocessing", body))
    assert run["status"] == "succeeded" and run["trigger"] == "reprocess", run
    return run


def test_reprocessing_takes_only_raw_of_the_task_source(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    client = make_client()
    two_sources_with_the_same_pages(client)
    stored = [o["material"] for o in neighbours.storage.stored_objects.values()]
    assert len(stored) == 12
    own = next(
        m for m in stored if m["source"]["source_id"] == "shop-example" and "/product/" in m["locator"]["url"]
    )
    same_url = [m for m in stored if m["material_id"] == own["material_id"]]
    assert {m["source"]["source_id"] for m in same_url} == {"shop-example", "shop-mirror"}

    # "reprocess this one stored material" of shop-catalog: one item, not one per source (WP-12d repro)
    one = reprocess(client, material_ids=[own["material_id"]])
    items = items_by_stage(db_dsn, one["run_id"])["extract-products"]
    assert [(i["observation_id"], i["source_id"]) for i in items] == [(own["observation_id"], "shop-example")]

    # everything stored for the task: its own 6 RAW objects, not the 12 of both sources
    every = reprocess(client)
    items = items_by_stage(db_dsn, every["run_id"])["extract-products"]
    own_observations = {m["observation_id"] for m in stored if m["source"]["source_id"] == "shop-example"}
    assert len(items) == 6 and {i["observation_id"] for i in items} == own_observations
    assert neighbours.storage.violations == []


def unrecognized_first_product(neighbours: Neighbours) -> None:
    """The extractor does not recognise ``/product/a-0`` (a new layout); the other products are fine."""

    def extractor(body: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        material = next(i["material"] for i in body["inputs"] if i["kind"] == "material")
        if material["locator"]["url"].endswith("/product/a-0"):
            result = base_result(body, "unrecognized", "extractor")
            result["unrecognized"] = {"partial": False, "reason": "new layout", "signature": "new-layout"}
            return result
        return product_extractor(body, ctx)

    neighbours.runtime.behaviors["shop-example.product-extractor"] = extractor


def test_problem_samples_and_unknown_materials_name_the_stored_raw(
    make_client: Any, neighbours: Neighbours, db_dsn: str
) -> None:
    unrecognized_first_product(neighbours)
    client = make_client()
    assert post(client, "/v1/sources", source_doc()).status_code == 201
    assert post(client, "/v1/tasks", catalog_task()).status_code == 201

    def observations(run: dict[str, Any]) -> set[str]:
        return {i["observation_id"] for i in items_by_stage(db_dsn, run["run_id"])["extract-products"]}

    # a test run only simulates writes: its samples have no stored RAW to point to
    trial = run_to_end(client, post(client, "/v1/tasks/shop-catalog/runs", {"test_mode": True}))
    raw_started, release_raw = Event(), Event()
    write = neighbours.storage.write

    def delayed_write(body: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        material = next(i["material"] for i in body["inputs"] if i["kind"] == "material")
        if material["locator"]["url"].endswith("/product/a-0"):
            raw_started.set()
            assert release_raw.wait(60), "the test did not release the RAW write"
        return write(body, ctx)

    # Gate the RAW neighbour so the real extractor records the problem before RAW has an id.
    neighbours.storage.behaviors["jane.storage-files"] = delayed_write
    real_job = post(client, "/v1/tasks/shop-catalog/runs", {})
    try:
        assert real_job.status_code == 202 and raw_started.wait(30)
        early = wait_until(
            lambda: (
                (groups := client.get("/v1/problem-groups").json()["items"])
                and (samples := [s for g in groups for s in g["samples"]])
                and len(samples) == 2
                and samples
            ),
            30,
        )
        assert all("stored_object_id" not in s for s in early)
    finally:
        release_raw.set()
    real = run_to_end(client, real_job)
    assert trial["status"] == real["status"] == "succeeded"
    raw = {o["material"]["observation_id"]: oid for oid, o in neighbours.storage.stored_objects.items()}
    assert len(raw) == 6  # RAW of the real run only

    def samples() -> list[dict[str, Any]]:
        groups = client.get("/v1/problem-groups", params={"source_id": "shop-example"}).json()["items"]
        return [s for g in groups for s in g["samples"]]

    by_obs = {s["observation_id"]: s for s in samples()}
    (trial_sample,) = [by_obs[o] for o in observations(trial) if o in by_obs]
    assert "stored_object_id" not in trial_sample
    (real_sample,) = [by_obs[o] for o in observations(real) if o in by_obs]
    assert real_sample["stored_object_id"] == raw[real_sample["observation_id"]]
    # the RAW really is the material of the sample (what the assistant will fetch from storage)
    stored = neighbours.storage.stored_objects[real_sample["stored_object_id"]]["material"]
    assert (stored["material_id"], stored["observation_id"]) == (
        real_sample["material_id"],
        real_sample["observation_id"],
    )

    unknown = client.get("/v1/unknown-materials").json()["items"]
    real_unknown = [u for u in unknown if u["run_id"] == real["run_id"]]
    assert (
        len(real_unknown) == 1
        and real_unknown[0]["stored_object_id"] == raw[real_unknown[0]["observation_id"]]
    )
    assert all("stored_object_id" not in u for u in unknown if u["run_id"] == trial["run_id"])

    # A separate API instance reads the durable association, without the first instance's memory.
    fresh = make_client(run_workers=False)
    fresh_groups = fresh.get("/v1/problem-groups").json()["items"]
    fresh_samples = [s for g in fresh_groups for s in g["samples"]]
    assert {s["observation_id"]: s.get("stored_object_id") for s in fresh_samples} == {
        s["observation_id"]: s.get("stored_object_id") for s in samples()
    }

    # reprocessing the stored RAW: new samples (the gift card now reaches the extractor) name that RAW too
    reprocess(client)
    for sample in samples():
        if sample["observation_id"] in raw:
            assert sample["stored_object_id"] == raw[sample["observation_id"]], sample
        else:
            assert "stored_object_id" not in sample, sample
    stored_samples = [s for s in samples() if "stored_object_id" in s]
    # a-0 is a problem in both the live and the reprocessing runs; the gift card only in reprocessing.
    assert len(stored_samples) == 3 and len({s["observation_id"] for s in stored_samples}) == 2
    for path in ("/v1/problem-groups", "/v1/unknown-materials"):
        response = client.get(path)
        SPECS["orchestrator"].validate_response(
            "GET", path, response.status_code, response.json(), "application/json"
        )
    assert neighbours.storage.violations == [] and neighbours.runtime.violations == []


def test_stored_raw_migration_upgrades_an_existing_database(db_dsn: str) -> None:
    # Existing schema, including a real user record, rather than a fresh app creating all migrations.
    with psycopg.connect(db_dsn) as conn:
        conn.execute("CREATE TABLE schema_migrations (version integer PRIMARY KEY)")
        for version, sql in enumerate(MIGRATIONS[:-1], start=1):
            conn.execute(sql)
            conn.execute("INSERT INTO schema_migrations VALUES (%s)", (version,))
        conn.execute(
            "INSERT INTO unknown_materials (material_id, observation_id, source_id, run_id, forwarded_to_llm)"
            " VALUES ('old-material', 'old-observation', 'shop-example', 'old-run', false)"
        )
    db = Database(db_dsn)
    db.open()
    try:
        assert db.migrate() == len(MIGRATIONS)
        assert db.migrate() == len(MIGRATIONS)  # the second process/startup is harmless
        with db.conn() as conn:
            assert conn.execute("SELECT material_id FROM unknown_materials").fetchone() == {
                "material_id": "old-material"
            }
            assert conn.execute("SELECT stored_object_id FROM items").fetchall() == []
    finally:
        db.close()
