"""Types of the extractor protocol (what the ``entry.callable`` of a package receives and returns).

The callable has the signature ``extract(material, params, ctx) -> ExtractResult``:

* ``material`` - a ``Material`` document (``contracts/schemas/material.schema.json``); for ``entities`` or
  ``data`` inputs (transform packages) it is the ``HandlerInput`` object itself;
* ``params`` - stage parameters, already validated against ``params_schema`` of the package (defaults applied);
* ``ctx`` - :class:`jane_extractor_sdk.context.Context` (content access, diagnostics, test mode).

The runtime turns an :class:`ExtractResult` into a ``HandlerResult``: it validates entity fields against the
package schemas (``schema_mismatch`` -> ``failed``), fills ``key`` from ``key_fields`` when it is missing, and
adds ``observation``, ``provenance`` and ``schema``. ``failed`` is never returned by the callable: raising an
exception is the way to fail.
"""

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict

__all__ = [
    "Diagnostic",
    "DiagnosticLevel",
    "EntityKey",
    "EntityOut",
    "ExtractResult",
    "ExtractStatus",
    "Material",
    "Unrecognized",
]

ExtractStatus = Literal["success", "empty", "unrecognized"]
DiagnosticLevel = Literal["debug", "info", "warning", "error"]

Material = dict[str, Any]
"""A ``Material`` document as JSON (open object, see ``material.schema.json``)."""


class EntityKey(TypedDict):
    scope: str
    natural: dict[str, str | int | float | bool]


class EntityOut(TypedDict):
    """An entity as returned by an extractor (a subset of ``EntityRecord``)."""

    entity_type: str
    fields: dict[str, Any]
    key: NotRequired[EntityKey]
    cleared: NotRequired[list[str]]
    completeness: NotRequired[Literal["full", "partial"]]
    confidence: NotRequired[float]


class Unrecognized(TypedDict):
    partial: bool
    reason: NotRequired[str]
    signature: NotRequired[str]


class Diagnostic(TypedDict):
    level: DiagnosticLevel
    message: str
    code: NotRequired[str]
    pointer: NotRequired[str]
    selector: NotRequired[str]
    material_id: NotRequired[str]


class ExtractResult(TypedDict):
    status: ExtractStatus
    entities: NotRequired[list[EntityOut]]
    data: NotRequired[Any]
    unrecognized: NotRequired[Unrecognized]
    diagnostics: NotRequired[list[Diagnostic]]
