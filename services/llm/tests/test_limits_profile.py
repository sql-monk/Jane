"""A whole platform profile (``deploy/profiles/<profile>.json``) as ``JANE_LLM_LIMITS_FILE`` (WP-01b)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.config import LimitLayer
from jane_llm.app import build_app
from jane_llm.settings import Settings, resolve_service_limits
from jane_llm.store import MemoryStore

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
def settings(profile: tuple[Path, dict[str, Any]]) -> Settings:
    return Settings(log_format="console", store="memory", limits_file=profile[0])


def test_whole_profile_is_accepted_and_its_llm_limits_apply(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    resolved = resolve_service_limits(settings)
    lim, want = resolved.limits, doc["defaults"]
    assert resolved.profile == doc["profile"]
    assert lim.llm.max_requests_per_minute == want["llm"]["max_requests_per_minute"] != 60  # not the default
    assert lim.llm.max_input_tokens_per_request == want["llm"]["max_input_tokens_per_request"]
    assert lim.llm.max_output_tokens_per_request == want["llm"]["max_output_tokens_per_request"]
    assert lim.llm.budget.model_dump() == want["llm"]["budget"]
    # provider calls: connection and retries are the contract's timeouts.connect_timeout_ms / retries (the profile
    # sets them); one model call has the gateway's own timeout, not the profile's web-sized one (R12, WP-15)
    assert lim.provider.connect_timeout_ms == want["timeouts"]["connect_timeout_ms"]
    assert lim.provider.request_timeout_ms == 120_000 != want["timeouts"]["request_timeout_ms"]
    assert lim.provider.retries.model_dump() == want["retries"]
    assert "timeouts.request_timeout_ms" in resolved.ignored
    assert lim.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"] != 86_400
    assert lim.gateway.default_max_output_tokens == 1_024  # service-only limits keep their defaults
    applied, wanted = leaves(resolved.platform_limits()["defaults"]), leaves(want)
    assert {p: applied[p] for p in applied} == {p: wanted[p] for p in applied}
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert {"llm.max_onboarding_samples", "sandbox.memory_mb", "crawl.max_depth"} <= set(resolved.ignored)


def test_provider_call_timeout_is_set_only_by_the_service(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``provider.request_timeout_ms`` is internal: a profile cannot shorten it, the service's variable can."""
    monkeypatch.setenv("JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS", "300000")
    resolved = resolve_service_limits(settings)
    assert resolved.limits.provider.request_timeout_ms == 300_000
    assert "request_timeout_ms" not in resolved.platform_limits()["defaults"].get("timeouts", {})


def test_profile_hard_caps_bound_the_request(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    asked = LimitLayer("request", {"llm": {"max_output_tokens_per_request": 100_000}})
    lim = resolve_service_limits(settings, asked).limits
    cap = doc["hard_caps"].get("llm", {}).get("max_output_tokens_per_request", 100_000)
    assert lim.llm.max_output_tokens_per_request == cap


def test_service_starts_with_the_profile(profile: tuple[Path, dict[str, Any]], settings: Settings) -> None:
    _, doc = profile
    with TestClient(build_app(settings, store=MemoryStore())) as client:
        assert client.get("/v1/health").status_code == 200
        info = client.get("/v1/info").json()["limits"]
    assert info["profile"] == doc["profile"]
    assert info["defaults"]["llm"]["budget"] == doc["defaults"]["llm"]["budget"]
    assert "sandbox" not in info["defaults"]
