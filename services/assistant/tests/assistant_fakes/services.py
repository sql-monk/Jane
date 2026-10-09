"""Fakes of collector, handler-runtime, orchestrator and storage (all bound to their contracts)."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

from .base import ContractFake, FakeRequest, Reply, load_spec, problem
from .registry import NOW, FakeRegistry
from .runtime import run_package_tests, unzip
from .site import SITES, TELEGRAM, material, telegram_material

__all__ = ["FakeCollector", "FakeHandler", "FakeOrchestrator", "FakeStorage"]


def _job(job_id: str, kind: str, status: str, result: dict[str, Any] | None = None) -> dict[str, Any]:
    job: dict[str, Any] = {
        "job_id": job_id,
        "kind": kind,
        "status": status,
        "created_at": NOW,
        "links": {"self": f"/v1/jobs/{job_id}", "cancel": f"/v1/jobs/{job_id}/cancel"},
    }
    if result is not None:
        job["result"] = result
    return job


class FakeCollector:
    """Collections over :data:`SITES` / :data:`TELEGRAM`; pages are served in sitemap order."""

    def __init__(self, contracts: Path, name: str = "collector") -> None:
        self.app = ContractFake(contracts / "openapi" / "collector.v1.yaml", name)
        self.collections: dict[str, dict[str, Any]] = {}
        self.cancelled: list[str] = []
        spec = load_spec(contracts / "openapi" / "collector.v1.yaml")
        self._rules_validator = Draft202012Validator(
            {"$ref": (contracts / "schemas" / "collector-rules.schema.json").resolve().as_uri()},
            registry=spec.registry,
        )
        a = self.app
        a.on("startCollection")(self.start)
        a.on("getCollection")(self.get)
        a.on("listCollectionMaterials")(self.materials)
        a.on("validateRules")(self.validate)
        a.on("cancelJob")(self.cancel)

    def _items(self, rules: dict[str, Any], source_id: str | None) -> list[dict[str, Any]]:
        if rules["collector"] == "telegram":
            channel = rules["channels"][0]["username"]
            return [telegram_material(channel, i + 1, t) for i, t in enumerate(TELEGRAM.get(channel, []))]
        hosts = rules["scope"]["allowed_domains"]
        pages = {u: h for host in hosts for u, h in SITES.get(host, {}).items()}
        order = sorted(pages, key=lambda u: (0 if "/product/" in u else 1 if "/catalog/" in u else 2, u))
        return [material(u, pages[u], source_id) for u in order]

    def start(self, req: FakeRequest) -> Reply:
        b = req.json
        cid = f"col_{len(self.collections) + 1:04d}"
        items = self._items(b["rules"], b.get("source_id"))
        self.collections[cid] = {"request": b, "items": items, "status": "running"}
        return Reply(202, _job(cid, "collection", "queued"), {"Location": f"/v1/jobs/{cid}"})

    def _collection(self, cid: str) -> dict[str, Any]:
        c = self.collections[cid]
        return {
            "collection_id": cid,
            "status": c["status"],
            "source_kind": c["request"]["source_kind"],
            "created_at": NOW,
            "stats": {
                "discovered": len(c["items"]),
                "fetched": len(c["items"]),
                "by_strategy": {"sitemap": len(c["items"])},
            },
        }

    def get(self, req: FakeRequest) -> Reply:
        cid = req.path_params["collection_id"]
        return Reply(200, self._collection(cid)) if cid in self.collections else problem(404, "not_found")

    def materials(self, req: FakeRequest) -> Reply:
        c = self.collections[req.path_params["collection_id"]]
        start = int(req.query.get("after", "c_0").split("_")[1])
        limit = int(req.query.get("limit", "50"))
        page = c["items"][start : start + limit]
        end = start + len(page)
        done = end >= len(c["items"])
        if done and c["status"] == "running":
            c["status"] = "succeeded"
        return Reply(
            200,
            {
                "items": page,
                "next_cursor": f"c_{end}" if page else None,
                "end_of_stream": done,
                "collection_status": c["status"],
            },
        )

    def validate(self, req: FakeRequest) -> Reply:
        errors = [
            {"pointer": "/" + "/".join(map(str, e.absolute_path)), "message": e.message}
            for e in self._rules_validator.iter_errors(req.json)
        ]
        supported = not any(s.get("type") == "llm_explore" for s in req.json.get("strategies") or [])
        return Reply(200, {"valid": not errors, "errors": errors, "warnings": [], "supported": supported})

    def cancel(self, req: FakeRequest) -> Reply:
        cid = req.path_params["job_id"]
        self.cancelled.append(cid)
        c = self.collections.get(cid)
        if c is None:
            return problem(404, "not_found")
        if c["status"] != "running":
            return Reply(200, _job(cid, "collection", c["status"]))
        c["status"] = "cancelled"
        return Reply(202, _job(cid, "collection", "cancelling"))


class FakeHandler:
    """Test runs: executes package tests (inline archive or a registry version) — see runtime.py."""

    def __init__(self, contracts: Path, registry: FakeRegistry) -> None:
        self.app = ContractFake(contracts / "openapi" / "handler.v1.yaml", "handler")
        self.registry = registry
        self.jobs: dict[str, dict[str, Any]] = {}
        self.fail_params: list[dict[str, Any]] = []
        self.app.on("startTestRun")(self.test_run)
        self.app.on("getJob")(self.get_job)

    def test_run(self, req: FakeRequest) -> Reply:
        b = req.json
        ref = b["handler"]
        if "package_archive" in b:
            files = unzip(base64.b64decode(b["package_archive"]["data"]))
        else:
            entry = self.registry.versions.get(ref["package_id"], {}).get(ref["version"])
            if entry is None:
                return problem(404, "not_found")
            files = unzip(entry["archive"])
        params = b.get("params")
        fail = params is not None and any(
            all(params.get(k) == v for k, v in f.items()) for f in self.fail_params
        )
        cases = run_package_tests(
            files, b.get("tests", "all"), b.get("extra_cases") or [], params, fail_all=fail
        )
        report = {
            "package": {"package_id": ref["package_id"], "version": ref["version"]},
            "passed": sum(1 for c in cases if c["passed"]),
            "failed": sum(1 for c in cases if not c["passed"]),
            "cases": cases,
            "started_at": NOW,
            "finished_at": NOW,
        }
        jid = f"job_tr{len(self.jobs) + 1:05d}"
        self.jobs[jid] = _job(jid, "test_run", "succeeded", report)
        return Reply(202, _job(jid, "test_run", "queued"), {"Location": f"/v1/jobs/{jid}"})

    def get_job(self, req: FakeRequest) -> Reply:
        job = self.jobs.get(req.path_params["job_id"])
        return Reply(200, job) if job else problem(404, "not_found")


class FakeOrchestrator:
    def __init__(self, contracts: Path, registry: FakeRegistry) -> None:
        self.app = ContractFake(contracts / "openapi" / "orchestrator.v1.yaml", "orchestrator")
        self.registry = registry
        self.sources: dict[str, dict[str, Any]] = {}
        self.tasks: dict[str, dict[str, Any]] = {}
        self.activations: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self.groups: dict[str, dict[str, Any]] = {}
        self.refuse_auto: set[tuple[str, str]] = set()
        a = self.app
        a.on("createSource")(self.create_source)
        a.on("getSource")(self.get_source)
        a.on("createTask")(self.create_task)
        a.on("getTask")(self.get_task)
        a.on("listTasks")(self.list_tasks)
        a.on("activateStageVersion")(self.activate)
        a.on("listStageActivations")(self.list_activations)
        a.on("updateProblemGroup")(self.update_group)

    def stage(self, task_id: str, stage_id: str) -> dict[str, Any]:
        return next(s for s in self.tasks[task_id]["stages"] if s["stage_id"] == stage_id)

    def create_source(self, req: FakeRequest) -> Reply:
        if req.json["source_id"] in self.sources:
            return problem(409, "conflict")
        self.sources[req.json["source_id"]] = {**req.json, "created_at": NOW, "updated_at": NOW}
        return Reply(
            201, self.sources[req.json["source_id"]], {"Location": f"/v1/sources/{req.json['source_id']}"}
        )

    def get_source(self, req: FakeRequest) -> Reply:
        s = self.sources.get(req.path_params["source_id"])
        return Reply(200, s) if s else problem(404, "not_found")

    def create_task(self, req: FakeRequest) -> Reply:
        if req.json["task_id"] in self.tasks:
            return problem(409, "conflict")
        self.tasks[req.json["task_id"]] = json.loads(json.dumps(req.json))
        return Reply(201, self.tasks[req.json["task_id"]], {"Location": f"/v1/tasks/{req.json['task_id']}"})

    def get_task(self, req: FakeRequest) -> Reply:
        t = self.tasks.get(req.path_params["task_id"])
        return Reply(200, t) if t else problem(404, "not_found")

    def list_tasks(self, req: FakeRequest) -> Reply:
        pid = req.query.get("package_id")
        items = []
        for t in self.tasks.values():
            stages = [
                {"stage_id": s["stage_id"], "package": s["handler"]}
                for s in t["stages"]
                if s.get("handler", {}).get("package_id") == pid
            ]
            if pid and not stages:
                continue
            item = {
                "task_id": t["task_id"],
                "title": t["title"],
                "source_id": t["input"]["source_id"],
                "enabled": t.get("enabled", True),
            }
            if pid:
                item["package_stages"] = stages
            items.append(item)
        return Reply(200, {"items": items, "next_cursor": None})

    def activate(self, req: FakeRequest) -> Reply:
        task_id, stage_id = req.path_params["task_id"], req.path_params["stage_id"]
        if task_id not in self.tasks:
            return problem(404, "not_found")
        stage = self.stage(task_id, stage_id)
        b = req.json
        history = self.activations.setdefault((task_id, stage_id), [])
        current = dict(stage["handler"])
        if b["kind"] == "rollback":
            target = b.get("package") or (history[-1]["previous"] if history else None)
            if target is None:
                return problem(409, "conflict", "Nothing to roll back")
        else:
            target = b["package"]
            version = self.registry.versions.get(target["package_id"], {}).get(target["version"])
            package = self.registry.packages.get(target["package_id"], {})
            if version is None:
                return problem(404, "not_found")
            if b["kind"] == "auto_activate":
                source = self.sources.get(self.tasks[task_id]["input"]["source_id"], {})
                reason = None
                if (task_id, stage_id) in self.refuse_auto or (source.get("change_policy") or {}).get(
                    "llm_versions"
                ) != "auto_after_checks":
                    reason = "source_policy"
                elif not package.get("auto_changes_allowed"):
                    reason = "package_auto_changes_forbidden"
                elif version["test_status"] != "passed":
                    reason = "tests_not_passed"
                if reason:
                    return problem(
                        403,
                        "access_denied_by_policy",
                        "Automatic activation is not allowed",
                        retryable=False,
                        details={"reason": reason},
                    )
            elif version["status"] != "approved":
                return problem(409, "conflict", "Version is not approved")
        stage["handler"] = {k: target[k] for k in ("package_id", "version", "digest") if k in target}
        act = {
            "activation_id": f"act_{sum(len(h) for h in self.activations.values()) + 1:05d}",
            "task_id": task_id,
            "stage_id": stage_id,
            "package": stage["handler"],
            "previous": current,
            "kind": b["kind"],
            "reason": b.get("reason", ""),
            "activated_by": "assistant",
            "activated_at": NOW,
        }
        history.append(act)
        return Reply(200, act)

    def list_activations(self, req: FakeRequest) -> Reply:
        items = list(
            reversed(self.activations.get((req.path_params["task_id"], req.path_params["stage_id"]), []))
        )
        return Reply(200, {"items": items, "next_cursor": None})

    def update_group(self, req: FakeRequest) -> Reply:
        g = self.groups.get(req.path_params["group_id"])
        if g is None:
            return problem(404, "not_found")
        g.update(req.json)
        return Reply(200, g)


class FakeStorage:
    def __init__(self, contracts: Path) -> None:
        self.app = ContractFake(contracts / "openapi" / "storage.v1.yaml", "storage")
        self.objects: dict[str, tuple[dict[str, Any] | None, bytes, str]] = {}
        self.app.on("getObject")(self.get_object)
        self.app.on("getObjectContent")(self.get_content)

    def put(self, object_id: str, mat: dict[str, Any]) -> None:
        """RAW stored as the original HTML file (files adapter): Material with a ``file://`` blob reference."""
        data = mat["content"]["data"].encode()
        stored = {
            **mat,
            "content": {
                "kind": "blob",
                "uri": f"file:///var/lib/jane/raw/{object_id}.html",
                "media_type": "text/html",
                "size_bytes": len(data),
                "sha256": mat["revision"]["content_sha256"],
                "store": "persistent",
                "expires_at": None,
            },
        }
        self.put_object(object_id, stored, data, "text/html")

    def put_object(
        self, object_id: str, material: dict[str, Any] | None, data: bytes, media_type: str
    ) -> None:
        """Any ``getObject`` answer the contract allows: ``material`` (or none) and the stored object's bytes."""
        self.objects[object_id] = (material, data, media_type)

    def get_object(self, req: FakeRequest) -> Reply:
        obj = self.objects.get(req.path_params["object_id"])
        if obj is None:
            return problem(404, "not_found")
        material, data, media_type = obj
        body: dict[str, Any] = {
            "object": {
                "object_id": req.path_params["object_id"],
                "adapter": "filesystem",
                "connection_id": req.query["connection_id"],
                "media_type": media_type,
                "size_bytes": len(data),
            },
            "stored_at": NOW,
        }
        if material is not None:
            body["material"] = material
        return Reply(200, body)

    def get_content(self, req: FakeRequest) -> Reply:
        obj = self.objects.get(req.path_params["object_id"])
        if obj is None:
            return problem(404, "not_found")
        _, data, media_type = obj
        return Reply(200, raw=data, media_type=media_type)


_ = Registry  # referencing is used through OpenAPISpec.registry
