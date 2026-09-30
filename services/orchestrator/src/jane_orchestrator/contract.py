"""Request validation against ``contracts/openapi/orchestrator.v1.yaml`` (the source of truth).

The orchestrator does not re-declare contract documents (Source, TaskConfig, Connection, PlatformLimits…)
as its own models: request bodies are validated with the JSON Schemas of the contract, and violations
become ``422 validation_failed`` with JSON-pointer ``errors``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from jane_kit.contracts import OpenAPISpec, contracts_dir
from jane_kit.errors import FieldError, ValidationFailed

__all__ = ["ContractSchemas"]

MAX_ERRORS = 20  # reported per request (diagnostics size, not an operational limit)


class ContractSchemas:
    def __init__(self, directory: Path | None = None) -> None:
        root = directory or contracts_dir(Path(__file__).parent)
        if root is None or not (root / "openapi" / "orchestrator.v1.yaml").is_file():
            raise RuntimeError(
                "contracts/openapi/orchestrator.v1.yaml not found: set JANE_CONTRACTS_DIR or "
                "JANE_ORCHESTRATOR_CONTRACTS_DIR"
            )
        self.root = root
        self.spec = OpenAPISpec.load(root / "openapi" / "orchestrator.v1.yaml")
        self._validators: dict[str, Draft202012Validator] = {}

    def _validator(self, uri: str) -> Draft202012Validator:
        if uri not in self._validators:
            self._validators[uri] = Draft202012Validator({"$ref": uri}, registry=self.spec.registry)
        return self._validators[uri]

    def request_schema_uri(self, method: str, path: str, media: str = "application/json") -> str:
        op = self.spec.operation(method, path)
        rb = self.spec.follow(op.loc.child("requestBody"))
        return rb.child("content", media, "schema").ref

    def schema_uri(self, relative: str) -> str:
        """URI of a schema relative to ``contracts/schemas`` (``source.schema.json``, ``x.json#/$defs/Y``)."""
        path, _, fragment = relative.partition("#")
        return (self.root / "schemas" / path).resolve().as_uri() + "#" + fragment

    def check(self, uri: str, instance: Any, prefix: str = "") -> list[FieldError]:
        errors = sorted(self._validator(uri).iter_errors(instance), key=lambda e: list(e.absolute_path))
        out = []
        for e in errors[:MAX_ERRORS]:
            pointer = prefix + "".join(f"/{p}" for p in e.absolute_path)
            out.append(FieldError(pointer=pointer or "/", code="schema", message=e.message[:500]))
        return out

    def validate(self, uri: str, instance: Any, prefix: str = "") -> None:
        errors = self.check(uri, instance, prefix)
        if errors:
            raise ValidationFailed("request body does not match the contract", errors=errors)

    def validate_request(self, method: str, path: str, body: Any, media: str = "application/json") -> None:
        self.validate(self.request_schema_uri(method, path, media), body)
