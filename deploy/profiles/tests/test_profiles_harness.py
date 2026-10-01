"""Profiles, the profile stack and the limits harness without Docker: metrics, probe site, thresholds.

Run: ``uv run --all-packages pytest deploy/profiles -q``. The measurements themselves need a free Docker host
(``limits_harness.py run``, docs/operations/limits-validation.md) and are not part of these tests.
"""

from __future__ import annotations

import argparse
import importlib
import json
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import check as profile_check
import httpx
import limits_harness as lh
import metrics as m
import probe_site
import pytest
import stack as jane_stack
import yaml

from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

PROFILES = Path(__file__).resolve().parents[1]
MEASURED = ("dev-laptop", "ci")


def ev(start: float, end: float | None = None, path: str = "/s/t/p/1", status: int = 200) -> dict[str, Any]:
    return {"start": start, "end": start + 0.01 if end is None else end, "path": path, "status": status}


# ------------------------------------------------------------------------------------------ profiles
def test_profiles_are_valid_platform_limits(capsys: pytest.CaptureFixture[str]) -> None:
    profile_check.main()
    out = capsys.readouterr().out
    assert out.count("schema valid") == 3


def test_every_measured_profile_has_complete_thresholds() -> None:
    data = json.loads((PROFILES / "thresholds.json").read_text(encoding="utf-8"))
    keys = {k: set(v) for k, v in data["dev-laptop"].items()}
    for name in MEASURED:
        assert {k: set(v) for k, v in data[name].items()} == keys, name
        plan = lh.plan(name)
        assert set(plan["scenarios"]) == set(lh.SCENARIOS)
        assert plan["estimated_minutes_per_repetition"] > 0


@pytest.mark.parametrize("cleanup_fails", [False, True])
def test_harness_reports_startup_failure_and_bounded_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, cleanup_fails: bool
) -> None:
    """Run the real harness orchestration with a failing Stack boundary, without Docker."""
    project = "jane-limits-startup-test"
    stack_file = tmp_path / "stack.json"
    executors_file = tmp_path / "executors.json"
    recordings_dir = tmp_path / "recordings"
    calls: list[tuple[str, Any]] = []

    class FailingStack:
        def __init__(self, project: str, profile: str) -> None:
            self.project = project

        def up(self, services: list[str]) -> None:
            stack_file.write_text("{}", encoding="utf-8")
            executors_file.write_text("[]", encoding="utf-8")
            recordings_dir.mkdir()
            raise RuntimeError("synthetic startup failure")

        def compose(self, *args: str, timeout: int) -> None:
            calls.append(("compose", (args, timeout)))
            if cleanup_fails:
                raise TimeoutError("synthetic cleanup timeout")

        def run(self, cmd: list[str], *, check: bool, timeout: int) -> None:
            calls.append(("run", (cmd, check, timeout)))

    monkeypatch.setattr(jane_stack, "Stack", FailingStack)
    monkeypatch.setattr(jane_stack, "stack_file", lambda _project: stack_file)
    monkeypatch.setattr(jane_stack, "executors_file", lambda _project: executors_file)
    monkeypatch.setattr(jane_stack, "recordings_dir", lambda _project: recordings_dir)
    monkeypatch.setattr(lh, "ROOT", tmp_path)
    monkeypatch.setattr(lh, "OUT_ROOT", tmp_path / ".jane" / "limits")
    monkeypatch.setattr(
        lh,
        "environment",
        lambda profile, project: {
            "profile": profile,
            "project": project,
            "measured_at": "2026-09-30T00:00:00Z",
            "git_sha": "test-sha",
            "git_dirty": False,
            "docker": {"ServerVersion": "test", "OperatingSystem": "test", "NCPU": 1, "MemTotal": 1024},
            "foreign_containers": 0,
        },
    )
    ns = argparse.Namespace(
        profile="ci", project=project, only=None, repeat=None, no_up=False, allow_busy=False, keep=False
    )

    assert lh.run(ns) == 1
    run_dir = next((tmp_path / ".jane" / "limits").iterdir())
    assert (run_dir / "environment.json").is_file()
    assert "**Verdict: fail**" in (run_dir / "summary.md").read_text(encoding="utf-8")
    result = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    assert result["summary"]["verdict"] == "fail"
    assert result["results"][0]["id"] == "startup"
    assert "synthetic startup failure" in result["results"][0]["error"]
    assert calls[0] == (
        "compose",
        (("--profile", "*", "down", "--remove-orphans", "-v", "--rmi", "local"), 180),
    )
    if cleanup_fails:
        assert "synthetic cleanup timeout" in result["results"][0]["metrics"]["cleanup_errors"][0]
        assert stack_file.exists() and executors_file.exists() and recordings_dir.exists()
        assert len(calls) == 1
    else:
        assert result["results"][0]["metrics"]["cleanup_errors"] == []
        assert not stack_file.exists() and not executors_file.exists() and not recordings_dir.exists()
        assert calls[1][1][-1] == 30


def test_dev_laptop_sandbox_wall_time_covers_the_observed_docker_desktop_cold_start() -> None:
    """WP-13 saw 30.7 s of container start for a 1 s extractor on Docker Desktop: 30 s was too tight;
    its e2e runs pass with 60 s (JANE_E2E_SANDBOX_WALL_TIME_MS). Phase 2 (L6) measures the real headroom."""
    profile = json.loads((PROFILES / "dev-laptop.json").read_text(encoding="utf-8"))
    sandbox, timeouts = profile["defaults"]["sandbox"], profile["defaults"]["timeouts"]
    assert sandbox["wall_time_ms"] >= 60_000 > 30_700
    assert timeouts["invocation_timeout_ms"] > sandbox["wall_time_ms"]
    assert sandbox["wall_time_ms"] <= profile["hard_caps"]["sandbox"]["wall_time_ms"]


@pytest.mark.parametrize("service", ["orchestrator", "web_collector", "telegram_collector"])
def test_services_that_take_the_whole_profile_as_limits_file(service: str) -> None:
    settings = importlib.import_module(f"jane_{service}.settings")
    for name in jane_stack.PROFILES:
        resolved = settings.resolve_service_limits(
            settings.Settings.model_construct().model_copy(
                update={"limits_file": jane_stack.profile_path(name)}
            )
        )
        assert resolved is not None


@pytest.mark.parametrize("service", ["storage", "handler_runtime", "registry", "llm", "assistant"])
def test_services_that_reject_the_whole_profile_as_limits_file(service: str) -> None:
    settings = importlib.import_module(f"jane_{service}.settings")
    settings.resolve_service_limits(
        settings.Settings.model_construct().model_copy(
            update={"limits_file": jane_stack.profile_path("dev-laptop")}
        )
    )


# ------------------------------------------------------------------------------------------ stack
def test_stack_overlay_applies_the_profile_where_it_is_accepted() -> None:
    doc = yaml.safe_load(jane_stack.STACK_COMPOSE.read_text(encoding="utf-8"))
    services = doc["services"]
    for name, var in (
        ("orchestrator", "JANE_ORCHESTRATOR_LIMITS_FILE"),
        ("web-collector", "JANE_WEB_COLLECTOR_LIMITS_FILE"),
        ("telegram-collector", "JANE_TELEGRAM_COLLECTOR_LIMITS_FILE"),
    ):
        assert services[name]["environment"][var] == "/cfg/limits/platform.json"
    for name in ("storage", "handler-runtime", "registry"):
        assert not any("LIMITS_FILE" in k for k in (services.get(name) or {}).get("environment", {}))
    assert (
        services["orchestrator"]["environment"]["JANE_ORCHESTRATOR_EXECUTORS_FILE"] == "/cfg/executors.json"
    )
    executors = jane_stack.executors_for(jane_stack.DEFAULT_SERVICES)
    assert {e["role"] for e in executors} == {"collector", "handler", "storage_read", "registry"}
    assert "telegram-collector" not in {e["executor"] for e in executors}
    telegram = jane_stack.executors_for(["telegram-collector"], telegram_backend="telethon")
    assert telegram[0]["sync_connections"] is True  # telegram_account is pushed only for the real backend
    assert jane_stack.executors_for(["telegram-collector"])[0]["sync_connections"] is False
    assert (
        services["handler-runtime"]["environment"]["JANE_HANDLER_RUNTIME_REGISTRY_URL"]
        == "http://registry:8000"
    )
    assert services["probe-site"]["profiles"] == ["limits-probe"]


def test_stack_credentials_and_names_are_isolated() -> None:
    a, b = jane_stack.new_credentials(), jane_stack.new_credentials()
    assert set(a) == set(b) and a["JANE_PG_PASSWORD"] != b["JANE_PG_PASSWORD"]
    assert set(jane_stack.PG_PASSWORD_KEYS) <= set(a)
    assert jane_stack.default_project(Path("C:/x")) != jane_stack.default_project(Path("C:/y"))
    assert jane_stack.sandbox_image("jane-p").startswith("jane-p-")
    with pytest.raises(SystemExit):
        jane_stack.profile_path("no-such-profile")


# ------------------------------------------------------------------------------------------ metrics
def test_window_gap_and_concurrency_metrics() -> None:
    events = [ev(0.0, 1.0), ev(0.5, 1.5), ev(1.0, 2.0), ev(3.0, 3.1)]
    assert m.start_gaps(events) == [0.5, 0.5, 2.0]
    assert m.max_in_window([0.0, 0.5, 1.0, 3.0], 1.0) == 2  # half-open window
    assert m.max_in_window([0.0, 0.5, 0.99, 3.0], 1.0) == 3
    assert m.max_concurrency(events) == 2  # an end and a start at 1.0 do not overlap
    assert m.percentile([1, 2, 3, 4, 5], 95) == 5
    assert m.percentile([], 50) is None
    assert m.request_interval({"requests_per_second_per_host": 2, "min_delay_ms_per_host": 700}) == 0.7


RATE_TH = {"gap_tolerance_fraction": 0.1, "gap_tolerance_abs_s": 0.02, "min_efficiency": 0.6}
RATE = {"requests_per_second_per_host": 2, "min_delay_ms_per_host": 0}


def test_rate_checks_pass_for_a_polite_collector() -> None:
    events = [ev(i * 0.5) for i in range(10)]
    metrics, checks = m.rate_checks(events, RATE, RATE_TH, expected=10)
    assert m.verdict(checks) == "pass", checks
    assert metrics["max_in_1s"] == 2 and metrics["avg_rate_rps"] == pytest.approx(2.0)


def test_rate_checks_fail_when_two_collections_double_the_rate() -> None:
    """What L2 detects if every collection keeps its own per-host limiter."""
    events = [ev(i * 0.5) for i in range(10)] + [ev(i * 0.5 + 0.01, path="/s/b/p/1") for i in range(10)]
    _, checks = m.rate_checks(events, RATE, RATE_TH, expected=20)
    failed = {c["name"] for c in checks if not c["ok"]}
    assert m.verdict(checks) == "fail"
    assert {"single gap not below half the interval, s", "requests in any 1 s window"} <= failed


def test_rate_checks_warn_on_an_over_throttled_collector() -> None:
    events = [ev(i * 2.0) for i in range(5)]
    _, checks = m.rate_checks(events, RATE, RATE_TH, expected=5)
    assert m.verdict(checks) == "warn"


RETRIES = {
    "max_attempts": 3,
    "initial_backoff_ms": 1000,
    "max_backoff_ms": 60000,
    "backoff_multiplier": 2,
    "jitter": True,
}


def test_retry_checks_accept_jittered_backoff_and_reject_hammering() -> None:
    polite = [ev(0.0, path="/s/r/flaky/0"), ev(0.7, path="/s/r/flaky/0"), ev(2.2, path="/s/r/flaky/0")]
    _, checks = m.retry_checks(polite, RETRIES, failures_per_path=2, interval_s=0.0)
    assert m.verdict(checks) == "pass", checks
    hammering = [ev(0.0, path="/s/r/flaky/0"), ev(0.1, path="/s/r/flaky/0"), ev(0.2, path="/s/r/flaky/0")]
    _, checks = m.retry_checks(hammering, RETRIES, failures_per_path=2, interval_s=0.0)
    assert m.verdict(checks) == "fail"
    too_many = [ev(float(i) * 5, path="/s/r/flaky/0") for i in range(4)]
    _, checks = m.retry_checks(too_many, RETRIES, failures_per_path=5, interval_s=0.0)
    assert not next(c for c in checks if c["name"].endswith(": attempts"))["ok"]


def test_resource_parsing_and_summary() -> None:
    assert lh.parse_mib("512MiB / 15.6GiB") == 512
    assert lh.parse_mib("1.5GiB / 15.6GiB") == 1536
    assert lh.parse_mib("") is None
    results = [
        {"id": "L1", "checks": [m.check("x", 1, "<=", 2)]},
        {"id": "L2", "checks": [m.check("y", 3, "<=", 2)]},
        {"id": "L3", "checks": [m.check("z", 3, "<=", 2, "warning")]},
    ]
    summary = lh.summarize(results)
    assert summary["verdict"] == "fail"
    assert [s["verdict"] for s in summary["scenarios"]] == ["pass", "fail", "warn"]
    env = {
        "profile": "ci",
        "measured_at": "t",
        "git_sha": "abc",
        "git_dirty": False,
        "docker": {},
        "foreign_containers": 0,
    }
    assert "| L2 | 1 | y | 3 | <= 2 | FAIL |" in lh.markdown(env, results, summary)


# ------------------------------------------------------------------------------------------ probe site
@pytest.fixture
def probe() -> Iterator[str]:
    server = probe_site.make_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def test_probe_site_logs_requests_failures_and_retry_after(probe: str) -> None:
    with httpx.Client(base_url=probe, timeout=10) as c:
        c.post("/_probe/reset", params={"ns": "t"})
        assert c.get("/s/t/p/1").status_code == 200
        assert [c.get("/s/t/flaky/1", params={"fail": 2}).status_code for _ in range(3)] == [503, 503, 200]
        limited = c.get("/s/t/limited/1", params={"fail": 1, "retry_after": 3})
        assert limited.status_code == 429 and limited.headers["Retry-After"] == "3"
        slow = c.get("/s/t/slow/1", params={"ms": 60})
        assert slow.status_code == 200
        assert c.get("/robots.txt").text.startswith("User-agent: *")
        log = c.get("/_probe/log", params={"ns": "t"}).json()["events"]
        assert [e["status"] for e in log] == [200, 503, 503, 200, 429, 200]
        assert log[-1]["end"] - log[-1]["start"] >= 0.05
        c.post("/_probe/reset", params={"ns": "t"})
        assert c.get("/_probe/log", params={"ns": "t"}).json()["events"] == []
        assert c.get("/s/t/flaky/1", params={"fail": 1}).status_code == 503  # counters reset too


# ------------------------------------------------------------------------------------------ sandbox probe
def test_sandbox_probe_package() -> None:
    assert_package_tests_pass(lh.PROBE_PACKAGE)
    manifest = json.loads((lh.PROBE_PACKAGE / "jane-package.json").read_text(encoding="utf-8"))
    assert lh.examples().package_json_problems(lh.PROBE_PACKAGE, manifest) == []
    result = run_local(
        lh.PROBE_PACKAGE,
        file=lh.PROBE_PACKAGE / "tests" / "page" / "page.html",
        media_type="text/html",
        params={"sleep_ms": 1, "alloc_mb": 2},
    )
    assert result["status"] == "empty"


def test_sandbox_invocation_body_is_valid_against_the_contract() -> None:
    ex = lh.examples()
    harness = lh.Harness.__new__(lh.Harness)
    harness.d = lh.load_profile("dev-laptop")["defaults"]
    harness.probe_host = lh.PROBE_HOST
    body = harness.invocation({"sleep_ms": 10}, mode="async")
    assert ex.validate("handler-invocation.schema.json", body) == []
    assert body["limits"]["sandbox"] == harness.d["sandbox"]


# ------------------------------------------------------------------------------------------ harness self-test
SELF_TEST_PROFILE: dict[str, Any] = {
    "profile": "harness-self-test",
    "defaults": {
        "concurrency": {"max_parallel_fetches": 4, "max_parallel_fetches_per_host": 2},
        "rate": {"requests_per_second_per_host": 10, "min_delay_ms_per_host": 0, "respect_crawl_delay": True},
        "timeouts": {"connect_timeout_ms": 1000, "request_timeout_ms": 1000},
        "retries": {
            "max_attempts": 3,
            "initial_backoff_ms": 100,
            "max_backoff_ms": 1000,
            "backoff_multiplier": 2,
            "jitter": True,
        },
        "queue": {"max_unacked_materials": 500},
    },
    "hard_caps": {},
}
SELF_TEST_THRESHOLDS: dict[str, Any] = {
    "rate": {"pages": 12, "gap_tolerance_fraction": 0.2, "gap_tolerance_abs_s": 0.01, "min_efficiency": 0.3},
    "shared_host": {"pages_per_collection": 6},
    "parallel": {"pages": 6, "slow_ms": 400},
    "retries": {"flaky_pages": 2, "failures_per_path": 2, "retry_after_s": 1, "timeout_extra_ms": 500},
    "backpressure": {"pages": 20, "max_unacked": 3, "hold_s": 2},
}


def test_harness_collector_scenarios_run_against_a_local_collector(probe: str, tmp_path: Path) -> None:
    """Self-test of the scenario code (NOT a profile measurement): a local web-collector process with a
    synthetic fast profile and the in-process probe site. Real measurements run in Docker (phase 2)."""
    import socket

    from jane_web_collector.testing import ServiceProcess

    limits_file = tmp_path / "limits.json"
    limits_file.write_text(json.dumps(SELF_TEST_PROFILE), encoding="utf-8")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = int(s.getsockname()[1])
    state = tmp_path / "state"
    env = ServiceProcess.environment(port, state, JANE_WEB_COLLECTOR_LIMITS_FILE=str(limits_file))
    service = ServiceProcess(port=port, state_dir=state, env=env)
    service.start()
    try:
        probe_host = probe.removeprefix("http://")
        harness = lh.Harness(
            "harness-self-test",
            "self-test",
            tmp_path / "out",
            urls={"web-collector": service.base, "probe-site": probe},
            probe_host=probe_host,
            profile=SELF_TEST_PROFILE,
            thresholds=SELF_TEST_THRESHOLDS,
        )
        results = {
            r["id"]: r
            for r in (
                harness.l1_rate(),
                harness.l2_shared_host(),
                harness.l3_parallel(),
                harness.l4_retries(),
                harness.l5_backpressure(),
            )
        }
    finally:
        service.stop()
    # Deterministic mechanisms of the collector: the harness must see them hold.
    for sid in ("L3", "L4", "L5"):
        failed = [c for c in results[sid]["checks"] if not c["ok"] and c["severity"] == "blocker"]
        assert failed == [], (sid, failed, results[sid]["metrics"])
    assert results["L1"]["metrics"]["requests"] == 12
    assert {c["name"] for c in results["L1"]["checks"]} >= {
        "requests in any 1 s window",
        "all pages requested",
    }
    assert results["L3"]["metrics"]["max_in_flight"] <= 2
    assert (tmp_path / "out" / "raw" / "r1-L1-probe.jsonl").is_file()
    # Politeness in time (L1, L2) is what phase 2 measures; here it is only reported as an indication.
    for sid in ("L1", "L2"):
        print(
            f"{sid} (self-test indication):",
            json.dumps(results[sid]["metrics"]),
            [c for c in results[sid]["checks"] if not c["ok"]],
        )
