"""Helpers that build :class:`~jane_extractor_sdk.types.ExtractResult` values (the four states of TZ §9).

``success`` / ``empty`` / ``unrecognized`` are returned; ``failed`` happens when the callable raises.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Literal

from .types import Diagnostic, EntityKey, EntityOut, ExtractResult, Unrecognized

__all__ = ["empty", "entity", "success", "unrecognized"]


def entity(
    entity_type: str,
    fields: Mapping[str, Any],
    *,
    key: EntityKey | None = None,
    cleared: Iterable[str] | None = None,
    completeness: Literal["full", "partial"] | None = None,
    confidence: float | None = None,
) -> EntityOut:
    """One entity. Fields whose value is ``None`` are dropped: a value that is absent from the material is
    *not* sent (a missing field never means "delete it"); explicit clearing goes to ``cleared``.

    ``key`` may be omitted: the runtime builds it from ``key_fields`` of the package output contract and the
    material's ``source.source_id`` (``"local"`` in standalone runs).
    """
    out: EntityOut = {
        "entity_type": entity_type,
        "fields": {k: v for k, v in fields.items() if v is not None},
    }
    if key is not None:
        out["key"] = key
    if cleared:
        out["cleared"] = sorted(set(cleared))
    if completeness is not None:
        out["completeness"] = completeness
    if confidence is not None:
        out["confidence"] = confidence
    return out


def _with_diagnostics(result: ExtractResult, diagnostics: Iterable[Diagnostic] | None) -> ExtractResult:
    diags = list(diagnostics or [])
    if diags:
        result["diagnostics"] = diags
    return result


def success(
    entities: Iterable[EntityOut] | None = None,
    *,
    data: Any = None,
    diagnostics: Iterable[Diagnostic] | None = None,
) -> ExtractResult:
    """Successful processing: entities (extractor) and/or ``data`` (transform)."""
    result: ExtractResult = {"status": "success", "entities": list(entities or [])}
    if data is not None:
        result["data"] = data
    return _with_diagnostics(result, diagnostics)


def empty(*, diagnostics: Iterable[Diagnostic] | None = None) -> ExtractResult:
    """The material is understood and correctly contains none of the requested entities."""
    return _with_diagnostics({"status": "empty", "entities": []}, diagnostics)


def unrecognized(
    reason: str,
    *,
    signature: str | None = None,
    entities: Iterable[EntityOut] | None = None,
    diagnostics: Iterable[Diagnostic] | None = None,
) -> ExtractResult:
    """Unknown or partially parsed format. Entities parsed so far (if any) make it ``partial``.

    ``signature`` is a short fingerprint of the problem used to group problem samples
    (e.g. ``"missing-selector:.price"``).
    """
    found = list(entities or [])
    info: Unrecognized = {"partial": bool(found), "reason": reason}
    if signature:
        info["signature"] = signature
    return _with_diagnostics({"status": "unrecognized", "entities": found, "unrecognized": info}, diagnostics)
