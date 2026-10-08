"""Deterministic fake provider ``fake`` for tests (this and other WPs).

It deliberately behaves like a **gullible, obedient model**, so that injection tests are meaningful:

1. It reads the system channel like a model would and learns the data-block nonce announced there
   (``<<<JANE-DATA <nonce> ...>>>``). Text between that exact opening and closing delimiter is *data*;
   everything else it receives (system text and the rest of the user text) is *instructions*.
   Without an announced nonce **everything is instructions** (a naive prompt).
2. **It obeys injections in the instruction channel**: a phrase like
   ``ignore previous instructions ... {"json": "object"}`` makes it reply with that JSON object
   (or, without JSON, with ``INJECTION-OBEYED: <rest of the line>``) regardless of the task.
3. Otherwise it answers deterministically: the first matching script from the connection params
   (``responses``: ``when_data_contains`` / ``when_data_matches`` → ``output`` / ``output_text`` /
   ``error``), else a minimal value that satisfies the output schema, else ``fake:<sha256 prefix>``.

So an injection placed inside data is harmless **only if** the gateway really keeps data inside
unforgeable delimiters; the same text in the instruction channel, or any delimiter forgery that
works, changes the answer. Token counts are ``ceil(chars / 4)``.

4. It can hold its answer, so that tests get a deterministic "call still in flight" window (R-04): the
   ``delay_ms`` of the first matching script that has one (a script with ``delay_ms`` and no answer only sets
   the delay; matching goes on to the next scripts for the answer), else the connection's ``params.delay_ms``.
   The delay is bounded by ``limits.fake.max_delay_ms`` (``0`` turns delays off) and logged
   (:data:`HOLD_LOG_MESSAGE` with ``connection_id`` and ``delay_ms``) before it starts.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import re
from typing import TYPE_CHECKING, Any

from jane_llm.providers.base import ProviderError, ProviderRequest, ProviderResponse, ResolvedConnection

if TYPE_CHECKING:
    from jane_llm.settings import ServiceLimits

FAKE_PROVIDER_ID = "fake"
FAKE_MODEL_ID = "fake-deterministic-1"
HOLD_LOG_MESSAGE = "fake provider holds its answer"
"""Log message emitted (INFO, with ``connection_id`` and ``delay_ms``) when a call starts its delay."""
_ANSWER_KEYS = ("output_text", "output")

log = logging.getLogger(__name__)

_NONCE_RE = re.compile(r"<<<JANE-DATA ([0-9a-f]{32})")
_DIRECTIVE_RE = re.compile(
    r"ignore\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above|earlier)\s+instructions\b", re.IGNORECASE
)


def split_channels(system: str, user: str) -> tuple[str, list[str]]:
    """Return ``(instruction_text, data_texts)`` as the fake model understands the prompt."""
    m = _NONCE_RE.search(system)
    if m is None:
        return f"{system}\n{user}", []
    nonce = re.escape(m.group(1))
    block = re.compile(rf"<<<JANE-DATA {nonce}[^\n]*>>>\n(.*?)\n<<<JANE-END {nonce}>>>", re.DOTALL)
    data = block.findall(user)
    return f"{system}\n{block.sub('', user)}", data


def find_directive(instruction_text: str) -> str | None:
    """The reply an obedient model would give to an injection in its instruction channel."""
    m = _DIRECTIVE_RE.search(instruction_text)
    if m is None:
        return None
    rest = instruction_text[m.end() :]
    brace = rest.find("{")
    if brace != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(rest[brace:])
            return json.dumps(obj, ensure_ascii=False)
        except ValueError:
            pass
    line = rest.strip().splitlines()[0] if rest.strip() else ""
    return f"INJECTION-OBEYED: {line}".strip()


def minimal_instance(schema: Any, depth: int = 0) -> Any:
    """Deterministic minimal JSON value valid for common JSON Schema constructs."""
    if not isinstance(schema, dict) or depth > 20:
        return None
    if "const" in schema:
        return schema["const"]
    if schema.get("enum"):
        return schema["enum"][0]
    for key in ("oneOf", "anyOf", "allOf"):
        if schema.get(key):
            return minimal_instance(schema[key][0], depth + 1)
    typ = schema.get("type")
    if isinstance(typ, list):
        typ = next((t for t in typ if t != "null"), typ[0] if typ else None)
    if typ == "object" or (typ is None and "properties" in schema):
        props = schema.get("properties") or {}
        return {name: minimal_instance(props.get(name, {}), depth + 1) for name in schema.get("required", [])}
    if typ == "array":
        n = int(schema.get("minItems", 0))
        return [minimal_instance(schema.get("items", {}), depth + 1) for _ in range(n)]
    if typ == "string":
        return "x" * int(schema.get("minLength", 0))
    if typ in {"number", "integer"}:
        low = float(schema.get("minimum", schema.get("exclusiveMinimum", 0)) or 0)
        value = low + (1 if "exclusiveMinimum" in schema else 0)
        return int(value) if typ == "integer" else float(value)
    if typ == "boolean":
        return False
    if typ == "null":
        return None
    return {}


def _tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


class FakeProvider:
    kind = "fake"

    async def complete(
        self, request: ProviderRequest, connection: ResolvedConnection | None, limits: ServiceLimits
    ) -> ProviderResponse:
        instruction_text, data = split_channels(request.system, request.user)
        data_text = "\n".join(data) if data else request.user
        script, delay_ms = self._match(data_text, connection)
        if delay_ms is None:
            params = connection.params if connection else {}
            delay_ms = _delay_ms(params.get("delay_ms", 0), "params.delay_ms")
        held = min(delay_ms, limits.fake.max_delay_ms)
        if held > 0:
            log.info(
                HOLD_LOG_MESSAGE,
                extra={
                    "connection_id": connection.connection_id if connection else None,
                    "delay_ms": held,
                    "requested_delay_ms": delay_ms,
                },
            )
            await self._hold(held / 1000)
        text = find_directive(instruction_text)
        if text is None and script is not None:
            text = self._answer(script)
        if text is None:
            if request.output_schema is not None:
                text = json.dumps(minimal_instance(request.output_schema), ensure_ascii=False)
            else:
                text = "fake:" + hashlib.sha256(data_text.encode()).hexdigest()[:16]
        finish = "stop"
        max_chars = request.max_output_tokens * 4
        if len(text) > max_chars:
            text, finish = text[:max_chars], "length"
        return ProviderResponse(
            text=text,
            input_tokens=_tokens(request.system + request.user),
            output_tokens=_tokens(text),
            finish_reason=finish,
        )

    async def _hold(self, seconds: float) -> None:
        """Wait before answering (the delay of a script or connection)."""
        await asyncio.sleep(seconds)

    @staticmethod
    def _match(
        data_text: str, connection: ResolvedConnection | None
    ) -> tuple[dict[str, Any] | None, int | None]:
        """The first matching script with an answer, and the ``delay_ms`` of the first matching script that
        has one up to it (``None``: no script sets a delay)."""
        scripts = (connection.params.get("responses") if connection else None) or []
        delay_ms: int | None = None
        for i, script in enumerate(scripts):
            if not isinstance(script, dict):
                continue
            contains = script.get("when_data_contains")
            pattern = script.get("when_data_matches")
            if contains is not None and str(contains) not in data_text:
                continue
            if pattern is not None and not re.search(str(pattern), data_text):
                continue
            if delay_ms is None and "delay_ms" in script:
                delay_ms = _delay_ms(script["delay_ms"], f"params.responses[{i}].delay_ms")
            if script.get("error") or any(k in script for k in _ANSWER_KEYS):
                return script, delay_ms
        return None, delay_ms

    @staticmethod
    def _answer(script: dict[str, Any]) -> str:
        if err := script.get("error"):
            raise ProviderError(f"scripted fake error: {err}", retryable=err == "unavailable")
        if "output_text" in script:
            return str(script["output_text"])
        return json.dumps(script["output"], ensure_ascii=False)


def _delay_ms(value: Any, where: str) -> int:
    """A delay from the connection params: a non-negative integer of milliseconds, else the call fails."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProviderError(
            f"fake provider: {where} must be a non-negative integer (ms), got {value!r}", retryable=False
        )
    return value
