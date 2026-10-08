"""Analysis of an unknown material (ТЗ §8, criterion 11).

The orchestrator forwards a material without a matching handler only when the effective flag
«Передавати в LLM невідомі сторінки» (``forward_unknown_to_llm``) is on. The assistant checks the flag
again and refuses (403 ``access_denied_by_policy``) *before* any LLM call when it is off.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from jane_kit.errors import JaneError

from .clients import Neighbours, RemoteError
from .content import decode_text, material_bytes, material_label, truncate
from .llm import BudgetExhausted, LlmSession, part
from .prompts import UNKNOWN, UNKNOWN_SCHEMA
from .settings import ServiceLimits, Settings

__all__ = ["FlagOff", "run_unknown"]

NAVIGATION_TYPES = {"category", "listing", "news_list", "sitemap", "feed", "index", "search"}

log = logging.getLogger(__name__)


class FlagOff(JaneError):
    code = "access_denied_by_policy"


async def run_unknown(
    *, nb: Neighbours, req: dict[str, Any], settings: Settings, limits: ServiceLimits, job_id: str
) -> dict[str, Any]:
    material = req["material"]
    raw = await material_bytes(material)
    text = truncate(
        decode_text(raw, (material.get("format") or {}).get("charset")), limits.unknown.max_sample_chars
    )
    llm = LlmSession(
        nb.llm, limits.llm, "unknown_material", job_id, source_id=req["source_id"], task_id=req.get("task_id")
    )
    try:
        out = await llm.ask(
            "classify_unknown",
            UNKNOWN,
            [
                part(
                    "material",
                    f"url: {material_label(material)}\n\n{text}",
                    (material.get("format") or {}).get("media_type", "text/plain"),
                )
            ],
            UNKNOWN_SCHEMA,
            model=settings.llm_model_cheap,
        )
    except BudgetExhausted as exc:
        return {
            "classification": {"material_type": "unknown", "confidence": 0},
            "suggestion": {"action": "none", "details": f"not analysed: {exc}"},
        }
    mtype, conf = str(out["material_type"]), float(out["confidence"])
    entity_types = sorted({str(t) for t in out.get("entity_types") or []})
    # The source's expected entity types only refine the suggestion (the assistant works without the
    # orchestrator): an error answer or an orchestrator still unreachable after the client's retries
    # (transport errors) leaves them unknown instead of failing the analysis the LLM was already paid for.
    expected: set[str] | None = None
    if nb.orchestrator.configured:
        try:
            source = await nb.orchestrator.get_source(req["source_id"])
            expected = set(source.get("expected_entity_types") or [])
        except (RemoteError, JaneError, httpx.HTTPError) as exc:
            log.warning(
                "expected entity types not read from the orchestrator",
                extra={"source_id": req["source_id"], "error": f"{type(exc).__name__}: {exc}"},
            )
            expected = None
    if conf < limits.unknown.min_confidence or not (out.get("relevant") or out.get("navigation")):
        action, details = "none", f"{mtype} (confidence {conf:.2f}) is not worth a handler"
    elif out.get("navigation") or mtype in NAVIGATION_TYPES:
        action, details = (
            "extend_rules",
            f"{mtype} page can serve as a discovery source in the collector rules",
        )
    elif expected is not None and entity_types and not set(entity_types) <= expected:
        new = sorted(set(entity_types) - expected)
        action, details = (
            "expand_entity_types",
            f"material carries {', '.join(new)} not in the source's expected entity types; the user decides",
        )
    else:
        action, details = (
            "new_extractor",
            f"no extractor handles {mtype} materials carrying {', '.join(entity_types) or 'records'}",
        )
    if out.get("details"):
        details = f"{details}. Model note: {str(out['details'])[:500]}"
    return {
        "classification": {"material_type": mtype, "confidence": round(conf, 4)},
        "suggestion": {"action": action, "details": details[:2000]},
    }
