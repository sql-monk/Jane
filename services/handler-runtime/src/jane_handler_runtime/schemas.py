"""JSON Schema validation against the WP-00 contracts (``contracts/schemas``) and package schemas."""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from functools import cached_property
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from jane_kit.contracts import contracts_dir

__all__ = ["ContractSchemas", "SchemaError", "find_contracts_dir", "validate_instance"]

BASE = "https://jane.local/contracts/schemas/"


class SchemaError(RuntimeError):
    """Contracts are not available (misconfigured deployment)."""


def find_contracts_dir(configured: Path | None) -> Path:
    if configured is not None:
        found: Path | None = configured
    else:
        found = contracts_dir(Path(__file__).parent)
    if found is None or not (found / "schemas").is_dir():
        raise SchemaError(
            "contracts/schemas not found; set JANE_HANDLER_RUNTIME_CONTRACTS_DIR (or JANE_CONTRACTS_DIR)"
        )
    return found


def _errors(validator: Draft202012Validator, instance: Any) -> Iterator[ValidationError]:
    return iter(sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)))


def _pointer(error: ValidationError) -> str:
    return "".join(f"/{str(p).replace('~', '~0').replace('/', '~1')}" for p in error.absolute_path)


def validate_instance(schema: Mapping[str, Any], instance: Any, prefix: str = "") -> list[dict[str, str]]:
    """Validate against a standalone (package) schema; returns ``validation_errors`` items."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        {
            "pointer": prefix + _pointer(e),
            "message": e.message[:1000],
            "schema_pointer": "/" + "/".join(str(p) for p in e.absolute_schema_path),
        }
        for e in _errors(validator, instance)
    ]


class ContractSchemas:
    """All ``contracts/schemas/**.schema.json`` in one registry, addressable by relative path."""

    def __init__(self, root: Path) -> None:
        self.root = root / "schemas"

    @cached_property
    def registry(self) -> Registry[Any]:
        resources = []
        for path in sorted(self.root.rglob("*.schema.json")):
            rel = path.relative_to(self.root).as_posix()
            doc = json.loads(path.read_text(encoding="utf-8"))
            resources.append((BASE + rel, Resource.from_contents(doc, default_specification=DRAFT202012)))
        return Registry().with_resources(resources)

    def validator(self, ref: str) -> Draft202012Validator:
        """``ref`` like ``handler-result.schema.json`` or ``handler-result.schema.json#/$defs/TestReport``."""
        return Draft202012Validator(
            {"$ref": BASE + ref}, registry=self.registry, format_checker=FormatChecker()
        )

    def errors(self, ref: str, instance: Any) -> list[dict[str, str]]:
        return [
            {"pointer": _pointer(e), "message": e.message[:1000]}
            for e in _errors(self.validator(ref), instance)
        ]

    def check(self, ref: str, instance: Any) -> None:
        errors = self.errors(ref, instance)
        if errors:
            raise ValueError(f"{ref}: {errors[:5]}")
