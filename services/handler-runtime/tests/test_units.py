from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path
from typing import Any

import pytest

from jane_handler_runtime.cli import build_context, main
from jane_handler_runtime.profiles import check_dependencies, load_profiles
from jane_handler_runtime.sandbox import Bundle
from jane_handler_runtime.settings import Settings, request_layer, resolve_service_limits

SERVICE = Path(__file__).resolve().parents[1]


def test_profile_matches_image_requirements() -> None:
    profile = load_profiles()["python-extractor@1"]
    lines = (
        (SERVICE / "sandbox" / "python-extractor-1" / "requirements.txt")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    pinned = dict(line.split("==") for line in lines if line and not line.startswith("#"))
    assert pinned == dict(profile.libraries)
    dockerfile = (SERVICE / "sandbox" / "python-extractor-1" / "Dockerfile").read_text(encoding="utf-8")
    assert profile.document["base_image"] in dockerfile


@pytest.mark.parametrize(
    ("requirement", "problem"),
    [
        ("selectolax>=0.3,<0.4", None),
        ("lxml==6.1.3", None),
        ("Python-Dateutil>=2.8", None),
        ("selectolax>=0.4", "does not satisfy"),
        ("requests", "not available"),
        ("lxml @ https://example.test/lxml.whl", "direct URL"),
        ("not a requirement!!", "invalid requirement"),
        ("pywin32; sys_platform == 'win32'", None),
    ],
)
def test_dependency_check(requirement: str, problem: str | None) -> None:
    problems = check_dependencies(load_profiles()["python-extractor@1"], [requirement])
    if problem is None:
        assert problems == []
    else:
        assert problem in problems[0].message


def test_request_limits_are_clamped_by_hard_caps(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(log_format="console")
    layer = request_layer(
        {"sandbox": {"memory_mb": 100_000, "wall_time_ms": 5000}, "crawl": {"max_depth": 3}}
    )
    resolved = resolve_service_limits(settings, layer)
    assert resolved.limits.sandbox.memory_mb == 4096  # service default hard cap
    assert resolved.limits.sandbox.wall_time_ms == 5000
    assert resolved.provenance()["sandbox.memory_mb"] == "hard_cap"
    monkeypatch.setenv("JANE_HANDLER_RUNTIME_LIMITS__HARD_CAPS__SANDBOX__MEMORY_MB", "8192")
    monkeypatch.setenv("JANE_HANDLER_RUNTIME_LIMITS__SANDBOX__WALL_TIME_MS", "10000")
    resolved = resolve_service_limits(Settings(log_format="console"), layer)
    assert resolved.limits.sandbox.memory_mb == 8192  # platform cap replaces the service default cap
    base = resolve_service_limits(Settings(log_format="console"))
    assert base.limits.sandbox.wall_time_ms == 10000


def test_limits_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "limits.json"
    path.write_text(
        json.dumps(
            {
                "profile": "ci",
                "defaults": {"sandbox": {"cpu_cores": 0.5}},
                "hard_caps": {"sandbox": {"cpu_cores": 1}},
            }
        ),
        encoding="utf-8",
    )
    resolved = resolve_service_limits(Settings(log_format="console", limits_file=path))
    assert resolved.limits.sandbox.cpu_cores == 0.5
    assert resolved.platform_limits()["profile"] == "ci"


def test_bundle_tar_is_read_only_for_the_sandbox_user() -> None:
    bundle = Bundle()
    bundle.add("package/src/a.py", b"x")
    bundle.add("request.json", b"{}")
    with pytest.raises(ValueError, match="invalid bundle path"):
        bundle.add("../escape", b"")
    with tarfile.open(fileobj=io.BytesIO(bundle.tar())) as tar:
        members = {m.name: m for m in tar.getmembers()}
    assert members["package"].isdir() and members["package"].mode == 0o555
    assert members["package/src/a.py"].mode == 0o444
    assert all(m.uid == 0 for m in members.values())


def test_build_context_contains_only_needed_files() -> None:
    context, dockerfile = build_context("python-extractor@1")
    with tarfile.open(fileobj=io.BytesIO(context)) as tar:
        names = tar.getnames()
    assert dockerfile in names
    assert "services/handler-runtime/sandbox/python-extractor-1/requirements.txt" in names
    assert "libs/extractor-sdk/src/jane_extractor_sdk/runner.py" in names
    assert all(n.startswith(("services/handler-runtime/sandbox/", "libs/extractor-sdk/src/")) for n in names)


def test_cli_profile_and_run(capsys: pytest.CaptureFixture[str], h: Any, tmp_path: Path) -> None:
    assert main(["profile", "--json"]) == 0
    assert "lxml" in json.loads(capsys.readouterr().out)["python-extractor@1"]["libraries"]
    page = h.example / "tests" / "product-phone-alpha" / "page.html"
    out = tmp_path / "result.json"
    code = main(
        ["run", str(h.example), str(page), "--media-type", "text/html", "--url", "https://t.test/product/phone-alpha",
         "--backend", "subprocess", "--unsafe-no-sandbox", "-o", str(out)]
    )  # fmt: skip
    assert code == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["status"] == "success" and result["test_mode"] is True
    code = main(
        [
            "run",
            str(h.example),
            str(page),
            "--params",
            '{"default_currency": 1}',
            "--backend",
            "subprocess",
            "--unsafe-no-sandbox",
        ]
    )
    assert code == 2
    assert "params_schema" in capsys.readouterr().err
