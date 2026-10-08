"""Reliability scenarios R-01, R-03 and R-08 on orchestrated chains (docs/acceptance/scenarios.md; criterion 8,
partly 13).

Real services: orchestrator (WP-09), web-collector (WP-02), handler-runtime (WP-06), storage (WP-07), registry
(WP-05), testsite and PostgreSQL (WP-01); no stand-ins. Orchestrated stages send no ``package_archive``: the
example extractor of the SDK and the fixture ``tests/e2e/packages/e2e.slow-product-extractor`` (whose
``params.delay_seconds`` keeps one extraction call in flight for a given time) are published to the real
registry, and handler-runtime downloads them from it and checks the pinned digest.

Faults are injected with Docker only: ``docker pause``/``unpause`` and ``docker kill``/``start`` of orchestrator
replicas (R-01), ``docker network disconnect``/``connect`` of storage (R-03).

Everything the scenarios assert about the product is read through the public contracts (orchestrator.v1,
collector.v1, storage.v1). Observations outside the contracts (operational, documented in the service
READMEs): the orchestrator counter ``jane_orchestrator_leases_reclaimed_total`` and the jane-kit request
counter ``jane_http_requests_total`` of handler-runtime (``/metrics``); JSON log lines ``orchestrator started``
(worker threads, engine limits) and ``item lease reclaimed`` of the orchestrator, the jane-kit access log
``request`` (path, status, duration, time) of handler-runtime; the Docker labels of runtime sandboxes
(``io.jane.invocation-id``, ``io.jane.package``, ``io.jane.e2e-project``).
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import (
    CONNECTIONS,
    RULES_REF,
    TESTSITE,
    create_source,
    create_task,
    list_items,
    m1_task,
    start_run,
    wait_run,
)
from jane_e2e.stack import E2EStack, StackError
from jane_e2e.steps import sandbox_limits
from jane_e2e.verify import assert_effects_once, site_paths
from jane_registry.archive import canonical_archive, files_from_dir

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

POLL_S = 0.2
STORE_STAGES = frozenset({"store-raw", "store-products"})
HANDLER_STAGES = frozenset({"store-raw", "extract-products", "store-products"})
TERMINAL_ITEM = frozenset({"completed", "failed", "skipped", "cancelled"})
OTHERS = ["/catalog/phones/", "/pages/faq"]  # RAW only: no binding of the extractor matches them
LEASES_RECLAIMED = "jane_orchestrator_leases_reclaimed_total"
HTTP_REQUESTS = "jane_http_requests_total"  # jane-kit metrics of every service

PACKAGES = Path(__file__).resolve().parent / "packages"
SLOW_EXTRACTOR = "e2e.slow-product-extractor"
SLOW_PRODUCT = "/product/phone-alpha"
# Labels of handler-runtime sandboxes (docker_sandbox.py, sandbox.py; the project label comes from
# JANE_HANDLER_RUNTIME_SANDBOX_LABELS in tests/e2e/compose.e2e.yaml).
INVOCATION_LABEL = "io.jane.invocation-id"
PACKAGE_LABEL = "io.jane.package"
PROJECT_LABEL = "io.jane.e2e-project"


# ---------------------------------------------------------------------------- helpers
def wait_for[T](what: str, probe: Callable[[], T | None], timeout_s: float = 120.0) -> T:
    """Poll ``probe`` until it returns a value other than ``None`` (no blind sleeps)."""
    deadline = time.monotonic() + timeout_s
    while True:
        value = probe()
        if value is not None:
            return value
        if time.monotonic() > deadline:
            raise TimeoutError(f"{what}: not reached in {timeout_s:.0f}s")
        time.sleep(POLL_S)


def run_view(orch: JaneClient, run_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get(f"/v1/runs/{run_id}")
    assert r.status_code == 200, r.text
    return dict(r.json())


def handler_items(orch: JaneClient, run_id: str) -> list[dict[str, Any]]:
    return [i for i in list_items(orch, run_id) if i["stage_id"] in HANDLER_STAGES]


def queue_idle(orch: JaneClient) -> bool | None:
    """True when no run of any task is queued, running or cancelling (nothing else occupies the workers)."""
    for status in ("queued", "running", "cancelling"):
        r = orch.api("orchestrator").get("/v1/runs", params={"status": status, "limit": 1})
        assert r.status_code == 200, r.text
        if r.json()["items"]:
            return None
    return True


def connections_synced(orch: JaneClient, executor: str) -> bool | None:
    """True when no registered connection waits to be pushed to ``executor`` (``PlatformConnection``)."""
    for conn in CONNECTIONS:
        r = orch.api("orchestrator").get(f"/v1/connections/{conn['connection_id']}")
        assert r.status_code == 200, r.text
        if any(
            e["executor"] == executor and e["sync_status"] == "pending" for e in r.json().get("executors", [])
        ):
            return None
    return True


def effective_limits(orch: JaneClient, task_id: str, stage_id: str) -> dict[str, Any]:
    r = orch.api("orchestrator").get(
        "/v1/limits/effective", params={"task_id": task_id, "stage_id": stage_id}
    )
    assert r.status_code == 200, r.text
    return dict(r.json()["limits"])


_PROM_LINE = re.compile(r"^(?P<name>[A-Za-z_:][A-Za-z0-9_:]*)(?:\{(?P<labels>[^}]*)\})?\s+(?P<value>\S+)")
_PROM_LABEL = re.compile(r'(\w+)="((?:[^"\\]|\\.)*)"')


def prom_value(text: str, name: str, **labels: str) -> float | None:
    """Sum of the samples ``name`` whose labels include ``labels`` (Prometheus text format); None if absent."""
    found: float | None = None
    for line in text.splitlines():
        m = _PROM_LINE.match(line)
        if m is None or m["name"] != name:
            continue
        sample = dict(_PROM_LABEL.findall(m["labels"] or ""))
        if all(sample.get(k) == v for k, v in labels.items()):
            found = (found or 0.0) + float(m["value"])
    return found


def metrics_text(service: JaneClient) -> str:
    r = service.http.get("/metrics")
    assert r.status_code == 200, r.text
    return r.text


def reclaimed_leases(orch: JaneClient) -> float:
    """Lease take-overs counted by one orchestrator replica since its start (jane-kit ``/metrics``)."""
    value = prom_value(metrics_text(orch), LEASES_RECLAIMED)
    assert value is not None, f"{LEASES_RECLAIMED} is not exported by {orch.base_url}/metrics"
    return value


def runtime_invocations(runtime: JaneClient, status: int) -> float:
    """``POST /v1/invocations`` answered with ``status`` by one runtime instance since its start."""
    text = metrics_text(runtime)
    return prom_value(text, HTTP_REQUESTS, method="POST", route="/v1/invocations", status=str(status)) or 0.0


def log_records(stack: E2EStack, service: str, index: int = 1, *, echo: bool = True) -> list[dict[str, Any]]:
    """JSON log records of one replica (jane-kit JSON logs; ``JANE_ORCHESTRATOR_LOG_FORMAT=json``)."""
    out = []
    for line in stack.logs(service, index, echo=echo).splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def log_time(record: dict[str, Any]) -> datetime:
    """Time of a log record (``ts``, UTC); every container of the stack reads the same engine clock."""
    return datetime.fromisoformat(str(record["ts"]))


def started_record(stack: E2EStack, index: int) -> dict[str, Any]:
    started = [r for r in log_records(stack, "orchestrator", index) if r.get("msg") == "orchestrator started"]
    assert started, f"orchestrator#{index}: no 'orchestrator started' log line"
    return started[-1]


def worker_threads(stack: E2EStack, index: int) -> int:
    """Worker threads of one orchestrator replica, from its own start-up log line."""
    return int(started_record(stack, index)["workers"])


def engine_limits(stack: E2EStack, index: int) -> dict[str, Any]:
    """Effective ``engine`` limits of one orchestrator replica (lease, heartbeat, polling), from its start-up
    log line - the e2e overlay shortens them, so the scenarios derive their timing from these values."""
    record = started_record(stack, index)
    engine = ((record.get("limits") or {}).get("limits") or {}).get("engine")
    assert isinstance(engine, dict) and "lease_ms" in engine, record.get("limits")
    return engine


def task_with(
    run_id: str, name: str, extractor: dict[str, Any], urls: list[str], limits: dict[str, Any]
) -> dict[str, Any]:
    source_id = task_id = f"e2e-{run_id}-{name}"
    return m1_task(task_id, source_id, urls, extractor, limits=limits)


def registry_package(stack: E2EStack, name: str) -> dict[str, Any]:
    """Fixture package of ``tests/e2e/packages`` published to the REAL registry of the stack and approved (its
    manifest is checked against the contract first); returns the pinned ``PackageRef`` with the registry digest.
    Orchestrated stages send no ``package_archive``, so the executor downloads this archive and checks it."""
    archive = canonical_archive(files_from_dir(PACKAGES / name))
    manifest = json.loads((PACKAGES / name / "jane-package.json").read_text(encoding="utf-8"))
    return stack.publish_local_package(manifest["package_id"], manifest["version"], archive)


def slow_extraction(task: dict[str, Any], delay_s: float) -> None:
    """``extract-products`` of an M1 task built with the slow fixture: one call lasts ``delay_s`` and the
    runtime still answers it synchronously (``sync_response_max_ms`` above the call), so its delivery key stays
    ``in_progress`` in the runtime for the whole call instead of turning into a stored 202 + job."""
    [stage] = [s for s in task["stages"] if s["stage_id"] == "extract-products"]
    wall = max(int(sandbox_limits()["sandbox"]["wall_time_ms"]), int((delay_s + 30) * 1000))
    stage["params"] = {"delay_seconds": delay_s}
    stage["limits"] = {
        "sandbox": {"wall_time_ms": wall},
        "timeouts": {"sync_response_max_ms": wall + 10_000, "invocation_timeout_ms": wall + 30_000},
    }


def sandbox_labels(stack: E2EStack, package: dict[str, Any]) -> dict[str, str]:
    """Labels of the runtime sandboxes of ``package`` in this stack."""
    return {PROJECT_LABEL: stack.project, PACKAGE_LABEL: f"{package['package_id']}@{package['version']}"}


def backoff_ms(policy: dict[str, Any], attempt: int) -> float:
    """RetryPolicy without jitter: the delay after the failed attempt ``attempt``."""
    delay = policy["initial_backoff_ms"] * policy["backoff_multiplier"] ** (attempt - 1)
    return float(min(delay, policy["max_backoff_ms"]))


# ---------------------------------------------------------------------------- R-01
@pytest.mark.criteria(8)
def test_r_01_lease_lost_during_active_call_taken_over_with_409_without_spent_attempt(
    stack: E2EStack,
    orchestrated: JaneClient,
    client: Callable[..., JaneClient],
    run_id: str,
) -> None:
    """R-01: two orchestrator replicas on one database. Replica 1 holds the lease of a long extraction call
    and is killed (SIGKILL) while handler-runtime still executes that call, then it is restarted. Replica 2
    takes the expired lease over and repeats the call with the same delivery key: the runtime answers 409
    ``idempotency_in_progress`` until the orphaned call ends and then replays its result. The take-over
    spends no retry attempt, the handler runs once and every effect happens once."""
    storage, runtime = client("storage"), client("handler-runtime")
    slow = registry_package(stack, SLOW_EXTRACTOR)
    products = [SLOW_PRODUCT]
    urls = [TESTSITE + p for p in products + OTHERS]
    task = task_with(run_id, "r01", slow, urls, {})
    # retries are available, so `attempts == 1` below means the take-over did not consume any of them
    task["retries"] = {
        "max_attempts": 3,
        "initial_backoff_ms": 500,
        "backoff_multiplier": 2,
        "max_backoff_ms": 2000,
        "jitter": False,
    }
    source_id, task_id = task["input"]["source_id"], task["task_id"]
    sandbox = sandbox_labels(stack, slow)

    stack.scale("orchestrator", 2)
    replica1, replica2 = client("orchestrator", 1), client("orchestrator", 2)
    paused = False
    try:
        workers = worker_threads(stack, 1)
        engine = engine_limits(stack, 1)
        assert workers >= 1 and worker_threads(stack, 2) == workers
        assert engine_limits(stack, 2)["lease_ms"] == engine["lease_ms"]
        lease_s = engine["lease_ms"] / 1000
        # the orphaned call must outlive the kill, the lease expiry and the claim by replica 2 by a wide
        # margin (relative to the configured lease; the fixture accepts at most 60 s)
        delay_s = min(60.0, 3 * lease_s + 6)
        slow_extraction(task, delay_s)

        wait_for("no other run in the orchestrator queue", lambda: queue_idle(replica1), timeout_s=300)
        reclaimed_before = reclaimed_leases(replica2)
        conflicts_before = runtime_invocations(runtime, 409)
        runtime_offset = len(log_records(stack, "handler-runtime"))
        replica2_offset = len(log_records(stack, "orchestrator", 2))
        create_source(replica1, source_id)
        create_task(replica1, task)
        limits = effective_limits(replica1, task_id, "extract-products")
        assert limits["timeouts"]["sync_response_max_ms"] > delay_s * 1000, limits
        assert limits["sandbox"]["wall_time_ms"] > delay_s * 1000, limits

        # replica 2 stays frozen until the extraction call runs, so replica 1 is the one holding its lease
        stack.pause_instance("orchestrator", 2)
        paused = True
        run_key = f"r06-{run_id}"
        run = start_run(replica1, task_id, key=run_key)

        # 1. replica 1 is inside the extraction call: the sandbox of the slow package runs
        seen: set[str] = set()  # invocation ids of every sandbox of the slow package seen running

        def sandbox_running() -> set[str] | None:
            active = set(stack.running_label_values(sandbox, INVOCATION_LABEL))
            seen.update(active)
            return active or None

        wait_for("slow extraction running in a sandbox", sandbox_running, timeout_s=300)
        [extract] = [i for i in list_items(replica1, run, "extract-products") if i["status"] != "skipped"]
        assert extract["status"] == "running" and extract["attempts"] == 1, extract

        # 2. replica 2 resumes; replica 1 dies (SIGKILL) with the call in flight
        stack.unpause_instance("orchestrator", 2)
        paused = False
        stack.kill_instance("orchestrator", 1)

        # 3. replica 2 reclaims the expired lease of the extraction item
        def reclaim_record() -> dict[str, Any] | None:
            seen.update(stack.running_label_values(sandbox, INVOCATION_LABEL))
            for r in log_records(stack, "orchestrator", 2, echo=False)[replica2_offset:]:
                if r.get("msg") == "item lease reclaimed" and r.get("item_id") == extract["item_id"]:
                    return r
            return None

        reclaim = wait_for("extraction lease reclaimed by replica 2", reclaim_record, timeout_s=lease_s + 120)
        active_at_reclaim = set(stack.running_label_values(sandbox, INVOCATION_LABEL))
        seen.update(active_at_reclaim)

        # 4. replica 2 completes the item with the result of the orphaned call
        def extraction_finished() -> dict[str, Any] | None:
            seen.update(stack.running_label_values(sandbox, INVOCATION_LABEL))
            [item] = [i for i in list_items(replica2, run, "extract-products") if i["status"] != "skipped"]
            return item if item["status"] in TERMINAL_ITEM else None

        taken_over = wait_for(
            "extraction finished by replica 2", extraction_finished, timeout_s=delay_s + 180
        )

        # 5. restart of the killed replica; it rejoins the same queue
        stack.start_instance("orchestrator", 1)
        stack.wait_healthy("orchestrator", 1)
        final = wait_run(replica2, run)
        replayed = replica2.api("orchestrator").post(
            f"/v1/tasks/{task_id}/runs",
            json={"reason": "e2e"},
            headers={"Idempotency-Key": run_key},
        )
        assert replayed.status_code == 202, replayed.text
        assert replayed.headers["Idempotency-Replayed"] == "true"
        assert replayed.json()["job_id"] == run
        restarted_orchestrator = client("orchestrator", 1)
        replayed_after_restart = restarted_orchestrator.api("orchestrator").post(
            f"/v1/tasks/{task_id}/runs",
            json={"reason": "e2e"},
            headers={"Idempotency-Key": run_key},
        )
        assert replayed_after_restart.status_code == 202, replayed_after_restart.text
        assert replayed_after_restart.headers["Idempotency-Replayed"] == "true"
        assert replayed_after_restart.json() == replayed.json()
        restarted_view = run_view(restarted_orchestrator, run)
        items = handler_items(replica2, run)  # replica 2 is removed by the scale-down below
        reclaimed = reclaimed_leases(replica2) - reclaimed_before
        reclaim_log = {
            r["item_id"]
            for r in log_records(stack, "orchestrator", 2)[replica2_offset:]
            if r.get("msg") == "item lease reclaimed"
        }
    finally:
        if paused:
            stack.unpause_instance("orchestrator", 2)
        try:
            if not stack.state("orchestrator", 1).get("Running"):
                stack.start_instance("orchestrator", 1)
        except StackError:
            pass
        stack.scale("orchestrator", 1)

    conflicts = runtime_invocations(runtime, 409) - conflicts_before
    calls = [
        r
        for r in log_records(stack, "handler-runtime")[runtime_offset:]
        if r.get("msg") == "request" and r.get("method") == "POST" and r.get("path") == "/v1/invocations"
    ]
    in_progress = [r for r in calls if r.get("status") == 409]
    answered = [r for r in calls if r.get("status") == 200]
    assert answered, calls
    orphan = max(answered, key=lambda r: float(r.get("duration_ms", 0)))  # the call replica 1 left behind
    print(
        f"\nR-01: workers/replica={workers} lease={lease_s:g}s call={delay_s:g}s "
        f"sandboxes={sorted(seen)} active at reclaim={sorted(active_at_reclaim)}"
        f"\nR-01: reclaim(replica 2)={reclaim['ts']} 409 answers={len(in_progress)} (metric +{conflicts:g}) "
        f"first={in_progress[0]['ts'] if in_progress else None} last={in_progress[-1]['ts'] if in_progress else None}"
        f"\nR-01: orphaned call ended={orphan['ts']} after {orphan['duration_ms']} ms; item "
        f"attempts={taken_over['attempts']} status={taken_over['status']}/{taken_over.get('result_status')} "
        f"invocation={taken_over.get('invocation_id')} reclaimed={reclaimed:g} run={final['status']}"
    )
    assert final["status"] == "succeeded", final
    assert restarted_view["status"] == "succeeded", restarted_view
    assert final["counters"]["materials"] == len(urls), final
    stages = {s["stage_id"]: s.get("counts", {}) for s in final["stages"]}
    assert stages["store-raw"].get("success") == len(urls), stages
    assert stages["extract-products"].get("success") == len(products), stages
    assert stages["store-products"].get("success") == len(products), stages

    # the lease of the call in flight was taken over by replica 2 while that call still ran in the runtime
    assert reclaimed >= 1, reclaimed
    assert extract["item_id"] in reclaim_log, (extract, reclaim_log)
    assert reclaim_log <= {i["item_id"] for i in items}, (reclaim_log, items)
    assert float(orphan["duration_ms"]) >= delay_s * 1000, orphan
    assert log_time(reclaim) < log_time(orphan), (reclaim, orphan)
    # the repeated call met the delivery key in progress: 409, answered before the orphaned call ended
    assert conflicts >= 1 and in_progress, (conflicts, calls)
    assert all(log_time(r) >= log_time(reclaim) for r in in_progress), (reclaim, in_progress)
    assert log_time(in_progress[0]) < log_time(orphan), (in_progress[0], orphan)
    # the handler ran once: one sandbox, and the item carries the result of exactly that invocation
    assert seen == {taken_over.get("invocation_id")}, (seen, taken_over)
    # the 409 did not spend an attempt; nothing else did either
    assert taken_over["status"] == "completed" and taken_over.get("result_status") == "success", taken_over
    assert taken_over["attempts"] == 1, taken_over
    assert all(i["status"] == "completed" for i in items), [i for i in items if i["status"] != "completed"]
    assert all(i["attempts"] == 1 for i in items), [(i["stage_id"], i["attempts"]) for i in items]
    # every effect once: one RAW object per material, one entity and one history event per product
    assert_effects_once(storage, source_id, materials=len(urls), products=len(products))


# ---------------------------------------------------------------------------- R-03
# Delays well above the worker polling interval and the API latency, so that the bounds read by polling stay
# decisive on a loaded host (3 s, then 6 s; jitter off to compare with exact values).
R03_POLICY = {
    "max_attempts": 8,
    "initial_backoff_ms": 3000,
    "backoff_multiplier": 2,
    "max_backoff_ms": 12000,
    "jitter": False,
}
R03_HOLD_S = 15.0  # the extraction keeps store-products back until the partition is in place
R03_POLL_S = 0.1  # target period of the polling: the resolution of both bounds of every wait
# The orchestrator schedules `available_at = now() + delay` with now() = start of the retry transaction, so the
# visible `retrying` state may be shorter than the delay by the duration of that transaction.
R03_COMMIT_TOLERANCE_MS = 250


class Poll(NamedTuple):
    sent: float  # time.monotonic() before the request
    received: float  # time.monotonic() after the response
    item: dict[str, Any] | None  # the store-products item (None until it exists)
    running: int  # items of the run in status `running`


class RetryWait(NamedTuple):
    attempt: int  # the failed attempt the item waits after
    delay_ms: float  # policy delay after that attempt
    lower_ms: float  # proven minimum of the wait (last poll still `retrying` - first poll `retrying`)
    upper_ms: float  # proven maximum (first poll of the next attempt - last poll before `retrying`)
    polls: int  # polls that saw the item `retrying`
    isolated: bool  # no item of the run was running at any of those polls


def retry_waits(polls: list[Poll], policy: dict[str, Any]) -> list[RetryWait]:
    """Bounds of every observed wait between a failed attempt and the claim of the next one.

    A poll reads the database at some moment between ``sent`` and ``received``. With ``a`` the first and ``b``
    the last poll that saw the item ``retrying`` after attempt ``n``, the wait began after poll ``a - 1`` was
    sent and before ``a`` was received, and ended after ``b`` was sent and before ``b + 1`` was received.
    """
    waits: list[RetryWait] = []
    retrying: list[tuple[int, dict[str, Any]]] = []
    for n, p in enumerate(polls):
        if p.item is not None and p.item["status"] == "retrying":
            retrying.append((n, p.item))
    for attempt in sorted({int(item["attempts"]) for _, item in retrying}):
        idx = [n for n, item in retrying if item["attempts"] == attempt]
        a, b = idx[0], idx[-1]
        if a == 0 or b + 1 >= len(polls):
            continue  # no poll before or after the wait: one of the bounds is unknown
        after = polls[b + 1].item
        assert after is not None and after["attempts"] >= attempt + 1, (attempt, after)
        waits.append(
            RetryWait(
                attempt=attempt,
                delay_ms=backoff_ms(policy, attempt),
                lower_ms=(polls[b].sent - polls[a].received) * 1000,
                upper_ms=(polls[b + 1].received - polls[a - 1].sent) * 1000,
                polls=b - a + 1,
                isolated=all(p.running == 0 for p in polls[a : b + 1]),
            )
        )
    return waits


@pytest.mark.criteria(8)
def test_r_03_partition_to_storage_isolated_retry_waits_for_backoff_without_duplicates(
    stack: E2EStack,
    orchestrated: JaneClient,
    client: Callable[..., JaneClient],
    run_id: str,
) -> None:
    """R-03: storage is disconnected from the stack network in the middle of a run - the RAW of the material
    is already stored, its extraction still runs - and reconnected after two failed attempts of
    ``store-products``. That storage item is then the only unfinished item of the run, so a worker and the
    stage slot are free while it waits: frequent polling of the items API bounds each wait from both sides
    and compares it with the configured backoff. After the partition the run completes, nothing twice."""
    orch = orchestrated
    slow = registry_package(stack, SLOW_EXTRACTOR)
    policy = dict(R03_POLICY)
    products = [SLOW_PRODUCT]
    task = task_with(run_id, "r03", slow, [TESTSITE + p for p in products], {})
    slow_extraction(task, R03_HOLD_S)
    for stage in task["stages"]:
        if stage["stage_id"] in STORE_STAGES:
            stage["retries"] = policy
            # a call on a pooled connection to the vanished peer fails by this timeout, not by the default
            stage["limits"] = {"timeouts": {"invocation_timeout_ms": 5_000}}
    source_id, task_id = task["input"]["source_id"], task["task_id"]
    engine = engine_limits(stack, 1)
    poll_ms = float(engine["poll_interval_ms"])  # an idle worker looks for work this often
    # half of the shortest delay must be well above the claim latency of a free worker
    assert backoff_ms(policy, 1) / 2 > poll_ms, (policy, engine)

    wait_for("no other run in the orchestrator queue", lambda: queue_idle(orch), timeout_s=300)
    # no connection push to storage may be pending: it would occupy a worker during the partition
    wait_for("connections synced to storage", lambda: connections_synced(orch, "storage"), timeout_s=120)
    create_source(orch, source_id)
    create_task(orch, task)
    run = start_run(orch, task_id)

    def raw_stored_extraction_running() -> bool | None:
        by_stage = {i["stage_id"]: i for i in handler_items(orch, run)}
        raw, extract = by_stage.get("store-raw"), by_stage.get("extract-products")
        done = raw is not None and raw["status"] == "completed" and extract is not None
        return True if done and extract is not None and extract["status"] == "running" else None

    wait_for("RAW stored while the extraction runs", raw_stored_extraction_running, timeout_s=300)

    polls: list[Poll] = []
    published_before = stack.url("storage")
    stack.disconnect("storage")
    try:
        # the partition is in place before store-products made its first attempt
        before = [i for i in handler_items(orch, run) if i["stage_id"] == "store-products"]
        assert all(i["attempts"] == 0 for i in before), before
        deadline = time.monotonic() + R03_HOLD_S + 300
        while True:
            sent = time.monotonic()
            items = handler_items(orch, run)
            received = time.monotonic()
            target = [i for i in items if i["stage_id"] == "store-products"]
            assert len(target) <= 1, target
            running = sum(1 for i in items if i["status"] == "running")
            polls.append(Poll(sent, received, target[0] if target else None, running))
            if target and target[0]["attempts"] >= 3:
                break  # two failed attempts and two waits observed
            if time.monotonic() > deadline:
                raise AssertionError(f"store-products did not reach its third attempt: {run_view(orch, run)}")
            time.sleep(max(0.0, R03_POLL_S - (received - sent)))
    finally:
        stack.reconnect("storage")

    final = wait_run(orch, run)
    items = handler_items(orch, run)
    # storage is read from the host only now, through its current published port: after the reconnect
    # Docker Engine on Linux may publish it on another host port (or lose the binding - then it restarts it)
    published_after = stack.published_url("storage")
    storage = client("storage")
    errors = [
        p.item["error"]
        for p in polls
        if p.item is not None and p.item["status"] == "retrying" and p.item.get("error")
    ]
    waits = retry_waits(polls, policy)
    latency_ms = sorted((p.received - p.sent) * 1000 for p in polls)
    print(
        f"\nR-03: polls={len(polls)} poll latency ms median={latency_ms[len(latency_ms) // 2]:.0f} "
        f"max={latency_ms[-1]:.0f}; worker poll={poll_ms:g} ms; codes={sorted({str(e.get('code')) for e in errors})} "
        f"run={final['status']}; storage on the host {published_before} -> {published_after}"
        f"\nR-03: failure details={sorted({str(e.get('detail'))[:120] for e in errors})}"
        "\nR-03: waits (attempt, policy delay ms, lower..upper ms, polls, isolated): "
        f"{[(w.attempt, w.delay_ms, round(w.lower_ms), round(w.upper_ms), w.polls, w.isolated) for w in waits]}"
    )
    assert final["status"] == "succeeded", final
    assert final["counters"]["materials"] == len(products), final

    # the orchestrator saw the partition as a retryable failure of the storage executor
    assert errors
    assert all(e.get("retryable") is True for e in errors), errors
    assert all(e.get("code") == "upstream_unavailable" for e in errors), errors
    assert all((e.get("details") or {}).get("executor") == "storage" for e in errors), errors

    # backoff. The API exposes neither `available_at` nor a claim history, so each wait is known only between
    # two bounds read by polling; the causal claim is limited to what these bounds prove.
    assert {1, 2} <= {w.attempt for w in waits}, (waits, polls)
    for w in waits:
        # isolated: no item of the run was running during the wait, so a worker and the stage slot were free
        # (the queue held no other run, no connection push was pending)
        assert w.isolated, w
        # not claimed before the policy delay had elapsed
        assert w.upper_ms >= w.delay_ms - R03_COMMIT_TOLERANCE_MS, w
        # held back for at least half of the delay although a free worker looked for work every poll_ms
        assert w.lower_ms >= w.delay_ms / 2, w
        # and claimed within the order of the delay - the wait is not explained by something slower
        assert w.upper_ms <= 2 * w.delay_ms + 5_000, w

    # after the partition: everything completed within the policy, the retried item included, nothing twice
    assert all(i["status"] == "completed" and i["result_status"] == "success" for i in items), items
    attempts = {i["stage_id"]: i["attempts"] for i in items}
    assert attempts["store-raw"] == 1 and attempts["extract-products"] == 1, attempts
    assert 3 <= attempts["store-products"] <= policy["max_attempts"], attempts
    assert_effects_once(storage, source_id, materials=len(products), products=len(products))
    # Docker reconnect may leave an HTTP keep-alive socket in the orchestrator pointing at
    # the old storage endpoint. Reset that client pool before the next, independent scenario.
    stack.kill("orchestrator")
    stack.restart("orchestrator")


# ---------------------------------------------------------------------------- R-08
R08_UNACKED_LIMIT = 2


@pytest.mark.criteria(8, 13)
def test_r_08_bounded_queue_holds_back_collection(
    orchestrated: JaneClient, client: Callable[..., JaneClient], extractor: dict[str, Any], run_id: str
) -> None:
    """R-08: a small collector buffer (``queue.max_unacked_materials``) and a slow consumer (the orchestrator
    takes one material at a time, ``queue.max_inflight_materials: 1``, each one extracted in the sandbox).
    The collector pauses (``paused_by_backpressure``) while pages are still to be fetched, resumes after the
    orchestrator consumed the buffer, and the run completes without duplicates. The exact bound of the
    buffer is checked by ``test_r_08_collector_buffer_never_exceeds_max_unacked``."""
    orch, collector, storage = orchestrated, client("web-collector"), client("storage")
    products = site_paths("product")[:8]
    urls = [TESTSITE + p for p in products]
    limits = {"queue": {"max_unacked_materials": R08_UNACKED_LIMIT, "max_inflight_materials": 1}}
    task = task_with(run_id, "r08", extractor, urls, limits)
    source_id, task_id = task["input"]["source_id"], task["task_id"]
    create_source(orch, source_id)
    create_task(orch, task)
    effective = orch.api("orchestrator").get(
        "/v1/limits/effective", params={"task_id": task_id, "stage_id": "collect"}
    )
    assert effective.status_code == 200, effective.text
    assert effective.json()["limits"]["queue"]["max_unacked_materials"] == R08_UNACKED_LIMIT
    assert effective.json()["provenance"]["queue.max_unacked_materials"] == "task"

    run = start_run(orch, task_id)
    # (orchestrator backpressure, collector paused, unacked, fetched, collection status) over the whole run
    samples: list[tuple[bool, bool, int, int, str]] = []
    deadline = time.monotonic() + 600
    while True:
        view = run_view(orch, run)
        if view.get("collection_id"):
            r = collector.api("collector").get(f"/v1/collections/{view['collection_id']}")
            assert r.status_code == 200, r.text
            col = r.json()
            stats = col["stats"]
            samples.append(
                (
                    bool(view.get("backpressure")),
                    bool(col.get("paused_by_backpressure")),
                    int(stats["unacked"]),
                    int(stats["fetched"]),
                    str(col["status"]),
                )
            )
        if view["status"] in {"succeeded", "failed", "cancelled"}:
            break
        assert time.monotonic() < deadline, f"run {run} still {view['status']}"
        time.sleep(POLL_S)

    collection = collector.api("collector").get(f"/v1/collections/{view['collection_id']}").json()
    paused = [s for s in samples if s[1]]
    print(
        f"\nR-08: samples={len(samples)} paused={len(paused)} orchestrator-backpressure={sum(s[0] for s in samples)} "
        f"max unacked={max(s[2] for s in samples)} (limit {R08_UNACKED_LIMIT}) "
        f"fetched while paused={sorted({s[3] for s in paused})} final stats={collection['stats']}"
    )
    assert view["status"] == "succeeded", view
    assert view["counters"]["materials"] == len(urls), view
    assert collection["effective_limits"]["queue"]["max_unacked_materials"] == R08_UNACKED_LIMIT, collection

    # held back: the collector paused while pages were still to be fetched, the orchestrator saw a full queue
    assert any(s[3] < len(urls) for s in paused), samples
    assert any(s[0] for s in samples), samples
    # resumed: after a pause the collector fetched more pages, and finally all of them
    assert any(later[3] > s[3] for n, s in enumerate(samples) if s[1] for later in samples[n + 1 :]), samples
    assert collection["status"] == "succeeded", collection
    assert not collection.get("paused_by_backpressure"), collection
    stats = collection["stats"]
    assert stats["fetched"] == stats["emitted"] == len(urls), stats
    assert stats["duplicates"] == 0 and stats["errors"] == 0, stats
    assert stats["unacked"] == 0, stats
    assert stats["acknowledged"] == len(urls), stats
    completed = handler_items(orch, run)
    failures = [(i["stage_id"], i.get("error")) for i in completed if i["status"] != "completed"]
    assert completed and not failures, failures
    assert_effects_once(storage, source_id, materials=len(urls), products=len(products))


@pytest.mark.criteria(8, 13)
def test_r_08_collector_buffer_never_exceeds_max_unacked(
    require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """R-08, the bound itself: the collector used directly (collector.v1, no orchestrator) by a consumer that
    reads nothing. With ``queue.max_unacked_materials: 2`` it must pause holding at most 2 unacknowledged
    materials, whatever its fetch parallelism."""
    require("testsite", "web-collector")
    collector = client("web-collector").api("collector")
    body = {
        "source_kind": "web",
        "source_id": f"e2e-{run_id}-r08-buffer",
        "rules_ref": RULES_REF,
        "urls": [TESTSITE + p for p in site_paths("product")[:8]],
        "limits": {"queue": {"max_unacked_materials": R08_UNACKED_LIMIT}},
    }
    r = collector.post("/v1/collections", json=body, headers={"Idempotency-Key": f"e2e-{run_id}-r08-buffer"})
    assert r.status_code == 202, r.text
    cid = r.json()["job_id"]
    samples: list[dict[str, Any]] = []
    try:

        def settled_pause() -> bool | None:
            r = collector.get(f"/v1/collections/{cid}")
            assert r.status_code == 200, r.text
            samples.append(r.json())
            # paused for 10 consecutive polls (2 s): the fetches that were in flight have landed
            tail = samples[-10:]
            return True if len(tail) == 10 and all(s.get("paused_by_backpressure") for s in tail) else None

        wait_for("collector paused by backpressure", settled_pause, timeout_s=60)
    finally:
        collector.post(f"/v1/jobs/{cid}/cancel", json={"reason": "e2e R-08 buffer check done"})
    unacked = [s["stats"]["unacked"] for s in samples]
    print(f"\nR-08 buffer: limit={R08_UNACKED_LIMIT} unacked over time={unacked}")
    assert samples[-1]["effective_limits"]["queue"]["max_unacked_materials"] == R08_UNACKED_LIMIT
    assert samples[-1]["stats"]["fetched"] < len(body["urls"])  # held back
    assert max(unacked) <= R08_UNACKED_LIMIT, unacked
