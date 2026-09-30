"""Reliability scenarios R-01, R-03 and R-08 on orchestrated chains (docs/acceptance/scenarios.md; criterion 8,
partly 13).

Real services: orchestrator (WP-09), web-collector (WP-02), handler-runtime (WP-06), storage (WP-07), testsite
and PostgreSQL (WP-01). The only stand-in is ``package-host`` (Т): it serves the archive of the LOCAL example
extractor because orchestrated stages send no ``package_archive``.

Faults are injected with Docker only: ``docker kill`` / ``docker start`` of one orchestrator replica (R-01),
``docker network disconnect`` / ``connect`` of storage (R-03). R-01 additionally ``docker pause``-s storage for a
few seconds: every worker thread then sits inside a storage call, so the kill always lands on held item leases
(a worker thread holds at most one) instead of on a random moment between two calls.

Everything the scenarios check is read through the public contracts (orchestrator.v1, collector.v1,
storage.v1). Two observations are operational, not contract fields: the orchestrator's Prometheus counter
``jane_orchestrator_leases_reclaimed_total`` (jane-kit ``/metrics``) and its JSON log lines
``orchestrator started`` (number of worker threads) and ``item lease reclaimed`` (which item was taken over).
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import (
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
from jane_e2e.verify import assert_effects_once, site_paths

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2")]

POLL_S = 0.2
STORE_STAGES = frozenset({"store-raw", "store-products"})
HANDLER_STAGES = frozenset({"store-raw", "extract-products", "store-products"})
OTHERS = ["/catalog/phones/", "/pages/faq"]  # RAW only: no binding of the extractor matches them
LEASES_RECLAIMED = "jane_orchestrator_leases_reclaimed_total"


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


def reclaimed_leases(orch: JaneClient) -> float:
    """Lease take-overs counted by one orchestrator replica since its start (jane-kit ``/metrics``)."""
    r = orch.http.get("/metrics")
    assert r.status_code == 200, r.text
    for line in r.text.splitlines():
        if line.startswith(LEASES_RECLAIMED + " "):
            return float(line.split()[1])
    raise AssertionError(f"{LEASES_RECLAIMED} is not exported by {orch.base_url}/metrics")


def log_records(stack: E2EStack, service: str, index: int) -> list[dict[str, Any]]:
    """JSON log records of one replica (``JANE_ORCHESTRATOR_LOG_FORMAT=json``)."""
    out = []
    for line in stack.logs(service, index).splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def worker_threads(stack: E2EStack, index: int) -> int:
    """Worker threads of one orchestrator replica, from its own start-up log line."""
    started = [r for r in log_records(stack, "orchestrator", index) if r.get("msg") == "orchestrator started"]
    assert started, f"orchestrator#{index}: no 'orchestrator started' log line"
    return int(started[-1]["workers"])


def task_with(
    run_id: str, name: str, extractor: dict[str, Any], urls: list[str], limits: dict[str, Any]
) -> dict[str, Any]:
    source_id = task_id = f"e2e-{run_id}-{name}"
    return m1_task(task_id, source_id, urls, extractor, limits=limits)


def backoff_ms(policy: dict[str, Any], attempt: int) -> float:
    """RetryPolicy without jitter: the delay after the failed attempt ``attempt``."""
    delay = policy["initial_backoff_ms"] * policy["backoff_multiplier"] ** (attempt - 1)
    return float(min(delay, policy["max_backoff_ms"]))


# ---------------------------------------------------------------------------- R-01
@pytest.mark.criteria(8)
def test_r_01_killed_orchestrator_worker_lease_taken_over_without_double_effects(
    stack: E2EStack,
    orchestrated: JaneClient,
    client: Callable[..., JaneClient],
    extractor: dict[str, Any],
    run_id: str,
) -> None:
    """R-01: two orchestrator replicas on one database; replica 1 is killed (SIGKILL) in the middle of the
    chain while its workers hold item leases, then restarted. The run completes, every effect happens once,
    replica 2 takes the expired leases over and the take-over does not spend retry attempts."""
    storage = client("storage")
    products = site_paths("product")[:8]
    urls = [TESTSITE + p for p in products + OTHERS]
    # a slow collection (contract limit, 2 pages/s) keeps the run in progress around the kill
    task = task_with(run_id, "r01", extractor, urls, {"rate": {"requests_per_second_per_host": 2}})
    # retries are available, so `attempts == 1` below means the kill did not consume any of them
    task["retries"] = {
        "max_attempts": 3,
        "initial_backoff_ms": 500,
        "backoff_multiplier": 2,
        "max_backoff_ms": 2000,
        "jitter": False,
    }
    source_id, task_id = task["input"]["source_id"], task["task_id"]

    stack.scale("orchestrator", 2)
    storage_paused = False
    try:
        survivor = client("orchestrator", 2)  # replica 1 dies: every call of the scenario goes to replica 2
        workers = worker_threads(stack, 1)
        assert workers >= 1 and worker_threads(stack, 2) == workers
        # the counting argument below needs workers that serve this run only
        wait_for("no other run in the orchestrator queue", lambda: queue_idle(survivor), timeout_s=300)
        reclaimed_before = reclaimed_leases(survivor)
        create_source(survivor, source_id)
        create_task(survivor, task)
        run = start_run(survivor, task_id)

        # 1. mid-chain: the run is running and part of the materials is already stored
        def first_raw_stored() -> bool | None:
            view = run_view(survivor, run)
            done = view["status"] == "running" and any(
                s["stage_id"] == "store-raw" and s.get("counts", {}).get("success", 0) >= 1
                for s in view.get("stages", [])
            )
            return True if done else None

        wait_for("first RAW stored while the run is running", first_raw_stored)

        # 2. storage paused: each worker thread that claims a storage item stays inside that call (lease
        #    extended by heartbeats) until every thread of both replicas is there
        stack.pause_instance("storage")
        storage_paused = True

        def all_threads_in_storage_calls() -> set[str] | None:
            running = {
                i["item_id"]
                for i in handler_items(survivor, run)
                if i["stage_id"] in STORE_STAGES and i["status"] == "running"
            }
            assert len(running) <= 2 * workers, running  # a worker thread holds at most one item lease
            return running if len(running) == 2 * workers else None

        held = wait_for(f"{2 * workers} storage calls in flight", all_threads_in_storage_calls)
        run_before_kill = run_view(survivor, run)
        assert run_before_kill["status"] == "running", run_before_kill

        # 3. SIGKILL of replica 1: it holds exactly `workers` of the `held` leases
        stack.kill_instance("orchestrator", 1)
        stack.unpause_instance("storage")
        storage_paused = False

        # 4. replica 2 finishes its own calls at once; the leases of the dead replica stay `running`
        #    until they expire (lease_ms, e2e overlay) - that set is what replica 1 held
        def dead_replica_leases() -> set[str] | None:
            running = {
                i["item_id"]
                for i in handler_items(survivor, run)
                if i["item_id"] in held and i["status"] == "running"
            }
            return running if len(running) <= workers else None

        stale = wait_for("own calls of replica 2 finished", dead_replica_leases, timeout_s=60)
        assert len(stale) == workers, (stale, held)

        # 5. take-over: replica 2 claims the expired leases and completes those items
        def taken_over() -> list[dict[str, Any]] | None:
            items = [i for i in handler_items(survivor, run) if i["item_id"] in held]
            return items if all(i["status"] == "completed" for i in items) else None

        held_items = wait_for("expired leases taken over and completed", taken_over, timeout_s=120)
        reclaimed = reclaimed_leases(survivor) - reclaimed_before
        reclaim_log = {
            r["item_id"]
            for r in log_records(stack, "orchestrator", 2)
            if r.get("msg") == "item lease reclaimed"
        }

        # 6. restart of the killed replica; it rejoins the same queue
        stack.start_instance("orchestrator", 1)
        stack.wait_healthy("orchestrator", 1)
        final = wait_run(survivor, run)
        restarted_view = run_view(client("orchestrator", 1), run)
        items = handler_items(survivor, run)  # replica 2 is removed by the scale-down below
    finally:
        if storage_paused:
            stack.unpause_instance("storage")
        try:
            if not stack.state("orchestrator", 1).get("Running"):
                stack.start_instance("orchestrator", 1)
        except StackError:
            pass
        stack.scale("orchestrator", 1)

    print(
        f"\nR-01: workers/replica={workers} held={len(held)} stale(replica 1)={len(stale)} "
        f"reclaimed={reclaimed:g} reclaim-log&held={len(reclaim_log & held)} run={final['status']}"
    )
    assert final["status"] == "succeeded", final
    assert restarted_view["status"] == "succeeded", restarted_view
    assert final["counters"]["materials"] == len(urls), final
    stages = {s["stage_id"]: s.get("counts", {}) for s in final["stages"]}
    assert stages["store-raw"].get("success") == len(urls), stages
    assert stages["extract-products"].get("success") == len(products), stages
    assert stages["store-products"].get("success") == len(products), stages

    # lease taken over: exactly the leases of the killed replica, by replica 2
    assert reclaimed == workers, (reclaimed, workers)
    assert reclaim_log & held == stale, (reclaim_log, held, stale)
    # retries not spent on the kill: the take-over is not an attempt
    assert all(i["attempts"] == 1 and i["result_status"] == "success" for i in held_items), held_items
    assert all(i["status"] == "completed" for i in items), [i for i in items if i["status"] != "completed"]
    assert all(i["attempts"] == 1 for i in items), [(i["stage_id"], i["attempts"]) for i in items]
    # every effect once: one RAW object per material, one entity and one history event per product
    assert_effects_once(storage, source_id, materials=len(urls), products=len(products))


# ---------------------------------------------------------------------------- R-03
@pytest.mark.criteria(8)
def test_r_03_network_partition_to_storage_retried_with_backoff_without_duplicates(
    stack: E2EStack,
    orchestrated: JaneClient,
    client: Callable[..., JaneClient],
    extractor: dict[str, Any],
    run_id: str,
) -> None:
    """R-03: storage is disconnected from the stack network in the middle of a run and reconnected later.
    The orchestrator retries its storage items with the configured backoff; after the partition the run
    completes and nothing is stored twice."""
    orch, storage = orchestrated, client("storage")
    products = site_paths("product")[:6]
    urls = [TESTSITE + p for p in products + OTHERS]
    policy = {
        "max_attempts": 8,
        "initial_backoff_ms": 1000,
        "backoff_multiplier": 2,
        "max_backoff_ms": 4000,
        "jitter": False,
    }
    task = task_with(run_id, "r03", extractor, urls, {"rate": {"requests_per_second_per_host": 4}})
    for stage in task["stages"]:
        if stage["stage_id"] in STORE_STAGES:
            stage["retries"] = policy
            # a call on a pooled connection to the vanished peer fails by this timeout, not by the default
            stage["limits"] = {"timeouts": {"invocation_timeout_ms": 10_000}}
    source_id, task_id = task["input"]["source_id"], task["task_id"]
    create_source(orch, source_id)
    create_task(orch, task)
    run = start_run(orch, task_id)

    def first_raw_stored() -> bool | None:
        items = handler_items(orch, run)
        return (
            True if any(i["stage_id"] == "store-raw" and i["status"] == "completed" for i in items) else None
        )

    wait_for("first RAW stored", first_raw_stored)

    # (t_sent, t_received, attempts, status) of every storage item, polled while storage is unreachable
    polls: dict[str, list[tuple[float, float, int, str]]] = {}
    errors: list[dict[str, Any]] = []
    stack.disconnect("storage")
    try:
        deadline = time.monotonic() + 180
        while True:
            sent = time.monotonic()
            items = handler_items(orch, run)
            received = time.monotonic()
            for i in items:
                if i["stage_id"] in STORE_STAGES:
                    polls.setdefault(i["item_id"], []).append((sent, received, i["attempts"], i["status"]))
                    if i["status"] == "retrying" and i.get("error"):
                        errors.append(i["error"])
            if errors and any(i["stage_id"] in STORE_STAGES and i["attempts"] >= 3 for i in items):
                break  # at least two failed attempts separated by the backoff
            assert time.monotonic() < deadline, (
                "no storage item reached its third attempt during the partition"
            )
            assert run_view(orch, run)["status"] == "running"
            time.sleep(POLL_S)
    finally:
        stack.reconnect("storage")

    final = wait_run(orch, run)
    print(
        f"\nR-03: retrying errors seen={len(errors)} codes={sorted({str(e.get('code')) for e in errors})} "
        f"max attempts during partition={max(p[2] for h in polls.values() for p in h)} run={final['status']}"
        f"\nR-03: failure details={sorted({str(e.get('detail'))[:120] for e in errors})}"
    )
    assert final["status"] == "succeeded", final
    assert final["counters"]["materials"] == len(urls), final

    # the orchestrator saw the partition as a retryable failure of the storage executor
    assert errors
    assert all(e.get("retryable") is True for e in errors), errors
    assert all(e.get("code") == "upstream_unavailable" for e in errors), errors
    assert all((e.get("details") or {}).get("executor") == "storage" for e in errors), errors

    # backoff: the gap between two claims of an item is at least the policy delay. Only upper bounds of the
    # true gap are known from polling (previous poll sent .. first poll that sees the next attempt received),
    # so an upper bound below the delay proves a retry without backoff.
    checked: list[tuple[int, float, float]] = []
    for history in polls.values():
        first_seen: dict[int, int] = {}
        for n, (_, _, attempts, _) in enumerate(history):
            first_seen.setdefault(attempts, n)
        for attempt in range(1, max(first_seen) if first_seen else 1):
            a, b = first_seen.get(attempt), first_seen.get(attempt + 1)
            if a is None or b is None or a == 0:
                continue
            upper_ms = (history[b][1] - history[a - 1][0]) * 1000
            checked.append((attempt, upper_ms, backoff_ms(policy, attempt)))
    print(
        f"R-03: claim gaps (attempt, upper bound ms, policy delay ms): {[(a, round(u), d) for a, u, d in checked]}"
    )
    assert any(attempt >= 2 for attempt, _, _ in checked), (checked, polls)
    assert all(upper >= delay for _, upper, delay in checked), checked

    # after the partition: everything completed within the policy, retried items included, nothing twice
    items = handler_items(orch, run)
    assert all(i["status"] == "completed" and i["result_status"] == "success" for i in items), items
    store_attempts = [i["attempts"] for i in items if i["stage_id"] in STORE_STAGES]
    assert max(store_attempts) >= 3 and max(store_attempts) <= policy["max_attempts"], store_attempts
    assert_effects_once(storage, source_id, materials=len(urls), products=len(products))


# ---------------------------------------------------------------------------- R-08
R08_UNACKED_LIMIT = 2


class BufferBoundExceeded(AssertionError):
    """The collector held more unacknowledged materials than ``queue.max_unacked_materials``."""


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
    # the last page is not acknowledged: the consumer stops at `end_of_stream` (collector.v1 does not ask for
    # a final `after=`), so it stays unacked in the finished collection - see docs/delivery/WP-13.md
    assert stats["acknowledged"] + stats["unacked"] == len(urls), stats
    assert_effects_once(storage, source_id, materials=len(urls), products=len(products))


@pytest.mark.criteria(8, 13)
@pytest.mark.xfail(
    strict=True,
    raises=BufferBoundExceeded,  # any other failure of the scenario stays a failure
    reason=(
        "WP-02 defect (docs/delivery/WP-13.md, R-01/R-03/R-08 increment): web-collector checks "
        "`unacked < max_unacked_materials` before a fetch without reserving a slot, so up to "
        "concurrency.max_parallel_fetches fetches pass the check together; the paused buffer settles at "
        "max_unacked_materials + max_parallel_fetches - 1 (5 for limit 2 and the default 4)"
    ),
)
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
    if max(unacked) > R08_UNACKED_LIMIT:
        raise BufferBoundExceeded(
            f"unacked {max(unacked)} > max_unacked_materials {R08_UNACKED_LIMIT}: {unacked}"
        )
