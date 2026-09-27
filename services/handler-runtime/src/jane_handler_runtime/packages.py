"""Getting a package: a local directory or zip (CLI), ``package_archive`` (ContentRef) or the registry.

Every archive is verified: ``handler.digest`` (``sha256:`` of the archive bytes) must match when given,
``ContentRef.sha256``/``size_bytes`` must match for blobs, and the registry ``ETag`` must match the bytes.
Unpacking is bounded by ``PackageLimits``; verified packages are cached by digest.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import shutil
import tempfile
import threading
from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import httpx

from jane_extractor_sdk.package import (
    MANIFEST_NAME,
    PackageError,
    UnpackLimits,
    build_archive,
    digest_of,
    load_manifest,
    safe_unpack,
)
from jane_kit.errors import JaneError, NotFound, UpstreamUnavailable, ValidationFailed

from .settings import PackageLimits, Settings

__all__ = ["ContentFetcher", "LoadedPackage", "PackageStore", "digest_mismatch"]


def digest_mismatch(detail: str) -> JaneError:
    return JaneError(detail, code="digest_mismatch", title="Package digest mismatch")


@dataclass(frozen=True)
class LoadedPackage:
    root: Path
    manifest: dict[str, Any]
    digest: str
    source: str  # "local" | "archive" | "registry"

    @property
    def ref(self) -> dict[str, str]:
        return {
            "package_id": self.manifest["package_id"],
            "version": self.manifest["version"],
            "digest": self.digest,
        }


class ContentFetcher:
    """Reads ``ContentRef`` values: inline, ``file://`` (only under configured roots) or ``download_url``.

    ``s3://`` without ``download_url`` is not readable: the runtime holds no storage credentials (ADR-0004/0006).
    """

    def __init__(
        self, settings: Settings, request_timeout_s: float, transport: httpx.AsyncBaseTransport | None = None
    ):
        self.roots = [p.resolve() for p in settings.blob_roots]
        self.timeout = request_timeout_s
        self.transport = transport

    def _file(self, uri: str, limit: int) -> bytes:
        parsed = urlparse(uri)
        raw = unquote(parsed.path)
        if parsed.netloc and parsed.netloc != "localhost":
            raw = f"//{parsed.netloc}{raw}"
        if len(raw) > 2 and raw[0] == "/" and raw[2] == ":":  # file:///C:/x on Windows
            raw = raw[1:]
        path = Path(raw).resolve()
        if not any(path.is_relative_to(root) for root in self.roots):
            raise ValidationFailed(
                "file:// content outside the allowed roots (JANE_HANDLER_RUNTIME_BLOB_ROOTS)",
                details={"uri": uri},
            )
        if not path.is_file():
            raise NotFound(f"blob not found: {uri}")
        if path.stat().st_size > limit:
            raise JaneError(f"blob is larger than {limit} bytes", code="payload_too_large")
        return path.read_bytes()

    async def _download(self, url: str, limit: int) -> bytes:
        try:
            async with (
                httpx.AsyncClient(
                    timeout=self.timeout, transport=self.transport, follow_redirects=True
                ) as client,
                client.stream("GET", url) as response,
            ):
                if response.status_code >= 400:
                    raise UpstreamUnavailable(f"download_url returned HTTP {response.status_code}")
                buf = bytearray()
                async for chunk in response.aiter_bytes():
                    buf.extend(chunk)
                    if len(buf) > limit:
                        raise JaneError(f"blob is larger than {limit} bytes", code="payload_too_large")
                return bytes(buf)
        except httpx.HTTPError as exc:
            raise UpstreamUnavailable(f"cannot download blob: {exc}") from exc

    async def read(self, ref: Mapping[str, Any], limit: int) -> bytes:
        kind = ref.get("kind")
        if kind == "inline":
            data = str(ref.get("data", ""))
            raw = base64.b64decode(data) if ref.get("encoding") == "base64" else data.encode("utf-8")
            if len(raw) > limit:
                raise JaneError(f"content is larger than {limit} bytes", code="payload_too_large")
        elif kind == "blob":
            uri = str(ref.get("uri", ""))
            if ref.get("download_url"):
                raw = await self._download(str(ref["download_url"]), limit)
            elif uri.startswith("file://"):
                raw = await asyncio.to_thread(self._file, uri, limit)
            else:
                raise ValidationFailed(
                    "blob without download_url cannot be read by handler-runtime (no storage credentials)",
                    details={"uri": uri},
                )
            if "size_bytes" in ref and int(ref["size_bytes"]) != len(raw):
                raise ValidationFailed("blob size_bytes does not match the content", details={"uri": uri})
        else:
            raise ValidationFailed(f"unknown content kind {kind!r}")
        expected = ref.get("sha256")
        if expected and hashlib.sha256(raw).hexdigest() != expected:
            raise ValidationFailed("content sha256 does not match", details={"kind": kind})
        return raw


class PackageStore:
    def __init__(
        self,
        settings: Settings,
        limits: PackageLimits,
        fetcher: ContentFetcher,
        *,
        registry_transport: httpx.AsyncBaseTransport | None = None,
        request_timeout_s: float = 30.0,
    ) -> None:
        self.settings = settings
        self.limits = limits
        self.fetcher = fetcher
        self._registry_transport = registry_transport
        self._timeout = request_timeout_s
        if settings.package_cache_dir is not None:
            self.cache_dir = settings.package_cache_dir
            self._owns_cache = False
        else:
            self.cache_dir = Path(tempfile.mkdtemp(prefix="jane-packages-"))
            self._owns_cache = True
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lru: OrderedDict[str, LoadedPackage] = OrderedDict()
        self._lock = threading.Lock()

    @property
    def unpack_limits(self) -> UnpackLimits:
        return UnpackLimits(
            self.limits.max_archive_bytes, self.limits.max_unpacked_bytes, self.limits.max_files
        )

    def close(self) -> None:
        if self._owns_cache:
            shutil.rmtree(self.cache_dir, ignore_errors=True)

    # ------------------------------------------------------------------ archives

    def _from_archive_bytes(self, archive: bytes, source: str, expected_digest: str | None) -> LoadedPackage:
        digest = digest_of(archive)
        if expected_digest and expected_digest != digest:
            raise digest_mismatch(f"expected {expected_digest}, archive has {digest}")
        with self._lock:
            cached = self._lru.get(digest)
            if cached is not None and cached.root.is_dir():
                self._lru.move_to_end(digest)
                return cached
        target = self.cache_dir / digest.removeprefix("sha256:")
        if not (target / MANIFEST_NAME).is_file():
            staging = Path(tempfile.mkdtemp(prefix="unpack-", dir=self.cache_dir))
            try:
                safe_unpack(archive, staging, self.unpack_limits)
            except PackageError as exc:
                shutil.rmtree(staging, ignore_errors=True)
                raise ValidationFailed(f"invalid package archive: {exc}") from exc
            shutil.rmtree(target, ignore_errors=True)
            staging.replace(target)
        try:
            manifest = load_manifest(target)
        except PackageError as exc:
            raise ValidationFailed(str(exc)) from exc
        loaded = LoadedPackage(target, manifest, digest, source)
        with self._lock:
            self._lru[digest] = loaded
            while len(self._lru) > self.limits.cache_max_entries:
                _, old = self._lru.popitem(last=False)
                shutil.rmtree(old.root, ignore_errors=True)
        return loaded

    def load_local(self, path: Path) -> LoadedPackage:
        """A package directory or zip on disk (CLI, trusted location). Digest = canonical archive."""
        try:
            archive = build_archive(path) if path.is_dir() else path.read_bytes()
        except PackageError as exc:
            raise ValidationFailed(str(exc)) from exc
        return self._from_archive_bytes(archive, "local", None)

    async def load(self, handler: Mapping[str, Any], archive_ref: Mapping[str, Any] | None) -> LoadedPackage:
        expected = handler.get("digest")
        if archive_ref is not None:
            archive = await self.fetcher.read(archive_ref, self.limits.max_archive_bytes)
            loaded = await asyncio.to_thread(self._from_archive_bytes, archive, "archive", expected)
        else:
            loaded = await self._from_registry(handler)
        manifest = loaded.manifest
        if manifest.get("package_id") != handler.get("package_id") or manifest.get("version") != handler.get(
            "version"
        ):
            raise ValidationFailed(
                "package archive does not match handler",
                details={
                    "handler": f"{handler.get('package_id')}@{handler.get('version')}",
                    "manifest": f"{manifest.get('package_id')}@{manifest.get('version')}",
                },
            )
        return loaded

    async def _from_registry(self, handler: Mapping[str, Any]) -> LoadedPackage:
        if not self.settings.registry_url:
            raise ValidationFailed(
                "no package_archive and no registry configured (JANE_HANDLER_RUNTIME_REGISTRY_URL)"
            )
        pid, version = str(handler["package_id"]), str(handler["version"])
        headers = {"Accept": "application/zip"}
        if self.settings.registry_token is not None:
            headers["Authorization"] = f"Bearer {self.settings.registry_token.get_secret_value()}"
        url = f"/v1/packages/{pid}/versions/{version}/archive"
        try:
            async with (
                httpx.AsyncClient(
                    base_url=self.settings.registry_url.rstrip("/"),
                    timeout=self._timeout,
                    transport=self._registry_transport,
                ) as client,
                client.stream("GET", url, headers=headers) as response,
            ):
                if response.status_code == 404:
                    raise NotFound(f"{pid}@{version}", title="Package version not found")
                if response.status_code >= 400:
                    raise UpstreamUnavailable(f"registry returned HTTP {response.status_code}")
                limit = self.limits.max_archive_bytes
                declared = response.headers.get("content-length")
                if declared and declared.isdigit() and int(declared) > limit:
                    raise ValidationFailed(f"archive exceeds max_archive_bytes={limit}")
                buf = bytearray()
                async for chunk in response.aiter_bytes():
                    buf.extend(chunk)
                    if len(buf) > limit:
                        raise ValidationFailed(f"archive exceeds max_archive_bytes={limit}")
                archive = bytes(buf)
        except httpx.HTTPError as exc:
            raise UpstreamUnavailable(f"registry did not respond: {exc}") from exc
        etag = response.headers.get("etag", "").strip('"').removeprefix("W/").strip('"')
        actual = digest_of(archive)
        if etag and etag != actual:
            raise digest_mismatch(f"registry ETag {etag} does not match archive {actual}")
        return await asyncio.to_thread(self._from_archive_bytes, archive, "registry", handler.get("digest"))
