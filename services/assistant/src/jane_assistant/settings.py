"""Settings and limits of the assistant. Every limit has a safe default documented in README.md.

Limits follow ``contracts/schemas/common/limits.schema.json`` where the limit exists there
(``llm.*``, ``transfer.*``, ``timeouts.*``, ``retries``). Assistant-specific knobs (confidence
threshold, batch size, sample text size, match thresholds...) live in the ``onboarding`` and
``improvement`` groups; they are internal because the contract schema is strict.

Resolution order: model defaults <- platform file (``JANE_ASSISTANT_LIMITS_FILE``) <-
``JANE_ASSISTANT_LIMITS__*`` <- request ``limits`` (``OnboardingRequest.limits`` etc., contract
``limits.llm``), with platform ``hard_caps`` applied last (``min``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from jane_kit.clients import ClientLimits
from jane_kit.config import (
    JaneSettings,
    LimitLayer,
    Limits,
    ResolvedLimits,
    contract_field,
    resolve_limits,
)
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits

ENV_PREFIX = "JANE_ASSISTANT_"


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "assistant"

    # Neighbour services (contracts/openapi/<api>.v1.yaml). Empty -> the feature that needs the
    # neighbour fails with ``upstream_unavailable`` instead of guessing.
    llm_url: str | None = None
    registry_url: str | None = None
    collector_web_url: str | None = None
    collector_telegram_url: str | None = None
    handler_runtime_url: str | None = None
    orchestrator_url: str | None = None
    storage_url: str | None = None
    service_token_env: str | None = None
    """Name of the environment variable that holds the bearer token for neighbour services
    (a secret reference, never the value itself; ADR-0005/0006)."""

    # Source search provider (plan.md WP-11: "налаштований пошуковий провайдер").
    search_provider: Literal["none", "static", "http_json"] = "none"
    search_static_file: Path | None = None
    """``static``: JSON file ``[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?}]``."""
    search_url_template: str | None = None
    """``http_json``: URL with ``{query}``, e.g. an internal search gateway."""
    search_items_path: str = "results"
    search_title_field: str = "title"
    search_url_field: str = "url"
    search_description_field: str = "description"

    contracts_dir: Path | None = None
    """Where ``contracts/schemas`` live (local validation of generated rules and manifests).
    Empty -> found upwards from the package (dev checkout) or ``/app/contracts`` (Docker)."""

    default_storage_package: str | None = None
    """``package_id@version`` of a storage package added to task drafts (optional)."""
    default_storage_connection: str | None = None
    """``connection_id`` for that storage stage."""
    llm_model_cheap: str = "cheap"
    """Model alias of the LLM gateway for classification (sampling, unknown materials)."""
    llm_model_strong: str = "strong"
    """Model alias for analysis, proposals and code generation."""
    generated_code_allowed_modules: list[str] = Field(
        default_factory=lambda: [
            "re",
            "html",
            "json",
            "math",
            "datetime",
            "decimal",
            "string",
            "unicodedata",
            "itertools",
            "functools",
            "collections",
            "typing",
            "dataclasses",
        ]
    )
    """Policy (not a limit): modules generated extractor code may import. The runtime sandbox
    (WP-06) is the real barrier; this list rejects obviously unsuitable code early."""
    onboarding_allow_activation: bool = True
    """Allow ``acceptProposal`` with ``activate: true`` to create the source and task in the
    orchestrator (only when every extractor passed its tests)."""


class Budget(Limits):
    """Contract ``limits.llm.budget`` (``Budget``)."""

    amount: float = Field(default=2.0, ge=0)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    period: Literal["run", "day", "week", "month", "total"] = "run"


class LlmLimits(Limits):
    """Contract ``limits.llm``. The gateway enforces its own budgets too; the assistant also stops
    by itself when the spend of one job reaches ``budget.amount``."""

    max_requests_per_minute: int = Field(default=30, ge=1)
    max_input_tokens_per_request: int = Field(default=16_000, ge=1)
    """Data sent to the model is truncated to about 4 characters per token of this limit."""
    max_output_tokens_per_request: int = Field(default=4_000, ge=1)
    budget: Budget = Budget()
    max_improvement_attempts: int = Field(default=3, ge=0)
    max_onboarding_samples: int = Field(default=60, ge=1)


class OnboardingLimits(Limits):
    min_confidence: float = Field(default=0.8, gt=0, le=1)
    """Sampling stops once the sample-coverage confidence reaches this value."""
    sample_batch_size: int = Field(default=10, ge=1)
    """Materials classified per LLM request during adaptive sampling."""
    max_sample_chars: int = Field(default=6_000, ge=200)
    """Text of one material passed to the model (the rest is cut)."""
    min_examples_per_type: int = Field(default=2, ge=1)
    """A material type counts as distinguished after this many examples."""
    max_examples_per_type: int = Field(default=3, ge=1)
    """Examples of one type sent to analysis and code generation."""
    max_candidates: int = Field(default=5, ge=1)
    """Search results kept for disambiguation."""
    auto_select_confidence: float = Field(default=0.8, gt=0, le=1)
    auto_select_margin: float = Field(default=0.2, ge=0, le=1)
    max_candidate_packages: int = Field(default=5, ge=1)
    """Existing extractors tested per entity type."""
    bind_threshold: float = Field(default=0.9, ge=0, le=1)
    """Share of samples an existing extractor must pass to be bound as is."""
    fork_threshold: float = Field(default=0.5, ge=0, le=1)
    """Share of samples above which an existing extractor is forked and adapted."""
    max_generation_attempts: int = Field(default=2, ge=1)
    """LLM attempts to produce a new extractor that passes its tests."""
    max_proposals: int = Field(default=4, ge=1)
    fetch_ratio: int = Field(default=3, ge=1)
    """The sampling collection may fetch up to ``max_onboarding_samples x fetch_ratio`` materials
    (``limits.crawl.max_pages_per_run`` / ``telegram.max_messages_per_run`` of that collection); only
    the most diverse ones are classified."""
    collection_poll_wait_ms: int = Field(default=1_000, ge=0)
    """Long-poll of ``listCollectionMaterials`` while sampling."""
    max_empty_polls: int = Field(default=30, ge=1)
    """Consecutive empty polls of a running collection before sampling gives up."""
    requests_overhead_ratio: float = Field(default=0.05, ge=0)
    """Added to estimated materials for the ``requests_per_run_estimate`` of a proposal."""


class ImprovementLimits(Limits):
    max_sample_chars: int = Field(default=6_000, ge=200)
    max_problem_samples: int = Field(default=10, ge=1)
    max_successful_examples: int = Field(default=5, ge=0)
    max_file_chars: int = Field(default=20_000, ge=200)
    """Package source file passed to the model (longer files are cut)."""


class UnknownLimits(Limits):
    max_sample_chars: int = Field(default=6_000, ge=200)
    min_confidence: float = Field(default=0.6, ge=0, le=1)
    """Below this, the suggestion for an unknown material is ``none``."""


class TransferLimits(Limits):
    inline_max_bytes: int = contract_field("transfer.inline_max_bytes", 262_144, ge=0)
    """Package archives up to this size are sent to the runtime inline (base64)."""


class ServiceLimits(Limits):
    llm: LlmLimits = contract_field("llm", LlmLimits())
    transfer: TransferLimits = TransferLimits()
    onboarding: OnboardingLimits = OnboardingLimits()
    improvement: ImprovementLimits = ImprovementLimits()
    unknown: UnknownLimits = UnknownLimits()
    clients: ClientLimits = ClientLimits()
    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_ASSISTANT_LIMITS__*`` <- ``extra``."""
    return resolve_limits(ServiceLimits, *settings.platform_layers(f"{ENV_PREFIX}LIMITS__"), *extra)


def request_layer(llm_limits: dict[str, Any] | None) -> list[LimitLayer]:
    """Contract ``limits.llm`` from a request as a ``request`` layer (empty list if absent)."""
    return [LimitLayer("request", {"llm": llm_limits})] if llm_limits else []
