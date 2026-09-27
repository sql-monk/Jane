"""Tests of the WP-01 Claude Code hooks (.claude/hooks/format.py, scan_secrets.py)."""

from __future__ import annotations

import hashlib
import json
import os
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


HEX64 = hashlib.sha256(b"jane-delivery").hexdigest()  # high-entropy, like real delivery keys


def _gitleaks_on_commit(base: Path, files: dict[str, str]) -> int:
    """Commit ``files`` into a fresh repo and scan its history with the repository's .gitleaks.toml."""
    repo = base / f"r{len(list(base.iterdir()))}"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "test")
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "x")
    cfg = str(ROOT / ".gitleaks.toml")
    cmd = ["gitleaks", "git", "--config", cfg, "--no-banner", "--redact", "--exit-code", "3", str(repo)]
    return subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60).returncode


@needs_gitleaks
def test_gitleaks_config_allows_only_contract_delivery_keys(tmp_path: Path) -> None:
    allowed = {
        "contracts/examples/invocation.json": f'{{"delivery_key": "{HEX64}"}}\n',
        "contracts/openapi/storage.v1.yaml": f"delivery_key: {HEX64}\n",
    }
    assert _gitleaks_on_commit(tmp_path, allowed) == 0
    # the same value under another name, or outside contracts/, is still a finding
    assert _gitleaks_on_commit(tmp_path, {"contracts/examples/x.yaml": f"api_key: {HEX64}\n"}) == 3
    assert _gitleaks_on_commit(tmp_path, {"app/settings.yaml": f"delivery_key: {HEX64}\n"}) == 3
    # real-looking credentials are caught everywhere, contracts/ included
    assert _gitleaks_on_commit(tmp_path, {"creds.txt": FAKE}) == 3
    assert _gitleaks_on_commit(tmp_path, {"contracts/examples/leak.txt": FAKE}) == 3


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


def test_format_hook_formats_python_and_reports_leftovers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path
    (repo / ".git").mkdir()  # the hook only needs a checkout root marker; no git binary required
    ruff = shutil.which("ruff") or shutil.which("ruff", path=str(Path(sys.executable).parent))
    if ruff is None:
        pytest.skip("ruff not found (uv sync)")
    # The hook falls back to `ruff` on PATH when the checkout has no .venv (the temp repo has none).
    monkeypatch.setenv("PATH", str(Path(ruff).parent) + os.pathsep + os.environ.get("PATH", ""))
    target = repo / "probe.py"
    target.write_text("import os\nx=[1,\n2]\ndef f( a ):\n    return undefined_name\n", encoding="utf-8")
    r = run_hook("format.py", {"tool_input": {"file_path": str(target)}, "cwd": str(repo)})
    assert r.returncode == 0, r.stderr
    text = target.read_text(encoding="utf-8")
    assert "import os" not in text  # unused import removed by ruff --fix
    assert "x = [1, 2]" in text  # ruff format
    out = json.loads(r.stdout)
    assert "F821" in out["hookSpecificOutput"]["additionalContext"]  # not auto-fixable -> reported


def test_format_hook_skips_missing_and_non_python(tmp_path: Path) -> None:
    f = tmp_path / "x.txt"
    f.write_text("a  =  1\n", encoding="utf-8")
    for path in (f, tmp_path / "missing.py"):
        r = run_hook("format.py", {"tool_input": {"file_path": str(path)}, "cwd": str(tmp_path)})
        assert r.returncode == 0 and r.stdout == ""
    assert f.read_text(encoding="utf-8") == "a  =  1\n"
