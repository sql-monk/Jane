"""Comparison of an expected test output with the actual one (``TestCase.compare``: ``exact`` | ``subset``).

Runtime-added metadata of entities (``observation``, ``provenance``, ``schema``) is ignored on both sides.
Differences are reported as ``{"pointer", "expected", "actual"}`` (``TestCaseResult.differences``).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

__all__ = ["IGNORED_ENTITY_KEYS", "compare_output", "strip_runtime_metadata"]

IGNORED_ENTITY_KEYS = frozenset({"observation", "provenance", "schema"})
_MISSING = object()


def _escape(token: str | int) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def strip_runtime_metadata(output: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(output)
    entities = out.get("entities")
    if isinstance(entities, list):
        out["entities"] = [
            {k: v for k, v in e.items() if k not in IGNORED_ENTITY_KEYS} if isinstance(e, Mapping) else e
            for e in entities
        ]
    return out


def _same_scalar(a: Any, b: Any) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, int | float) and isinstance(b, int | float):
        return a == b
    return type(a) is type(b) and a == b


def _diff(expected: Any, actual: Any, pointer: str, subset: bool, out: list[dict[str, Any]]) -> None:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            out.append({"pointer": pointer or "/", "expected": expected, "actual": actual})
            return
        for key, value in expected.items():
            child = f"{pointer}/{_escape(key)}"
            if key not in actual:
                out.append({"pointer": child, "expected": value, "actual": None})
            else:
                _diff(value, actual[key], child, subset, out)
        if not subset:
            for key in actual:
                if key not in expected:
                    out.append(
                        {"pointer": f"{pointer}/{_escape(key)}", "expected": None, "actual": actual[key]}
                    )
        return
    if isinstance(expected, list):
        if not isinstance(actual, list):
            out.append({"pointer": pointer or "/", "expected": expected, "actual": actual})
            return
        if subset:
            _diff_list_subset(expected, actual, pointer, out)
            return
        if len(expected) != len(actual):
            out.append({"pointer": f"{pointer}/length", "expected": len(expected), "actual": len(actual)})
        for index, (exp, act) in enumerate(zip(expected, actual, strict=False)):
            _diff(exp, act, f"{pointer}/{index}", subset, out)
        return
    if not _same_scalar(expected, actual):
        out.append({"pointer": pointer or "/", "expected": expected, "actual": actual})


def _diff_list_subset(
    expected: list[Any], actual: list[Any], pointer: str, out: list[dict[str, Any]]
) -> None:
    """Every expected item must match (as a subset) a distinct actual item; order does not matter."""
    used: set[int] = set()
    for index, exp in enumerate(expected):
        match = None
        for candidate, act in enumerate(actual):
            if candidate in used:
                continue
            probe: list[dict[str, Any]] = []
            _diff(exp, act, "", True, probe)
            if not probe:
                match = candidate
                break
        if match is None:
            # Report against the item at the same position (or nothing) to show what differs.
            act = actual[index] if index < len(actual) and index not in used else None
            if act is None:
                out.append({"pointer": f"{pointer}/{index}", "expected": exp, "actual": None})
            else:
                _diff(exp, act, f"{pointer}/{index}", True, out)
        else:
            used.add(match)


def compare_output(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any] | None,
    mode: Literal["exact", "subset"] = "exact",
) -> list[dict[str, Any]]:
    """Differences between the expected and the actual ``HandlerOutput`` (empty list = equal)."""
    out: list[dict[str, Any]] = []
    _diff(strip_runtime_metadata(expected), strip_runtime_metadata(actual or {}), "", mode == "subset", out)
    return out
