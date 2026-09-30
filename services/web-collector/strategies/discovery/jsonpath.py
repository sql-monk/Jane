"""A small, dependency-free JSONPath subset for ``api_feed`` (``items_path``, ``url_path``, …).

Supported: ``$`` (or ``@``) root, ``.name``, ``['name']`` / ``["name"]``, ``[n]`` (negative from the end),
``[*]`` / ``.*`` (all children), ``..name`` / ``..*`` (recursive descent). A path without ``$`` is taken as
relative to the root (``items`` = ``$.items``). Filters, slices and unions are not supported (``ValueError``).
Evaluation never recurses in Python, so deeply nested documents cannot exhaust the stack.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

__all__ = ["JsonPath"]

_NAME = re.compile(r"[A-Za-z_$][\w$-]*")
_INDEX = re.compile(r"-?\d+")

Step = tuple[str, Any]  # ("key", name) | ("index", n) | ("all", None) | ("descend", name or None)


def _parse(expr: str) -> list[Step]:
    text = expr.strip()
    if not text:
        raise ValueError("empty JSONPath")
    i = 0
    if text[0] in "$@":
        i = 1
    elif text[0] not in ".[":
        text = "." + text
    steps: list[Step] = []
    while i < len(text):
        if text.startswith("..", i):
            i += 2
            if i < len(text) and text[i] == "*":
                steps.append(("descend", None))
                i += 1
                continue
            if i < len(text) and text[i] == "[":
                step, i = _bracket(text, i)
                if step[0] != "key":
                    raise ValueError(f"unsupported JSONPath {expr!r}: '..' needs a name")
                steps.append(("descend", step[1]))
                continue
            match = _NAME.match(text, i)
            if not match:
                raise ValueError(f"unsupported JSONPath {expr!r} at {i}")
            steps.append(("descend", match.group(0)))
            i = match.end()
        elif text[i] == ".":
            i += 1
            if i < len(text) and text[i] == "*":
                steps.append(("all", None))
                i += 1
                continue
            match = _NAME.match(text, i)
            if not match:
                raise ValueError(f"unsupported JSONPath {expr!r} at {i}")
            steps.append(("key", match.group(0)))
            i = match.end()
        elif text[i] == "[":
            step, i = _bracket(text, i)
            steps.append(step)
        else:
            raise ValueError(f"unsupported JSONPath {expr!r} at {i}")
    return steps


def _bracket(text: str, i: int) -> tuple[Step, int]:
    end = text.find("]", i)
    if end < 0:
        raise ValueError(f"unclosed '[' in JSONPath {text!r}")
    inner = text[i + 1 : end].strip()
    if inner == "*":
        return ("all", None), end + 1
    if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in "'\"":
        return ("key", inner[1:-1]), end + 1
    if _INDEX.fullmatch(inner):
        return ("index", int(inner)), end + 1
    raise ValueError(
        f"unsupported JSONPath selector [{inner}] (filters, slices and unions are not supported)"
    )


def _walk(node: Any) -> Iterator[Any]:
    """The node and all its descendants, iteratively (document order)."""
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        if isinstance(current, dict):
            stack.extend(reversed(list(current.values())))
        elif isinstance(current, list):
            stack.extend(reversed(current))


def _children(node: Any) -> list[Any]:
    if isinstance(node, dict):
        return list(node.values())
    if isinstance(node, list):
        return list(node)
    return []


class JsonPath:
    """A compiled JSONPath expression (see the module docstring for the supported subset)."""

    __slots__ = ("expr", "steps")

    def __init__(self, expr: str) -> None:
        self.expr = expr
        self.steps: list[Step] = _parse(expr)

    def __repr__(self) -> str:
        return f"JsonPath({self.expr!r})"

    def find(self, data: Any) -> list[Any]:
        nodes = [data]
        for kind, arg in self.steps:
            out: list[Any] = []
            for node in nodes:
                if kind == "key":
                    if isinstance(node, dict) and arg in node:
                        out.append(node[arg])
                elif kind == "index":
                    if isinstance(node, list) and -len(node) <= arg < len(node):
                        out.append(node[arg])
                elif kind == "all":
                    out.extend(_children(node))
                elif arg is None:  # descend, all
                    out.extend(d for d in _walk(node) if d is not node)
                else:  # descend to a name
                    out.extend(d[arg] for d in _walk(node) if isinstance(d, dict) and arg in d)
            nodes = out
        return nodes

    def first(self, data: Any) -> Any | None:
        found = self.find(data)
        return found[0] if found else None
