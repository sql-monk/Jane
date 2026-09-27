"""Runs: creation (with a snapshot of the task, source and effective limits), state, cancellation, items,
the material trace and the ``Job`` view (run_id = job_id, ``kind: run``)."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from jane_kit.errors import Conflict, FieldError, JaneError, LimitExceeded, NotFound, ValidationFailed
from jane_kit.pagination import decode_cursor, encode_cursor
from jane_kit.tracing import new_trace_id
from jane_orchestrator.common import etag, new_id, now, rfc3339
from jane_orchestrator.core import Core
from jane_orchestrator.dag import stage_map
from jane_orchestrator.db import Jsonb

__all__ = ["ACTIVE_ITEM", "TERMINAL_RUN", "Runs"]

log = logging.getLogger(__name__)

TERMINAL_RUN = ("succeeded", "failed", "cancelled")
ACTIVE_RUN = ("queued", "running", "cancelling")
ACTIVE_ITEM = ("queued", "retrying", "leased", "running")


def _collect_stage(config: Mapping[str, Any]) -> dict[str, Any]:
    return next(dict(s) for s in config["stages"] if s["kind"] == "collect")


def canonical_key(entity: Mapping[str, Any]) -> str | None:
    """Canonical key string of an entity (entity.schema.json ``EntityKey``: scope + '|' + sorted JSON)."""
    key = entity.get("key") or {}
    if "scope" not in key or "natural" not in key:
        return None
    return f"{key['scope']}|{json.dumps(key['natural'], sort_keys=True, separators=(',', ':'), ensure_ascii=False)}"


class Runs:
    def __init__(self, core: Core) -> None:
        self.core = core

    # ------------------------------------------------------------------ creation
    def create(
        self,
        conn: Any,
        task_row: Mapping[str, Any],
        source_doc: Mapping[str, Any],
        *,
        trigger: str,
        test_mode: bool = False,
        reason: str | None = None,
        input_override: Mapping[str, Any] | None = None,
        request_limits: Mapping[str, Any] | None = None,
        requested_by: str | None = None,
        idempotency_key: str | None = None,
        from_stage: str | None = None,
        enforce_overlap: bool = True,
    ) -> dict[str, Any] | None:
        """Insert a queued run. Returns the run row, or ``None`` when a scheduled run is skipped
        (``overlap: skip`` with an active run). A manual start in that case is ``409 conflict``."""
        config = dict(task_row["doc"])
        task_id = config["task_id"]
        schedule = config.get("schedule") or {}
        overlap = schedule.get("overlap", "skip")
        if enforce_overlap and overlap == "skip":
            active = conn.execute(
                "SELECT 1 FROM runs WHERE task_id = %s AND status IN ('queued', 'running', 'cancelling') LIMIT 1",
                (task_id,),
            ).fetchone()
            if active:
                if trigger == "schedule":
                    return None
                raise Conflict("A run of this task is already in progress", title="Conflict")
        platform, _ = self.core.platform_limits(conn)
        stages = stage_map(config)
        if from_stage is not None and (from_stage not in stages or stages[from_stage]["kind"] != "handler"):
            raise ValidationFailed(
                f"from_stage '{from_stage}' is not a handler stage of task '{task_id}'",
                errors=[FieldError(pointer="/from_stage", message="unknown handler stage")],
            )
        stage_limits = {
            sid: self.core.effective(platform, dict(source_doc), config, s, dict(request_limits or {})).limits
            for sid, s in stages.items()
        }
        task_eff = self.core.effective(platform, dict(source_doc), config, None, dict(request_limits or {}))
        task_input = dict(config.get("input") or {})
        override = dict(input_override or {})
        run_input: dict[str, Any] = {}
        urls = override.get("urls", task_input.get("urls"))
        stored = override.get("stored_materials", task_input.get("stored_materials"))
        if stored:
            run_input["stored_materials"] = stored
        elif urls:
            collect_eff = self.core.effective(
                platform, dict(source_doc), config, _collect_stage(config), dict(request_limits or {})
            )
            max_seed = collect_eff.get("crawl.max_seed_urls")
            if isinstance(max_seed, int) and len(urls) > max_seed:
                raise LimitExceeded(
                    f"{len(urls)} URLs exceed limits.crawl.max_seed_urls={max_seed}",
                    details={"limit": "crawl.max_seed_urls", "value": max_seed},
                )
            run_input["urls"] = list(urls)
        if from_stage:
            run_input["from_stage"] = from_stage
        run_id = new_id("run")
        row = conn.execute(
            """
            INSERT INTO runs (run_id, task_id, source_id, task_etag, config, source_doc, limits, input, status,
                              trigger, test_mode, reason, requested_by, idempotency_key, trace_id, overlap)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'queued', %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                run_id,
                task_id,
                source_doc["source_id"],
                etag(int(task_row["version"])),
                Jsonb(config),
                Jsonb(dict(source_doc)),
                Jsonb({"task": task_eff.limits, "stages": stage_limits}),
                Jsonb(run_input),
                trigger,
                test_mode,
                reason,
                requested_by,
                idempotency_key,
                new_trace_id(),
                overlap,
            ),
        ).fetchone()
        log.info("run created", extra={"run_id": run_id, "task_id": task_id, "trigger": trigger})
        return dict(row) if row else None

    # ------------------------------------------------------------------ views
    def get_row(self, conn: Any, run_id: str) -> dict[str, Any]:
        row = conn.execute("SELECT * FROM runs WHERE run_id = %s", (run_id,)).fetchone()
        if row is None:
            raise NotFound(f"run '{run_id}' not found")
        return dict(row)

    @staticmethod
    def _counts(conn: Any, run_id: str) -> dict[str, dict[str, int]]:
        rows = conn.execute(
            "SELECT stage_id, status, result_status, count(*) AS n FROM items WHERE run_id = %s"
            " GROUP BY stage_id, status, result_status",
            (run_id,),
        ).fetchall()
        out: dict[str, dict[str, int]] = {}
        for r in rows:
            counts = out.setdefault(r["stage_id"], {})
            counts[r["status"]] = counts.get(r["status"], 0) + int(r["n"])
            if r["result_status"]:
                counts[r["result_status"]] = counts.get(r["result_status"], 0) + int(r["n"])
        return out

    def run_view(self, conn: Any, row: Mapping[str, Any]) -> dict[str, Any]:
        run_id = row["run_id"]
        counts = self._counts(conn, run_id)
        stages = []
        for s in row["config"]["stages"]:
            progress: dict[str, Any] = {"stage_id": s["stage_id"], "counts": counts.get(s["stage_id"], {})}
            if s["kind"] == "handler":
                progress["handler"] = s["handler"]
            stages.append(progress)
        collect_id = _collect_stage(row["config"])["stage_id"]
        unknown = conn.execute(
            "SELECT count(*) AS n FROM unknown_materials WHERE run_id = %s", (run_id,)
        ).fetchone()
        cost = conn.execute(
            "SELECT llm_currency AS c, sum(llm_cost) AS s FROM items WHERE run_id = %s AND llm_cost IS NOT NULL"
            " GROUP BY llm_currency ORDER BY sum(llm_cost) DESC LIMIT 1",
            (run_id,),
        ).fetchone()
        view: dict[str, Any] = {
            "run_id": run_id,
            "task_id": row["task_id"],
            "task_etag": row["task_etag"],
            "status": row["status"],
            "trigger": row["trigger"],
            "test_mode": row["test_mode"],
            "created_at": rfc3339(row["created_at"]),
            "stages": stages,
            "counters": {
                "materials": counts.get(collect_id, {}).get("completed", 0),
                "unknown_materials": int(unknown["n"]) if unknown else 0,
            },
            "backpressure": row["backpressure"],
        }
        for key in ("started_at", "finished_at"):
            if row[key] is not None:
                view[key] = rfc3339(row[key])
        if row["collection_id"]:
            view["collection_id"] = row["collection_id"]
        if cost is not None and cost["c"]:
            view["costs"] = {"llm": {"amount": float(cost["s"]), "currency": cost["c"]}}
        if row["error"]:
            view["error"] = row["error"]
        return view

    def job_view(self, conn: Any, row: Mapping[str, Any]) -> dict[str, Any]:
        run_id = row["run_id"]
        counts = self._counts(conn, run_id)
        collect_id = _collect_stage(row["config"])["stage_id"]
        done = sum(
            n
            for sid, c in counts.items()
            if sid != collect_id
            for st, n in c.items()
            if st in {"completed", "failed", "skipped", "cancelled"}
        )
        active = sum(n for c in counts.values() for st, n in c.items() if st in ACTIVE_ITEM)
        job: dict[str, Any] = {
            "job_id": run_id,
            "kind": "run",
            "status": row["status"],
            "created_at": rfc3339(row["created_at"]),
            "updated_at": rfc3339(row["updated_at"]),
            "progress": {
                "completed": done,
                "total": None if not row["feed_done"] else done + active,
                "unit": "items",
                "counters": {"materials": counts.get(collect_id, {}).get("completed", 0)},
            },
            "links": {
                "self": f"/v1/jobs/{run_id}",
                "cancel": f"/v1/jobs/{run_id}/cancel",
                "run": f"/v1/runs/{run_id}",
            },
        }
        for key in ("started_at", "finished_at"):
            if row[key] is not None:
                job[key] = rfc3339(row[key])
        if row["error"] and row["status"] == "failed":
            job["error"] = row["error"]
        if row["cancel_requested_at"] is not None:
            cancellation: dict[str, Any] = {"requested_at": rfc3339(row["cancel_requested_at"])}
            if row["cancel_requested_by"]:
                cancellation["requested_by"] = row["cancel_requested_by"]
            if row["cancel_reason"]:
                cancellation["reason"] = row["cancel_reason"]
            job["cancellation"] = cancellation
        if row["idempotency_key"]:
            job["idempotency_key"] = row["idempotency_key"]
        return job

    def list_runs(
        self,
        conn: Any,
        *,
        task_id: str | None,
        status: str | None,
        since: datetime | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict[str, Any]], str | None]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if task_id:
            where.append("task_id = %s")
            params.append(task_id)
        if status:
            where.append("status = %s")
            params.append(status)
        if since:
            where.append("created_at >= %s")
            params.append(since)
        if cursor:
            where.append("seq < %s")
            params.append(int(decode_cursor(cursor)))
        rows = conn.execute(
            f"SELECT * FROM runs WHERE {' AND '.join(where)} ORDER BY seq DESC LIMIT %s",  # noqa: S608 - fixed fragments
            (*params, limit + 1),
        ).fetchall()
        items = [self.run_view(conn, r) for r in rows[:limit]]
        nxt = encode_cursor(int(rows[limit - 1]["seq"])) if len(rows) > limit else None
        return items, nxt

    # ------------------------------------------------------------------ items & trace
    @staticmethod
    def item_view(r: Mapping[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {
            "item_id": r["item_id"],
            "stage_id": r["stage_id"],
            "status": r["status"],
            "attempts": r["attempts"],
        }
        for key in ("material_id", "observation_id", "result_status", "invocation_id", "delivery_key"):
            if r.get(key):
                out[key] = r[key]
        if r.get("handler"):
            out["handler"] = r["handler"]
        if r.get("error"):
            out["error"] = r["error"]
        for key in ("started_at", "finished_at"):
            if r.get(key) is not None:
                out[key] = rfc3339(r[key])
        return out

    def list_items(
        self,
        conn: Any,
        run_id: str,
        *,
        stage_id: str | None,
        status: str | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict[str, Any]], str | None]:
        self.get_row(conn, run_id)
        where: list[str] = ["run_id = %s"]
        params: list[Any] = [run_id]
        if stage_id:
            where.append("stage_id = %s")
            params.append(stage_id)
        if status:
            where.append("status = %s")
            params.append(status)
        if cursor:
            where.append("seq > %s")
            params.append(int(decode_cursor(cursor)))
        rows = conn.execute(
            f"SELECT * FROM items WHERE {' AND '.join(where)} ORDER BY seq LIMIT %s",  # noqa: S608 - fixed fragments
            (*params, limit + 1),
        ).fetchall()
        nxt = encode_cursor(int(rows[limit - 1]["seq"])) if len(rows) > limit else None
        return [self.item_view(r) for r in rows[:limit]], nxt

    def trace(self, conn: Any, material_id: str) -> dict[str, Any]:
        rows = conn.execute(
            "SELECT i.*, r.config FROM items i JOIN runs r ON r.run_id = i.run_id"
            " WHERE i.material_id = %s ORDER BY i.seq",
            (material_id,),
        ).fetchall()
        if not rows:
            raise NotFound(f"material '{material_id}' has no trace")
        observations: dict[tuple[str, str], dict[str, Any]] = {}
        source_id = url = None
        for r in rows:
            key = (r["observation_id"] or "", r["run_id"])
            collect_id = _collect_stage(r["config"])["stage_id"]
            obs = observations.setdefault(
                key,
                {
                    "observation_id": r["observation_id"] or "",
                    "run_id": r["run_id"],
                    "task_id": r["task_id"],
                    "stages": [],
                },
            )
            source_id = source_id or r["source_id"]
            url = url or r["url"]
            if r["stage_id"] == collect_id:
                if r["fetched_at"] is not None:
                    obs["fetched_at"] = rfc3339(r["fetched_at"])
                if r["content_sha256"]:
                    obs["content_sha256"] = r["content_sha256"]
                continue
            stage: dict[str, Any] = {"stage_id": r["stage_id"]}
            if r["handler"]:
                stage["handler"] = r["handler"]
            if r["invocation_id"]:
                stage["invocation_id"] = r["invocation_id"]
            if r["result_status"]:
                stage["result_status"] = r["result_status"]
            if r["outputs"]:
                stage["outputs"] = r["outputs"]
            obs["stages"].append(stage)
        out: dict[str, Any] = {"material_id": material_id, "observations": list(observations.values())}
        if source_id:
            out["source_id"] = source_id
        if url:
            out["url"] = url
        return out

    # ------------------------------------------------------------------ cancellation & completion
    def request_cancel(self, run_id: str, actor: str, reason: str | None) -> tuple[dict[str, Any], bool]:
        """Returns ``(job, accepted)``; ``accepted=False`` when the run was already terminal (200)."""
        with self.core.db.tx() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id = %s FOR UPDATE", (run_id,)).fetchone()
            if row is None:
                raise NotFound(f"run '{run_id}' not found")
            if row["status"] in TERMINAL_RUN:
                return self.job_view(conn, row), False
            if row["status"] != "cancelling":
                conn.execute(
                    "UPDATE runs SET status = 'cancelling', cancel_requested_at = now(), cancel_requested_by = %s,"
                    " cancel_reason = %s, updated_at = now() WHERE run_id = %s",
                    (actor, reason, run_id),
                )
                self._cancel_pending_items(conn, run_id)
        self.maybe_finish(run_id)
        with self.core.db.conn() as conn:
            return self.job_view(conn, self.get_row(conn, run_id)), True

    @staticmethod
    def _cancel_pending_items(conn: Any, run_id: str) -> int:
        cur = conn.execute(
            "UPDATE items SET status = 'cancelled', payload = NULL, lease_owner = NULL, finished_at = now(),"
            " updated_at = now() WHERE run_id = %s AND (status IN ('queued', 'retrying')"
            " OR (status IN ('leased', 'running') AND lease_expires_at < now()))",
            (run_id,),
        )
        return int(cur.rowcount or 0)

    def fail_run(self, conn: Any, run_id: str, problem: Mapping[str, Any]) -> None:
        """Mark a run failed (``on_failure: fail_run``, collector failure, run timeout). Caller holds a tx."""
        conn.execute(
            "UPDATE runs SET status = 'failed', error = %s, finished_at = now(), updated_at = now()"
            " WHERE run_id = %s AND status NOT IN ('succeeded', 'failed', 'cancelled')",
            (Jsonb(dict(problem)), run_id),
        )
        self._cancel_pending_items(conn, run_id)
        self.core.metrics.inc("runs", status="failed")

    def maybe_finish(self, run_id: str) -> str | None:
        """Close the run when the feed is exhausted and no item is active. Returns the new status."""
        with self.core.db.tx() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id = %s FOR UPDATE", (run_id,)).fetchone()
            if row is None or row["status"] in TERMINAL_RUN or row["status"] == "queued":
                return None
            if row["status"] == "cancelling":
                self._cancel_pending_items(conn, run_id)
            if not row["feed_done"]:
                return None
            active = conn.execute(
                "SELECT count(*) AS n FROM items WHERE run_id = %s AND status IN ('queued', 'retrying', 'leased', 'running')",
                (run_id,),
            ).fetchone()
            if active and int(active["n"]) > 0:
                return None
            if row["status"] == "cancelling":
                status = "cancelled"
            elif row["error"] or row["feed_error"]:
                status = "failed"
            else:
                status = "succeeded"
            conn.execute(
                "UPDATE runs SET status = %s, error = coalesce(error, feed_error), finished_at = now(),"
                " updated_at = now() WHERE run_id = %s",
                (status, run_id),
            )
        self.core.metrics.inc("runs", status=status)
        log.info("run finished", extra={"run_id": run_id, "status": status})
        return status


def problem(code: str, detail: str, status: int = 500, retryable: bool = False) -> dict[str, Any]:
    return {
        "type": f"urn:jane:problem:{code}",
        "title": code.replace("_", " ").capitalize(),
        "status": status,
        "code": code,
        "retryable": retryable,
        "detail": detail[:1000],
    }


def job_problem(error: JaneError) -> dict[str, Any]:
    return error.to_problem().model_dump(exclude_none=True)


def utcnow() -> datetime:
    return now()
