"""Canonical package archive and its digest (ADR-0002 §2).

The registry stores every version as a **canonical zip** and publishes ``digest = "sha256:" +
sha256(archive bytes)``. The same set of files always gives the same bytes on Windows and Linux:

* one entry per regular file, no directory entries, no symlinks;
* entry names are package paths (``PackagePath`` of the manifest schema: ASCII ``[A-Za-z0-9._/-]``,
  ``/`` separator, no leading ``/``, no ``..``), unique, sorted in ascending byte order;
* compression method 0 (**stored**, no compression) - the bytes do not depend on a zlib build;
* timestamp 1980-01-01 00:00:00, ``external_attr = 0o100644 << 16`` (regular file, rw-r--r--),
  ``create_system = 3`` (Unix), no extra fields, no comments, no encryption;
* written by Python ``zipfile`` (local headers + central directory, no data descriptors).

An uploaded zip may be built in any way (deflated, other timestamps, directory entries): the
registry unpacks it with limits and re-packs the files canonically, so the digest depends only on
the file paths and contents. ``jane-package.json`` produced from a JSON ``manifest`` is serialised by
:func:`manifest_bytes`.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "MANIFEST_NAME",
    "SKIP_PARTS",
    "ArchiveError",
    "ArchiveLimits",
    "canonical_archive",
    "check_package_path",
    "digest_of",
    "files_from_dir",
    "is_canonical",
    "manifest_bytes",
    "read_archive",
]

MANIFEST_NAME = "jane-package.json"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
FILE_ATTR = (stat.S_IFREG | 0o644) << 16
UNIX = 3
PACKAGE_PATH_RE = re.compile(r"^(?!/)(?!.*(^|/)\.\.(/|$))[A-Za-z0-9._/-]{1,300}$")
SKIP_PARTS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".venv"})
"""Cache/VCS directories that :func:`files_from_dir` never packs (they are not part of a package)."""


class ArchiveError(ValueError):
    """The archive or a path in it is not acceptable; ``limit`` is set when a size limit was exceeded."""

    def __init__(self, message: str, *, limit: str | None = None, path: str | None = None) -> None:
        super().__init__(message)
        self.limit = limit
        self.path = path


@dataclass(frozen=True)
class ArchiveLimits:
    """Bounds for reading an untrusted archive; values come from ``RegistryLimits.packages``."""

    max_archive_bytes: int
    max_unpacked_bytes: int
    max_files: int


def check_package_path(name: str) -> str:
    if not PACKAGE_PATH_RE.match(name) or name.endswith("/") or "//" in name:
        raise ArchiveError(f"invalid package path {name!r}", path=name)
    return name


def digest_of(data: bytes) -> str:
    """``sha256:<hex>`` - ``Digest`` of the contracts."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_archive(files: Mapping[str, bytes]) -> bytes:
    """The canonical zip of ``files`` (package path -> content)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for name in sorted(files):
            check_package_path(name)
            info = zipfile.ZipInfo(name, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = FILE_ATTR
            info.create_system = UNIX
            zf.writestr(info, files[name])
    return buf.getvalue()


def read_archive(data: bytes, limits: ArchiveLimits) -> dict[str, bytes]:
    """Files of an untrusted zip with path, symlink, duplicate, count and size checks."""
    if len(data) > limits.max_archive_bytes:
        raise ArchiveError(
            f"archive is {len(data)} bytes, limit max_archive_bytes={limits.max_archive_bytes}",
            limit="packages.max_archive_bytes",
        )
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ArchiveError(f"not a zip archive: {exc}") from exc
    files: dict[str, bytes] = {}
    with zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > limits.max_files:
            raise ArchiveError(
                f"archive has {len(infos)} files, limit max_files={limits.max_files}",
                limit="packages.max_files",
            )
        total = 0
        for info in infos:
            name = check_package_path(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ArchiveError(f"symlinks are not allowed in a package: {name}", path=name)
            if info.flag_bits & 0x1:
                raise ArchiveError(f"encrypted entries are not allowed: {name}", path=name)
            if name in files:
                raise ArchiveError(f"duplicate entry in archive: {name}", path=name)
            total += info.file_size
            if total > limits.max_unpacked_bytes:
                raise ArchiveError(
                    f"unpacked size exceeds max_unpacked_bytes={limits.max_unpacked_bytes}",
                    limit="packages.max_unpacked_bytes",
                )
            try:
                with zf.open(info) as src:
                    content = src.read(info.file_size + 1)
            except (zipfile.BadZipFile, NotImplementedError, RuntimeError, OSError) as exc:
                raise ArchiveError(f"cannot read {name}: {exc}", path=name) from exc
            if len(content) != info.file_size:
                raise ArchiveError(f"size mismatch for {name}", path=name)
            files[name] = content
    return files


def is_canonical(data: bytes, limits: ArchiveLimits) -> bool:
    """``True`` if ``data`` is exactly the canonical archive of its own files."""
    try:
        return canonical_archive(read_archive(data, limits)) == data
    except ArchiveError:
        return False


def manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    """Serialisation of ``jane-package.json`` written by the registry (JSON publish, fork, upstream port):
    UTF-8, two-space indent, key order as given, non-ASCII kept, trailing newline."""
    return (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def files_from_dir(package_dir: Path) -> dict[str, bytes]:
    """Files of a package directory (for the CLI): caches skipped, symlinks rejected."""
    root = package_dir.resolve()
    out: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ArchiveError(f"symlinks are not allowed in a package: {rel.as_posix()}")
        if path.is_file():
            out[check_package_path(rel.as_posix())] = path.read_bytes()
    return out
