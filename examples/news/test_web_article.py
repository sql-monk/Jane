"""Readable article boundaries and confirmed metadata of the actual web package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

PACKAGE = Path(__file__).resolve().parent / "packages/news.web-article"
PARAMS = {
    "source_id": "news-web-example",
    "source_name": "Example News",
    "region": "europe",
    "language": "en",
}
ARTICLE_BODY = (
    "The European Commission and the City of Vienna announced a joint transport project. "
    "The programme will improve access to public transport and connect the city's districts. "
    "Officials said construction will start in November after the council approves the budget."
)


def extract_page(tmp_path: Path, page: str) -> dict[str, Any]:
    path = tmp_path / "page.html"
    path.write_text(page, encoding="utf-8")
    result = run_local(
        PACKAGE,
        file=path,
        media_type="text/html",
        url="https://news.example.test/article/1",
        params=PARAMS,
    )
    if result["status"] == "success":
        schema = json.loads((PACKAGE / "schemas/article.schema.json").read_text(encoding="utf-8"))
        for entity in result["output"]["entities"]:
            Draft202012Validator(schema).validate(entity["fields"])
    return result


def test_manifest_examples_execute_actual_package() -> None:
    assert_package_tests_pass(PACKAGE)


def test_html_article_excludes_navigation_and_sidebar(tmp_path: Path) -> None:
    result = extract_page(
        tmp_path,
        '<html><head><meta property="og:title" content="Vienna transport agreement"></head><body>'
        "<nav>Unrelated election scandal involving Atlantis.</nav>"
        "<main><article><h1>Vienna transport agreement</h1>"
        f"<p>{ARTICLE_BODY}</p><aside>Celebrity gossip and betting promotions.</aside>"
        "</article></main><footer>Cookie settings and advertisements.</footer></body></html>",
    )
    assert result["status"] == "success"
    fields = result["output"]["entities"][0]["fields"]
    assert fields["title"] == "Vienna transport agreement"
    assert "European Commission" in fields["text"]
    for unrelated in ("Atlantis", "Celebrity gossip", "Cookie settings", "betting"):
        assert unrelated not in fields["text"]


def test_jsonld_graph_supplies_confirmed_author_time_and_body(tmp_path: Path) -> None:
    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "name": "Example News"},
            {
                "@type": "NewsArticle",
                "headline": "Vienna transport agreement",
                "articleBody": ARTICLE_BODY,
                "datePublished": "2026-10-11T03:00:00Z",
                "author": {"@type": "Person", "name": "Ada Reporter"},
            },
        ],
    }
    result = extract_page(
        tmp_path,
        '<html><head><link rel="canonical" href="/canonical/1">'
        f'<script type="application/ld+json">{json.dumps(structured)}</script></head>'
        "<body><nav>Unrelated campaign allegations.</nav></body></html>",
    )
    assert result["status"] == "success"
    fields = result["output"]["entities"][0]["fields"]
    assert fields["text"] == ARTICLE_BODY
    assert fields["author"] == "Ada Reporter"
    assert fields["published_at"] == "2026-10-11T03:00:00Z"
    assert fields["url"] == "https://news.example.test/canonical/1"


@pytest.mark.parametrize("accessible", [False, "false"])
def test_paywall_is_unrecognized_even_when_teaser_is_long(tmp_path: Path, accessible: bool | str) -> None:
    article = {
        "@type": "NewsArticle",
        "headline": "Vienna transport agreement",
        "articleBody": ARTICLE_BODY,
        "isAccessibleForFree": accessible,
    }
    result = extract_page(
        tmp_path,
        f'<html><head><script type="application/ld+json">{json.dumps(article)}</script></head>'
        f"<body><article>{ARTICLE_BODY}</article></body></html>",
    )
    assert result["status"] == "unrecognized"
    assert result["output"]["entities"] == []
    assert result["unrecognized"]["signature"] == "news:paywall"


def test_main_news_listing_is_not_an_article(tmp_path: Path) -> None:
    result = extract_page(
        tmp_path,
        '<html><head><meta property="og:title" content="Latest headlines"></head><body>'
        '<main><h1>Latest headlines</h1><section><a href="/one">Vienna project</a>'
        f'<p>{ARTICLE_BODY}</p><a href="/two">Another headline</a>'
        f"<p>{ARTICLE_BODY}</p></section></main></body></html>",
    )
    assert result["status"] == "unrecognized"
    assert result["output"]["entities"] == []


def test_short_article_cannot_borrow_navigation_text(tmp_path: Path) -> None:
    result = extract_page(
        tmp_path,
        '<html><head><meta property="og:title" content="Brief notice"></head>'
        f"<body><nav>{ARTICLE_BODY}</nav><article><h1>Brief notice</h1><p>Short teaser.</p>"
        f"</article><footer>{ARTICLE_BODY}</footer></body></html>",
    )
    assert result["status"] == "unrecognized"


def test_main_lead_cannot_enter_primary_article_text(tmp_path: Path) -> None:
    result = extract_page(
        tmp_path,
        '<html><head><meta property="og:title" content="Vienna project"></head><body><main>'
        "<p>Unrelated lead outside the article: Saturday incident involving Atlantis.</p>"
        f"<article><p>{ARTICLE_BODY}</p></article></main></body></html>",
    )
    fields = result["output"]["entities"][0]["fields"]
    assert fields["text"] == ARTICLE_BODY
    assert "Atlantis" not in fields["text"]


def test_primary_jsonld_wins_over_larger_unrelated_article(tmp_path: Path) -> None:
    primary = {
        "@type": "NewsArticle",
        "url": "https://news.example.test/article/1",
        "articleBody": ARTICLE_BODY,
        "headline": "Vienna project",
        "datePublished": "2026-10-11T03:00:00Z",
        "author": {"name": "Ada Reporter"},
    }
    unrelated = {
        "@type": "NewsArticle",
        "url": "https://news.example.test/article/2",
        "articleBody": "Unrelated election allegations. " * 40,
        "headline": "Foreign article",
        "datePublished": "2022-01-01T00:00:00Z",
        "isAccessibleForFree": False,
    }
    result = extract_page(
        tmp_path,
        f'<html><head><script type="application/ld+json">{json.dumps([unrelated, primary])}</script>'
        "</head><body></body></html>",
    )
    fields = result["output"]["entities"][0]["fields"]
    assert fields["text"] == ARTICLE_BODY
    assert fields["published_at"] == primary["datePublished"]
    assert fields["author"] == "Ada Reporter"


def test_unrelated_jsonld_does_not_supply_body_or_publication(tmp_path: Path) -> None:
    unrelated = {
        "@type": "NewsArticle",
        "mainEntityOfPage": {"@id": "https://news.example.test/foreign"},
        "articleBody": "Unrelated election allegations. " * 40,
        "headline": "Foreign article",
        "datePublished": "2022-01-01T00:00:00Z",
    }
    result = extract_page(
        tmp_path,
        '<html><head><meta property="og:title" content="Vienna project">'
        f'<script type="application/ld+json">{json.dumps(unrelated)}</script></head>'
        f"<body><article><p>{ARTICLE_BODY}</p></article>"
        '<aside><time datetime="2022-01-01T00:00:00Z"></time></aside></body></html>',
    )
    fields = result["output"]["entities"][0]["fields"]
    assert fields["text"] == ARTICLE_BODY
    assert fields["title"] == "Vienna project"
    assert "published_at" not in fields


def test_later_html_article_cannot_supply_text_or_timestamp(tmp_path: Path) -> None:
    result = extract_page(
        tmp_path,
        '<html><head><meta property="og:title" content="Vienna project"></head><body><main>'
        f"<article><p>{ARTICLE_BODY}</p></article>"
        '<article><h1>Unrelated Atlantis</h1><time datetime="2022-01-01T00:00:00Z"></time>'
        "<p>Unrelated election allegations involving Atlantis.</p></article></main></body></html>",
    )
    fields = result["output"]["entities"][0]["fields"]
    assert fields["text"] == ARTICLE_BODY
    assert "published_at" not in fields
