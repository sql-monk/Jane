"""PreToolUse (Bash|PowerShell): scan for secrets with gitleaks before `git commit`.

Scans the staged diff and the unstaged diff of tracked files (covers `git commit -a` and
`git add ... && git commit`). Files that are still untracked at this point are covered by the git
pre-commit hook (`just hooks`). Findings block the command (exit 2) with a redacted report.
If gitleaks is not installed the hook only warns: it must not break work on machines without it.

Time budget: ``JANE_SECRET_SCAN_TIMEOUT_S`` (default 100 s) is the total for both scans, so both scans
plus the ``uv run`` start-up fit into the hook timeout (150 s in ``.claude/settings.json``). A scan
that runs out of time is reported as a warning and does not block. Rules: gitleaks defaults extended by
``.gitleaks.toml`` in the repository root (picked up automatically for the scanned path).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jane_wp import find_root

COMMIT_RE = re.compile(r"\bgit\b[^;&|\n]*\bcommit\b")
TOTAL_TIMEOUT_S = float(os.environ.get("JANE_SECRET_SCAN_TIMEOUT_S", "100"))


def scan(root: Path, gitleaks: str, staged: bool, timeout_s: float) -> tuple[int, str]:
    cmd = [gitleaks, "git", "--pre-commit", "--redact", "--no-banner", "--verbose", "--exit-code", "3"]
    if staged:
        cmd.append("--staged")
    cmd.append(str(root))
    proc = subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
        check=False,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not COMMIT_RE.search(cmd):
        return 0
    root = find_root(Path(data.get("cwd") or "."))
    if root is None:
        return 0
    gitleaks = shutil.which("gitleaks")
    if gitleaks is None:
        print(
            "Jane secret scan: gitleaks not found, commit is not scanned (install gitleaks).", file=sys.stderr
        )
        return 0
    reports = []
    deadline = time.monotonic() + TOTAL_TIMEOUT_S
    for staged in (True, False):
        remaining = deadline - time.monotonic()
        try:
            if remaining <= 0:
                raise subprocess.TimeoutExpired("gitleaks", 0)
            code, out = scan(root, gitleaks, staged, remaining)
        except subprocess.TimeoutExpired:
            print(
                f"Jane secret scan: gitleaks did not finish within {TOTAL_TIMEOUT_S:.0f}s "
                "(JANE_SECRET_SCAN_TIMEOUT_S); commit is not fully scanned.",
                file=sys.stderr,
            )
            continue
        if code == 3:
            reports.append(("staged" if staged else "unstaged") + " changes:\n" + out[-4000:])
        elif code not in (0, 3):
            print(f"Jane secret scan: gitleaks failed ({code}), ignored: {out[-500:]}", file=sys.stderr)
    if not reports:
        return 0
    print(
        "Jane secret scan: gitleaks found possible secrets - commit blocked. Remove them (use env/"
        "managed connections), or add a justified allowlist entry to .gitleaks.toml.\n\n"
        + "\n\n".join(reports),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"scan_secrets hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
