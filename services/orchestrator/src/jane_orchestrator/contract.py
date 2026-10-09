"""Request validation against ``contracts/openapi/orchestrator.v1.yaml`` (the source of truth).

The orchestrator does not re-declare contract documents (Source, TaskConfig, Connection, PlatformLimits…)
as its own models: request bodies are validated with the JSON Schemas of the contract, and violations
become ``422 validation_failed`` with JSON-pointer ``errors``. The validators are jane-kit's shared
:class:`jane_kit.schemas.ContractSchemas` (R17); pointers follow RFC 6901.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jane_kit.errors import FieldError
from jane_kit.schemas import ContractSchemas as KitSchemas
from jane_kit.schemas import ContractsNotFound

__all__ = ["ContractSchemas"]

MAX_ERRORS = 20  # reported per request (diagnostics size, not an operational limit)


class ContractSchemas(KitSchemas):
    def __init__(self, directory: Path | None = None) -> None:
        try:
            located = KitSchemas.locate(
                directory,
                setting="JANE_ORCHESTRATOR_CONTRACTS_DIR",
                marker="openapi/orchestrator.v1.yaml",
                start=Path(__file__).parent,
                fallbacks=(),
            )
        except ContractsNotFound as exc:
            raise RuntimeError(str(exc)) from None
        super().__init__(located.root, openapi="orchestrator.v1.yaml")

    def schema_uri(self, relative: str) -> str:
        """URI of a schema relative to ``contracts/schemas`` (``source.schema.json``, ``x.json#/$defs/Y``)."""
        return self.uri(relative)

    def check(self, uri: str, instance: Any, prefix: str = "") -> list[FieldError]:
        return self.field_errors(uri, instance, prefix, limit=MAX_ERRORS, message_max=500)

    def validate(
        self,
        ref: str,
        instance: Any,
        prefix: str = "",
        *,
        detail: str = "request body does not match the contract",
        **options: Any,
    ) -> None:
        super().validate(
            ref, instance, prefix, detail=detail, **{"limit": MAX_ERRORS, "message_max": 500, **options}
        )

    def validate_request(self, method: str, path: str, body: Any, media: str = "application/json") -> None:
        self.validate(self.request_schema_uri(method, path, media), body)
