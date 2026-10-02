"""Queue engine: workers with leases over the orchestrator's PostgreSQL (``FOR UPDATE SKIP LOCKED``).

Four kinds of work, all claimed with a lease so several workers (threads, processes, instances) never
do the same work twice and a killed worker's work is taken over once its lease expires:

* **feed** — a run's collection: start it in the collector (``Idempotency-Key`` = ``run:<id>:collect``),
  pull material pages with the cursor, create stage items and only then advance the cursor (the next
  pull acknowledges the page). A full queue (``limits.queue``) stops pulling: the collector's buffer
  fills up and it pauses crawling — backpressure. Reprocessing feeds stored RAW from ``storage.v1``.
* **item** — invoke a handler (``handler.v1``) with ``delivery_key`` as ``Idempotency-Key``; record the
  result, create downstream items and mark the item completed **in one transaction** (ADR-0008 §8).
  After a crash the lease expires and the item is retried with the same key: the executor returns its
  stored result (``duplicate: true``) instead of repeating the effect.
* **schedule** — due tasks create runs (row lock per task: exactly one run per tick).
* **sync** — push the connections registry to executors (``PUT/DELETE /v1/connections/{id}``).
"""

from __future__ import annotations

import logging
import random
import threading
import time
from collections.abc import Callable, Mapping
from datetime import timedelta
from typing import Any

from jane_orchestrator.common import delivery_key, new_id, now
from jane_orchestrator.core import Core
from jane_orchestrator.dag import effective_forward_unknown, stage_map
from jane_orchestrator.db import Jsonb
from jane_orchestrator.executors import ExecutorError
from jane_orchestrator.limits import flatten
from jane_orchestrator.routing import NewItem, collect_stage_id, route_material, route_result
from jane_orchestrator.runs import Runs, canonical_key, problem
from jane_orchestrator.schedule import next_fire

__all__ = ["Engine", "Worker"]

log = logging.getLogger(__name__)

TERMINAL_JOB = {"succeeded", "failed", "cancelled"}


def _ms(value: int) -> timedelta:
    return timedelta(milliseconds=value)


def backoff_ms(retries: Mapping[str, Any], attempt: int) -> int:
    """Delay before attempt ``attempt + 1`` (RetryPolicy: initial * multiplier^(attempt-1), capped, jitter)."""
    initial = float(retries.get("initial_backoff_ms", 0))
    mult = float(retries.get("backoff_multiplier", 1))
    cap = float(retries.get("max_backoff_ms", initial))
    base = min(initial * mult ** max(attempt - 1, 0), cap)
    if retries.get("jitter"):
        base += random.uniform(0, base / 2)  # noqa: S311 - jitter, not crypto
    return int(min(base, cap if cap > 0 else base))


class Heartbeat:
    """Extends a lease periodically while a call is in flight; ``lost`` if the lease was taken over."""

    def __init__(self, fn: Callable[[], bool], interval_ms: int) -> None:
        self._fn = fn
        self._interval = interval_ms / 1000
        self._stop = threading.Event()
        self.lost = False
        self._thread = threading.Thread(target=self._run, daemon=True, name="lease-heartbeat")

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            try:
                if not self._fn():
                    self.lost = True
                    return
            except Exception:  # a failed heartbeat is not fatal; the next one retries
                log.warning("lease heartbeat failed", exc_info=True)

    def __enter__(self) -> Heartbeat:
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join()


class Engine:
    """The work-claiming operations; stateless apart from ``core`` (safe to share between threads)."""

    def __init__(self, core: Core) -> None:
        self.core = core
        self.runs = Runs(core)

    @property
    def lease(self) -> timedelta:
        return _ms(self.core.engine.lease_ms)

    # ================================================================== items
    def claim_item(self, worker: str) -> dict[str, Any] | None:
        with self.core.db.tx() as conn:
            row = conn.execute(
                """
                WITH c AS (
                    SELECT i.item_id, i.status AS old_status
                    FROM items i JOIN runs r ON r.run_id = i.run_id
                    WHERE r.status = 'running'
                      AND ((i.status IN ('queued', 'retrying') AND i.available_at <= now())
                           OR (i.status = 'running' AND i.lease_expires_at < now()))
                      AND (SELECT count(*) FROM items x
                           WHERE x.run_id = i.run_id AND x.stage_id = i.stage_id
                             AND x.status = 'running' AND x.lease_expires_at >= now()) < i.parallel_limit
                    ORDER BY i.seq
                    LIMIT 1
                    FOR UPDATE OF i SKIP LOCKED
                )
                UPDATE items SET status = 'running', lease_owner = %s, lease_expires_at = now() + %s,
                                 attempts = CASE WHEN c.old_status = 'running'
                                                   OR (c.old_status = 'retrying' AND
                                                       items.error->>'code' = 'idempotency_in_progress')
                                                 THEN items.attempts
                                                 ELSE items.attempts + 1 END,
                                 lease_reclaims = items.lease_reclaims
                                                  + CASE WHEN c.old_status = 'running' THEN 1 ELSE 0 END,
                                 started_at = coalesce(items.started_at, now()),
                                 updated_at = now()
                FROM c WHERE items.item_id = c.item_id
                RETURNING items.*, c.old_status
                """,
                (worker, self.lease),
            ).fetchone()
        if row is not None and row["old_status"] == "running":
            self.core.metrics.inc("leases_expired")
            log.info("item lease reclaimed", extra={"item_id": row["item_id"], "worker": worker})
        return dict(row) if row else None

    def _extend_item(self, item_id: str, worker: str) -> bool:
        with self.core.db.tx() as conn:
            cur = conn.execute(
                "UPDATE items SET lease_expires_at = now() + %s WHERE item_id = %s AND lease_owner = %s"
                " AND status = 'running'",
                (self.lease, item_id, worker),
            )
            return bool(cur.rowcount)

    def process_item(self, item: dict[str, Any], worker: str) -> str:
        """Invoke the handler for a claimed item and record the outcome. Returns the outcome label."""
        with self.core.db.conn() as conn:
            run = self.runs.get_row(conn, item["run_id"])
        config = run["config"]
        stage = stage_map(config)[item["stage_id"]]
        stage_limits = run["limits"]["stages"][item["stage_id"]]
        flat = flatten(stage_limits)
        retries = stage_limits.get("retries") or {}
        timeout_ms = int(
            flat.get("timeouts.invocation_timeout_ms")
            or self.core.limits.contract.timeouts.invocation_timeout_ms
        )
        if item["lease_reclaims"] > self.core.engine.max_lease_reclaims:
            # a worker kept dying on this item: fail it instead of looping forever (not a retry attempt)
            return self._finish_failed(
                item,
                worker,
                run,
                stage,
                problem(
                    "internal_error",
                    f"lease taken over {item['lease_reclaims']} times (engine.max_lease_reclaims)",
                    500,
                    False,
                ),
            )
        body: dict[str, Any] = {
            "handler": stage["handler"],
            "inputs": item["payload"],
            "delivery": {"delivery_key": item["delivery_key"]},
            "context": {
                "trace": {
                    "trace_id": run["trace_id"],
                    "run_id": run["run_id"],
                    "task_id": run["task_id"],
                    "stage_id": item["stage_id"],
                    "source_id": run["source_id"],
                },
                # The delivery key is stable across retries, so its request body must be stable too.
                # HandlerInvocation.context.attempt is optional; item attempts remain in our own state.
                "test_mode": bool(run["test_mode"]),
            },
            "limits": stage_limits,
            "mode": "sync",
        }
        if run["requested_by"]:
            body["context"]["requested_by"] = run["requested_by"]
        if stage.get("params") is not None:
            body["params"] = stage["params"]
        if stage.get("connections"):
            body["connections"] = stage["connections"]
        executor = self.core.executors.handler_for(stage["handler"]["package_id"])
        if executor is None:
            err = problem(
                "service_unavailable", f"no executor for package {stage['handler']['package_id']}", 503, True
            )
            return self._retry_or_fail(item, worker, run, stage, retries, err, retryable=True)
        result: dict[str, Any] | None = None
        error: ExecutorError | None = None
        with Heartbeat(
            lambda: self._extend_item(item["item_id"], worker), self.core.engine.heartbeat_ms
        ) as hb:
            try:
                result = self._invoke_after_in_progress(executor, body, item, run["trace_id"], timeout_ms, hb)
            except ExecutorError as exc:
                error = exc
        if hb.lost:
            log.warning("item lease lost during invocation", extra={"item_id": item["item_id"]})
            return "lease_lost"
        if error is not None:
            if error.status == 409 and error.code == "idempotency_in_progress":
                return self._park_in_progress(item, worker, error.as_problem())
            return self._retry_or_fail(
                item, worker, run, stage, retries, error.as_problem(), retryable=error.retryable
            )
        assert result is not None
        if result.get("status") == "failed":
            failure = result.get("failure") or {}
            if failure.get("retryable") and item["attempts"] < item["max_attempts"]:
                err = problem(
                    "upstream_unavailable", f"handler failed: {failure.get('message', '')}", 502, True
                )
                err["details"] = {"failure_kind": failure.get("kind")}
                return self._retry_or_fail(
                    item, worker, run, stage, retries, err, retryable=True, result=result
                )
        return self._complete(item, worker, run, stage, result)

    def _invoke_after_in_progress(
        self,
        executor: Any,
        body: dict[str, Any],
        item: Mapping[str, Any],
        trace_id: str,
        timeout_ms: int,
        heartbeat: Heartbeat,
    ) -> dict[str, Any]:
        """Replay a delivery in flight under one lease, without spending ordinary retry attempts."""
        deadline: float | None = None
        while True:
            if heartbeat.lost:
                raise ExecutorError(executor.executor, 409, None, "item lease lost")
            remaining_ms = int((deadline - time.monotonic()) * 1000) if deadline else timeout_ms
            if remaining_ms <= 0:
                break
            try:
                return self._invoke(executor, body, item, trace_id, min(timeout_ms, remaining_ms))
            except ExecutorError as exc:
                in_progress = exc.status == 409 and exc.code == "idempotency_in_progress"
                # Once the executor confirmed this key is active, a later network timeout or
                # retryable 5xx cannot prove the effect did not happen. Keep checking the key.
                if not in_progress and (deadline is None or not exc.retryable):
                    raise
                if deadline is None:
                    deadline = time.monotonic() + self.core.engine.idempotency_in_progress_max_wait_ms / 1000
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                time.sleep(min(self.core.engine.idempotency_in_progress_poll_ms / 1000, remaining))
        raise ExecutorError(
            executor.executor,
            409,
            {
                "type": "urn:jane:problem:idempotency_in_progress",
                "title": "Invocation still in progress",
                "status": 409,
                "code": "idempotency_in_progress",
                "retryable": True,
                "detail": "configured wait window expired; delivery key will be checked again",
            },
            "configured wait window expired; delivery key will be checked again",
        )

    def _invoke(
        self, executor: Any, body: dict[str, Any], item: Mapping[str, Any], trace_id: str, timeout_ms: int
    ) -> dict[str, Any]:
        executors = self.core.executors
        resp = executors.call(
            executor,
            "POST",
            "/v1/invocations",
            json=body,
            idempotency_key=item["delivery_key"],
            trace_id=trace_id,
            timeout_ms=timeout_ms,
        )
        if resp.status_code == 200:
            result: dict[str, Any] = resp.json()
            return result
        job = resp.json()  # 202 + Job: poll the executor until terminal
        job_id = job["job_id"]
        with self.core.db.tx() as conn:
            conn.execute("UPDATE items SET executor_job = %s WHERE item_id = %s", (job_id, item["item_id"]))
        deadline = time.monotonic() + timeout_ms / 1000
        while job.get("status") not in TERMINAL_JOB:
            if time.monotonic() >= deadline:
                raise ExecutorError(
                    executor.executor, 504, None, f"invocation job {job_id} not finished in time"
                )
            time.sleep(self.core.engine.job_poll_interval_ms / 1000)
            job = executors.call(executor, "GET", f"/v1/jobs/{job_id}", trace_id=trace_id).json()
        if job["status"] == "succeeded" and isinstance(job.get("result"), dict):
            final: dict[str, Any] = job["result"]
            return final
        err = job.get("error") or {}
        raise ExecutorError(
            executor.executor, int(err.get("status") or 502), err or None, f"invocation job {job['status']}"
        )

    def _lock_item(self, conn: Any, item: Mapping[str, Any], worker: str) -> dict[str, Any] | None:
        run = conn.execute(
            "SELECT status FROM runs WHERE run_id = %s FOR SHARE", (item["run_id"],)
        ).fetchone()
        row = conn.execute("SELECT * FROM items WHERE item_id = %s FOR UPDATE", (item["item_id"],)).fetchone()
        if row is None or row["status"] != "running" or row["lease_owner"] != worker:
            return None
        out = dict(row)
        out["run_status"] = run["status"] if run else None
        return out

    def _park_in_progress(self, item: Mapping[str, Any], worker: str, err: dict[str, Any]) -> str:
        """Release the worker, retaining the delivery key and attempt until its result can be replayed."""
        delay = self.core.engine.idempotency_in_progress_retry_ms
        with self.core.db.tx() as conn:
            if self._lock_item(conn, item, worker) is None:
                return "lease_lost"
            conn.execute(
                "UPDATE items SET status = 'retrying', lease_owner = NULL, lease_expires_at = NULL,"
                " available_at = now() + %s, error = %s, updated_at = now() WHERE item_id = %s",
                (_ms(delay), Jsonb(err), item["item_id"]),
            )
        self.core.metrics.inc("items", outcome="retrying")
        log.info("in-progress delivery parked", extra={"item_id": item["item_id"], "delay_ms": delay})
        return "retrying"

    def _retry_or_fail(
        self,
        item: Mapping[str, Any],
        worker: str,
        run: Mapping[str, Any],
        stage: Mapping[str, Any],
        retries: Mapping[str, Any],
        err: dict[str, Any],
        *,
        retryable: bool,
        result: dict[str, Any] | None = None,
    ) -> str:
        if retryable and item["attempts"] < item["max_attempts"]:
            delay = backoff_ms(retries, int(item["attempts"]))
            with self.core.db.tx() as conn:
                if self._lock_item(conn, item, worker) is None:
                    return "lease_lost"
                conn.execute(
                    "UPDATE items SET status = 'retrying', lease_owner = NULL, lease_expires_at = NULL,"
                    " available_at = now() + %s, error = %s, updated_at = now() WHERE item_id = %s",
                    (_ms(delay), Jsonb(err), item["item_id"]),
                )
            self.core.metrics.inc("items", outcome="retrying")
            log.info(
                "item retry scheduled",
                extra={"item_id": item["item_id"], "delay_ms": delay, "code": err.get("code")},
            )
            return "retrying"
        if result is not None:
            return self._complete(item, worker, run, stage, result)
        return self._finish_failed(item, worker, run, stage, err)

    def _finish_failed(
        self,
        item: Mapping[str, Any],
        worker: str,
        run: Mapping[str, Any],
        stage: Mapping[str, Any],
        err: dict[str, Any],
    ) -> str:
        with self.core.db.tx() as conn:
            if self._lock_item(conn, item, worker) is None:
                return "lease_lost"
            conn.execute(
                "UPDATE items SET status = 'failed', lease_owner = NULL, lease_expires_at = NULL, payload = NULL,"
                " error = %s, finished_at = now(), updated_at = now() WHERE item_id = %s",
                (Jsonb(err), item["item_id"]),
            )
            run_failed = stage.get("on_failure") == "fail_run" and self.runs.fail_run(
                conn, run["run_id"], {**err, "details": {"stage_id": stage["stage_id"]}}
            )
        self.core.metrics.inc("items", outcome="failed")
        if run_failed:
            self._cancel_collection(run)
        self.runs.maybe_finish(run["run_id"])
        return "failed"

    def _outputs(self, result: Mapping[str, Any]) -> list[dict[str, Any]]:
        cap = self.core.engine.trace_outputs_max
        out: list[dict[str, Any]] = []
        output = result.get("output") or {}
        for e in output.get("entities") or []:
            ref: dict[str, Any] = {"kind": "entity", "entity_type": e.get("entity_type")}
            if (ck := canonical_key(e)) is not None:
                ref["canonical_key"] = ck
            out.append(ref)
        for w in output.get("writes") or []:
            conn_id = (w.get("target") or {}).get("connection_id")
            if w.get("object"):
                ref = {"kind": "stored_object", "object_id": w["object"]["object_id"]}
            elif w.get("entity"):
                ref = {"kind": "entity"}
                for k in ("entity_type", "canonical_key"):
                    if w["entity"].get(k):
                        ref[k] = w["entity"][k]
            else:
                ref = {"kind": "data"}
            if conn_id:
                ref["connection_id"] = conn_id
            out.append(ref)
        if "data" in output or output.get("data_ref"):
            out.append({"kind": "data"})
        return out[:cap]

    def _complete(
        self,
        item: Mapping[str, Any],
        worker: str,
        run: Mapping[str, Any],
        stage: Mapping[str, Any],
        result: dict[str, Any],
    ) -> str:
        status = result.get("status")
        final_failed = status == "failed"
        usage = ((result.get("usage") or {}).get("llm") or {}).get("cost") or {}
        new_items: list[NewItem] = []
        with self.core.db.tx() as conn:
            locked = self._lock_item(conn, item, worker)
            if locked is None:
                return "lease_lost"
            conn.execute(
                "UPDATE items SET status = %s, result_status = %s, invocation_id = %s, handler = %s, outputs = %s,"
                " lease_owner = NULL, lease_expires_at = NULL, payload = NULL, error = %s,"
                " llm_cost = %s, llm_currency = %s, finished_at = now(), updated_at = now() WHERE item_id = %s",
                (
                    "failed" if final_failed else "completed",
                    status,
                    result.get("invocation_id"),
                    Jsonb(result.get("handler") or stage["handler"]),
                    Jsonb(self._outputs(result)),
                    Jsonb(
                        problem(
                            "upstream_conflict", str((result.get("failure") or {}).get("message", "")), 502
                        )
                    )
                    if final_failed
                    else None,
                    usage.get("amount"),
                    usage.get("currency"),
                    item["item_id"],
                ),
            )
            if status in {"unrecognized", "failed"}:
                self._record_problem(conn, run, item, stage, result)
            if locked["run_status"] == "running":
                new_items = route_result(
                    run["config"],
                    run["source_id"],
                    item["stage_id"],
                    item["item_id"],
                    item["payload"],
                    result,
                )
                self._insert_items(conn, run, new_items)
            run_failed = (
                final_failed
                and stage.get("on_failure") == "fail_run"
                and self.runs.fail_run(
                    conn,
                    run["run_id"],
                    problem("upstream_conflict", f"stage '{stage['stage_id']}' failed", 502),
                )
            )
        self.core.metrics.inc("items", outcome=str(status))
        if run_failed:
            self._cancel_collection(run)
        self.runs.maybe_finish(run["run_id"])
        return str(status)

    def _record_problem(
        self,
        conn: Any,
        run: Mapping[str, Any],
        item: Mapping[str, Any],
        stage: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> None:
        status = str(result.get("status"))
        package = dict(result.get("handler") or stage["handler"])
        if status == "unrecognized":
            signature = str((result.get("unrecognized") or {}).get("signature") or "unrecognized")
            failure_kind = None
        else:
            failure_kind = str((result.get("failure") or {}).get("kind") or "execution_error")
            signature = failure_kind
        material = next(
            (i.get("material") for i in item["payload"] or [] if i.get("material")),
            None,
        )
        sample: dict[str, Any] = {}
        if material:
            sample = {
                "material_id": material.get("material_id"),
                "observation_id": material.get("observation_id"),
            }
        if result.get("invocation_id"):
            sample["invocation_id"] = result["invocation_id"]
        samples_cap = self.core.engine.problem_samples
        conn.execute(
            """
            INSERT INTO problem_groups (group_id, source_id, package_id, package_version, package, problem,
                                        failure_kind, signature, count, samples)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s)
            ON CONFLICT (source_id, package_id, package_version, problem, signature) DO UPDATE SET
                count = problem_groups.count + 1,
                last_seen_at = now(),
                status = CASE WHEN problem_groups.status = 'resolved' THEN 'open' ELSE problem_groups.status END,
                samples = CASE WHEN jsonb_array_length(problem_groups.samples) < %s
                               THEN problem_groups.samples || EXCLUDED.samples ELSE problem_groups.samples END
            """,
            (
                new_id("pg"),
                run["source_id"],
                package["package_id"],
                package["version"],
                Jsonb(package),
                status,
                failure_kind,
                signature,
                Jsonb([sample] if sample and samples_cap > 0 else []),
                samples_cap,
            ),
        )

    def _insert_items(self, conn: Any, run: Mapping[str, Any], items: list[NewItem]) -> int:
        created = 0
        stages = stage_map(run["config"])
        for ni in items:
            stage_limits = run["limits"]["stages"][ni.stage_id]
            flat = flatten(stage_limits)
            max_attempts = int(flat.get("retries.max_attempts") or 1)
            parallel = int(flat.get("concurrency.max_parallel_stage_items") or 1)
            mat = ni.material or {}
            loc = mat.get("locator") or {}
            cur = conn.execute(
                """
                INSERT INTO items (item_id, run_id, task_id, stage_id, item_key, status, payload, material_id,
                                   observation_id, source_id, url, upstream_item_id, max_attempts, parallel_limit,
                                   delivery_key, handler)
                VALUES (%s, %s, %s, %s, %s, 'queued', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id, stage_id, item_key) DO NOTHING
                """,
                (
                    new_id("itm"),
                    run["run_id"],
                    run["task_id"],
                    ni.stage_id,
                    ni.item_key,
                    Jsonb(ni.inputs),
                    mat.get("material_id"),
                    mat.get("observation_id"),
                    (mat.get("source") or {}).get("source_id") or run["source_id"],
                    loc.get("canonical_url") or loc.get("url"),
                    ni.upstream_item_id,
                    max_attempts,
                    parallel,
                    delivery_key(run["run_id"], ni.stage_id, ni.item_key),
                    Jsonb(stages[ni.stage_id].get("handler")),
                ),
            )
            created += int(cur.rowcount or 0)
        return created

    # ================================================================== feed
    def claim_feed(self, worker: str) -> dict[str, Any] | None:
        with self.core.db.tx() as conn:
            row = conn.execute(
                """
                UPDATE runs SET feed_lease_owner = %s, feed_lease_expires_at = now() + %s
                WHERE run_id = (
                    SELECT run_id FROM runs
                    WHERE status IN ('queued', 'running', 'cancelling') AND NOT feed_done
                      AND feed_available_at <= now()
                      AND (feed_lease_expires_at IS NULL OR feed_lease_expires_at < now())
                    ORDER BY feed_available_at LIMIT 1
                    FOR UPDATE SKIP LOCKED)
                RETURNING *
                """,
                (worker, self.lease),
            ).fetchone()
        return dict(row) if row else None

    def _release_feed(self, run_id: str, worker: str, delay_ms: int = 0, **updates: Any) -> bool:
        sets = [
            "feed_lease_owner = NULL",
            "feed_lease_expires_at = NULL",
            "feed_available_at = now() + %s",
            "updated_at = now()",
        ]
        params: list[Any] = [_ms(delay_ms)]
        for key, value in updates.items():
            sets.append(f"{key} = %s")
            params.append(Jsonb(value) if isinstance(value, dict) else value)
        with self.core.db.tx() as conn:
            cur = conn.execute(
                f"UPDATE runs SET {', '.join(sets)} WHERE run_id = %s AND feed_lease_owner = %s",  # noqa: S608
                (*params, run_id, worker),
            )
            return bool(cur.rowcount)

    def process_feed(self, run: dict[str, Any], worker: str) -> str:
        eng = self.core.engine
        run_id = run["run_id"]
        if run["status"] == "cancelling":
            self._cancel_collection(run)
            self._release_feed(run_id, worker, feed_done=True)
            self.runs.maybe_finish(run_id)
            return "cancelled"
        task_limits = flatten(run["limits"]["task"])
        if run["status"] == "queued":
            allowed = (
                int(task_limits.get("concurrency.max_parallel_runs_per_task") or 1)
                if run["overlap"] == "allow"
                else 1
            )
            with self.core.db.tx() as conn:
                # serialize queued -> running per task across all workers and instances
                conn.execute(
                    "SELECT pg_advisory_xact_lock(hashtext(%s))", (f"jane-run-start:{run['task_id']}",)
                )
                n = conn.execute(
                    "SELECT count(*) AS n FROM runs WHERE task_id = %s AND run_id <> %s AND status IN ('running', 'cancelling')",
                    (run["task_id"], run_id),
                ).fetchone()
                older = conn.execute(
                    "SELECT 1 FROM runs WHERE task_id = %s AND status = 'queued' AND seq < %s LIMIT 1",
                    (run["task_id"], run["seq"]),
                ).fetchone()
                if int(n["n"]) >= allowed or older is not None:
                    waiting = True
                else:
                    # Lock this row before evaluating the timestamp. An UPDATE blocked on another
                    # row holder can otherwise evaluate clock_timestamp() before the wait.
                    locked = conn.execute(
                        "SELECT status FROM runs WHERE run_id = %s FOR UPDATE", (run_id,)
                    ).fetchone()
                    waiting = locked is None or locked["status"] != "queued"
                    if not waiting:
                        started = conn.execute(
                            "UPDATE runs SET status = 'running', started_at = clock_timestamp(),"
                            " updated_at = clock_timestamp() WHERE run_id = %s AND status = 'queued'"
                            " RETURNING started_at",
                            (run_id,),
                        ).fetchone()
                        assert started is not None
                        run["status"] = "running"
                        run["started_at"] = started["started_at"]
            if waiting:
                self._release_feed(run_id, worker, eng.backpressure_recheck_ms)
                return "waiting"
        run_timeout = task_limits.get("timeouts.run_timeout_ms")
        if run_timeout and run["started_at"] and now() - run["started_at"] > _ms(int(run_timeout)):
            with self.core.db.tx() as conn:
                changed = self.runs.fail_run(
                    conn,
                    run_id,
                    problem("timeout", f"run exceeded timeouts.run_timeout_ms={run_timeout}", 504, True),
                )
            if changed:
                self._cancel_collection(run)
            self._release_feed(run_id, worker, feed_done=True)
            return "timeout"
        capacity = self._capacity(run, task_limits)
        acknowledge_only = (
            capacity <= 0
            and not run["input"].get("stored_materials")
            and bool(run["collection_id"])
            and bool(run["feed_cursor"])
        )
        if capacity <= 0 and not acknowledge_only:
            self.core.metrics.inc("backpressure")
            self._release_feed(run_id, worker, eng.backpressure_recheck_ms, backpressure=True)
            return "backpressure"
        try:
            with Heartbeat(lambda: self._extend_feed(run_id, worker), eng.heartbeat_ms) as hb:
                if run["input"].get("stored_materials"):
                    outcome = self._feed_stored(run, worker, capacity)
                else:
                    outcome = self._feed_collector(run, worker, max(capacity, 1), acknowledge_only)
            if hb.lost:
                return "lease_lost"
            if outcome == "failed":
                self._release_feed(run_id, worker, feed_done=True)
            elif outcome == "backpressure":
                self.core.metrics.inc("backpressure")
                self._release_feed(run_id, worker, eng.backpressure_recheck_ms, backpressure=True)
            elif outcome.startswith("wait:"):
                reason = outcome.split(":", 1)[1]
                delay = int(reason) if reason.isdigit() else eng.backpressure_recheck_ms
                self._release_feed(run_id, worker, delay)
            else:
                self._release_feed(run_id, worker)
        except ExecutorError as exc:
            log.warning("feed call failed", extra={"run_id": run_id, "error": str(exc)})
            retries = run["limits"]["task"].get("retries") or {}
            if not exc.retryable:
                with self.core.db.tx() as conn:
                    self.runs.fail_run(conn, run_id, exc.as_problem())
                self._release_feed(run_id, worker, feed_done=True)
                return "failed"
            self._release_feed(run_id, worker, backoff_ms(retries, 1))
            return "feed_retry"
        self.runs.maybe_finish(run_id)
        return outcome

    def _extend_feed(self, run_id: str, worker: str) -> bool:
        with self.core.db.tx() as conn:
            cur = conn.execute(
                "UPDATE runs SET feed_lease_expires_at = now() + %s WHERE run_id = %s AND feed_lease_owner = %s",
                (self.lease, run_id, worker),
            )
            return bool(cur.rowcount)

    def _capacity(self, run: Mapping[str, Any], task_limits: Mapping[str, Any]) -> int:
        max_depth = int(task_limits.get("queue.max_queue_depth") or 1)
        max_inflight = int(task_limits.get("queue.max_inflight_materials") or 1)
        with self.core.db.conn() as conn:
            depth = conn.execute(
                "SELECT count(*) AS n FROM items WHERE task_id = %s AND status IN ('queued', 'retrying', 'leased', 'running')",
                (run["task_id"],),
            ).fetchone()
            inflight = conn.execute(
                "SELECT count(DISTINCT observation_id) AS n FROM items WHERE run_id = %s"
                " AND status IN ('queued', 'retrying', 'leased', 'running')",
                (run["run_id"],),
            ).fetchone()
        return min(
            max_depth - int(depth["n"]), max_inflight - int(inflight["n"]), self.core.engine.feed_page_size
        )

    def _collection_request(self, run: Mapping[str, Any]) -> dict[str, Any]:
        config, source = run["config"], run["source_doc"]
        collect = next(s for s in config["stages"] if s["kind"] == "collect")
        body: dict[str, Any] = {
            "source_kind": source["kind"],
            "source_id": source["source_id"],
            "mode": collect["collector"].get("mode", "full"),
            "limits": run["limits"]["stages"][collect["stage_id"]],
            "trace": {
                "trace_id": run["trace_id"],
                "run_id": run["run_id"],
                "task_id": run["task_id"],
                "stage_id": collect["stage_id"],
                "source_id": source["source_id"],
            },
        }
        rules = collect["collector"].get("rules") or source.get("collector_rules")
        if rules:
            body["rules_ref"] = rules
        if run["input"].get("urls"):
            body["urls"] = run["input"]["urls"]
        return body

    def _feed_collector(
        self, run: dict[str, Any], worker: str, capacity: int, acknowledge_only: bool = False
    ) -> str:
        eng = self.core.engine
        config = run["config"]
        collect = next(s for s in config["stages"] if s["kind"] == "collect")
        name = collect["collector"]["collector"]
        executor = self.core.executors.collector(name)
        if executor is None:
            raise ExecutorError("collector:" + name, 503, None, f"no collector executor for '{name}'")
        if not run["collection_id"]:
            if self._connections_pending(run, executor.executor):
                return "wait:connections"  # e.g. telegram_account not yet pushed to this collector
            body = self._collection_request(run)
            restarts = int(run.get("collection_restarts") or 0)
            if restarts:
                body["mode"] = "incremental"  # continue from the collector's saved cursor/state
            if "rules_ref" not in body:
                with self.core.db.tx() as conn:
                    self.runs.fail_run(
                        conn,
                        run["run_id"],
                        problem(
                            "validation_failed",
                            "no collector rules: set stages[collect].collector.rules or source.collector_rules",
                            422,
                        ),
                    )
                return "failed"
            job = self.core.executors.call(
                executor,
                "POST",
                "/v1/collections",
                json=body,
                idempotency_key=f"run:{run['run_id']}:collect" + (f":{restarts}" if restarts else ""),
                trace_id=run["trace_id"],
            ).json()
            run["collection_id"] = job["job_id"]
            with self.core.db.tx() as conn:
                conn.execute(
                    "UPDATE runs SET collection_id = %s WHERE run_id = %s AND feed_lease_owner = %s",
                    (run["collection_id"], run["run_id"], worker),
                )
        params: dict[str, Any] = {"limit": capacity, "wait_ms": 0 if acknowledge_only else eng.feed_wait_ms}
        if run["feed_cursor"]:
            params["after"] = run["feed_cursor"]
        page = self.core.executors.call(
            executor,
            "GET",
            f"/v1/collections/{run['collection_id']}/materials",
            params=params,
            trace_id=run["trace_id"],
            timeout_ms=self.core.limits.contract.timeouts.request_timeout_ms + eng.feed_wait_ms,
        ).json()
        materials = page.get("items") or []
        if acknowledge_only and materials:
            # `after` has acknowledged the durable previous page. Leave any new materials
            # unacknowledged until queue capacity returns; the collector will redeliver them.
            return "backpressure"
        feed_error = None
        if page.get("end_of_stream") and page.get("collection_status") == "failed":
            job = self.core.executors.call(
                executor, "GET", f"/v1/jobs/{run['collection_id']}", trace_id=run["trace_id"]
            ).json()
            feed_error = job.get("error") or problem("source_unavailable", "collection failed", 502, True)
            delay_ms = self._rate_limit_restart(run, feed_error)
            if delay_ms is not None:
                if materials:
                    # Keep this collection and its durable cursor until a later GET with `after`
                    # confirms the last page. A crash before that GET must not orphan its buffer.
                    created = self._accept_materials(
                        run, worker, materials, page.get("next_cursor"), False, None
                    )
                    return f"fed:{created}"
                # Empty terminal response after `after` confirms every accepted page. Retrying
                # the same GET after a crash is safe, then the next collection may start.
                with self.core.db.tx() as conn:
                    conn.execute(
                        "UPDATE runs SET collection_id = NULL, feed_cursor = NULL,"
                        " collection_restarts = collection_restarts + 1 WHERE run_id = %s AND feed_lease_owner = %s",
                        (run["run_id"], worker),
                    )
                log.info(
                    "rate-limited collection restarts later",
                    extra={"run_id": run["run_id"], "delay_ms": delay_ms},
                )
                return f"wait:{delay_ms}"
        # The collector acknowledges `next_cursor` only when a subsequent request sends it as
        # `after`. Keep the feed claimable after a nonempty terminal page so a crash cannot leave
        # its final materials permanently unacknowledged.
        end = bool(page.get("end_of_stream")) and not materials
        created = self._accept_materials(run, worker, materials, page.get("next_cursor"), end, feed_error)
        return f"fed:{created}"

    def _rate_limit_restart(self, run: Mapping[str, Any], error: Mapping[str, Any]) -> int | None:
        """Delay before restarting a collection that ended with ``rate_limited`` (retryable), or ``None``.

        Waits at least ``retry_after_seconds`` of the collector's Problem (otherwise the collect stage backoff);
        restarts are bounded by the collect stage ``retries.max_attempts``."""
        if error.get("code") != "rate_limited" or error.get("retryable") is False:
            return None
        collect_id = collect_stage_id(run["config"])
        retries = run["limits"]["stages"][collect_id].get("retries") or {}
        restarts = int(run.get("collection_restarts") or 0)
        if restarts + 1 >= int(retries.get("max_attempts") or 1):
            return None
        after = error.get("retry_after_seconds")
        backoff = backoff_ms(retries, restarts + 1)
        return max(int(after) * 1000, backoff) if isinstance(after, int | float) else backoff

    def _connections_pending(self, run: Mapping[str, Any], executor: str) -> bool:
        """True while a connection the collection needs is still being pushed to this collector."""
        collect = next(s for s in run["config"]["stages"] if s["kind"] == "collect")
        ids = {
            *(run["source_doc"].get("connections") or {}).values(),
            *(collect.get("connections") or {}).values(),
        }
        if not ids:
            return False
        with self.core.db.conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM connection_sync WHERE executor = %s AND connection_id = ANY(%s)"
                " AND op = 'put' AND status = 'pending' LIMIT 1",
                (executor, list(ids)),
            ).fetchone()
        return row is not None

    def _accept_materials(
        self,
        run: Mapping[str, Any],
        worker: str,
        materials: list[dict[str, Any]],
        next_cursor: str | None,
        end: bool,
        feed_error: dict[str, Any] | None,
        from_stage: str | None = None,
    ) -> int:
        """Record materials as collect items + route them, then advance the cursor — one transaction."""
        config = run["config"]
        collect_id = collect_stage_id(config)
        forward = effective_forward_unknown(config, run["source_doc"])
        created = 0
        with self.core.db.tx() as conn:
            owner = conn.execute(
                "SELECT feed_lease_owner, status FROM runs WHERE run_id = %s FOR UPDATE", (run["run_id"],)
            ).fetchone()
            if owner is None or owner["feed_lease_owner"] != worker:
                return 0
            accept = owner["status"] == "running"
            for m in materials if accept else []:
                loc = m.get("locator") or {}
                cur = conn.execute(
                    """
                    INSERT INTO items (item_id, run_id, task_id, stage_id, item_key, status, material_id,
                                       observation_id, source_id, url, fetched_at, content_sha256, attempts,
                                       finished_at)
                    VALUES (%s, %s, %s, %s, %s, 'completed', %s, %s, %s, %s, %s, %s, 0, now())
                    ON CONFLICT (run_id, stage_id, item_key) DO NOTHING
                    """,
                    (
                        new_id("itm"),
                        run["run_id"],
                        run["task_id"],
                        collect_id,
                        str(m["observation_id"]),
                        m.get("material_id"),
                        m.get("observation_id"),
                        (m.get("source") or {}).get("source_id") or run["source_id"],
                        loc.get("canonical_url") or loc.get("url"),
                        m.get("fetched_at"),
                        (m.get("revision") or {}).get("content_sha256"),
                    ),
                )
                if not cur.rowcount:
                    continue  # re-delivered observation: already routed
                if (m.get("source") or {}).get("source_id") is None:
                    m = {**m, "source": {**(m.get("source") or {}), "source_id": run["source_id"]}}
                routing = route_material(config, run["source_id"], m, forward, from_stage)
                created += self._insert_items(conn, run, routing.items)
                if routing.unknown.unknown:
                    conn.execute(
                        "INSERT INTO unknown_materials (material_id, observation_id, source_id, run_id, url,"
                        " forwarded_to_llm, reason) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        " ON CONFLICT (run_id, observation_id) DO NOTHING",
                        (
                            m.get("material_id"),
                            m.get("observation_id"),
                            run["source_id"],
                            run["run_id"],
                            loc.get("canonical_url") or loc.get("url"),
                            routing.unknown.forwarded,
                            routing.unknown.reason,
                        ),
                    )
            self.core.metrics.inc("materials", len(materials))
            conn.execute(
                "UPDATE runs SET feed_cursor = coalesce(%s, feed_cursor), feed_done = %s, feed_error = %s,"
                " backpressure = false, updated_at = now() WHERE run_id = %s",
                (
                    next_cursor if accept else None,
                    end and accept,
                    Jsonb(feed_error) if feed_error else None,
                    run["run_id"],
                ),
            )
        return created

    def _feed_stored(self, run: dict[str, Any], worker: str, capacity: int) -> str:
        stored = run["input"]["stored_materials"]
        executor = self.core.executors.first("storage_read")
        if executor is None:
            raise ExecutorError("storage_read", 503, None, "no storage_read executor configured")
        conn_id = stored.get("storage_connection_id")
        if not conn_id:
            with self.core.db.tx() as conn:
                self.runs.fail_run(
                    conn,
                    run["run_id"],
                    problem("validation_failed", "stored_materials.storage_connection_id is required", 422),
                )
            return "failed"
        params: dict[str, Any] = {"connection_id": conn_id, "limit": capacity}
        if run["feed_cursor"]:
            params["cursor"] = run["feed_cursor"]
        for key in ("since", "until"):
            if stored.get(key):
                params[key] = stored[key]
        wanted = set(stored.get("material_ids") or [])
        page = self.core.executors.call(
            executor, "GET", "/v1/objects", params=params, trace_id=run["trace_id"]
        ).json()
        materials = []
        for obj in page.get("items") or []:
            mat_meta = obj.get("material") or {}
            if wanted and mat_meta.get("material_id") not in wanted:
                continue
            object_id = obj["object"]["object_id"]
            detail = self.core.executors.call(
                executor,
                "GET",
                f"/v1/objects/{object_id}",
                params={"connection_id": conn_id},
                trace_id=run["trace_id"],
            ).json()
            if isinstance(detail.get("material"), dict):
                materials.append(detail["material"])
        nxt = page.get("next_cursor")
        created = self._accept_materials(
            run, worker, materials, nxt, nxt is None, None, run["input"].get("from_stage")
        )
        return f"fed:{created}"

    def _cancel_collection(self, run: Mapping[str, Any]) -> None:
        if not run.get("collection_id") or run.get("collector_cancelled"):
            return
        collect = next(s for s in run["config"]["stages"] if s["kind"] == "collect")
        executor = self.core.executors.collector(collect["collector"]["collector"])
        if executor is None:
            return
        try:
            self.core.executors.call(
                executor,
                "POST",
                f"/v1/jobs/{run['collection_id']}/cancel",
                json={"reason": "run cancelled or failed in orchestrator"},
                trace_id=run["trace_id"],
            )
        except ExecutorError as exc:
            log.warning("collection cancel failed", extra={"run_id": run["run_id"], "error": str(exc)})
            return
        with self.core.db.tx() as conn:
            conn.execute("UPDATE runs SET collector_cancelled = true WHERE run_id = %s", (run["run_id"],))

    # ================================================================== schedules
    def schedule_due(self) -> int:
        """Create runs for due tasks (row lock per task: one run per tick across all instances)."""
        created = 0
        with self.core.db.tx() as conn:
            rows = conn.execute(
                "SELECT t.*, s.doc AS source_doc FROM tasks t JOIN sources s ON s.source_id = t.source_id"
                " WHERE t.next_run_at <= now() ORDER BY t.next_run_at LIMIT %s FOR UPDATE OF t SKIP LOCKED",
                (self.core.engine.schedule_batch,),
            ).fetchall()
            for row in rows:
                doc = row["doc"]
                fired_at = row["next_run_at"]
                if doc.get("enabled", True):
                    run = self.runs.create(
                        conn,
                        row,
                        row["source_doc"],
                        trigger="schedule",
                        reason=f"schedule tick {fired_at.isoformat()}",
                        requested_by="scheduler",
                    )
                    created += int(run is not None)
                nxt = next_fire(doc.get("schedule"), now(), fired_at) if doc.get("enabled", True) else None
                conn.execute(
                    "UPDATE tasks SET next_run_at = %s, last_scheduled_at = %s WHERE task_id = %s",
                    (nxt, fired_at, row["task_id"]),
                )
        return created

    # ================================================================== housekeeping
    def reap(self) -> int:
        """Close runs nobody else will close: a cancelling or drained run whose last worker died (the item
        and feed paths never see it again), and runs over ``timeouts.run_timeout_ms`` in any phase.

        Only runs that need action are selected, so busy runs never crowd out the ones to close (a batch of
        ``reap_batch`` always makes progress). Several reapers may pick the same run: state changes are
        conditional and only the reaper that changed the state counts it and calls the collector."""
        eng = self.core.engine
        with self.core.db.conn() as conn:
            timed_out = conn.execute(
                """
                SELECT * FROM runs
                WHERE status IN ('running', 'cancelling') AND started_at IS NOT NULL
                  AND jsonb_typeof(limits->'task'->'timeouts'->'run_timeout_ms') = 'number'
                  AND started_at + ((limits->'task'->'timeouts'->>'run_timeout_ms')::bigint
                                    * interval '1 millisecond') < now()
                ORDER BY started_at LIMIT %s
                """,
                (eng.reap_batch,),
            ).fetchall()
            # candidates that maybe_finish will close: a drained running run with no active item, or a
            # cancelling run whose remaining items are not held by a live lease
            drained = conn.execute(
                """
                SELECT r.run_id FROM runs r
                WHERE r.feed_done AND (
                    (r.status = 'running' AND NOT EXISTS (
                        SELECT 1 FROM items i WHERE i.run_id = r.run_id
                          AND i.status IN ('queued', 'retrying', 'leased', 'running')))
                    OR (r.status = 'cancelling' AND NOT EXISTS (
                        SELECT 1 FROM items i WHERE i.run_id = r.run_id
                          AND i.status IN ('leased', 'running') AND i.lease_expires_at >= now())))
                ORDER BY r.seq LIMIT %s
                """,
                (eng.reap_batch,),
            ).fetchall()
        closed = 0
        for run in timed_out:
            if run["status"] == "cancelling":
                with self.core.db.tx() as conn:
                    conn.execute(
                        "UPDATE runs SET feed_done = true WHERE run_id = %s AND status = 'cancelling'",
                        (run["run_id"],),
                    )
                    # items still leased by dead or stuck workers are cancelled regardless of the lease
                    conn.execute(
                        "UPDATE items SET status = 'cancelled', payload = NULL, lease_owner = NULL,"
                        " finished_at = now(), updated_at = now() WHERE run_id = %s"
                        " AND status IN ('queued', 'retrying', 'leased', 'running')",
                        (run["run_id"],),
                    )
                closed += int(self.runs.maybe_finish(run["run_id"]) is not None)
                continue
            limit = run["limits"]["task"]["timeouts"]["run_timeout_ms"]
            with self.core.db.tx() as conn:
                changed = self.runs.fail_run(
                    conn,
                    run["run_id"],
                    problem("timeout", f"run exceeded timeouts.run_timeout_ms={limit}", 504, True),
                )
                if changed:
                    conn.execute(
                        "UPDATE items SET status = 'cancelled', payload = NULL, lease_owner = NULL,"
                        " finished_at = now(), updated_at = now() WHERE run_id = %s"
                        " AND status IN ('leased', 'running')",
                        (run["run_id"],),
                    )
            if changed:
                self._cancel_collection(run)
                closed += 1
        for row in drained:
            closed += int(self.runs.maybe_finish(row["run_id"]) is not None)
        return closed

    # ================================================================== LLM budget sync
    def sync_budgets(self, worker: str) -> int:
        """Push ``limits.llm.budget`` / ``max_requests_per_minute`` of sources and tasks to the LLM gateway
        (``llm.v1 PUT/DELETE /v1/budgets/{scope_type}/{scope_id}``), idempotently, with retries."""
        eng = self.core.engine
        llm = self.core.executors.first("llm")
        done = 0
        while True:
            with self.core.db.tx() as conn:
                row = conn.execute(
                    """
                    UPDATE budget_sync SET lease_owner = %s, lease_expires_at = now() + %s, attempts = attempts + 1
                    WHERE (scope_type, scope_id) = (
                        SELECT scope_type, scope_id FROM budget_sync
                        WHERE status = 'pending' AND available_at <= now()
                          AND (lease_expires_at IS NULL OR lease_expires_at < now())
                        LIMIT 1 FOR UPDATE SKIP LOCKED)
                    RETURNING *
                    """,
                    (worker, self.lease),
                ).fetchone()
            if row is None:
                return done
            status, message = "synced", None
            path = f"/v1/budgets/{row['scope_type']}/{row['scope_id']}"
            if llm is None:
                status, message = "failed", "no llm executor configured"
            else:
                try:
                    if row["op"] == "delete":
                        self.core.executors.call(llm, "DELETE", path, ok=(404,))
                    else:
                        self.core.executors.call(llm, "PUT", path, json=row["doc"])
                except ExecutorError as exc:
                    message = str(exc)
                    status = (
                        "pending" if exc.retryable and row["attempts"] < eng.sync_max_attempts else "failed"
                    )
            with self.core.db.tx() as conn:
                if row["op"] == "delete" and status == "synced":
                    conn.execute(
                        "DELETE FROM budget_sync WHERE scope_type = %s AND scope_id = %s AND lease_owner = %s",
                        (row["scope_type"], row["scope_id"], worker),
                    )
                else:
                    conn.execute(
                        "UPDATE budget_sync SET status = %s, message = %s, lease_owner = NULL, lease_expires_at = NULL,"
                        " synced_at = CASE WHEN %s = 'synced' THEN now() ELSE synced_at END,"
                        " available_at = now() + %s WHERE scope_type = %s AND scope_id = %s AND lease_owner = %s",
                        (
                            status,
                            message,
                            status,
                            _ms(eng.sync_retry_ms),
                            row["scope_type"],
                            row["scope_id"],
                            worker,
                        ),
                    )
            done += 1

    # ================================================================== connection sync
    def sync_connections(self, worker: str) -> int:
        done = 0
        eng = self.core.engine
        while True:
            with self.core.db.tx() as conn:
                row = conn.execute(
                    """
                    UPDATE connection_sync SET lease_owner = %s, lease_expires_at = now() + %s, attempts = attempts + 1
                    WHERE (connection_id, executor) = (
                        SELECT connection_id, executor FROM connection_sync
                        WHERE status = 'pending' AND available_at <= now()
                          AND (lease_expires_at IS NULL OR lease_expires_at < now())
                        LIMIT 1 FOR UPDATE SKIP LOCKED)
                    RETURNING *
                    """,
                    (worker, self.lease),
                ).fetchone()
                doc_row = (
                    conn.execute(
                        "SELECT doc FROM connections WHERE connection_id = %s", (row["connection_id"],)
                    ).fetchone()
                    if row
                    else None
                )
            if row is None:
                return done
            cfg = self.core.executors.configs.get(row["executor"])
            status, message = "synced", None
            if cfg is None:
                status, message = "failed", "executor is no longer configured"
            else:
                try:
                    if row["op"] == "delete":
                        self.core.executors.call(
                            cfg, "DELETE", f"/v1/connections/{row['connection_id']}", ok=(404,)
                        )
                    elif doc_row is not None:
                        self.core.executors.call(
                            cfg, "PUT", f"/v1/connections/{row['connection_id']}", json=doc_row["doc"]
                        )
                except ExecutorError as exc:
                    message = str(exc)
                    if exc.status == 501:
                        status, message = (
                            "failed",
                            "executor does not use managed connections (not_implemented)",
                        )
                    elif exc.retryable and row["attempts"] < eng.sync_max_attempts:
                        status = "pending"
                    else:
                        status = "failed"
            with self.core.db.tx() as conn:
                if row["op"] == "delete" and status == "synced":
                    conn.execute(
                        "DELETE FROM connection_sync WHERE connection_id = %s AND executor = %s AND lease_owner = %s",
                        (row["connection_id"], row["executor"], worker),
                    )
                else:
                    conn.execute(
                        "UPDATE connection_sync SET status = %s, message = %s, lease_owner = NULL, lease_expires_at = NULL,"
                        " synced_at = CASE WHEN %s = 'synced' THEN now() ELSE synced_at END,"
                        " available_at = now() + %s WHERE connection_id = %s AND executor = %s AND lease_owner = %s",
                        (
                            status,
                            message,
                            status,
                            _ms(eng.sync_retry_ms),
                            row["connection_id"],
                            row["executor"],
                            worker,
                        ),
                    )
            done += 1


class Worker:
    """A thread that repeatedly claims and processes work (feeds first, then items, schedules, syncs)."""

    def __init__(self, engine: Engine, name: str, *, scheduler: bool = True) -> None:
        self.engine = engine
        self.name = name
        self.scheduler = scheduler
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True, name=f"worker-{name}")
        self._last_schedule = 0.0

    def start(self) -> None:
        self._thread.start()

    def stop(self, timeout: float | None = None) -> None:
        self._stop.set()
        self._thread.join(timeout)

    def step(self) -> bool:
        """One unit of work; ``False`` when there was nothing to do."""
        eng = self.engine
        did = False
        feed = eng.claim_feed(self.name)
        if feed is not None:
            eng.process_feed(feed, self.name)
            did = True
        item = eng.claim_item(self.name)
        if item is not None:
            eng.process_item(item, self.name)
            did = True
        interval = eng.core.engine.scheduler_interval_ms / 1000
        if time.monotonic() - self._last_schedule >= interval:
            self._last_schedule = time.monotonic()
            if self.scheduler:
                did = eng.schedule_due() > 0 or did
            did = eng.sync_connections(self.name) > 0 or did
            did = eng.sync_budgets(self.name) > 0 or did
            did = eng.reap() > 0 or did
        return did

    def _loop(self) -> None:
        poll = self.engine.core.engine.poll_interval_ms / 1000
        while not self._stop.is_set():
            try:
                if not self.step():
                    self._stop.wait(poll)
            except Exception:
                log.exception("worker step failed", extra={"worker": self.name})
                self._stop.wait(poll)
