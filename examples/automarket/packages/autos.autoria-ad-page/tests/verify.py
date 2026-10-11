"""Verify AUTO.RIA package fixtures, field contracts, source evidence and collector URL boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from jsonschema import Draft202012Validator
from lxml import html  # type: ignore[import-untyped]
from referencing import Registry, Resource

from jane_extractor_sdk.testing import run_local, run_package_tests
from jane_web_collector.discovery.links import extract_hrefs
from jane_web_collector.urls import Scope


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _no_null(value: Any) -> None:
    assert value is not None, "null fields must be omitted"
    if isinstance(value, dict):
        for item in value.values():
            _no_null(item)
    elif isinstance(value, list):
        for item in value:
            _no_null(item)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-samples", type=Path, help="Optional local raw/meta sample directory")
    args = parser.parse_args()
    package_dir = Path(__file__).resolve().parents[1]
    packages = package_dir.parent
    automarket = packages.parent
    root = next(p for p in package_dir.parents if (p / "contracts/schemas").is_dir())
    resources = []
    for path in (root / "contracts/schemas").rglob("*.schema.json"):
        contents = _json(path)
        contents["$id"] = path.as_uri()
        resources.append((path.as_uri(), Resource.from_contents(contents)))
    registry = Registry().with_resources(resources)

    def validate_contract(schema_name: str, instance: Any) -> None:
        path = root / "contracts/schemas" / schema_name
        schema = _json(path)
        schema["$id"] = path.as_uri()
        Draft202012Validator(schema, registry=registry).validate(instance)

    passed = 0
    entities_checked = 0
    for package_name in ("autos.autoria-ad-page", "autos.autoria-search-page", "autos.autoria-rules"):
        path = packages / package_name
        manifest = _json(path / "jane-package.json")
        validate_contract("package-manifest.schema.json", manifest)
        if manifest["kind"] != "extractor":
            continue
        entity_schema = _json(path / manifest["output"]["entities"][0]["schema"])
        Draft202012Validator.check_schema(entity_schema)
        for case in run_package_tests(path):
            assert case.passed, f"{package_name}/{case.name}: {case.differences}; {case.result}"
            for entity in case.result.get("output", {}).get("entities", []):
                Draft202012Validator(entity_schema).validate(entity["fields"])
                _no_null(entity["fields"])
                assert entity["key"]["natural"] == {
                    "site": entity["fields"]["site"],
                    "ad_id": entity["fields"]["ad_id"],
                }
                entities_checked += 1
            passed += 1
            print(f"PASS {package_name}/{case.name}: {case.actual_status}")

    rules_dir = packages / "autos.autoria-rules"
    rules = _json(rules_dir / "rules.json")
    validate_contract("collector-rules.schema.json", rules)
    selector = rules["strategies"][0]["item_links"]
    links = extract_hrefs(
        html.fromstring((rules_dir / "tests/listing-links/page.html").read_text(encoding="utf-8")),
        selector_type=selector["type"],
        selector=selector["value"],
    )
    assert links == _json(rules_dir / "tests/listing-links/expected.json")
    scope = Scope.from_rules(rules)
    assert scope is not None
    for url in links + rules["strategies"][0]["start_urls"]:
        assert scope.check(url) is None, url
    for url in (
        "https://auto.ria.com/uk/news/",
        "https://auto.ria.com/bff/auto/123",
        "https://auto.ria.com/uk/newauto/",
        "https://example.org/uk/auto_bmw_x5_40065331.html",
    ):
        assert scope.check(url) is not None, url
    assert rules["robots"]["mode"] == "respect"
    assert rules["limits"]["rate"]["requests_per_second_per_host"] == 1
    print("PASS collector: detail links, unrelated URL exclusions, robots and 1 request/s configuration")

    evidence = _json(automarket / "evidence/autoria.json")
    catalog = evidence["catalog"]
    catalog_fixture = automarket / catalog["fixture"]
    assert hashlib.sha256(catalog_fixture.read_bytes()).hexdigest() == catalog["fixture_sha256"]
    assert links == catalog["links"]
    assert len(links) == catalog["matched_links"] == 21
    assert len(set(links)) == catalog["unique_links"] == 21
    if args.live_samples:
        meta_path = next(
            p for p in args.live_samples.glob("*.meta.json") if _json(p)["requested_url"] == catalog["url"]
        )
        meta = _json(meta_path)
        assert (
            hashlib.sha256((args.live_samples / meta["raw_file"]).read_bytes()).hexdigest()
            == catalog["raw_sha256"]
        )
        raw_links = extract_hrefs(
            html.fromstring((args.live_samples / meta["utf8_file"]).read_text(encoding="utf-8")),
            selector_type=selector["type"],
            selector=selector["value"],
        )
        assert [urljoin(catalog["url"], link) for link in raw_links] == links
    print("PASS live catalog comparison: 21 unique detail URLs from configured search selector")
    for sample in evidence["samples"]:
        fixture = automarket / sample["fixture"]
        assert hashlib.sha256(fixture.read_bytes()).hexdigest() == sample["fixture_sha256"]
        result = run_local(package_dir, file=fixture, url=sample["url"])
        fields = result["output"]["entities"][0]["fields"]
        assert all(fields.get(k) == v for k, v in sample["manual_assertions"].items())
        assert fields["equipment"] == sample["equipment"]
        assert result["diagnostics"] == sample["diagnostics"]
        if args.live_samples:
            meta_path = next(
                p for p in args.live_samples.glob("*.meta.json") if _json(p)["requested_url"] == sample["url"]
            )
            meta = _json(meta_path)
            raw = args.live_samples / meta["raw_file"]
            assert hashlib.sha256(raw.read_bytes()).hexdigest() == sample["raw_sha256"]
            live = run_local(package_dir, file=args.live_samples / meta["utf8_file"], url=sample["url"])
            assert live["status"] == sample["result_status"] == "success"
            assert live["output"]["entities"][0]["fields"] == sample["fields"] | {
                "description": live["output"]["entities"][0]["fields"]["description"]
            }
        print(f"PASS manual source comparison: ad {sample['natural_key']['ad_id']}")
    print(
        f"{passed} fixture cases passed; {entities_checked} entity fields validated; 3 source comparisons passed"
    )


if __name__ == "__main__":
    main()
