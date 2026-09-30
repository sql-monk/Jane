"""Metadata store of the registry: records, the store protocol and the in-memory implementation.

The PostgreSQL implementation (:mod:`jane_registry.postgres`) is the production store (ADR-0002 §1).
:class:`MemoryStore` keeps the same semantics in one process (``JANE_REGISTRY_DB=memory``): local
experiments and fast tests; it loses everything on restart and does not support several instances.
"""

from __future__ import annotations

import asyncio
import copy
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Any, Protocol

from .semver import SemVer

__all__ = [
    "INACTIVE_FOR_LATEST",
    "AlreadyExists",
    "LimitReached",
    "MemoryStore",
    "MetadataStore",
    "PackageFilter",
    "PackageRecord",
    "RevisionMismatch",
    "StatusMismatch",
    "VersionExists",
    "VersionRecord",
    "iso",
    "now",
    "pick_latest",
]

INACTIVE_FOR_LATEST = frozenset({"rejected", "yanked"})


def now() -> datetime:
    t = datetime.now(UTC)
    return t.replace(microsecond=t.microsecond // 1000 * 1000)


def iso(t: datetime) -> str:
    """RFC 3339 UTC with ``Z`` and milliseconds, as the contracts require."""
    return t.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class AlreadyExists(Exception):
    pass


class VersionExists(Exception):
    pass


class RevisionMismatch(Exception):
    pass


class StatusMismatch(Exception):
    def __init__(self, actual: str) -> None:
        super().__init__(actual)
        self.actual = actual


@dataclass
class PackageRecord:
    package_id: str
    kind: str
    title: str
    auto_changes_allowed: bool
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    deprecated: bool = False
    fork_of: dict[str, str] | None = None
    owner: str | None = None
    labels: dict[str, str] = field(default_factory=dict)
    revision: int = 1
    latest_version: str | None = None
    tags: list[str] = field(default_factory=list)
    entity_types: list[str] = field(default_factory=list)
    media_types: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)


@dataclass
class VersionRecord:
    package_id: str
    version: str
    digest: str
    status: str
    test_status: str
    manifest: dict[str, Any]
    files: list[dict[str, Any]]
    size_bytes: int
    created_at: datetime
    created_by: str
    published_by: str | None = None
    ported_parent_version: str | None = None
    seq: int = 0
    status_history: list[dict[str, Any]] = field(default_factory=list)
    test_reports: list[dict[str, Any]] = field(default_factory=list)

    # search fields derived from the manifest (copied to the package when this is the latest version)
    @property
    def search_fields(self) -> dict[str, list[str]]:
        m = self.manifest
        entities = (m.get("output") or {}).get("entities") or []
        hint = m.get("bindings_hint") or {}
        return {
            "tags": list(m.get("tags") or []),
            "entity_types": sorted({str(e.get("entity_type")) for e in entities if e.get("entity_type")}),
            "media_types": list((m.get("input") or {}).get("media_types") or []),
            "domains": [d.lower() for d in hint.get("domains") or []],
        }


@dataclass(frozen=True)
class PackageFilter:
    kind: str | None = None
    q: str | None = None
    tag: str | None = None
    entity_type: str | None = None
    media_type: str | None = None
    domain: str | None = None
    fork_of: str | None = None


def pick_latest(versions: Sequence[tuple[str, str]]) -> str | None:
    """Highest SemVer among versions whose status is not rejected/yanked."""
    active = [v for v, status in versions if status not in INACTIVE_FOR_LATEST]
    return max(active, key=SemVer) if active else None


def media_matches(wanted: str, offered: Sequence[str]) -> bool:
    wanted = wanted.lower()
    major = wanted.split("/", 1)[0]
    return any(o.lower() in {wanted, f"{major}/*", "*/*"} for o in offered)


def domain_matches(wanted: str, hints: Sequence[str]) -> bool:
    wanted = wanted.lower().rstrip(".")
    return any(wanted == h or wanted.endswith("." + h) for h in hints)


def matches(pkg: PackageRecord, f: PackageFilter) -> bool:
    if f.kind and pkg.kind != f.kind:
        return False
    if f.fork_of and (pkg.fork_of or {}).get("package_id") != f.fork_of:
        return False
    if f.tag and f.tag not in pkg.tags:
        return False
    if f.entity_type and f.entity_type not in pkg.entity_types:
        return False
    if f.media_type and not media_matches(f.media_type, pkg.media_types):
        return False
    if f.domain and not domain_matches(f.domain, pkg.domains):
        return False
    if f.q:
        hay = " ".join(
            [pkg.package_id, pkg.title, pkg.description or "", *pkg.tags, *pkg.entity_types]
        ).lower()
        if f.q.lower() not in hay:
            return False
    return True


class MetadataStore(Protocol):
    name: str

    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def check(self) -> bool: ...

    async def create_package(self, pkg: PackageRecord) -> PackageRecord: ...
    async def get_package(self, package_id: str) -> PackageRecord | None: ...
    async def update_package(
        self, package_id: str, changes: dict[str, Any], expected_revision: int | None
    ) -> PackageRecord: ...
    async def list_packages(
        self, flt: PackageFilter, after: str | None, limit: int
    ) -> list[PackageRecord]: ...
    async def count_forks(self, package_id: str) -> int: ...
    async def delete_package_if_empty(self, package_id: str) -> None: ...

    async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord: ...
    async def get_version(self, package_id: str, version: str) -> VersionRecord | None: ...
    async def list_versions(
        self, package_id: str, status: str | None, before_seq: int | None, limit: int
    ) -> list[VersionRecord]: ...
    async def version_numbers(self, package_id: str) -> list[tuple[str, str]]: ...
    async def count_versions(self, package_id: str) -> int: ...
    async def set_status(
        self, package_id: str, version: str, expected: str, entry: dict[str, Any]
    ) -> VersionRecord: ...
    async def add_test_report(
        self, package_id: str, version: str, record: dict[str, Any], test_status: str
    ) -> VersionRecord: ...


class LimitReached(Exception):
    def __init__(self, count: int) -> None:
        super().__init__(count)
        self.count = count


class MemoryStore:
    name = "memory"

    def __init__(self) -> None:
        self._packages: dict[str, PackageRecord] = {}
        self._versions: dict[tuple[str, str], VersionRecord] = {}
        self._seq = 0
        self._lock = asyncio.Lock()

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def check(self) -> bool:
        return True

    def _refresh(self, package_id: str) -> None:
        pkg = self._packages[package_id]
        rows = [(v.version, v.status) for (pid, _), v in self._versions.items() if pid == package_id]
        latest = pick_latest(rows)
        pkg.latest_version = latest
        fields = self._versions[(package_id, latest)].search_fields if latest else {}
        pkg.tags = fields.get("tags", [])
        pkg.entity_types = fields.get("entity_types", [])
        pkg.media_types = fields.get("media_types", [])
        pkg.domains = fields.get("domains", [])

    async def create_package(self, pkg: PackageRecord) -> PackageRecord:
        async with self._lock:
            if pkg.package_id in self._packages:
                raise AlreadyExists(pkg.package_id)
            self._packages[pkg.package_id] = copy.deepcopy(pkg)
            return copy.deepcopy(pkg)

    async def get_package(self, package_id: str) -> PackageRecord | None:
        pkg = self._packages.get(package_id)
        return copy.deepcopy(pkg) if pkg else None

    async def update_package(
        self, package_id: str, changes: dict[str, Any], expected_revision: int | None
    ) -> PackageRecord:
        async with self._lock:
            pkg = self._packages[package_id]
            if expected_revision is not None and pkg.revision != expected_revision:
                raise RevisionMismatch(pkg.revision)
            updated = replace(pkg, **changes, revision=pkg.revision + 1, updated_at=now())
            self._packages[package_id] = updated
            return copy.deepcopy(updated)

    async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
        items = [
            p
            for pid, p in sorted(self._packages.items())
            if (after is None or pid > after) and matches(p, flt)
        ]
        return copy.deepcopy(items[:limit])

    async def count_forks(self, package_id: str) -> int:
        return sum(1 for p in self._packages.values() if (p.fork_of or {}).get("package_id") == package_id)

    async def delete_package_if_empty(self, package_id: str) -> None:
        async with self._lock:
            if not any(pid == package_id for pid, _ in self._versions):
                self._packages.pop(package_id, None)

    async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord:
        async with self._lock:
            key = (version.package_id, version.version)
            if key in self._versions:
                raise VersionExists(version.version)
            count = sum(1 for pid, _ in self._versions if pid == version.package_id)
            if count >= max_versions:
                raise LimitReached(count)
            self._seq += 1
            stored = replace(copy.deepcopy(version), seq=self._seq)
            self._versions[key] = stored
            pkg = self._packages[version.package_id]
            pkg.updated_at = version.created_at
            pkg.revision += 1
            self._refresh(version.package_id)
            return copy.deepcopy(stored)

    async def get_version(self, package_id: str, version: str) -> VersionRecord | None:
        v = self._versions.get((package_id, version))
        return copy.deepcopy(v) if v else None

    async def list_versions(
        self, package_id: str, status: str | None, before_seq: int | None, limit: int
    ) -> list[VersionRecord]:
        items = sorted(
            (
                v
                for (pid, _), v in self._versions.items()
                if pid == package_id
                and (status is None or v.status == status)
                and (before_seq is None or v.seq < before_seq)
            ),
            key=lambda v: v.seq,
            reverse=True,
        )
        return copy.deepcopy(items[:limit])

    async def version_numbers(self, package_id: str) -> list[tuple[str, str]]:
        return [(v.version, v.status) for (pid, _), v in self._versions.items() if pid == package_id]

    async def count_versions(self, package_id: str) -> int:
        return sum(1 for pid, _ in self._versions if pid == package_id)

    async def set_status(
        self, package_id: str, version: str, expected: str, entry: dict[str, Any]
    ) -> VersionRecord:
        async with self._lock:
            v = self._versions[(package_id, version)]
            if v.status != expected:
                raise StatusMismatch(v.status)
            v.status = str(entry["status"])
            v.status_history.append(dict(entry))
            pkg = self._packages[package_id]
            pkg.updated_at = now()
            pkg.revision += 1
            self._refresh(package_id)
            return copy.deepcopy(v)

    async def add_test_report(
        self, package_id: str, version: str, record: dict[str, Any], test_status: str
    ) -> VersionRecord:
        async with self._lock:
            v = self._versions[(package_id, version)]
            v.test_reports.append(dict(record))
            v.test_status = test_status
            return copy.deepcopy(v)
