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


class HttpLimits(Limits):
    timeout_s: float = Field(default=10.0, gt=0)
    max_redirects: int = 5


class CrawlLimits(Limits):
    concurrency: int = Field(default=4, ge=1)
    max_depth: int = 3
    http: HttpLimits = HttpLimits()


def test_defaults_when_no_layers() -> None:
    r = resolve_limits(CrawlLimits)
    assert r.limits.concurrency == 4
    assert r.limits.http.timeout_s == 10.0
    assert all(origin == "default" for _, _, origin in r.explain())


def test_platform_source_job_inheritance() -> None:
    r = resolve_limits(
        CrawlLimits,
        LimitLayer("platform", {"concurrency": 8, "http": {"timeout_s": 20}}),
        LimitLayer("source", {"max_depth": 10}, name="shop.example"),
        LimitLayer("job", {"concurrency": 2}, name="prices"),
    )
    assert r.limits.concurrency == 2
    assert r.limits.max_depth == 10
    assert r.limits.http.timeout_s == 20
    assert r.limits.http.max_redirects == 5
    assert r.origin == {
        "concurrency": "job:prices",
        "http.timeout_s": "platform",
        "max_depth": "source:shop.example",
    }


def test_ceiling_clamps_more_specific_layers() -> None:
    r = resolve_limits(
        CrawlLimits,
        LimitLayer("platform", ceilings={"concurrency": 6}),
        LimitLayer("job", {"concurrency": 50}),
    )
    assert r.limits.concurrency == 6
    assert r.clamped == {"concurrency": "platform"}
    assert ("concurrency", 6, "job (clamped by platform)") in r.explain()


def test_ceiling_error_mode() -> None:
    with pytest.raises(LimitError, match="exceeds ceiling"):
        resolve_limits(CrawlLimits, LimitLayer("platform", ceilings={"max_depth": 2}), on_exceed="error")


def test_lower_layer_cannot_loosen_ceiling() -> None:
    with pytest.raises(LimitError, match="exceeds ceiling"):
        resolve_limits(
            CrawlLimits,
            LimitLayer("platform", ceilings={"concurrency": 6}),
            LimitLayer("source", ceilings={"concurrency": 60}),
        )


def test_unknown_and_invalid_values_rejected() -> None:
    with pytest.raises(LimitError, match="unknown limit"):
        resolve_limits(CrawlLimits, LimitLayer("job", {"concurency": 1}))
    with pytest.raises(LimitError, match="invalid limits"):
        resolve_limits(CrawlLimits, LimitLayer("job", {"concurrency": 0}))


def test_limits_subclass_requires_defaults() -> None:
    with pytest.raises(TypeError, match="safe default"):

        class Bad(Limits):
            concurrency: int


def test_env_layer_coerces_strings() -> None:
    env = {
        "X_LIMITS__CONCURRENCY": "7",
        "X_LIMITS__HTTP__TIMEOUT_S": "2.5",
        "X_LIMITS__CEILING__MAX_DEPTH": "4",
        "OTHER": "1",
    }
    layer = layer_from_env("X_LIMITS__", environ=env)
    r = resolve_limits(CrawlLimits, layer)
    assert r.limits.concurrency == 7
    assert r.limits.http.timeout_s == 2.5
    assert r.limits.max_depth == 3
    assert r.origin["concurrency"] == "platform:env"


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("l.toml", "[limits]\nconcurrency = 3\n[limits.http]\ntimeout_s = 1.5\n[ceilings]\nmax_depth = 2\n"),
        (
            "l.json",
            '{"limits": {"concurrency": 3, "http": {"timeout_s": 1.5}}, "ceilings": {"max_depth": 2}}',
        ),
        ("l.yaml", "limits:\n  concurrency: 3\n  http:\n    timeout_s: 1.5\nceilings:\n  max_depth: 2\n"),
    ],
)
def test_load_layer_formats(tmp_path: Path, name: str, text: str) -> None:
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    r = resolve_limits(CrawlLimits, load_layer(f, "platform"))
    assert (r.limits.concurrency, r.limits.http.timeout_s, r.limits.max_depth) == (3, 1.5, 2)


def test_load_layer_rejects_unknown_sections(tmp_path: Path) -> None:
    f = tmp_path / "bad.toml"
    f.write_text("concurrency = 3\n", encoding="utf-8")
    with pytest.raises(LimitError, match="unexpected top-level"):
        load_layer(f, "platform")


def test_settings_platform_layers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "p.toml"
    f.write_text("[limits]\nconcurrency = 3\nmax_depth = 9\n", encoding="utf-8")
    monkeypatch.setenv("SVC_LIMITS__CONCURRENCY", "5")
    settings = JaneSettings(limits_file=f)
    r = resolve_limits(CrawlLimits, *settings.platform_layers("SVC_LIMITS__"))
    assert (r.limits.concurrency, r.limits.max_depth) == (5, 9)
    assert r.origin["concurrency"] == "platform:env"
