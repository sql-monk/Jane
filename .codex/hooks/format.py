"""PostToolUse (Edit|Write|MultiEdit): format the changed file (soft, never blocks).

* ``*.py``  -> ``ruff format`` + ``ruff check --fix`` (project venv ruff, else ``ruff`` on PATH);
  remaining lint findings are returned to the agent as additional context.
* files under ``web/`` -> ``prettier --write`` if it is installed in ``node_modules``.
Missing tools, timeouts and errors are ignored: the hook must not break the work.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jane_wp import find_root, relative_to_root

TIMEOUT_S = float(os.environ.get("JANE_FORMAT_HOOK_TIMEOUT_S", "20"))
PRETTIER_SUFFIXES = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".json",
    ".css",
    ".scss",
    ".html",
    ".md",
    ".yaml",
    ".yml",
    ".vue",
}


def _bin(name: str, *dirs: Path) -> str | None:
    for d in dirs:
        for candidate in (d / name, d / f"{name}.exe", d / f"{name}.cmd"):
            if candidate.is_file():
                return str(candidate)
    return shutil.which(name)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str] | None:
    try:
        # Callers supply a resolved formatter executable and fixed arguments; no shell.
        return subprocess.run(  # noqa: S603
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def format_python(root: Path, target: Path) -> str | None:
    venv = root / ".venv"
    ruff = _bin("ruff", venv / "Scripts", venv / "bin")
    if ruff is None:
        return None
    path = str(target)
    _run([ruff, "check", "--fix", "--force-exclude", "--quiet", path], root)
    _run([ruff, "format", "--force-exclude", "--quiet", path], root)
    left = _run([ruff, "check", "--force-exclude", "--output-format", "concise", path], root)
    if left is not None and left.returncode != 0 and left.stdout.strip():
        lines = [ln for ln in left.stdout.strip().splitlines() if ln and not ln.startswith("Found")]
        return "ruff: remaining findings after auto-fix:\n" + "\n".join(lines[:20])
    return None


def format_web(root: Path, target: Path, rel: str) -> None:
    if not rel.startswith("web/") or target.suffix.lower() not in PRETTIER_SUFFIXES:
        return
    # Only a project-installed prettier (pnpm install); never download one on the fly.
    for directory in (target.parent, *target.parents):
        for name in ("prettier.cmd", "prettier"):
            candidate = directory / "node_modules" / ".bin" / name
            if candidate.is_file():
                _run([str(candidate), "--write", "--log-level", "warn", str(target)], root)
                return
        if directory == root:
            return


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    tool_input = data.get("tool_input") or {}
    raw = tool_input.get("file_path")
    if not raw:
        return 0
    target = Path(raw)
    if not target.is_absolute():
        target = Path(data.get("cwd") or ".") / target
    if not target.is_file():
        return 0
    root = find_root(target)
    if root is None:
        return 0
    rel = relative_to_root(root, target)
    if rel is None:
        return 0
    note = None
    if target.suffix == ".py":
        note = format_python(root, target)
    else:
        format_web(root, target, rel)
    if note:
        print(
            json.dumps(
                {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": note}},
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"format hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
