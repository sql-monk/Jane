"""Settings and limits of the service. Every limit has a safe default documented in README.md."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from jane_kit.clients import RetryPolicy
from jane_kit.config import JaneSettings, LimitLayer, Limits, ResolvedLimits, contract_field, resolve_limits
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits
from jane_kit.pagination import PageLimits

from .policy import ConnectionPolicy

ENV_PREFIX = "JANE_STORAGE_"


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "storage"
    port: int = 8107
    connections_file: Path | None = None
    """JSON/YAML with ``{"connections": [Connection, ...]}`` (secret values only as ``secret_refs``)."""
    transit_connection_id: str | None = None
    """Connection (kind ``s3``/``minio``) used to read ``s3://`` blobs of materials (ADR-0004)."""
    package_dirs: list[Path] = Field(default_factory=list)
    """Extra storage package directories besides the installed adapter distributions."""
    validate_requests: bool = True
    """Validate invocations against ``contracts/schemas`` when the contracts directory is available."""
    secret_env_prefix: str = "JANE_SECRET_"  # noqa: S105 - a variable-name prefix, not a secret
    """``env:`` secret references may name only variables with this prefix (empty: ``env:`` disabled)."""
    secret_files_dir: Path | None = Path("/run/secrets")
    """``file:`` secret references must point inside this directory (empty: ``file:`` disabled)."""
    connection_host_allowlist: list[str] = Field(default_factory=list)
    """``hostname`` / ``hostname:port`` a connection may contact (JSON list); default none: connections with
    a network address are rejected."""
    content_files_dir: Path | None = None
    """Only ``file:///`` ContentRef blobs below this directory may be read; None disables local blobs."""
    download_host_allowlist: list[str] = Field(default_factory=list)
    """``hostname`` or ``hostname:port`` allowed for ContentRef download_url; empty disables downloads."""

    @field_validator("secret_files_dir", "content_files_dir", mode="before")
    @classmethod
    def _empty_files_dir_disables(cls, value: object) -> object:
        return None if isinstance(value, str) and not value.strip() else value

    @field_validator("connection_host_allowlist", "download_host_allowlist")
    @classmethod
    def _valid_allowlist(cls, value: list[str]) -> list[str]:
        ConnectionPolicy(host_allowlist=tuple(value))  # raises on an entry that is not hostname[:port]
        return value

    def connection_policy(self) -> ConnectionPolicy:
        return ConnectionPolicy(
            env_prefix=self.secret_env_prefix,
            files_dir=self.secret_files_dir,
            host_allowlist=tuple(self.connection_host_allowlist),
        )


class Timeouts(Limits):
    sync_response_max_ms: int = contract_field("timeouts.sync_response_max_ms", 30_000, ge=1)
    """Contract ``limits.timeouts.sync_response_max_ms``: a sync invocation not done by then → 202 + Job."""
    request_timeout_ms: int = contract_field("timeouts.request_timeout_ms", 30_000, ge=1)
    """Reading blob content (``download_url``, ``s3://``)."""


class Transfer(Limits):
    max_request_body_bytes: int = contract_field("transfer.max_request_body_bytes", 16 * 1024 * 1024, ge=1)
    """Contract ``limits.transfer.max_request_body_bytes``: larger bodies → 413 (send blobs instead)."""
    inline_max_bytes: int = contract_field("transfer.inline_max_bytes", 1024 * 1024, ge=0)
    """Contract ``limits.transfer.inline_max_bytes``: stored content up to this size is returned inline
    in ``GET /v1/objects/{id}`` when the adapter has no persistent URI for it."""


class Objects(Limits):
    max_object_bytes: int = Field(default=100 * 1024 * 1024, ge=1)
    """Largest RAW / result document the service stores (content read into memory)."""


class Adapters(Limits):
    """Options passed to every adapter's ``open`` (each adapter uses the ones it knows)."""

    lock_timeout_ms: int = Field(default=30_000, ge=1)
    lock_stale_ms: int = Field(default=120_000, ge=1)
    lock_poll_ms: int = Field(default=10, ge=1)
    replace_retry_ms: int = Field(default=5_000, ge=0)
    pool_min_size: int = Field(default=1, ge=0)
    pool_max_size: int = Field(default=10, ge=1)
    connect_timeout_ms: int = Field(default=10_000, ge=1)
    command_timeout_ms: int = Field(default=30_000, ge=1)


class Invocations(Limits):
    max_results_in_memory: int = Field(default=10_000, ge=1)
    """How many recent HandlerResults ``GET /v1/invocations/{id}`` keeps (per instance)."""


class ServiceLimits(Limits):
    """Limits of this service. Contract names (``limits.schema.json``) where the limit exists there."""

    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()
    retries: RetryPolicy = contract_field("retries", RetryPolicy())
    """Contract ``limits.retries``: retries of the core on ``CONFLICT`` (concurrent writers)."""
    timeouts: Timeouts = Timeouts()
    transfer: Transfer = Transfer()
    objects: Objects = Objects()
    adapters: Adapters = Adapters()
    pages: PageLimits = PageLimits()
    invocations: Invocations = Invocations()


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_STORAGE_LIMITS__*`` <- ``extra``
    (request layer from ``HandlerInvocation.limits``)."""
    return resolve_limits(ServiceLimits, *settings.platform_layers(f"{ENV_PREFIX}LIMITS__"), *extra)
