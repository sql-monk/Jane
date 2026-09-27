"""Anthropic Messages API adapter (``POST {api_base}/v1/messages`` over httpx).

The official ``anthropic`` SDK is not used on purpose: its 1.x line depends on ``httpx2``, and installing
that into the shared uv workspace switches Starlette's ``TestClient`` of every service to ``httpx2``
(breaking jane-kit's typed contract helpers). The wire format follows the Messages API docs.

Connection (``kind: llm_provider``): ``params.api_base`` (optional, default the public API),
``params.anthropic_version`` (optional), ``secret_refs.api_key`` (required). The key is resolved by this
service and never leaves it. Structured output uses ``output_config.format`` (JSON Schema) when the model
is marked ``supports_structured_output``; the gateway validates the reply against the schema in any case.
Timeouts and retries (429, 5xx, connection errors) come from ``limits.provider``.
"""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, Any

import httpx

from jane_llm.providers.base import ProviderError, ProviderRequest, ProviderResponse, ResolvedConnection

if TYPE_CHECKING:
    from jane_llm.settings import ServiceLimits

DEFAULT_API_BASE = "https://api.anthropic.com"
DEFAULT_VERSION = "2023-06-01"
_FINISH = {"end_turn": "stop", "stop_sequence": "stop", "max_tokens": "length", "refusal": "content_filter"}
_RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


class AnthropicProvider:
    kind = "anthropic"

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.transport = transport

    async def complete(
        self, request: ProviderRequest, connection: ResolvedConnection | None, limits: ServiceLimits
    ) -> ProviderResponse:
        if connection is None or not connection.secrets.get("api_key"):
            raise ProviderError(
                "anthropic provider needs a connection with secret_refs.api_key", retryable=False
            )
        pl = limits.provider
        base = str(connection.params.get("api_base") or DEFAULT_API_BASE).rstrip("/")
        headers = {
            "x-api-key": connection.secrets["api_key"],
            "anthropic-version": str(connection.params.get("anthropic_version") or DEFAULT_VERSION),
            "content-type": "application/json",
        }
        body: dict[str, Any] = {
            "model": request.model_id,
            "max_tokens": request.max_output_tokens,
            "system": request.system,
            "messages": [{"role": "user", "content": request.user}],
        }
        if request.output_schema is not None and request.structured_output:
            body["output_config"] = {"format": {"type": "json_schema", "schema": request.output_schema}}
        timeout = httpx.Timeout(pl.request_timeout_ms / 1000, connect=pl.connect_timeout_ms / 1000)
        policy = pl.retries
        async with httpx.AsyncClient(timeout=timeout, transport=self.transport) as client:
            for attempt in range(1, policy.max_attempts + 1):
                try:
                    resp = await client.post(f"{base}/v1/messages", json=body, headers=headers)
                except httpx.TransportError as exc:
                    if attempt >= policy.max_attempts:
                        raise ProviderError(
                            f"anthropic unavailable: {type(exc).__name__}", retryable=True
                        ) from exc
                    await asyncio.sleep(self._delay(attempt, None, limits))
                    continue
                if resp.status_code < 400:
                    return self._parse(resp.json())
                retryable = resp.status_code in _RETRY_STATUS
                if not retryable or attempt >= policy.max_attempts:
                    raise ProviderError(f"anthropic returned HTTP {resp.status_code}", retryable=retryable)
                await asyncio.sleep(self._delay(attempt, resp, limits))
        raise ProviderError("anthropic: no attempts made", retryable=True)  # pragma: no cover

    @staticmethod
    def _delay(attempt: int, resp: httpx.Response | None, limits: ServiceLimits) -> float:
        p = limits.provider.retries
        cap = p.max_backoff_ms / 1000
        if resp is not None and (ra := resp.headers.get("retry-after")):
            try:
                return min(float(ra), cap)
            except ValueError:
                pass
        base = p.initial_backoff_ms / 1000 * p.backoff_multiplier ** (attempt - 1)
        if p.jitter:
            base += random.uniform(0, base / 2)  # noqa: S311 - jitter, not crypto
        return float(min(base, cap))

    @staticmethod
    def _parse(message: dict[str, Any]) -> ProviderResponse:
        text = "".join(b.get("text", "") for b in message.get("content") or [] if b.get("type") == "text")
        usage = message.get("usage") or {}
        stop = str(message.get("stop_reason"))
        return ProviderResponse(
            text=text,
            input_tokens=int(usage.get("input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
            finish_reason=_FINISH.get(stop, stop),
        )
