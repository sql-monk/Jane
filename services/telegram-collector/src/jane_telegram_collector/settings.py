"""Settings and limits of the Telegram Collector. Every limit has a safe default documented in README.md.

Limit levels (``contracts/schemas/common/limits.schema.json``): service defaults -> platform (limits file,
then ``JANE_TELEGRAM_COLLECTOR_LIMITS__*``) -> source (``rules.limits``) -> request (``CollectionRequest.limits``
or ``FetchRequest.limits``). ``hard_caps`` bound the result.

The layers are jane-kit's, with the same error checks as every other service (R20): the limits file is a
shared ``PlatformLimits`` profile (contract groups the collector does not use - ``crawl``, ``sandbox``, ``llm``...
- are ignored and listed in ``ResolvedLimits.ignored``, a path unknown to the contract and to the model is an
error); the environment layer takes model paths (``..._LIMITS__COLLECTOR__HISTORY_PAGE_SIZE``); source and
request layers are contract-shaped ``Limits`` documents applied the same way as the profile
(:func:`contract_layer`).
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

ENV_PREFIX = "JANE_TELEGRAM_COLLECTOR_"
LIMITS_ENV_PREFIX = f"{ENV_PREFIX}LIMITS__"

log = logging.getLogger(__name__)


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "telegram-collector"
    port: int = 8102

    state_dir: Path = Path(".jane/telegram-collector")
    """Own state store (SQLite ``state.db``): runs, channel cursors, seen revisions, buffer, jobs."""
    client_backend: str = "recorded"
    """Telegram client: ``recorded`` (JSON recordings, tests/demos), ``telethon`` (optional extra) or
    ``<module>:<factory>`` returning a :class:`~jane_telegram_collector.client.ClientFactory`."""
    recordings_dir: Path | None = None
    """``recorded`` backend: directory with ``<username or channel_id>.json`` recordings."""
    default_account_connection_id: str | None = None
    """Connection (``kind=telegram_account``) used when rules name none (e.g. ``/v1/fetches`` without rules)."""
    transit_dir: Path | None = None
    """Transit blob store for large content and media (``file://`` ContentRef). Unset: inline only."""
    rules_dir: Path | None = None
    """Local collector-rules packages for ``rules_ref`` without a registry (``<package_id>/<version>/``)."""
    registry_url: str | None = None
    """registry.v1 base URL for ``rules_ref``; checked after ``rules_dir``."""
    registry_token_env: str | None = None
    """Name of the environment variable holding the bearer token for the registry (never the value)."""
    contracts_dir: Path | None = None
    """``contracts/`` with the JSON Schemas; default: ``JANE_CONTRACTS_DIR`` or the checkout's contracts."""
    secret_env_prefix: str = "JANE_SECRET_"  # noqa: S105 - a variable-name prefix, not a secret
    """``env:`` secret references may name only variables with this prefix."""
    secret_files_dir: Path | None = Path("/run/secrets")
    """``file:`` secret references must point inside this directory (unset: ``file:`` disabled)."""
    telegram_host_allowlist: list[str] = Field(default_factory=list)
    """Hosts allowed in host-like connection params (``server``, ``proxy_host``...); default: none."""
    lease_seconds: int = Field(default=30, ge=2)
    """A running collection is owned by one instance; after this long without a heartbeat another takes it."""
    heartbeat_interval_ms: int = Field(default=5_000, ge=50)
    """How often the owner renews the lease and checks for cancellation requested through other instances."""
    state_busy_timeout_ms: int = Field(default=10_000, ge=1)
    """How long a write waits for another process holding the SQLite lock."""
    idempotency_lease_ms: int = Field(default=900_000, ge=1_000)
    """An ``Idempotency-Key`` claim of a killed instance (not renewed for this long) can be claimed again; a live
    instance renews its claims in the resume loop (R17)."""

    def connection_policy(self) -> ConnectionPolicy:

        return ConnectionPolicy(
            env_prefix=self.secret_env_prefix,
            files_dir=self.secret_files_dir,
            host_allowlist=tuple(self.telegram_host_allowlist),
        )

    @model_validator(mode="after")
    def _lease_rules(self) -> Settings:
        # The owner must renew its lease before it expires even if one write waited the full busy timeout;
        # otherwise a live instance would lose the collection to another one.
        lease_ms = self.lease_seconds * 1000
        if self.heartbeat_interval_ms + self.state_busy_timeout_ms >= lease_ms:
            raise ValueError(
                f"heartbeat_interval_ms ({self.heartbeat_interval_ms}) + state_busy_timeout_ms "
                f"({self.state_busy_timeout_ms}) must be less than lease_seconds*1000 ({lease_ms})"
            )
        return self


class Rate(Limits):
    min_delay_ms_per_host: int = Field(default=200, ge=0)
    """Minimum interval between two Telegram API calls of one run (the API is the only "host")."""


class Timeouts(Limits):
    connect_timeout_ms: int = Field(default=15_000, ge=1)
    """Opening the Telegram client (connect + authorization check)."""
    request_timeout_ms: int = Field(default=30_000, ge=1)
    """One Telegram API call (history page, difference, message, media download)."""


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


class Telegram(Limits):
    max_messages_per_run: int = Field(default=10_000, ge=1)
    max_media_bytes: int = Field(default=20 * 1024**2, ge=0)
    max_flood_wait_seconds: int = Field(default=300, ge=0)


class Collector(Limits):
    """Service-specific limits (not in the contract; visible in the start-up log)."""

    history_page_size: int = Field(default=100, ge=1)
    """Messages per history request (Telegram returns at most 100)."""
    changes_page_size: int = Field(default=100, ge=1)
    """Updates per ``getChannelDifference`` request."""
    max_wait_ms: int = Field(default=30_000, ge=0)
    """Upper bound of ``wait_ms`` long-poll on ``/materials``."""
    long_poll_interval_ms: int = Field(default=100, ge=10)
    """``/materials?wait_ms=``: how often new materials are looked for while waiting."""
    backpressure_poll_ms: int = Field(default=1_000, ge=10)
    """While paused by backpressure: how often the buffer is re-checked (acks may arrive via another instance)."""
    gc_interval_seconds: int = Field(default=3_600, ge=1)
    """How often expired collections and transit files are cleaned up."""


class ServiceLimits(Limits):
    """Limits of the Telegram Collector; group and field names follow ``limits.schema.json``."""

    rate: Rate = contract_field("rate", Rate())
    timeouts: Timeouts = contract_field("timeouts", Timeouts())
    retries: Retries = contract_field("retries", Retries())
    queue: Queue = contract_field("queue", Queue())
    transfer: Transfer = contract_field("transfer", Transfer())
    telegram: Telegram = contract_field("telegram", Telegram())
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
    """A contract-shaped ``Limits`` document (``rules.limits``, request ``limits``) as a jane-kit layer: contract
    paths go to the fields that declare them (``transfer.job_retention_seconds`` -> ``jobs.job_retention_seconds``),
    contract limits the collector does not have are ignored, anything else is a
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
    """Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_TELEGRAM_COLLECTOR_LIMITS__*`` <- ``extra``
    (source/request layers, contract-shaped). Invalid limits raise :class:`~jane_kit.config.LimitError`."""
    return resolve_limits(ServiceLimits, *platform_layers(settings), *(contract_layer(x) for x in extra))
