"""JSON Schema validation against the WP-00 contracts (``contracts/schemas``) and package schemas.

The contract validators are jane-kit's shared :class:`jane_kit.schemas.ContractSchemas` (R17; ``format`` is
checked, as before); this module keeps the runtime's error shape (``validation_errors`` items) and the
validation of standalone package schemas.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from jane_kit.schemas import ContractSchemas as _KitSchemas
from jane_kit.schemas import ContractsNotFound, json_pointer

__all__ = ["ContractSchemas", "SchemaError", "find_contracts_dir", "validate_instance"]

SETTING = "JANE_HANDLER_RUNTIME_CONTRACTS_DIR"


class SchemaError(ContractsNotFound):
    """Contracts are not available (misconfigured deployment)."""


def find_contracts_dir(configured: Path | None) -> Path:
    try:
        return _KitSchemas.locate(configured, setting=SETTING, start=Path(__file__).parent, fallbacks=()).root
    except ContractsNotFound as exc:
        raise SchemaError(str(exc)) from None


def _errors(validator: Draft202012Validator, instance: Any) -> Iterator[ValidationError]:
    return iter(
        sorted(
            validator.iter_errors(instance), key=lambda e: [(isinstance(p, str), p) for p in e.absolute_path]
        )
    )


def validate_instance(schema: Mapping[str, Any], instance: Any, prefix: str = "") -> list[dict[str, str]]:
    """Validate against a standalone (package) schema; returns ``validation_errors`` items."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        {
            "pointer": json_pointer(e.absolute_path, prefix),
            "message": e.message[:1000],
            "schema_pointer": "/" + "/".join(str(p) for p in e.absolute_schema_path),
        }
        for e in _errors(validator, instance)
    ]


class ContractSchemas(_KitSchemas):
    """All ``contracts/schemas/**.schema.json``, addressable by relative path (``handler-result.schema.json`` or
    ``handler-result.schema.json#/$defs/TestReport``)."""

    def __init__(self, root: Path) -> None:
        super().__init__(root, format_check=True)

    def errors(self, ref: str, instance: Any) -> list[dict[str, str]]:
        return [
            {"pointer": json_pointer(e.absolute_path), "message": e.message[:1000]}
            for e in self.iter_errors(ref, instance)
        ]

    def check(self, ref: str, instance: Any) -> None:
        errors = self.errors(ref, instance)
        if errors:
            raise ValueError(f"{ref}: {errors[:5]}")
