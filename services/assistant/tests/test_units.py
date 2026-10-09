"""Unit tests of the assistant's building blocks (no neighbours)."""

from __future__ import annotations

import asyncio
import json
from collections import Counter
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_assistant.clients import LlmClient
from jane_assistant.guards import SchemaValidator, check_code, sanitize_web_rules
from jane_assistant.llm import BudgetExhausted, InvalidModelOutput, LlmSession
from jane_assistant.packages import PackageDraft, bump, slug
from jane_assistant.sampling import Sample, coverage, pick_diverse
from jane_assistant.search import HttpJsonSearchProvider, StaticSearchProvider, direct_candidate
from jane_assistant.settings import LlmLimits, Settings, request_layer, resolve_service_limits
from jane_kit.clients import ServiceClient
from jane_kit.config import LimitError


def test_good_turing_coverage() -> None:
    assert coverage(Counter(), 2) == 0.0
    assert coverage(Counter({"a": 1, "b": 1, "c": 1}), 2) == 0.0  # only singletons: nothing is known
    assert coverage(Counter({"a": 5, "b": 4, "c": 1}), 2) == pytest.approx(0.9)
    assert coverage(Counter({"a": 2, "b": 2}), 3) == 0.0  # stricter min_examples_per_type


def test_pick_diverse_round_robins_over_shapes() -> None:
    reserve = [Sample({}, "", s) for s in ["p", "p", "p", "c", "c", "n"]]
    batch = pick_diverse(reserve, Counter({"p": 1}), 4)
    assert [s.shape for s in batch] == ["c", "n", "p", "c"]


def test_sanitize_rules_keeps_only_the_source() -> None:
    proposal = {
        "strategies": [
            {
                "type": "sitemap",
                "urls": ["https://shop.example.test/sitemap.xml", "https://evil.test/s.xml"],
                "limits": {"crawl": {"max_depth": 99}},
            },
            {"type": "llm_explore"},
            {
                "type": "api_feed",
                "url": "https://evil.test/api",
                "items_path": "$.items",
                "url_path": "$.url",
            },
            {
                "type": "recursive",
                "seeds": ["https://cdn.shop.example.test/"],
                "follow": ["shop.example.test/product/**", "evil.test/**"],
            },
        ],
        "sections": [
            {"section_id": "Product", "patterns": ["shop.example.test/product/**"]},
            {"section_id": "x", "patterns": ["*.test/**"]},
        ],
        "exclude": ["shop.example.test/cart/**", "evil.test/**"],
    }
    check = sanitize_web_rules(proposal, ["shop.example.test"], {"scope": {"include_subdomains": True}})
    rules = check.rules
    assert rules is not None
    assert rules["strategies"] == [
        {"type": "sitemap", "urls": ["https://shop.example.test/sitemap.xml"]},
        {
            "type": "recursive",
            "seeds": ["https://cdn.shop.example.test/"],
            "follow": [{"type": "glob", "value": "shop.example.test/product/**"}],
        },
    ]
    assert rules["scope"] == {
        "allowed_domains": ["shop.example.test"],
        "include_subdomains": True,
        "exclude": [{"type": "glob", "value": "shop.example.test/cart/**"}],
    }
    assert rules["sections"] == [
        {"section_id": "product", "patterns": [{"type": "glob", "value": "shop.example.test/product/**"}]}
    ]
    assert rules["robots"] == {"mode": "respect"}
    assert any("llm_explore" in r for r in check.rejected) and any("api_feed" in r for r in check.rejected)
    assert (
        sanitize_web_rules(
            {"strategies": [{"type": "seed_list", "urls": ["https://evil.test/"]}]}, ["shop.example.test"]
        ).rules
        is None
    )


def test_rules_and_manifests_validate_against_contract_schemas(contracts: Path) -> None:
    v = SchemaValidator.locate(contracts)
    assert v.available
    rules = sanitize_web_rules({"strategies": [{"type": "sitemap"}]}, ["shop.example.test"]).rules
    assert v.errors("collector-rules.schema.json", rules) == []
    assert v.errors("collector-rules.schema.json", {"collector": "web"})


def test_check_code() -> None:
    ok = check_code("import re\n\ndef extract(material, params, ctx):\n    return {}\n", "extract", ["re"])
    assert ok.ok
    bad = check_code(
        "import socket\nfrom os import path\n\ndef run():\n    eval('1')\n    return ().__class__\n",
        "extract",
        ["re"],
    )
    assert not bad.ok
    assert len(bad.problems) == 5
    assert not check_code("def extract(:\n", "extract", []).ok


def test_package_draft_archive_is_deterministic_and_has_tests() -> None:
    d = PackageDraft({"package_id": "a.b", "version": "1.0.0", "tests": []}, {"src/m/main.py": b"x"})
    mat = {
        "material_id": "web:1",
        "source": {"kind": "web"},
        "content": {"kind": "inline", "data": "<p>", "encoding": "utf-8", "media_type": "text/html"},
        "extra": 1,
    }
    name = d.add_test(
        "my case!",
        mat,
        "success",
        [{"entity_type": "t", "fields": {"a": 1}, "observation": {}}],
        "problem_sample",
    )
    again = d.add_test("my case!", mat, "empty", None, "llm")
    assert (name, again) == ("my-case", "my-case-2")
    assert json.loads(d.files["tests/my-case/expected.json"]) == {
        "entities": [{"entity_type": "t", "fields": {"a": 1}}]
    }
    assert "extra" not in json.loads(d.files["tests/my-case/material.json"])
    assert d.archive() == d.copy().archive()
    body = d.publish_body()
    assert "jane-package.json" not in body["files"] and body["manifest"]["tests"][0]["compare"] == "subset"
    assert (
        bump("1.2.3", "patch") == "1.2.4"
        and bump("1.2.3", "minor") == "1.3.0"
        and bump("1.2.3", "major") == "2.0.0"
    )
    assert slug("Shop.Example.TEST") == "shop.example.test" and slug("@@") == "source"


def test_search_providers(tmp_path: Path) -> None:
    assert direct_candidate("https://shop.example.test/x", None).url == "https://shop.example.test/x"  # type: ignore[union-attr]
    assert direct_candidate("@city_events", None).telegram_username == "city_events"  # type: ignore[union-attr]
    assert direct_candidate("t.me/city_events", None).source_kind == "telegram"  # type: ignore[union-attr]
    assert direct_candidate("Shop Example", None) is None
    f = tmp_path / "sources.json"
    f.write_text(
        json.dumps(
            [
                {"title": "Shop Example", "url": "https://shop.example.test/", "aliases": ["kettles"]},
                {"title": "City events", "telegram_username": "city_events_example"},
            ]
        ),
        encoding="utf-8",
    )
    static = StaticSearchProvider.from_file(f)
    found = asyncio.run(static.search("shop example kettles", None, 5))
    assert [c.title for c in found] == ["Shop Example", "City events"]
    assert found[0].confidence == pytest.approx(0.8) and found[1].confidence < 0.3
    assert asyncio.run(static.search("shop kettles", "telegram", 5)) == []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["q"] == "shop example"
        return httpx.Response(
            200, json={"data": {"hits": [{"name": "Shop Example", "link": "https://shop.example.test/"}]}}
        )

    http = HttpJsonSearchProvider(
        "https://search.test/?q={query}",
        items_path="data.hits",
        title_field="name",
        url_field="link",
        http=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    hits = asyncio.run(http.search("shop example", None, 5))
    assert hits[0].url == "https://shop.example.test/"


def test_limits_resolution_and_hard_caps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__HARD_CAPS__LLM__MAX_IMPROVEMENT_ATTEMPTS", "2")
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__LLM__MIN_ONBOARDING_CONFIDENCE", "0.7")
    resolved = resolve_service_limits(
        Settings(), *request_layer({"max_improvement_attempts": 5, "max_onboarding_samples": 10})
    )
    assert resolved.limits.llm.max_improvement_attempts == 2  # clamped by the platform hard cap
    assert resolved.limits.llm.max_onboarding_samples == 10
    assert (
        resolved.limits.llm.min_onboarding_confidence == 0.7
    )  # contract llm.min_onboarding_confidence (R08)
    asked = resolve_service_limits(Settings(), *request_layer({"min_onboarding_confidence": 0.95}))
    assert asked.limits.llm.min_onboarding_confidence == 0.95  # a request may ask for a stricter sample
    assert resolved.provenance()["llm.max_improvement_attempts"] == "hard_cap"
    with pytest.raises(LimitError):
        resolve_service_limits(Settings(), *request_layer({"unknown": 1}))
    info = resolve_service_limits(Settings()).platform_limits()
    assert info["defaults"]["llm"]["budget"] == {"amount": 2.0, "currency": "USD", "period": "run"}
    assert info["defaults"]["llm"]["min_onboarding_confidence"] == 0.7  # visible in /v1/info


def _llm_session(responder: Any, **limits: Any) -> LlmSession:
    transport = httpx.MockTransport(responder)
    client = LlmClient(ServiceClient("http://llm.test", transport=transport))
    return LlmSession(client, LlmLimits(**limits), "onboarding", "job_1")


def _completion(output: Any, cost: float = 0.4, valid: bool = True) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "completion_id": "c1",
            "model": {"provider_id": "p", "model_id": "m"},
            "output": output,
            "valid": valid,
            "usage": {"input_tokens": 1, "output_tokens": 1, "cost": {"amount": cost, "currency": "USD"}},
        },
    )


def test_llm_session_budget_truncation_and_validation() -> None:
    seen: list[dict[str, Any]] = []

    def responder(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return _completion({"x": 1})

    llm = _llm_session(
        responder, max_input_tokens_per_request=10, budget={"amount": 1, "currency": "USD", "period": "run"}
    )
    schema = {"type": "object", "required": ["x"], "properties": {"x": {"type": "integer"}}}
    data = [{"name": "a", "text": "y" * 100}, {"name": "b", "text": "z"}]
    assert asyncio.run(llm.ask("s", "do it", data, schema, model="cheap")) == {"x": 1}
    assert len(seen[0]["data"]) == 1 and seen[0]["data"][0]["text"].startswith("y" * 40)
    # R13: the whole run budget and the run id - the gateway counts the run itself (not "what is left")
    assert seen[0]["limits"]["budget"] == {"amount": 1, "currency": "USD", "period": "run"}
    assert seen[0]["scope"] == {"purpose": "onboarding", "run_id": "job_1"}
    assert "mode" not in seen[0]  # sync by default
    asyncio.run(llm.ask("s", "do it", [], schema, model="cheap"))
    asyncio.run(llm.ask("s", "do it", [], schema, model="cheap"))
    assert seen[-1]["limits"]["budget"]["amount"] == 1
    assert llm.spent == pytest.approx(1.2) and llm.exhausted
    with pytest.raises(BudgetExhausted):
        asyncio.run(llm.ask("s", "do it", [], schema, model="cheap"))
    assert len(seen) == 3

    bad = _llm_session(lambda r: _completion({"x": "not int"}))
    with pytest.raises(InvalidModelOutput):
        asyncio.run(bad.ask("s", "i", [], schema, model="m"))
    invalid = _llm_session(lambda r: _completion(None, valid=False))
    with pytest.raises(InvalidModelOutput):
        asyncio.run(invalid.ask("s", "i", [], schema, model="m"))
    gateway = _llm_session(
        lambda r: httpx.Response(
            429,
            json={
                "type": "urn:jane:problem:budget_exhausted",
                "title": "t",
                "status": 429,
                "code": "budget_exhausted",
                "retryable": False,
            },
        )
    )
    with pytest.raises(BudgetExhausted):
        asyncio.run(gateway.ask("s", "i", [], schema, model="m"))


def test_session_document_roundtrip_and_optimistic_version() -> None:
    from jane_assistant.onboarding import ExtractorPlan, InMemorySessionStore, Session
    from jane_assistant.sampling import SampleResult
    from jane_assistant.search import Candidate
    from jane_assistant.testing import TestOutcome

    draft = PackageDraft(
        {"package_id": "a.b", "version": "1.0.0", "tests": []}, {"src/m/main.py": b"\x00code"}
    )
    sample = SampleResult(
        [Sample({"material_id": "web:1"}, "text", "t/*", "product", 0.9)], 0.9, True, None, {"k": 1}
    )
    plan = ExtractorPlan(
        "product",
        "product",
        "create",
        {"package_id": "a.b", "version": "1.0.0"},
        0.4,
        TestOutcome("ctx", {"passed": 1, "failed": 0}),
        draft,
    )
    s = Session(
        "onb_1",
        "q",
        {"query": "q"},
        candidates=[Candidate("T", url="https://t.test/", confidence=0.5)],
        selected_candidate_id="cand_1",
        sample=sample,
        plans={"product": plan},
    )
    back = Session.from_doc(json.loads(json.dumps(s.to_doc())), 3)
    assert back.to_doc() == s.to_doc() and back.version == 3
    assert back.plans["product"].draft is not None and back.plans["product"].draft.files == draft.files
    assert back.candidate() == s.candidate()

    store = InMemorySessionStore()
    assert asyncio.run(store.save_if(s, 0)) and s.version == 1
    stale = asyncio.run(store.get("onb_1"))
    assert stale is not None
    s.status = "sampling"
    assert asyncio.run(store.save_if(s, 1)) and s.version == 2
    stale.status = "cancelled"
    assert not asyncio.run(store.save_if(stale, stale.version))  # lost the race: nothing written
    current = asyncio.run(store.get("onb_1"))
    assert current is not None and current.status == "sampling"
