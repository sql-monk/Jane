"""Verify observed detail fields and the unchanged legacy golden cases."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO = Path(__file__).resolve().parents[5]
PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "libs/extractor-sdk/src"))
sys.path.insert(0, str(REPO / "services/web-collector/src"))

from jane_extractor_sdk.testing import run_local, run_package_tests  # noqa: E402
from jane_web_collector.urls import Normalizer, Scope, UrlPattern  # noqa: E402


def main() -> None:
    cases = run_package_tests(PACKAGE)
    validator = Draft202012Validator(
        json.loads((PACKAGE / "schemas/car_ad.schema.json").read_text(encoding="utf-8"))
    )
    for case in cases:
        assert case.passed, f"{case.name}: {case.result}; {case.differences}"
        for entity in case.result.get("output", {}).get("entities", []):
            validator.validate(entity["fields"])
        print(f"PASS {case.name}: {case.actual_status}")

    resources = []
    for file in (REPO / "contracts/schemas").rglob("*.json"):
        resources.append(
            (file.as_uri(), Resource.from_contents(json.loads(file.read_text(encoding="utf-8"))))
        )
    registry = Registry().with_resources(resources)
    for directory in [PACKAGE, PACKAGE.parent / "autos.rst-rules"]:
        manifest = json.loads((directory / "jane-package.json").read_text(encoding="utf-8"))
        Draft202012Validator(
            {"$ref": (REPO / "contracts/schemas/package-manifest.schema.json").as_uri()}, registry=registry
        ).validate(manifest)
    rules = json.loads((PACKAGE.parent / "autos.rst-rules/rules.json").read_text(encoding="utf-8"))
    Draft202012Validator(
        {"$ref": (REPO / "contracts/schemas/collector-rules.schema.json").as_uri()}, registry=registry
    ).validate(rules)
    scope = Scope.from_rules(rules)
    assert scope is not None
    normalizer = Normalizer.from_rules(rules)
    for source in [
        "https://rst.ua/ukr/oldcars/",
        "https://rst.ua/ukr/oldcars/2.html",
        "https://rst.ua/ukr/oldcars/gmc/acadia/gmc_acadia_15481914.html",
    ]:
        canonical = normalizer.normalize(source)
        assert canonical is not None and scope.check(canonical) is None
        for section in rules["sections"]:
            matched = any(UrlPattern.from_rule(pattern).matches(canonical) for pattern in section["patterns"])
            assert matched == (("gmc_acadia" in source) == (section["section_id"] == "ad"))
    assert scope.check("https://evil.example/ukr/oldcars/") is not None
    assert scope.check("https://rst.ua/ukr/new/example/") is not None
    print("PASS manifest schemas, collector rules, full canonical URL sections and scope")

    samples = []
    for name in ["gmc-acadia-live", "mercedes-sprinter-live", "nissan-qashqai-live"]:
        case = next(case for case in cases if case.name == name)
        fields = case.result["output"]["entities"][0]["fields"]
        metadata = json.loads((PACKAGE / "tests" / name / "source.json").read_text(encoding="utf-8"))
        raw = (PACKAGE / "tests" / name / "page.html").read_bytes()
        assert metadata["sha256"] == hashlib.sha256(raw).hexdigest()
        assert metadata["status"] == 200 and not metadata["redirect_history"]
        if name == "gmc-acadia-live":
            assert len(fields["equipment"]) == 28 and len(fields["photos"]) == 11
            assert len(fields["description_full"]) > 500
        elif name == "mercedes-sprinter-live":
            assert "vin" not in fields and "equipment" not in fields
            assert len(fields["registration_history"]) == 3 and len(fields["photos"]) == 11
        else:
            assert len(fields["photos"]) == 13
            assert all(
                key not in fields for key in ["vin", "vin_masked", "equipment", "registration_history"]
            )
        limited = run_local(
            PACKAGE,
            file=PACKAGE / "tests" / name / "page.html",
            url=fields["url"],
            params={"full_description_max_chars": 0, "photos_max_items": 0, "equipment_max_items": 0},
        )
        assert limited["status"] == "success"
        assert all(
            key not in limited["output"]["entities"][0]["fields"]
            for key in ["description_full", "photos", "equipment"]
        )
        samples.append({"source": metadata, "fields": fields})
    print("PASS live values, source SHA-256, omitted unavailable fields and configured limits")
    print(f"{len(cases)} passed; entity_schema_errors=0; verified_live_entities={len(samples)}")
    evidence: dict[str, Any] = {
        "site": "rst.ua",
        "status": "verified",
        "package": {"package_id": "autos.rst-car-ads", "version": "1.1.0"},
        "rules": {"package_id": "autos.rst-rules", "version": "1.1.0"},
        "checks": {
            "local_sdk_cases_passed": len(cases),
            "entity_schema_errors": 0,
            "verified_live_entities": len(samples),
            "sha256_checked": True,
            "manifest_and_rules_valid": True,
            "legacy_exact_cases_preserved": True,
            "omitted_unavailable_fields": True,
            "configured_limits_checked": True,
        },
        "samples": samples,
        "limitations": [
            "Оснащення, опис та історія реєстрації є твердженнями продавця/сайту, а не незалежною перевіркою автомобіля.",
            "Прихований VIN не відновлюється. Платні або приховані звіти й телефони не отримуються.",
            "GMC: структурований пробіг 33000 км, опис продавця містить 35 тис. км; обидва значення збережені без підміни.",
        ],
    }
    runtime = REPO / ".jane/rst-runtime-test.json"
    if runtime.is_file():
        report = json.loads(runtime.read_text(encoding="utf-8"))
        evidence["runtime_cli_test"] = {key: report.get(key) for key in ["passed", "failed", "package"]}
        evidence["runtime_cli_test"]["backend"] = "subprocess, local trusted-code validation"
    destination = REPO / "examples/automarket/evidence/rst.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
