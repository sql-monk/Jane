"""Test utilities for extractor authors: run a package in-process, without the sandbox and without services.

This is a fast feedback loop for *trusted* code (your own package in pytest). It does not validate entity
schemas and does not enforce limits or isolation; the authoritative check is the handler-runtime CLI::

    uv run --package jane-handler-runtime jane-handler-runtime test path/to/package

Example (pytest)::

    from pathlib import Path
    from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

    PKG = Path(__file__).parents[1]

    def test_manifest_tests():
        assert_package_tests_pass(PKG)

    def test_one_page():
        result = run_local(PKG, file=PKG / "tests/product/page.html", media_type="text/html")
        assert result["status"] == "success"
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from .compare import compare_output
from .entities import to_entity_record
from .package import case_input, load_manifest, material_from_file, read_package_file
from .runner import execute

__all__ = [
    "LocalCaseResult",
    "apply_param_defaults",
    "assert_package_tests_pass",
    "run_local",
    "run_package_tests",
]


def apply_param_defaults(
    schema: Mapping[str, Any] | None, params: Mapping[str, Any] | None
) -> dict[str, Any]:
    """Top-level ``default`` values of an object ``params_schema`` for parameters that were not given."""
    out = dict(params or {})
    for name, prop in ((schema or {}).get("properties") or {}).items():
        if name not in out and isinstance(prop, Mapping) and "default" in prop:
            out[name] = prop["default"]
    return out


def _params_schema(package_dir: Path, manifest: Mapping[str, Any]) -> dict[str, Any] | None:
    name = manifest.get("params_schema")
    if not name:
        return None
    return cast(dict[str, Any], json.loads(read_package_file(package_dir, str(name))))


def _forget_modules(module: str) -> None:
    top = module.split(".", 1)[0]
    for name in [n for n in sys.modules if n == top or n.startswith(top + ".")]:
        del sys.modules[name]


def run_local(
    package_dir: Path,
    handler_input: Mapping[str, Any] | None = None,
    *,
    file: Path | None = None,
    media_type: str | None = None,
    url: str | None = None,
    params: Mapping[str, Any] | None = None,
    test_mode: bool = True,
) -> dict[str, Any]:
    """Run the entry callable in this process on one input; return a simplified result::

    {"status": "success|empty|unrecognized|failed", "output": {"entities": [...]}, "unrecognized": {...},
     "diagnostics": [...], "error": {...}}
    """
    package_dir = Path(package_dir).resolve()
    manifest = load_manifest(package_dir)
    if handler_input is None:
        if file is None:
            raise ValueError("pass handler_input or file")
        handler_input = {
            "kind": "material",
            "material": material_from_file(file, media_type=media_type, url=url),
        }
    effective = apply_param_defaults(_params_schema(package_dir, manifest), params)
    entry = manifest["entry"]
    _forget_modules(str(entry["module"]))
    request = {
        "protocol": 1,
        "entry": entry,
        "package_dir": str(package_dir),
        "params": effective,
        "test_mode": test_mode,
        "inputs": [{"input": dict(handler_input), "content_file": None}],
    }
    response = execute(request, package_dir)
    raw = response["results"][0]
    if "error" in raw:
        return {"status": "failed", "error": raw["error"], "diagnostics": []}
    material = handler_input.get("material") if handler_input.get("kind") == "material" else None
    key_fields = {
        str(e["entity_type"]): list(e.get("key_fields") or [])
        for e in (manifest.get("output") or {}).get("entities") or []
    }
    output: dict[str, Any] = {}
    if raw.get("entities") or raw.get("status") != "empty":
        output["entities"] = [
            to_entity_record(e, key_fields=key_fields.get(str(e.get("entity_type")), []), material=material)
            for e in raw.get("entities") or []
        ]
    if "data" in raw:
        output["data"] = raw["data"]
    result: dict[str, Any] = {
        "status": raw["status"],
        "output": output,
        "diagnostics": raw.get("diagnostics", []),
    }
    if "unrecognized" in raw:
        result["unrecognized"] = raw["unrecognized"]
    return result


@dataclass
class LocalCaseResult:
    name: str
    passed: bool
    expected_status: str
    actual_status: str
    differences: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)


def run_package_tests(package_dir: Path, names: Iterable[str] | None = None) -> list[LocalCaseResult]:
    """Run the manifest ``tests`` in-process and compare with the expected results."""
    package_dir = Path(package_dir).resolve()
    manifest = load_manifest(package_dir)
    wanted = set(names) if names is not None else None
    out: list[LocalCaseResult] = []
    for case in manifest.get("tests") or []:
        if wanted is not None and case["name"] not in wanted:
            continue
        result = run_local(package_dir, case_input(package_dir, case), params=case.get("params"))
        differences: list[dict[str, Any]] = []
        if case.get("expected") and result["status"] == case["expected_status"]:
            expected = json.loads(read_package_file(package_dir, str(case["expected"])))
            mode = cast(Literal["exact", "subset"], case.get("compare", "exact"))
            differences = compare_output(expected, result.get("output"), mode)
        passed = result["status"] == case["expected_status"] and not differences
        out.append(
            LocalCaseResult(
                case["name"], passed, case["expected_status"], result["status"], differences, result
            )
        )
    return out


def assert_package_tests_pass(package_dir: Path, names: Iterable[str] | None = None) -> None:
    results = run_package_tests(package_dir, names)
    if not results:
        raise AssertionError(f"{package_dir}: no tests in the manifest")
    failed = [r for r in results if not r.passed]
    if failed:
        lines = [
            f"{r.name}: expected {r.expected_status}, got {r.actual_status}; differences={r.differences}; "
            f"error={r.result.get('error')}"
            for r in failed
        ]
        raise AssertionError("package tests failed:\n" + "\n".join(lines))
