"""Storage packages (``kind: storage``): catalog of installed packages, canonical archive, publication.

A storage package is a manifest plus configuration, without code (contracts/docs/handler-packages.md):
``jane-package.json`` with ``StorageEntry`` (adapter, writes, formats), ``schemas/params.schema.json``
and tests. Every adapter distribution ships its package and registers it in the entry-point group
``jane.storage.packages`` (see :mod:`jane_storage.adapters`), so the storage service knows the packages
of all installed adapters without the registry (ADR-0009: standard ``jane.storage-*`` packages are
built into the service).

Publication to the registry (``registry.v1``: ``POST /v1/packages`` + ``POST
/v1/packages/{id}/versions``) is done by ``jane-storage-packages publish --registry <url>``.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import sys
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from .adapters import package_dirs

__all__ = [
    "PackageCatalog",
    "PublishOutcome",
    "StoragePackage",
    "canonical_archive",
    "load_package",
    "main",
    "publish",
]

MANIFEST = "jane-package.json"
_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def _package_files(root: Path) -> list[tuple[str, bytes]]:
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in rel.split("/"):
            continue
        files.append((rel, path.read_bytes()))
    return sorted(files)


def canonical_archive(files: Sequence[tuple[str, bytes]]) -> bytes:
    """Deterministic zip: paths sorted, fixed time and permissions, no compression.

    The same files always give the same bytes (and digest) on Windows and Linux.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for rel, data in sorted(files):
            info = zipfile.ZipInfo(rel, date_time=_ZIP_DATE)
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            zf.writestr(info, data)
    return buf.getvalue()


@dataclass(frozen=True)
class StoragePackage:
    manifest: dict[str, Any]
    files: tuple[tuple[str, bytes], ...]
    params_schema: dict[str, Any] | None
    archive: bytes = field(repr=False)

    @property
    def package_id(self) -> str:
        return str(self.manifest["package_id"])

    @property
    def version(self) -> str:
        return str(self.manifest["version"])

    @property
    def digest(self) -> str:
        return "sha256:" + hashlib.sha256(self.archive).hexdigest()

    @property
    def entry(self) -> dict[str, Any]:
        return dict(self.manifest["entry"])

    @property
    def adapter(self) -> str:
        return str(self.entry["adapter"])

    @property
    def writes(self) -> str:
        return str(self.entry["writes"])

    @property
    def accepts(self) -> list[str]:
        return list((self.manifest.get("input") or {}).get("accepts") or [])

    @property
    def ref(self) -> dict[str, str]:
        return {"package_id": self.package_id, "version": self.version, "digest": self.digest}

    def file(self, path: str) -> bytes:
        for rel, data in self.files:
            if rel == path:
                return data
        raise KeyError(path)


def _from_files(files: Sequence[tuple[str, bytes]]) -> StoragePackage:
    table = dict(files)
    if MANIFEST not in table:
        raise ValueError(f"package archive has no {MANIFEST}")
    manifest = json.loads(table[MANIFEST])
    if manifest.get("kind") != "storage" or (manifest.get("entry") or {}).get("executor") != "storage":
        raise ValueError(f"{manifest.get('package_id')}: not a storage package")
    params_path = manifest.get("params_schema")
    params_schema = json.loads(table[params_path]) if params_path else None
    ordered = tuple(sorted(files))
    return StoragePackage(
        manifest=manifest, files=ordered, params_schema=params_schema, archive=canonical_archive(ordered)
    )


def load_package(root: Path) -> StoragePackage:
    return _from_files(_package_files(root))


def package_from_archive(archive: bytes) -> StoragePackage:
    """Package given in ``HandlerInvocation.package_archive`` (zip with ``jane-package.json``)."""
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        files = []
        for info in zf.infolist():
            name = info.filename
            if info.is_dir():
                continue
            if name.startswith("/") or ".." in name.split("/"):
                raise ValueError(f"unsafe path in package archive: {name!r}")
            files.append((name, zf.read(info)))
    return _from_files(files)


class PackageCatalog:
    """Storage packages known to this service (installed adapter distributions + extra directories)."""

    def __init__(self, packages: Sequence[StoragePackage] = ()) -> None:
        self._by_ref: dict[tuple[str, str], StoragePackage] = {}
        for pkg in packages:
            self.add(pkg)

    @classmethod
    def discover(cls, extra_dirs: Sequence[Path] = ()) -> PackageCatalog:
        roots = [*package_dirs().values(), *extra_dirs]
        return cls([load_package(root) for root in roots])

    def add(self, pkg: StoragePackage) -> None:
        self._by_ref[(pkg.package_id, pkg.version)] = pkg

    def get(self, package_id: str, version: str) -> StoragePackage | None:
        return self._by_ref.get((package_id, version))

    def all(self) -> list[StoragePackage]:
        return [self._by_ref[k] for k in sorted(self._by_ref)]


# ------------------------------------------------------------------------------------------ publish
@dataclass(frozen=True)
class PublishOutcome:
    package_id: str
    version: str
    digest: str
    package_status: int
    version_status: int

    @property
    def ok(self) -> bool:
        return self.package_status in (201, 409) and self.version_status in (200, 201, 202, 409)


def publish_request(pkg: StoragePackage) -> dict[str, Any]:
    """``PublishRequest`` body (registry.v1): manifest + every other file of the package."""
    files: dict[str, dict[str, str]] = {}
    for rel, data in pkg.files:
        if rel == MANIFEST:
            continue
        try:
            files[rel] = {"encoding": "utf-8", "data": data.decode("utf-8")}
        except UnicodeDecodeError:
            files[rel] = {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
    return {"manifest": pkg.manifest, "files": files}


def publish(
    client: httpx.Client, packages: Sequence[StoragePackage], headers: Mapping[str, str] | None = None
) -> list[PublishOutcome]:
    """Create the package (409 = already exists) and publish its version (409 = version exists)."""
    outcomes = []
    for pkg in packages:
        base = dict(headers or {})
        created = client.post(
            "/v1/packages",
            json={
                "package_id": pkg.package_id,
                "kind": "storage",
                "title": pkg.manifest["title"],
                "description": pkg.manifest.get("description", ""),
                "auto_changes_allowed": False,
            },
            headers={**base, "Idempotency-Key": f"create:{pkg.package_id}"},
        )
        published = client.post(
            f"/v1/packages/{pkg.package_id}/versions",
            json=publish_request(pkg),
            headers={**base, "Idempotency-Key": f"publish:{pkg.package_id}@{pkg.version}:{pkg.digest}"},
        )
        outcomes.append(
            PublishOutcome(
                pkg.package_id, pkg.version, pkg.digest, created.status_code, published.status_code
            )
        )
    return outcomes


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jane-storage-packages", description="Storage packages of this service"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="installed storage packages with digests")
    pub = sub.add_parser("publish", help="publish installed storage packages to the registry (registry.v1)")
    pub.add_argument("--registry", required=True, help="registry base URL, e.g. http://localhost:8105")
    pub.add_argument("--token-env", default=None, help="environment variable with a bearer token")
    pub.add_argument(
        "--timeout-ms", type=int, default=30_000, help="HTTP timeout per request (default 30000)"
    )
    arch = sub.add_parser("archive", help="write the canonical archive of a package")
    arch.add_argument("package_id")
    arch.add_argument("--out", required=True, type=Path)
    ns = parser.parse_args(argv)
    catalog = PackageCatalog.discover()
    if ns.cmd == "list":
        for pkg in catalog.all():
            print(f"{pkg.package_id}@{pkg.version}  adapter={pkg.adapter}  writes={pkg.writes}  {pkg.digest}")
        return 0
    if ns.cmd == "archive":
        matches = [p for p in catalog.all() if p.package_id == ns.package_id]
        if not matches:
            print(f"unknown package {ns.package_id}", file=sys.stderr)
            return 2
        ns.out.write_bytes(matches[-1].archive)
        print(f"{ns.out}  {matches[-1].digest}")
        return 0
    headers = {}
    if ns.token_env:
        headers["Authorization"] = f"Bearer {os.environ[ns.token_env]}"
    with httpx.Client(base_url=ns.registry, timeout=ns.timeout_ms / 1000) as client:
        outcomes = publish(client, catalog.all(), headers)
    for o in outcomes:
        print(
            f"{o.package_id}@{o.version} {o.digest}: package {o.package_status}, version {o.version_status}"
        )
    return 0 if all(o.ok for o in outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
