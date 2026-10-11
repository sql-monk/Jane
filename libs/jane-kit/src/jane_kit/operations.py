"""Per-module configuration and durable sampled telemetry; no neighbouring databases."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import sqlite3
import time
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.concurrency import run_in_threadpool

from jane_kit.auth import require
from jane_kit.errors import BadRequest, JaneError, ValidationFailed

log = logging.getLogger(__name__)

# Deliberate allow-list: credentials, paths, executors, network policy and auth never enter this API.
EDITABLE_SETTINGS = {
    "log_level",
    "health_check_timeout_ms",
    "render_enabled",
    "render_wait_until",
    "user_agent",
    "run_workers",
    "scheduler_enabled",
    "lease_seconds",
    "heartbeat_interval_ms",
    "operations_sample_interval_seconds",
    "operations_retention_seconds",
    "operations_max_points",
}


def operations_path(settings: Any) -> Path:
    return (
        Path(settings.operations_dir)
        if settings.operations_dir
        else Path(".jane") / "operations" / settings.service_name
    )


def read_overrides(settings: Any) -> dict[str, Any]:
    path = operations_path(settings) / "operations.sqlite3"
    if not path.exists():
        return {}
    with closing(sqlite3.connect(path, timeout=5)) as db:
        row = db.execute("SELECT document FROM configuration WHERE id=1").fetchone()
    return json.loads(row[0]) if row else {}


def flatten(value: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(item, dict):
            out.update(flatten(item, path))
        else:
            out[path] = item
    return out


def unflatten(value: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, item in value.items():
        parts = key.split(".")
        target = out
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = item
    return out


class ConfigurationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    values: dict[str, bool | int | float | str]


class Operations:
    def __init__(self, app: FastAPI, settings: Any, resolved: Any) -> None:
        self.app, self.settings, self.resolved = app, settings, resolved
        self.path = operations_path(settings) / "operations.sqlite3"
        self.previous: tuple[float, dict[str, float]] | None = None

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        await run_in_threadpool(self.initialize)
        task = asyncio.create_task(self.sample_loop(), name="module-telemetry")
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=self.settings.health_check_timeout_ms / 1000)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS configuration (id INTEGER PRIMARY KEY, "
                "revision INTEGER NOT NULL, document TEXT NOT NULL, updated_at TEXT)"
            )
            db.execute("INSERT OR IGNORE INTO configuration VALUES (1,0,'{}',NULL)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS samples (sample_id INTEGER PRIMARY KEY, "
                "at REAL NOT NULL, instance TEXT NOT NULL, document TEXT NOT NULL)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS samples_at ON samples(at)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS changes (revision INTEGER PRIMARY KEY, "
                "at TEXT NOT NULL, actor TEXT NOT NULL, document TEXT NOT NULL)"
            )

    def fields(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []

        def walk(model: BaseModel, prefix: str) -> None:
            schema = type(model).model_json_schema()
            for name, field in type(model).model_fields.items():
                value = getattr(model, name)
                path = f"{prefix}.{name}"
                if isinstance(value, BaseModel):
                    walk(value, path)
                elif isinstance(value, (bool, int, float, str)):
                    if prefix == "settings" and name not in EDITABLE_SETTINGS:
                        continue
                    prop = schema.get("properties", {}).get(name, {})
                    kind = (
                        "boolean"
                        if isinstance(value, bool)
                        else "number"
                        if isinstance(value, (int, float))
                        else "string"
                    )
                    row: dict[str, Any] = {
                        "path": path,
                        "value": value,
                        "inherited_value": self.settings._operations_baseline.get(name, value)
                        if prefix == "settings"
                        else self.resolved.module_baseline.get(path.removeprefix("limits."), value),
                        "type": kind,
                        "description": field.description or "",
                        "requires_restart": True,
                        "origin": self.resolved.origin.get(path.removeprefix("limits."), "default")
                        if self.resolved is not None and prefix != "settings"
                        else "startup",
                    }
                    for source, target in [
                        ("minimum", "minimum"),
                        ("maximum", "maximum"),
                        ("exclusiveMinimum", "exclusive_minimum"),
                        ("enum", "choices"),
                    ]:
                        if source in prop:
                            row[target] = prop[source]
                    if prop.get("type") == "integer":
                        row["integer"] = True
                    if path == "settings.log_level":
                        row["choices"] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                    if self.resolved is not None and path.startswith("limits."):
                        cap = self.resolved.hard_caps.get(path[7:])
                        if isinstance(cap, (int, float)) and not isinstance(cap, bool):
                            row["maximum"] = min(row.get("maximum", cap), cap)
                    out.append(row)

        walk(self.settings, "settings")
        if self.resolved is not None:
            walk(self.resolved.limits, "limits")
        return out

    def configuration(self) -> tuple[dict[str, Any], str]:
        with self.connect() as db:
            row = db.execute("SELECT * FROM configuration WHERE id=1").fetchone()
        assert row is not None
        overrides = json.loads(row["document"])
        fields = self.fields()
        for field in fields:
            if field["value"] != field["inherited_value"]:
                field["origin"] = "module"
            if field["path"] in overrides:
                field["configured_value"] = overrides[field["path"]]
                field["origin"] = "module" if field["value"] == overrides[field["path"]] else field["origin"]
        doc = {
            "service": self.settings.service_name,
            "instance_id": self.settings.instance_id,
            "revision": row["revision"],
            "updated_at": row["updated_at"],
            "fields": fields,
            "overrides": overrides,
            "pending_restart": any(
                f["value"] != overrides.get(f["path"], f["inherited_value"]) for f in fields
            ),
        }
        return doc, f'"module-{row["revision"]}"'

    def save(self, values: dict[str, Any], expected: str | None, actor: str) -> tuple[dict[str, Any], str]:
        if expected is None:
            raise JaneError("Read configuration before saving", code="precondition_required")
        fields = {f["path"]: f for f in self.fields()}
        if set(values) - fields.keys():
            raise ValidationFailed("Unknown or protected configuration field")
        for path, value in values.items():
            field = fields[path]
            kind = field["type"]
            if (
                (kind == "boolean" and not isinstance(value, bool))
                or (kind == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))))
                or (kind == "string" and not isinstance(value, str))
            ):
                raise ValidationFailed(f"Invalid type for {path}")
            if "choices" in field and value not in field["choices"]:
                raise ValidationFailed(f"Invalid choice for {path}")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValidationFailed(f"Invalid number for {path}")
            if "maximum" in field and value > field["maximum"]:
                raise ValidationFailed(f"{path} exceeds its hard cap")
        settings_values = {p[9:]: v for p, v in values.items() if p.startswith("settings.")}
        limit_values = {p[7:]: v for p, v in values.items() if p.startswith("limits.")}
        try:
            self.settings.validate_configuration({**self.settings._operations_baseline, **settings_values})
            if self.resolved is not None:
                merged = {**self.resolved.module_baseline, **limit_values}
                type(self.resolved.limits).model_validate(unflatten(merged))
        except ValidationError as exc:
            # Do not put startup configuration (which includes secrets) in a validation error.
            raise ValidationFailed(
                "Configuration constraints failed: "
                + ", ".join(".".join(map(str, error["loc"])) for error in exc.errors())
            ) from None
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision FROM configuration WHERE id=1").fetchone()
            assert row is not None
            if expected != f'"module-{row["revision"]}"':
                raise JaneError("Configuration changed; reload before saving", code="precondition_failed")
            revision = row["revision"] + 1
            document = json.dumps(values, allow_nan=False)
            db.execute(
                "UPDATE configuration SET revision=?, document=?, updated_at=? WHERE id=1",
                (revision, document, now),
            )
            db.execute("INSERT INTO changes VALUES (?,?,?,?)", (revision, now, actor, document))
        log.info(
            "module configuration saved",
            extra={"revision": revision, "actor": actor, "fields": sorted(values)},
        )
        return self.configuration()

    def definitions(self) -> list[dict[str, str]]:
        return [
            {"key": "http_requests_per_second", "label": "API-запити", "unit": "запитів/с"},
            {"key": "http_errors_per_second", "label": "Помилки API (5xx)", "unit": "помилок/с"},
            {"key": "http_latency_ms", "label": "Середній час API-запиту", "unit": "мс"},
            {"key": "http_in_flight", "label": "API-запити у виконанні", "unit": "запитів"},
            {"key": "materials_per_second", "label": "Прийняті матеріали", "unit": "матеріалів/с"},
            {"key": "stage_items_per_second", "label": "Завершені елементи етапів", "unit": "елементів/с"},
            {"key": "storage_writes_per_second", "label": "Підтвердження запису", "unit": "записів/с"},
            {"key": "llm_requests_per_second", "label": "LLM-запити", "unit": "запитів/с"},
            *getattr(self.app.state, "operations_metric_definitions", []),
        ]

    def sample(self) -> None:
        totals: dict[str, float] = {}
        metrics = getattr(self.app.state, "metrics", None)
        if metrics is not None:
            for metric in metrics.registry.collect():
                if metric.type == "counter":
                    totals.setdefault(f"{metric.name}_total", 0)
                for item in metric.samples:
                    if item.labels.get("route", "").startswith(
                        ("/v1/telemetry", "/v1/configuration", "/v1/health", "/v1/info")
                    ):
                        continue
                    totals[item.name] = totals.get(item.name, 0) + item.value
                    if item.name.endswith("http_requests_total") and item.labels.get("status", "").startswith(
                        "5"
                    ):
                        totals["errors"] = totals.get("errors", 0) + item.value
            # An empty registered counter is still known; absent domain metrics are unavailable.
            for key in [
                "jane_http_requests_total",
                "jane_http_request_duration_seconds_count",
                "jane_http_request_duration_seconds_sum",
                "errors",
            ]:
                totals.setdefault(key, 0)
        monotonic = time.monotonic()
        previous_time, previous = self.previous or (monotonic, {})
        elapsed = monotonic - previous_time

        def delta(key: str) -> float | None:
            if key not in totals or key not in previous or elapsed <= 0:
                return None
            return max(0, totals[key] - previous[key])

        def rate(key: str) -> float | None:
            amount = delta(key)
            return amount / elapsed if amount is not None else None

        count = delta("jane_http_request_duration_seconds_count")
        duration = delta("jane_http_request_duration_seconds_sum")
        values: dict[str, float | None] = {
            "http_requests_per_second": rate("jane_http_requests_total"),
            "http_errors_per_second": rate("errors"),
            "http_latency_ms": duration * 1000 / count if duration is not None and count else None,
            "http_in_flight": totals.get("jane_http_requests_in_flight"),
            "materials_per_second": rate("jane_orchestrator_materials_total"),
            "stage_items_per_second": rate("jane_orchestrator_items_total"),
            "storage_writes_per_second": rate("jane_storage_writes_total"),
            "llm_requests_per_second": rate("jane_llm_requests_total"),
        }
        probe: Callable[[], dict[str, float]] | None = getattr(self.app.state, "operations_probe", None)
        if probe is not None:
            try:
                values.update(probe())
            except Exception:
                log.exception("module telemetry probe unavailable")
                for definition in getattr(self.app.state, "operations_metric_definitions", []):
                    values[definition["key"]] = None
        self.previous = monotonic, totals
        now = time.time()
        with self.connect() as db:
            db.execute(
                "INSERT INTO samples(at,instance,document) VALUES (?,?,?)",
                (now, self.settings.instance_id, json.dumps(values, allow_nan=False)),
            )
            db.execute(
                "DELETE FROM samples WHERE at < ?", (now - self.settings.operations_retention_seconds,)
            )

    async def sample_loop(self) -> None:
        while True:
            try:
                await run_in_threadpool(self.sample)
            except Exception:
                log.exception("module telemetry sample failed")
            await asyncio.sleep(self.settings.operations_sample_interval_seconds)

    def telemetry(self, since: datetime | None, until: datetime | None, limit: int) -> dict[str, Any]:
        end = until.timestamp() if until else time.time()
        start = since.timestamp() if since else end - self.settings.operations_retention_seconds
        start = max(start, time.time() - self.settings.operations_retention_seconds)
        if start > end:
            raise BadRequest("since must precede until")
        limit = min(limit, self.settings.operations_max_points)
        with self.connect() as db:
            count = db.execute(
                "SELECT count(*) FROM samples WHERE at BETWEEN ? AND ?", (start, end)
            ).fetchone()[0]
            indexes = [round(i * (count - 1) / (limit - 1)) for i in range(limit)] if count > limit else []
            rows = db.execute(
                "SELECT at,instance,document FROM (SELECT at,instance,document, "
                "row_number() OVER (ORDER BY at,sample_id)-1 AS idx FROM samples WHERE at BETWEEN ? AND ?) "
                "WHERE (? = 0 OR idx IN (SELECT value FROM json_each(?))) ORDER BY at LIMIT ?",
                (start, end, len(indexes), json.dumps(indexes), limit),
            ).fetchall()
        return {
            "service": self.settings.service_name,
            "instance_id": self.settings.instance_id,
            "sample_interval_seconds": self.settings.operations_sample_interval_seconds,
            "resolution_seconds": self.settings.operations_sample_interval_seconds
            * (max(1, math.ceil((count - 1) / (limit - 1))) if count else 1),
            "retention_seconds": self.settings.operations_retention_seconds,
            "metrics": self.definitions(),
            "samples": [
                {
                    "at": datetime.fromtimestamp(row["at"], UTC).isoformat().replace("+00:00", "Z"),
                    "instance_id": row["instance"],
                    "values": json.loads(row["document"]),
                }
                for row in rows
            ],
        }


def install_operations(app: FastAPI, settings: Any, resolved: Any) -> Operations:
    operations = Operations(app, settings, resolved)

    @app.get(
        "/v1/configuration",
        tags=["operations"],
        operation_id="getModuleConfiguration",
        dependencies=[Depends(require("modules:read", "modules:write"))],
    )
    async def get_configuration() -> JSONResponse:
        doc, etag = await run_in_threadpool(operations.configuration)
        return JSONResponse(doc, headers={"ETag": etag, "Cache-Control": "no-store"})

    @app.put(
        "/v1/configuration",
        tags=["operations"],
        operation_id="putModuleConfiguration",
        dependencies=[Depends(require("modules:write"))],
    )
    async def put_configuration(body: ConfigurationUpdate, request: Request) -> JSONResponse:
        principal = getattr(request.state, "principal", None)
        actor = getattr(principal, "name", "local")
        doc, etag = await run_in_threadpool(
            operations.save, body.values, request.headers.get("If-Match"), actor
        )
        return JSONResponse(doc, headers={"ETag": etag, "Cache-Control": "no-store"})

    @app.get(
        "/v1/telemetry",
        tags=["operations"],
        operation_id="getModuleTelemetry",
        dependencies=[Depends(require("modules:read", "modules:write"))],
    )
    async def get_telemetry(
        since: datetime | None = None, until: datetime | None = None, limit: int = Query(default=600, ge=2)
    ) -> dict[str, Any]:
        return await run_in_threadpool(operations.telemetry, since, until, limit)

    return operations
