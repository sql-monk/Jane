"""Settings and limits of the LLM service. Every limit has a safe default documented in README.md."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from jane_kit.clients import ClientLimits, RetryPolicy
from jane_kit.config import JaneSettings, LimitLayer, Limits, ResolvedLimits, contract_field, resolve_limits
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits
from jane_llm.connections import ConnectionPolicy

ENV_PREFIX = "JANE_LLM_"


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "llm"
    port: int = 8110

    store: Literal["postgres", "memory"] = "postgres"
    """Where budgets, usage, providers, connections, idempotency keys and jobs live.
    ``postgres`` (default) is shared between instances; ``memory`` is for tests and single-process demos."""
    database_url: str | None = None
    """PostgreSQL DSN (``postgresql://user:pass@host:5432/db``); required for ``store=postgres``.
    Give the password through the environment (for example ``PGPASSWORD``), not in files."""
    db_schema: str = Field(default="llm", pattern=r"^[a-z_][a-z0-9_]{0,62}$")
    """Own schema of the service in the database (the service never reads other services' tables)."""

    seed_file: Path | None = None
    """YAML/JSON with providers, model aliases, connections and budgets applied at startup
    (only entries that do not exist yet are created). See ``config/seed.example.yaml``."""
    fake_provider_enabled: bool = True
    """Register the deterministic ``fake`` provider and the ``default`` alias pointing to it."""
    packages_dir: Path | None = None
    """Directory with unpacked LLM packages (``<dir>/<package_id>/jane-package.json``) usable without a
    registry. The built-in ``services/llm/packages`` is used when unset and present."""
    registry_url: str | None = None
    """Base URL of the handler registry (``registry.v1``) for packages referenced by ``handler``."""
    registry_token: str | None = None
    """Bearer token for the registry (give it through the environment)."""
    db_pool_min_size: int = Field(default=1, ge=0)
    """Minimum PostgreSQL connections per instance."""
    db_pool_max_size: int = Field(default=10, ge=1)
    """Maximum PostgreSQL connections per instance (size it with ``jobs.max_concurrent_jobs`` and traffic)."""
    secret_env_prefix: str = "JANE_SECRET_"  # noqa: S105 - a variable-name prefix, not a secret
    """``env:`` secret references may only name variables with this prefix."""
    secret_files_dir: Path | None = Path("/run/secrets")
    """``file:`` secret references may only point inside this directory (unset: ``file:`` disabled)."""
    provider_api_base_allowlist: list[str] = Field(default_factory=lambda: ["https://api.anthropic.com"])
    """Origins a connection's ``params.api_base`` may point to (JSON list in the environment)."""

    def connection_policy(self) -> ConnectionPolicy:
        return ConnectionPolicy(
            env_prefix=self.secret_env_prefix,
            files_dir=self.secret_files_dir,
            api_base_allowlist=tuple(self.provider_api_base_allowlist),
        )


class LlmBudget(Limits):
    """Contract ``limits.llm.budget`` (``Budget``): the platform budget when no stored definition exists."""

    amount: float = Field(default=10.0, ge=0)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    period: Literal["run", "day", "week", "month", "total"] = "day"


class LlmLimits(Limits):
    max_requests_per_minute: int = contract_field("llm.max_requests_per_minute", 60, ge=1)
    """Platform-wide provider calls per minute (all instances together)."""
    max_input_tokens_per_request: int = contract_field("llm.max_input_tokens_per_request", 100_000, ge=1)
    max_output_tokens_per_request: int = contract_field("llm.max_output_tokens_per_request", 4_096, ge=1)
    budget: LlmBudget = contract_field("llm.budget", LlmBudget())


class GatewayLimits(Limits):
    """Service-specific knobs (not in ``limits.schema.json``)."""

    default_max_output_tokens: int = Field(default=1_024, ge=1)
    """Used when neither the request nor the package gives ``max_output_tokens``."""
    max_schema_retries: int = Field(default=1, ge=0)
    """Default and upper bound of ``max_schema_retries`` (extra calls on output invalid for the schema)."""
    chars_per_token_estimate: float = Field(default=2.0, gt=0)
    """Conservative input-token estimate (characters per token) used to reserve budget before a call."""
    reservation_ttl_seconds: int = Field(default=900, ge=1)
    """A reservation older than this (instance crashed mid-call) is charged at its estimate."""
    max_data_part_bytes: int = Field(default=2_000_000, ge=1)
    """Largest single data part (material content) accepted from inline or blob content."""
    content_fetch_timeout_ms: int = Field(default=30_000, ge=1)
    """Timeout of downloading blob content (``download_url``) of materials and package archives."""
    max_package_bytes: int = Field(default=20_000_000, ge=1)
    """Largest package archive (compressed, and total uncompressed size) from a request or the registry."""
    max_package_files: int = Field(default=1_000, ge=1)
    """Most files in a package archive."""


class RegistryLimits(Limits):
    """Calls to the handler registry (internal; the contract fields are used by ``provider``)."""

    connect_timeout_ms: int = Field(default=5_000, ge=1)
    request_timeout_ms: int = Field(default=30_000, ge=1)
    max_attempts: int = Field(default=3, ge=1)

    def client_limits(self) -> ClientLimits:
        return ClientLimits(
            connect_timeout_ms=self.connect_timeout_ms,
            request_timeout_ms=self.request_timeout_ms,
            retries=RetryPolicy(max_attempts=self.max_attempts),
        )


class FakeProviderLimits(Limits):
    """The deterministic test provider ``fake`` (internal, not in ``limits.schema.json``)."""

    max_delay_ms: int = Field(default=30_000, ge=0)
    """Upper bound of the delay a ``fake`` connection asks for (``params.delay_ms``,
    ``params.responses[].delay_ms``); a longer delay is shortened to it, ``0`` turns delays off."""


class ServiceLimits(Limits):
    llm: LlmLimits = LlmLimits()
    gateway: GatewayLimits = GatewayLimits()
    fake: FakeProviderLimits = FakeProviderLimits()
    provider: ClientLimits = ClientLimits(
        request_timeout_ms=120_000, retries=RetryPolicy(max_attempts=2, initial_backoff_ms=500)
    )
    """Timeouts and retries of calls to LLM providers (contract ``timeouts.*``, ``retries``)."""
    registry: RegistryLimits = RegistryLimits()
    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- platform file (``JANE_LLM_LIMITS_FILE``) <- ``JANE_LLM_LIMITS__*`` <- ``extra``
    (request layer in autonomous mode).

    The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
    this service does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail. Its
    ``timeouts.*`` and ``retries`` reach ``provider`` (declared as those contract fields)."""
    return resolve_limits(ServiceLimits, *settings.platform_layers(f"{ENV_PREFIX}LIMITS__"), *extra)
