"""Unit tests of large-page handling: reduction, digests, evidence, URL shapes and the plan decisions built on them."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest
from assistant_fakes.site import listing_page, material
from pydantic import ValidationError

from jane_assistant.content import url_shape
from jane_assistant.material import (
    declared_canonical,
    empty_shell,
    html_digest,
    lean_html,
    link_pattern,
    material_text,
    outside_blocks,
    page_links,
    pagination_templates,
    reduce_material,
    same_url,
)
from jane_assistant.onboarding import _canonical_dedup, _estimate
from jane_assistant.sampling import sampling_rules
from jane_assistant.settings import MaterialLimits, OnboardingLimits

BASE = "https://shop.example.test/catalog/c80004/"
URL = OnboardingLimits().max_risk_url_chars
PRODUCTS = [(f"Laptop {k}", f"https://shop.example.test/laptop-{k}/p{1000 + k}/", 100 + k) for k in range(60)]


def _ld(page: str) -> list[Any]:
    start = page.index('<script type="application/ld+json">') + len('<script type="application/ld+json">')
    return [json.loads(page[start : page.index("</script>", start)])]


def test_lean_html_keeps_structured_data_and_markup_drops_code() -> None:
    page = listing_page(BASE, PRODUCTS, [f"{BASE}page=2/"])
    lean = lean_html(page, 64_000)
    assert len(lean.encode()) <= 64_000 < len(page.encode())
    assert "window.__STATE__" not in lean and "<style>" not in lean and "<svg>" not in lean
    assert _ld(lean) == _ld(page)  # the JSON-LD is kept whole
    tiles = page[page.index("<main>") :]
    assert tiles in lean  # everything kept is byte-identical to the page

    tight = lean_html(page, 16_000)  # the body is cut at a tag; the JSON-LD block stays whole
    assert len(tight.encode()) <= 16_000
    assert _ld(tight) == _ld(page) and tight.endswith("</body></html>")
    assert '<div class="tile"><a href="https://shop.example.test/laptop-59/p1059/">' not in tight
    assert tight.startswith(page[: page.index("<style>")])  # the head is kept as is

    no_room = lean_html(page, 8_000)  # JSON-LD larger than the budget is dropped whole, never cut
    assert len(no_room.encode()) <= 8_000 and "ld+json" not in no_room
    assert no_room.startswith(page[: page.index("<style>")])

    small = "<html><head><script>x()</script></head><body>hi</body></html>"
    assert lean_html(small, 1_000) == small  # a page that fits is never touched


def test_lean_html_drops_large_data_scripts_before_cutting_the_body() -> None:
    state = '<script type="application/json" id="state">' + json.dumps({"s": "x" * 50_000}) + "</script>"
    page = f"<html><head>{state}</head><body><main>{'<p>row</p>' * 100}</main></body></html>"
    lean = lean_html(page, 10_000)
    assert 'id="state"' not in lean and lean.count("<p>row</p>") == 100


def test_digest_shows_structured_data_beyond_the_first_kilobytes() -> None:
    page = listing_page(BASE, PRODUCTS, [f"{BASE}page=2/"])
    limits = MaterialLimits()
    assert page.index("ld+json") > 6_000
    text = material_text(page, "text/html; charset=utf-8", 6_000, limits)
    assert len(text) <= 6_000
    assert text.startswith(f"[HTML digest of a {len(page.encode())}-byte page")
    assert '<meta name="jane:page-type" content="category">' in text and "viewport" not in text
    assert f'<link rel="canonical" href="{BASE}">' in text
    ld = text[text.index('<script type="application/ld+json">') :]
    assert '"name":"Laptop 0"' in ld and '"price":100' in ld
    assert "... 57 more item(s), 60 in total on the page" in ld
    assert "## visible text" in text and "## body markup (start)" in text
    assert "window.__STATE__" not in text

    tiny = html_digest(page, 1_500, limits)  # a smaller budget shortens lists further instead of cutting JSON
    assert len(tiny) <= 1_500 and "59 more item(s)" in tiny

    long_name = listing_page(BASE, [("N" * 5_000, PRODUCTS[0][1], 1)], [])
    assert "...[+4000 chars]" in material_text(long_name, "text/html", 6_000, limits)

    assert material_text("<p>small</p>", "text/html", 6_000, limits) == "<p>small</p>"
    plain = material_text("y" * 7_000, "text/plain", 6_000, limits)
    kept = len(plain) - len(plain.lstrip("y"))
    assert len(plain) <= 6_000 and kept > 5_900
    assert plain.endswith(f"[... truncated {7_000 - kept} characters]")


def test_reduced_material_describes_its_own_content() -> None:
    page = listing_page(BASE, PRODUCTS, [])
    original = material(BASE, page)
    limits = MaterialLimits(max_fixture_bytes=20_000)
    reduced = reduce_material(original, page.encode(), page, limits)
    content = reduced["content"]
    data = content["data"].encode()
    assert (
        content["kind"] == "inline"
        and content["encoding"] == "utf-8"
        and content["media_type"] == "text/html"
    )
    assert content["size_bytes"] == len(data) <= 20_000
    assert content["sha256"] == hashlib.sha256(data).hexdigest() == reduced["revision"]["content_sha256"]
    assert original["content"]["data"] == page  # the original is not changed

    small = material(BASE, "<p>hi</p>")
    assert reduce_material(small, b"<p>hi</p>", "<p>hi</p>", limits) == small
    blob = {**small, "content": {"kind": "blob", "uri": "file:///x", "media_type": "text/html"}}
    inlined = reduce_material(blob, b"<p>hi</p>", "<p>hi</p>", limits)
    assert inlined["content"]["data"] == "<p>hi</p>" and inlined["content"]["kind"] == "inline"
    assert reduce_material(blob, b"<p>hi</p>", "<p>hi</p>", limits, inline=False) == blob

    shell = empty_shell(reduced)
    assert shell["content"]["data"].count("<title>Laptops - Laptops Example</title>") == 1
    assert "<body></body>" in shell["content"]["data"] and "ld+json" not in shell["content"]["data"]
    assert shell["locator"] == reduced["locator"]


def test_url_shapes_collapse_ids_parameters_and_file_names() -> None:
    def shape(url: str) -> str:
        return url_shape({"locator": {"url": url}})

    assert shape(f"{BASE}producer=asus/") == shape(f"{BASE}page=2/") == shape(f"{BASE}a=1;b=2/")
    assert shape(f"{BASE}producer=asus/") == "shop.example.test/catalog/*/*=*"
    assert shape("https://shop.example.test/ua/asus-x1504/p621368348/") == "shop.example.test/ua/*/*"
    assert shape("https://shop.example.test/ua/notebooks/c80004/") == "shop.example.test/ua/notebooks/*"
    assert shape("https://shop.example.test/item/laptop-asus-790214.html") == "shop.example.test/item/*.html"
    assert shape("https://shop.example.test/about/index.php") == "shop.example.test/about/index.php"
    assert link_pattern(f"{BASE}producer=asus;series=1/") == "shop.example.test/catalog/*/producer=*;series=*"
    assert (
        link_pattern("https://shop.example.test/list?page=2&sort=asc")
        == "shop.example.test/list?page=*&sort=*"
    )


def test_evidence_canonical_links_and_pagination() -> None:
    page = listing_page(
        BASE,
        [],
        [
            f"{BASE}page=2/",
            f"{BASE}page=3/",
            "/catalog/c80004/page=67/",
            f"{BASE}processor=intel-core-3/",
            f"{BASE}processor=intel-core-5/",
            f"{BASE}ram=8-gb/",
            f"{BASE}ram=16-gb/",
            "https://other.example.test/x",
            "#top",
        ],
    )
    assert declared_canonical(page, f"{BASE}page=2/") == BASE
    assert same_url("https://Shop.example.test:443/catalog/c80004", BASE)
    assert not same_url(f"{BASE}page=2/", BASE)
    links = page_links(page, f"{BASE}page=2/", ["shop.example.test"])
    assert f"{BASE}page=67/" in links and all("other.example" not in u for u in links)
    assert pagination_templates(links) == {f"{BASE}page={{n}}/": [2, 3, 67]}
    assert pagination_templates(
        ["https://shop.example.test/list?page=2", "https://shop.example.test/list?page=3"]
    )


def test_sampling_rules_follow_the_crawl_hints() -> None:
    hinted = sampling_rules(
        "web",
        BASE,
        None,
        ["shop.example.test"],
        {
            "scope": {"allowed_schemes": ["https"], "path_prefixes": ["/catalog/c80004/"]},
            "strategies": [{"type": "listing", "start_urls": [BASE]}],
        },
    )
    assert hinted["strategies"] == [{"type": "listing", "start_urls": [BASE]}]  # the user bounded discovery
    assert hinted["scope"] == {
        "allowed_domains": ["shop.example.test"],
        "allowed_schemes": ["https"],
        "path_prefixes": ["/catalog/c80004/"],
    }
    assert hinted["dedup"] == {"use_link_rel_canonical": False}
    default = sampling_rules("web", BASE, None, ["shop.example.test"], None)
    assert [s["strategy_id"] for s in default["strategies"]] == [
        "sample-sitemap",
        "sample-feed",
        "sample-recursive",
    ]
    own = sampling_rules("web", BASE, None, ["shop.example.test"], {"dedup": {"key": "canonical_url"}})
    assert own["dedup"] == {"key": "canonical_url"}


def _rules(*strategies: dict[str, Any]) -> dict[str, Any]:
    return {
        "collector": "web",
        "scope": {"allowed_domains": ["shop.example.test"]},
        "strategies": list(strategies),
    }


def test_canonical_dedup_follows_what_a_plan_targets() -> None:
    evidence = {
        "canonical": {
            "declared_elsewhere": 1,
            "examples": [{"url": f"{BASE}page=2/", "canonical": BASE, "content": "different"}],
            "urls": [f"{BASE}page=2/"],
        },
        "pagination": [{"template": f"{BASE}page={{n}}/", "pages_seen": [2, 3]}],
    }
    off = {"use_link_rel_canonical": False}
    pages = _rules({"type": "seed_list", "urls": [BASE, f"{BASE}page=2/"]})
    assert _canonical_dedup(pages, evidence, {}, URL)[0] == off
    assert _canonical_dedup(pages, {}, {}, URL)[0] == off  # an explicit page list, evidence or not
    assert _canonical_dedup(_rules({"type": "listing", "start_urls": [BASE]}), {}, {}, URL)[0] == off
    follow = _rules(
        {
            "type": "recursive",
            "seeds": [BASE],
            "follow": [{"type": "glob", "value": "shop.example.test/catalog/c80004/page=*"}],
        }
    )
    dedup, risk = _canonical_dedup(follow, evidence, {}, URL)
    assert dedup == off and risk and "pagination pages" in risk
    sitemap = _rules({"type": "sitemap"})
    dedup, risk = _canonical_dedup(sitemap, evidence, {}, URL)
    assert dedup is None and risk and f"{BASE}page=2/ -> {BASE}" in risk
    assert _canonical_dedup(sitemap, {}, {}, URL) == (None, None)
    template = _rules(
        {"type": "url_template", "template": f"{BASE}page={{n}}/", "variables": {"n": {"values": [2]}}}
    )
    dedup, risk = _canonical_dedup(template, {}, {}, URL)
    assert dedup == off and risk and "generates its page URLs" in risk
    one_seed = _rules({"type": "seed_list", "urls": [BASE]})
    assert _canonical_dedup(one_seed, {}, {}, URL) == (None, None)
    long = {
        "canonical": {
            "examples": [{"url": f"{BASE}page=2/?" + "q" * 5_000, "canonical": BASE + "c" * 5_000}],
            "urls": [f"{BASE}page=2/?" + "q" * 5_000],
        }
    }
    dedup, risk = _canonical_dedup(sitemap, long, {}, 120)
    assert dedup is None and risk and len(risk) < 2 * 120 + 200  # page URLs in a risk are cut
    user = {"dedup": {"use_link_rel_canonical": True, "bogus": 1}}
    assert _canonical_dedup(pages, evidence, user, URL) == (
        {"use_link_rel_canonical": True},
        None,
    )  # the user decides


def test_estimates_count_listed_pages_and_respect_the_users_page_budget() -> None:
    listed = _rules({"type": "seed_list", "urls": [BASE, f"{BASE}page=2/", BASE]})
    assert _estimate(listed, 500, 1.0, None) == (2, "exactly the 2 listed or generated URL(s) per run")
    template = {
        "type": "url_template",
        "template": "https://shop.example.test/catalog/c80004/page={n}/",
        "variables": {"n": {"range": {"start": 2, "end": 100}}},
    }
    assert _estimate(_rules({"type": "seed_list", "urls": [BASE]}, template), 500, 1.0, None)[0] == 100
    assert _estimate(_rules(template), 500, 1.0, 60)[0] == 60  # a run fetches at most the user's pages
    crawl = _rules({"type": "recursive", "seeds": [BASE]})
    estimated, notes = _estimate(crawl, 500, 0.5, 60)
    assert estimated == 60 and "max_pages_per_run=60" in notes
    assert _estimate(crawl, 500, 0.5, None)[0] == 250


def test_script_text_never_starts_a_comment_style_or_another_block() -> None:
    """Review repro: ``"<!--"`` / ``"<style"`` inside JavaScript used to eat the page up to the next ``-->``."""
    rows = "<p>row</p>" * 20_000
    page = (
        '<html><body><script>var s="<!--"; var t="<style>"; var u="<svg>";</script><main>'
        f'{rows}</main><script type="application/ld+json">{{"a":1}}</script><!-- c --><p>tail</p></body></html>'
    )
    lean = lean_html(page, 131_072)
    assert lean.count("<p>row</p>") > 10_000 and '<script type="application/ld+json">{"a":1}</script>' in lean
    assert "var s=" not in lean and "<!-- c -->" not in lean
    full = lean_html(page, 1_000_000)  # fits: untouched
    assert full == page
    padded = page.replace("<main>", "<main>" + "<i>x</i>" * 3_000)  # over the limit, nothing to cut but code
    assert lean_html(padded, len(padded.encode()) - 10).count("<p>row</p>") == 20_000
    # a commented-out script is a comment, a script inside a comment is not a block of its own
    assert outside_blocks('a<!-- <script>x</script> -->b<script>"-->"</script>c') == "a b c"
    assert declared_canonical(
        '<script>"<link rel=canonical href=/x>"</script><link rel="canonical" href="/y">', BASE
    ) == ("https://shop.example.test/y")
    assert page_links(
        '<script>"<a href=/in-js>"</script><!-- <a href="/in-comment"> --><a href="/real">', BASE
    ) == ["https://shop.example.test/real"]


def test_digest_and_cut_texts_respect_their_size() -> None:
    page = listing_page(BASE, PRODUCTS, [f"{BASE}page=2/"])
    limits = MaterialLimits()
    for size in (0, 1, 50, 181, 400, 2_000):
        assert len(html_digest(page, size, limits)) <= size
        assert len(material_text("y" * 7_000, "text/plain", size, limits)) <= size
    assert html_digest(page, 0, limits) == ""


def test_material_limits_shares_must_fit() -> None:
    MaterialLimits(head_share=0.2, structured_share=0.6, text_share=0.2)  # exactly 1 is fine
    with pytest.raises(ValidationError, match="must not exceed 1"):
        MaterialLimits(head_share=0.5, structured_share=0.5, text_share=0.1)
