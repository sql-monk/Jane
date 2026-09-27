"""Validation of a package before publication: manifest schema, kind <-> entry, referenced files,
schemas, collector rules, tests (ADR-0002, contracts/docs/handler-packages.md).

Schemas are the contract files (``contracts/schemas``); the registry never keeps its own copy.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, SchemaError
from jsonschema.exceptions import best_match
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .archive import MANIFEST_NAME

__all__ = ["ContractSchemas", "Issue", "PackageValidator", "find_contracts_dir"]

MAX_REPORTED = 50


@dataclass(frozen=True)
class Issue:
    pointer: str
    message: str
    code: str | None = None


def find_contracts_dir(configured: Path | None) -> Path:
    """``contracts/`` from settings, ``JANE_CONTRACTS_DIR``, the checkout, or ``/app/contracts`` (image)."""
    from jane_kit.contracts import contracts_dir

    candidates = [configured, contracts_dir(Path(__file__).parent), Path("/app/contracts")]
    for c in candidates:
        if c is not None and (c / "schemas" / "package-manifest.schema.json").is_file():
            return c
    raise FileNotFoundError(
        "contracts/schemas/package-manifest.schema.json not found; set JANE_REGISTRY_CONTRACTS_DIR"
    )


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _pointer(prefix: str, path: Any) -> str:
    return prefix + "".join(f"/{_escape(str(p))}" for p in path)


class ContractSchemas:
    """JSON Schema 2020-12 validators for contract schemas with cross-file ``$ref``."""

    def __init__(self, contracts: Path) -> None:
        self.root = (contracts / "schemas").resolve()
        self._registry: Registry[Any] = Registry(retrieve=self._retrieve)  # type: ignore[call-arg]

    @staticmethod
    def _retrieve(uri: str) -> Resource[Any]:
        from urllib.parse import unquote, urlsplit

        parts = urlsplit(uri)
        raw = unquote(parts.path)
        if len(raw) > 2 and raw[0] == "/" and raw[2] == ":":  # file:///C:/... on Windows
            raw = raw[1:]
        doc = json.loads(Path(raw).read_text(encoding="utf-8"))
        return DRAFT202012.create_resource(doc)

    def validator(self, relative: str, fragment: str = "") -> Draft202012Validator:
        uri = (self.root / relative).as_uri() + (f"#{fragment}" if fragment else "")
        return Draft202012Validator(
            {"$ref": uri}, registry=self._registry, format_checker=Draft202012Validator.FORMAT_CHECKER
        )

    def issues(self, relative: str, instance: Any, prefix: str, fragment: str = "") -> list[Issue]:
        errors = sorted(
            self.validator(relative, fragment).iter_errors(instance), key=lambda e: list(e.absolute_path)
        )
        out: list[Issue] = []
        for e in errors[:MAX_REPORTED]:
            # a failed oneOf/anyOf carries the useful message in its best sub-error
            message = e.message
            if e.context:
                sub = best_match(e.context)
                if sub is not None:
                    message = f"{sub.message} (at {_pointer(prefix, sub.absolute_path)})"
            out.append(Issue(_pointer(prefix, e.absolute_path), message, "schema"))
        return out


_ENTRY_SHAPES: dict[str, tuple[set[str], ...]] = {
    # kind -> accepted entry shapes (keys that identify PythonEntry / ExecutorEntry / ...)
    "extractor": ({"runtime"},),
    "transform": ({"runtime"}, {"executor"}),
    "storage": ({"executor", "adapter", "writes"},),
    "llm": ({"executor", "instructions", "output_schema"},),
    "collector-rules": ({"collector", "rules"},),
}


class PackageValidator:
    def __init__(self, schemas: ContractSchemas, *, require_tests: bool = True) -> None:
        self.schemas = schemas
        self.require_tests = require_tests

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _load_json(files: Mapping[str, bytes], path: str) -> Any:
        return json.loads(files[path].decode("utf-8"))

    def _entry_matches(self, kind: str, entry: Mapping[str, Any]) -> bool:
        shapes = _ENTRY_SHAPES.get(kind, ())
        if not any(shape <= set(entry) for shape in shapes):
            return False
        if kind == "storage":
            return entry.get("executor") == "storage"
        if kind == "llm":
            return entry.get("executor") == "llm"
        if kind == "transform" and "executor" in entry:
            return "runtime" not in entry
        return True

    @staticmethod
    def referenced_paths(manifest: Mapping[str, Any]) -> Iterator[tuple[str, str]]:
        """``(JSON pointer in the manifest, package path)`` of every file the manifest refers to."""
        if isinstance(manifest.get("params_schema"), str):
            yield "/params_schema", manifest["params_schema"]
        entry = manifest.get("entry") or {}
        for key in ("instructions", "input_template", "output_schema", "rules"):
            if isinstance(entry.get(key), str):
                yield f"/entry/{key}", entry[key]
        inp = manifest.get("input") or {}
        if isinstance(inp.get("data_schema"), str):
            yield "/input/data_schema", inp["data_schema"]
        out = manifest.get("output") or {}
        for i, ent in enumerate(out.get("entities") or []):
            if isinstance(ent, Mapping) and isinstance(ent.get("schema"), str):
                yield f"/output/entities/{i}/schema", ent["schema"]
        if isinstance(out.get("data_schema"), str):
            yield "/output/data_schema", out["data_schema"]
        for i, case in enumerate(manifest.get("tests") or []):
            if not isinstance(case, Mapping):
                continue
            for key in ("material", "file", "entities", "data"):
                value = (case.get("input") or {}).get(key)
                if isinstance(value, str):
                    yield f"/tests/{i}/input/{key}", value
            if isinstance(case.get("expected"), str):
                yield f"/tests/{i}/expected", case["expected"]

    # ------------------------------------------------------------------ checks
    def manifest_issues(self, manifest: Any, prefix: str = "/manifest") -> list[Issue]:
        if not isinstance(manifest, Mapping):
            return [Issue(prefix, "manifest must be a JSON object")]
        return self.schemas.issues("package-manifest.schema.json", manifest, prefix)

    def package_issues(
        self, manifest: Mapping[str, Any], files: Mapping[str, bytes], prefix: str
    ) -> list[Issue]:
        """Checks beyond the JSON Schema. ``manifest`` is already schema-valid."""
        issues: list[Issue] = []
        kind = str(manifest["kind"])
        entry = manifest.get("entry") or {}
        if not self._entry_matches(kind, entry):
            issues.append(
                Issue(f"{prefix}/entry", f"entry does not match kind {kind!r}", "entry_kind_mismatch")
            )
        for pointer, path in self.referenced_paths(manifest):
            if path not in files:
                issues.append(Issue(prefix + pointer, f"file {path!r} is not in the package", "missing_file"))
        if entry.get("runtime") == "python":
            module = str(entry.get("module", ""))
            base = "src/" + module.replace(".", "/")
            if f"{base}.py" not in files and f"{base}/__init__.py" not in files:
                issues.append(
                    Issue(
                        f"{prefix}/entry/module",
                        f"module {module!r} not found (expected {base}.py or {base}/__init__.py)",
                        "missing_file",
                    )
                )
        issues.extend(self._schema_files(manifest, files, prefix))
        issues.extend(self._rules(manifest, files, prefix))
        issues.extend(self._tests(manifest, files, prefix))
        return issues

    def _schema_files(
        self, manifest: Mapping[str, Any], files: Mapping[str, bytes], prefix: str
    ) -> list[Issue]:
        issues: list[Issue] = []
        schema_pointers = {
            "/params_schema",
            "/input/data_schema",
            "/output/data_schema",
            "/entry/output_schema",
        }
        out = manifest.get("output") or {}
        entities = list(out.get("entities") or [])
        for pointer, path in self.referenced_paths(manifest):
            is_entity = pointer.startswith("/output/entities/")
            if (pointer not in schema_pointers and not is_entity) or path not in files:
                continue
            try:
                schema = self._load_json(files, path)
                Draft202012Validator.check_schema(schema)
            except (ValueError, UnicodeDecodeError) as exc:
                issues.append(Issue(prefix + pointer, f"{path}: invalid JSON: {exc}", "invalid_schema"))
                continue
            except SchemaError as exc:
                issues.append(
                    Issue(prefix + pointer, f"{path}: not a JSON Schema: {exc.message}", "invalid_schema")
                )
                continue
            if is_entity:
                index = int(pointer.split("/")[3])
                required = set(schema.get("required") or []) if isinstance(schema, Mapping) else set()
                missing = [f for f in entities[index].get("key_fields", []) if f not in required]
                if missing:
                    issues.append(
                        Issue(
                            f"{prefix}/output/entities/{index}/key_fields",
                            f"key fields {missing} must be required in {path}",
                            "key_field_not_required",
                        )
                    )
        return issues

    def _rules(self, manifest: Mapping[str, Any], files: Mapping[str, bytes], prefix: str) -> list[Issue]:
        if manifest.get("kind") != "collector-rules":
            return []
        path = (manifest.get("entry") or {}).get("rules")
        if not isinstance(path, str) or path not in files:
            return []
        try:
            rules = self._load_json(files, path)
        except (ValueError, UnicodeDecodeError) as exc:
            return [Issue(f"{prefix}/entry/rules", f"{path}: invalid JSON: {exc}", "invalid_rules")]
        return self.schemas.issues("collector-rules.schema.json", rules, "/files/" + _escape(path))

    def _tests(self, manifest: Mapping[str, Any], files: Mapping[str, bytes], prefix: str) -> list[Issue]:
        issues: list[Issue] = []
        tests = list(manifest.get("tests") or [])
        names = [t.get("name") for t in tests]
        for i, name in enumerate(names):
            if names.index(name) != i:
                issues.append(
                    Issue(f"{prefix}/tests/{i}/name", f"duplicate test name {name!r}", "duplicate_test")
                )
        for i, case in enumerate(tests):
            expected = case.get("expected")
            if isinstance(expected, str) and expected in files:
                try:
                    self._load_json(files, expected)
                except (ValueError, UnicodeDecodeError) as exc:
                    issues.append(Issue(f"{prefix}/tests/{i}/expected", f"{expected}: invalid JSON: {exc}"))
        if self.require_tests and manifest.get("kind") in {"extractor", "llm"}:
            statuses = {t.get("expected_status") for t in tests}
            if "success" not in statuses or not statuses & {"empty", "unrecognized"}:
                issues.append(
                    Issue(
                        f"{prefix}/tests",
                        "extractor and llm packages need at least one 'success' test and one "
                        "'empty' or 'unrecognized' test",
                        "tests_required",
                    )
                )
        return issues


def manifest_prefix(from_zip: bool) -> str:
    return "/files/" + _escape(MANIFEST_NAME) if from_zip else "/manifest"
