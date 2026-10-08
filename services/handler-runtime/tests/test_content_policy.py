"""ContentRef policy of ``POST /v1/invocations`` (WP-01h): ``file://`` only under ``JANE_HANDLER_RUNTIME_BLOB_ROOTS``,
``download_url`` only to ``JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST`` hosts, no redirects, sizes from
``limits.packages``. Refusals happen before a sandbox starts; the extractor's result is never built from them.
"""

from __future__ import annotations

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
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from jane_handler_runtime.app import build_app
from jane_handler_runtime.settings import Settings

SECRET = b"JANE_SECRET_REGISTRY_TOKEN=do-not-return\n"


def page_bytes(h: Any) -> bytes:
    return Path(h.example / "tests" / "product-phone-alpha" / "page.html").read_bytes()


def blob(uri: str, data: bytes, **extra: Any) -> dict[str, Any]:
    return {
        "kind": "blob",
        "uri": uri,
        "media_type": "text/html",
        "charset": "utf-8",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        **extra,
    }


def invoke(client: TestClient, h: Any, content: dict[str, Any], key: str) -> httpx.Response:
    material = h.product_material()
    material["content"] = content
    body = h.invocation(h.example, material, key=key)
    response: httpx.Response = client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})
    return response


def refused(
    client: TestClient, h: Any, content: dict[str, Any], key: str, status: int, code: str
) -> dict[str, Any]:
    r = invoke(client, h, content, key)
    assert (r.status_code, r.json().get("code")) == (status, code), r.text
    assert "do-not-return" not in r.text
    problem: dict[str, Any] = r.json()
    return problem


def app(settings: Settings, **update: Any) -> TestClient:
    return TestClient(build_app(settings.model_copy(update=update)))


@pytest.fixture
def client(subprocess_settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(subprocess_settings)) as c:
        yield c


@pytest.fixture
def tree(tmp_path: Path, h: Any) -> dict[str, Path]:
    root = tmp_path / "blobs"
    (root / "sub").mkdir(parents=True)
    (root / "page.html").write_bytes(page_bytes(h))
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.env").write_bytes(SECRET)
    return {"root": root, "outside": outside}


@pytest.fixture
def servers(h: Any) -> Iterator[tuple[str, str, list[str]]]:
    """Two blob hosts over real HTTP: ``/page``, ``/big``, ``/redirect`` (to the second host)."""
    hits: list[str] = []
    urls: list[str] = []
    page = page_bytes(h)

    async def serve(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(page, media_type="text/html")

    async def big(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(b"x" * 200_000, media_type="text/html")

    async def redirect(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return RedirectResponse(f"{urls[1]}/page", status_code=302)

    routes = [Route("/page", serve), Route("/big", big), Route("/redirect", redirect)]
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


def test_file_uris_are_refused_by_default(client: TestClient, h: Any, tree: dict[str, Path]) -> None:
    problem = refused(client, h, blob("file:///proc/self/environ", SECRET), "env", 422, "validation_failed")
    assert "JANE_HANDLER_RUNTIME_BLOB_ROOTS" in problem["detail"] and "environ" not in problem["detail"]
    refused(
        client,
        h,
        blob((tree["root"] / "page.html").as_uri(), page_bytes(h)),
        "no-roots",
        422,
        "validation_failed",
    )


def test_file_uris_only_inside_the_roots(
    subprocess_settings: Settings, h: Any, tree: dict[str, Path]
) -> None:
    secret = tree["outside"] / "secret.env"
    escape = (tree["root"] / "sub").as_uri() + "/../../outside/secret.env"
    with app(subprocess_settings, blob_roots=[tree["root"]]) as c:
        for key, uri in (
            ("proc", "file:///proc/self/environ"),
            ("outside", secret.as_uri()),
            ("dotdot", escape),
        ):
            problem = refused(c, h, blob(uri, SECRET), key, 422, "validation_failed")
            assert str(tree["outside"]) not in problem["detail"]
        try:
            os.symlink(secret, tree["root"] / "link.env")
        except (OSError, NotImplementedError):
            pass  # Windows without the symlink privilege: the jane-kit tests cover symlinks where possible
        else:
            refused(
                c, h, blob((tree["root"] / "link.env").as_uri(), SECRET), "symlink", 422, "validation_failed"
            )
        ok = invoke(c, h, blob((tree["root"] / "page.html").as_uri(), page_bytes(h)), "inside")
        assert ok.status_code == 200 and ok.json()["status"] == "success", ok.text


def test_download_url_only_to_allowed_hosts_without_redirects(
    subprocess_settings: Settings, client: TestClient, h: Any, servers: tuple[str, str, list[str]]
) -> None:
    first, second, hits = servers
    first_host = first.removeprefix("http://")
    page = page_bytes(h)
    refused(
        client, h, blob("s3://t/k", page, download_url=f"{first}/page"), "default", 422, "validation_failed"
    )
    assert hits == []
    with app(subprocess_settings, download_host_allowlist=[first_host]) as c:
        problem = refused(
            c, h, blob("s3://t/k", page, download_url=f"{second}/page"), "other", 422, "validation_failed"
        )
        assert "JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST" in problem["detail"]
        metadata = blob("s3://t/k", page, download_url="http://169.254.169.254/latest/meta-data/")
        refused(c, h, metadata, "metadata", 422, "validation_failed")
        problem = refused(
            c,
            h,
            blob("s3://t/k", page, download_url=f"{first}/redirect"),
            "redirect",
            502,
            "upstream_unavailable",
        )
        assert problem["retryable"] is False
        assert hits == [f"{first_host.split(':')[1]}/redirect"]  # the second host was never contacted
        ok = invoke(c, h, blob("s3://t/k", page, download_url=f"{first}/page"), "allowed")
        assert ok.status_code == 200 and ok.json()["status"] == "success", ok.text


def test_download_size_comes_from_package_limits(
    subprocess_settings: Settings,
    h: Any,
    servers: tuple[str, str, list[str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, _, _ = servers
    monkeypatch.setenv("JANE_HANDLER_RUNTIME_LIMITS__PACKAGES__MAX_INPUT_BYTES", "100000")
    with app(subprocess_settings, download_host_allowlist=[first.removeprefix("http://")]) as c:
        # size_bytes under the limit (wrong on purpose): the stream itself is cut at the limit.
        understated = blob("s3://t/k", b"x" * 50_000, download_url=f"{first}/big")
        problem = refused(c, h, understated, "big", 422, "limit_exceeded")
        assert problem["details"] == {"path": "packages.max_input_bytes", "limit": 100000}


def test_download_host_allowlist_is_validated_at_start() -> None:
    with pytest.raises(ValueError, match="hostname"):
        Settings(download_host_allowlist=["http://registry:8000"])
