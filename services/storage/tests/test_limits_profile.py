"""A whole platform profile (``deploy/profiles/<profile>.json``) as ``JANE_STORAGE_LIMITS_FILE`` (WP-01b)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_storage.app import build_app
from jane_storage.settings import Settings, resolve_service_limits

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


def test_whole_profile_is_accepted_and_its_storage_limits_apply(profile: tuple[Path, dict[str, Any]]) -> None:
    path, doc = profile
    resolved = resolve_service_limits(Settings(log_format="console", limits_file=path))
    lim, want = resolved.limits, doc["defaults"]
    assert resolved.profile == doc["profile"]
    assert (
        lim.transfer.inline_max_bytes == want["transfer"]["inline_max_bytes"] != 1024 * 1024
    )  # not the default
    assert lim.transfer.max_request_body_bytes == want["transfer"]["max_request_body_bytes"]
    assert lim.timeouts.sync_response_max_ms == want["timeouts"]["sync_response_max_ms"] != 30_000
    assert lim.timeouts.request_timeout_ms == want["timeouts"]["request_timeout_ms"]
    assert lim.retries.model_dump() == want["retries"]
    assert lim.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"] != 86_400
    assert lim.idempotency.idempotency_ttl_seconds == want["transfer"]["idempotency_ttl_seconds"]
    # every contract limit storage has took the profile's value; the rest is ignored, not lost silently
    applied, wanted = leaves(resolved.platform_limits()["defaults"]), leaves(want)
    assert {p: applied[p] for p in applied} == {p: wanted[p] for p in applied}
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert {"sandbox.memory_mb", "crawl.max_depth", "llm.budget.amount"} <= set(resolved.ignored)
    assert set(resolved.ignored_hard_caps) == set(leaves(doc["hard_caps"]))  # storage has no capped limit


def test_service_starts_with_the_profile(profile: tuple[Path, dict[str, Any]]) -> None:
    path, doc = profile
    with TestClient(build_app(Settings(log_format="console", limits_file=path))) as client:
        assert client.get("/v1/health").status_code == 200
        info = client.get("/v1/info").json()["limits"]
    assert info["profile"] == doc["profile"]
    assert info["defaults"]["transfer"]["inline_max_bytes"] == doc["defaults"]["transfer"]["inline_max_bytes"]
    assert "sandbox" not in info["defaults"]


def test_profile_typo_still_fails_the_start(tmp_path: Path) -> None:
    from jane_kit.config import LimitError

    bad = tmp_path / "profile.json"
    bad.write_text(
        json.dumps({"profile": "x", "defaults": {"transfer": {"inline_max_byte": 1}}}), encoding="utf-8"
    )
    with pytest.raises(LimitError, match="inline_max_byte"):
        build_app(Settings(log_format="console", limits_file=bad))
