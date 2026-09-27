"""PreToolUse (Bash|PowerShell): scan for secrets with gitleaks before `git commit`.

Scans the staged diff and the unstaged diff of tracked files (covers `git commit -a` and
`git add ... && git commit`). Files that are still untracked at this point are covered by the git
pre-commit hook (`just hooks`). Findings block the command (exit 2) with a redacted report.
If gitleaks is not installed the hook only warns: it must not break work on machines without it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jane_wp import find_root

COMMIT_RE = re.compile(r"\bgit\b[^;&|\n]*\bcommit\b")
TIMEOUT_S = float(os.environ.get("JANE_SECRET_SCAN_TIMEOUT_S", "60"))


def scan(root: Path, gitleaks: str, staged: bool) -> tuple[int, str]:
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
        timeout=TIMEOUT_S,
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
    for staged in (True, False):
        code, out = scan(root, gitleaks, staged)
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
