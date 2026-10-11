# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Generate the API and type references of the Jane documentation from contracts and code.

    uv run --script scripts/docs_reference.py generate
    uv run --script scripts/docs_reference.py check

* API (``contracts/openapi/<api>.v1.yaml``): an index page and one page per operation - method, path, scope,
  idempotency, parameters, request and response fields, errors and the contract's examples. Shared contracts
  (``collector.v1``, ``handler.v1``) go to ``docs/reference/api/<api>/``, the others to
  ``docs/components/<module>/reference/api/``; every module gets ``reference/api/README.md``.
* Python types (``ast``, nothing is imported): one page per public module with classes (bases, kind, fields and
  properties with read/write access, constructor, methods), functions, constants and re-exports; signatures,
  docstrings, exceptions raised in the body and links to the source lines.
* TypeScript (Admin UI): exported declarations of ``web/admin/src`` via ``scripts/docs_reference_ts.mjs``
  (TypeScript compiler of ``web/admin/node_modules``).

``check`` regenerates in memory and fails when a generated file differs or is missing (exit code 1).
Generated files are marked in their first line and must not be edited by hand.
"""

from __future__ import annotations

import argparse
import ast
import itertools
import json
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OPENAPI = ROOT / "contracts" / "openapi"
GENERATED = "> Згенеровано `scripts/docs_reference.py` з {source}. Не редагуйте вручну."

SHARED_APIS = {"collector": "docs/reference/api/collector", "handler": "docs/reference/api/handler"}
OWN_APIS = {
    "orchestrator": "orchestrator",
    "registry": "registry",
    "llm": "llm",
    "assistant": "assistant",
    "storage": "storage",
}
MODULE_APIS: dict[str, list[str]] = {
    "web-collector": ["collector"],
    "telegram-collector": ["collector"],
    "storage": ["storage", "handler"],
    "handler-runtime": ["handler"],
    "llm": ["llm", "handler"],
    "registry": ["registry"],
    "orchestrator": ["orchestrator"],
    "assistant": ["assistant"],
}
PY_MODULES: dict[str, list[str]] = {
    "web-collector": ["services/web-collector/src/jane_web_collector"],
    "telegram-collector": ["services/telegram-collector/src/jane_telegram_collector"],
    "storage": ["services/storage/src/jane_storage"]
    + [
        f"services/storage/adapters/{a}/src/jane_storage_{a}"
        for a in ("files", "postgres", "sqlserver", "mongodb", "minio", "s3")
    ],
    "handler-runtime": ["services/handler-runtime/src/jane_handler_runtime"],
    "llm": ["services/llm/src/jane_llm"],
    "registry": ["services/registry/src/jane_registry"],
    "orchestrator": ["services/orchestrator/src/jane_orchestrator"],
    "assistant": ["services/assistant/src/jane_assistant"],
    "jane-kit": ["libs/jane-kit/src/jane_kit"],
    "extractor-sdk": ["libs/extractor-sdk/src/jane_extractor_sdk"],
    "contracts": ["contracts/python/src/jane_contracts"],
}
TITLES = {
    "web-collector": "Web Collector",
    "telegram-collector": "Telegram Collector",
    "storage": "Storage",
    "handler-runtime": "Handler Runtime",
    "llm": "LLM gateway",
    "registry": "Registry",
    "orchestrator": "Orchestrator",
    "assistant": "Assistant",
    "jane-kit": "jane-kit",
    "extractor-sdk": "jane-extractor-sdk",
    "contracts": "jane-contracts",
    "admin": "Admin UI",
}
HTTP_METHODS = ("get", "put", "post", "patch", "delete")


def rel(target: Path, page: Path) -> str:
    """Relative POSIX link from ``page`` to ``target``."""
    import os

    return Path(os.path.relpath(target, page.parent)).as_posix()


CODE_SPAN = re.compile(r"(`+)(.+?)\1", re.S)


def no_html(text: str) -> str:
    """Escape ``<`` outside code spans so that ``<name>`` placeholders do not become raw HTML."""
    out, pos = [], 0
    for m in CODE_SPAN.finditer(text):
        out.append(text[pos : m.start()].replace("<", "&lt;"))
        out.append(m.group(0))
        pos = m.end()
    out.append(text[pos:].replace("<", "&lt;"))
    return "".join(out)


def md_cell(text: str) -> str:
    return no_html(" ".join(str(text).split())).replace("|", "\\|")


def first_line(text: str | None) -> str:
    if not text:
        return ""
    para = text.strip().split("\n\n")[0]
    return " ".join(para.split())


def code_safe(text: str) -> str:
    """Docstring/description text for Markdown: keep paragraphs, escape what would become raw HTML."""
    # Reflow wrapped lines (a code span may continue on the next line), keep list items and indented blocks.
    lines: list[str] = []
    for line in text.strip().splitlines():
        starts_block = not line.strip() or re.match(r"\s*([-*+]|\d+[.)])\s", line) or line.startswith("    ")
        if lines and lines[-1].strip() and not starts_block:
            lines[-1] = f"{lines[-1].rstrip()} {line.strip()}"
        else:
            lines.append(line)
    return no_html("\n".join(lines))


def line_of(path: Path, needle: str) -> int:
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if needle in line:
            return n
    return 1


# ---------------------------------------------------------------------------------------------- OpenAPI


class Resolver:
    def __init__(self) -> None:
        self.cache: dict[Path, Any] = {}

    def load(self, path: Path) -> Any:
        path = path.resolve()
        if path not in self.cache:
            text = path.read_text(encoding="utf-8")
            self.cache[path] = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        return self.cache[path]

    def resolve(self, node: Any, base: Path) -> tuple[Any, Path, str | None]:
        """Follow ``$ref`` chains; returns (node, file it lives in, name of the last ref)."""
        name = None
        seen = 0
        while isinstance(node, dict) and "$ref" in node and seen < 20:
            ref = node["$ref"]
            file_part, _, pointer = ref.partition("#")
            target = (base.parent / file_part).resolve() if file_part else base
            doc = self.load(target)
            for token in [t for t in pointer.split("/") if t]:
                doc = doc[token.replace("~1", "/").replace("~0", "~")]
            name = pointer.rsplit("/", 1)[-1] if pointer else Path(file_part).name.split(".")[0]
            extra = {k: v for k, v in node.items() if k != "$ref"}
            node, base = (doc | extra if isinstance(doc, dict) and extra else doc), target
            seen += 1
        return node, base, name


def type_of(schema: Any, base: Path, res: Resolver, depth: int = 0) -> str:
    if not isinstance(schema, dict):
        return "—"
    if "$ref" in schema:
        node, nbase, name = res.resolve(schema, base)
        if isinstance(node, dict) and (node.get("properties") or node.get("type") == "object"):
            return f"`{name}`"
        inner = type_of(node, nbase, res, depth + 1) if depth < 4 else ""
        return inner or f"`{name}`"
    for key, sep in (("oneOf", " \\| "), ("anyOf", " \\| ")):
        if key in schema:
            return sep.join(type_of(s, base, res, depth + 1) for s in schema[key])
    if "allOf" in schema:
        return " + ".join(type_of(s, base, res, depth + 1) for s in schema["allOf"])
    if "const" in schema:
        return f"`{json.dumps(schema['const'], ensure_ascii=False)}`"
    if "enum" in schema:
        return "enum: " + ", ".join(f"`{v}`" for v in schema["enum"])
    t = schema.get("type")
    if isinstance(t, list):
        t = " \\| ".join(t)
    if t == "array":
        return f"array of {type_of(schema.get('items', {}), base, res, depth + 1)}"
    if t is None and "properties" in schema:
        t = "object"
    out = f"`{t}`" if t else "—"
    if fmt := schema.get("format"):
        out += f" ({fmt})"
    return out


def constraints(schema: dict[str, Any]) -> str:
    parts = []
    for key, label in (
        ("default", "типово"),
        ("minimum", "мін."),
        ("maximum", "макс."),
        ("minLength", "мін. довжина"),
        ("maxLength", "макс. довжина"),
        ("minItems", "мін. елементів"),
        ("maxItems", "макс. елементів"),
        ("pattern", "шаблон"),
    ):
        if key in schema:
            parts.append(f"{label} `{json.dumps(schema[key], ensure_ascii=False)}`")
    return "; ".join(parts)


def merged(schema: Any, base: Path, res: Resolver) -> tuple[dict[str, Any], set[str], Path]:
    """Properties and required names of an object schema (allOf merged)."""
    node, base, _ = res.resolve(schema, base)
    if not isinstance(node, dict):
        return {}, set(), base
    props: dict[str, Any] = {}
    required: set[str] = set(node.get("required", []))
    for part in node.get("allOf", []):
        p, r, _ = merged(part, base, res)
        props |= p
        required |= r
    props |= node.get("properties", {})
    return props, required, base


def field_rows(
    schema: Any,
    base: Path,
    res: Resolver,
    prefix: str = "",
    depth: int = 0,
    seen: frozenset[int] = frozenset(),
) -> list[str]:
    props, required, base = merged(schema, base, res)
    rows = []
    for name, sub in props.items():
        node, nbase, _ = res.resolve(sub, base)
        node = node if isinstance(node, dict) else {}
        desc = first_line(
            node.get("description") or (sub.get("description") if isinstance(sub, dict) else "")
        )
        extra = constraints(node)
        rows.append(
            f"| `{prefix}{name}` | {type_of(sub, base, res)} | {'так' if name in required else 'ні'} | "
            f"{md_cell(desc)}{'; ' if desc and extra else ''}{md_cell(extra)} |"
        )
        key = id(node)
        if depth < 2 and key not in seen:
            if node.get("properties") or node.get("allOf"):
                rows += field_rows(node, nbase, res, f"{prefix}{name}.", depth + 1, seen | {key})
            elif node.get("type") == "array":
                item, ibase, _ = res.resolve(node.get("items", {}), nbase)
                if isinstance(item, dict) and (item.get("properties") or item.get("allOf")):
                    rows += field_rows(item, ibase, res, f"{prefix}{name}[].", depth + 1, seen | {key})
    return rows


def example_values(media: dict[str, Any], base: Path, res: Resolver) -> Iterator[tuple[str, Any]]:
    if "example" in media:
        yield "приклад", media["example"]
    for name, ex in (media.get("examples") or {}).items():
        node, nbase, _ = res.resolve(ex, base)
        if isinstance(node, dict) and "value" in node:
            value = node["value"]
            if isinstance(value, dict) and "$ref" in value:
                value, _, _ = res.resolve(value, nbase)
            yield name, value
        elif isinstance(node, dict) and "externalValue" in node:
            yield name, res.load((nbase.parent / node["externalValue"]).resolve())
        else:
            yield name, node


def render_examples(media: dict[str, Any], base: Path, res: Resolver) -> list[str]:
    out = []
    for name, value in example_values(media, base, res):
        out += [
            f"Приклад `{name}`:",
            "",
            "```json",
            json.dumps(value, ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    return out


@dataclass
class Operation:
    api: str
    method: str
    path: str
    op: dict[str, Any]
    base: Path
    line: int

    @property
    def op_id(self) -> str:
        return str(self.op.get("operationId") or f"{self.method}_{self.path}")


def operations(api: str, res: Resolver) -> list[Operation]:
    spec_path = OPENAPI / f"{api}.v1.yaml"
    spec = res.load(spec_path)
    ops = []
    for path, item in (spec.get("paths") or {}).items():
        item_node, item_base, _ = res.resolve(item, spec_path)
        common_params = item_node.get("parameters", [])
        for method in HTTP_METHODS:
            if method in item_node:
                op = dict(item_node[method])
                op["parameters"] = common_params + op.get("parameters", [])
                needle = f"operationId: {op.get('operationId')}"
                line = line_of(item_base, needle)
                ops.append(Operation(api, method.upper(), path, op, item_base, line))
    return ops


def idempotency(op: Operation, res: Resolver) -> str:
    for p in op.op.get("parameters", []):
        node, _, _ = res.resolve(p, op.base)
        if isinstance(node, dict) and node.get("name") == "Idempotency-Key":
            return (
                "обов'язковий `Idempotency-Key`"
                if node.get("required")
                else "необов'язковий `Idempotency-Key`"
            )
    if note := op.op.get("x-jane-no-idempotency-key"):
        return f"не потрібна: {note}"
    return "—"


def scope(op: Operation) -> str:
    s = op.op.get("x-jane-scope")
    if s in (None, []):
        return "без автентифікації" if s == [] else "—"
    return ", ".join(f"`{x}`" for x in (s if isinstance(s, list) else [s]))


def render_operation(op: Operation, page: Path, res: Resolver) -> str:
    o = op.op
    src = op.base
    lines = [
        f"# {op.method} {op.path}",
        "",
        GENERATED.format(source=f"[{src.name}]({rel(src, page)}#L{op.line})"),
        "",
        f"**{md_cell(o.get('summary', ''))}**",
        "",
        "| Властивість | Значення |",
        "|---|---|",
        f"| operationId | `{op.op_id}` |",
        f"| Метод і шлях | `{op.method} {op.path}` |",
        f"| Scope | {scope(op)} |",
        f"| Ідемпотентність | {md_cell(idempotency(op, res))} |",
        f"| Теги | {', '.join(o.get('tags', [])) or '—'} |",
        "",
    ]
    if desc := o.get("description"):
        lines += [code_safe(desc), ""]
    params = []
    for p in o.get("parameters", []):
        node, nbase, _ = res.resolve(p, op.base)
        if not isinstance(node, dict):
            continue
        schema = node.get("schema", {})
        params.append(
            f"| `{node.get('name')}` | {node.get('in')} | {type_of(schema, nbase, res)} | "
            f"{'так' if node.get('required') else 'ні'} | {md_cell(first_line(node.get('description')))} |"
        )
    if params:
        lines += [
            "## Параметри",
            "",
            "| Назва | Де | Тип | Обов'язковий | Опис |",
            "|---|---|---|---|---|",
            *params,
            "",
        ]
    if body := o.get("requestBody"):
        bnode, bbase, _ = res.resolve(body, op.base)
        lines += ["## Тіло запиту", ""]
        if d := bnode.get("description"):
            lines += [code_safe(d), ""]
        for media_type, media in (bnode.get("content") or {}).items():
            schema = media.get("schema", {})
            lines += [
                f"Тип вмісту `{media_type}`, схема {type_of(schema, bbase, res)}; обов'язкове: {'так' if bnode.get('required') else 'ні'}.",
                "",
            ]
            rows = field_rows(schema, bbase, res)
            if rows:
                lines += ["| Поле | Тип | Обов'язкове | Опис |", "|---|---|---|---|", *rows, ""]
            lines += render_examples(media, bbase, res)
    lines += ["## Відповіді", ""]
    responses = o.get("responses") or {}
    lines += ["| Код | Опис | Схема |", "|---|---|---|"]
    details: list[str] = []
    for code, resp in responses.items():
        rnode, rbase, _ = res.resolve(resp, op.base)
        content = (rnode or {}).get("content") or {}
        schemas = ", ".join(type_of(m.get("schema", {}), rbase, res) for m in content.values()) or "—"
        lines.append(f"| `{code}` | {md_cell(first_line(rnode.get('description')))} | {schemas} |")
        if str(code).startswith("2"):
            for media_type, media in content.items():
                rows = field_rows(media.get("schema", {}), rbase, res)
                title = f"### Відповідь {code}" + (f" ({media_type})" if len(content) > 1 else "")
                details += [title, "", f"Тип вмісту `{media_type}`.", ""]
                if rows:
                    details += ["| Поле | Тип | Обов'язкове | Опис |", "|---|---|---|---|", *rows, ""]
                details += render_examples(media, rbase, res)
    lines += ["", *details]
    errors = [c for c in responses if not str(c).startswith("2")]
    notes = []
    if errors:
        notes.append(
            "Помилки повертаються як `application/problem+json` "
            f"([модель помилок]({rel(ROOT / 'contracts/docs/errors.md', page)})): "
            + ", ".join(f"`{c}`" for c in errors)
            + "."
        )
    if "202" in {str(c) for c in responses}:
        notes.append(
            "Операція асинхронна: `202` повертає job; стан, прогрес і результат — через `GET /v1/jobs/{job_id}`."
        )
    if notes:
        lines += ["## Примітки", "", *[f"- {n}" for n in notes], ""]
    return "\n".join(lines).rstrip() + "\n"


def api_dir(api: str) -> Path:
    if api in SHARED_APIS:
        return ROOT / SHARED_APIS[api]
    return DOCS / "components" / OWN_APIS[api] / "reference" / "api"


def render_api_index(api: str, ops: list[Operation], res: Resolver) -> dict[Path, str]:
    spec_path = OPENAPI / f"{api}.v1.yaml"
    spec = res.load(spec_path)
    out_dir = api_dir(api)
    page = out_dir / "README.md"
    info = spec.get("info", {})
    files: dict[Path, str] = {}
    lines = [
        f"# API {api}.v1",
        "",
        GENERATED.format(source=f"[{spec_path.name}]({rel(spec_path, page)})"),
        "",
        f"**{md_cell(info.get('title', ''))}**, версія `{info.get('version', '')}`.",
        "",
    ]
    if desc := info.get("description"):
        lines += [code_safe(desc), ""]
    lines += [
        "Спільні правила для всіх операцій: автентифікація `Authorization: Bearer <ключ або JWT>` і scope операції, "
        f"помилки `application/problem+json` ([модель помилок]({rel(ROOT / 'contracts/docs/errors.md', page)})), "
        "ідемпотентність через `Idempotency-Key`, асинхронні операції — `202` і job, курсорна пагінація "
        "(`cursor`, `limit`, `next_cursor`).",
        "",
        "## Операції",
        "",
        "| Метод | Шлях | Операція | Scope | Призначення |",
        "|---|---|---|---|---|",
    ]
    for op in ops:
        lines.append(
            f"| {op.method} | `{op.path}` | [{op.op_id}]({op.op_id}.md) | {scope(op)} | {md_cell(op.op.get('summary', ''))} |"
        )
        files[out_dir / f"{op.op_id}.md"] = render_operation(op, out_dir / f"{op.op_id}.md", res)
    files[page] = "\n".join(lines) + "\n"
    return files


def render_module_api(module: str, apis: list[str]) -> str:
    page = DOCS / "components" / module / "reference" / "api" / "README.md"
    lines = [f"# API: {TITLES[module]}", "", GENERATED.format(source="контрактів `contracts/openapi`"), ""]
    lines += ["Модуль реалізує такі контракти:", "", "| Контракт | Довідник |", "|---|---|"]
    for api in apis:
        target = api_dir(api) / "README.md"
        if target == page:
            continue
        lines.append(f"| `{api}.v1` | [{rel(target, page)}]({rel(target, page)}) |")
    return "\n".join(lines) + "\n"


def generate_api(res: Resolver) -> dict[Path, str]:
    files: dict[Path, str] = {}
    apis = sorted(set(SHARED_APIS) | set(OWN_APIS))
    index = DOCS / "reference" / "api" / "README.md"
    rows = []
    for api in apis:
        ops = operations(api, res)
        pages = render_api_index(api, ops, res)
        own_index = api_dir(api) / "README.md"
        if api in OWN_APIS and api in MODULE_APIS[OWN_APIS[api]] and len(MODULE_APIS[OWN_APIS[api]]) > 1:
            # module with several contracts: its own contract index + a short list of the others
            extra = [a for a in MODULE_APIS[OWN_APIS[api]] if a != api]
            text = pages[own_index].rstrip("\n") + "\n\n## Інші контракти модуля\n\n"
            for a in extra:
                target = api_dir(a) / "README.md"
                text += f"- `{a}.v1` — [{rel(target, own_index)}]({rel(target, own_index)})\n"
            pages[own_index] = text
        files |= pages
        info = res.load(OPENAPI / f"{api}.v1.yaml").get("info", {})
        rows.append(
            f"| `{api}.v1` | {md_cell(info.get('title', ''))} | {len(ops)} | [{rel(own_index, index)}]({rel(own_index, index)}) |"
        )
    for module, apis_of in MODULE_APIS.items():
        page = DOCS / "components" / module / "reference" / "api" / "README.md"
        if page not in files:
            files[page] = render_module_api(module, apis_of)
    for module, text in (
        ("jane-kit", "HTTP API не має; публічний інтерфейс — типи й функції бібліотеки."),
        ("extractor-sdk", "HTTP API не має; публічний інтерфейс — типи й функції SDK."),
        (
            "contracts",
            "Каталог усіх HTTP-контрактів — [загальний довідник API](../../../../reference/api/README.md); Python Protocol-и — у довіднику типів.",
        ),
        (
            "admin",
            "Admin UI не надає власного API; він викликає API сервісів — [загальний довідник API](../../../../reference/api/README.md).",
        ),
    ):
        page = DOCS / "components" / module / "reference" / "api" / "README.md"
        types = DOCS / "components" / module / "reference" / "types" / "README.md"
        files[page] = (
            f"# API: {TITLES[module]}\n\n{GENERATED.format(source='каталогу модулів')}\n\n{text}\n\n"
            f"Довідник типів — [{rel(types, page)}]({rel(types, page)}).\n"
        )
    files[index] = (
        "\n".join(
            [
                "# Довідник HTTP API",
                "",
                GENERATED.format(source=f"[contracts/openapi]({rel(OPENAPI, index)})"),
                "",
                "Кожен контракт описано один раз; модулі, що його реалізують, посилаються сюди.",
                "",
                "| Контракт | Назва | Операцій | Довідник |",
                "|---|---|---|---|",
                *rows,
                "",
                "| Модуль | Контракти |",
                "|---|---|",
                *[
                    f"| [{TITLES[m]}]({rel(DOCS / 'components' / m / 'reference/api/README.md', index)}) | "
                    + ", ".join(f"`{a}.v1`" for a in a_list)
                    + " |"
                    for m, a_list in MODULE_APIS.items()
                ],
            ]
        )
        + "\n"
    )
    return files


# ---------------------------------------------------------------------------------------------- Python


@dataclass
class PyModule:
    name: str
    path: Path
    tree: ast.Module
    package_root: Path
    defined: dict[str, ast.AST] = field(default_factory=dict)
    reexports: dict[str, str] = field(default_factory=dict)


def is_public(name: str) -> bool:
    return not name.startswith("_")


def iter_modules(root: Path) -> Iterator[PyModule]:
    pkg = root.name
    for path in sorted(root.rglob("*.py")):
        rel_parts = path.relative_to(root).with_suffix("").parts
        if (
            any(p.startswith("_") and p not in ("__init__", "__main__") for p in rel_parts)
            or "_generated" in path.parts
        ):
            continue
        if "tests" in rel_parts:
            continue
        parts = [pkg, *rel_parts]
        if parts[-1] == "__init__":
            parts = parts[:-1]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        yield PyModule(".".join(parts), path, tree, root)


def explicit_all(tree: ast.Module) -> list[str] | None:
    for node in tree.body:
        targets = (
            node.targets
            if isinstance(node, ast.Assign)
            else [node.target]
            if isinstance(node, ast.AnnAssign)
            else []
        )
        for t in targets:
            if (
                isinstance(t, ast.Name)
                and t.id == "__all__"
                and isinstance(node, (ast.Assign, ast.AnnAssign))
                and isinstance(node.value, (ast.List, ast.Tuple))
            ):
                return [
                    e.value
                    for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                ]
    return None


def collect(mod: PyModule) -> None:
    allowed = explicit_all(mod.tree)
    imported: dict[str, str] = {}
    for node in mod.tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            mod.defined[node.name] = node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id != "__all__":
                    mod.defined[t.id] = node
        elif (isinstance(node, ast.ImportFrom) and node.module is not None) or isinstance(
            node, ast.ImportFrom
        ):
            base = mod.name if mod.path.name == "__init__.py" else mod.name.rsplit(".", 1)[0]
            if node.level:
                anchor = base.split(".")
                anchor = anchor[: len(anchor) - (node.level - 1)] if node.level > 1 else anchor
                source = ".".join(anchor + ([node.module] if node.module else []))
            else:
                source = node.module or ""
            for alias in node.names:
                imported[alias.asname or alias.name] = source
    names = allowed if allowed is not None else [n for n in mod.defined if is_public(n)]
    mod.defined = {n: mod.defined[n] for n in names if n in mod.defined}
    if allowed is not None:
        mod.reexports = {n: imported[n] for n in allowed if n in imported and n not in mod.defined}


def unparse(node: ast.AST | None) -> str:
    return ast.unparse(node) if node is not None else ""


def signature(fn: ast.FunctionDef | ast.AsyncFunctionDef, owner: str | None = None) -> str:
    a = fn.args
    parts: list[str] = []
    positional = a.posonlyargs + a.args
    defaults = [None] * (len(positional) - len(a.defaults)) + list(a.defaults)
    for i, (arg, default) in enumerate(zip(positional, defaults, strict=True)):
        text = arg.arg + (f": {unparse(arg.annotation)}" if arg.annotation else "")
        if default is not None:
            text += f" = {unparse(default)}" if arg.annotation else f"={unparse(default)}"
        parts.append(text)
        if a.posonlyargs and i == len(a.posonlyargs) - 1:
            parts.append("/")
    if a.vararg:
        parts.append(
            "*" + a.vararg.arg + (f": {unparse(a.vararg.annotation)}" if a.vararg.annotation else "")
        )
    elif a.kwonlyargs:
        parts.append("*")
    for arg, default in zip(a.kwonlyargs, a.kw_defaults, strict=True):
        text = arg.arg + (f": {unparse(arg.annotation)}" if arg.annotation else "")
        if default is not None:
            text += f" = {unparse(default)}" if arg.annotation else f"={unparse(default)}"
        parts.append(text)
    if a.kwarg:
        parts.append("**" + a.kwarg.arg + (f": {unparse(a.kwarg.annotation)}" if a.kwarg.annotation else ""))
    prefix = "async def" if isinstance(fn, ast.AsyncFunctionDef) else "def"
    ret = f" -> {unparse(fn.returns)}" if fn.returns else ""
    decorators = "".join(f"@{unparse(d)}\n" for d in fn.decorator_list)
    one = f"{decorators}{prefix} {fn.name}({', '.join(parts)}){ret}: ..."
    if len(one.splitlines()[-1]) <= 100:
        return one
    inner = "".join(f"    {p},\n" for p in parts)
    return f"{decorators}{prefix} {fn.name}(\n{inner}){ret}: ..."


def raised(fn: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            text = unparse(exc)
            if re.fullmatch(r"[A-Za-z_][\w.]*", text) and text[0].isupper() and text not in names:
                names.append(text)
    return names


def docstring(node: ast.AST) -> str:
    doc = (
        ast.get_docstring(node)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module))
        else None
    )
    return code_safe(doc) if doc else ""


def attr_docs(body: list[ast.stmt]) -> dict[str, str]:
    """Attribute docstrings: a string literal right after an (annotated) assignment."""
    docs = {}
    for prev, node in itertools.pairwise(body):
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            target = (
                prev.target
                if isinstance(prev, ast.AnnAssign)
                else prev.targets[0]
                if isinstance(prev, ast.Assign)
                else None
            )
            if isinstance(target, ast.Name):
                docs[target.id] = " ".join(node.value.value.split())
    return docs


def class_kind(cls: ast.ClassDef) -> str:
    bases = [unparse(b) for b in cls.bases]
    decos = [unparse(d) for d in cls.decorator_list]
    if any(b.endswith("Protocol") or b.startswith("Protocol[") for b in bases):
        return "протокол"
    if any(re.search(r"\b(Enum|StrEnum|IntEnum|Flag)\b", b) for b in bases):
        return "перелік"
    if any("TypedDict" in b for b in bases):
        return "TypedDict"
    if any(d.startswith("dataclass") or d.startswith("dataclasses.dataclass") for d in decos):
        frozen = any("frozen=True" in d for d in decos)
        return "dataclass (незмінний)" if frozen else "dataclass"
    if any(b.endswith(("Exception", "Error")) for b in bases):
        return "виняток"
    if any(b.endswith(("BaseModel", "BaseSettings", "Settings", "JaneSettings")) for b in bases):
        return "модель Pydantic"
    if any(b in ("NamedTuple",) for b in bases):
        return "NamedTuple"
    return "клас"


def anchor(text: str) -> str:
    import unicodedata

    text = text.replace("`", "").strip().lower()
    return "".join(ch for ch in text if ch in " -_" or unicodedata.category(ch)[0] in "LNM").replace(" ", "-")


def src_link(mod: PyModule, node: ast.AST, page: Path) -> str:
    line = getattr(node, "lineno", 1)
    return f"[{mod.path.name}:{line}]({rel(mod.path, page)}#L{line})"


def render_class(mod: PyModule, cls: ast.ClassDef, page: Path) -> list[str]:
    kind = class_kind(cls)
    bases = [unparse(b) for b in cls.bases if unparse(b) not in ("object",)]
    protocols = [b for b in bases if "Protocol" in b]
    out = [f"### Клас `{cls.name}`", ""]
    meta = ["| Властивість | Значення |", "|---|---|", f"| Вид | {kind} |", f"| Модуль | `{mod.name}` |"]
    if bases:
        meta.append(f"| Успадкування | {', '.join(f'`{b}`' for b in bases)} |")
    if protocols and kind != "протокол":
        meta.append(f"| Реалізує | {', '.join(f'`{b}`' for b in protocols)} |")
    meta.append(f"| Код | {src_link(mod, cls, page)} |")
    out += [*meta, ""]
    decl = (
        "".join(f"@{unparse(d)}\n" for d in cls.decorator_list)
        + f"class {cls.name}"
        + (
            f"({', '.join(unparse(b) for b in cls.bases + cls.keywords)})"
            if cls.bases or cls.keywords
            else ""
        )
        + ": ..."
    )
    out += ["```python", decl, "```", ""]
    if doc := docstring(cls):
        out += [doc, ""]
    docs = attr_docs(cls.body)
    frozen = "незмінний" in kind or any(
        isinstance(n, ast.Assign)
        and "frozen=True" in unparse(n.value)
        and any(isinstance(t, ast.Name) and t.id in ("model_config", "Config") for t in n.targets)
        for n in cls.body
    )
    enum = kind == "перелік"
    fields, consts, props, methods = [], [], {}, []
    for node in cls.body:
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and is_public(node.target.id)
        ):
            ann = unparse(node.annotation)
            access = (
                "читання"
                if frozen or ann.startswith("ClassVar") or kind == "NamedTuple"
                else "читання й запис"
            )
            default = unparse(node.value) if node.value is not None else "—"
            fields.append(
                f"| `{node.target.id}` | `{md_cell(ann)}` | {f'`{md_cell(default[:80])}`' if default != '—' else '—'} | {access} | {md_cell(docs.get(node.target.id, ''))} |"
            )
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and is_public(t.id):
                    consts.append(
                        f"| `{t.id}` | `{md_cell(unparse(node.value)[:80])}` | {md_cell(docs.get(t.id, ''))} |"
                    )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decos = [unparse(d) for d in node.decorator_list]
            if "property" in decos or "cached_property" in decos or "functools.cached_property" in decos:
                if is_public(node.name):
                    props[node.name] = [unparse(node.returns) or "—", "читання", first_line(docstring(node))]
            elif any(d.endswith(".setter") for d in decos):
                if node.name in props:
                    props[node.name][1] = "читання й запис"
            elif is_public(node.name) or node.name in (
                "__init__",
                "__call__",
                "__enter__",
                "__exit__",
                "__aenter__",
                "__aexit__",
                "__iter__",
                "__len__",
            ):
                methods.append(node)
    if fields or props:
        out += [
            "**Поля й властивості**",
            "",
            "| Член | Тип | Типове значення | Доступ | Опис |",
            "|---|---|---|---|---|",
            *fields,
        ]
        out += [
            f"| `{n}` | `{md_cell(t)}` | — | {a} (властивість) | {md_cell(d)} |"
            for n, (t, a, d) in props.items()
        ]
        out.append("")
        if kind.startswith("модель Pydantic") or kind.startswith("dataclass"):
            out += [
                "Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.",
                "",
            ]
    if consts:
        out += [
            "**Значення переліку**" if enum else "**Атрибути класу**",
            "",
            "| Назва | Значення | Опис |",
            "|---|---|---|",
            *consts,
            "",
        ]
    for fn in methods:
        title = "Конструктор" if fn.name == "__init__" else "Метод"
        out += [f"#### {title} `{cls.name}.{fn.name}`", "", "```python", signature(fn), "```", ""]
        if doc := docstring(fn):
            out += [doc, ""]
        if exc := raised(fn):
            out += [f"Винятки в коді методу: {', '.join(f'`{e}`' for e in exc)}.", ""]
        out += [f"Код: {src_link(mod, fn, page)}.", ""]
    return out


def render_py_module(mod: PyModule, page: Path, module_index: dict[str, Path]) -> str:
    out = [
        f"# Модуль `{mod.name}`",
        "",
        GENERATED.format(source=f"[{mod.path.relative_to(ROOT).as_posix()}]({rel(mod.path, page)})"),
        "",
    ]
    if doc := docstring(mod.tree):
        out += [doc, ""]
    classes = [n for n in mod.defined.values() if isinstance(n, ast.ClassDef)]
    funcs = [n for n in mod.defined.values() if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    consts = [(name, n) for name, n in mod.defined.items() if isinstance(n, (ast.Assign, ast.AnnAssign))]
    toc = []
    if classes:
        toc += [f"- [Клас `{c.name}`](#{anchor('Клас ' + c.name)})" for c in classes]
    if funcs:
        toc += [f"- [Функція `{f.name}`](#{anchor('Функція ' + f.name)})" for f in funcs]
    if len(toc) > 3:
        out += ["## Зміст", "", *toc, ""]
    if classes:
        out += ["## Класи", ""]
        for c in classes:
            out += render_class(mod, c, page)
    if funcs:
        out += ["## Функції", ""]
        for f in funcs:
            out += [f"### Функція `{f.name}`", "", "```python", signature(f), "```", ""]
            if doc := docstring(f):
                out += [doc, ""]
            if exc := raised(f):
                out += [f"Винятки в коді функції: {', '.join(f'`{e}`' for e in exc)}.", ""]
            out += [f"Код: {src_link(mod, f, page)}.", ""]
    if consts:
        docs = attr_docs(mod.tree.body)
        out += ["## Константи й змінні модуля", "", "| Назва | Тип | Значення | Опис |", "|---|---|---|---|"]
        for name, n in consts:
            ann = unparse(n.annotation) if isinstance(n, ast.AnnAssign) else ""
            value = unparse(n.value)[:80] if n.value is not None else "—"
            out.append(
                f"| `{name}` | {f'`{md_cell(ann)}`' if ann else '—'} | `{md_cell(value)}` | {md_cell(docs.get(name, ''))} |"
            )
        out.append("")
    if mod.reexports:
        out += ["## Реекспорт", "", "| Назва | Визначено в |", "|---|---|"]
        for name, source in mod.reexports.items():
            target = module_index.get(source)
            where = f"[`{source}`]({rel(target, page)})" if target else f"`{source}`"
            out.append(f"| `{name}` | {where} |")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def generate_python(module: str) -> dict[Path, str]:
    out_dir = DOCS / "components" / module / "reference" / "types"
    mods: list[PyModule] = []
    for root in PY_MODULES[module]:
        for mod in iter_modules(ROOT / root):
            collect(mod)
            mods.append(mod)
    index = {m.name: out_dir / f"{m.name}.md" for m in mods}
    files = {index[m.name]: render_py_module(m, index[m.name], index) for m in mods}
    page = out_dir / "README.md"
    lines = [
        f"# Типи й члени: {TITLES[module]}",
        "",
        GENERATED.format(source=", ".join(f"[{r}]({rel(ROOT / r, page)})" for r in PY_MODULES[module])),
        "",
        "Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. "
        "Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.",
        "",
        "## Модулі",
        "",
        "| Модуль | Класи | Функції | Призначення |",
        "|---|---|---|---|",
    ]
    for m in mods:
        n_cls = sum(isinstance(n, ast.ClassDef) for n in m.defined.values())
        n_fn = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in m.defined.values())
        lines.append(
            f"| [`{m.name}`]({m.name}.md) | {n_cls} | {n_fn} | {md_cell(first_line(ast.get_docstring(m.tree)))[:160]} |"
        )
    entries = []
    for m in mods:
        for name, n in m.defined.items():
            if isinstance(n, ast.ClassDef):
                entries.append(
                    (name, f"[`{name}`]({m.name}.md#{anchor('Клас ' + name)})", class_kind(n), m.name)
                )
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                entries.append(
                    (name, f"[`{name}`]({m.name}.md#{anchor('Функція ' + name)})", "функція", m.name)
                )
    lines += ["", "## Покажчик", "", "| Назва | Вид | Модуль |", "|---|---|---|"]
    for _, link, kind, mname in sorted(entries, key=lambda e: e[0].lower()):
        lines.append(f"| {link} | {kind} | `{mname}` |")
    files[page] = "\n".join(lines) + "\n"
    return files


# ---------------------------------------------------------------------------------------------- TypeScript


def generate_typescript() -> dict[Path, str]:
    out_dir = DOCS / "components" / "admin" / "reference" / "types"
    script = ROOT / "scripts" / "docs_reference_ts.mjs"
    proc = subprocess.run(
        ["node", str(script)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False
    )
    if proc.returncode != 0:
        sys.exit(
            f"TypeScript reference failed (needs `corepack pnpm --dir web/admin install`):\n{proc.stderr}"
        )
    data = json.loads(proc.stdout)
    files: dict[Path, str] = {}
    page = out_dir / "README.md"
    rows, entries = [], []
    for module in data:
        name = module["module"]
        mpage = out_dir / f"{name}.md"
        src = ROOT / module["file"]
        lines = [
            f"# Модуль `{name}`",
            "",
            GENERATED.format(source=f"[{module['file']}]({rel(src, mpage)})"),
            "",
        ]
        if module.get("doc"):
            lines += [code_safe(module["doc"]), ""]
        kinds: dict[str, list[dict[str, Any]]] = {}
        for decl in module["exports"]:
            kinds.setdefault(decl["kind"], []).append(decl)
        titles = {
            "component": "Компоненти React",
            "function": "Функції",
            "interface": "Інтерфейси",
            "type": "Типи",
            "class": "Класи",
            "variable": "Константи",
            "enum": "Переліки",
        }
        for kind in ("component", "function", "class", "interface", "type", "enum", "variable"):
            decls = kinds.get(kind, [])
            if not decls:
                continue
            lines += [f"## {titles[kind]}", ""]
            for d in decls:
                label = {
                    "component": "Компонент",
                    "function": "Функція",
                    "class": "Клас",
                    "interface": "Інтерфейс",
                    "type": "Тип",
                    "enum": "Перелік",
                    "variable": "Константа",
                }[kind]
                lines += [f"### {label} `{d['name']}`", "", "```typescript", d["declaration"], "```", ""]
                if d.get("doc"):
                    lines += [code_safe(d["doc"]), ""]
                if d.get("members"):
                    lines += ["| Член | Тип | Обов'язковий | Доступ | Опис |", "|---|---|---|---|---|"]
                    for mem in d["members"]:
                        lines.append(
                            f"| `{mem['name']}` | `{md_cell(mem['type'])[:120]}` | {'ні' if mem['optional'] else 'так'} | "
                            f"{'читання' if mem['readonly'] else 'читання й запис'} | {md_cell(mem.get('doc', ''))} |"
                        )
                    lines.append("")
                lines += [
                    f"Код: [{Path(module['file']).name}:{d['line']}]({rel(src, mpage)}#L{d['line']}).",
                    "",
                ]
                entries.append(
                    (
                        d["name"],
                        f"[`{d['name']}`]({name}.md#{anchor(label + ' ' + d['name'])})",
                        label.lower(),
                        name,
                    )
                )
        files[mpage] = "\n".join(lines).rstrip() + "\n"
        rows.append(
            f"| [`{name}`]({name}.md) | {len(module['exports'])} | {md_cell(first_line(module.get('doc')))} |"
        )
    files[page] = (
        "\n".join(
            [
                "# Типи й члени: Admin UI",
                "",
                GENERATED.format(source=f"[web/admin/src]({rel(ROOT / 'web/admin/src', page)})"),
                "",
                "Експортовані оголошення модулів `web/admin/src` (без тестів і згенерованих клієнтів `src/api/generated`, "
                f"які відтворюють контракти — [довідник API]({rel(DOCS / 'reference/api/README.md', page)})). "
                "Сигнатури виведено компілятором TypeScript.",
                "",
                "## Модулі",
                "",
                "| Модуль | Експортів | Призначення |",
                "|---|---|---|",
                *rows,
                "",
                "## Покажчик",
                "",
                "| Назва | Вид | Модуль |",
                "|---|---|---|",
                *[
                    f"| {link} | {kind} | `{mod}` |"
                    for _, link, kind, mod in sorted(entries, key=lambda e: e[0].lower())
                ],
            ]
        )
        + "\n"
    )
    return files


# ---------------------------------------------------------------------------------------------- main


def generate_all() -> dict[Path, str]:
    res = Resolver()
    files = generate_api(res)
    for module in PY_MODULES:
        files |= generate_python(module)
    files |= generate_typescript()
    return files


def generated_roots() -> list[Path]:
    roots = [ROOT / p for p in SHARED_APIS.values()] + [DOCS / "reference" / "api" / "README.md"]
    for module in {*PY_MODULES, *MODULE_APIS, "admin"}:
        roots += [
            DOCS / "components" / module / "reference" / "api",
            DOCS / "components" / module / "reference" / "types",
        ]
    return roots


def existing_generated() -> set[Path]:
    found = set()
    for root in generated_roots():
        paths = [root] if root.is_file() else root.rglob("*.md") if root.is_dir() else []
        for p in paths:
            if "Згенеровано `scripts/docs_reference.py`" in p.read_text(encoding="utf-8"):
                found.add(p.resolve())
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("generate", "check"))
    ns = parser.parse_args()
    files = {p.resolve(): text for p, text in generate_all().items()}
    stale = existing_generated() - set(files)
    if ns.command == "generate":
        for p in stale:
            p.unlink()
        for p, text in files.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists() or p.read_text(encoding="utf-8") != text:
                p.write_text(text, encoding="utf-8", newline="\n")
        print(f"{len(files)} files generated, {len(stale)} stale removed")
        return 0
    bad = [
        p
        for p, text in files.items()
        if not p.exists() or p.read_text(encoding="utf-8").replace("\r\n", "\n") != text
    ]
    for p in sorted(set(bad) | stale):
        print(f"outdated: {p.relative_to(ROOT).as_posix()}")
    print(f"{len(files)} generated files, {len(bad) + len(stale)} outdated")
    return 1 if bad or stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
