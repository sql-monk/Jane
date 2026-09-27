"""Tests of the WP-01 Claude Code hooks (.claude/hooks/format.py, scan_secrets.py)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"


def run_hook(name: str, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=120,
    )


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "test")
    (tmp_path / "a.txt").write_text("hello\n", encoding="utf-8")
    git(tmp_path, "add", "a.txt")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


# Synthetic AWS-style key pair split so that this file itself is not a finding.
FAKE = (
    "aws_access_key_id = AKIA"
    + "Q3EGRIIBV7XHKT2D\naws_secret_access_key = wJalrXUtnFEMI"
    + "K7MDENGbPxRfiCYzEXAMPLEKEY9x\n"
)
needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks not installed")


@needs_gitleaks
def test_scan_blocks_staged_secret(repo: Path) -> None:
    (repo / "creds.txt").write_text(FAKE, encoding="utf-8")
    git(repo, "add", "creds.txt")
    r = run_hook("scan_secrets.py", {"tool_input": {"command": 'git commit -m "x"'}, "cwd": str(repo)})
    assert r.returncode == 2, r.stderr
    assert "commit blocked" in r.stderr
    assert "wJalrXUtnFEMI" not in r.stderr  # redacted


@needs_gitleaks
def test_scan_blocks_unstaged_secret_for_commit_all(repo: Path) -> None:
    (repo / "a.txt").write_text(FAKE, encoding="utf-8")
    r = run_hook("scan_secrets.py", {"tool_input": {"command": "git commit -am x"}, "cwd": str(repo)})
    assert r.returncode == 2, r.stderr


@needs_gitleaks
def test_scan_allows_clean_commit_and_ignores_other_commands(repo: Path) -> None:
    (repo / "b.txt").write_text("nothing secret\n", encoding="utf-8")
    git(repo, "add", "b.txt")
    assert (
        run_hook(
            "scan_secrets.py", {"tool_input": {"command": "git commit -m ok"}, "cwd": str(repo)}
        ).returncode
        == 0
    )
    (repo / "creds.txt").write_text(FAKE, encoding="utf-8")
    git(repo, "add", "creds.txt")
    assert (
        run_hook("scan_secrets.py", {"tool_input": {"command": "git status"}, "cwd": str(repo)}).returncode
        == 0
    )


def test_hooks_never_fail_on_bad_input() -> None:
    for name in ("scan_secrets.py", "format.py"):
        r = subprocess.run(
            [sys.executable, str(HOOKS / name)],
            input="not json",
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        assert r.returncode == 0, (name, r.stderr)


def test_format_hook_formats_python_and_reports_leftovers(tmp_path: Path) -> None:
    ruff = (
        ROOT
        / ".venv"
        / ("Scripts" if sys.platform == "win32" else "bin")
        / ("ruff.exe" if sys.platform == "win32" else "ruff")
    )
    if not ruff.is_file():
        pytest.skip("workspace venv with ruff not found (uv sync)")
    target = ROOT / "scripts" / "_format_hook_probe.py"
    target.write_text("import os\nx=[1,\n2]\ndef f( a ):\n    return eval(a)\n", encoding="utf-8")
    try:
        r = run_hook("format.py", {"tool_input": {"file_path": str(target)}, "cwd": str(ROOT)})
        assert r.returncode == 0
        text = target.read_text(encoding="utf-8")
        assert "import os" not in text  # unused import removed by ruff --fix
        assert "x = [1, 2]" in text
        out = json.loads(r.stdout)
        assert "S307" in out["hookSpecificOutput"]["additionalContext"]
    finally:
        target.unlink(missing_ok=True)


def test_format_hook_skips_missing_and_non_python(tmp_path: Path) -> None:
    f = tmp_path / "x.txt"
    f.write_text("a  =  1\n", encoding="utf-8")
    for path in (f, tmp_path / "missing.py"):
        r = run_hook("format.py", {"tool_input": {"file_path": str(path)}, "cwd": str(tmp_path)})
        assert r.returncode == 0 and r.stdout == ""
    assert f.read_text(encoding="utf-8") == "a  =  1\n"
