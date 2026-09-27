"""Fan-out of the stage DAG: which items a material or a handler result creates downstream (pure logic).

Item keys are deterministic so a repeated delivery never creates a second item
(``UNIQUE (run_id, stage_id, item_key)``):

* a material from the collect stage (or a reprocessed stored RAW): ``observation_id`` — a collector
  re-delivering the same observation hits the same item and the same ``delivery_key``;
* anything derived from a handler result: ``<upstream item_id>#<edge index>``.

Inputs are passed **by reference**: a Material carries its ``ContentRef`` (inline or blob) as received;
entities/data are passed as returned (``entities_ref``/``data_ref`` stay references).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from jane_orchestrator.conditions import condition_uses_entity, evaluate, stage_bindings_match

__all__ = [
    "NewItem",
    "UnknownDecision",
    "collect_stage_id",
    "material_of",
    "result_context",
    "route_material",
    "route_result",
]


@dataclass
class NewItem:
    stage_id: str
    item_key: str
    inputs: list[dict[str, Any]]
    material: dict[str, Any] | None = None
    upstream_item_id: str | None = None


@dataclass
class UnknownDecision:
    unknown: bool
    forwarded: bool
    reason: str = ""


@dataclass
class MaterialRouting:
    items: list[NewItem] = field(default_factory=list)
    unknown: UnknownDecision = field(default_factory=lambda: UnknownDecision(False, False))


def collect_stage_id(config: Mapping[str, Any]) -> str:
    return str(next(s["stage_id"] for s in config["stages"] if s["kind"] == "collect"))


def material_of(inputs: list[Mapping[str, Any]] | None) -> dict[str, Any] | None:
    """The material an item is about (MaterialInput, or the material attached to EntitiesInput)."""
    for inp in inputs or []:
        if inp.get("kind") in {"material", "entities"} and inp.get("material"):
            return dict(inp["material"])
    return None


def route_material(
    config: Mapping[str, Any],
    source_id: str,
    material: dict[str, Any],
    forward_unknown: bool,
    from_stage: str | None = None,
) -> MaterialRouting:
    """Items for a material emitted by the collect stage (or injected at ``from_stage`` on reprocessing)."""
    out = MaterialRouting()
    key = str(material["observation_id"])
    stages = config["stages"]
    if from_stage is not None:
        out.items.append(NewItem(from_stage, key, [{"kind": "material", "material": material}], material))
        return out
    collect = collect_stage_id(config)
    bound = [s for s in stages if s.get("bindings")]
    unknown = bool(bound) and not any(stage_bindings_match(s["bindings"], material, source_id) for s in bound)
    consumers = [
        s
        for s in stages
        if any(
            e["from"] == collect and e.get("select") == "unmatched_materials" for e in s.get("inputs") or []
        )
    ]
    if unknown:
        if not forward_unknown:
            out.unknown = UnknownDecision(True, False, "no binding matched and forward_unknown_to_llm=false")
        elif not consumers:
            out.unknown = UnknownDecision(
                True, False, "no binding matched and no stage consumes unmatched_materials"
            )
        else:
            out.unknown = UnknownDecision(
                True, True, "no binding matched; forwarded (forward_unknown_to_llm=true)"
            )
    ctx = {"material": material}
    for s in stages:
        if s["kind"] != "handler":
            continue
        for edge in s.get("inputs") or []:
            if edge["from"] != collect:
                continue
            select = edge.get("select", "output")
            if select == "output":
                if not stage_bindings_match(s.get("bindings"), material, source_id):
                    continue
            elif select == "unmatched_materials":
                if not out.unknown.forwarded:
                    continue
            else:
                continue
            if not evaluate(edge.get("when"), ctx):
                continue
            if any(i.stage_id == s["stage_id"] for i in out.items):
                continue  # two edges from collect into one stage: one item per material
            out.items.append(
                NewItem(s["stage_id"], key, [{"kind": "material", "material": material}], material)
            )
    return out


def result_context(result: Mapping[str, Any]) -> dict[str, Any]:
    output = result.get("output") or {}
    ctx: dict[str, Any] = {"status": result.get("status")}
    if result.get("failure"):
        ctx["failure"] = {"kind": result["failure"].get("kind")}
    if isinstance(output.get("entities"), list):
        ctx["entities_count"] = len(output["entities"])
    return ctx


def _problem_data(stage_id: str, result: Mapping[str, Any]) -> dict[str, Any]:
    problem: dict[str, Any] = {
        "stage_id": stage_id,
        "status": result.get("status"),
        "invocation_id": result.get("invocation_id"),
        "handler": result.get("handler"),
    }
    for key in ("unrecognized", "failure", "diagnostics"):
        if result.get(key) is not None:
            problem[key] = result[key]
    return {"problem": problem}


def route_result(
    config: Mapping[str, Any],
    source_id: str,
    stage_id: str,
    upstream_item_id: str,
    inputs: list[Mapping[str, Any]] | None,
    result: Mapping[str, Any],
) -> list[NewItem]:
    """Items created by a completed handler item with ``result`` (HandlerResult)."""
    material = material_of(inputs)
    output = result.get("output") or {}
    rctx = result_context(result)
    base_ctx: dict[str, Any] = {"material": material or {}, "result": rctx}
    items: list[NewItem] = []
    for s in config["stages"]:
        for j, edge in enumerate(s.get("inputs") or []):
            if edge["from"] != stage_id:
                continue
            select = edge.get("select", "output")
            when = edge.get("when")
            key = f"{upstream_item_id}#{s['stage_id']}#{j}"
            new_inputs: list[dict[str, Any]] = []
            if select == "output":
                entities = output.get("entities") if isinstance(output.get("entities"), list) else None
                if condition_uses_entity(when) and entities is not None:
                    entities = [e for e in entities if evaluate(when, {**base_ctx, "entity": e})]
                    if not entities:
                        continue
                elif not evaluate(when, base_ctx):
                    continue
                if material is not None and not stage_bindings_match(s.get("bindings"), material, source_id):
                    continue
                if entities or output.get("entities_ref"):
                    inp: dict[str, Any] = {"kind": "entities"}
                    if entities:
                        inp["entities"] = entities
                    else:
                        inp["entities_ref"] = output["entities_ref"]
                    if result.get("invocation_id"):
                        inp["from_invocation_id"] = result["invocation_id"]
                    if material is not None:
                        inp["material"] = material
                    new_inputs.append(inp)
                elif "data" in output or output.get("data_ref"):
                    data_inp: dict[str, Any] = {"kind": "data"}
                    if "data" in output:
                        data_inp["data"] = output["data"]
                    else:
                        data_inp["data_ref"] = output["data_ref"]
                    if result.get("invocation_id"):
                        data_inp["from_invocation_id"] = result["invocation_id"]
                    new_inputs.append(data_inp)
                elif output.get("writes"):
                    new_inputs.append(
                        {
                            "kind": "data",
                            "data": {"writes": output["writes"]},
                            **(
                                {"from_invocation_id": result["invocation_id"]}
                                if result.get("invocation_id")
                                else {}
                            ),
                        }
                    )
                else:
                    continue  # nothing to deliver (e.g. empty result)
            elif select == "input_material":
                if material is None or not evaluate(when, base_ctx):
                    continue
                new_inputs.append({"kind": "material", "material": material})
            elif select == "problems":
                if result.get("status") not in {"unrecognized", "failed"} or not evaluate(when, base_ctx):
                    continue
                if material is not None:
                    new_inputs.append({"kind": "material", "material": material})
                data: dict[str, Any] = {"kind": "data", "data": _problem_data(stage_id, result)}
                if result.get("invocation_id"):
                    data["from_invocation_id"] = result["invocation_id"]
                new_inputs.append(data)
            else:
                continue
            items.append(NewItem(s["stage_id"], key, new_inputs, material, upstream_item_id))
    return items
