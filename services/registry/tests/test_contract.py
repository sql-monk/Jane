"""Contract tests: every operation of ``contracts/openapi/registry.v1.yaml`` is called on the real app and
each response is validated against the contract (``ContractClient``); ``uncovered()`` must be empty."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import ContractClient, OpenAPISpec, contracts_dir
from jane_registry.app import build_app
from jane_registry.settings import Settings
from jane_registry.testing import (
    MAIN_PY,
    TEST_PROFILE,
    extractor_files,
    extractor_manifest,
    publish_body,
    zip_of,
)

pytestmark = pytest.mark.contract

CONTRACTS = contracts_dir(Path(__file__).parent)
SERVICE_SPEC = CONTRACTS / "openapi" / "registry.v1.yaml" if CONTRACTS else None


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps(TEST_PROFILE), encoding="utf-8")
    settings = Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path / "blobs",
        runtime_profiles=[str(profile)],
    )
    with TestClient(build_app(settings)) as c:
        yield c


@pytest.fixture(scope="module")
def spec() -> OpenAPISpec:
    if SERVICE_SPEC is None or not SERVICE_SPEC.is_file():
        pytest.skip("contracts/openapi/registry.v1.yaml not available")
    return OpenAPISpec.load(SERVICE_SPEC)


JSON = {"Content-Type": "application/json"}


def _key(name: str) -> dict[str, str]:
    return {"Idempotency-Key": name}


def test_common_resources_match_contract(client: TestClient) -> None:
    assert CONTRACTS is not None
    common = OpenAPISpec.load(CONTRACTS / "openapi" / "common.yaml")
    common.validate_component("Health", client.get("/v1/health").json())
    common.validate_component("ServiceInfo", client.get("/v1/info").json())
    common.validate_component("Problem", client.get("/v1/jobs/unknown").json())


def test_every_operation_matches_contract(client: TestClient, spec: OpenAPISpec) -> None:
    api = ContractClient(spec, client)
    api.get("/v1/health")
    api.get("/v1/info")
    pid, fork_id = "contract.parent", "contract.fork"

    assert (
        api.post(
            "/v1/packages", json={"package_id": pid, "kind": "extractor", "title": "P"}, headers=_key("c1")
        ).status_code
        == 201
    )
    assert (
        api.post(
            "/v1/packages", json={"package_id": pid, "kind": "extractor", "title": "P"}, headers=_key("c2")
        ).status_code
        == 409
    )
    assert (
        api.post(
            "/v1/packages",
            content=json.dumps({"package_id": "Bad Id", "kind": "extractor", "title": "P"}),
            headers={**JSON, **_key("c3")},
        ).status_code
        == 422
    )
    assert api.get("/v1/packages", params={"kind": "extractor", "q": "contract"}).status_code == 200
    assert api.get(f"/v1/packages/{pid}").status_code == 200
    assert api.get("/v1/packages/nothing.here").status_code == 404
    patch = {"Content-Type": "application/merge-patch+json"}
    assert api.patch(f"/v1/packages/{pid}", content=b'{"description": "d"}', headers=patch).status_code == 200
    assert (
        api.patch(
            f"/v1/packages/{pid}", content=b'{"title": "x"}', headers={**patch, "If-Match": '"r0"'}
        ).status_code
        == 412
    )
    assert api.patch(f"/v1/packages/{pid}", content=b'{"nope": 1}', headers=patch).status_code == 422
    assert api.patch("/v1/packages/nothing.here", content=b'{"title": "x"}', headers=patch).status_code == 404

    body = publish_body(extractor_manifest(pid, "1.0.0"), extractor_files())
    assert api.post(f"/v1/packages/{pid}/versions", json=body, headers=_key("p1")).status_code == 201
    assert api.post(f"/v1/packages/{pid}/versions", json=body, headers=_key("p2")).status_code == 409
    zip_body = zip_of(extractor_manifest(pid, "1.1.0"), extractor_files(main_py=MAIN_PY + "\n# v1.1\n"))
    r = api.post(
        f"/v1/packages/{pid}/versions",
        content=zip_body,
        headers={"Content-Type": "application/zip", **_key("p3")},
    )
    assert r.status_code == 201
    secret = extractor_files(main_py="token = 'ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8" + "'\n")
    bad = publish_body(extractor_manifest(pid, "1.2.0"), secret)
    assert (
        api.post(f"/v1/packages/{pid}/versions", json=bad, headers=_key("p4")).json()["code"]
        == "secret_detected"
    )
    assert (
        api.post(
            f"/v1/packages/{pid}/versions",
            content=b"{",
            headers={"Content-Type": "application/json", **_key("p5")},
        ).status_code
        == 400
    )
    assert api.post("/v1/packages/nothing.here/versions", json=body, headers=_key("p6")).status_code == 404

    assert api.get(f"/v1/packages/{pid}/versions").status_code == 200
    assert api.get("/v1/packages/nothing.here/versions").status_code == 404
    assert api.get(f"/v1/packages/{pid}/versions/1.0.0").status_code == 200
    assert api.get(f"/v1/packages/{pid}/versions/9.0.0").status_code == 404
    assert api.get(f"/v1/packages/{pid}/versions/1.0.0/archive").status_code == 200
    assert api.get(f"/v1/packages/{pid}/versions/9.0.0/archive").status_code == 404
    assert (
        api.get(
            f"/v1/packages/{pid}/versions/1.0.0/file", params={"path": "src/demo_extractor/main.py"}
        ).status_code
        == 200
    )
    assert (
        api.get(f"/v1/packages/{pid}/versions/1.0.0/file", params={"path": "absent.txt"}).status_code == 404
    )

    status = f"/v1/packages/{pid}/versions/1.0.0/status"
    assert (
        api.post(status, json={"status": "approved", "reason": "ok"}, headers=_key("s1")).status_code == 200
    )
    assert api.post(status, json={"status": "rejected"}, headers=_key("s2")).status_code == 409
    assert (
        api.post(
            f"/v1/packages/{pid}/versions/9.0.0/status", json={"status": "approved"}, headers=_key("s3")
        ).status_code
        == 404
    )

    report = {
        "runner": "handler-runtime@0.1.0",
        "report": {"package": {"package_id": pid, "version": "1.0.0"}, "passed": 2, "failed": 0, "cases": []},
    }
    tests = f"/v1/packages/{pid}/versions/1.0.0/test-results"
    assert api.post(tests, json=report, headers=_key("t1")).status_code == 200
    assert (
        api.post(
            tests, content=json.dumps({"report": {"passed": 1}}), headers={**JSON, **_key("t2")}
        ).status_code
        == 422
    )
    assert (
        api.post(
            f"/v1/packages/{pid}/versions/9.0.0/test-results", json=report, headers=_key("t3")
        ).status_code
        == 404
    )

    fork = {"new_package_id": fork_id, "from_version": "1.0.0", "title": "Fork"}
    assert api.post(f"/v1/packages/{pid}/forks", json=fork, headers=_key("f1")).status_code == 201
    assert (
        api.post(f"/v1/packages/{pid}/forks", json={**fork, "title": "again"}, headers=_key("f2")).status_code
        == 409
    )
    assert api.post("/v1/packages/nothing.here/forks", json=fork, headers=_key("f3")).status_code == 404

    assert api.get(f"/v1/packages/{pid}/diff", params={"from": "1.0.0", "to": "1.1.0"}).status_code == 200
    assert (
        api.get(f"/v1/packages/{fork_id}/diff", params={"from": "1.0.0", "to": "parent:1.1.0"}).status_code
        == 200
    )
    assert api.get(f"/v1/packages/{pid}/diff", params={"to": "7.0.0"}).status_code == 404
    assert api.get(f"/v1/packages/{fork_id}/upstream").status_code == 200
    assert api.get(f"/v1/packages/{pid}/upstream").status_code == 409
    assert api.get("/v1/packages/nothing.here/upstream").status_code == 404

    port = {"parent_version": "1.1.0", "new_version": "1.1.0"}
    accepted = api.post(f"/v1/packages/{fork_id}/upstream-ports", json=port, headers=_key("u1"))
    assert accepted.status_code == 202
    assert api.post(f"/v1/packages/{pid}/upstream-ports", json=port, headers=_key("u2")).status_code == 409
    assert (
        api.post("/v1/packages/nothing.here/upstream-ports", json=port, headers=_key("u3")).status_code == 404
    )
    assert (
        api.post(
            f"/v1/packages/{fork_id}/upstream-ports",
            content=json.dumps({"parent_version": "x"}),
            headers={**JSON, **_key("u4")},
        ).status_code
        == 422
    )
    job_id = accepted.json()["job_id"]
    for _ in range(200):
        job = api.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed"}:
            break
        time.sleep(0.02)
    assert job["status"] == "succeeded", job
    spec.validate_component("PackageVersion", job["result"])
    assert api.post(f"/v1/jobs/{job_id}/cancel").status_code == 200  # already terminal

    assert api.uncovered() == []


def test_forbidden_is_documented(client: TestClient, spec: OpenAPISpec) -> None:
    api = ContractClient(spec, client)
    body = {"package_id": "locked.pkg", "kind": "extractor", "title": "L", "auto_changes_allowed": False}
    api.post("/v1/packages", json=body, headers=_key("l1"))
    llm = publish_body(extractor_manifest("locked.pkg", provenance={"created_by": "llm"}), extractor_files())
    r = api.post("/v1/packages/locked.pkg/versions", json=llm, headers=_key("l2"))
    assert r.status_code == 403 and r.json()["code"] == "forbidden"
