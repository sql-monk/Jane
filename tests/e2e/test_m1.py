"""M1 - first end-to-end slice (plan.md §6): Web -> RAW in files and, in parallel, extraction by a local
package -> results in PostgreSQL. Scenarios S-M1-* of docs/acceptance/scenarios.md.

All services are real (web-collector WP-02, handler-runtime WP-06, storage WP-07, orchestrator WP-09, registry
WP-05, testsite WP-01); no stand-ins. Without the orchestrator (S-M1-01/02/04) the extractor is a LOCAL package
of a third-party application (inline archive, runtime CLI); orchestrated scenarios (S-M1-03/05/06) take it from
the real registry by ``package_id@version`` with its digest (``conftest.extractor``).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import (
    RULES_REF,
    TESTSITE,
    create_source,
    create_task,
    list_items,
    m1_task,
    start_run,
    wait_run,
)
from jane_e2e.stack import E2EStack
from jane_e2e.steps import EXTRACTOR_DIR, collector_fetch, extract, store
from jane_e2e.verify import (
    assert_effects_once,
    entities,
    expected_set,
    history,
    objects_by_source,
    raw_bytes,
    site_paths,
)

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M1")]

PRODUCT_PATH = "/product/phone-alpha"
# Expected card of this product: the package's own test case (same page model as the test site).
EXPECTED_FIELDS = {
    "sku": "phone-alpha",
    "title": "Phone Alpha",
    "price": {"amount": 299.0, "currency": "UAH"},
    "availability": "in_stock",
}


# ---------------------------------------------------------------------------- chain without orchestrator
def _objects_of(storage: JaneClient, connection: str, material: dict[str, Any]) -> list[dict[str, Any]]:
    r = storage.api("storage").get(
        "/v1/objects", params={"connection_id": connection, "material_id": material["material_id"]}
    )
    assert r.status_code == 200, r.text
    return [i for i in r.json()["items"] if i["material"]["observation_id"] == material["observation_id"]]


def store_raw_in_files(
    stack: E2EStack, storage: JaneClient, material: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """Branch 1: RAW -> filesystem adapter (default format of a web page: HTML, TZ §5) + redelivery."""
    raw = raw_bytes(material)
    inputs = [{"kind": "material", "material": material}]
    kw: dict[str, Any] = {"run_id": run_id, "stage_id": "store-raw", "key_part": material["observation_id"]}
    body, result = store(
        storage, package_id="jane.storage-files", connection="raw-files", inputs=inputs, **kw
    )
    assert result["status"] == "success", result
    (ack,) = result["output"]["writes"]
    assert ack["status"] == "written", ack
    obj = ack["object"]
    assert obj["locator"]["path"].endswith(".html"), obj
    assert obj["sha256"] == hashlib.sha256(raw).hexdigest()

    # the file itself on the storage volume: byte-for-byte the collected page
    assert stack.exec("storage", "cat", f"/var/lib/jane/storage/{obj['locator']['path']}") == raw

    # storage.v1 read API: listed for the material, content retrievable
    (listed,) = _objects_of(storage, "raw-files", material)
    assert listed["object"]["object_id"] == obj["object_id"]
    content = storage.api("storage").get(
        f"/v1/objects/{obj['object_id']}/content", params={"connection_id": "raw-files"}
    )
    assert content.status_code == 200
    assert content.content == raw

    # technical redelivery of the same result: duplicate, no second record (TZ §11)
    _, again = storage.invoke(body)
    assert again["duplicate"] is True
    assert again["output"]["writes"][0]["status"] == "duplicate"
    assert len(_objects_of(storage, "raw-files", material)) == 1
    return dict(obj)


def extract_products(runtime: JaneClient, material: dict[str, Any], run_id: str) -> dict[str, Any]:
    """Branch 2: extraction by a local package (inline archive) in the sandbox runtime."""
    _, result = extract(runtime, material, run_id)
    assert result["status"] == "success", result
    (entity,) = result["output"]["entities"]
    assert entity["entity_type"] == "product"
    assert entity["key"] == {
        "scope": material["source"]["source_id"],
        "natural": {"sku": EXPECTED_FIELDS["sku"]},
    }
    for name, value in EXPECTED_FIELDS.items():
        assert entity["fields"][name] == value, (name, entity["fields"])
    assert entity["observation"]["observation_id"] == material["observation_id"]
    assert entity["provenance"]["package"]["digest"] == result["handler"]["digest"]
    return result


def store_entities(
    storage: JaneClient, package_id: str, connection: str, extracted: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """Results -> storage adapter, redelivery is a duplicate; returns the entity state from storage.v1."""
    inputs = [
        {
            "kind": "entities",
            "entities": extracted["output"]["entities"],
            "from_invocation_id": extracted["invocation_id"],
        }
    ]
    kw: dict[str, Any] = {
        "run_id": run_id,
        "stage_id": f"store-{connection}",
        "key_part": extracted["invocation_id"],
    }
    body, result = store(storage, package_id=package_id, connection=connection, inputs=inputs, **kw)
    assert result["status"] == "success", result
    assert result["output"]["writes"][0]["status"] == "written", result
    _, again = storage.invoke(body)
    assert again["duplicate"] is True
    assert again["output"]["writes"][0]["status"] == "duplicate"

    scope = extracted["output"]["entities"][0]["key"]["scope"]
    (state,) = entities(storage, connection, scope)
    assert state["version"] == 1, state  # redelivery did not create a new version
    for name, value in EXPECTED_FIELDS.items():
        assert state["fields"][name] == value
    assert len(history(storage, connection, state["canonical_key"])) == 1
    return dict(state)


def run_m1_chain(
    stack: E2EStack, storage: JaneClient, runtime: JaneClient, material: dict[str, Any], run_id: str
) -> dict[str, Any]:
    """The M1 chain for one material: store-raw (files) || extract (runtime) -> store-products (PostgreSQL)."""
    obj = store_raw_in_files(stack, storage, material, run_id)
    extracted = extract_products(runtime, material, run_id)
    state = store_entities(storage, "jane.storage-postgresql", "results-pg", extracted, run_id)
    return {"object": obj, "extracted": extracted, "state": state}


# ---------------------------------------------------------------------------- collector.v1 helpers
def _start_collection(collector: JaneClient, body: dict[str, Any], key: str) -> str:
    r = collector.api("collector").post("/v1/collections", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def _drain(collector: JaneClient, cid: str, timeout_s: float = 300) -> list[dict[str, Any]]:
    """Pull every material with acknowledgement by cursor (``after``) until ``end_of_stream``."""
    out: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        params: dict[str, Any] = {"wait_ms": 2000, **({"after": after} if after else {})}
        page = collector.api("collector").get(f"/v1/collections/{cid}/materials", params=params).json()
        out.extend(page["items"])
        after = page.get("next_cursor") or after
        if page["end_of_stream"]:
            return out
    raise TimeoutError(f"collection {cid} did not reach end_of_stream in {timeout_s}s")


def _collection(collector: JaneClient, cid: str, timeout_s: float = 120) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    while True:
        view: dict[str, Any] = collector.api("collector").get(f"/v1/collections/{cid}").json()
        if view["status"] in {"succeeded", "failed", "cancelled"} or time.monotonic() > deadline:
            return view
        time.sleep(0.5)


def _path(url: str) -> str:
    """Root-relative path with query parameters sorted (canonical URLs of the collector sort them)."""
    parts = urlsplit(url)
    query = "&".join(sorted(parts.query.split("&"))) if parts.query else ""
    return parts.path + (f"?{query}" if query else "")


# ---------------------------------------------------------------------------- scenarios
@pytest.mark.criteria(1, 2, 8, 12)
def test_s_m1_01_collector_fetch_to_files_and_extraction_to_postgres(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-01: a third-party app chains the autonomous services itself (no orchestrator): Web Collector
    fetchMaterial -> RAW HTML in files || local extractor (inline archive) -> PostgreSQL; redelivery = duplicate."""
    require("testsite", "web-collector", "storage", "handler-runtime")
    material = collector_fetch(client("web-collector"), TESTSITE + PRODUCT_PATH, f"e2e-{run_id}")
    assert material["locator"]["url"] == TESTSITE + PRODUCT_PATH
    assert material["format"]["media_type"] == "text/html"
    run_m1_chain(stack, client("storage"), client("handler-runtime"), material, run_id)


@pytest.mark.criteria(1, 2, 12)
def test_s_m1_02_collection_pull_with_ack_then_chain(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """S-M1-02: collector.v1 collection (explicit URLs, rules from the local rules package) pulled with cursor
    acknowledgement; an unacknowledged page is re-delivered with the same observation_id; every material then
    goes through the chain."""
    require("testsite", "web-collector", "storage", "handler-runtime")
    collector, storage, runtime = client("web-collector"), client("storage"), client("handler-runtime")
    urls = [f"{TESTSITE}/product/phone-alpha", f"{TESTSITE}/product/phone-beta", f"{TESTSITE}/about"]
    body = {"source_kind": "web", "source_id": f"e2e-{run_id}", "rules_ref": RULES_REF, "urls": urls}
    cid = _start_collection(collector, body, f"e2e-{run_id}-collect")

    # first page without acknowledgement, then the same again: same observations (redelivery, not new ones)
    first = (
        collector.api("collector").get(f"/v1/collections/{cid}/materials", params={"wait_ms": 5000}).json()
    )
    assert first["items"], first
    again = collector.api("collector").get(f"/v1/collections/{cid}/materials", params={"wait_ms": 100}).json()
    assert [m["observation_id"] for m in again["items"][: len(first["items"])]] == [
        m["observation_id"] for m in first["items"]
    ]

    materials = _drain(collector, cid)
    assert sorted(m["locator"]["url"] for m in materials) == sorted(urls)
    assert len({m["observation_id"] for m in materials}) == len(urls)
    assert _collection(collector, cid)["status"] == "succeeded"

    for m in materials:
        store_raw_in_files(stack, storage, m, run_id)
    products = [m for m in materials if "/product/" in m["locator"]["url"]]
    for m in products:
        _, result = extract(runtime, m, run_id)
        assert result["status"] == "success", result
    about = next(m for m in materials if m["locator"]["url"].endswith("/about"))
    _, not_a_product = extract(runtime, about, run_id)
    assert not_a_product["status"] in {"empty", "unrecognized"}, not_a_product


@pytest.mark.criteria(2, 8, 11, 12)
def test_s_m1_03_orchestrated_task_web_to_files_and_postgres(
    orchestrated: JaneClient, client: Callable[..., JaneClient], extractor: dict[str, Any], run_id: str
) -> None:
    """S-M1-03 (M1 milestone): task collect -> store-raw || extract-products (bound to /product/*) ->
    store-products, run by the orchestrator's workers on real services; trace and 'exactly once'."""
    orch, storage = orchestrated, client("storage")
    source_id, task_id = f"e2e-{run_id}", f"e2e-{run_id}-m1"
    products = site_paths("product")[:6]
    others = ["/catalog/phones/", "/pages/faq"]  # a category page and an 'unknown' page: RAW only
    urls = [TESTSITE + p for p in products + others]
    create_source(orch, source_id)
    create_task(orch, m1_task(task_id, source_id, urls, extractor))

    run = wait_run(orch, start_run(orch, task_id))
    assert run["status"] == "succeeded", run
    stages = {s["stage_id"]: s.get("counts", {}) for s in run["stages"]}
    assert stages["collect"].get("completed") == len(urls), stages
    assert stages["store-raw"].get("success") == len(urls), stages
    assert stages["extract-products"].get("success") == len(products), stages
    assert stages["store-products"].get("success") == len(products), stages
    assert run["counters"]["materials"] == len(urls)

    items = list_items(orch, run["run_id"])
    assert all(i["status"] == "completed" for i in items), [i for i in items if i["status"] != "completed"]
    extracted_urls = {i["material_id"] for i in items if i["stage_id"] == "extract-products"}
    assert len(extracted_urls) == len(products)

    effects = assert_effects_once(storage, source_id, materials=len(urls), products=len(products))
    assert {e["fields"]["sku"] for e in effects["entities"]} == {p.rsplit("/", 1)[1] for p in products}
    assert all(o["object"]["locator"]["path"].endswith(".html") for o in effects["objects"])

    # traceability: material -> stages -> invocation -> package version (with digest) -> outputs
    product_item = next(i for i in items if i["stage_id"] == "extract-products")
    trace = orch.api("orchestrator").get(f"/v1/materials/{product_item['material_id']}/trace").json()
    text = json.dumps(trace)
    for stage in ("store-raw", "extract-products", "store-products"):
        assert stage in text, (stage, trace)
    assert extractor["digest"] in text  # the digest the real registry gave the published version

    # stages carry no package_archive, so the runtime loaded the extractor from the registry of the stack
    info = client("handler-runtime").api("handler").get("/v1/info")
    assert info.status_code == 200, info.text
    assert info.json()["capabilities"]["package_sources"] == ["package_archive", "registry"], info.json()

    # pages that match no binding are registered as unknown and NOT forwarded to an LLM (flag off by default)
    unknown = (
        orch.api("orchestrator").get("/v1/unknown-materials", params={"source_id": source_id}).json()["items"]
    )
    assert len(unknown) == len(others), unknown
    assert not any(u["forwarded_to_llm"] for u in unknown)


@pytest.mark.criteria(1, 10)
def test_s_m1_04_collector_and_extractor_used_by_a_third_party_app(
    stack: E2EStack,
    require: Callable[..., None],
    client: Callable[..., JaneClient],
    run_id: str,
    tmp_path: Path,
) -> None:
    """S-M1-04: recursive crawl of the test site through collector.v1 only (inline rules, no orchestrator,
    no registry) = the expected `recursive` set; then the extractor through the runtime CLI on a collected
    page (no service at all, sandbox on the local Docker engine)."""
    require("testsite", "web-collector", "handler-runtime")
    collector = client("web-collector")
    rules = json.loads(
        (
            Path(__file__).parent / "config" / "rules" / "testsite.web-rules" / "1.0.0" / "rules.json"
        ).read_text(encoding="utf-8")
    )
    cid = _start_collection(
        collector, {"source_kind": "web", "source_id": f"e2e-{run_id}", "rules": rules}, f"e2e-{run_id}-crawl"
    )
    materials = _drain(collector, cid)
    view = _collection(collector, cid)
    assert view["status"] == "succeeded", view
    got = [_path(m["locator"]["canonical_url"]) for m in materials]
    assert len(got) == len(set(got)), "a page was emitted twice"
    expected = {_path(path) for path in expected_set("recursive")}
    assert set(got) == expected, set(got) ^ expected
    assert not set(got) & expected_set("robots_disallowed")
    assert all(urlsplit(m["locator"]["final_url"]).hostname == "testsite" for m in materials)

    page = next(m for m in materials if _path(m["locator"]["canonical_url"]) == PRODUCT_PATH)
    html = tmp_path / "page.html"
    html.write_bytes(raw_bytes(page))
    cli = [sys.executable, "-m", "jane_handler_runtime.cli", "run", str(EXTRACTOR_DIR), str(html)]
    cli += ["--media-type", "text/html", "--url", page["locator"]["url"], "--image", stack.sandbox_image]
    r = subprocess.run(cli, capture_output=True, text=True, encoding="utf-8", timeout=300, check=False)
    assert r.returncode == 0, r.stderr[-2000:]
    result = json.loads(r.stdout)
    assert result["status"] == "success"
    assert result["output"]["entities"][0]["fields"]["sku"] == EXPECTED_FIELDS["sku"]


@pytest.mark.criteria(3)
def test_s_m1_05_storage_swap_is_task_configuration_only(
    orchestrated: JaneClient, client: Callable[..., JaneClient], extractor: dict[str, Any], run_id: str
) -> None:
    """S-M1-05: two tasks identical except the storage stage (`handler.package_id` + `connections.target`):
    PostgreSQL vs files. Same collector, same extractor package and digest; the same entity state results."""
    orch, storage = orchestrated, client("storage")
    urls = [TESTSITE + p for p in site_paths("product")[:3]]
    states: dict[str, list[dict[str, Any]]] = {}
    for variant, (package, connection) in {
        "pg": ("jane.storage-postgresql", "results-pg"),
        "files": ("jane.storage-files", "raw-files"),
    }.items():
        source_id, task_id = f"e2e-{run_id}-{variant}", f"e2e-{run_id}-{variant}"
        create_source(orch, source_id)
        task = m1_task(
            task_id, source_id, urls, extractor, entities_package=package, entities_connection=connection
        )
        create_task(orch, task)
        run = wait_run(orch, start_run(orch, task_id))
        assert run["status"] == "succeeded", run
        states[variant] = sorted(entities(storage, connection, source_id), key=lambda e: e["fields"]["sku"])
        assert len(states[variant]) == len(urls)
        assert len(objects_by_source(storage, "raw-files", source_id)) >= len(urls)
    assert [e["fields"] for e in states["pg"]] == [e["fields"] for e in states["files"]]
    assert [e["key"]["natural"] for e in states["pg"]] == [e["key"]["natural"] for e in states["files"]]


@pytest.mark.criteria(8)
def test_s_m1_06_new_observation_is_a_new_record(
    orchestrated: JaneClient, client: Callable[..., JaneClient], extractor: dict[str, Any], run_id: str
) -> None:
    """TZ §11: fetching the same material again (a second run) is a NEW observation - a new RAW record and a new
    history event - unlike a technical redelivery."""
    orch, storage = orchestrated, client("storage")
    source_id, task_id = f"e2e-{run_id}", f"e2e-{run_id}-again"
    urls = [TESTSITE + p for p in site_paths("product")[:2]]
    create_source(orch, source_id)
    create_task(orch, m1_task(task_id, source_id, urls, extractor))
    for _ in range(2):
        run = wait_run(orch, start_run(orch, task_id, key=uuid.uuid4().hex))
        assert run["status"] == "succeeded", run
    assert_effects_once(
        storage, source_id, materials=len(urls), products=len(urls), observations_per_material=2
    )
