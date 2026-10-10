"""LLM calls of one assistant job: trusted instructions, untrusted data, budget and size limits.

* Instructions are constants of :mod:`jane_assistant.prompts`; material content, package code and
  diagnostics go only into ``data`` parts (``llm.v1`` ``DataPart``: "never instructions").
* Output is always structured (``output_schema``); an invalid output is rejected, not repaired.
* Budget (``limits.schema.json`` ``Budget``, the same rule as the gateway): every call carries the whole
  ``limits.llm.budget`` and ``scope.run_id`` = the assistant run (onboarding session, improvement or
  unknown-material job), so the gateway counts a ``period: run`` budget across all calls of the run, on any
  instance; other periods narrow the counter of the request's most specific scope. The session stops by
  itself once ``spent >= amount`` (``amount: 0`` = no call at all, as in the gateway); the gateway's
  ``budget_exhausted`` (429, or a failed async job) stops it as well.
* The call waits as long as the model needs: ``mode=sync`` with the client's own timeout
  (``limits.llm_call.request_timeout_ms``) or ``mode=async`` (202 + job, polled within
  ``clients.job_wait_timeout_ms``). Data is cut to ``max_input_tokens_per_request`` counted like the gateway
  counts it (``llm_call.chars_per_token`` characters per token, the instructions and the gateway's preamble and
  delimiters included) and the model's output to ``max_output_tokens_per_request``. :meth:`LlmSession.room`
  tells a step how many characters each of its materials may take, so materials are shown in full or as
  digests rather than dropped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from jsonschema import Draft202012Validator

from jane_kit.errors import JaneError

from .clients import LlmClient, RemoteError, idem_key
from .settings import LlmCallLimits, LlmLimits

__all__ = ["BudgetExhausted", "InvalidModelOutput", "LlmSession", "part"]

CUT_MARK = "\n[... truncated to fit max_input_tokens_per_request]"
NAME_ALLOWANCE = 40
"""Characters :meth:`LlmSession.room` assumes for the name and media type of a part it has not seen yet."""


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
    run_id: str | None = None
    """``scope.run_id`` of every call: the window of a ``period: run`` budget (default: ``job_key``)."""
    mode: str = "sync"
    """``CompletionRequest.mode``: ``sync`` or ``async`` (202 + job, awaited by the client)."""
    call: LlmCallLimits = field(default_factory=LlmCallLimits)
    """How request size is counted (``llm_call.chars_per_token``, ``*_overhead_chars``)."""
    spent: float = 0.0
    calls: int = 0
    currency: str = field(init=False)
    model_used: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.currency = self.limits.budget.currency
        if self.run_id is None:
            self.run_id = self.job_key

    @property
    def exhausted(self) -> bool:
        """The run's spend reached the budget: no further call (``amount: 0`` - none at all)."""
        return self.spent >= self.limits.budget.amount

    def cost(self) -> dict[str, Any]:
        return {"amount": round(self.spent, 6), "currency": self.currency}

    def _part_overhead(self, p: dict[str, Any]) -> int:
        return self.call.part_overhead_chars + len(str(p.get("name", ""))) + len(str(p.get("media_type", "")))

    def data_budget(self, instructions: str) -> int:
        """Characters of data parts (their delimiters included) one request may carry."""
        total = int(self.limits.max_input_tokens_per_request * self.call.chars_per_token)
        return total - len(instructions) - self.call.prompt_overhead_chars

    def room(self, instructions: str, fixed: list[dict[str, Any]], count: int, cap: int) -> int:
        """Characters each of ``count`` further data parts may take next to the ``fixed`` ones (at most ``cap``)."""
        left = self.data_budget(instructions) - sum(
            len(str(p.get("text", ""))) + self._part_overhead(p) for p in fixed
        )
        each = left // max(1, count) - self.call.part_overhead_chars - NAME_ALLOWANCE
        return max(0, min(cap, each))

    def _fit(self, instructions: str, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        budget = self.data_budget(instructions)
        out = []
        for p in data:
            text = str(p.get("text", ""))
            budget -= self._part_overhead(p)
            if budget <= 0:
                break
            if len(text) > budget:
                text = text[: max(0, budget - len(CUT_MARK))] + CUT_MARK
            budget -= len(text)
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
        if self.exhausted:
            raise BudgetExhausted(
                f"assistant budget {self.limits.budget.amount} {self.currency} "
                f"per {self.limits.budget.period} spent",
                details={"spent": self.cost(), "step": step, "run_id": self.run_id},
            )
        scope: dict[str, Any] = {"purpose": self.purpose, "run_id": self.run_id}
        if self.source_id:
            scope["source_id"] = self.source_id
        if self.task_id:
            scope["task_id"] = self.task_id
        request: dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "data": self._fit(instructions, data),
            "output_schema": output_schema,
            "max_output_tokens": self.limits.max_output_tokens_per_request,
            "temperature": 0,
            "scope": scope,
            "limits": {
                # The whole budget: the gateway counts the run (scope.run_id) itself, atomically for all instances.
                "budget": self.limits.budget.model_dump(),
                "max_input_tokens_per_request": self.limits.max_input_tokens_per_request,
                "max_output_tokens_per_request": self.limits.max_output_tokens_per_request,
                "max_requests_per_minute": self.limits.max_requests_per_minute,
            },
        }
        if self.mode != "sync":
            request["mode"] = self.mode
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
