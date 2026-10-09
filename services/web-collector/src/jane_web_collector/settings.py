"""Settings and limits of the Web Collector. Every limit has a safe default documented in README.md.

Limit levels (``contracts/schemas/common/limits.schema.json``): service defaults -> platform (limits file,
then ``JANE_WEB_COLLECTOR_LIMITS__*``) -> source (``rules.limits``) -> request (``CollectionRequest.limits``)
-> strategy (``strategies[].limits``, only for that strategy's URLs). ``hard_caps`` bound the result.

The layers are jane-kit's, with the same error checks as every other service (R20): the limits file is a
shared ``PlatformLimits`` profile (contract paths map to the fields that declare them, contract groups the
collector does not use - ``sandbox``, ``llm``, ``telegram``... - are ignored and listed in
``ResolvedLimits.ignored``, a path unknown to the contract and to the model is an error); the environment layer
takes model paths (``..._LIMITS__JOBS__JOB_RETENTION_SECONDS``); source, request and strategy layers are
contract-shaped ``Limits`` documents (validated against the contract before they get here) and are applied the
same way as the profile (:func:`contract_layer`).
"""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict

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
from jane_kit.pagination import PageLimits

from .connections import ConnectionPolicy
from .egress import EgressPolicy

ENV_PREFIX = "JANE_WEB_COLLECTOR_"
LIMITS_ENV_PREFIX = f"{ENV_PREFIX}LIMITS__"

log = logging.getLogger(__name__)


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "web-collector"
    port: int = 8101

    state_dir: Path = Path(".jane/web-collector")
    """Own state store (SQLite ``state.db``): frontier, known URLs, strategy state, buffer, jobs."""
    transit_dir: Path | None = None
    """Transit blob store for large materials (``file://`` ContentRef). Unset: inline only."""
    rules_dir: Path | None = None
    """Local collector-rules packages for ``rules_ref`` without a registry (``<package_id>/<version>/``)."""
    registry_url: str | None = None
    """registry.v1 base URL for ``rules_ref``; checked after ``rules_dir``."""
    registry_token_env: str | None = None
    """Name of the environment variable holding the bearer token for the registry (never the value)."""
    secret_env_prefix: str = "JANE_SECRET_"  # noqa: S105 - variable-name prefix, not a credential
    """Only env: references with this prefix may be resolved; empty disables env: references."""
    secret_files_dir: Path | None = Path("/run/secrets")
    """Only file: references inside this directory may be resolved; empty disables file: references."""
    connection_origin_allowlist: list[str] = Field(default_factory=list)
    """Exact HTTP(S) origins allowed to receive resolved connection credentials; empty denies all."""
    egress_deny_link_local: bool = True
    """Outbound policy: never connect to link-local addresses (169.254.0.0/16 with the cloud metadata service,
    fe80::/10, fd00:ec2::254). Checked after DNS resolution for every connection, including redirect hops."""
    egress_deny_private: bool = False
    """Outbound policy: also never connect to loopback, private and other non-public addresses. Off by default:
    the dev/e2e test site is in a private Docker network; turn it on where sources are public sites only."""
    contracts_dir: Path | None = None
    """``contracts/`` with the JSON Schemas; default: ``JANE_CONTRACTS_DIR`` or the checkout's contracts."""
    discovery_path: Path | None = None
    """Directory of the WP-03 discovery package; default ``services/web-collector/strategies/discovery``."""
    user_agent: str = "JaneBot/0.1 (+https://github.com/jane)"
    """Default User-Agent; ``rules.fetch.user_agent`` overrides it. The robots token is its first word."""
    lease_seconds: int = Field(default=30, ge=2)
    """A running collection is owned by one instance; after this long without a heartbeat another takes it."""
    heartbeat_interval_ms: int = Field(default=5_000, ge=50)
    """How often the owner renews the lease and checks for cancellation from other instances."""
    state_busy_timeout_ms: int = Field(default=10_000, ge=1)
    """How long a write waits for another process holding the SQLite lock."""

    @model_validator(mode="after")
    def _lease_rules(self) -> Settings:
        # The owner must renew its lease before it expires even if one write waited the full busy timeout;
        # otherwise a live instance would lose the collection to another one (duplicates, lost URLs).
        lease_ms = self.lease_seconds * 1000
        if self.heartbeat_interval_ms + self.state_busy_timeout_ms >= lease_ms:
            raise ValueError(
                f"heartbeat_interval_ms ({self.heartbeat_interval_ms}) + state_busy_timeout_ms "
                f"({self.state_busy_timeout_ms}) must be less than lease_seconds*1000 ({lease_ms})"
            )
        self.connection_policy()
        return self

    def egress_policy(self) -> EgressPolicy:
        return EgressPolicy(
            deny_link_local=self.egress_deny_link_local, deny_private=self.egress_deny_private
        )

    def connection_policy(self) -> ConnectionPolicy:
        return ConnectionPolicy(
            env_prefix=self.secret_env_prefix,
            files_dir=self.secret_files_dir,
            origin_allowlist=tuple(self.connection_origin_allowlist),
        )


class Concurrency(Limits):
    max_parallel_fetches: int = Field(default=4, ge=1)
    max_parallel_fetches_per_host: int = Field(default=2, ge=1)


class Rate(Limits):
    requests_per_second_per_host: float = Field(default=1.0, gt=0)
    min_delay_ms_per_host: int = Field(default=500, ge=0)
    respect_crawl_delay: bool = True


class Crawl(Limits):
    max_depth: int = Field(default=5, ge=0)
    max_pages_per_run: int = Field(default=5_000, ge=1)
    max_bytes_per_run: int = Field(default=2 * 1024**3, ge=1)
    max_material_bytes: int = Field(default=10 * 1024**2, ge=1)
    max_redirects: int = Field(default=5, ge=0)
    max_links_per_page: int = Field(default=2_000, ge=0)
    max_seed_urls: int = Field(default=100_000, ge=1)
    max_frontier_size: int = Field(default=100_000, ge=1)
    revisit_interval_seconds: int = Field(default=86_400, ge=0)


class Timeouts(Limits):
    connect_timeout_ms: int = Field(default=10_000, ge=1)
    request_timeout_ms: int = Field(default=30_000, ge=1)


class Retries(Limits):
    max_attempts: int = Field(default=3, ge=1)
    initial_backoff_ms: int = Field(default=1_000, ge=0)
    max_backoff_ms: int = Field(default=60_000, ge=0)
    backoff_multiplier: float = Field(default=2.0, ge=1)
    jitter: bool = True


class Queue(Limits):
    max_unacked_materials: int = Field(default=500, ge=1)


class Transfer(Limits):
    inline_max_bytes: int = Field(default=262_144, ge=0)
    transit_ttl_seconds: int = Field(default=604_800, ge=60)


class Collector(Limits):
    """Service-specific limits (not in the contract; visible only in the start-up log)."""

    max_wait_ms: int = Field(default=30_000, ge=0)
    """Upper bound of ``wait_ms`` long-poll on ``/materials``."""
    robots_cache_ttl_seconds: int = Field(default=3_600, ge=0)
    robots_max_bytes: int = Field(default=512_000, ge=1)
    """robots.txt larger than this is truncated (RFC 9309 allows >= 500 KiB)."""
    max_retry_after_seconds: int = Field(default=300, ge=0)
    """A source asking to wait longer (Retry-After, Crawl-delay) makes the URL fail with ``rate_limited``."""
    backpressure_poll_ms: int = Field(default=1_000, ge=10)
    """While paused by backpressure: how often the buffer is re-checked (acks may arrive via another instance)."""
    long_poll_interval_ms: int = Field(default=100, ge=10)
    """``/materials?wait_ms=``: how often new materials are looked for while waiting."""
    gc_interval_seconds: int = Field(default=3_600, ge=1)
    """How often expired collections and transit files are cleaned up."""
    host_state_prune_interval_seconds: int = Field(default=60, ge=1)
    """How often the shared per-host limiter drops the state of hosts nobody uses any more."""
    shared_host_limits: bool = True
    """Coordinate the per-host limits with the other instances that share the state store (R15)."""
    shared_host_poll_ms: int = Field(default=100, ge=10)
    """A request waiting for a host slot that other instances hold re-checks this often."""
    shared_host_ttl_seconds: int = Field(default=120, ge=1)
    """A registration of an instance on a host, or a slot it holds, expires after this long without a renewal or
    a release (an instance that was killed stops limiting the others); keep it above
    ``timeouts.request_timeout_ms``."""


class ServiceLimits(Limits):
    """Limits of the Web Collector; group and field names follow ``limits.schema.json``."""

    concurrency: Concurrency = contract_field("concurrency", Concurrency())
    rate: Rate = contract_field("rate", Rate())
    crawl: Crawl = contract_field("crawl", Crawl())
    timeouts: Timeouts = contract_field("timeouts", Timeouts())
    retries: Retries = contract_field("retries", Retries())
    queue: Queue = contract_field("queue", Queue())
    transfer: Transfer = contract_field("transfer", Transfer())
    jobs: JobLimits = JobLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()
    page: PageLimits = PageLimits()
    collector: Collector = Collector()

    @model_validator(mode="after")
    def _backoff_bounds(self) -> ServiceLimits:
        if self.retries.max_backoff_ms < self.retries.initial_backoff_ms:
            raise ValueError("retries.max_backoff_ms must be >= retries.initial_backoff_ms")
        return self


# ---------------------------------------------------------------- jane-kit layers (R20)


def contract_layer(layer: LimitLayer) -> LimitLayer:
    """A contract-shaped ``Limits`` document (``rules.limits``, request ``limits``, ``strategies[].limits``) as a
    jane-kit layer: contract paths go to the fields that declare them (``transfer.job_retention_seconds`` ->
    ``jobs.job_retention_seconds``), contract limits the collector does not have are ignored, anything else is a
    :class:`~jane_kit.config.LimitError` - exactly as for the platform profile."""
    return dataclasses.replace(layer, shared=True)


def to_contract(limits: ServiceLimits) -> dict[str, Any]:
    """Model -> contract ``Limits`` document (only fields that exist in the contract), by jane-kit's mapping."""
    defaults: dict[str, Any] = ResolvedLimits(limits=limits, origin={}, clamped={}).platform_limits()[
        "defaults"
    ]
    return defaults


def platform_layers(settings: Settings) -> list[LimitLayer]:
    """jane-kit's platform layers: the ``PlatformLimits`` file (shared profile) and the env overrides."""
    return settings.platform_layers(LIMITS_ENV_PREFIX)


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_WEB_COLLECTOR_LIMITS__*`` <- ``extra``
    (source/request/strategy layers, contract-shaped). Invalid limits raise :class:`~jane_kit.config.LimitError`."""
    return resolve_limits(ServiceLimits, *platform_layers(settings), *(contract_layer(x) for x in extra))
