"""Settings and limits of the service. Every limit has a safe default documented in README.md."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from jane_kit.config import (
    JaneSettings,
    LimitLayer,
    Limits,
    ResolvedLimits,
    contract_field,
    resolve_limits,
)
from jane_kit.content import parse_host_allowlist
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.jobs import JobLimits

ENV_PREFIX = "JANE_HANDLER_RUNTIME_"
DEFAULT_PROFILE = "python-extractor@1"


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "handler-runtime"

    sandbox_backend: Literal["docker", "subprocess"] = "docker"
    """``docker`` (default, ADR-0003) or ``subprocess`` - no isolation, trusted local packages only."""
    allow_unsafe_subprocess: bool = False
    """The ``subprocess`` backend refuses to run unless this is true (never in production)."""
    docker_host: str | None = None
    """Docker/Podman API endpoint; default: ``DOCKER_HOST`` or the platform socket / named pipe."""
    docker_runtime: str | None = None
    """OCI runtime of sandbox containers, e.g. ``runsc`` (gVisor)."""
    sandbox_user: str = "65534:65534"
    """Non-root uid:gid inside the sandbox."""
    sandbox_labels: dict[str, str] = Field(default_factory=dict)
    """Extra labels on sandbox containers (e.g. to find and clean them up in a test stack)."""
    profile_images: dict[str, str] = Field(
        default_factory=lambda: {DEFAULT_PROFILE: "jane/python-extractor:1"}
    )
    """Runtime profile -> sandbox image (pin by digest in production: ``repo@sha256:...``)."""

    registry_url: str | None = None
    """Base URL of the handler repository (registry.v1); packages without ``package_archive`` come from it."""
    registry_token: SecretStr | None = None
    """Bearer token for the registry (from the environment, never logged)."""
    package_cache_dir: Path | None = None
    """Where verified packages are cached by digest; default: a temporary directory."""
    blob_roots: list[Path] = Field(default_factory=list)
    """Directories from which ``file://`` blobs (package archives, material content) may be read.
    Empty = ``file://`` blobs are refused (the service must not read arbitrary host files)."""
    download_host_allowlist: list[str] = Field(default_factory=list)
    """``hostname`` (any port) or ``hostname:port`` a ContentRef ``download_url`` may point to (JSON list).
    Empty (default): downloads are refused. Redirects are never followed."""
    state_dsn: SecretStr | None = None
    """PostgreSQL DSN of the service's own state (idempotency keys, jobs, results) shared by instances.
    Unset: in-memory state - only for a single standalone instance and the CLI (lost on restart)."""
    state_schema: str = Field(default="jane_handler_runtime", pattern=r"^[a-z_][a-z0-9_]{0,62}$")
    """Schema of the state tables (created if missing)."""
    contracts_dir: Path | None = None
    """``contracts/`` with the JSON Schemas; default: found upwards from the package (repo checkout)."""

    @field_validator("download_host_allowlist")
    @classmethod
    def _valid_download_hosts(cls, value: list[str]) -> list[str]:
        parse_host_allowlist(value)  # a typo stops the service at start
        return value


class SandboxLimits(Limits):
    """``limits.sandbox`` of the contract (ADR-0003)."""

    cpu_cores: float = Field(default=1.0, gt=0)
    memory_mb: int = Field(default=512, ge=16)
    wall_time_ms: int = Field(default=30_000, ge=1)
    max_output_bytes: int = Field(default=4_194_304, ge=1)
    max_processes: int = Field(default=16, ge=1)
    tmpfs_mb: int = Field(default=64, ge=0)


class TimeoutLimits(Limits):
    invocation_timeout_ms: int = contract_field("timeouts.invocation_timeout_ms", 60_000, ge=1)
    sync_response_max_ms: int = contract_field("timeouts.sync_response_max_ms", 25_000, ge=1)
    request_timeout_ms: int = contract_field("timeouts.request_timeout_ms", 30_000, ge=1)
    """Registry calls and blob downloads (a whole ``download_url`` download, connection included)."""


class ConcurrencyLimits(Limits):
    max_parallel_invocations: int = contract_field("concurrency.max_parallel_invocations", 2, ge=1)
    """Sandboxes running at the same time in one instance."""


class PackageLimits(Limits):
    """Service-specific bounds for untrusted package archives and inputs (not in the contract)."""

    max_archive_bytes: int = Field(default=50 * 2**20, ge=1)
    max_unpacked_bytes: int = Field(default=200 * 2**20, ge=1)
    max_files: int = Field(default=5_000, ge=1)
    cache_max_entries: int = Field(default=64, ge=1)
    max_input_bytes: int = Field(default=64 * 2**20, ge=1)
    """Content of one material (inline or blob)."""
    max_stored_results: int = Field(default=10_000, ge=1)
    """``GET /v1/invocations/{id}`` keeps at most this many results (in memory, per instance)."""
    docker_api_timeout_ms: int = Field(default=60_000, ge=1)
    max_stderr_in_result_bytes: int = Field(default=16_000, ge=0)
    """Tail of the sandbox stderr put into ``diagnostics.logs_ref`` (inline)."""
    unavailable_retry_after_seconds: int = Field(default=5, ge=0)
    """``Retry-After`` of 503 when the container engine is not reachable."""
    kill_grace_ms: int = Field(default=2_000, ge=0)
    """In-container ``timeout -s KILL`` fires at wall_time_ms + this (safety net if the runtime dies)."""


class StateLimits(Limits):
    """Shared PostgreSQL state (``state_dsn``)."""

    pool_max_size: int = Field(default=10, ge=1)
    connect_timeout_ms: int = Field(default=10_000, ge=1)
    in_progress_lease_ms: int = Field(default=900_000, ge=1)
    """An in-progress idempotency claim of a crashed instance can be taken over after this."""
    job_lease_ms: int = Field(default=30_000, ge=1)
    """A job whose owner stops renewing this lease is marked failed when read."""
    heartbeat_interval_ms: int = Field(default=5_000, ge=1)
    """How often this instance renews leases for its unfinished jobs."""


class ServiceLimits(Limits):
    """Limits of this service. Contract names (``limits.schema.json``) where the limit exists there."""

    sandbox: SandboxLimits = contract_field("sandbox", SandboxLimits())
    timeouts: TimeoutLimits = TimeoutLimits()
    concurrency: ConcurrencyLimits = ConcurrencyLimits()
    packages: PackageLimits = PackageLimits()
    state: StateLimits = StateLimits()
    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()


DEFAULT_HARD_CAPS: dict[str, Any] = {
    "sandbox": {
        "cpu_cores": 4.0,
        "memory_mb": 4096,
        "wall_time_ms": 600_000,
        "max_output_bytes": 64 * 2**20,
        "max_processes": 256,
        "tmpfs_mb": 1024,
    },
    "timeouts": {"invocation_timeout_ms": 900_000},
}
"""Service-level ceilings for values a request may ask for (a request can never raise a limit above these).
A platform file or env hard cap for the same field replaces the default."""

REQUEST_GROUPS = ("sandbox", "timeouts")
"""Groups of ``HandlerInvocation.limits`` this service applies (other groups belong to other services)."""


def _flat(data: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, Mapping):
            out.update(_flat(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


def _nest(flat: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for path, value in flat.items():
        node = out
        *parents, leaf = path.split(".")
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = value
    return out


def _default_caps_layer(platform: list[LimitLayer]) -> LimitLayer:
    configured: set[str] = set()
    for layer in platform:
        configured |= set(_flat(layer.hard_caps))
    caps = {p: v for p, v in _flat(DEFAULT_HARD_CAPS).items() if p not in configured}
    return LimitLayer("platform", hard_caps=_nest(caps), name="service-default-caps")


def request_layer(limits: Mapping[str, Any] | None) -> LimitLayer | None:
    """``HandlerInvocation.limits`` -> request layer with only the fields this service models."""
    if not limits:
        return None
    known = {p for p in _flat(ServiceLimits().model_dump()) if p.split(".", 1)[0] in REQUEST_GROUPS}
    values = {
        p: v for p, v in _flat({g: limits[g] for g in REQUEST_GROUPS if g in limits}).items() if p in known
    }
    return LimitLayer("request", values=_nest(values), name="invocation") if values else None


def resolve_service_limits(settings: Settings, *extra: LimitLayer | None) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- service default caps <- platform file (``..._LIMITS_FILE``) <- ``JANE_HANDLER_RUNTIME_LIMITS__*``
    <- ``extra`` (request layer). Values above a hard cap are clamped (``min(request, hard_caps)``).

    The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
    the runtime does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail."""
    platform = settings.platform_layers(f"{ENV_PREFIX}LIMITS__")
    layers = [_default_caps_layer(platform), *platform, *(x for x in extra if x is not None)]
    return resolve_limits(ServiceLimits, *layers)
