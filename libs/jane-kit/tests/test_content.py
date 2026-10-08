"""``jane_kit.content.ContentReader``: the ContentRef policy shared by llm, assistant and handler-runtime."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import os
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response, StreamingResponse
from starlette.routing import Route

from jane_kit.content import ContentReader, parse_host_allowlist
from jane_kit.errors import JaneError

PAYLOAD = b"<html>price 1299</html>"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(uri: str, data: bytes = PAYLOAD, **extra: Any) -> dict[str, Any]:
    return {
        "kind": "blob",
        "uri": uri,
        "media_type": "text/html",
        "size_bytes": len(data),
        "sha256": sha(data),
        **extra,
    }


def reader(**kwargs: Any) -> ContentReader:
    kwargs.setdefault("timeout_ms", 5_000)
    return ContentReader(settings_prefix="JANE_TEST_", **kwargs)


async def refused(r: ContentReader, ref: dict[str, Any], max_bytes: int = 1_000_000) -> JaneError:
    with pytest.raises(JaneError) as exc:
        await r.read(ref, max_bytes=max_bytes, limit="test.max_bytes")
    return exc.value


def code(err: JaneError) -> tuple[int, str]:
    return err.status, err.error_code


# ------------------------------------------------------------------------------------------------ inline
async def test_inline_utf8_and_base64_with_sha256() -> None:
    r = reader()
    text = {"kind": "inline", "media_type": "text/plain", "encoding": "utf-8", "data": "Ціна 1299"}
    assert await r.read(text, max_bytes=100) == "Ціна 1299".encode()
    b64 = {
        "kind": "inline",
        "media_type": "application/octet-stream",
        "encoding": "base64",
        "data": base64.b64encode(PAYLOAD).decode(),
        "sha256": sha(PAYLOAD),
    }
    assert await r.read(b64, max_bytes=100) == PAYLOAD
    no_encoding = {"kind": "inline", "media_type": "text/plain", "data": "x"}
    assert await r.read(no_encoding, max_bytes=1) == b"x"


async def test_inline_refusals() -> None:
    r = reader()
    base = {"kind": "inline", "media_type": "text/plain"}
    assert code(await refused(r, {**base, "encoding": "base64", "data": "not base64!"})) == (
        422,
        "validation_failed",
    )
    assert code(await refused(r, {**base, "encoding": "utf-16", "data": "x"})) == (422, "validation_failed")
    assert code(await refused(r, {**base, "data": "x", "sha256": "0" * 64})) == (422, "validation_failed")
    too_big = await refused(r, {**base, "data": "x" * 11}, max_bytes=10)
    assert code(too_big) == (422, "limit_exceeded")
    assert too_big.details == {"path": "test.max_bytes", "limit": 10}
    assert code(await refused(r, {"kind": "url", "data": "x"})) == (422, "validation_failed")


# ------------------------------------------------------------------------------------------------ file://
@pytest.fixture
def tree(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "root"
    (root / "sub").mkdir(parents=True)
    (root / "page.html").write_bytes(PAYLOAD)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_bytes(b"JANE_SECRET_X=value")
    return {"root": root, "outside": outside}


def symlink(link: Path, target: Path) -> None:
    try:
        os.symlink(target, link, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError) as exc:  # Windows without the symlink privilege
        pytest.skip(f"symlinks are not available here: {exc}")


async def test_file_is_disabled_without_roots(tree: dict[str, Path]) -> None:
    err = await refused(reader(), blob((tree["root"] / "page.html").as_uri()))
    assert code(err) == (422, "validation_failed")
    assert "JANE_TEST_BLOB_ROOTS" in str(err.detail)


async def test_file_inside_a_root_is_read(tree: dict[str, Path]) -> None:
    r = reader(blob_roots=[tree["root"]])
    assert await r.read(blob((tree["root"] / "page.html").as_uri()), max_bytes=1_000) == PAYLOAD
    # ``..`` that stays inside the root is fine: the resolved path is what counts.
    inside = (tree["root"] / "sub").as_uri() + "/../page.html"
    assert await r.read(blob(inside), max_bytes=1_000) == PAYLOAD


async def test_proc_self_environ_is_refused(tree: dict[str, Path]) -> None:
    for r in (reader(), reader(blob_roots=[tree["root"]])):
        err = await refused(r, blob("file:///proc/self/environ", b""))
        assert code(err) == (422, "validation_failed")
        assert "environ" not in str(err.detail) and "proc" not in str(err.detail)


async def test_paths_outside_the_roots_are_refused(tree: dict[str, Path]) -> None:
    r = reader(blob_roots=[tree["root"]])
    secret = tree["outside"] / "secret.txt"
    escape = (tree["root"] / "sub").as_uri() + "/../../outside/secret.txt"
    encoded = (tree["root"] / "sub").as_uri() + "/%2E%2E/%2E%2E/outside/secret.txt"
    for uri in (secret.as_uri(), escape, encoded, tree["root"].as_uri()):
        err = await refused(r, blob(uri, b"JANE_SECRET_X=value"))
        assert code(err) == (422, "validation_failed"), uri
        assert str(tree["outside"]) not in str(err.detail) and "secret" not in str(err.detail)


async def test_symlink_out_of_a_root_is_refused(tree: dict[str, Path]) -> None:
    symlink(tree["root"] / "link.txt", tree["outside"] / "secret.txt")
    symlink(tree["root"] / "linkdir", tree["outside"])
    r = reader(blob_roots=[tree["root"]])
    for uri in ((tree["root"] / "link.txt").as_uri(), (tree["root"] / "linkdir" / "secret.txt").as_uri()):
        assert code(await refused(r, blob(uri, b"JANE_SECRET_X=value"))) == (422, "validation_failed")
    # A symlink that stays inside the root reads its (resolved) target.
    symlink(tree["root"] / "alias.html", tree["root"] / "page.html")
    assert await r.read(blob((tree["root"] / "alias.html").as_uri()), max_bytes=1_000) == PAYLOAD


async def test_file_uri_forms_are_strict(tree: dict[str, Path]) -> None:
    r = reader(blob_roots=[tree["root"]])
    good = (tree["root"] / "page.html").as_uri()
    for uri in (
        good.replace("file:///", "file://evil-host/"),
        good + "?x=1",
        good + "#frag",
        "file:relative/page.html",
        good.replace("page.html", "page%00.html"),
    ):
        assert code(await refused(r, blob(uri))) == (422, "validation_failed"), uri


async def test_file_missing_size_and_digest(tree: dict[str, Path]) -> None:
    r = reader(blob_roots=[tree["root"]])
    missing = await refused(r, blob((tree["root"] / "nope.html").as_uri()))
    assert code(missing) == (404, "not_found")
    page = (tree["root"] / "page.html").as_uri()
    big = await refused(r, blob(page), max_bytes=5)
    assert code(big) == (422, "limit_exceeded")
    undeclared = {k: v for k, v in blob(page).items() if k != "size_bytes"}
    assert code(await refused(r, undeclared, max_bytes=5)) == (422, "limit_exceeded")  # file size checked
    assert code(await refused(r, blob(page, size_bytes=3))) == (422, "validation_failed")
    assert code(await refused(r, blob(page, sha256="0" * 64))) == (422, "validation_failed")
    assert code(await refused(r, blob("s3://bucket/key"))) == (422, "validation_failed")


# ------------------------------------------------------------------------------------------------ download_url
class Chunks(httpx.AsyncByteStream):
    """A response body streamed in chunks: no ``Content-Length`` unless the test sets one."""

    def __init__(self, chunks: int, size: int = 1_000) -> None:
        self.chunks, self.size = chunks, size
        self.sent = 0

    async def __aiter__(self) -> Any:
        for _ in range(self.chunks):
            self.sent += self.size
            yield b"x" * self.size


def mock(seen: list[httpx.Request], respond: Any) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        result: httpx.Response = respond(request)
        return result

    return httpx.MockTransport(handler)


def remote(url: str, data: bytes = PAYLOAD) -> dict[str, Any]:
    return blob("s3://transit/key", data, download_url=url)


async def test_download_from_an_allowed_host() -> None:
    seen: list[httpx.Request] = []
    t = mock(seen, lambda _: httpx.Response(200, content=PAYLOAD))
    r = reader(download_host_allowlist=["blobs.local", "gate:8080"], transport=t)
    assert await r.read(remote("https://blobs.local/k?X-Amz-Signature=abc"), max_bytes=1_000) == PAYLOAD
    assert await r.read(remote("http://gate:8080/e2e/gates/a/content"), max_bytes=1_000) == PAYLOAD
    assert [str(q.url.host) for q in seen] == ["blobs.local", "gate"]
    assert seen[0].headers["accept-encoding"] == "identity"


async def test_download_hosts_outside_the_allowlist_are_refused_before_any_request() -> None:
    seen: list[httpx.Request] = []
    t = mock(seen, lambda _: httpx.Response(200, content=PAYLOAD))
    default = await refused(reader(transport=t), remote("http://gate:8080/x"))
    assert code(default) == (422, "validation_failed") and "JANE_TEST_DOWNLOAD_HOST_ALLOWLIST" in str(
        default.detail
    )
    r = reader(download_host_allowlist=["gate:8080"], transport=t)
    for url in (
        "http://gate:9090/x",  # another port
        "http://169.254.169.254/latest/meta-data/",
        "http://user:pw@gate:8080/x",
        "ftp://gate:8080/x",
        "file:///etc/passwd",
        "http://[::1]:8080/x",
        "http://gate:8080/x#frag",
        "http://gate:8080/a b",
        "http:\\\\gate:8080\\x",
    ):
        assert code(await refused(r, remote(url))) == (422, "validation_failed"), url
    assert seen == []


async def test_redirects_are_not_followed() -> None:
    seen: list[httpx.Request] = []
    t = mock(seen, lambda _: httpx.Response(302, headers={"Location": "http://169.254.169.254/x"}))
    err = await refused(reader(download_host_allowlist=["gate"], transport=t), remote("http://gate/x"))
    assert code(err) == (502, "upstream_unavailable") and err.retryable is False
    assert len(seen) == 1 and "169.254" not in str(err.detail)


async def test_download_size_limit_and_statuses() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/big":
            return httpx.Response(200, content=b"x" * 5_000)
        if path == "/declared":
            return httpx.Response(200, content=b"x", headers={"Content-Length": "999999"})
        if path == "/gzip":
            return httpx.Response(200, content=PAYLOAD, headers={"Content-Encoding": "gzip"})
        return httpx.Response(int(path.strip("/")))

    r = reader(download_host_allowlist=["gate"], transport=mock([], respond))
    big = await refused(r, remote("http://gate/big", b"x" * 10), max_bytes=1_000)
    assert code(big) == (422, "limit_exceeded")
    assert code(await refused(r, remote("http://gate/declared", b"x"), max_bytes=1_000)) == (
        422,
        "limit_exceeded",
    )
    assert code(await refused(r, remote("http://gate/big", b"x" * 5_000), max_bytes=1_000)) == (
        422,
        "limit_exceeded",
    )  # declared size_bytes above the limit: refused before the download
    assert code(await refused(r, remote("http://gate/gzip"))) == (502, "upstream_unavailable")
    assert code(await refused(r, remote("http://gate/404"))) == (404, "not_found")
    server = await refused(r, remote("http://gate/503"))
    assert code(server) == (502, "upstream_unavailable") and server.retryable is True
    client = await refused(r, remote("http://gate/403"))
    assert code(client) == (502, "upstream_unavailable") and client.retryable is False


@pytest.mark.parametrize(
    "content_length", [None, "10"], ids=["no-content-length", "understated-content-length"]
)
async def test_streamed_body_is_cut_at_the_limit(content_length: str | None) -> None:
    """Without (or with a false) ``Content-Length`` only the count while streaming stops the download."""
    body = Chunks(chunks=100)  # 100 000 bytes, far above the limit
    headers = {"Content-Length": content_length} if content_length else {}
    t = mock([], lambda _: httpx.Response(200, headers=headers, stream=body))
    r = reader(download_host_allowlist=["gate"], transport=t)
    # size_bytes understated on purpose, so neither the reference nor a header refuses it before the stream.
    err = await refused(r, remote("http://gate/stream", b"x" * 10), max_bytes=5_000)
    assert code(err) == (422, "limit_exceeded")
    assert err.details == {"path": "test.max_bytes", "limit": 5_000}
    assert body.sent <= 6_000  # stopped right after the limit, not after reading the whole body


async def test_internationalized_hosts_are_compared_in_punycode() -> None:
    seen: list[httpx.Request] = []
    t = mock(seen, lambda _: httpx.Response(200, content=PAYLOAD))
    r = reader(download_host_allowlist=["xn--bcher-kva.example"], transport=t)
    assert await r.read(remote("http://xn--bcher-kva.example/k"), max_bytes=1_000) == PAYLOAD
    assert seen[0].url.raw_host == b"xn--bcher-kva.example"
    for url in (
        "http://bücher.example/k",
        "http://xn--bcher-kva.example.evil/k",
        "http://bcher-kva.example/k",
    ):
        assert code(await refused(r, remote(url))) == (422, "validation_failed"), url
    other = reader(download_host_allowlist=["bücher.example".encode("idna").decode()], transport=t)
    assert other.download_hosts == {("xn--bcher-kva.example", None)}
    assert len(seen) == 1


async def test_download_timeout_is_bounded() -> None:
    async def slow(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(5)
        return httpx.Response(200, content=PAYLOAD)

    r = reader(download_host_allowlist=["gate"], timeout_ms=100, transport=httpx.MockTransport(slow))
    started = time.monotonic()
    err = await refused(r, remote("http://gate/slow"))
    assert code(err) == (502, "upstream_unavailable") and err.retryable is True
    assert time.monotonic() - started < 3


# Real HTTP: the policy holds on the network path too (no proxy from the environment, no redirect to another host).
@pytest.fixture
def servers() -> Iterator[tuple[int, int, list[str]]]:
    hits: list[str] = []

    async def page(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(PAYLOAD, media_type="text/html")

    async def redirect(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return RedirectResponse(f"http://localhost:{ports[1]}/page", status_code=302)

    async def stream(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")

        async def body() -> Any:
            for _ in range(200):  # 200 000 bytes, chunked transfer encoding: no Content-Length
                yield b"x" * 1_000

        return StreamingResponse(body(), media_type="text/html")

    routes = [Route("/page", page), Route("/redirect", redirect), Route("/stream", stream)]
    started: list[uvicorn.Server] = []
    ports: list[int] = []
    for _ in range(2):
        server = uvicorn.Server(
            uvicorn.Config(Starlette(routes=routes), host="127.0.0.1", port=0, log_level="warning")
        )
        threading.Thread(target=server.run, daemon=True).start()
        while not server.started:
            time.sleep(0.02)
        ports.append(server.servers[0].sockets[0].getsockname()[1])
        started.append(server)
    yield ports[0], ports[1], hits
    for server in started:
        server.should_exit = True


async def test_real_http_ignores_proxy_env_and_redirects(
    servers: tuple[int, int, list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second, hits = servers
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")  # would break every request if it were used
    monkeypatch.setenv("ALL_PROXY", "http://127.0.0.1:9")
    r = reader(download_host_allowlist=[f"127.0.0.1:{first}", "localhost"])
    assert await r.read(remote(f"http://127.0.0.1:{first}/page"), max_bytes=1_000) == PAYLOAD
    err = await refused(r, remote(f"http://127.0.0.1:{first}/redirect"))
    assert code(err) == (502, "upstream_unavailable")
    assert hits == [f"{first}/page", f"{first}/redirect"]  # the other host was never contacted
    assert second != first
    # A chunked body without Content-Length is cut while streaming (size_bytes understated on purpose).
    big = await refused(r, remote(f"http://127.0.0.1:{first}/stream", b"x" * 10), max_bytes=50_000)
    assert code(big) == (422, "limit_exceeded") and big.details == {"path": "test.max_bytes", "limit": 50_000}


def test_allowlist_entries_are_validated() -> None:
    assert parse_host_allowlist(["Gate", "gate:8080"]) == {("gate", None), ("gate", 8080)}
    for bad in ("http://gate", "gate:0", "gate:99999", "*.example.com", "gate.", "", "[::1]:80"):
        with pytest.raises(ValueError, match="hostname"):
            parse_host_allowlist([bad])
    with pytest.raises(ValueError, match="positive"):
        ContentReader(timeout_ms=0)
