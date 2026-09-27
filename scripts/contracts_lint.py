"""Lint `contracts/` (CI stage `contract`).

* If WP-00's linter ``contracts/tools/check_contracts.py`` exists, it is authoritative and is run via
  ``uv run --script`` (schemas, OpenAPI, Jane conventions, examples, Redocly). Redocly needs Node/npx;
  it runs only with ``JANE_CONTRACTS_REDOCLY=1`` (set in CI), otherwise ``--no-redocly`` is passed.
* Fallback (no WP-00 linter): every YAML/JSON parses, documents with ``openapi`` are valid OpenAPI 3.1,
  documents with ``$schema`` are valid JSON Schema 2020-12.
Exit code 0 when there is nothing to lint (before WP-00 is merged). ``JANE_CONTRACTS_DIR`` overrides
the location.
"""

from __future__ import annotations

import json
import os
import shutil
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
CONTRACTS = Path(os.environ.get("JANE_CONTRACTS_DIR") or ROOT / "contracts")
WP00_LINTER = CONTRACTS / "tools" / "check_contracts.py"


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)


def run_wp00_linter() -> int:
    redocly = os.environ.get("JANE_CONTRACTS_REDOCLY") == "1"
    uv = shutil.which("uv")
    cmd = [uv, "run", "--script", str(WP00_LINTER)] if uv else [sys.executable, str(WP00_LINTER)]
    cmd.append("--require-redocly" if redocly else "--no-redocly")
    print("$ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    if not CONTRACTS.is_dir():
        print("contracts lint: no contracts/ directory yet (WP-00) - nothing to check")
        return 0
    if WP00_LINTER.is_file():
        return run_wp00_linter()
    files = sorted(p for p in CONTRACTS.rglob("*") if p.is_file() and p.suffix in {".yaml", ".yml", ".json"})
    errors: list[str] = []
    specs = schemas = 0
    for path in files:
        rel = path.relative_to(CONTRACTS.parent).as_posix()
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
    for e in errors:
        print(f"ERROR {e}")
    print(
        f"contracts lint: {len(files)} file(s), {specs} OpenAPI, {schemas} JSON Schema, {len(errors)} error(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
