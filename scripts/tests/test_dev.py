from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tomllib
from argparse import Namespace
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"jane_scripts_{name}", SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


dev = load("dev")


def test_workspace_members_cover_every_locked_package() -> None:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    actual = dev.members()
    assert ROOT / "contracts" / "python" in actual
    assert len(actual) == len(set(actual))
    assert {dev.member_name(path) for path in actual} == set(lock["manifest"]["members"])


def test_new_service_renders_every_name(tmp_path: Path) -> None:
    dest = dev.new_service("price-checker", tmp_path)
    files = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    assert "src/jane_price_checker/app.py" in files
    assert {"Dockerfile", "README.md", "CLAUDE.md", "pyproject.toml", "tests/test_app.py"} <= files
    for f in dest.rglob("*"):
        if f.is_file():
            text = f.read_text(encoding="utf-8")
            assert not re.search(r"template[-_ ]service|TemplateService|TEMPLATE_SERVICE", text, re.I), f
    pyproject = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "jane-price-checker"' in pyproject
    docker = (dest / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY services/price-checker/ services/price-checker/" in docker
    assert "--package jane-price-checker" in docker
    assert "JANE_PRICE_CHECKER_PORT" in docker
    claude = (dest / "CLAUDE.md").read_text(encoding="utf-8").strip().splitlines()
    assert len(claude) == 3


@pytest.mark.parametrize("bad", ["Web", "web_collector", "-x", "x-", "1abc", "a--b"])
def test_new_service_rejects_bad_names(tmp_path: Path, bad: str) -> None:
    with pytest.raises(SystemExit):
        dev.new_service(bad, tmp_path)


def test_new_service_refuses_to_overwrite(tmp_path: Path) -> None:
    dev.new_service("svc", tmp_path)
    with pytest.raises(SystemExit, match="already exists"):
        dev.new_service("svc", tmp_path)


def test_default_project_is_valid_and_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JANE_COMPOSE_PROJECT", raising=False)
    name = dev.default_project()
    assert re.fullmatch(r"jane-[a-z0-9-]+-[0-9a-f]{6}", name)
    assert name == dev.default_project()
    monkeypatch.setenv("JANE_COMPOSE_PROJECT", "jane-custom")
    assert dev.default_project() == "jane-custom"


def test_existing_stack_receives_distinct_service_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "stack-test.json"
    path.write_text('{"env":{"JANE_PG_PASSWORD":"existing"},"services":{}}', encoding="utf-8")
    monkeypatch.setattr(dev, "stack_file", lambda project: path)
    creds = dev.load_or_create_credentials("test")
    assert creds["JANE_PG_PASSWORD"] == "existing"
    passwords = [creds[key] for _, key in dev.PG_SERVICE_DATABASES.values()]
    assert len(passwords) == len(set(passwords))
    assert all(password != "existing" for password in passwords)
    assert dev.load_or_create_credentials("test") == creds


def test_describe_separates_database_credentials_from_app_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        dev, "host_port", lambda project, env, service, port: 15432 if service == "postgres" else None
    )
    env = {"JANE_PG_USER": "jane", "JANE_PG_PASSWORD": "root-test", "JANE_PG_DB": "jane"}
    env.update({key: f"{name}-test" for name, (_, key) in dev.PG_SERVICE_DATABASES.items()})
    services = dev.describe("test", env)
    assert "handler-runtime" not in services
    assert services["db-handler-runtime"]["db_user"] == "jane_handler_runtime"
    assert services["db-handler-runtime"]["db_name"] == "jane_handler_runtime"


def test_up_postgres_runs_provision_gate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "stack-test.json"
    monkeypatch.setattr(dev, "ROOT", tmp_path)
    monkeypatch.setattr(dev, "stack_file", lambda project: path)
    monkeypatch.setattr(dev, "describe", lambda project, env: {})
    calls: list[list[str]] = []

    def fake_compose(project: str, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(dev, "compose", fake_compose)
    assert dev.cmd_up(Namespace(project="test", wait_timeout=10, no_build=True, services=["postgres"])) == 0
    assert calls[0][-1] == "postgres"
    assert calls[1] == ["run", "--rm", "--no-deps", "pg-provision"]


def test_up_default_excludes_one_shot_from_wait(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dev, "ROOT", tmp_path)
    monkeypatch.setattr(dev, "stack_file", lambda project: tmp_path / "stack-test.json")
    monkeypatch.setattr(dev, "describe", lambda project, env: {})
    calls: list[list[str]] = []

    def fake_compose(project: str, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(dev, "compose", fake_compose)
    assert dev.cmd_up(Namespace(project="test", wait_timeout=10, no_build=True, services=[])) == 0
    assert calls[0][-len(dev.DEFAULT_STACK_SERVICES) :] == list(dev.DEFAULT_STACK_SERVICES)
    assert calls[1] == ["run", "--rm", "--no-deps", "pg-provision"]


def test_web_runs_corepack_from_each_package(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    package = tmp_path / "web" / "admin"
    package.mkdir(parents=True)
    (package / "package.json").write_text('{"packageManager":"pnpm@11.27.1"}', encoding="utf-8")
    monkeypatch.setattr(dev, "web_packages", lambda: [package])
    monkeypatch.setattr(dev.shutil, "which", lambda name: "corepack" if name == "corepack" else None)
    calls: list[tuple[list[str], Path]] = []

    def fake_run(cmd: list[str], *, cwd: Path, **_: object) -> subprocess.CompletedProcess[str]:
        calls.append((cmd, cwd))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(dev, "run", fake_run)
    assert dev.cmd_web(Namespace()) == 0
    assert len(calls) == 5
    assert all(cwd == package and cmd[:2] == ["corepack", "pnpm"] for cmd, cwd in calls)
    assert calls[-1][0][-2:] == ["--if-present", "build"]


def test_e2e_runs_only_acceptance_suite(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        seen.extend(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(dev, "run", fake_run)
    assert dev.cmd_e2e(Namespace(pytest_args=["-v"])) == 0
    assert seen[-5:] == ["pytest", "tests/e2e", "-m", "e2e", "-v"]


def test_down_includes_inactive_profiles(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "stack-test.json"
    path.write_text('{"env":{"JANE_PG_PASSWORD":"local-test"}}', encoding="utf-8")
    monkeypatch.setattr(dev, "stack_file", lambda project: path)
    seen: list[str] = []

    def fake_compose(project: str, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
        seen.extend(args)
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(dev, "compose", fake_compose)
    assert dev.cmd_down(Namespace(project="test", volumes=True)) == 0
    assert seen[:2] == ["--profile", "*"]
    assert "-v" in seen
    assert not path.exists()


def test_devstack_uses_the_same_default_project(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from jane_kit import devstack

    monkeypatch.delenv("JANE_COMPOSE_PROJECT", raising=False)
    monkeypatch.delenv("JANE_STACK_FILE", raising=False)
    assert devstack.default_project(ROOT) == dev.default_project()
    # load_stack never falls back to another project's file
    repo = tmp_path / "checkout"
    (repo / "infra").mkdir(parents=True)
    (repo / "justfile").write_text("", encoding="utf-8")
    (repo / ".jane").mkdir()
    other = {"project": "jane-other", "services": {"postgres": {"host": "h", "port": 1}}}
    (repo / ".jane" / "stack-jane-other.json").write_text(dev.json.dumps(other), encoding="utf-8")
    assert devstack.load_stack(root=repo) is None
    assert devstack.load_stack("jane-other", root=repo) is not None
    mine = {"project": devstack.default_project(repo.resolve()), "services": {}}
    (repo / ".jane" / f"stack-{mine['project']}.json").write_text(dev.json.dumps(mine), encoding="utf-8")
    info = devstack.load_stack(root=repo)
    assert info is not None and info.project == mine["project"]
    monkeypatch.setenv("JANE_STACK_FILE", str(repo / ".jane" / "stack-jane-other.json"))
    info = devstack.load_stack(root=repo)
    assert info is not None and info.project == "jane-other"


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["unit", "-v"], ["-v"]),
        (["check", "-v", "-k", "limits"], ["-v", "-k", "limits"]),
        (["contract", "-x", "--", "-q"], ["-x", "-q"]),
        (["integration", "--project", "jane-x", "-v"], ["-v"]),
        (["isolation", "-vv"], ["-vv"]),
        (["test", "jane-kit", "-k", "limits", "-v"], ["-k", "limits", "-v"]),
    ],
)
def test_pytest_arguments_pass_through(
    monkeypatch: pytest.MonkeyPatch, argv: list[str], expected: list[str]
) -> None:
    seen: dict[str, object] = {}

    def fake(ns: object) -> int:
        seen["args"] = ns.pytest_args  # type: ignore[attr-defined]
        seen["ns"] = ns
        return 0

    for name in ("cmd_unit", "cmd_check", "cmd_contract", "cmd_integration", "cmd_isolation", "cmd_test"):
        monkeypatch.setattr(dev, name, fake)
    assert dev.main(argv) == 0
    assert seen["args"] == expected
    if argv[0] == "integration":
        assert seen["ns"].project == "jane-x"  # type: ignore[attr-defined]
    if argv[0] == "test":
        assert seen["ns"].target == "jane-kit"  # type: ignore[attr-defined]


def _record_runs(monkeypatch: pytest.MonkeyPatch, codes: dict[str, int] | None = None) -> list[list[str]]:
    """Replace dev.run; a command whose text contains a key of ``codes`` returns that exit code."""
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        text = " ".join(cmd)
        return subprocess.CompletedProcess(cmd, next((c for k, c in (codes or {}).items() if k in text), 0))

    monkeypatch.setattr(dev, "run", fake_run)
    return calls


def test_types_checks_examples_and_profiles_one_run_each(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dev, "members", list)
    calls = _record_runs(monkeypatch, {"mypy deploy/profiles": 1})
    assert dev.main(["types"]) == 1
    mypy = [cmd[cmd.index("mypy") + 1 :] for cmd in calls]
    assert mypy == [["scripts", "infra/tests"], ["examples"], ["deploy/profiles"]]


def test_contract_runs_the_compat_self_test(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_runs(monkeypatch)
    assert dev.main(["contract"]) == 0
    assert dev.contract_tool("compat.py", "--self-test") in calls
    calls = _record_runs(monkeypatch, {"--self-test": 1})
    assert dev.main(["contract"]) == 1
    assert any(cmd[-2:] == ["-m", "contract"] for cmd in calls)  # contract tests still run


def test_contracts_compat_self_test_then_base(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_runs(monkeypatch)
    assert dev.main(["contracts-compat", "origin/main", "--oasdiff"]) == 0
    assert calls == [
        ["uv", "run", "--script", "contracts/tools/compat.py", "--self-test"],
        ["uv", "run", "--script", "contracts/tools/compat.py", "--base", "origin/main", "--oasdiff"],
    ]
    calls = _record_runs(monkeypatch)
    assert dev.main(dev.from_just(["--just", "contracts-compat", "contracts-compat"])) == 0
    assert calls[-1][-2:] == ["--base", "main"]
    calls = _record_runs(monkeypatch, {"--self-test": 1})
    assert dev.main(["contracts-compat"]) == 1
    assert len(calls) == 1  # a broken comparator never reports "0 breaking"


def test_contracts_check_mock_and_gen(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record_runs(monkeypatch)
    assert dev.main(["contracts-check"]) == 0
    assert calls[-1][-2:] == ["python", "scripts/contracts_lint.py"]
    assert dev.main(["contracts-mock", "handler", "--port", "4011"]) == 0
    assert calls[-1] == dev.contract_tool("mock.py", "handler", "--port", "4011", "--host", "127.0.0.1")
    assert dev.main(["contracts-gen", "storage", "out/storage"]) == 0
    assert calls[-1][3:] == [
        "jane-codegen",
        "client",
        "contracts/openapi/storage.v1.yaml",
        "--out",
        "out/storage",
        "--no-models",
    ]
    with pytest.raises(SystemExit, match="unknown contract 'nope'"):
        dev.main(["contracts-gen", "nope", "out"])


def test_unknown_arguments_rejected_for_non_pytest_commands() -> None:
    with pytest.raises(SystemExit):
        dev.main(["lint", "-v"])


def test_resolve_target() -> None:
    assert dev.resolve_target("jane-kit") == ROOT / "libs" / "jane-kit"
    assert dev.resolve_target("template-service") == ROOT / "templates" / "service"
    assert dev.resolve_target("testsite") == ROOT / "tests" / "fixtures" / "testsite"


@pytest.mark.skipif(
    shutil.which("gitleaks") is None or shutil.which("git") is None, reason="needs git + gitleaks"
)
def test_pre_commit_hook_blocks_secret(tmp_path: Path) -> None:
    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "core.autocrlf=false", *args],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "test")
    hook = dev.install_hook(tmp_path)
    assert hook.is_file()
    (tmp_path / "ok.txt").write_text("hello\n", encoding="utf-8")
    git("add", "ok.txt")
    assert git("commit", "-q", "-m", "ok").returncode == 0
    # A synthetic AWS-style key pair (not a real credential).
    fake = (
        "aws_access_key_id = AKIA"
        + "Q3EGRIIBV7XHKT2D"
        + "\naws_secret_access_key = "
        + "wJalrXUtnFEMI"
        + "K7MDENGbPxRfiCYzEXAMPLEKEY9x"
        + "\n"
    )
    (tmp_path / "leak.txt").write_text(fake, encoding="utf-8")
    git("add", "leak.txt")
    blocked = git("commit", "-q", "-m", "leak")
    assert blocked.returncode != 0, blocked.stdout + blocked.stderr


def test_from_just_keeps_argument_quoting() -> None:
    assert dev.from_just(["--just", "unit", "unit", "-v", "-k", "not slow"]) == [
        "unit",
        "-v",
        "-k",
        "not slow",
    ]
    assert dev.from_just(["--just", "test", "test", "jane-kit", "-k", "a b"]) == [
        "test",
        "jane-kit",
        "-k",
        "a b",
    ]
    assert dev.from_just(["check", "-v"]) == ["check", "-v"]
