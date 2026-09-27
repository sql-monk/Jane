"""Minimal stand-in for handler-runtime test execution (WP-06 owns the real sandbox).

Only the fake handler service and the fake "model" use it, to give the scenarios real pass/fail
results: the extractor code produced in a scenario is actually executed on the materials. It runs
in-process, which is acceptable only because the code comes from the test fixtures below.
"""

from __future__ import annotations

import base64
import copy
import io
import json
import types
import zipfile
from typing import Any

__all__ = [
    "PRODUCT_CODE_V1",
    "PRODUCT_CODE_V2",
    "PRODUCT_CODE_V2_BREAKING",
    "compare",
    "run_code",
    "run_package_tests",
    "unzip",
]

PRODUCT_CODE_V1 = """import html
import re

_SKU = re.compile(r'data-sku="([^"]+)"')
_TITLE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
_PRICE = re.compile(r'class="price"[^>]*>\\s*([0-9]+(?:[.,][0-9]+)?)\\s*([A-Z]{3})')


def extract(material, params, ctx):
    page = ctx.text()
    sku = _SKU.search(page)
    if not sku:
        return {"status": "empty", "entities": []}
    fields = {"sku": sku.group(1)}
    title = _TITLE.search(page)
    if title:
        fields["title"] = html.unescape(title.group(1)).strip()
    key = {"scope": material["source"].get("source_id", "local"), "natural": {"sku": fields["sku"]}}
    price = _PRICE.search(page)
    if not price:
        return {
            "status": "unrecognized",
            "entities": [{"entity_type": "product", "key": key, "fields": fields}],
            "unrecognized": {"partial": True, "reason": "price not found", "signature": "missing-selector:.price"},
            "diagnostics": [{"level": "warning", "code": "extract.missing_selector", "message": "selector .price matched 0 elements", "selector": ".price"}],
        }
    fields["price"] = {"amount": float(price.group(1).replace(",", ".")), "currency": price.group(2)}
    return {"status": "success", "entities": [{"entity_type": "product", "key": key, "fields": fields}]}
"""

PRODUCT_CODE_V2 = PRODUCT_CODE_V1.replace('class="price"', 'class="price(?:-new)?"')

PRODUCT_CODE_V2_BREAKING = PRODUCT_CODE_V2.replace('fields["price"] = ', 'fields["price_value"] = ')


class Ctx:
    def __init__(self, material: dict[str, Any]) -> None:
        self._material = material
        self.logs: list[str] = []

    def bytes(self) -> bytes:
        content = self._material.get("content") or {}
        data = str(content.get("data", ""))
        return base64.b64decode(data) if content.get("encoding") == "base64" else data.encode("utf-8")

    def text(self) -> str:
        return self.bytes().decode("utf-8", errors="replace")

    def log(self, message: str) -> None:
        self.logs.append(message)


def run_code(code: str, material: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
    module = types.ModuleType("jane_fixture_extractor")
    try:
        exec(compile(code, "extractor.py", "exec"), module.__dict__)
        out = module.extract(material, params or {}, Ctx(material))
    except Exception as exc:
        return {
            "status": "failed",
            "failure": {"kind": "execution_error", "message": f"{type(exc).__name__}: {exc}"},
            "entities": [],
        }
    return dict(out)


def unzip(data: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return {n: zf.read(n) for n in zf.namelist()}


def compare(expected: Any, actual: Any, mode: str, pointer: str = "") -> list[dict[str, Any]]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        diffs: list[dict[str, Any]] = []
        keys = set(expected) if mode == "subset" else set(expected) | set(actual)
        for k in sorted(keys - {"observation", "provenance"}):
            if k not in actual or k not in expected:
                diffs.append(
                    {"pointer": f"{pointer}/{k}", "expected": expected.get(k), "actual": actual.get(k)}
                )
            else:
                diffs += compare(expected[k], actual[k], mode, f"{pointer}/{k}")
        return diffs
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [{"pointer": pointer, "expected": len(expected), "actual": len(actual)}]
        return [
            d
            for i, (e, a) in enumerate(zip(expected, actual, strict=True))
            for d in compare(e, a, mode, f"{pointer}/{i}")
        ]
    return [] if expected == actual else [{"pointer": pointer, "expected": expected, "actual": actual}]


def _case(
    name: str,
    code: str,
    material: dict[str, Any],
    params: dict[str, Any] | None,
    expected_status: str,
    expected: dict[str, Any] | None,
    mode: str,
) -> dict[str, Any]:
    out = run_code(code, material, params)
    diffs = []
    if out.get("status") != expected_status:
        diffs.append({"pointer": "/status", "expected": expected_status, "actual": out.get("status")})
    if expected is not None:
        diffs += compare(expected.get("entities", []), out.get("entities", []), mode, "/entities")
    case: dict[str, Any] = {
        "name": name,
        "passed": not diffs,
        "expected_status": expected_status,
        "actual_status": out.get("status", "failed"),
    }
    if diffs:
        case["differences"] = diffs
    return case


def run_package_tests(
    files: dict[str, bytes],
    tests: Any,
    extra_cases: list[dict[str, Any]],
    params: dict[str, Any] | None,
    fail_all: bool = False,
) -> list[dict[str, Any]]:
    manifest = json.loads(files["jane-package.json"])
    module_path = "src/" + manifest["entry"]["module"].replace(".", "/") + ".py"
    code = files[module_path].decode("utf-8")
    cases = []
    selected = manifest.get("tests") or []
    if tests == "none":
        selected = []
    elif isinstance(tests, list):
        selected = [t for t in selected if t["name"] in tests]
    for t in selected:
        inp = t["input"]
        if "material" in inp:
            material = json.loads(files[inp["material"]])
        else:
            data = files[inp["file"]].decode("utf-8")
            material = {
                "source": {"kind": "web"},
                "locator": {"url": inp.get("url", "https://local.test/")},
                "content": {
                    "kind": "inline",
                    "encoding": "utf-8",
                    "media_type": inp.get("media_type", "text/html"),
                    "data": data,
                },
            }
        expected = json.loads(files[t["expected"]]) if t.get("expected") else None
        cases.append(
            _case(
                t["name"],
                code,
                material,
                {**(t.get("params") or {}), **(params or {})},
                t["expected_status"],
                expected,
                t.get("compare", "exact"),
            )
        )
    for c in extra_cases:
        cases.append(
            _case(
                c["name"],
                code,
                copy.deepcopy(c["input"]["material"]),
                {**(c.get("params") or {}), **(params or {})},
                c["expected_status"],
                c.get("expected"),
                c.get("compare", "exact"),
            )
        )
    if fail_all:
        for c in cases:
            c["passed"] = False
            c.setdefault("differences", []).append(
                {"pointer": "/params", "expected": "compatible", "actual": "binding params rejected"}
            )
    return cases
