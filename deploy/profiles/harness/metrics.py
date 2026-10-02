"""Pure metric and verdict functions of the limits harness (unit-tested without Docker).

A probe event is the JSON of ``probe_site.py``: ``{"seq", "ns", "path", "query", "start", "end", "status"}``
with server epoch seconds. A check is ``{"name", "value", "op", "limit", "ok", "severity"}``; severity
``blocker`` fails the profile, ``warning`` is reported but does not.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from itertools import pairwise
from typing import Any

Event = Mapping[str, Any]
Check = dict[str, Any]

OPS = {
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
}


def check(name: str, value: Any, op: str, limit: Any, severity: str = "blocker") -> Check:
    ok = value is not None and bool(OPS[op](value, limit))
    return {"name": name, "value": value, "op": op, "limit": limit, "ok": ok, "severity": severity}


def verdict(checks: Iterable[Check]) -> str:
    items = list(checks)
    if any(not c["ok"] and c["severity"] == "blocker" for c in items):
        return "fail"
    if any(not c["ok"] for c in items):
        return "warn"
    return "pass"


def percentile(values: Sequence[float], p: float) -> float | None:
    """Nearest-rank percentile (``p`` in 0..100); ``None`` for no values."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def starts(events: Iterable[Event]) -> list[float]:
    return sorted(float(e["start"]) for e in events)


def start_gaps(events: Iterable[Event]) -> list[float]:
    s = starts(events)
    return [b - a for a, b in pairwise(s)]


def max_in_window(times: Sequence[float], window_s: float) -> int:
    """Largest number of ``times`` inside any half-open window ``[t, t + window_s)``."""
    ordered = sorted(times)
    best, lo = 0, 0
    for hi, t in enumerate(ordered):
        while ordered[lo] <= t - window_s:
            lo += 1
        best = max(best, hi - lo + 1)
    return best


def max_concurrency(events: Iterable[Event]) -> int:
    """Largest number of requests in flight at once (server side: from ``start`` to ``end``)."""
    points: list[tuple[float, int]] = []
    for e in events:
        end = e.get("end")
        if end is None:
            continue
        points.append((float(e["start"]), 1))
        points.append((float(end), -1))
    points.sort(key=lambda p: (p[0], p[1]))  # an end before a start at the same instant
    best = cur = 0
    for _, delta in points:
        cur += delta
        best = max(best, cur)
    return best


def request_interval(rate: Mapping[str, Any]) -> float:
    """Minimum interval between request starts to one host, as the web collector derives it."""
    rps = float(rate.get("requests_per_second_per_host") or 0)
    base = 1.0 / rps if rps > 0 else 0.0
    return max(base, float(rate.get("min_delay_ms_per_host") or 0) / 1000)


MEAN_GAP_SPAN = 5
"""Gaps averaged by the rate check: a single late request start (event-loop or timer jitter, ~15 ms on
Windows) shortens the next gap without making the source see a higher rate."""


def mean_gaps(gaps: Sequence[float], span: int = MEAN_GAP_SPAN) -> list[float]:
    """Means of every ``span`` consecutive gaps (all gaps when there are fewer)."""
    if len(gaps) < span:
        return [sum(gaps) / len(gaps)] if gaps else []
    return [sum(gaps[i : i + span]) / span for i in range(len(gaps) - span + 1)]


def compensated_gaps(gaps: Sequence[float]) -> list[float]:
    """For each gap, its best neighbouring pair mean; a delayed arrival can compensate on either side."""
    out = []
    for i, gap in enumerate(gaps):
        pairs = []
        if i:
            pairs.append((gaps[i - 1] + gap) / 2)
        if i + 1 < len(gaps):
            pairs.append((gap + gaps[i + 1]) / 2)
        out.append(max(pairs) if pairs else gap)
    return out


def rate_checks(
    events: Sequence[Event], rate: Mapping[str, Any], th: Mapping[str, Any], *, expected: int
) -> tuple[dict[str, Any], list[Check]]:
    """Politeness per host (server-side request starts).

    Blockers: requests in any 1 s window <= ceil(1 / interval) + 1; every gap has an adjacent
    gap whose pair mean, and every 5-gap mean, are >= interval - tolerance; the number of gaps
    below half the interval is bounded by the profile. Warnings: a single gap below
    interval - tolerance (jitter), average rate below ``min_efficiency`` of the limit (over-throttling).
    """
    interval = request_interval(rate)
    gaps = start_gaps(events)
    s = starts(events)
    duration = (s[-1] - s[0]) if len(s) > 1 else 0.0
    means = mean_gaps(gaps)
    compensated = compensated_gaps(gaps)
    metrics = {
        "requests": len(events),
        "interval_s": interval,
        "min_gap_s": min(gaps) if gaps else None,
        "sub_half_gaps": sum(gap < interval / 2 for gap in gaps),
        "p50_gap_s": percentile(gaps, 50),
        f"min_mean_of_{MEAN_GAP_SPAN}_gaps_s": min(means) if means else None,
        "min_compensated_gap_s": min(compensated) if compensated else None,
        "max_in_1s": max_in_window(s, 1.0),
        "avg_rate_rps": (len(s) - 1) / duration if duration > 0 else None,
    }
    tolerance = max(interval * float(th["gap_tolerance_fraction"]), float(th["gap_tolerance_abs_s"]))
    checks = [check("all pages requested", len(events), ">=", expected)]
    if interval > 0 and gaps:
        checks += [
            check("requests in any 1 s window", metrics["max_in_1s"], "<=", math.ceil(1.0 / interval) + 1),
            check(
                f"mean of {MEAN_GAP_SPAN} consecutive gaps, s",
                metrics[f"min_mean_of_{MEAN_GAP_SPAN}_gaps_s"],
                ">=",
                round(interval - tolerance, 4),
            ),
            check(
                "short gap compensated by an adjacent gap, s",
                metrics["min_compensated_gap_s"],
                ">=",
                round(interval - tolerance, 4),
            ),
            check(
                "gaps below half the interval", metrics["sub_half_gaps"], "<=", int(th["max_sub_half_gaps"])
            ),
            check(
                "single gap (jitter), s",
                metrics["min_gap_s"],
                ">=",
                round(interval - tolerance, 4),
                "warning",
            ),
        ]
        if metrics["avg_rate_rps"] is not None:
            floor = round(float(th["min_efficiency"]) / interval, 3)
            checks.append(
                check("average rate, rps (efficiency)", metrics["avg_rate_rps"], ">=", floor, "warning")
            )
    return metrics, checks


def attempts_by_path(events: Iterable[Event]) -> dict[str, list[Event]]:
    out: dict[str, list[Event]] = defaultdict(list)
    for e in events:
        out[str(e["path"])].append(e)
    for items in out.values():
        items.sort(key=lambda e: float(e["start"]))
    return dict(out)


def nominal_backoff(retries: Mapping[str, Any], attempt: int) -> float:
    """Backoff before attempt ``attempt + 1`` without jitter (the collector's formula), seconds."""
    raw = float(retries["initial_backoff_ms"]) * float(retries["backoff_multiplier"]) ** (attempt - 1)
    return min(float(retries["max_backoff_ms"]), raw) / 1000


def retry_checks(
    events: Sequence[Event], retries: Mapping[str, Any], *, failures_per_path: int, interval_s: float
) -> tuple[dict[str, Any], list[Check]]:
    """Paths that fail ``failures_per_path`` times then succeed: attempts and backoff gaps."""
    max_attempts = int(retries["max_attempts"])
    expected = min(failures_per_path + 1, max_attempts)
    jitter_floor = 0.5 if retries.get("jitter", True) else 1.0
    by_path = attempts_by_path(events)
    gaps: list[dict[str, Any]] = []
    checks: list[Check] = []
    for path, items in sorted(by_path.items()):
        checks.append(check(f"{path}: attempts", len(items), "==", expected))
        for k in range(1, len(items)):
            gap = float(items[k]["start"]) - float(items[k - 1]["start"])
            nominal = nominal_backoff(retries, k)
            gaps.append({"path": path, "attempt": k + 1, "gap_s": gap, "nominal_backoff_s": nominal})
            checks.append(
                check(
                    f"{path}: gap before attempt {k + 1}, s",
                    gap,
                    ">=",
                    round(nominal * jitter_floor - 0.05, 3),
                )
            )
            checks.append(
                check(
                    f"{path}: gap before attempt {k + 1} bounded, s",
                    gap,
                    "<=",
                    round(nominal + interval_s + 2.0, 3),
                    "warning",
                )
            )
    return {"paths": len(by_path), "expected_attempts": expected, "gaps": gaps}, checks
