"""Management operations behind ``orchestrator.v1``: sources, tasks, runs, connections, limits,
activations with audit, problem groups, unknown materials, executors."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from jane_kit.errors import (
    Conflict,
    FieldError,
    JaneError,
    NotFound,
    ServiceUnavailable,
    ValidationFailed,
)
from jane_kit.pagination import decode_cursor, encode_cursor
from jane_orchestrator.common import etag, new_id, now, parse_etag, rfc3339
from jane_orchestrator.core import Core
from jane_orchestrator.dag import effective_forward_unknown, stage_map, validate_task
from jane_orchestrator.db import Jsonb
from jane_orchestrator.executors import ExecutorError
from jane_orchestrator.runs import Runs
from jane_orchestrator.schedule import CronError, next_fire
from jane_orchestrator.stored_raw import stored_raw_id

__all__ = ["Admin", "PreconditionFailed"]

READ_ONLY_SOURCE = ("created_at", "updated_at")
SECRET_NAME = re.compile(r"(pass(word|wd)?|secret|token|api[_-]?key|private[_-]?key|credential)", re.I)


class PreconditionFailed(JaneError):
    code = "precondition_failed"


class AccessDeniedByPolicy(JaneError):
    code = "access_denied_by_policy"


def _check_if_match(if_match: str | None, version: int) -> None:
    if if_match is not None and parse_etag(if_match) != version and if_match.strip() != "*":
        raise PreconditionFailed(f"If-Match {if_match} does not match current ETag {etag(version)}")


def _page(rows: list[Any], limit: int, key: str) -> tuple[list[Any], str | None]:
    nxt = encode_cursor(rows[limit - 1][key]) if len(rows) > limit else None
    return rows[:limit], nxt


class Admin:
    def __init__(self, core: Core) -> None:
        self.core = core
        self.runs = Runs(core)

    # ================================================================== LLM budgets
    def _enqueue_budget(
        self, conn: Any, scope_type: str, scope_id: str, limits: Mapping[str, Any] | None
    ) -> None:
        """Queue the sync of a source/task LLM budget to the gateway (llm.v1 ``BudgetDefinition``).

        ``limits.llm.budget`` / ``max_requests_per_minute`` set → PUT; unset after an earlier sync, or the
        object deleted → DELETE (the inherited budget applies again)."""
        if self.core.executors.first("llm") is None:
            return
        llm = (limits or {}).get("llm") or {}
        doc: dict[str, Any] = {"scope_type": scope_type, "scope_id": scope_id}
        if llm.get("budget"):
            doc["budget"] = llm["budget"]
        if llm.get("max_requests_per_minute"):
            doc["max_requests_per_minute"] = llm["max_requests_per_minute"]
        if len(doc) > 2:
            conn.execute(
                "INSERT INTO budget_sync (scope_type, scope_id, op, doc, status) VALUES (%s, %s, 'put', %s, 'pending')"
                " ON CONFLICT (scope_type, scope_id) DO UPDATE SET op = 'put', doc = EXCLUDED.doc,"
                " status = 'pending', attempts = 0, available_at = now(), message = NULL",
                (scope_type, scope_id, Jsonb(doc)),
            )
        else:
            conn.execute(
                "UPDATE budget_sync SET op = 'delete', doc = NULL, status = 'pending', attempts = 0,"
                " available_at = now(), message = NULL WHERE scope_type = %s AND scope_id = %s",
                (scope_type, scope_id),
            )

    # ================================================================== sources
    @staticmethod
    def _source_view(row: Mapping[str, Any]) -> dict[str, Any]:
        doc = dict(row["doc"])
        doc["created_at"] = rfc3339(row["created_at"])
        doc["updated_at"] = rfc3339(row["updated_at"])
        return doc

    def _validate_source(self, doc: Mapping[str, Any]) -> dict[str, Any]:
        self.core.schemas.validate(self.core.schemas.schema_uri("source.schema.json"), doc)
        return {k: v for k, v in doc.items() if k not in READ_ONLY_SOURCE}

    def create_source(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]:
        clean = self._validate_source(doc)
        with self.core.db.tx() as conn:
            row = conn.execute(
                "INSERT INTO sources (source_id, doc) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING *",
                (clean["source_id"], Jsonb(clean)),
            ).fetchone()
            if row is None:
                raise Conflict(f"source '{clean['source_id']}' already exists")
            self._enqueue_budget(conn, "source", clean["source_id"], clean.get("limits"))
            self.core.audit(conn, actor, "source.create", "source", clean["source_id"], {})
        return self._source_view(row), 1

    def get_source(self, source_id: str) -> tuple[dict[str, Any], int]:
        with self.core.db.conn() as conn:
            row = conn.execute("SELECT * FROM sources WHERE source_id = %s", (source_id,)).fetchone()
        if row is None:
            raise NotFound(f"source '{source_id}' not found")
        return self._source_view(row), int(row["version"])

    def replace_source(
        self, source_id: str, doc: Mapping[str, Any], if_match: str | None, actor: str
    ) -> tuple[dict[str, Any], int]:
        clean = self._validate_source(doc)
        if clean["source_id"] != source_id:
            raise ValidationFailed(
                "source_id in the body differs from the path",
                errors=[FieldError(pointer="/source_id", message="must equal the path parameter")],
            )
        with self.core.db.tx() as conn:
            row = conn.execute(
                "SELECT * FROM sources WHERE source_id = %s FOR UPDATE", (source_id,)
            ).fetchone()
            if row is None:
                raise NotFound(f"source '{source_id}' not found")
            _check_if_match(if_match, int(row["version"]))
            new = conn.execute(
                "UPDATE sources SET doc = %s, version = version + 1, updated_at = now() WHERE source_id = %s RETURNING *",
                (Jsonb(clean), source_id),
            ).fetchone()
            changed = sorted(k for k in set(clean) | set(row["doc"]) if clean.get(k) != row["doc"].get(k))
            self._enqueue_budget(conn, "source", source_id, clean.get("limits"))
            self.core.audit(conn, actor, "source.update", "source", source_id, {"changed": changed})
        return self._source_view(new), int(new["version"])

    def delete_source(self, source_id: str, actor: str) -> None:
        with self.core.db.tx() as conn:
            row = conn.execute(
                "SELECT 1 FROM sources WHERE source_id = %s FOR UPDATE", (source_id,)
            ).fetchone()
            if row is None:
                raise NotFound(f"source '{source_id}' not found")
            if conn.execute("SELECT 1 FROM tasks WHERE source_id = %s LIMIT 1", (source_id,)).fetchone():
                raise Conflict(f"source '{source_id}' has tasks")
            conn.execute("DELETE FROM sources WHERE source_id = %s", (source_id,))
            self._enqueue_budget(conn, "source", source_id, None)
            self.core.audit(conn, actor, "source.delete", "source", source_id, {})

    def list_sources(
        self, kind: str | None, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str | None]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if kind:
            where.append("doc->>'kind' = %s")
            params.append(kind)
        if cursor:
            where.append("source_id > %s")
            params.append(str(decode_cursor(cursor)))
        with self.core.db.conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM sources WHERE {' AND '.join(where)} ORDER BY source_id LIMIT %s",  # noqa: S608
                (*params, limit + 1),
            ).fetchall()
        page, nxt = _page(rows, limit, "source_id")
        return [self._source_view(r) for r in page], nxt

    # ================================================================== tasks
    def _known_connections(self, conn: Any) -> set[str]:
        return {r["connection_id"] for r in conn.execute("SELECT connection_id FROM connections").fetchall()}

    def validate_task(self, doc: Any) -> dict[str, Any]:
        """``TaskValidation``: schema + DAG + references (never raises for an invalid config)."""
        uri = self.core.schemas.schema_uri("task-config.schema.json")
        errors = self.core.schemas.check(uri, doc)
        warnings: list[FieldError] = []
        source = None
        if not errors:
            with self.core.db.conn() as conn:
                row = conn.execute(
                    "SELECT doc FROM sources WHERE source_id = %s", (doc["input"]["source_id"],)
                ).fetchone()
                source = dict(row["doc"]) if row else None
                sem_errors, warnings = validate_task(doc, source, self._known_connections(conn))
            errors += sem_errors
            errors += self._schedule_errors(doc)
        out: dict[str, Any] = {
            "valid": not errors,
            "errors": [e.model_dump(exclude_none=True) for e in errors],
            "warnings": [w.model_dump(exclude_none=True) for w in warnings],
        }
        if isinstance(doc, dict) and isinstance(doc.get("input"), dict):
            out["effective_forward_unknown_to_llm"] = effective_forward_unknown(doc, source)
        return out

    @staticmethod
    def _schedule_errors(doc: Mapping[str, Any]) -> list[FieldError]:
        schedule = doc.get("schedule")
        if not schedule:
            return []
        try:
            next_fire(schedule, now(), None)
        except CronError as exc:
            return [FieldError(pointer="/schedule/cron", code="invalid_cron", message=str(exc))]
        except Exception as exc:
            return [FieldError(pointer="/schedule", code="invalid_schedule", message=str(exc))]
        return []

    def _check_task(self, conn: Any, doc: Mapping[str, Any]) -> dict[str, Any]:
        self.core.schemas.validate(self.core.schemas.schema_uri("task-config.schema.json"), doc)
        row = conn.execute(
            "SELECT doc FROM sources WHERE source_id = %s", (doc["input"]["source_id"],)
        ).fetchone()
        source = dict(row["doc"]) if row else None
        errors, _ = validate_task(doc, source, None)
        errors += self._schedule_errors(doc)
        if errors:
            raise ValidationFailed("task configuration is invalid", errors=errors)
        assert source is not None
        return source

    @staticmethod
    def _next_run(doc: Mapping[str, Any], last: datetime | None) -> datetime | None:
        if not doc.get("enabled", True):
            return None
        return next_fire(doc.get("schedule"), now(), last)

    def create_task(self, doc: Mapping[str, Any], actor: str) -> tuple[dict[str, Any], int]:
        with self.core.db.tx() as conn:
            self._check_task(conn, doc)
            row = conn.execute(
                "INSERT INTO tasks (task_id, source_id, doc, next_run_at) VALUES (%s, %s, %s, %s)"
                " ON CONFLICT DO NOTHING RETURNING *",
                (doc["task_id"], doc["input"]["source_id"], Jsonb(dict(doc)), self._next_run(doc, None)),
            ).fetchone()
            if row is None:
                raise Conflict(f"task '{doc['task_id']}' already exists")
            self._enqueue_budget(conn, "task", doc["task_id"], doc.get("limits"))
            self.core.audit(conn, actor, "task.create", "task", doc["task_id"], {})
        return dict(row["doc"]), 1

    def get_task_row(self, conn: Any, task_id: str, lock: bool = False) -> dict[str, Any]:
        row = conn.execute(
            "SELECT * FROM tasks WHERE task_id = %s FOR UPDATE"
            if lock
            else "SELECT * FROM tasks WHERE task_id = %s",
            (task_id,),
        ).fetchone()
        if row is None:
            raise NotFound(f"task '{task_id}' not found")
        return dict(row)

    def get_task(self, task_id: str) -> tuple[dict[str, Any], int]:
        with self.core.db.conn() as conn:
            row = self.get_task_row(conn, task_id)
        return dict(row["doc"]), int(row["version"])

    def replace_task(
        self, task_id: str, doc: Mapping[str, Any], if_match: str | None, actor: str
    ) -> tuple[dict[str, Any], int]:
        if doc.get("task_id") != task_id:
            raise ValidationFailed(
                "task_id in the body differs from the path",
                errors=[FieldError(pointer="/task_id", message="must equal the path parameter")],
            )
        with self.core.db.tx() as conn:
            row = self.get_task_row(conn, task_id, lock=True)
            _check_if_match(if_match, int(row["version"]))
            self._check_task(conn, doc)
            new = conn.execute(
                "UPDATE tasks SET doc = %s, source_id = %s, version = version + 1, next_run_at = %s, updated_at = now()"
                " WHERE task_id = %s RETURNING *",
                (
                    Jsonb(dict(doc)),
                    doc["input"]["source_id"],
                    self._next_run(doc, row["last_scheduled_at"]),
                    task_id,
                ),
            ).fetchone()
            changed = sorted(k for k in set(doc) | set(row["doc"]) if doc.get(k) != row["doc"].get(k))
            self._enqueue_budget(conn, "task", task_id, doc.get("limits"))
            self.core.audit(conn, actor, "task.update", "task", task_id, {"changed": changed})
        return dict(new["doc"]), int(new["version"])

    def delete_task(self, task_id: str, actor: str) -> None:
        with self.core.db.tx() as conn:
            self.get_task_row(conn, task_id, lock=True)
            active = conn.execute(
                "SELECT 1 FROM runs WHERE task_id = %s AND status IN ('queued', 'running', 'cancelling') LIMIT 1",
                (task_id,),
            ).fetchone()
            if active:
                raise Conflict(f"task '{task_id}' has an active run; cancel it first")
            conn.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
            self._enqueue_budget(conn, "task", task_id, None)
            self.core.audit(conn, actor, "task.delete", "task", task_id, {})

    @staticmethod
    def _package_stages(
        doc: Mapping[str, Any], source: Mapping[str, Any], package_id: str, version: str | None
    ) -> list[dict[str, Any]]:
        out = []
        for s in doc.get("stages", []):
            ref = (
                s.get("handler")
                if s["kind"] == "handler"
                else (s.get("collector") or {}).get("rules") or source.get("collector_rules")
            )
            if (
                ref
                and ref.get("package_id") == package_id
                and (version is None or ref.get("version") == version)
            ):
                out.append({"stage_id": s["stage_id"], "package": ref})
        return out

    def list_tasks(
        self,
        source_id: str | None,
        package_id: str | None,
        package_version: str | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict[str, Any]], str | None]:
        if package_version and not package_id:
            raise ValidationFailed(
                "package_version requires package_id",
                errors=[FieldError(parameter="package_version", message="only together with package_id")],
            )
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if source_id:
            where.append("t.source_id = %s")
            params.append(source_id)
        if package_id:
            ref: dict[str, Any] = {"package_id": package_id}
            if package_version:
                ref["version"] = package_version
            where.append(
                "(t.doc->'stages' @> %s OR t.doc->'stages' @> %s OR (s.doc->'collector_rules' @> %s"
                " AND NOT t.doc->'stages' @> %s))"
            )
            params += [
                Jsonb([{"handler": ref}]),
                Jsonb([{"collector": {"rules": ref}}]),
                Jsonb(ref),
                Jsonb([{"kind": "collect", "collector": {"rules": {}}}]),
            ]
        if cursor:
            where.append("t.task_id > %s")
            params.append(str(decode_cursor(cursor)))
        with self.core.db.conn() as conn:
            rows = conn.execute(
                "SELECT t.*, s.doc AS source_doc FROM tasks t JOIN sources s ON s.source_id = t.source_id"  # noqa: S608
                f" WHERE {' AND '.join(where)} ORDER BY t.task_id LIMIT %s",
                (*params, limit + 1),
            ).fetchall()
            page, nxt = _page(rows, limit, "task_id")
            items = []
            for r in page:
                doc = r["doc"]
                summary: dict[str, Any] = {
                    "task_id": r["task_id"],
                    "title": doc["title"],
                    "source_id": r["source_id"],
                    "enabled": doc.get("enabled", True),
                }
                if doc.get("schedule"):
                    summary["schedule"] = doc["schedule"]
                if r["next_run_at"]:
                    summary["next_run_at"] = rfc3339(r["next_run_at"])
                if package_id:
                    summary["package_stages"] = self._package_stages(
                        doc, r["source_doc"], package_id, package_version
                    )
                last = conn.execute(
                    "SELECT run_id, status, finished_at FROM runs WHERE task_id = %s ORDER BY seq DESC LIMIT 1",
                    (r["task_id"],),
                ).fetchone()
                if last:
                    lr: dict[str, Any] = {"run_id": last["run_id"], "status": last["status"]}
                    if last["finished_at"]:
                        lr["finished_at"] = rfc3339(last["finished_at"])
                    summary["last_run"] = lr
                items.append(summary)
        return items, nxt

    # ================================================================== runs
    def start_run(
        self, task_id: str, body: Mapping[str, Any], actor: str, idempotency_key: str | None
    ) -> dict[str, Any]:
        with self.core.db.tx() as conn:
            row = self.get_task_row(conn, task_id, lock=True)
            source = conn.execute(
                "SELECT doc FROM sources WHERE source_id = %s", (row["source_id"],)
            ).fetchone()
            run = self.runs.create(
                conn,
                row,
                source["doc"],
                trigger="manual",
                test_mode=bool(body.get("test_mode", False)),
                reason=body.get("reason"),
                input_override=body.get("input_override"),
                request_limits=body.get("limits"),
                requested_by=actor,
                idempotency_key=idempotency_key,
            )
            assert run is not None
            return self.runs.job_view(conn, run)

    def start_reprocessing(
        self, body: Mapping[str, Any], actor: str, idempotency_key: str | None
    ) -> dict[str, Any]:
        stored = dict(body["stored_materials"])
        if not stored.get("storage_connection_id"):
            raise ValidationFailed(
                "stored_materials.storage_connection_id is required",
                errors=[FieldError(pointer="/stored_materials/storage_connection_id", message="required")],
            )
        if self.core.executors.first("storage_read") is None:
            raise ServiceUnavailable("no storage_read executor configured for reprocessing")
        with self.core.db.tx() as conn:
            row = self.get_task_row(conn, body["task_id"], lock=True)
            source = conn.execute(
                "SELECT doc FROM sources WHERE source_id = %s", (row["source_id"],)
            ).fetchone()
            run = self.runs.create(
                conn,
                row,
                source["doc"],
                trigger="reprocess",
                test_mode=bool(body.get("test_mode", False)),
                reason=body.get("reason"),
                input_override={"stored_materials": stored},
                requested_by=actor,
                idempotency_key=idempotency_key,
                from_stage=body.get("from_stage"),
                enforce_overlap=False,
            )
            assert run is not None
            return self.runs.job_view(conn, run)

    # ================================================================== activations
    @staticmethod
    def _activation_view(r: Mapping[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {
            "activation_id": r["activation_id"],
            "task_id": r["task_id"],
            "stage_id": r["stage_id"],
            "package": r["package"],
            "kind": r["kind"],
            "activated_at": rfc3339(r["activated_at"]),
        }
        for key in ("previous", "reason", "activated_by"):
            if r.get(key):
                out[key] = r[key]
        return out

    def list_activations(
        self, task_id: str, stage_id: str, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str | None]:
        with self.core.db.conn() as conn:
            row = self.get_task_row(conn, task_id)
            if stage_id not in stage_map(row["doc"]):
                raise NotFound(f"stage '{stage_id}' not found in task '{task_id}'")
            where: list[str] = ["task_id = %s", "stage_id = %s"]
            params: list[Any] = [task_id, stage_id]
            if cursor:
                where.append("seq < %s")
                params.append(int(decode_cursor(cursor)))
            rows = conn.execute(
                f"SELECT * FROM activations WHERE {' AND '.join(where)} ORDER BY seq DESC LIMIT %s",  # noqa: S608
                (*params, limit + 1),
            ).fetchall()
        page, nxt = _page(rows, limit, "seq")
        return [self._activation_view(r) for r in page], nxt

    def _registry_get(self, path: str) -> dict[str, Any]:
        registry = self.core.executors.first("registry")
        if registry is None:
            raise ServiceUnavailable("no registry executor configured: cannot verify the package version")
        try:
            data: dict[str, Any] = self.core.executors.call(registry, "GET", path).json()
            return data
        except ExecutorError as exc:
            if exc.status == 404:
                raise NotFound(f"registry: {path} not found") from exc
            raise JaneError(str(exc), code="upstream_unavailable") from exc

    def activate(self, task_id: str, stage_id: str, body: Mapping[str, Any], actor: str) -> dict[str, Any]:
        """Read → check in the registry (no DB lock held during network calls) → write if the task is unchanged."""
        kind = body["kind"]
        package = dict(body["package"]) if body.get("package") else None
        # 1. read
        with self.core.db.conn() as conn:
            row = self.get_task_row(conn, task_id)
            stages = stage_map(row["doc"])
            if stage_id not in stages:
                raise NotFound(f"stage '{stage_id}' not found in task '{task_id}'")
            stage = stages[stage_id]
            if stage["kind"] != "handler":
                raise ValidationFailed(
                    "activations apply to handler stages",
                    errors=[FieldError(parameter="stage_id", message="stage is not kind=handler")],
                )
            read_version = int(row["version"])
            if kind == "rollback" and package is None:
                last = conn.execute(
                    "SELECT * FROM activations WHERE task_id = %s AND stage_id = %s ORDER BY seq DESC LIMIT 1",
                    (task_id, stage_id),
                ).fetchone()
                if last is None or not last["previous"]:
                    raise Conflict("nothing to roll back: the stage has no previous activation")
                package = dict(last["previous"])
            source = conn.execute(
                "SELECT doc FROM sources WHERE source_id = %s", (row["source_id"],)
            ).fetchone()
            policy = ((source["doc"] if source else {}).get("change_policy") or {}).get(
                "llm_versions", "manual_approval"
            )
        if package is None:
            raise ValidationFailed(
                f"package is required for kind={kind}",
                errors=[FieldError(pointer="/package", message="required")],
            )
        # 2. check (network, outside any transaction)
        if kind == "auto_activate" and policy != "auto_after_checks":
            raise AccessDeniedByPolicy(
                "Automatic activation is not allowed",
                title="Automatic activation is not allowed",
                details={"reason": "source_policy"},
            )
        version = self._registry_get(f"/v1/packages/{package['package_id']}/versions/{package['version']}")
        if kind == "rollback" and version.get("status") == "yanked":
            raise Conflict(f"{package['package_id']}@{package['version']} is yanked")
        if kind == "activate" and version.get("status") != "approved":
            raise Conflict(
                f"{package['package_id']}@{package['version']} is not approved (status {version.get('status')})"
            )
        if kind == "auto_activate":
            pkg = self._registry_get(f"/v1/packages/{package['package_id']}")
            reason = None
            if not pkg.get("auto_changes_allowed"):
                reason = "package_auto_changes_forbidden"
            elif version.get("test_status") != "passed":
                reason = "tests_not_passed"
            if reason is not None:
                raise AccessDeniedByPolicy(
                    "Automatic activation is not allowed",
                    title="Automatic activation is not allowed",
                    details={"reason": reason},
                )
        registry_digest = version.get("digest")
        if package.get("digest") and registry_digest and package["digest"] != registry_digest:
            raise JaneError("package digest differs from the registry", code="digest_mismatch")
        if registry_digest:
            package["digest"] = registry_digest
        # 3. write, only if nobody changed the task meanwhile
        with self.core.db.tx() as conn:
            row = self.get_task_row(conn, task_id, lock=True)
            if int(row["version"]) != read_version:
                raise Conflict("the task changed during activation; repeat the request", retryable=True)
            doc = dict(row["doc"])
            current = dict(stage_map(doc)[stage_id]["handler"])
            for s in doc["stages"]:
                if s["stage_id"] == stage_id:
                    s["handler"] = package
            conn.execute(
                "UPDATE tasks SET doc = %s, version = version + 1, updated_at = now() WHERE task_id = %s",
                (Jsonb(doc), task_id),
            )
            act = conn.execute(
                "INSERT INTO activations (activation_id, task_id, stage_id, package, previous, kind, reason, activated_by)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                (
                    new_id("act"),
                    task_id,
                    stage_id,
                    Jsonb(package),
                    Jsonb(current),
                    kind,
                    body.get("reason"),
                    actor,
                ),
            ).fetchone()
            self.core.audit(
                conn,
                actor,
                f"stage.{kind}",
                "stage",
                f"{task_id}/{stage_id}",
                {
                    "package_id": package["package_id"],
                    "version": package["version"],
                    "previous": current.get("version"),
                    "previous_package_id": current.get("package_id"),
                    "reason": body.get("reason"),
                },
            )
        return self._activation_view(act)

    # ================================================================== problems & unknown
    def _group_view(self, r: Mapping[str, Any]) -> dict[str, Any]:
        samples = [dict(s) for s in r["samples"]]
        # RAW storage and extraction run in parallel. Enrich at read time so a RAW write completed
        # after the problem was registered is visible, also after a new API process starts.
        with self.core.db.conn() as conn:
            for sample in samples:
                object_id = stored_raw_id(
                    conn,
                    r["source_id"],
                    sample.get("observation_id"),
                    invocation_id=sample.get("invocation_id"),
                )
                if object_id:
                    sample["stored_object_id"] = object_id
        out: dict[str, Any] = {
            "group_id": r["group_id"],
            "source_id": r["source_id"],
            "package": r["package"],
            "problem": r["problem"],
            "signature": r["signature"],
            "count": r["count"],
            "first_seen_at": rfc3339(r["first_seen_at"]),
            "last_seen_at": rfc3339(r["last_seen_at"]),
            "status": r["status"],
            "samples": samples,
        }
        if r["failure_kind"]:
            out["failure_kind"] = r["failure_kind"]
        if r["assistant_job_id"]:
            out["assistant_job_id"] = r["assistant_job_id"]
        return out

    def list_problem_groups(
        self, source_id: str | None, status: str | None, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str | None]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if source_id:
            where.append("source_id = %s")
            params.append(source_id)
        if status:
            where.append("status = %s")
            params.append(status)
        if cursor:
            where.append("seq > %s")
            params.append(int(decode_cursor(cursor)))
        with self.core.db.conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM problem_groups WHERE {' AND '.join(where)} ORDER BY seq LIMIT %s",  # noqa: S608
                (*params, limit + 1),
            ).fetchall()
        page, nxt = _page(rows, limit, "seq")
        return [self._group_view(r) for r in page], nxt

    def update_problem_group(self, group_id: str, patch: Mapping[str, Any], actor: str) -> dict[str, Any]:
        with self.core.db.tx() as conn:
            row = conn.execute(
                "SELECT * FROM problem_groups WHERE group_id = %s FOR UPDATE", (group_id,)
            ).fetchone()
            if row is None:
                raise NotFound(f"problem group '{group_id}' not found")
            new = conn.execute(
                "UPDATE problem_groups SET status = coalesce(%s, status),"
                " assistant_job_id = coalesce(%s, assistant_job_id) WHERE group_id = %s RETURNING *",
                (patch.get("status"), patch.get("assistant_job_id"), group_id),
            ).fetchone()
            self.core.audit(conn, actor, "problem_group.update", "problem_group", group_id, dict(patch))
        return self._group_view(new)

    def list_unknown(
        self, source_id: str | None, forwarded: bool | None, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str | None]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if source_id:
            where.append("source_id = %s")
            params.append(source_id)
        if forwarded is not None:
            where.append("forwarded_to_llm = %s")
            params.append(forwarded)
        if cursor:
            where.append("id > %s")
            params.append(int(decode_cursor(cursor)))
        with self.core.db.conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM unknown_materials WHERE {' AND '.join(where)} ORDER BY id LIMIT %s",  # noqa: S608
                (*params, limit + 1),
            ).fetchall()
            for row in rows:
                row["stored_object_id"] = stored_raw_id(
                    conn, row["source_id"], row["observation_id"], run_id=row["run_id"]
                )
        page, nxt = _page(rows, limit, "id")
        out = []
        for r in page:
            item: dict[str, Any] = {
                "material_id": r["material_id"],
                "observation_id": r["observation_id"],
                "source_id": r["source_id"],
                "run_id": r["run_id"],
                "registered_at": rfc3339(r["registered_at"]),
                "forwarded_to_llm": r["forwarded_to_llm"],
            }
            if r["url"]:
                item["url"] = r["url"]
            if r["reason"]:
                item["reason"] = r["reason"]
            if r["stored_object_id"]:
                item["stored_object_id"] = r["stored_object_id"]
            out.append(item)
        return out, nxt

    # ================================================================== connections
    def _connection_view(self, conn: Any, row: Mapping[str, Any]) -> dict[str, Any]:
        syncs = conn.execute(
            "SELECT * FROM connection_sync WHERE connection_id = %s AND op = 'put' ORDER BY executor",
            (row["connection_id"],),
        ).fetchall()
        executors = []
        for s in syncs:
            e: dict[str, Any] = {"executor": s["executor"], "sync_status": s["status"]}
            if s["synced_at"]:
                e["synced_at"] = rfc3339(s["synced_at"])
            if s["message"]:
                e["message"] = s["message"]
            executors.append(e)
        return {"connection": row["doc"], "executors": executors}

    @staticmethod
    def _secret_like_params(params: Mapping[str, Any], prefix: str = "/params") -> list[FieldError]:
        errors = []
        for key, value in params.items():
            pointer = f"{prefix}/{key}"
            if isinstance(value, dict):
                errors += Admin._secret_like_params(value, pointer)
            elif SECRET_NAME.search(str(key)) and value not in (None, "", False):
                errors.append(
                    FieldError(
                        pointer=pointer,
                        code="secret_detected",
                        message="looks like a secret value; use secret_refs (env:/file:/vault:)",
                    )
                )
        return errors

    def list_connections(
        self, kind: str | None, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str | None]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if kind:
            where.append("doc->>'kind' = %s")
            params.append(kind)
        if cursor:
            where.append("connection_id > %s")
            params.append(str(decode_cursor(cursor)))
        with self.core.db.conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM connections WHERE {' AND '.join(where)} ORDER BY connection_id LIMIT %s",  # noqa: S608
                (*params, limit + 1),
            ).fetchall()
            page, nxt = _page(rows, limit, "connection_id")
            return [self._connection_view(conn, r) for r in page], nxt

    def get_connection(self, connection_id: str) -> tuple[dict[str, Any], int]:
        with self.core.db.conn() as conn:
            row = conn.execute(
                "SELECT * FROM connections WHERE connection_id = %s", (connection_id,)
            ).fetchone()
            if row is None:
                raise NotFound(f"connection '{connection_id}' not found")
            return self._connection_view(conn, row), int(row["version"])

    def put_connection(
        self, connection_id: str, doc: Mapping[str, Any], if_match: str | None, actor: str
    ) -> tuple[dict[str, Any], int]:
        self.core.schemas.validate(self.core.schemas.schema_uri("common/connection.schema.json"), doc)
        if doc["connection_id"] != connection_id:
            raise ValidationFailed(
                "connection_id in the body differs from the path",
                errors=[FieldError(pointer="/connection_id", message="must equal the path parameter")],
            )
        secrets = self._secret_like_params(doc.get("params") or {})
        if secrets:
            raise JaneError("secret-like values in params", code="secret_detected", errors=secrets)
        with self.core.db.tx() as conn:
            row = conn.execute(
                "SELECT * FROM connections WHERE connection_id = %s FOR UPDATE", (connection_id,)
            ).fetchone()
            if row is not None:
                _check_if_match(if_match, int(row["version"]))
                new = conn.execute(
                    "UPDATE connections SET doc = %s, version = version + 1, updated_at = now()"
                    " WHERE connection_id = %s RETURNING *",
                    (Jsonb(dict(doc)), connection_id),
                ).fetchone()
            else:
                if if_match is not None and if_match.strip() != "*":
                    raise PreconditionFailed("connection does not exist")
                new = conn.execute(
                    "INSERT INTO connections (connection_id, doc) VALUES (%s, %s) RETURNING *",
                    (connection_id, Jsonb(dict(doc))),
                ).fetchone()
            for cfg in self.core.executors.configs.values():
                if cfg.syncs_connections:
                    conn.execute(
                        "INSERT INTO connection_sync (connection_id, executor, op, status) VALUES (%s, %s, 'put', 'pending')"
                        " ON CONFLICT (connection_id, executor) DO UPDATE SET op = 'put', status = 'pending',"
                        " attempts = 0, available_at = now(), message = NULL",
                        (connection_id, cfg.executor),
                    )
            self.core.audit(
                conn,
                actor,
                "connection.update",
                "connection",
                connection_id,
                {"kind": doc["kind"], "secret_refs": sorted((doc.get("secret_refs") or {}).keys())},
            )
            return self._connection_view(conn, new), int(new["version"])

    def delete_connection(self, connection_id: str, actor: str) -> None:
        with self.core.db.tx() as conn:
            row = conn.execute(
                "SELECT 1 FROM connections WHERE connection_id = %s FOR UPDATE", (connection_id,)
            ).fetchone()
            if row is None:
                raise NotFound(f"connection '{connection_id}' not found")
            refs = conn.execute(
                "SELECT task_id FROM tasks t, jsonb_array_elements(t.doc->'stages') st"
                " WHERE EXISTS (SELECT 1 FROM jsonb_each_text(coalesce(st->'connections', '{}'::jsonb)) c"
                "               WHERE c.value = %s) LIMIT 1",
                (connection_id,),
            ).fetchone()
            src_refs = conn.execute(
                "SELECT source_id FROM sources s WHERE EXISTS (SELECT 1 FROM"
                " jsonb_each_text(coalesce(s.doc->'connections', '{}'::jsonb)) c WHERE c.value = %s) LIMIT 1",
                (connection_id,),
            ).fetchone()
            if refs or src_refs:
                who = f"task '{refs['task_id']}'" if refs else f"source '{src_refs['source_id']}'"
                raise Conflict(f"connection '{connection_id}' is referenced by {who}")
            conn.execute("DELETE FROM connections WHERE connection_id = %s", (connection_id,))
            conn.execute(
                "UPDATE connection_sync SET op = 'delete', status = 'pending', attempts = 0, available_at = now()"
                " WHERE connection_id = %s",
                (connection_id,),
            )
            self.core.audit(conn, actor, "connection.delete", "connection", connection_id, {})

    # ================================================================== limits
    def get_platform_limits(self) -> tuple[dict[str, Any], int]:
        with self.core.db.conn() as conn:
            return self.core.platform_limits(conn)

    def put_platform_limits(
        self, doc: Mapping[str, Any], if_match: str | None, actor: str
    ) -> tuple[dict[str, Any], int]:
        uri = self.core.schemas.schema_uri("common/limits.schema.json#/$defs/PlatformLimits")
        self.core.schemas.validate(uri, doc)
        with self.core.db.tx() as conn:
            current, version = self.core.platform_limits(conn)
            conn.execute("SELECT 1 FROM platform_limits WHERE id = 1 FOR UPDATE")
            _check_if_match(if_match, version)
            row = conn.execute(
                "UPDATE platform_limits SET doc = %s, version = version + 1, updated_at = now() WHERE id = 1 RETURNING *",
                (Jsonb(dict(doc)),),
            ).fetchone()
            self.core.audit(
                conn,
                actor,
                "limits.update",
                "limits",
                "platform",
                {"before": current, "after": dict(doc)},
            )
        return dict(row["doc"]), int(row["version"])

    def effective_limits(
        self, source_id: str | None, task_id: str | None, stage_id: str | None
    ) -> dict[str, Any]:
        with self.core.db.conn() as conn:
            platform, _ = self.core.platform_limits(conn)
            source = task = stage = None
            if stage_id and not task_id:
                raise ValidationFailed(
                    "stage_id requires task_id",
                    errors=[FieldError(parameter="stage_id", message="requires task_id")],
                )
            if task_id:
                row = self.get_task_row(conn, task_id)
                task = dict(row["doc"])
                if source_id and source_id != row["source_id"]:
                    raise ValidationFailed(
                        "task belongs to another source",
                        errors=[
                            FieldError(parameter="source_id", message=f"task source is {row['source_id']}")
                        ],
                    )
                source_id = row["source_id"]
                if stage_id:
                    stages = stage_map(task)
                    if stage_id not in stages:
                        raise NotFound(f"stage '{stage_id}' not found in task '{task_id}'")
                    stage = stages[stage_id]
            if source_id:
                srow = conn.execute("SELECT doc FROM sources WHERE source_id = %s", (source_id,)).fetchone()
                if srow is None:
                    raise NotFound(f"source '{source_id}' not found")
                source = dict(srow["doc"])
        return self.core.effective(platform, source, task, stage).doc()

    # ================================================================== executors & audit
    def list_executors(self) -> list[dict[str, Any]]:
        out = []
        for cfg in self.core.executors.configs.values():
            out.append(
                {
                    "executor": cfg.executor,
                    "role": cfg.role,
                    "base_url": cfg.base_url,
                    "status": self.core.executors.health(cfg, self.core.engine.executor_health_timeout_ms),
                    "capabilities": cfg.capabilities,
                }
            )
        return out

    def list_audit(
        self, subject_type: str | None, subject_id: str | None, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str | None]:
        where: list[str] = ["TRUE"]
        params: list[Any] = []
        if subject_type:
            where.append("subject_type = %s")
            params.append(subject_type)
        if subject_id:
            where.append("subject_id = %s")
            params.append(subject_id)
        if cursor:
            where.append("seq < %s")
            params.append(int(decode_cursor(cursor)))
        with self.core.db.conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM audit_events WHERE {' AND '.join(where)} ORDER BY seq DESC LIMIT %s",  # noqa: S608
                (*params, limit + 1),
            ).fetchall()
        page, nxt = _page(rows, limit, "seq")
        return [
            {
                "event_id": r["event_id"],
                "at": rfc3339(r["at"]),
                "actor": r["actor"],
                "action": r["action"],
                "subject_type": r["subject_type"],
                "subject_id": r["subject_id"],
                "details": json.loads(json.dumps(r["details"] or {}, default=str)),
            }
            for r in page
        ], nxt
