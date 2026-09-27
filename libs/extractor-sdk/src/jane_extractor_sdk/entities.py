"""Turning extractor entities into ``EntityRecord`` documents (shared by the runtime and local test runs)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

__all__ = ["DEFAULT_SCOPE", "build_key", "observation_of", "to_entity_record"]

DEFAULT_SCOPE = "local"
"""Key scope when the material has no ``source.source_id`` (standalone run)."""


def observation_of(material: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """``ObservationOrder`` of a material: observed_at = fetched_at, sequence = revision.sequence."""
    if not material or "observation_id" not in material or "fetched_at" not in material:
        return None
    obs: dict[str, Any] = {
        "observation_id": material["observation_id"],
        "observed_at": material["fetched_at"],
    }
    revision = material.get("revision") or {}
    if isinstance(revision.get("sequence"), int):
        obs["sequence"] = revision["sequence"]
    if material.get("material_id"):
        obs["material_id"] = material["material_id"]
    if revision.get("content_sha256"):
        obs["content_sha256"] = revision["content_sha256"]
    return obs


def build_key(fields: Mapping[str, Any], key_fields: Sequence[str], scope: str) -> dict[str, Any] | None:
    """``EntityKey`` from ``key_fields``; ``None`` if a key field is missing or not a scalar."""
    natural: dict[str, Any] = {}
    for name in key_fields:
        value = fields.get(name)
        if not isinstance(value, str | int | float | bool):
            return None
        natural[name] = value
    return {"scope": scope, "natural": natural} if natural else None


def to_entity_record(
    raw: Mapping[str, Any],
    *,
    key_fields: Sequence[str],
    material: Mapping[str, Any] | None,
    schema_ref: str | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Add what the runtime owns: ``key`` (if missing), ``observation``, ``schema``, ``provenance``."""
    record = dict(raw)
    source = (material or {}).get("source") or {}
    scope = str(source.get("source_id") or DEFAULT_SCOPE)
    if "key" not in record and isinstance(record.get("fields"), Mapping):
        key = build_key(record["fields"], key_fields, scope)
        if key is not None:
            record["key"] = key
    obs = observation_of(material)
    if obs is not None:
        record["observation"] = obs
    if schema_ref:
        record["schema"] = schema_ref
    if provenance:
        record["provenance"] = dict(provenance)
    return record
