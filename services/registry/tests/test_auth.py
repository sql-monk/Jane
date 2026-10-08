"""ADR-0005 in the registry on jane-kit: scope table of every route, actors, the token for runtime profiles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from jane_kit.auth import AuthConfigError, sha256_hex
from jane_registry.app import build_app
from jane_registry.profiles import ProfileSource
from jane_registry.settings import ProfileLimits, Settings
from jane_registry.testing import TEST_PROFILE


def settings(tmp_path: Path, profile_file: Path, keys: list[dict[str, Any]], **kw: Any) -> Settings:
    return Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path / "b",
        auth_mode="api_key",
        api_keys=keys,
        runtime_profiles=[str(profile_file)],
        **kw,
    )


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_jobs_and_unknown_actor(tmp_path: Path, profile_file: Path) -> None:
    keys = [
        {"name": "reader", "sha256": sha256_hex("k-reg-reader"), "scopes": ["registry:read"]},
        {"name": "runtime", "sha256": sha256_hex("k-reg-runtime"), "scopes": []},
    ]
    with TestClient(build_app(settings(tmp_path, profile_file, keys))) as c:
        assert c.get("/v1/jobs/job_x").status_code == 401
        assert c.get("/v1/jobs/job_x", headers=auth("k-reg-runtime")).status_code == 403
        assert c.get("/v1/jobs/job_x", headers=auth("k-reg-reader")).status_code == 404
        assert c.post("/v1/jobs/job_x/cancel", headers=auth("k-reg-reader")).status_code == 403
        archive = "/v1/packages/a.b/versions/1.0.0/archive"
        assert c.get(archive, headers=auth("k-reg-runtime")).status_code == 403
        assert c.get(archive, headers=auth("k-reg-reader")).status_code == 404
    bad = [{"name": "x", "sha256": sha256_hex("k"), "scopes": [], "actor": "robot"}]
    with pytest.raises(ValueError, match="actor"):
        build_app(settings(tmp_path, profile_file, bad))


def test_unresolvable_runtime_profiles_token_refuses_to_start(tmp_path: Path, profile_file: Path) -> None:
    keys = [{"name": "reader", "sha256": sha256_hex("k-reg-reader"), "scopes": ["registry:read"]}]
    s = settings(
        tmp_path, profile_file, keys, runtime_profiles_token_ref="env:JANE_TEST_UNSET_REGISTRY_TOKEN"
    )
    with pytest.raises(AuthConfigError, match="JANE_TEST_UNSET_REGISTRY_TOKEN"):
        build_app(s)


async def test_runtime_profiles_are_read_with_the_registry_token() -> None:
    seen: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization"))
        return httpx.Response(
            200, json={"capabilities": {"runtime_profiles": {"python-extractor@1": TEST_PROFILE}}}
        )

    source = ProfileSource(
        ["http://runtime.test/v1/info"],
        ProfileLimits(),
        transport=httpx.MockTransport(handler),
        token="k-reg",
    )
    assert set(await source.profiles()) == {"python-extractor@1"}
    assert seen == ["Bearer k-reg"]
