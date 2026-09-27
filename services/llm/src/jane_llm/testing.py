"""``POST /v1/test-runs``: package tests without writing to working data (always ``test_mode``)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from jane_kit.errors import NotFound, ValidationFailed
from jane_llm.handler import LlmHandler
from jane_llm.packages import LoadedPackage

_IGNORED = {"observation", "provenance"}


def _ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _strip(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if k not in _IGNORED}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def differences(expected: Any, actual: Any, mode: str, pointer: str = "") -> list[dict[str, Any]]:
    """``exact`` — equal; ``subset`` — every expected value present (extra fields allowed)."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        out = []
        for k, v in expected.items():
            if k not in actual:
                out.append({"pointer": f"{pointer}/{k}", "expected": v, "actual": None})
            else:
                out.extend(differences(v, actual[k], mode, f"{pointer}/{k}"))
        if mode == "exact":
            out.extend(
                {"pointer": f"{pointer}/{k}", "expected": None, "actual": actual[k]}
                for k in actual
                if k not in expected
            )
        return out
    if isinstance(expected, list) and isinstance(actual, list):
        if len(actual) < len(expected) or (mode == "exact" and len(actual) != len(expected)):
            return [{"pointer": pointer, "expected": expected, "actual": actual}]
        out = []
        for i, v in enumerate(expected):
            out.extend(differences(v, actual[i], mode, f"{pointer}/{i}"))
        return out
    return [] if expected == actual else [{"pointer": pointer, "expected": expected, "actual": actual}]


def _test_input(pkg: LoadedPackage, spec: dict[str, Any]) -> dict[str, Any]:
    if "material" in spec:
        return {"kind": "material", "material": pkg.json(spec["material"])}
    if "file" in spec:
        path = spec["file"]
        media = spec.get("media_type") or "text/plain"
        text = pkg.text(path)
        material: dict[str, Any] = {
            "material_id": f"test:{pkg.package_id}:{path}",
            "observation_id": f"obs_test_{uuid.uuid4().hex[:12]}",
            "source": {"kind": "test", "source_id": "local"},
            "locator": {"url": spec["url"]} if spec.get("url") else {},
            "fetched_at": _ts(),
            "format": {"media_type": media},
            "revision": {},
            "content": {"kind": "inline", "media_type": media, "encoding": "utf-8", "data": text},
            "collector": {"name": "test", "version": "0"},
        }
        return {"kind": "material", "material": material}
    if "entities" in spec:
        return {"kind": "entities", "entities": pkg.json(spec["entities"])}
    if "data" in spec:
        return {"kind": "data", "data": pkg.json(spec["data"])}
    raise ValidationFailed(f"unsupported test input {sorted(spec)}")


async def run_tests(handler: LlmHandler, request: dict[str, Any]) -> dict[str, Any]:
    started = _ts()
    ref = request["handler"]
    pkg = await handler.loader.load(ref, request.get("package_archive"))
    selected = request.get("tests", "all")
    cases: list[dict[str, Any]] = []
    for t in pkg.manifest.get("tests") or []:
        if selected == "none" or (isinstance(selected, list) and t["name"] not in selected):
            continue
        cases.append(
            {
                "name": t["name"],
                "input": _test_input(pkg, t["input"]),
                "params": t.get("params"),
                "expected_status": t["expected_status"],
                "expected": pkg.json(t["expected"]) if t.get("expected") else None,
                "compare": t.get("compare", "exact"),
            }
        )
    if isinstance(selected, list):
        missing = set(selected) - {c["name"] for c in cases}
        if missing:
            raise NotFound(f"tests not in the manifest: {sorted(missing)}")
    for extra in request.get("extra_cases") or []:
        cases.append({**extra, "compare": extra.get("compare", "exact"), "expected": extra.get("expected")})

    archive = request.get("package_archive")
    results = []
    for case in cases:
        inv = {
            "handler": {**ref, "digest": pkg.digest},
            "inputs": [case["input"]],
            "params": case.get("params") or request.get("params") or {},
            "context": {"test_mode": True, "trace": {}},
            "delivery": {"delivery_key": f"test-{uuid.uuid4().hex}"},
        }
        if archive is not None:
            inv["package_archive"] = archive
        if request.get("limits"):
            inv["limits"] = request["limits"]
        res = await handler.invoke(inv, force_test_mode=True)
        diffs: list[dict[str, Any]] = []
        if case.get("expected") is not None and res["status"] == case["expected_status"]:
            diffs = differences(_strip(case["expected"]), _strip(res.get("output") or {}), case["compare"])
        passed = res["status"] == case["expected_status"] and not diffs
        results.append(
            {
                "name": case["name"],
                "passed": passed,
                "expected_status": case["expected_status"],
                "actual_status": res["status"],
                "differences": json.loads(json.dumps(diffs)),
                "result": res,
            }
        )
    return {
        "package": {"package_id": pkg.package_id, "version": pkg.version, "digest": pkg.digest},
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "cases": results,
        "started_at": started,
        "finished_at": _ts(),
    }
