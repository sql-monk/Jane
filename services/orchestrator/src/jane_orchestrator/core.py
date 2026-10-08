"""Shared state of one orchestrator process: DB, contract schemas, executors, limits, metrics."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from jane_kit.errors import ValidationFailed
from jane_kit.metrics import Metrics
from jane_orchestrator.common import new_id
from jane_orchestrator.contract import ContractSchemas
from jane_orchestrator.db import Database, Jsonb
from jane_orchestrator.executors import Executors
from jane_orchestrator.limits import Effective, LimitsLayer, merge_limits
from jane_orchestrator.settings import ServiceLimits, Settings

__all__ = ["Core", "EngineMetrics"]

log = logging.getLogger(__name__)


@dataclass
class EngineMetrics:
    """Prometheus metrics of the queue engine (attached to the app registry when metrics are enabled)."""

    metrics: Metrics | None = None
    _counters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metrics is None:
            return
        m = self.metrics
        self._counters = {
            "items": m.counter("orchestrator_items_total", "Stage items finished by outcome", ["outcome"]),
            "materials": m.counter(
                "orchestrator_materials_total", "Materials taken from collectors or storage"
            ),
            "backpressure": m.counter(
                "orchestrator_backpressure_total", "Feed iterations held back by a full queue"
            ),
            "runs": m.counter("orchestrator_runs_total", "Runs finished by status", ["status"]),
            "leases_expired": m.counter(
                "orchestrator_leases_reclaimed_total", "Items re-claimed after an expired lease"
            ),
        }

    def inc(self, name: str, amount: float = 1, **labels: str) -> None:
        counter = self._counters.get(name)
        if counter is None:
            return
        (counter.labels(**labels) if labels else counter).inc(amount)


class Core:
    def __init__(self, settings: Settings, limits: ServiceLimits, metrics: Metrics | None = None) -> None:
        self.settings = settings
        self.limits = limits
        self.engine = limits.engine
        self.db = Database(settings.database_url, max_size=limits.engine.db_pool_max)
        self.schemas = ContractSchemas(settings.contracts_dir)
        c = limits.contract
        self.executors = Executors(
            settings.all_executors(),
            connect_timeout_ms=c.timeouts.connect_timeout_ms,
            request_timeout_ms=c.timeouts.request_timeout_ms,
            keepalive_expiry_ms=limits.engine.executor_keepalive_expiry_ms,
            stale_connection_retries=limits.engine.executor_stale_connection_retries,
        )
        self.metrics = EngineMetrics(metrics)
        self.fallback: dict[str, Any] = c.model_dump(mode="json")

    def open(self) -> None:
        self.db.open()
        self.db.migrate()
        self.seed_platform_limits()

    def close(self) -> None:
        self.executors.close()
        self.db.close()

    # ------------------------------------------------------------------ platform limits
    def seed_platform_limits(self) -> None:
        """First start: platform document from ``LIMITS_FILE`` (PlatformLimits) or the documented defaults."""
        from jane_kit.config import load_layer

        doc: dict[str, Any]
        if self.settings.limits_file is not None:
            layer = load_layer(self.settings.limits_file, "platform")
            doc = {"defaults": dict(layer.values)}
            if layer.hard_caps:
                doc["hard_caps"] = dict(layer.hard_caps)
            if layer.profile:
                doc["profile"] = layer.profile
        else:
            doc = {"profile": "orchestrator-defaults", "defaults": self.fallback}
        errors = self.schemas.check(
            self.schemas.schema_uri("common/limits.schema.json#/$defs/PlatformLimits"), doc
        )
        if errors:
            raise ValidationFailed("platform limits file does not match limits.schema.json", errors=errors)
        with self.db.tx() as conn:
            conn.execute(
                "INSERT INTO platform_limits (id, doc) VALUES (1, %s) ON CONFLICT (id) DO NOTHING",
                (Jsonb(doc),),
            )

    def platform_limits(self, conn: Any) -> tuple[dict[str, Any], int]:
        row = conn.execute("SELECT doc, version FROM platform_limits WHERE id = 1").fetchone()
        return (dict(row["doc"]), int(row["version"])) if row else ({"defaults": {}}, 0)

    def effective(
        self,
        platform: dict[str, Any],
        source: dict[str, Any] | None = None,
        task: dict[str, Any] | None = None,
        stage: dict[str, Any] | None = None,
        request: dict[str, Any] | None = None,
    ) -> Effective:
        layers = [LimitsLayer("platform", platform.get("defaults") or {})]
        if source is not None:
            layers.append(LimitsLayer("source", source.get("limits") or {}))
        if task is not None:
            tl = dict(task.get("limits") or {})
            if task.get("retries"):
                tl["retries"] = {**(tl.get("retries") or {}), **task["retries"]}
            layers.append(LimitsLayer("task", tl))
        if stage is not None:
            sl = dict(stage.get("limits") or {})
            if stage.get("retries"):
                sl["retries"] = {**(sl.get("retries") or {}), **stage["retries"]}
            layers.append(LimitsLayer("stage", sl))
        if request:
            layers.append(LimitsLayer("request", request))
        return merge_limits(self.fallback, layers, platform.get("hard_caps") or {})

    # ------------------------------------------------------------------ audit
    @staticmethod
    def audit(
        conn: Any, actor: str, action: str, subject_type: str, subject_id: str, details: dict[str, Any] | None
    ) -> None:
        conn.execute(
            "INSERT INTO audit_events (event_id, actor, action, subject_type, subject_id, details)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (new_id("aud"), actor, action, subject_type, subject_id, Jsonb(details or {})),
        )
