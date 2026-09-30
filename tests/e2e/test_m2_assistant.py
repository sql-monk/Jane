"""M2: the source assistant (WP-11) on the full stack (docs/acceptance/scenarios.md).

* S-M2-06 (criterion 4): a new source given by its name -> search (two candidates, the user picks one)
  -> adaptive sampling through the real Web Collector -> analysis -> several collection plans with coverage,
  cost and risks -> a new extractor generated, tested in the real runtime and published to the real registry
  (provenance ``llm``) -> the source and the task are created in the orchestrator -> a run stores entities.
  The full chain runs with the user's crawl hints (entry pages of the sections); with the name ONLY the
  sample settles on the first two product pages - a WP-11 defect, kept as a strict xfail.
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

import base64
import copy
import hashlib
import io
import json
import os
import time
import uuid
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from jane_e2e.clients import CONTRACTS, JaneClient, spec
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
from jane_e2e.stack import E2EStack, default_project
from jane_e2e.steps import sandbox_limits
from jane_e2e.verify import entities, expected_set, objects_by_source, site_paths

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

PACKAGES = Path(__file__).resolve().parent / "packages"
IMPROVABLE = PACKAGES / "e2e.improvable-product-extractor"
MANIFEST_SCHEMA = (CONTRACTS.parent / "schemas" / "package-manifest.schema.json").as_uri() + "#"
SERVICES = (
    "testsite",
    "registry",
    "handler-runtime",
    "storage",
    "web-collector",
    "orchestrator",
    "llm",
    "assistant",
)
# The stack of this module: the runtime, the collector and the orchestrator use the REAL registry.
REGISTRY_ENV = {
    "JANE_E2E_RUNTIME_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_REGISTRY_RUNTIME_PROFILES": '["http://handler-runtime:8000/v1/info"]',
    "JANE_E2E_COLLECTOR_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_ORCHESTRATOR_EXTRA_EXECUTORS": "executors-registry.json",
}
TESTSITE_URL = f"{TESTSITE}/"  # the site as the services see it (assistant-search.json)
RUNNING = frozenset({"resolving", "sampling", "analyzing", "applying"})
SUCCESS = {"field": "result.status", "op": "eq", "value": "success"}


@dataclass
class Flows:
    stack: E2EStack
    clients: dict[str, JaneClient] = field(default_factory=dict)

    def __getitem__(self, service: str) -> JaneClient:
        if service not in self.clients:
            self.clients[service] = JaneClient(self.stack.url(service))
        return self.clients[service]


@pytest.fixture(scope="module")
def flows(stack: E2EStack) -> Iterator[Flows]:
    """An isolated stack of all services the assistant combines, with the real registry everywhere.

    ``stack`` (session) only checks Docker; this module never starts services in it. S-M2-06 runs first on the
    empty registry (so that no existing extractor is bound instead of generating one), then S-M2-07.
    """
    own = E2EStack(project=f"{default_project()}-assistant-{uuid.uuid4().hex[:6]}")
    own.env().update(REGISTRY_ENV)
    flows = Flows(own)
    try:
        if reasons := own.missing(SERVICES):
            pytest.skip("; ".join(reasons))
        own.ensure(*SERVICES)
        put_connections(flows["orchestrator"])
        yield flows
    finally:
        for client in flows.clients.values():
            client.close()
        if os.environ.get("JANE_E2E_KEEP") != "1":
            own.down(volumes=True)


# ---------------------------------------------------------------------------- helpers
def _key() -> str:
    return uuid.uuid4().hex


def note(scenario: str, what: str, value: Any = None) -> None:
    """One evidence line for the report (visible with ``pytest -s``)."""
    text = what if value is None else f"{what}: {json.dumps(value, ensure_ascii=False, sort_keys=True)}"
    print(f"[{scenario}] {text}", flush=True)


def poll(what: str, read: Any, done: Any, timeout_s: float = 900.0, poll_s: float = 1.0) -> Any:
    deadline = time.monotonic() + timeout_s
    while True:
        value = read()
        if done(value):
            return value
        if time.monotonic() > deadline:
            raise TimeoutError(f"{what}: not done after {timeout_s}s: {json.dumps(value)[:3000]}")
        time.sleep(poll_s)


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


def llm_usage(llm: JaneClient, **params: str) -> dict[str, Any]:
    r = llm.api("llm").get("/v1/usage", params=params)
    assert r.status_code == 200, r.text
    return dict(r.json())


def by_purpose(llm: JaneClient) -> dict[str, int]:
    rows = llm_usage(llm, group_by="purpose")["items"]
    return {str(row["purpose"]): int(row["requests"]) for row in rows}


def registry_version(registry: JaneClient, ref: dict[str, Any]) -> dict[str, Any]:
    r = registry.api("registry").get(f"/v1/packages/{ref['package_id']}/versions/{ref['version']}")
    assert r.status_code == 200, r.text
    return dict(r.json())


def registry_package(registry: JaneClient, package_id: str) -> tuple[dict[str, Any], str]:
    r = registry.api("registry").get(f"/v1/packages/{package_id}")
    assert r.status_code == 200, r.text
    return dict(r.json()), r.headers["etag"]


def archive_digest(registry: JaneClient, ref: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Digest of the canonical archive the registry serves, and the manifest inside it."""
    r = registry.api("registry").get(f"/v1/packages/{ref['package_id']}/versions/{ref['version']}/archive")
    assert r.status_code == 200, r.text
    digest = "sha256:" + hashlib.sha256(r.content).hexdigest()
    assert r.headers["etag"] == f'"{digest}"'
    with zipfile.ZipFile(io.BytesIO(r.content)) as archive:
        return digest, json.loads(archive.read("jane-package.json"))


def runtime_tests(runtime: JaneClient, ref: dict[str, Any]) -> dict[str, Any]:
    """Tests of a PUBLISHED version in the real runtime: the archive comes from the registry by reference
    (``handler.v1`` ``startTestRun`` without ``package_archive``), its digest is checked by the runtime."""
    body = {"handler": ref, "tests": "all", "limits": sandbox_limits()}
    r = runtime.api("handler").post("/v1/test-runs", json=body, headers={"Idempotency-Key": _key()})
    assert r.status_code == 202, r.text
    job = runtime.wait_job("handler", r.json()["job_id"])
    assert job["status"] == "succeeded", job
    return dict(job["result"])


def publish_fixture(
    registry: JaneClient, directory: Path, package_id: str, *, auto_changes_allowed: bool = True
) -> dict[str, Any]:
    """A human-written fixture package published to the real registry under a per-run id; returns the
    ``PackageVersion``. The manifest is checked against the contract schema first."""
    manifest = json.loads((directory / "jane-package.json").read_text(encoding="utf-8"))
    manifest["package_id"] = package_id
    spec("registry").validate_at(MANIFEST_SCHEMA, manifest, f"{directory.name}/jane-package.json")
    files: dict[str, dict[str, str]] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name != "jane-package.json" and "__pycache__" not in path.parts:
            files[path.relative_to(directory).as_posix()] = {
                "encoding": "base64",
                "data": base64.b64encode(path.read_bytes()).decode("ascii"),
            }
    created = registry.api("registry").post(
        "/v1/packages",
        json={
            "package_id": package_id,
            "kind": manifest["kind"],
            "title": manifest["title"],
            "auto_changes_allowed": auto_changes_allowed,
        },
        headers={"Idempotency-Key": _key()},
    )
    assert created.status_code == 201, created.text
    published = registry.api("registry").post(
        f"/v1/packages/{package_id}/versions",
        json={"manifest": manifest, "files": files},
        headers={"Idempotency-Key": _key()},
    )
    assert published.status_code == 201, published.text
    return dict(published.json())


def approve(registry: JaneClient, ref: dict[str, Any], reason: str) -> None:
    r = registry.api("registry").post(
        f"/v1/packages/{ref['package_id']}/versions/{ref['version']}/status",
        json={"status": "approved", "reason": reason},
        headers={"Idempotency-Key": _key()},
    )
    assert r.status_code == 200, r.text


def ref_of(version: dict[str, Any]) -> dict[str, Any]:
    return {k: version[k] for k in ("package_id", "version", "digest")}


def stage_handler(orch: JaneClient, task_id: str, stage_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get(f"/v1/tasks/{task_id}")
    assert r.status_code == 200, r.text
    (stage,) = [s for s in r.json()["stages"] if s["stage_id"] == stage_id]
    return dict(stage["handler"])


def activations(orch: JaneClient, task_id: str, stage_id: str) -> list[dict[str, Any]]:
    r = orch.api("orchestrator").get(f"/v1/tasks/{task_id}/stages/{stage_id}/activations")
    assert r.status_code == 200, r.text
    return list(r.json()["items"])


def problem_group(orch: JaneClient, source_id: str, package_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get("/v1/problem-groups", params={"source_id": source_id})
    assert r.status_code == 200, r.text
    (group,) = [g for g in r.json()["items"] if (g.get("package") or {}).get("package_id") == package_id]
    return dict(group)


def items_by_path(orch: JaneClient, run_id: str, stage_id: str, path_of: dict[str, str]) -> dict[str, Any]:
    return {path_of[i["material_id"]]: i for i in list_items(orch, run_id, stage_id)}


# ---------------------------------------------------------------------------- S-M2-06
# Entry pages of the site's sections: the user's crawl hint (OnboardingRequest.crawl_hints, a CollectorRules
# fragment - ТЗ §8 "правила обходу"). The sampling collection starts from them before the sitemap.
SECTION_PAGES = (
    "/",
    "/catalog/phones/",
    "/product/phone-alpha",
    "/news/",
    "/news/2026/autumn-sale",
    "/about",
    "/catalog/laptops/",
    "/product/laptop-one",
    "/news/2026/holiday-hours",
    "/pages/faq",
)


class SamplingStopsEarly(AssertionError):
    """The known WP-11 defect: the sample settles on one material type (see docs/delivery/WP-13.md)."""


def onboard_by_name(assistant: JaneClient, body: dict[str, Any]) -> dict[str, Any]:
    """``startOnboarding`` by the site NAME -> two search candidates -> the user picks the test site -> the
    session after adaptive sampling (real Web Collector), analysis and extractor preparation."""
    api = assistant.api("assistant")
    started = api.post("/v1/onboarding-sessions", json=body, headers={"Idempotency-Key": _key()})
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
    if sample["distinct_types"] < 2:
        raise SamplingStopsEarly(f"the sample has one material type: {sample} {session.get('analysis')}")
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
@pytest.mark.xfail(
    strict=True,
    raises=SamplingStopsEarly,
    reason=(
        "WP-11 defect: adaptive sampling stops after the first two materials of one type "
        "(sitemap products come first; Good-Turing coverage of n=2 is 1.0) - see docs/delivery/WP-13.md"
    ),
)
def test_s_m2_06_name_only_sample_distinguishes_material_types(flows: Flows) -> None:
    """Only the site's name (ТЗ §8): the sample must be diverse enough to tell the material types apart, and
    the extractor made from it must pass its tests. Runs before any package exists in the registry and stops
    before acceptance (publishes nothing)."""
    session = onboard_by_name(flows["assistant"], {"query": "testsite"})
    check_sample_and_proposals(session)


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
    hints = {"strategies": [{"type": "seed_list", "urls": [TESTSITE + p for p in SECTION_PAGES]}]}
    session = onboard_by_name(assistant, {"query": "testsite", "crawl_hints": hints})
    session_id = session["session_id"]
    check_sample_and_proposals(session)
    assert session["sample"]["distinct_types"] >= 4, session["sample"]
    proposals = session["proposals"]
    assert by_purpose(llm).get("onboarding", 0) > onboarding_before

    # ---- 3. the user accepts the recommended plan with activation, under its own source id
    proposal = next(p for p in proposals if p["recommended"])
    assert [s["type"] for s in proposal["collector_rules"]["strategies"]] == ["sitemap"], proposal
    source_id = f"e2e-{run_id}"
    accepted = api.post(
        f"/v1/onboarding-sessions/{session_id}/proposals/{proposal['proposal_id']}/acceptance",
        json={"activate": True, "source_id": source_id},
        headers={"Idempotency-Key": _key()},
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


# ---------------------------------------------------------------------------- S-M2-07
PRODUCT_URLS = {
    "/product/phone-alpha": "success",  # InStock
    "/product/phone-beta": "success",  # InStock
    "/product/phone-gamma": "unrecognized",  # OutOfStock: not handled by 1.0.0
    "/product/phone-zeta": "unrecognized",  # PreOrder: not handled by 1.0.0
}
PROBLEMS = ("/product/phone-gamma", "/product/phone-zeta")  # p1, p2 of the scripted fix (llm-seed.yaml)
SUCCESSES = ("/product/phone-alpha", "/product/phone-beta")


def samples_of(
    runtime: JaneClient, run_items: dict[str, Any], stored: dict[str, str], paths: tuple[str, ...]
) -> list[dict[str, Any]]:
    """``ProblemSample`` documents: the stored RAW by reference and the runtime's own ``HandlerResult``."""
    out = []
    for path in paths:
        item = run_items[path]
        r = runtime.api("handler").get(f"/v1/invocations/{item['invocation_id']}")
        assert r.status_code == 200, r.text
        result = r.json()
        sample: dict[str, Any] = {
            "material_ref": {"storage_connection_id": "raw-files", "object_id": stored[item["material_id"]]},
            "result": result,
        }
        if messages := (result.get("diagnostics") or {}).get("messages"):
            sample["diagnostics"] = messages
        out.append(sample)
    return out


def reprocess(
    orch: JaneClient, task_id: str, material_ids: list[str], since: str, reason: str
) -> dict[str, Any]:
    """``/v1/reprocessing`` of stored RAW from the extractor stage on. ``since`` keeps RAW stored by earlier
    scenarios on a reused stack out: material ids depend only on the URL, and the orchestrator filters the
    objects of the connection by ``material_ids`` only (not by the task's source - see WP-13.md)."""
    body = {
        "task_id": task_id,
        "stored_materials": {
            "storage_connection_id": "raw-files",
            "material_ids": material_ids,
            "since": since,
        },
        "from_stage": "extract-products",
        "reason": reason,
    }
    r = orch.api("orchestrator").post("/v1/reprocessing", json=body, headers={"Idempotency-Key": _key()})
    assert r.status_code == 202, r.text
    run = wait_run(orch, r.json()["job_id"])
    assert run["status"] == "succeeded", run
    return run


def improve(assistant: JaneClient, body: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    r = assistant.api("assistant").post(
        "/v1/improvement-runs", json=body, headers={"Idempotency-Key": _key()}
    )
    assert r.status_code == 202, r.text
    job = assistant.wait_job("assistant", r.json()["job_id"], timeout_s=600)
    assert job["status"] == "succeeded", job
    return str(job["job_id"]), dict(job["result"])


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
    package_id = f"e2e-{run_id}.improvable-product-extractor"
    v1 = publish_fixture(registry, IMPROVABLE, package_id)
    assert v1["manifest"]["provenance"]["created_by"] == "human"
    old = ref_of(v1)
    approve(registry, old, "e2e: human-written baseline")
    source_id = f"e2e-{run_id}"
    create_source(orch, source_id, change_policy={"llm_versions": "auto_after_checks"})
    task_id, recheck_id = f"e2e-{run_id}-catalog", f"e2e-{run_id}-recheck"
    create_task(orch, m1_task(task_id, source_id, [TESTSITE + p for p in PRODUCT_URLS], old))
    create_task(orch, m1_task(recheck_id, source_id, [TESTSITE + SUCCESSES[0]], old))

    # ---- 1. a real run: 1.0.0 does not recognise out-of-stock and pre-order cards -> a problem group
    first = wait_run(orch, start_run(orch, task_id))
    assert first["status"] == "succeeded", first
    stored_objects = objects_by_source(storage, "raw-files", source_id)
    stored = {o["material"]["material_id"]: o["object"]["object_id"] for o in stored_objects}
    path_of = {
        o["material"]["material_id"]: o["material"]["url"].removeprefix(TESTSITE) for o in stored_objects
    }
    assert set(path_of.values()) == set(PRODUCT_URLS), path_of
    mid = {p: m for m, p in path_of.items()}
    run1 = items_by_path(orch, first["run_id"], "extract-products", path_of)
    assert {p: i["result_status"] for p, i in run1.items()} == PRODUCT_URLS
    note("S-M2-07", "run 1 (1.0.0)", {p: i["result_status"] for p, i in sorted(run1.items())})
    group = problem_group(orch, source_id, package_id)
    note(
        "S-M2-07",
        "problem group",
        {k: group[k] for k in ("problem", "signature", "count", "status", "package")},
    )
    assert (group["problem"], group["signature"], group["count"]) == (
        "unrecognized",
        "unknown-availability",
        2,
    )
    assert group["package"]["version"] == "1.0.0" and group["status"] == "open", group
    assert {s["material_id"] for s in group.get("samples") or []} <= {mid[p] for p in PROBLEMS}, group

    # ---- 2. improvement run: the LLM fixes the code; old + new tests and every binding are checked
    request = {
        "package": {"package_id": package_id, "version": "1.0.0"},
        "source_id": source_id,
        "problem_group_id": group["group_id"],
        "problem_samples": samples_of(runtime, run1, stored, PROBLEMS),
        "successful_examples": samples_of(runtime, run1, stored, SUCCESSES),
        "policy": {"approval": "auto_after_checks", "allow_fork": True},
    }
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
        headers={"Idempotency-Key": _key()},
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
        headers={"Idempotency-Key": _key()},
    )
    assert refused.status_code == 403, refused.text
    assert refused.json()["code"] == "access_denied_by_policy", refused.json()
    assert refused.json()["details"]["reason"] == "package_auto_changes_forbidden", refused.json()
    assert stage_handler(orch, task_id, "extract-products") == old
    note(
        "S-M2-07", "auto_activate refused", {k: refused.json().get(k) for k in ("status", "code", "details")}
    )
