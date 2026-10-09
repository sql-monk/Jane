"""R20: the Web Collector takes its limits through jane-kit's layers with the same error checks as every
other service (``deploy/profiles/<profile>.json`` as ``JANE_WEB_COLLECTOR_LIMITS_FILE``).

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
from fastapi.testclient import TestClient

from jane_kit.config import LimitError, LimitLayer
from jane_web_collector.app import build_app
from jane_web_collector.settings import ServiceLimits, resolve_service_limits, to_contract
from jane_web_collector.testing import REPO_ROOT, make_settings

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
    assert resolved.limits.crawl.max_depth == want["crawl"]["max_depth"]
    assert resolved.limits.jobs.job_retention_seconds == want["transfer"]["job_retention_seconds"]
    applied, wanted = leaves(resolved.platform_limits()["defaults"]), leaves(want)
    assert {p: applied[p] for p in applied} == {p: wanted[p] for p in applied}
    # what the collector does not model is listed (start-up log of jane-kit), not dropped silently
    assert set(resolved.ignored) == set(wanted) - set(applied)
    assert {"sandbox.memory_mb", "llm.budget.amount", "telegram.max_messages_per_run"} <= set(
        resolved.ignored
    )


def test_profile_typo_fails_the_start(tmp_path: Path) -> None:
    bad = tmp_path / "typo.json"
    bad.write_text(json.dumps({"profile": "typo", "defaults": {"crawl": {"max_dept": 3}}}), encoding="utf-8")
    settings = make_settings(tmp_path, limits_file=bad)
    with pytest.raises(LimitError, match=r"crawl\.max_dept"):
        resolve_service_limits(settings)
    with pytest.raises(LimitError):
        build_app(settings)


def test_environment_layer_takes_model_paths_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__JOBS__JOB_RETENTION_SECONDS", "600")
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__COLLECTOR__MAX_WAIT_MS", "1000")
    resolved = resolve_service_limits(make_settings(tmp_path))
    assert resolved.limits.jobs.job_retention_seconds == 600
    assert resolved.limits.collector.max_wait_ms == 1000
    monkeypatch.setenv("JANE_WEB_COLLECTOR_LIMITS__CRAWL__MAX_DEPHT", "3")
    with pytest.raises(LimitError, match=r"crawl\.max_depht"):
        resolve_service_limits(make_settings(tmp_path))


def test_source_and_request_layers_are_contract_documents(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    resolved = resolve_service_limits(
        settings,
        LimitLayer("source", {"crawl": {"max_depth": 2}, "sandbox": {"memory_mb": 64}}, name="rules"),
        LimitLayer("request", {"transfer": {"job_retention_seconds": 120}}, name="request"),
    )
    assert resolved.limits.crawl.max_depth == 2
    assert resolved.limits.jobs.job_retention_seconds == 120  # contract path -> the field that declares it
    assert "sandbox.memory_mb" in resolved.ignored
    with pytest.raises(LimitError, match="unknown limit"):
        resolve_service_limits(settings, LimitLayer("request", {"retries": {"max_attempt": 1}}))
    # the contract document of the limits keeps its shape
    assert set(to_contract(ServiceLimits())) == {
        "concurrency",
        "rate",
        "crawl",
        "timeouts",
        "retries",
        "queue",
        "transfer",
    }
    assert to_contract(ServiceLimits())["transfer"]["job_retention_seconds"] == 86_400


def test_rules_limits_typo_is_rejected_before_a_job(tmp_path: Path) -> None:
    """A strategy-level typo cannot reach the resolver as a silently ignored path: the rules schema rejects it."""
    with TestClient(build_app(make_settings(tmp_path))) as client:
        rules = {
            "collector": "web",
            "scope": {"allowed_domains": ["example.test"]},
            "strategies": [{"type": "seed_list", "urls": ["https://example.test/"]}],
            "limits": {"crawl": {"max_dept": 3}},
        }
        r = client.post(
            "/v1/collections", json={"source_kind": "web", "rules": rules}, headers={"Idempotency-Key": "t1"}
        )
    assert r.status_code == 422 and r.json()["code"] == "validation_failed"
