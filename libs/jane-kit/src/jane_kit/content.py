"""Reading ``ContentRef`` values (ADR-0004) under an explicit operator policy.

A ``ContentRef`` arrives in a request, so every reference is untrusted input. :class:`ContentReader` reads:

* ``inline`` - ``data`` as ``utf-8`` text (default) or strict ``base64`` (RFC 4648);
* ``blob`` with ``download_url`` - only ``http``/``https`` to a host on the allowlist (``hostname`` = any port,
  ``hostname:port`` = that port; empty by default, so downloads are disabled). Hosts are compared in their ASCII
  (wire) form - an internationalized name is allowed by its punycode ``xn--...`` entry, the host actually
  connected to; a URL with non-ASCII characters is refused. Redirects are not followed, proxies
  and ``.netrc`` of the environment are ignored (``trust_env=False``), only an unencoded body is accepted
  (``Accept-Encoding: identity``), the size limit is enforced while streaming and the whole download is bounded by
  the timeout;
* ``blob`` ``file:///...`` - only strictly inside one of the configured roots (none by default, so ``file://`` is
  disabled). The path is resolved first (``..`` and symlinks), the *resolved* path is checked against the
  resolved roots and the resolved file is the one opened (``O_NOFOLLOW`` where the platform has it; on POSIX the
  opened file must be the checked one). Only regular files are read; ``file://host/...`` and UNC paths are refused;
* other blobs (``s3://`` without ``download_url``) - refused: the reader holds no storage credentials (ADR-0006).

The checks after reading: ``size_bytes`` of a blob must match (it is also checked against the limit before
reading), ``sha256`` must match when given (contract: every consumer verifies it).

Errors are :class:`~jane_kit.errors.JaneError` (codes of ``contracts/docs/errors.md``); ``detail`` never carries a
file path, a resolved path or content:

* invalid reference, refused by the policy, ``sha256``/``size_bytes`` mismatch - ``422 validation_failed``;
* larger than the limit - ``422 limit_exceeded`` (``details.path`` = name of the limit, ``details.limit`` = bytes);
* missing file, ``download_url`` answered 404/410 - ``404 not_found``;
* download failed (network, timeout, HTTP 5xx/408/429, I/O error) - ``502 upstream_unavailable``, retryable;
  redirect, other HTTP 4xx, encoded body - ``502 upstream_unavailable``, not retryable.

Settings of a service (env prefix ``JANE_<SERVICE>_``): ``BLOB_ROOTS`` (JSON list of directories) and
``DOWNLOAD_HOST_ALLOWLIST`` (JSON list of ``hostname[:port]``); validate the allowlist with
:func:`parse_host_allowlist` so that a typo stops the service at start.

**Writing** (the producer part of ADR-0004, R18):

* :func:`inline_ref` - an ``inline`` reference (``utf-8`` text when asked and decodable, else ``base64``) with
  ``size_bytes`` and ``sha256``;
* :class:`FileTransitStore` - transit blobs of one producer on a local/shared directory
  (``<root>/<producer>/<YYYY>/<MM>/<DD>/<name><ext>``, written atomically, ``file://`` URIs, single node or a shared
  volume) and the producer's cleaner (:meth:`FileTransitStore.cleanup`: files older than
  ``limits.transfer.transit_ttl_seconds``);
* :class:`ContentWriter` - the delivery decision of a producer: ``auto`` (inline up to
  ``limits.transfer.inline_max_bytes``, else a transit blob with ``store: transit`` and ``expires_at``), ``inline``
  (larger content is :class:`ContentTooLarge`, ``limit_exceeded``) or ``blob`` (always transit). Without a transit
  store a blob cannot be written: :class:`ContentTooLarge` with a hint to configure one (ADR-0004 §7).

Persistent objects (``store: persistent``) are written only by the storage handler with its adapters; S3/MinIO
transit (bucket lifecycle) is not implemented by this module.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import errno
import hashlib
import os
import re
import secrets
import stat
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit
from urllib.request import url2pathname

import httpx

from jane_kit.errors import LimitExceeded, NotFound, UpstreamUnavailable, ValidationFailed
from jane_kit.secrets import parse_host_port

__all__ = [
    "ContentReader",
    "ContentTooLarge",
    "ContentWriter",
    "FileTransitStore",
    "inline_ref",
    "parse_host_allowlist",
]

_UNSAFE_URL = re.compile(r"[^\x21-\x7e]|\\")
"""Anything but printable ASCII, or a backslash: URL parsers disagree on such values."""
_DEFAULT_PORTS = {"http": 80, "https": 443}
_MAX_URL = 8192
_OPEN_FLAGS = (
    os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
)
_REFUSED_ERRNOS = {errno.ELOOP, errno.EACCES, errno.EPERM, errno.EISDIR, errno.ENXIO}


def _host_port(value: str) -> tuple[str, int | None] | None:
    """Strict ``hostname[:port]`` -> ``(lower-case host, port)``; anything else -> ``None``."""
    return parse_host_port(value)


def parse_host_allowlist(entries: Iterable[str]) -> frozenset[tuple[str, int | None]]:
    """``hostname`` (any port) or ``hostname:port`` entries; anything else raises ``ValueError``."""
    allowed: set[tuple[str, int | None]] = set()
    for entry in entries:
        parsed = _host_port(entry) if isinstance(entry, str) else None
        if parsed is None:
            raise ValueError(f"download host allowlist entry {entry!r} must be hostname or hostname:port")
        allowed.add(parsed)
    return frozenset(allowed)


class ContentReader:
    """Reads ``ContentRef`` values under the policy of one service (see the module docstring).

    ``timeout_ms`` bounds a whole download (and each network operation); ``connect_timeout_ms`` (default: the
    same) bounds establishing the connection. ``settings_prefix`` (``"JANE_LLM_"``) only names the settings in
    error messages. ``transport`` replaces the network in tests.
    """

    def __init__(
        self,
        *,
        timeout_ms: int,
        blob_roots: Iterable[Path | str] = (),
        download_host_allowlist: Iterable[str] = (),
        connect_timeout_ms: int | None = None,
        settings_prefix: str = "",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if timeout_ms <= 0 or (connect_timeout_ms is not None and connect_timeout_ms <= 0):
            raise ValueError("content reader timeouts must be positive")
        self.blob_roots = tuple(Path(root).resolve() for root in blob_roots)
        self.download_hosts = parse_host_allowlist(download_host_allowlist)
        self.timeout_s = timeout_ms / 1000
        self.connect_timeout_s = min(connect_timeout_ms or timeout_ms, timeout_ms) / 1000
        self.roots_setting = f"{settings_prefix}BLOB_ROOTS"
        self.allowlist_setting = f"{settings_prefix}DOWNLOAD_HOST_ALLOWLIST"
        self._transport = transport

    async def read(self, ref: Mapping[str, Any], *, max_bytes: int, limit: str = "max_bytes") -> bytes:
        """Bytes of ``ref``; ``max_bytes`` comes from the service's limits, ``limit`` is its name for errors."""
        if not isinstance(ref, Mapping):
            raise ValidationFailed("content reference must be an object")
        kind = ref.get("kind")
        if kind == "inline":
            raw = self._inline(ref, max_bytes, limit)
        elif kind == "blob":
            declared = ref.get("size_bytes")
            if declared is not None:
                if isinstance(declared, bool) or not isinstance(declared, int) or declared < 0:
                    raise ValidationFailed("blob size_bytes must be a non-negative integer")
                if declared > max_bytes:
                    raise _too_large(max_bytes, limit)
            raw = await self._blob(ref, max_bytes, limit)
            if declared is not None and declared != len(raw):
                raise ValidationFailed("blob size_bytes does not match the content")
        else:
            raise ValidationFailed("content kind must be inline or blob")
        expected = ref.get("sha256")
        if expected is not None and (
            not isinstance(expected, str) or hashlib.sha256(raw).hexdigest() != expected.lower()
        ):
            raise ValidationFailed("content sha256 does not match the content reference")
        return raw

    # ------------------------------------------------------------------------------------------------ inline
    @staticmethod
    def _inline(ref: Mapping[str, Any], max_bytes: int, limit: str) -> bytes:
        data = ref.get("data")
        if not isinstance(data, str):
            raise ValidationFailed("inline content has no data string")
        encoding = ref.get("encoding") or "utf-8"
        if encoding == "base64":
            if len(data) > 4 * (max_bytes // 3 + 1) + 4:
                raise _too_large(max_bytes, limit)
            try:
                raw = base64.b64decode(data, validate=True)
            except (binascii.Error, ValueError):
                raise ValidationFailed("inline content is not valid base64") from None
        elif encoding == "utf-8":
            if len(data) > max_bytes:
                raise _too_large(max_bytes, limit)
            try:
                raw = data.encode("utf-8")
            except UnicodeEncodeError:
                raise ValidationFailed("inline content is not valid UTF-8 text") from None
        else:
            raise ValidationFailed("inline content encoding must be utf-8 or base64")
        if len(raw) > max_bytes:
            raise _too_large(max_bytes, limit)
        return raw

    # ------------------------------------------------------------------------------------------------ blob
    async def _blob(self, ref: Mapping[str, Any], max_bytes: int, limit: str) -> bytes:
        url = ref.get("download_url")
        if url is not None and url != "":
            return await self._download(url, max_bytes, limit)
        uri = ref.get("uri")
        if not isinstance(uri, str) or not uri:
            raise ValidationFailed("blob has neither download_url nor uri")
        if urlsplit(uri).scheme.lower() == "file":
            return await asyncio.to_thread(self._read_file, uri, max_bytes, limit)
        raise ValidationFailed(
            "blob without download_url can be read only from file:// (this service holds no storage credentials)"
        )

    # ------------------------------------------------------------------------------------------------ file://
    def _read_file(self, uri: str, max_bytes: int, limit: str) -> bytes:
        if not self.blob_roots:
            raise ValidationFailed(f"file:// content is disabled: no allowed roots ({self.roots_setting})")
        outside = ValidationFailed(f"file:// content is outside the allowed roots ({self.roots_setting})")
        path = _file_path(uri)
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError, ValueError):
            raise outside from None
        if not any(resolved != root and resolved.is_relative_to(root) for root in self.blob_roots):
            raise outside
        try:
            return _read_regular(resolved, max_bytes, limit)
        except (FileNotFoundError, NotADirectoryError):
            raise NotFound("file:// content not found") from None
        except OSError as exc:
            if exc.errno in _REFUSED_ERRNOS:
                raise ValidationFailed(
                    "file:// content cannot be read (not a readable regular file)"
                ) from None
            raise UpstreamUnavailable("file:// content cannot be read (I/O error)", retryable=True) from exc

    # ------------------------------------------------------------------------------------------------ download
    def _download_target(self, url: object) -> tuple[httpx.URL, str]:
        bad = ValidationFailed("download_url must be an http(s) URL without userinfo, fragment or whitespace")
        if not isinstance(url, str) or len(url) > _MAX_URL or _UNSAFE_URL.search(url):
            raise bad
        try:
            target = httpx.URL(url)
        except (httpx.InvalidURL, ValueError):
            raise bad from None
        if target.scheme not in _DEFAULT_PORTS or not target.host or target.userinfo or target.fragment:
            raise bad
        # raw_host is the ASCII (punycode) host httpx connects to; ``host`` would be the decoded IDN form.
        host = _host_port(target.raw_host.decode("ascii", errors="replace"))
        if host is None or host[1] is not None:
            raise ValidationFailed("download_url host must be a plain hostname")
        port = target.port or _DEFAULT_PORTS[target.scheme]
        name = f"{host[0]}:{port}"
        if (host[0], None) not in self.download_hosts and (host[0], port) not in self.download_hosts:
            raise ValidationFailed(f"download_url host {name} is not allowed ({self.allowlist_setting})")
        return target, name

    async def _download(self, url: object, max_bytes: int, limit: str) -> bytes:
        target, name = self._download_target(url)
        timeout = httpx.Timeout(self.timeout_s, connect=self.connect_timeout_s)
        try:
            async with (
                asyncio.timeout(self.timeout_s),
                httpx.AsyncClient(
                    timeout=timeout, follow_redirects=False, trust_env=False, transport=self._transport
                ) as client,
                client.stream("GET", target, headers={"Accept-Encoding": "identity"}) as resp,
            ):
                _check_response(resp, name, max_bytes, limit)
                buf = bytearray()
                # Identity only (checked above), so no decoder can expand the body beyond what is counted.
                async for chunk in resp.aiter_bytes():
                    buf.extend(chunk)
                    if len(buf) > max_bytes:
                        raise _too_large(max_bytes, limit)
                return bytes(buf)
        except TimeoutError:
            raise UpstreamUnavailable(f"download_url {name} timed out", retryable=True) from None
        except httpx.HTTPError as exc:
            raise UpstreamUnavailable(
                f"download_url {name} failed: {type(exc).__name__}", retryable=True
            ) from exc


def _too_large(max_bytes: int, limit: str) -> LimitExceeded:
    return LimitExceeded(
        f"content exceeds {limit}={max_bytes} bytes", details={"path": limit, "limit": max_bytes}
    )


def _file_path(uri: str) -> Path:
    bad = ValidationFailed("file:// URI must be file:///<absolute path> without host, query or fragment")
    parts = urlsplit(uri)
    if parts.netloc not in ("", "localhost") or parts.query or parts.fragment:
        raise bad
    try:
        path = Path(url2pathname(parts.path))
    except (OSError, ValueError):
        raise bad from None
    text = str(path)
    # A UNC or device path (\\server\share, \\?\...) would make Windows contact another host while resolving.
    if "\x00" in text or not path.is_absolute() or path.drive.startswith(("\\\\", "//")):
        raise bad
    return path


def _read_regular(path: Path, max_bytes: int, limit: str) -> bytes:
    """Read the resolved ``path``: a regular file, not swapped for a symlink or another file since the check."""
    checked = os.stat(path)
    if not stat.S_ISREG(checked.st_mode):
        raise ValidationFailed("file:// content is not a regular file")
    if checked.st_size > max_bytes:
        raise _too_large(max_bytes, limit)
    fd = os.open(path, _OPEN_FLAGS)
    with os.fdopen(fd, "rb") as f:
        opened = os.fstat(f.fileno())
        same = os.name != "posix" or (opened.st_dev, opened.st_ino) == (checked.st_dev, checked.st_ino)
        if not stat.S_ISREG(opened.st_mode) or not same:
            raise ValidationFailed("file:// content changed while it was opened")
        data = f.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise _too_large(max_bytes, limit)
    return data


def _check_response(resp: httpx.Response, name: str, max_bytes: int, limit: str) -> None:
    status = resp.status_code
    if 300 <= status < 400:
        raise UpstreamUnavailable(
            f"download_url {name} answered with a redirect (HTTP {status}); redirects are not followed",
            retryable=False,
        )
    if status in (404, 410):
        raise NotFound(f"download_url {name}: content not found (HTTP {status})")
    if not 200 <= status < 300:
        raise UpstreamUnavailable(
            f"download_url {name} returned HTTP {status}", retryable=status >= 500 or status in (408, 429)
        )
    if resp.headers.get("content-encoding", "identity").strip().lower() not in ("", "identity"):
        raise UpstreamUnavailable(
            f"download_url {name} answered with an encoded body; only Content-Encoding identity is accepted",
            retryable=False,
        )
    declared = resp.headers.get("content-length", "")
    if declared.isdigit() and int(declared) > max_bytes:
        raise _too_large(max_bytes, limit)


# ================================================================================================ writing (R18)
EXTENSIONS: Mapping[str, str] = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/json": ".json",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "application/zip": ".zip",
}
"""File extension of a transit blob by media type (``.bin`` otherwise); only a convenience for operators."""

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}")
"""Safe file name of a transit blob: no separators, no ``..``, no ``:`` (Windows)."""


class ContentTooLarge(LimitExceeded):
    """Content cannot be delivered: larger than ``transfer.inline_max_bytes`` with inline delivery, or a blob is
    needed and no transit store is configured (``limit_exceeded``, ADR-0004 §7)."""


def _rfc3339(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def inline_ref(
    body: bytes, media_type: str, *, text: bool = False, charset: str | None = None
) -> dict[str, Any]:
    """``inline`` ContentRef of ``body``: ``utf-8`` data when ``text`` and the bytes decode, else ``base64``."""
    ref: dict[str, Any] = {"kind": "inline", "media_type": media_type}
    if charset:
        ref["charset"] = charset
    decoded: str | None = None
    if text:
        try:
            decoded = body.decode("utf-8")
        except UnicodeDecodeError:
            decoded = None
    if decoded is not None:
        ref.update(encoding="utf-8", data=decoded)
    else:
        ref.update(encoding="base64", data=base64.b64encode(body).decode("ascii"))
    ref.update(size_bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    return ref


class FileTransitStore:
    """Transit blobs of one producer under ``<root>/<producer>/`` (``file://`` URIs; one node or a shared volume).

    The consumers read them only inside their configured ``BLOB_ROOTS`` (:class:`ContentReader`); the producer
    removes them after the TTL (:meth:`cleanup`, run by the producer's own periodic task).
    """

    def __init__(self, root: Path, producer: str) -> None:
        if not _NAME.fullmatch(producer):
            raise ValueError(f"invalid transit producer name {producer!r}")
        self.root = root.resolve()
        self.producer = producer

    @property
    def base(self) -> Path:
        return self.root / self.producer

    def put(self, name: str, body: bytes, media_type: str, now: datetime, *, reuse: bool = False) -> Path:
        """Write ``body`` atomically as ``<base>/<YYYY>/<MM>/<DD>/<name><ext>``.

        ``reuse`` (only for a content-addressed ``name``): an existing file of the same size is kept and only its
        time is refreshed, so the cleaner keeps it for another TTL.
        """
        if not _NAME.fullmatch(name):
            raise ValueError(f"invalid transit blob name {name!r}")
        folder = self.base / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
        path = folder / f"{name}{EXTENSIONS.get(media_type, '.bin')}"
        if reuse:
            try:
                if path.stat().st_size == len(body):
                    os.utime(path)
                    return path
            except FileNotFoundError:
                pass
        for attempt in range(2):
            folder.mkdir(parents=True, exist_ok=True)
            tmp = folder / f".{path.name}.{secrets.token_hex(6)}.tmp"
            try:
                tmp.write_bytes(body)
                os.replace(tmp, path)
                return path
            except FileNotFoundError:
                if attempt:  # the cleaner removed the (empty) folder in between: create it once more
                    raise
            finally:
                tmp.unlink(missing_ok=True)
        raise AssertionError("unreachable")  # pragma: no cover

    def cleanup(self, ttl_seconds: float) -> int:
        """Remove this producer's transit files older than ``ttl_seconds`` (and empty day folders); returns the
        number of files removed. Files being written are newer than the TTL, so they are never touched."""
        cutoff = time.time() - ttl_seconds
        removed = 0
        if not self.base.is_dir():
            return 0
        for path in sorted(self.base.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            try:
                if path.is_symlink() or path.is_file():
                    if path.lstat().st_mtime < cutoff:
                        path.unlink(missing_ok=True)
                        removed += 1
                elif path.is_dir() and not any(path.iterdir()) and path.lstat().st_mtime < cutoff:
                    path.rmdir()
            except OSError:
                continue  # removed or written concurrently (another instance, a new blob): next round
        return removed


@dataclass
class ContentWriter:
    """Delivery of a producer's content as ContentRef (see the module docstring)."""

    mode: Literal["auto", "inline", "blob"]
    inline_max_bytes: int
    transit_ttl_seconds: int
    store: FileTransitStore | None

    def ref(
        self,
        body: bytes,
        media_type: str,
        name: str,
        now: datetime | None = None,
        *,
        text: bool = False,
        charset: str | None = None,
    ) -> dict[str, Any]:
        """ContentRef of ``body``; ``name`` names the transit blob if one is written (unique per content)."""
        now = now or datetime.now(UTC)
        too_big = len(body) > self.inline_max_bytes
        if self.mode == "inline" and too_big:
            raise ContentTooLarge(
                f"{len(body)} bytes > transfer.inline_max_bytes={self.inline_max_bytes} (content_delivery=inline)",
                details={"path": "transfer.inline_max_bytes", "limit": self.inline_max_bytes},
            )
        if self.mode == "blob" or (self.mode == "auto" and too_big):
            if self.store is None:
                raise ContentTooLarge(
                    f"{len(body)} bytes > transfer.inline_max_bytes={self.inline_max_bytes} and no blob store "
                    "configured"
                    if self.mode == "auto"
                    else "content_delivery=blob but no blob store configured",
                    details={"path": "transfer.inline_max_bytes", "limit": self.inline_max_bytes},
                )
            return self.blob(body, media_type, name, now, charset=charset)
        return inline_ref(body, media_type, text=text, charset=charset)

    def blob(
        self, body: bytes, media_type: str, name: str, now: datetime, *, charset: str | None = None
    ) -> dict[str, Any]:
        """A transit blob of ``body`` (the store must be configured)."""
        if self.store is None:
            raise ContentTooLarge("no blob store configured")
        path = self.store.put(name, body, media_type, now)
        ref: dict[str, Any] = {
            "kind": "blob",
            "uri": path.as_uri(),
            "media_type": media_type,
            "size_bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "store": "transit",
            "expires_at": _rfc3339(now + timedelta(seconds=self.transit_ttl_seconds)),
        }
        if charset:
            ref["charset"] = charset
        return ref
