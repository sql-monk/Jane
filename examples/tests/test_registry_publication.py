"""Reviewed package publication against an HTTP registry neighbor, using the real contract client."""

from __future__ import annotations

import io
import json
import sys
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_kit.contracts import ContractClient

SITES = Path(__file__).resolve().parents[1] / "sites"
sys.path.insert(0, str(SITES))

import setup_sites  # noqa: E402

import jane_examples as ex  # noqa: E402

PACKAGE_ID = "tests.reviewed-rules"
VERSION = "1.1.0"
PACKAGE_PATH = f"/v1/packages/{PACKAGE_ID}"
VERSION_PATH = f"{PACKAGE_PATH}/versions/{VERSION}"
TIMESTAMP = "2026-10-11T04:00:00Z"


@pytest.fixture
def package(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    manifest = {
        "schema_version": "1",
        "package_id": PACKAGE_ID,
        "version": VERSION,
        "kind": "collector-rules",
        "title": "Reviewed catalog rules",
        "entry": {"collector": "web", "rules": "rules.json"},
        "tests": [],
        "provenance": {
            "created_by": "llm",
            "based_on": {"package_id": PACKAGE_ID, "version": "1.0.0"},
            "llm": {"model": "test", "reason": "improvement"},
        },
    }
    rules = {
        "collector": "web",
        "scope": {"allowed_domains": ["example.test"]},
        "strategies": [{"type": "seed_list", "urls": ["https://example.test/product"]}],
        "robots": {"mode": "respect"},
    }
    ex.write_json(tmp_path / "jane-package.json", manifest)
    ex.write_json(tmp_path / "rules.json", rules)
    assert ex.validate("package-manifest.schema.json", manifest) == []
    assert ex.validate("collector-rules.schema.json", rules) == []
    return tmp_path, manifest


class RegistryNeighbor:
    """Only the neighboring registry is simulated; request and response shapes use registry.v1."""

    def __init__(
        self,
        manifest: dict[str, Any],
        *,
        allowed: bool = False,
        upload_error: bool = False,
        existing_digest: str | None = None,
    ) -> None:
        self.manifest = manifest
        self.allowed = allowed
        self.upload_error = upload_error
        self.revision = 1
        self.requests: list[httpx.Request] = []
        self.policy_changes: list[bool] = []
        self.uploaded_manifest: dict[str, Any] | None = None
        self.version = self._version(existing_digest, "approved") if existing_digest else None

    @property
    def etag(self) -> str:
        return f'"package-{self.revision}"'

    def _package(self) -> dict[str, Any]:
        return {
            "package_id": PACKAGE_ID,
            "kind": "collector-rules",
            "title": "Reviewed catalog rules",
            "auto_changes_allowed": self.allowed,
            "deprecated": False,
            "created_at": TIMESTAMP,
            "updated_at": TIMESTAMP,
        }

    def _version(self, digest: str, status: str) -> dict[str, Any]:
        return {
            "package_id": PACKAGE_ID,
            "version": VERSION,
            "digest": digest,
            "status": status,
            "test_status": "unknown",
            "created_at": TIMESTAMP,
            "manifest": self.manifest,
        }

    @staticmethod
    def _problem(status: int, code: str) -> httpx.Response:
        return httpx.Response(
            status,
            json={"type": f"urn:jane:problem:{code}", "title": code, "status": status, "code": code},
            headers={"Content-Type": "application/problem+json"},
        )

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        method, path = request.method, request.url.path
        if method == "POST" and path == "/v1/packages":
            assert request.headers["Idempotency-Key"]
            assert json.loads(request.content)["auto_changes_allowed"] is False
            return self._problem(409, "conflict")
        if method == "GET" and path == PACKAGE_PATH:
            return httpx.Response(200, json=self._package(), headers={"ETag": self.etag})
        if method == "PATCH" and path == PACKAGE_PATH:
            # Upload changes the revision, so restoration must read a fresh ETag.
            assert request.headers["If-Match"] == self.etag
            assert request.headers["Content-Type"] == "application/merge-patch+json"
            ex.spec("registry").validate_request(
                method, path, json.loads(request.content), content_type=request.headers["Content-Type"]
            )
            self.allowed = json.loads(request.content)["auto_changes_allowed"]
            self.policy_changes.append(self.allowed)
            self.revision += 1
            return httpx.Response(200, json=self._package(), headers={"ETag": self.etag})
        if method == "GET" and path == VERSION_PATH:
            return httpx.Response(200, json=self.version) if self.version else self._problem(404, "not_found")
        if method == "POST" and path == f"{PACKAGE_PATH}/versions":
            assert self.allowed
            assert request.headers["Idempotency-Key"]
            assert request.headers["Content-Type"] == "application/zip"
            with zipfile.ZipFile(io.BytesIO(request.content)) as archive:
                self.uploaded_manifest = json.loads(archive.read("jane-package.json"))
            assert self.uploaded_manifest == self.manifest
            self.revision += 1
            if self.upload_error:
                raise httpx.ConnectError("registry upload interrupted", request=request)
            self.version = self._version(ex.digest_of(request.content), "draft")
            return httpx.Response(201, json=self.version)
        if method == "POST" and path == f"{VERSION_PATH}/status":
            assert self.version is not None
            assert request.headers["Idempotency-Key"]
            assert json.loads(request.content)["status"] == "approved"
            self.version["status"] = "approved"
            return httpx.Response(200, json=self.version)
        raise AssertionError(f"Unexpected registry request: {method} {path}")


@contextmanager
def registry_client(neighbor: RegistryNeighbor) -> Iterator[ex.Api]:
    registry = ex.Api("https://registry.test", "registry")
    registry.http.close()
    registry.http = httpx.Client(base_url="https://registry.test", transport=httpx.MockTransport(neighbor))
    registry.client = ContractClient(ex.spec("registry"), registry.http)
    try:
        yield registry
    finally:
        registry.close()


def test_reviewed_upload_restores_policy_with_fresh_etag_and_preserves_llm_provenance(
    package: tuple[Path, dict[str, Any]],
) -> None:
    directory, manifest = package
    neighbor = RegistryNeighbor(manifest)
    with registry_client(neighbor) as registry:
        refs = setup_sites.publish(
            ex.Services(registry, registry, registry), {PACKAGE_ID: directory}, reviewed_updates=True
        )
    assert refs[PACKAGE_ID] == setup_sites.local_ref(directory)
    assert neighbor.policy_changes == [True, False]
    assert neighbor.allowed is False
    assert neighbor.uploaded_manifest is not None
    assert neighbor.uploaded_manifest["provenance"]["created_by"] == "llm"
    assert neighbor.version is not None and neighbor.version["status"] == "approved"
    assert [(r.method, r.url.path) for r in neighbor.requests] == [
        ("POST", "/v1/packages"),
        ("GET", VERSION_PATH),
        ("GET", PACKAGE_PATH),
        ("PATCH", PACKAGE_PATH),
        ("POST", f"{PACKAGE_PATH}/versions"),
        ("GET", PACKAGE_PATH),
        ("PATCH", PACKAGE_PATH),
        ("POST", f"{VERSION_PATH}/status"),
    ]


def test_upload_exception_still_restores_original_policy(package: tuple[Path, dict[str, Any]]) -> None:
    directory, manifest = package
    neighbor = RegistryNeighbor(manifest, upload_error=True)
    with registry_client(neighbor) as registry, pytest.raises(httpx.ConnectError, match="upload interrupted"):
        setup_sites.publish(
            ex.Services(registry, registry, registry), {PACKAGE_ID: directory}, reviewed_updates=True
        )
    assert neighbor.policy_changes == [True, False]
    assert neighbor.allowed is False
    assert neighbor.version is None
    assert [(r.method, r.url.path) for r in neighbor.requests[-2:]] == [
        ("GET", PACKAGE_PATH),
        ("PATCH", PACKAGE_PATH),
    ]


def test_no_authorization_rejects_before_policy_mutation(package: tuple[Path, dict[str, Any]]) -> None:
    _, manifest = package
    neighbor = RegistryNeighbor(manifest)
    with (
        registry_client(neighbor) as registry,
        pytest.raises(RuntimeError, match="--reviewed-package-updates"),
        setup_sites.reviewed_publication(registry, PACKAGE_ID, manifest, authorized=False),
    ):
        pytest.fail("unauthorized upload body was entered")
    assert [(r.method, r.url.path) for r in neighbor.requests] == [("GET", PACKAGE_PATH)]
    assert neighbor.allowed is False and neighbor.policy_changes == []


def test_default_publish_does_not_unlock_llm_changes(package: tuple[Path, dict[str, Any]]) -> None:
    directory, manifest = package
    neighbor = RegistryNeighbor(manifest)
    with (
        registry_client(neighbor) as registry,
        pytest.raises(RuntimeError, match="--reviewed-package-updates"),
    ):
        setup_sites.publish(ex.Services(registry, registry, registry), {PACKAGE_ID: directory})
    assert neighbor.allowed is False and neighbor.policy_changes == []
    assert neighbor.uploaded_manifest is None


@pytest.mark.parametrize("authorized", [False, True])
def test_already_allowed_package_policy_is_unchanged(
    package: tuple[Path, dict[str, Any]], authorized: bool
) -> None:
    directory, manifest = package
    neighbor = RegistryNeighbor(manifest, allowed=True)
    with registry_client(neighbor) as registry:
        setup_sites.publish(
            ex.Services(registry, registry, registry), {PACKAGE_ID: directory}, reviewed_updates=authorized
        )
    assert neighbor.allowed is True and neighbor.policy_changes == []
    assert neighbor.uploaded_manifest == manifest


def test_existing_version_is_reused_without_policy_change_or_upload(
    package: tuple[Path, dict[str, Any]],
) -> None:
    directory, manifest = package
    ref = setup_sites.local_ref(directory)
    neighbor = RegistryNeighbor(manifest, existing_digest=ref["digest"])
    with registry_client(neighbor) as registry:
        assert setup_sites.publish(ex.Services(registry, registry, registry), {PACKAGE_ID: directory}) == {
            PACKAGE_ID: ref
        }
    assert [(r.method, r.url.path) for r in neighbor.requests] == [
        ("POST", "/v1/packages"),
        ("GET", VERSION_PATH),
    ]
    assert neighbor.allowed is False and neighbor.policy_changes == []
    assert neighbor.uploaded_manifest is None


def test_existing_version_digest_collision_is_rejected_without_mutation(
    package: tuple[Path, dict[str, Any]],
) -> None:
    directory, manifest = package
    neighbor = RegistryNeighbor(manifest, existing_digest="sha256:" + "1" * 64)
    with (
        registry_client(neighbor) as registry,
        pytest.raises(RuntimeError, match="another digest; bump the version"),
    ):
        setup_sites.publish(
            ex.Services(registry, registry, registry), {PACKAGE_ID: directory}, reviewed_updates=True
        )
    assert [(r.method, r.url.path) for r in neighbor.requests] == [
        ("POST", "/v1/packages"),
        ("GET", VERSION_PATH),
    ]
    assert neighbor.allowed is False and neighbor.policy_changes == []
    assert neighbor.uploaded_manifest is None
