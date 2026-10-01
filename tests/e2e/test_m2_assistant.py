"""M2: the source assistant (WP-11) on the full stack (docs/acceptance/scenarios.md).

* S-M2-06 (criterion 4): a new source given by its name -> search (two candidates, the user picks one)
  -> adaptive sampling through the real Web Collector -> analysis -> several collection plans with coverage,
  cost and risks -> a new extractor generated, tested in the real runtime and published to the real registry
  (provenance ``llm``) -> the source and the task are created in the orchestrator -> a run stores entities.
  The full chain runs with the user's crawl hints (entry pages of the sections). The name-only path
  checks whether the real collector yields the main material types and testable extractor plans.
* S-M2-07 (criterion 6): a human-written extractor leaves part of the pages ``unrecognized`` -> problem group
  in the orchestrator -> improvement run -> a new version in the registry (provenance ``llm``) that passes the
  old and the new tests and the tests of every binding -> automatic activation in the task stages ->
  reprocessing of the stored RAW gives ``success`` -> rollback -> the old behaviour is back -> the audit log
  has the activation and the rollback. Separately: a package whose automatic changes are forbidden gets only a
  proposal, and the orchestrator refuses its automatic activation.

Real services: assistant (WP-11), LLM gateway (WP-10), registry (WP-05), web-collector (WP-02/03),
handler-runtime (WP-06), orchestrator (WP-09), storage (WP-07), testsite, PostgreSQL and MinIO (WP-01).
In this module's own stack the runtime, the collector and the orchestrator take packages and rules from the
real registry (no ``package-host``).

Substitutes of EXTERNAL systems (**З**): the LLM is the deterministic provider ``fake`` of WP-10; only the text
of its answers is scripted (tests/e2e/config/llm-seed.yaml, connection ``e2e-assistant-scripts``). The web
search is the ``static`` provider of WP-11 (tests/e2e/config/assistant-search.json).
"""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from typing import Any

import pytest

from jane_e2e.assistant import (
    PROBLEMS,
    Flows,
    activations,
    archive_digest,
    assistant_flows,
    by_purpose,
    improve,
    items_by_path,
    new_key,
    note,
    poll,
    prepare_improvable,
    problem_group,
    registry_package,
    registry_version,
    reprocess,
    runtime_tests,
    stage_handler,
)
from jane_e2e.clients import JaneClient, spec
from jane_e2e.orchestration import TESTSITE, list_items, start_run, wait_run
from jane_e2e.stack import E2EStack
from jane_e2e.verify import entities, expected_set, site_paths

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

TESTSITE_URL = f"{TESTSITE}/"  # the site as the services see it (assistant-search.json)
RUNNING = frozenset({"resolving", "sampling", "analyzing", "applying"})
SUCCESS = {"field": "result.status", "op": "eq", "value": "success"}


@pytest.fixture(scope="module")
def flows(stack: E2EStack) -> Iterator[Flows]:
    """An isolated stack of all services the assistant combines, with the real registry everywhere
    (``jane_e2e.assistant.assistant_flows``).

    ``stack`` (session) only checks Docker; this module never starts services in it. S-M2-06 runs first on the
    empty registry (so that no existing extractor is bound instead of generating one), then S-M2-07."""
    with assistant_flows("assistant", label="S-M2-06/07") as own:
        yield own


# ---------------------------------------------------------------------------- helpers
def session_of(assistant: JaneClient, session_id: str) -> dict[str, Any]:
    r = assistant.api("assistant").get(f"/v1/onboarding-sessions/{session_id}")
    assert r.status_code == 200, r.text
    return dict(r.json())


def wait_session(
    assistant: JaneClient, session_id: str, *, leave: frozenset[str] = RUNNING
) -> dict[str, Any]:
    """Poll the session until its status leaves ``leave`` (the onboarding job runs in the background)."""
    return dict(
        poll(
            f"onboarding session {session_id}",
            lambda: session_of(assistant, session_id),
            lambda s: s["status"] not in leave,
        )
    )


# ---------------------------------------------------------------------------- S-M2-06
# Relevant sections supplied by the user (OnboardingRequest.crawl_hints, a CollectorRules fragment - ТЗ §8
# "правила обходу"). The scope excludes unrelated low-confidence pages such as FAQ and calendar, while
# retaining products, categories, articles and news listings. The sitemap paths must also remain in scope:
# the chosen collector rules use them to discover the material pages after activation.
SECTION_PREFIXES = ("/catalog/", "/product/", "/news/", "/sitemap.xml", "/sitemaps/")
SECTION_PAGES = (
    "/catalog/phones/",
    "/product/phone-alpha",
    "/news/",
    "/news/2026/autumn-sale",
    "/catalog/laptops/",
    "/product/laptop-one",
    "/news/2026/holiday-hours",
)


def onboard_by_name(assistant: JaneClient, body: dict[str, Any]) -> dict[str, Any]:
    """``startOnboarding`` by the site NAME -> two search candidates -> the user picks the test site -> the
    session after adaptive sampling (real Web Collector), analysis and extractor preparation."""
    api = assistant.api("assistant")
    started = api.post("/v1/onboarding-sessions", json=body, headers={"Idempotency-Key": new_key()})
    assert started.status_code == 202, started.text
    session_id = started.json()["labels"]["session_id"]  # WP-11 convention (Job.labels), see WP-11.md
    session = wait_session(assistant, session_id)
    assert session["status"] == "needs_disambiguation", session
    candidates = {c["url"]: c for c in session["candidates"]}
    assert set(candidates) == {TESTSITE_URL, "http://testsite-mirror.example.test/"}, session["candidates"]
    chosen = candidates[TESTSITE_URL]["candidate_id"]
    note(
        "S-M2-06",
        "candidates",
        [(c["candidate_id"], c["url"], c["confidence"]) for c in session["candidates"]],
    )
    selected = api.post(
        f"/v1/onboarding-sessions/{session_id}/candidate-selection", json={"candidate_id": chosen}
    )
    assert selected.status_code == 200, selected.text
    assert selected.json()["selected_candidate_id"] == chosen
    session = wait_session(assistant, session_id)
    if session["status"] != "proposals_ready":
        note("S-M2-06", "onboarding unexpected terminal session", session)
    assert session["status"] == "proposals_ready", session
    return session


def check_sample_and_proposals(session: dict[str, Any]) -> None:
    """A sample that distinguishes the material types of the site, the analysis, a new product extractor that
    passed its tests on the samples in the real runtime, and several plans with coverage, cost and risks."""
    sample = session["sample"]
    note("S-M2-06", "sample", sample)
    counts = {t["type"]: t["count"] for t in (session.get("analysis") or {}).get("material_types") or []}
    note("S-M2-06", "material types", counts)
    assert sample["sufficient"] is True and sample["confidence"] >= 0.8, sample
    assert sample["distinct_types"] >= 2, (sample, session.get("analysis"))
    analysis = session["analysis"]
    assert analysis["source_kind"] == "web" and "sitemap" in analysis["discovery_methods"], analysis
    types = {t["type"]: t for t in analysis["material_types"]}
    assert "product" in types and sum(t["count"] for t in types.values()) == sample["materials"], types
    sampled_urls = [u for t in analysis["material_types"] for u in t.get("example_urls", [])]
    assert sampled_urls and all(u.startswith(TESTSITE_URL) for u in sampled_urls), sampled_urls
    assert all(u.startswith(f"{TESTSITE}/product/") for u in types["product"]["example_urls"]), types
    (product_entity,) = analysis["entities"]
    assert product_entity["entity_type"] == "product"
    assert {"sku", "price"} <= {f["name"] for f in product_entity["fields"]}

    proposals = session["proposals"]
    for p in proposals:
        note(
            "S-M2-06",
            f"proposal {p['proposal_id']}",
            {
                "title": p["title"],
                "recommended": p["recommended"],
                "strategies": [s["type"] for s in p["collector_rules"]["strategies"]],
                "coverage": p["coverage"],
                "cost": p["cost"],
                "risks": p["risks"],
                "extractors": p["extractors"],
            },
        )
    assert len(proposals) >= 2, proposals
    assert [p["recommended"] for p in proposals].count(True) == 1, proposals
    for p in proposals:
        assert p["coverage"]["estimated_materials"] > 0 and p["coverage"]["entity_types"] == ["product"], p
        assert "discovered while sampling" in p["coverage"]["notes"], p  # the collector's own statistics
        assert p["cost"]["requests_per_run_estimate"] >= p["coverage"]["estimated_materials"], p
        assert p["cost"]["llm_setup_cost"]["amount"] > 0, p  # sampling and analysis were paid for
        assert p["cost"]["llm_cost_per_run"]["amount"] == 0, p  # the generated extractor calls no LLM
        assert p["risks"], p
        assert p["collector_rules"]["scope"]["allowed_domains"] == ["testsite"], p
        (plan,) = p["extractors"]
        assert plan["entity_type"] == "product" and plan["action"] == "create", plan
        assert plan["tested_on_samples"]["passed"] >= 2 and plan["tested_on_samples"]["failed"] == 0, plan
    assert session["costs"]["amount"] > 0, session


@pytest.mark.criteria(4)
def test_s_m2_06_name_only_sample_distinguishes_material_types(flows: Flows) -> None:
    """Only the site's name (ТЗ §8): the sample must be diverse enough to tell the material types apart, and
    the extractor made from it must pass its tests. Runs before any package exists in the registry and stops
    before acceptance (publishes nothing)."""
    session = onboard_by_name(flows["assistant"], {"query": "testsite"})
    check_sample_and_proposals(session)
    counts = {t["type"]: t["count"] for t in session["analysis"]["material_types"]}
    # The testsite sitemap contains products, category pages and articles. A single
    # negative page does not establish that the main material types were distinguished.
    assert all(counts.get(kind, 0) >= 2 for kind in ("product", "category", "article")), counts
    note("S-M2-06", "LLM requests after name-only onboarding", by_purpose(flows["llm"]))


@pytest.mark.criteria(4)
def test_s_m2_06_name_and_crawl_hints_to_extractor_source_task_and_entities(
    flows: Flows, run_id: str
) -> None:
    """Name + the user's crawl hints -> candidates -> the user picks the test site -> adaptive sampling via the
    real collector -> proposals with coverage, cost and risks -> acceptance with activation -> an extractor
    created by the LLM is published (provenance llm), its tests pass in the real runtime, the source and the
    task exist in the orchestrator, and a run of that task stores product entities."""
    assistant, llm, registry = flows["assistant"], flows["llm"], flows["registry"]
    runtime, orch, storage = flows["handler-runtime"], flows["orchestrator"], flows["storage"]
    api = assistant.api("assistant")
    onboarding_before = by_purpose(llm).get("onboarding", 0)

    # ---- 1-2. the name of the site plus entry pages of its sections; search, choice, sampling, proposals
    hints = {
        "scope": {"path_prefixes": list(SECTION_PREFIXES)},
        "strategies": [{"type": "seed_list", "urls": [TESTSITE + p for p in SECTION_PAGES]}],
    }
    session = onboard_by_name(assistant, {"query": "testsite", "crawl_hints": hints})
    session_id = session["session_id"]
    check_sample_and_proposals(session)
    assert session["sample"]["distinct_types"] >= 4, session["sample"]
    counts = {t["type"]: t["count"] for t in session["analysis"]["material_types"]}
    assert all(counts.get(kind, 0) >= 2 for kind in ("product", "category", "article")), counts
    proposals = session["proposals"]
    assert by_purpose(llm).get("onboarding", 0) > onboarding_before

    # ---- 3. the user accepts the recommended plan with activation, under its own source id
    proposal = next(p for p in proposals if p["recommended"])
    assert [s["type"] for s in proposal["collector_rules"]["strategies"]] == ["sitemap"], proposal
    source_id = f"e2e-{run_id}"
    accepted = api.post(
        f"/v1/onboarding-sessions/{session_id}/proposals/{proposal['proposal_id']}/acceptance",
        json={"activate": True, "source_id": source_id},
        headers={"Idempotency-Key": new_key()},
    )
    assert accepted.status_code == 202, accepted.text
    done = assistant.wait_job("assistant", accepted.json()["job_id"], timeout_s=600)
    assert done["status"] == "succeeded", done
    result = done["result"]
    assert result["activated"] is True, result
    (created,) = result["extractors"]
    assert created["action"] == "create", created
    package = created["package"]
    assert created["test_report"]["failed"] == 0 and created["test_report"]["passed"] >= 2, created
    rules_ref = result["collector_rules"]
    assert wait_session(assistant, session_id)["status"] == "completed"
    note("S-M2-06", "accepted", {"rules": rules_ref, "extractor": package, "activated": result["activated"]})

    # ---- 4. the real registry: an LLM-made extractor and LLM-made collector rules, approved, tests recorded
    version = registry_version(registry, package)
    manifest = version["manifest"]
    assert manifest["kind"] == "extractor" and manifest["provenance"]["created_by"] == "llm", manifest
    assert manifest["provenance"]["llm"]["reason"] == "onboarding", manifest["provenance"]
    assert manifest["provenance"]["llm"]["provider"] == "e2e-assistant", manifest["provenance"]  # З: fake LLM
    assert version["status"] == "approved" and version["test_status"] == "passed", version
    assert any(r.get("runner") == "assistant" for r in version.get("test_reports") or []), version
    assert archive_digest(registry, package)[0] == package["digest"] == version["digest"]
    assert {t["origin"] for t in manifest["tests"]} == {"llm"}
    assert {t["expected_status"] for t in manifest["tests"]} >= {"success", "empty"}, manifest["tests"]
    note(
        "S-M2-06",
        "registry extractor",
        {
            "status": version["status"],
            "test_status": version["test_status"],
            "provenance": manifest["provenance"],
        },
    )
    note(
        "S-M2-06",
        "registry tests",
        [(t["name"], t["expected_status"], t["origin"]) for t in manifest["tests"]],
    )
    rules = registry_version(registry, rules_ref)
    assert rules["manifest"]["kind"] == "collector-rules", rules
    assert rules["manifest"]["provenance"]["created_by"] == "llm" and rules["status"] == "approved", rules

    # ---- 5. the published version passes its own tests in the real runtime (archive taken from the registry)
    report = runtime_tests(runtime, package)
    note(
        "S-M2-06", "runtime test run (by reference)", {k: report[k] for k in ("passed", "failed", "package")}
    )
    assert report["failed"] == 0 and report["passed"] == len(manifest["tests"]), report
    assert report["package"]["digest"] == package["digest"], report

    # ---- 6. the orchestrator: the source and the task the assistant created
    source = orch.api("orchestrator").get(f"/v1/sources/{source_id}")
    assert source.status_code == 200, source.text
    assert source.json()["collector_rules"] == rules_ref, source.json()
    assert source.json()["locator"]["url"] == TESTSITE_URL
    task_id = f"{source_id}-collect"
    task = orch.api("orchestrator").get(f"/v1/tasks/{task_id}")
    assert task.status_code == 200, task.text
    stages = {s["stage_id"]: s for s in task.json()["stages"]}
    note(
        "S-M2-06", "orchestrator task", {k: v.get("handler") or v.get("collector") for k, v in stages.items()}
    )
    assert stages["collect"]["collector"]["rules"] == rules_ref, stages
    assert stages["extract-product"]["handler"] == package, stages
    assert stages["store-product"]["handler"]["package_id"] == "jane.storage-postgresql", stages
    assert stages["store-product"]["connections"] == {"target": "results-pg"}, stages

    # ---- 7. a run of that task: sitemap -> extractor -> product entities in storage
    run = wait_run(orch, start_run(orch, task_id))
    assert run["status"] == "succeeded", run
    products = expected_set("sitemap") & set(site_paths("product"))
    extracted = list_items(orch, run["run_id"], "extract-product")
    statuses = [i["result_status"] for i in extracted]
    assert statuses.count("success") == len(products), statuses
    assert set(statuses) == {"success", "empty"}, statuses
    stored = entities(storage, "results-pg", source_id, "product")
    note("S-M2-06", "run", {"status": run["status"], "stages": run["stages"], "entities": len(stored)})
    assert {e["fields"]["sku"] for e in stored} == {p.rsplit("/", 1)[1] for p in products}, stored
    alpha = next(e for e in stored if e["fields"]["sku"] == "phone-alpha")
    assert alpha["fields"]["price"] == {"amount": 299.0, "currency": "UAH"}, alpha
    assert alpha["fields"]["availability"] == "in_stock", alpha
    note("S-M2-06", "LLM requests after hinted onboarding", by_purpose(llm))


# ---------------------------------------------------------------------------- S-M2-07


@pytest.mark.criteria(6)
def test_s_m2_07_improvement_activation_rollback_and_forbidden_auto_changes(
    flows: Flows, run_id: str
) -> None:
    """Problem samples -> new version by the LLM that passes old and new tests on every binding -> automatic
    activation -> reprocessed RAW succeeds -> rollback -> old behaviour and audit; then automatic changes of
    the package are forbidden: only a proposal, and the orchestrator refuses an automatic activation."""
    assistant, registry, runtime = flows["assistant"], flows["registry"], flows["handler-runtime"]
    orch, storage = flows["orchestrator"], flows["storage"]
    oapi = orch.api("orchestrator")

    # ---- setup: a human-written extractor 1.0.0 in the registry, a source that allows automatic LLM versions,
    #      a task bound to the extractor (and a second task: a second binding of the same package)
    # ---- 1. a real run: 1.0.0 does not recognise out-of-stock and pre-order cards -> a problem group
    case = prepare_improvable(flows, f"e2e-{run_id}", "S-M2-07")
    package_id, v1, old = case.package_id, case.v1, case.old
    source_id, task_id, recheck_id = case.source_id, case.task_id, case.recheck_id
    first, path_of, mid, request = case.first, case.path_of, case.mid, case.request

    # ---- 2. improvement run: the LLM fixes the code; old + new tests and every binding are checked
    job_id, improved = improve(assistant, request)
    assert improved["outcome"] == "new_version" and improved["activated"] is True, improved
    assert improved["attempts"] == 1, improved
    new = improved["version"]
    assert (new["package_id"], new["version"]) == (package_id, "1.1.0"), new  # additive schema change
    reports = {r["context"]: r["report"] for r in improved["test_reports"]}
    assert set(reports) == {
        "tests",
        f"bindings:{task_id}/extract-products",
        f"bindings:{recheck_id}/extract-products",
    }, reports
    for context, report in reports.items():
        assert report["failed"] == 0 and report["passed"] > 0, (context, report)
    cases = {c["name"] for c in reports["tests"]["cases"]}
    note(
        "S-M2-07",
        "improvement",
        {
            "outcome": improved["outcome"],
            "version": new,
            "attempts": improved["attempts"],
            "activated": improved["activated"],
            "costs": improved.get("costs"),
            "reports": {c: (r["passed"], r["failed"]) for c, r in reports.items()},
            "cases": sorted(cases),
        },
    )
    old_tests = {t["name"] for t in v1["manifest"]["tests"]}
    assert old_tests | {"problem-p1", "problem-p2", "success-s1", "success-s2"} <= cases, cases

    # the registry: an LLM version based on 1.0.0, approved, all test reports recorded
    v2 = registry_version(registry, new)
    prov = v2["manifest"]["provenance"]
    assert prov["created_by"] == "llm" and prov["based_on"] == {"package_id": package_id, "version": "1.0.0"}
    assert prov["llm"]["reason"] == "improvement" and prov["llm"]["assistant_job_id"] == job_id, prov
    assert prov["llm"]["provider"] == "e2e-assistant", prov  # З: the fake LLM provider
    assert v2["status"] == "approved" and v2["test_status"] == "passed", v2
    assert {r["context"] for r in v2.get("test_reports") or []} >= set(reports), v2.get("test_reports")
    origins = {t["name"]: t["origin"] for t in v2["manifest"]["tests"]}
    assert origins == {
        **{n: "human" for n in old_tests},
        "problem-p1": "problem_sample",
        "problem-p2": "problem_sample",
    }
    diff = registry.api("registry").get(
        f"/v1/packages/{package_id}/diff", params={"from": "1.0.0", "to": "1.1.0"}
    )
    assert diff.status_code == 200, diff.text
    changed = {f["path"] for f in diff.json()["files"] if f["status"] != "unchanged"}
    note(
        "S-M2-07",
        "registry 1.1.0",
        {"status": v2["status"], "test_status": v2["test_status"], "provenance": prov},
    )
    note("S-M2-07", "diff 1.0.0..1.1.0", sorted(changed))
    assert {"src/e2e_improvable_products/main.py", "schemas/product.schema.json"} <= changed, diff.json()
    assert runtime_tests(runtime, new)["failed"] == 0  # the published archive, by reference, in the runtime

    # the orchestrator: both bindings run the new version, activated automatically; the group is resolved
    for task in (task_id, recheck_id):
        assert stage_handler(orch, task, "extract-products") == new, task
        latest = activations(orch, task, "extract-products")[0]
        assert latest["kind"] == "auto_activate" and latest["package"] == new, latest
        assert latest["previous"]["version"] == "1.0.0", latest
        note("S-M2-07", f"activation {task}", {k: latest.get(k) for k in ("kind", "package", "previous")})
    resolved = problem_group(orch, source_id, package_id)
    assert resolved["status"] == "resolved" and resolved["assistant_job_id"] == job_id, resolved
    note(
        "S-M2-07", "problem group after the run", {k: resolved.get(k) for k in ("status", "assistant_job_id")}
    )

    # ---- 3. reprocessing of the stored RAW with the active version: the problem pages succeed now
    problem_ids = [mid[p] for p in PROBLEMS]
    since = first["created_at"]
    fixed = reprocess(orch, task_id, problem_ids, since, "e2e: 1.1.0 handles out-of-stock and pre-order")
    run2 = items_by_path(orch, fixed["run_id"], "extract-products", path_of)
    assert {p: i["result_status"] for p, i in run2.items()} == dict.fromkeys(PROBLEMS, "success"), run2
    for path, item in run2.items():
        trace = oapi.get(f"/v1/materials/{item['material_id']}/trace").json()
        (obs,) = [o for o in trace["observations"] if o.get("run_id") == fixed["run_id"]]
        step = next(s for s in obs["stages"] if s["stage_id"] == "extract-products")
        assert step["handler"]["digest"] == new["digest"], (path, step)
    saved = {e["fields"]["sku"]: e["fields"] for e in entities(storage, "results-pg", source_id, "product")}
    assert saved["phone-gamma"]["availability"] == "out_of_stock", saved
    assert saved["phone-zeta"]["availability"] == "pre_order", saved
    note("S-M2-07", "reprocessing (1.1.0)", {p: i["result_status"] for p, i in sorted(run2.items())})
    note("S-M2-07", "stored entities", {k: v.get("availability") for k, v in sorted(saved.items())})

    # ---- 4. rollback of the catalog task to the previous version: the old behaviour is back
    rolled = oapi.post(
        f"/v1/tasks/{task_id}/stages/extract-products/activations",
        json={"kind": "rollback", "reason": "e2e: back to the human baseline"},
        headers={"Idempotency-Key": new_key()},
    )
    assert rolled.status_code == 200, rolled.text
    assert rolled.json()["kind"] == "rollback" and rolled.json()["package"] == old, rolled.json()
    assert stage_handler(orch, task_id, "extract-products") == old
    assert stage_handler(orch, recheck_id, "extract-products") == new  # rollback is per stage
    again = reprocess(orch, task_id, problem_ids, since, "e2e: after the rollback")
    run3 = items_by_path(orch, again["run_id"], "extract-products", path_of)
    assert {p: i["result_status"] for p, i in run3.items()} == dict.fromkeys(PROBLEMS, "unrecognized"), run3
    assert list_items(orch, again["run_id"], "store-products") == []
    note("S-M2-07", "rollback", {k: rolled.json().get(k) for k in ("kind", "package", "previous")})
    note(
        "S-M2-07", "reprocessing after the rollback", {p: i["result_status"] for p, i in sorted(run3.items())}
    )

    # the audit log of the stage has the automatic activation and the rollback
    audit = oapi.get(
        "/v1/audit-events", params={"subject_type": "stage", "subject_id": f"{task_id}/extract-products"}
    )
    assert audit.status_code == 200, audit.text
    events = {e["action"]: e for e in audit.json()["items"]}
    note("S-M2-07", "audit", [(e["action"], e["details"]) for e in audit.json()["items"]])
    assert {"stage.auto_activate", "stage.rollback"} <= set(events), audit.json()
    assert events["stage.auto_activate"]["details"]["version"] == "1.1.0"
    assert events["stage.auto_activate"]["details"]["previous"] == "1.0.0"
    assert events["stage.rollback"]["details"]["version"] == "1.0.0"
    assert events["stage.rollback"]["details"]["previous"] == "1.1.0"

    # ---- 5. the user forbids automatic changes of the package
    pkg, etag = registry_package(registry, package_id)
    assert pkg["auto_changes_allowed"] is True
    forbid, merge_patch = {"auto_changes_allowed": False}, "application/merge-patch+json"
    spec("registry").validate_request("PATCH", f"/v1/packages/{package_id}", forbid, merge_patch)
    patched = registry.api("registry").patch(  # the response is checked by the contract client
        f"/v1/packages/{package_id}",
        content=json.dumps(forbid),
        headers={"If-Match": etag, "Content-Type": merge_patch},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["auto_changes_allowed"] is False
    history_before = activations(orch, task_id, "extract-products")

    # the assistant only proposes: nothing is published, nothing is activated, the group stays unresolved
    blocked = copy.deepcopy(request)
    _, proposal = improve(assistant, blocked)
    assert proposal["outcome"] == "proposal_only" and proposal["activated"] is False, proposal
    assert proposal["version"]["package_id"] == package_id, proposal
    missing = registry.api("registry").get(
        f"/v1/packages/{package_id}/versions/{proposal['version']['version']}"
    )
    assert missing.status_code == 404, missing.text
    assert registry_package(registry, package_id)[0]["latest_version"] == "1.1.0"
    note(
        "S-M2-07",
        "auto changes forbidden: improvement",
        {"outcome": proposal["outcome"], "version": proposal["version"], "activated": proposal["activated"]},
    )
    assert stage_handler(orch, task_id, "extract-products") == old
    assert activations(orch, task_id, "extract-products") == history_before
    assert problem_group(orch, source_id, package_id)["status"] == "unresolved"

    # and the orchestrator itself refuses an automatic activation of that package (approved, tests passed)
    refused = oapi.post(
        f"/v1/tasks/{task_id}/stages/extract-products/activations",
        json={"kind": "auto_activate", "package": new, "reason": "e2e: must be refused"},
        headers={"Idempotency-Key": new_key()},
    )
    assert refused.status_code == 403, refused.text
    assert refused.json()["code"] == "access_denied_by_policy", refused.json()
    assert refused.json()["details"]["reason"] == "package_auto_changes_forbidden", refused.json()
    assert stage_handler(orch, task_id, "extract-products") == old
    note(
        "S-M2-07", "auto_activate refused", {k: refused.json().get(k) for k in ("status", "code", "details")}
    )
    note("S-M2-07", "LLM requests after improvement", by_purpose(flows["llm"]))
