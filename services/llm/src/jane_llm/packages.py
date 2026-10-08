"""LLM packages (``kind: llm``): loading from an archive, the registry or a local directory.

A package is a manifest (``jane-package.json``) plus prompts and schemas; no code. The executor verifies
``handler.digest`` when given (``sha256:`` of the archive bytes; for a local directory — of the canonical
archive built by :func:`build_archive`).
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import httpx

from jane_kit.clients import ClientLimits, RemoteError, ServiceClient
from jane_kit.content import ContentReader
from jane_kit.errors import JaneError, NotFound, UpstreamUnavailable, ValidationFailed
from jane_llm.settings import GatewayLimits

MANIFEST = "jane-package.json"
_FIXED_TIME = (1980, 1, 1, 0, 0, 0)


class DigestMismatch(JaneError):
    code = "digest_mismatch"


@dataclass(frozen=True)
class LoadedPackage:
    manifest: dict[str, Any]
    files: dict[str, bytes]
    digest: str

    @property
    def package_id(self) -> str:
        return str(self.manifest["package_id"])

    @property
    def version(self) -> str:
        return str(self.manifest["version"])

    def text(self, path: str) -> str:
        if path not in self.files:
            raise ValidationFailed(f"package {self.package_id}@{self.version} has no file {path!r}")
        return self.files[path].decode("utf-8")

    def json(self, path: str) -> Any:
        try:
            return json.loads(self.text(path))
        except ValueError as exc:
            raise ValidationFailed(f"{path} in package {self.package_id} is not valid JSON") from exc


def _safe(path: str) -> bool:
    p = PurePosixPath(path)
    return not p.is_absolute() and ".." not in p.parts and "\\" not in path


def build_archive(files: dict[str, bytes]) -> bytes:
    """Canonical zip: sorted paths, fixed timestamps and permissions, deflate."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files):
            info = zipfile.ZipInfo(path, date_time=_FIXED_TIME)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[path])
    return buf.getvalue()


def read_dir(root: Path) -> dict[str, bytes]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            out[p.relative_to(root).as_posix()] = p.read_bytes()
    return out


def digest_of(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def unpack(archive: bytes, max_total_bytes: int, max_files: int) -> dict[str, bytes]:
    """Files of a package zip; rejects archives above ``max_files`` or ``max_total_bytes`` uncompressed."""
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            infos = [i for i in zf.infolist() if not i.is_dir()]
            if len(infos) > max_files:
                raise ValidationFailed(
                    f"package archive has {len(infos)} files; gateway.max_package_files={max_files}"
                )
            total = sum(i.file_size for i in infos)
            if total > max_total_bytes:
                raise ValidationFailed(
                    f"package archive unpacks to {total} bytes; gateway.max_package_bytes={max_total_bytes}"
                )
            files = {}
            for info in infos:
                if info.is_dir():
                    continue
                if not _safe(info.filename):
                    raise ValidationFailed(f"unsafe path in package archive: {info.filename!r}")
                files[info.filename] = zf.read(info)
            return files
    except zipfile.BadZipFile as exc:
        raise ValidationFailed("package archive is not a zip file") from exc


def check_llm_manifest(manifest: dict[str, Any], ref: dict[str, Any] | None = None) -> None:
    entry = manifest.get("entry") or {}
    if manifest.get("kind") != "llm" or entry.get("executor") != "llm":
        raise ValidationFailed(
            f"package {manifest.get('package_id')} is kind={manifest.get('kind')!r}; this executor runs kind=llm only"
        )
    for key in ("instructions", "output_schema"):
        if not entry.get(key):
            raise ValidationFailed(f"LLM package entry has no {key}")
    if ref and (
        manifest.get("package_id") != ref.get("package_id") or manifest.get("version") != ref.get("version")
    ):
        raise ValidationFailed(
            f"package archive is {manifest.get('package_id')}@{manifest.get('version')}, "
            f"requested {ref.get('package_id')}@{ref.get('version')}"
        )


class PackageLoader:
    """Finds LLM packages: request archive -> local directory -> registry. Caches by digest.

    The caches only save fetching and unpacking; a load gives the same answer on a cold and a warm loader:

    * ``package_archive`` of the request is read and verified every time; ``_archives`` (digest of the archive
      bytes -> package) only skips unpacking the same bytes again;
    * a reference without an archive reuses ``_found`` (packages found in the local directory or the registry)
      only for exactly its ``package_id@version`` and digest. A digest of another package or version, or a
      package seen only in some request's archive, goes the cold way and gets its ``digest_mismatch`` /
      ``not_found``.

    ``package_archive`` is read by ``content`` (``jane_kit.content.ContentReader`` under ``JANE_LLM_BLOB_ROOTS`` /
    ``JANE_LLM_DOWNLOAD_HOST_ALLOWLIST``); without it only inline archives can be read.
    """

    def __init__(
        self,
        packages_dir: Path | None,
        registry_url: str | None,
        registry_limits: ClientLimits,
        registry_token: str | None = None,
        *,
        limits: GatewayLimits,
        transport: httpx.AsyncBaseTransport | None = None,
        content: ContentReader | None = None,
    ) -> None:
        self.transport = transport
        self.limits = limits
        self.content = content or ContentReader(timeout_ms=limits.content_fetch_timeout_ms)
        self.packages_dir = packages_dir
        self.registry_url = registry_url
        self.registry_limits = registry_limits
        self.registry_token = registry_token
        self._archives: dict[str, LoadedPackage] = {}
        self._found: dict[str, LoadedPackage] = {}

    def _local(self, package_id: str, version: str) -> LoadedPackage | None:
        if self.packages_dir is None or not self.packages_dir.is_dir():
            return None
        for manifest_path in sorted(self.packages_dir.rglob(MANIFEST)):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if manifest.get("package_id") == package_id and manifest.get("version") == version:
                files = read_dir(manifest_path.parent)
                return LoadedPackage(manifest, files, digest_of(build_archive(files)))
        return None

    async def _registry(self, package_id: str, version: str) -> bytes | None:
        if not self.registry_url:
            return None
        headers = {"Authorization": f"Bearer {self.registry_token}"} if self.registry_token else None
        async with ServiceClient(
            self.registry_url, self.registry_limits, headers=headers, transport=self.transport
        ) as client:
            try:
                resp = await client.request("GET", f"/v1/packages/{package_id}/versions/{version}/archive")
            except RemoteError as exc:
                if exc.status == 404:
                    return None
                raise UpstreamUnavailable(
                    f"registry error: HTTP {exc.status}", retryable=exc.retryable
                ) from exc
            except httpx.HTTPError as exc:
                raise UpstreamUnavailable(
                    f"registry unavailable: {type(exc).__name__}", retryable=True
                ) from exc
            declared = int(resp.headers.get("content-length") or 0)
            if declared > self.limits.max_package_bytes or len(resp.content) > self.limits.max_package_bytes:
                raise ValidationFailed(
                    f"registry archive exceeds gateway.max_package_bytes={self.limits.max_package_bytes}"
                )
            return resp.content

    def _cached(self, digest: str | None, package_id: str, version: str) -> LoadedPackage | None:
        """The package found earlier under ``digest`` if it is ``package_id@version`` of the reference."""
        pkg = self._found.get(digest) if digest else None
        if (
            pkg is None
            or pkg.manifest.get("package_id") != package_id
            or pkg.manifest.get("version") != version
        ):
            return None
        return pkg

    async def load(self, ref: dict[str, Any], archive_ref: dict[str, Any] | None) -> LoadedPackage:
        package_id, version, wanted = str(ref["package_id"]), str(ref["version"]), ref.get("digest")
        pkg: LoadedPackage | None = None
        if archive_ref is not None:
            # The request's archive is what runs: read it every time, the cache only skips unpacking it.
            data = await self.content.read(
                archive_ref, max_bytes=self.limits.max_package_bytes, limit="gateway.max_package_bytes"
            )
            pkg = self._archives.get(digest_of(data)) or self._from_archive(data)
            cache = self._archives
        else:
            cache = self._found
            pkg = self._cached(wanted, package_id, version)
            if pkg is None:
                pkg = self._local(package_id, version)
            if pkg is None:
                data_or_none = await self._registry(package_id, version)
                if data_or_none is not None:
                    pkg = self._from_archive(data_or_none)
        if pkg is None:
            raise NotFound(f"package {package_id}@{version} not found (archive, local directory, registry)")
        check_llm_manifest(pkg.manifest, ref)
        if wanted and wanted != pkg.digest:
            raise DigestMismatch(f"package digest {pkg.digest} does not match {wanted}")
        cache[pkg.digest] = pkg
        return pkg

    def _from_archive(self, data: bytes) -> LoadedPackage:
        if len(data) > self.limits.max_package_bytes:
            raise ValidationFailed(
                f"package archive exceeds gateway.max_package_bytes={self.limits.max_package_bytes}"
            )
        files = unpack(data, self.limits.max_package_bytes, self.limits.max_package_files)
        if MANIFEST not in files:
            raise ValidationFailed(f"package archive has no {MANIFEST}")
        try:
            manifest = json.loads(files[MANIFEST])
        except ValueError as exc:
            raise ValidationFailed(f"{MANIFEST} is not valid JSON") from exc
        return LoadedPackage(manifest, files, digest_of(data))


def publish_request(root: Path) -> dict[str, Any]:
    """``registry.v1`` ``PublishRequest`` body for a package directory (manifest + files)."""
    files = read_dir(root)
    manifest = json.loads(files.pop(MANIFEST))
    payload = {}
    for path, data in files.items():
        try:
            payload[path] = {"encoding": "utf-8", "data": data.decode("utf-8")}
        except UnicodeDecodeError:
            payload[path] = {"encoding": "base64", "data": base64.b64encode(data).decode()}
    return {"manifest": manifest, "files": payload}


async def publish(
    root: Path,
    registry_url: str,
    limits: ClientLimits | None = None,
    token: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    """Create the package (if needed) and publish its version in the registry (``registry.v1``)."""
    body = publish_request(root)
    manifest = body["manifest"]
    headers = {"Authorization": f"Bearer {token}"} if token else None
    async with ServiceClient(registry_url, limits, headers=headers, transport=transport) as client:
        create = {"package_id": manifest["package_id"], "kind": manifest["kind"], "title": manifest["title"]}
        if manifest.get("description"):
            create["description"] = manifest["description"]
        try:
            await client.post_json("/v1/packages", create, idempotency_key=f"create-{manifest['package_id']}")
        except RemoteError as exc:
            if exc.status != 409:
                raise
        version_key = f"publish-{manifest['package_id']}-{manifest['version']}-{digest_of(build_archive(read_dir(root)))[7:23]}"
        result: dict[str, Any] = await client.post_json(
            f"/v1/packages/{manifest['package_id']}/versions", body, idempotency_key=version_key
        )
        return result


def main(argv: list[str] | None = None) -> int:
    """``python -m jane_llm.packages {digest|publish} <dir> [--registry URL]``.

    The registry token is read from the environment variable ``JANE_LLM_REGISTRY_TOKEN``.
    """
    import argparse
    import os

    parser = argparse.ArgumentParser(prog="python -m jane_llm.packages")
    parser.add_argument("command", choices=["digest", "publish"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--registry", default=os.environ.get("JANE_LLM_REGISTRY_URL"))
    ns = parser.parse_args(argv)
    files = read_dir(ns.directory)
    check_llm_manifest(json.loads(files[MANIFEST]))
    if ns.command == "digest":
        print(digest_of(build_archive(files)))
        return 0
    if not ns.registry:
        parser.error("--registry (or JANE_LLM_REGISTRY_URL) is required for publish")
    result = asyncio.run(publish(ns.directory, ns.registry, token=os.environ.get("JANE_LLM_REGISTRY_TOKEN")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
