"""Jane developer commands (cross-platform; stdlib only). Usually called through `just`.

    uv run --no-project python scripts/dev.py <command> [args]

Commands: check, lint, fmt, types, unit, contract, test, integration, isolation, web,
          e2e, up, down, ps, logs, env, new-service, hooks, testsite, gen-client, sync,
          contracts-check, contracts-compat, contracts-mock, contracts-gen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import secrets
import shutil
import subprocess
import sys
import time
import tomllib
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "infra" / "compose.yaml"
STACK_DIR = ROOT / ".jane"
UNIT_MARKERS = "not contract and not integration and not isolation"
# Offline tests outside the workspace members and the root `testpaths`: examples (WP-14) and the limits
# profiles with their harness. They need no Docker. A separate pytest session, because their conftest files
# put generic module names (stack, check, metrics, jane_examples) on sys.path. `types` checks the same
# directories, one mypy run each (both have a top-level `conftest` module).
EXTRA_UNIT_PATHS = ("examples", "deploy/profiles")
# WP-00 contract tools: PEP 723 scripts with their own dependencies (`uv run --script`, as in contracts/README).
CONTRACT_TOOLS = Path("contracts") / "tools"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


# ----------------------------------------------------------------------------- helpers
def run(
    cmd: Sequence[str],
    *,
    env: dict[str, str] | None = None,
    check: bool = False,
    capture: bool = False,
    cwd: Path = ROOT,
) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(cmd)}", flush=True)
    return subprocess.run(
        list(cmd),
        cwd=cwd,
        env={**os.environ, **(env or {})},
        check=check,
        text=True,
        capture_output=capture,
        encoding="utf-8" if capture else None,
    )


def uv_run(*args: str) -> list[str]:
    return ["uv", "run", "--all-packages", *args]


def members() -> list[Path]:
    """Workspace members (directories with pyproject.toml) matching the root globs."""
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    paths = {
        p
        for pattern in config["tool"]["uv"]["workspace"]["members"]
        for p in ROOT.glob(pattern)
        if (p / "pyproject.toml").is_file()
    }
    return sorted(paths)


def member_name(path: Path) -> str:
    text = (path / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^name\s*=\s*"([^"]+)"', text, re.M)
    return m.group(1) if m else path.name


def resolve_target(name: str) -> Path:
    """`web-collector` -> services/web-collector; also libs/<x>, dist names, or a path."""
    candidates = [ROOT / name, ROOT / "services" / name, ROOT / "libs" / name]
    for c in candidates:
        if c.is_dir():
            return c
    for m in members():
        dist = member_name(m)
        if name in {dist, dist.removeprefix("jane-")}:
            return m
    known = ", ".join(sorted(member_name(m).removeprefix("jane-") for m in members()))
    sys.exit(f"unknown target {name!r}; known: {known}")


def pytest_ok(code: int) -> bool:
    return code in (0, 5)  # 5 = no tests collected (e.g. no contract tests yet)


# ----------------------------------------------------------------------------- quality
def cmd_sync(_: argparse.Namespace) -> int:
    return run(["uv", "sync", "--all-packages"]).returncode


def cmd_lint(_: argparse.Namespace) -> int:
    codes = [
        run(uv_run("ruff", "check", ".")).returncode,
        run(uv_run("ruff", "format", "--check", ".", "contracts/python")).returncode,
        run(uv_run("python", "scripts/contracts_lint.py")).returncode,
    ]
    return max(codes)


def cmd_fmt(_: argparse.Namespace) -> int:
    run(uv_run("ruff", "check", "--fix", "."))
    return run(uv_run("ruff", "format", ".", "contracts/python")).returncode


def cmd_types(_: argparse.Namespace) -> int:
    code = 0
    for m in members():
        targets = [str(p.relative_to(ROOT)) for p in (m / "src", m / "tests") if p.is_dir()]
        if targets:
            code = max(code, run(uv_run("mypy", *targets)).returncode)
    code = max(code, run(uv_run("mypy", "scripts", "infra/tests")).returncode)
    for extra in EXTRA_UNIT_PATHS:
        if (ROOT / extra).is_dir():
            code = max(code, run(uv_run("mypy", extra)).returncode)
    return code


def names_test_paths(pytest_args: Sequence[str]) -> bool:
    """True when the caller selected tests by path (`just unit services/x/tests`): pytest then ignores
    `testpaths`, and the extra sessions are not added either."""
    return any(not a.startswith("-") and (ROOT / a.split("::", 1)[0]).exists() for a in pytest_args)


def cmd_unit(ns: argparse.Namespace) -> int:
    code = run(uv_run("pytest", "-m", UNIT_MARKERS, *ns.pytest_args)).returncode
    result = 0 if pytest_ok(code) else code
    if not names_test_paths(ns.pytest_args):
        extra = run(uv_run("pytest", *EXTRA_UNIT_PATHS, "-m", UNIT_MARKERS, *ns.pytest_args)).returncode
        result = result or (0 if pytest_ok(extra) else extra)
    return result


def contract_tool(name: str, *args: str) -> list[str]:
    """``uv run --script contracts/tools/<name> <args>`` (the tools declare their own dependencies)."""
    return ["uv", "run", "--script", (CONTRACT_TOOLS / name).as_posix(), *args]


def compat_self_test() -> int:
    """The comparator of compat.py on its built-in breaking cases (no git, milliseconds)."""
    if not (ROOT / CONTRACT_TOOLS / "compat.py").is_file():
        print("contracts compat: no contracts/tools/compat.py - skipped")
        return 0
    return run(contract_tool("compat.py", "--self-test")).returncode


def cmd_contract(ns: argparse.Namespace) -> int:
    lint = run(uv_run("python", "scripts/contracts_lint.py")).returncode
    self_test = compat_self_test()
    code = run(uv_run("pytest", "-m", "contract", *ns.pytest_args)).returncode
    return max(lint, self_test, 0 if pytest_ok(code) else code)


def cmd_contracts_check(ns: argparse.Namespace) -> int:
    """The contracts linter alone (as in `lint`/`contract`); `--redocly` also requires Redocly (Node/npx)."""
    env = {"JANE_CONTRACTS_REDOCLY": "1"} if ns.redocly else None
    return run(uv_run("python", "scripts/contracts_lint.py"), env=env).returncode


def cmd_contracts_compat(ns: argparse.Namespace) -> int:
    """Self-test of the comparator, then backward compatibility of contracts/ against a git ref."""
    self_test = compat_self_test()
    if self_test:
        return self_test
    args = ["--base", ns.base] + (["--oasdiff"] if ns.oasdiff else [])
    return run(contract_tool("compat.py", *args)).returncode


def cmd_contracts_mock(ns: argparse.Namespace) -> int:
    return run(contract_tool("mock.py", ns.api, "--port", str(ns.port), "--host", ns.host)).returncode


def contract_spec(api: str) -> Path:
    spec = Path("contracts") / "openapi" / f"{api}.v1.yaml"
    if not (ROOT / spec).is_file():
        known = sorted(p.name.removesuffix(".v1.yaml") for p in (ROOT / spec.parent).glob("*.v1.yaml"))
        sys.exit(f"unknown contract {api!r}; known: {', '.join(known) or '(none)'}")
    return spec


def cmd_contracts_gen(ns: argparse.Namespace) -> int:
    """Python client of one contract (`jane-codegen client --no-models`), e.g. into `<pkg>/_generated/<api>`.

    No Pydantic models: datamodel-code-generator does not take the multi-file Jane contracts (nor their
    Redocly bundle): "Modular references require an output directory". `gen-client` stays for other specs."""
    args = [contract_spec(ns.api).as_posix(), "--out", ns.out, "--no-models"]
    return run(uv_run("jane-codegen", "client", *args)).returncode


def cmd_integration(ns: argparse.Namespace) -> int:
    # Tests find the stack via JANE_STACK_FILE (jane_kit.devstack.load_stack), so they never pick up
    # another project's stack file.
    project = ns.project or default_project()
    print(f"stack project: {project}", flush=True)
    env = {"JANE_STACK_FILE": str(stack_file(project))}
    code = run(uv_run("pytest", "-m", "integration", *ns.pytest_args), env=env).returncode
    return 0 if pytest_ok(code) else code


def cmd_isolation(ns: argparse.Namespace) -> int:
    if platform.system() != "Linux":
        print("isolation tests run on Linux only (plan.md §9); skipped on", sys.platform)
        return 0
    code = run(uv_run("pytest", "-m", "isolation", *ns.pytest_args)).returncode
    return 0 if pytest_ok(code) else code


def cmd_e2e(ns: argparse.Namespace) -> int:
    code = run(uv_run("pytest", "tests/e2e", "-m", "e2e", *ns.pytest_args)).returncode
    if os.environ.get("JANE_E2E_REQUIRED") == "1":
        # Mandatory e2e (CI job e2e): no collected scenario (exit 5) is an error, not a green run;
        # tests/e2e/conftest.py also turns every skipped scenario into a failure.
        if code == 5:
            print("JANE_E2E_REQUIRED=1: no e2e scenario was collected", file=sys.stderr, flush=True)
        return code
    return 0 if pytest_ok(code) else code


def web_packages() -> list[Path]:
    web = ROOT / "web"
    return sorted(p for p in web.glob("*") if (p / "package.json").is_file()) if web.is_dir() else []


def cmd_web(_: argparse.Namespace) -> int:
    """Each web/<app> is a standalone pnpm project (own lockfile, `packageManager` pins pnpm)."""
    packages = web_packages()
    if not packages:
        print("web: no packages under web/ yet (WP-12) - skipped")
        return 0
    corepack = shutil.which("corepack")
    if corepack is None:
        print("corepack not found (Node.js 24 ships it)", file=sys.stderr)
        return 1
    for pkg in packages:
        pnpm = [corepack, "pnpm"]
        for args in (
            ["install", "--frozen-lockfile"],
            ["run", "--if-present", "lint"],
            ["run", "--if-present", "typecheck"],
            ["run", "--if-present", "test"],
            ["run", "--if-present", "build"],
        ):
            code = run([*pnpm, *args], cwd=pkg).returncode
            if code:
                return code
    return 0


def cmd_check(ns: argparse.Namespace) -> int:
    steps = [
        ("lint", cmd_lint),
        ("types", cmd_types),
        ("unit", cmd_unit),
        ("contract", cmd_contract),
        ("web", cmd_web),
    ]
    results: list[tuple[str, int, float]] = []
    for name, fn in steps:
        print(f"\n=== {name} ===", flush=True)
        start = time.monotonic()
        results.append((name, fn(ns), time.monotonic() - start))
    print("\n=== summary ===")
    for name, code, secs in results:
        print(f"  {name:<9} {'ok' if code == 0 else f'FAILED ({code})':<12} {secs:6.1f}s")
    return 0 if all(code == 0 for _, code, _ in results) else 1


def cmd_test(ns: argparse.Namespace) -> int:
    target = resolve_target(ns.target)
    args = list(ns.pytest_args)
    if "-m" not in args:
        args = ["-m", "not integration and not isolation", *args]
    code = run(uv_run("pytest", str(target.relative_to(ROOT)), *args)).returncode
    return 0 if pytest_ok(code) else code


# ----------------------------------------------------------------------------- dev stack
def default_project() -> str:
    if env := os.environ.get("JANE_COMPOSE_PROJECT"):
        return env
    slug = re.sub(r"[^a-z0-9]+", "-", ROOT.name.lower()).strip("-")[:24] or "repo"
    digest = hashlib.sha256(str(ROOT).lower().encode()).hexdigest()[:6]
    return f"jane-{slug}-{digest}"


def stack_file(project: str) -> Path:
    return STACK_DIR / f"stack-{project}.json"


PORT_VARS = {
    "postgres": ("JANE_PORT_POSTGRES", 5432),
    "sqlserver": ("JANE_PORT_SQLSERVER", 1433),
    "mongodb": ("JANE_PORT_MONGODB", 27017),
    "minio": ("JANE_PORT_MINIO", 9000),
    "minio-console": ("JANE_PORT_MINIO_CONSOLE", 9001),
    "s3": ("JANE_PORT_S3", 8333),
    "testsite": ("JANE_PORT_TESTSITE", 8080),
    "proxy": ("JANE_PORT_PROXY", 8080),
    "storage": ("JANE_PORT_STORAGE", 8000),
    "handler-runtime": ("JANE_PORT_HANDLER_RUNTIME", 8000),
    "web-collector": ("JANE_PORT_WEB_COLLECTOR", 8101),
    "telegram-collector": ("JANE_PORT_TELEGRAM_COLLECTOR", 8102),
    "orchestrator": ("JANE_PORT_ORCHESTRATOR", 8000),
    "registry": ("JANE_PORT_REGISTRY", 8000),
    "llm": ("JANE_PORT_LLM", 8110),
    "assistant": ("JANE_PORT_ASSISTANT", 8000),
}

PG_SERVICE_DATABASES = {
    "handler-runtime": ("jane_handler_runtime", "JANE_PG_HANDLER_RUNTIME_PASSWORD"),
    "orchestrator": ("jane_orchestrator", "JANE_PG_ORCHESTRATOR_PASSWORD"),
    "registry": ("jane_registry", "JANE_PG_REGISTRY_PASSWORD"),
    "llm": ("jane_llm", "JANE_PG_LLM_PASSWORD"),
    "assistant": ("jane_assistant", "JANE_PG_ASSISTANT_PASSWORD"),
    "storage-results": ("jane_storage_results", "JANE_PG_STORAGE_RESULTS_PASSWORD"),
}
DEFAULT_STACK_SERVICES = ("postgres", "sqlserver", "mongodb", "minio", "s3", "testsite", "proxy")
# ADR-0005: the stack runs in auth_mode=api_key. One key per caller identity; the services verify only the hashes
# (infra/compose.yaml). Copy of jane_kit.devstack.STACK_IDENTITIES/new_api_keys (this script is stdlib only);
# infra/tests/test_auth_config.py keeps them equal.
STACK_IDENTITIES = (
    "admin",
    "orchestrator",
    "assistant",
    "handler-runtime",
    "storage",
    "llm",
    "web-collector",
    "telegram-collector",
    "registry",
)


def api_key_var(identity: str) -> str:
    return "JANE_API_KEY_" + identity.upper().replace("-", "_")


def new_api_keys(existing: dict[str, str] | None = None) -> dict[str, str]:
    """Keys and their SHA-256 for every identity; keys already in ``existing`` are kept."""
    out: dict[str, str] = {}
    have = existing or {}
    for identity in STACK_IDENTITIES:
        var = api_key_var(identity)
        key = have.get(var) or "jk_" + secrets.token_urlsafe(32)
        out[var] = key
        out[f"{var}_SHA256"] = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return out


def load_or_create_credentials(project: str) -> dict[str, str]:
    path = stack_file(project)
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if "env" in data:
            creds = dict(data["env"])
            keys = new_api_keys(creds)
            missing = [key for _, key in PG_SERVICE_DATABASES.values() if key not in creds]
            if missing or any(creds.get(k) != v for k, v in keys.items()):
                creds.update({key: secrets.token_urlsafe(24) for key in missing})
                creds.update(keys)
                data["env"] = creds
                path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return creds
    creds = {
        "JANE_PG_USER": "jane",
        "JANE_PG_DB": "jane",
        "JANE_PG_PASSWORD": secrets.token_urlsafe(18),
        "JANE_MSSQL_SA_PASSWORD": "Jn1_" + secrets.token_hex(12),  # SQL Server complexity rules
        "JANE_MONGO_USER": "jane",
        "JANE_MONGO_PASSWORD": secrets.token_urlsafe(18),
        "JANE_MINIO_ACCESS_KEY": "jane-" + secrets.token_hex(4),
        "JANE_MINIO_SECRET_KEY": secrets.token_urlsafe(24),
        "JANE_S3_ACCESS_KEY": "jane-" + secrets.token_hex(4),
        "JANE_S3_SECRET_KEY": secrets.token_urlsafe(24),
    }
    creds.update({key: secrets.token_urlsafe(24) for _, key in PG_SERVICE_DATABASES.values()})
    creds.update(new_api_keys())
    STACK_DIR.mkdir(exist_ok=True)
    path.write_text(
        json.dumps({"project": project, "env": creds, "services": {}}, indent=2), encoding="utf-8"
    )
    return creds


def compose(
    project: str, env: dict[str, str], *args: str, capture: bool = False
) -> subprocess.CompletedProcess[str]:
    return run(["docker", "compose", "-f", str(COMPOSE_FILE), "-p", project, *args], env=env, capture=capture)


def host_port(project: str, env: dict[str, str], service: str, container_port: int) -> int | None:
    r = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "-p", project, "port", service, str(container_port)],
        cwd=ROOT,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    out = r.stdout.strip().splitlines()
    if r.returncode or not out:
        return None
    return int(out[0].rsplit(":", 1)[1])


def describe(project: str, env: dict[str, str]) -> dict[str, dict[str, object]]:
    ports = {
        name: host_port(project, env, name.replace("-console", ""), cport)
        for name, (_, cport) in PORT_VARS.items()
    }
    host = "127.0.0.1"
    services: dict[str, dict[str, object]] = {}
    if ports["postgres"]:
        services["postgres"] = {
            "host": host,
            "port": ports["postgres"],
            "user": env["JANE_PG_USER"],
            "password": env["JANE_PG_PASSWORD"],
            "database": env["JANE_PG_DB"],
            "dsn": f"postgresql://{env['JANE_PG_USER']}:{env['JANE_PG_PASSWORD']}@{host}:{ports['postgres']}/{env['JANE_PG_DB']}",
        }
    if ports["sqlserver"]:
        services["sqlserver"] = {
            "host": host,
            "port": ports["sqlserver"],
            "user": "sa",
            "password": env["JANE_MSSQL_SA_PASSWORD"],
        }
    if ports["mongodb"]:
        services["mongodb"] = {
            "host": host,
            "port": ports["mongodb"],
            "user": env["JANE_MONGO_USER"],
            "password": env["JANE_MONGO_PASSWORD"],
            "uri": f"mongodb://{env['JANE_MONGO_USER']}:{env['JANE_MONGO_PASSWORD']}@{host}:{ports['mongodb']}/?authSource=admin",
        }
    if ports["minio"]:
        services["minio"] = {
            "host": host,
            "port": ports["minio"],
            "endpoint": f"http://{host}:{ports['minio']}",
            "console": f"http://{host}:{ports['minio-console']}",
            "access_key": env["JANE_MINIO_ACCESS_KEY"],
            "secret_key": env["JANE_MINIO_SECRET_KEY"],
        }
    if ports["s3"]:
        services["s3"] = {
            "host": host,
            "port": ports["s3"],
            "endpoint": f"http://{host}:{ports['s3']}",
            "region": "us-east-1",
            "access_key": env["JANE_S3_ACCESS_KEY"],
            "secret_key": env["JANE_S3_SECRET_KEY"],
        }
    if ports["testsite"]:
        services["testsite"] = {
            "host": host,
            "port": ports["testsite"],
            "url": f"http://{host}:{ports['testsite']}",
        }
    if ports["proxy"]:
        services["proxy"] = {"host": host, "port": ports["proxy"], "url": f"http://{host}:{ports['proxy']}"}
    for name in (
        "storage",
        "handler-runtime",
        "web-collector",
        "telegram-collector",
        "orchestrator",
        "registry",
        "llm",
        "assistant",
    ):
        if port := ports[name]:
            services[name] = {"host": host, "port": port, "url": f"http://{host}:{port}"}
    if admin_key := env.get(api_key_var("admin")):
        # ADR-0005: the operator's key for the admin UI (login page) and API calls through the proxy.
        services["auth"] = {"mode": "api_key", "admin_api_key": admin_key}
    if pg_port := ports["postgres"]:
        for name, (database, password_key) in PG_SERVICE_DATABASES.items():
            services[f"db-{name}"] = {
                "host": host,
                "port": pg_port,
                "endpoint": f"postgresql://{host}:{pg_port}/{database}",
                "db_user": database,
                "db_password": env[password_key],
                "db_name": database,
                "db_dsn": f"postgresql://{database}:{env[password_key]}@{host}:{pg_port}/{database}",
            }
    return services


def cmd_up(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    env = load_or_create_credentials(project)
    admin_dist = ROOT / "web" / "admin" / "dist"
    if admin_dist.is_dir():
        env["JANE_ADMIN_DIST_PATH"] = str(admin_dist)
    args = ["up", "-d", "--wait", "--wait-timeout", str(ns.wait_timeout)]
    if not ns.no_build:
        args.append("--build")
    selected = list(ns.services) or list(DEFAULT_STACK_SERVICES)
    if "pg-provision" in selected:
        selected.remove("pg-provision")
        if "postgres" not in selected:
            selected.append("postgres")
    code = compose(project, env, *args, *selected).returncode
    db_apps = set(PG_SERVICE_DATABASES) - {"storage-results"}
    if code == 0 and "postgres" in selected and not (db_apps | {"storage"}) & set(selected):
        # `up --wait` treats a successful one-shot target as a failure. For infrastructure-only
        # starts, wait for postgres first, then run the idempotent provisioner to completion.
        code = compose(project, env, "run", "--rm", "--no-deps", "pg-provision").returncode
    services = describe(project, env)
    stack_file(project).write_text(
        json.dumps(
            {"project": project, "compose_file": str(COMPOSE_FILE), "env": env, "services": services},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nproject: {project}   (stack file: {stack_file(project).relative_to(ROOT).as_posix()})")
    for name, info in services.items():
        if name == "auth":  # never print the key itself here; `just env` shows it on request
            print(f"  {name:<10} api_key (admin key: `just env` -> JANE_STACK_AUTH_ADMIN_API_KEY)")
            continue
        print(f"  {name:<10} {info.get('url') or info.get('endpoint') or f'{info["host"]}:{info["port"]}'}")
    if code:
        print(
            f"\n`docker compose up` failed ({code}); see `just logs`. Clean up: just down -v", file=sys.stderr
        )
    return code


def cmd_down(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    path = stack_file(project)
    env = json.loads(path.read_text(encoding="utf-8")).get("env", {}) if path.is_file() else {}
    for var in (
        "JANE_PG_PASSWORD",
        "JANE_MSSQL_SA_PASSWORD",
        "JANE_MONGO_PASSWORD",
        "JANE_MINIO_SECRET_KEY",
        "JANE_S3_SECRET_KEY",
        *(key for _, key in PG_SERVICE_DATABASES.values()),
        *(f"{api_key_var(i)}{suffix}" for i in STACK_IDENTITIES for suffix in ("", "_SHA256")),
    ):
        env.setdefault(var, "unused")
    # -v also removes locally built images (<project>-testsite) so they do not pile up.
    args = ["down", "--remove-orphans"] + (["-v", "--rmi", "local"] if ns.volumes else [])
    code = compose(project, env, "--profile", "*", *args).returncode
    if ns.volumes and code == 0 and path.is_file():
        path.unlink()
    return code


def _stack_env(project: str) -> dict[str, str]:
    path = stack_file(project)
    if not path.is_file():
        sys.exit(f"no stack for project {project}; run `just up` first")
    return dict(json.loads(path.read_text(encoding="utf-8"))["env"])


def cmd_ps(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    return compose(project, _stack_env(project), "--profile", "*", "ps").returncode


def cmd_logs(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    return compose(
        project, _stack_env(project), "--profile", "*", "logs", "--tail", str(ns.tail), *ns.services
    ).returncode


def cmd_env(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    path = stack_file(project)
    if not path.is_file():
        sys.exit(f"no stack for project {project}; run `just up` first")
    data = json.loads(path.read_text(encoding="utf-8"))
    if ns.format == "json":
        print(json.dumps(data["services"], indent=2))
        return 0
    print(f"JANE_STACK_FILE={path}")
    for svc, info in data["services"].items():
        for key, value in info.items():
            print(f"JANE_STACK_{svc.upper().replace('-', '_')}_{key.upper()}={value}")
    return 0


# ----------------------------------------------------------------------------- scaffolding
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SKIP_DIRS = {".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}


def render(text: str, name: str) -> str:
    snake = name.replace("-", "_")
    title = " ".join(part.capitalize() for part in name.split("-"))
    pascal = "".join(part.capitalize() for part in name.split("-"))
    for old, new in (
        ("templates/service", f"services/{name}"),
        ("jane-template-service", f"jane-{name}"),
        ("jane_template_service", f"jane_{snake}"),
        ("JANE_TEMPLATE_SERVICE_", f"JANE_{snake.upper()}_"),
        ("template-service", name),
        ("Template Service", title),
        ("TemplateService", pascal),
    ):
        text = text.replace(old, new)
    return text


def new_service(name: str, dest_root: Path, template: Path | None = None) -> Path:
    if not NAME_RE.match(name):
        raise SystemExit(
            f"invalid service name {name!r}: use lowercase words separated by '-' (e.g. web-collector)"
        )
    template = template or ROOT / "templates" / "service"
    dest = dest_root / name
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    for src in sorted(template.rglob("*")):
        rel_parts = src.relative_to(template).parts
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in rel_parts):
            continue
        target = dest / Path(*(render(part, name) for part in rel_parts))
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, target)
            continue
        target.write_text(render(text, name), encoding="utf-8", newline="\n")
    return dest


def cmd_new_service(ns: argparse.Namespace) -> int:
    dest = new_service(ns.name, ROOT / "services")
    print(f"created {dest.relative_to(ROOT).as_posix()}")
    code = run(["uv", "lock"]).returncode
    print(
        f"next: just test {ns.name}   |   uv run --package jane-{ns.name} python -m jane_{ns.name.replace('-', '_')}"
    )
    return code


# ----------------------------------------------------------------------------- misc
HOOK = """#!/bin/sh
# Installed by `just hooks` (Jane). Blocks commits that contain secrets.
if command -v gitleaks >/dev/null 2>&1; then
    exec gitleaks git --pre-commit --staged --redact --no-banner --verbose
fi
echo "jane pre-commit: gitleaks not found - secret scan skipped (install: https://github.com/gitleaks/gitleaks)" >&2
exit 0
"""


def install_hook(repo: Path) -> Path:
    hooks_dir = Path(
        subprocess.run(
            ["git", "rev-parse", "--git-path", "hooks"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    if not hooks_dir.is_absolute():
        hooks_dir = repo / hooks_dir
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook = hooks_dir / "pre-commit"
    if hook.exists() and "Jane" not in hook.read_text(encoding="utf-8", errors="replace"):
        backup = hook.with_name("pre-commit.local")
        hook.replace(backup)
        print(f"existing hook saved as {backup}")
    hook.write_text(HOOK, encoding="utf-8", newline="\n")
    hook.chmod(0o755)
    return hook


def cmd_hooks(_: argparse.Namespace) -> int:
    hook = install_hook(ROOT)
    print(f"installed {hook}")
    return 0


def cmd_testsite(ns: argparse.Namespace) -> int:
    return run(
        uv_run("python", "-m", "jane_testsite", "--host", ns.host, "--port", str(ns.port), "--verbose")
    ).returncode


def cmd_gen_client(ns: argparse.Namespace) -> int:
    return run(uv_run("jane-codegen", "client", ns.spec, "--out", ns.out)).returncode


# ----------------------------------------------------------------------------- CLI
def from_just(argv: list[str]) -> list[str]:
    """``just`` calls ``dev.py --just <recipe line> <recipe name> <args...>`` (see justfile)."""
    if argv[:1] != ["--just"]:
        return argv
    line, rest = argv[1].split(), argv[3:]
    if line == ["list"]:
        just = shutil.which("just") or os.environ.get("JUST_EXECUTABLE")
        if just is None:
            sys.exit("run `just --list` to see the recipes")
        sys.exit(subprocess.run([just, "--list", "--unsorted"], cwd=ROOT, check=False).returncode)
    return line + rest


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="dev", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, fn: object, help_: str, pytest_args: bool = False) -> argparse.ArgumentParser:
        # Commands with pytest_args pass every unknown argument to pytest unchanged
        # (`just unit -v -k limits`), no `--` needed.
        p = sub.add_parser(name, help=help_ + (" (unknown arguments go to pytest)" if pytest_args else ""))
        p.set_defaults(fn=fn, takes_pytest_args=pytest_args)
        return p

    add("sync", cmd_sync, "uv sync --all-packages")
    add("lint", cmd_lint, "ruff check + format check + contracts lint")
    add("fmt", cmd_fmt, "ruff fix + format")
    add("types", cmd_types, "mypy for workspace members, scripts, infra/tests, examples, deploy/profiles")
    add("unit", cmd_unit, "unit tests", True)
    add("contract", cmd_contract, "contracts lint + contract tests", True)
    p = add("integration", cmd_integration, "integration tests (need `just up`)", True)
    p.add_argument("--project", help="compose project of the stack (default: unique per checkout)")
    add("isolation", cmd_isolation, "sandbox isolation tests (Linux only)", True)
    add("e2e", cmd_e2e, "end-to-end acceptance tests (Docker)", True)
    add("web", cmd_web, "pnpm install/lint/typecheck/test for web/* (if present)")
    add("check", cmd_check, "lint + types + unit + contract (+ web)", True)
    p = add("test", cmd_test, "tests of one service/library", True)
    p.add_argument("target")

    for name, fn, help_ in (
        ("up", cmd_up, "start the dev stack"),
        ("down", cmd_down, "stop the dev stack"),
        ("ps", cmd_ps, "stack status"),
        ("logs", cmd_logs, "stack logs"),
        ("env", cmd_env, "print stack endpoints and credentials"),
    ):
        p = add(name, fn, help_)
        p.add_argument("--project", "-p", help="compose project name (default: unique per checkout)")
        if name == "up":
            p.add_argument("services", nargs="*")
            p.add_argument("--no-build", action="store_true")
            p.add_argument(
                "--wait-timeout", type=int, default=int(os.environ.get("JANE_UP_WAIT_TIMEOUT", "600"))
            )
        if name == "down":
            p.add_argument(
                "--volumes", "-v", action="store_true", help="also remove volumes and the stack file"
            )
        if name == "logs":
            p.add_argument("services", nargs="*")
            p.add_argument("--tail", type=int, default=200)
        if name == "env":
            p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")

    p = add("new-service", cmd_new_service, "create services/<name> from templates/service")
    p.add_argument("name")
    add("hooks", cmd_hooks, "install the git pre-commit hook (gitleaks)")
    p = add("testsite", cmd_testsite, "run the test site locally")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p = add("gen-client", cmd_gen_client, "generate a client package from an OpenAPI contract")
    p.add_argument("spec")
    p.add_argument("out")

    p = add("contracts-check", cmd_contracts_check, "contracts linter (contracts/tools/check_contracts.py)")
    p.add_argument("--redocly", action="store_true", help="also require the Redocly lint (Node/npx)")
    p = add("contracts-compat", cmd_contracts_compat, "compat.py self-test + compatibility against a git ref")
    p.add_argument("base", nargs="?", default="main", help="git ref to compare with (default: main)")
    p.add_argument("--oasdiff", action="store_true", help="also run oasdiff breaking (binary or Docker)")
    p = add("contracts-mock", cmd_contracts_mock, "example-driven mock of one API (contracts/tools/mock.py)")
    p.add_argument("api", help="collector | handler | storage | registry | orchestrator | llm | assistant")
    p.add_argument("--port", type=int, default=4010)
    p.add_argument("--host", default="127.0.0.1")
    p = add("contracts-gen", cmd_contracts_gen, "Python client of one contract (jane-codegen client)")
    p.add_argument("api", help="contract name: contracts/openapi/<api>.v1.yaml")
    p.add_argument("out", help="output package directory, e.g. services/<me>/src/<pkg>/_generated/<api>")

    ns, extra = ap.parse_known_args(from_just(list(sys.argv[1:] if argv is None else argv)))
    extra = [a for a in extra if a != "--"]
    if extra and not ns.takes_pytest_args:
        ap.error(f"unrecognized arguments: {' '.join(extra)}")
    ns.pytest_args = extra
    return int(ns.fn(ns))


if __name__ == "__main__":
    sys.exit(main())
