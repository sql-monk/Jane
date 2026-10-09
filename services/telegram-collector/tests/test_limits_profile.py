"""R20: the Telegram Collector takes its limits through jane-kit's layers with the same error checks as every
other service (``deploy/profiles/<profile>.json`` as ``JANE_TELEGRAM_COLLECTOR_LIMITS_FILE``).

Before R20 the collector translated the platform layer itself (``translate_layer``) and silently dropped any
path it did not know, typos included; jane-kit rejects a typo and records the contract limits a service does
not have in ``ResolvedLimits.ignored``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from jane_kit.config import LimitError, LimitLayer
from jane_telegram_collector.app import build_app
from jane_telegram_collector.settings import ServiceLimits, resolve_service_limits, to_contract
from jane_telegram_collector.testing import REPO_ROOT, make_settings

PROFILES = REPO_ROOT / "deploy" / "profiles"


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


def test_whole_profile_applies_its_collector_limits_and_lists_the_rest(
    tmp_path: Path, profile: tuple[Path, dict[str, Any]]
) -> None:
    path, doc = profile
    resolved = resolve_service_limits(make_settings(tmp_path, limits_file=path))
    want = doc["defaults"]
    assert resolved.profile == doc["profile"]
    assert resolved.limits.telegram.max_messages_per_run == want["telegram"]["max_messages_per_run"]
    assert resolved.limits.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"]
    applied, wanted = leaves(resolved.platform_limits()["defaults"]), leaves(want)
    assert {p: applied[p] for p in applied} == {p: wanted[p] for p in applied}
    # what the collector does not model is listed (start-up log of jane-kit), not dropped silently
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert {"crawl.max_depth", "sandbox.memory_mb", "llm.budget.amount"} <= set(resolved.ignored)


def test_profile_typo_fails_the_start(tmp_path: Path) -> None:
    bad = tmp_path / "typo.json"
    bad.write_text(
        json.dumps({"profile": "typo", "defaults": {"telegram": {"max_messages_per_rnu": 3}}}),
        encoding="utf-8",
    )
    settings = make_settings(tmp_path, limits_file=bad)
    with pytest.raises(LimitError, match=r"telegram\.max_messages_per_rnu"):
        resolve_service_limits(settings)
    with pytest.raises(LimitError):
        build_app(settings)


def test_environment_layer_takes_model_paths_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_TELEGRAM_COLLECTOR_LIMITS__JOBS__JOB_RETENTION_SECONDS", "600")
    monkeypatch.setenv("JANE_TELEGRAM_COLLECTOR_LIMITS__COLLECTOR__HISTORY_PAGE_SIZE", "7")
    resolved = resolve_service_limits(make_settings(tmp_path))
    assert resolved.limits.jobs.job_retention_seconds == 600
    assert resolved.limits.collector.history_page_size == 7
    monkeypatch.setenv("JANE_TELEGRAM_COLLECTOR_LIMITS__TELEGRAM__MAX_FLOOD_WAIT", "3")
    with pytest.raises(LimitError, match=r"telegram\.max_flood_wait"):
        resolve_service_limits(make_settings(tmp_path))


def test_source_and_request_layers_are_contract_documents(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    resolved = resolve_service_limits(
        settings,
        LimitLayer(
            "source", {"telegram": {"max_messages_per_run": 9}, "crawl": {"max_depth": 2}}, name="rules"
        ),
        LimitLayer("request", {"transfer": {"job_retention_seconds": 120}}, name="request"),
    )
    assert resolved.limits.telegram.max_messages_per_run == 9
    assert resolved.limits.jobs.job_retention_seconds == 120  # contract path -> the field that declares it
    assert "crawl.max_depth" in resolved.ignored
    with pytest.raises(LimitError, match="unknown limit"):
        resolve_service_limits(settings, LimitLayer("request", {"retries": {"max_attempt": 1}}))
    assert set(to_contract(ServiceLimits())) == {
        "rate",
        "timeouts",
        "retries",
        "queue",
        "transfer",
        "telegram",
    }
    assert to_contract(ServiceLimits())["transfer"]["job_retention_seconds"] == 86_400
