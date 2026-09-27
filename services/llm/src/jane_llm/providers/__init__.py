"""LLM provider adapters by ``Provider.kind``."""

from __future__ import annotations

from jane_llm.providers.anthropic import AnthropicProvider
from jane_llm.providers.base import (
    ProviderAdapter,
    ProviderError,
    ProviderRequest,
    ProviderResponse,
    ResolvedConnection,
)
from jane_llm.providers.fake import FakeProvider

__all__ = [
    "ADAPTERS",
    "AnthropicProvider",
    "FakeProvider",
    "ProviderAdapter",
    "ProviderError",
    "ProviderRequest",
    "ProviderResponse",
    "ResolvedConnection",
]

ADAPTERS: dict[str, ProviderAdapter] = {"fake": FakeProvider(), "anthropic": AnthropicProvider()}
