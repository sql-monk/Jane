from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import Field

from jane_kit.clients import ClientLimits
from jane_kit.config import (
    JaneSettings,
    LimitError,
    LimitLayer,
    Limits,
    contract_field,
    layer_from_env,
    load_layer,
    resolve_limits,
)
from jane_kit.jobs import JobLimits


class SvcLimits(Limits):
    client: ClientLimits = ClientLimits()
    crawl_depth: int = contract_field("crawl.max_depth", 3, ge=0)
    internal_only: int = 7


def test_platform_limits_maps_contract_fields(tmp_path: Path) -> None:
    f = tmp_path / "p.json"
    f.write_text(
        '{"profile": "ci", "defaults": {"crawl_depth": 2}, "hard_caps": {"crawl_depth": 4}}', encoding="utf-8"
    )
    doc = resolve_limits(SvcLimits, load_layer(f)).platform_limits()
    assert doc["profile"] == "ci"
    assert doc["hard_caps"] == {"crawl": {"max_depth": 4}}
    assert doc["defaults"]["crawl"] == {"max_depth": 2}
    assert doc["defaults"]["timeouts"] == {"connect_timeout_ms": 5000, "request_timeout_ms": 30000}
    assert doc["defaults"]["retries"]["max_attempts"] == 4
    assert "internal_only" not in str(doc) and "job_poll_interval_ms" not in str(doc)


class CrawlGroup(Limits):
    max_depth: int = Field(default=3, ge=0)
    max_redirects: int = Field(default=5, ge=0)


class TimeoutsGroup(Limits):
    request_timeout_ms: int = Field(default=10_000, ge=1)


class ConcurrencyGroup(Limits):
    max_parallel_fetches: int = Field(default=4, ge=1)


class CollectorLimits(Limits):
    concurrency: ConcurrencyGroup = ConcurrencyGroup()
    crawl: CrawlGroup = CrawlGroup()
    timeouts: TimeoutsGroup = TimeoutsGroup()


def test_defaults_when_no_layers() -> None:
    r = resolve_limits(CollectorLimits)
    assert r.limits.concurrency.max_parallel_fetches == 4
    assert all(origin == "default" for _, _, origin in r.explain())
    assert set(r.provenance().values()) == {"platform"}  # service defaults are platform defaults


def test_platform_source_task_stage_inheritance() -> None:
    r = resolve_limits(
        CollectorLimits,
        LimitLayer(
            "platform",
            {"concurrency": {"max_parallel_fetches": 8}, "timeouts": {"request_timeout_ms": 20_000}},
        ),
        LimitLayer("source", {"crawl": {"max_depth": 10}}, name="shop"),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 2}}, name="prices"),
        LimitLayer("stage", {"timeouts": {"request_timeout_ms": 5_000}}, name="fetch"),
    )
    lim = r.limits
    assert (lim.concurrency.max_parallel_fetches, lim.crawl.max_depth, lim.crawl.max_redirects) == (2, 10, 5)
    assert lim.timeouts.request_timeout_ms == 5_000
    assert r.origin == {
        "concurrency.max_parallel_fetches": "task:prices",
        "timeouts.request_timeout_ms": "stage:fetch",
        "crawl.max_depth": "source:shop",
    }
    assert r.provenance() == {
        "concurrency.max_parallel_fetches": "task",
        "crawl.max_depth": "source",
        "crawl.max_redirects": "platform",
        "timeouts.request_timeout_ms": "stage",
    }


def test_hard_caps_clamp_more_specific_layers() -> None:
    r = resolve_limits(
        CollectorLimits,
        LimitLayer("platform", hard_caps={"concurrency": {"max_parallel_fetches": 6}}),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 50}}),
    )
    assert r.limits.concurrency.max_parallel_fetches == 6
    assert r.provenance()["concurrency.max_parallel_fetches"] == "hard_cap"
    eff = r.effective()
    assert eff["limits"]["concurrency"]["max_parallel_fetches"] == 6
    assert eff["provenance"]["concurrency.max_parallel_fetches"] == "hard_cap"


def test_hard_cap_error_mode_for_requests() -> None:
    with pytest.raises(LimitError, match="exceeds hard cap"):
        resolve_limits(
            CollectorLimits,
            LimitLayer("platform", hard_caps={"crawl": {"max_depth": 5}}),
            LimitLayer("request", {"crawl": {"max_depth": 50}}),
            on_exceed="error",
        )


def test_lower_layer_cannot_loosen_hard_cap() -> None:
    with pytest.raises(LimitError, match="loosens"):
        resolve_limits(
            CollectorLimits,
            LimitLayer("platform", hard_caps={"crawl": {"max_depth": 5}}),
            LimitLayer("source", hard_caps={"crawl": {"max_depth": 60}}),
        )


def test_unknown_null_and_invalid_values_rejected() -> None:
    with pytest.raises(LimitError, match="unknown limit"):
        resolve_limits(CollectorLimits, LimitLayer("task", {"crawl": {"max_dept": 1}}))
    with pytest.raises(LimitError, match="null is not a limit value"):
        resolve_limits(CollectorLimits, LimitLayer("task", {"crawl": {"max_depth": None}}))
    with pytest.raises(LimitError, match="invalid limits"):
        resolve_limits(CollectorLimits, LimitLayer("task", {"concurrency": {"max_parallel_fetches": 0}}))


def test_limits_subclass_requires_defaults() -> None:
    with pytest.raises(TypeError, match="safe default"):

        class Bad(Limits):
            concurrency: int


def test_env_layer_coerces_strings() -> None:
    env = {
        "X_LIMITS__CONCURRENCY__MAX_PARALLEL_FETCHES": "7",
        "X_LIMITS__HARD_CAPS__CRAWL__MAX_DEPTH": "2",
        "OTHER": "1",
    }
    r = resolve_limits(CollectorLimits, layer_from_env("X_LIMITS__", environ=env))
    assert r.limits.concurrency.max_parallel_fetches == 7
    assert r.limits.crawl.max_depth == 2
    assert r.origin["concurrency.max_parallel_fetches"] == "platform:env"
    assert r.clamped == {"crawl.max_depth": "platform:env"}


PLATFORM = {
    "toml": 'profile = "dev-laptop"\n[defaults.crawl]\nmax_depth = 4\n[hard_caps.concurrency]\nmax_parallel_fetches = 3\n',
    "json": '{"profile": "dev-laptop", "defaults": {"crawl": {"max_depth": 4}}, "hard_caps": {"concurrency": {"max_parallel_fetches": 3}}}',
    "yaml": "profile: dev-laptop\ndefaults:\n  crawl:\n    max_depth: 4\nhard_caps:\n  concurrency:\n    max_parallel_fetches: 3\n",
}


@pytest.mark.parametrize("fmt", sorted(PLATFORM))
def test_platform_limits_file_formats(tmp_path: Path, fmt: str) -> None:
    f = tmp_path / f"platform.{fmt}"
    f.write_text(PLATFORM[fmt], encoding="utf-8")
    layer = load_layer(f)
    assert layer.name == "dev-laptop"
    r = resolve_limits(CollectorLimits, layer)
    assert (r.limits.crawl.max_depth, r.limits.concurrency.max_parallel_fetches) == (4, 3)


def test_source_layer_file_is_plain_limits(tmp_path: Path) -> None:
    f = tmp_path / "source.json"
    f.write_text('{"crawl": {"max_depth": 9}}', encoding="utf-8")
    r = resolve_limits(CollectorLimits, load_layer(f, "source", name="shop"))
    assert r.provenance()["crawl.max_depth"] == "source"


def test_platform_file_rejects_unknown_sections(tmp_path: Path) -> None:
    f = tmp_path / "bad.toml"
    f.write_text("[limits]\nx = 3\n", encoding="utf-8")
    with pytest.raises(LimitError, match="unexpected top-level"):
        load_layer(f)


def test_settings_platform_layers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "p.toml"
    f.write_text(
        "[defaults.crawl]\nmax_depth = 9\n[defaults.concurrency]\nmax_parallel_fetches = 3\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SVC_LIMITS__CONCURRENCY__MAX_PARALLEL_FETCHES", "5")
    r = resolve_limits(CollectorLimits, *JaneSettings(limits_file=f).platform_layers("SVC_LIMITS__"))
    assert (r.limits.concurrency.max_parallel_fetches, r.limits.crawl.max_depth) == (5, 9)
    assert r.origin["concurrency.max_parallel_fetches"] == "platform:env"


# ---------------------------------------------------------------- shared platform profile (WP-01b)


class SharedSvcLimits(Limits):
    """A service that has only some limits of the contract, some of them under its own paths."""

    crawl: CrawlGroup = CrawlGroup()  # undeclared, at the contract paths crawl.max_depth / max_redirects
    client: ClientLimits = ClientLimits()  # contract timeouts.connect/request_timeout_ms and retries.*
    jobs: JobLimits = JobLimits()  # contract transfer.job_retention_seconds
    internal_only: int = 7


SHARED_PROFILE: dict[str, Any] = {
    "profile": "shared-test",
    "defaults": {
        "crawl": {"max_depth": 4, "max_pages_per_run": 100},
        "timeouts": {"request_timeout_ms": 15_000, "invocation_timeout_ms": 60_000},
        "retries": {"max_attempts": 2, "jitter": False},
        "transfer": {"job_retention_seconds": 604_800, "inline_max_bytes": 1024},
        "sandbox": {"memory_mb": 512, "cpu_cores": 0.5},
        "llm": {"budget": {"amount": 5, "currency": "USD", "period": "day"}},
        "jobs": {"max_concurrent_jobs": 3},  # a model path (not in the contract) is still accepted
    },
    "hard_caps": {
        "crawl": {"max_depth": 3},
        "timeouts": {"request_timeout_ms": 20_000},
        "sandbox": {"memory_mb": 1024},
    },
}


def write_profile(tmp_path: Path, doc: dict[str, Any], name: str = "profile.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def test_shared_profile_applies_declared_limits_and_ignores_other_contract_limits(tmp_path: Path) -> None:
    layer = load_layer(write_profile(tmp_path, SHARED_PROFILE))
    assert layer.shared
    r = resolve_limits(SharedSvcLimits, layer)
    lim, label = r.limits, "platform:shared-test"
    assert lim.client.request_timeout_ms == 15_000  # contract timeouts.request_timeout_ms
    assert (lim.client.retries.max_attempts, lim.client.retries.jitter) == (2, False)
    assert lim.jobs.job_retention_seconds == 604_800  # contract transfer.job_retention_seconds
    assert lim.jobs.max_concurrent_jobs == 3
    assert lim.client.connect_timeout_ms == 5_000 and lim.internal_only == 7  # not in the profile: defaults
    assert r.origin["client.request_timeout_ms"] == label
    assert r.origin["jobs.job_retention_seconds"] == label
    assert r.ignored == dict.fromkeys(
        [
            "crawl.max_pages_per_run",
            "timeouts.invocation_timeout_ms",
            "transfer.inline_max_bytes",
            "sandbox.memory_mb",
            "sandbox.cpu_cores",
            "llm.budget.amount",
            "llm.budget.currency",
            "llm.budget.period",
        ],
        label,
    )
    assert r.ignored_hard_caps == {"sandbox.memory_mb": label}
    # hard caps of modelled limits apply: crawl.max_depth 4 -> 3
    assert lim.crawl.max_depth == 3
    assert r.clamped == {"crawl.max_depth": label}
    assert r.provenance()["crawl.max_depth"] == "hard_cap"
    assert r.hard_caps == {"crawl.max_depth": 3, "client.request_timeout_ms": 20_000}
    doc = r.platform_limits()  # /v1/info: the profile's values at contract paths
    assert doc["profile"] == "shared-test"
    assert doc["defaults"]["timeouts"]["request_timeout_ms"] == 15_000
    assert doc["defaults"]["transfer"] == {"job_retention_seconds": 604_800}
    assert doc["hard_caps"] == {"timeouts": {"request_timeout_ms": 20_000}}


def test_shared_profile_hard_cap_bounds_more_specific_layers(tmp_path: Path) -> None:
    layer = load_layer(write_profile(tmp_path, SHARED_PROFILE))
    r = resolve_limits(SharedSvcLimits, layer, LimitLayer("task", {"client": {"request_timeout_ms": 90_000}}))
    assert r.limits.client.request_timeout_ms == 20_000
    with pytest.raises(LimitError, match="exceeds hard cap"):
        resolve_limits(
            SharedSvcLimits,
            layer,
            LimitLayer("request", {"client": {"request_timeout_ms": 90_000}}),
            on_exceed="error",
        )


@pytest.mark.parametrize(
    ("doc", "match"),
    [
        ({"defaults": {"crawl": {"max_dept": 1}}}, r"unknown limit\(s\) \['crawl.max_dept'\].*schema"),
        ({"defaults": {"crawls": {"max_depth": 1}}}, r"unknown limit\(s\) \['crawls.max_depth'\]"),
        ({"defaults": {"sandbox": {"memory_mb": 512, "memroy_mb": 1}}}, r"\['sandbox.memroy_mb'\]"),
        ({"defaults": {"sandbox": 512}}, r"unknown limit\(s\) \['sandbox'\]"),
        ({"defaults": {"internal_onl": 1}}, r"unknown limit\(s\) \['internal_onl'\]"),
        (
            {"defaults": {}, "hard_caps": {"timeouts": {"request_timeout": 1}}},
            r"\['timeouts.request_timeout'\]",
        ),
    ],
)
def test_shared_profile_still_rejects_typos(tmp_path: Path, doc: dict[str, Any], match: str) -> None:
    with pytest.raises(LimitError, match=match):
        resolve_limits(SharedSvcLimits, load_layer(write_profile(tmp_path, doc)))


@pytest.mark.parametrize(
    ("doc", "match"),
    [
        ({"defaults": {"crawl": {"max_depth": -1}}}, "invalid limits"),
        ({"defaults": {"timeouts": {"request_timeout_ms": "soon"}}}, "invalid limits"),
        ({"defaults": {"retries": {"max_attempts": 0}}}, "invalid limits"),
        ({"defaults": {}, "hard_caps": {"crawl": {"max_depth": "deep"}}}, "invalid hard_caps"),
        ({"defaults": {"timeouts": {"request_timeout_ms": None}}}, "null is not a limit value"),
        ({"defaults": {"sandbox": {"memory_mb": None}}}, "null is not a limit value"),  # even if ignored
        (
            {
                "defaults": {
                    "transfer": {"job_retention_seconds": 100},
                    "jobs": {"job_retention_seconds": 200},
                }
            },
            "jobs.job_retention_seconds is set twice",
        ),
    ],
)
def test_shared_profile_rejects_invalid_values_of_modelled_limits(
    tmp_path: Path, doc: dict[str, Any], match: str
) -> None:
    with pytest.raises(LimitError, match=match):
        resolve_limits(SharedSvcLimits, load_layer(write_profile(tmp_path, doc)))


def test_same_value_under_contract_and_model_path_is_not_a_conflict(tmp_path: Path) -> None:
    doc = {"defaults": {"transfer": {"job_retention_seconds": 100}, "jobs": {"job_retention_seconds": 100}}}
    r = resolve_limits(SharedSvcLimits, load_layer(write_profile(tmp_path, doc)))
    assert r.limits.jobs.job_retention_seconds == 100


def test_only_platform_files_are_shared(tmp_path: Path) -> None:
    """Env, source/task and request layers keep rejecting limits the service does not have
    (a request asking for them still gets limit_exceeded/422)."""
    for layer in (
        LimitLayer("request", {"sandbox": {"memory_mb": 512}}),
        LimitLayer("task", {"timeouts": {"request_timeout_ms": 1_000}}),  # contract path, model has client.*
        layer_from_env("X_LIMITS__", environ={"X_LIMITS__SANDBOX__MEMORY_MB": "512"}),
        load_layer(write_profile(tmp_path, {"sandbox": {"memory_mb": 512}}, "source.json"), "source"),
    ):
        assert not layer.shared
        with pytest.raises(LimitError, match="unknown limit"):
            resolve_limits(SharedSvcLimits, layer)


def test_settings_platform_layers_take_a_whole_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = write_profile(tmp_path, SHARED_PROFILE)
    monkeypatch.setenv("SVC_LIMITS__CLIENT__REQUEST_TIMEOUT_MS", "12000")
    r = resolve_limits(SharedSvcLimits, *JaneSettings(limits_file=f).platform_layers("SVC_LIMITS__"))
    assert r.limits.client.request_timeout_ms == 12_000  # env overrides the file
    assert r.limits.jobs.job_retention_seconds == 604_800
    assert "sandbox.memory_mb" in r.ignored
    assert r.profile == "shared-test"
