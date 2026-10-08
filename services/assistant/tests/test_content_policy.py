"""ContentRef policy of material content (WP-01h): ``file://`` only under ``JANE_ASSISTANT_BLOB_ROOTS``,
``download_url`` only to ``JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST`` hosts, no redirects, size from
``limits.content``; the ``http_json`` search provider takes its timeouts from ``limits.search``.

Driven through ``POST /v1/unknown-materials`` (material content of a request read inside a job); refused content
never reaches the LLM gateway.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import uvicorn
from assistant_fakes import World, world
from assistant_fakes.site import material
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from jane_assistant.app import build_search
from jane_assistant.content import material_bytes
from jane_assistant.settings import Settings, resolve_service_limits
from jane_kit.errors import JaneError

HTML = b"<html><body><h1>Spring meetup</h1><p>BLOB-MARKER-41c2</p></body></html>"
SECRET = b"JANE_SECRET_TOKEN=do-not-send\n"


def blob(uri: str, data: bytes = HTML, **extra: Any) -> dict[str, Any]:
    return {
        "kind": "blob",
        "uri": uri,
        "media_type": "text/html",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        **extra,
    }


def analyse(w: World, content: dict[str, Any], key: str) -> dict[str, Any]:
    m = material("https://shop.example.test/events/7", HTML.decode(), "shop-example")
    m["content"] = content
    body = {"source_id": "shop-example", "forward_unknown_to_llm": True, "material": m}
    r = w.api.post("/v1/unknown-materials", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 202, r.text
    return w.wait(r.json()["job_id"])


def refused(w: World, content: dict[str, Any], key: str, code: str) -> dict[str, Any]:
    requests = len(w.llm.requests)
    job = analyse(w, content, key)
    assert job["status"] == "failed", job
    assert job["error"]["code"] == code, job["error"]
    assert len(w.llm.requests) == requests  # nothing reached the LLM gateway
    assert "do-not-send" not in json.dumps(job)
    return dict(job["error"])


def llm_saw_blob(w: World) -> bool:
    return any("BLOB-MARKER-41c2" in json.dumps(req) for req in w.llm.requests)


def settings(contracts: Path, **kwargs: Any) -> Settings:
    return Settings(log_format="console", contracts_dir=contracts, **kwargs)


@pytest.fixture
def tree(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "blobs"
    (root / "sub").mkdir(parents=True)
    (root / "page.html").write_bytes(HTML)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.env").write_bytes(SECRET)
    return {"root": root, "outside": outside}


@pytest.fixture
def servers() -> Iterator[tuple[str, str, list[str]]]:
    """Two hosts over real HTTP: ``/page``, ``/big``, ``/redirect`` (to the second host), ``/slow`` (search)."""
    hits: list[str] = []
    urls: list[str] = []

    async def page(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(HTML, media_type="text/html")

    async def big(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(b"x" * 100_000, media_type="text/html")

    async def redirect(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return RedirectResponse(f"{urls[1]}/page", status_code=302)

    async def slow(request: Request) -> Response:
        await asyncio.sleep(3)
        return Response(b'{"results": []}', media_type="application/json")

    routes = [Route("/page", page), Route("/big", big), Route("/redirect", redirect), Route("/slow", slow)]
    running: list[uvicorn.Server] = []
    for _ in range(2):
        server = uvicorn.Server(
            uvicorn.Config(Starlette(routes=routes), host="127.0.0.1", port=0, log_level="warning")
        )
        threading.Thread(target=server.run, daemon=True).start()
        while not server.started:
            time.sleep(0.02)
        urls.append(f"http://127.0.0.1:{server.servers[0].sockets[0].getsockname()[1]}")
        running.append(server)
    yield urls[0], urls[1], hits
    for server in running:
        server.should_exit = True


def test_file_uris_are_refused_by_default(w: World, tree: dict[str, Path]) -> None:
    error = refused(w, blob("file:///proc/self/environ", SECRET), "env", "validation_failed")
    assert "JANE_ASSISTANT_BLOB_ROOTS" in error["detail"] and "environ" not in error["detail"]
    refused(w, blob((tree["root"] / "page.html").as_uri()), "no-roots", "validation_failed")


def test_file_uris_only_inside_the_roots(contracts: Path, tree: dict[str, Path]) -> None:
    secret = tree["outside"] / "secret.env"
    escape = (tree["root"] / "sub").as_uri() + "/../../outside/secret.env"
    with world(contracts, settings(contracts, blob_roots=[tree["root"]])) as w:
        for key, uri in (
            ("proc", "file:///proc/self/environ"),
            ("outside", secret.as_uri()),
            ("dotdot", escape),
        ):
            error = refused(w, blob(uri, SECRET), key, "validation_failed")
            assert str(tree["outside"]) not in error["detail"]
        try:
            os.symlink(secret, tree["root"] / "link.env")
        except (OSError, NotImplementedError):
            pass  # Windows without the symlink privilege: the jane-kit tests cover symlinks where possible
        else:
            refused(w, blob((tree["root"] / "link.env").as_uri(), SECRET), "symlink", "validation_failed")
        ok = analyse(w, blob((tree["root"] / "page.html").as_uri()), "inside")
        assert ok["status"] == "succeeded", ok
        assert llm_saw_blob(w)


def test_download_url_only_to_allowed_hosts_without_redirects(
    contracts: Path, servers: tuple[str, str, list[str]], w: World
) -> None:
    first, second, hits = servers
    first_host = first.removeprefix("http://")
    refused(w, blob("s3://t/k", download_url=f"{first}/page"), "default", "validation_failed")
    assert hits == []
    with world(contracts, settings(contracts, download_host_allowlist=[first_host])) as allowed:
        error = refused(
            allowed, blob("s3://t/k", download_url=f"{second}/page"), "other", "validation_failed"
        )
        assert "JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST" in error["detail"]
        metadata = blob("s3://t/k", download_url="http://169.254.169.254/latest/meta-data/")
        refused(allowed, metadata, "metadata", "validation_failed")
        error = refused(
            allowed, blob("s3://t/k", download_url=f"{first}/redirect"), "redirect", "upstream_unavailable"
        )
        assert error["retryable"] is False
        assert hits == [f"{first_host.split(':')[1]}/redirect"]  # the second host was never contacted
        ok = analyse(allowed, blob("s3://t/k", download_url=f"{first}/page"), "allowed")
        assert ok["status"] == "succeeded", ok
        assert llm_saw_blob(allowed)


def test_download_size_comes_from_content_limits(
    contracts: Path, servers: tuple[str, str, list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    first, _, _ = servers
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__CONTENT__MAX_MATERIAL_BYTES", "50000")
    allow = settings(contracts, download_host_allowlist=[first.removeprefix("http://")])
    with world(contracts, allow) as w:
        # size_bytes under the limit (wrong on purpose): the stream itself is cut at the limit.
        understated = blob("s3://t/k", download_url=f"{first}/big", size_bytes=40_000)
        error = refused(w, understated, "big", "limit_exceeded")
        assert error["details"] == {"path": "content.max_material_bytes", "limit": 50000}


async def test_outside_an_app_only_inline_content_is_read(tree: dict[str, Path]) -> None:
    inline = {"content": {"kind": "inline", "media_type": "text/html", "encoding": "utf-8", "data": "x"}}
    assert await material_bytes(inline) == b"x"
    for content in (blob((tree["root"] / "page.html").as_uri()), blob("s3://t/k", download_url="http://h/x")):
        with pytest.raises(JaneError) as exc:
            await material_bytes({"content": content})
        assert exc.value.error_code == "validation_failed"


async def test_search_provider_timeout_comes_from_limits(
    contracts: Path, servers: tuple[str, str, list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    first, _, _ = servers
    monkeypatch.setenv("JANE_ASSISTANT_LIMITS__SEARCH__REQUEST_TIMEOUT_MS", "300")
    s = settings(contracts, search_provider="http_json", search_url_template=f"{first}/slow?q={{query}}")
    provider = build_search(s, resolve_service_limits(s).limits)
    started = time.monotonic()
    with pytest.raises(JaneError) as exc:
        await provider.search("meetup", None, 5)
    assert exc.value.error_code == "upstream_unavailable"
    assert time.monotonic() - started < 2.5  # the server answers after 3 s; httpx alone would wait 5 s
