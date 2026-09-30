"""Registry API on both backends (memory: unit tier; real: PostgreSQL + MinIO, integration tier)."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from typing import Any

from fastapi.testclient import TestClient

from jane_registry.archive import canonical_archive, digest_of, manifest_bytes
from jane_registry.testing import extractor_files, extractor_manifest, publish_body, zip_of


def key(name: str) -> dict[str, str]:
    return {"Idempotency-Key": f"{name}-{hashlib.sha256(name.encode()).hexdigest()[:8]}"}


def create(
    client: TestClient, package_id: str, *, auto: bool = True, kind: str = "extractor"
) -> dict[str, Any]:
    r = client.post(
        "/v1/packages",
        json={"package_id": package_id, "kind": kind, "title": "Demo", "auto_changes_allowed": auto},
        headers=key(f"create-{package_id}"),
    )
    assert r.status_code == 201, r.text
    return dict(r.json())


def publish(
    client: TestClient,
    package_id: str,
    version: str = "1.0.0",
    files: dict[str, bytes] | None = None,
    **mf: Any,
) -> Any:
    body = publish_body(extractor_manifest(package_id, version, **mf), files or extractor_files())
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]
    return client.post(
        f"/v1/packages/{package_id}/versions", json=body, headers={"Idempotency-Key": f"pub-{digest}"}
    )


def test_create_publish_get_archive(client: TestClient, uid: Any) -> None:
    pid = uid("demo")
    pkg = create(client, pid)
    assert pkg["latest_version"] is None and pkg["forks_count"] == 0
    r = publish(client, pid)
    assert r.status_code == 201, r.text
    v = r.json()
    assert r.headers["Location"] == f"/v1/packages/{pid}/versions/1.0.0"
    assert v["status"] == "draft" and v["test_status"] == "unknown" and v["created_by"] == "human"
    assert v["status_history"][0]["status"] == "draft"
    paths = [f["path"] for f in v["files"]]
    assert paths == sorted(paths) and "jane-package.json" in paths

    archive = client.get(f"/v1/packages/{pid}/versions/1.0.0/archive")
    assert archive.status_code == 200
    assert archive.headers["content-type"] == "application/zip"
    assert archive.headers["etag"] == f'"{v["digest"]}"'
    assert digest_of(archive.content) == v["digest"]
    # the stored archive is canonical: rebuilding it from its own files gives the same bytes
    with zipfile.ZipFile(io.BytesIO(archive.content)) as zf:
        files = {i.filename: zf.read(i) for i in zf.infolist()}
        assert all(
            i.compress_type == zipfile.ZIP_STORED and i.date_time == (1980, 1, 1, 0, 0, 0)
            for i in zf.infolist()
        )
    assert canonical_archive(files) == archive.content
    assert files["jane-package.json"] == manifest_bytes(extractor_manifest(pid))

    got = client.get(f"/v1/packages/{pid}").json()
    assert got["latest_version"] == "1.0.0"
    text = client.get(
        f"/v1/packages/{pid}/versions/1.0.0/file", params={"path": "src/demo_extractor/main.py"}
    )
    assert text.status_code == 200 and text.headers["content-type"].startswith("text/plain")
    assert "def extract" in text.text
    missing = client.get(f"/v1/packages/{pid}/versions/1.0.0/file", params={"path": "nope.txt"})
    assert missing.status_code == 404


def test_zip_and_json_publish_give_the_same_digest(client: TestClient, uid: Any) -> None:
    """The digest depends only on paths and contents: a deflated zip with directory entries is re-packed."""
    a, b = uid("zip-a"), uid("zip-b")
    create(client, a)
    create(client, b)
    files = extractor_files()
    j = client.post(
        f"/v1/packages/{a}/versions", json=publish_body(extractor_manifest(a), files), headers=key(f"j-{a}")
    )
    manifest_b = extractor_manifest(b)
    z = client.post(
        f"/v1/packages/{b}/versions",
        content=zip_of(manifest_b, files),
        headers={"Content-Type": "application/zip", **key(f"z-{b}")},
    )
    assert j.status_code == 201 and z.status_code == 201, z.text
    expected = digest_of(canonical_archive({**files, "jane-package.json": manifest_bytes(manifest_b)}))
    assert z.json()["digest"] == expected


def test_versions_are_immutable(client: TestClient, uid: Any) -> None:
    pid = uid("immutable")
    create(client, pid)
    first = publish(client, pid)
    assert first.status_code == 201
    again = publish(client, pid, files=extractor_files(extra={"README.md": b"changed"}))
    assert again.status_code == 409
    assert again.json()["code"] == "version_exists"
    same = client.get(f"/v1/packages/{pid}/versions/1.0.0").json()
    assert same["digest"] == first.json()["digest"]


def test_idempotent_publish_replays(client: TestClient, uid: Any) -> None:
    pid = uid("idem")
    create(client, pid)
    body = publish_body(extractor_manifest(pid), extractor_files())
    h = {"Idempotency-Key": f"idem-{pid}"}
    r1 = client.post(f"/v1/packages/{pid}/versions", json=body, headers=h)
    r2 = client.post(f"/v1/packages/{pid}/versions", json=body, headers=h)
    assert r1.status_code == r2.status_code == 201
    assert r2.headers["Idempotency-Replayed"] == "true"
    assert r2.json()["digest"] == r1.json()["digest"]
    other = client.post(f"/v1/packages/{pid}/versions", json={**body, "files": {}}, headers=h)
    assert other.status_code == 422 and other.json()["code"] == "idempotency_key_reused"
    no_key = client.post(f"/v1/packages/{pid}/versions", json=body)
    assert no_key.status_code == 422


def test_secret_detected(client: TestClient, uid: Any) -> None:
    pid = uid("secret")
    create(client, pid)
    fake_key = "AKIA" + "QX7Z" * 4  # built at run time so that the literal is not in the repository
    main = "API_KEY_ID = '" + fake_key + "'\n\ndef extract(material, params, ctx=None):\n    return {}\n"
    r = publish(client, pid, files=extractor_files(main_py=main))
    assert r.status_code == 422
    problem = r.json()
    assert problem["code"] == "secret_detected"
    assert problem["errors"][0]["pointer"] == "/files/src~1demo_extractor~1main.py"
    assert problem["errors"][0]["code"] == "aws_access_key"
    assert fake_key not in r.text  # the value is never echoed
    env = publish(client, pid, files=extractor_files(extra={".env": b"X=1\n"}))
    assert env.status_code == 422 and env.json()["errors"][0]["code"] == "secret_file"
    assert client.get(f"/v1/packages/{pid}/versions").json()["items"] == []


def test_dependency_not_allowed(client: TestClient, uid: Any) -> None:
    pid = uid("deps")
    create(client, pid)
    r = publish(
        client, pid, dependencies={"runtime_profile": "python-extractor@1", "python": ["requests>=2"]}
    )
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "dependency_not_allowed"
    assert body["errors"][0]["pointer"] == "/manifest/dependencies/python/0"
    old = publish(client, pid, dependencies={"runtime_profile": "python-extractor@1", "python": ["lxml<5"]})
    assert old.json()["code"] == "dependency_not_allowed"
    unknown = publish(client, pid, dependencies={"runtime_profile": "python-extractor@9", "python": []})
    assert unknown.json()["code"] == "dependency_not_allowed"
    ok = publish(
        client,
        pid,
        dependencies={
            "runtime_profile": "python-extractor@1",
            "python": ["lxml>=6", "pywin32; sys_platform == 'win32'"],
        },
    )
    assert ok.status_code == 201, ok.text


def test_manifest_validation(client: TestClient, uid: Any) -> None:
    pid = uid("invalid")
    create(client, pid)
    bad = publish(client, pid, version="latest")
    assert bad.status_code == 422 and bad.json()["code"] == "validation_failed"
    assert any(e["pointer"] == "/manifest/version" for e in bad.json()["errors"])
    wrong_id = client.post(
        f"/v1/packages/{pid}/versions",
        json=publish_body(extractor_manifest("someone.else"), extractor_files()),
        headers=key(f"wrong-{pid}"),
    )
    assert wrong_id.status_code == 422
    assert wrong_id.json()["errors"][0]["pointer"] == "/manifest/package_id"
    files = extractor_files()
    del files["tests/product/expected.json"]
    missing = publish(client, pid, files=files)
    assert missing.status_code == 422
    assert missing.json()["errors"][0]["code"] == "missing_file"
    no_tests = publish(client, pid, tests=[])
    assert no_tests.status_code == 422 and no_tests.json()["errors"][0]["code"] == "tests_required"
    storage_entry = publish(
        client, pid, entry={"executor": "storage", "adapter": "filesystem", "writes": "raw"}
    )
    assert storage_entry.json()["errors"][0]["code"] == "entry_kind_mismatch"
    traversal = client.post(
        f"/v1/packages/{pid}/versions",
        content=zip_of(extractor_manifest(pid), {**extractor_files(), "../evil.py": b"x"}),
        headers={"Content-Type": "application/zip", **key(f"trav-{pid}")},
    )
    assert traversal.status_code == 422
    bad_path = publish(client, pid, files=extractor_files(extra={"a/../../etc/passwd": b"x"}))
    assert bad_path.status_code == 422 and bad_path.json()["errors"][0]["code"] == "invalid_path"
    unknown_pkg = publish(client, uid("missing"))
    assert unknown_pkg.status_code == 404


def test_auto_changes_forbidden_for_llm(client: TestClient, uid: Any) -> None:
    pid = uid("locked")
    create(client, pid, auto=False)
    r = publish(
        client, pid, provenance={"created_by": "llm", "llm": {"model": "strong", "reason": "improvement"}}
    )
    assert r.status_code == 403 and r.json()["code"] == "forbidden"
    human = publish(client, pid, provenance={"created_by": "human"})
    assert human.status_code == 201
    patched = client.patch(
        f"/v1/packages/{pid}",
        content=json.dumps({"auto_changes_allowed": True}),
        headers={"Content-Type": "application/merge-patch+json"},
    )
    assert patched.status_code == 200 and patched.json()["auto_changes_allowed"] is True
    llm = publish(client, pid, version="1.1.0", provenance={"created_by": "llm"})
    assert llm.status_code == 201 and llm.json()["created_by"] == "llm"


def test_patch_with_if_match(client: TestClient, uid: Any) -> None:
    pid = uid("patch")
    create(client, pid)
    got = client.get(f"/v1/packages/{pid}")
    etag = got.headers["etag"]
    headers = {"Content-Type": "application/merge-patch+json"}
    ok = client.patch(
        f"/v1/packages/{pid}", content='{"title": "New"}', headers={**headers, "If-Match": etag}
    )
    assert ok.status_code == 200 and ok.json()["title"] == "New"
    assert ok.headers["etag"] != etag
    stale = client.patch(
        f"/v1/packages/{pid}", content='{"deprecated": true}', headers={**headers, "If-Match": etag}
    )
    assert stale.status_code == 412 and stale.json()["code"] == "precondition_failed"
    unknown = client.patch(f"/v1/packages/{pid}", content='{"nope": 1}', headers=headers)
    assert unknown.status_code == 422


def test_status_transitions_and_latest(client: TestClient, uid: Any) -> None:
    pid = uid("status")
    create(client, pid)
    assert publish(client, pid, "1.0.0").status_code == 201
    assert publish(client, pid, "1.2.0").status_code == 201
    assert publish(client, pid, "1.1.0").status_code == 201
    assert client.get(f"/v1/packages/{pid}").json()["latest_version"] == "1.2.0"
    url = f"/v1/packages/{pid}/versions/1.2.0/status"
    approved = client.post(
        url, json={"status": "approved", "reason": "tests passed"}, headers=key(f"a-{pid}")
    )
    assert approved.status_code == 200
    assert [h["status"] for h in approved.json()["status_history"]] == ["draft", "approved"]
    assert approved.json()["status_history"][1]["reason"] == "tests passed"
    back = client.post(url, json={"status": "rejected"}, headers=key(f"r-{pid}"))
    assert back.status_code == 409 and back.json()["code"] == "conflict"
    yanked = client.post(url, json={"status": "yanked"}, headers=key(f"y-{pid}"))
    assert yanked.status_code == 200
    assert client.get(f"/v1/packages/{pid}").json()["latest_version"] == "1.1.0"
    # a yanked version stays downloadable (existing bindings do not break)
    assert client.get(f"/v1/packages/{pid}/versions/1.2.0/archive").status_code == 200
    listed = client.get(f"/v1/packages/{pid}/versions", params={"status": "draft"}).json()["items"]
    assert [v["version"] for v in listed] == ["1.1.0", "1.0.0"]
    page1 = client.get(f"/v1/packages/{pid}/versions", params={"limit": 2}).json()
    page2 = client.get(
        f"/v1/packages/{pid}/versions", params={"limit": 2, "cursor": page1["next_cursor"]}
    ).json()
    assert [v["version"] for v in page1["items"] + page2["items"]] == ["1.1.0", "1.2.0", "1.0.0"]
    assert page2["next_cursor"] is None


def test_test_results(client: TestClient, uid: Any) -> None:
    pid = uid("tests")
    create(client, pid)
    v = publish(client, pid).json()
    report: dict[str, Any] = {
        "runner": "handler-runtime@0.1.0",
        "report": {
            "package": {"package_id": pid, "version": "1.0.0", "digest": v["digest"]},
            "passed": 2,
            "failed": 0,
            "cases": [{"name": "product-a100", "passed": True}, {"name": "category-empty", "passed": True}],
        },
    }
    url = f"/v1/packages/{pid}/versions/1.0.0/test-results"
    r = client.post(url, json=report, headers=key(f"t-{pid}"))
    assert r.status_code == 200, r.text
    assert r.json()["test_status"] == "passed" and r.json()["test_reports"][0]["recorded_at"]
    # one report per binding (context); every report is kept, test_status follows the latest one
    failed = {
        **report,
        "context": "bindings:shop-catalog/extract-products",
        "report": {**report["report"], "passed": 1, "failed": 1},
    }
    after = client.post(url, json=failed, headers=key(f"t2-{pid}")).json()
    assert after["test_status"] == "failed"
    assert [r.get("context") for r in after["test_reports"]] == [
        None,
        "bindings:shop-catalog/extract-products",
    ]
    wrong = {**report, "report": {**report["report"], "package": {"package_id": pid, "version": "9.9.9"}}}
    assert client.post(url, json=wrong, headers=key(f"t3-{pid}")).status_code == 422


def test_search(client: TestClient, uid: Any) -> None:
    pid = uid("search")
    create(client, pid)
    publish(client, pid, tags=["kettles"], bindings_hint={"domains": ["kettle-shop.test"]})
    rules = uid("rules")
    create(client, rules, kind="collector-rules")

    def ids(**params: Any) -> list[str]:
        return [p["package_id"] for p in client.get("/v1/packages", params=params).json()["items"]]

    assert (
        pid in ids(kind="extractor")
        and pid not in ids(kind="collector-rules")
        and rules in ids(kind="collector-rules")
    )
    assert pid in ids(tag="kettles") and pid not in ids(tag="phones")
    assert pid in ids(entity_type="product") and pid not in ids(entity_type="event")
    assert pid in ids(media_type="text/html") and pid not in ids(media_type="application/json")
    assert pid in ids(domain="www.kettle-shop.test") and pid not in ids(domain="other.test")
    assert pid in ids(q=pid[-8:]) and pid in ids(q="KETTLES")
    page = client.get("/v1/packages", params={"limit": 1}).json()
    assert len(page["items"]) == 1 and page["next_cursor"]


def test_collector_rules_package(client: TestClient, uid: Any) -> None:
    pid = uid("web-rules")
    create(client, pid, kind="collector-rules")
    rules = json.loads(open_example("collector-rules/web-shop.json"))
    manifest = {
        "schema_version": "1",
        "package_id": pid,
        "version": "1.0.0",
        "kind": "collector-rules",
        "title": "Shop rules",
        "entry": {"collector": "web", "rules": "rules.json"},
        "provenance": {"created_by": "human"},
    }
    ok = client.post(
        f"/v1/packages/{pid}/versions",
        json=publish_body(manifest, {"rules.json": json.dumps(rules).encode()}),
        headers=key(f"rules-{pid}"),
    )
    assert ok.status_code == 201, ok.text
    broken = client.post(
        f"/v1/packages/{pid}/versions",
        json=publish_body({**manifest, "version": "1.0.1"}, {"rules.json": b'{"typo_field": 1}'}),
        headers=key(f"rules2-{pid}"),
    )
    assert broken.status_code == 422
    assert broken.json()["errors"][0]["pointer"].startswith("/files/rules.json")


def open_example(name: str) -> str:
    from jane_kit.contracts import contracts_dir

    root = contracts_dir()
    assert root is not None
    return (root / "examples" / "schemas" / name).read_text(encoding="utf-8")


def test_payload_too_large(backend: Any, uid: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("JANE_REGISTRY_LIMITS__REQUESTS__MAX_REQUEST_BODY_BYTES", "2048")
    with backend.client() as c:
        pid = uid("big")
        create(c, pid)
        r = publish(c, pid, files=extractor_files(extra={"big.txt": b"x" * 4096}))
        assert r.status_code == 413 and r.json()["code"] == "payload_too_large"


def test_max_versions_limit(backend: Any, uid: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("JANE_REGISTRY_LIMITS__PACKAGES__MAX_VERSIONS_PER_PACKAGE", "2")
    with backend.client() as c:
        pid = uid("cap")
        create(c, pid)
        assert publish(c, pid, "1.0.0").status_code == 201
        assert publish(c, pid, "1.0.1").status_code == 201
        third = publish(c, pid, "1.0.2")
        assert third.status_code == 422 and third.json()["code"] == "limit_exceeded"
        info = c.get("/v1/info").json()
        assert info["limits"]["defaults"]["transfer"]["max_request_body_bytes"] > 0


def test_health_and_metrics(client: TestClient) -> None:
    health = client.get("/v1/health").json()
    assert health["status"] == "ok" and set(health["checks"]) == {"metadata_store", "blob_store"}
    info = client.get("/v1/info").json()
    assert info["service"] == "registry" and info["capabilities"]["archive"]["compression"] == "stored"
    assert "jane_http_requests_total" in client.get("/metrics").text


def test_review1_scan_limit_encodings_and_paths(backend: Any, uid: Any, monkeypatch: Any) -> None:
    """Review 1: a file too large to scan is refused, not accepted; UTF-16 text is scanned; case-only and
    dot-segment path variants are rejected."""
    monkeypatch.setenv("JANE_REGISTRY_LIMITS__SECRETS__MAX_SCAN_BYTES_PER_FILE", "4096")
    with backend.client() as c:
        pid = uid("review1")
        create(c, pid)
        aws = "AKIA" + "QX7Z" * 4
        padded = b"#" * 4096 + f"\nK = '{aws}'\n".encode()
        big = publish(c, pid, files=extractor_files(extra={"src/demo_extractor/pad.py": padded}))
        assert big.status_code == 422 and big.json()["code"] == "limit_exceeded"
        assert big.json()["details"]["path"] == "secrets.max_scan_bytes_per_file"
        assert big.json()["errors"][0]["pointer"] == "/files/src~1demo_extractor~1pad.py"
        utf16 = ('{"k": "' + aws + '"}').encode("utf-16")
        hidden = publish(c, pid, files=extractor_files(extra={"tests/cfg.json": utf16}))
        assert hidden.status_code == 422 and hidden.json()["code"] == "secret_detected"
        case = publish(
            c, pid, files=extractor_files(extra={"tests/Readme.txt": b"1", "tests/README.txt": b"2"})
        )
        assert case.status_code == 422 and case.json()["errors"][0]["code"] == "duplicate_path"
        dot = publish(c, pid, files=extractor_files(extra={"src/demo_extractor/./x.py": b"1"}))
        assert dot.status_code == 422 and dot.json()["errors"][0]["code"] == "invalid_path"
        assert c.get(f"/v1/packages/{pid}/versions").json()["items"] == []
