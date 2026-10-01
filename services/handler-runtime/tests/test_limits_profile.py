"""A whole platform profile (``deploy/profiles/<profile>.json``) as ``JANE_HANDLER_RUNTIME_LIMITS_FILE`` (WP-01b)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_handler_runtime.app import build_app
from jane_handler_runtime.settings import DEFAULT_HARD_CAPS, Settings, request_layer, resolve_service_limits

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
def settings(profile: tuple[Path, dict[str, Any]], subprocess_settings: Settings) -> Settings:
    return subprocess_settings.model_copy(update={"limits_file": profile[0]})


def test_whole_profile_is_accepted_and_its_runtime_limits_apply(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    resolved = resolve_service_limits(settings)
    lim, want, caps = resolved.limits, doc["defaults"], doc["hard_caps"]
    assert resolved.profile == doc["profile"]
    assert lim.sandbox.model_dump() == want["sandbox"]
    assert lim.timeouts.invocation_timeout_ms == want["timeouts"]["invocation_timeout_ms"]
    assert lim.timeouts.sync_response_max_ms == want["timeouts"]["sync_response_max_ms"]
    assert lim.concurrency.max_parallel_invocations == want["concurrency"]["max_parallel_invocations"]
    assert lim.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"] != 86_400
    platform = resolved.platform_limits()
    applied, wanted = leaves(platform["defaults"]), leaves(want)
    assert {p: applied[p] for p in applied} == {p: wanted[p] for p in applied}
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert {"crawl.max_depth", "llm.budget.amount", "rate.burst_per_host"} <= set(resolved.ignored)
    # profile hard caps of runtime limits replace the service's own ceilings; the other ceilings stay
    profile_caps, effective_caps = leaves(caps), leaves(platform["hard_caps"])
    assert set(resolved.ignored_hard_caps) == set(profile_caps) - set(applied)
    capped = set(profile_caps) & set(applied)
    assert capped and {p: effective_caps[p] for p in capped} == {p: profile_caps[p] for p in capped}
    invocation_cap = DEFAULT_HARD_CAPS["timeouts"]["invocation_timeout_ms"]
    assert effective_caps["timeouts.invocation_timeout_ms"] == invocation_cap


def test_profile_hard_caps_bound_the_request(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    asked = {"sandbox": {"memory_mb": 64 * 1024, "wall_time_ms": 10**7}}
    lim = resolve_service_limits(settings, request_layer(asked)).limits
    assert lim.sandbox.memory_mb == doc["hard_caps"]["sandbox"]["memory_mb"]
    assert lim.sandbox.wall_time_ms == doc["hard_caps"]["sandbox"]["wall_time_ms"]


def test_service_starts_with_the_profile(profile: tuple[Path, dict[str, Any]], settings: Settings) -> None:
    _, doc = profile
    with TestClient(build_app(settings)) as client:
        info = client.get("/v1/info").json()["limits"]
    assert info["profile"] == doc["profile"]
    assert info["defaults"]["sandbox"] == doc["defaults"]["sandbox"]
    assert info["hard_caps"]["sandbox"]["memory_mb"] == doc["hard_caps"]["sandbox"]["memory_mb"]
    assert "crawl" not in info["defaults"]
