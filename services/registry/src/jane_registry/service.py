"""Domain logic of the registry (registry.v1): packages, immutable versions, statuses, test reports,
forks, diff, upstream status and explicit upstream ports. HTTP-agnostic; :mod:`jane_registry.app` maps
it to the API.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import logging
from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from jane_kit.errors import (
    Conflict,
    FieldError,
    Forbidden,
    JaneError,
    LimitExceeded,
    NotFound,
    UpstreamUnavailable,
    ValidationFailed,
)

from .archive import (
    MANIFEST_NAME,
    ArchiveError,
    ArchiveLimits,
    canonical_archive,
    check_package_path,
    digest_of,
    manifest_bytes,
    read_archive,
)
from .auth import Principal
from .blobs import BlobStore
from .diffing import diff_files, diff_manifest
from .merge import merge_packages
from .profiles import ProfileSource, check_dependencies
from .secrets import scan_files
from .semver import SemVer, max_version
from .settings import ServiceLimits
from .store import (
    AlreadyExists,
    LimitReached,
    MetadataStore,
    PackageFilter,
    PackageRecord,
    RevisionMismatch,
    StatusMismatch,
    VersionExists,
    VersionRecord,
    iso,
    now,
    pick_latest,
)
from .validation import Issue, PackageValidator

__all__ = ["STATUS_TRANSITIONS", "PortPlan", "RegistryService", "package_wire", "version_wire"]

log = logging.getLogger(__name__)

STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"approved", "rejected", "deprecated", "yanked"}),
    "approved": frozenset({"deprecated", "yanked"}),
    "deprecated": frozenset({"approved", "yanked"}),
    "rejected": frozenset(),
    "yanked": frozenset(),
}
PARENT_PREFIX = "parent:"


def version_exists(version: str) -> JaneError:
    return JaneError(f"version {version} already exists; versions are immutable", code="version_exists")


def _issues_to_errors(issues: list[Issue]) -> list[FieldError]:
    return [FieldError(pointer=i.pointer, code=i.code, message=i.message) for i in issues]


def package_wire(pkg: PackageRecord, forks_count: int | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "package_id": pkg.package_id,
        "kind": pkg.kind,
        "title": pkg.title,
        "latest_version": pkg.latest_version,
        "auto_changes_allowed": pkg.auto_changes_allowed,
        "deprecated": pkg.deprecated,
        "created_at": iso(pkg.created_at),
        "updated_at": iso(pkg.updated_at),
    }
    if pkg.description is not None:
        out["description"] = pkg.description
    if pkg.fork_of:
        out["fork_of"] = dict(pkg.fork_of)
    if forks_count is not None:
        out["forks_count"] = forks_count
    if pkg.owner:
        out["owner"] = pkg.owner
    if pkg.labels:
        out["labels"] = dict(pkg.labels)
    return out


def package_etag(pkg: PackageRecord) -> str:
    return f'"r{pkg.revision}"'


def version_wire(v: VersionRecord, *, full: bool = True) -> dict[str, Any]:
    out: dict[str, Any] = {
        "package_id": v.package_id,
        "version": v.version,
        "digest": v.digest,
        "status": v.status,
        "test_status": v.test_status,
        "size_bytes": v.size_bytes,
        "created_at": iso(v.created_at),
        "created_by": v.created_by,
    }
    if v.published_by:
        out["published_by"] = v.published_by
    if full:
        out["manifest"] = v.manifest
        out["files"] = v.files
        out["status_history"] = v.status_history
        out["test_reports"] = v.test_reports
    return out


@dataclass(frozen=True)
class PortPlan:
    fork: PackageRecord
    parent_id: str
    parent_version: str
    base_version: str
    merge_base: str
    new_version: str
    requested_by: str


class ArchiveCache:
    """LRU of archive bytes by digest, bounded by ``packages.archive_cache_bytes``."""

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        self._items: OrderedDict[str, bytes] = OrderedDict()
        self._size = 0

    def get(self, digest: str) -> bytes | None:
        data = self._items.get(digest)
        if data is not None:
            self._items.move_to_end(digest)
        return data

    def put(self, digest: str, data: bytes) -> None:
        if len(data) > self.max_bytes or digest in self._items:
            return
        self._items[digest] = data
        self._size += len(data)
        while self._size > self.max_bytes:
            _, old = self._items.popitem(last=False)
            self._size -= len(old)


class RegistryService:
    def __init__(
        self,
        store: MetadataStore,
        blobs: BlobStore,
        validator: PackageValidator,
        profiles: ProfileSource,
        limits: ServiceLimits,
    ) -> None:
        self.store = store
        self.blobs = blobs
        self.validator = validator
        self.profiles = profiles
        self.limits = limits
        self.cache = ArchiveCache(limits.packages.archive_cache_bytes)

    @property
    def archive_limits(self) -> ArchiveLimits:
        p = self.limits.packages
        return ArchiveLimits(p.max_archive_bytes, p.max_unpacked_bytes, p.max_files)

    # ------------------------------------------------------------------ packages
    async def package(self, package_id: str) -> PackageRecord:
        pkg = await self.store.get_package(package_id)
        if pkg is None:
            raise NotFound(f"package {package_id} not found")
        return pkg

    async def create_package(self, body: Mapping[str, Any], principal: Principal) -> PackageRecord:
        t = now()
        pkg = PackageRecord(
            package_id=str(body["package_id"]),
            kind=str(body["kind"]),
            title=str(body["title"]),
            description=body.get("description"),
            auto_changes_allowed=bool(body.get("auto_changes_allowed", True)),
            labels=dict(body.get("labels") or {}),
            owner=principal.name if principal.name != "anonymous" else None,
            created_at=t,
            updated_at=t,
        )
        try:
            return await self.store.create_package(pkg)
        except AlreadyExists as exc:
            raise Conflict(f"package {pkg.package_id} already exists") from exc

    async def update_package(
        self, package_id: str, changes: dict[str, Any], if_match: str | None
    ) -> PackageRecord:
        pkg = await self.package(package_id)
        expected: int | None = None
        if if_match is not None:
            tags = [t.strip().removeprefix("W/") for t in if_match.split(",")]
            if "*" not in tags:
                if package_etag(pkg) not in tags:
                    raise JaneError("If-Match does not match the current ETag", code="precondition_failed")
                expected = pkg.revision
        try:
            return await self.store.update_package(package_id, changes, expected)
        except RevisionMismatch as exc:
            raise JaneError("the package changed concurrently", code="precondition_failed") from exc

    # ------------------------------------------------------------------ archives
    async def archive(self, v: VersionRecord) -> bytes:
        cached = self.cache.get(v.digest)
        if cached is not None:
            return cached
        data = await self.blobs.get(v.digest)
        if data is None:
            raise UpstreamUnavailable(f"archive {v.digest} is missing in the blob store")
        self.cache.put(v.digest, data)
        return data

    async def files_of(self, v: VersionRecord) -> dict[str, bytes]:
        return read_archive(await self.archive(v), self.archive_limits)

    async def version(self, package_id: str, version: str) -> VersionRecord:
        v = await self.store.get_version(package_id, version)
        if v is None:
            await self.package(package_id)
            raise NotFound(f"version {package_id}@{version} not found")
        return v

    # ------------------------------------------------------------------ publication
    @staticmethod
    def files_from_json(body: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, bytes]]:
        files: dict[str, bytes] = {}
        errors: list[FieldError] = []
        for path, entry in (body.get("files") or {}).items():
            pointer = "/files/" + path.replace("~", "~0").replace("/", "~1")
            try:
                check_package_path(path)
            except ArchiveError as exc:
                errors.append(FieldError(pointer=pointer, code="invalid_path", message=str(exc)))
                continue
            if path == MANIFEST_NAME:
                errors.append(
                    FieldError(
                        pointer=pointer,
                        code="manifest_in_files",
                        message="jane-package.json is formed from manifest",
                    )
                )
                continue
            try:
                if entry["encoding"] == "base64":
                    files[path] = base64.b64decode(entry["data"], validate=True)
                else:
                    files[path] = str(entry["data"]).encode("utf-8")
            except (binascii.Error, ValueError) as exc:
                errors.append(FieldError(pointer=pointer, code="invalid_encoding", message=str(exc)))
        if errors:
            raise ValidationFailed("invalid files", errors=errors)
        return dict(body["manifest"]), files

    def files_from_zip(self, data: bytes) -> tuple[Any, dict[str, bytes]]:
        try:
            files = read_archive(data, self.archive_limits)
        except ArchiveError as exc:
            if exc.limit:
                raise LimitExceeded(str(exc), details={"path": exc.limit}) from exc
            pointer = "/files/" + exc.path.replace("~", "~0").replace("/", "~1") if exc.path else None
            raise ValidationFailed(str(exc), errors=[FieldError(pointer=pointer, message=str(exc))]) from exc
        if MANIFEST_NAME not in files:
            raise ValidationFailed(
                "archive has no jane-package.json at its root",
                errors=[
                    FieldError(pointer="/files/jane-package.json", code="missing_file", message="required")
                ],
            )
        try:
            manifest = json.loads(files[MANIFEST_NAME].decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValidationFailed(
                f"jane-package.json is not valid JSON: {exc}",
                errors=[
                    FieldError(pointer="/files/jane-package.json", code="invalid_json", message=str(exc))
                ],
            ) from exc
        return manifest, files

    def _check_sizes(self, files: Mapping[str, bytes]) -> None:
        p = self.limits.packages
        if len(files) > p.max_files:
            raise LimitExceeded(
                f"package has {len(files)} files, limit {p.max_files}",
                details={"path": "packages.max_files", "limit": p.max_files},
            )
        total = sum(len(b) for b in files.values())
        if total > p.max_unpacked_bytes:
            raise LimitExceeded(
                f"package files are {total} bytes, limit {p.max_unpacked_bytes}",
                details={"path": "packages.max_unpacked_bytes", "limit": p.max_unpacked_bytes},
            )

    async def _check_dependencies(self, pkg: PackageRecord, manifest: Mapping[str, Any]) -> None:
        deps = manifest.get("dependencies") or {}
        errors: list[FieldError] = []
        profile_name = deps.get("runtime_profile")
        python = list(deps.get("python") or [])
        if python and not profile_name:
            errors.append(
                FieldError(
                    pointer="/manifest/dependencies/runtime_profile",
                    message="dependencies.python requires dependencies.runtime_profile",
                )
            )
        if profile_name:
            profiles = await self.profiles.profiles()
            profile = profiles.get(profile_name)
            if profile is None:
                if self.profiles.errors and not profiles:
                    raise UpstreamUnavailable(
                        "runtime profiles cannot be loaded", details={"sources": self.profiles.errors}
                    )
                known = sorted(profiles) or "none configured (JANE_REGISTRY_RUNTIME_PROFILES)"
                errors.append(
                    FieldError(
                        pointer="/manifest/dependencies/runtime_profile",
                        message=f"unknown runtime profile {profile_name}; known: {known}",
                    )
                )
            else:
                for problem in check_dependencies(profile, python):
                    errors.append(
                        FieldError(
                            pointer=f"/manifest/dependencies/python/{problem.index}", message=problem.message
                        )
                    )
        if errors:
            raise JaneError("dependency not allowed", code="dependency_not_allowed", errors=errors)
        ref_errors: list[FieldError] = []
        for i, ref in enumerate(deps.get("packages") or []):
            pointer = f"/manifest/dependencies/packages/{i}"
            if ref["package_id"] == pkg.package_id:
                ref_errors.append(FieldError(pointer=pointer, message="a package cannot depend on itself"))
                continue
            dep = await self.store.get_version(ref["package_id"], ref["version"])
            if dep is None:
                ref_errors.append(
                    FieldError(
                        pointer=pointer,
                        message=f"{ref['package_id']}@{ref['version']} is not in the registry",
                    )
                )
            elif ref.get("digest") and ref["digest"] != dep.digest:
                ref_errors.append(FieldError(pointer=pointer, message=f"digest does not match {dep.digest}"))
        if ref_errors:
            raise ValidationFailed("package dependencies are not satisfied", errors=ref_errors)

    async def _ported_parent_for(self, pkg: PackageRecord, manifest: Mapping[str, Any]) -> str | None:
        """Parent version whose changes a new (non-port) version of a fork contains."""
        if not pkg.fork_of:
            return None
        based = (manifest.get("provenance") or {}).get("based_on") or {}
        candidate: VersionRecord | None = None
        if based.get("package_id") == pkg.package_id:
            candidate = await self.store.get_version(pkg.package_id, str(based.get("version")))
        if candidate is None and pkg.latest_version:
            candidate = await self.store.get_version(pkg.package_id, pkg.latest_version)
        if candidate is not None and candidate.ported_parent_version:
            return candidate.ported_parent_version
        return str(pkg.fork_of["version"])

    async def publish(
        self,
        pkg: PackageRecord,
        manifest: Any,
        files: dict[str, bytes],
        principal: Principal,
        *,
        from_zip: bool,
        ported_parent_version: str | None = None,
        created_package: bool = False,
    ) -> VersionRecord:
        """Validate and store a new immutable version (status ``draft``)."""
        issues = self.validator.manifest_issues(manifest)
        if issues:
            raise ValidationFailed("manifest is not valid", errors=_issues_to_errors(issues))
        assert isinstance(manifest, dict)
        if not from_zip:
            files = {**files, MANIFEST_NAME: manifest_bytes(manifest)}
        self._check_sizes(files)
        semantic: list[Issue] = []
        if manifest["package_id"] != pkg.package_id:
            semantic.append(
                Issue("/manifest/package_id", f"must be {pkg.package_id!r} (the package being published)")
            )
        if manifest["kind"] != pkg.kind:
            semantic.append(Issue("/manifest/kind", f"must be {pkg.kind!r} (kind of the package)"))
        if pkg.fork_of and manifest.get("fork_of") != pkg.fork_of:
            semantic.append(
                Issue(
                    "/manifest/fork_of",
                    f"a fork carries fork_of set by the registry unchanged: {pkg.fork_of}",
                )
            )
        if not pkg.fork_of and "fork_of" in manifest:
            semantic.append(Issue("/manifest/fork_of", "fork_of is set only by the registry when forking"))
        semantic.extend(self.validator.package_issues(manifest, files, "/manifest"))
        if semantic:
            raise ValidationFailed("package is not valid", errors=_issues_to_errors(semantic))
        created_by = str(manifest["provenance"]["created_by"])
        if created_by == "llm" and not pkg.auto_changes_allowed:
            raise Forbidden(
                "automatic changes are forbidden for this package (auto_changes_allowed=false)",
                title="Automatic changes are forbidden for this package",
            )
        version = str(manifest["version"])
        if not created_package and await self.store.get_version(pkg.package_id, version) is not None:
            raise version_exists(version)
        findings = scan_files(files, self.limits.secrets)
        if findings:
            log.warning(
                "secret detected in package",
                extra={
                    "package_id": pkg.package_id,
                    "version": version,
                    "findings": [(f.path, f.code, f.line) for f in findings],
                },
            )
            raise JaneError(
                "secret detected in package",
                code="secret_detected",
                title="Secret detected in package",
                errors=[FieldError(pointer=f.pointer, code=f.code, message=f.message) for f in findings],
            )
        await self._check_dependencies(pkg, manifest)

        archive = canonical_archive(files)
        if len(archive) > self.limits.packages.max_archive_bytes:
            raise LimitExceeded(
                f"archive is {len(archive)} bytes, limit {self.limits.packages.max_archive_bytes}",
                details={
                    "path": "packages.max_archive_bytes",
                    "limit": self.limits.packages.max_archive_bytes,
                },
            )
        digest = digest_of(archive)
        await self.blobs.put(digest, archive)
        self.cache.put(digest, archive)
        t = now()
        if ported_parent_version is None:
            ported_parent_version = await self._ported_parent_for(pkg, manifest)
        record = VersionRecord(
            package_id=pkg.package_id,
            version=version,
            digest=digest,
            status="draft",
            test_status="unknown",
            manifest=manifest,
            files=[
                {"path": p, "size_bytes": len(files[p]), "sha256": hashlib.sha256(files[p]).hexdigest()}
                for p in sorted(files)
            ],
            size_bytes=len(archive),
            created_at=t,
            created_by=created_by,
            published_by=principal.name,
            ported_parent_version=ported_parent_version,
            status_history=[{"status": "draft", "at": iso(t), "by": principal.name}],
        )
        try:
            stored = await self.store.insert_version(record, self.limits.packages.max_versions_per_package)
        except VersionExists as exc:
            raise version_exists(version) from exc
        except LimitReached as exc:
            raise LimitExceeded(
                f"package has {exc.count} versions, limit {self.limits.packages.max_versions_per_package}",
                details={
                    "path": "packages.max_versions_per_package",
                    "limit": self.limits.packages.max_versions_per_package,
                },
            ) from exc
        log.info(
            "version published",
            extra={
                "package_id": pkg.package_id,
                "version": version,
                "digest": digest,
                "created_by": created_by,
            },
        )
        return stored

    # ------------------------------------------------------------------ statuses and tests
    async def set_status(
        self, package_id: str, version: str, status: str, reason: str | None, principal: Principal
    ) -> VersionRecord:
        v = await self.version(package_id, version)
        if status not in STATUS_TRANSITIONS[v.status]:
            raise Conflict(f"status {v.status} -> {status} is not allowed", details={"current": v.status})
        entry: dict[str, Any] = {"status": status, "at": iso(now()), "by": principal.name}
        if reason:
            entry["reason"] = reason
        try:
            return await self.store.set_status(package_id, version, v.status, entry)
        except StatusMismatch as exc:
            raise Conflict(
                f"status changed concurrently to {exc.actual}", details={"current": exc.actual}
            ) from exc

    async def record_test_results(
        self, package_id: str, version: str, record: dict[str, Any]
    ) -> VersionRecord:
        v = await self.version(package_id, version)
        issues = self.validator.schemas.issues(
            "handler-result.schema.json", record.get("report"), "/report", fragment="/$defs/TestReport"
        )
        if issues:
            raise ValidationFailed("test report is not valid", errors=_issues_to_errors(issues))
        ref = record["report"]["package"]
        if ref["package_id"] != package_id or ref["version"] != version:
            raise ValidationFailed(
                "report.package does not match the version",
                errors=[FieldError(pointer="/report/package", message=f"must be {package_id}@{version}")],
            )
        if ref.get("digest") and ref["digest"] != v.digest:
            raise JaneError(
                f"report was made for {ref['digest']}, version has {v.digest}", code="digest_mismatch"
            )
        stored = dict(record)
        stored.setdefault("recorded_at", iso(now()))
        report = record["report"]
        test_status = "failed" if report["failed"] > 0 else ("passed" if report["passed"] > 0 else "unknown")
        return await self.store.add_test_report(package_id, version, stored, test_status)

    # ------------------------------------------------------------------ forks
    async def fork(
        self, parent_id: str, body: Mapping[str, Any], principal: Principal
    ) -> tuple[PackageRecord, VersionRecord]:
        parent = await self.package(parent_id)
        source = await self.version(parent_id, str(body["from_version"]))
        new_id = str(body["new_package_id"])
        if await self.store.get_package(new_id) is not None:
            raise Conflict(f"package {new_id} already exists")
        files = await self.files_of(source)
        manifest = json.loads(files.pop(MANIFEST_NAME).decode("utf-8"))
        fork_of = {"package_id": parent_id, "version": source.version, "digest": source.digest}
        original = manifest.get("provenance") or {}
        provenance: dict[str, Any] = {"created_by": original.get("created_by", "import")}
        if original.get("authors"):
            provenance["authors"] = original["authors"]
        provenance["based_on"] = dict(fork_of)
        provenance["change_summary"] = f"Fork of {parent_id}@{source.version}."
        manifest.update(
            package_id=new_id,
            version=str(body.get("initial_version") or source.version),
            fork_of=fork_of,
            provenance=provenance,
        )
        t = now()
        record = PackageRecord(
            package_id=new_id,
            kind=parent.kind,
            title=str(body.get("title") or parent.title),
            description=parent.description,
            auto_changes_allowed=bool(body.get("auto_changes_allowed", False)),
            fork_of=fork_of,
            owner=principal.name if principal.name != "anonymous" else None,
            labels=dict(parent.labels),
            created_at=t,
            updated_at=t,
        )
        # the fork is a human command: the copy is published even if the parent was LLM-made
        record_for_checks = PackageRecord(**{**record.__dict__, "auto_changes_allowed": True})
        try:
            created = await self.store.create_package(record)
        except AlreadyExists as exc:
            raise Conflict(f"package {new_id} already exists") from exc
        try:
            version = await self.publish(
                record_for_checks,
                manifest,
                files,
                principal,
                from_zip=False,
                ported_parent_version=source.version,
                created_package=True,
            )
        except BaseException:
            await self.store.delete_package_if_empty(new_id)
            raise
        created = await self.package(new_id)
        log.info("package forked", extra={"package_id": new_id, "fork_of": fork_of})
        return created, version

    async def _resolve(self, pkg: PackageRecord, ref: str) -> VersionRecord:
        if ref.startswith(PARENT_PREFIX):
            if not pkg.fork_of:
                raise ValidationFailed(
                    f"{pkg.package_id} is not a fork; 'parent:' references need a fork",
                    errors=[FieldError(parameter="from", message="not a fork")],
                )
            return await self.version(str(pkg.fork_of["package_id"]), ref.removeprefix(PARENT_PREFIX))
        return await self.version(pkg.package_id, ref)

    async def diff(
        self, package_id: str, from_ref: str | None, to_ref: str, context_lines: int
    ) -> dict[str, Any]:
        pkg = await self.package(package_id)
        to_v = await self._resolve(pkg, to_ref)
        if from_ref is None:
            older = [
                v for v, _ in await self.store.version_numbers(package_id) if SemVer(v) < SemVer(to_v.version)
            ]
            if older:
                from_v = await self.version(package_id, str(max_version(older)))
            elif pkg.fork_of:
                from_v = await self.version(str(pkg.fork_of["package_id"]), str(pkg.fork_of["version"]))
            else:
                raise ValidationFailed(
                    f"{to_v.version} is the first version; pass 'from'",
                    errors=[FieldError(parameter="from", message="required: no earlier version")],
                )
        else:
            from_v = await self._resolve(pkg, from_ref)
        old_files, new_files = await self.files_of(from_v), await self.files_of(to_v)
        n = max(0, min(context_lines, self.limits.diff.max_context_lines))
        return {
            "from": {"package_id": from_v.package_id, "version": from_v.version, "digest": from_v.digest},
            "to": {"package_id": to_v.package_id, "version": to_v.version, "digest": to_v.digest},
            "manifest_changes": diff_manifest(from_v.manifest, to_v.manifest),
            "files": diff_files(
                old_files,
                new_files,
                context_lines=n,
                max_file_bytes=self.limits.diff.max_diff_file_bytes,
                old_label=f"{from_v.package_id}@{from_v.version}",
                new_label=f"{to_v.package_id}@{to_v.version}",
            ),
        }

    # ------------------------------------------------------------------ upstream
    async def _fork_package(self, package_id: str) -> PackageRecord:
        pkg = await self.package(package_id)
        if not pkg.fork_of:
            raise Conflict(f"package {package_id} is not a fork", title="Package is not a fork")
        return pkg

    async def _last_ported(self, pkg: PackageRecord) -> str:
        assert pkg.fork_of
        versions = await self.store.list_versions(
            pkg.package_id, None, None, self.limits.packages.max_versions_per_package
        )
        ported = [str(pkg.fork_of["version"])] + [
            v.ported_parent_version for v in versions if v.ported_parent_version
        ]
        return str(max_version(ported))

    async def upstream(self, package_id: str) -> dict[str, Any]:
        pkg = await self._fork_package(package_id)
        assert pkg.fork_of
        parent_id = str(pkg.fork_of["package_id"])
        last = await self._last_ported(pkg)
        parent_versions = await self.store.version_numbers(parent_id)
        active = [v for v, status in parent_versions if status not in {"rejected", "yanked"}]
        newer = sorted((v for v in active if SemVer(v) > SemVer(last)), key=SemVer)
        return {
            "fork_of": dict(pkg.fork_of),
            "last_ported_version": last,
            "parent_latest_version": pick_latest(parent_versions) or last,
            "newer_parent_versions": newer,
        }

    async def plan_port(self, package_id: str, body: Mapping[str, Any], principal: Principal) -> PortPlan:
        pkg = await self._fork_package(package_id)
        assert pkg.fork_of
        parent_id = str(pkg.fork_of["package_id"])
        parent_version = str(body["parent_version"])
        await self.version(parent_id, parent_version)
        base_version = body.get("base_version") or pkg.latest_version
        if not base_version:
            raise Conflict(f"{package_id} has no active version to port into; pass base_version")
        base = await self.version(package_id, str(base_version))
        new_version = str(body["new_version"])
        if await self.store.get_version(package_id, new_version) is not None:
            raise version_exists(new_version)
        return PortPlan(
            fork=pkg,
            parent_id=parent_id,
            parent_version=parent_version,
            base_version=base.version,
            merge_base=base.ported_parent_version or str(pkg.fork_of["version"]),
            new_version=new_version,
            requested_by=principal.name,
        )

    async def port(self, plan: PortPlan, principal: Principal) -> VersionRecord:
        base_v = await self.version(plan.parent_id, plan.merge_base)
        theirs_v = await self.version(plan.parent_id, plan.parent_version)
        ours_v = await self.version(plan.fork.package_id, plan.base_version)
        result = merge_packages(
            await self.files_of(base_v),
            await self.files_of(ours_v),
            await self.files_of(theirs_v),
            max_merge_file_bytes=self.limits.diff.max_merge_file_bytes,
        )
        if result.conflicts:
            raise JaneError(
                f"{len(result.conflicts)} conflict(s) while porting {plan.parent_id}@{plan.parent_version}",
                code="upstream_conflict",
                title="Upstream changes conflict with the fork",
                details={
                    "conflicts": [c.wire() for c in result.conflicts],
                    "merge_base": plan.merge_base,
                    "parent_version": plan.parent_version,
                    "base_version": plan.base_version,
                },
            )
        manifest = dict(result.manifest)
        manifest["package_id"] = plan.fork.package_id
        manifest["version"] = plan.new_version
        manifest["fork_of"] = dict(plan.fork.fork_of or {})
        manifest["provenance"] = {
            "created_by": "human",
            "based_on": {
                "package_id": plan.fork.package_id,
                "version": ours_v.version,
                "digest": ours_v.digest,
            },
            "change_summary": (
                f"Ported changes of {plan.parent_id} {plan.merge_base} -> {plan.parent_version} "
                f"into {ours_v.version}."
            ),
            "upstream_port": {"parent_version": plan.parent_version, "requested_by": plan.requested_by},
        }
        fork = await self.package(plan.fork.package_id)
        return await self.publish(
            fork, manifest, result.files, principal, from_zip=False, ported_parent_version=plan.parent_version
        )

    async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
        return await self.store.list_packages(flt, after, limit)
