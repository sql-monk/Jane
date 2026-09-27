"""Operational behaviour: API keys and scopes, several instances on one database, runtime profiles by URL."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from jane_registry.app import build_app
from jane_registry.profiles import ProfileSource
from jane_registry.settings import ProfileLimits, Settings
from jane_registry.testing import TEST_PROFILE, extractor_files, extractor_manifest, publish_body


def test_api_keys_and_scopes(tmp_path: Path, profile_file: Path) -> None:
    keys = {
        "reader": ["registry:read"],
        "writer": ["registry:read", "registry:write"],
        "admin": sorted(["registry:read", "registry:write", "registry:approve"]),
    }
    doc = [
        {"name": n, "sha256": hashlib.sha256(f"key-{n}".encode()).hexdigest(), "scopes": s}
        for n, s in keys.items()
    ]
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps(doc), encoding="utf-8")
    settings = Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path / "b",
        auth_mode="api_key",
        api_keys_file=keys_file,
        runtime_profiles=[str(profile_file)],
    )

    def auth(name: str) -> dict[str, str]:
        return {"Authorization": f"Bearer key-{name}"}

    with TestClient(build_app(settings)) as c:
        assert c.get("/v1/health").status_code == 200  # no auth for health
        assert c.get("/v1/info").json()["auth_mode"] == "api_key"
        assert c.get("/v1/packages").status_code == 401
        assert c.get("/v1/packages", headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert c.get("/v1/packages", headers=auth("reader")).status_code == 200
        body = {"package_id": "auth.pkg", "kind": "extractor", "title": "A"}
        denied = c.post("/v1/packages", json=body, headers={**auth("reader"), "Idempotency-Key": "a1"})
        assert denied.status_code == 403 and denied.json()["code"] == "forbidden"
        assert (
            c.post("/v1/packages", json=body, headers={**auth("writer"), "Idempotency-Key": "a2"}).status_code
            == 201
        )
        pub = publish_body(extractor_manifest("auth.pkg"), extractor_files())
        v = c.post(
            "/v1/packages/auth.pkg/versions", json=pub, headers={**auth("writer"), "Idempotency-Key": "a3"}
        )
        assert v.status_code == 201 and v.json()["published_by"] == "writer"
        url = "/v1/packages/auth.pkg/versions/1.0.0/status"
        assert (
            c.post(
                url, json={"status": "approved"}, headers={**auth("writer"), "Idempotency-Key": "a4"}
            ).status_code
            == 403
        )
        ok = c.post(url, json={"status": "approved"}, headers={**auth("admin"), "Idempotency-Key": "a5"})
        assert ok.status_code == 200 and ok.json()["status_history"][-1]["by"] == "admin"
        assert c.get("/v1/packages/auth.pkg", headers=auth("reader")).json()["owner"] == "writer"


def test_jwt_mode_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="jwt"):
        build_app(Settings(db="memory", blob="filesystem", blob_root=tmp_path, auth_mode="jwt"))


async def test_profiles_from_runtime_info_url() -> None:
    info = {
        "service": "handler-runtime",
        "capabilities": {"runtime_profiles": {"python-extractor@1": TEST_PROFILE}},
    }
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(200, json=info)

    source = ProfileSource(
        ["http://runtime.test/v1/info"], ProfileLimits(), transport=httpx.MockTransport(handler)
    )
    assert set(await source.profiles()) == {"python-extractor@1"}
    await source.profiles()  # cached for refresh_seconds
    assert calls == ["http://runtime.test/v1/info"]

    def failing(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    broken = ProfileSource(
        ["http://runtime.test/v1/info"], ProfileLimits(), transport=httpx.MockTransport(failing)
    )
    assert await broken.profiles() == {}
    assert broken.errors and "503" in broken.errors[0]


def test_unreachable_profile_source_is_retryable(tmp_path: Path, uid: Any) -> None:
    settings = Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path,
        runtime_profiles=[str(tmp_path / "missing.json")],
    )
    with TestClient(build_app(settings)) as c:
        pid = uid("prof")
        c.post(
            "/v1/packages",
            json={"package_id": pid, "kind": "extractor", "title": "P"},
            headers={"Idempotency-Key": pid},
        )
        r = c.post(
            f"/v1/packages/{pid}/versions",
            json=publish_body(extractor_manifest(pid), extractor_files()),
            headers={"Idempotency-Key": f"v-{pid}"},
        )
        assert (
            r.status_code == 502
            and r.json()["code"] == "upstream_unavailable"
            and r.json()["retryable"] is True
        )


@pytest.mark.integration
def test_several_instances_share_state(real_backend: Any, profile_file: Path, uid: Any) -> None:
    """Two registry instances on the same PostgreSQL + MinIO: one publishes, the other serves; a
    concurrent publish of the same version succeeds exactly once; idempotency keys are shared."""
    schema = f"t_{uid('multi').split('-')[1]}"
    settings = real_backend.settings(schema, runtime_profiles=[str(profile_file)])
    with TestClient(build_app(settings)) as a, TestClient(build_app(settings)) as b:
        pid = uid("multi")
        assert (
            a.post(
                "/v1/packages",
                json={"package_id": pid, "kind": "extractor", "title": "M"},
                headers={"Idempotency-Key": f"c-{pid}"},
            ).status_code
            == 201
        )
        body = publish_body(extractor_manifest(pid), extractor_files())
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(
                    c.post,
                    f"/v1/packages/{pid}/versions",
                    json=body,
                    headers={"Idempotency-Key": f"{name}-{pid}"},
                )
                for name, c in (("a", a), ("b", b))
            ]
            codes = sorted(f.result().status_code for f in futures)
        assert codes == [201, 409]
        got = b.get(f"/v1/packages/{pid}/versions/1.0.0")
        assert got.status_code == 200
        archive = b.get(f"/v1/packages/{pid}/versions/1.0.0/archive")
        assert archive.headers["etag"] == f'"{got.json()["digest"]}"'
        replay = b.post(f"/v1/packages/{pid}/versions", json=body, headers={"Idempotency-Key": f"a-{pid}"})
        first = a.post(f"/v1/packages/{pid}/versions", json=body, headers={"Idempotency-Key": f"a-{pid}"})
        assert replay.status_code == first.status_code
        assert replay.headers.get("Idempotency-Replayed") == "true"
        # a job started on one instance is visible on the other
        fork = {"new_package_id": f"{pid}-fork", "from_version": "1.0.0"}
        assert (
            a.post(
                f"/v1/packages/{pid}/forks", json=fork, headers={"Idempotency-Key": f"f-{pid}"}
            ).status_code
            == 201
        )
        job = a.post(
            f"/v1/packages/{pid}-fork/upstream-ports",
            json={"parent_version": "1.0.0", "new_version": "1.0.1"},
            headers={"Idempotency-Key": f"u-{pid}"},
        ).json()
        seen = b.get(f"/v1/jobs/{job['job_id']}")
        assert seen.status_code == 200 and seen.json()["kind"] == "upstream_port"
