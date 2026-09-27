from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import Field

from jane_kit.config import (
    JaneSettings,
    LimitError,
    LimitLayer,
    Limits,
    layer_from_env,
    load_layer,
    resolve_limits,
)


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
