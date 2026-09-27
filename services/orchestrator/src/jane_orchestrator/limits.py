"""Effective limits (``limits.schema.json``): platform → source → task → stage → request, with hard caps.

jane-kit's :func:`~jane_kit.config.resolve_limits` merges into a static model with a default for every
field. The orchestrator merges *contract documents* whose fields are set by users at any level (crawl,
sandbox, llm… — values it only forwards to executors), so it merges JSON documents here with the same
rules: deep merge, lower level overrides, ``null`` is never a value, numeric leaves are capped by the
platform ``hard_caps`` (provenance ``hard_cap``). Fields the orchestrator consumes itself fall back to
:class:`~jane_orchestrator.settings.ContractDefaults` (provenance ``platform``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Effective", "LimitsLayer", "flatten", "merge_limits", "unflatten"]


def flatten(data: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}{key}"
        if isinstance(value, Mapping):
            out.update(flatten(value, f"{path}."))
        else:
            out[path] = value
    return out


def unflatten(flat: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for path, value in flat.items():
        node = out
        *parents, leaf = path.split(".")
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = value
    return out


# Groups that are atomic objects in the contract (all-or-nothing): llm.budget has required fields.
_ATOMIC = ("llm.budget",)


def _flatten_limits(doc: Mapping[str, Any]) -> dict[str, Any]:
    flat = flatten(doc)
    for group in _ATOMIC:
        keys = [k for k in flat if k.startswith(group + ".")]
        if keys:
            flat[group] = {k[len(group) + 1 :]: flat.pop(k) for k in keys}
    return flat


@dataclass(frozen=True)
class LimitsLayer:
    level: str  # platform | source | task | stage | request
    values: Mapping[str, Any]


@dataclass
class Effective:
    limits: dict[str, Any]
    provenance: dict[str, str]
    flat: dict[str, Any] = field(default_factory=dict)

    def doc(self) -> dict[str, Any]:
        """``EffectiveLimits`` document."""
        return {"limits": self.limits, "provenance": self.provenance}

    def get(self, path: str, default: Any = None) -> Any:
        return self.flat.get(path, default)


def _is_number(v: Any) -> bool:
    return isinstance(v, int | float) and not isinstance(v, bool)


def merge_limits(
    fallback: Mapping[str, Any],
    layers: Sequence[LimitsLayer],
    hard_caps: Mapping[str, Any] | None = None,
) -> Effective:
    """Merge ``fallback`` (code defaults, level platform) and ``layers`` (least specific first)."""
    flat: dict[str, Any] = {}
    prov: dict[str, str] = {}
    for path, value in _flatten_limits(fallback).items():
        flat[path] = value
        prov[path] = "platform"
    for layer in layers:
        for path, value in _flatten_limits(layer.values or {}).items():
            if value is None:
                continue
            flat[path] = value
            prov[path] = layer.level
    for path, cap in _flatten_limits(hard_caps or {}).items():
        value = flat.get(path)
        if _is_number(value) and _is_number(cap) and value > cap:
            flat[path] = cap
            prov[path] = "hard_cap"
    return Effective(limits=unflatten(flat), provenance=dict(sorted(prov.items())), flat=flat)
