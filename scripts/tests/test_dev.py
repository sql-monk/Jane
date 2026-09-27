from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"jane_scripts_{name}", SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


dev = load("dev")


def test_new_service_renders_every_name(tmp_path: Path) -> None:
    dest = dev.new_service("price-checker", tmp_path)
    files = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    assert "src/jane_price_checker/app.py" in files
    assert {"Dockerfile", "README.md", "CLAUDE.md", "pyproject.toml", "tests/test_app.py"} <= files
    for f in dest.rglob("*"):
        if f.is_file():
            text = f.read_text(encoding="utf-8")
            assert not re.search(r"template[-_ ]service|TemplateService|TEMPLATE_SERVICE", text, re.I), f
    pyproject = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "jane-price-checker"' in pyproject
    docker = (dest / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY services/price-checker/ services/price-checker/" in docker
    assert "--package jane-price-checker" in docker
    assert "JANE_PRICE_CHECKER_PORT" in docker
    claude = (dest / "CLAUDE.md").read_text(encoding="utf-8").strip().splitlines()
    assert len(claude) == 3


@pytest.mark.parametrize("bad", ["Web", "web_collector", "-x", "x-", "1abc", "a--b"])
def test_new_service_rejects_bad_names(tmp_path: Path, bad: str) -> None:
    with pytest.raises(SystemExit):
        dev.new_service(bad, tmp_path)


def test_new_service_refuses_to_overwrite(tmp_path: Path) -> None:
    dev.new_service("svc", tmp_path)
    with pytest.raises(SystemExit, match="already exists"):
        dev.new_service("svc", tmp_path)


def test_default_project_is_valid_and_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JANE_COMPOSE_PROJECT", raising=False)
    name = dev.default_project()
    assert re.fullmatch(r"jane-[a-z0-9-]+-[0-9a-f]{6}", name)
    assert name == dev.default_project()
    monkeypatch.setenv("JANE_COMPOSE_PROJECT", "jane-custom")
    assert dev.default_project() == "jane-custom"


def test_resolve_target() -> None:
    assert dev.resolve_target("jane-kit") == ROOT / "libs" / "jane-kit"
    assert dev.resolve_target("template-service") == ROOT / "templates" / "service"
    assert dev.resolve_target("testsite") == ROOT / "tests" / "fixtures" / "testsite"


@pytest.mark.skipif(
    shutil.which("gitleaks") is None or shutil.which("git") is None, reason="needs git + gitleaks"
)
def test_pre_commit_hook_blocks_secret(tmp_path: Path) -> None:
    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "core.autocrlf=false", *args],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "test")
    hook = dev.install_hook(tmp_path)
    assert hook.is_file()
    (tmp_path / "ok.txt").write_text("hello\n", encoding="utf-8")
    git("add", "ok.txt")
    assert git("commit", "-q", "-m", "ok").returncode == 0
    # A synthetic AWS-style key pair (not a real credential).
    fake = (
        "aws_access_key_id = AKIA"
        + "Q3EGRIIBV7XHKT2D"
        + "\naws_secret_access_key = "
        + "wJalrXUtnFEMI"
        + "K7MDENGbPxRfiCYzEXAMPLEKEY9x"
        + "\n"
    )
    (tmp_path / "leak.txt").write_text(fake, encoding="utf-8")
    git("add", "leak.txt")
    blocked = git("commit", "-q", "-m", "leak")
    assert blocked.returncode != 0, blocked.stdout + blocked.stderr
