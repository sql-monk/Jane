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
import json
import logging
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
_log = logging.getLogger(__name__)

# Structured outputs accept a subset of JSON Schema ("JSON Schema limitations" of the Messages API): every
# object needs ``additionalProperties: false``; numeric, string-length and array-size constraints are not
# supported. Such keywords are dropped from the grammar only - the gateway validates the reply against the
# full schema. Keywords outside both sets make the schema inexpressible (sent as instructions instead).
_DROPPED = frozenset(
    {
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minProperties",
        "maxProperties",
        "$schema",
        "$id",
    }
)
_KEPT = frozenset(
    {"type", "properties", "required", "items", "enum", "const", "anyOf", "allOf", "$ref", "$defs"}
)
_KEPT |= {"title", "description", "default", "examples", "format", "additionalProperties"}
_FORMATS = frozenset(
    {"date-time", "time", "date", "duration", "email", "hostname", "uri", "ipv4", "ipv6", "uuid"}
)


class _Inexpressible(Exception):
    pass


def api_schema(schema: dict[str, Any]) -> dict[str, Any] | None:
    """``schema`` in the subset ``output_config.format`` accepts, or ``None`` when it cannot be expressed
    there (a free-form object - no ``properties`` or ``additionalProperties`` other than ``false`` - or an
    unsupported keyword such as ``oneOf`` or ``patternProperties``)."""
    try:
        out = _grammar(schema)
    except _Inexpressible:
        return None
    return out if isinstance(out, dict) else None


def _grammar(node: Any) -> Any:
    if isinstance(node, list):
        return [_grammar(x) for x in node]
    if not isinstance(node, dict):
        return node
    out: dict[str, Any] = {}
    for key, value in node.items():
        if key in _DROPPED or (key == "format" and value not in _FORMATS):
            continue
        if key not in _KEPT:
            raise _Inexpressible(key)
        if key in ("properties", "$defs"):
            out[key] = {name: _grammar(sub) for name, sub in value.items()}
        elif key in ("items", "anyOf", "allOf"):
            out[key] = _grammar(value)
        else:
            out[key] = value
    kind = node.get("type")
    if kind == "object" or (isinstance(kind, list) and "object" in kind):
        if "properties" not in node or node.get("additionalProperties", False) is not False:
            raise _Inexpressible("free-form object")
        out["additionalProperties"] = False
    return out


def _error_summary(resp: httpx.Response) -> str:
    """``<type>: <message>`` of an API error body (no request content), cut to 500 characters."""
    try:
        err = resp.json().get("error") or {}
        return f"{err.get('type', '')}: {err.get('message', '')}"[:500]
    except (ValueError, AttributeError):
        return ""


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
        system = request.system
        grammar = None
        if request.output_schema is not None:
            grammar = api_schema(request.output_schema) if request.structured_output else None
            if grammar is None:
                # Not expressible as output_config.format (or the model has no structured output): the model
                # gets the schema as trusted instructions; the gateway validates the reply and retries.
                system += (
                    f"\n\n# Output JSON Schema\n{json.dumps(request.output_schema, ensure_ascii=False)}\n"
                )
        body: dict[str, Any] = {
            "model": request.model_id,
            "max_tokens": request.max_output_tokens,
            "system": system,
            "messages": [{"role": "user", "content": request.user}],
        }
        if grammar is not None:
            body["output_config"] = {"format": {"type": "json_schema", "schema": grammar}}
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
                if not retryable:
                    _log.warning(
                        "anthropic rejected the request",
                        extra={"status": resp.status_code, "error": _error_summary(resp)},
                    )
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
