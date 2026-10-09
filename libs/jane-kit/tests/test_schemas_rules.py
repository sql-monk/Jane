"""Shared contract schema validation and collector rules loading (R17)."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from jane_kit.contracts import contracts_dir
from jane_kit.errors import JaneError, ValidationFailed
from jane_kit.rules import CollectorSchemas, RulesLoader
from jane_kit.schemas import ContractSchemas, ContractsNotFound, json_pointer

ROOT = contracts_dir(Path(__file__).parent)
pytestmark = pytest.mark.skipif(ROOT is None, reason="contracts/ not found")
EXAMPLES = (ROOT / "examples") if ROOT else Path()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_schemas_validate_with_pointers_and_codes() -> None:
    assert ROOT is not None
    schemas = ContractSchemas(ROOT)
    material = load(
        EXAMPLES
        / "schemas"
        / "material"
        / next(iter(sorted(p.name for p in (EXAMPLES / "schemas" / "material").glob("*.json"))))
    )
    assert schemas.field_errors("material.schema.json", material) == []
    broken = {**material, "content": {"kind": "inline"}, "a/b": 1}
    errors = schemas.field_errors("material.schema.json", broken, "/inputs/0/material", best=True, limit=50)
    assert errors and all(e.pointer and e.pointer.startswith("/inputs/0/material") for e in errors)
    assert all(e.code == "schema" for e in errors)
    with pytest.raises(ValidationFailed) as exc:
        schemas.validate("material.schema.json", broken, detail="bad material")
    assert exc.value.detail == "bad material" and exc.value.errors
    report = schemas.field_errors("handler-result.schema.json#/$defs/TestReport", {}, limit=1)
    assert len(report) == 1 and report[0].pointer == "/"
    assert json_pointer(["a/b", "c~d", 0], "/p") == "/p/a~1b/c~0d/0"


def test_openapi_components_and_request_bodies() -> None:
    assert ROOT is not None
    schemas = ContractSchemas(ROOT, openapi="orchestrator.v1.yaml")
    uri = schemas.request_schema_uri("PUT", "/v1/sources/shop")
    assert uri.startswith("file://") and "#" in uri
    assert schemas.field_errors(uri, {"source_id": "shop"})  # missing required fields


def test_locate_names_the_setting(tmp_path: Path) -> None:
    with pytest.raises(ContractsNotFound, match="JANE_X_CONTRACTS_DIR"):
        ContractSchemas.locate(tmp_path, setting="JANE_X_CONTRACTS_DIR")
    assert ROOT is not None
    found = ContractSchemas.locate(
        None, setting="S", marker="schemas/package-manifest.schema.json", start=Path(__file__).parent
    )
    assert found.root.resolve() == ROOT.resolve()


def test_collector_rules_errors_follow_the_discriminator() -> None:
    assert ROOT is not None
    schemas = CollectorSchemas.locate_collector(None, setting="S", start=Path(__file__).parent)
    for example in sorted((EXAMPLES / "schemas" / "collector-rules").glob("*.json")):
        assert schemas.rules_errors(load(example)) == [], example.name
    rules = load(EXAMPLES / "schemas" / "collector-rules" / "web-shop.json")
    rules["strategies"][0]["max_depthh"] = 1
    errors = schemas.rules_errors(rules, ["rules"])
    assert errors and errors[0].pointer is not None and errors[0].pointer.startswith("/rules/strategies/0")
    assert errors[0].code == "unevaluated_properties"  # the branch of the strategy type, not the oneOf
    assert schemas.errors(schemas.component("CollectionRequest"), {}) != []


def package(tmp_path: Path, rules: dict[str, Any], *, kind: str = "collector-rules") -> dict[str, Any]:
    manifest = {
        "package_id": "shop-rules",
        "version": "1.0.0",
        "kind": kind,
        "entry": {"rules": "rules.json"},
    }
    directory = tmp_path / "rules" / "shop-rules" / "1.0.0"
    directory.mkdir(parents=True)
    (directory / "jane-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    (directory / "rules.json").write_text(json.dumps(rules), encoding="utf-8")
    return manifest


async def test_rules_loader_local_directory_and_archive(tmp_path: Path) -> None:
    rules = {"collector": "web", "strategies": []}
    manifest = package(tmp_path, rules)
    loader = RulesLoader(
        rules_dir=tmp_path / "rules",
        registry_url=None,
        registry_token_env=None,
        timeout_s=1,
        settings_prefix="JANE_T_",
    )
    ref = {"package_id": "shop-rules", "version": "1.0.0"}
    assert await loader.load(ref) == rules
    with pytest.raises(ValidationFailed, match="digest"):
        await loader.load({**ref, "digest": "sha256:" + "0" * 64})  # an unpacked directory cannot be verified
    archive = tmp_path / "zips" / "shop-rules-2.0.0.zip"
    archive.parent.mkdir()
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("jane-package.json", json.dumps({**manifest, "version": "2.0.0"}))
        zf.writestr("rules.json", json.dumps(rules))
    zipped = RulesLoader(rules_dir=archive.parent, registry_url=None, registry_token_env=None, timeout_s=1)
    digest = "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()
    assert await zipped.load({"package_id": "shop-rules", "version": "2.0.0", "digest": digest}) == rules
    with pytest.raises(JaneError) as exc:
        await zipped.load({"package_id": "shop-rules", "version": "2.0.0", "digest": "sha256:" + "1" * 64})
    assert exc.value.error_code == "digest_mismatch"
    with pytest.raises(ValidationFailed) as missing:
        await loader.load({"package_id": "other", "version": "1.0.0"})
    assert "JANE_T_RULES_DIR" in str(missing.value.errors)
    assert loader.sources() == ["inline", "local_dir"]


async def test_rules_loader_refuses_wrong_packages(tmp_path: Path) -> None:
    package(tmp_path, {"collector": "web"}, kind="extractor")
    loader = RulesLoader(
        rules_dir=tmp_path / "rules", registry_url=None, registry_token_env=None, timeout_s=1
    )
    with pytest.raises(ValidationFailed, match="not collector-rules"):
        await loader.load({"package_id": "shop-rules", "version": "1.0.0"})


async def test_registry_token_must_be_a_header_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_SECRET_T", "bad\nvalue")
    loader = RulesLoader(
        rules_dir=None,
        registry_url="http://registry.invalid",
        registry_token_env="JANE_SECRET_T",
        timeout_s=1,
    )
    with pytest.raises(JaneError, match="not valid for an HTTP header"):
        await loader.load({"package_id": "p", "version": "1.0.0"})
