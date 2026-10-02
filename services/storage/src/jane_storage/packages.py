"""Storage packages (``kind: storage``): catalog of installed packages, canonical archive, publication.

A storage package is a manifest plus configuration, without code (contracts/docs/handler-packages.md):
``jane-package.json`` with ``StorageEntry`` (adapter, writes, formats), ``schemas/params.schema.json``
and tests. Every adapter distribution ships its package and registers it in the entry-point group
``jane.storage.packages`` (see :mod:`jane_storage.adapters`), so the storage service knows the packages
of all installed adapters without the registry (ADR-0009: standard ``jane.storage-*`` packages are
built into the service).

Other storage packages (forks, new versions) come as ``HandlerInvocation.package_archive`` or from the registry
(:mod:`jane_storage.registry_packages`); both are untrusted archives read by :func:`package_from_archive` within
:class:`ArchiveLimits`. A storage package has no code, so - like the built-in ones - it declares no dependencies
(runtime profile, Python requirements, other packages).

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
import stat
import sys
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from .adapters import package_dirs

__all__ = [
    "ArchiveLimits",
    "DependencyNotAllowed",
    "PackageCatalog",
    "PublishOutcome",
    "StoragePackage",
    "canonical_archive",
    "load_package",
    "main",
    "package_from_archive",
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


class DependencyNotAllowed(ValueError):
    """The manifest declares dependencies the storage executor cannot provide (``dependency_not_allowed``)."""


@dataclass(frozen=True)
class ArchiveLimits:
    """Bounds for reading an untrusted package archive (``limits.packages`` of the service)."""

    max_archive_bytes: int = 20 * 1024 * 1024
    max_unpacked_bytes: int = 50 * 1024 * 1024
    max_files: int = 2_000


_DEPENDENCY_KEYS = ("runtime_profile", "python", "packages")


def _from_files(files: Sequence[tuple[str, bytes]]) -> StoragePackage:
    table = dict(files)
    if MANIFEST not in table:
        raise ValueError(f"package archive has no {MANIFEST}")
    try:
        manifest = json.loads(table[MANIFEST])
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f"{MANIFEST} is not valid JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"{MANIFEST} must be a JSON object")
    entry = manifest.get("entry")
    if manifest.get("kind") != "storage" or not isinstance(entry, dict) or entry.get("executor") != "storage":
        raise ValueError(
            f"{manifest.get('package_id')}: kind={manifest.get('kind')!r} is not a storage package "
            "(this executor runs kind=storage, entry.executor=storage only)"
        )
    for key in ("package_id", "version"):
        if not isinstance(manifest.get(key), str):
            raise ValueError(f"{MANIFEST}: {key} must be a string")
    if not isinstance(entry.get("adapter"), str) or not entry["adapter"] or not isinstance(entry.get("writes"), str):
        raise ValueError(f"{manifest['package_id']}: entry.adapter and entry.writes are required")
    if entry["writes"] not in {"raw", "entities", "raw_and_entities", "data"}:
        raise ValueError(f"{manifest['package_id']}: unsupported entry.writes {entry['writes']!r}")
    fmt = entry.get("format") or {}
    if not isinstance(fmt, dict):
        raise ValueError(f"{manifest['package_id']}: invalid entry.format")
    raw_format, entities_format = fmt.get("raw", "original"), fmt.get("entities", "json")
    if (
        not isinstance(raw_format, str)
        or raw_format not in {"original", "html", "json"}
        or not isinstance(entities_format, str)
        or entities_format not in {"json", "jsonl"}
    ):
        raise ValueError(f"{manifest['package_id']}: invalid entry.format")
    if entry.get("history", True) is not True:
        # History is part of the delivery-completeness check of every adapter; it cannot be switched off.
        raise ValueError(
            f"{manifest.get('package_id')}: entry.history=false is not supported by this executor"
        )
    deps = manifest.get("dependencies") or {}
    if not isinstance(deps, dict) or any(deps.values()):
        declared = [k for k in _DEPENDENCY_KEYS if isinstance(deps, dict) and deps.get(k)]
        raise DependencyNotAllowed(
            f"{manifest['package_id']}: a storage package has no code and declares no dependencies "
            f"({', '.join(f'dependencies.{k}' for k in declared) or 'dependencies'})"
        )
    input_contract = manifest.get("input") or {}
    if not isinstance(input_contract, dict):
        raise ValueError(f"{manifest['package_id']}: invalid input.accepts")
    accepts = input_contract.get("accepts", [])
    if not isinstance(accepts, list) or any(
        not isinstance(kind, str) or kind not in {"material", "entities", "data"} for kind in accepts
    ):
        raise ValueError(f"{manifest['package_id']}: invalid input.accepts")
    params_path = manifest.get("params_schema")
    if params_path is not None and not isinstance(params_path, str):
        raise ValueError(f"{manifest['package_id']}: params_schema must be a path")
    if params_path is not None and params_path not in table:
        raise ValueError(f"{manifest['package_id']}: params_schema {params_path!r} is not in the package")
    try:
        params_schema = json.loads(table[params_path]) if params_path else None
    except (ValueError, UnicodeError) as exc:
        raise ValueError(f"{manifest['package_id']}: params_schema is not valid JSON: {exc}") from exc
    if params_schema is not None:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError

        try:
            Draft202012Validator.check_schema(params_schema)
        except SchemaError as exc:
            raise ValueError(f"{manifest['package_id']}: invalid params_schema: {exc.message}") from exc
    ordered = tuple(sorted(files))
    return StoragePackage(
        manifest=manifest, files=ordered, params_schema=params_schema, archive=canonical_archive(ordered)
    )


def load_package(root: Path) -> StoragePackage:
    return _from_files(_package_files(root))


def _archive_path(name: str) -> str:
    if not name or name.startswith("/") or "\\" in name or {"", ".", ".."} & set(name.split("/")):
        raise ValueError(f"unsafe path in package archive: {name!r}")
    return name


def package_from_archive(archive: bytes, limits: ArchiveLimits | None = None) -> StoragePackage:
    """Package from an untrusted zip with ``jane-package.json`` (``package_archive`` or a registry download).

    Raises ``ValueError`` (:class:`DependencyNotAllowed` for declared dependencies) when the archive is not a
    readable zip, exceeds ``limits``, has unsafe, duplicate or symlink entries, or is not a storage package.
    The package's digest is that of the canonical archive of its files (the registry's algorithm).
    """
    lim = limits or ArchiveLimits()
    if len(archive) > lim.max_archive_bytes:
        raise ValueError(
            f"package archive is {len(archive)} bytes, limit max_archive_bytes={lim.max_archive_bytes}"
        )
    try:
        zf = zipfile.ZipFile(io.BytesIO(archive))
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError(f"package archive is not a zip file: {exc}") from exc
    files: dict[str, bytes] = {}
    with zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > lim.max_files:
            raise ValueError(f"package archive has {len(infos)} files, limit max_files={lim.max_files}")
        total = 0
        for info in infos:
            name = _archive_path(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f"symlinks are not allowed in a package: {name!r}")
            if name in files:
                raise ValueError(f"duplicate entry in package archive: {name!r}")
            total += info.file_size
            if total > lim.max_unpacked_bytes:
                raise ValueError(
                    f"package archive unpacks beyond max_unpacked_bytes={lim.max_unpacked_bytes}"
                )
            try:
                with zf.open(info) as src:
                    data = src.read(info.file_size + 1)
            except (zipfile.BadZipFile, NotImplementedError, RuntimeError, OSError) as exc:
                raise ValueError(f"cannot read {name!r} from the package archive: {exc}") from exc
            if len(data) != info.file_size:
                raise ValueError(f"size mismatch of {name!r} in the package archive")
            files[name] = data
    return _from_files(list(files.items()))


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
