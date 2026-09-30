"""Export of package versions for autonomous use and their offline verification.

``export`` downloads the archive of ``package_id@version`` (and, recursively, of every
``dependencies.packages`` entry), checks that the bytes match the ``ETag`` and the version's
``digest``, and writes::

    <out>/<package_id>-<version>.zip     exact canonical archive from the registry
    <out>/jane-export.json               index: package, version, digest, file, size, status

``verify`` works without the registry: the archive is canonical, its digest matches the index (or
``--digest``), ``jane-package.json`` is valid (contract schema when ``contracts/`` is available), every
file the manifest refers to is present, and no secrets are found. An exported archive is what
handler-runtime runs locally (``jane-handler-runtime test <zip>``) or receives as
``HandlerInvocation.package_archive``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from .archive import MANIFEST_NAME, ArchiveError, ArchiveLimits, digest_of, is_canonical, read_archive
from .secrets import ScanBudgetExceeded, oversized_files, scan_files
from .settings import PackageLimits, SecretScanLimits
from .validation import ContractSchemas, PackageValidator, find_contracts_dir

__all__ = ["EXPORT_FORMAT", "INDEX_NAME", "ExportError", "VerifyReport", "export_package", "verify_archive"]

EXPORT_FORMAT = "jane-export@1"
INDEX_NAME = "jane-export.json"


class ExportError(RuntimeError):
    pass


def _etag_digest(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().removeprefix("W/").strip('"')


def export_package(
    client: httpx.Client,
    package_id: str,
    version: str,
    out: Path,
    *,
    with_dependencies: bool = True,
    max_packages: int,
) -> list[dict[str, Any]]:
    """Download and verify; returns the index entries (also written to ``out/jane-export.json``)."""
    out.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    queue = [(package_id, version)]
    seen: set[tuple[str, str]] = set()
    while queue:
        pid, ver = queue.pop(0)
        if (pid, ver) in seen:
            continue
        if len(seen) >= max_packages:
            raise ExportError(f"more than {max_packages} packages in the dependency closure")
        seen.add((pid, ver))
        meta = client.get(f"/v1/packages/{pid}/versions/{ver}")
        if meta.status_code != 200:
            raise ExportError(f"{pid}@{ver}: registry returned HTTP {meta.status_code}: {meta.text[:300]}")
        info = meta.json()
        response = client.get(f"/v1/packages/{pid}/versions/{ver}/archive")
        if response.status_code != 200:
            raise ExportError(f"{pid}@{ver}: archive download returned HTTP {response.status_code}")
        data = response.content
        actual = digest_of(data)
        etag = _etag_digest(response.headers.get("etag"))
        if etag != actual or info["digest"] != actual:
            raise ExportError(
                f"{pid}@{ver}: digest mismatch (ETag {etag}, version {info['digest']}, bytes {actual})"
            )
        name = f"{pid}-{ver}.zip"
        (out / name).write_bytes(data)
        entries.append(
            {
                "package_id": pid,
                "version": ver,
                "digest": actual,
                "file": name,
                "size_bytes": len(data),
                "status": info.get("status"),
                "kind": (info.get("manifest") or {}).get("kind"),
            }
        )
        if with_dependencies:
            for dep in ((info.get("manifest") or {}).get("dependencies") or {}).get("packages") or []:
                queue.append((str(dep["package_id"]), str(dep["version"])))
    index = {
        "format": EXPORT_FORMAT,
        "exported_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "registry": str(client.base_url),
        "root": {"package_id": package_id, "version": version},
        "packages": entries,
    }
    (out / INDEX_NAME).write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return entries


@dataclass
class VerifyReport:
    path: str
    digest: str | None = None
    package: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def wire(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "ok": self.ok,
            "digest": self.digest,
            "package": self.package,
            "checks": self.checks,
            "errors": self.errors,
        }


def _expected_from_index(archive: Path) -> str | None:
    index = archive.parent / INDEX_NAME
    if not index.is_file():
        return None
    doc = json.loads(index.read_text(encoding="utf-8"))
    for entry in doc.get("packages") or []:
        if entry.get("file") == archive.name:
            return str(entry["digest"])
    return None


def verify_archive(
    archive: Path,
    *,
    expected_digest: str | None = None,
    contracts: Path | None = None,
    package_limits: PackageLimits | None = None,
    secret_limits: SecretScanLimits | None = None,
) -> VerifyReport:
    limits = package_limits or PackageLimits()
    report = VerifyReport(path=str(archive))
    data = archive.read_bytes()
    report.digest = digest_of(data)
    expected = expected_digest or _expected_from_index(archive)
    if expected is not None:
        report.checks["digest"] = expected == report.digest
        if not report.checks["digest"]:
            report.errors.append(f"digest {report.digest} does not match expected {expected}")
    alimits = ArchiveLimits(limits.max_archive_bytes, limits.max_unpacked_bytes, limits.max_files)
    try:
        files = read_archive(data, alimits)
    except ArchiveError as exc:
        report.errors.append(f"archive is not a valid package: {exc}")
        return report
    report.checks["canonical"] = is_canonical(data, alimits)
    if not report.checks["canonical"]:
        report.errors.append("archive is not in the canonical form (sorted, stored, fixed time and mode)")
    if MANIFEST_NAME not in files:
        report.errors.append("jane-package.json is missing")
        return report
    try:
        manifest: Mapping[str, Any] = json.loads(files[MANIFEST_NAME].decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        report.errors.append(f"jane-package.json is not valid JSON: {exc}")
        return report
    report.package = {
        k: manifest.get(k) for k in ("package_id", "version", "kind", "fork_of") if k in manifest
    }
    try:
        schemas = ContractSchemas(find_contracts_dir(contracts))
    except FileNotFoundError:
        schemas = None
    if schemas is not None:
        validator = PackageValidator(schemas, require_tests=False)
        issues = validator.manifest_issues(manifest)
        if not issues:
            issues = validator.package_issues(manifest, files, "/manifest")
        report.checks["manifest"] = not issues
        report.errors.extend(f"{i.pointer}: {i.message}" for i in issues)
    else:
        missing = [p for _, p in PackageValidator.referenced_paths(manifest) if p not in files]
        report.checks["referenced_files"] = not missing
        report.errors.extend(f"referenced file is missing: {p}" for p in missing)
    slimits = secret_limits or SecretScanLimits()
    too_big = oversized_files(files, slimits)
    report.checks["scan_limit"] = not too_big
    report.errors.extend(
        f"{p}: larger than secrets.max_scan_bytes_per_file, cannot be scanned" for p in too_big
    )
    try:
        findings = scan_files(files, slimits)
    except ScanBudgetExceeded as exc:
        report.checks["secrets"] = False
        report.errors.append(str(exc))
        return report
    report.checks["secrets"] = not findings
    report.errors.extend(f"{f.path}: {f.message}" for f in findings)
    return report
