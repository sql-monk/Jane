"""Generate deterministic source-backed public API inventories and Markdown references."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from common import ROOT, cell, code, digest, json_text, read, relative, slug
from manual_coverage import load as manual_coverage
from python_symbols import configuration, extract
from usage import examples

METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
KIND = {
    "class": "Клас",
    "interface": "Інтерфейс",
    "type": "Тип",
    "enum": "Перелік",
    "function": "Функція",
    "method": "Метод",
    "constructor": "Конструктор",
    "generated-constructor": "Конструктор dataclass",
    "property": "Властивість",
    "field": "Поле",
    "instance-field": "Поле екземпляра",
    "constant": "Константа",
    "variable": "Змінна",
    "reexport": "Повторний експорт",
}


def sources(root: Path) -> list[tuple[str, Path, Path]]:
    result = []
    for family in ("services", "libs"):
        for component in sorted((root / family).iterdir()):
            if not component.is_dir():
                continue
            for source_root in sorted(component.rglob("src")):
                if any(
                    part in {"node_modules", ".venv", "tests", "__pycache__"} for part in source_root.parts
                ):
                    continue
                for path in sorted(source_root.rglob("*.py")):
                    result.append((component.name, path, source_root))
    discovery = root / "services/web-collector/strategies"
    for path in sorted(discovery.rglob("*.py")):
        result.append(("web-collector", path, discovery))
    # Repository public Protocols participate in consumers' Python surface.
    contract_root = root / "contracts/python/src"
    for path in sorted(contract_root.rglob("*.py")):
        result.append(("jane-kit", path, contract_root))
    return result


def source_link(root: Path, page: Path, record: dict[str, Any]) -> str:
    return (
        f"[{record['source']}:{record['line']}]({relative(page, root / record['source'])}#L{record['line']})"
    )


def symbol_page(
    root: Path, page: Path, module: str, records: list[dict[str, Any]], by_id: dict[str, Any]
) -> str:
    lines = [
        f"# {module}",
        "",
        "Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.",
        "",
        "## Зміст",
        "",
    ]
    lines += [f"- [{x['id']}](#{slug(x['id'])})" for x in records]
    lines.append("")
    for record in records:
        lines += [
            f"## {record['id']}",
            "",
            f"**{KIND.get(record['kind'], record['kind'])}.** Код: {source_link(root, page, record)}.",
            "",
            code(record["signature"], record["language"]),
        ]
        if record.get("overloads"):
            lines += ["Варіанти сигнатури:", "", code("\n".join(record["overloads"]), record["language"])]
        if record.get("call_signatures"):
            lines += [
                "Сигнатури виклику:",
                "",
                code("\n".join(record["call_signatures"]), record["language"]),
            ]
        if record.get("target"):
            target = by_id.get(record["target"])
            if target:
                url = (
                    relative(page, root / target["document"].split("#")[0])
                    + "#"
                    + target["document"].split("#")[1]
                )
                lines += [f"Повторний експорт: [{record['target']}]({url}).", ""]
            else:
                lines += [f"Повторний експорт із `{record['target']}`.", ""]
        if record.get("bases"):
            lines += ["Базові типи / інтерфейси: " + ", ".join(f"`{x}`" for x in record["bases"]) + ".", ""]
        if record.get("decorators"):
            lines += ["Декоратори: " + ", ".join(f"`{x}`" for x in record["decorators"]) + ".", ""]
        if record.get("parameters"):
            lines += [
                "### Параметри",
                "",
                "| Ім’я | Тип | Типове значення | Спосіб передавання |",
                "|---|---|---|---|",
            ]
            for param in record["parameters"]:
                default = param.get("default")
                if default is None:
                    default = "—"
                if param.get("default_factory"):
                    default = "factory: " + param["default_factory"]
                lines.append(
                    f"| `{cell(param['name'])}` | `{cell(param.get('type') or 'не вказано')}` | `{cell(default)}` | {cell(param['kind'])} |"
                )
            lines.append("")
        if record.get("returns") is not None:
            lines += [f"Результат: `{record['returns']}`.", ""]
        if "readable" in record:
            lines += [
                f"Доступ: читання — {'так' if record['readable'] else 'ні'}; запис — {'так' if record.get('writable') else 'ні'}.",
                "",
            ]
            if record.get("accessors"):
                lines += [code("\n".join(record["accessors"]), record["language"])]
        if record.get("raises"):
            lines += [
                "Явні `raise` у тілі: "
                + ", ".join(f"`{x}`" for x in record["raises"])
                + ". Винятки викликаних залежностей описуються у ручному довіднику.",
                "",
            ]
        if record.get("constraints"):
            lines += ["Обмеження й метадані декларації:", "", code(json_text(record["constraints"]), "json")]
        if record.get("members"):
            lines += ["### Публічні члени", "", "| Член | Тип | Успадковано |", "|---|---|---|"]
            for member in record["members"]:
                target = by_id.get(member["id"])
                if target:
                    url = (
                        relative(page, root / target["document"].split("#")[0])
                        + "#"
                        + target["document"].split("#")[1]
                    )
                    link = f"[{cell(member['name'])}]({url})"
                else:
                    link = f"`{cell(member['name'])}`"
                lines.append(
                    f"| {link} | {KIND.get(member['kind'], member['kind'])} | {'так' if member.get('inherited') else 'ні'} |"
                )
            lines.append("")
        if record.get("docstring"):
            lines += ["### Опис із вихідного коду", "", code(record["docstring"], "text")]
        if record.get("examples"):
            lines += ["### Приклади з тестів", ""]
            for example in record["examples"]:
                lines += [
                    f"Контекст і передумови: {source_link(root, page, example)}.",
                    "",
                    code(example["code"], example["language"]),
                ]
    return "\n".join(lines).rstrip() + "\n"


class Contracts:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.documents: dict[Path, Any] = {}

    def load(self, path: Path) -> Any:
        path = path.resolve()
        if not path.is_relative_to(self.root / "contracts"):
            raise ValueError(f"Contract reference outside contracts/: {path}")
        if path not in self.documents:
            self.documents[path] = yaml.safe_load(read(path))
        return self.documents[path]

    def resolve(
        self, value: dict[str, Any], path: Path, visited: frozenset[str] = frozenset()
    ) -> tuple[dict[str, Any], Path]:
        if "$ref" not in value:
            return value, path
        reference = value["$ref"]
        if reference.startswith(("https:", "http:")):
            raise ValueError(f"Remote OpenAPI reference is not reproducible: {reference}")
        file, _, pointer = reference.partition("#")
        target = (path.parent / file).resolve() if file else path
        key = str(target) + "#" + pointer
        if key in visited:
            raise ValueError(f"Reference cycle outside schema: {key}")
        result = self.load(target)
        for part in pointer.split("/")[1:]:
            result = result[part.replace("~1", "/").replace("~0", "~")]
        resolved, origin = self.resolve(result, target, visited | {key})
        return {**resolved, **{k: v for k, v in value.items() if k != "$ref"}}, origin

    def refs(self, value: Any, path: Path) -> list[dict[str, Any]]:
        found = []
        if isinstance(value, dict):
            if "$ref" in value:
                file, _, pointer = value["$ref"].partition("#")
                target = (path.parent / file).resolve() if file else path
                if not target.is_relative_to(self.root / "contracts"):
                    raise ValueError(f"Reference outside contracts/: {value['$ref']}")
                self.load(target)
                found.append({"file": target.relative_to(self.root).as_posix(), "pointer": pointer})
            for child in value.values():
                found += self.refs(child, path)
        elif isinstance(value, list):
            for child in value:
                found += self.refs(child, path)
        return list({(x["file"], x["pointer"]): x for x in found}.values())


def operations(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contracts = Contracts(root)
    records = []
    mapping = {
        "collector": ["web-collector", "telegram-collector"],
        "handler": ["handler-runtime"],
        "storage": ["storage"],
        "registry": ["registry"],
        "orchestrator": ["orchestrator"],
        "llm": ["llm"],
        "assistant": ["assistant"],
    }
    for path in sorted((root / "contracts/openapi").glob("*.v1.yaml")):
        document = contracts.load(path)
        for route, raw_path in document["paths"].items():
            path_item, path_origin = contracts.resolve(raw_path, path)
            for method, raw_operation in path_item.items():
                if method not in METHODS:
                    continue
                operation, origin = contracts.resolve(raw_operation, path_origin)
                op_id = operation.get("operationId")
                if not op_id:
                    raise ValueError(f"Operation without operationId: {path}:{method} {route}")
                params = {}
                refs = []
                for parameter in path_item.get("parameters", []) + operation.get("parameters", []):
                    param, param_origin = contracts.resolve(parameter, origin)
                    params[(param["in"], param["name"])] = param
                    refs += contracts.refs(param, param_origin)
                request, req_origin = contracts.resolve(operation.get("requestBody", {}), origin)
                refs += contracts.refs(request, req_origin)
                responses = {}
                for status, raw_response in operation.get("responses", {}).items():
                    response, res_origin = contracts.resolve(raw_response, origin)
                    responses[str(status)] = response
                    refs += contracts.refs(response, res_origin)
                record = {
                    "operation_id": op_id,
                    "method": method.upper(),
                    "path": route,
                    "summary": operation.get("summary"),
                    "description": operation.get("description"),
                    "parameters": list(params.values()),
                    "request_body": request,
                    "responses": responses,
                    "errors": [x for x in responses if x == "default" or (x.isdigit() and int(x) >= 400)],
                    "security": operation.get("security", document.get("security", [])),
                    "scope": operation.get("x-jane-scope"),
                    "tags": operation.get("tags", []),
                    "extensions": {k: v for k, v in operation.items() if k.startswith("x-")},
                    "source": path.relative_to(root).as_posix(),
                    "definition_source": origin.relative_to(root).as_posix(),
                    "schema_links": list({(x["file"], x["pointer"]): x for x in refs}.values()),
                }
                for component in mapping[path.name.split(".")[0]]:
                    records.append(
                        {
                            **record,
                            "component": component,
                            "document": f"docs/components/{component}/reference/api/generated/{op_id}.md",
                        }
                    )
    inputs = [
        {"path": path.relative_to(root).as_posix(), "sha256": digest(path)}
        for path in sorted(contracts.documents)
    ]
    return sorted(records, key=lambda x: (x["component"], x["path"], x["method"])), inputs


def operation_page(root: Path, record: dict[str, Any]) -> str:
    page = root / record["document"]
    lines = [
        f"# {record['operation_id']}",
        "",
        record.get("summary") or "Операція HTTP API.",
        "",
        f"Контракт: [{record['source']}]({relative(page, root / record['source'])}).",
        "",
        code(f"{record['method']} {record['path']}", "http"),
    ]
    if record.get("description"):
        # Descriptions belong to the contract. Literal block prevents inherited HTML from
        # becoming author markup and preserves exact source provenance.
        lines += ["## Опис із контракту", "", code(record["description"], "text")]
    lines += [
        "## Доступ",
        "",
        code(json_text({"security": record["security"], "scope": record["scope"]}), "json"),
    ]
    lines += ["## Параметри", ""]
    if record["parameters"]:
        lines += ["| Ім’я | Розміщення | Обов’язковий |", "|---|---|---|"]
        lines += [
            f"| `{cell(x['name'])}` | `{cell(x['in'])}` | {'так' if x.get('required') else 'ні'} |"
            for x in record["parameters"]
        ]
        lines += ["", code(json_text(record["parameters"]), "json")]
    else:
        lines += ["Параметрів у контракті немає.", ""]
    lines += [
        "## Тіло запиту",
        "",
        code(json_text(record["request_body"]), "json")
        if record["request_body"]
        else "Тіло запиту не визначено.",
        "",
        "## Відповіді та помилки",
        "",
        "| HTTP | Опис | Помилка |",
        "|---|---|---|",
    ]
    for status, response in record["responses"].items():
        lines.append(
            f"| `{status}` | {cell(response.get('description', ''))} | {'так' if status in record['errors'] else 'ні'} |"
        )
    lines += ["", code(json_text(record["responses"]), "json")]
    if record["extensions"]:
        lines += ["## Метадані поведінки", "", code(json_text(record["extensions"]), "json")]
    if record["schema_links"]:
        lines += ["## Схеми", ""]
        for ref in record["schema_links"]:
            suffix = "#" + ref["pointer"] if ref["pointer"] else ""
            lines.append(f"- [{ref['file']}{suffix}]({relative(page, root / ref['file'])}{suffix})")
    return "\n".join(lines).rstrip() + "\n"


def build(root: Path, typescript: bool = True) -> dict[Path, str]:
    py_symbols, modules, py_inputs = extract(root, sources(root))
    config = configuration(py_symbols, modules)
    ts_inputs = []
    ts_version = None
    ts_symbols = []
    if typescript:
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node is required for the TypeScript compiler parser")
        command = [node, str(root / "scripts/docs/typescript-symbols.mjs"), str(root)]
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
        parsed = json.loads(result.stdout)
        ts_symbols, ts_version = parsed["symbols"], parsed["version"]
        ts_inputs = [{"path": file, "sha256": digest(root / file)} for file in parsed["inputs"]]
    symbols = py_symbols + ts_symbols
    example_inputs, found_examples = examples(root, py_symbols)
    for symbol in symbols:
        name = symbol["module"].replace("/", ".")
        symbol["document"] = (
            f"docs/components/{symbol['component']}/reference/types/generated/{name}.md#{slug(symbol['id'])}"
        )
        symbol["examples"] = found_examples.get(symbol["id"], [])
    by_id = {x["id"]: x for x in symbols}
    for entry in config:
        entry["document"] = by_id.get(entry.get("symbol_id"), {}).get("document")
    manual_inputs, manual = manual_coverage(root, symbols)
    for symbol in symbols:
        if symbol["id"] in manual:
            symbol["manual_documentation"] = manual[symbol["id"]]
    api, contract_inputs = operations(root)
    outputs = {}
    groups = defaultdict(list)
    for symbol in symbols:
        groups[(symbol["component"], symbol["module"])].append(symbol)
    for (_component, module), records in sorted(groups.items()):
        page = root / records[0]["document"].split("#")[0]
        outputs[page] = symbol_page(root, page, module, records, by_id)
    for component in sorted({x["component"] for x in symbols}):
        page = root / f"docs/components/{component}/reference/types/generated/README.md"
        lines = [
            f"# Публічні типи та члени — {component}",
            "",
            "Індекс згенеровано з Python AST і TypeScript compiler API.",
            "",
            "| Модуль | Публічних декларацій |",
            "|---|---|",
        ]
        for (comp, module), records in sorted(groups.items()):
            if comp == component:
                lines.append(
                    f"| [{module}]({Path(records[0]['document'].split('#')[0]).name}) | {len(records)} |"
                )
        outputs[page] = "\n".join(lines) + "\n"
    api_groups = defaultdict(list)
    for record in api:
        outputs[root / record["document"]] = operation_page(root, record)
        api_groups[record["component"]].append(record)
    for component, records in sorted(api_groups.items()):
        page = root / f"docs/components/{component}/reference/api/generated/README.md"
        lines = [
            f"# HTTP API — {component}",
            "",
            "Усі операції чинного OpenAPI, включно зі спільними pathItems.",
            "",
            "| Метод | Шлях | Операція |",
            "|---|---|---|",
        ]
        lines += [
            f"| `{x['method']}` | `{x['path']}` | [{x['operation_id']}]({x['operation_id']}.md) |"
            for x in records
        ]
        outputs[page] = "\n".join(lines) + "\n"
    registry = json.loads(read(root / ".claude/wp-paths.json"))["documentation_packages"]
    meta = {"format_version": 1, "source_revision": registry["base_revision"], "deterministic": True}
    outputs[root / "docs/reference/symbols.json"] = json_text(
        {
            **meta,
            "parsers": {"python": "stdlib-ast", "typescript": ts_version},
            "inputs": sorted(py_inputs + ts_inputs + example_inputs + manual_inputs, key=lambda x: x["path"]),
            "coverage": {
                "symbols": len(symbols),
                "components": sorted({x["component"] for x in symbols}),
                "with_source_description": sum(bool(x.get("docstring")) for x in symbols),
                "with_source_examples": sum(bool(x.get("examples")) for x in symbols),
                "manual_coverage": {
                    "registered_symbols": len(manual),
                    "entries": manual,
                    "semantic_review_required": True,
                },
                "explanation_gap_scope": "Source docstrings and repository test call sites only. This list does not account for manual explanations or prove missing semantic coverage.",
                "explanation_gaps": [
                    {
                        "id": x["id"],
                        "missing": [
                            field
                            for field, present in (
                                ("purpose-docstring", bool(x.get("docstring"))),
                                ("usage-example", bool(x.get("examples"))),
                                (
                                    "dependency-exceptions",
                                    x["kind"]
                                    not in {"function", "method", "constructor", "generated-constructor"},
                                ),
                            )
                            if not present
                        ],
                        "document": x["document"],
                    }
                    for x in symbols
                    if not x.get("docstring")
                    or not x.get("examples")
                    or x["kind"] in {"function", "method", "constructor", "generated-constructor"}
                ],
                "source_files": len(py_inputs) + len(ts_inputs),
                "policy": "__all__ when declared; otherwise public declarations; reexports, repo-defined inherited members, dataclass constructors, explicit TypeScript exports. External dependency members are not copied.",
            },
            "symbols": symbols,
        }
    )
    outputs[root / "docs/reference/api-operations.json"] = json_text(
        {
            **meta,
            "inputs": contract_inputs,
            "coverage": {"operations": len(api), "components": sorted(api_groups)},
            "operations": api,
        }
    )
    outputs[root / "docs/reference/configuration.json"] = json_text(
        {
            **meta,
            "inputs": py_inputs,
            "coverage": {
                "entries": len(config),
                "policy": "AST Settings/inherited fields/limit models and explicit getenv/environ reads; no ENV values or production imports.",
            },
            "entries": config,
        }
    )
    return outputs


def synchronize(root: Path, outputs: dict[Path, str], check: bool) -> tuple[int, list[str]]:
    existing = set((root / "docs/components").glob("*/reference/*/generated/**/*.md"))
    expected = set(outputs)
    stale = sorted(existing - expected)
    changed = sorted(path for path, value in outputs.items() if not path.is_file() or read(path) != value)
    issues = [f"stale: {x.relative_to(root).as_posix()}" for x in stale] + [
        f"drift: {x.relative_to(root).as_posix()}" for x in changed
    ]
    if not check:
        for path in stale:
            path.unlink()
        for path in changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(outputs[path], encoding="utf-8", newline="\n")
    return len(issues), issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--check", action="store_true", help="Compare against code-derived output without changing files"
    )
    parser.add_argument(
        "--python-only", action="store_true", help="Diagnostic mode; not a complete acceptance run"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    outputs = build(root, not args.python_only)
    count, issues = synchronize(root, outputs, args.check)
    print(
        f"Documentation generation: {len(outputs)} outputs, {count} differences; mode={'check' if args.check else 'write'}"
    )
    if args.check:
        for issue in issues[:30]:
            print(issue)
    if args.python_only:
        print("TypeScript was excluded; full coverage is not verified.")
    return 1 if args.check and count else 0


if __name__ == "__main__":
    sys.exit(main())
