"""Timing of the secret scanner on adversarial inputs (review 2: ReDoS).

    uv run --package jane-registry python services/registry/scripts/scan_bench.py [--timeout 60] [--repeat 3]

For every case the scanner runs on N, 2N, 4N bytes and on ``secrets.max_scan_bytes_per_file`` (2 MiB by default)
in a child process with a timeout; the minimum of ``--repeat`` runs is printed together with the ratios
t(2N)/t(N) and t(4N)/t(2N) (about 2 for a linear scanner, about 4 for a quadratic one).
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import random
import time
from collections.abc import Callable

from jane_registry.secrets import scan_files
from jane_registry.settings import SecretScanLimits


def _random(n: int) -> bytes:
    return random.Random(1).randbytes(n)  # noqa: S311 - reproducible test data, not crypto


CASES: list[tuple[str, str, Callable[[int], bytes]]] = [
    ("newlines", "c.yaml", lambda n: b"\n" * n),
    ("newlines", "LICENSE", lambda n: b"\n" * n),
    ("space+newline", "c.yaml", lambda n: b" \n" * (n // 2)),
    ("tab+CR+newline", "c.ini", lambda n: b"\t\r\n" * (n // 3)),
    ("NUL+space", "c.yaml", lambda n: b"\0 " * (n // 2)),
    ("random binary (NUL)", "m.bin", _random),
    ("random binary (NUL)", "blob", _random),
    ("random binary (NUL)", "c.yaml", _random),
    ("password= lines", "c.ini", lambda n: b"password=abcdef1\n" * (n // 17)),
    ("jwt eyJ- repeated", "c.py", lambda n: b"eyJ-" * (n // 4)),
    ("url a://x:::", "c.py", lambda n: b"a://x" + b":" * n),
    ("bearer + newlines", "c.py", lambda n: b"bearer" + b"\n" * n + b"!"),
    ("= then newlines", "c.py", lambda n: b"=" + b"\n" * n + b"!"),
    ("name.name.name", "c.yaml", lambda n: b"a." * (n // 2)),
    ("password password...", "c.yaml", lambda n: b"password" * (n // 8)),
    ("password password...", "LICENSE", lambda n: b"password" * (n // 8)),
    ("secretsecret...", "c.py", lambda n: b"secret" * (n // 6)),
    ("password=a password=a", "c.yaml", lambda n: b"password=a" * (n // 10)),
    ("token token ...", "c.yaml", lambda n: b"token " * (n // 6)),
    ("python source", "c.py", lambda n: b"def f(x):\n    return x + 1  # comment\n" * (n // 38)),
]


def _run(path: str, data: bytes, repeat: int, out: mp.Queue) -> None:  # type: ignore[type-arg]
    limits = SecretScanLimits()
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        scan_files({path: data}, limits)
        best = min(best, time.perf_counter() - t0)
        if best > 5:
            break
    out.put(best)


def measure(path: str, data: bytes, repeat: int, timeout: float) -> float | None:
    q: mp.Queue = mp.Queue()  # type: ignore[type-arg]
    p = mp.Process(target=_run, args=(path, data, repeat, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return None
    return float(q.get())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16_384, help="base size N in bytes (default 16384)")
    ap.add_argument("--timeout", type=float, default=60.0, help="seconds per measurement (default 60)")
    ap.add_argument("--repeat", type=int, default=3, help="runs per size, minimum is reported (default 3)")
    ap.add_argument("--no-full", action="store_true", help="skip the max_scan_bytes_per_file size")
    ns = ap.parse_args()
    full = SecretScanLimits().max_scan_bytes_per_file
    sizes = [ns.n, 2 * ns.n, 4 * ns.n] + ([] if ns.no_full else [full])
    print(f"sizes: {sizes}  timeout: {ns.timeout}s  repeat: {ns.repeat} (min)")
    for name, path, gen in CASES:
        times: list[float | None] = []
        cells = []
        for size in sizes:
            data = gen(size)
            t = measure(path, data, ns.repeat, ns.timeout) if not (times and times[-1] is None) else None
            times.append(t)
            cells.append(f"{len(data)}B:" + (f"{t:.3f}s" if t is not None else f">{ns.timeout:.0f}s"))
        ratios = []
        for a, b in ((0, 1), (1, 2)):
            ta, tb = times[a], times[b]
            ratios.append(f"{tb / ta:.2f}" if ta and tb and ta > 0 else "-")
        print(
            f"{name:22s} {path:8s} " + "  ".join(cells) + f"  ratio 2N/N={ratios[0]} 4N/2N={ratios[1]}",
            flush=True,
        )


if __name__ == "__main__":
    main()
