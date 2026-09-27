"""Provider adapter interface. Adapters receive fully rendered prompts and resolved connections."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from jane_llm.settings import ServiceLimits


@dataclass(frozen=True)
class ResolvedConnection:
    """A managed connection with secret values resolved in this service's environment (never logged)."""

    connection_id: str
    kind: str
    params: dict[str, Any] = field(default_factory=dict)
    secrets: dict[str, str] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class ProviderRequest:
    model_id: str
    system: str
    user: str
    max_output_tokens: int
    output_schema: dict[str, Any] | None = None
    temperature: float | None = None
    structured_output: bool = False
    """The model supports native structured output (``supports_structured_output``)."""


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    input_tokens: int
    output_tokens: int
    finish_reason: str = "stop"


class ProviderError(Exception):
    """The provider call did not produce a response."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


class ProviderAdapter(Protocol):
    kind: str

    async def complete(
        self, request: ProviderRequest, connection: ResolvedConnection | None, limits: ServiceLimits
    ) -> ProviderResponse: ...
