"""Profiles, the profile stack and the limits harness without Docker: metrics, probe site, thresholds.

Run: ``uv run --all-packages pytest deploy/profiles -q``. The measurements themselves need a free Docker host
(``limits_harness.py run``, docs/operations/limits-validation.md) and are not part of these tests.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import threading
from collections.abc import Iterator, Mapping
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
PROFILE_NAMES = tuple(sorted(p.stem for p in PROFILES.glob("*.json") if p.name != "thresholds.json"))
"""Every profile document of deploy/profiles; the profile tests run for each of them (single-node too)."""
JANE_KIT_SERVICES = ("storage", "handler_runtime", "registry", "llm", "assistant")
"""Services whose platform file is the shared jane-kit layer (WP-01b): unmodelled contract limits are ignored."""
LIMITS_FILE_ENV = {
    "storage": "JANE_STORAGE_LIMITS_FILE",
    "handler-runtime": "JANE_HANDLER_RUNTIME_LIMITS_FILE",
    "registry": "JANE_REGISTRY_LIMITS_FILE",
    "llm": "JANE_LLM_LIMITS_FILE",
    "assistant": "JANE_ASSISTANT_LIMITS_FILE",
    "web-collector": "JANE_WEB_COLLECTOR_LIMITS_FILE",
    "telegram-collector": "JANE_TELEGRAM_COLLECTOR_LIMITS_FILE",
    "orchestrator": "JANE_ORCHESTRATOR_LIMITS_FILE",
}
PROFILE_MOUNT = {
    "type": "bind",
    "source": "${JANE_PROFILE_FILE:?set by deploy/profiles/stack.py}",
    "target": "/cfg/limits/platform.json",
    "read_only": True,
}


def ev(start: float, end: float | None = None, path: str = "/s/t/p/1", status: int = 200) -> dict[str, Any]:
    return {"start": start, "end": start + 0.01 if end is None else end, "path": path, "status": status}


def leaves(doc: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in doc.items():
        if isinstance(value, Mapping):
            out.update(leaves(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = value
    return out


def load(profile: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(jane_stack.profile_path(profile).read_text(encoding="utf-8"))
    return data


def overlay_services() -> dict[str, Any]:
    doc: dict[str, Any] = yaml.safe_load(jane_stack.STACK_COMPOSE.read_text(encoding="utf-8"))
    return dict(doc["services"])


def jane_module(module: str) -> Any:
    """``jane_<module>`` of a service (imported dynamically: service packages ship no ``py.typed``)."""
    return importlib.import_module(f"jane_{module}")


def compose_default(value: str) -> str:
    """``${VAR:-default}`` of the compose file -> ``default`` (what the stack uses when VAR is unset)."""
    assert value.startswith("${") and ":-" in value and value.endswith("}"), value
    return value[2:-1].split(":-", 1)[1]


# ------------------------------------------------------------------------------------------ profiles
def test_profiles_are_valid_platform_limits(capsys: pytest.CaptureFixture[str]) -> None:
    profile_check.main()
    out = capsys.readouterr().out
    assert out.count("schema valid") == len(PROFILE_NAMES) == 3


def test_every_profile_file_is_known_to_the_stack_and_the_check() -> None:
    assert set(PROFILE_NAMES) == set(jane_stack.PROFILES) == set(profile_check.PROFILES)
    assert set(MEASURED) < set(PROFILE_NAMES)


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_profile_defaults_fit_their_hard_caps_and_timeouts_nest(profile: str) -> None:
    doc = load(profile)
    defaults, caps = leaves(doc["defaults"]), leaves(doc["hard_caps"])
    assert doc["profile"] == profile
    assert {p: (defaults[p], cap) for p, cap in caps.items() if defaults[p] > cap} == {}
    t = doc["defaults"]["timeouts"]
    assert doc["defaults"]["sandbox"]["wall_time_ms"] < t["invocation_timeout_ms"] <= t["stage_timeout_ms"]
    assert t["request_timeout_ms"] <= t["stage_timeout_ms"] <= t["run_timeout_ms"]


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


@pytest.mark.parametrize("profile", PROFILE_NAMES)
@pytest.mark.parametrize("name", ["orchestrator", "web_collector", "telegram_collector", *JANE_KIT_SERVICES])
def test_every_service_takes_the_whole_profile_as_limits_file(name: str, profile: str) -> None:
    """One profile for every service (criterion 13): the whole document is a valid ``LIMITS_FILE`` and each
    service applies the contract limits it models with the profile's values (as ``/v1/info`` publishes)."""
    settings = importlib.import_module(f"jane_{name}.settings")
    path = jane_stack.profile_path(profile)
    resolved = settings.resolve_service_limits(
        settings.Settings.model_construct().model_copy(update={"limits_file": path})
    )
    if name == "orchestrator":
        # the file seeds the platform document of its DB (schema-checked like check.py); own limits: env only
        assert resolved.profile is None
        return
    wanted = leaves(load(profile)["defaults"])
    applied = leaves(resolved.platform_limits()["defaults"])
    assert resolved.profile == profile
    assert applied and {p: applied[p] for p in applied} == {p: wanted.get(p) for p in applied}
    if name in JANE_KIT_SERVICES:  # the collectors drop unmodelled groups silently (translate_layer)
        assert set(resolved.ignored) == set(wanted) - set(applied)


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_assistant_reaches_the_fake_llm_within_the_profile_budget(
    profile: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With the profile mounted the assistant's own budget check (``spent >= budget.amount``) and the gateway's
    (``spent + estimate <= limit``) must both let a call to the free fake model through; ``amount: 0`` did not.
    Real llm service (fake provider, memory store) as the assistant's neighbour, both with the stack's env."""
    from fastapi.testclient import TestClient

    assistant_llm, assistant, llm = (
        jane_module(n) for n in ("assistant.llm", "assistant.settings", "llm.settings")
    )
    path = jane_stack.profile_path(profile)
    key = "JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS"
    monkeypatch.setenv(key, compose_default(overlay_services()["llm"]["environment"][key]))
    budget = load(profile)["defaults"]["llm"]["budget"]
    assert budget["amount"] > 0
    limits = assistant.resolve_service_limits(
        assistant.Settings.model_construct().model_copy(update={"limits_file": path})
    )
    assert limits.limits.llm.budget.model_dump() == budget

    class Gateway:
        """``LlmClient.complete`` over the in-process llm app (transport only, the service itself is real)."""

        def __init__(self, client: TestClient) -> None:
            self.client = client

        async def complete(self, request: Mapping[str, Any], key: str) -> dict[str, Any]:
            r = self.client.post("/v1/completions", json=dict(request), headers={"Idempotency-Key": key})
            assert r.status_code == 200, r.text
            body: dict[str, Any] = r.json()
            return body

    settings = llm.Settings(log_format="console", store="memory", limits_file=path)
    app = jane_module("llm.app").build_app(settings, store=jane_module("llm.store").MemoryStore())
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}
    with TestClient(app) as client:
        assert client.get("/v1/info").json()["limits"]["defaults"]["llm"]["budget"] == budget
        session = assistant_llm.LlmSession(
            Gateway(client), limits.limits.llm, "onboarding", f"profile-{profile}"
        )
        data = [assistant_llm.part("page", "x")]
        output = asyncio.run(session.ask("probe", "Answer with the schema.", data, schema, model="default"))
    assert set(output) == {"ok"} and session.calls == 1 and session.spent == 0


# ------------------------------------------------------------------------------------------ stack
def test_stack_overlay_applies_the_profile_to_every_service() -> None:
    services = overlay_services()
    assert set(LIMITS_FILE_ENV) == jane_stack.APP_SERVICES
    for name, var in LIMITS_FILE_ENV.items():
        assert services[name]["environment"][var] == PROFILE_MOUNT["target"], name
        mounts = [
            v
            for v in services[name]["volumes"]
            if isinstance(v, dict) and v["target"] == PROFILE_MOUNT["target"]
        ]
        assert mounts == [PROFILE_MOUNT], name
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


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_stack_llm_keeps_its_provider_timeout_and_the_profile_keeps_its_web_timeout(
    profile: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The profile's ``timeouts.request_timeout_ms`` is sized for web fetches; llm declares its provider timeout
    as that contract field, so the stack overrides only ``provider.request_timeout_ms`` (to the service's own
    default) and every other service keeps the profile's value (request to WP-10 in docs/delivery/WP-14.md)."""
    llm = jane_module("llm.settings")
    key = "JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS"
    override = int(compose_default(overlay_services()["llm"]["environment"][key]))
    assert override == llm.ServiceLimits().provider.request_timeout_ms == 120_000
    doc = load(profile)
    web_timeout = doc["defaults"]["timeouts"]["request_timeout_ms"]
    assert web_timeout < override
    path = jane_stack.profile_path(profile)
    llm_settings = llm.Settings.model_construct().model_copy(update={"limits_file": path})
    assert llm.resolve_service_limits(llm_settings).limits.provider.request_timeout_ms == web_timeout
    monkeypatch.setenv(key, str(override))
    resolved = llm.resolve_service_limits(llm_settings)
    assert resolved.limits.provider.request_timeout_ms == override
    assert resolved.limits.provider.connect_timeout_ms == doc["defaults"]["timeouts"]["connect_timeout_ms"]
    assert resolved.profile == profile
    for name in ("storage", "handler_runtime", "assistant", "web_collector"):
        settings = jane_module(f"{name}.settings")
        applied = settings.resolve_service_limits(
            settings.Settings.model_construct().model_copy(update={"limits_file": path})
        ).platform_limits()["defaults"]
        assert applied.get("timeouts", {}).get("request_timeout_ms", web_timeout) == web_timeout, name


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_runtime_info_with_the_profile_passes_the_l6_profile_checks(profile: str, tmp_path: Path) -> None:
    """L6 reads ``max_parallel_invocations`` from handler-runtime ``/v1/info`` (``limits.defaults``, a
    ``PlatformLimits`` document). CI run 36908333153 read ``limits.concurrency`` and got ``None``. Here the real
    runtime app (subprocess backend, no Docker) runs with the profile as its ``LIMITS_FILE``, like the stack."""
    from fastapi.testclient import TestClient

    settings = jane_module("handler_runtime.settings").Settings(
        log_format="console",
        sandbox_backend="subprocess",
        allow_unsafe_subprocess=True,
        package_cache_dir=tmp_path / "cache",
        limits_file=jane_stack.profile_path(profile),
    )
    cap = load(profile)["defaults"]["concurrency"]["max_parallel_invocations"]
    with TestClient(jane_module("handler_runtime.app").build_app(settings)) as client:
        info = client.get("/v1/info").json()
    checks = lh.runtime_profile_checks(info, profile, cap)
    assert [(c["name"], c["value"], c["ok"]) for c in checks] == [
        ("runtime limits profile = profile", profile, True),
        ("runtime max_parallel_invocations = profile", cap, True),
    ]
    without_profile = {"limits": {"defaults": {"concurrency": {"max_parallel_invocations": cap}}}}
    assert [c["ok"] for c in lh.runtime_profile_checks(without_profile, profile, cap)] == [False, True]
    assert m.verdict(lh.runtime_profile_checks({"limits": {"concurrency": {}}}, profile, cap)) == "warn"


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
