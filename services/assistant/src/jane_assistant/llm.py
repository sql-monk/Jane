"""LLM calls of one assistant job: trusted instructions, untrusted data, budget and size limits.

* Instructions are constants of :mod:`jane_assistant.prompts`; material content, package code and
  diagnostics go only into ``data`` parts (``llm.v1`` ``DataPart``: "never instructions").
* Output is always structured (``output_schema``); an invalid output is rejected, not repaired.
* The job stops by itself when its spend reaches ``limits.llm.budget.amount``; the gateway's
  ``budget_exhausted`` (429) stops it as well. Data is cut to ``max_input_tokens_per_request``
  (about 4 characters per token) and the model's output to ``max_output_tokens_per_request``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from jsonschema import Draft202012Validator

from jane_kit.errors import JaneError

from .clients import LlmClient, RemoteError, idem_key
from .settings import LlmLimits

__all__ = ["BudgetExhausted", "InvalidModelOutput", "LlmSession", "part"]

CHARS_PER_TOKEN = 4
"""Conservative size estimate used to keep data under ``max_input_tokens_per_request``."""


class BudgetExhausted(JaneError):
    code = "budget_exhausted"


class InvalidModelOutput(JaneError):
    code = "schema_mismatch"


def part(name: str, text: str, media_type: str = "text/plain") -> dict[str, Any]:
    return {"name": name, "media_type": media_type, "text": text}


@dataclass
class LlmSession:
    client: LlmClient
    limits: LlmLimits
    purpose: str
    job_key: str
    source_id: str | None = None
    task_id: str | None = None
    spent: float = 0.0
    calls: int = 0
    currency: str = field(init=False)
    model_used: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.currency = self.limits.budget.currency

    @property
    def remaining(self) -> float:
        return max(0.0, self.limits.budget.amount - self.spent)

    def cost(self) -> dict[str, Any]:
        return {"amount": round(self.spent, 6), "currency": self.currency}

    def _fit(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        budget_chars = self.limits.max_input_tokens_per_request * CHARS_PER_TOKEN
        out = []
        for p in data:
            text = str(p.get("text", ""))
            if budget_chars <= 0:
                break
            if len(text) > budget_chars:
                text = text[:budget_chars] + "\n[... truncated to fit max_input_tokens_per_request]"
            budget_chars -= len(text)
            out.append({**p, "text": text})
        return out

    async def ask(
        self,
        step: str,
        instructions: str,
        data: list[dict[str, Any]],
        output_schema: dict[str, Any],
        *,
        model: str,
    ) -> dict[str, Any]:
        """One structured completion. Raises :class:`BudgetExhausted` or :class:`InvalidModelOutput`."""
        if self.spent >= self.limits.budget.amount:
            raise BudgetExhausted(
                f"assistant budget {self.limits.budget.amount} {self.currency} spent",
                details={"spent": self.cost(), "step": step},
            )
        scope: dict[str, Any] = {"purpose": self.purpose}
        if self.source_id:
            scope["source_id"] = self.source_id
        if self.task_id:
            scope["task_id"] = self.task_id
        request = {
            "model": model,
            "instructions": instructions,
            "data": self._fit(data),
            "output_schema": output_schema,
            "max_output_tokens": self.limits.max_output_tokens_per_request,
            "temperature": 0,
            "scope": scope,
            "limits": {
                "budget": {
                    "amount": round(self.remaining, 6),
                    "currency": self.currency,
                    "period": self.limits.budget.period,
                },
                "max_input_tokens_per_request": self.limits.max_input_tokens_per_request,
                "max_output_tokens_per_request": self.limits.max_output_tokens_per_request,
                "max_requests_per_minute": self.limits.max_requests_per_minute,
            },
        }
        self.calls += 1
        key = idem_key(self.job_key, step, str(self.calls))
        try:
            result = await self.client.complete(request, key)
        except RemoteError as exc:
            code = exc.problem.code if exc.problem else ""
            if code == "budget_exhausted":
                raise BudgetExhausted(
                    "LLM gateway budget exhausted", details=exc.problem.details if exc.problem else None
                ) from exc
            raise JaneError(f"LLM request failed: {exc}", code="upstream_unavailable") from exc
        cost = ((result.get("usage") or {}).get("cost") or {}).get("amount") or 0
        self.spent += float(cost)
        self.model_used = dict(result.get("model") or {})
        if not result.get("valid", False) or not isinstance(result.get("output"), dict):
            raise InvalidModelOutput(
                f"model output for {step} does not match its schema",
                details={"validation_errors": result.get("validation_errors") or []},
            )
        output: dict[str, Any] = result["output"]
        errors = list(Draft202012Validator(output_schema).iter_errors(output))
        if errors:  # the gateway validated too; never trust a neighbour blindly with model output
            raise InvalidModelOutput(
                f"model output for {step} failed local validation: {errors[0].message}",
                details={"pointer": "/" + "/".join(map(str, errors[0].absolute_path))},
            )
        return output


def as_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=1)
