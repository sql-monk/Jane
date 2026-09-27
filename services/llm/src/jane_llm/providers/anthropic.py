"""Anthropic Messages API adapter (official ``anthropic`` SDK).

Connection (``kind: llm_provider``): ``params.api_base`` (optional, default the public API),
``secret_refs.api_key`` (required). The key is resolved by this service and never leaves it.
Structured output uses ``output_config.format`` (JSON Schema) when the model is marked
``supports_structured_output``; the gateway validates the reply against the schema in any case.
Timeouts and retries come from ``limits.provider`` (contract ``timeouts.*``, ``retries``).
"""

from __future__ import annotations

from typing import Any

import anthropic

from jane_llm.providers.base import ProviderError, ProviderRequest, ProviderResponse, ResolvedConnection
from jane_llm.settings import ServiceLimits

_FINISH = {"end_turn": "stop", "stop_sequence": "stop", "max_tokens": "length", "refusal": "content_filter"}


class AnthropicProvider:
    kind = "anthropic"

    async def complete(
        self, request: ProviderRequest, connection: ResolvedConnection | None, limits: ServiceLimits
    ) -> ProviderResponse:
        if connection is None or not connection.secrets.get("api_key"):
            raise ProviderError(
                "anthropic provider needs a connection with secret_refs.api_key", retryable=False
            )
        pl = limits.provider
        client = anthropic.AsyncAnthropic(
            api_key=connection.secrets["api_key"],
            base_url=connection.params.get("api_base") or None,
            timeout=anthropic.Timeout(pl.request_timeout_ms / 1000, connect=pl.connect_timeout_ms / 1000),
            max_retries=max(pl.retries.max_attempts - 1, 0),
        )
        kwargs: dict[str, Any] = {
            "model": request.model_id,
            "max_tokens": request.max_output_tokens,
            "system": request.system,
            "messages": [{"role": "user", "content": request.user}],
        }
        if request.output_schema is not None and request.structured_output:
            kwargs["output_config"] = {"format": {"type": "json_schema", "schema": request.output_schema}}
        try:
            async with client:
                message = await client.messages.create(**kwargs)
        except (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError) as exc:
            raise ProviderError(f"anthropic unavailable: {type(exc).__name__}", retryable=True) from exc
        except anthropic.APIStatusError as exc:
            raise ProviderError(
                f"anthropic rejected the request: HTTP {exc.status_code}", retryable=exc.status_code >= 500
            ) from exc
        text = "".join(block.text for block in message.content if block.type == "text")
        return ProviderResponse(
            text=text,
            input_tokens=int(message.usage.input_tokens),
            output_tokens=int(message.usage.output_tokens),
            finish_reason=_FINISH.get(str(message.stop_reason), str(message.stop_reason)),
        )
