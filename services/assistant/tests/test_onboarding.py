"""End-to-end onboarding scenarios on the real assistant app with contract-bound fakes of neighbours.

«Готово, коли» (plan.md WP-11): new source -> proposals -> package -> tests.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from assistant_fakes import World
from assistant_fakes.base import FakeRequest, Reply
from assistant_fakes.runtime import PRODUCT_CODE_V1
from assistant_fakes.site import INJECTION, material, page, product

from jane_assistant.content import url_shape
from jane_assistant.packages import extractor_draft


def start(w: World, body: dict[str, Any], key: str = "onb-1") -> tuple[str, str]:
    r = w.api.post("/v1/onboarding-sessions", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202, r.text
    job = r.json()
    assert r.headers["Location"] == f"/v1/jobs/{job['job_id']}"
    return job["job_id"], job["labels"]["session_id"]


def session(w: World, session_id: str) -> dict[str, Any]:
    r = w.api.get(f"/v1/onboarding-sessions/{session_id}")
    assert r.status_code == 200
    return dict(r.json())


def seed_extractor(
    w: World,
    package_id: str = "catalog.product-extractor",
    code: str = PRODUCT_CODE_V1,
    domains: list[str] | None = None,
) -> None:
    draft = extractor_draft(
        package_id=package_id,
        version="1.2.0",
        title="Generic product cards",
        entity_type="product",
        key_fields=["sku"],
        entity_schema={"type": "object", "properties": {"sku": {"type": "string"}}},
        module_code=code,
        domains=domains or [],
        source_kind="web",
        media_types=["text/html"],
        job_id="seed",
        model={},
        reason="onboarding",
    )
    draft.manifest["provenance"] = {"created_by": "human"}
    w.registry.seed(draft.manifest, draft.files)


def test_new_source_by_name_to_proposals_package_and_tests(w: World) -> None:
    job_id, sid = start(w, {"query": "Shop Example kettles", "expected_entity_types": ["product"]})
    first = w.result(job_id, "OnboardingSession")
    assert first["status"] == "needs_disambiguation"
    assert [c["candidate_id"] for c in first["candidates"]] == ["cand_1", "cand_2"]
    assert w.llm.requests == []  # nothing sampled before the user chose

    missing = w.api.post(
        f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_9"}
    )
    assert missing.status_code == 404
    r = w.api.post(f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"})
    assert r.status_code == 200 and r.json()["status"] == "sampling"
    again = w.api.post(f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"})
    assert (
        again.status_code == 200 and again.json()["job_id"] == r.json()["job_id"]
    )  # same choice, same state
    s = w.result(r.json()["job_id"], "OnboardingSession")
    assert s["status"] == "proposals_ready", s
    assert s["sample"]["sufficient"] is True and s["sample"]["confidence"] >= 0.8
    # This small site has a singleton home type; the conservative coverage bound
    # needs every fetched page. The larger mixed-stream test below checks early LLM stop.
    assert s["sample"]["materials"] == len(next(iter(w.collector.collections.values()))["items"])
    assert {t["type"] for t in s["analysis"]["material_types"]} >= {"product", "category"}
    assert "llm_explore" not in s["analysis"]["discovery_methods"]  # only real discovery strategies
    assert "product" in {e["entity_type"] for e in s["analysis"]["entities"]}
    assert w.collector.cancelled, "the sampling collection is cancelled once the sample is sufficient"

    proposals = s["proposals"]
    assert len(proposals) == 2
    assert sum(p["recommended"] for p in proposals) == 1
    for p in proposals:
        rules = p["collector_rules"]
        assert rules["scope"]["allowed_domains"] == ["shop.example.test"]
        dumped = json.dumps(rules)
        assert "evil.example.org" not in dumped and "llm_explore" not in dumped
        assert rules["robots"] == {"mode": "respect"}
        assert p["cost"]["requests_per_run_estimate"] >= p["coverage"]["estimated_materials"]
        assert p["cost"]["llm_setup_cost"]["amount"] > 0
        ex = p["extractors"][0]
        assert ex["action"] == "create" and ex["entity_type"] == "product"
        assert ex["tested_on_samples"]["failed"] == 0 and ex["tested_on_samples"]["passed"] >= 2
    assert any("ignored model suggestion" in r for r in proposals[1]["risks"])

    # prompt injection in a product page never reaches instructions
    for req in w.llm.requests:
        assert "IGNORE ALL PREVIOUS" not in req["instructions"]
        assert req["scope"]["purpose"] == "onboarding"
    assert any(INJECTION[:40] in p.get("text", "") for req in w.llm.requests for p in req["data"])

    acc = w.api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
        json={"activate": False, "source_id": "shop-example"},
        headers={"Idempotency-Key": "acc-1"},
    )
    assert acc.status_code == 202
    result = w.result(acc.json()["job_id"], "AcceptanceResult")
    assert result["activated"] is False
    rules_ref = result["collector_rules"]
    assert rules_ref["package_id"] == "shop-example.web-rules"
    ext = result["extractors"][0]
    assert ext["action"] == "create" and ext["package"]["package_id"] == "shop-example.product-extractor"
    assert ext["test_report"]["failed"] == 0
    version = w.registry.versions["shop-example.product-extractor"]["1.0.0"]
    assert version["status"] == "draft" and version["test_status"] == "passed"
    manifest = version["manifest"]
    assert (
        manifest["provenance"]["created_by"] == "llm"
        and manifest["provenance"]["llm"]["reason"] == "onboarding"
    )
    statuses = {t["expected_status"] for t in manifest["tests"]}
    assert "success" in statuses and statuses & {"empty", "unrecognized"}
    assert result["source_draft"]["collector_rules"] == rules_ref
    assert result["source_draft"]["change_policy"] == {"llm_versions": "manual_approval"}
    task = result["task_drafts"][0]
    assert [s["kind"] for s in task["stages"]] == ["collect", "handler"]
    assert task["stages"][1]["bindings"] == [
        {"url_patterns": [{"type": "glob", "value": "shop.example.test/product/**"}]}
    ]
    assert w.orchestrator.sources == {} and w.orchestrator.tasks == {}  # user did not activate
    assert session(w, sid)["status"] == "completed"

    # replay of the same acceptance returns the same job
    replay = w.api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
        json={"activate": False, "source_id": "shop-example"},
        headers={"Idempotency-Key": "acc-1"},
    )
    assert (
        replay.headers.get("Idempotency-Replayed") == "true"
        and replay.json()["job_id"] == acc.json()["job_id"]
    )


def test_name_only_sampling_waits_for_types_beyond_first_streamed_products(w: World) -> None:
    """A slow collector must not make two early product pages look like the entire source."""

    def one_material_per_poll(req: FakeRequest) -> Reply:
        req.query["limit"] = "1"  # contract-valid long-poll page, as from a slow live collector
        return w.collector.materials(req)

    w.collector.app.on("listCollectionMaterials")(one_material_per_poll)
    job_id, sid = start(w, {"query": "Shop Example kettles", "expected_entity_types": ["product"]})
    first = w.result(job_id, "OnboardingSession")
    assert first["status"] == "needs_disambiguation"
    selected = w.api.post(
        f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"}
    )
    assert selected.status_code == 200
    result = w.result(selected.json()["job_id"], "OnboardingSession")

    collected = next(iter(w.collector.collections.values()))["items"]
    assert all("/product/" in item["locator"]["url"] for item in collected[:2])
    assert len(w.collector.app.called("listCollectionMaterials")) >= 10
    assert result["status"] == "proposals_ready", result
    assert result["sample"]["sufficient"] and result["sample"]["materials"] >= 10
    assert result["sample"]["distinct_types"] >= 2
    assert {t["type"] for t in result["analysis"]["material_types"]} >= {"product", "category"}
    assert result["proposals"][0]["extractors"][0]["tested_on_samples"]["passed"] >= 2
    assert w.violations() == []


def test_single_streamed_type_reports_insufficient_at_sample_budget(w: World) -> None:
    """High coverage from one early type is not enough when the collector still has more pages."""

    def only_products(req: FakeRequest) -> Reply:
        reply = w.collector.start(req)
        collection = next(iter(w.collector.collections.values()))
        collection["items"] = [
            material(
                f"https://shop.example.test/product/p-{i:02d}",
                product(f"P-{i:02d}", f"Product {i}", "100"),
            )
            for i in range(12)
        ]
        return reply

    w.collector.app.on("startCollection")(only_products)

    def one_material_per_poll(req: FakeRequest) -> Reply:
        req.query["limit"] = "1"
        return w.collector.materials(req)

    w.collector.app.on("listCollectionMaterials")(one_material_per_poll)
    job_id, _ = start(
        w,
        {"query": "https://shop.example.test/", "limits": {"max_onboarding_samples": 4}},
        key="single-type-bound",
    )
    result = w.result(job_id, "OnboardingSession")
    assert result["status"] == "insufficient_sample", result
    assert result["sample"]["materials"] == 4 and result["sample"]["distinct_types"] == 1
    fetched = len(next(iter(w.collector.collections.values()))["items"])
    assert result["sample"]["confidence"] == pytest.approx(0.9 * 4 / fetched, abs=1e-4)
    assert not result["sample"]["sufficient"]
    assert "max_onboarding_samples=4" in result["sample"]["message"]
    assert w.violations() == []


def test_name_only_sampling_finds_types_after_long_homogeneous_prefix(w: World) -> None:
    """Two early types do not prove diversity when the collector has later URL families."""

    def delayed_types(req: FakeRequest) -> Reply:
        reply = w.collector.start(req)
        collection = next(iter(w.collector.collections.values()))
        base = "https://shop.example.test"
        products = [
            material(f"{base}/product/p-{i:02d}", product(f"P-{i:02d}", f"Product {i}", "100"))
            for i in range(17)
        ]
        collection["items"] = [
            *products,
            material(f"{base}/news/1", page("article", "First article", "<p>News</p>")),
            material(f"{base}/news/2", page("article", "Second article", "<p>News</p>")),
            material(f"{base}/catalog/kettles/", page("category", "Kettles", "<p>List</p>")),
            material(f"{base}/catalog/toasters/", page("category", "Toasters", "<p>List</p>")),
            material(f"{base}/news/", page("news_list", "News", "<p>Index</p>")),
            material(f"{base}/news/page/2", page("news_list", "More news", "<p>Index</p>")),
            material(f"{base}/about", page("other", "About", "<p>About us</p>")),
            material(f"{base}/contact", page("other", "Contact", "<p>Call us</p>")),
        ]
        return reply

    def delayed_materials(req: FakeRequest) -> Reply:
        req.query["limit"] = "1" if req.query.get("after") else "18"
        return w.collector.materials(req)

    w.collector.app.on("startCollection")(delayed_types)
    w.collector.app.on("listCollectionMaterials")(delayed_materials)
    job_id, sid = start(w, {"query": "Shop Example kettles"}, key="delayed-types")
    first = w.result(job_id, "OnboardingSession")
    assert first["status"] == "needs_disambiguation", first
    selected = w.api.post(
        f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"}
    )
    assert selected.status_code == 200
    result = w.result(selected.json()["job_id"], "OnboardingSession")

    assert result["status"] == "proposals_ready", result
    assert result["sample"]["sufficient"]
    assert result["sample"]["materials"] < len(next(iter(w.collector.collections.values()))["items"])
    assert result["sample"]["distinct_types"] >= 4
    assert {t["type"] for t in result["analysis"]["material_types"]} >= {
        "product",
        "article",
        "category",
        "news_list",
        "other",
    }
    assert len(w.collector.app.called("listCollectionMaterials")) >= 8
    assert w.violations() == []


@pytest.mark.parametrize("sample_budget", [8, 60])
def test_same_url_shape_late_type_is_classified_or_insufficient(w: World, sample_budget: int) -> None:
    """News-list pages share the article URL shape and arrive after a confident first page."""

    def delayed_type(req: FakeRequest) -> Reply:
        reply = w.collector.start(req)
        collection = next(iter(w.collector.collections.values()))
        base = "https://shop.example.test"
        collection["items"] = [
            *[
                material(f"{base}/product/p-{i:02d}", product(f"P-{i:02d}", f"Product {i}", "100"))
                for i in range(4)
            ],
            *[
                material(f"{base}/news/{i}", page("article", f"Article {i}", "<p>Story</p>"))
                for i in range(1, 5)
            ],
            *[
                material(f"{base}/news/{i}", page("news_list", f"News list {i}", "<p>Index</p>"))
                for i in (5, 6)
            ],
        ]
        return reply

    def eight_then_rest(req: FakeRequest) -> Reply:
        if not req.query.get("after"):
            req.query["limit"] = "8"
        return w.collector.materials(req)

    w.collector.app.on("startCollection")(delayed_type)
    w.collector.app.on("listCollectionMaterials")(eight_then_rest)
    job_id, sid = start(
        w,
        {"query": "Shop Example kettles", "limits": {"max_onboarding_samples": sample_budget}},
        key=f"same-shape-{sample_budget}",
    )
    assert w.result(job_id, "OnboardingSession")["status"] == "needs_disambiguation"
    selected = w.api.post(
        f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_1"}
    )
    assert selected.status_code == 200
    result = w.result(selected.json()["job_id"], "OnboardingSession")

    items = next(iter(w.collector.collections.values()))["items"]
    assert url_shape(items[4]) == url_shape(items[8]) == url_shape(items[9])

    if sample_budget == 8:
        assert result["status"] == "insufficient_sample", result
        assert not result["sample"]["sufficient"]
        assert "max_onboarding_samples=8" in result["sample"]["message"]
    else:
        assert result["status"] == "proposals_ready", result
        assert result["sample"]["sufficient"]
        assert result["sample"]["materials"] == 10
        assert {t["type"] for t in result["analysis"]["material_types"]} >= {
            "product",
            "article",
            "news_list",
        }
        assert len(w.collector.app.called("listCollectionMaterials")) == 2
    assert w.violations() == []


def test_confident_sample_stays_insufficient_when_collection_never_ends(w: World) -> None:
    """A contract-valid stream that stalls cannot certify undiscovered material types."""

    def never_finished(req: FakeRequest) -> Reply:
        reply = w.collector.materials(req)
        reply.body["end_of_stream"] = False
        reply.body["collection_status"] = "running"
        return reply

    w.collector.app.on("listCollectionMaterials")(never_finished)
    job_id, _ = start(w, {"query": "https://shop.example.test/"}, key="never-finished")
    result = w.result(job_id, "OnboardingSession")

    assert result["status"] == "insufficient_sample", result
    fetched = len(next(iter(w.collector.collections.values()))["items"])
    assert result["sample"]["materials"] < fetched
    assert 0 < result["sample"]["confidence"] <= 0.9 * result["sample"]["materials"] / fetched
    assert not result["sample"]["sufficient"]
    assert "did not finish" in result["sample"]["message"]
    assert len(w.collector.app.called("listCollectionMaterials")) >= 30
    assert w.violations() == []


def test_existing_extractor_is_bound_and_auto_activation_creates_source_and_task(w: World) -> None:
    seed_extractor(w, domains=["shop.example.test"])
    job_id, _sid = start(
        w,
        {
            "query": "https://shop.example.test/",
            "expected_entity_types": ["product"],
            "auto_activation": True,
        },
    )
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "completed", s
    plan = s["proposals"][0]["extractors"][0]
    assert plan["action"] == "bind_existing"
    assert plan["package"] == {"package_id": "catalog.product-extractor", "version": "1.2.0"}
    assert plan["match_score"] == 1.0
    assert "generate_extractor" not in w.llm.steps()  # a ready extractor needs no code generation
    source = w.orchestrator.sources["shop.example.test"]
    assert source["change_policy"] == {"llm_versions": "auto_after_checks"}
    assert source["collector_rules"]["package_id"] == "shop.example.test.web-rules"
    task = w.orchestrator.tasks["shop.example.test-collect"]
    assert task["stages"][1]["handler"]["package_id"] == "catalog.product-extractor"
    assert w.registry.versions["shop.example.test.web-rules"]["1.0.0"]["status"] == "approved"


def test_partially_matching_extractor_is_forked_and_adapted(w: World) -> None:
    weak = PRODUCT_CODE_V1.replace("_TITLE = re.compile", "_UNUSED = 0\n_TITLE = re.compile").replace(
        'return {"status": "success"',
        'if fields["sku"] > "B":\n        return {"status": "empty", "entities": []}\n    return {"status": "success"',
    )
    seed_extractor(w, package_id="other.product-extractor", code=weak)
    w.llm.knobs.improve_code = PRODUCT_CODE_V1
    job_id, sid = start(w, {"query": "Shop Example store", "expected_entity_types": ["product"]})
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "proposals_ready", s
    plan = s["proposals"][0]["extractors"][0]
    assert plan["action"] == "fork", plan
    assert 0.5 <= plan["match_score"] < 0.9
    acc = w.api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
        json={},
        headers={"Idempotency-Key": "acc-f"},
    )
    result = w.result(acc.json()["job_id"], "AcceptanceResult")
    ref = result["extractors"][0]["package"]
    assert ref["package_id"] == "shop.example.test.product-extractor"
    published = w.registry.versions[ref["package_id"]][ref["version"]]["manifest"]
    assert published["fork_of"]["package_id"] == "other.product-extractor"
    assert w.registry.versions["other.product-extractor"]["1.2.0"]["manifest"]["entry"]  # parent untouched
    assert len(w.registry.versions["other.product-extractor"]) == 1


def test_insufficient_sample_is_reported_within_budget(w: World) -> None:
    job_id, _sid = start(w, {"query": "https://tiny.example.test/"})
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "insufficient_sample"
    assert s["sample"]["sufficient"] is False and s["sample"]["materials"] == 4
    assert "only 4" in s["sample"]["message"]
    assert s["costs"]["amount"] > 0
    assert "proposals" not in s


def test_sampling_stops_at_the_llm_budget(w: World) -> None:
    job_id, _ = start(
        w,
        {
            "query": "https://shop.example.test/",
            "limits": {"budget": {"amount": 0.005, "currency": "USD", "period": "run"}},
        },
    )
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "insufficient_sample"
    assert "budget" in s["sample"]["message"]


def test_sample_bound_comes_from_request_limits(w: World) -> None:
    job_id, _ = start(w, {"query": "https://shop.example.test/", "limits": {"max_onboarding_samples": 4}})
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "insufficient_sample"
    assert s["sample"]["materials"] == 4
    assert "max_onboarding_samples=4" in s["sample"]["message"]


def test_generated_code_with_forbidden_import_is_rejected_and_regenerated(w: World) -> None:
    w.llm.knobs.bad_code_first = True
    job_id, _ = start(w, {"query": "https://shop.example.test/", "expected_entity_types": ["product"]})
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "proposals_ready"
    assert w.llm.steps().count("generate_extractor") == 2
    retry = [r for r in w.llm.requests if r["output_schema"]["title"].endswith("generate_extractor.v1")][1]
    feedback = next(p for p in retry["data"] if p["name"] == "previous_attempt")
    assert "socket" in feedback["text"]
    assert s["proposals"][0]["extractors"][0]["tested_on_samples"]["failed"] == 0


def test_only_off_source_proposals_fall_back_to_safe_plan(w: World) -> None:
    w.llm.knobs.only_evil_proposals = True
    job_id, _ = start(w, {"query": "https://shop.example.test/", "expected_entity_types": ["product"]})
    s = w.result(job_id, "OnboardingSession")
    assert len(s["proposals"]) == 1
    p = s["proposals"][0]
    assert p["collector_rules"]["strategies"] == [
        {"type": "recursive", "seeds": ["https://shop.example.test/"]}
    ]
    assert "evil" not in json.dumps(p["collector_rules"])


def test_telegram_channel_onboarding(w: World) -> None:
    job_id, _ = start(w, {"query": "@city_events_example", "expected_entity_types": ["event"]})
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "proposals_ready", s
    assert s["analysis"]["source_kind"] == "telegram"
    assert [p["collector_rules"]["collector"] for p in s["proposals"]] == ["telegram", "telegram"]
    assert s["proposals"][0]["collector_rules"]["channels"] == [{"username": "city_events_example"}]
    assert w.tg_collector.app.called("startCollection")


def test_unknown_session_and_wrong_state(w: World) -> None:
    assert w.api.get("/v1/onboarding-sessions/onb_missing").status_code == 404
    job_id, sid = start(w, {"query": "https://tiny.example.test/"})
    w.wait(job_id)
    r = w.api.post(f"/v1/onboarding-sessions/{sid}/candidate-selection", json={"candidate_id": "cand_2"})
    assert r.status_code == 409
    r = w.api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance", json={}, headers={"Idempotency-Key": "x"}
    )
    assert r.status_code == 409


def test_invalid_request_limits_are_rejected(w: World) -> None:
    r = w.client.post(
        "/v1/onboarding-sessions",
        json={"query": "x", "limits": {"no_such_limit": 1}},
        headers={"Idempotency-Key": "bad"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "validation_failed"
