"""Semantic validation of ``TaskConfig`` beyond the JSON Schema (task-config.schema.json description):
exactly one ``collect`` stage, acyclic graph, every ``from`` refers to an existing stage, every handler
stage has an input; plus orchestrator checks (``select`` fits the upstream kind, regexes compile,
connections exist, the «unknown pages» flag warning)."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from jane_kit.errors import FieldError

__all__ = ["effective_forward_unknown", "stage_map", "topo_order", "validate_task"]


def stage_map(task: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["stage_id"]: s for s in task.get("stages", [])}


def topo_order(task: Mapping[str, Any]) -> list[str] | None:
    """Stage ids in topological order, or ``None`` if the graph has a cycle."""
    stages = stage_map(task)
    deps = {sid: {i["from"] for i in s.get("inputs", []) if i["from"] in stages} for sid, s in stages.items()}
    order: list[str] = []
    ready = [sid for sid, d in deps.items() if not d]
    remaining = {sid: set(d) for sid, d in deps.items()}
    while ready:
        sid = ready.pop(0)
        order.append(sid)
        for other, d in remaining.items():
            if sid in d:
                d.discard(sid)
                if not d and other not in order and other not in ready:
                    ready.append(other)
    return order if len(order) == len(stages) else None


def effective_forward_unknown(task: Mapping[str, Any], source: Mapping[str, Any] | None) -> bool:
    """«Передавати в LLM невідомі сторінки»: task value, else source value, else false."""
    if "forward_unknown_to_llm" in task:
        return bool(task["forward_unknown_to_llm"])
    return bool((source or {}).get("forward_unknown_to_llm", False))


def _patterns(bindings: Iterable[Mapping[str, Any]]) -> Iterable[tuple[int, int, Mapping[str, Any]]]:
    for bi, b in enumerate(bindings):
        for pi, p in enumerate(b.get("url_patterns") or []):
            yield bi, pi, p


def validate_task(
    task: Mapping[str, Any],
    source: Mapping[str, Any] | None,
    known_connections: set[str] | None = None,
) -> tuple[list[FieldError], list[FieldError]]:
    """``(errors, warnings)`` for a schema-valid TaskConfig."""
    errors: list[FieldError] = []
    warnings: list[FieldError] = []
    stages = task.get("stages", [])
    index = {s["stage_id"]: i for i, s in enumerate(stages)}
    if len(index) != len(stages):
        seen: set[str] = set()
        for i, s in enumerate(stages):
            if s["stage_id"] in seen:
                errors.append(
                    FieldError(
                        pointer=f"/stages/{i}/stage_id", code="duplicate", message="duplicate stage_id"
                    )
                )
            seen.add(s["stage_id"])
    collects = [i for i, s in enumerate(stages) if s["kind"] == "collect"]
    if len(collects) != 1:
        errors.append(
            FieldError(
                pointer="/stages",
                code="collect_stage_count",
                message=f"exactly one stage of kind 'collect' is required, got {len(collects)}",
            )
        )
    if source is None:
        errors.append(
            FieldError(pointer="/input/source_id", code="not_found", message="source does not exist")
        )
    for i, s in enumerate(stages):
        if s["kind"] != "handler":
            continue
        inputs = s.get("inputs") or []
        if not inputs:
            errors.append(
                FieldError(
                    pointer=f"/stages/{i}/inputs", code="no_inputs", message="handler stage needs an input"
                )
            )
        for j, edge in enumerate(inputs):
            src = edge["from"]
            if src not in index:
                errors.append(
                    FieldError(
                        pointer=f"/stages/{i}/inputs/{j}/from",
                        code="unknown_stage",
                        message=f"stage '{src}' does not exist",
                    )
                )
                continue
            if src == s["stage_id"]:
                errors.append(
                    FieldError(pointer=f"/stages/{i}/inputs/{j}/from", code="cycle", message="self-loop")
                )
            select = edge.get("select", "output")
            src_kind = stages[index[src]]["kind"]
            if select == "unmatched_materials" and src_kind != "collect":
                errors.append(
                    FieldError(
                        pointer=f"/stages/{i}/inputs/{j}/select",
                        code="invalid_select",
                        message="unmatched_materials can only be selected from the collect stage",
                    )
                )
            if select in {"problems", "input_material"} and src_kind == "collect":
                errors.append(
                    FieldError(
                        pointer=f"/stages/{i}/inputs/{j}/select",
                        code="invalid_select",
                        message=f"{select} can only be selected from a handler stage",
                    )
                )
            if select == "unmatched_materials" and not effective_forward_unknown(task, source):
                warnings.append(
                    FieldError(
                        pointer=f"/stages/{i}",
                        code="unknown_flag_off",
                        message=(
                            f"stage '{s['stage_id']}' consumes unmatched_materials but forward_unknown_to_llm "
                            "is false; materials will only be registered"
                        ),
                    )
                )
        for bi, pi, p in _patterns(s.get("bindings") or []):
            if p.get("type") == "regex":
                try:
                    re.compile(str(p["value"]))
                except re.error as exc:
                    errors.append(
                        FieldError(
                            pointer=f"/stages/{i}/bindings/{bi}/url_patterns/{pi}/value",
                            code="invalid_regex",
                            message=str(exc),
                        )
                    )
        if known_connections is not None:
            for name, conn_id in (s.get("connections") or {}).items():
                if conn_id not in known_connections:
                    warnings.append(
                        FieldError(
                            pointer=f"/stages/{i}/connections/{name}",
                            code="unknown_connection",
                            message=f"connection '{conn_id}' is not in the connections registry",
                        )
                    )
    if not errors and topo_order(task) is None:
        errors.append(FieldError(pointer="/stages", code="cycle", message="stage graph has a cycle"))
    unmatched = any(e.get("select") == "unmatched_materials" for s in stages for e in (s.get("inputs") or []))
    if unmatched and not any(s.get("bindings") for s in stages):
        warnings.append(
            FieldError(
                pointer="/stages",
                code="no_bindings",
                message="no stage has bindings, so no material is ever unmatched",
            )
        )
    return errors, warnings
