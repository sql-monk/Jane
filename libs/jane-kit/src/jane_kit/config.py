"""Service settings and limits inherited across levels: platform -> source -> task -> stage (-> request).

Follows ``contracts/schemas/common/limits.schema.json`` (WP-00):

* Every numeric limit lives in a :class:`Limits` model of the service and **must** declare a safe
  default there (those defaults are the service's platform defaults); code never hard-codes a limit.
* A layer overrides any subset of fields (deep merge); a missing field is inherited; ``null`` is not
  a value (to inherit, omit the field).
* ``hard_caps`` (platform level; a more specific layer may only tighten them) bound every value after
  merging: effective = min(value, hard cap).
* The result keeps the provenance of every leaf (``EffectiveLimits`` in the contract).

Files: a platform file has the ``PlatformLimits`` shape ``{"profile", "defaults", "hard_caps"}``
(TOML/JSON/YAML); other levels are plain Limits objects. Environment variables:
``<PREFIX>CRAWL__MAX_DEPTH=5`` (value), ``<PREFIX>HARD_CAPS__CRAWL__MAX_DEPTH=10`` (hard cap).

A platform file is one profile shared by all services (ТЗ §12, criterion 13), so its layer is
``shared``: a path of the contract (:data:`CONTRACT_LIMIT_PATHS`) goes to the model fields that declare it
(:func:`contract_field`, or a field at the same path), a contract path no field declares is ignored and
recorded in :attr:`ResolvedLimits.ignored`, and a path unknown to both the model and the contract (a typo)
is still a :class:`LimitError`. Other layers (env, source, task, request) accept model paths only.
"""

from __future__ import annotations

import functools
import json
import os
import socket
import tomllib
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from jane_kit.auth import AuthSettings

__all__ = [
    "CONTRACT_LIMIT_PATHS",
    "LEVELS",
    "JaneSettings",
    "LimitError",
    "LimitLayer",
    "Limits",
    "ResolvedLimits",
    "contract_field",
    "layer_from_env",
    "load_layer",
    "resolve_limits",
]

LEVELS: tuple[str, ...] = ("platform", "source", "task", "stage", "request")
"""Levels of ``LimitLevel`` in the contract, least specific first (plus ``hard_cap`` in provenance)."""

_CONTRACT_LIMITS: dict[str, tuple[str, ...]] = {
    "concurrency": (
        "max_parallel_fetches",
        "max_parallel_fetches_per_host",
        "max_parallel_invocations",
        "max_parallel_runs_per_task",
        "max_parallel_stage_items",
    ),
    "rate": (
        "requests_per_second_per_host",
        "min_delay_ms_per_host",
        "burst_per_host",
        "respect_crawl_delay",
    ),
    "crawl": (
        "max_depth",
        "max_pages_per_run",
        "max_bytes_per_run",
        "max_material_bytes",
        "max_redirects",
        "max_links_per_page",
        "max_seed_urls",
        "max_frontier_size",
        "revisit_interval_seconds",
    ),
    "timeouts": (
        "connect_timeout_ms",
        "request_timeout_ms",
        "invocation_timeout_ms",
        "stage_timeout_ms",
        "run_timeout_ms",
        "sync_response_max_ms",
    ),
    "retries": ("max_attempts", "initial_backoff_ms", "max_backoff_ms", "backoff_multiplier", "jitter"),
    "queue": ("max_queue_depth", "max_inflight_materials", "max_unacked_materials"),
    "sandbox": ("cpu_cores", "memory_mb", "wall_time_ms", "max_output_bytes", "max_processes", "tmpfs_mb"),
    "llm": (
        "max_requests_per_minute",
        "max_input_tokens_per_request",
        "max_output_tokens_per_request",
        "budget.amount",
        "budget.currency",
        "budget.period",
        "max_improvement_attempts",
        "max_onboarding_samples",
    ),
    "transfer": (
        "inline_max_bytes",
        "max_request_body_bytes",
        "transit_ttl_seconds",
        "download_url_ttl_seconds",
        "job_retention_seconds",
        "idempotency_ttl_seconds",
    ),
    "telegram": ("max_messages_per_run", "max_media_bytes", "max_flood_wait_seconds"),
}

CONTRACT_LIMIT_PATHS: frozenset[str] = frozenset(
    f"{group}.{name}" for group, names in _CONTRACT_LIMITS.items() for name in names
)
"""Leaf paths of ``limits.schema.json`` (``Limits``). A copy, because services run without ``contracts/``;
``tests/test_wp00_contracts.py`` keeps it equal to the schema."""


class LimitError(ValueError):
    """Invalid limit configuration (unknown field, wrong type, loosened hard cap)."""


class Limits(BaseModel):
    """Base class for a service's limits. Subclasses must give every field a default.

    Use the field names of ``limits.schema.json`` where the limit exists there
    (``timeouts.request_timeout_ms``, ``transfer.idempotency_ttl_seconds``...). Nested groups are
    fields whose type is another :class:`Limits` subclass with a default instance.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        missing = [name for name, f in cls.model_fields.items() if f.is_required()]
        if missing:
            raise TypeError(
                f"{cls.__name__}: every limit needs a documented safe default; missing for {missing}"
            )


@dataclass(frozen=True)
class LimitLayer:
    """One level of configuration (platform, source ``shop``, task ``prices``, stage ``extract``...)."""

    level: str
    values: Mapping[str, Any] = field(default_factory=dict)
    hard_caps: Mapping[str, Any] = field(default_factory=dict)
    name: str | None = None  # e.g. source id or file name, for diagnostics
    profile: str | None = None  # PlatformLimits.profile of a platform file
    shared: bool = False
    """Contract-shaped document shared by all services (a platform file): contract paths map to the fields
    that declare them, contract paths the model does not declare are ignored (``ResolvedLimits.ignored``).
    Paths unknown to the contract and to the model are still rejected."""

    @property
    def label(self) -> str:
        return f"{self.level}:{self.name}" if self.name else self.level


@dataclass(frozen=True)
class ResolvedLimits[L: Limits]:
    limits: L
    origin: dict[str, str]
    """Dotted leaf path -> label of the layer that set it (``default`` = the model's default)."""
    clamped: dict[str, str]
    """Dotted leaf path -> label of the layer whose hard cap reduced the value."""
    hard_caps: dict[str, Any] = field(default_factory=dict)
    """Dotted leaf path -> effective hard cap (the tightest one of all layers)."""
    profile: str | None = None
    """Name of the platform limits profile, if a PlatformLimits file declared one."""
    ignored: dict[str, str] = field(default_factory=dict)
    """Contract path -> label of the shared layer whose value was not applied: this service has no such limit."""
    ignored_hard_caps: dict[str, str] = field(default_factory=dict)
    """Same for ``hard_caps`` of shared layers."""

    def platform_limits(self) -> dict[str, Any]:
        """``PlatformLimits`` document for ``/v1/info`` (WP-00 ``ServiceInfo.limits``).

        Only fields that map to ``limits.schema.json`` (declared with :func:`contract_field` or nested
        under a group with a contract path) are included; service-specific limits stay internal because
        the contract schema is strict (``additionalProperties: false``).
        """
        mapping = _contract_paths(type(self.limits))
        flat = _flatten(self.limits.model_dump(mode="json"))
        defaults = {mapping[p]: v for p, v in flat.items() if p in mapping}
        caps = {mapping[p]: v for p, v in self.hard_caps.items() if p in mapping}
        doc: dict[str, Any] = {"defaults": _unflatten(defaults)}
        if caps:
            doc["hard_caps"] = _unflatten(caps)
        if self.profile:
            doc["profile"] = self.profile
        return doc

    def provenance(self) -> dict[str, str]:
        """Leaf path -> contract ``LimitLevel`` (model defaults count as ``platform``)."""
        out = {}
        for path in _flatten(self.limits.model_dump()):
            if path in self.clamped:
                out[path] = "hard_cap"
            else:
                out[path] = self.origin.get(path, "platform:default").split(":", 1)[0]
                if out[path] == "default":
                    out[path] = "platform"
        return out

    def effective(self) -> dict[str, Any]:
        """``EffectiveLimits`` document: ``{"limits": {...}, "provenance": {...}}``."""
        return {"limits": self.limits.model_dump(mode="json"), "provenance": self.provenance()}

    def explain(self) -> list[tuple[str, Any, str]]:
        """Rows ``(path, value, origin)`` for logs and diagnostics."""
        flat = _flatten(self.limits.model_dump())
        rows = []
        for path in sorted(flat):
            origin = self.origin.get(path, "default")
            if path in self.clamped:
                origin = f"{origin} (hard cap from {self.clamped[path]})"
            rows.append((path, flat[path], origin))
        return rows


def _flatten(data: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}{key}"
        if isinstance(value, Mapping):
            out.update(_flatten(value, f"{path}."))
        else:
            out[path] = value
    return out


def _unflatten(flat: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for path, value in flat.items():
        node = out
        *parents, leaf = path.split(".")
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = value
    return out


CONTRACT_KEY = "contract"


def contract_field(path: str, default: Any, **kwargs: Any) -> Any:
    """``Field`` for a limit that exists in ``limits.schema.json`` under dotted ``path``
    (e.g. ``"transfer.idempotency_ttl_seconds"``). For a nested group, ``path`` is the group
    (``"retries"``) and its fields map to ``retries.<name>``."""
    extra = dict(kwargs.pop("json_schema_extra", None) or {})
    extra[CONTRACT_KEY] = path
    return Field(default=default, json_schema_extra=extra, **kwargs)


def _contract_paths(model: type[BaseModel], prefix: str = "", group: str | None = None) -> dict[str, str]:
    """Model leaf path -> contract path for fields that have one."""
    out: dict[str, str] = {}
    for name, info in model.model_fields.items():
        extra = info.json_schema_extra if isinstance(info.json_schema_extra, dict) else {}
        own = extra.get(CONTRACT_KEY)
        contract = str(own) if own else (f"{group}.{name}" if group else None)
        ann = info.annotation
        if isinstance(ann, type) and issubclass(ann, BaseModel):
            out.update(_contract_paths(ann, f"{prefix}{name}.", contract))
        elif contract:
            out[f"{prefix}{name}"] = contract
    return out


def _field_paths(model: type[BaseModel], prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for name, info in model.model_fields.items():
        ann = info.annotation
        if isinstance(ann, type) and issubclass(ann, BaseModel):
            paths |= _field_paths(ann, f"{prefix}{name}.")
        else:
            paths.add(f"{prefix}{name}")
    return paths


@functools.cache
def _shared_targets(model: type[BaseModel]) -> dict[str, tuple[str, ...]]:
    """Contract path -> model leaves a shared layer sets with it: the fields that declare the path
    (:func:`contract_field`) and an undeclared field at the same path."""
    declared = _contract_paths(model)
    out: dict[str, list[str]] = {}
    for leaf, contract in declared.items():
        out.setdefault(contract, []).append(leaf)
    for leaf in sorted(_field_paths(model) - declared.keys()):
        if leaf in CONTRACT_LIMIT_PATHS:
            out.setdefault(leaf, []).append(leaf)
    return {path: tuple(leaves) for path, leaves in out.items()}


def _fit_shared(
    flat: Mapping[str, Any], targets: Mapping[str, tuple[str, ...]], label: str
) -> tuple[dict[str, Any], list[str]]:
    """Leaf paths of a shared layer -> model paths; returns ``(values, ignored contract paths)``.

    A contract path sets every field that declares it, or is ignored when none does; any other path is
    taken as a model path (an unknown one is then rejected by the caller)."""
    out: dict[str, Any] = {}
    source: dict[str, str] = {}
    ignored: list[str] = []
    for path, value in flat.items():
        if path in CONTRACT_LIMIT_PATHS:
            leaves = targets.get(path, ())
            if not leaves:
                ignored.append(path)
        else:
            leaves = (path,)
        for leaf in leaves:
            if leaf in out and out[leaf] != value:
                raise LimitError(
                    f"{label}: {leaf} is set twice: {source[leaf]}={out[leaf]!r} and {path}={value!r}"
                )
            out[leaf] = value
            source[leaf] = path
    return out, ignored


def _reject_nulls(label: str, *flats: Mapping[str, Any]) -> None:
    nulls = sorted({p for flat in flats for p, v in flat.items() if v is None})
    if nulls:
        raise LimitError(f"{label}: null is not a limit value (omit the field to inherit): {nulls}")


def _gt(a: Any, b: Any) -> bool:
    try:
        return bool(a > b)
    except TypeError as exc:
        raise LimitError(f"hard cap {b!r} is not comparable with value {a!r}") from exc


def resolve_limits[L: Limits](
    model: type[L],
    *layers: LimitLayer,
    on_exceed: Literal["clamp", "error"] = "clamp",
) -> ResolvedLimits[L]:
    """Merge ``layers`` (least specific first) over the defaults of ``model`` and apply hard caps.

    ``on_exceed='clamp'`` lowers a value above a hard cap to the cap (recorded in ``clamped``,
    provenance ``hard_cap``); ``'error'`` raises :class:`LimitError` instead (useful to reject a
    request that asks for more than allowed with ``limit_exceeded``).

    A ``shared`` layer (platform file) may carry limits of other services: see :attr:`LimitLayer.shared`;
    what it set but this model lacks is listed in ``ignored`` / ``ignored_hard_caps`` of the result.
    """
    known = _field_paths(model)
    merged: dict[str, Any] = {}
    origin: dict[str, str] = {}
    caps: dict[str, tuple[Any, str]] = {}
    ignored: dict[str, str] = {}
    ignored_caps: dict[str, str] = {}

    for layer in layers:
        values = _flatten(layer.values)
        layer_caps = _flatten(layer.hard_caps)
        if layer.shared:
            _reject_nulls(layer.label, values, layer_caps)  # also in limits this service ignores
            targets = _shared_targets(model)
            values, skipped = _fit_shared(values, targets, layer.label)
            ignored.update(dict.fromkeys(skipped, layer.label))
            layer_caps, skipped = _fit_shared(layer_caps, targets, layer.label)
            ignored_caps.update(dict.fromkeys(skipped, layer.label))
        unknown = (set(values) | set(layer_caps)) - known
        if unknown:
            hint = " (not in limits.schema.json either)" if layer.shared else ""
            raise LimitError(f"{layer.label}: unknown limit(s) {sorted(unknown)} for {model.__name__}{hint}")
        _reject_nulls(layer.label, values, layer_caps)
        if layer_caps:  # coerce to declared types ("4" from env -> 4)
            try:
                typed = _flatten(model.model_validate(_unflatten(layer_caps)).model_dump())
            except ValidationError as exc:
                raise LimitError(f"{layer.label}: invalid hard_caps for {model.__name__}: {exc}") from exc
            for path in layer_caps:
                cap = typed[path]
                if path in caps and _gt(cap, caps[path][0]):
                    raise LimitError(
                        f"{layer.label}: hard cap {path}={cap!r} loosens {caps[path][0]!r} from {caps[path][1]}"
                    )
                caps[path] = (cap, layer.label)
        for path, value in values.items():
            merged[path] = value
            origin[path] = layer.label

    try:
        limits = model.model_validate(_unflatten(merged))
    except ValidationError as exc:
        raise LimitError(f"invalid limits for {model.__name__}: {exc}") from exc

    clamped: dict[str, str] = {}
    flat = _flatten(limits.model_dump())
    for path, (cap, label) in caps.items():
        value = flat.get(path)
        if value is not None and _gt(value, cap):
            if on_exceed == "error":
                raise LimitError(
                    f"{path}={value!r} (from {origin.get(path, 'default')}) exceeds hard cap {cap!r} from {label}"
                )
            flat[path] = cap
            clamped[path] = label
    if clamped:
        limits = model.model_validate(_unflatten(flat))
    profile = next((layer.profile for layer in reversed(layers) if layer.profile), None)
    return ResolvedLimits(
        limits=limits,
        origin=origin,
        clamped=clamped,
        hard_caps={p: c for p, (c, _) in caps.items()},
        profile=profile,
        ignored=ignored,
        ignored_hard_caps=ignored_caps,
    )


def _read_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".toml":
        data: Any = tomllib.loads(text)
    elif suffix == ".json":
        data = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(text) or {}
    else:
        raise LimitError(f"unsupported limits file format: {path}")
    if not isinstance(data, dict):
        raise LimitError(f"{path}: top level must be a mapping")
    return data


def load_layer(path: str | Path, level: str = "platform", *, name: str | None = None) -> LimitLayer:
    """Read a layer file. ``level='platform'`` expects ``PlatformLimits`` (``defaults``/``hard_caps``/``profile``)
    and gives a ``shared`` layer (one profile for every service); other levels expect a plain Limits object."""
    data = _read_mapping(Path(path))
    if level != "platform":
        return LimitLayer(level=level, values=data, name=name)
    extra = set(data) - {"profile", "defaults", "hard_caps"}
    if extra:
        raise LimitError(
            f"{path}: unexpected top-level keys {sorted(extra)}; PlatformLimits has profile/defaults/hard_caps"
        )
    return LimitLayer(
        level="platform",
        values=data.get("defaults") or {},
        hard_caps=data.get("hard_caps") or {},
        name=name or data.get("profile"),
        profile=data.get("profile"),
        shared=True,
    )


def layer_from_env(
    prefix: str = "JANE_LIMITS__",
    level: str = "platform",
    environ: Mapping[str, str] | None = None,
) -> LimitLayer:
    """Layer from environment variables; ``__`` separates nesting, ``HARD_CAPS__`` marks a hard cap.

    Values stay strings; pydantic coerces them to the declared types.
    """
    env = os.environ if environ is None else environ
    values: dict[str, Any] = {}
    caps: dict[str, Any] = {}
    for key, raw in env.items():
        if not key.upper().startswith(prefix.upper()):
            continue
        parts = [p.lower() for p in key[len(prefix) :].split("__") if p]
        target = values
        if parts[:1] == ["hard_caps"]:
            target, parts = caps, parts[1:]
        if parts:
            target[".".join(parts)] = raw
    return LimitLayer(level=level, values=_unflatten(values), hard_caps=_unflatten(caps), name="env")


class JaneSettings(BaseSettings, AuthSettings):
    """Common process settings. A service subclasses it and sets its own ``env_prefix``.

    Only process-level knobs live here; operational limits belong in a :class:`Limits` model.
    Authentication fields (``auth_mode``, ``api_keys``, ``jwt_*``...) come from
    :class:`jane_kit.auth.AuthSettings` (ADR-0005); ``create_app`` enforces them.
    """

    model_config = SettingsConfigDict(env_prefix="JANE_", extra="ignore", env_nested_delimiter="__")

    service_name: str = "jane-service"
    instance_id: str = Field(
        default_factory=lambda: f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex}"
    )
    """Unique to this process start, including a restart that reuses the container hostname and PID."""
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"
    metrics_enabled: bool = True
    health_check_timeout_ms: int = Field(default=2_000, ge=1)
    """Time box of every ``/v1/health`` check (env ``<PREFIX>HEALTH_CHECK_TIMEOUT_MS``)."""
    limits_file: Path | None = None
    """Platform limits file (``PlatformLimits`` shape, e.g. a whole ``deploy/profiles/<profile>.json``: limits
    this service does not have are ignored, typos are errors); env ``<PREFIX>LIMITS__*`` overrides it."""

    def platform_layers(self, env_prefix: str = "JANE_LIMITS__") -> list[LimitLayer]:
        """Platform layers in order: limits file, then environment overrides."""
        layers = []
        if self.limits_file is not None:
            layers.append(load_layer(self.limits_file, "platform", name=str(self.limits_file)))
        env_layer = layer_from_env(env_prefix, level="platform")
        if env_layer.values or env_layer.hard_caps:
            layers.append(env_layer)
        return layers

    def with_overrides(self, **values: Any) -> Self:
        return self.model_copy(update=values)
