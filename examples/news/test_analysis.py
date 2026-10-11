"""News package contracts and provenance checks without an external model."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any, cast

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = Path(__file__).parent / "packages"
NORMALIZER = PACKAGES / "news.article-normalize"
ANALYZER = PACKAGES / "news.article-analysis"
SPEC = importlib.util.spec_from_file_location(
    "news_article_normalize", NORMALIZER / "src/news_article_normalize/main.py"
)
assert SPEC is not None
assert SPEC.loader is not None
NORMALIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NORMALIZE)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def article(quote: str, language: str = "en") -> dict[str, Any]:
    fields = load(NORMALIZER / "tests/unavailable/entities.json")[0]["fields"]
    fields["source_language"] = language
    fields["sentiment"]["evidence"][0]["quote"] = quote
    fields["entities"] = []
    fields["event"] = {
        "summary": "Єврокомісія схвалила конкретну програму допомоги Україні.",
        "canonical": {
            "date": "2026-10-11",
            "primary_actor": "European Commission",
            "action": "approve",
            "object": "Ukraine Assistance Programme Decision 2026/123",
            "location": "Brussels",
        },
        "identity_specificity": "specific",
        "identity_confidence": 0.95,
        "evidence": [
            {"quote": quote, "reason": "Конкретний акт підтверджено текстом.", "attribution": "author"}
        ],
    }
    return {
        "entity_type": "news_article",
        "key": {"scope": "news-fixture", "natural": {"url": fields["url"]}},
        "fields": fields,
        "observation": {
            "observation_id": "obs-fixture",
            "observed_at": "2026-10-11T08:00:01Z",
            "material_id": "web:neutral-news",
        },
    }


def material(text: str, source: str = "news-fixture") -> dict[str, Any]:
    value = load(ANALYZER / "tests/neutral-bad-news/material.json")
    value["source"]["source_id"] = source
    value["content"]["data"] = text
    value["content"]["size_bytes"] = len(text.encode("utf-8"))
    return cast(dict[str, Any], value)


def run(entity: dict[str, Any], source: dict[str, Any] | None, **params: Any) -> dict[str, Any]:
    handler_input: dict[str, Any] = {"kind": "entities", "entities": [entity]}
    if source:
        handler_input["material"] = source
    return cast(dict[str, Any], NORMALIZE.normalize(handler_input, params, None))


@pytest.mark.parametrize("package", [ANALYZER, NORMALIZER])
def test_package_manifest_and_schemas_are_valid(package: Path) -> None:
    resources = []
    for path in (ROOT / "contracts/schemas").rglob("*.json"):
        resources.append((path.as_uri(), Resource.from_contents(load(path))))
    registry = Registry().with_resources(resources)
    contract = ROOT / "contracts/schemas/package-manifest.schema.json"
    validator = Draft202012Validator(
        {"$ref": contract.as_uri()}, registry=registry, format_checker=FormatChecker()
    )
    manifest = load(package / "jane-package.json")
    validator.validate(manifest)
    for schema_path in (package / "schemas").glob("*.json"):
        Draft202012Validator.check_schema(load(schema_path))
    for case in manifest["tests"]:
        for path in case["input"].values():
            assert (package / path).is_file()


def test_multilingual_same_precise_event_has_one_global_id() -> None:
    descriptions = {
        "en": "The European Commission approved Ukraine Assistance Programme Decision 2026/123 in Brussels on 11 October 2026.",
        "uk": "Європейська комісія схвалила рішення 2026/123 щодо програми допомоги Україні в Брюсселі 11 жовтня 2026 року.",
        "ru": "Европейская комиссия одобрила решение 2026/123 по программе помощи Украине в Брюсселе 11 октября 2026 года.",
    }
    event_ids = set()
    source_scopes = set()
    for language, quote in descriptions.items():
        result = run(article(quote, language), material(quote, f"news-{language}"))
        shared, publication = result["entities"]
        assert shared["entity_type"] == "news_event"
        assert shared["key"]["scope"] == "news-events"
        assert shared["observation"]["observation_id"] == "obs-fixture"
        assert publication["fields"]["evidence_validation"] == "verified"
        assert publication["fields"]["source_language"] == language
        assert publication["fields"]["analysis_language"] == "uk"
        event_ids.add(publication["fields"]["event_id"])
        source_scopes.add(publication["key"]["scope"])
    assert len(event_ids) == 1
    assert len(source_scopes) == 3


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("date", "2026-10-12"),
        ("action", "announce"),
        ("object", "Ukraine Assistance Programme Decision 2026/124"),
        ("primary_actor", "European Council"),
        ("location", "Berlin"),
    ],
)
def test_distinct_acts_dates_and_objects_do_not_merge(field: str, value: str) -> None:
    event = article("News.")["fields"]["event"]
    original, _ = NORMALIZE.event_identity(event, 0.9)
    changed = copy.deepcopy(event)
    changed["canonical"][field] = value
    different, _ = NORMALIZE.event_identity(changed, 0.9)
    assert original
    assert different
    assert original != different


@pytest.mark.parametrize("missing", ["date", "primary_actor", "action", "object", "location"])
def test_incomplete_identity_is_ungrouped(missing: str) -> None:
    entity = article("News.")
    del entity["fields"]["event"]["canonical"][missing]
    result = run(entity, material("News."))
    assert len(result["entities"]) == 1
    fields = result["entities"][0]["fields"]
    assert fields["event_grouping"]["status"] == "ungrouped"
    assert "event_id" not in fields


@pytest.mark.parametrize("specificity", ["broad", "unknown"])
def test_broad_topic_never_becomes_shared_event(specificity: str) -> None:
    entity = article("News.")
    entity["fields"]["event"]["identity_specificity"] = specificity
    fields = run(entity, material("News."))["entities"][0]["fields"]
    assert fields["event_grouping"]["status"] == "ungrouped"


def test_neutral_reporting_of_negative_fact_stays_neutral() -> None:
    original = load(NORMALIZER / "tests/unavailable/entities.json")[0]
    source = load(ANALYZER / "tests/neutral-bad-news/material.json")
    result = run(original, source)
    fields = result["entities"][0]["fields"]
    assert fields["sentiment"]["label"] == "neutral"
    assert fields["entities"][0]["attitude"] == "neutral"


def test_invented_quote_is_rejected() -> None:
    with pytest.raises(ValueError, match="quotation is absent"):
        run(article("Invented praise."), material("Plain factual news."))


def test_quoted_accusation_cannot_become_author_attitude() -> None:
    entity = article("A critic called the minister incompetent.")
    entity["fields"]["entities"] = [
        {
            "name": "minister",
            "canonical_name": "minister",
            "type": "person",
            "role": "object",
            "attitude": "negative",
            "attitude_confidence": 0.95,
            "evidence": [
                {"quote": "incompetent", "attribution": "quoted_source", "reason": "Цитата критика."}
            ],
        }
    ]
    with pytest.raises(ValueError, match="author's framing"):
        run(entity, material("A critic called the minister incompetent."))


def test_quoted_accusation_cannot_become_overall_author_sentiment() -> None:
    entity = article("A critic called the minister incompetent.")
    entity["fields"]["sentiment"]["label"] = "negative"
    entity["fields"]["sentiment"]["evidence"][0]["attribution"] = "quoted_source"
    with pytest.raises(ValueError, match="overall sentiment"):
        run(entity, material("A critic called the minister incompetent."))


def test_grouping_threshold_is_configurable() -> None:
    entity = article("News.")
    grouped = run(entity, material("News."), min_grouping_confidence=0.9)
    rejected = run(entity, material("News."), min_grouping_confidence=0.99)
    assert len(grouped["entities"]) == 2
    assert rejected["entities"][0]["fields"]["event_grouping"]["reason"] == "low_identity_confidence"


def test_per_post_publication_metadata_survives_collection_page_metadata() -> None:
    entity = article("Post news.")
    entity["fields"].update({"published_at": "2026-10-10T20:00:00Z", "source_kind": "telegram"})
    source = material("Post news.")
    result = run(entity, source)
    fields = result["entities"][-1]["fields"]
    assert fields["published_at"] == "2026-10-10T20:00:00Z"
    assert fields["source_kind"] == "telegram"
    assert fields["fetched_at"] == source["fetched_at"]
    assert fields["material_id"] == source["material_id"]


def test_normalizer_manifest_cases() -> None:
    from jane_extractor_sdk.testing import assert_package_tests_pass

    assert_package_tests_pass(NORMALIZER)


def test_prepared_source_name_is_preserved_and_stage_metadata_is_authoritative() -> None:
    entity = article("News.")
    entity["fields"]["source_name"] = "Prepared publisher"
    assert run(entity, material("News."))["entities"][-1]["fields"]["source_name"] == "Prepared publisher"
    result = run(entity, material("News."), source_name="Configured publisher", region="UA", transport="web")
    assert result["entities"][-1]["fields"]["source_name"] == "Configured publisher"
    assert result["entities"][-1]["fields"]["region"] == "UA"


def test_hallucinated_foreign_article_url_is_rejected() -> None:
    entity = article("News.")
    entity["fields"]["url"] = "https://other.example.test/article"
    with pytest.raises(ValueError, match="original source host"):
        run(entity, material("News."))


def test_hallucinated_other_telegram_channel_url_is_rejected() -> None:
    entity = article("News.")
    entity["fields"].update({"url": "https://t.me/otherchannel/1", "source_kind": "telegram"})
    source = material("News.")
    source["locator"] = {"url": "https://t.me/s/channel"}
    with pytest.raises(ValueError, match="original channel"):
        run(entity, source)


@pytest.mark.parametrize("tag", ["nav", "footer", "header", "aside", "form"])
def test_page_chrome_cannot_supply_news_evidence(tag: str) -> None:
    source = material(f"<{tag}>Unrelated promotional praise.</{tag}><article>Actual neutral story.</article>")
    source["format"]["media_type"] = "text/html"
    with pytest.raises(ValueError, match="quotation is absent"):
        run(article("Unrelated promotional praise."), source)
    assert (
        run(article("Actual neutral story."), source)["entities"][-1]["fields"]["evidence_validation"]
        == "verified"
    )


def test_same_host_different_article_path_is_rejected() -> None:
    entity = article("Actual neutral story.")
    entity["fields"]["url"] = "https://news.example.test/entirely-different-article"
    source = material("<article>Actual neutral story.</article>")
    source["format"]["media_type"] = "text/html"
    with pytest.raises(ValueError, match="verified canonical article URL"):
        run(entity, source)


def test_jsonld_article_body_and_explicit_canonical_are_supported() -> None:
    raw = (
        '<head><link rel="canonical" href="/canonical-article">'
        '<script type="application/ld+json">'
        '{"@type":"NewsArticle","headline":"Article headline", "articleBody":"Actual article body."}'
        "</script></head><nav>Promotion.</nav><main>Paywall chrome.</main>"
    )
    source = material(raw)
    source["format"]["media_type"] = "text/html"
    entity = article("Actual article body.")
    entity["fields"]["url"] = "https://news.example.test/canonical-article"
    assert run(entity, source)["entities"][-1]["fields"]["evidence_validation"] == "verified"
    entity["fields"]["sentiment"]["evidence"][0]["quote"] = "Paywall chrome."
    with pytest.raises(ValueError, match="quotation is absent"):
        run(entity, source)


def test_same_path_different_meaningful_query_is_rejected() -> None:
    source = material("News.")
    source["locator"]["url"] = "https://news.example.test/article?id=1"
    entity = article("News.")
    entity["fields"]["url"] = "https://news.example.test/article?id=2"
    with pytest.raises(ValueError, match="verified canonical article URL"):
        run(entity, source)


def test_telegram_post_id_must_exist_in_collected_html() -> None:
    source = material('<div data-post="channel/1"><div class="tgme_widget_message_text">News.</div></div>')
    source["format"]["media_type"] = "text/html"
    source["locator"] = {"url": "https://t.me/s/channel"}
    entity = article("News.")
    entity["fields"].update({"url": "https://t.me/channel/99", "source_kind": "telegram"})
    with pytest.raises(ValueError, match="present in the original material"):
        run(entity, source)


def test_html_quotation_uses_visible_decoded_text() -> None:
    entity = article("News & evidence.")
    source = material(
        "<html><script>Invented quote</script><article>News &amp; <b>evidence.</b></article></html>"
    )
    source["format"]["media_type"] = "text/html"
    assert run(entity, source)["entities"][-1]["fields"]["evidence_validation"] == "verified"
    with pytest.raises(ValueError, match="quotation is absent"):
        run(article("Invented quote"), source)


def test_html_inline_formatting_whitespace_before_punctuation_is_equivalent() -> None:
    source = material("<article>Reported by the <b>minister</b>, an official.</article>")
    source["format"]["media_type"] = "text/html"
    assert (
        run(article("minister, an official."), source)["entities"][-1]["fields"]["evidence_validation"]
        == "verified"
    )
    with pytest.raises(ValueError, match="quotation is absent"):
        run(article("minister, a criminal."), source)


def test_telegram_quotes_are_verified_against_the_specific_post() -> None:
    source = material(
        '<div data-post="channel/1"><div class="tgme_widget_message_text">First post.</div></div>'
        '<div data-post="channel/2"><div class="tgme_widget_message_text">Second post.</div></div>'
    )
    source["format"]["media_type"] = "text/html"
    source["locator"] = {"url": "https://t.me/s/channel"}
    entity = article("Second post.")
    entity["fields"].update({"url": "https://t.me/channel/2", "source_kind": "telegram"})
    assert run(entity, source)["entities"][-1]["key"]["natural"] == {"url": "https://t.me/channel/2"}
    entity["fields"]["url"] = "https://t.me/channel/1"
    with pytest.raises(ValueError, match="quotation is absent"):
        run(entity, source)


def test_telegram_feed_cannot_be_disguised_as_a_web_article() -> None:
    source = material(
        '<div class="tgme_widget_message" data-post="channel/1">'
        '<div class="tgme_widget_message_text">Actual first post.</div><a>Footer praise.</a></div>'
    )
    source["format"]["media_type"] = "text/html"
    source["locator"] = {"url": "https://t.me/s/channel"}
    entity = article("Footer praise.")
    entity["fields"].update({"url": "https://t.me/s/channel", "source_kind": "web"})
    with pytest.raises(ValueError, match="original channel"):
        run(entity, source)
    entity["fields"]["url"] = "https://t.me/channel/1"
    with pytest.raises(ValueError, match="quotation is absent"):
        run(entity, source)
    real = article("Actual first post.")
    real["fields"].update({"url": "https://t.me/channel/1", "source_kind": "web"})
    fields = run(real, source)["entities"][-1]["fields"]
    assert fields["source_kind"] == "telegram"
    assert fields["transport"] == "telegram_public_web"


@pytest.mark.parametrize("extra_class", ["tgme_widget_message_reply", "tgme_widget_message_link_preview"])
def test_telegram_reply_and_preview_are_not_article_evidence(extra_class: str) -> None:
    source = material(
        '<div class="tgme_widget_message" data-post="channel/1">'
        '<div class="tgme_widget_message_text">Actual post.'
        f'<div class="{extra_class}">Unrelated quoted content.</div></div></div>'
    )
    source["format"]["media_type"] = "text/html"
    source["locator"] = {"url": "https://t.me/s/channel"}
    entity = article("Unrelated quoted content.")
    entity["fields"]["url"] = "https://t.me/channel/1"
    with pytest.raises(ValueError, match="quotation is absent"):
        run(entity, source)


def test_blob_evidence_is_unavailable_and_cannot_group_without_verification() -> None:
    source = material("News.")
    source["content"] = {"kind": "blob", "uri": "file:///transit/news", "size_bytes": 5, "sha256": "1" * 64}
    with pytest.raises(ValueError, match="inline content"):
        run(article("News."), source)
    fields = run(article("News."), source, require_verified_evidence=False)["entities"][0]["fields"]
    assert fields["evidence_validation"] == "unavailable"
    assert fields["event_grouping"]["status"] == "ungrouped"
    assert "event_id" not in fields


def test_runtime_loaded_blob_has_the_same_article_boundary_and_url_checks() -> None:
    from jane_extractor_sdk import Context

    payload = b'<head><link rel="canonical" href="/canonical-article"></head><nav>Promotion.</nav><article>News.</article>'
    source = material("News.")
    source["format"]["media_type"] = "text/html"
    source["content"] = {
        "kind": "blob",
        "uri": "file:///transit/news",
        "size_bytes": len(payload),
        "sha256": "1" * 64,
    }
    entity = article("News.")
    entity["fields"]["url"] = "https://news.example.test/canonical-article"
    wrapper = {"kind": "entities", "entities": [entity], "material": source}
    ctx = Context(wrapper, content_loader=lambda: payload)
    result = NORMALIZE.normalize(wrapper, {}, ctx)
    assert result["entities"][-1]["fields"]["evidence_validation"] == "verified"
    entity["fields"]["sentiment"]["evidence"][0]["quote"] = "Promotion."
    with pytest.raises(ValueError, match="quotation is absent"):
        NORMALIZE.normalize(wrapper, {}, ctx)


def test_normalized_output_matches_entity_schemas() -> None:
    result = run(article("News."), material("News."))
    for record in result["entities"]:
        schema = load(NORMALIZER / f"schemas/{record['entity_type']}.schema.json")
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(record["fields"])


def incident(quote: str, language: str = "en") -> dict[str, Any]:
    entity = article(quote, language)
    event = entity["fields"]["event"]
    event.update(
        {
            "identity_kind": "incident",
            "summary": "Напад на конкретний аеропорт.",
            "date_resolution": {
                "method": "publication_weekday",
                "quote": quote,
                "reference_published_at": "2026-10-10T15:05:55Z",
            },
        }
    )
    event["canonical"] = {
        "date": "2026-10-10",
        "action": "attack",
        "object": "King Khalid International Airport",
        "location": "Riyadh",
        "country": "Saudi Arabia",
    }
    return entity


def incident_material(quote: str, language: str = "en") -> dict[str, Any]:
    source = material(quote, f"news-{language}")
    source["published_at"] = "2026-10-10T15:05:55Z"
    return source


def test_actorless_specific_incident_groups_across_languages_and_blame_claims() -> None:
    quotes = {
        "en": "Saturday's attack hit King Khalid International Airport in Riyadh.",
        "uk": "У суботу стався напад на міжнародний аеропорт імені короля Халіда в Ер-Ріяді.",
        "ru": "В субботу атакован международный аэропорт имени короля Халида в Эр-Рияде.",
    }
    event_ids = set()
    for language, quote in quotes.items():
        entity = incident(quote, language)
        if language == "ru":
            entity["fields"]["event"]["canonical"]["primary_actor"] = "Alleged perpetrator"
        result = run(entity, incident_material(quote, language))
        assert len(result["entities"]) == 2
        shared, publication = result["entities"]
        assert shared["fields"]["identity_kind"] == "incident"
        event_ids.add(publication["fields"]["event_id"])
    assert len(event_ids) == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("date", "2026-10-11"),
        ("action", "fire"),
        ("object", "King Fahd International Airport"),
        ("location", "Dammam"),
        ("country", "Jordan"),
    ],
)
def test_incidents_separate_dates_named_objects_places_and_countries(field: str, value: str) -> None:
    event = incident("Saturday's attack.")["fields"]["event"]
    original, _ = NORMALIZE.event_identity(event, 0.9)
    other = copy.deepcopy(event)
    other["canonical"][field] = value
    changed, _ = NORMALIZE.event_identity(other, 0.9)
    assert original
    assert changed
    assert original != changed


@pytest.mark.parametrize(
    "generic_object",
    ["war", "warehouse", "military warehouse", "international airport", "civilian infrastructure"],
)
def test_generic_incident_object_cannot_merge_despite_high_model_confidence(generic_object: str) -> None:
    entity = incident("Saturday's attack.")
    entity["fields"]["event"]["canonical"]["object"] = generic_object
    fields = run(entity, incident_material("Saturday's attack."))["entities"][0]["fields"]
    assert fields["event_grouping"]["status"] == "ungrouped"
    assert fields["event_grouping"]["reason"] == "generic_incident_object"


@pytest.mark.parametrize(
    "quote",
    [
        "Last Saturday's attack.",
        "The attack happened on Saturday and Thursday.",
        "The attack happened recently.",
    ],
)
def test_relative_event_date_does_not_invent_an_unknown_week(quote: str) -> None:
    fields = run(incident(quote), incident_material(quote))["entities"][0]["fields"]
    assert fields["event_grouping"]["status"] == "ungrouped"
    assert "event_id" not in fields


def test_relative_event_date_requires_original_publication_metadata() -> None:
    quote = "Saturday's attack."
    source = material(quote)
    fields = run(incident(quote), source)["entities"][0]["fields"]
    assert fields["event_grouping"]["reason"] == "ambiguous_relative_event_date"
    source["published_at"] = "2026-10-11T10:00:00Z"
    assert run(incident(quote), source)["entities"][0]["fields"]["event_grouping"]["status"] == "ungrouped"


def test_date_resolution_uses_original_jsonld_and_rejects_fabricated_date_quote() -> None:
    quote = "Saturday's attack."
    source = material(
        '<script type="application/ld+json">{"@type":"NewsArticle","url":"https://news.example.test/article","datePublished":"2026-10-10T15:05:55Z"}</script><article>Saturday\'s attack.</article>'
    )
    source["format"]["media_type"] = "text/html"
    source.pop("published_at", None)
    assert len(run(incident(quote), source)["entities"]) == 2
    entity = incident(quote)
    entity["fields"]["event"]["date_resolution"]["quote"] = "On 10 October 2026"
    assert run(entity, source)["entities"][0]["fields"]["event_grouping"]["status"] == "ungrouped"


@pytest.mark.parametrize(
    "quote",
    [
        "On 10 October 2026 the airport was attacked.",
        "10 жовтня 2026 року стався напад.",
        "10 октября 2026 года произошел напад.",
    ],
)
def test_explicit_incident_date_is_grounded_without_publication_date(quote: str) -> None:
    entity = incident(quote)
    entity["fields"]["event"]["date_resolution"] = {"method": "explicit", "quote": quote}
    assert len(run(entity, material(quote))["entities"]) == 2


def test_two_incidents_same_target_same_day_with_explicit_times_are_distinct() -> None:
    event_ids = set()
    for value in ("10:00", "20:00"):
        quote = f"On 10 October 2026 an attack hit King Khalid International Airport at {value}."
        entity = incident(quote)
        event = entity["fields"]["event"]
        event["canonical"]["time"] = value
        event["date_resolution"] = {"method": "explicit", "quote": quote}
        event["time_evidence"] = {
            "quote": quote,
            "reason": "Час конкретного інциденту.",
            "attribution": "author",
        }
        event_ids.add(run(entity, material(quote))["entities"][-1]["fields"]["event_id"])
    assert len(event_ids) == 2


def test_invented_incident_time_prevents_grouping() -> None:
    quote = "Saturday's attack."
    entity = incident(quote)
    entity["fields"]["event"]["canonical"]["time"] = "10:00"
    entity["fields"]["event"]["time_evidence"] = {"quote": quote, "reason": "Час.", "attribution": "author"}
    assert (
        run(entity, incident_material(quote))["entities"][0]["fields"]["event_grouping"]["reason"]
        == "unverified_incident_time"
    )


@pytest.mark.parametrize("main_has_date", [False, True])
def test_unrelated_jsonld_article_does_not_anchor_or_conflict_with_primary_date(main_has_date: bool) -> None:
    quote = "Saturday's attack."
    primary = {
        "@type": "NewsArticle",
        "url": "https://news.example.test/article",
        "headline": "Primary story",
    }
    if main_has_date:
        primary["datePublished"] = "2026-10-10T15:05:55Z"
    related = {
        "@type": "NewsArticle",
        "url": "https://news.example.test/unrelated-story",
        "datePublished": "2026-10-11T12:00:00Z" if main_has_date else "2026-10-10T12:00:00Z",
        "articleBody": "Unrelated praise. " * 100,
    }
    source = material(
        f'<script type="application/ld+json">{json.dumps([primary, related])}</script><article>{quote}</article>'
    )
    source.pop("published_at", None)
    source["format"]["media_type"] = "text/html"
    result = run(incident(quote), source)
    assert len(result["entities"]) == (2 if main_has_date else 1)
    with pytest.raises(ValueError, match="quotation is absent"):
        run(article("Unrelated praise."), source)


def test_related_html_article_time_does_not_anchor_primary_story() -> None:
    quote = "Saturday's attack."
    source = material(
        '<article>Saturday\'s attack.</article><article><a href="/unrelated">Other story</a><time datetime="2026-10-10T15:05:55Z"></time></article>'
    )
    source.pop("published_at", None)
    source["format"]["media_type"] = "text/html"
    assert (
        run(incident(quote), source)["entities"][0]["fields"]["event_grouping"]["reason"]
        == "ambiguous_relative_event_date"
    )


@pytest.mark.parametrize("container", ["footer", "aside", "nav"])
def test_page_chrome_publication_meta_cannot_anchor_primary_incident(container: str) -> None:
    quote = "Saturday's attack."
    source = material(
        f'<article>{quote}</article><{container}><meta itemprop="datePublished" content="2026-10-10T15:05:55Z"></{container}>'
    )
    source.pop("published_at", None)
    source["format"]["media_type"] = "text/html"
    assert run(incident(quote), source)["entities"][0]["fields"]["event_grouping"]["status"] == "ungrouped"


def test_first_primary_article_publication_meta_can_anchor_its_incident() -> None:
    quote = "Saturday's attack."
    source = material(
        f'<article><meta itemprop="datePublished" content="2026-10-10T15:05:55Z">{quote}</article>'
    )
    source.pop("published_at", None)
    source["format"]["media_type"] = "text/html"
    assert len(run(incident(quote), source)["entities"]) == 2


def test_primary_jsonld_publication_date_takes_precedence_over_update_time() -> None:
    quote = "Saturday's attack."
    source = material(
        '<head><script type="application/ld+json">{"@type":"NewsArticle","url":"https://news.example.test/article","datePublished":"2026-10-10T15:05:55Z"}</script></head><article>Saturday\'s attack.<time datetime="2026-10-11T10:00:00Z">Updated</time></article>'
    )
    source.pop("published_at", None)
    source["format"]["media_type"] = "text/html"
    assert len(run(incident(quote), source)["entities"]) == 2


@pytest.mark.parametrize("value", ["10:00", "20:00"])
def test_explicit_clock_in_event_evidence_cannot_be_dropped_from_identity(value: str) -> None:
    quote = f"On 10 October 2026 an attack hit King Khalid International Airport at {value}."
    entity = incident(quote)
    entity["fields"]["event"]["date_resolution"] = {"method": "explicit", "quote": quote}
    fields = run(entity, material(quote))["entities"][0]["fields"]
    assert fields["event_grouping"]["reason"] == "missing_incident_time_discriminator"
    assert "event_id" not in fields


@pytest.mark.parametrize("package", [ANALYZER, NORMALIZER])
def test_incident_schema_requires_date_provenance_and_keeps_legacy_actor_actions(package: Path) -> None:
    validator = Draft202012Validator(
        load(package / "schemas/news_article.schema.json")["properties"]["event"]
    )
    validator.validate(article("News.")["fields"]["event"])
    entity = incident("Saturday's attack.")
    validator.validate(entity["fields"]["event"])
    del entity["fields"]["event"]["date_resolution"]
    errors = list(validator.iter_errors(entity["fields"]["event"]))
    assert any(error.validator == "required" and "date_resolution" in error.message for error in errors)


def test_storage_grouped_then_ungrouped_then_regrouped_does_not_keep_a_stale_event_id() -> None:
    from datetime import UTC, datetime

    from jane_storage.merge import merge

    source = material("News.")
    first = run(article("News."), source)["entities"][-1]
    event_id = first["fields"]["event_id"]
    assert "event_id" not in first.get("cleared", [])
    current = merge(None, first, now=datetime.now(UTC)).snapshot
    incoming = article("News.")
    incoming["fields"]["event"]["identity_confidence"] = 0.1
    incoming["cleared"] = ["obsolete_note"]
    incoming["observation"].update(observed_at="2026-10-11T08:01:00Z", observation_id="obs-ungrouped")
    ungrouped = run(incoming, source)["entities"][-1]
    assert set(ungrouped["cleared"]) == {"event_id", "obsolete_note"}
    current = merge(current, ungrouped, now=datetime.now(UTC)).snapshot
    assert "event_id" not in current.fields
    assert current.fields["event_grouping"]["status"] == "ungrouped"
    assert "event_id" in current.cleared_fields
    incoming = article("News.")
    incoming["cleared"] = ["event_id", "obsolete_note"]
    incoming["observation"].update(observed_at="2026-10-11T08:02:00Z", observation_id="obs-regrouped")
    regrouped = run(incoming, source)["entities"][-1]
    assert regrouped["cleared"] == ["obsolete_note"]
    current = merge(current, regrouped, now=datetime.now(UTC)).snapshot
    assert current.fields["event_id"] == event_id
    assert current.fields["event_grouping"]["status"] == "grouped"
    assert "event_id" not in current.cleared_fields


def test_cached_analysis_binding_checks_all_prepared_fields_and_ignores_only_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    from validate_live import prepared_content_binding

    previous = [article("Original complete article.")]
    current = copy.deepcopy(previous)
    current[0]["observation"].update(material_id="new-raw", observed_at="2026-10-11T09:00:00Z")
    assert prepared_content_binding(previous, current) == prepared_content_binding(previous, previous)


@pytest.mark.parametrize("field", ["text", "title", "url", "published_at", "source_name", "region"])
def test_cached_analysis_binding_rejects_any_changed_prepared_field(
    field: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    from validate_live import prepared_content_binding

    previous = [article("Original complete article.")]
    current = copy.deepcopy(previous)
    current[0]["fields"][field] = "changed"
    with pytest.raises(ValueError, match="Prepared article fields changed"):
        prepared_content_binding(previous, current)


def test_cached_analysis_binding_distinguishes_equal_python_values_with_different_json_types(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    from validate_live import prepared_content_binding

    previous = [{"fields": {"flag": True}}]
    current = [{"fields": {"flag": 1}}]
    with pytest.raises(ValueError, match="Prepared article fields changed"):
        prepared_content_binding(previous, current)
