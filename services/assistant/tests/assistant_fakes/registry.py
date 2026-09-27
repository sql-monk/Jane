"""Stateful fake of the handler registry (``registry.v1``), just enough for the scenarios."""

from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

from .base import ContractFake, FakeRequest, Reply, problem

__all__ = ["FakeRegistry"]

NOW = "2026-09-27T12:00:00Z"


def _archive(manifest: dict[str, Any], files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    entries = {**files, "jane-package.json": json.dumps(manifest, sort_keys=True).encode()}
    with zipfile.ZipFile(buf, "w") as zf:
        for path in sorted(entries):
            zf.writestr(zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0)), entries[path])
    return buf.getvalue()


class FakeRegistry:
    def __init__(self, contracts: Path) -> None:
        self.app = ContractFake(contracts / "openapi" / "registry.v1.yaml", "registry")
        self.packages: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, dict[str, Any]]] = {}
        a = self.app
        a.on("listPackages")(self.list_packages)
        a.on("createPackage")(self.create_package)
        a.on("getPackage")(self.get_package)
        a.on("getPackageVersion")(self.get_version)
        a.on("downloadPackageArchive")(self.archive)
        a.on("publishPackageVersion")(self.publish)
        a.on("setPackageVersionStatus")(self.set_status)
        a.on("recordTestResults")(self.record_tests)
        a.on("forkPackage")(self.fork)

    # ------------------------------------------------------------------ seeding (test setup)
    def seed(
        self,
        manifest: dict[str, Any],
        files: dict[str, bytes],
        *,
        auto_changes_allowed: bool = True,
        status: str = "approved",
    ) -> dict[str, Any]:
        pid = manifest["package_id"]
        self.packages.setdefault(
            pid,
            {
                "package_id": pid,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "latest_version": None,
                "auto_changes_allowed": auto_changes_allowed,
                "deprecated": False,
                "created_at": NOW,
                "updated_at": NOW,
            },
        )
        return self._store(manifest, files, status=status, test_status="passed")

    def _store(
        self,
        manifest: dict[str, Any],
        files: dict[str, bytes],
        status: str = "draft",
        test_status: str = "unknown",
    ) -> dict[str, Any]:
        pid, ver = manifest["package_id"], manifest["version"]
        data = _archive(manifest, files)
        entry = {
            "manifest": copy.deepcopy(manifest),
            "files": dict(files),
            "archive": data,
            "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
            "status": status,
            "test_status": test_status,
            "test_reports": [],
            "created_at": NOW,
            "created_by": manifest.get("provenance", {}).get("created_by", "human"),
            "status_history": [
                {"status": status, "at": NOW, "by": "seed" if status != "draft" else "assistant"}
            ],
        }
        self.versions.setdefault(pid, {})[ver] = entry
        self.packages[pid]["latest_version"] = ver
        return entry

    def _pv(self, pid: str, ver: str) -> dict[str, Any]:
        e = self.versions[pid][ver]
        return {
            "package_id": pid,
            "version": ver,
            "digest": e["digest"],
            "status": e["status"],
            "test_status": e["test_status"],
            "manifest": e["manifest"],
            "created_at": e["created_at"],
            "created_by": e["created_by"],
            "status_history": e["status_history"],
            "test_reports": e["test_reports"],
        }

    # ------------------------------------------------------------------ operations
    def list_packages(self, req: FakeRequest) -> Reply:
        q = req.query
        items = []
        for pid, pkg in sorted(self.packages.items()):
            latest = self.versions.get(pid, {}).get(pkg["latest_version"] or "", {}).get("manifest") or {}
            if q.get("kind") and pkg["kind"] != q["kind"]:
                continue
            if q.get("entity_type") and q["entity_type"] not in [
                e["entity_type"] for e in (latest.get("output") or {}).get("entities") or []
            ]:
                continue
            if q.get("domain") and q["domain"] not in (
                (latest.get("bindings_hint") or {}).get("domains") or []
            ):
                continue
            items.append(pkg)
        return Reply(200, {"items": items, "next_cursor": None})

    def create_package(self, req: FakeRequest) -> Reply:
        b = req.json
        if b["package_id"] in self.packages:
            return problem(409, "conflict", "Package exists")
        self.packages[b["package_id"]] = {
            "package_id": b["package_id"],
            "kind": b["kind"],
            "title": b["title"],
            "latest_version": None,
            "auto_changes_allowed": b.get("auto_changes_allowed", True),
            "deprecated": False,
            "created_at": NOW,
            "updated_at": NOW,
        }
        return Reply(201, self.packages[b["package_id"]], {"Location": f"/v1/packages/{b['package_id']}"})

    def get_package(self, req: FakeRequest) -> Reply:
        pkg = self.packages.get(req.path_params["package_id"])
        return Reply(200, pkg) if pkg else problem(404, "not_found")

    def get_version(self, req: FakeRequest) -> Reply:
        pid, ver = req.path_params["package_id"], req.path_params["version"]
        if ver not in self.versions.get(pid, {}):
            return problem(404, "not_found")
        return Reply(200, self._pv(pid, ver))

    def archive(self, req: FakeRequest) -> Reply:
        pid, ver = req.path_params["package_id"], req.path_params["version"]
        e = self.versions.get(pid, {}).get(ver)
        if e is None:
            return problem(404, "not_found")
        return Reply(
            200, raw=e["archive"], media_type="application/zip", headers={"ETag": f'"{e["digest"]}"'}
        )

    def publish(self, req: FakeRequest) -> Reply:
        pid = req.path_params["package_id"]
        manifest, files = req.json["manifest"], req.json["files"]
        pkg = self.packages.get(pid)
        if pkg is None:
            return problem(404, "not_found")
        if manifest["package_id"] != pid:
            return problem(422, "validation_failed", detail="manifest package_id differs from path")
        if manifest["version"] in self.versions.get(pid, {}):
            return problem(409, "version_exists", "Version already exists")
        if not pkg["auto_changes_allowed"] and manifest["provenance"]["created_by"] == "llm":
            return problem(403, "forbidden", "Automatic changes are forbidden for this package")
        raw = {
            p: (base64.b64decode(f["data"]) if f["encoding"] == "base64" else f["data"].encode())
            for p, f in files.items()
        }
        referenced = [
            t["input"].get("material") or t["input"].get("file") for t in manifest.get("tests") or []
        ]
        referenced += [t["expected"] for t in manifest.get("tests") or [] if t.get("expected")]
        missing = [r for r in referenced if r and r not in raw]
        if missing:
            return problem(422, "validation_failed", detail=f"missing files {missing}")
        self._store(manifest, raw)
        return Reply(
            201,
            self._pv(pid, manifest["version"]),
            {"Location": f"/v1/packages/{pid}/versions/{manifest['version']}"},
        )

    def set_status(self, req: FakeRequest) -> Reply:
        pid, ver = req.path_params["package_id"], req.path_params["version"]
        e = self.versions.get(pid, {}).get(ver)
        if e is None:
            return problem(404, "not_found")
        e["status"] = req.json["status"]
        e["status_history"].append(
            {"status": req.json["status"], "at": NOW, "by": "assistant", "reason": req.json.get("reason", "")}
        )
        return Reply(200, self._pv(pid, ver))

    def record_tests(self, req: FakeRequest) -> Reply:
        pid, ver = req.path_params["package_id"], req.path_params["version"]
        e = self.versions.get(pid, {}).get(ver)
        if e is None:
            return problem(404, "not_found")
        e["test_reports"].append({**req.json, "recorded_at": NOW})
        failed = any(r["report"]["failed"] for r in e["test_reports"])
        e["test_status"] = "failed" if failed else "passed"
        return Reply(200, self._pv(pid, ver))

    def fork(self, req: FakeRequest) -> Reply:
        pid = req.path_params["package_id"]
        b = req.json
        parent = self.versions.get(pid, {}).get(b["from_version"])
        if parent is None:
            return problem(404, "not_found")
        new_id = b["new_package_id"]
        if new_id in self.packages:
            return problem(409, "conflict", "Package exists")
        fork_of = {"package_id": pid, "version": b["from_version"], "digest": parent["digest"]}
        self.packages[new_id] = {
            "package_id": new_id,
            "kind": self.packages[pid]["kind"],
            "title": b.get("title", new_id),
            "latest_version": None,
            "auto_changes_allowed": b.get("auto_changes_allowed", False),
            "deprecated": False,
            "fork_of": fork_of,
            "created_at": NOW,
            "updated_at": NOW,
        }
        manifest = copy.deepcopy(parent["manifest"])
        manifest.update(
            {"package_id": new_id, "version": b.get("initial_version", b["from_version"]), "fork_of": fork_of}
        )
        self._store(manifest, parent["files"], status="draft")
        return Reply(201, self.packages[new_id], {"Location": f"/v1/packages/{new_id}"})
