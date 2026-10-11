"""Contract and evidence checks for the news website onboarding catalog.

Samples are short metadata excerpts fetched from real publishers on 2026-10-11.
They document onboarding; the scheduled tasks always collect publishers live.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import jane_examples as examples  # noqa: E402

SOURCES = json.loads((HERE / "sources.web.json").read_text(encoding="utf-8"))


def test_catalog_covers_each_requested_region() -> None:
    assert Counter(source["region"] for source in SOURCES) == {
        "ukraine": 2,
        "europe": 2,
        "usa": 2,
        "russia": 2,
    }
    assert len({source["source_id"] for source in SOURCES}) == len(SOURCES)
    assert all(source["source_id"].startswith("news-web-") for source in SOURCES)


@pytest.mark.parametrize("source", SOURCES, ids=[source["source_id"] for source in SOURCES])
def test_rules_and_live_onboarding_sample(source: dict[str, str]) -> None:
    package = HERE / "packages" / source["rules_package_id"]
    manifest = examples.read_json(package / "jane-package.json")
    rules = examples.read_json(package / "rules.json")
    assert examples.validate("package-manifest.schema.json", manifest) == []
    assert examples.validate("collector-rules.schema.json", rules) == []
    assert manifest["package_id"] == source["rules_package_id"]
    assert manifest["kind"] == "collector-rules"
    assert rules["robots"]["mode"] == "respect"
    assert rules["strategies"] == [
        {
            "type": "feed",
            "strategy_id": "latest-news",
            "urls": [source["url"]],
            "autodiscover": False,
        }
    ]
    assert rules["limits"]["crawl"]["max_pages_per_run"] == 5
    for field in ("url", "article_url"):
        host = urlsplit(source[field]).hostname
        assert host in rules["scope"]["allowed_domains"]
    sample = examples.read_json(HERE / "samples" / "web" / f"{source['source_id']}.json")
    assert sample["source_id"] == source["source_id"]
    assert sample["article_url"] == source["article_url"]
    assert sample["feed_http_status"] == 200
    assert sample["article_http_status"] == 200
    assert sample["robots_allowed"] is True
    assert sample["title"]
    assert len(sample["excerpt"]) <= 400
    assert sample["fetched_at"].endswith("Z")
