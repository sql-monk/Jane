"""Operational behaviour: API keys and scopes, several instances on one database, runtime profiles by URL."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import time
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
        # common.yaml Info has bearerAuth and 401: any valid key reads it (ADR-0005, M3 auth)
        assert c.get("/v1/info").status_code == 401
        assert c.get("/v1/info", headers=auth("reader")).json()["auth_mode"] == "api_key"
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
            results = {name: f.result() for name, f in zip(("a", "b"), futures, strict=True)}
        assert sorted(r.status_code for r in results.values()) == [201, 409]
        winner = next(name for name, r in results.items() if r.status_code == 201)
        other = b if winner == "a" else a
        got = b.get(f"/v1/packages/{pid}/versions/1.0.0")
        assert got.status_code == 200
        archive = b.get(f"/v1/packages/{pid}/versions/1.0.0/archive")
        assert archive.headers["etag"] == f'"{got.json()["digest"]}"'
        # the winner's key replays its stored 201 on the other instance (keys live in PostgreSQL)
        replay = other.post(
            f"/v1/packages/{pid}/versions", json=body, headers={"Idempotency-Key": f"{winner}-{pid}"}
        )
        assert replay.status_code == 201
        assert replay.headers.get("Idempotency-Replayed") == "true"
        assert replay.json()["digest"] == results[winner].json()["digest"]
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


def _keys_settings(tmp_path: Path, profile_file: Path, keys: dict[str, tuple[list[str], str]]) -> Settings:
    doc = [
        {"name": n, "sha256": hashlib.sha256(f"key-{n}".encode()).hexdigest(), "scopes": s, "actor": a}
        for n, (s, a) in keys.items()
    ]
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps(doc), encoding="utf-8")
    return Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path / "b",
        auth_mode="api_key",
        api_keys_file=keys_file,
        runtime_profiles=[str(profile_file)],
    )


def test_review1_scopes_and_actor(tmp_path: Path, profile_file: Path) -> None:
    """Allowing automatic changes needs registry:approve; cancelling a job needs registry:write; an llm key
    publishes only created_by=llm versions and its upstream ports are recorded as llm."""
    rw = ["registry:read", "registry:write"]
    settings = _keys_settings(
        tmp_path,
        profile_file,
        {
            "reader": (["registry:read"], "human"),
            "writer": (rw, "human"),
            "admin": ([*rw, "registry:approve"], "human"),
            "assistant": (rw, "llm"),
        },
    )

    def h(name: str, key: str | None = None) -> dict[str, str]:
        out = {"Authorization": f"Bearer key-{name}"}
        if key:
            out["Idempotency-Key"] = key
        return out

    patch_ct = {"Content-Type": "application/merge-patch+json"}
    with TestClient(build_app(settings)) as c:
        body = {"package_id": "locked.pkg", "kind": "extractor", "title": "L", "auto_changes_allowed": False}
        assert c.post("/v1/packages", json=body, headers=h("writer", "k1")).status_code == 201
        denied = c.patch(
            "/v1/packages/locked.pkg",
            content=b'{"auto_changes_allowed": true}',
            headers={**patch_ct, **h("writer")},
        )
        assert denied.status_code == 403 and denied.json()["code"] == "forbidden"
        # locking needs only write
        assert (
            c.patch(
                "/v1/packages/locked.pkg",
                content=b'{"auto_changes_allowed": false}',
                headers={**patch_ct, **h("writer")},
            ).status_code
            == 200
        )
        ok = c.patch(
            "/v1/packages/locked.pkg",
            content=b'{"auto_changes_allowed": true}',
            headers={**patch_ct, **h("admin")},
        )
        assert ok.status_code == 200 and ok.json()["auto_changes_allowed"] is True

        human_manifest = publish_body(extractor_manifest("locked.pkg"), extractor_files())
        mismatch = c.post(
            "/v1/packages/locked.pkg/versions", json=human_manifest, headers=h("assistant", "k2")
        )
        assert mismatch.status_code == 403
        llm = publish_body(
            extractor_manifest("locked.pkg", provenance={"created_by": "llm"}), extractor_files()
        )
        assert (
            c.post("/v1/packages/locked.pkg/versions", json=llm, headers=h("assistant", "k3")).status_code
            == 201
        )

        fork = {"new_package_id": "locked.fork", "from_version": "1.0.0", "auto_changes_allowed": True}
        assert (
            c.post("/v1/packages/locked.pkg/forks", json=fork, headers=h("assistant", "k4")).status_code
            == 201
        )
        parent2 = publish_body(
            extractor_manifest("locked.pkg", "1.1.0", provenance={"created_by": "llm"}, description="v2"),
            extractor_files(),
        )
        assert (
            c.post("/v1/packages/locked.pkg/versions", json=parent2, headers=h("assistant", "k5")).status_code
            == 201
        )
        port = c.post(
            "/v1/packages/locked.fork/upstream-ports",
            json={"parent_version": "1.1.0", "new_version": "1.1.0"},
            headers=h("assistant", "k6"),
        )
        assert port.status_code == 202
        job_id = port.json()["job_id"]
        assert c.post(f"/v1/jobs/{job_id}/cancel", headers=h("reader")).status_code == 403
        for _ in range(200):
            job = c.get(f"/v1/jobs/{job_id}", headers=h("reader")).json()
            if job["status"] in {"succeeded", "failed"}:
                break
            time.sleep(0.02)
        assert job["status"] == "succeeded", job
        prov = job["result"]["manifest"]["provenance"]
        assert prov["created_by"] == "llm" and prov["upstream_port"]["requested_by"] == "assistant"
        assert c.post(f"/v1/jobs/{job_id}/cancel", headers=h("writer")).status_code == 200  # terminal


async def test_port_checks_cancellation_before_publishing(tmp_path: Path, profile_file: Path) -> None:
    """A cancellation seen before publishing (e.g. requested on another instance) publishes nothing."""
    from jane_kit.jobs import JobCancelledError
    from jane_registry.auth import Principal

    settings = Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path / "b",
        runtime_profiles=[str(profile_file)],
    )
    app = build_app(settings)
    with TestClient(app) as c:
        c.post(
            "/v1/packages",
            json={"package_id": "p.cancel", "kind": "extractor", "title": "P"},
            headers={"Idempotency-Key": "c"},
        )
        c.post(
            "/v1/packages/p.cancel/versions",
            json=publish_body(extractor_manifest("p.cancel"), extractor_files()),
            headers={"Idempotency-Key": "v"},
        )
        c.post(
            "/v1/packages/p.cancel/forks",
            json={"new_package_id": "p.cancel-f", "from_version": "1.0.0"},
            headers={"Idempotency-Key": "f"},
        )
        service = app.state.service
        who = Principal("tester", frozenset({"registry:write"}))
        plan = await service.plan_port("p.cancel-f", {"parent_version": "1.0.0", "new_version": "1.0.1"}, who)

        async def cancelled() -> None:
            raise JobCancelledError("job")

        with pytest.raises(JobCancelledError):
            await service.port(plan, who, before_publish=cancelled)
        assert [v["version"] for v in c.get("/v1/packages/p.cancel-f/versions").json()["items"]] == ["1.0.0"]


@pytest.mark.integration
def test_recovery_after_instance_crash(
    real_backend: Any, profile_file: Path, uid: Any, monkeypatch: Any
) -> None:
    """Review 1: an instance dies holding an Idempotency-Key and a running job. Another instance frees the
    key after its lease and reports the job as failed (retryable) instead of running forever."""
    import asyncio

    from jane_kit.idempotency import fingerprint
    from jane_kit.jobs import Job, JobStatus

    monkeypatch.setenv("JANE_REGISTRY_LIMITS__RECOVERY__IN_PROGRESS_LEASE_MS", "1000")
    monkeypatch.setenv("JANE_REGISTRY_LIMITS__RECOVERY__JOB_LEASE_MS", "1000")
    monkeypatch.setenv("JANE_REGISTRY_LIMITS__RECOVERY__JOB_HEARTBEAT_MS", "200")
    schema = f"t_{uid('crash').split('-')[1]}"
    common = {"runtime_profiles": [str(profile_file)]}
    pid = uid("crash")
    raw = json.dumps(publish_body(extractor_manifest(pid), extractor_files())).encode()
    ct = {"Content-Type": "application/json"}
    key = f"pub-{pid}"
    path = f"/v1/packages/{pid}/versions"

    app_a = build_app(real_backend.settings(schema, instance_id="instance-a", **common))
    with TestClient(app_a) as a:
        assert (
            a.post(
                "/v1/packages",
                json={"package_id": pid, "kind": "extractor", "title": "C"},
                headers={"Idempotency-Key": f"c-{pid}"},
            ).status_code
            == 201
        )
        comp = app_a.state.components
        portal = a.portal
        assert portal is not None
        # "crash" in the middle of a request and of a job: claimed, never completed
        claimed = portal.call(comp.idempotency.begin, key, fingerprint("POST", path, raw), 86400.0)
        assert claimed is None
        running = Job(job_id=f"job_{pid}", kind="upstream_port", status=JobStatus.RUNNING)
        portal.call(comp.jobs.create, running)
        portal.call(comp.jobs.save, running)
        blocked = a.post(path, content=raw, headers={**ct, "Idempotency-Key": key})
        assert blocked.status_code == 409 and blocked.json()["code"] == "idempotency_in_progress"
        assert a.get(f"/v1/jobs/{running.job_id}").json()["status"] == "running"  # heartbeat keeps it alive
    # instance A is gone; its leases are no longer renewed
    asyncio.run(asyncio.sleep(1.5))
    with TestClient(build_app(real_backend.settings(schema, instance_id="instance-b", **common))) as b:
        retry = b.post(path, content=raw, headers={**ct, "Idempotency-Key": key})
        assert retry.status_code == 201, retry.text
        job = b.get(f"/v1/jobs/{running.job_id}").json()
        assert job["status"] == "failed"
        assert job["error"]["code"] == "service_unavailable" and job["error"]["retryable"] is True
