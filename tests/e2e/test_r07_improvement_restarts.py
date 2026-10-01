"""R-07 (criteria 6 and 8): the improvement cycle of S-M2-07 with restarts in the middle, under load
(docs/acceptance/scenarios.md).

Each scenario prepares S-M2-07 anew (``jane_e2e.assistant.prepare_improvable``: extractor 1.0.0 in the real
registry, two bindings, a run that leaves out-of-stock and pre-order cards ``unrecognized``), starts a load run of
another task (19 product pages, its own copy of the extractor) and then an improvement run. While the candidate
version 1.1.0 is being tested in the runtime (a sandbox of ``<package>@1.1.0`` runs, the LLM has answered,
nothing is published yet):

* ``assistant`` - the assistant gets ``docker kill`` (SIGKILL) and ``docker start``;
* ``runtime`` - handler-runtime gets ``docker kill`` and stays down until the assistant's job has reacted, then
  ``docker start``.

The interrupted job must end in a state the client can act on, and a repeated improvement run (new
``Idempotency-Key``) must finish the cycle: exactly one new version 1.1.0 (digest, parent 1.0.0, made by the
repeated job), 1.0.0 unchanged, one automatic activation per binding, then a rollback. Which version a task uses
is checked by execution: runs of the tasks, the ``HandlerResult.handler`` the runtime reports for every call
and the stored entities. The load run must finish with every effect once.

What the services do with the interrupted job is recorded in ``OBSERVED`` and asserted by the last two
tests, ``xfail(strict=True)`` while the defects they reproduce are open (docs/delivery/WP-13.md, R-07).

Real services: assistant, LLM gateway, registry, web-collector, handler-runtime, orchestrator, storage,
testsite, PostgreSQL, MinIO. Substitutes of EXTERNAL systems (**З**): the LLM provider ``fake`` (scripted
answers, tests/e2e/config/llm-seed.yaml) and the static web search. Operational observations outside the
contracts: the JSON access log of handler-runtime (``request`` records, jane-kit) for the ids of the test-run
jobs the assistant polls, and the Docker labels of runtime sandboxes (``io.jane.package``,
``io.jane.invocation-id``, ``io.jane.e2e-project``).
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

import pytest

from jane_e2e.assistant import (
    IMPROVABLE,
    PRODUCT_URLS,
    SUCCESSES,
    Flows,
    Improvable,
    activations,
    approve,
    archive_digest,
    assistant_flows,
    by_purpose,
    improve,
    items_by_path,
    new_key,
    note,
    prepare_improvable,
    problem_group,
    publish_fixture,
    ref_of,
    registry_package,
    registry_version,
    stage_handler,
    start_improvement,
)
from jane_e2e.clients import TERMINAL_JOB_STATES, JaneClient
from jane_e2e.orchestration import (
    TESTSITE,
    create_source,
    create_task,
    list_items,
    m1_task,
    start_run,
    wait_run,
)
from jane_e2e.stack import E2EStack
from jane_e2e.verify import assert_effects_once, entities, site_paths

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

SCENARIO = "R-07"
POLL_S = 0.2
# Settings of this module's stack (tests/e2e/compose.e2e.yaml); defaults chosen for the e2e time budget.
JOB_LEASE_MS = int(os.environ.get("JANE_E2E_ASSISTANT_JOB_LEASE_MS", "20000"))
HEARTBEAT_MS = int(os.environ.get("JANE_E2E_ASSISTANT_HEARTBEAT_MS", "2000"))
IN_PROGRESS_LEASE_MS = int(os.environ.get("JANE_E2E_RUNTIME_IN_PROGRESS_LEASE_MS", "30000"))
STACK_ENV = {
    "JANE_E2E_ASSISTANT_JOB_LEASE_MS": str(JOB_LEASE_MS),
    "JANE_E2E_ASSISTANT_HEARTBEAT_MS": str(HEARTBEAT_MS),
    "JANE_E2E_RUNTIME_IN_PROGRESS_LEASE_MS": str(IN_PROGRESS_LEASE_MS),
}
# Upper bound of every wait of the scenario (conditions are polled; nothing is timed against a threshold).
WAIT_S = float(os.environ.get("JANE_E2E_R07_WAIT_S", "600"))

CANDIDATE = "1.1.0"  # the scripted fix adds fields to the schema: a minor version
LOAD_PRODUCTS = site_paths("product")
LOAD_LIMITS = {"concurrency": {"max_parallel_stage_items": 1}}  # one call at a time: the load lasts
# Retries of the load task outlast a runtime restart (attempts are spent while the runtime is down).
LOAD_RETRIES = {
    "max_attempts": 10,
    "initial_backoff_ms": 1000,
    "backoff_multiplier": 2,
    "max_backoff_ms": 10000,
    "jitter": False,
}
# Labels of handler-runtime sandboxes (executor.py, sandbox.py; the project label comes from
# JANE_HANDLER_RUNTIME_SANDBOX_LABELS in tests/e2e/compose.e2e.yaml).
INVOCATION_LABEL = "io.jane.invocation-id"
PACKAGE_LABEL = "io.jane.package"
PROJECT_LABEL = "io.jane.e2e-project"
JOB_PATH = re.compile(r"^/v1/jobs/(?P<job_id>[^/]+)$")

# What the services did with the interrupted jobs; asserted by the xfail tests at the end of the module.
OBSERVED: dict[str, dict[str, Any]] = {}


@pytest.fixture(scope="module")
def flows(stack: E2EStack) -> Iterator[Flows]:
    """The S-M2-06/07 stack (real registry everywhere) under its own compose project, with the shorter assistant
    job lease and runtime in-progress lease of ``STACK_ENV``; both are read back from the start-up log line
    ``configured limits`` of the services (these limits are service-specific, not in ``/v1/info``).
    ``stack`` (session) only checks Docker; this module never starts services in it."""
    with assistant_flows("r07", label=SCENARIO, env=STACK_ENV) as own:
        state = configured_limits(own.stack, "assistant")["state"]
        assert (state["job_lease_ms"], state["heartbeat_interval_ms"]) == (JOB_LEASE_MS, HEARTBEAT_MS), state
        runtime = configured_limits(own.stack, "handler-runtime")["state"]
        assert runtime["in_progress_lease_ms"] == IN_PROGRESS_LEASE_MS, runtime
        note(SCENARIO, "assistant state limits", state)
        note(SCENARIO, "runtime state limits", runtime)
        yield own


# ---------------------------------------------------------------------------- helpers
def wait_for[T](what: str, probe: Callable[[], T | None], timeout_s: float = WAIT_S) -> T:
    """Poll ``probe`` until it returns a value other than ``None`` (no blind sleeps)."""
    deadline = time.monotonic() + timeout_s
    while True:
        value = probe()
        if value is not None:
            return value
        if time.monotonic() > deadline:
            raise TimeoutError(f"{what}: not reached in {timeout_s:.0f}s")
        time.sleep(POLL_S)


def job_of(client: JaneClient, api: str, job_id: str) -> dict[str, Any]:
    r = client.api(api).get(f"/v1/jobs/{job_id}")
    assert r.status_code == 200, r.text
    return dict(r.json())


def job_brief(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": job["status"],
        "progress": (job.get("progress") or {}).get("message"),
        "error": {k: (job.get("error") or {}).get(k) for k in ("code", "retryable", "detail")}
        if job.get("error")
        else None,
        "cancellation": (job.get("cancellation") or {}).get("reason") if job.get("cancellation") else None,
    }


def versions(registry: JaneClient, package_id: str) -> list[dict[str, Any]]:
    r = registry.api("registry").get(f"/v1/packages/{package_id}/versions", params={"limit": 100})
    assert r.status_code == 200, r.text
    body = r.json()
    assert not body.get("next_cursor"), body
    return list(body["items"])


def version_numbers(registry: JaneClient, package_id: str) -> list[str]:
    return sorted(v["version"] for v in versions(registry, package_id))


def candidate_sandboxes(stack: E2EStack, package_id: str) -> set[str]:
    """Invocation ids of the running runtime sandboxes of the candidate ``<package>@1.1.0`` (a test case)."""
    labels = {PROJECT_LABEL: stack.project, PACKAGE_LABEL: f"{package_id}@{CANDIDATE}"}
    return set(stack.running_label_values(labels, INVOCATION_LABEL))


def log_records(stack: E2EStack, service: str, msg: str) -> list[dict[str, Any]]:
    """JSON log records ``msg`` of one service (jane-kit JSON logs), including those before a restart."""
    out = []
    for line in stack.logs(service, echo=False).splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("msg") == msg:
            out.append(record)
    return out


def access_log(stack: E2EStack, service: str) -> list[dict[str, Any]]:
    """jane-kit access-log records (``request``: method, path, status) of one service."""
    return log_records(stack, service, "request")


def configured_limits(stack: E2EStack, service: str) -> dict[str, Any]:
    """Effective limits of the running service from its last start-up line ``configured limits``."""
    records = log_records(stack, service, "configured limits")
    assert records, f"{service}: no 'configured limits' log line"
    return dict(records[-1]["limits"]["limits"])


def polled_jobs(stack: E2EStack, service: str, offset: int) -> list[str]:
    """Ids of the jobs polled (``GET /v1/jobs/{id}``) on ``service`` since access-log record ``offset``."""
    ids: list[str] = []
    for record in access_log(stack, service)[offset:]:
        m = JOB_PATH.match(str(record.get("path", "")))
        if record.get("method") == "GET" and m and m["job_id"] not in ids:
            ids.append(m["job_id"])
    return ids


def run_view(orch: JaneClient, run_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get(f"/v1/runs/{run_id}")
    assert r.status_code == 200, r.text
    return dict(r.json())


def improvement_requests(flows: Flows) -> int:
    return by_purpose(flows["llm"]).get("improvement", 0)


# ---------------------------------------------------------------------------- load
@dataclass
class Load:
    source_id: str
    task_id: str
    run: str  # orchestrator run (job) id
    package: dict[str, Any]


def start_load(flows: Flows, prefix: str) -> Load:
    """Another source and task with its own copy of the extractor (so that it is not a binding of the improved
    package): 19 product pages, one stage item at a time, retries that outlast a restart. Returns once the
    runtime is executing its extraction calls."""
    registry, orch = flows["registry"], flows["orchestrator"]
    package = ref_of(publish_fixture(registry, IMPROVABLE, f"{prefix}-load.improvable-product-extractor"))
    approve(registry, package, "e2e: load of R-07")
    source_id = task_id = f"{prefix}-load"
    create_source(orch, source_id)
    task = m1_task(task_id, source_id, [TESTSITE + p for p in LOAD_PRODUCTS], package, limits=LOAD_LIMITS)
    task["retries"] = LOAD_RETRIES
    create_task(orch, task)
    run = start_run(orch, task_id)

    def extracting() -> bool | None:
        items = list_items(orch, run, "extract-products")
        return True if any(i["status"] in ("running", "completed") for i in items) else None

    wait_for("load run extracting", extracting)
    return Load(source_id, task_id, run, package)


def finish_load(flows: Flows, load: Load, scenario: str) -> dict[str, Any]:
    """The load run succeeded; every material stored once and every recognised product stored once."""
    orch, storage = flows["orchestrator"], flows["storage"]
    run = wait_run(orch, load.run, timeout_s=WAIT_S)
    items = list_items(orch, load.run)
    extracted = [i for i in items if i["stage_id"] == "extract-products"]
    # items that needed more than one attempt: "<stage> x<attempts>" -> number of items
    retried = dict(Counter(f"{i['stage_id']} x{i['attempts']}" for i in items if i["attempts"] > 1))
    counts = {s["stage_id"]: s.get("counts") for s in run["stages"]}
    note(scenario, "load run", {"status": run["status"], "stages": counts, "retried items": retried})
    assert run["status"] == "succeeded", run
    assert all(i["status"] == "completed" for i in items), [i for i in items if i["status"] != "completed"]
    assert len(extracted) == len(LOAD_PRODUCTS), extracted
    products = sum(1 for i in extracted if i.get("result_status") == "success")
    assert products > 0, extracted
    assert_effects_once(storage, load.source_id, materials=len(LOAD_PRODUCTS), products=products)
    return {"retried": retried, "products": products}


# ---------------------------------------------------------------------------- the fault window
def wait_candidate_under_test(flows: Flows, case: Improvable, job_id: str) -> set[str]:
    """The improvement job is between the LLM answer and the publication: a candidate sandbox runs."""
    stack, assistant, registry = flows.stack, flows["assistant"], flows["registry"]

    def probe() -> set[str] | None:
        if (sandboxes := candidate_sandboxes(stack, case.package_id)) and (
            job_of(assistant, "assistant", job_id)["status"] == "running"
        ):
            return sandboxes
        job = job_of(assistant, "assistant", job_id)
        assert job["status"] not in TERMINAL_JOB_STATES, job  # finished before the fault: no window
        return None

    sandboxes = wait_for("candidate test case running in a sandbox", probe)
    assert version_numbers(registry, case.package_id) == ["1.0.0"]  # nothing published yet
    return sandboxes


# ---------------------------------------------------------------------------- the recovered cycle
def check_one_new_version(
    flows: Flows, case: Improvable, job_id: str, result: dict[str, Any], scenario: str
) -> dict[str, Any]:
    """Exactly one new version, made by the repeated job; 1.0.0 unchanged; one activation per binding."""
    registry, orch = flows["registry"], flows["orchestrator"]
    assert result["outcome"] == "new_version" and result["activated"] is True, result
    assert result["attempts"] == 1, result
    new = result["version"]
    assert (new["package_id"], new["version"]) == (case.package_id, CANDIDATE), new
    assert version_numbers(registry, case.package_id) == ["1.0.0", CANDIDATE]
    assert registry_package(registry, case.package_id)[0]["latest_version"] == CANDIDATE

    old_now = registry_version(registry, case.old)
    assert old_now["digest"] == case.v1["digest"] == archive_digest(registry, case.old)[0], old_now
    v2 = registry_version(registry, new)
    assert v2["digest"] == new["digest"] == archive_digest(registry, new)[0], v2
    prov = v2["manifest"]["provenance"]
    assert prov["created_by"] == "llm" and prov["llm"]["assistant_job_id"] == job_id, prov
    assert prov["based_on"] == {"package_id": case.package_id, "version": "1.0.0"}, prov
    assert v2["status"] == "approved" and v2["test_status"] == "passed", v2
    # every test report of the assistant recorded once (the registry may add its own runtime checks)
    contexts = [r["context"] for r in v2.get("test_reports") or [] if r.get("runner") == "assistant"]
    bindings = {f"bindings:{t}/extract-products" for t in (case.task_id, case.recheck_id)}
    assert sorted(contexts) == sorted({"tests", *bindings}), v2.get("test_reports")

    for task in (case.task_id, case.recheck_id):
        history = activations(orch, task, "extract-products")
        auto = [a for a in history if a["kind"] == "auto_activate"]
        assert len(auto) == 1 and auto[0]["package"] == new, history
        assert auto[0]["previous"]["version"] == "1.0.0", auto
        assert stage_handler(orch, task, "extract-products") == new
    resolved = problem_group(orch, case.source_id, case.package_id)
    assert resolved["status"] == "resolved" and resolved["assistant_job_id"] == job_id, resolved
    note(
        scenario,
        "registry after the cycle",
        {
            "versions": [
                (v["version"], v["digest"], v["status"]) for v in versions(registry, case.package_id)
            ],
            "based_on": prov["based_on"],
            "assistant_job_id": prov["llm"]["assistant_job_id"],
            "test_reports": sorted(contexts),
        },
    )
    return dict(new)


def executed(
    flows: Flows, case: Improvable, task_id: str, expected: dict[str, str], ref: dict[str, Any]
) -> dict[str, Any]:
    """A real run of ``task_id``: extraction statuses by page, and the package the runtime itself reports as
    executed (``HandlerResult.handler``) for every call - the digest of ``ref``."""
    orch, runtime = flows["orchestrator"], flows["handler-runtime"]
    run = wait_run(orch, start_run(orch, task_id), timeout_s=WAIT_S)
    assert run["status"] == "succeeded", run
    items = items_by_path(orch, run["run_id"], "extract-products", case.path_of)
    assert {p: i["result_status"] for p, i in items.items()} == expected, items
    for path, item in items.items():
        r = runtime.api("handler").get(f"/v1/invocations/{item['invocation_id']}")
        assert r.status_code == 200, r.text
        assert r.json()["handler"] == ref, (path, r.json()["handler"], ref)
    return run


def check_activation_and_rollback(flows: Flows, case: Improvable, new: dict[str, Any], scenario: str) -> None:
    """After the restarts: the tasks run the new version, the rollback brings 1.0.0 back on one stage only."""
    orch, storage = flows["orchestrator"], flows["storage"]
    oapi = orch.api("orchestrator")
    fixed = dict.fromkeys(PRODUCT_URLS, "success")
    run = executed(flows, case, case.task_id, fixed, new)
    saved = {
        e["fields"]["sku"]: e["fields"] for e in entities(storage, "results-pg", case.source_id, "product")
    }
    assert saved["phone-gamma"]["availability"] == "out_of_stock", saved
    assert saved["phone-zeta"]["availability"] == "pre_order", saved
    note(scenario, "run with 1.1.0", {"run": run["run_id"], "statuses": fixed, "digest": new["digest"]})

    rolled = oapi.post(
        f"/v1/tasks/{case.task_id}/stages/extract-products/activations",
        json={"kind": "rollback", "reason": "e2e R-07: back to the human baseline"},
        headers={"Idempotency-Key": new_key()},
    )
    assert rolled.status_code == 200, rolled.text
    assert rolled.json()["kind"] == "rollback" and rolled.json()["package"] == case.old, rolled.json()
    assert rolled.json()["previous"]["version"] == CANDIDATE, rolled.json()
    assert stage_handler(orch, case.task_id, "extract-products") == case.old
    executed(flows, case, case.task_id, PRODUCT_URLS, case.old)
    # the rollback is per stage: the second binding still runs 1.1.0
    executed(flows, case, case.recheck_id, {SUCCESSES[0]: "success"}, new)

    audit = oapi.get(
        "/v1/audit-events",
        params={"subject_type": "stage", "subject_id": f"{case.task_id}/extract-products"},
    )
    assert audit.status_code == 200, audit.text
    actions = [e["action"] for e in audit.json()["items"]]
    assert actions.count("stage.auto_activate") == 1 and actions.count("stage.rollback") == 1, actions
    note(scenario, "rollback", {"package": rolled.json()["package"], "audit": actions})


# ---------------------------------------------------------------------------- R-07 with an assistant kill
@pytest.mark.criteria(6, 8)
def test_r_07_assistant_killed_while_candidate_is_tested_rerun_publishes_exactly_one_version(
    flows: Flows, run_id: str
) -> None:
    """SIGKILL of the assistant after the LLM answered and while the candidate is tested (nothing published),
    then a restart: the dead job publishes and activates nothing; a repeated run publishes exactly one 1.1.0,
    activates it once per binding, and the activation and the rollback work by execution, under a load run."""
    scenario = "R-07/assistant"
    stack, registry = flows.stack, flows["registry"]
    case = prepare_improvable(flows, f"e2e-{run_id}", scenario)
    load = start_load(flows, f"e2e-{run_id}")
    llm_before = improvement_requests(flows)

    first = start_improvement(flows["assistant"], case.request)
    sandboxes = wait_candidate_under_test(flows, case, first)
    stack.kill_instance("assistant", 1)
    killed_at = time.monotonic()
    load_at_fault = run_view(flows["orchestrator"], load.run)["status"]
    note(
        scenario,
        "assistant killed",
        {"job": first, "candidate sandboxes": sorted(sandboxes), "load": load_at_fault},
    )
    assert load_at_fault == "running"  # the fault happens under load
    assert improvement_requests(flows) == llm_before + 1  # the LLM step of the killed job was done

    stack.start_instance("assistant", 1)
    stack.wait_healthy("assistant", 1)
    assistant = flows.reconnect("assistant")
    # The README of WP-11: the job of a killed instance is marked failed once its lease has expired. Observe it
    # for two leases plus two heartbeats after the kill (it ends as soon as the job is terminal).
    limit_s = (2 * JOB_LEASE_MS + 2 * HEARTBEAT_MS) / 1000

    def settled() -> dict[str, Any] | None:
        job = job_of(assistant, "assistant", first)
        if job["status"] in TERMINAL_JOB_STATES or time.monotonic() - killed_at > limit_s:
            return job
        return None

    dead = wait_for("killed job observed", settled)
    # the instance id (job owner) the assistant logged at its start before and after the restart
    starts = [str(r.get("instance")) for r in log_records(stack, "assistant", "configured limits")]
    OBSERVED["assistant_job_after_kill"] = {
        **job_brief(dead),
        "seconds_after_kill": round(time.monotonic() - killed_at, 1),
        "instance ids (start before, after the restart)": starts[-2:],
    }
    note(scenario, "job of the killed assistant after the restart", OBSERVED["assistant_job_after_kill"])
    assert version_numbers(registry, case.package_id) == ["1.0.0"]  # the dead job published nothing
    for task in (case.task_id, case.recheck_id):
        assert stage_handler(flows["orchestrator"], task, "extract-products") == case.old

    # recovery: the improvement is started again (a new Idempotency-Key)
    second, result = improve(assistant, case.request)
    assert second != first
    new = check_one_new_version(flows, case, second, result, scenario)
    assert improvement_requests(flows) == llm_before + 2  # one LLM answer per job, nothing replayed
    check_activation_and_rollback(flows, case, new, scenario)
    finish_load(flows, load, scenario)


# ---------------------------------------------------------------------------- R-07 with a runtime restart
@pytest.mark.criteria(6, 8)
def test_r_07_runtime_restarted_while_candidate_is_tested_rerun_publishes_exactly_one_version(
    flows: Flows, run_id: str
) -> None:
    """SIGKILL of handler-runtime while it tests the candidate (and executes calls of the load run); it stays
    down until the assistant's job has reacted, then starts again. The interrupted job publishes nothing; a
    repeated run publishes exactly one 1.1.0, activation and rollback work by execution, and the load run
    finishes with every effect once."""
    scenario = "R-07/runtime"
    stack, registry = flows.stack, flows["registry"]
    case = prepare_improvable(flows, f"e2e-{run_id}", scenario)
    load = start_load(flows, f"e2e-{run_id}")
    llm_before = improvement_requests(flows)
    log_offset = len(access_log(stack, "handler-runtime"))

    first = start_improvement(flows["assistant"], case.request)
    sandboxes = wait_candidate_under_test(flows, case, first)
    runtime = flows["handler-runtime"]

    def running_test_runs() -> list[str] | None:
        """Test-run jobs the assistant polls (runtime access log) that the runtime reports as running."""
        polled = polled_jobs(stack, "handler-runtime", log_offset)
        return [j for j in polled if job_of(runtime, "handler", j)["status"] == "running"] or None

    test_runs = wait_for("a test-run job of the candidate running in the runtime", running_test_runs)
    stack.kill_instance("handler-runtime", 1)
    killed_at = time.monotonic()
    load_at_fault = run_view(flows["orchestrator"], load.run)["status"]
    note(
        scenario,
        "runtime killed",
        {
            "job": first,
            "candidate sandboxes": sorted(sandboxes),
            "test-run jobs": test_runs,
            "load": load_at_fault,
        },
    )
    assert load_at_fault == "running"  # the fault happens under load
    assert improvement_requests(flows) == llm_before + 1  # the LLM step was done

    # the runtime stays down until the assistant's job has reacted to it
    assistant = flows["assistant"]
    interrupted = wait_for(
        "assistant job reacts to the runtime being down",
        lambda: j if (j := job_of(assistant, "assistant", first))["status"] in TERMINAL_JOB_STATES else None,
    )
    OBSERVED["assistant_job_runtime_down"] = {
        **job_brief(interrupted),
        "seconds_after_kill": round(time.monotonic() - killed_at, 1),
    }
    note(scenario, "assistant job while the runtime is down", OBSERVED["assistant_job_runtime_down"])
    stack.start_instance("handler-runtime", 1)
    stack.wait_healthy("handler-runtime", 1)
    restarted_at = time.monotonic()
    runtime = flows.reconnect("handler-runtime")
    right_after = {j: job_of(runtime, "handler", j)["status"] for j in test_runs}
    assert version_numbers(registry, case.package_id) == ["1.0.0"]  # the interrupted job published nothing

    # recovery: the improvement is started again (a new Idempotency-Key)
    second, result = improve(assistant, case.request)
    assert second != first
    new = check_one_new_version(flows, case, second, result, scenario)
    assert improvement_requests(flows) == llm_before + 2  # one LLM answer per job, nothing replayed
    check_activation_and_rollback(flows, case, new, scenario)
    load_result = finish_load(flows, load, scenario)

    # the runtime's own record of the test-run jobs the kill interrupted (read again at the end)
    OBSERVED["runtime_test_run_after_restart"] = {
        "jobs": {j: job_brief(job_of(runtime, "handler", j)) for j in test_runs},
        "right_after_restart": right_after,
        "seconds_after_restart": round(time.monotonic() - restarted_at, 1),
    }
    note(scenario, "runtime test-run jobs after the restart", OBSERVED["runtime_test_run_after_restart"])
    note(scenario, "load affected by the restart", load_result["retried"])


# ---------------------------------------------------------------------------- what happens to the interrupted job
@pytest.mark.criteria(8)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "WP-11: the default instance id 'hostname-pid' is the same after a container restart (python is PID 1), "
        "so the restarted assistant renews the lease of the dead job by its heartbeat; the job stays 'running' "
        "(docs/delivery/WP-13.md, R-07)"
    ),
)
def test_r_07_job_of_killed_assistant_fails_after_its_lease() -> None:
    """The README of WP-11: an instance killed with a job running -> after the lease the job is ``failed``
    (``service_unavailable``, retryable), so a client knows it must start the improvement again.

    Repro: ``R-07/assistant`` above - SIGKILL + start of the only assistant replica during an improvement run,
    then ``GET /v1/jobs/{id}`` for two leases (``limits.state.job_lease_ms``) plus two heartbeats."""
    observed = OBSERVED.get("assistant_job_after_kill")
    if observed is None:
        pytest.skip("the assistant-kill scenario did not reach the observation")
    assert observed["status"] == "failed", observed
    assert observed["error"] is not None and observed["error"]["code"] == "service_unavailable", observed


@pytest.mark.criteria(8)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "WP-06: jobs in the runtime's PostgreSQL state have no owner or lease; a job of a killed instance stays "
        "'running' after the restart (docs/delivery/WP-13.md, R-07)"
    ),
)
def test_r_07_runtime_test_run_cut_by_a_kill_becomes_terminal() -> None:
    """A test-run job of handler-runtime cut by a kill of its instance must end (``failed`` or ``cancelled``)
    after the restart, otherwise a client that polls it (the assistant waits up to
    ``clients.job_wait_timeout_ms``, 1 h by default) cannot tell that it will never finish.

    Repro: ``R-07/runtime`` above - SIGKILL of the only runtime replica while it runs a test-run job, start,
    then ``GET /v1/jobs/{id}`` on the runtime at the end of the scenario (well after the sandbox wall time)."""
    observed = OBSERVED.get("runtime_test_run_after_restart")
    if observed is None:
        pytest.skip("the runtime-restart scenario did not reach the observation")
    statuses = {j: o["status"] for j, o in observed["jobs"].items()}
    assert statuses and all(s in TERMINAL_JOB_STATES for s in statuses.values()), observed
