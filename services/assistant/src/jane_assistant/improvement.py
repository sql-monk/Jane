"""Improvement of an extractor on problem samples (ТЗ §9, plan.md WP-11 «Вдосконалення»).

1. Problem samples are grouped by source and character (unrecognized signature, failure kind or
   diagnostic codes); the model gets the grouped samples, the current code and schemas, the
   diagnostics and successful examples (which must keep working).
2. Each attempt produces a candidate version; it must pass the old tests, new tests made from the
   problem samples (``origin: problem_sample``) and regressions on successful examples, then the
   test suite with the params of every binding of a shared package (``listTasks?package_id=``).
3. A version that breaks bindings of other sources (or changes the schema incompatibly while the
   package is shared) becomes a fork for this source when ``policy.allow_fork``; otherwise the run is
   unresolved.
4. ``auto_changes_allowed = false`` -> proposal only, nothing is published. ``policy.approval =
   auto_after_checks`` -> the version is approved and auto-activated on its bindings (the
   orchestrator re-checks the source policy); a partial activation is rolled back.
5. Attempts (``limits.llm.max_improvement_attempts``) and spend (``limits.llm.budget``) are bounded;
   an unresolved run is reported to the orchestrator's problem group (shown in the admin UI).
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from jane_kit.errors import JaneError, ValidationFailed

from .clients import Neighbours, RemoteError, idem_key
from .content import decode_text, material_bytes, material_label, truncate
from .guards import SchemaValidator, check_code
from .llm import BudgetExhausted, InvalidModelOutput, LlmSession, as_json, part
from .packages import PackageDraft, bump, case_name, slug
from .prompts import IMPROVE, IMPROVE_SCHEMA
from .settings import ServiceLimits, Settings
from .testing import TestOutcome, extra_case, run_tests

__all__ = [
    "ImproveOutcome",
    "ProblemCase",
    "group_problems",
    "improve_draft",
    "run_improvement",
    "signature_of",
]

log = logging.getLogger(__name__)
_ENTITY_SLUG = r"^[a-z][a-z0-9_]{0,63}$"


@dataclass
class ProblemCase:
    name: str
    material: dict[str, Any]
    text: str
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] | None = None
    signature: str = "unknown"
    source_id: str | None = None


def signature_of(result: dict[str, Any] | None, diagnostics: list[dict[str, Any]]) -> str:
    result = result or {}
    unrec = result.get("unrecognized") or {}
    if unrec.get("signature"):
        return f"unrecognized:{unrec['signature']}"
    if result.get("failure"):
        return f"failed:{result['failure'].get('kind', 'unknown')}"
    codes = sorted(
        {
            str(d["code"])
            for d in diagnostics + list((result.get("diagnostics") or {}).get("messages") or [])
            if d.get("code")
        }
    )
    if codes:
        return "diagnostics:" + ",".join(codes)
    return f"status:{result.get('status', 'unknown')}"


def group_problems(cases: list[ProblemCase]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for c in cases:
        groups[(c.source_id or "-", c.signature)].append(c.name)
    return [
        {"source_id": src, "signature": sig, "count": len(names), "samples": names}
        for (src, sig), names in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]


async def load_case(nb: Neighbours, sample: dict[str, Any], name: str, max_chars: int) -> ProblemCase:
    if sample.get("material"):
        material = dict(sample["material"])
    else:
        ref = sample["material_ref"]
        material = await nb.storage.material(str(ref["storage_connection_id"]), str(ref["object_id"]))
    raw = await material_bytes(material)
    text = truncate(decode_text(raw, (material.get("format") or {}).get("charset")), max_chars)
    diagnostics = list(sample.get("diagnostics") or [])
    result = sample.get("result")
    return ProblemCase(
        name=name,
        material=material,
        text=text,
        diagnostics=diagnostics,
        result=result,
        signature=signature_of(result, diagnostics),
        source_id=(material.get("source") or {}).get("source_id"),
    )


@dataclass
class ImproveOutcome:
    draft: PackageDraft | None
    outcomes: list[TestOutcome]
    attempts: int
    schema_change: str = "none"
    suggested: list[str] = field(default_factory=list)
    change_summary: str = ""
    reason: str | None = None
    other_bindings_failed: bool = False


@dataclass
class BindingContext:
    task_id: str
    stage_id: str
    source_id: str | None
    params: dict[str, Any] | None
    own: bool

    @property
    def context(self) -> str:
        return f"bindings:{self.task_id}/{self.stage_id}"


def _package_view(draft: PackageDraft, max_chars: int) -> list[dict[str, Any]]:
    parts = [part("package", as_json(draft.manifest), "application/json")]
    files = {
        p: truncate(draft.text(p), max_chars)
        for p in sorted(draft.files)
        if p.startswith(("src/", "schemas/"))
    }
    parts.append(part("files", as_json(files), "application/json"))
    return parts


def _apply_files(
    draft: PackageDraft, files: dict[str, str], settings: Settings, validator: SchemaValidator
) -> list[str]:
    problems: list[str] = []
    callable_name = str(draft.manifest.get("entry", {}).get("callable", "extract"))
    entry_module = str(draft.manifest.get("entry", {}).get("module", ""))
    entry_path = "src/" + entry_module.replace(".", "/") + ".py" if entry_module else ""
    for path, text in files.items():
        if not path.startswith(("src/", "schemas/")) or ".." in path or path.startswith("/"):
            problems.append(f"{path}: only files under src/ or schemas/ may change")
            continue
        if path.endswith(".py"):
            check = check_code(
                text,
                callable_name if path == entry_path else "__any__",
                settings.generated_code_allowed_modules,
            )
            issues = [p for p in check.problems if path == entry_path or "does not define" not in p]
            problems += [f"{path}: {p}" for p in issues]
        elif path.endswith(".json"):
            try:
                json.loads(text)
            except ValueError as exc:
                problems.append(f"{path}: invalid JSON ({exc})")
        draft.files[path] = text.encode("utf-8")
    if not problems and validator.available:
        problems += [
            f"manifest {e}" for e in validator.errors("package-manifest.schema.json", draft.manifest)
        ]
    return problems


async def improve_draft(
    *,
    nb: Neighbours,
    llm: LlmSession,
    settings: Settings,
    limits: ServiceLimits,
    validator: SchemaValidator,
    base: PackageDraft,
    version_after: Any,
    problems: list[ProblemCase],
    successes: list[ProblemCase],
    bindings: list[BindingContext],
    attempts: int,
    job_key: str,
    job_id: str,
    reason: str = "improvement",
    retry_on_other_failure: bool = True,
) -> ImproveOutcome:
    """Ask the model for a fixed version until one passes all checks or attempts run out.

    ``version_after(schema_change) -> str`` picks the new version number (SemVer part by change).
    """
    groups = group_problems(problems)
    feedback: Any = None
    outcomes: list[TestOutcome] = []
    produced = set(
        (
            (base.manifest.get("output") or {}).get("entities")
            and [e["entity_type"] for e in base.manifest["output"]["entities"]]
        )
        or []
    )
    for attempt in range(1, attempts + 1):
        data = _package_view(base, limits.improvement.max_file_chars)
        data.append(
            part(
                "problems",
                as_json(
                    {
                        "groups": groups,
                        "samples": [
                            {
                                "name": c.name,
                                "url": material_label(c.material),
                                "signature": c.signature,
                                "diagnostics": c.diagnostics,
                                "status": (c.result or {}).get("status"),
                            }
                            for c in problems
                        ],
                    }
                ),
                "application/json",
            )
        )
        data += [
            part(
                f"problem_{c.name}", c.text, (c.material.get("format") or {}).get("media_type", "text/plain")
            )
            for c in problems
        ]
        data += [
            part(
                f"success_{c.name}", c.text, (c.material.get("format") or {}).get("media_type", "text/plain")
            )
            for c in successes
        ]
        if feedback is not None:
            data.append(part("previous_attempt", as_json(feedback), "application/json"))
        try:
            out = await llm.ask("improve", IMPROVE, data, IMPROVE_SCHEMA, model=settings.llm_model_strong)
        except InvalidModelOutput as exc:
            feedback = {"error": str(exc)}
            continue
        draft = base.copy()
        issues = _apply_files(draft, dict(out.get("files") or {}), settings, validator)
        expectations = {str(e["name"]): e for e in out.get("expectations") or []}
        if issues:
            feedback = {"rejected": issues}
            continue
        schema_change = str(out.get("schema_change", "none"))
        draft.manifest["version"] = version_after(schema_change)
        prov = dict(draft.manifest.get("provenance") or {})
        prov.update(
            {
                "created_by": "llm",
                "based_on": base.ref,
                "change_summary": str(out.get("change_summary", ""))[:4000],
                "llm": {
                    "reason": reason,
                    "assistant_job_id": job_id,
                    **{
                        k: v
                        for k, v in {
                            "provider": llm.model_used.get("provider_id"),
                            "model": llm.model_used.get("model_id"),
                        }.items()
                        if v
                    },
                },
            }
        )
        prov.pop("upstream_port", None)
        draft.manifest["provenance"] = prov
        missing = []
        for c in problems:
            exp = expectations.get(c.name) or expectations.get(f"problem_{c.name}")
            if exp is None:
                missing.append(c.name)
                continue
            draft.add_test(
                f"problem-{c.name}",
                c.material,
                str(exp["expected_status"]),
                list(exp.get("entities") or []),
                "problem_sample",
            )
        if missing:
            feedback = {"rejected": [f"no expected output for problem sample(s) {missing}"]}
            continue
        # Successful examples must keep working: same status and, unless the schema changes
        # incompatibly (then field shapes legitimately differ), the same entities.
        regressions = [
            extra_case(
                case_name(f"success-{c.name}"),
                c.material,
                str((c.result or {}).get("status") or "success"),
                None
                if schema_change == "breaking"
                else list(((c.result or {}).get("output") or {}).get("entities") or []) or None,
            )
            for c in successes
        ]
        outcome = await run_tests(
            nb.handler,
            job_key=job_key,
            context="tests",
            draft=draft,
            extra_cases=regressions,
            inline_max_bytes=limits.transfer.inline_max_bytes,
        )
        outcomes = [outcome]
        if not outcome.passed:
            feedback = {"failed_tests": outcome.failures()}
            continue
        failed_own: list[dict[str, Any]] = []
        failed_other: list[dict[str, Any]] = []
        for b in bindings:
            o = await run_tests(
                nb.handler,
                job_key=job_key,
                context=b.context,
                draft=draft,
                params=b.params,
                inline_max_bytes=limits.transfer.inline_max_bytes,
            )
            outcomes.append(o)
            if not o.passed:
                (failed_own if b.own else failed_other).append(
                    {"binding": b.context, "failures": o.failures()}
                )
        if failed_own or (failed_other and retry_on_other_failure):
            feedback = {"failed_bindings": failed_own + failed_other}
            continue
        suggested = sorted(
            {
                t
                for t in out.get("suggested_entity_types") or []
                if isinstance(t, str) and t not in produced and _is_slug(t)
            }
        )
        return ImproveOutcome(
            draft,
            outcomes,
            attempt,
            schema_change,
            suggested,
            prov["change_summary"],
            other_bindings_failed=bool(failed_other),
        )
    return ImproveOutcome(
        None,
        outcomes,
        attempts,
        reason=f"no version passed all checks in {attempts} attempt(s): {as_json(feedback)[:1500]}",
    )


def _is_slug(value: str) -> bool:
    import re

    return re.match(_ENTITY_SLUG, value) is not None


async def _bindings(nb: Neighbours, req: dict[str, Any]) -> list[BindingContext]:
    package_id = req["package"]["package_id"]
    source_id = req.get("source_id")
    pairs: list[tuple[str, str]] = [(b["task_id"], b["stage_id"]) for b in req.get("bindings") or []]
    task_sources: dict[str, str | None] = {}
    if nb.orchestrator.configured:
        for t in await nb.orchestrator.tasks_using(package_id):
            task_sources[t["task_id"]] = t.get("source_id")
            if not req.get("bindings"):
                pairs += [(t["task_id"], s["stage_id"]) for s in t.get("package_stages") or []]
    out = []
    for task_id, stage_id in dict.fromkeys(pairs):
        params = None
        task_source = task_sources.get(task_id)
        if nb.orchestrator.configured:
            try:
                task = await nb.orchestrator.get_task(task_id)
                task_source = (task.get("input") or {}).get("source_id", task_source)
                stage: dict[str, Any] = next(
                    (s for s in task.get("stages") or [] if s.get("stage_id") == stage_id), {}
                )
                params = stage.get("params")
            except RemoteError as exc:
                log.warning("binding task not readable", extra={"task_id": task_id, "error": str(exc)})
        own = source_id is None or task_source is None or task_source == source_id
        out.append(BindingContext(task_id, stage_id, task_source, params, own))
    return out


async def _patch_group(nb: Neighbours, group_id: str | None, patch: dict[str, Any]) -> None:
    if not group_id or not nb.orchestrator.configured:
        return
    try:
        await nb.orchestrator.update_problem_group(group_id, patch)
    except (RemoteError, JaneError) as exc:
        log.warning("problem group not updated", extra={"group_id": group_id, "error": str(exc)})


async def run_improvement(
    *,
    nb: Neighbours,
    req: dict[str, Any],
    settings: Settings,
    limits: ServiceLimits,
    validator: SchemaValidator,
    job_id: str,
    progress: Any,
) -> dict[str, Any]:
    ref = req["package"]
    package_id, version = ref["package_id"], ref["version"]
    policy = {"approval": "manual", "allow_fork": True, **(req.get("policy") or {})}
    group_id = req.get("problem_group_id")
    llm = LlmSession(nb.llm, limits.llm, "improvement", job_id, source_id=req.get("source_id"))
    await _patch_group(nb, group_id, {"status": "in_progress", "assistant_job_id": job_id})

    def result(outcome: str, **extra: Any) -> dict[str, Any]:
        return {"outcome": outcome, "costs": llm.cost(), **{k: v for k, v in extra.items() if v is not None}}

    async def unresolved(
        reason: str, attempts: int, reports: list[TestOutcome] | None = None
    ) -> dict[str, Any]:
        await _patch_group(
            nb, group_id, {"status": "unresolved", "assistant_job_id": job_id, "note": reason[:2000]}
        )
        return result(
            "unresolved",
            attempts=attempts,
            unresolved_reason=reason,
            activated=False,
            test_reports=[o.wire() for o in reports or []],
        )

    package = await nb.registry.get_package(package_id)
    if package.get("kind") != "extractor":
        raise ValidationFailed(
            f"{package_id} is a {package.get('kind')} package; improvement supports extractors"
        )
    files, _digest = await nb.registry.archive_files(package_id, version)
    base = PackageDraft.from_files(files)
    await progress(1, "package loaded")
    problems = [
        await load_case(nb, s, f"p{i + 1}", limits.improvement.max_sample_chars)
        for i, s in enumerate(req["problem_samples"][: limits.improvement.max_problem_samples])
    ]
    successes = [
        await load_case(nb, s, f"s{i + 1}", limits.improvement.max_sample_chars)
        for i, s in enumerate(
            (req.get("successful_examples") or [])[: limits.improvement.max_successful_examples]
        )
    ]
    bindings = await _bindings(nb, req)
    await progress(2, f"{len(problems)} problem sample(s), {len(bindings)} binding(s)")
    attempts = limits.llm.max_improvement_attempts
    if attempts == 0:
        return await unresolved("limits.llm.max_improvement_attempts is 0", 0)
    latest = str(package.get("latest_version") or version)
    top = max([version, latest], key=_semver_key)

    def version_after(change: str) -> str:
        return bump(top, {"breaking": "major", "additive": "minor"}.get(change, "patch"))

    try:
        out = await improve_draft(
            nb=nb,
            llm=llm,
            settings=settings,
            limits=limits,
            validator=validator,
            base=base,
            version_after=version_after,
            problems=problems,
            successes=successes,
            bindings=bindings,
            attempts=attempts,
            job_key=job_id,
            job_id=job_id,
            retry_on_other_failure=not policy["allow_fork"],
        )
    except BudgetExhausted as exc:
        return await unresolved(f"LLM budget exhausted: {exc}", llm.calls)
    if out.draft is None:
        return await unresolved(out.reason or "no candidate version", out.attempts, out.outcomes)
    await progress(3, f"candidate {out.draft.manifest['version']} passed tests")

    shared_other = any(not b.own for b in bindings)
    needs_fork = out.other_bindings_failed or (out.schema_change == "breaking" and shared_other)
    reports = [o.wire() for o in out.outcomes]
    common = {
        "attempts": out.attempts,
        "test_reports": reports,
        "suggested_entity_types": out.suggested or None,
    }
    if needs_fork and not policy["allow_fork"]:
        return await unresolved(
            "the new version breaks bindings of other sources and forking is not allowed",
            out.attempts,
            out.outcomes,
        )
    if not package.get("auto_changes_allowed", True):
        await _patch_group(
            nb,
            group_id,
            {
                "status": "unresolved",
                "assistant_job_id": job_id,
                "note": f"automatic changes of {package_id} are forbidden; proposal {out.draft.manifest['version']} needs a manual change",
            },
        )
        return result("proposal_only", version=out.draft.ref, activated=False, **common)

    draft = out.draft
    targets = [b for b in bindings if b.own] if needs_fork else bindings
    if needs_fork:
        fork_id = slug(f"{package_id}.{req.get('source_id') or 'fork'}")
        fork = await nb.registry.fork(
            package_id,
            {
                "new_package_id": fork_id,
                "from_version": version,
                "title": f"{package.get('title', package_id)} ({req.get('source_id') or 'fork'})"[:200],
                "auto_changes_allowed": True,
            },
            idem_key(job_id, "fork", fork_id),
        )
        draft.manifest["package_id"] = fork_id
        if fork.get("fork_of"):
            draft.manifest["fork_of"] = fork["fork_of"]
        draft.manifest["version"] = bump(
            str(fork.get("latest_version") or version),
            {"breaking": "major", "additive": "minor"}.get(out.schema_change, "patch"),
        )
        draft.manifest["provenance"]["based_on"] = {
            "package_id": fork_id,
            "version": str(fork.get("latest_version") or version),
        }
    published = await nb.registry.publish(
        draft.manifest["package_id"],
        draft.publish_body(),
        idem_key(job_id, "publish", draft.manifest["package_id"]),
    )
    new_ref = {
        "package_id": published["package_id"],
        "version": published["version"],
        "digest": published["digest"],
    }
    for o in out.outcomes:
        if (
            needs_fork
            and o.context.startswith("bindings:")
            and not any(o.context == b.context for b in targets)
        ):
            continue
        report = {**o.report, "package": new_ref}
        await nb.registry.record_tests(
            new_ref["package_id"],
            new_ref["version"],
            {"runner": "assistant", "context": o.context, "report": report},
            idem_key(job_id, "tests", o.context),
        )
    await progress(4, f"published {new_ref['package_id']}@{new_ref['version']}")
    outcome = "fork_created" if needs_fork else "new_version"
    activated = False
    note = f"version {new_ref['package_id']}@{new_ref['version']} awaits manual approval"
    if policy["approval"] == "auto_after_checks":
        activated, note = await _auto_activate(nb, job_id, new_ref, targets)
    await _patch_group(
        nb,
        group_id,
        {
            "status": "resolved" if activated else "in_progress",
            "assistant_job_id": job_id,
            "note": note[:2000],
        },
    )
    return result(outcome, version=new_ref, activated=activated, **common)


async def _auto_activate(
    nb: Neighbours, job_id: str, ref: dict[str, str], targets: list[BindingContext]
) -> tuple[bool, str]:
    if not targets:
        return False, "no bindings to activate"
    await nb.registry.set_status(
        ref["package_id"],
        ref["version"],
        "approved",
        f"assistant job {job_id}: tests passed on {len(targets)} binding(s)",
        idem_key(job_id, "approve"),
    )
    done: list[BindingContext] = []
    for b in targets:
        try:
            await nb.orchestrator.activate(
                b.task_id,
                b.stage_id,
                {
                    "kind": "auto_activate",
                    "package": ref,
                    "reason": f"assistant job {job_id} passed tests on {len(targets)} binding(s)",
                },
                idem_key(job_id, "activate", b.context),
            )
            done.append(b)
        except RemoteError as exc:
            reason = ((exc.problem.details or {}).get("reason") if exc.problem else None) or (
                exc.problem.code if exc.problem else str(exc)
            )
            for d in reversed(done):  # all-or-nothing across the bindings of one package
                try:
                    await nb.orchestrator.activate(
                        d.task_id,
                        d.stage_id,
                        {
                            "kind": "rollback",
                            "reason": f"assistant job {job_id}: activation on {b.context} refused ({reason})",
                        },
                        idem_key(job_id, "rollback", d.context),
                    )
                except RemoteError as rb_exc:
                    log.error("rollback failed", extra={"binding": d.context, "error": str(rb_exc)})
            return (
                False,
                f"auto activation refused on {b.context}: {reason}; {len(done)} activation(s) rolled back",
            )
    return True, f"auto-activated on {len(done)} binding(s)"


def _semver_key(v: str) -> tuple[int, int, int, int]:
    import re

    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(-)?", v)
    if not m:
        return (0, 0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), 0 if m.group(4) else 1)
