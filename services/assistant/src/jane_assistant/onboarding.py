"""Onboarding of a new source (ТЗ §8, §13.1 п.2, plan.md WP-11 «Підключення»).

States (``assistant.v1`` ``OnboardingSession.status``)::

    resolving -> needs_disambiguation --(candidate-selection)--> sampling
    resolving -> sampling -> analyzing -> proposals_ready --(acceptance)--> applying -> completed
                          \\-> insufficient_sample
    any running state -> failed | cancelled

* resolving: a URL/@channel is taken as is; a name goes to the search provider; a clear winner is
  selected automatically, otherwise the user chooses.
* sampling: adaptive (see :mod:`jane_assistant.sampling`).
* analyzing: material types, entities and fields; for every entity type existing extractors are
  searched in the registry and tested on the samples (bind / fork+adapt / create), new code is
  generated and tested; then several collection plans with coverage, cost and risks.
* acceptance: publishes rules and packages (``draft``), records test reports and returns source and
  task drafts. With ``activate: true`` (or ``auto_activation`` in the request, which accepts the
  recommended plan) and all tests passing, versions are approved and the source and task are created
  in the orchestrator.
"""

from __future__ import annotations

import asyncio
import base64
import copy
import dataclasses
import logging
import math
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from jane_kit.errors import Conflict, JaneError, NotFound
from jane_kit.jobs import JobCancelledError, JobContext, JobRunner

from .clients import Neighbours, RemoteError, idem_key
from .content import host_of, material_label
from .guards import SchemaValidator, check_code, sanitize_web_rules
from .improvement import ProblemCase, improve_draft
from .llm import BudgetExhausted, InvalidModelOutput, LlmSession, as_json, part
from .packages import PackageDraft, bump, collector_rules_draft, extractor_draft, model_ref, slug
from .prompts import ANALYZE, ANALYZE_SCHEMA, GENERATE, GENERATE_SCHEMA, PROPOSE, PROPOSE_SCHEMA
from .sampling import Sample, SampleResult, sample_source, sampling_rules
from .search import Candidate, SearchProvider, direct_candidate
from .settings import ServiceLimits, Settings, request_layer, resolve_service_limits
from .testing import TestOutcome, extra_case, run_tests

__all__ = ["InMemorySessionStore", "OnboardingService", "Session", "SessionStore"]

log = logging.getLogger(__name__)
TERMINAL = {"completed", "failed", "cancelled"}
RUNNING = {"resolving", "sampling", "analyzing", "applying"}
DISCOVERY_METHODS = {"seed_list", "sitemap", "feed", "listing", "url_template", "api_feed", "recursive"}


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ExtractorPlan:
    entity_type: str
    material_type: str
    action: str
    package: dict[str, Any] | None = None
    match_score: float | None = None
    outcome: TestOutcome | None = None
    draft: PackageDraft | None = None
    fork_from: dict[str, Any] | None = None

    @property
    def tests_passed(self) -> bool:
        return self.outcome is not None and self.outcome.passed

    def wire(self) -> dict[str, Any]:
        out: dict[str, Any] = {"entity_type": self.entity_type, "action": self.action}
        if self.package:
            out["package"] = self.package
        if self.match_score is not None:
            out["match_score"] = round(self.match_score, 4)
        if self.outcome is not None:
            out["tested_on_samples"] = {
                "passed": int(self.outcome.report.get("passed", 0)),
                "failed": int(self.outcome.report.get("failed", 0)),
            }
        return out


@dataclass
class Session:
    session_id: str
    query: str
    request: dict[str, Any]
    status: str = "resolving"
    created_at: str = field(default_factory=_now)
    candidates: list[Candidate] = field(default_factory=list)
    selected_candidate_id: str | None = None
    sample: SampleResult | None = None
    analysis: dict[str, Any] | None = None
    proposals: list[dict[str, Any]] = field(default_factory=list)
    plans: dict[str, ExtractorPlan] = field(default_factory=dict)
    spent: float = 0.0
    currency: str = "USD"
    job_id: str | None = None
    error: dict[str, Any] | None = None
    acceptance: dict[str, Any] | None = None
    version: int = 0
    """Optimistic concurrency version of the stored session (set by the store)."""

    def to_doc(self) -> dict[str, Any]:
        """JSON document of the whole session (shared state of all instances)."""
        return {
            "session_id": self.session_id,
            "query": self.query,
            "request": self.request,
            "status": self.status,
            "created_at": self.created_at,
            "candidates": [dataclasses.asdict(c) for c in self.candidates],
            "selected_candidate_id": self.selected_candidate_id,
            "sample": dataclasses.asdict(self.sample) if self.sample is not None else None,
            "analysis": self.analysis,
            "proposals": self.proposals,
            "plans": {k: _plan_doc(p) for k, p in self.plans.items()},
            "spent": self.spent,
            "currency": self.currency,
            "job_id": self.job_id,
            "error": self.error,
            "acceptance": self.acceptance,
        }

    @classmethod
    def from_doc(cls, doc: dict[str, Any], version: int = 0) -> Session:
        sample = doc.get("sample")
        return cls(
            session_id=doc["session_id"],
            query=doc["query"],
            request=doc["request"],
            status=doc["status"],
            created_at=doc["created_at"],
            candidates=[Candidate(**c) for c in doc.get("candidates") or []],
            selected_candidate_id=doc.get("selected_candidate_id"),
            sample=SampleResult(
                samples=[Sample(**s) for s in sample["samples"]],
                confidence=sample["confidence"],
                sufficient=sample["sufficient"],
                message=sample.get("message"),
                hints=sample.get("hints") or {},
            )
            if sample
            else None,
            analysis=doc.get("analysis"),
            proposals=doc.get("proposals") or [],
            plans={k: _plan_from_doc(p) for k, p in (doc.get("plans") or {}).items()},
            spent=float(doc.get("spent") or 0.0),
            currency=doc.get("currency") or "USD",
            job_id=doc.get("job_id"),
            error=doc.get("error"),
            acceptance=doc.get("acceptance"),
            version=version,
        )

    def candidate(self) -> Candidate | None:
        if self.selected_candidate_id is None:
            return None
        idx = int(self.selected_candidate_id.split("_", 1)[1]) - 1
        return self.candidates[idx] if 0 <= idx < len(self.candidates) else None

    def wire(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "session_id": self.session_id,
            "status": self.status,
            "query": self.query,
            "created_at": self.created_at,
        }
        if self.candidates:
            out["candidates"] = [c.wire(f"cand_{i + 1}") for i, c in enumerate(self.candidates)]
        if self.selected_candidate_id:
            out["selected_candidate_id"] = self.selected_candidate_id
        if self.sample is not None:
            out["sample"] = self.sample.wire()
        if self.analysis is not None:
            out["analysis"] = self.analysis
        if self.proposals:
            out["proposals"] = self.proposals
        if self.spent or self.sample is not None:
            out["costs"] = {"amount": round(self.spent, 6), "currency": self.currency}
        if self.job_id:
            out["job_id"] = self.job_id
        if self.error:
            out["error"] = self.error
        return out

    def summary(self) -> dict[str, Any]:
        """``OnboardingSessionSummary`` (``listOnboardingSessions``)."""
        full = self.wire()
        out: dict[str, Any] = {k: full[k] for k in ("session_id", "status", "query", "created_at")}
        for k in ("selected_candidate_id", "costs", "job_id", "error"):
            if k in full:
                out[k] = full[k]
        out["proposal_count"] = len(self.proposals)
        return out

    @property
    def position(self) -> tuple[str, str]:
        """Sort key of the list (newest first): ``created_at`` (fixed ``%Y-%m-%dT%H:%M:%SZ``), ``session_id``."""
        return (self.created_at, self.session_id)


def _plan_doc(p: ExtractorPlan) -> dict[str, Any]:
    return {
        "entity_type": p.entity_type,
        "material_type": p.material_type,
        "action": p.action,
        "package": p.package,
        "match_score": p.match_score,
        "outcome": {"context": p.outcome.context, "report": p.outcome.report} if p.outcome else None,
        "draft": {
            "manifest": p.draft.manifest,
            "files": {k: base64.b64encode(v).decode() for k, v in p.draft.files.items()},
        }
        if p.draft
        else None,
        "fork_from": p.fork_from,
    }


def _plan_from_doc(d: dict[str, Any]) -> ExtractorPlan:
    draft = d.get("draft")
    outcome = d.get("outcome")
    return ExtractorPlan(
        entity_type=d["entity_type"],
        material_type=d["material_type"],
        action=d["action"],
        package=d.get("package"),
        match_score=d.get("match_score"),
        outcome=TestOutcome(outcome["context"], outcome["report"]) if outcome else None,
        draft=PackageDraft(draft["manifest"], {k: base64.b64decode(v) for k, v in draft["files"].items()})
        if draft
        else None,
        fork_from=d.get("fork_from"),
    )


class SessionStore(Protocol):
    """Sessions shared by instances. ``save`` always writes (the job that owns a running session);
    ``save_if`` writes only if the stored version is still ``expected`` (API state transitions)."""

    async def get(self, session_id: str) -> Session | None: ...
    async def save(self, session: Session) -> None: ...
    async def save_if(self, session: Session, expected: int) -> bool: ...
    async def page(
        self, *, statuses: frozenset[str] | None, after: tuple[str, str] | None, limit: int
    ) -> list[Session]:
        """Newest first by :attr:`Session.position`, strictly after the ``after`` position (the cursor)."""
        ...


class InMemorySessionStore:
    """Single standalone instance and tests only (lost on restart). Several instances use
    :class:`jane_assistant.state.PostgresState` (``JANE_ASSISTANT_STATE_DSN``). Stores serialized
    documents, so it behaves like the shared store (copies, versions)."""

    def __init__(self) -> None:
        self._items: dict[str, tuple[int, dict[str, Any]]] = {}

    async def get(self, session_id: str) -> Session | None:
        item = self._items.get(session_id)
        return Session.from_doc(copy.deepcopy(item[1]), item[0]) if item else None

    async def save(self, session: Session) -> None:
        version = self._items.get(session.session_id, (0, {}))[0] + 1
        self._items[session.session_id] = (version, session.to_doc())
        session.version = version

    async def save_if(self, session: Session, expected: int) -> bool:
        if self._items.get(session.session_id, (0, {}))[0] != expected:
            return False
        await self.save(session)
        return True

    async def page(
        self, *, statuses: frozenset[str] | None, after: tuple[str, str] | None, limit: int
    ) -> list[Session]:
        rows = sorted(((doc["created_at"], sid), version, doc) for sid, (version, doc) in self._items.items())
        out: list[Session] = []
        for position, version, doc in reversed(rows):
            if after is not None and position >= after:
                continue
            if statuses and doc["status"] not in statuses:
                continue
            out.append(Session.from_doc(copy.deepcopy(doc), version))
            if len(out) >= limit:
                break
        return out


Progress = Callable[[int, str], Awaitable[None]]


class OnboardingService:
    def __init__(
        self,
        *,
        settings: Settings,
        neighbours: Neighbours,
        search: SearchProvider,
        runner: JobRunner,
        store: SessionStore,
        validator: SchemaValidator,
    ) -> None:
        self.settings = settings
        self.nb = neighbours
        self.search = search
        self.runner = runner
        self.store = store
        self.validator = validator

    # ------------------------------------------------------------------ API entry points
    async def start(self, request: dict[str, Any], idempotency_key: str | None) -> tuple[dict[str, Any], str]:
        limits = self._limits(request)  # invalid request limits fail now, not inside the job
        session = Session(
            session_id=f"onb_{uuid.uuid4().hex}",
            query=request["query"],
            request=request,
            currency=limits.llm.budget.currency,
        )
        job = await self._submit(session, "onboarding", self._resolve_and_continue, idempotency_key)
        return job, session.session_id

    async def get(self, session_id: str) -> Session:
        session = await self.store.get(session_id)
        if session is None:
            raise NotFound(f"onboarding session {session_id} not found")
        return await self._refresh(session)

    async def page(
        self, statuses: frozenset[str] | None, after: tuple[str, str] | None, limit: int
    ) -> tuple[list[Session], tuple[str, str] | None]:
        """One page of ``listOnboardingSessions`` (newest first) and the position after it (``None`` = last page).

        Running sessions are refreshed like ``GET`` (a job that ended without its handler updating the session),
        so the list never shows a session as running whose job already failed or was cancelled."""
        found = await self.store.page(statuses=statuses, after=after, limit=limit + 1)
        sessions = [await self._refresh(s) if s.status in RUNNING else s for s in found[:limit]]
        if statuses:
            sessions = [s for s in sessions if s.status in statuses]
        return sessions, (found[limit - 1].position if len(found) > limit else None)

    async def select(self, session_id: str, candidate_id: str) -> Session:
        session = await self.get(session_id)
        if session.selected_candidate_id == candidate_id and session.status != "needs_disambiguation":
            return session  # same choice again: same state
        if session.status != "needs_disambiguation":
            raise Conflict(
                f"session is {session.status}; a candidate can be selected only when disambiguation is needed"
            )
        if candidate_id not in {f"cand_{i + 1}" for i in range(len(session.candidates))}:
            raise NotFound(f"candidate {candidate_id} not found in session {session_id}")
        session.selected_candidate_id = candidate_id
        session.status = "sampling"
        if not await self.store.save_if(session, session.version):
            # another instance (or request) changed the session first: same choice -> its state
            current = await self.get(session_id)
            if current.selected_candidate_id == candidate_id and current.status != "needs_disambiguation":
                return current
            raise Conflict(f"session {session_id} was changed concurrently (now {current.status})")
        await self._submit(session, "onboarding", self._continue_after_selection, None)
        return session

    async def accept(
        self,
        session_id: str,
        proposal_id: str,
        activate: bool,
        source_id: str | None,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        session = await self.get(session_id)
        if session.status != "proposals_ready":
            raise Conflict(f"session is {session.status}; proposals can be accepted only when they are ready")
        proposal = next((p for p in session.proposals if p["proposal_id"] == proposal_id), None)
        if proposal is None:
            raise NotFound(f"proposal {proposal_id} not found in session {session_id}")
        session.status = "applying"
        if not await self.store.save_if(session, session.version):
            raise Conflict(f"session {session_id} was changed concurrently; read it again")

        async def work(ctx: JobContext, s: Session) -> dict[str, Any]:
            return await self._apply(ctx, s, proposal, activate, source_id)

        return await self._submit(session, "onboarding_acceptance", work, idempotency_key)

    # ------------------------------------------------------------------ jobs

    def _limits(self, request: dict[str, Any]) -> ServiceLimits:
        return resolve_service_limits(self.settings, *request_layer(request.get("limits"))).limits

    async def _submit(
        self,
        session: Session,
        kind: str,
        fn: Callable[[JobContext, Session], Awaitable[dict[str, Any]]],
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        async def work(ctx: JobContext) -> dict[str, Any]:
            try:
                return await fn(ctx, session)
            except (asyncio.CancelledError, JobCancelledError):
                session.status = "cancelled"
                job = await self.runner.store.get(ctx.job_id)
                cancel = job.cancellation if job else None
                reason = cancel.reason if cancel and cancel.reason else "instance shutdown or restart"
                session.error = (
                    JaneError(
                        f"onboarding job cancelled: {reason}", code="service_unavailable", retryable=True
                    )
                    .to_problem()
                    .model_dump(mode="json", exclude_none=True)
                )
                await self.store.save(session)
                raise
            except JaneError as exc:
                session.status = "failed"
                session.error = exc.to_problem().model_dump(mode="json", exclude_none=True)
                await self.store.save(session)
                raise
            except Exception as exc:
                session.status = "failed"
                session.error = (
                    JaneError(f"{type(exc).__name__}: {exc}")
                    .to_problem()
                    .model_dump(mode="json", exclude_none=True)
                )
                await self.store.save(session)
                raise

        job = await self.runner.submit(
            kind,
            work,
            idempotency_key=idempotency_key,
            labels={"session_id": session.session_id},
        )
        session.job_id = job.job_id
        session.error = None
        fresh = await self.runner.store.get(job.job_id) or job
        fresh.links = {**(fresh.links or {}), "session": f"/v1/onboarding-sessions/{session.session_id}"}
        await self.runner.store.save(fresh)
        job = fresh
        await self.store.save(session)
        return job.wire()

    async def _refresh(self, session: Session) -> Session:
        """Mirror a job that ended without its handler updating the session: cancelled before it
        started, or failed because its instance stopped (lease expired, see ``state.py``)."""
        if session.job_id and session.status in RUNNING:
            job = await self.runner.store.get(session.job_id)
            if job is not None and job.status in {"cancelled", "failed"}:
                expected = session.version
                session.status = str(job.status)
                if job.error is not None:
                    session.error = job.error.model_dump(mode="json", exclude_none=True)
                else:
                    reason = job.cancellation.reason if job.cancellation else None
                    session.error = (
                        JaneError(f"onboarding job cancelled: {reason or 'no reason given'}", code="conflict")
                        .to_problem()
                        .model_dump(mode="json", exclude_none=True)
                    )
                if not await self.store.save_if(session, expected):
                    return await self.get(session.session_id)
        return session

    async def _resolve_and_continue(self, ctx: JobContext, session: Session) -> dict[str, Any]:
        limits = self._limits(session.request)
        ob = limits.onboarding
        kind = session.request.get("source_kind")
        direct = direct_candidate(session.query, kind)
        if direct is not None:
            session.candidates = [direct]
            session.selected_candidate_id = "cand_1"
        else:
            found = await self.search.search(session.query, kind, ob.max_candidates)
            session.candidates = found[: ob.max_candidates]
            if not session.candidates:
                raise NotFound(f"no source found for {session.query!r}")
            top = session.candidates[0]
            second = session.candidates[1].confidence if len(session.candidates) > 1 else 0.0
            if (
                top.confidence >= ob.auto_select_confidence
                and top.confidence - second >= ob.auto_select_margin
            ):
                session.selected_candidate_id = "cand_1"
            else:
                session.status = "needs_disambiguation"
                await self.store.save(session)
                return session.wire()
        session.status = "sampling"
        await self.store.save(session)
        return await self._continue_after_selection(ctx, session)

    async def _continue_after_selection(self, ctx: JobContext, session: Session) -> dict[str, Any]:
        limits = self._limits(session.request)
        cand = session.candidate()
        if cand is None:
            raise JaneError("no candidate selected", code="conflict")
        kind = cand.source_kind
        host = host_of(cand.url)
        allowed = sorted(
            {
                h
                for h in [
                    host,
                    *(
                        ((session.request.get("crawl_hints") or {}).get("scope") or {}).get("allowed_domains")
                        or []
                    ),
                ]
                if h
            }
        )
        source_id = slug(host or cand.telegram_username or session.query)
        llm = LlmSession(
            self.nb.llm,
            limits.llm,
            "onboarding",
            session.session_id + (session.job_id or ""),
            source_id=None,
            run_id=session.session_id,  # one onboarding run = the session, whichever job continues it
            mode=self.settings.llm_completion_mode,
        )

        async def progress(done: int, message: str) -> None:
            session.spent = llm.spent
            await ctx.progress(done, None, unit="materials", message=message)
            await ctx.check_cancelled()  # a cancel request may come through another instance
            await self.store.save(session)

        rules = sampling_rules(
            kind, cand.url, cand.telegram_username, allowed, session.request.get("crawl_hints")
        )
        try:
            session.sample = await sample_source(
                collector=self.nb.collector(kind),
                llm=llm,
                limits=limits,
                job_key=session.job_id or session.session_id,
                source_id=source_id,
                source_kind=kind,
                rules=rules,
                model=self.settings.llm_model_cheap,
                progress=progress,
            )
        finally:
            session.spent = llm.spent
        if not session.sample.sufficient:
            session.status = "insufficient_sample"
            await self.store.save(session)
            return session.wire()
        session.status = "analyzing"
        await self.store.save(session)
        try:
            await self._analyze(session, llm, limits, kind, host, source_id, allowed)
        except BudgetExhausted as exc:
            session.spent = llm.spent
            session.sample.sufficient = False
            session.sample.message = f"LLM budget exhausted during analysis: {exc}"
            session.status = "insufficient_sample"
            await self.store.save(session)
            return session.wire()
        session.spent = llm.spent
        session.status = "proposals_ready"
        await self.store.save(session)
        if session.request.get("auto_activation") and session.proposals:
            recommended = next((p for p in session.proposals if p.get("recommended")), session.proposals[0])
            session.status = "applying"
            await self.store.save(session)
            await self._apply(ctx, session, recommended, True, None)
        return session.wire()

    # ------------------------------------------------------------------ analysis
    async def _analyze(
        self,
        session: Session,
        llm: LlmSession,
        limits: ServiceLimits,
        kind: str,
        host: str | None,
        source_id: str,
        allowed: list[str],
    ) -> None:
        assert session.sample is not None
        sample = session.sample
        ob = limits.onboarding
        counts = sample.counts()
        context = {
            "material_types": dict(counts),
            "hints": {k: v for k, v in sample.hints.items() if k != "shapes"},
        }
        data = [part("context", as_json(context), "application/json")]
        for mtype in sorted(counts):
            for i, s in enumerate(sample.of_type(mtype)[: ob.max_examples_per_type]):
                data.append(part(f"ex_{mtype}_{i}", f"url: {material_label(s.material)}\n\n{s.text}"))
        out = await llm.ask("analyze", ANALYZE, data, ANALYZE_SCHEMA, model=self.settings.llm_model_strong)
        observed = {
            str(k).removeprefix("sample-") for k, v in (sample.hints.get("by_strategy") or {}).items() if v
        }
        methods = sorted((set(out.get("discovery_methods") or []) | observed) & DISCOVERY_METHODS)
        expected = set(session.request.get("expected_entity_types") or [])
        entities = [e for e in out.get("entities") or [] if e.get("material_type") in counts]
        wanted = [e for e in entities if not expected or e["entity_type"] in expected]
        session.analysis = {
            "source_kind": kind,
            "discovery_methods": methods,
            "material_types": [
                {
                    "type": t,
                    "count": c,
                    "example_urls": [
                        material_label(s.material) for s in sample.of_type(t)[: ob.max_examples_per_type]
                    ],
                }
                for t, c in counts.most_common()
            ],
            "entities": [
                {
                    "entity_type": e["entity_type"],
                    "fields": [
                        {k: f[k] for k in ("name", "type", "examples", "coverage") if k in f}
                        for f in e["fields"]
                    ],
                }
                for e in entities
            ],
        }
        await self.store.save(session)
        for e in wanted:
            plan = await self._plan_extractor(session, llm, limits, e, kind, host, source_id)
            session.plans[e["entity_type"]] = plan
            session.spent = llm.spent
            await self.store.save(session)
        session.proposals = await self._propose(session, llm, limits, kind, host, allowed, source_id)

    # ------------------------------------------------------------------ extractors
    def _cases(
        self, sample: SampleResult, material_type: str, limits: ServiceLimits
    ) -> tuple[list[Sample], list[Sample]]:
        ob = limits.onboarding
        positives = sample.of_type(material_type)[: ob.max_examples_per_type]
        negatives = [s for s in sample.samples if s.material_type != material_type][
            : ob.max_negative_examples
        ]
        return positives, negatives

    async def _plan_extractor(
        self,
        session: Session,
        llm: LlmSession,
        limits: ServiceLimits,
        entity: dict[str, Any],
        kind: str,
        host: str | None,
        source_id: str,
    ) -> ExtractorPlan:
        assert session.sample is not None
        ob = limits.onboarding
        etype, mtype = entity["entity_type"], entity["material_type"]
        positives, negatives = self._cases(session.sample, mtype, limits)
        extra = [extra_case(f"sample-{i}", s.material, "success") for i, s in enumerate(positives)]
        extra += [extra_case(f"negative-{i}", s.material, "empty") for i, s in enumerate(negatives)]
        best: tuple[float, dict[str, Any], TestOutcome] | None = None
        if self.nb.registry.configured:
            found: dict[str, dict[str, Any]] = {}
            for params in ({"domain": host or ""}, {}):
                for p in await self.nb.registry.search(kind="extractor", entity_type=etype, **params):
                    if p.get("latest_version") and not p.get("deprecated"):
                        found.setdefault(p["package_id"], p)
            for pkg in list(found.values())[: ob.max_candidate_packages]:
                ref = {"package_id": pkg["package_id"], "version": pkg["latest_version"]}
                outcome = await run_tests(
                    self.nb.handler,
                    job_key=session.job_id or session.session_id,
                    context=f"onboarding:{etype}",
                    package=ref,
                    tests="none",
                    extra_cases=extra,
                    inline_max_bytes=limits.transfer.inline_max_bytes,
                )
                if best is None or outcome.pass_rate > best[0]:
                    best = (outcome.pass_rate, ref, outcome)
        package_id = slug(f"{source_id}.{etype}-extractor")
        if best is not None and best[0] >= ob.bind_threshold:
            return ExtractorPlan(etype, mtype, "bind_existing", best[1], best[0], best[2])
        if best is not None and best[0] >= ob.fork_threshold:
            plan = await self._adapt_fork(
                session, llm, limits, etype, mtype, best, package_id, positives, negatives
            )
            if plan is not None:
                return plan
        return await self._generate(
            session, llm, limits, entity, kind, host, package_id, positives, negatives, best
        )

    async def _next_version(self, package_id: str, first: str = "1.0.0") -> str:
        if not self.nb.registry.configured:
            return first
        try:
            pkg = await self.nb.registry.get_package(package_id)
        except RemoteError as exc:
            if exc.status == 404:
                return first
            raise
        return (
            bump(str(pkg.get("latest_version") or "0.0.0"), "minor") if pkg.get("latest_version") else first
        )

    async def _adapt_fork(
        self,
        session: Session,
        llm: LlmSession,
        limits: ServiceLimits,
        etype: str,
        mtype: str,
        best: tuple[float, dict[str, Any], TestOutcome],
        package_id: str,
        positives: list[Sample],
        negatives: list[Sample],
    ) -> ExtractorPlan | None:
        score, parent, outcome = best
        files, _ = await self.nb.registry.archive_files(parent["package_id"], parent["version"])
        base = PackageDraft.from_files(files)
        failed = {c["name"] for c in outcome.report.get("cases") or [] if not c.get("passed")}
        problems: list[ProblemCase] = []
        successes: list[ProblemCase] = []
        for i, s in enumerate(positives):
            case = ProblemCase(
                f"sample-{i}", s.material, s.text, source_id=None, signature="onboarding:sample"
            )
            (problems if f"sample-{i}" in failed else successes).append(case)
        if not problems:
            return None
        base.manifest["package_id"] = package_id
        base.manifest["version"] = parent["version"]
        adapted = await improve_draft(
            nb=self.nb,
            llm=llm,
            settings=self.settings,
            limits=limits,
            validator=self.validator,
            base=base,
            version_after=lambda change: bump(
                parent["version"], {"breaking": "major", "additive": "minor"}.get(change, "patch")
            ),
            problems=problems,
            successes=successes,
            bindings=[],
            attempts=limits.onboarding.max_generation_attempts,
            job_key=session.job_id or session.session_id,
            job_id=session.job_id or session.session_id,
            reason="onboarding",
        )
        if adapted.draft is None:
            return None
        return ExtractorPlan(
            etype, mtype, "fork", adapted.draft.ref, score, adapted.outcomes[0], adapted.draft, parent
        )

    async def _generate(
        self,
        session: Session,
        llm: LlmSession,
        limits: ServiceLimits,
        entity: dict[str, Any],
        kind: str,
        host: str | None,
        package_id: str,
        positives: list[Sample],
        negatives: list[Sample],
        best: tuple[float, dict[str, Any], TestOutcome] | None,
    ) -> ExtractorPlan:
        etype, mtype = entity["entity_type"], entity["material_type"]
        version = await self._next_version(package_id)
        feedback: Any = None
        last: TestOutcome | None = None
        draft: PackageDraft | None = None
        job_key = session.job_id or session.session_id
        for _attempt in range(limits.onboarding.max_generation_attempts):
            data = [
                part(
                    "spec",
                    as_json({"entity_type": etype, "material_type": mtype, "fields": entity["fields"]}),
                    "application/json",
                )
            ]
            data += [
                part(f"sample_{i}", f"url: {material_label(s.material)}\n\n{s.text}")
                for i, s in enumerate(positives)
            ]
            data += [
                part(f"neg_{i}", f"url: {material_label(s.material)}\n\n{s.text}")
                for i, s in enumerate(negatives)
            ]
            if feedback is not None:
                data.append(part("previous_attempt", as_json(feedback), "application/json"))
            try:
                out = await llm.ask(
                    "generate_extractor",
                    GENERATE,
                    data,
                    GENERATE_SCHEMA,
                    model=self.settings.llm_model_strong,
                )
            except InvalidModelOutput as exc:
                feedback = {"error": str(exc)}
                continue
            check = check_code(out["module_code"], "extract", self.settings.generated_code_allowed_modules)
            if not check.ok:
                feedback = {"rejected_code": check.problems}
                continue
            media = sorted(
                {(s.material.get("format") or {}).get("media_type", "text/html") for s in positives}
            ) or ["text/html"]
            draft = extractor_draft(
                package_id=package_id,
                version=version,
                title=f"{session.candidate().title if session.candidate() else package_id}: {etype}",  # type: ignore[union-attr]
                entity_type=etype,
                key_fields=list(out["key_fields"]),
                entity_schema=dict(out["entity_schema"]),
                module_code=out["module_code"],
                domains=[host] if host else [],
                source_kind=kind,
                media_types=media,
                job_id=job_key,
                model=model_ref(llm.model_used),
                reason="onboarding",
            )
            exp = {str(e["name"]): e for e in out.get("expectations") or []}
            for i, s in enumerate(positives):
                e = exp.get(f"sample_{i}")
                if e:
                    draft.add_test(
                        f"sample-{i}",
                        s.material,
                        str(e["expected_status"]),
                        list(e.get("entities") or []),
                        "llm",
                    )
            for i, s in enumerate(negatives):
                e = exp.get(f"neg_{i}")
                if e:
                    draft.add_test(
                        f"negative-{i}",
                        s.material,
                        str(e["expected_status"]),
                        list(e.get("entities") or []),
                        "llm",
                    )
            statuses = {t["expected_status"] for t in draft.manifest["tests"]}
            problems = []
            if "success" not in statuses or not statuses & {"empty", "unrecognized"}:
                problems.append("tests must include at least one success and one empty or unrecognized case")
            problems += [
                f"manifest {e}" for e in self.validator.errors("package-manifest.schema.json", draft.manifest)
            ]
            if problems:
                feedback = {"rejected": problems}
                continue
            last = await run_tests(
                self.nb.handler,
                job_key=job_key,
                context=f"generated:{etype}",
                draft=draft,
                inline_max_bytes=limits.transfer.inline_max_bytes,
            )
            if last.passed:
                break
            feedback = {"failed_tests": last.failures()}
        return ExtractorPlan(
            etype,
            mtype,
            "create",
            draft.ref if draft else {"package_id": package_id, "version": version},
            best[0] if best else None,
            last,
            draft,
        )

    # ------------------------------------------------------------------ proposals
    async def _propose(
        self,
        session: Session,
        llm: LlmSession,
        limits: ServiceLimits,
        kind: str,
        host: str | None,
        allowed: list[str],
        source_id: str,
    ) -> list[dict[str, Any]]:
        assert session.sample is not None
        ob = limits.onboarding
        sample = session.sample
        extractors = [p.wire() for p in session.plans.values()]
        entity_types = sorted(session.plans)
        discovered = int(sample.hints.get("discovered") or len(sample.samples))
        setup_cost = {"amount": round(llm.spent, 6), "currency": llm.currency}
        per_run = {"amount": 0, "currency": llm.currency}
        risks_common = [
            f"extractor for {p.entity_type} failed its tests on samples"
            for p in session.plans.values()
            if not p.tests_passed
        ]
        proposals: list[dict[str, Any]] = []
        if kind == "telegram":
            cand = session.candidate()
            channel = {"username": cand.telegram_username} if cand else {}
            variants = [
                (
                    "Full history and updates",
                    {"history": {"enabled": True}, "updates": {"new_messages": True, "edits": True}},
                    True,
                    ["history import may take long on big channels"],
                ),
                (
                    "New messages and edits only",
                    {"history": {"enabled": False}, "updates": {"new_messages": True, "edits": True}},
                    False,
                    ["older messages are never collected"],
                ),
            ]
            for i, (title, extra, rec, risks) in enumerate(variants):
                rules = {"collector": "telegram", "channels": [channel], **extra}
                proposals.append(
                    self._proposal(
                        f"p{i + 1}",
                        title,
                        None,
                        rec,
                        rules,
                        extractors,
                        discovered,
                        entity_types,
                        setup_cost,
                        per_run,
                        risks + risks_common,
                        ob,
                    )
                )
            return proposals
        hints = {
            "by_strategy": sample.hints.get("by_strategy"),
            "discovered": discovered,
            "shapes": sample.hints.get("shapes"),
        }
        out = await llm.ask(
            "propose",
            PROPOSE,
            [
                part("analysis", as_json(session.analysis), "application/json"),
                part("hints", as_json(hints), "application/json"),
            ],
            PROPOSE_SCHEMA,
            model=self.settings.llm_model_strong,
        )
        setup_cost = {"amount": round(llm.spent, 6), "currency": llm.currency}
        for raw in (out.get("proposals") or [])[: ob.max_proposals]:
            check = sanitize_web_rules(raw, allowed, session.request.get("crawl_hints"))
            if check.rules is None:
                log.info("proposal rejected", extra={"title": raw.get("title"), "reasons": check.rejected})
                continue
            errors = self.validator.errors("collector-rules.schema.json", check.rules)
            if not errors and self.nb.collector(kind).configured:
                verdict = await self.nb.collector(kind).validate_rules(check.rules)
                if not verdict.get("valid") or verdict.get("supported") is False:
                    errors = [str(e.get("message")) for e in verdict.get("errors") or []] or [
                        "not supported by the collector"
                    ]
            if errors:
                log.info("proposal rules invalid", extra={"title": raw.get("title"), "errors": errors[:5]})
                continue
            risks = [str(r) for r in raw.get("risks") or []] + risks_common
            risks += [f"ignored model suggestion: {r}" for r in check.rejected]
            share = self._share(sample, check.rules)
            proposals.append(
                self._proposal(
                    f"p{len(proposals) + 1}",
                    str(raw["title"]),
                    raw.get("summary"),
                    bool(raw.get("recommended")),
                    check.rules,
                    extractors,
                    max(1, round(discovered * share)),
                    entity_types,
                    setup_cost,
                    per_run,
                    risks,
                    ob,
                    notes=f"estimated from {discovered} URL(s) discovered while sampling; {round(share * 100)}% of sampled materials match the plan's sections",
                )
            )
        if not proposals and host:
            rules = {
                "collector": "web",
                "scope": {"allowed_domains": allowed},
                "strategies": [{"type": "recursive", "seeds": [f"https://{host}/"]}],
                "robots": {"mode": "respect"},
            }
            proposals.append(
                self._proposal(
                    "p1",
                    "Recursive crawl from the entry point",
                    "Fallback plan: no model proposal passed validation.",
                    True,
                    rules,
                    extractors,
                    discovered,
                    entity_types,
                    setup_cost,
                    per_run,
                    ["fallback plan: model proposals were rejected by validation", *risks_common],
                    ob,
                )
            )
        if proposals and not any(p.get("recommended") for p in proposals):
            proposals[0]["recommended"] = True
        seen = False
        for p in proposals:  # exactly one recommended
            if p.get("recommended"):
                p["recommended"] = not seen
                seen = True
        return proposals

    @staticmethod
    def _share(sample: SampleResult, rules: dict[str, Any]) -> float:
        sections = rules.get("sections") or []
        if not sections:
            return 1.0
        import fnmatch

        pats = [p["value"] for s in sections for p in s["patterns"]]
        urls = [material_label(s.material).split("://", 1)[-1] for s in sample.samples]
        hits = sum(1 for u in urls if any(fnmatch.fnmatch(u, p.replace("**", "*")) for p in pats))
        return hits / len(urls) if urls else 0.0

    @staticmethod
    def _proposal(
        pid: str,
        title: str,
        summary: str | None,
        recommended: bool,
        rules: dict[str, Any],
        extractors: list[dict[str, Any]],
        estimated: int,
        entity_types: list[str],
        setup_cost: dict[str, Any],
        per_run: dict[str, Any],
        risks: list[str],
        ob: Any,
        notes: str | None = None,
    ) -> dict[str, Any]:
        coverage: dict[str, Any] = {"estimated_materials": estimated, "entity_types": entity_types}
        if notes:
            coverage["notes"] = notes
        out: dict[str, Any] = {
            "proposal_id": pid,
            "title": title[:200],
            "recommended": recommended,
            "collector_rules": rules,
            "extractors": copy.deepcopy(extractors),
            "coverage": coverage,
            "cost": {
                "requests_per_run_estimate": math.ceil(estimated * (1 + ob.requests_overhead_ratio)),
                "llm_setup_cost": setup_cost,
                "llm_cost_per_run": per_run,
            },
            "risks": risks,
        }
        if summary:
            out["summary"] = str(summary)[:2000]
        return out

    # ------------------------------------------------------------------ acceptance
    async def _apply(
        self,
        ctx: JobContext,
        session: Session,
        proposal: dict[str, Any],
        activate: bool,
        source_id: str | None,
    ) -> dict[str, Any]:
        cand = session.candidate()
        assert cand is not None
        job_key = session.job_id or session.session_id
        host = host_of(cand.url)
        source_id = source_id or slug(host or cand.telegram_username or session.query)
        rules = proposal["collector_rules"]
        rules_id = slug(f"{source_id}.{rules['collector']}-rules")
        await ctx.progress(0, None, unit="steps", message="publishing collector rules")
        rules_draft = collector_rules_draft(
            package_id=rules_id,
            version=await self._next_version(rules_id),
            title=f"{cand.title} collection rules",
            rules=rules,
            job_id=job_key,
            model={},
        )
        rules_ref = await self._publish(
            job_key, rules_draft, "collector-rules", f"{cand.title} collection rules"
        )
        extractors: list[dict[str, Any]] = []
        entity_types: list[str] = []
        all_passed = True
        for i, plan_wire in enumerate(proposal["extractors"]):
            plan = session.plans[plan_wire["entity_type"]]
            await ctx.progress(
                i + 1, None, unit="steps", message=f"extractor {plan.entity_type}: {plan.action}"
            )
            all_passed &= plan.tests_passed
            if plan.action == "bind_existing":
                ref = dict(plan.package or {})
            elif plan.action == "fork":
                assert plan.draft is not None
                assert plan.fork_from is not None
                new_id = slug(f"{source_id}.{plan.entity_type}-extractor")
                fork = await self.nb.registry.fork(
                    plan.fork_from["package_id"],
                    {
                        "new_package_id": new_id,
                        "from_version": plan.fork_from["version"],
                        "title": f"{cand.title}: {plan.entity_type}"[:200],
                        "auto_changes_allowed": True,
                    },
                    idem_key(job_key, "fork", new_id),
                )
                draft = plan.draft.copy()
                draft.manifest["package_id"] = new_id
                if fork.get("fork_of"):
                    draft.manifest["fork_of"] = fork["fork_of"]
                draft.manifest["provenance"]["based_on"] = {
                    "package_id": new_id,
                    "version": str(fork.get("latest_version") or plan.fork_from["version"]),
                }
                ref = await self._publish(job_key, draft, "extractor", draft.manifest["title"], create=False)
            else:
                if plan.draft is None:
                    raise JaneError(
                        f"no extractor could be generated for {plan.entity_type}", code="conflict"
                    )
                draft = plan.draft.copy()
                new_id = slug(f"{source_id}.{plan.entity_type}-extractor")
                if new_id != draft.manifest["package_id"]:  # the user chose another source_id
                    draft.manifest["package_id"] = new_id
                    draft.manifest["version"] = await self._next_version(new_id)
                ref = await self._publish(job_key, draft, "extractor", draft.manifest["title"])
            entry: dict[str, Any] = {"action": plan.action, "package": ref}
            entity_types.append(plan.entity_type)
            if plan.outcome is not None:
                report = {**plan.outcome.report, "package": ref}
                entry["test_report"] = report
                if plan.action != "bind_existing":
                    await self.nb.registry.record_tests(
                        ref["package_id"],
                        ref["version"],
                        {"runner": "assistant", "context": plan.outcome.context, "report": report},
                        idem_key(job_key, "tests", ref["package_id"]),
                    )
            extractors.append(entry)
        source_draft = self._source_draft(session, cand, source_id, rules_ref)
        task_draft = self._task_draft(
            session, cand, source_id, rules_ref, proposal, list(zip(entity_types, extractors, strict=True))
        )
        activated = False
        if (
            activate
            and all_passed
            and self.settings.onboarding_allow_activation
            and self.nb.orchestrator.configured
        ):
            for e in extractors:
                if e["action"] != "bind_existing":
                    await self.nb.registry.set_status(
                        e["package"]["package_id"],
                        e["package"]["version"],
                        "approved",
                        f"accepted in onboarding session {session.session_id}; tests passed",
                        idem_key(job_key, "approve", e["package"]["package_id"]),
                    )
            await self.nb.registry.set_status(
                rules_ref["package_id"],
                rules_ref["version"],
                "approved",
                f"accepted in onboarding session {session.session_id}",
                idem_key(job_key, "approve", rules_id),
            )
            await self.nb.orchestrator.create_source(source_draft, idem_key(job_key, "source", source_id))
            await self.nb.orchestrator.create_task(
                task_draft, idem_key(job_key, "task", task_draft["task_id"])
            )
            activated = True
        result = {
            "collector_rules": rules_ref,
            "extractors": extractors,
            "source_draft": source_draft,
            "task_drafts": [task_draft],
            "activated": activated,
        }
        session.acceptance = result
        session.status = "completed"
        await self.store.save(session)
        return result

    async def _publish(
        self, job_key: str, draft: PackageDraft, kind: str, title: str, create: bool = True
    ) -> dict[str, Any]:
        package_id = draft.manifest["package_id"]
        if self.validator.available:
            errors = self.validator.errors("package-manifest.schema.json", draft.manifest)
            if errors:
                raise JaneError(
                    f"generated manifest of {package_id} is invalid: {errors[:3]}", code="validation_failed"
                )
        if create:
            await self.nb.registry.create_package(
                {"package_id": package_id, "kind": kind, "title": title[:200]},
                idem_key(job_key, "package", package_id),
            )
        v = await self.nb.registry.publish(
            package_id,
            draft.publish_body(),
            idem_key(job_key, "publish", package_id, draft.manifest["version"]),
        )
        return {"package_id": v["package_id"], "version": v["version"], "digest": v["digest"]}

    def _source_draft(
        self, session: Session, cand: Candidate, source_id: str, rules_ref: dict[str, Any]
    ) -> dict[str, Any]:
        locator: dict[str, Any] = (
            {"url": cand.url} if cand.url else {"telegram_username": cand.telegram_username}
        )
        types = sorted(set(session.plans) | set(session.request.get("expected_entity_types") or []))
        draft: dict[str, Any] = {
            "source_id": source_id,
            "kind": cand.source_kind,
            "title": cand.title[:200],
            "locator": locator,
            "collector_rules": rules_ref,
            "forward_unknown_to_llm": False,
            "change_policy": {
                "llm_versions": "auto_after_checks"
                if session.request.get("auto_activation")
                else "manual_approval"
            },
        }
        if types:
            draft["expected_entity_types"] = types
        if cand.description:
            draft["description"] = cand.description[:4000]
        return draft

    def _task_draft(
        self,
        session: Session,
        cand: Candidate,
        source_id: str,
        rules_ref: dict[str, Any],
        proposal: dict[str, Any],
        extractors: list[tuple[str, dict[str, Any]]],
    ) -> dict[str, Any]:
        rules = proposal["collector_rules"]
        stages: list[dict[str, Any]] = [
            {
                "stage_id": "collect",
                "kind": "collect",
                "collector": {"collector": rules["collector"], "rules": rules_ref, "mode": "full"},
            }
        ]
        sections = {s["section_id"]: s for s in rules.get("sections") or []}
        for etype, e in extractors:
            plan = session.plans[etype]
            section = sections.get(plan.entity_type) or sections.get(plan.material_type)
            if section:
                binding: dict[str, Any] = {"url_patterns": section["patterns"]}
            else:
                media = sorted(
                    {
                        (s.material.get("format") or {}).get("media_type", "text/html")
                        for s in (session.sample.of_type(plan.material_type) if session.sample else [])
                    }
                )
                binding = {"media_types": media or ["text/html"]}
            stages.append(
                {
                    "stage_id": slug(f"extract-{plan.entity_type}"),
                    "kind": "handler",
                    "handler": e["package"],
                    "inputs": [{"from": "collect"}],
                    "bindings": [binding],
                }
            )
        if self.settings.default_storage_package and "@" in self.settings.default_storage_package:
            pkg, ver = self.settings.default_storage_package.split("@", 1)
            for st in [s for s in stages if s["kind"] == "handler"]:
                storage_stage: dict[str, Any] = {
                    "stage_id": slug(f"store-{st['stage_id'].removeprefix('extract-')}"),
                    "kind": "handler",
                    "handler": {"package_id": pkg, "version": ver},
                    "inputs": [{"from": st["stage_id"]}],
                }
                if self.settings.default_storage_connection:
                    storage_stage["connections"] = {"target": self.settings.default_storage_connection}
                stages.append(storage_stage)
        return {
            "task_id": slug(f"{source_id}-collect"),
            "title": f"{cand.title}: {proposal['title']}"[:200],
            "description": (proposal.get("summary") or "Created by the source assistant.")[:4000],
            "enabled": True,
            "input": {"source_id": source_id},
            "stages": stages,
            "schedule": {"type": "manual"},
        }
