"""Pydantic models of ``contracts/openapi/llm.v1.yaml`` and the shared ``Connection`` schema.

Configuration documents are strict (``extra='forbid'``) like the contract; results are built as dicts.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SLUG = r"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"
CURRENCY = r"^[A-Z]{3}$"
ScopeType = Literal["platform", "source", "task"]
Period = Literal["run", "day", "week", "month", "total"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Pricing(Strict):
    input_per_mtok: float = Field(ge=0)
    output_per_mtok: float = Field(ge=0)
    currency: str = Field(pattern=CURRENCY)


class ModelInfo(Strict):
    model_id: str
    max_context_tokens: int | None = Field(default=None, ge=1)
    supports_structured_output: bool | None = None
    pricing: Pricing | None = None


class Budget(Strict):
    amount: float = Field(ge=0)
    currency: str = Field(pattern=CURRENCY)
    period: Period


class LlmLimitsIn(Strict):
    """Contract ``limits.llm`` as sent in requests and provider definitions."""

    max_requests_per_minute: int | None = Field(default=None, ge=1)
    max_input_tokens_per_request: int | None = Field(default=None, ge=1)
    max_output_tokens_per_request: int | None = Field(default=None, ge=1)
    budget: Budget | None = None
    max_improvement_attempts: int | None = Field(default=None, ge=0)
    max_onboarding_samples: int | None = Field(default=None, ge=1)
    min_onboarding_confidence: float | None = Field(default=None, gt=0, le=1)
    """The assistant's limit; accepted (the contract allows it in any ``limits.llm``), not used by the gateway."""


class Provider(Strict):
    provider_id: str = Field(pattern=SLUG)
    kind: str
    connection_id: str | None = Field(default=None, pattern=SLUG)
    enabled: bool
    models: list[ModelInfo]
    limits: LlmLimitsIn | None = None

    def model(self, model_id: str) -> ModelInfo | None:
        return next((m for m in self.models if m.model_id == model_id), None)


class ModelAlias(Strict):
    alias: str
    provider_id: str
    model_id: str


class DataPart(Strict):
    name: str
    media_type: str | None = None
    text: str | None = None
    content: dict[str, Any] | None = None


class CompletionScope(Strict):
    source_id: str | None = None
    task_id: str | None = None
    run_id: str | None = None
    purpose: Literal["handler", "onboarding", "improvement", "unknown_material", "other"]


class CompletionRequest(Strict):
    model: str | None = None
    instructions: str
    data: list[DataPart] = Field(default_factory=list)
    output_schema: dict[str, Any] | None = None
    max_output_tokens: int | None = Field(default=None, ge=1)
    temperature: float | None = Field(default=None, ge=0, le=2)
    max_schema_retries: int | None = Field(default=None, ge=0)
    scope: CompletionScope
    limits: LlmLimitsIn | None = None
    test_mode: bool | None = None
    mode: Literal["sync", "async"] = "sync"


class BudgetDefinition(Strict):
    scope_type: ScopeType
    scope_id: str
    budget: Budget | None = None
    max_requests_per_minute: int | None = Field(default=None, ge=1)
    status: dict[str, Any] | None = None  # read-only; ignored on input


# Pattern of secret *references* (not a secret).
SECRET_REF_PATTERN = r"^(env:[A-Z_][A-Z0-9_]{0,127}|file:.{1,512}|vault:[^#]{1,512}#[A-Za-z0-9_.-]{1,128})$"  # noqa: S105
NAME_PATTERN = r"^[a-z][a-z0-9_]{0,63}$"


class Connection(Strict):
    connection_id: str = Field(pattern=SLUG)
    kind: str = Field(pattern=r"^[a-z][a-z0-9_]{1,31}$")
    title: str | None = Field(default=None, max_length=200)
    params: dict[str, Any] | None = None
    secret_refs: dict[str, str] | None = None
    labels: dict[str, str] | None = None

    @field_validator("secret_refs")
    @classmethod
    def _refs(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        for name, ref in (value or {}).items():
            if not re.match(NAME_PATTERN, name):
                raise ValueError(f"secret name {name!r} must match {NAME_PATTERN}")
            if not re.match(SECRET_REF_PATTERN, ref):
                raise ValueError(f"secret_refs.{name} must be env:VAR, file:<path> or vault:<path>#<key>")
        return value
