"""Settings and limits of the registry. Every limit has a safe default documented in README.md."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from jane_kit.config import JaneSettings, LimitLayer, Limits, ResolvedLimits, contract_field, resolve_limits
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits
from jane_kit.pagination import PageLimits

ENV_PREFIX = "JANE_REGISTRY_"


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "registry"
    port: int = 8105

    # ---------------------------------------------------------------- metadata (ADR-0002 §1)
    db: Literal["postgres", "memory"] = "postgres"
    """``postgres`` - own PostgreSQL database (``jane_registry``); ``memory`` - one process, no persistence
    (local experiments and fast tests only)."""
    db_url: SecretStr | None = None
    """PostgreSQL DSN of the registry's own database, e.g. ``postgresql://jane_registry:...@host/jane_registry``.
    Passed through the environment (``JANE_REGISTRY_DB_URL``) or a secrets file, never committed."""
    db_schema: str = Field(default="public", pattern=r"^[a-z_][a-z0-9_]{0,62}$")

    # ---------------------------------------------------------------- archives (ADR-0002 §2)
    blob: Literal["s3", "filesystem"] = "s3"
    blob_bucket: str = "jane-registry"
    blob_prefix: str = "sha256/"
    """Object key = ``<prefix><sha256 hex>`` (content-addressed)."""
    blob_root: Path | None = None
    """``filesystem``: directory that plays the role of the bucket (``<root>/<bucket>/<prefix><hex>``)."""
    s3_endpoint_url: str | None = None
    """MinIO / S3-compatible endpoint (``http://127.0.0.1:9000``); empty for AWS S3."""
    s3_region: str = "us-east-1"
    s3_access_key: SecretStr | None = None
    s3_secret_key: SecretStr | None = None
    s3_create_bucket: bool = True
    """Create the bucket on start if it does not exist (dev stack)."""

    # ---------------------------------------------------------------- validation
    contracts_dir: Path | None = None
    """Directory with ``schemas/package-manifest.schema.json`` etc.; default - ``contracts/`` of the
    checkout (env ``JANE_CONTRACTS_DIR``) or ``/app/contracts`` in the image."""
    runtime_profiles: list[str] = Field(default_factory=list)
    """Sources of runtime profile descriptions (``dependencies.runtime_profile``) published by
    handler-runtime (WP-06): file paths or http(s) URLs. A source may be one profile document, a list of
    them, ``{"runtime_profiles": {...}}`` or a ``ServiceInfo`` (``GET <runtime>/v1/info``). JSON list in env:
    ``JANE_REGISTRY_RUNTIME_PROFILES='["/etc/jane/python-extractor-1.json"]'``."""
    require_tests: bool = True
    """extractor/llm packages need at least one ``success`` and one ``empty|unrecognized`` test
    (contracts/docs/handler-packages.md)."""

    # ---------------------------------------------------------------- auth (ADR-0005)
    # auth_mode, api_keys, api_keys_file, jwt_* come from jane_kit.auth.AuthSettings (JaneSettings).
    runtime_profiles_token_ref: str | None = None
    """Secret reference (``env:VAR`` / ``file:/path``, ADR-0006) of the registry's own token for http(s)
    ``runtime_profiles`` sources: ``GET <runtime>/v1/info`` needs a valid token of the runtime."""


class PackageLimits(Limits):
    max_archive_bytes: int = Field(default=20 * 1024 * 1024, ge=1024)
    """Largest accepted package archive (uploaded zip or canonical archive of a JSON publish)."""
    max_unpacked_bytes: int = Field(default=50 * 1024 * 1024, ge=1024)
    """Sum of file sizes in one package."""
    max_files: int = Field(default=2000, ge=1)
    """Files in one package."""
    max_versions_per_package: int = Field(default=1000, ge=1)
    """Published versions of one package; beyond -> 422 ``limit_exceeded``."""
    archive_cache_bytes: int = Field(default=64 * 1024 * 1024, ge=0)
    """In-process LRU of archives read from the blob store (per instance)."""


class SecretScanLimits(Limits):
    max_scan_bytes_per_file: int = Field(default=2 * 1024 * 1024, ge=1024)
    """Largest file the secret scanner reads; a package with a larger file is rejected with
    422 ``limit_exceeded`` (it is never accepted unscanned)."""
    min_entropy_token_length: int = Field(default=32, ge=8)
    """Shortest quoted/assigned token checked for high entropy."""
    scan_time_budget_ms: int = Field(default=20_000, ge=1)
    """Wall time of scanning one package; beyond it the publish fails with 422 ``limit_exceeded``
    (a safeguard - the patterns themselves are linear)."""
    max_findings_per_file: int = Field(default=20, ge=1)
    """Findings reported per file (one is enough to reject; the cap keeps responses and scans small)."""
    entropy_threshold: float = Field(default=4.3, gt=0)
    """Shannon entropy (bits per character) above which a mixed-alphabet token counts as a secret."""


class DiffLimits(Limits):
    max_context_lines: int = Field(default=50, ge=0)
    """Upper bound for the ``context_lines`` query parameter (larger values are clamped)."""
    max_diff_file_bytes: int = Field(default=1024 * 1024, ge=1024)
    """Files larger than this get ``status`` only, without ``unified_diff``."""
    max_merge_file_bytes: int = Field(default=1024 * 1024, ge=1024)
    """Text files larger than this are not merged line by line in an upstream port (conflict if both sides
    changed them)."""


class RequestLimits(Limits):
    max_request_body_bytes: int = contract_field("transfer.max_request_body_bytes", 30 * 1024 * 1024, ge=1024)
    """Contract ``limits.transfer.max_request_body_bytes``: larger bodies -> 413 ``payload_too_large``."""


class ProfileLimits(Limits):
    fetch_timeout_ms: int = Field(default=5000, ge=1)
    """Timeout of reading a runtime profile from a URL."""
    refresh_seconds: int = Field(default=300, ge=1)
    """How long loaded profiles are reused before the sources are read again."""


class DbLimits(Limits):
    pool_min_size: int = Field(default=1, ge=0)
    pool_max_size: int = Field(default=10, ge=1)
    connect_timeout_ms: int = Field(default=5000, ge=1)
    statement_timeout_ms: int = Field(default=30_000, ge=1)


class BlobLimits(Limits):
    connect_timeout_ms: int = Field(default=5000, ge=1)
    read_timeout_ms: int = Field(default=60_000, ge=1)
    max_attempts: int = Field(default=3, ge=1)
    """Attempts of one S3 request (botocore standard retry mode)."""


class RecoveryLimits(Limits):
    """Recovery after an instance crash (several instances share PostgreSQL)."""

    in_progress_lease_ms: int = Field(default=120_000, ge=1000)
    """An ``Idempotency-Key`` claimed by a request that has not finished is released after this lease, so a
    retry on another instance is not blocked by a crashed one."""
    job_lease_ms: int = Field(default=60_000, ge=1000)
    """A running job belongs to its instance while the instance renews this lease; an expired lease makes
    the job ``failed`` with a retryable error."""
    job_heartbeat_ms: int = Field(default=15_000, ge=100)
    """How often an instance renews the leases of its running jobs (must be below ``job_lease_ms``)."""


class ServiceLimits(Limits):
    """Limits of the registry. Contract names (``limits.schema.json``) where the limit exists there."""

    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()
    pages: PageLimits = PageLimits()
    packages: PackageLimits = PackageLimits()
    secrets: SecretScanLimits = SecretScanLimits()
    diff: DiffLimits = DiffLimits()
    requests: RequestLimits = RequestLimits()
    profiles: ProfileLimits = ProfileLimits()
    db: DbLimits = DbLimits()
    blob: BlobLimits = BlobLimits()
    recovery: RecoveryLimits = RecoveryLimits()


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- platform file (``JANE_REGISTRY_LIMITS_FILE``) <- ``JANE_REGISTRY_LIMITS__*`` <- ``extra``.

    The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
    the registry does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail."""
    return resolve_limits(ServiceLimits, *settings.platform_layers(f"{ENV_PREFIX}LIMITS__"), *extra)
