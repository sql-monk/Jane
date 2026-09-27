"""LLM handler (``handler.v1``): executes ``kind: llm`` packages through the gateway.

For every input one structured completion is made: trusted text = the package's ``instructions`` file;
untrusted data = the input (material content and metadata, rendered ``input_template``, entities or
data) — never mixed into the instructions. The model output is validated against the package's
``output_schema`` (retries per ``gateway.max_schema_retries``), then mapped to ``HandlerResult``:

* ``output.data`` — the model output (a list ``{"results": [...]}`` for several inputs);
* ``output.entities`` — for each ``output.entities[]`` of the manifest with ``entity_type`` T, the items
  of the top-level array ``T + "s"`` (or ``T``) of the output become ``EntityRecord`` s; key fields are
  taken from the item, key fields named ``message``/``material``/``material_id`` fall back to the
  material id; observation comes from the material;
* status: ``success`` (entities, or non-empty data when the package declares no entities), ``empty``,
  ``failed`` with ``schema_mismatch`` / ``budget_exhausted`` / ``invalid_params``.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from jsonschema import Draft202012Validator

from jane_kit.errors import JaneError, ValidationFailed
from jane_llm.gateway import BudgetExhausted, Gateway
from jane_llm.models import CompletionRequest, CompletionScope, LlmLimitsIn
from jane_llm.packages import LoadedPackage, PackageLoader, read_content
from jane_llm.prompt import DataBlock

_KEY_FROM_MATERIAL = {"message", "material", "material_id"}
_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_.]+)\s*\}\}")


def _ts(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _lookup(obj: Any, path: str) -> Any:
    for part in path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(part)
        elif isinstance(obj, list) and part.isdigit() and int(part) < len(obj):
            obj = obj[int(part)]
        else:
            return None
    return obj


def render_template(template: str, context: dict[str, Any]) -> str:
    """``{{path.to.value}}`` placeholders; values are JSON for non-strings, empty for missing."""

    def sub(m: re.Match[str]) -> str:
        value = _lookup(context, m.group(1))
        if value is None:
            return ""
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)

    return _PLACEHOLDER.sub(sub, template)


class HandlerFailure(Exception):
    def __init__(
        self, kind: str, message: str, *, retryable: bool = False, details: dict[str, Any] | None = None
    ):
        super().__init__(message)
        self.kind, self.message, self.retryable, self.details = kind, message, retryable, details


class LlmHandler:
    def __init__(self, gateway: Gateway, loader: PackageLoader) -> None:
        self.gateway = gateway
        self.loader = loader

    async def _input_blocks(
        self, inp: dict[str, Any], index: int, pkg: LoadedPackage
    ) -> tuple[list[DataBlock], dict[str, Any]]:
        """Data blocks for one input and the template context (``content`` = decoded text)."""
        max_bytes = self.gateway.limits.gateway.max_data_part_bytes
        kind = inp.get("kind")
        ctx: dict[str, Any] = {"input": inp, "index": index}
        if kind == "material":
            material = inp["material"]
            raw = await read_content(material["content"], max_bytes)
            charset = material["content"].get("charset") or "utf-8"
            text = raw.decode(charset if charset.lower() != "binary" else "utf-8", errors="replace")
            ctx.update(material=material, content=text)
            meta = {
                k: material.get(k)
                for k in (
                    "material_id",
                    "locator",
                    "source",
                    "fetched_at",
                    "published_at",
                    "edited_at",
                    "format",
                )
                if material.get(k) is not None
            }
            media = material.get("format", {}).get("media_type") or material["content"].get("media_type")
            blocks = [
                DataBlock(
                    f"material[{index}].metadata", "application/json", json.dumps(meta, ensure_ascii=False)
                ),
                DataBlock(f"material[{index}].content", media, text),
            ]
        elif kind == "entities":
            entities = inp.get("entities")
            if entities is None and inp.get("entities_ref"):
                entities = json.loads(await read_content(inp["entities_ref"], max_bytes))
            ctx.update(entities=entities, content=json.dumps(entities, ensure_ascii=False))
            blocks = [DataBlock(f"entities[{index}]", "application/json", ctx["content"])]
        elif kind == "data":
            data = inp.get("data")
            if data is None and inp.get("data_ref"):
                data = json.loads(await read_content(inp["data_ref"], max_bytes))
            ctx.update(
                data=data, content=data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
            )
            blocks = [DataBlock(f"data[{index}]", "application/json", ctx["content"])]
        else:
            raise ValidationFailed(f"unsupported input kind {kind!r}")
        accepts = (pkg.manifest.get("input") or {}).get("accepts")
        if accepts and kind not in accepts:
            raise HandlerFailure("invalid_params", f"package accepts {accepts}, got input kind {kind!r}")
        template_path = pkg.manifest["entry"].get("input_template")
        if template_path:
            # The template is part of the package, but once filled it carries source content: data channel.
            blocks = [
                DataBlock(f"input[{index}]", "text/markdown", render_template(pkg.text(template_path), ctx))
            ]
        return blocks, ctx

    def _entities(
        self, pkg: LoadedPackage, output: Any, inp: dict[str, Any], scope_default: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        defs = (pkg.manifest.get("output") or {}).get("entities") or []
        if not defs or not isinstance(output, dict) or inp.get("kind") != "material":
            return [], []
        material = inp["material"]
        observation = {
            "observation_id": material["observation_id"],
            "observed_at": material["fetched_at"],
            "material_id": material["material_id"],
        }
        if (seq := (material.get("revision") or {}).get("sequence")) is not None:
            observation["sequence"] = seq
        if sha := (material.get("revision") or {}).get("content_sha256"):
            observation["content_sha256"] = sha
        scope = (material.get("source") or {}).get("source_id") or scope_default
        entities: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        for d in defs:
            etype = d["entity_type"]
            items = output.get(f"{etype}s", output.get(etype))
            if isinstance(items, dict):
                items = [items]
            if not isinstance(items, list):
                continue
            validator = Draft202012Validator(pkg.json(d["schema"])) if d.get("schema") in pkg.files else None
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                fields = {k: v for k, v in item.items() if v is not None}
                natural: dict[str, Any] = {}
                for kf in d["key_fields"]:
                    if kf in fields and isinstance(fields[kf], str | int | float | bool):
                        natural[kf] = fields[kf]
                    elif kf in _KEY_FROM_MATERIAL:
                        natural[kf] = material["material_id"]
                if len(natural) != len(d["key_fields"]):
                    errors.append(
                        {"pointer": f"/{etype}s/{i}", "message": f"missing key fields {d['key_fields']}"}
                    )
                    continue
                if validator is not None:
                    for e in validator.iter_errors(fields):
                        path = "/".join(str(p) for p in e.absolute_path)
                        errors.append(
                            {"pointer": f"/{etype}s/{i}/{path}".rstrip("/"), "message": e.message[:500]}
                        )
                entities.append(
                    {
                        "entity_type": etype,
                        "schema": f"{pkg.package_id}@{pkg.version}#{etype}",
                        "key": {"scope": scope, "natural": natural},
                        "fields": fields,
                        "observation": observation,
                    }
                )
        return entities, errors

    async def invoke(
        self, inv: dict[str, Any], *, invocation_id: str | None = None, force_test_mode: bool = False
    ) -> dict[str, Any]:
        """Run one invocation; returns ``HandlerResult`` (never raises for handler failures)."""
        started = datetime.now(UTC)
        invocation_id = invocation_id or f"inv_{uuid.uuid4().hex}"
        context = inv.get("context") or {}
        trace = context.get("trace") or {}
        test_mode = force_test_mode or bool(context.get("test_mode"))
        pkg = await self.loader.load(inv["handler"], inv.get("package_archive"))
        base = {
            "invocation_id": invocation_id,
            "handler": {"package_id": pkg.package_id, "version": pkg.version, "digest": pkg.digest},
            "handler_kind": "llm",
            "inputs": [self._input_ref(i) for i in inv["inputs"]],
            "delivery_key": (inv.get("delivery") or {}).get("delivery_key"),
            "test_mode": test_mode,
        }
        usage: dict[str, Any] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
            "currency": "USD",
            "provider": None,
            "model": None,
        }
        try:
            result = await self._run(inv, pkg, trace, test_mode, usage)
        except HandlerFailure as f:
            failure: dict[str, Any] = {"kind": f.kind, "message": f.message, "retryable": f.retryable}
            if f.details:
                failure["details"] = f.details
            result = {"status": "failed", "failure": failure}
            if f.details and f.details.get("validation_errors"):
                result["diagnostics"] = {"validation_errors": f.details.pop("validation_errors")}
        finished = datetime.now(UTC)
        out = {**base, **result, "started_at": _ts(started), "finished_at": _ts(finished)}
        if usage["provider"]:
            out["usage"] = {
                "llm": {
                    "provider": usage["provider"],
                    "model": usage["model"],
                    "input_tokens": usage["input_tokens"],
                    "output_tokens": usage["output_tokens"],
                    "cost": {"amount": round(usage["cost"], 10), "currency": usage["currency"]},
                }
            }
        diagnostics = out.setdefault("diagnostics", {})
        diagnostics.setdefault("metrics", {})["duration_ms"] = int(
            (finished - started).total_seconds() * 1000
        )
        return out

    @staticmethod
    def _input_ref(inp: dict[str, Any]) -> dict[str, Any]:
        ref: dict[str, Any] = {"kind": inp.get("kind")}
        if inp.get("kind") == "material":
            m = inp["material"]
            ref.update(material_id=m.get("material_id"), observation_id=m.get("observation_id"))
            if sha := (m.get("revision") or {}).get("content_sha256"):
                ref["content_sha256"] = sha
        elif inp.get("from_invocation_id"):
            ref["from_invocation_id"] = inp["from_invocation_id"]
        return ref

    async def _run(
        self,
        inv: dict[str, Any],
        pkg: LoadedPackage,
        trace: dict[str, Any],
        test_mode: bool,
        usage: dict[str, Any],
    ) -> dict[str, Any]:
        entry = pkg.manifest["entry"]
        params = inv.get("params") or {}
        if ps := pkg.manifest.get("params_schema"):
            errs = list(Draft202012Validator(pkg.json(ps)).iter_errors(params))
            if errs:
                raise HandlerFailure("invalid_params", "; ".join(e.message for e in errs[:5]))
        instructions = pkg.text(entry["instructions"])
        schema = pkg.json(entry["output_schema"])
        limits = (inv.get("limits") or {}).get("llm")
        outputs: list[Any] = []
        entities: list[dict[str, Any]] = []
        entity_errors: list[dict[str, str]] = []
        for index, inp in enumerate(inv["inputs"]):
            blocks, _ = await self._input_blocks(inp, index, pkg)
            req = CompletionRequest(
                model=entry.get("model"),
                instructions=instructions,
                output_schema=schema,
                max_output_tokens=entry.get("max_output_tokens"),
                temperature=entry.get("temperature"),
                scope=CompletionScope(
                    source_id=trace.get("source_id"),
                    task_id=trace.get("task_id"),
                    run_id=trace.get("run_id"),
                    purpose="handler",
                ),
                limits=LlmLimitsIn.model_validate(limits) if limits else None,
                test_mode=test_mode,
            )
            try:
                res = await self.gateway.complete(req, extra_data=blocks)
            except BudgetExhausted as exc:
                raise HandlerFailure(
                    "budget_exhausted",
                    exc.detail or "LLM budget exhausted",
                    retryable=False,
                    details=exc.details,
                ) from exc
            except JaneError as exc:
                if exc.error_code in {"validation_failed", "limit_exceeded", "not_found"}:
                    raise HandlerFailure("invalid_params", exc.detail or exc.error_code) from exc
                raise
            u = res["usage"]
            usage["input_tokens"] += u["input_tokens"]
            usage["output_tokens"] += u["output_tokens"]
            usage["cost"] += u["cost"]["amount"]
            usage["currency"] = u["cost"]["currency"]
            usage["provider"], usage["model"] = res["model"]["provider_id"], res["model"]["model_id"]
            if not res["valid"]:
                raise HandlerFailure(
                    "schema_mismatch",
                    "LLM output does not match the package output_schema",
                    details={
                        "validation_errors": res["validation_errors"]
                        or [{"pointer": "", "message": "invalid"}]
                    },
                )
            outputs.append(res["output"])
            ents, errs = self._entities(pkg, res["output"], inp, trace.get("source_id") or "local")
            entities.extend(ents)
            entity_errors.extend(errs)
        if entity_errors:
            raise HandlerFailure(
                "schema_mismatch",
                "entities produced by the LLM do not match the package schemas",
                details={"validation_errors": entity_errors},
            )
        data = outputs[0] if len(outputs) == 1 else {"results": outputs}
        declares_entities = bool((pkg.manifest.get("output") or {}).get("entities"))
        has_content = bool(entities) if declares_entities else any(bool(o) for o in outputs)
        output: dict[str, Any] = {"data": data}
        if declares_entities:
            output["entities"] = entities
        return {"status": "success" if has_content else "empty", "output": output}
