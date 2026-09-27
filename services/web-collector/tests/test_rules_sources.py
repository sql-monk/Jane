"""Rules by ``rules_ref``: registry.v1 (a fake built from the registry contract), local archive, digests, errors."""

from __future__ import annotations

import hashlib
import io
import json
import threading
import time
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import uvicorn
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

from jane_kit.contracts import OpenAPISpec
from jane_web_collector.app import build_app
from jane_web_collector.testing import (
    FAST_LIMITS,
    REPO_ROOT,
    Site,
    drain,
    free_port,
    make_settings,
    web_rules,
)

REGISTRY = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "registry.v1.yaml")
REF = {"package_id": "testsite.web-rules", "version": "1.2.0"}
DIGEST = "sha256:" + "ab" * 32


def _manifest(ref: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "package_id": ref["package_id"],
        "version": ref["version"],
        "kind": "collector-rules",
        "title": "testsite rules",
        "entry": {"collector": "web", "rules": "rules.json"},
        "tests": [],
        "provenance": {"created_by": "human"},
    }


class FakeRegistry:
    """Neighbour mock: only the two registry.v1 operations the collector uses; every response body is
    validated against the registry contract before it is served."""

    def __init__(self, rules: dict[str, Any]) -> None:
        self.rules = rules
        self.calls: list[str] = []
        self.tampered = False  # serve a rules file that differs from the version's file list
        base = "/v1/packages/{package_id}/versions/{version}"
        self.app = Starlette(routes=[Route(base, self.version), Route(base + "/file", self.file)])

    async def version(self, request: Request) -> Response:
        self.calls.append(request.url.path)
        p = request.path_params
        if (p["package_id"], p["version"]) != (REF["package_id"], REF["version"]):
            body = {
                "type": "urn:jane:problem:not_found",
                "title": "Not found",
                "status": 404,
                "code": "not_found",
            }
            REGISTRY.validate_response("GET", request.url.path, 404, body, "application/problem+json")
            return JSONResponse(body, status_code=404, media_type="application/problem+json")
        raw = json.dumps(self.rules).encode()
        body = {
            **REF,
            "digest": DIGEST,
            "status": "approved",
            "test_status": "passed",
            "manifest": _manifest(REF),
            "files": [
                {"path": "rules.json", "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            ],
            "created_at": "2026-09-27T10:00:00Z",
        }
        REGISTRY.validate_response("GET", request.url.path, 200, body)
        return JSONResponse(body)

    async def file(self, request: Request) -> Response:
        self.calls.append(f"{request.url.path}?path={request.query_params['path']}")
        assert request.query_params["path"] == "rules.json"
        rules = {**self.rules, "strategies": [{"type": "recursive"}]} if self.tampered else self.rules
        return PlainTextResponse(json.dumps(rules))


@pytest.fixture
def registry(site: Site) -> Iterator[tuple[str, FakeRegistry]]:
    fake = FakeRegistry(web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/about")]}]))
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(fake.app, host="127.0.0.1", port=port, log_config=None))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.02)
    try:
        yield f"http://127.0.0.1:{port}", fake
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def _post(client: TestClient, body: dict[str, Any]) -> Any:
    return client.post(
        "/v1/collections",
        json=body,
        headers={"Idempotency-Key": hashlib.sha256(json.dumps(body).encode()).hexdigest()},
    )


def test_rules_from_registry(tmp_path: Path, site: Site, registry: tuple[str, FakeRegistry]) -> None:
    url, fake = registry
    with TestClient(build_app(make_settings(tmp_path, registry_url=url))) as client:
        r = _post(
            client, {"source_kind": "web", "rules_ref": {**REF, "digest": DIGEST}, "limits": FAST_LIMITS}
        )
        assert r.status_code == 202, r.text
        materials = drain(client, r.json()["job_id"])
        assert [m["locator"]["canonical_url"] for m in materials] == [site.url("/about")]
        assert materials[0]["collector"]["rules"] == {**REF, "digest": DIGEST}

        wrong = _post(client, {"source_kind": "web", "rules_ref": {**REF, "digest": "sha256:" + "cd" * 32}})
        assert wrong.status_code == 422
        assert wrong.json()["code"] == "digest_mismatch"

        missing = _post(client, {"source_kind": "web", "rules_ref": {**REF, "version": "9.9.9"}})
        assert missing.status_code == 422
        assert missing.json()["errors"][0]["pointer"] == "/rules_ref"
    assert f"/v1/packages/{REF['package_id']}/versions/{REF['version']}/file?path=rules.json" in fake.calls


def test_tampered_rules_file_is_rejected(tmp_path: Path, registry: tuple[str, FakeRegistry]) -> None:
    url, fake = registry
    fake.tampered = True
    with TestClient(build_app(make_settings(tmp_path, registry_url=url))) as client:
        r = _post(client, {"source_kind": "web", "rules_ref": REF})
    assert r.status_code == 422
    assert r.json()["code"] == "digest_mismatch"


def test_registry_unavailable_is_retryable(tmp_path: Path) -> None:
    with TestClient(
        build_app(make_settings(tmp_path, registry_url=f"http://127.0.0.1:{free_port()}"))
    ) as client:
        r = _post(client, {"source_kind": "web", "rules_ref": REF})
    assert r.status_code == 502
    assert r.json()["code"] == "upstream_unavailable"
    assert r.json()["retryable"] is True


def test_rules_from_local_archive_with_digest(tmp_path: Path, site: Site) -> None:
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("jane-package.json", json.dumps(_manifest(REF)))
        zf.writestr(
            "rules.json",
            json.dumps(web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/")]}])),
        )
    archive = rules_dir / f"{REF['package_id']}-{REF['version']}.zip"
    archive.write_bytes(buf.getvalue())
    digest = "sha256:" + hashlib.sha256(buf.getvalue()).hexdigest()
    with TestClient(build_app(make_settings(tmp_path, rules_dir=rules_dir))) as client:
        ok = _post(
            client, {"source_kind": "web", "rules_ref": {**REF, "digest": digest}, "limits": FAST_LIMITS}
        )
        assert ok.status_code == 202, ok.text
        assert len(drain(client, ok.json()["job_id"])) == 1
        bad = _post(client, {"source_kind": "web", "rules_ref": {**REF, "digest": "sha256:" + "00" * 32}})
        assert bad.json()["code"] == "digest_mismatch"


def test_rules_ref_without_any_source(client: TestClient) -> None:
    r = _post(client, {"source_kind": "web", "rules_ref": REF})
    assert r.status_code == 422
    assert r.json()["code"] == "validation_failed"
