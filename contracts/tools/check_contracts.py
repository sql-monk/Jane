# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "jsonschema[format-nongpl]>=4.23,<5",
#   "referencing>=0.35",
#   "pyyaml>=6",
#   "openapi-spec-validator>=0.7.1,<0.8",
# ]
# ///
"""Contract linter for Jane: one command, non-zero exit on any problem.

    uv run contracts/tools/check_contracts.py [--no-redocly | --require-redocly]

Checks:
  1. every JSON Schema is valid against the 2020-12 meta-schema and all $refs resolve;
  2. every OpenAPI document is valid OpenAPI 3.1 (openapi-spec-validator);
  3. Jane conventions (/v1 prefix, operationId, problem+json errors, Idempotency-Key on POST,
     202 -> Job, examples present for request bodies and success responses);
  4. every example (inline in OpenAPI, $ref'd Example Objects, contracts/examples/schemas/**)
     validates against its schema; every contracts/examples/invalid/** example is rejected;
  5. Python interfaces in contracts/python compile and import;
  6. tools/mock.py can serve a success example for every operation of every API;
  7. Redocly lint (npx @redocly/cli) if Node is available (required with --require-redocly).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    CONTRACTS_DIR,
    EXAMPLES_DIR,
    OPENAPI_DIR,
    SCHEMAS_DIR,
    deref,
    iter_operations,
    load_file,
    openapi_files,
    pointer_escape,
)
from jsonschema import Draft202012Validator  # noqa: E402
from jsonschema.exceptions import SchemaError  # noqa: E402

REDOCLY = "@redocly/cli@2.54.3"
PROBLEM_SCHEMA_SUFFIX = "schemas/common/problem.schema.json"
JOB_SCHEMA_SUFFIX = "schemas/common/job.schema.json"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.counts: dict[str, int] = {}

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def count(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n


def rel(path: Path | str) -> str:
    p = Path(path)
    try:
        return p.resolve().relative_to(CONTRACTS_DIR.parent).as_posix()
    except ValueError:
        return str(p)


def validator_for(ref_uri: str, registry) -> Draft202012Validator:
    return Draft202012Validator(
        {"$schema": "https://json-schema.org/draft/2020-12/schema", "$ref": ref_uri},
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def first_errors(validator: Draft202012Validator, instance: Any, limit: int = 3) -> list[str]:
    out = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        loc = "/" + "/".join(str(p) for p in err.absolute_path)
        out.append(f"{loc}: {err.message[:300]}")
        if len(out) >= limit:
            break
    return out


# 1. JSON Schemas -----------------------------------------------------------------------------

def walk_refs(node: Any):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            yield ref
        for v in node.values():
            yield from walk_refs(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_refs(v)


def check_schemas(report: Report, registry) -> None:
    for path in sorted(SCHEMAS_DIR.rglob("*.json")):
        report.count("schemas")
        try:
            schema = load_file(path)
        except Exception as exc:  # noqa: BLE001
            report.error(f"{rel(path)}: cannot parse: {exc}")
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            report.error(f"{rel(path)}: invalid JSON Schema: {exc.message}")
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            report.error(f"{rel(path)}: $schema must be JSON Schema 2020-12")
        resolver = registry.resolver(base_uri=path.as_uri())
        for ref in walk_refs(schema):
            try:
                resolver.lookup(ref)
            except Exception as exc:  # noqa: BLE001
                report.error(f"{rel(path)}: unresolvable $ref {ref!r}: {exc}")


# 2. OpenAPI structural validation --------------------------------------------------------------

def check_openapi_valid(report: Report) -> None:
    from openapi_spec_validator import validate
    from openapi_spec_validator.readers import read_from_filename

    for path in [OPENAPI_DIR / "common.yaml", *openapi_files()]:
        report.count("openapi_documents")
        try:
            spec, base_uri = read_from_filename(str(path))
            validate(spec, base_uri=path.as_uri())
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).splitlines()[0] if str(exc) else repr(exc)
            report.error(f"{rel(path)}: invalid OpenAPI 3.1: {msg[:500]}")


# 3 + 4. Conventions and examples --------------------------------------------------------------

def ref_target_uri(node: Any, base_uri: str) -> str | None:
    """Absolute URI a schema node points to, if it is a pure $ref."""
    from urllib.parse import urljoin

    if isinstance(node, dict) and "$ref" in node:
        return urljoin(base_uri, node["$ref"])
    return None


def schema_points_to(schema: Any, base_uri: str, suffix: str) -> bool:
    seen = 0
    node, uri = schema, base_uri
    while isinstance(node, dict) and "$ref" in node and seen < 10:
        target = ref_target_uri(node, uri)
        if target and target.split("#")[0].endswith(suffix) and (target.split("#")[1] if "#" in target else "") in ("", "/"):
            return True
        from _common import resolve_ref

        node, uri = resolve_ref(node["$ref"], uri)
        seen += 1
    return False


def collect_examples(media: dict, media_uri: str) -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if "example" in media:
        out.append(("example", media["example"]))
    for name, ex in (media.get("examples") or {}).items():
        ex_node, _ = deref(ex, media_uri)
        if isinstance(ex_node, dict) and "value" in ex_node:
            out.append((name, ex_node["value"]))
    return out


def check_media(report: Report, registry, where: str, media_type: str, media: dict, media_uri: str,
                media_pointer: str) -> int:
    """Validate all examples of one media type object. Returns number of examples."""
    examples = collect_examples(media, media_uri)
    if "schema" not in media:
        return len(examples)
    schema_uri = f"{media_uri.split('#')[0]}#{media_pointer}/schema"
    try:
        validator = validator_for(schema_uri, registry)
    except Exception as exc:  # noqa: BLE001
        report.error(f"{where} {media_type}: cannot build validator: {exc}")
        return len(examples)
    for name, value in examples:
        report.count("openapi_examples")
        try:
            errs = first_errors(validator, value)
        except Exception as exc:  # noqa: BLE001
            report.error(f"{where} {media_type} example '{name}': validation crashed: {exc}")
            continue
        for e in errs:
            report.error(f"{where} {media_type} example '{name}' invalid at {e}")
    return len(examples)


def node_pointer(uri: str) -> str:
    return uri.split("#", 1)[1] if "#" in uri else ""


def check_openapi_conventions(report: Report, registry) -> None:
    for path in openapi_files():
        doc = load_file(path)
        doc_uri = path.as_uri()
        name = path.name
        if not (doc.get("info") or {}).get("version"):
            report.error(f"{name}: info.version is required")
        if "bearerAuth" not in ((doc.get("components") or {}).get("securitySchemes") or {}):
            report.error(f"{name}: components.securitySchemes.bearerAuth is required")
        if not doc.get("security"):
            report.error(f"{name}: top-level security requirement is required")
        op_ids: set[str] = set()
        for api_path, method, op, item_uri, _item in iter_operations(doc, doc_uri):
            report.count("operations")
            where = f"{name} {method.upper()} {api_path}"
            if not api_path.startswith("/v1/"):
                report.error(f"{where}: path must start with /v1/")
            op_id = op.get("operationId")
            if not op_id:
                report.error(f"{where}: operationId is required")
            elif op_id in op_ids:
                report.error(f"{where}: duplicate operationId {op_id}")
            else:
                op_ids.add(op_id)
            for key in ("summary", "tags", "responses"):
                if not op.get(key):
                    report.error(f"{where}: '{key}' is required")
            op_ptr = f"{node_pointer(item_uri)}/{method}" if "#" in item_uri else f"/paths/{pointer_escape(api_path)}/{method}"
            op_uri = f"{item_uri.split('#')[0]}#{op_ptr}"

            # Idempotency-Key on POST with side effects
            if method == "post":
                params = [deref(p, op_uri)[0] for p in op.get("parameters") or []]
                has_key = any(p.get("in") == "header" and p.get("name") == "Idempotency-Key" for p in params)
                if not has_key and not op.get("x-jane-no-idempotency-key"):
                    report.error(f"{where}: POST must declare Idempotency-Key header or x-jane-no-idempotency-key: <reason>")

            # Request body examples
            body = op.get("requestBody")
            if body:
                body_node, body_uri = deref(body, op_uri)
                body_ptr = node_pointer(body_uri) if body_node is not body else f"{op_ptr}/requestBody"
                for mt, media in (body_node.get("content") or {}).items():
                    n = check_media(report, registry, where + " request", mt, media, body_uri,
                                    f"{body_ptr}/content/{pointer_escape(mt)}")
                    if n == 0 and ("json" in mt):
                        report.error(f"{where}: request body {mt} needs at least one example")

            # Responses
            responses = op.get("responses") or {}
            secured = op.get("security", doc.get("security")) not in ([], [{}])
            if secured and "401" not in {str(c) for c in responses}:
                report.error(f"{where}: secured operation must declare a 401 response")
            success_examples = 0
            success_json = False
            for code, resp in responses.items():
                resp_node, resp_uri = deref(resp, op_uri)
                resp_ptr = node_pointer(resp_uri) if resp_node is not resp else f"{op_ptr}/responses/{code}"
                content = resp_node.get("content") or {}
                code_s = str(code)
                if code_s.startswith(("4", "5")) and not op.get("x-jane-health"):
                    for mt in content:
                        if mt != "application/problem+json":
                            report.error(f"{where} {code_s}: error responses must use application/problem+json (got {mt})")
                        elif not schema_points_to(content[mt].get("schema"), resp_uri, PROBLEM_SCHEMA_SUFFIX):
                            report.error(f"{where} {code_s}: error schema must be the common Problem schema")
                if code_s == "202":
                    media = content.get("application/json")
                    if not media or not schema_points_to(media.get("schema"), resp_uri, JOB_SCHEMA_SUFFIX):
                        report.error(f"{where} 202: body must be the common Job schema")
                for mt, media in content.items():
                    n = check_media(report, registry, f"{where} {code_s}", mt, media, resp_uri,
                                    f"{resp_ptr}/content/{pointer_escape(mt)}")
                    if code_s.startswith("2") and "json" in mt:
                        success_json = True
                        success_examples += n
            if success_json and success_examples == 0:
                report.error(f"{where}: success response needs at least one example")


def example_target(example_path: Path, root: Path) -> tuple[Path, str]:
    """examples/schemas/<rel>/<file>.json -> (schemas/<rel>.schema.json, pointer)."""
    rel_dir = example_path.parent.relative_to(root).as_posix()
    pointer = ""
    if "@" in rel_dir:
        rel_dir, def_name = rel_dir.rsplit("@", 1)
        pointer = f"/$defs/{def_name}"
    return SCHEMAS_DIR / f"{rel_dir}.schema.json", pointer


def check_schema_examples(report: Report, registry) -> None:
    valid_root = EXAMPLES_DIR / "schemas"
    invalid_root = EXAMPLES_DIR / "invalid" / "schemas"
    for root, expect_valid in ((valid_root, True), (invalid_root, False)):
        if not root.exists():
            continue
        for ex in sorted(root.rglob("*.json")):
            report.count("schema_examples" if expect_valid else "invalid_examples")
            schema_path, pointer = example_target(ex, root)
            if not schema_path.exists():
                report.error(f"{rel(ex)}: no schema {rel(schema_path)} for this example")
                continue
            validator = validator_for(f"{schema_path.as_uri()}#{pointer}", registry)
            instance = load_file(ex)
            errs = first_errors(validator, instance)
            if expect_valid:
                for e in errs:
                    report.error(f"{rel(ex)} invalid against {rel(schema_path)}{('#' + pointer) if pointer else ''} at {e}")
            elif not errs:
                report.error(f"{rel(ex)}: expected to be REJECTED by {rel(schema_path)} but it is valid")


# 5. Python interfaces --------------------------------------------------------------------------

def check_python(report: Report) -> None:
    for py in sorted((CONTRACTS_DIR / "python").rglob("*.py")):
        report.count("python_files")
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as exc:
            report.error(f"{rel(py)}:{exc.lineno}: {exc.msg}")
    src = CONTRACTS_DIR / "python" / "src"
    if src.exists():
        import importlib

        sys.path.insert(0, str(src))
        for mod in ("jane_contracts", "jane_contracts.discovery", "jane_contracts.storage_adapter"):
            try:
                importlib.import_module(mod)
            except Exception as exc:  # noqa: BLE001
                report.error(f"import {mod} failed: {exc!r}")


# 6. Mock routes ------------------------------------------------------------------------------

def check_mock_routes(report: Report) -> None:
    """Every operation of every API can be served by tools/mock.py with a success response."""
    import mock
    from _common import API_NAMES

    for api in API_NAMES:
        for route in mock.load_routes(api):
            report.count("mock_routes")
            try:
                code, _mt, _body = route.choose({})
            except LookupError as exc:
                report.error(f"mock {api}: {route.method} {route.template}: {exc}")
                continue
            if not 200 <= code < 300:
                report.error(f"mock {api}: {route.method} {route.template}: no success response")


# 7. Redocly ------------------------------------------------------------------------------------

def run_redocly(report: Report, required: bool) -> str:
    npx = shutil.which("npx")
    if not npx:
        if required:
            report.error("redocly: npx not found (Node.js required with --require-redocly)")
        return "skipped (npx not found)"
    cmd = [npx, "--yes", REDOCLY, "lint", "--config", str(CONTRACTS_DIR / "redocly.yaml"),
           *[str(p) for p in openapi_files()]]
    env = {**os.environ, "NO_COLOR": "1", "FORCE_COLOR": "0", "REDOCLY_TELEMETRY": "off"}
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, env=env)
    tail = (proc.stdout + proc.stderr).strip().splitlines()
    if proc.returncode != 0:
        report.error("redocly lint failed:\n    " + "\n    ".join(tail[-40:]))
        return "failed"
    return "ok" + (f" ({tail[-1]})" if tail else "")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--no-redocly", action="store_true", help="skip Redocly lint")
    g.add_argument("--require-redocly", action="store_true", help="fail if Redocly cannot run (use in CI)")
    args = ap.parse_args()

    from _common import build_registry

    report = Report()
    registry = build_registry()
    steps = [
        ("JSON Schema meta-validation and $refs", lambda: check_schemas(report, registry)),
        ("OpenAPI 3.1 validation", lambda: check_openapi_valid(report)),
        ("Jane API conventions and inline examples", lambda: check_openapi_conventions(report, registry)),
        ("Standalone schema examples", lambda: check_schema_examples(report, registry)),
        ("Python interfaces compile", lambda: check_python(report)),
        ("Mock server can serve every operation", lambda: check_mock_routes(report)),
    ]
    for title, fn in steps:
        before = len(report.errors)
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            report.error(f"{title}: crashed: {exc!r}")
        print(f"[{'ok' if len(report.errors) == before else 'FAIL'}] {title}")
    if not args.no_redocly:
        before = len(report.errors)
        status = run_redocly(report, args.require_redocly)
        print(f"[{'ok' if len(report.errors) == before else 'FAIL'}] Redocly lint: {status}")
    else:
        print("[skip] Redocly lint")

    counts = ", ".join(f"{k}={v}" for k, v in sorted(report.counts.items()))
    print(f"\nChecked: {counts}")
    if report.errors:
        print(f"\n{len(report.errors)} problem(s):")
        for e in report.errors:
            print(f"  - {e}")
        return 1
    print("All contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
