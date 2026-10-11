"""Validate real public-channel excerpts and message boundaries without live network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from jane_extractor_sdk.package import material_from_file
from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

BASE = Path(__file__).resolve().parent
PACKAGE = BASE / "packages" / "news.telegram-public-posts"
CATALOG = json.loads((BASE / "sources.telegram.json").read_text(encoding="utf-8"))


def test_manifest_examples() -> None:
    assert_package_tests_pass(PACKAGE)


@pytest.mark.parametrize("source", CATALOG, ids=lambda source: source["source_id"])
def test_real_channel_excerpt_has_valid_article_and_metadata(source: dict[str, str]) -> None:
    channel = source["url"].rsplit("/", 1)[-1]
    sample = BASE / "samples" / "telegram" / channel / "message.html"
    receipt = json.loads(sample.with_name("receipt.json").read_text(encoding="utf-8"))
    material = material_from_file(sample, media_type="text/html", url=source["url"])
    material["source"]["source_id"] = source["source_id"]
    result = run_local(
        PACKAGE,
        {"kind": "material", "material": material},
        params={
            "source_name": source["title"],
            "region": source["region"],
            "language": source["language"],
        },
    )
    assert result["status"] == "success"
    assert len(result["output"]["entities"]) == 1
    article = result["output"]["entities"][0]
    fields = article["fields"]
    schema = json.loads((PACKAGE / "schemas" / "article.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(fields)
    assert fields["url"] == receipt["post_url"]
    assert fields["channel"] == channel
    assert fields["source_id"] == source["source_id"]
    assert fields["source_name"] == source["title"]
    assert fields["region"] == source["region"]
    assert fields["language"] == source["language"]
    assert fields["source_kind"] == "telegram"
    assert fields["transport"] == "telegram_public_web"
    assert receipt["http_status"] == 200
    assert receipt["observed_text_posts"] > 0
    assert receipt["excerpt_words"] <= 18
    assert receipt["snippet_is_partial"] is True


def test_configurable_message_bound_preserves_individual_urls(tmp_path: Path) -> None:
    page = tmp_path / "feed.html"
    page.write_text(
        "".join(
            f'<div class="tgme_widget_message" data-post="channel/{number}">'
            '<div class="tgme_widget_message_reply">Quoted older report</div>'
            f'<div class="tgme_widget_message_text">News {number}<br>Second <b>line</b></div>'
            '<div class="tgme_widget_message_link_preview">Unrelated preview</div>'
            '<div class="tgme_widget_message_footer">100K views</div></div>'
            for number in range(1, 5)
        ),
        encoding="utf-8",
    )
    result = run_local(PACKAGE, file=page, media_type="text/html", params={"max_posts": 2})
    fields = [record["fields"] for record in result["output"]["entities"]]
    assert [row["url"] for row in fields] == ["https://t.me/channel/3", "https://t.me/channel/4"]
    assert [row["text"] for row in fields] == ["News 3\nSecond line", "News 4\nSecond line"]


def test_duplicate_embed_and_media_only_do_not_create_articles(tmp_path: Path) -> None:
    page = tmp_path / "feed.html"
    page.write_text(
        '<div class="tgme_widget_message" data-post="channel/5">'
        '<div class="tgme_widget_message_text">First revision</div></div>'
        '<div class="tgme_widget_message" data-post="channel/6">Media only</div>'
        '<div class="tgme_widget_message" data-post="CHANNEL/5">'
        '<div class="tgme_widget_message_text">Updated revision</div></div>',
        encoding="utf-8",
    )
    result = run_local(PACKAGE, file=page, media_type="text/html")
    articles = result["output"]["entities"]
    assert len(articles) == 1
    assert articles[0]["fields"]["url"] == "https://t.me/channel/5"
    assert articles[0]["fields"]["text"] == "Updated revision"


def test_reply_and_auxiliary_subtrees_never_become_the_post_body() -> None:
    result = run_local(
        PACKAGE,
        file=PACKAGE / "tests" / "tass-reply" / "message.html",
        media_type="text/html",
    )
    fields = result["output"]["entities"][0]["fields"]
    assert fields["url"] == "https://t.me/tass_agency/399748"
    assert fields["text"] == ('"Украинские выборы приближаются": Дмитриев прокомментировал слова Трампа')
    assert fields["published_at"] == "2026-10-11T04:44:01Z"


def test_nested_reply_text_and_script_do_not_interrupt_the_own_body(tmp_path: Path) -> None:
    page = tmp_path / "nested.html"
    page.write_text(
        '<div class="tgme_widget_message" data-post="channel/7">'
        '<div class="tgme_widget_message_text">Own start '
        '<div class="js-message_reply_text">Older quote<br><b>Still quote</b></div>'
        "<script>Ignored executable text</script>"
        '<div class="tgme_widget_message_footer">Views<br>More metadata</div>'
        "Own end</div></div>",
        encoding="utf-8",
    )
    result = run_local(PACKAGE, file=page, media_type="text/html")
    assert result["output"]["entities"][0]["fields"]["text"] == "Own start Own end"
