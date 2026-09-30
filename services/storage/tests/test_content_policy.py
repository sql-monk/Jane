"""ContentRef cannot read local secrets or call network hosts without operator opt-in."""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from jane_storage.app import build_app
from jane_storage.content import ContentError, ContentReader
from jane_storage.settings import Settings


def reader(*, files_dir: Path | None = None, hosts: tuple[str, ...] = ()) -> ContentReader:
    return ContentReader(
        max_bytes=1024,
        request_timeout_ms=1000,
        files_dir=files_dir,
        download_host_allowlist=hosts,
    )


def blob(uri: str, data: bytes, **extra: str) -> dict[str, object]:
    return {
        "kind": "blob",
        "uri": uri,
        "media_type": "text/plain",
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        **extra,
    }


@pytest.mark.asyncio
async def test_local_blob_requires_a_directory_and_stays_inside_it(tmp_path: Path) -> None:
    shared = tmp_path / "shared"
    shared.mkdir()
    inside = shared / "payload.txt"
    inside.write_bytes(b"payload")
    secret = tmp_path / "secret.txt"
    secret.write_bytes(b"do-not-expose")

    with pytest.raises(ContentError, match="disabled"):
        await reader().read(blob(inside.as_uri(), b"payload"))
    configured = reader(files_dir=shared)
    assert await configured.read(blob(inside.as_uri(), b"payload")) == b"payload"
    for uri in (secret.as_uri(), (shared / ".." / "secret.txt").as_uri()):
        with pytest.raises(ContentError, match="outside"):
            await configured.read(blob(uri, b"do-not-expose"))
    with pytest.raises(ContentError, match="invalid"):
        await configured.read(blob("file://remote/share/payload.txt", b"payload"))


@pytest.mark.asyncio
async def test_local_blob_symlink_escape_is_denied(tmp_path: Path) -> None:
    shared = tmp_path / "shared"
    shared.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_bytes(b"do-not-expose")
    link = shared / "alias"
    try:
        link.symlink_to(secret)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks require extra privileges on this platform")
    with pytest.raises(ContentError, match="outside"):
        await reader(files_dir=shared).read(blob(link.as_uri(), b"do-not-expose"))


@pytest.mark.asyncio
async def test_download_allowlist_and_redirect_do_not_contact_other_hosts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        if request.url.path == "/redirect":
            return httpx.Response(302, headers={"Location": "http://metadata.internal/secret"})
        return httpx.Response(200, content=b"payload")

    original_client = httpx.AsyncClient
    transport = httpx.MockTransport(respond)

    def client(*, timeout: float, follow_redirects: bool, trust_env: bool) -> httpx.AsyncClient:
        assert follow_redirects is False
        assert trust_env is False
        return original_client(
            transport=transport, timeout=timeout, follow_redirects=follow_redirects, trust_env=trust_env
        )

    monkeypatch.setattr(httpx, "AsyncClient", client)
    configured = reader(hosts=("allowed.internal:443",))
    for url in (
        "http://allowed.internal/payload",
        "https://metadata.internal/secret",
        "https://allowed.internal:8443/payload",
        "https://allowed.internal@metadata.internal/secret",
        "file:///etc/passwd",
    ):
        with pytest.raises(ContentError, match="not allowed"):
            await configured.read(blob("s3://bucket/item", b"payload", download_url=url))
    assert requested == []
    assert (
        await configured.read(
            blob("s3://bucket/item", b"payload", download_url="https://allowed.internal/payload")
        )
        == b"payload"
    )
    with pytest.raises(ContentError, match="redirect"):
        await configured.read(
            blob("s3://bucket/item", b"payload", download_url="https://allowed.internal/redirect")
        )
    assert requested == ["https://allowed.internal/payload", "https://allowed.internal/redirect"]


def test_content_policy_settings_from_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("JANE_STORAGE_CONTENT_FILES_DIR", str(tmp_path))
    monkeypatch.setenv("JANE_STORAGE_DOWNLOAD_HOST_ALLOWLIST", '["cdn.internal:443"]')
    settings = Settings()
    assert settings.content_files_dir == tmp_path
    assert settings.download_host_allowlist == ["cdn.internal:443"]


def test_invocation_does_not_store_a_local_secret(
    settings: Settings, h: SimpleNamespace, tmp_path: Path
) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_bytes(b"private")
    material = h.material()
    material["content"] = blob(secret.as_uri(), b"private")
    with TestClient(build_app(settings)) as client:
        response = h.post(client, h.invocation([{"kind": "material", "material": material}], "blocked-file"))
        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        assert "disabled" in response.json()["failure"]["message"]
        objects = client.get("/v1/objects", params={"connection_id": "raw-files"})
        assert objects.status_code == 200
        assert objects.json()["items"] == []
