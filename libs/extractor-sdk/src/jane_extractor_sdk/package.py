"""Package utilities: manifest, canonical archive and digest, safe unpacking, test-case inputs.

Package layout and manifest: ``contracts/docs/handler-packages.md``, ``package-manifest.schema.json``.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import mimetypes
import re
import stat
import zipfile
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

__all__ = [
    "MANIFEST_NAME",
    "PackageError",
    "UnpackLimits",
    "build_archive",
    "case_input",
    "digest_of",
    "iter_package_files",
    "load_manifest",
    "material_from_bytes",
    "material_from_file",
    "read_package_file",
    "safe_unpack",
]

MANIFEST_NAME = "jane-package.json"
# PackagePath of the manifest schema: relative, '/', no '..', no absolute paths.
PACKAGE_PATH_RE = re.compile(r"^(?!/)(?!.*(^|/)\.\.(/|$))[A-Za-z0-9._/-]{1,300}$")
SKIP_PARTS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".venv"})
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
FILE_ATTR = (stat.S_IFREG | 0o644) << 16
UNIX = 3
TEXT_MEDIA_PREFIXES = ("text/",)
TEXT_MEDIA_TYPES = frozenset(
    {
        "application/json",
        "application/xml",
        "application/xhtml+xml",
        "application/rss+xml",
        "application/atom+xml",
    }
)


class PackageError(ValueError):
    """Invalid package (bad path, symlink, size above a limit, missing manifest...)."""


@dataclass(frozen=True)
class UnpackLimits:
    """Bounds for unpacking an untrusted archive; values come from the runtime configuration."""

    max_archive_bytes: int
    max_unpacked_bytes: int
    max_files: int


def check_package_path(name: str) -> str:
    if not PACKAGE_PATH_RE.match(name) or name.endswith("/"):
        raise PackageError(f"invalid package path {name!r}")
    return name


def iter_package_files(package_dir: Path) -> Iterator[tuple[str, Path]]:
    """``(package path, file)`` for every file of a package directory, sorted, caches skipped.

    Symlinks are rejected (the archive format forbids them).
    """
    root = package_dir.resolve()
    entries: list[tuple[str, Path]] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise PackageError(f"symlinks are not allowed in a package: {rel.as_posix()}")
        if path.is_file():
            entries.append((check_package_path(rel.as_posix()), path))
    yield from sorted(entries)


def build_archive(package_dir: Path) -> bytes:
    """Canonical zip of a package directory - the same bytes, and so the same digest, as the registry.

    The algorithm is the one of the registry (``services/registry/README.md``, "Канонічний архів і дайджест"):
    one entry per regular file (no directory entries, no symlinks), names sorted in ascending byte order,
    compression method 0 (**stored**: the bytes do not depend on a zlib build), timestamp
    1980-01-01 00:00:00, ``external_attr = 0o100644 << 16``, ``create_system = 3`` (Unix), no extra fields,
    no comments. The same directory always gives the same bytes on Windows and Linux.
    """
    if not (package_dir / MANIFEST_NAME).is_file():
        raise PackageError(f"{package_dir}: no {MANIFEST_NAME}")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        # iter_package_files sorts by package path; paths are ASCII, so str order = byte order.
        for name, path in iter_package_files(package_dir):
            info = zipfile.ZipInfo(name, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = FILE_ATTR
            info.create_system = UNIX  # independent of the building OS
            zf.writestr(info, path.read_bytes())
    return buf.getvalue()


def digest_of(data: bytes) -> str:
    """``sha256:<hex>`` - the ``Digest`` format of the contracts."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def safe_unpack(archive: bytes, dest: Path, limits: UnpackLimits) -> None:
    """Unpack an untrusted package zip into ``dest`` with path, symlink, count and size checks."""
    if len(archive) > limits.max_archive_bytes:
        raise PackageError(
            f"archive is {len(archive)} bytes; limit max_archive_bytes={limits.max_archive_bytes}"
        )
    try:
        zf = zipfile.ZipFile(io.BytesIO(archive))
    except zipfile.BadZipFile as exc:
        raise PackageError(f"not a zip archive: {exc}") from exc
    with zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > limits.max_files:
            raise PackageError(f"archive has {len(infos)} files; limit max_files={limits.max_files}")
        total = 0
        for info in infos:
            name = check_package_path(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise PackageError(f"symlinks are not allowed in a package: {name}")
            total += info.file_size
            if total > limits.max_unpacked_bytes:
                raise PackageError(f"unpacked size exceeds max_unpacked_bytes={limits.max_unpacked_bytes}")
        dest.mkdir(parents=True, exist_ok=True)
        root = dest.resolve()
        for info in infos:
            target = (root / PurePosixPath(info.filename)).resolve()
            if not target.is_relative_to(root):
                raise PackageError(f"path escapes the package: {info.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src:
                data = src.read(limits.max_unpacked_bytes + 1)
            if len(data) != info.file_size:
                raise PackageError(f"size mismatch for {info.filename}")
            target.write_bytes(data)
    if not (dest / MANIFEST_NAME).is_file():
        raise PackageError(f"archive has no {MANIFEST_NAME} at its root")


def load_manifest(package_dir: Path) -> dict[str, Any]:
    path = package_dir / MANIFEST_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageError(f"{package_dir}: no {MANIFEST_NAME}") from exc
    except ValueError as exc:
        raise PackageError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PackageError(f"{path}: manifest must be a JSON object")
    return data


def read_package_file(package_dir: Path, name: str) -> bytes:
    rel = check_package_path(name)
    root = package_dir.resolve()
    target = (root / PurePosixPath(rel)).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise PackageError(f"package file not found: {name}")
    return target.read_bytes()


def _is_text(media_type: str) -> bool:
    return media_type.startswith(TEXT_MEDIA_PREFIXES) or media_type in TEXT_MEDIA_TYPES


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def material_from_bytes(
    data: bytes,
    *,
    media_type: str,
    url: str | None = None,
    source_id: str | None = None,
    charset: str | None = None,
    fetched_at: str | None = None,
) -> dict[str, Any]:
    """A standalone ``Material`` with inline content (for CLI runs and package tests).

    ``material_id`` follows the collector rule for web (``web:`` + sha256(url)[:32]) when a URL is given,
    otherwise ``file:`` + sha256(content)[:32]; ``observation_id`` is derived from the content hash.
    """
    sha = hashlib.sha256(data).hexdigest()
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest() if url else ""
    material_id = f"web:{url_hash[:32]}" if url else f"file:{sha[:32]}"
    content: dict[str, Any] = {
        "kind": "inline",
        "media_type": media_type,
        "size_bytes": len(data),
        "sha256": sha,
    }
    text: str | None = None
    if _is_text(media_type):
        try:
            text = data.decode(charset or "utf-8")
        except (UnicodeDecodeError, LookupError):
            text = None
    if text is not None:
        content.update(encoding="utf-8", data=text)
        if charset:
            content["charset"] = charset
    else:
        content.update(encoding="base64", data=base64.b64encode(data).decode("ascii"))
    source: dict[str, Any] = {"kind": "web" if url else "file"}
    if source_id:
        source["source_id"] = source_id
    material: dict[str, Any] = {
        "material_id": material_id,
        "observation_id": "obs_local_" + sha[:24],
        "source": source,
        "locator": {"url": url} if url else {},
        "fetched_at": fetched_at or _now(),
        "format": {"media_type": media_type},
        "revision": {"content_sha256": sha},
        "content": content,
        "collector": {"name": "local-file", "version": "1"},
    }
    if charset:
        material["format"]["charset"] = charset
    return material


def guess_media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def material_from_file(
    path: Path,
    *,
    media_type: str | None = None,
    url: str | None = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    return material_from_bytes(
        path.read_bytes(), media_type=media_type or guess_media_type(path), url=url, source_id=source_id
    )


def _load_json_file(package_dir: Path, name: str) -> Any:
    try:
        return json.loads(read_package_file(package_dir, name).decode("utf-8"))
    except ValueError as exc:
        raise PackageError(f"{name}: invalid JSON: {exc}") from exc


def case_input(package_dir: Path, case: Mapping[str, Any]) -> dict[str, Any]:
    """``HandlerInput`` for a manifest ``TestCase.input``.

    * ``material`` - JSON ``Material``; an optional top-level ``content_file`` (package path) replaces the
      content with the file (inline);
    * ``file`` (+ ``media_type``, ``url``) - raw file, minimal metadata;
    * ``entities`` / ``data`` - JSON file with an ``EntityRecord`` array / any JSON.
    """
    spec = case.get("input") or {}
    if "material" in spec:
        material = _load_json_file(package_dir, str(spec["material"]))
        if not isinstance(material, dict):
            raise PackageError(f"{spec['material']}: material must be a JSON object")
        content_file = material.pop("content_file", None)
        if content_file:
            fmt = material.get("format") or {}
            fresh = material_from_bytes(
                read_package_file(package_dir, str(content_file)),
                media_type=str(fmt.get("media_type") or "application/octet-stream"),
                charset=fmt.get("charset"),
            )
            material["content"] = fresh["content"]
            material.setdefault("revision", {})["content_sha256"] = fresh["content"]["sha256"]
        return {"kind": "material", "material": material}
    if "file" in spec:
        name = str(spec["file"])
        data = read_package_file(package_dir, name)
        media_type = str(spec.get("media_type") or guess_media_type(Path(name)))
        url = spec.get("url")
        return {"kind": "material", "material": material_from_bytes(data, media_type=media_type, url=url)}
    if "entities" in spec:
        entities = _load_json_file(package_dir, str(spec["entities"]))
        return {"kind": "entities", "entities": entities}
    if "data" in spec:
        return {"kind": "data", "data": _load_json_file(package_dir, str(spec["data"]))}
    raise PackageError(f"test {case.get('name')!r}: input needs material, file, entities or data")
