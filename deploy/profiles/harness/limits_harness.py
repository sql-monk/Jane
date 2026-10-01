"""Limits harness of WP-14: measures a Jane stack against a profile and deploy/profiles/thresholds.json.

    uv run --all-packages python deploy/profiles/harness/limits_harness.py plan --profile dev-laptop
    uv run --all-packages python deploy/profiles/harness/limits_harness.py run --profile dev-laptop
    uv run --all-packages python deploy/profiles/harness/limits_harness.py evaluate .jane/limits/<run dir>

``run`` starts an isolated stack (deploy/profiles/stack.py, compose profile ``limits-probe``), refuses to
measure on a busy Docker host (foreign containers; ``--allow-busy`` marks the result as not valid for
acceptance), runs the scenarios ``--repeat`` times (workers restarted between repetitions), samples
``docker stats`` all the time, writes the raw data and the verdicts, and removes the stack unless ``--keep``.

Output: ``.jane/limits/<profile>-<UTC time>/`` - ``environment.json`` (host, Docker, Git SHA, profile digest),
``raw/*.jsonl|json`` (probe request log, collector/runtime responses, docker samples), ``results.json``,
``summary.md``. No credentials are written. Scenarios (docs/operations/limits-validation.md):

    L1 rate          request rate and gaps to one host, one collection (web-collector, profile via LIMITS_FILE)
    L2 shared-host   the same, two concurrent collections of one host (the platform promise is per host)
    L3 parallel      requests in flight to one host (slow pages) <= concurrency.max_parallel_fetches_per_host
    L4 retries       5xx then success, 429 + Retry-After, request timeout: attempts and backoff gaps
    L5 backpressure  queue.max_unacked_materials pauses fetching until the consumer acknowledges
    L6 sandbox       cold start vs sandbox.wall_time_ms, wall time and memory enforcement, parallel sandboxes
    L7 resources     peak memory of the stack, OOM kills and restarts (docker stats / inspect)
    L8 e2e           examples/jane_examples.py demo: catalog + scheduled price check durations and effects
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import json
import math
import platform
import shutil
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROFILES_DIR = HERE.parent
ROOT = PROFILES_DIR.parents[1]
for extra in (PROFILES_DIR, ROOT / "examples"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

import metrics as m  # noqa: E402 - sibling module of this script
import stack as jane_stack  # noqa: E402 - deploy/profiles/stack.py

THRESHOLDS = PROFILES_DIR / "thresholds.json"
PROBE_PACKAGE = HERE / "packages" / "harness.sandbox-probe"
OUT_ROOT = ROOT / ".jane" / "limits"
PROBE_HOST = "probe-site:8080"  # as the services see the probe site inside the compose network
SCENARIOS = ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8")
TITLES = {
    "startup": "stack startup",
    "L1": "rate: one collection, one host",
    "L2": "rate: two collections, one host",
    "L3": "parallel requests per host",
    "L4": "retries, Retry-After, request timeout",
    "L5": "backpressure (unacknowledged materials)",
    "L6": "sandbox: cold start, wall time, memory, parallel sandboxes",
    "L7": "resources of the stack",
    "L8": "end to end: catalog + scheduled price check",
}
RESTART_BETWEEN = ("web-collector", "handler-runtime", "orchestrator")


# ============================================================================================ inputs
def examples() -> Any:
    """``examples/jane_examples.py`` (client, publication and the catalog/price-check scenario)."""
    return importlib.import_module("jane_examples")


def load_profile(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(jane_stack.profile_path(name).read_text(encoding="utf-8"))
    return data


def load_thresholds(name: str) -> dict[str, Any]:
    data = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    if name not in data:
        raise SystemExit(
            f"no thresholds for profile {name!r} in {THRESHOLDS.name} (have: {', '.join(k for k in data if k != 'comment')})"
        )
    th: dict[str, Any] = data[name]
    return th


def plan(profile_name: str) -> dict[str, Any]:
    """What ``run`` will measure, with the profile values and thresholds (no Docker needed)."""
    d = load_profile(profile_name)["defaults"]
    th = load_thresholds(profile_name)
    interval = m.request_interval(d["rate"])
    timeout_s = d["timeouts"]["request_timeout_ms"] / 1000
    wall_s = d["sandbox"]["wall_time_ms"] / 1000
    steps = {
        "L1": f"{th['rate']['pages']} pages, start gap >= {interval:.3f} s (tolerance), <= {math.ceil(1 / interval) + 1 if interval else '-'} starts in any 1 s",
        "L2": f"2 x {th['shared_host']['pages_per_collection']} pages of one host at once, same per-host bounds as L1",
        "L3": f"{th['parallel']['pages']} pages answering after {th['parallel']['slow_ms']} ms, in flight <= {d['concurrency']['max_parallel_fetches_per_host']}",
        "L4": f"{th['retries']['flaky_pages']} pages failing {th['retries']['failures_per_path']}x then 200, 429 Retry-After {th['retries']['retry_after_s']} s, "
        f"timeout page {timeout_s + th['retries']['timeout_extra_ms'] / 1000:.0f} s vs request_timeout {timeout_s:.0f} s x {d['retries']['max_attempts']} attempts",
        "L5": f"{th['backpressure']['pages']} pages, max_unacked {th['backpressure']['max_unacked']}, hold {th['backpressure']['hold_s']} s",
        "L6": f"{th['sandbox']['cold_starts']} cold starts p95 <= {th['sandbox']['cold_start_p95_max_fraction_of_wall_time']} x {wall_s:.0f} s, "
        f"sleep {wall_s + 5:.0f} s -> timeout, alloc {d['sandbox']['memory_mb'] + th['sandbox']['memory_overshoot_mb']} MB -> resource_exceeded, "
        f"{2 * d['concurrency']['max_parallel_invocations']} parallel -> <= {d['concurrency']['max_parallel_invocations']} sandboxes",
        "L7": f"docker stats every {th['resources']['sample_interval_s']} s, total peak <= {th['resources']['memory_total_peak_mib']} MiB, no OOM/restarts",
        "L8": f"catalog <= {th['e2e']['catalog_run_max_s']} s, price check <= {th['e2e']['price_check_run_max_s']} s, effects verified",
    }
    estimate = (
        th["rate"]["pages"] * interval
        + 2 * th["shared_host"]["pages_per_collection"] * interval
        + th["parallel"]["pages"]
        * th["parallel"]["slow_ms"]
        / 1000
        / d["concurrency"]["max_parallel_fetches_per_host"]
        + d["retries"]["max_attempts"] * (timeout_s + 2)
        + 30
        + th["backpressure"]["hold_s"]
        + th["backpressure"]["pages"] * 0.05
        + 10
        + th["sandbox"]["cold_starts"] * 10
        + wall_s
        + 20
        + 20
        + 120
    )
    return {
        "profile": profile_name,
        "repeat": th["machine"]["repeat"],
        "scenarios": steps,
        "estimated_minutes_per_repetition": round(estimate / 60, 1),
        "stack_start_minutes": "3-10 (image builds; faster when cached)",
    }


# ============================================================================================ helpers
def now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_cmd(cmd: Sequence[str], timeout: float = 120) -> str:
    r = subprocess.run(  # noqa: S603 - fixed docker/git command lines of this module
        list(cmd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    return r.stdout


def environment(profile_name: str, project: str) -> dict[str, Any]:
    info_raw = run_cmd(["docker", "info", "--format", "{{json .}}"])
    info = json.loads(info_raw) if info_raw.strip().startswith("{") else {}
    foreign = [
        n
        for n in run_cmd(["docker", "ps", "--format", "{{.Names}}"]).split()
        if not n.startswith(f"{project}-")
    ]
    profile_file = jane_stack.profile_path(profile_name)
    return {
        "measured_at": now_utc(),
        "git_sha": run_cmd(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).strip(),
        "git_dirty": bool(run_cmd(["git", "-C", str(ROOT), "status", "--porcelain"]).strip()),
        "host": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
        "docker": {
            k: info.get(k) for k in ("ServerVersion", "OperatingSystem", "KernelVersion", "NCPU", "MemTotal")
        },
        "profile": profile_name,
        "profile_sha256": hashlib.sha256(profile_file.read_bytes()).hexdigest(),
        "thresholds_sha256": hashlib.sha256(THRESHOLDS.read_bytes()).hexdigest(),
        "project": project,
        "foreign_containers": len(foreign),
    }


class ResourceSampler(threading.Thread):
    """``docker stats`` of the project containers (and its sandboxes) every ``interval_s`` seconds."""

    def __init__(self, project: str, interval_s: float, out: Path) -> None:
        super().__init__(daemon=True)
        self.project, self.interval_s, self.out = project, interval_s, out
        self.stop_event = threading.Event()
        self.rows: list[dict[str, Any]] = []

    def run(self) -> None:
        while not self.stop_event.is_set():
            ts = time.time()
            label = f"label={jane_stack.SANDBOX_LABEL}={self.project}"
            sandboxes = set(run_cmd(["docker", "ps", "--filter", label, "--format", "{{.Names}}"]).split())
            raw = run_cmd(["docker", "stats", "--no-stream", "--format", "{{json .}}"], timeout=60)
            for line in raw.splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                name = str(row.get("Name", ""))
                if name.startswith(f"{self.project}-") or name in sandboxes:
                    self.rows.append(
                        {"t": ts, "name": name, "mem": row.get("MemUsage"), "cpu": row.get("CPUPerc")}
                    )
            self.stop_event.wait(self.interval_s)

    def finish(self) -> list[dict[str, Any]]:
        self.stop_event.set()
        self.join(timeout=120)
        write_jsonl(self.out, self.rows)
        return self.rows


def parse_mib(value: str | None) -> float | None:
    """``"123.4MiB / 15.6GiB"`` -> 123.4."""
    if not value:
        return None
    used = value.split("/", 1)[0].strip()
    units = {
        "KiB": 1 / 1024,
        "MiB": 1.0,
        "GiB": 1024.0,
        "B": 1 / 1024 / 1024,
        "kB": 1 / 1024,
        "MB": 1.0,
        "GB": 1024.0,
    }
    for unit in sorted(units, key=len, reverse=True):
        if used.endswith(unit):
            try:
                return float(used[: -len(unit)]) * units[unit]
            except ValueError:
                return None
    return None


def runtime_profile_checks(info: Mapping[str, Any], profile_name: str, cap: int) -> list[m.Check]:
    """L6 warnings from handler-runtime ``GET /v1/info``: ``limits`` there is a ``PlatformLimits`` document
    (WP-00 ``ServiceInfo``; values under ``defaults``). The runtime must run with the profile of the stack
    (its ``LIMITS_FILE``), so its own ``max_parallel_invocations`` is the profile's."""
    limits = info.get("limits") or {}
    defaults = limits.get("defaults") or {}
    service_cap = (defaults.get("concurrency") or {}).get("max_parallel_invocations")
    return [
        m.check("runtime limits profile = profile", limits.get("profile"), "==", profile_name, "warning"),
        m.check("runtime max_parallel_invocations = profile", service_cap, "==", cap, "warning"),
    ]


# ============================================================================================ scenarios
class Harness:
    """Scenarios against one stack. ``urls``/``probe_host``/``profile``/``thresholds`` default to the stack
    file of ``project`` and the files of this directory (the self-test passes a local collector and probe)."""

    def __init__(
        self,
        profile_name: str,
        project: str,
        out: Path,
        *,
        repetition: int = 1,
        urls: Mapping[str, str] | None = None,
        probe_host: str = PROBE_HOST,
        profile: Mapping[str, Any] | None = None,
        thresholds: Mapping[str, Any] | None = None,
    ) -> None:
        api = examples().Api  # the contract-validating client of the examples

        self.profile_name = profile_name
        self.profile = dict(profile) if profile is not None else load_profile(profile_name)
        self.d = self.profile["defaults"]
        self.th = dict(thresholds) if thresholds is not None else load_thresholds(profile_name)
        self.project = project
        self.out = out
        self.repetition = repetition
        self.urls = dict(urls) if urls is not None else jane_stack.service_urls(project)
        self.probe_host = probe_host
        self.collector = api(self.urls["web-collector"], "collector")
        self.runtime: Any = (
            api(self.urls["handler-runtime"], "handler") if "handler-runtime" in self.urls else None
        )
        self.probe_url = self.urls["probe-site"]

    def raw(self, name: str) -> Path:
        return self.out / "raw" / f"r{self.repetition}-{name}"

    # ------------------------------------------------------------------ probe site
    def probe_reset(self, ns: str) -> None:
        import httpx

        httpx.post(f"{self.probe_url}/_probe/reset", params={"ns": ns}, timeout=10).raise_for_status()

    def probe_events(self, ns: str) -> list[dict[str, Any]]:
        import httpx

        r = httpx.get(f"{self.probe_url}/_probe/log", params={"ns": ns}, timeout=30)
        r.raise_for_status()
        events: list[dict[str, Any]] = r.json()["events"]
        return events

    # ------------------------------------------------------------------ collector
    def collect(
        self, ns: str, paths: Sequence[str], limits: Mapping[str, Any] | None = None, *, consume: bool = True
    ) -> str:
        urls = [f"http://{self.probe_host}/s/{ns}/{p}" for p in paths]
        rules = {
            "collector": "web",
            "scope": {"allowed_domains": [self.probe_host.split(":", 1)[0]], "allowed_schemes": ["http"]},
            "strategies": [{"type": "seed_list", "strategy_id": "seeds", "urls": urls}],
            "robots": {"mode": "respect"},
        }
        body: dict[str, Any] = {
            "source_kind": "web",
            "source_id": f"harness-{ns}",
            "state_key": f"harness-{ns}-{uuid.uuid4().hex[:8]}",
            "rules": rules,
            "urls": urls,
            "mode": "full",
        }
        if limits:
            body["limits"] = dict(limits)
        r = self.collector.call(
            "POST", "/v1/collections", ok=(202,), json=body, headers={"Idempotency-Key": uuid.uuid4().hex}
        )
        return str(r.json()["job_id"])

    def drain(self, collection_id: str, timeout_s: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        materials: list[dict[str, Any]] = []
        after: str | None = None
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            params: dict[str, Any] = {"wait_ms": 2000, **({"after": after} if after else {})}
            page = self.collector.call(
                "GET", f"/v1/collections/{collection_id}/materials", params=params
            ).json()
            materials.extend(page["items"])
            after = page.get("next_cursor") or after
            if page["end_of_stream"]:
                view = self.collector.call("GET", f"/v1/collections/{collection_id}").json()
                return materials, view
        raise TimeoutError(f"collection {collection_id} did not finish in {timeout_s:.0f}s")

    def errors(self, collection_id: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = self.collector.call(
            "GET", f"/v1/collections/{collection_id}/errors", params={"limit": 500}
        ).json()["items"]
        return items

    def collection_timeout(self, pages: int) -> float:
        interval = m.request_interval(self.d["rate"])
        return 300 + pages * interval * 3

    # ------------------------------------------------------------------ L1 / L2
    def l1_rate(self) -> dict[str, Any]:
        n = int(self.th["rate"]["pages"])
        self.probe_reset("l1")
        cid = self.collect("l1", [f"p/{i}" for i in range(n)])
        materials, view = self.drain(cid, self.collection_timeout(n))
        events = self.probe_events("l1")
        write_jsonl(self.raw("L1-probe.jsonl"), events)
        write_json(self.raw("L1-collection.json"), view)
        return self.evaluate_rate("L1", events, view, n, len(materials))

    def evaluate_rate(
        self, sid: str, events: Sequence[Mapping[str, Any]], view: Mapping[str, Any], n: int, emitted: int
    ) -> dict[str, Any]:
        rate = (view.get("effective_limits") or {}).get("rate") or self.d["rate"]
        metrics, checks = m.rate_checks(events, rate, self.th["rate"], expected=n)
        checks.append(m.check("collection status", view.get("status"), "==", "succeeded"))
        checks.append(m.check("materials emitted", emitted, "==", n))
        checks.append(
            m.check(
                "effective rate = profile",
                rate.get("requests_per_second_per_host"),
                "==",
                self.d["rate"]["requests_per_second_per_host"],
                "warning",
            )
        )
        return {"id": sid, "metrics": metrics | {"effective_rate": rate}, "checks": checks}

    def l2_shared_host(self) -> dict[str, Any]:
        n = int(self.th["shared_host"]["pages_per_collection"])
        for ns in ("l2a", "l2b"):
            self.probe_reset(ns)
        ids = [self.collect(ns, [f"p/{i}" for i in range(n)]) for ns in ("l2a", "l2b")]
        results: list[tuple[list[dict[str, Any]], dict[str, Any]]] = []
        done: dict[str, Any] = {}

        def worker(cid: str) -> None:
            done[cid] = self.drain(cid, self.collection_timeout(2 * n))

        threads = [threading.Thread(target=worker, args=(cid,)) for cid in ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        results = [done[cid] for cid in ids]
        events = self.probe_events("l2a") + self.probe_events("l2b")
        write_jsonl(self.raw("L2-probe.jsonl"), events)
        write_json(self.raw("L2-collections.json"), [v for _, v in results])
        rate = self.d["rate"]
        metrics, checks = m.rate_checks(events, rate, self.th["rate"], expected=2 * n)
        for _, view in results:
            checks.append(m.check("collection status", view.get("status"), "==", "succeeded"))
        return {
            "id": "L2",
            "metrics": metrics,
            "checks": checks,
            "note": "per-host politeness across concurrent collections",
        }

    # ------------------------------------------------------------------ L3
    def l3_parallel(self) -> dict[str, Any]:
        n, slow = int(self.th["parallel"]["pages"]), int(self.th["parallel"]["slow_ms"])
        self.probe_reset("l3")
        fast = {"rate": {"requests_per_second_per_host": 1000, "min_delay_ms_per_host": 0}}
        cid = self.collect("l3", [f"slow/{i}?ms={slow}" for i in range(n)], fast)
        materials, view = self.drain(cid, 300 + n * slow / 1000)
        events = self.probe_events("l3")
        write_jsonl(self.raw("L3-probe.jsonl"), events)
        write_json(self.raw("L3-collection.json"), view)
        per_host = int(
            ((view.get("effective_limits") or {}).get("concurrency") or self.d["concurrency"])[
                "max_parallel_fetches_per_host"
            ]
        )
        inflight = m.max_concurrency(events)
        checks = [
            m.check("requests in flight to one host", inflight, "<=", per_host),
            m.check("parallelism is used", inflight, ">=", per_host, "warning"),
            m.check(
                "effective per-host parallelism = profile",
                per_host,
                "==",
                self.d["concurrency"]["max_parallel_fetches_per_host"],
                "warning",
            ),
            m.check("materials emitted", len(materials), "==", n),
        ]
        return {
            "id": "L3",
            "metrics": {"max_in_flight": inflight, "limit": per_host, "requests": len(events)},
            "checks": checks,
        }

    # ------------------------------------------------------------------ L4
    def l4_retries(self) -> dict[str, Any]:
        th, d = self.th["retries"], self.d
        interval = m.request_interval(d["rate"])
        timeout_ms = int(d["timeouts"]["request_timeout_ms"])
        checks: list[m.Check] = []
        metrics: dict[str, Any] = {}
        # (a) 503 then success
        self.probe_reset("l4a")
        fails = int(th["failures_per_path"])
        cid = self.collect(
            "l4a", [f"flaky/{i}?fail={fails}&status=503" for i in range(int(th["flaky_pages"]))]
        )
        materials, _ = self.drain(cid, 600)
        ev_a = self.probe_events("l4a")
        write_jsonl(self.raw("L4a-probe.jsonl"), ev_a)
        ma, ca = m.retry_checks(ev_a, d["retries"], failures_per_path=fails, interval_s=interval)
        metrics["flaky"] = ma
        checks += ca
        if int(d["retries"]["max_attempts"]) > fails:
            checks.append(
                m.check("flaky pages finally fetched", len(materials), "==", int(th["flaky_pages"]))
            )
        # (b) 429 + Retry-After
        self.probe_reset("l4b")
        wait_s = int(th["retry_after_s"])
        cid = self.collect("l4b", [f"limited/0?fail=1&retry_after={wait_s}"])
        self.drain(cid, 300)
        ev_b = sorted(self.probe_events("l4b"), key=lambda e: e["start"])
        write_jsonl(self.raw("L4b-probe.jsonl"), ev_b)
        gap_b = ev_b[1]["start"] - ev_b[0]["start"] if len(ev_b) > 1 else None
        metrics["retry_after_gap_s"] = gap_b
        checks.append(m.check("429: attempts", len(ev_b), "==", 2))
        checks.append(m.check("429: waits Retry-After, s", gap_b, ">=", wait_s - 0.05))
        # (c) request timeout
        self.probe_reset("l4c")
        slow_ms = timeout_ms + int(th["timeout_extra_ms"])
        cid = self.collect("l4c", [f"slow/0?ms={slow_ms}"])
        self.drain(cid, d["retries"]["max_attempts"] * (slow_ms / 1000 + 60) + 120)
        errs = self.errors(cid)
        ev_c = sorted(self.probe_events("l4c"), key=lambda e: e["start"])
        write_jsonl(self.raw("L4c-probe.jsonl"), ev_c)
        write_json(self.raw("L4c-errors.json"), errs)
        gaps_c = m.start_gaps(ev_c)
        metrics["timeout"] = {
            "attempts": len(ev_c),
            "gaps_s": gaps_c,
            "errors": [e.get("code") for e in errs],
        }
        checks.append(m.check("timeout: attempts", len(ev_c), "==", int(d["retries"]["max_attempts"])))
        if gaps_c:
            checks.append(
                m.check(
                    "timeout: attempt not shorter than request_timeout, s",
                    min(gaps_c),
                    ">=",
                    round(timeout_ms / 1000 * 0.95, 3),
                )
            )
            bound = timeout_ms / 1000 + m.nominal_backoff(d["retries"], len(ev_c)) + interval + 5
            checks.append(
                m.check(
                    "timeout: attempt ends near request_timeout, s",
                    max(gaps_c),
                    "<=",
                    round(bound, 3),
                    "warning",
                )
            )
        checks.append(
            m.check(
                "timeout: reported as source_unavailable",
                "source_unavailable" in [e.get("code") for e in errs],
                "==",
                True,
            )
        )
        return {"id": "L4", "metrics": metrics, "checks": checks}

    # ------------------------------------------------------------------ L5
    def l5_backpressure(self) -> dict[str, Any]:
        th = self.th["backpressure"]
        n, cap, hold = int(th["pages"]), int(th["max_unacked"]), float(th["hold_s"])
        self.probe_reset("l5")
        limits = {
            "queue": {"max_unacked_materials": cap},
            "rate": {"requests_per_second_per_host": 1000, "min_delay_ms_per_host": 0},
        }
        cid = self.collect("l5", [f"p/{i}" for i in range(n)], limits)
        # Nobody consumes: wait (at most hold_s) until the collector pauses, let admitted fetches settle,
        # then count what reached the site.
        deadline = time.monotonic() + hold
        while time.monotonic() < deadline:
            if self.collector.call("GET", f"/v1/collections/{cid}").json().get("paused_by_backpressure"):
                break
            time.sleep(0.2)
        time.sleep(min(2.0, hold / 4))
        view_hold = self.collector.call("GET", f"/v1/collections/{cid}").json()
        fetched_hold = len(self.probe_events("l5"))
        materials, view = self.drain(cid, 600)
        events = self.probe_events("l5")
        write_jsonl(self.raw("L5-probe.jsonl"), events)
        write_json(self.raw("L5-collection.json"), {"hold": view_hold, "final": view})
        parallel = int(self.d["concurrency"]["max_parallel_fetches"])
        stats = view_hold.get("stats") or {}
        checks = [
            m.check("fetched while nobody consumes", fetched_hold, "<=", cap + parallel),
            # the check runs before each fetch, so fetches already admitted may finish past the cap
            m.check("unacked while nobody consumes", stats.get("unacked"), "<=", cap + parallel - 1),
            m.check("unacked within the cap itself", stats.get("unacked"), "<=", cap, "warning"),
            m.check("paused_by_backpressure", view_hold.get("paused_by_backpressure"), "==", True),
            m.check("all materials after the consumer resumes", len(materials), "==", n),
            m.check("collection status", view.get("status"), "==", "succeeded"),
        ]
        profile_cap = ((view.get("effective_limits") or {}).get("queue") or {}).get("max_unacked_materials")
        return {
            "id": "L5",
            "metrics": {
                "fetched_during_hold": fetched_hold,
                "stats_during_hold": stats,
                "requested_cap": cap,
                "profile_cap": self.d["queue"]["max_unacked_materials"],
                "effective_cap": profile_cap,
            },
            "checks": checks,
        }

    # ------------------------------------------------------------------ L6
    def invocation(self, params: Mapping[str, Any], *, mode: str = "sync") -> dict[str, Any]:
        from jane_registry.archive import canonical_archive, digest_of, files_from_dir

        archive = canonical_archive(files_from_dir(PROBE_PACKAGE))
        sha = hashlib.sha256(archive).hexdigest()
        html = b"<!doctype html><html><body><p>probe</p></body></html>"
        material = {
            "material_id": "web:" + uuid.uuid4().hex,
            "observation_id": "obs_" + uuid.uuid4().hex,
            "source": {"source_id": "harness", "kind": "web"},
            "locator": {"url": f"http://{self.probe_host}/s/l6/p/0"},
            "fetched_at": now_utc(),
            "format": {"media_type": "text/html", "charset": "utf-8", "content_kind": "page"},
            "revision": {"content_sha256": hashlib.sha256(html).hexdigest()},
            "content": {
                "kind": "inline",
                "media_type": "text/html",
                "encoding": "utf-8",
                "data": html.decode(),
                "size_bytes": len(html),
                "sha256": hashlib.sha256(html).hexdigest(),
            },
            "collector": {"name": "limits-harness", "version": "1"},
        }
        return {
            "handler": {
                "package_id": "harness.sandbox-probe",
                "version": "1.0.0",
                "digest": digest_of(archive),
            },
            "package_archive": {
                "kind": "inline",
                "media_type": "application/zip",
                "encoding": "base64",
                "data": base64.b64encode(archive).decode(),
                "size_bytes": len(archive),
                "sha256": sha,
            },
            "params": dict(params),
            "inputs": [{"kind": "material", "material": material}],
            "context": {"trace": {"run_id": "run_harness", "stage_id": "sandbox-probe"}},
            "delivery": {"delivery_key": uuid.uuid4().hex},
            "mode": mode,
            # As the orchestrator does: the profile reaches the runtime in every request.
            "limits": {
                "sandbox": self.d["sandbox"],
                "timeouts": {
                    k: v
                    for k, v in self.d["timeouts"].items()
                    if k in {"invocation_timeout_ms", "sync_response_max_ms"}
                },
            },
        }

    def invoke(self, body: Mapping[str, Any], timeout_s: float) -> tuple[float, dict[str, Any]]:
        start = time.monotonic()
        r = self.runtime.call(
            "POST",
            "/v1/invocations",
            ok=(200, 202),
            json=body,
            headers={"Idempotency-Key": body["delivery"]["delivery_key"]},
        )
        if r.status_code == 202:
            job_id = r.json()["job_id"]
            deadline = time.monotonic() + timeout_s
            while True:
                job = self.runtime.call("GET", f"/v1/jobs/{job_id}").json()
                if job["status"] in {"succeeded", "failed", "cancelled"}:
                    result = dict(job.get("result") or {"status": "failed", "failure": job.get("error")})
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError(f"invocation job {job_id} still {job['status']}")
                time.sleep(0.25)
        else:
            result = dict(r.json())
        return time.monotonic() - start, result

    def l6_sandbox(self) -> dict[str, Any]:
        th, sb = self.th["sandbox"], self.d["sandbox"]
        wall_s = sb["wall_time_ms"] / 1000
        rows: list[dict[str, Any]] = []
        checks: list[m.Check] = []
        cold: list[float] = []
        for _ in range(int(th["cold_starts"])):
            elapsed, result = self.invoke(self.invocation({"sleep_ms": 0}), wall_s + 120)
            cold.append(elapsed)
            rows.append(
                {
                    "case": "cold",
                    "elapsed_s": elapsed,
                    "status": result.get("status"),
                    "failure": result.get("failure"),
                }
            )
        checks.append(
            m.check(
                "cold start: all empty (no timeouts)",
                sum(r["status"] == "empty" for r in rows),
                "==",
                len(cold),
            )
        )
        p95 = m.percentile(cold, 95)
        checks.append(
            m.check(
                "cold start p95, s",
                p95,
                "<=",
                round(wall_s * float(th["cold_start_p95_max_fraction_of_wall_time"]), 2),
            )
        )
        elapsed, result = self.invoke(self.invocation({"sleep_ms": sb["wall_time_ms"] + 5000}), wall_s + 180)
        rows.append(
            {
                "case": "wall_time",
                "elapsed_s": elapsed,
                "status": result.get("status"),
                "failure": result.get("failure"),
            }
        )
        checks.append(
            m.check(
                "wall time exceeded -> failure.kind",
                (result.get("failure") or {}).get("kind"),
                "==",
                "timeout",
            )
        )
        checks.append(
            m.check("wall time enforced within, s", elapsed, "<=", round(wall_s + 30, 1), "warning")
        )
        alloc = int(sb["memory_mb"]) + int(th["memory_overshoot_mb"])
        elapsed, result = self.invoke(self.invocation({"alloc_mb": alloc}), wall_s + 120)
        rows.append(
            {
                "case": "memory",
                "elapsed_s": elapsed,
                "status": result.get("status"),
                "failure": result.get("failure"),
            }
        )
        checks.append(
            m.check(
                "memory exceeded -> failure.kind",
                (result.get("failure") or {}).get("kind"),
                "==",
                "resource_exceeded",
            )
        )
        # parallel sandboxes: count running containers with the stack's sandbox label while jobs run
        cap = int(self.d["concurrency"]["max_parallel_invocations"])
        info = self.runtime.call("GET", "/v1/info").json()
        profile_checks = runtime_profile_checks(info, self.profile_name, cap)
        bodies = [
            self.invocation({"sleep_ms": int(th["parallel_sleep_ms"])}, mode="async") for _ in range(2 * cap)
        ]
        samples: list[int] = []
        results: list[dict[str, Any]] = []

        def one(body: Mapping[str, Any]) -> None:
            results.append(self.invoke(body, wall_s + 300)[1])

        threads = [threading.Thread(target=one, args=(b,)) for b in bodies]
        for t in threads:
            t.start()
        while any(t.is_alive() for t in threads):
            out = run_cmd(
                ["docker", "ps", "-q", "--filter", f"label={jane_stack.SANDBOX_LABEL}={self.project}"],
                timeout=30,
            )
            samples.append(len(out.split()))
            time.sleep(0.25)
        for t in threads:
            t.join()
        rows.append({"case": "parallel", "samples": samples, "statuses": [r.get("status") for r in results]})
        checks.append(m.check("parallel sandboxes", max(samples or [0]), "<=", cap))
        checks += profile_checks
        checks.append(
            m.check(
                "parallel invocations finished",
                sum(r.get("status") == "empty" for r in results),
                "==",
                len(bodies),
            )
        )
        write_jsonl(self.raw("L6-runtime.jsonl"), rows)
        return {
            "id": "L6",
            "metrics": {
                "cold_start_s": cold,
                "cold_start_p95_s": p95,
                "max_parallel_sandboxes": max(samples or [0]),
                "runtime_profile": profile_checks[0]["value"],
                "runtime_service_cap": profile_checks[1]["value"],
            },
            "checks": checks,
        }

    # ------------------------------------------------------------------ L8
    def l8_e2e(self) -> dict[str, Any]:
        ex = examples()
        svc = ex.Services.of_project(self.project)
        t: dict[str, float | None] = {}
        try:
            ex.publish(svc)
            ex.apply(svc)
            catalog = ex.catalog(svc, 900)
            t["catalog_s"] = _duration(catalog)
            price = ex.price_check(svc, 10, 600)
            t["price_check_s"] = _duration(price)
            result = ex.verify(svc, catalog, price)
        finally:
            svc.close()
        write_json(self.raw("L8-examples.json"), {"catalog": catalog, "price_check": price, "verify": result})
        th = self.th["e2e"]
        checks = [
            m.check("examples verified", result["ok"], "==", True),
            m.check("catalog run, s", t["catalog_s"], "<=", th["catalog_run_max_s"], "warning"),
            m.check("price-check run, s", t["price_check_s"], "<=", th["price_check_run_max_s"], "warning"),
        ]
        return {"id": "L8", "metrics": t | {"failures": result["failures"]}, "checks": checks}


def _duration(run: Mapping[str, Any]) -> float | None:
    try:
        a = datetime.fromisoformat(str(run["started_at"]).replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(run["finished_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return None
    return round((b - a).total_seconds(), 1)


def resources_result(
    rows: Sequence[Mapping[str, Any]], project: str, th: Mapping[str, Any]
) -> dict[str, Any]:
    by_time: dict[float, float] = {}
    peak: dict[str, float] = {}
    for r in rows:
        mib = parse_mib(r.get("mem"))
        if mib is None:
            continue
        by_time[float(r["t"])] = by_time.get(float(r["t"]), 0.0) + mib
        peak[str(r["name"])] = max(peak.get(str(r["name"]), 0.0), mib)
    names = run_cmd(
        ["docker", "ps", "-a", "-q", "--filter", f"label=com.docker.compose.project={project}"]
    ).split()
    oom, restarts = 0, 0
    for cid in names:
        state = json.loads(run_cmd(["docker", "inspect", "--format", "{{json .}}", cid]) or "{}")
        oom += bool((state.get("State") or {}).get("OOMKilled"))
        restarts += int(state.get("RestartCount") or 0)
    total = max(by_time.values()) if by_time else None
    checks = [
        m.check("samples collected", len(rows), ">=", 1),
        m.check(
            "total memory peak, MiB",
            round(total, 1) if total is not None else None,
            "<=",
            th["memory_total_peak_mib"],
        ),
        m.check("OOM-killed containers", oom, "==", 0),
        m.check("container restarts", restarts, "==", 0),
    ]
    return {
        "id": "L7",
        "metrics": {
            "peak_mib_by_container": {k: round(v, 1) for k, v in sorted(peak.items())},
            "total_peak_mib": total,
        },
        "checks": checks,
    }


# ============================================================================================ report
def summarize(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per: list[dict[str, Any]] = []
    for r in results:
        per.append(
            {
                "id": r["id"],
                "repetition": r.get("repetition", 1),
                "title": TITLES.get(str(r["id"]), ""),
                "verdict": r.get("verdict") or m.verdict(r.get("checks") or []),
                "error": r.get("error"),
            }
        )
    blockers = [p for p in per if p["verdict"] in {"fail", "error"}]
    return {
        "verdict": "fail" if blockers else ("warn" if any(p["verdict"] == "warn" for p in per) else "pass"),
        "scenarios": per,
    }


def markdown(env: Mapping[str, Any], results: Sequence[Mapping[str, Any]], summary: Mapping[str, Any]) -> str:
    lines = [
        f"# Limits harness: {env['profile']} ({env['measured_at']})",
        "",
        f"Git `{env['git_sha']}` (dirty: {env['git_dirty']}), Docker {env['docker'].get('ServerVersion')} "
        f"on {env['docker'].get('OperatingSystem')}, {env['docker'].get('NCPU')} CPU, "
        f"{round((env['docker'].get('MemTotal') or 0) / 2**30, 1)} GiB; foreign containers: {env['foreign_containers']}.",
        "",
        f"**Verdict: {summary['verdict']}**"
        + (" (NOT valid for acceptance: busy host)" if env.get("busy") else ""),
        "",
        "| Scenario | Rep | Check | Value | Limit | Result |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        if r.get("error"):
            lines.append(
                f"| {r['id']} | {r.get('repetition', 1)} | error | {str(r['error'])[:120]} | | error |"
            )
        for c in r.get("checks") or []:
            result = "ok" if c["ok"] else ("FAIL" if c["severity"] == "blocker" else "warn")
            lines.append(
                f"| {r['id']} | {r.get('repetition', 1)} | {c['name']} | {c['value']} | {c['op']} {c['limit']} | {result} |"
            )
    return "\n".join(lines) + "\n"


def cleanup_failed_start(stack: jane_stack.Stack) -> list[str]:
    """Bound Docker cleanup after a partial ``up``; keep stack metadata if Compose down fails."""
    try:
        stack.compose("--profile", "*", "down", "--remove-orphans", "-v", "--rmi", "local", timeout=180)
    except Exception as exc:
        return [f"compose down: {type(exc).__name__}: {exc}"]
    errors: list[str] = []
    try:
        stack.run(
            ["docker", "image", "rm", "-f", jane_stack.sandbox_image(stack.project)], check=False, timeout=30
        )
    except Exception as exc:
        errors.append(f"sandbox image: {type(exc).__name__}: {exc}")
    for path in (jane_stack.stack_file(stack.project), jane_stack.executors_file(stack.project)):
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
    try:
        shutil.rmtree(jane_stack.recordings_dir(stack.project), ignore_errors=False)
    except FileNotFoundError:
        pass
    except OSError as exc:
        errors.append(f"recordings: {type(exc).__name__}: {exc}")
    return errors


def run(ns: argparse.Namespace) -> int:
    th = load_thresholds(ns.profile)
    project = ns.project or f"jane-limits-{ns.profile}"
    out = OUT_ROOT / f"{ns.profile}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    only = [s.strip() for s in (ns.only or ",".join(SCENARIOS)).split(",") if s.strip()]
    stack = jane_stack.Stack(project, ns.profile)
    env = environment(ns.profile, project)
    env["busy"] = env["foreign_containers"] > int(th["machine"]["max_foreign_containers"])
    if env["busy"] and not ns.allow_busy:
        print(
            f"refusing to measure: {env['foreign_containers']} foreign containers are running (use --allow-busy for a smoke run)",
            file=sys.stderr,
        )
        return 2
    write_json(out / "environment.json", env)
    if not ns.no_up:
        try:
            stack.up([*jane_stack.DEFAULT_SERVICES, "probe-site"])
        except Exception as exc:
            cleanup_errors = cleanup_failed_start(stack)
            reason = f"{type(exc).__name__}: {(str(exc).splitlines() or ['no details'])[0][:300]}"
            startup_result = {
                "id": "startup",
                "repetition": 0,
                "verdict": "error",
                "error": reason,
                "metrics": {"cleanup_errors": cleanup_errors},
            }
            startup_results = [startup_result]
            summary = summarize(startup_results)
            write_json(
                out / "results.json", {"environment": env, "summary": summary, "results": startup_results}
            )
            (out / "summary.md").write_text(markdown(env, startup_results, summary), encoding="utf-8")
            print(f"startup failed: {reason}; cleanup errors: {cleanup_errors}", file=sys.stderr)
            print(f"verdict: {summary['verdict']}   results: {out.relative_to(ROOT).as_posix()}")
            return 1
    sampler = ResourceSampler(
        project, float(th["resources"]["sample_interval_s"]), out / "raw" / "resources.jsonl"
    )
    sampler.start()
    results: list[dict[str, Any]] = []
    try:
        for rep in range(1, int(ns.repeat or th["machine"]["repeat"]) + 1):
            if rep > 1:
                stack.compose("restart", *RESTART_BETWEEN, timeout=600)
                stack.compose("up", "-d", "--wait", *RESTART_BETWEEN, timeout=900)
            harness = Harness(ns.profile, project, out, repetition=rep)
            steps: dict[str, Callable[[], dict[str, Any]]] = {
                "L1": harness.l1_rate,
                "L2": harness.l2_shared_host,
                "L3": harness.l3_parallel,
                "L4": harness.l4_retries,
                "L5": harness.l5_backpressure,
                "L6": harness.l6_sandbox,
                "L8": harness.l8_e2e if rep == 1 else lambda: {"id": "L8", "checks": [], "verdict": "skip"},
            }
            for sid in [s for s in only if s in steps]:
                print(f"[{now_utc()}] repetition {rep}: {sid} {TITLES[sid]}", flush=True)
                try:
                    result = steps[sid]()
                except Exception as exc:  # a scenario error is a result, the others still run
                    result = {
                        "id": sid,
                        "checks": [],
                        "error": f"{type(exc).__name__}: {exc}",
                        "verdict": "error",
                    }
                result["repetition"] = rep
                result.setdefault("verdict", m.verdict(result.get("checks") or []))
                results.append(result)
                print(f"    -> {result['verdict']}", flush=True)
    finally:
        rows = sampler.finish()
        if "L7" in only:
            results.append(resources_result(rows, project, th["resources"]) | {"repetition": 0})
            results[-1]["verdict"] = m.verdict(results[-1]["checks"])
        if not ns.keep and not ns.no_up:
            stack.down()
    summary = summarize(results)
    write_json(out / "results.json", {"environment": env, "summary": summary, "results": results})
    (out / "summary.md").write_text(markdown(env, results, summary), encoding="utf-8")
    print(f"verdict: {summary['verdict']}   results: {out.relative_to(ROOT).as_posix()}")
    return 0 if summary["verdict"] != "fail" else 1


def evaluate(ns: argparse.Namespace) -> int:
    """Re-print the verdicts of a saved run (e.g. after reviewing thresholds)."""
    data = json.loads((Path(ns.run_dir) / "results.json").read_text(encoding="utf-8"))
    summary = summarize(data["results"])
    print(markdown(data["environment"], data["results"], summary))
    return 0 if summary["verdict"] != "fail" else 1


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(
        prog="limits_harness.py", description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan", help="print what will be measured (no Docker)")
    p.add_argument("--profile", default="dev-laptop", choices=["dev-laptop", "ci"])
    p = sub.add_parser("run", help="measure (needs a free Docker host)")
    p.add_argument("--profile", default="dev-laptop", choices=["dev-laptop", "ci"])
    p.add_argument("--project", default=None, help="compose project (default jane-limits-<profile>)")
    p.add_argument("--only", default=None, help=f"comma list of {','.join(SCENARIOS)}")
    p.add_argument("--repeat", type=int, default=None, help="repetitions (default from thresholds.json)")
    p.add_argument("--keep", action="store_true", help="keep the stack after the run")
    p.add_argument("--no-up", action="store_true", help="use an already running stack (started with --probe)")
    p.add_argument(
        "--allow-busy",
        action="store_true",
        help="measure on a busy host; the result is not valid for acceptance",
    )
    p = sub.add_parser("evaluate", help="summarize a saved run")
    p.add_argument("run_dir")
    ns = ap.parse_args(argv)
    if ns.command == "plan":
        print(json.dumps(plan(ns.profile), ensure_ascii=False, indent=2))
        return 0
    if ns.command == "run":
        return run(ns)
    return evaluate(ns)


if __name__ == "__main__":
    sys.exit(main())
