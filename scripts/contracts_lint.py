"""Lint `contracts/`: OpenAPI 3.1 documents and JSON Schema 2020-12 files.

* ``openapi*.yaml|yml|json`` -> openapi-spec-validator (3.1) + every ``$ref`` resolvable;
* other ``*.schema.json|yaml`` / files under ``schemas/`` with ``$schema`` -> Draft 2020-12 meta-schema;
* everything must parse as YAML/JSON (UTF-8).

CONNECTION POINT (WP-00): if WP-00 adds its own linter config (e.g. ``contracts/.spectral.yaml`` or
``contracts/lint.py``), call it from ``extra_linters`` below.
Exit code 0 when there is nothing to lint (before WP-00 is merged).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def extra_linters() -> list[list[str]]:
    cmds = []
    if (CONTRACTS / "lint.py").is_file():
        cmds.append([sys.executable, str(CONTRACTS / "lint.py")])
    return cmds


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    if not CONTRACTS.is_dir():
        print("contracts lint: no contracts/ directory yet (WP-00) - nothing to check")
        return 0
    files = sorted(p for p in CONTRACTS.rglob("*") if p.is_file() and p.suffix in {".yaml", ".yml", ".json"})
    errors: list[str] = []
    specs = schemas = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            doc = load(path)
        except (yaml.YAMLError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{rel}: does not parse: {exc}")
            continue
        if not isinstance(doc, dict):
            continue
        if "openapi" in doc:
            specs += 1
            if not str(doc["openapi"]).startswith("3.1"):
                errors.append(f"{rel}: OpenAPI {doc['openapi']} - contracts must be 3.1")
                continue
            try:
                spec_dict, base_uri = read_from_filename(str(path))
                validate(spec_dict, base_uri=base_uri)
            except Exception as exc:
                errors.append(f"{rel}: invalid OpenAPI: {str(exc).splitlines()[0]}")
        elif "$schema" in doc:
            schemas += 1
            if "2020-12" not in str(doc["$schema"]):
                errors.append(f"{rel}: $schema must be JSON Schema 2020-12")
                continue
            try:
                Draft202012Validator.check_schema(doc)
            except SchemaError as exc:
                errors.append(f"{rel}: invalid JSON Schema: {exc.message}")
    code = 0
    for cmd in extra_linters():
        code = max(code, subprocess.run(cmd, cwd=ROOT, check=False).returncode)
    for e in errors:
        print(f"ERROR {e}")
    print(
        f"contracts lint: {len(files)} file(s), {specs} OpenAPI, {schemas} JSON Schema, {len(errors)} error(s)"
    )
    return 1 if errors or code else 0


if __name__ == "__main__":
    sys.exit(main())
