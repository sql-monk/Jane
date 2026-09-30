"""Reading ``ContentRef`` (inline / blob) with sha256 and size checks (ADR-0004).

* ``inline`` — ``utf-8`` or ``base64`` data;
* ``blob`` ``file:///…`` — local file below the configured transit directory;
* ``blob`` ``s3://bucket/key`` — through the configured transit connection (kind ``s3``/``minio``);
* otherwise ``download_url`` (pre-signed HTTP(S) link on the configured allowlist).
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

import httpx

from jane_contracts.storage_adapter import ResolvedConnection

from .policy import Address, ConnectionPolicy, parse_host_port

__all__ = ["ContentError", "ContentReader"]


class ContentError(Exception):
    """Content cannot be read or is inconsistent. ``retryable`` — worth retrying later."""

    def __init__(self, message: str, *, retryable: bool, kind: str = "execution_error") -> None:
        super().__init__(message)
        self.retryable = retryable
        self.kind = kind


TransitResolver = Callable[[], Awaitable[ResolvedConnection | None]]


class ContentReader:
    def __init__(
        self,
        *,
        max_bytes: int,
        request_timeout_ms: int,
        transit: TransitResolver | None = None,
        files_dir: Path | None = None,
        download_host_allowlist: list[str] | tuple[str, ...] = (),
    ) -> None:
        self.max_bytes = max_bytes
        self.request_timeout_ms = request_timeout_ms
        self._transit = transit
        self._files_dir = files_dir
        self._download_policy = ConnectionPolicy(host_allowlist=download_host_allowlist)

    async def read(self, ref: Mapping[str, Any]) -> bytes:
        kind = ref.get("kind")
        if kind == "inline":
            data = self._inline(ref)
        elif kind == "blob":
            data = await self._blob(ref)
        else:
            raise ContentError(f"unsupported content kind {kind!r}", retryable=False)
        if len(data) > self.max_bytes:
            raise ContentError(
                f"content of {len(data)} bytes exceeds objects.max_object_bytes={self.max_bytes}",
                retryable=False,
                kind="resource_exceeded",
            )
        expected = ref.get("sha256")
        if expected and hashlib.sha256(data).hexdigest() != expected:
            raise ContentError("content sha256 mismatch", retryable=False)
        size = ref.get("size_bytes")
        if size is not None and int(size) != len(data):
            raise ContentError(f"content size {len(data)} != size_bytes {size}", retryable=False)
        return data

    @staticmethod
    def _inline(ref: Mapping[str, Any]) -> bytes:
        data = str(ref.get("data", ""))
        if ref.get("encoding") == "base64":
            try:
                return base64.b64decode(data, validate=True)
            except binascii.Error as exc:
                raise ContentError(f"invalid base64 content: {exc}", retryable=False) from exc
        return data.encode("utf-8")

    async def _blob(self, ref: Mapping[str, Any]) -> bytes:
        uri = str(ref.get("uri", ""))
        parsed = urlparse(uri)
        if parsed.scheme == "file":
            if self._files_dir is None:
                raise ContentError("local blob reading is disabled", retryable=False)
            if parsed.netloc or parsed.query or parsed.fragment or not parsed.path.startswith("/"):
                raise ContentError("invalid local blob URI", retryable=False)
            try:
                path = Path(url2pathname(unquote(parsed.path)))
                return await asyncio.to_thread(self._read_allowed_file, path)
            except FileNotFoundError as exc:
                raise ContentError("local blob not found", retryable=False) from exc
            except OSError as exc:
                raise ContentError("cannot read local blob", retryable=True, kind="connection_error") from exc
        if parsed.scheme == "s3" and (parsed.query or parsed.fragment):
            raise ContentError("invalid s3 blob URI", retryable=False)
        if parsed.scheme == "s3" and self._transit is not None:
            conn = await self._transit()
            if conn is not None:
                return await asyncio.to_thread(self._read_s3, conn, parsed.netloc, parsed.path.lstrip("/"))
        if url := ref.get("download_url"):
            return await self._download(str(url))
        raise ContentError("no transit connection configured and no download_url", retryable=False)

    def _read_allowed_file(self, path: Path) -> bytes:
        assert self._files_dir is not None
        base = self._files_dir.resolve(strict=True)
        path = path.resolve(strict=True)
        if path == base or not path.is_relative_to(base) or not path.is_file():
            raise ContentError("local blob is outside the configured directory", retryable=False)
        size = path.stat().st_size
        if size > self.max_bytes:
            raise ContentError(
                f"blob of {size} bytes exceeds objects.max_object_bytes={self.max_bytes}",
                retryable=False,
                kind="resource_exceeded",
            )
        return path.read_bytes()

    def _read_s3(self, conn: ResolvedConnection, bucket: str, key: str) -> bytes:
        import boto3  # type: ignore[import-untyped]
        from botocore.config import Config  # type: ignore[import-untyped]
        from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]

        params = conn.params
        timeout = self.request_timeout_ms / 1000
        client = boto3.client(
            "s3",
            endpoint_url=params.get("endpoint"),
            region_name=params.get("region", "us-east-1"),
            aws_access_key_id=conn.secrets.get("access_key"),
            aws_secret_access_key=conn.secrets.get("secret_key"),
            config=Config(connect_timeout=timeout, read_timeout=timeout, s3={"addressing_style": "path"}),
        )
        try:
            obj = client.get_object(Bucket=bucket, Key=key)
            if int(obj.get("ContentLength", 0)) > self.max_bytes:
                raise ContentError(
                    "blob exceeds objects.max_object_bytes", retryable=False, kind="resource_exceeded"
                )
            return bytes(obj["Body"].read())
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            missing = code in {"NoSuchKey", "404", "NoSuchBucket"}
            raise ContentError(
                "s3 blob not found" if missing else "s3 blob read failed", retryable=not missing
            ) from exc
        except BotoCoreError as exc:
            raise ContentError("s3 blob read failed", retryable=True, kind="connection_error") from exc

    async def _download(self, url: str) -> bytes:
        if not self._download_allowed(url):
            raise ContentError("download_url host is not allowed", retryable=False)
        timeout = self.request_timeout_ms / 1000
        try:
            async with (
                httpx.AsyncClient(timeout=timeout, follow_redirects=False, trust_env=False) as client,
                client.stream("GET", url) as resp,
            ):
                if 300 <= resp.status_code < 400:
                    raise ContentError("download_url redirect is not allowed", retryable=False)
                if resp.status_code >= 400:
                    raise ContentError(
                        f"download_url returned {resp.status_code}", retryable=resp.status_code >= 500
                    )
                chunks = []
                total = 0
                async for chunk in resp.aiter_bytes():
                    total += len(chunk)
                    if total > self.max_bytes:
                        raise ContentError(
                            "download exceeds objects.max_object_bytes",
                            retryable=False,
                            kind="resource_exceeded",
                        )
                    chunks.append(chunk)
                return b"".join(chunks)
        except httpx.HTTPError as exc:
            raise ContentError("download failed", retryable=True, kind="connection_error") from exc

    def _download_allowed(self, url: str) -> bool:
        if len(url) > 8192 or any(ch.isspace() or ord(ch) < 32 for ch in url) or "\\" in url:
            return False
        try:
            parsed = httpx.URL(url)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.host
                or parsed.userinfo
                or parsed.fragment
            ):
                return False
            host = parse_host_port(parsed.host)
            if host is None or host[1] is not None:
                return False
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            return self._download_policy.host_allowed(Address("/download_url", host[0], port))
        except (ValueError, httpx.InvalidURL):
            return False
