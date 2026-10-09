"""A whole platform profile (``deploy/profiles/<profile>.json``) as ``JANE_ASSISTANT_LIMITS_FILE`` (WP-01b)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_assistant.app import build_app
from jane_assistant.settings import Settings, request_layer, resolve_service_limits
from jane_kit.config import LimitError

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
    return Settings(log_format="console", limits_file=profile[0])


def test_whole_profile_is_accepted_and_its_assistant_limits_apply(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    resolved = resolve_service_limits(settings)
    lim, want = resolved.limits, doc["defaults"]
    assert resolved.profile == doc["profile"]
    llm = lim.llm.model_dump()
    # every llm.* limit of the profile, incl. the budget; a profile older than WP-15 lacks the confidence limit
    assert {k: llm[k] for k in want["llm"]} == want["llm"]
    assert llm["min_onboarding_confidence"] == want["llm"].get("min_onboarding_confidence", 0.8)
    assert lim.llm.max_input_tokens_per_request != 16_000  # not the default
    assert lim.transfer.inline_max_bytes == want["transfer"]["inline_max_bytes"]
    assert lim.clients.connect_timeout_ms == want["timeouts"]["connect_timeout_ms"]
    assert lim.clients.request_timeout_ms == want["timeouts"]["request_timeout_ms"]
    assert lim.clients.retries.model_dump() == want["retries"]
    assert lim.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"] != 86_400
    assert lim.onboarding.min_distinct_types == 2  # assistant-only limits keep their defaults
    applied, wanted = leaves(resolved.platform_limits()["defaults"]), leaves(want)
    assert set(applied) - set(wanted) <= {"llm.min_onboarding_confidence"}  # see above
    assert {p: applied[p] for p in applied if p in wanted} == {p: wanted[p] for p in applied if p in wanted}
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert {"sandbox.memory_mb", "crawl.max_depth", "timeouts.invocation_timeout_ms"} <= set(resolved.ignored)


def test_profile_hard_caps_bound_the_request(
    profile: tuple[Path, dict[str, Any]], settings: Settings
) -> None:
    _, doc = profile
    lim = resolve_service_limits(settings, *request_layer({"max_output_tokens_per_request": 100_000})).limits
    cap = doc["hard_caps"].get("llm", {}).get("max_output_tokens_per_request", 100_000)
    assert lim.llm.max_output_tokens_per_request == cap


def test_request_limits_stay_strict_with_the_profile(settings: Settings) -> None:
    """Only the platform file is lenient: an unknown request limit is still an error (-> 422)."""
    with pytest.raises(LimitError, match="unknown limit"):
        resolve_service_limits(settings, *request_layer({"max_onboarding_sample": 4}))


def test_service_starts_with_the_profile(profile: tuple[Path, dict[str, Any]], settings: Settings) -> None:
    _, doc = profile
    with TestClient(build_app(settings)) as client:
        assert client.get("/v1/health").status_code == 200
        info = client.get("/v1/info").json()["limits"]
    assert info["profile"] == doc["profile"]
    assert info["defaults"]["llm"] == {"min_onboarding_confidence": 0.8, **doc["defaults"]["llm"]}
    assert "sandbox" not in info["defaults"]
