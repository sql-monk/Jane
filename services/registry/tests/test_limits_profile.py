"""A whole platform profile (``deploy/profiles/<profile>.json``) as ``JANE_REGISTRY_LIMITS_FILE`` (WP-01b)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_registry.app import build_app
from jane_registry.settings import Settings, resolve_service_limits

PROFILES = Path(__file__).resolve().parents[3] / "deploy" / "profiles"


def leaves(doc: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in doc.items():
        if isinstance(value, Mapping):
            out.update(leaves(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


@pytest.fixture(params=["ci", "dev-laptop"])
def profile(request: pytest.FixtureRequest) -> tuple[Path, dict[str, Any]]:
    path = PROFILES / f"{request.param}.json"
    if not path.is_file():
        pytest.skip(f"{path} not in this checkout (WP-14)")
    return path, json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def settings(profile: tuple[Path, dict[str, Any]], tmp_path: Path, profile_file: Path) -> Settings:
    return Settings(
        log_format="console",
        db="memory",
        blob="filesystem",
        blob_root=tmp_path / "blobs",
        runtime_profiles=[str(profile_file)],
        limits_file=profile[0],
    )


def test_whole_profile_is_accepted_and_its_registry_limits_apply(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    resolved = resolve_service_limits(settings)
    lim, want = resolved.limits, doc["defaults"]
    assert resolved.profile == doc["profile"]
    body_limit = want["transfer"]["max_request_body_bytes"]
    assert lim.requests.max_request_body_bytes == body_limit != 30 * 1024 * 1024  # not the default
    assert lim.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"] != 86_400
    assert lim.idempotency.idempotency_ttl_seconds == want["transfer"]["idempotency_ttl_seconds"]
    assert lim.packages.max_files == 2000  # registry-only limits keep their defaults
    applied, wanted = leaves(resolved.platform_limits()["defaults"]), leaves(want)
    assert set(applied) == {
        "transfer.max_request_body_bytes",
        "transfer.job_retention_seconds",
        "transfer.idempotency_ttl_seconds",
    }
    assert {p: applied[p] for p in applied} == {p: wanted[p] for p in applied}
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert set(resolved.ignored_hard_caps) == set(leaves(doc["hard_caps"]))


def test_service_starts_with_the_profile_and_enforces_its_body_limit(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    body_limit = doc["defaults"]["transfer"]["max_request_body_bytes"]
    with TestClient(build_app(settings)) as client:
        info = client.get("/v1/info").json()["limits"]
        too_big = client.post(
            "/v1/packages",
            content=b"x" * (body_limit + 1),
            headers={"Content-Type": "application/json", "Idempotency-Key": "profile-body-limit"},
        )
    assert info["profile"] == doc["profile"]
    assert info["defaults"]["transfer"]["max_request_body_bytes"] == body_limit
    assert too_big.status_code == 413, too_big.text
