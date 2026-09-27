"""Settings and limits of the orchestrator. Every limit has a safe default documented in README.md.

Two kinds of limits:

* **Contract limits** (``limits.schema.json``): the platform document lives in the orchestrator DB
  (``GET/PUT /v1/limits/platform``) and is merged with source → task → stage → request levels for every
  run (``GET /v1/limits/effective``). :class:`ContractDefaults` gives the fallback for the fields the
  orchestrator itself consumes when the platform document does not set them; it also seeds the platform
  document on the first start when no limits file is configured.
* **Internal knobs** (:class:`EngineLimits`): lease duration, polling intervals, page sizes — they are
  not in the contract and come from env ``JANE_ORCHESTRATOR_LIMITS__ENGINE__*``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import SettingsConfigDict

from jane_kit.clients import RetryPolicy
from jane_kit.config import JaneSettings, LimitLayer, Limits, ResolvedLimits, contract_field, resolve_limits
from jane_kit.idempotency import IdempotencyLimits
from jane_kit.pagination import PageLimits

ENV_PREFIX = "JANE_ORCHESTRATOR_"


class ExecutorConfig(BaseModel):
    """A service the orchestrator calls (``orchestrator.v1`` ``Executor``)."""

    model_config = ConfigDict(extra="forbid")

    executor: str
    role: Literal["collector", "handler", "storage_read", "registry", "llm", "assistant"]
    base_url: str
    capabilities: dict[str, Any] = Field(default_factory=dict)
    """``collector: web`` for collectors; ``handler_kinds: [...]`` and ``packages: ["jane.storage-*"]``
    (globs of package ids routed to this executor) for handlers; ``default: true`` marks the fallback
    handler executor."""
    sync_connections: bool | None = None
    """Push the connections registry to this executor (``PUT /v1/connections/{id}``). Default: true for
    collectors, handlers and llm."""
    token: str | None = None
    """Bearer token for this executor (service account); never logged or returned by the API."""

    @property
    def syncs_connections(self) -> bool:
        if self.sync_connections is not None:
            return self.sync_connections
        return self.role in {"collector", "handler", "llm"}


class Queue(Limits):
    max_queue_depth: int = contract_field("queue.max_queue_depth", 10_000, ge=1)
    max_inflight_materials: int = contract_field("queue.max_inflight_materials", 100, ge=1)


class Concurrency(Limits):
    max_parallel_runs_per_task: int = contract_field("concurrency.max_parallel_runs_per_task", 1, ge=1)
    max_parallel_stage_items: int = contract_field("concurrency.max_parallel_stage_items", 4, ge=1)


class Timeouts(Limits):
    connect_timeout_ms: int = contract_field("timeouts.connect_timeout_ms", 5_000, ge=1)
    request_timeout_ms: int = contract_field("timeouts.request_timeout_ms", 30_000, ge=1)
    invocation_timeout_ms: int = contract_field("timeouts.invocation_timeout_ms", 60_000, ge=1)
    run_timeout_ms: int = contract_field("timeouts.run_timeout_ms", 21_600_000, ge=1)


class Transfer(Limits):
    idempotency_ttl_seconds: int = contract_field("transfer.idempotency_ttl_seconds", 86_400, ge=60)


class ContractDefaults(Limits):
    """Fallback values of contract limits the orchestrator consumes (level ``platform``)."""

    queue: Queue = Queue()
    concurrency: Concurrency = Concurrency()
    timeouts: Timeouts = Timeouts()
    transfer: Transfer = Transfer()
    retries: RetryPolicy = contract_field(
        "retries",
        RetryPolicy(max_attempts=3, initial_backoff_ms=1_000, max_backoff_ms=60_000),
    )


class EngineLimits(Limits):
    """Internal knobs of the queue engine (not part of ``limits.schema.json``)."""

    workers: int = Field(default=2, ge=0)
    """Worker threads per process (0 — API only)."""
    lease_ms: int = Field(default=30_000, ge=100)
    """Lease of a claimed item / collection feed; extended by heartbeats while a call runs."""
    heartbeat_ms: int = Field(default=10_000, ge=50)
    poll_interval_ms: int = Field(default=500, ge=10)
    """Idle sleep of a worker when there is nothing to claim."""
    feed_page_size: int = Field(default=100, ge=1)
    """Materials requested from a collector per page (bounded further by queue limits)."""
    feed_wait_ms: int = Field(default=1_000, ge=0)
    """Long-poll ``wait_ms`` for collector material pages."""
    backpressure_recheck_ms: int = Field(default=500, ge=10)
    scheduler_interval_ms: int = Field(default=1_000, ge=10)
    sync_retry_ms: int = Field(default=5_000, ge=10)
    """Delay before retrying a failed connection sync."""
    sync_max_attempts: int = Field(default=5, ge=1)
    executor_health_timeout_ms: int = Field(default=2_000, ge=1)
    job_poll_interval_ms: int = Field(default=500, ge=10)
    """Polling interval for an executor's 202 job (async handler invocation)."""
    problem_samples: int = Field(default=10, ge=0)
    """Samples kept per problem group."""
    trace_outputs_max: int = Field(default=100, ge=0)
    """Output references (entity keys, stored object ids) recorded per item for the material trace."""
    db_pool_max: int = Field(default=10, ge=1)
    max_lease_reclaims: int = Field(default=5, ge=1)
    """Take-overs of an expired lease before an item is failed as poisonous (a worker keeps dying on it).
    Take-overs are not retry attempts (``retries.max_attempts``): the handler may have done its effect."""
    schedule_batch: int = Field(default=20, ge=1)
    """Due tasks turned into runs per scheduler pass."""
    reap_batch: int = Field(default=50, ge=1)
    """Runs checked per housekeeping pass (finish cancelled/drained runs, run timeouts)."""


class ServiceLimits(Limits):
    contract: ContractDefaults = ContractDefaults()
    engine: EngineLimits = EngineLimits()
    idempotency: IdempotencyLimits = IdempotencyLimits()
    pages: PageLimits = PageLimits()


class Settings(JaneSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra="ignore", env_nested_delimiter="__")

    service_name: str = "orchestrator"
    port: int = 8109
    database_url: str = "postgresql://jane@127.0.0.1:5432/jane_orchestrator"
    """DSN of the orchestrator's own database (it never touches other services' databases)."""
    executors: list[ExecutorConfig] = Field(default_factory=list)
    executors_file: Path | None = None
    """JSON file with a list of executors (alternative to ``JANE_ORCHESTRATOR_EXECUTORS``)."""
    contracts_dir: Path | None = None
    """``contracts/`` for request validation (default: env ``JANE_CONTRACTS_DIR`` or the checkout)."""
    api_keys: list[dict[str, Any]] = Field(default_factory=list)
    """``auth_mode=api_key``: ``[{"name": "admin", "sha256": "<hex of key>", "scopes": [...]}]``."""
    scheduler_enabled: bool = True
    run_workers: bool = True
    """Start worker threads inside the API process (``python -m jane_orchestrator worker`` runs them alone)."""

    def all_executors(self) -> list[ExecutorConfig]:
        items = list(self.executors)
        if self.executors_file is not None:
            data = json.loads(self.executors_file.read_text(encoding="utf-8"))
            items += [ExecutorConfig.model_validate(x) for x in data]
        return items


def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
    """Defaults <- ``JANE_ORCHESTRATOR_LIMITS__*`` env <- ``extra``.

    The platform limits *file* (``JANE_ORCHESTRATOR_LIMITS_FILE``, ``PlatformLimits``) seeds the platform
    document in the DB instead (see :mod:`jane_orchestrator.limits`), because it has the contract shape.
    """
    env_layers = [
        layer
        for layer in settings.model_copy(update={"limits_file": None}).platform_layers(
            f"{ENV_PREFIX}LIMITS__"
        )
    ]
    return resolve_limits(ServiceLimits, *env_layers, *extra)
