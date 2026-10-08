"""Registry-side steps (registry.v1): publication, archives, forks, upstream ports.

Shared by S-M2-01 (``test_m2_registry.py``) and its continuation for the other package kinds
(``test_m2_registry_types.py``). Every call goes through the contract-validating client; the helpers assert
the documented status codes, so a scenario reads as the sequence of registry operations it performs.

:func:`publish_fixture_package` / :func:`publish_archive` put the packages of this checkout (the SDK example
extractor, the fixtures of ``tests/e2e/packages``) into the REAL registry of a stack for the orchestrated
scenarios: their stages send no ``package_archive``, so handler-runtime and the LLM gateway download the
archive from the registry by ``package_id@version`` and check the pinned digest.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import uuid
import zipfile
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from jane_e2e.clients import CONTRACTS, JaneClient, spec, token_for
from jane_e2e.orchestration import list_items
from jane_e2e.stack import ROOT, E2EStack, default_project
from jane_registry.archive import canonical_archive, digest_of, files_from_dir

__all__ = [
    "FILES_DIR",
    "FIXTURE_APPROVAL",
    "LLM_DIR",
    "POSTGRES_DIR",
    "REGISTRY_ENV",
    "RULES_DIR",
    "archive",
    "archive_file",
    "archive_paths",
    "fork",
    "key",
    "new_parent_version",
    "package_diff",
    "package_files",
    "port_upstream",
    "publish",
    "publish_archive",
    "publish_body",
    "publish_fixture_package",
    "publish_storage_packages",
    "publish_version",
    "ref_of",
    "registry_stack",
    "run_stage_handler",
    "upstream",
    "version",
]

LLM_DIR = ROOT / "services/llm/packages/jane.llm-event-extractor"
FILES_DIR = ROOT / "services/storage/adapters/files/src/jane_storage_files/package"
POSTGRES_DIR = ROOT / "services/storage/adapters/postgres/src/jane_storage_postgres/package"
RULES_DIR = ROOT / "tests/e2e/config/rules/testsite.web-rules/1.0.0"
MANIFEST_SCHEMA = (CONTRACTS.parent / "schemas" / "package-manifest.schema.json").as_uri() + "#"
FIXTURE_APPROVAL = "e2e: package of the checkout (tests/e2e/packages, SDK example), tests run by its owner WP"

# The executors of an isolated registry stack take packages from the REAL registry, not from local stand-ins:
# the runtime and storage fetch archives, the Web Collector reads rules (its local rules directory does not exist),
# the LLM gateway fetches LLM packages, and the registry checks dependencies against the runtime's profile.
REGISTRY_ENV = {
    "JANE_E2E_RUNTIME_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_STORAGE_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_REGISTRY_RUNTIME_PROFILES": '["http://handler-runtime:8000/v1/info"]',
    "JANE_E2E_COLLECTOR_RULES_DIR": "/cfg/registry-only",
    "JANE_E2E_COLLECTOR_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_LLM_REGISTRY_URL": "http://registry:8000",
}


@contextmanager
def registry_stack(name: str, services: Sequence[str]) -> Iterator[E2EStack]:
    """An isolated stack (own compose project ``<project>-<name>-<hex>``) whose executors use the real registry.

    Skips when a service is not in this checkout; removes containers, volumes and images afterwards unless
    ``JANE_E2E_KEEP=1``. The caller starts the services it needs (``stack.ensure``)."""
    stack = E2EStack(project=f"{default_project()}-{name}-{uuid.uuid4().hex[:6]}")
    stack.env().update(REGISTRY_ENV)
    try:
        if missing := stack.missing(services):
            pytest.skip("; ".join(missing))
        yield stack
    finally:
        if os.environ.get("JANE_E2E_KEEP") != "1":
            stack.down(volumes=True)


def key() -> str:
    return uuid.uuid4().hex


# ---------------------------------------------------------------------------- publication
def package_files(directory: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Manifest and every other file of a package directory (``PublishRequest`` parts)."""
    manifest = json.loads((directory / "jane-package.json").read_text(encoding="utf-8"))
    files = {
        p.relative_to(directory).as_posix(): p.read_bytes()
        for p in directory.rglob("*")
        if p.is_file() and p.name != "jane-package.json" and "__pycache__" not in p.parts
    }
    return manifest, files


def publish_body(manifest: dict[str, Any], files: Mapping[str, bytes]) -> dict[str, Any]:
    encoded: dict[str, dict[str, str]] = {}
    for path, data in files.items():
        try:
            encoded[path] = {"encoding": "utf-8", "data": data.decode("utf-8")}
        except UnicodeDecodeError:
            encoded[path] = {"encoding": "base64", "data": base64.b64encode(data).decode("ascii")}
    return {"manifest": manifest, "files": encoded}


def publish(registry: JaneClient, manifest: dict[str, Any], files: Mapping[str, bytes]) -> dict[str, Any]:
    """Create the package and publish its first version (``draft``)."""
    package_id = manifest["package_id"]
    created = registry.api("registry").post(
        "/v1/packages",
        json={"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]},
        headers={"Idempotency-Key": key()},
    )
    assert created.status_code == 201, created.text
    published = publish_version(registry, manifest, files)
    assert published["status"] == "draft"
    return published


def publish_version(
    registry: JaneClient, manifest: dict[str, Any], files: Mapping[str, bytes]
) -> dict[str, Any]:
    response = registry.api("registry").post(
        f"/v1/packages/{manifest['package_id']}/versions",
        json=publish_body(manifest, files),
        headers={"Idempotency-Key": key()},
    )
    assert response.status_code == 201, response.text
    return dict(response.json())


def publish_storage_packages(registry_url: str) -> str:
    """``jane-storage-packages publish`` (WP-07 CLI): every built-in ``jane.storage-*`` package -> registry.

    Time limit of the CLI call: ``JANE_E2E_CLI_TIMEOUT_S`` (default 120 s)."""
    token = token_for(registry_url)
    cli = [sys.executable, "-m", "jane_storage.packages", "publish", "--registry", registry_url]
    done = subprocess.run(
        [*cli, "--token-env", "JANE_E2E_REGISTRY_TOKEN"] if token else cli,
        env={**os.environ, "JANE_E2E_REGISTRY_TOKEN": token or ""},
        capture_output=True,
        text=True,
        timeout=float(os.environ.get("JANE_E2E_CLI_TIMEOUT_S", "120")),
        check=False,
    )
    assert done.returncode == 0, (done.stdout, done.stderr)
    return done.stdout


def publish_archive(registry: JaneClient, data: bytes, *, reason: str = FIXTURE_APPROVAL) -> dict[str, str]:
    """Publish a package archive of this checkout to the REAL registry, approve it, return the pinned ref.

    The registry keeps its canonical archive of the files (``jane_registry.archive.canonical_archive``), so the
    pinned digest is computed here from the same files and must equal the registry's answer and the downloaded
    archive (``ETag`` and SHA-256). Idempotent on a shared stack: an existing package is reused and an existing
    version must have exactly this digest (versions are immutable; other content fails the scenario)."""
    with zipfile.ZipFile(io.BytesIO(data)) as zipped:
        files = {i.filename: zipped.read(i) for i in zipped.infolist() if not i.is_dir()}
    canonical = canonical_archive(files)
    expected = digest_of(canonical)
    manifest = json.loads(files["jane-package.json"])
    package_id, version_ = str(manifest["package_id"]), str(manifest["version"])
    spec("registry").validate_at(MANIFEST_SCHEMA, manifest, f"{package_id}/jane-package.json")
    api = registry.api("registry")
    body = {"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]}
    created = api.post("/v1/packages", json=body, headers={"Idempotency-Key": key()})
    if created.status_code == 409:  # published by an earlier scenario of this stack
        existing = api.get(f"/v1/packages/{package_id}")
        assert existing.status_code == 200, existing.text
        assert existing.json()["kind"] == manifest["kind"], existing.json()
    else:
        assert created.status_code == 201, created.text
    published = api.post(
        f"/v1/packages/{package_id}/versions",
        content=canonical,
        headers={"Content-Type": "application/zip", "Idempotency-Key": key()},
    )
    if published.status_code == 409:
        assert published.json()["code"] == "version_exists", published.text
        doc = version(registry, package_id, version_)
    else:
        assert published.status_code == 201, published.text
        doc = dict(published.json())
    assert doc["digest"] == expected, (package_id, version_, doc["digest"], expected)
    if doc["status"] == "draft":
        approved = api.post(
            f"/v1/packages/{package_id}/versions/{version_}/status",
            json={"status": "approved", "reason": reason},
            headers={"Idempotency-Key": key()},
        )
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "approved", approved.json()
    archive(registry, package_id, version_, expected)
    return {"package_id": package_id, "version": version_, "digest": expected}


def publish_fixture_package(
    registry: JaneClient, package_dir: Path, *, reason: str = FIXTURE_APPROVAL
) -> dict[str, str]:
    """:func:`publish_archive` of a package directory of this checkout; returns ``package_id@version`` + digest."""
    return publish_archive(registry, canonical_archive(files_from_dir(package_dir)), reason=reason)


def new_parent_version(
    manifest: Mapping[str, Any],
    files: Mapping[str, bytes],
    new_version: str,
    summary: str,
    change: Callable[[dict[str, Any], dict[str, bytes]], None],
) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Next version of a parent package: ``change`` edits copies of the manifest and the files in place;
    ``provenance.based_on`` points to the published version (a human change)."""
    next_manifest: dict[str, Any] = json.loads(json.dumps(manifest))
    next_files = dict(files)
    next_manifest["version"] = new_version
    next_manifest["provenance"] = {
        "created_by": "human",
        "based_on": {"package_id": manifest["package_id"], "version": manifest["version"]},
        "change_summary": summary,
    }
    change(next_manifest, next_files)
    return next_manifest, next_files


# ---------------------------------------------------------------------------- reading
def version(registry: JaneClient, package_id: str, version_: str) -> dict[str, Any]:
    response = registry.api("registry").get(f"/v1/packages/{package_id}/versions/{version_}")
    assert response.status_code == 200, response.text
    return dict(response.json())


def ref_of(version_doc: Mapping[str, Any]) -> dict[str, str]:
    """Pinned ``PackageRef`` (id, version, digest) of a registry version."""
    manifest = version_doc["manifest"]
    return {
        "package_id": str(manifest["package_id"]),
        "version": str(manifest["version"]),
        "digest": str(version_doc["digest"]),
    }


def archive(registry: JaneClient, package_id: str, version_: str, digest: str) -> bytes:
    """Archive bytes of a version; ETag and SHA-256 must equal ``digest``."""
    response = registry.api("registry").get(f"/v1/packages/{package_id}/versions/{version_}/archive")
    assert response.status_code == 200, response.text
    assert response.headers["etag"] == f'"{digest}"'
    assert "sha256:" + hashlib.sha256(response.content).hexdigest() == digest
    with zipfile.ZipFile(io.BytesIO(response.content)) as zipped:
        assert "jane-package.json" in zipped.namelist()
        assert json.loads(zipped.read("jane-package.json"))["package_id"] == package_id
    return response.content


def archive_file(archive_: bytes, path: str) -> bytes:
    with zipfile.ZipFile(io.BytesIO(archive_)) as zipped:
        return zipped.read(path)


def archive_paths(archive_: bytes) -> set[str]:
    with zipfile.ZipFile(io.BytesIO(archive_)) as zipped:
        return set(zipped.namelist())


# ---------------------------------------------------------------------------- forks
def fork(registry: JaneClient, parent: Mapping[str, Any], fork_id: str) -> dict[str, Any]:
    """Fork ``parent`` (a registry version) as ``fork_id``; returns the fork's first version.

    The fork's ``fork_of`` is the parent's pinned reference; its version equals the parent's."""
    parent_ref = ref_of(parent)
    forked = registry.api("registry").post(
        f"/v1/packages/{parent_ref['package_id']}/forks",
        json={"new_package_id": fork_id, "from_version": parent_ref["version"]},
        headers={"Idempotency-Key": key()},
    )
    assert forked.status_code == 201, forked.text
    assert forked.json()["fork_of"] == parent_ref, forked.json()
    first = version(registry, fork_id, parent_ref["version"])
    assert first["manifest"]["fork_of"] == parent_ref, first["manifest"]
    assert first["manifest"]["kind"] == parent["manifest"]["kind"]
    return first


def upstream(registry: JaneClient, fork_id: str) -> dict[str, Any]:
    response = registry.api("registry").get(f"/v1/packages/{fork_id}/upstream")
    assert response.status_code == 200, response.text
    return dict(response.json())


def package_diff(
    registry: JaneClient, package_id: str, from_: str, to: str
) -> tuple[dict[str, str], dict[str, str]]:
    """``GET /diff`` (``to`` may be ``parent:<version>``): ``path -> status`` of the files other than the
    manifest, and ``JSON Pointer -> op`` of the manifest changes."""
    response = registry.api("registry").get(
        f"/v1/packages/{package_id}/diff", params={"from": from_, "to": to}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    files = {str(f["path"]): str(f["status"]) for f in body["files"]}
    manifest = {str(c["pointer"]): str(c["op"]) for c in body.get("manifest_changes") or []}
    return files, manifest


def port_upstream(
    registry: JaneClient, fork_id: str, parent_version: str, new_version: str
) -> dict[str, Any]:
    """Explicit upstream port (job ``upstream_port``); returns the new fork version."""
    started = registry.api("registry").post(
        f"/v1/packages/{fork_id}/upstream-ports",
        json={"parent_version": parent_version, "new_version": new_version},
        headers={"Idempotency-Key": key()},
    )
    assert started.status_code == 202, started.text
    job = registry.wait_job("registry", started.json()["job_id"])
    assert job["status"] == "succeeded", job
    ported = dict(job["result"])
    assert ported["version"] == new_version, ported
    return ported


# ---------------------------------------------------------------------------- orchestrator trace
def run_stage_handler(orch: JaneClient, run_id: str, stage_id: str) -> dict[str, Any]:
    """Handler ref that the orchestrator recorded for ``stage_id`` of this run (material trace)."""
    items = list_items(orch, run_id, stage_id)
    assert len(items) == 1 and items[0]["status"] == "completed", items
    response = orch.api("orchestrator").get(f"/v1/materials/{items[0]['material_id']}/trace")
    assert response.status_code == 200, response.text
    trace = response.json()
    stages = [
        stage
        for observation in trace["observations"]
        if observation.get("run_id") == run_id
        for stage in observation["stages"]
        if stage["stage_id"] == stage_id
    ]
    assert len(stages) == 1, trace
    assert stages[0]["result_status"] == "success", stages
    return dict(stages[0]["handler"])
