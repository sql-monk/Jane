"""Transition conditions (``TaskConfig`` ``Condition``), URL patterns and extractor bindings.

* Condition fields: ``material.*`` (Material metadata), ``result.status``, ``result.failure.kind``,
  ``result.entities_count``, ``entity.entity_type``, ``entity.fields.<name>``.
* ``UrlPattern`` glob: ``*`` — within one path segment, ``**`` — any part, ``?`` — one character; matched
  against the canonical URL without the scheme. ``regex`` — against the whole canonical URL.
* A binding matches when **every** property it sets matches (AND); a stage matches when **any** of its
  bindings matches (OR). Empty ``source_ids`` means the task's source.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from typing import Any

from jane_orchestrator.common import get_path

__all__ = [
    "binding_matches",
    "condition_uses_entity",
    "evaluate",
    "glob_to_regex",
    "material_url",
    "stage_bindings_match",
    "url_pattern_matches",
]

PATTERN_CACHE = 1024  # compiled patterns kept in memory (cache size, not an operational limit)


@lru_cache(maxsize=PATTERN_CACHE)
def glob_to_regex(pattern: str) -> re.Pattern[str]:
    out = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "*":
            if pattern[i : i + 2] == "**":
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(ch))
        i += 1
    return re.compile("^" + "".join(out) + "$")


@lru_cache(maxsize=PATTERN_CACHE)
def _regex(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern)


def _strip_scheme(url: str) -> str:
    return re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", url)


def url_pattern_matches(pattern: Mapping[str, Any], url: str) -> bool:
    kind = pattern.get("type", "glob")
    value = str(pattern.get("value", ""))
    if kind == "regex":
        return _regex(value).search(url) is not None
    return glob_to_regex(value).match(_strip_scheme(url)) is not None


def material_url(material: Mapping[str, Any]) -> str | None:
    loc = material.get("locator") or {}
    for key in ("canonical_url", "final_url", "url"):
        if loc.get(key):
            return str(loc[key])
    return None


def binding_matches(binding: Mapping[str, Any], material: Mapping[str, Any], task_source_id: str) -> bool:
    source_ids = binding.get("source_ids") or [task_source_id]
    mat_source = (material.get("source") or {}).get("source_id") or task_source_id
    if mat_source not in source_ids:
        return False
    if binding.get("sections"):
        section = (material.get("discovery") or {}).get("section")
        if section not in binding["sections"]:
            return False
    if binding.get("url_patterns"):
        url = material_url(material)
        if url is None or not any(url_pattern_matches(p, url) for p in binding["url_patterns"]):
            return False
    if binding.get("media_types"):
        media = (material.get("format") or {}).get("media_type")
        if media not in binding["media_types"]:
            return False
    if binding.get("content_kinds"):
        kind = (material.get("format") or {}).get("content_kind")
        if kind not in binding["content_kinds"]:
            return False
    return True


def stage_bindings_match(
    bindings: Sequence[Mapping[str, Any]] | None, material: Mapping[str, Any], task_source_id: str
) -> bool:
    """A stage without bindings accepts everything from its inputs."""
    if not bindings:
        return True
    return any(binding_matches(b, material, task_source_id) for b in bindings)


# ------------------------------------------------------------------ conditions
def _num(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _predicate(pred: Mapping[str, Any], ctx: Mapping[str, Any]) -> bool:
    field = str(pred["field"])
    op = pred["op"]
    expected = pred.get("value")
    root, _, rest = field.partition(".")
    found, actual = get_path(ctx.get(root) or {}, rest)
    if op == "exists":
        return found
    if op == "not_exists":
        return not found
    if op == "ne":
        return not found or actual != expected
    if op == "not_in":
        return not found or actual not in (expected or [])
    if not found:
        return False
    if op == "eq":
        return bool(actual == expected)
    if op == "in":
        return actual in (expected or [])
    if op in {"gt", "gte", "lt", "lte"}:
        a, b = _num(actual), _num(expected)
        if a is None or b is None:
            if isinstance(actual, str) and isinstance(expected, str):  # RFC 3339 timestamps compare as text
                a_s, b_s = actual, expected
                return {"gt": a_s > b_s, "gte": a_s >= b_s, "lt": a_s < b_s, "lte": a_s <= b_s}[op]
            return False
        return {"gt": a > b, "gte": a >= b, "lt": a < b, "lte": a <= b}[op]
    if op == "matches_glob":
        return isinstance(actual, str) and glob_to_regex(str(expected)).match(actual) is not None
    if op == "matches_regex":
        return isinstance(actual, str) and _regex(str(expected)).search(actual) is not None
    return False


def evaluate(cond: Mapping[str, Any] | None, ctx: Mapping[str, Any]) -> bool:
    """Evaluate a Condition against ``{"material": …, "result": …, "entity": …}``. ``None`` → true."""
    if cond is None:
        return True
    if "all" in cond:
        return all(evaluate(c, ctx) for c in cond["all"])
    if "any" in cond:
        return any(evaluate(c, ctx) for c in cond["any"])
    if "not" in cond:
        return not evaluate(cond["not"], ctx)
    return _predicate(cond, ctx)


def condition_uses_entity(cond: Mapping[str, Any] | None) -> bool:
    if cond is None:
        return False
    if "all" in cond or "any" in cond:
        return any(condition_uses_entity(c) for c in cond.get("all", cond.get("any", [])))
    if "not" in cond:
        return condition_uses_entity(cond["not"])
    return str(cond.get("field", "")).startswith("entity.")
