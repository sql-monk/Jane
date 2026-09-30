"""Run one pytest node id N times in a row (a stability check); stops at the first failure.

    uv run --all-packages python services/web-collector/scripts/repeat_test.py 20 \\
        services/web-collector/tests/test_multi_instance.py::test_stalled_owner_is_fenced_out
"""

from __future__ import annotations

import subprocess
import sys
import time


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    n, nodes = int(argv[0]), argv[1:]
    cmd = ["uv", "run", "--all-packages", "pytest", *nodes, "-p", "no:logging", "-q", "-rA"]
    print("$", " ".join(cmd), f"   # x{n}", flush=True)
    for i in range(1, n + 1):
        started = time.monotonic()
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")  # noqa: S603
        out = proc.stdout.strip().splitlines()
        summary = out[-1] if out else "(no output)"
        print(
            f"--- run {i}/{n} rc={proc.returncode} {time.monotonic() - started:.0f}s: {summary}", flush=True
        )
        for line in out:
            if line.startswith(("PASSED", "FAILED", "ERROR")):
                print("   ", line[:300], flush=True)
        if proc.returncode != 0:
            print(proc.stdout[-8000:], proc.stderr[-2000:], sep="\n", flush=True)
            print(f"=== {i} runs, 1 failed", flush=True)
            return 1
    print(f"=== {n} runs, 0 failed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
