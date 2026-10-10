"""Adaptive sampling of a source (ТЗ §8: no fixed sample size; stop at sufficient confidence or report
an insufficient sample within the budget).

The collector runs an ordinary, bounded collection: the strategies of the user's ``crawl_hints`` when given
(they bound discovery to what the user asked for), otherwise sitemap + feeds + recursion from the entry point
for the web and history for Telegram; ``limits.crawl.max_pages_per_run`` is
``max_onboarding_samples x fetch_ratio`` (or the user's smaller ``crawl_hints.limits.crawl`` value). The
sampling collection does not treat ``rel=canonical`` as a duplicate signal (unless the hints set ``dedup``):
the assistant observes pages as served and decides about canonical dedup for the proposals itself.

Materials are pulled in pages; each round the assistant picks the least represented URL shapes (diversity),
classifies them with the cheap model and recomputes the confidence:

    coverage   = 1 - (materials of types seen fewer than min_examples_per_type times) / n
    confidence = (1 - estimated unseen-type share) x mean model confidence

``coverage`` is the Good-Turing sample-coverage estimate (with ``min_examples_per_type = 2`` it is
exactly ``1 - singletons / n``): the probability that the next material belongs to a type already
seen often enough. This estimate cannot detect a type that occurs later in a source ordered by URL
or discovery strategy. After the first classification batch, the sampler probes the remaining
bounded collector stream, classifies newly seen URL shapes, then samples more within known shapes
if confidence is still low. Unclassified materials count toward a finite-population estimate of
unseen types even when their URL shape is already known; this estimate also accounts for the
observed rare types.

The population is the bounded stream. An unfinished stream cannot establish diversity: when the sample budget
is reached with enough confidence before the stream ends, the rest of the stream is still read (without
classification) - a URL shape that appears there and is not represented, or a stream that does not finish
within the poll limits, makes the sample insufficient. A stream the collector stopped at its page budget
(``fetched >= max_pages_per_run``: the crawl space is larger, as on every real shop with filter links) is a
finished stream; the sample is then sufficient *for those pages* and its message says so.

Large HTML pages are reduced and shown to the model as digests (:mod:`jane_assistant.material`). Evidence
for proposals is gathered from the full pages: declared ``rel=canonical``, in-page link patterns and
pagination-like URL templates.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from math import pow as float_pow
from typing import Any

from .clients import CollectorClient, idem_key
from .content import decode_text, material_bytes, material_label, url_shape
from .llm import BudgetExhausted, LlmSession, part
from .material import (
    declared_canonical,
    inline_text,
    is_html,
    link_pattern,
    material_text,
    page_links,
    pagination_templates,
    reduce_material,
    same_url,
)
from .prompts import CLASSIFY, CLASSIFY_SCHEMA
from .settings import ServiceLimits

__all__ = ["Evidence", "Sample", "SampleResult", "coverage", "sample_source", "sampling_rules"]

Progress = Callable[[int, str], Awaitable[None]]
MAX_EVIDENCE_EXAMPLES = 5
"""Examples kept per kind of evidence (canonical declarations) - only for the model and the user to read."""


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


def _url(material: dict[str, Any]) -> str:
    locator = material.get("locator") or {}
    return str(locator.get("final_url") or locator.get("url") or locator.get("canonical_url") or "")


@dataclass
class Evidence:
    """What sampled pages say about discovery: canonical declarations, link patterns, pagination."""

    hosts: list[str]
    max_patterns: int
    shas: dict[str, str] = field(default_factory=dict)
    canonicals: list[tuple[str, str]] = field(default_factory=list)
    patterns: Counter[str] = field(default_factory=Counter)
    examples: dict[str, list[str]] = field(default_factory=dict)
    pagination: dict[str, dict[str, Any]] = field(default_factory=dict)

    def observe(self, material: dict[str, Any], raw: bytes, text: str) -> None:
        url = _url(material)
        if not url:
            return
        self.shas[url] = hashlib.sha256(raw).hexdigest()
        if not is_html((material.get("format") or {}).get("media_type")):
            return
        canonical = declared_canonical(text, url)
        if canonical and not same_url(canonical, url):
            self.canonicals.append((url, canonical))
        links = page_links(text, url, self.hosts)
        for link in links:
            pattern = link_pattern(link)
            self.patterns[pattern] += 1
            seen = self.examples.setdefault(pattern, [])
            if len(seen) < 2 and link not in seen:
                seen.append(link)
        for template, pages in pagination_templates(links).items():
            entry = self.pagination.setdefault(template, {"pages": set(), "found_on": url})
            entry["pages"].update(pages)

    def canonical_wire(self) -> dict[str, Any]:
        rows = []
        for url, canonical in self.canonicals:
            target = next((sha for u, sha in self.shas.items() if same_url(u, canonical)), None)
            content = (
                "not_sampled" if target is None else "same" if target == self.shas.get(url) else "different"
            )
            rows.append({"url": url, "canonical": canonical, "content": content})
        return {
            "declared_elsewhere": len(rows),
            "different_content": sum(1 for r in rows if r["content"] == "different"),
            "same_content": sum(1 for r in rows if r["content"] == "same"),
            "examples": rows[:MAX_EVIDENCE_EXAMPLES],
            "urls": [r["url"] for r in rows if r["content"] != "same"],
        }

    def wire(self) -> dict[str, Any]:
        return {
            "canonical": self.canonical_wire(),
            "link_patterns": [
                {"pattern": p, "links": n, "examples": self.examples.get(p, [])}
                for p, n in self.patterns.most_common(self.max_patterns)
            ],
            "pagination": [
                {
                    "template": t,
                    "pages_seen": sorted(v["pages"])[:20],
                    "max_page_seen": max(v["pages"]),
                    "found_on": v["found_on"],
                }
                for t, v in sorted(self.pagination.items(), key=lambda kv: -len(kv[1]["pages"]))[
                    : self.max_patterns
                ]
            ],
        }


def pick_diverse(
    reserve: list[Sample], seen: Counter[str], size: int, *, from_tail: bool = False
) -> list[Sample]:
    """Round-robin over URL shapes: always take a material of the least represented shape
    (already classified + already picked). After EOS, prefer later items within a shape so a
    source ordered by URL does not hide a late type behind early pages of the same shape."""
    picked: Counter[str] = Counter()
    left = list(reserve)
    batch: list[Sample] = []
    while left and len(batch) < size:
        best = min(
            range(len(left)),
            key=lambda i: (seen[left[i].shape] + picked[left[i].shape], -i if from_tail else i),
        )
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


def unseen_risk(classified: int, fetched: int, min_confidence: float) -> float:
    """Estimate unseen-type share from a bounded, diversity-seeking sample.

    The finite-population share caps the estimate for small streams. The second term is the
    with-replacement miss rate at the configured confidence level; it avoids requiring a fixed
    fraction of a large source. This is a sampling estimate, not a completeness guarantee.
    """
    if classified == 0 or fetched == 0:
        return 1.0
    if classified >= fetched:
        return 0.0
    return min(
        (fetched - classified) / fetched,
        1.0 - float_pow(1.0 - min_confidence, 1.0 / classified),
    )


def confidence_of(
    samples: list[Sample],
    min_examples: int,
    unclassified: int,
    min_confidence: float,
    min_distinct_types: int,
) -> float:
    if not samples:
        return 0.0
    counts = Counter(s.material_type for s in samples)
    mean = sum(s.confidence for s in samples) / len(samples)
    rare_share = 1.0 - coverage(counts, min_examples)
    # When fewer types than the configured diversity target have appeared, use a
    # tighter miss-risk level. A genuinely homogeneous source can still become sufficient.
    risk_confidence = 1.0 - (1.0 - min_confidence) / max(1, min_distinct_types - len(counts) + 1)
    unseen_share = unseen_risk(len(samples), len(samples) + unclassified, risk_confidence)
    return (1.0 - max(rare_share, unseen_share)) * mean


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
    hints = hints or {}
    hint_scope = hints.get("scope") or {}
    scope: dict[str, Any] = {"allowed_domains": sorted(set(allowed))}
    for key in ("include_subdomains", "allowed_schemes", "path_prefixes", "include", "exclude"):
        if key in hint_scope:
            scope[key] = hint_scope[key]
    # The user's strategies bound discovery (a category listing of a shop, not the whole shop); without
    # them the collector discovers the usual way.
    strategies: list[dict[str, Any]] = [dict(s) for s in hints.get("strategies") or [] if isinstance(s, dict)]
    if not strategies:
        strategies.append({"type": "sitemap", "strategy_id": "sample-sitemap"})
        if url:
            strategies.append({"type": "feed", "strategy_id": "sample-feed", "autodiscover": True})
            strategies.append({"type": "recursive", "strategy_id": "sample-recursive", "seeds": [url]})
    for s in strategies:  # empty lists are not allowed by the schema
        if s.get("urls") == []:
            del s["urls"]
    dedup = hints.get("dedup")
    return {
        "collector": "web",
        "scope": scope,
        "strategies": strategies,
        "robots": {"mode": "respect"},
        # Pages as served: pagination pages often declare page 1 canonical and would be dropped (with the
        # links on them); the assistant decides about canonical dedup for the proposals from evidence.
        "dedup": dict(dedup) if isinstance(dedup, dict) else {"use_link_rel_canonical": False},
    }


async def _classify(llm: LlmSession, batch: list[Sample], limits: ServiceLimits, model: str) -> None:
    labels = [f"url: {material_label(s.material)}\n\n" for s in batch]
    each = llm.room(CLASSIFY, [], len(batch), limits.onboarding.max_sample_chars + max(map(len, labels)))
    data = [
        part(f"m{i}", label + sample_text(s, each - len(label), limits), "text/plain")
        for i, (s, label) in enumerate(zip(batch, labels, strict=True))
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


def sample_text(sample: Sample, max_chars: int, limits: ServiceLimits) -> str:
    """The sample's text within ``max_chars``: its stored text when that fits, else the material again (a smaller
    digest of a large page, a shorter cut of anything else)."""
    if len(sample.text) <= max_chars:
        return sample.text
    media = (sample.material.get("format") or {}).get("media_type")
    return material_text(inline_text(sample.material, sample.text), media, max(0, max_chars), limits.material)


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
    crawl_limits: dict[str, Any] | None = None,
) -> SampleResult:
    """``crawl_limits``: the user's ``crawl_hints.limits.crawl`` (validated by the caller); its
    ``max_pages_per_run`` can only lower the sampling bound."""
    ob = limits.onboarding
    max_samples = limits.llm.max_onboarding_samples
    min_confidence = limits.llm.min_onboarding_confidence  # contract limits.llm (R08, WP-15)
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
        crawl = dict(crawl_limits or {})
        fetch_bound = min(fetch_bound, int(crawl.get("max_pages_per_run") or fetch_bound))
        request["limits"] = {"crawl": {**crawl, "max_pages_per_run": fetch_bound}}
    job = await collector.start_collection(request, idem_key(job_key, "sample-collection"))
    collection_id = str(job["job_id"])
    evidence = Evidence(
        hosts=list((rules.get("scope") or {}).get("allowed_domains") or []), max_patterns=ob.max_link_patterns
    )

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

    async def read_page() -> list[Sample]:
        """One poll of the collection: new materials (reduced, with their text) appended to ``reserve``."""
        nonlocal after, ended, empty_polls
        page = await collector.materials(
            collection_id, after, ob.sample_batch_size * ob.poll_page_factor, ob.collection_poll_wait_ms
        )
        after = page.get("next_cursor") or after
        ended = bool(page.get("end_of_stream"))
        items = page.get("items") or []
        empty_polls = 0 if items else empty_polls + 1
        new: list[Sample] = []
        for m in items:
            raw = await material_bytes(m)
            decoded = decode_text(raw, (m.get("format") or {}).get("charset"))
            evidence.observe(m, raw, decoded)
            lean = reduce_material(m, raw, decoded, limits.material)
            media = (m.get("format") or {}).get("media_type")
            text = material_text(inline_text(lean, decoded), media, ob.max_sample_chars, limits.material)
            shape = url_shape(m)
            examples_by_shape.setdefault(shape, [])
            if len(examples_by_shape[shape]) < ob.max_examples_per_type:
                examples_by_shape[shape].append(material_label(m))
            if strategy := (m.get("discovery") or {}).get("strategy"):
                by_strategy[str(strategy)] += 1
            if ck := (m.get("format") or {}).get("content_kind"):
                content_kinds[str(ck)] += 1
            new.append(Sample(lean, text, shape))
        reserve.extend(new)
        return new

    def stalled() -> str | None:
        if not ended and empty_polls >= ob.max_empty_polls:
            return (
                f"collection did not finish after {empty_polls} empty poll(s); "
                "cannot confirm material-type diversity"
            )
        return None

    async def drain(reached: str) -> str | None:
        """Read the rest of the stream without classifying; why the sample is insufficient, if it is."""
        while not ended:
            new = await read_page()
            novel = sorted({s.shape for s in new if s.shape not in shapes})
            if novel:
                return (
                    f"{reached} with confidence {current():.2f}; URL shape(s) found later are not "
                    f"represented: {', '.join(novel[:5])}"
                )
            if (why := stalled()) is not None:
                return why
        return None

    def current() -> float:
        return confidence_of(
            samples, ob.min_examples_per_type, len(reserve), min_confidence, ob.min_distinct_types
        )

    try:
        while True:
            unseen_shape = any(s.shape not in shapes for s in reserve)
            probing = bool(samples) and not unseen_shape
            if not ended and (len(reserve) < ob.sample_batch_size or probing):
                new = await read_page()
                confidence = current()
                if (message := stalled()) is not None:
                    break
                if not ended and not new and not reserve:
                    continue
                unseen_shape = any(s.shape not in shapes for s in reserve)
                if samples and not unseen_shape and not ended:
                    continue
            if confidence >= min_confidence and ended and not unseen_shape:
                break
            if not reserve:
                message = message or (
                    f"the source yielded only {len(samples)} material(s); cannot distinguish material types"
                )
                break
            room = max_samples - len(samples)
            novel_shapes = {s.shape for s in reserve if s.shape not in shapes}
            if samples and novel_shapes:
                batch_size = min(len(novel_shapes), ob.sample_batch_size)
            elif ended and samples:
                mean = sum(s.confidence for s in samples) / len(samples)
                fetched = len(samples) + len(reserve)
                batch_size = min(len(reserve), room, ob.sample_batch_size)
                distinct = len({s.material_type for s in samples})
                risk_confidence = 1.0 - (1.0 - min_confidence) / max(1, ob.min_distinct_types - distinct + 1)
                # Smallest next batch that could meet the threshold if its classifications
                # resolve the current rare types. Re-evaluate after that batch.
                if mean > 0:
                    for additional in range(1, batch_size + 1):
                        optimistic = mean * (
                            1.0 - unseen_risk(len(samples) + additional, fetched, risk_confidence)
                        )
                        if optimistic >= min_confidence:
                            batch_size = additional
                            break
            else:
                batch_size = ob.sample_batch_size
            batch = pick_diverse(reserve, shapes, min(batch_size, room), from_tail=ended and bool(samples))
            reserve = [s for s in reserve if not any(s is b for b in batch)]
            try:
                await _classify(llm, batch, limits, model)
            except BudgetExhausted:
                message = f"LLM budget exhausted after {len(samples)} classified material(s)"
                break
            for s in batch:
                shapes[s.shape] += 1
            samples.extend(batch)
            confidence = current()
            await progress(len(samples), f"sampled {len(samples)}, confidence {confidence:.2f}")
            # A high score over classified pages says nothing about types in later pages.
            # Only a closed stream with all observed URL shapes represented confirms diversity.
            unseen_shape = any(s.shape not in shapes for s in reserve)
            if confidence >= min_confidence and ended and not unseen_shape:
                break
            if len(samples) >= max_samples:
                reached = f"reached limits.llm.max_onboarding_samples={max_samples}"
                if confidence >= min_confidence and not unseen_shape and not ended:
                    # Confident within the budget, but the stream is still running: read the rest without
                    # classifying. A new URL shape there (or no end) leaves the sample insufficient.
                    message = await drain(reached)
                    if message is None:
                        confidence = current()
                        if confidence < min_confidence:
                            message = f"{reached} with confidence {confidence:.2f} over the finished stream"
                    break
                message = f"{reached} with confidence {confidence:.2f}"
                break
            if ended and not reserve:
                message = (
                    f"the source has only {len(samples)} reachable material(s); confidence {confidence:.2f}"
                )
                break
    finally:
        await collector.cancel(collection_id)
    sufficient = (
        message is None
        and confidence >= min_confidence
        and ended
        and not any(s.shape not in shapes for s in reserve)
    )
    try:
        stats = (await collector.collection(collection_id)).get("stats") or {}
    except Exception:
        stats = {}
    read = len(samples) + len(reserve)
    discovered = int(stats.get("discovered") or read)
    fetched = int(stats.get("fetched") or read)
    hints: dict[str, Any] = {
        "by_strategy": dict(stats.get("by_strategy") or by_strategy),
        "strategy_types": {
            str(s.get("strategy_id") or s.get("type")): str(s.get("type"))
            for s in rules.get("strategies") or []
            if isinstance(s, dict)
        },
        "discovered": discovered,
        "content_kinds": dict(content_kinds),
        "shapes": examples_by_shape,
        **({} if source_kind == "telegram" else evidence.wire()),
    }
    note: str | None = None
    if ended and source_kind != "telegram" and fetched >= fetch_bound:
        hints["truncated"] = {"fetched": fetched, "discovered": discovered, "max_pages_per_run": fetch_bound}
        note = (
            f"the sampling collection stopped at limits.crawl.max_pages_per_run={fetch_bound} "
            f"({fetched} fetched of {discovered} discovered URL(s)); the sample represents these pages - "
            "material types reachable only beyond them are not estimated"
        )
    if sufficient:
        message = note
    return SampleResult(samples, confidence, sufficient, message, hints)
