"""ContentRef policy of ``POST /v1/invocations`` (WP-01h): ``file://`` only under ``JANE_LLM_BLOB_ROOTS``,
``download_url`` only to ``JANE_LLM_DOWNLOAD_HOST_ALLOWLIST`` hosts, no redirects, sizes from ``limits.gateway``.

Refused content never reaches the LLM provider: every refusal also checks that the fake provider was not called.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import uvicorn
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from jane_llm.packages import build_archive, read_dir

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "packages" / "jane.llm-event-extractor"
TEXT = "Концерт 12 жовтня о 19:00, Філармонія. BLOB-MARKER-7f3a".encode()
SECRET = b"JANE_SECRET_PROVIDER_KEY=do-not-send\n"


def blob(uri: str, data: bytes = TEXT, **extra: Any) -> dict[str, Any]:
    return {
        "kind": "blob",
        "uri": uri,
        "media_type": "text/plain",
        "charset": "utf-8",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        **extra,
    }


def invocation(content: dict[str, Any], key: str) -> dict[str, Any]:
    material = json.loads((PACKAGE_DIR / "tests" / "concert" / "material.json").read_text(encoding="utf-8"))
    material = copy.deepcopy(material)
    material["content"] = content
    return {
        "handler": {"package_id": "jane.llm-event-extractor", "version": "1.0.0"},
        "inputs": [{"kind": "material", "material": material}],
        "context": {"test_mode": True},
        "delivery": {"delivery_key": key},
    }


def post(client: TestClient, body: dict[str, Any]) -> Any:
    key = body["delivery"]["delivery_key"]
    return client.post("/v1/invocations", json=body, headers={"Idempotency-Key": key})


def refused(client: TestClient, fake: Any, body: dict[str, Any], status: int, code: str) -> dict[str, Any]:
    calls = len(fake.calls)
    r = post(client, body)
    assert (r.status_code, r.json().get("code")) == (status, code), r.text
    assert len(fake.calls) == calls  # nothing reached the provider
    problem: dict[str, Any] = r.json()
    assert "do-not-send" not in r.text and "PROVIDER_KEY" not in r.text
    return problem


def provider_saw_blob(fake: Any) -> bool:
    return any("BLOB-MARKER-7f3a" in call.user for call in fake.calls)


@pytest.fixture
def tree(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "blobs"
    (root / "sub").mkdir(parents=True)
    (root / "message.txt").write_bytes(TEXT)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.env").write_bytes(SECRET)
    return {"root": root, "outside": outside}


@pytest.fixture
def servers() -> Iterator[tuple[str, str, list[str]]]:
    """Two blob hosts over real HTTP: ``/page``, ``/big``, ``/redirect`` (to the second host)."""
    hits: list[str] = []
    urls: list[str] = []

    async def page(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(TEXT, media_type="text/plain")

    async def big(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return Response(b"x" * 200_000, media_type="text/plain")

    async def redirect(request: Request) -> Response:
        hits.append(f"{request.url.port}{request.url.path}")
        return RedirectResponse(f"{urls[1]}/page", status_code=302)

    app = Starlette(routes=[Route("/page", page), Route("/big", big), Route("/redirect", redirect)])
    running: list[uvicorn.Server] = []
    for _ in range(2):
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
        threading.Thread(target=server.run, daemon=True).start()
        while not server.started:
            time.sleep(0.02)
        urls.append(f"http://127.0.0.1:{server.servers[0].sockets[0].getsockname()[1]}")
        running.append(server)
    yield urls[0], urls[1], hits
    for server in running:
        server.should_exit = True


def test_file_uris_are_refused_by_default(client: TestClient, fake: Any, tree: dict[str, Path]) -> None:
    problem = refused(
        client, fake, invocation(blob("file:///proc/self/environ", SECRET), "env"), 422, "validation_failed"
    )
    assert "JANE_LLM_BLOB_ROOTS" in problem["detail"] and "environ" not in problem["detail"]
    inside = blob((tree["root"] / "message.txt").as_uri())
    refused(client, fake, invocation(inside, "no-roots"), 422, "validation_failed")


def test_file_uris_only_inside_the_roots(
    make_client: Callable[..., TestClient], fake: Any, tree: dict[str, Path]
) -> None:
    client = make_client(settings={"blob_roots": [tree["root"]]})
    secret = tree["outside"] / "secret.env"
    escape = (tree["root"] / "sub").as_uri() + "/../../outside/secret.env"
    for key, uri in (("proc", "file:///proc/self/environ"), ("outside", secret.as_uri()), ("dotdot", escape)):
        problem = refused(client, fake, invocation(blob(uri, SECRET), key), 422, "validation_failed")
        assert str(tree["outside"]) not in problem["detail"]
    try:
        os.symlink(secret, tree["root"] / "link.txt")
    except (OSError, NotImplementedError):
        pass  # Windows without the symlink privilege: the jane-kit tests cover symlinks where possible
    else:
        link = blob((tree["root"] / "link.txt").as_uri(), SECRET)
        refused(client, fake, invocation(link, "symlink"), 422, "validation_failed")

    ok = post(client, invocation(blob((tree["root"] / "message.txt").as_uri()), "inside"))
    assert ok.status_code == 200, ok.text
    assert provider_saw_blob(fake)


def test_package_archive_file_uri_outside_the_roots_is_refused(
    make_client: Callable[..., TestClient], fake: Any, tree: dict[str, Path]
) -> None:
    archive = build_archive(read_dir(PACKAGE_DIR))
    (tree["outside"] / "pkg.zip").write_bytes(archive)
    body = invocation(blob((tree["root"] / "message.txt").as_uri()), "archive")
    body["package_archive"] = blob(
        (tree["outside"] / "pkg.zip").as_uri(), archive, media_type="application/zip"
    )
    client = make_client(settings={"blob_roots": [tree["root"]]})
    refused(client, fake, body, 422, "validation_failed")


def test_download_url_only_to_allowed_hosts_without_redirects(
    make_client: Callable[..., TestClient], fake: Any, servers: tuple[str, str, list[str]]
) -> None:
    first, second, hits = servers
    first_host = first.removeprefix("http://")
    default = make_client()
    refused(
        default,
        fake,
        invocation(blob("s3://t/k", download_url=f"{first}/page"), "default"),
        422,
        "validation_failed",
    )
    assert hits == []

    client = make_client(settings={"download_host_allowlist": [first_host]})
    problem = refused(
        client,
        fake,
        invocation(blob("s3://t/k", download_url=f"{second}/page"), "other-host"),
        422,
        "validation_failed",
    )
    assert "JANE_LLM_DOWNLOAD_HOST_ALLOWLIST" in problem["detail"]
    metadata = blob("s3://t/k", download_url="http://169.254.169.254/latest/meta-data/")
    refused(client, fake, invocation(metadata, "metadata"), 422, "validation_failed")
    redirect = refused(
        client,
        fake,
        invocation(blob("s3://t/k", download_url=f"{first}/redirect"), "redirect"),
        502,
        "upstream_unavailable",
    )
    assert redirect["retryable"] is False
    assert hits == [f"{first_host.split(':')[1]}/redirect"]  # the second host was never contacted

    ok = post(client, invocation(blob("s3://t/k", download_url=f"{first}/page"), "allowed"))
    assert ok.status_code == 200, ok.text
    assert provider_saw_blob(fake)


def test_download_size_comes_from_gateway_limits(
    make_client: Callable[..., TestClient],
    fake: Any,
    servers: tuple[str, str, list[str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, _, _ = servers
    monkeypatch.setenv("JANE_LLM_LIMITS__GATEWAY__MAX_DATA_PART_BYTES", "100000")
    client = make_client(settings={"download_host_allowlist": [first.removeprefix("http://")]})
    # size_bytes under the limit (wrong on purpose): the stream itself is cut at the limit.
    understated = blob("s3://t/k", download_url=f"{first}/big", size_bytes=50_000)
    problem = refused(client, fake, invocation(understated, "big"), 422, "limit_exceeded")
    assert problem["details"] == {"path": "gateway.max_data_part_bytes", "limit": 100000}
