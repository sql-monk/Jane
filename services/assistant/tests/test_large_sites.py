"""Onboarding of large real-world sites on the real assistant app with contract-bound fakes of neighbours.

A shop category looks the same everywhere: hundreds of filter links inside the category (an effectively
unbounded crawl space), pages of 0.5-3 MB whose structured data (JSON-LD ``ItemList``) starts far beyond the
first kilobytes, and pagination pages 2..N that declare page 1 as their ``rel=canonical``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from assistant_fakes import World, world
from assistant_fakes.base import FakeRequest, Reply
from assistant_fakes.runtime import LISTING_JSONLD_CODE
from assistant_fakes.site import listing_page, material, page

from jane_assistant.settings import LlmCallLimits, LlmLimits, MaterialLimits, OnboardingLimits

HOST = "laptops.example.test"
BASE = f"https://{HOST}/catalog/laptops/c1234/"
FILTERS = [f"{BASE}producer=brand{i}/" for i in range(300)]
PAGES = [f"{BASE}page={n}/" for n in range(2, 6)]
HINTS: dict[str, Any] = {
    "collector": "web",
    "scope": {
        "allowed_domains": [HOST],
        "allowed_schemes": ["https"],
        "path_prefixes": ["/catalog/laptops/c1234/"],
    },
    "strategies": [{"type": "listing", "strategy_id": "laptops", "start_urls": [BASE]}],
    "robots": {"mode": "respect"},
    "limits": {"crawl": {"max_pages_per_run": 60, "max_depth": 10}},
}


def _products(n: int) -> list[tuple[str, str, int]]:
    return [
        (
            f"Laptop {n}-{k} 15.6 IPS / 16 GB",
            f"https://{HOST}/laptop-{n}-{k}/p{100000 + n * 100 + k}/",
            20_000 + k,
        )
        for k in range(20)
    ]


def _category_site(w: World) -> None:
    """Page 1, then filter pages (each a category page of its own) with the pagination pages among them;
    the collector honours the sampling request's page budget and reports the whole crawl space."""
    order = [BASE, *FILTERS[:4], PAGES[0], PAGES[1], *FILTERS[4:], *PAGES[2:]]
    nav = [*FILTERS[:12], *PAGES[:3], f"{BASE}page=67/"]

    def start(req: FakeRequest) -> Reply:
        reply = w.collector.start(req)
        collection = next(iter(w.collector.collections.values()))
        bound = req.json["limits"]["crawl"]["max_pages_per_run"]
        collection["items"] = [
            material(url, listing_page(BASE if url in PAGES else url, _products(i), nav), strategy="listing")
            for i, url in enumerate(order[:bound])
        ]
        collection["discovered"] = len(order)
        return reply

    w.collector.app.on("startCollection")(start)


def _start(w: World, body: dict[str, Any], key: str) -> tuple[str, str]:
    r = w.api.post("/v1/onboarding-sessions", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202, r.text
    return r.json()["job_id"], r.json()["labels"]["session_id"]


def _requests(w: World, step: str) -> list[dict[str, Any]]:
    return [r for r in w.llm.requests if r["output_schema"]["title"] == f"jane.assistant.{step}.v1"]


def _data_chars(request: dict[str, Any]) -> int:
    """Characters of a model request as the gateway estimates them (instructions, preamble, delimiters, data)."""
    call = LlmCallLimits()
    parts = sum(
        len(p["text"]) + call.part_overhead_chars + len(p["name"]) + len(p.get("media_type", ""))
        for p in request["data"]
    )
    return len(request["instructions"]) + call.prompt_overhead_chars + parts


def test_large_shop_category_is_sampled_analysed_and_proposed(w: World) -> None:
    _category_site(w)
    w.llm.knobs.listing_entities = True
    w.llm.knobs.generate_code = LISTING_JSONLD_CODE
    w.llm.knobs.proposals = [
        {
            "title": "First pages of the category",
            "recommended": True,
            "strategies": [{"type": "seed_list", "urls": [BASE, PAGES[0], PAGES[1]]}],
            "sections": [{"section_id": "laptops", "patterns": [f"{HOST}/catalog/laptops/c1234/**"]}],
        },
        {
            "title": "Every page of the category",
            "strategies": [
                {"type": "recursive", "seeds": [BASE], "follow": [f"{HOST}/catalog/laptops/c1234/page=*"]}
            ],
        },
        {"title": "Sitemap", "strategies": [{"type": "sitemap", "urls": [f"https://{HOST}/sitemap.xml"]}]},
    ]
    job_id, sid = _start(
        w,
        {
            "query": BASE,
            "source_kind": "web",
            "expected_entity_types": ["laptop"],
            "crawl_hints": HINTS,
            "limits": {"max_onboarding_samples": 20, "min_onboarding_confidence": 0.8},
        },
        "large-category",
    )
    s = w.result(job_id, "OnboardingSession")
    assert s["status"] == "proposals_ready", s

    # Sampling: only the user's strategy inside the user's scope, the user's crawl limits, pages as served.
    request = next(iter(w.collector.collections.values()))["request"]
    assert request["rules"]["strategies"] == HINTS["strategies"]
    assert request["rules"]["scope"] == {
        "allowed_domains": [HOST],
        **{k: HINTS["scope"][k] for k in ("allowed_schemes", "path_prefixes")},
    }
    assert request["rules"]["dedup"] == {"use_link_rel_canonical": False}
    assert request["limits"] == {"crawl": {"max_pages_per_run": 60, "max_depth": 10}}

    # The crawl space is unbounded (filters); the collector stopped at the page budget. That is a finished
    # stream: the sample is sufficient for those pages and says so.
    sample = s["sample"]
    assert sample["sufficient"] is True and sample["confidence"] >= 0.8
    assert sample["materials"] <= 20 and sample["distinct_types"] == 1
    assert (
        "max_pages_per_run=60" in sample["message"]
        and f"of {1 + len(FILTERS) + len(PAGES)} discovered" in sample["message"]
    )

    # The model sees the JSON-LD although it starts beyond max_sample_chars of the raw page, and every
    # request fits the gateway's estimate of llm.max_input_tokens_per_request.
    raw = listing_page(BASE, _products(0), [])
    assert raw.index("application/ld+json") > OnboardingLimits().max_sample_chars
    budget = int(LlmLimits().max_input_tokens_per_request * LlmCallLimits().chars_per_token)
    classify = _requests(w, "classify")
    assert classify
    for req in classify:
        assert _data_chars(req) <= budget
        for p in req["data"]:
            assert "[HTML digest of a" in p["text"] and '"@type":"ItemList"' in p["text"]
            assert "more item(s), 20 in total on the page" in p["text"]  # the list is shortened, not cut
            assert "window.__STATE__" not in p["text"]
    for step in ("analyze", "generate_extractor", "propose"):
        assert all(_data_chars(req) <= budget for req in _requests(w, step)), step

    # Analysis gets the user's entity type and the discovery evidence of the full pages.
    context = json.loads(
        next(p["text"] for p in _requests(w, "analyze")[0]["data"] if p["name"] == "context")
    )
    assert context["expected_entity_types"] == ["laptop"]
    hints = context["hints"]
    assert [p["template"] for p in hints["pagination"]] == [f"{BASE}page={{n}}/"]
    assert hints["pagination"][0]["max_page_seen"] == 67
    assert hints["canonical"]["declared_elsewhere"] == 2 and hints["canonical"]["different_content"] == 2
    assert hints["truncated"]["max_pages_per_run"] == 60
    assert hints["discovery_bounded_by_crawl_hints"] is True
    assert {"entity_type": "laptop"}.items() <= s["analysis"]["entities"][0].items()

    # A new extractor for the laptops listed on category pages; one material type only, so the negative
    # example is the empty shell of a sampled page.
    generate = _requests(w, "generate_extractor")[0]
    negative = next(p["text"] for p in generate["data"] if p["name"] == "neg_0")
    assert "<body></body>" in negative and "ld+json" not in negative
    plan = s["proposals"][0]["extractors"][0]
    assert plan["entity_type"] == "laptop" and plan["action"] == "create"
    assert plan["tested_on_samples"]["failed"] == 0 and plan["tested_on_samples"]["passed"] >= 4

    # Proposals keep the user's scope; plans that list or follow pagination pages do not treat rel=canonical
    # as a duplicate signal (page 2..N declare page 1), a plan that does not keeps it and names the risk.
    p1, p2, p3 = s["proposals"]
    for p in (p1, p2, p3):
        assert p["collector_rules"]["scope"]["path_prefixes"] == ["/catalog/laptops/c1234/"]
        assert p["collector_rules"]["scope"]["allowed_schemes"] == ["https"]
    assert p1["recommended"] and p1["collector_rules"]["dedup"] == {"use_link_rel_canonical": False}
    assert p1["coverage"]["estimated_materials"] == 3 and "exactly the 3 listed" in p1["coverage"]["notes"]
    assert any("rel=canonical is not used for dedup" in r for r in p1["risks"])
    # the extractor was tested on reduced copies (the full pages do not fit an inline test run): stated, and the
    # model was told the real pages also contain the removed scripts
    assert any("tested on reduced copies of" in r and "not on the full pages" in r for r in p1["risks"])
    assert "reduced copies of the real pages" in generate["instructions"]
    assert p2["collector_rules"]["dedup"] == {"use_link_rel_canonical": False}
    assert any("pagination pages" in r for r in p2["risks"])
    assert p2["coverage"]["estimated_materials"] == 60  # a run fetches at most the user's 60 pages
    assert "dedup" not in p3["collector_rules"]
    assert any("declare another page canonical" in r for r in p3["risks"])

    acc = w.api.post(
        f"/v1/onboarding-sessions/{sid}/proposals/p1/acceptance",
        json={"activate": False, "source_id": "laptops-example"},
        headers={"Idempotency-Key": "acc-large"},
    )
    assert acc.status_code == 202
    result = w.result(acc.json()["job_id"], "AcceptanceResult")
    task = result["task_drafts"][0]
    assert task["limits"] == HINTS["limits"]  # the user's crawl limits go to the task (rules carry none)
    version = w.registry.versions["laptops-example.laptop-extractor"]["1.0.0"]
    fixture = json.loads(version["files"]["tests/sample-0/material.json"])
    content = fixture["content"]
    assert content["size_bytes"] == len(content["data"].encode()) <= MaterialLimits().max_fixture_bytes
    assert "ItemList" in content["data"] and "window.__STATE__" not in content["data"]
    assert fixture["revision"]["content_sha256"] == content["sha256"]
    assert w.violations() == []


WORDS = [
    "alpha",
    "bravo",
    "charlie",
    "delta",
    "echo",
    "foxtrot",
    "golf",
    "hotel",
    "india",
    "juliett",
    "kilo",
    "lima",
    "mike",
    "november",
    "oscar",
    "papa",
    "quebec",
    "romeo",
    "sierra",
    "tango",
]


@pytest.mark.parametrize("tail", ["one_known", "long_known", "new_shape", "late_type"])
def test_sample_budget_reached_before_the_stream_ends_counts_the_tail_as_unknown(w: World, tail: str) -> None:
    """Confident at the sample budget while the collection still runs: the rest is read, never classified, so
    its whole share is unknown-type risk whatever its URL shapes. Only a short tail keeps the sample sufficient;
    a late type under already represented shapes (``late_type``, the review's repro: 40 product pages after 20
    category pages) is not hidden."""
    base = "https://drain.example.test"
    later = {
        "one_known": [("category", f"{base}/alpha/2")],
        "long_known": [("category", f"{base}/{word}/2") for word in WORDS[:15]],
        "new_shape": [("category", f"{base}/zulu/1")],
        "late_type": [("product", f"{base}/{WORDS[i % 20]}/{100 + i}") for i in range(40)],
    }[tail]

    def start(req: FakeRequest) -> Reply:
        reply = w.collector.start(req)
        collection = next(iter(w.collector.collections.values()))
        first = [("category", f"{base}/{word}/1") for word in WORDS]
        collection["items"] = [
            material(url, page(kind, f"Page {url}", "<p>Content</p>")) for kind, url in [*first, *later]
        ]
        return reply

    def one_per_poll(req: FakeRequest) -> Reply:
        req.query["limit"] = "1"
        return w.collector.materials(req)

    w.collector.app.on("startCollection")(start)
    w.collector.app.on("listCollectionMaterials")(one_per_poll)
    job_id, _ = _start(w, {"query": f"{base}/", "limits": {"max_onboarding_samples": 20}}, f"drain-{tail}")
    s = w.result(job_id, "OnboardingSession")

    assert s["sample"]["materials"] == 20
    assert len(_requests(w, "classify")) == 20  # one novel URL shape per poll, nothing after the budget
    polls = len(w.collector.app.called("listCollectionMaterials"))
    if tail == "one_known":
        assert s["status"] == "proposals_ready", s
        assert s["sample"]["sufficient"] is True
        # 1 unclassified of 21: unseen = max(min(1/21, 1 - 0.1^(1/20)), 1/21) - the tail counts in full
        assert s["sample"]["confidence"] == pytest.approx(0.9 * (1 - 1 / 21), abs=1e-4)
        assert polls >= 21
    elif tail == "new_shape":
        assert s["status"] == "insufficient_sample", s
        assert (
            "not represented" in s["sample"]["message"]
            and "drain.example.test/zulu/*" in s["sample"]["message"]
        )
    else:
        assert s["status"] == "insufficient_sample", s
        assert not s["sample"]["sufficient"] and "analysis" not in s
        assert "later material(s) could not be classified" in s["sample"]["message"]
        # it stops reading as soon as the tail alone makes the threshold unreachable: 0.9 * (1 - 3/23) < 0.8
        assert "3 later material(s)" in s["sample"]["message"] and polls == 23
    assert w.violations() == []


@pytest.mark.parametrize("larger", [False, True])
def test_truncation_is_reported_only_when_the_crawl_space_is_larger(w: World, larger: bool) -> None:
    """A stream that ends exactly at the page budget is not truncated unless more URLs were discovered."""

    def start(req: FakeRequest) -> Reply:
        reply = w.collector.start(req)
        collection = next(iter(w.collector.collections.values()))
        if larger:
            collection["discovered"] = len(collection["items"]) + 1
        return reply

    w.collector.app.on("startCollection")(start)
    pages = 16  # the fake shop: exactly the page budget of the hint
    job_id, _ = _start(
        w,
        {
            "query": "https://shop.example.test/",
            "crawl_hints": {"limits": {"crawl": {"max_pages_per_run": pages}}},
        },
        f"truncation-{larger}",
    )
    s = w.result(job_id, "OnboardingSession")
    request = next(iter(w.collector.collections.values()))["request"]
    assert request["limits"] == {"crawl": {"max_pages_per_run": pages}}
    assert len(next(iter(w.collector.collections.values()))["items"]) == pages
    assert s["sample"]["sufficient"] is True, s
    if larger:
        assert f"({pages} fetched of {pages + 1} discovered URL(s))" in s["sample"]["message"]
    else:
        assert "message" not in s["sample"]
    assert w.violations() == []


def test_generated_package_over_the_inline_limit_leaves_the_plan_untested(
    contracts: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A draft whose fixtures exceed transfer.inline_max_bytes cannot be test-run: the session still ends with
    proposals (the extractor's risk says it failed its tests) instead of a failed job."""
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__TRANSFER__INLINE_MAX_BYTES", "1024")
    with world(contracts) as w:
        job_id, _ = _start(
            w, {"query": "https://shop.example.test/", "expected_entity_types": ["product"]}, "tiny"
        )
        s = w.result(job_id, "OnboardingSession")
        assert s["status"] == "proposals_ready", s
        plan = s["proposals"][0]["extractors"][0]
        assert plan["action"] == "create" and "tested_on_samples" not in plan
        assert "extractor for product failed its tests on samples" in s["proposals"][0]["risks"]
        assert not w.handler.app.called("startTestRun")
        assert w.violations() == []
