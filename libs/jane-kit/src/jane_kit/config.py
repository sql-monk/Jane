"""Service settings and limits inherited across levels: defaults -> platform -> source -> job.

Rules (plan.md §3.6, TZ §13.1.5):

* Every numeric limit lives in a :class:`Limits` model and **must** declare a safe default there;
  code never hard-codes a limit, it reads the resolved model.
* A layer (platform, source, job) overrides any subset of fields. Missing fields are inherited.
* A layer may also declare *ceilings*: upper bounds that later (more specific) layers cannot
  exceed. A job cannot raise its concurrency above the platform ceiling, for example.
* The result remembers where every value came from (``origin``) for diagnostics.

Layers can be read from TOML/JSON/YAML files (``limits`` and ``ceilings`` tables) and from
environment variables (``JANE_LIMITS__HTTP__TIMEOUT_S=5`` -> ``{"http": {"timeout_s": "5"}}``).
"""

from __future__ import annotations

import json
import os
import socket
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "LEVELS",
    "JaneSettings",
    "LimitError",
    "LimitLayer",
    "Limits",
    "ResolvedLimits",
    "layer_from_env",
    "load_layer",
    "resolve_limits",
]

LEVELS: tuple[str, ...] = ("default", "platform", "source", "job")
"""Canonical inheritance order. Custom level names are allowed, order is the call order."""


class LimitError(ValueError):
    """Invalid limit configuration (unknown field, wrong type, bad ceiling)."""


class Limits(BaseModel):
    """Base class for a service's limits. Subclasses must give every field a default.

    Nested groups are allowed: declare a field whose type is another :class:`Limits` subclass
    with a default instance (``http: HttpLimits = HttpLimits()``).
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
    """One level of configuration (e.g. platform, source ``shop.example``, job ``prices``)."""

    level: str
    values: Mapping[str, Any] = field(default_factory=dict)
    ceilings: Mapping[str, Any] = field(default_factory=dict)
    name: str | None = None  # optional identifier, e.g. source id, for diagnostics

    @property
    def label(self) -> str:
        return f"{self.level}:{self.name}" if self.name else self.level


@dataclass(frozen=True)
class ResolvedLimits[L: Limits]:
    limits: L
    origin: dict[str, str]
    """Dotted field path -> label of the layer that set the value (``default`` if inherited)."""
    clamped: dict[str, str]
    """Dotted field path -> label of the layer whose ceiling reduced the value."""

    def explain(self) -> list[tuple[str, Any, str]]:
        """Rows ``(path, value, origin)`` for logs and diagnostics endpoints."""
        flat = _flatten(self.limits.model_dump())
        rows = []
        for path in sorted(flat):
            origin = self.origin.get(path, "default")
            if path in self.clamped:
                origin = f"{origin} (clamped by {self.clamped[path]})"
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


def _field_paths(model: type[BaseModel], prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for name, info in model.model_fields.items():
        ann = info.annotation
        if isinstance(ann, type) and issubclass(ann, BaseModel):
            paths |= _field_paths(ann, f"{prefix}{name}.")
        else:
            paths.add(f"{prefix}{name}")
    return paths


def resolve_limits[L: Limits](
    model: type[L],
    *layers: LimitLayer,
    on_exceed: Literal["clamp", "error"] = "clamp",
) -> ResolvedLimits[L]:
    """Merge ``layers`` (least specific first) over the defaults of ``model``.

    ``on_exceed='clamp'`` lowers a value above an inherited ceiling to the ceiling and records it
    in ``clamped``; ``'error'`` raises :class:`LimitError` instead.
    """
    known = _field_paths(model)
    merged: dict[str, Any] = {}
    origin: dict[str, str] = {}
    ceilings: dict[str, tuple[Any, str]] = {}

    for layer in layers:
        values = _flatten(layer.values)
        caps = _flatten(layer.ceilings)
        unknown = (set(values) | set(caps)) - known
        if unknown:
            raise LimitError(f"{layer.label}: unknown limit(s) {sorted(unknown)} for {model.__name__}")
        if caps:  # coerce ceilings to the declared field types ("4" from env -> 4)
            try:
                typed = _flatten(model.model_validate(_unflatten(caps)).model_dump())
            except ValidationError as exc:
                raise LimitError(f"{layer.label}: invalid ceilings for {model.__name__}: {exc}") from exc
            caps = {path: typed[path] for path in caps}
        for path, cap in caps.items():
            if path in ceilings:
                prev, prev_label = ceilings[path]
                # A more specific layer may tighten a ceiling but never loosen it.
                if _gt(cap, prev):
                    raise LimitError(
                        f"{layer.label}: ceiling {path}={cap!r} exceeds ceiling {prev!r} from {prev_label}"
                    )
            ceilings[path] = (cap, layer.label)
        for path, value in values.items():
            merged[path] = value
            origin[path] = layer.label

    try:
        limits = model.model_validate(_unflatten(merged))
    except ValidationError as exc:
        raise LimitError(f"invalid limits for {model.__name__}: {exc}") from exc

    clamped: dict[str, str] = {}
    flat = _flatten(limits.model_dump())
    for path, (cap, label) in ceilings.items():
        value = flat.get(path)
        if value is not None and _gt(value, cap):
            if on_exceed == "error":
                raise LimitError(
                    f"{path}={value!r} (from {origin.get(path, 'default')}) exceeds ceiling {cap!r} "
                    f"from {label}"
                )
            flat[path] = cap
            clamped[path] = label
    if clamped:
        try:
            limits = model.model_validate(_unflatten(flat))
        except ValidationError as exc:
            raise LimitError(f"ceiling makes limits invalid for {model.__name__}: {exc}") from exc
    return ResolvedLimits(limits=limits, origin=origin, clamped=clamped)


def _gt(a: Any, b: Any) -> bool:
    try:
        return bool(a > b)
    except TypeError as exc:
        raise LimitError(f"ceiling {b!r} is not comparable with value {a!r}") from exc


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


def load_layer(path: str | Path, level: str, *, name: str | None = None) -> LimitLayer:
    """Read a layer file with optional ``limits`` and ``ceilings`` tables."""
    data = _read_mapping(Path(path))
    extra = set(data) - {"limits", "ceilings"}
    if extra:
        raise LimitError(f"{path}: unexpected top-level keys {sorted(extra)}; use 'limits' and 'ceilings'")
    return LimitLayer(
        level=level, values=data.get("limits") or {}, ceilings=data.get("ceilings") or {}, name=name
    )


def layer_from_env(
    prefix: str = "JANE_LIMITS__",
    level: str = "platform",
    environ: Mapping[str, str] | None = None,
) -> LimitLayer:
    """Layer from environment variables. ``__`` separates nesting; ``CEILING__`` marks a ceiling.

    ``JANE_LIMITS__MAX_DEPTH=5`` -> value; ``JANE_LIMITS__CEILING__MAX_DEPTH=10`` -> ceiling.
    Values stay strings; pydantic coerces them to the declared types.
    """
    env = os.environ if environ is None else environ
    values: dict[str, Any] = {}
    ceilings: dict[str, Any] = {}
    for key, raw in env.items():
        if not key.upper().startswith(prefix.upper()):
            continue
        parts = [p.lower() for p in key[len(prefix) :].split("__") if p]
        if not parts:
            continue
        target = values
        if parts[0] == "ceiling":
            target, parts = ceilings, parts[1:]
        if parts:
            target[".".join(parts)] = raw
    return LimitLayer(level=level, values=_unflatten(values), ceilings=_unflatten(ceilings), name="env")


class JaneSettings(BaseSettings):
    """Common process settings. A service subclasses it and sets its own ``env_prefix``.

    Only process-level knobs live here; operational limits belong in a :class:`Limits` model.
    """

    model_config = SettingsConfigDict(env_prefix="JANE_", extra="ignore", env_nested_delimiter="__")

    service_name: str = "jane-service"
    instance_id: str = f"{socket.gethostname()}-{os.getpid()}"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"
    metrics_enabled: bool = True
    limits_file: Path | None = None
    """Platform-level limits file (TOML/JSON/YAML); env ``JANE_LIMITS__*`` overrides it."""

    def platform_layers(self, env_prefix: str = "JANE_LIMITS__") -> list[LimitLayer]:
        """Platform layers in order: limits file, then environment overrides."""
        layers = []
        if self.limits_file is not None:
            layers.append(load_layer(self.limits_file, "platform", name=str(self.limits_file)))
        env_layer = layer_from_env(env_prefix, level="platform")
        if env_layer.values or env_layer.ceilings:
            layers.append(env_layer)
        return layers

    def with_overrides(self, **values: Any) -> Self:
        return self.model_copy(update=values)
