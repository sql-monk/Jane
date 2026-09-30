"""Forks, diff, upstream status and explicit upstream ports (TZ §7, criteria 7 and 9).

``test_parent_update_does_not_change_fork`` is the WP-05 "done when" check; with the ``real`` backend it
runs on PostgreSQL + MinIO of the dev stack.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from fastapi.testclient import TestClient

from jane_registry.testing import MAIN_PY, extractor_files, extractor_manifest, publish_body


def key(body: Any, prefix: str) -> dict[str, str]:
    return {
        "Idempotency-Key": f"{prefix}-{hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]}"
    }


def create(client: TestClient, pid: str, **extra: Any) -> None:
    body = {"package_id": pid, "kind": "extractor", "title": "Parent", **extra}
    assert client.post("/v1/packages", json=body, headers=key(body, "c")).status_code == 201


def publish(client: TestClient, pid: str, version: str, main_py: str = MAIN_PY, **mf: Any) -> dict[str, Any]:
    body = publish_body(extractor_manifest(pid, version, **mf), extractor_files(main_py=main_py))
    r = client.post(f"/v1/packages/{pid}/versions", json=body, headers=key(body, "p"))
    assert r.status_code == 201, r.text
    return dict(r.json())


def fork(client: TestClient, parent: str, new: str, from_version: str, **extra: Any) -> Any:
    body = {"new_package_id": new, "from_version": from_version, **extra}
    return client.post(f"/v1/packages/{parent}/forks", json=body, headers=key(body, "f"))


def wait_job(client: TestClient, job_id: str, timeout_s: float = 30) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed", "cancelled"}:
            return dict(job)
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not finish")


def port(client: TestClient, pid: str, **body: Any) -> dict[str, Any]:
    r = client.post(f"/v1/packages/{pid}/upstream-ports", json=body, headers=key(body, f"port-{pid}"))
    assert r.status_code == 202, r.text
    assert r.headers["Location"] == f"/v1/jobs/{r.json()['job_id']}"
    return wait_job(client, r.json()["job_id"])


PARENT_V2 = MAIN_PY.replace('"title": m.group(2).strip()', '"title": m.group(2).strip(), "source": "h1"')
FORK_V2 = MAIN_PY.replace("import re\n", "import re\n\nFORK_MARKER = 'acme'\n")


def snapshot(client: TestClient, pid: str) -> dict[str, Any]:
    """Everything a consumer of the fork can observe."""
    versions = client.get(f"/v1/packages/{pid}/versions").json()["items"]
    out: dict[str, Any] = {"package": client.get(f"/v1/packages/{pid}").json(), "versions": {}}
    out["package"].pop("forks_count", None)
    for v in versions:
        full = client.get(f"/v1/packages/{pid}/versions/{v['version']}").json()
        archive = client.get(f"/v1/packages/{pid}/versions/{v['version']}/archive")
        out["versions"][v["version"]] = {
            "digest": full["digest"],
            "manifest": full["manifest"],
            "files": full["files"],
            "archive_sha256": hashlib.sha256(archive.content).hexdigest(),
            "etag": archive.headers["etag"],
        }
    return out


def test_parent_update_does_not_change_fork(client: TestClient, uid: Any) -> None:
    parent, child = uid("parent"), uid("acme")
    create(client, parent)
    p1 = publish(client, parent, "1.0.0")
    created = fork(client, parent, child, "1.0.0", title="ACME fork")
    assert created.status_code == 201, created.text
    pkg = created.json()
    assert pkg["fork_of"] == {"package_id": parent, "version": "1.0.0", "digest": p1["digest"]}
    assert pkg["latest_version"] == "1.0.0" and pkg["auto_changes_allowed"] is False
    assert created.headers["Location"] == f"/v1/packages/{child}"
    first = client.get(f"/v1/packages/{child}/versions/1.0.0").json()
    assert first["manifest"]["package_id"] == child
    assert first["manifest"]["fork_of"] == pkg["fork_of"]
    assert first["manifest"]["provenance"]["based_on"] == pkg["fork_of"]
    before = snapshot(client, child)

    # every kind of change to the parent: new versions, status changes, settings
    p2 = publish(client, parent, "1.1.0", main_py=PARENT_V2)
    publish(client, parent, "2.0.0", main_py=PARENT_V2, title="Parent v2")
    for version, status in [("1.0.0", "approved"), ("1.0.0", "deprecated"), ("1.0.0", "yanked")]:
        body = {"status": status}
        r = client.post(
            f"/v1/packages/{parent}/versions/{version}/status", json=body, headers=key(body, version)
        )
        assert r.status_code == 200, r.text
    patch = client.patch(
        f"/v1/packages/{parent}",
        content=json.dumps({"title": "Renamed parent", "deprecated": True}),
        headers={"Content-Type": "application/merge-patch+json"},
    )
    assert patch.status_code == 200

    after = snapshot(client, child)
    assert after == before, "a parent update changed the fork"
    assert client.get(f"/v1/packages/{parent}").json()["forks_count"] == 1
    assert [
        p["package_id"] for p in client.get("/v1/packages", params={"fork_of": parent}).json()["items"]
    ] == [child]

    # the fork sees the updates only as information
    up = client.get(f"/v1/packages/{child}/upstream").json()
    assert up["last_ported_version"] == "1.0.0"
    assert up["newer_parent_versions"] == ["1.1.0", "2.0.0"]
    assert up["parent_latest_version"] == "2.0.0"
    diff = client.get(f"/v1/packages/{child}/diff", params={"from": "1.0.0", "to": "parent:1.1.0"}).json()
    assert diff["to"] == {"package_id": parent, "version": "1.1.0", "digest": p2["digest"]}
    changed = {f["path"]: f for f in diff["files"] if f["status"] != "unchanged"}
    assert list(changed) == ["src/demo_extractor/main.py"]
    assert (
        '+    fields = {"sku": m.group(1), "title": m.group(2).strip(), "source": "h1"}'
        in changed["src/demo_extractor/main.py"]["unified_diff"]
    )
    assert {c["pointer"] for c in diff["manifest_changes"]} >= {"/package_id", "/fork_of", "/version"}


def test_fork_errors(client: TestClient, uid: Any) -> None:
    parent, child = uid("parent"), uid("child")
    create(client, parent)
    publish(client, parent, "1.0.0")
    assert fork(client, parent, child, "9.9.9").status_code == 404
    assert fork(client, uid("nobody"), child, "1.0.0").status_code == 404
    assert fork(client, parent, child, "1.0.0").status_code == 201
    dup = fork(client, parent, child, "1.0.0", title="again")
    assert dup.status_code == 409 and dup.json()["code"] == "conflict"
    not_fork = client.get(f"/v1/packages/{parent}/upstream")
    assert not_fork.status_code == 409 and not_fork.json()["code"] == "conflict"
    # a fork's new version must carry fork_of unchanged
    body = publish_body(extractor_manifest(child, "1.0.1"), extractor_files())
    r = client.post(f"/v1/packages/{child}/versions", json=body, headers=key(body, "nf"))
    assert r.status_code == 422 and r.json()["errors"][0]["pointer"] == "/manifest/fork_of"


def test_fork_of_llm_package_with_locked_fork(client: TestClient, uid: Any) -> None:
    """The fork command is a user's action: an LLM-made parent can be forked into a locked package, but
    the LLM cannot then publish into that fork."""
    parent, child = uid("llm-parent"), uid("locked-fork")
    create(client, parent)
    publish(client, parent, "1.0.0", provenance={"created_by": "llm"})
    created = fork(client, parent, child, "1.0.0", initial_version="0.1.0")
    assert created.status_code == 201, created.text
    assert created.json()["latest_version"] == "0.1.0"
    fork_of = created.json()["fork_of"]
    body = publish_body(
        extractor_manifest(child, "0.2.0", fork_of=fork_of, provenance={"created_by": "llm"}),
        extractor_files(),
    )
    r = client.post(f"/v1/packages/{child}/versions", json=body, headers=key(body, "llm"))
    assert r.status_code == 403 and r.json()["code"] == "forbidden"


def test_diff_between_versions(client: TestClient, uid: Any) -> None:
    pid = uid("diff")
    create(client, pid)
    publish(client, pid, "1.0.0")
    publish(
        client,
        pid,
        "1.1.0",
        main_py=PARENT_V2,
        provenance={"created_by": "human", "change_summary": "source"},
    )
    d = client.get(f"/v1/packages/{pid}/diff", params={"to": "1.1.0", "context_lines": 0}).json()
    assert d["from"]["version"] == "1.0.0"  # default: previous version
    assert {"pointer": "/version", "op": "replace", "old": "1.0.0", "new": "1.1.0"} in d["manifest_changes"]
    assert {"pointer": "/provenance/change_summary", "op": "add", "new": "source"} in d["manifest_changes"]
    main = next(f for f in d["files"] if f["path"] == "src/demo_extractor/main.py")
    assert main["status"] == "modified" and "@@" in main["unified_diff"]
    first = client.get(f"/v1/packages/{pid}/diff", params={"to": "1.0.0"})
    assert first.status_code == 422
    assert client.get(f"/v1/packages/{pid}/diff", params={"from": "0.0.1", "to": "1.0.0"}).status_code == 404
    assert (
        client.get(f"/v1/packages/{pid}/diff", params={"from": "parent:1.0.0", "to": "1.0.0"}).status_code
        == 422
    )


def test_explicit_upstream_port(client: TestClient, uid: Any) -> None:
    parent, child = uid("parent"), uid("fork")
    create(client, parent)
    publish(client, parent, "1.0.0")
    assert fork(client, parent, child, "1.0.0").status_code == 201
    fork_of = client.get(f"/v1/packages/{child}").json()["fork_of"]
    # the fork evolves on its own (a different region of the same file)
    body = publish_body(
        extractor_manifest(
            child,
            "1.0.1",
            fork_of=fork_of,
            tags=["demo", "products", "acme"],
            provenance={"created_by": "human", "based_on": {"package_id": child, "version": "1.0.0"}},
        ),
        extractor_files(main_py=FORK_V2),
    )
    assert (
        client.post(f"/v1/packages/{child}/versions", json=body, headers=key(body, "f2")).status_code == 201
    )
    publish(client, parent, "1.1.0", main_py=PARENT_V2, description="now with source")

    # nothing is applied without the explicit command
    assert client.get(f"/v1/packages/{child}").json()["latest_version"] == "1.0.1"

    job = port(client, child, parent_version="1.1.0", new_version="1.1.0")
    assert job["status"] == "succeeded", job
    assert job["kind"] == "upstream_port"
    result = job["result"]
    assert result["version"] == "1.1.0" and result["status"] == "draft"
    manifest = result["manifest"]
    assert manifest["provenance"]["upstream_port"] == {"parent_version": "1.1.0", "requested_by": "anonymous"}
    assert manifest["provenance"]["based_on"]["version"] == "1.0.1"
    assert manifest["fork_of"] == fork_of  # unchanged
    assert manifest["package_id"] == child
    assert manifest["tags"] == ["demo", "products", "acme"]  # the fork's change is kept
    assert manifest["description"] == "now with source"  # the parent's change is brought in
    code = client.get(
        f"/v1/packages/{child}/versions/1.1.0/file", params={"path": "src/demo_extractor/main.py"}
    ).text
    assert "FORK_MARKER = 'acme'" in code and '"source": "h1"' in code
    up = client.get(f"/v1/packages/{child}/upstream").json()
    assert up["last_ported_version"] == "1.1.0" and up["newer_parent_versions"] == []
    # the port is itself a new immutable version
    again = client.post(
        f"/v1/packages/{child}/upstream-ports",
        json={"parent_version": "1.1.0", "new_version": "1.1.0"},
        headers={"Idempotency-Key": f"again-{child}"},
    )
    assert again.status_code == 409 and again.json()["code"] == "version_exists"


def test_upstream_port_conflict_applies_nothing(client: TestClient, uid: Any) -> None:
    parent, child = uid("parent"), uid("fork")
    create(client, parent)
    publish(client, parent, "1.0.0")
    fork_of = fork(client, parent, child, "1.0.0").json()["fork_of"]
    ours = MAIN_PY.replace('"title": m.group(2).strip()', '"title": m.group(2).upper()')
    body = publish_body(extractor_manifest(child, "1.0.1", fork_of=fork_of), extractor_files(main_py=ours))
    assert (
        client.post(f"/v1/packages/{child}/versions", json=body, headers=key(body, "c1")).status_code == 201
    )
    publish(client, parent, "1.1.0", main_py=PARENT_V2)
    job = port(client, child, parent_version="1.1.0", base_version="1.0.1", new_version="1.1.0")
    assert job["status"] == "failed"
    assert job["error"]["code"] == "upstream_conflict"
    assert job["error"]["details"]["conflicts"] == [
        {"path": "src/demo_extractor/main.py", "reason": "1 conflicting hunk(s)"}
    ]
    versions = [v["version"] for v in client.get(f"/v1/packages/{child}/versions").json()["items"]]
    assert versions == ["1.0.1", "1.0.0"]
    missing = client.post(
        f"/v1/packages/{child}/upstream-ports",
        json={"parent_version": "7.0.0", "new_version": "7.0.0"},
        headers={"Idempotency-Key": f"missing-{child}"},
    )
    assert missing.status_code == 404
    not_fork = client.post(
        f"/v1/packages/{parent}/upstream-ports",
        json={"parent_version": "1.1.0", "new_version": "1.2.0"},
        headers={"Idempotency-Key": f"nf-{parent}"},
    )
    assert not_fork.status_code == 409
