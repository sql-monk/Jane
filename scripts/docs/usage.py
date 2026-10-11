"""Find source-backed public API examples in repository Python tests/call sites."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import digest, read


def examples(
    root: Path, symbols: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_id = {x["id"]: x for x in symbols if x["language"] == "python"}
    found: dict[str, list[dict[str, Any]]] = defaultdict(list)
    inputs = []
    paths = sorted(
        {
            path
            for family in ("services", "libs")
            for path in (root / family).rglob("*.py")
            if "tests" in path.relative_to(root).parts and "__pycache__" not in path.parts
        }
    )
    for path in paths:
        text = read(path)
        tree = ast.parse(text, filename=str(path))
        aliases: dict[str, str] = {}
        types: dict[str, str] = {}
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and not node.level:
                for alias in node.names:
                    aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    aliases[alias.asname or alias.name.split(".")[0]] = (
                        alias.name if alias.asname else alias.name.split(".")[0]
                    )

        def resolve(
            node: ast.AST, *, types: dict[str, str] = types, aliases: dict[str, str] = aliases
        ) -> str | None:
            if isinstance(node, ast.Name):
                return types.get(node.id) or aliases.get(node.id)
            if isinstance(node, ast.Attribute):
                base = resolve(node.value)
                if not base:
                    return None
                candidate = base + "." + node.attr
                if candidate in by_id:
                    return candidate
                cls = by_id.get(base)
                if cls and cls["kind"] == "class":
                    member = next((x for x in cls["members"] if x["name"] == node.attr), None)
                    if member:
                        return str(member["id"])
                return candidate
            return None

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for argument in node.args.args + node.args.kwonlyargs:
                    if argument.annotation:
                        target = resolve(argument.annotation)
                        if target is not None and target in by_id and by_id[target]["kind"] == "class":
                            types[argument.arg] = target
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Call):
                target = resolve(node.value.func)
                if target is not None and target in by_id and by_id[target]["kind"] == "class":
                    names = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for name in names:
                        if isinstance(name, ast.Name):
                            types[name.id] = target
        used = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                target = resolve(node.func)
            elif isinstance(node, ast.Attribute) and not isinstance(parents.get(node), ast.Call):
                target = resolve(node)
            else:
                continue
            if target is None or target not in by_id or len(found[target]) >= 2:
                continue
            parent: ast.AST = node
            while parent in parents and not isinstance(parent, ast.stmt):
                parent = parents[parent]
            if not isinstance(parent, (ast.Assert, ast.Expr, ast.Assign, ast.AnnAssign, ast.Return)):
                parent = node
            snippet = ast.get_source_segment(text, parent)
            if not snippet:
                continue
            example = {
                "source": path.relative_to(root).as_posix(),
                "line": parent.lineno,
                "end_line": parent.end_lineno,
                "language": "python",
                "code": snippet,
                "kind": "repository-test-call-site",
            }
            if not any(
                x["source"] == example["source"] and x["line"] == example["line"] for x in found[target]
            ):
                found[target].append(example)
                used = True
                ctor = target + ".__init__"
                if ctor in by_id and len(found[ctor]) < 2:
                    found[ctor].append(example)
        if used:
            inputs.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": digest(path),
                    "role": "source-backed-examples",
                }
            )
    return inputs, found
