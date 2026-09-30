"""M2: the LLM as a stage of orchestrated chains (docs/acceptance/scenarios.md).

* S-M2-11 (criterion 2): a task DAG whose branches have ``when`` conditions on
  ``material.format.media_type`` and ``result.status``; an LLM handler stands on the problem results of
  the extractor, its output is validated by the package schema and stored.
* S-M2-05 (criterion 11): unknown pages of a task reach the LLM only after the flag
  «Передавати в LLM невідомі сторінки» has been switched on explicitly.

Real services: orchestrator (WP-09), web-collector (WP-02), handler-runtime (WP-06), storage (WP-07),
llm gateway and LLM handler (WP-10), testsite and PostgreSQL (WP-01).
Substitutes: the external LLM is the deterministic provider ``fake`` of WP-10 (**З**), its answers are
scripted in ``tests/e2e/config/llm-seed.yaml``; ``package-host`` (**Т**) serves the archives of the LOCAL
fixture packages ``tests/e2e/packages/*`` because orchestrated stages send no ``package_archive``.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import pytest

from jane_e2e.clients import CONTRACTS, JaneClient, spec
from jane_e2e.orchestration import TESTSITE, create_source, create_task, list_items, start_run, wait_run
from jane_e2e.stack import E2EStack
from jane_e2e.verify import entities, objects_by_source, site_paths
from jane_extractor_sdk.package import build_archive

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

PACKAGES = Path(__file__).resolve().parent / "packages"
MANIFEST_SCHEMA = (CONTRACTS.parent / "schemas" / "package-manifest.schema.json").as_uri() + "#"
HTML = {"field": "material.format.media_type", "op": "eq", "value": "text/html"}
JSON = {"field": "material.format.media_type", "op": "eq", "value": "application/json"}
SUCCESS = {"field": "result.status", "op": "eq", "value": "success"}
UNRECOGNIZED = {"field": "result.status", "op": "eq", "value": "unrecognized"}


# ---------------------------------------------------------------------------- helpers
def local_package(stack: E2EStack, name: str) -> dict[str, Any]:
    """Fixture package of ``tests/e2e/packages``: manifest checked against the contract, canonical archive
    published to the ``package-host`` stand-in (Т); returns the pinned ``PackageRef`` with its digest."""
    package_dir = PACKAGES / name
    manifest = json.loads((package_dir / "jane-package.json").read_text(encoding="utf-8"))
    spec("registry").validate_at(MANIFEST_SCHEMA, manifest, f"{name}/jane-package.json")
    archive = build_archive(package_dir)
    stack.publish_local_package(manifest["package_id"], manifest["version"], archive)
    return {
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "digest": "sha256:" + hashlib.sha256(archive).hexdigest(),
    }


def llm_usage(llm: JaneClient, **params: str) -> dict[str, Any]:
    r = llm.api("llm").get("/v1/usage", params=params)
    assert r.status_code == 200, r.text
    return dict(r.json()["totals"])


def validate_task(orch: JaneClient, task: dict[str, Any]) -> dict[str, Any]:
    r = orch.api("orchestrator").post("/v1/task-validations", json=task)
    assert r.status_code == 200, r.text
    result: dict[str, Any] = r.json()
    assert result["valid"], result
    return result


def trace_of(orch: JaneClient, material_id: str, run_id: str) -> tuple[str, list[dict[str, Any]]]:
    """URL of the material and the stages of its observation in ``run_id`` (material ids are per URL and
    are shared with other scenarios of the stack, so the trace is narrowed to this run)."""
    r = orch.api("orchestrator").get(f"/v1/materials/{material_id}/trace")
    assert r.status_code == 200, r.text
    trace = r.json()
    (obs,) = [o for o in trace["observations"] if o.get("run_id") == run_id]
    return str(trace["url"]), list(obs["stages"])


def by_stage(items: Iterable[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """``stage_id -> material_id -> item`` (one item per material and stage in these tasks)."""
    out: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for item in items:
        assert item["material_id"] not in out[item["stage_id"]], item
        out[item["stage_id"]][item["material_id"]] = item
    return out


def invocation(llm: JaneClient, invocation_id: str) -> dict[str, Any]:
    """HandlerResult of the LLM handler (handler.v1 ``GET /v1/invocations/{id}``)."""
    r = llm.api("handler").get(f"/v1/invocations/{invocation_id}")
    assert r.status_code == 200, r.text
    return dict(r.json())


@pytest.fixture
def orchestrated_llm(require: Callable[..., None], orchestrated: JaneClient) -> JaneClient:
    """The M1 set of ``orchestrated`` plus the LLM gateway (executor ``llm`` of the orchestrator)."""
    require("llm")
    return orchestrated


# ---------------------------------------------------------------------------- S-M2-11
IN_STOCK = ("/product/phone-alpha", "/product/phone-beta")  # extractor: success
OUT_OF_STOCK = "/product/phone-gamma"  # extractor: unrecognized -> LLM: valid triage -> stored
PRE_ORDER = "/product/phone-zeta"  # extractor: unrecognized -> LLM: output violates the schema -> not stored
API_PRODUCT = "/api/v1/products/phone-alpha"  # application/json, bound to the extractor, not HTML
HTML_PAGES = (*IN_STOCK, OUT_OF_STOCK, PRE_ORDER)


def branching_task(
    task_id: str, source_id: str, extractor: dict[str, Any], triage: dict[str, Any]
) -> dict[str, Any]:
    """collect -> store-raw-html (HTML) || store-raw-json (JSON) || extract-products (HTML) ->
    store-products (success) || analyze-problems (LLM on unrecognized) -> store-triage (LLM success)."""
    return {
        "task_id": task_id,
        "title": f"e2e S-M2-11 {task_id}",
        "input": {"source_id": source_id, "urls": [TESTSITE + p for p in (*HTML_PAGES, API_PRODUCT)]},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}},
            {
                "stage_id": "store-raw-html",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
                "connections": {"target": "raw-files"},
                "inputs": [{"from": "collect", "when": HTML}],
            },
            {
                "stage_id": "store-raw-json",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
                "connections": {"target": "results-pg"},
                "inputs": [{"from": "collect", "when": JSON}],
            },
            {
                "stage_id": "extract-products",
                "kind": "handler",
                "handler": extractor,
                # Both URL forms of a product are bound; only the media-type condition keeps JSON out.
                "inputs": [{"from": "collect", "when": HTML}],
                "bindings": [{"url_patterns": [{"value": "*/product/*"}, {"value": "*/api/v1/products/*"}]}],
            },
            {
                "stage_id": "store-products",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
                "connections": {"target": "results-pg"},
                "inputs": [{"from": "extract-products", "select": "output", "when": SUCCESS}],
            },
            {
                "stage_id": "analyze-problems",
                "kind": "handler",
                "handler": triage,
                "inputs": [{"from": "extract-products", "select": "problems", "when": UNRECOGNIZED}],
                "on_failure": "continue",
            },
            {
                "stage_id": "store-triage",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
                "connections": {"target": "results-pg"},
                "inputs": [{"from": "analyze-problems", "select": "output", "when": SUCCESS}],
            },
        ],
    }


@pytest.mark.criteria(2)
def test_s_m2_11_conditional_branches_and_llm_on_problem_results(
    stack: E2EStack, orchestrated_llm: JaneClient, client: Callable[..., JaneClient], run_id: str
) -> None:
    """Branches run only when their conditions hold; the LLM stage gets exactly the problem results of the
    extractor; a schema-valid LLM output is stored, a schema-violating one is rejected and not stored;
    the trace shows every step of the material."""
    orch, storage, llm = orchestrated_llm, client("storage"), client("llm")
    extractor = local_package(stack, "e2e.instock-product-extractor")
    triage = local_package(stack, "e2e.llm-page-triage")
    source_id, task_id = f"e2e-{run_id}", f"e2e-{run_id}-branches"
    create_source(orch, source_id)
    task = branching_task(task_id, source_id, extractor, triage)
    validate_task(orch, task)
    create_task(orch, task)
    before = llm_usage(llm, scope_type="source", scope_id=source_id)
    assert before["requests"] == 0, before

    run = wait_run(orch, start_run(orch, task_id))
    assert run["status"] == "succeeded", run
    assert run["counters"]["materials"] == len(HTML_PAGES) + 1, run

    stages = by_stage(list_items(orch, run["run_id"]))
    path_of = {mid: trace_of(orch, mid, run["run_id"])[0].removeprefix(TESTSITE) for mid in stages["collect"]}
    mid = {path: m for m, path in path_of.items()}
    assert set(mid) == {*HTML_PAGES, API_PRODUCT}, path_of

    def routed(stage: str) -> set[str]:
        return {path_of[m] for m in stages.get(stage, {})}

    def status(stage: str, path: str) -> str:
        return str(stages[stage][mid[path]]["result_status"])

    # media-type branches: HTML RAW -> files, JSON RAW -> PostgreSQL, the extractor only on HTML
    assert routed("store-raw-html") == set(HTML_PAGES)
    assert routed("store-raw-json") == {API_PRODUCT}
    assert routed("extract-products") == set(HTML_PAGES), "JSON is bound but must be kept out by `when`"
    unknown = orch.api("orchestrator").get("/v1/unknown-materials", params={"source_id": source_id})
    assert unknown.json()["items"] == [], "every material matches the extractor binding"
    # result-status branches: success -> store-products; unrecognized -> LLM; LLM success -> store-triage
    assert {p: status("extract-products", p) for p in HTML_PAGES} == {
        **dict.fromkeys(IN_STOCK, "success"),
        OUT_OF_STOCK: "unrecognized",
        PRE_ORDER: "unrecognized",
    }
    assert routed("store-products") == set(IN_STOCK)
    assert routed("analyze-problems") == {OUT_OF_STOCK, PRE_ORDER}
    assert status("analyze-problems", OUT_OF_STOCK) == "success"
    assert status("analyze-problems", PRE_ORDER) == "failed"
    assert routed("store-triage") == {OUT_OF_STOCK}
    for stage, per_material in stages.items():
        for m, item in per_material.items():
            expected = "failed" if (stage, path_of[m]) == ("analyze-problems", PRE_ORDER) else "completed"
            assert item["status"] == expected, (stage, path_of[m], item)
            if stage not in {"collect", "analyze-problems"}:
                assert item["result_status"] in {"success", "unrecognized"}, (stage, item)

    # LLM output validated by the package schemas: the valid one became an entity, the invalid one failed
    ok = invocation(llm, stages["analyze-problems"][mid[OUT_OF_STOCK]]["invocation_id"])
    assert ok["status"] == "success", ok
    assert ok["handler"] == triage
    assert [i["kind"] for i in ok["inputs"]] == ["material", "data"]  # the page + the extractor's problem
    assert ok["inputs"][0]["material_id"] == mid[OUT_OF_STOCK]
    (triage_entity,) = ok["output"]["entities"]
    assert triage_entity["entity_type"] == "page_triage"
    assert triage_entity["key"] == {"scope": source_id, "natural": {"material_id": mid[OUT_OF_STOCK]}}
    assert triage_entity["fields"]["page_type"] == "product"
    assert ok["usage"]["llm"]["provider"] == "e2e-fake"
    assert ok["usage"]["llm"]["cost"]["amount"] > 0
    rejected = invocation(llm, stages["analyze-problems"][mid[PRE_ORDER]]["invocation_id"])
    assert rejected["status"] == "failed", rejected
    assert rejected["failure"]["kind"] == "schema_mismatch", rejected
    assert rejected["diagnostics"]["validation_errors"], rejected

    # storage: RAW by media type, products only from successful extraction, the stored LLM triage
    html_objects = objects_by_source(storage, "raw-files", source_id)
    assert {o["material"]["material_id"] for o in html_objects} == {mid[p] for p in HTML_PAGES}
    assert {o["object"]["media_type"] for o in html_objects} == {"text/html"}
    (json_object,) = objects_by_source(storage, "results-pg", source_id)
    assert json_object["material"]["material_id"] == mid[API_PRODUCT]
    assert json_object["object"]["media_type"] == "application/json"
    products = entities(storage, "results-pg", source_id, "product")
    assert {e["fields"]["sku"] for e in products} == {p.rsplit("/", 1)[1] for p in IN_STOCK}
    (stored_triage,) = entities(storage, "results-pg", source_id, "page_triage")
    assert stored_triage["fields"] == triage_entity["fields"]
    assert stored_triage["fields"]["material_id"] == mid[OUT_OF_STOCK]

    # traceability: material -> stages -> results -> package versions (with digests) -> outputs
    _, gamma = trace_of(orch, mid[OUT_OF_STOCK], run["run_id"])
    steps = {s["stage_id"]: s for s in gamma}
    assert set(steps) == {"store-raw-html", "extract-products", "analyze-problems", "store-triage"}, gamma
    assert steps["extract-products"]["handler"]["digest"] == extractor["digest"]
    assert steps["extract-products"]["result_status"] == "unrecognized"
    assert steps["analyze-problems"]["handler"]["digest"] == triage["digest"]
    assert any(
        o["kind"] == "entity" and o.get("entity_type") == "page_triage"
        for o in steps["analyze-problems"]["outputs"]
    ), steps["analyze-problems"]
    assert any(
        o.get("entity_type") == "page_triage" and o.get("connection_id") == "results-pg"
        for o in steps["store-triage"]["outputs"]
    ), steps["store-triage"]
    _, zeta = trace_of(orch, mid[PRE_ORDER], run["run_id"])
    assert [s["stage_id"] for s in zeta if s["stage_id"] == "store-triage"] == []
    assert next(s for s in zeta if s["stage_id"] == "analyze-problems")["result_status"] == "failed"
    _, api = trace_of(orch, mid[API_PRODUCT], run["run_id"])
    assert [s["stage_id"] for s in api] == ["store-raw-json"], api

    # problem grouping and cost accounting of the LLM stage
    groups = orch.api("orchestrator").get("/v1/problem-groups", params={"source_id": source_id}).json()
    (extractor_group,) = [
        g for g in groups["items"] if (g.get("package") or {}).get("package_id") == extractor["package_id"]
    ]
    assert extractor_group["problem"] == "unrecognized"
    assert extractor_group["signature"] == "unknown-availability"
    assert extractor_group["count"] == 2
    used = llm_usage(llm, scope_type="source", scope_id=source_id)
    assert used["requests"] >= 2 and used["cost"]["amount"] > 0, used
    assert run["costs"]["llm"]["amount"] > 0, run


# ---------------------------------------------------------------------------- S-M2-05
UNKNOWN_TYPES = {"/pages/event-spring-meetup": "event", "/pages/careers": "job", "/pages/faq": "faq"}


def unknown_pages_task(
    task_id: str, source_id: str, urls: list[str], extractor: dict[str, Any], triage: dict[str, Any]
) -> dict[str, Any]:
    """collect -> extract-products (bound to /product/*) -> store-products || unknown-pages (LLM on
    ``unmatched_materials``). The task leaves the flag to the source (no ``forward_unknown_to_llm``)."""
    return {
        "task_id": task_id,
        "title": f"e2e S-M2-05 {task_id}",
        "input": {"source_id": source_id, "urls": urls},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}},
            {
                "stage_id": "extract-products",
                "kind": "handler",
                "handler": extractor,
                "inputs": [{"from": "collect", "when": HTML}],
                "bindings": [{"url_patterns": [{"value": "*/product/*"}]}],
            },
            {
                "stage_id": "store-products",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
                "connections": {"target": "results-pg"},
                "inputs": [{"from": "extract-products", "select": "output", "when": SUCCESS}],
            },
            {
                "stage_id": "unknown-pages",
                "kind": "handler",
                "handler": triage,
                "inputs": [{"from": "collect", "select": "unmatched_materials"}],
            },
        ],
    }


def unknown_of_run(orch: JaneClient, source_id: str, run_id: str) -> dict[str, dict[str, Any]]:
    r = orch.api("orchestrator").get("/v1/unknown-materials", params={"source_id": source_id, "limit": 500})
    assert r.status_code == 200, r.text
    return {u["material_id"]: u for u in r.json()["items"] if u.get("run_id") == run_id}


@pytest.mark.criteria(11)
def test_s_m2_05_unknown_pages_reach_llm_only_after_the_flag_is_enabled(
    stack: E2EStack,
    orchestrated_llm: JaneClient,
    client: Callable[..., JaneClient],
    extractor: dict[str, Any],
    run_id: str,
) -> None:
    """Flag off on the source: unknown pages are registered, no LLM call at all. Flag switched on: the next
    run forwards exactly those pages to the LLM stage; calls, results and costs point to them."""
    orch, llm = orchestrated_llm, client("llm")
    api = orch.api("orchestrator")
    triage = local_package(stack, "e2e.llm-page-triage")
    source_id, task_id = f"e2e-{run_id}", f"e2e-{run_id}-unknown"
    products = site_paths("product")[:2]
    assert sorted(UNKNOWN_TYPES) == site_paths("unknown")  # testsite page_types: unknown
    urls = [TESTSITE + p for p in (*products, *UNKNOWN_TYPES)]
    create_source(orch, source_id, forward_unknown_to_llm=False)
    task = unknown_pages_task(task_id, source_id, urls, extractor, triage)
    off = validate_task(orch, task)
    assert off["effective_forward_unknown_to_llm"] is False, off
    create_task(orch, task)

    # ---- run 1, flag off: registered as unknown, not forwarded, the LLM gateway sees no request at all
    total_before = llm_usage(llm)["requests"]
    first = wait_run(orch, start_run(orch, task_id))
    assert first["status"] == "succeeded", first
    stages1 = by_stage(list_items(orch, first["run_id"]))
    assert len(stages1["collect"]) == len(urls)
    assert len(stages1["extract-products"]) == len(stages1["store-products"]) == len(products)
    assert "unknown-pages" not in stages1, stages1.get("unknown-pages")
    registered1 = unknown_of_run(orch, source_id, first["run_id"])
    assert {u["url"].removeprefix(TESTSITE) for u in registered1.values()} == set(UNKNOWN_TYPES)
    assert not any(u["forwarded_to_llm"] for u in registered1.values()), registered1
    assert all("forward_unknown_to_llm=false" in u["reason"] for u in registered1.values())
    assert llm_usage(llm, scope_type="source", scope_id=source_id)["requests"] == 0
    assert llm_usage(llm)["requests"] == total_before, "LLM called although the flag is off"
    assert "llm" not in (first.get("costs") or {}), first

    # ---- the user switches «Передавати в LLM невідомі сторінки» on for the source
    current = api.get(f"/v1/sources/{source_id}")
    assert current.status_code == 200, current.text
    doc = {k: v for k, v in current.json().items() if k not in {"created_at", "updated_at"}}
    doc["forward_unknown_to_llm"] = True
    updated = api.put(f"/v1/sources/{source_id}", json=doc, headers={"If-Match": current.headers["etag"]})
    assert updated.status_code == 200, updated.text
    on = validate_task(orch, task)
    assert on["effective_forward_unknown_to_llm"] is True, on

    # ---- run 2, flag on: exactly the unknown pages go to the LLM stage
    second = wait_run(orch, start_run(orch, task_id))
    assert second["status"] == "succeeded", second
    stages2 = by_stage(list_items(orch, second["run_id"]))
    registered2 = unknown_of_run(orch, source_id, second["run_id"])
    assert set(registered2) == set(registered1)  # the same pages (material ids), new observations
    assert all(u["forwarded_to_llm"] for u in registered2.values()), registered2
    forwarded = stages2["unknown-pages"]
    assert set(forwarded) == set(registered2), (sorted(forwarded), sorted(registered2))
    assert len(stages2["extract-products"]) == len(products)
    for material_id, item in forwarded.items():
        assert item["status"] == "completed" and item["result_status"] == "success", item
        assert item["observation_id"] == registered2[material_id]["observation_id"]
        result = invocation(llm, item["invocation_id"])
        assert [i["material_id"] for i in result["inputs"]] == [material_id]
        assert result["handler"]["digest"] == triage["digest"]
        (triaged,) = result["output"]["entities"]
        assert triaged["key"]["natural"] == {"material_id": material_id}
        path = registered2[material_id]["url"].removeprefix(TESTSITE)
        assert triaged["fields"]["page_type"] == UNKNOWN_TYPES[path], (path, triaged)
        assert result["usage"]["llm"]["cost"]["amount"] > 0, result["usage"]
        _, trace = trace_of(orch, material_id, second["run_id"])
        assert [s["stage_id"] for s in trace] == ["unknown-pages"], trace
        _, trace_off = trace_of(orch, material_id, first["run_id"])
        assert trace_off == [], trace_off  # run 1: registered only

    # ---- cost accounting: calls of this source, by purpose, and the run's LLM cost
    used = llm_usage(llm, scope_type="source", scope_id=source_id)
    assert used["requests"] == len(UNKNOWN_TYPES), used
    assert used["input_tokens"] > 0 and used["output_tokens"] > 0 and used["cost"]["amount"] > 0, used
    by_purpose = llm.api("llm").get(
        "/v1/usage", params={"scope_type": "source", "scope_id": source_id, "group_by": "purpose"}
    )
    assert by_purpose.status_code == 200, by_purpose.text
    assert {row["purpose"] for row in by_purpose.json()["items"]} == {"handler"}
    assert llm_usage(llm)["requests"] >= total_before + len(UNKNOWN_TYPES)
    assert second["costs"]["llm"]["amount"] > 0, second
