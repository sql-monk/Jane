"""Storage packages from the handler registry (``registry.v1``: ``GET /v1/packages/{id}/versions/{v}/archive``).

ADR-0009 §4: storage executes a package from the registry **or** the archive in the request. The handler looks
at ``package_archive`` first, then at the built-in catalog; this module is the third source, used only when
``JANE_STORAGE_REGISTRY_URL`` is set:

* the address and the bearer token are operator configuration (never from a request); the archive path is built
  from ``package_id``/``version`` checked against the contract patterns; no redirects, no proxies from the
  environment; the download stops at ``packages.max_archive_bytes`` and within
  ``packages.registry_request_timeout_ms``;
* ``ETag`` (when sent) must equal ``sha256:`` of the bytes; the package is read by
  :func:`~jane_storage.packages.package_from_archive` (storage kind only, no dependencies, archive limits) and
  its digest is that of the canonical archive (the registry's algorithm); its manifest must be the requested
  ``package_id``/``version`` and the digest must equal ``handler.digest`` when given;
* verified packages are kept in memory by digest (LRU, ``packages.cache_max_entries``). A cache hit is checked
  against the requested ``package_id``/``version`` exactly like a download, so a digest of another version is
  ``digest_mismatch`` with a cold and a warm cache alike. Requests without a digest use the version cached under
  its ``package_id@version`` (registry versions are immutable);
* concurrent requests for one version share one download.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from collections import OrderedDict
from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

import httpx

from jane_kit.errors import FieldError, JaneError, NotFound, UpstreamUnavailable, ValidationFailed
from jane_kit.logs import current_context
from jane_kit.tracing import TRACEPARENT, child_traceparent

from .packages import DependencyNotAllowed, StoragePackage, package_from_archive
from .settings import PackageLimits

__all__ = ["RegistryPackages", "check_ref", "digest_mismatch"]

log = logging.getLogger(__name__)

_SLUG = re.compile(r"[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?", re.ASCII)
_SEMVER = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", re.ASCII
)
_DIGEST = re.compile(r"sha256:[a-f0-9]{64}", re.ASCII)


def digest_mismatch(detail: str) -> JaneError:
    return JaneError(detail, code="digest_mismatch", title="Package digest mismatch", retryable=False)


def _ref_parts(ref: Mapping[str, Any]) -> tuple[str, str, str | None]:
    """``(package_id, version, digest)`` of a ``PackageRef`` matching the contract patterns (they become a URL)."""
    pid, version, digest = ref.get("package_id"), ref.get("version"), ref.get("digest")
    errors = []
    if not isinstance(pid, str) or not _SLUG.fullmatch(pid):
        errors.append(FieldError(pointer="/handler/package_id", message="must be a Slug"))
    if not isinstance(version, str) or not _SEMVER.fullmatch(version):
        errors.append(FieldError(pointer="/handler/version", message="must be an exact SemVer version"))
    if digest is not None and (not isinstance(digest, str) or not _DIGEST.fullmatch(digest)):
        errors.append(FieldError(pointer="/handler/digest", message="must be sha256:<64 hex>"))
    if errors:
        raise ValidationFailed("invalid handler reference", errors=errors)
    return str(pid), str(version), digest


def check_ref(pkg: StoragePackage, ref: Mapping[str, Any], source: str) -> None:
    """``pkg`` is the requested ``package_id@version`` and, when ``digest`` is given, has that digest."""
    pid, version, wanted = ref.get("package_id"), ref.get("version"), ref.get("digest")
    if (pkg.package_id, pkg.version) != (pid, version):
        if wanted and wanted == pkg.digest:
            # the pinned content is another package version: never run it under this reference
            raise digest_mismatch(
                f"requested {pid}@{version} with {wanted}, which is the digest of {pkg.package_id}@{pkg.version}"
            )
        raise ValidationFailed(
            f"{source} of {pid}@{version} contains {pkg.package_id}@{pkg.version}",
            errors=[FieldError(pointer="/handler", message=f"{source} has {pkg.package_id}@{pkg.version}")],
        )
    if wanted and wanted != pkg.digest:
        raise digest_mismatch(f"requested {wanted}, package has {pkg.digest}")


def _etag(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    value = value.removeprefix("W/")
    return value.strip('"') or None


class RegistryPackages:
    """Storage packages downloaded from one registry and cached by digest (one instance per service)."""

    def __init__(
        self,
        base_url: str,
        limits: PackageLimits,
        *,
        token: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.limits = limits
        self._token = token
        self._transport = transport
        self._cache: OrderedDict[str, StoragePackage] = OrderedDict()
        self._by_ref: dict[tuple[str, str], str] = {}
        self._locks: dict[tuple[str, str], tuple[asyncio.Lock, int]] = {}
        self.downloads = 0
        """Archives downloaded by this instance (cache misses)."""

    # ------------------------------------------------------------------------------ cache
    def _cached(self, pid: str, version: str, wanted: str | None) -> StoragePackage | None:
        digest = wanted or self._by_ref.get((pid, version))
        pkg = self._cache.get(digest) if digest else None
        if pkg is not None:
            self._cache.move_to_end(pkg.digest)
        return pkg

    def _remember(self, pkg: StoragePackage) -> None:
        self._cache[pkg.digest] = pkg
        self._cache.move_to_end(pkg.digest)
        self._by_ref[(pkg.package_id, pkg.version)] = pkg.digest
        while len(self._cache) > self.limits.cache_max_entries:
            old_digest, old = self._cache.popitem(last=False)
            if self._by_ref.get((old.package_id, old.version)) == old_digest:
                del self._by_ref[(old.package_id, old.version)]

    # ------------------------------------------------------------------------------ public
    async def get(self, ref: Mapping[str, Any]) -> StoragePackage:
        """The verified storage package of ``ref`` (``PackageRef``) from the cache or the registry.

        Raises ``NotFound`` (registry 404), ``UpstreamUnavailable`` (502: no answer, 5xx, refused),
        ``digest_mismatch``, ``ValidationFailed`` / ``limit_exceeded`` / ``dependency_not_allowed`` (422)."""
        pid, version, wanted = _ref_parts(ref)
        hit = self._cached(pid, version, wanted)
        if hit is not None:
            check_ref(hit, ref, "cached package")
            return hit
        key = (pid, version)
        lock, waiting = self._locks.get(key, (asyncio.Lock(), 0))
        self._locks[key] = (lock, waiting + 1)
        try:
            async with lock:
                hit = self._cached(pid, version, wanted)
                if hit is None:
                    hit = await self._download_package(pid, version)
            check_ref(hit, ref, "registry archive")
            return hit
        finally:
            lock_now, waiting_now = self._locks[key]
            if waiting_now <= 1:
                del self._locks[key]
            else:
                self._locks[key] = (lock_now, waiting_now - 1)

    # ------------------------------------------------------------------------------ download
    async def _download_package(self, pid: str, version: str) -> StoragePackage:
        started = time.monotonic()
        data, etag = await self._download(pid, version)
        actual = "sha256:" + hashlib.sha256(data).hexdigest()
        if etag is not None and etag != actual:
            raise digest_mismatch(f"registry ETag {etag} does not match the archive bytes ({actual})")
        try:
            pkg = await asyncio.to_thread(package_from_archive, data, self.limits.archive_limits())
        except DependencyNotAllowed as exc:
            raise JaneError(
                str(exc),
                code="dependency_not_allowed",
                errors=[FieldError(pointer="/handler", message=str(exc))],
            ) from exc
        except ValueError as exc:
            raise ValidationFailed(
                f"registry archive of {pid}@{version}: {exc}",
                errors=[FieldError(pointer="/handler", message=str(exc))],
            ) from exc
        self.downloads += 1
        if (pkg.package_id, pkg.version) == (pid, version):
            # only an archive consistent with its registry address is reused for later requests
            self._remember(pkg)
        log.info(
            "storage package downloaded from the registry",
            extra={
                "package_id": pid,
                "version": version,
                "digest": pkg.digest,
                "size_bytes": len(data),
                "duration_ms": int((time.monotonic() - started) * 1000),
            },
        )
        return pkg

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/zip"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        ctx = current_context()
        if trace_id := ctx.get("trace_id"):
            headers[TRACEPARENT] = child_traceparent(str(trace_id))
        if request_id := ctx.get("request_id"):
            headers["X-Request-ID"] = str(request_id)
        return headers

    async def _download(self, pid: str, version: str) -> tuple[bytes, str | None]:
        lim = self.limits
        path = f"/v1/packages/{quote(pid, safe='')}/versions/{quote(version, safe='')}/archive"
        timeout = httpx.Timeout(
            lim.registry_request_timeout_ms / 1000, connect=lim.registry_connect_timeout_ms / 1000
        )
        try:
            async with (
                asyncio.timeout(lim.registry_request_timeout_ms / 1000),
                httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=timeout,
                    follow_redirects=False,
                    trust_env=False,
                    transport=self._transport,
                ) as client,
                client.stream("GET", path, headers=self._headers()) as response,
            ):
                self._check_status(response.status_code, pid, version)
                declared = response.headers.get("content-length", "")
                if declared.isdigit() and int(declared) > lim.max_archive_bytes:
                    raise self._too_large(pid, version)
                buf = bytearray()
                async for chunk in response.aiter_bytes():
                    buf.extend(chunk)
                    if len(buf) > lim.max_archive_bytes:
                        raise self._too_large(pid, version)
                return bytes(buf), _etag(response.headers.get("etag"))
        except TimeoutError as exc:
            raise UpstreamUnavailable(
                f"registry did not deliver {pid}@{version} within "
                f"packages.registry_request_timeout_ms={lim.registry_request_timeout_ms}",
                retryable=True,
            ) from exc
        except httpx.HTTPError as exc:
            raise UpstreamUnavailable(
                f"registry did not respond: {type(exc).__name__}", retryable=True
            ) from exc

    def _too_large(self, pid: str, version: str) -> JaneError:
        limit = self.limits.max_archive_bytes
        return JaneError(
            f"registry archive of {pid}@{version} exceeds packages.max_archive_bytes={limit}",
            code="limit_exceeded",
            errors=[FieldError(pointer="/handler", message=f"archive larger than {limit} bytes")],
        )

    @staticmethod
    def _check_status(status: int, pid: str, version: str) -> None:
        if status == 200:
            return
        if status == 404:
            raise NotFound(f"{pid}@{version}", title="Package version not found")
        if 300 <= status < 400:
            raise UpstreamUnavailable(
                f"registry answered HTTP {status}; redirects are not followed", retryable=False
            )
        if status in (401, 403):
            raise UpstreamUnavailable(
                f"registry refused the archive download (HTTP {status}); check JANE_STORAGE_REGISTRY_TOKEN",
                retryable=False,
            )
        raise UpstreamUnavailable(
            f"registry returned HTTP {status}", retryable=status == 429 or status >= 500
        )
