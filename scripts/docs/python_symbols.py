"""Static Python public surface extraction using stdlib AST, without imports."""

from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
from typing import Any

from common import digest, read

SPECIAL = {
    "__init__",
    "__new__",
    "__call__",
    "__enter__",
    "__exit__",
    "__aenter__",
    "__aexit__",
    "__iter__",
    "__next__",
    "__aiter__",
    "__anext__",
    "__getitem__",
    "__setitem__",
    "__len__",
    "__str__",
    "__repr__",
    "__eq__",
    "__hash__",
}


def public(name: str) -> bool:
    return not name.startswith("_") or name in SPECIAL


def expr(node: ast.AST | None) -> str | None:
    return ast.unparse(node) if node is not None else None


def assigned(node: ast.AST) -> list[str]:
    if isinstance(node, ast.AnnAssign):
        return [node.target.id] if isinstance(node.target, ast.Name) else []
    if isinstance(node, ast.Assign):
        return [x.id for target in node.targets for x in ast.walk(target) if isinstance(x, ast.Name)]
    return []


def literal(node: ast.AST | None, values: dict[str, Any]) -> Any:
    """Evaluate literal config expressions only; never execute calls/source code."""
    if isinstance(node, ast.Name):
        return values.get(node.id)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = literal(node.left, values), literal(node.right, values)
        return left + right if type(left) is type(right) and isinstance(left, (str, list, tuple)) else None
    if isinstance(node, ast.JoinedStr):
        bits = [
            literal(x.value, values) if isinstance(x, ast.FormattedValue) else literal(x, values)
            for x in node.values
        ]
        return "".join(str(x) for x in bits) if all(x is not None for x in bits) else None
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [literal(x, values) for x in node.elts]
    return None


def parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, Any]]:
    result = []
    args = node.args
    positions = args.posonlyargs + args.args
    defaults = [None] * (len(positions) - len(args.defaults)) + list(args.defaults)
    for index, (arg, default) in enumerate(zip(positions, defaults, strict=True)):
        result.append(
            {
                "name": arg.arg,
                "type": expr(arg.annotation),
                "default": expr(default),
                "kind": "positional-only" if index < len(args.posonlyargs) else "positional-or-keyword",
            }
        )
    if args.vararg:
        result.append(
            {
                "name": args.vararg.arg,
                "type": expr(args.vararg.annotation),
                "default": None,
                "kind": "var-positional",
            }
        )
    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        result.append(
            {"name": arg.arg, "type": expr(arg.annotation), "default": expr(default), "kind": "keyword-only"}
        )
    if args.kwarg:
        result.append(
            {
                "name": args.kwarg.arg,
                "type": expr(args.kwarg.annotation),
                "default": None,
                "kind": "var-keyword",
            }
        )
    return result


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    bare = deepcopy(node)
    bare.body = [ast.Pass()]
    bare.decorator_list = []
    return ast.unparse(bare).rsplit("\n", 1)[0]


class Raises(ast.NodeVisitor):
    def __init__(self) -> None:
        self.values: set[str] = set()

    def visit_Raise(self, node: ast.Raise) -> None:
        self.values.add(
            expr(node.exc.func if isinstance(node.exc, ast.Call) else node.exc) or "повторний raise"
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        pass

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        pass

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        pass


def extra_doc(body: list[ast.stmt], index: int) -> str | None:
    if index + 1 < len(body):
        next_node = body[index + 1]
        if (
            isinstance(next_node, ast.Expr)
            and isinstance(next_node.value, ast.Constant)
            and isinstance(next_node.value.value, str)
        ):
            return next_node.value.value
    return None


def field_data(node: ast.Assign | ast.AnnAssign) -> dict[str, Any]:
    value = node.value
    data: dict[str, Any] = {
        "annotation": expr(node.annotation) if isinstance(node, ast.AnnAssign) else None,
        "default": expr(value),
        "required": value is None,
        "constraints": {},
    }
    if isinstance(value, ast.Call) and expr(value.func) in {
        "Field",
        "field",
        "dataclasses.field",
        "contract_field",
    }:
        kw = {x.arg: expr(x.value) for x in value.keywords if x.arg}
        data["constraints"] = kw
        if "default" in kw:
            data["default"] = kw["default"]
            data["required"] = kw["default"] == "..."
        elif "default_factory" in kw:
            data["default"] = None
            data["default_factory"] = kw["default_factory"]
            data["required"] = False
        elif value.args:
            # contract_field takes the contract key before the default value.
            position = 1 if expr(value.func) == "contract_field" else 0
            data["default"] = expr(value.args[position]) if len(value.args) > position else None
            if expr(value.func) == "contract_field":
                data["constraints"]["contract_key"] = expr(value.args[0])
            data["required"] = data["default"] == "..."
        else:
            data["required"] = True
    return data


def extract(
    root: Path, source_files: list[tuple[str, Path, Path]]
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    symbols: list[dict[str, Any]] = []
    modules: dict[str, dict[str, Any]] = {}
    inputs = []
    for component, path, source_root in source_files:
        rel = path.relative_to(source_root).with_suffix("").parts
        module = ".".join(rel[:-1] if rel[-1] == "__init__" else rel)
        text = read(path)
        tree = ast.parse(text, filename=str(path), type_comments=True)
        imports: dict[str, str] = {}
        values: dict[str, Any] = {}
        all_names: list[str] | None = None
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                parent = module if path.name == "__init__.py" else module.rsplit(".", 1)[0]
                parts = parent.split(".")
                base = ".".join(parts[: len(parts) - node.level + 1]) if node.level else ""
                target = ".".join(x for x in (base, node.module) if x)
                for imported_name in node.names:
                    imports[imported_name.asname or imported_name.name] = f"{target}.{imported_name.name}"
            elif isinstance(node, ast.Import):
                for imported_name in node.names:
                    imports[imported_name.asname or imported_name.name.split(".")[0]] = (
                        imported_name.name if imported_name.asname else imported_name.name.split(".")[0]
                    )
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                for name in assigned(node):
                    values[name] = literal(node.value, values)
                    if name == "__all__":
                        if not isinstance(values[name], list) or not all(
                            isinstance(x, str) for x in values[name]
                        ):
                            raise ValueError(f"Dynamic __all__ is not supported: {path}")
                        all_names = values[name]
        modules[module] = {
            "component": component,
            "source": path.relative_to(root).as_posix(),
            "imports": imports,
            "values": values,
            "all": all_names,
            "docstring": ast.get_docstring(tree),
            "tree": tree,
        }
        inputs.append({"path": path.relative_to(root).as_posix(), "sha256": digest(path)})

    def item(module: str, name: str, node: ast.AST, kind: str, parent: str | None = None) -> dict[str, Any]:
        m = modules[module]
        return {
            "id": f"{module}.{name}",
            "name": name.rsplit(".", 1)[-1],
            "module": module,
            "component": m["component"],
            "language": "python",
            "kind": kind,
            "parent": f"{module}.{parent}" if parent else None,
            "source": m["source"],
            "line": getattr(node, "lineno", 0),
            "end_line": getattr(node, "end_lineno", None),
        }

    def declarations(module: str, body: list[ast.stmt], parent: str | None = None) -> None:
        m = modules[module]
        for index, node in enumerate(body):
            names = (
                [node.name]
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                else assigned(node)
            )
            for name in names:
                if not public(name) and not (parent is None and m["all"] and name in m["all"]):
                    continue
                full_name = f"{parent}.{name}" if parent else name
                if isinstance(node, ast.ClassDef):
                    data = item(module, full_name, node, "class", parent)
                    data.update(
                        signature=f"class {name}({', '.join(ast.unparse(x) for x in node.bases)}):"
                        if node.bases
                        else f"class {name}:",
                        bases=[ast.unparse(x) for x in node.bases],
                        decorators=[ast.unparse(x) for x in node.decorator_list],
                        docstring=ast.get_docstring(node),
                        members=[],
                    )
                    symbols.append(data)
                    declarations(module, node.body, full_name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    decorators = [ast.unparse(x) for x in node.decorator_list]
                    kind = (
                        "constructor"
                        if name in {"__init__", "__new__"}
                        else "method"
                        if parent
                        else "function"
                    )
                    prop = (
                        "property" in decorators
                        or "cached_property" in decorators
                        or "functools.cached_property" in decorators
                    )
                    setter = next(
                        (x for x in decorators if x.endswith(".setter") or x.endswith(".deleter")), None
                    )
                    data = item(module, full_name, node, "property" if prop or setter else kind, parent)
                    raises = Raises()
                    for statement in node.body:
                        raises.visit(statement)
                    data.update(
                        signature=signature(node),
                        parameters=parameters(node),
                        returns=expr(node.returns),
                        decorators=decorators,
                        docstring=ast.get_docstring(node),
                        raises=sorted(raises.values),
                    )
                    if prop:
                        cached = any(x.endswith("cached_property") for x in decorators)
                        data.update(readable=True, writable=cached, deletable=cached)
                    if setter:
                        existing = next(
                            (
                                x
                                for x in reversed(symbols)
                                if x["id"] == data["id"] and x["kind"] == "property"
                            ),
                            None,
                        )
                        if existing:
                            existing["writable" if setter.endswith(".setter") else "deletable"] = True
                            existing.setdefault("accessors", []).append(data["signature"])
                            continue
                        data.update(
                            readable=False,
                            writable=setter.endswith(".setter"),
                            deletable=setter.endswith(".deleter"),
                        )
                    # Preserve overload declarations rather than dropping a public signature.
                    existing = next((x for x in reversed(symbols) if x["id"] == data["id"]), None)
                    if existing and any(x.endswith("overload") for x in existing.get("decorators", [])):
                        data["overloads"] = [*existing.get("overloads", []), existing["signature"]]
                        symbols.remove(existing)
                    symbols.append(data)
                    if parent and name == "__init__":
                        for assignment in ast.walk(node):
                            if not isinstance(assignment, (ast.Assign, ast.AnnAssign)):
                                continue
                            targets = (
                                assignment.targets
                                if isinstance(assignment, ast.Assign)
                                else [assignment.target]
                            )
                            for target in targets:
                                if (
                                    isinstance(target, ast.Attribute)
                                    and isinstance(target.value, ast.Name)
                                    and target.value.id == "self"
                                    and public(target.attr)
                                ):
                                    attr = item(
                                        module,
                                        f"{parent}.{target.attr}",
                                        assignment,
                                        "instance-field",
                                        parent,
                                    )
                                    attr.update(
                                        field_data(assignment),
                                        signature=ast.unparse(assignment),
                                        docstring=None,
                                    )
                                    if not any(x["id"] == attr["id"] for x in symbols):
                                        symbols.append(attr)
                elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                    data = item(
                        module,
                        full_name,
                        node,
                        "field" if parent else "constant" if name.isupper() else "variable",
                        parent,
                    )
                    data.update(
                        field_data(node), signature=ast.unparse(node), docstring=extra_doc(body, index)
                    )
                    if parent:
                        owner = next(
                            (
                                x
                                for x in reversed(symbols)
                                if x["id"] == f"{module}.{parent}" and x["kind"] == "class"
                            ),
                            None,
                        )
                        readonly = owner is not None and (
                            any(
                                x.split("[")[0].split(".")[-1]
                                in {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"}
                                for x in owner["bases"]
                            )
                            or any("frozen=True" in x.replace(" ", "") for x in owner["decorators"])
                        )
                        data.update(readable=True, writable=not readonly)
                    old = next((x for x in symbols if x["id"] == data["id"]), None)
                    if old and old["kind"] == "instance-field":
                        symbols.remove(old)
                    symbols.append(data)
            if isinstance(node, (ast.If, ast.Try, ast.With)):
                declarations(module, node.body, parent)
                declarations(module, getattr(node, "orelse", []), parent)
                if isinstance(node, ast.Try):
                    for handler in node.handlers:
                        declarations(module, handler.body, parent)

    for module, m in modules.items():
        declarations(module, m["tree"].body)
        if m["all"] or m["source"].endswith("/__init__.py"):
            candidates = m["all"] if m["all"] is not None else [x for x in m["imports"] if public(x)]
            for name in candidates:
                if name in m["imports"] and not any(x["id"] == f"{module}.{name}" for x in symbols):
                    node = next(
                        (
                            x
                            for x in m["tree"].body
                            if isinstance(x, (ast.Import, ast.ImportFrom))
                            and any((n.asname or n.name) == name for n in x.names)
                        ),
                        m["tree"].body[0],
                    )
                    data = item(module, name, node, "reexport")
                    data.update(
                        target=m["imports"][name],
                        signature=f"from {m['imports'][name].rsplit('.', 1)[0]} import {m['imports'][name].rsplit('.', 1)[-1]} as {name}",
                        docstring=None,
                    )
                    symbols.append(data)
    # Visibility applies to top-level exports. Members inherit their class visibility.
    by_id = {x["id"]: x for x in symbols}
    exported = set()
    for data in symbols:
        m = modules[data["module"]]
        top = data["id"][len(data["module"]) + 1 :].split(".")[0]
        private_module = any(x.startswith("_") and x != "__main__" for x in data["module"].split("."))
        if (m["all"] is None and not private_module) or (
            m["all"] is not None and top in m["all"] and not private_module
        ):
            exported.add(data["id"])
    for data in list(symbols):
        if data["id"] in exported and data["kind"] == "reexport" and data["target"] in by_id:
            target_record = by_id[data["target"]]
            exported.add(target_record["id"])
            exported.update(x["id"] for x in symbols if x.get("parent") == target_record["id"])
    symbols = [x for x in symbols if x["id"] in exported]
    by_id = {x["id"]: x for x in symbols}

    def resolve(module: str, base: str) -> str:
        base = base.split("[")[0]
        head, *tail = base.split(".")
        target = modules[module]["imports"].get(head, f"{module}.{head}")
        result = ".".join([target, *tail])
        while result in by_id and by_id[result]["kind"] == "reexport":
            result = by_id[result]["target"]
        return result

    def members(cls: dict[str, Any], seen: set[str] | None = None) -> list[dict[str, Any]]:
        seen = set() if seen is None else seen
        if cls["id"] in seen:
            return []
        seen = seen | {cls["id"]}
        own = [x for x in symbols if x.get("parent") == cls["id"]]
        names = {x["name"] for x in own}
        inherited = []
        for base in cls["bases"]:
            target = by_id.get(resolve(cls["module"], base))
            if target and target["kind"] == "class":
                for member in members(target, seen):
                    if member["name"] not in names:
                        inherited.append({**member, "inherited": True})
                        names.add(member["name"])
        return own + inherited

    for data in symbols:
        if data["kind"] == "class":
            data["base_ids"] = [resolve(data["module"], x) for x in data["bases"]]
            data["members"] = [
                {"id": x["id"], "name": x["name"], "kind": x["kind"], "inherited": x.get("inherited", False)}
                for x in members(data)
            ]
    # Dataclass constructors are generated by Python, not declared as AST functions.
    generated = []
    for cls in symbols:
        if cls["kind"] != "class" or not any(
            x.split("(")[0] in {"dataclass", "dataclasses.dataclass"} for x in cls["decorators"]
        ):
            continue
        if any(x["name"] == "__init__" and not x.get("inherited") for x in cls["members"]) or any(
            "init=False" in x.replace(" ", "") for x in cls["decorators"]
        ):
            continue
        fields = [
            by_id[x["id"]]
            for x in cls["members"]
            if x["kind"] == "field"
            and by_id[x["id"]].get("annotation")
            and "ClassVar" not in by_id[x["id"]]["annotation"]
            and by_id[x["id"]].get("constraints", {}).get("init") != "False"
            and (
                by_id[x["id"]].get("parent") == cls["id"]
                or any(
                    d.split("(")[0] in {"dataclass", "dataclasses.dataclass"}
                    for d in by_id.get(by_id[x["id"]].get("parent"), {}).get("decorators", [])
                )
            )
        ]
        fields = sorted(fields, key=lambda x: (x.get("parent") == cls["id"], x["line"]))
        kw_only = any("kw_only=True" in x.replace(" ", "") for x in cls["decorators"])
        args = [
            f"{x['name']}: {x['annotation']}"
            + (
                f" = {x['default']}"
                if x.get("default") is not None
                else f" = <factory {x['default_factory']}>"
                if x.get("default_factory")
                else ""
            )
            for x in fields
        ]
        constructor = {
            **cls,
            "id": cls["id"] + ".__init__",
            "name": "__init__",
            "parent": cls["id"],
            "kind": "generated-constructor",
            "signature": f"def __init__(self{', *, ' if kw_only and args else ', ' if args else ''}{', '.join(args)}) -> None:",
            "parameters": [
                {
                    "name": x["name"],
                    "type": x["annotation"],
                    "default": x.get("default"),
                    "default_factory": x.get("default_factory"),
                    "kind": "keyword-only" if kw_only else "positional-or-keyword",
                }
                for x in fields
            ],
            "returns": "None",
            "docstring": None,
        }
        constructor.pop("members", None)
        generated.append(constructor)
        cls["members"].append(
            {"id": constructor["id"], "name": "__init__", "kind": constructor["kind"], "inherited": False}
        )
    symbols.extend(generated)
    # Deduplicate conditional declarations while retaining their signatures.
    unique: dict[str, dict[str, Any]] = {}
    for data in symbols:
        if data["id"] in unique and unique[data["id"]]["signature"] != data["signature"]:
            data["overloads"] = list(
                dict.fromkeys(
                    [
                        *unique[data["id"]].get("overloads", []),
                        unique[data["id"]]["signature"],
                        *data.get("overloads", []),
                    ]
                )
            )
        unique[data["id"]] = data
    return (
        sorted(unique.values(), key=lambda x: (x["component"], x["module"], x["line"], x["id"])),
        modules,
        inputs,
    )


def configuration(symbols: list[dict[str, Any]], modules: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {x["id"]: x for x in symbols}
    result = []
    for cls in symbols:
        if cls["kind"] != "class":
            continue
        m = modules[cls["module"]]
        fields = [by_id[x["id"]] for x in cls.get("members", []) if x["kind"] == "field" and x["id"] in by_id]
        settings = cls["name"].endswith("Settings") or any(
            x.endswith((".BaseSettings", ".JaneSettings")) for x in cls.get("base_ids", [])
        )
        limits = cls["name"].endswith("Limits") or "settings.py" in cls["source"]
        if not settings and not limits:
            continue
        config = next((x for x in fields if x["name"] == "model_config"), None)
        prefix = m["values"].get("ENV_PREFIX")
        if config:
            value = ast.parse(config["signature"]).body[0].value
            if isinstance(value, ast.Call):
                kw = {x.arg: x.value for x in value.keywords}
                prefix = literal(kw.get("env_prefix"), m["values"]) or prefix
        for field in fields:
            if not field.get("annotation") or field["name"] == "model_config":
                continue
            result.append(
                {
                    "id": cls["id"] + "." + field["name"],
                    "owner": cls["id"],
                    "component": cls["component"],
                    "field": field["name"],
                    "type": field["annotation"],
                    "default": field.get("default"),
                    "default_factory": field.get("default_factory"),
                    "required": field.get("required"),
                    "constraints": field.get("constraints", {}),
                    "description_source": field.get("docstring"),
                    "environment": str(prefix) + field["name"].upper() if settings and prefix else None,
                    "kind": "setting" if settings else "limit-model-field",
                    "source": field["source"],
                    "line": field["line"],
                    "symbol_id": field["id"],
                    "inherited": field.get("parent") != cls["id"],
                }
            )

    def model_type(module: str, annotation: str | None) -> dict[str, Any] | None:
        if not annotation:
            return None
        name = annotation.split("[")[0].strip("'\"")
        qualified = modules[module]["imports"].get(name, f"{module}.{name}")
        data = by_id.get(qualified)
        return data if data and data["kind"] == "class" else None

    def leaves(
        cls: dict[str, Any], prefix: str = "", seen: frozenset[str] = frozenset()
    ) -> list[tuple[str, dict[str, Any]]]:
        if cls["id"] in seen:
            return []
        result: list[tuple[str, dict[str, Any]]] = []
        for member in cls.get("members", []):
            field = by_id.get(member["id"])
            if (
                not field
                or member["kind"] != "field"
                or not field.get("annotation")
                or field["name"] == "model_config"
            ):
                continue
            key = prefix + field["name"]
            child = model_type(field["module"], field["annotation"])
            nested = leaves(child, key + ".", seen | {cls["id"]}) if child else []
            result += nested if nested else [(key, field)]
        return result

    for cls in symbols:
        if cls["kind"] != "class" or cls["name"] != "ServiceLimits":
            continue
        env_prefix = modules[cls["module"]]["values"].get("ENV_PREFIX")
        if not env_prefix:
            continue
        for key, field in leaves(cls):
            result.append(
                {
                    "id": cls["id"] + ":" + key,
                    "owner": cls["id"],
                    "component": cls["component"],
                    "field": key,
                    "type": field["annotation"],
                    "default": field.get("default"),
                    "default_factory": field.get("default_factory"),
                    "required": field.get("required"),
                    "constraints": field.get("constraints", {}),
                    "description_source": field.get("docstring"),
                    "environment": str(env_prefix) + "LIMITS__" + key.upper().replace(".", "__"),
                    "hard_cap_environment": str(env_prefix)
                    + "LIMITS__HARD_CAPS__"
                    + key.upper().replace(".", "__"),
                    "kind": "effective-limit-leaf",
                    "source": field["source"],
                    "line": field["line"],
                    "symbol_id": field["id"],
                }
            )
    for module, m in modules.items():
        for node in ast.walk(m["tree"]):
            value = None
            default = None
            if (
                isinstance(node, ast.Call)
                and expr(node.func) in {"os.getenv", "getenv", "os.environ.get", "environ.get"}
                and node.args
            ):
                value = node.args[0]
                default = expr(node.args[1]) if len(node.args) > 1 else None
            elif isinstance(node, ast.Subscript) and expr(node.value) in {"os.environ", "environ"}:
                value = node.slice
            if value is not None:
                name = literal(value, m["values"])
                result.append(
                    {
                        "id": f"{module}:env:{getattr(node, 'lineno', 0)}",
                        "component": m["component"],
                        "kind": "environment-read",
                        "environment": name if isinstance(name, str) else None,
                        "expression": expr(value),
                        "default": default,
                        "source": m["source"],
                        "line": getattr(node, "lineno", 0),
                    }
                )
    return sorted(result, key=lambda x: (x["component"], x["id"]))
