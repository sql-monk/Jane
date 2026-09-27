"""Package test runs without writing to working data (``POST /v1/test-runs``, CLI ``test``).

Every case (manifest ``tests`` and ``extra_cases``) is a separate sandbox run in ``test_mode``; the result is a
``TestReport`` (``handler-result.schema.json#/$defs/TestReport``).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Literal, cast

from jane_extractor_sdk.compare import compare_output
from jane_extractor_sdk.package import PackageError, case_input, read_package_file
from jane_kit.errors import JaneError, NotFound, ValidationFailed

from .executor import Executor, now_rfc3339
from .packages import LoadedPackage

__all__ = ["CaseSpec", "run_tests", "select_cases"]

CaseSpec = dict[str, Any]
"""``{"name", "input": HandlerInput, "params", "expected_status", "expected": HandlerOutput | None, "compare"}``"""


def select_cases(
    package: LoadedPackage,
    tests: str | Sequence[str] | None = "all",
    extra_cases: Sequence[Mapping[str, Any]] = (),
) -> list[CaseSpec]:
    """Manifest tests (``all`` / ``none`` / names) + extra cases, with inputs and expected outputs loaded."""
    manifest_tests = list(package.manifest.get("tests") or [])
    if tests is None or tests == "all":
        chosen = manifest_tests
    elif tests == "none":
        chosen = []
    else:
        names = list(tests)
        known = {t["name"] for t in manifest_tests}
        missing = [n for n in names if n not in known]
        if missing:
            raise NotFound(f"tests not found in the manifest: {missing}")
        chosen = [t for t in manifest_tests if t["name"] in names]
    cases: list[CaseSpec] = []
    for test in chosen:
        try:
            handler_input = case_input(package.root, test)
            expected = None
            if test.get("expected"):
                expected = json.loads(read_package_file(package.root, str(test["expected"])))
        except (PackageError, ValueError) as exc:
            raise ValidationFailed(f"test {test['name']!r}: {exc}") from exc
        cases.append(
            {
                "name": test["name"],
                "input": handler_input,
                "params": test.get("params"),
                "expected_status": test["expected_status"],
                "expected": expected,
                "compare": test.get("compare", "exact"),
            }
        )
    for extra in extra_cases:
        cases.append(
            {
                "name": extra["name"],
                "input": dict(extra["input"]),
                "params": extra.get("params"),
                "expected_status": extra["expected_status"],
                "expected": extra.get("expected"),
                "compare": extra.get("compare", "exact"),
            }
        )
    if not cases:
        raise ValidationFailed("no test cases to run")
    return cases


async def run_tests(
    executor: Executor,
    package: LoadedPackage,
    cases: Sequence[CaseSpec],
    *,
    params: Mapping[str, Any] | None = None,
    limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    started_at = now_rfc3339()
    results: list[dict[str, Any]] = []
    for case in cases:
        invocation = {
            "handler": {"package_id": package.manifest["package_id"], "version": package.manifest["version"]},
            "params": {**dict(params or {}), **dict(case.get("params") or {})},
            "inputs": [case["input"]],
            "context": {"test_mode": True},
            "delivery": {"delivery_key": f"test:{case['name']}"},
            "limits": dict(limits or {}),
        }
        entry: dict[str, Any] = {"name": case["name"], "expected_status": case["expected_status"]}
        full_result = True
        try:
            prep = await executor.prepare(invocation, package=package, test_mode=True)
            result = await executor.run(prep)
        except JaneError as exc:
            if exc.error_code == "service_unavailable":
                raise
            # The case could not start (invalid params, unsupported input): failed without a sandbox run.
            on_params = any((e.pointer or "").startswith("/params") for e in exc.errors or [])
            kind = "invalid_params" if on_params else "execution_error"
            result = {"status": "failed", "failure": {"kind": kind, "message": str(exc)}}
            full_result = False
        entry["actual_status"] = result["status"]
        differences: list[dict[str, Any]] = []
        if result["status"] != case["expected_status"]:
            differences.append(
                {"pointer": "/status", "expected": case["expected_status"], "actual": result["status"]}
            )
        elif case.get("expected") is not None:
            mode = cast(Literal["exact", "subset"], case.get("compare") or "exact")
            differences = compare_output(case["expected"], result.get("output"), mode)
        if not full_result:
            differences.append({"pointer": "/failure", "expected": None, "actual": result["failure"]})
        entry["passed"] = not differences or (not full_result and case["expected_status"] == "failed")
        if differences:
            entry["differences"] = differences
        if full_result:
            entry["result"] = result
        results.append(entry)
    passed = sum(1 for r in results if r["passed"])
    return {
        "package": package.ref,
        "passed": passed,
        "failed": len(results) - passed,
        "cases": results,
        "started_at": started_at,
        "finished_at": now_rfc3339(),
    }
