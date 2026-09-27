"""Adaptive sampling of a source (ТЗ §8: no fixed sample size; stop at sufficient confidence or report
an insufficient sample within the budget).

The collector runs an ordinary collection (sitemap + feeds + recursion from the entry point for the
web, history for Telegram) with ``limits.crawl.max_pages_per_run`` derived from
``limits.llm.max_onboarding_samples``. Materials are pulled in pages; each round the assistant picks
the least represented URL shapes (diversity), classifies them with the cheap model and recomputes
the confidence:

    coverage   = 1 - (materials of types seen fewer than min_examples_per_type times) / n
    confidence = coverage x mean model confidence

``coverage`` is the Good-Turing sample-coverage estimate (with ``min_examples_per_type = 2`` it is
exactly ``1 - singletons / n``): the probability that the next material belongs to a type already
seen often enough. Sampling stops when ``confidence >= limits.onboarding.min_confidence``, or when the
sample bound, the collection or the LLM budget runs out; then the sample is reported insufficient.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from .clients import CollectorClient, idem_key
from .content import decode_text, material_bytes, material_label, truncate, url_shape
from .llm import BudgetExhausted, LlmSession, part
from .prompts import CLASSIFY, CLASSIFY_SCHEMA
from .settings import ServiceLimits

__all__ = ["Sample", "SampleResult", "coverage", "sample_source", "sampling_rules"]

Progress = Callable[[int, str], Awaitable[None]]


@dataclass
class Sample:
    material: dict[str, Any]
    text: str
    shape: str
    material_type: str = "other"
    confidence: float = 0.0


@dataclass
class SampleResult:
    samples: list[Sample]
    confidence: float
    sufficient: bool
    message: str | None
    hints: dict[str, Any] = field(default_factory=dict)

    def counts(self) -> Counter[str]:
        return Counter(s.material_type for s in self.samples)

    def of_type(self, material_type: str) -> list[Sample]:
        return [s for s in self.samples if s.material_type == material_type]

    def wire(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "materials": len(self.samples),
            "distinct_types": len(self.counts()),
            "confidence": round(self.confidence, 4),
            "sufficient": self.sufficient,
        }
        if self.message:
            out["message"] = self.message
        return out


def pick_diverse(reserve: list[Sample], seen: Counter[str], size: int) -> list[Sample]:
    """Round-robin over URL shapes: always take a material of the least represented shape
    (already classified + already picked), keeping the collector's order within a shape."""
    picked: Counter[str] = Counter()
    left = list(reserve)
    batch: list[Sample] = []
    while left and len(batch) < size:
        best = min(range(len(left)), key=lambda i: (seen[left[i].shape] + picked[left[i].shape], i))
        s = left.pop(best)
        picked[s.shape] += 1
        batch.append(s)
    return batch


def coverage(counts: Counter[str], min_examples: int) -> float:
    n = sum(counts.values())
    if n == 0:
        return 0.0
    rare = sum(c for c in counts.values() if c < min_examples)
    return 1.0 - rare / n


def confidence_of(samples: list[Sample], min_examples: int) -> float:
    if not samples:
        return 0.0
    counts = Counter(s.material_type for s in samples)
    mean = sum(s.confidence for s in samples) / len(samples)
    return coverage(counts, min_examples) * mean


def sampling_rules(
    source_kind: str,
    url: str | None,
    telegram_username: str | None,
    allowed: list[str],
    hints: dict[str, Any] | None,
) -> dict[str, Any]:
    if source_kind == "telegram":
        return {
            "collector": "telegram",
            "channels": [{"username": telegram_username}],
            "history": {"enabled": True},
            "updates": {"new_messages": False, "edits": False},
        }
    hint_scope = (hints or {}).get("scope") or {}
    scope: dict[str, Any] = {"allowed_domains": sorted(set(allowed))}
    for key in ("include_subdomains", "path_prefixes", "include", "exclude"):
        if key in hint_scope:
            scope[key] = hint_scope[key]
    strategies: list[dict[str, Any]] = list((hints or {}).get("strategies") or [])
    kinds = {s.get("type") for s in strategies}
    if "sitemap" not in kinds:
        strategies.append({"type": "sitemap", "strategy_id": "sample-sitemap"})
    if "feed" not in kinds and url:
        strategies.append({"type": "feed", "strategy_id": "sample-feed", "urls": [], "autodiscover": True})
    if "recursive" not in kinds and url:
        strategies.append({"type": "recursive", "strategy_id": "sample-recursive", "seeds": [url]})
    for s in strategies:  # empty lists are not allowed by the schema
        if s.get("urls") == []:
            del s["urls"]
    return {"collector": "web", "scope": scope, "strategies": strategies, "robots": {"mode": "respect"}}


async def _classify(llm: LlmSession, batch: list[Sample], limits: ServiceLimits, model: str) -> None:
    data = [
        part(f"m{i}", f"url: {material_label(s.material)}\n\n{s.text}", "text/plain")
        for i, s in enumerate(batch)
    ]
    out = await llm.ask("classify", CLASSIFY, data, CLASSIFY_SCHEMA, model=model)
    by_name = {str(item["name"]): item for item in out.get("items") or []}
    for i, s in enumerate(batch):
        item = by_name.get(f"m{i}")
        if item:
            s.material_type = str(item["material_type"])
            s.confidence = float(item["confidence"])
        else:  # the model skipped it: counts as an unknown, low-confidence material
            s.material_type, s.confidence = "other", 0.0


async def sample_source(
    *,
    collector: CollectorClient,
    llm: LlmSession,
    limits: ServiceLimits,
    job_key: str,
    source_id: str,
    source_kind: str,
    rules: dict[str, Any],
    model: str,
    progress: Progress,
) -> SampleResult:
    ob = limits.onboarding
    max_samples = limits.llm.max_onboarding_samples
    fetch_bound = max_samples * ob.fetch_ratio
    request: dict[str, Any] = {
        "source_kind": source_kind,
        "source_id": source_id,
        "rules": rules,
        "mode": "full",
        "state_key": f"assistant-{job_key[-24:]}".lower(),
        "content_delivery": "inline",
        "labels": {"purpose": "onboarding-sample"},
    }
    if source_kind == "telegram":
        request["limits"] = {"telegram": {"max_messages_per_run": fetch_bound}}
    else:
        request["limits"] = {"crawl": {"max_pages_per_run": fetch_bound}}
    job = await collector.start_collection(request, idem_key(job_key, "sample-collection"))
    collection_id = str(job["job_id"])

    samples: list[Sample] = []
    reserve: list[Sample] = []
    shapes: Counter[str] = Counter()
    examples_by_shape: dict[str, list[str]] = {}
    by_strategy: Counter[str] = Counter()
    content_kinds: Counter[str] = Counter()
    after: str | None = None
    ended = False
    empty_polls = 0
    confidence = 0.0
    message: str | None = None
    try:
        while True:
            if not ended and len(reserve) < ob.sample_batch_size:
                page = await collector.materials(
                    collection_id,
                    after,
                    ob.sample_batch_size * ob.poll_page_factor,
                    ob.collection_poll_wait_ms,
                )
                after = page.get("next_cursor") or after
                ended = bool(page.get("end_of_stream"))
                items = page.get("items") or []
                empty_polls = 0 if items else empty_polls + 1
                for m in items:
                    raw = await material_bytes(m)
                    text = truncate(
                        decode_text(raw, (m.get("format") or {}).get("charset")), ob.max_sample_chars
                    )
                    shape = url_shape(m)
                    examples_by_shape.setdefault(shape, [])
                    if len(examples_by_shape[shape]) < ob.max_examples_per_type:
                        examples_by_shape[shape].append(material_label(m))
                    if strategy := (m.get("discovery") or {}).get("strategy"):
                        by_strategy[str(strategy)] += 1
                    if ck := (m.get("format") or {}).get("content_kind"):
                        content_kinds[str(ck)] += 1
                    reserve.append(Sample(m, text, shape))
                if not ended and not items and not reserve and empty_polls < ob.max_empty_polls:
                    continue
            if not reserve:
                message = message or (
                    f"the source yielded only {len(samples)} material(s); cannot distinguish material types"
                )
                break
            room = max_samples - len(samples)
            batch = pick_diverse(reserve, shapes, min(ob.sample_batch_size, room))
            reserve = [s for s in reserve if not any(s is b for b in batch)]
            try:
                await _classify(llm, batch, limits, model)
            except BudgetExhausted:
                message = f"LLM budget exhausted after {len(samples)} classified material(s)"
                break
            for s in batch:
                shapes[s.shape] += 1
            samples.extend(batch)
            confidence = confidence_of(samples, ob.min_examples_per_type)
            await progress(len(samples), f"sampled {len(samples)}, confidence {confidence:.2f}")
            if confidence >= ob.min_confidence:
                break
            if len(samples) >= max_samples:
                message = f"reached limits.llm.max_onboarding_samples={max_samples} with confidence {confidence:.2f}"
                break
            if ended and not reserve:
                message = (
                    f"the source has only {len(samples)} reachable material(s); confidence {confidence:.2f}"
                )
                break
    finally:
        await collector.cancel(collection_id)
    sufficient = confidence >= ob.min_confidence
    try:
        stats = (await collector.collection(collection_id)).get("stats") or {}
    except Exception:
        stats = {}
    hints = {
        "by_strategy": dict(stats.get("by_strategy") or by_strategy),
        "discovered": int(stats.get("discovered") or len(samples) + len(reserve)),
        "content_kinds": dict(content_kinds),
        "shapes": examples_by_shape,
    }
    return SampleResult(samples, confidence, sufficient, None if sufficient else message, hints)
