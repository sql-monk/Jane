"""Jane developer commands (cross-platform; stdlib only). Usually called through `just`.

    uv run --no-project python scripts/dev.py <command> [args]

Commands: check, lint, fmt, types, unit, contract, test, integration, isolation, web,
          up, down, ps, logs, env, new-service, hooks, testsite, gen-client, sync.
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
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "infra" / "compose.yaml"
STACK_DIR = ROOT / ".jane"
UNIT_MARKERS = "not contract and not integration and not isolation"

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
    out: list[Path] = []
    for pattern in ("libs/*", "services/*", "templates/service", "tests/fixtures/testsite"):
        out += [p for p in sorted(ROOT.glob(pattern)) if (p / "pyproject.toml").is_file()]
    return out


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


def has_web() -> bool:
    return (
        any((p / "package.json").is_file() for p in (ROOT / "web").glob("*"))
        if (ROOT / "web").is_dir()
        else False
    )


# ----------------------------------------------------------------------------- quality
def cmd_sync(_: argparse.Namespace) -> int:
    return run(["uv", "sync", "--all-packages"]).returncode


def cmd_lint(_: argparse.Namespace) -> int:
    codes = [
        run(uv_run("ruff", "check", ".")).returncode,
        run(uv_run("ruff", "format", "--check", ".")).returncode,
        run(uv_run("python", "scripts/contracts_lint.py")).returncode,
    ]
    return max(codes)


def cmd_fmt(_: argparse.Namespace) -> int:
    run(uv_run("ruff", "check", "--fix", "."))
    return run(uv_run("ruff", "format", ".")).returncode


def cmd_types(_: argparse.Namespace) -> int:
    code = 0
    for m in members():
        targets = [str(p.relative_to(ROOT)) for p in (m / "src", m / "tests") if p.is_dir()]
        if targets:
            code = max(code, run(uv_run("mypy", *targets)).returncode)
    code = max(code, run(uv_run("mypy", "scripts")).returncode)
    return code


def cmd_unit(ns: argparse.Namespace) -> int:
    code = run(uv_run("pytest", "-m", UNIT_MARKERS, *ns.pytest_args)).returncode
    return 0 if pytest_ok(code) else code


def cmd_contract(ns: argparse.Namespace) -> int:
    lint = run(uv_run("python", "scripts/contracts_lint.py")).returncode
    code = run(uv_run("pytest", "-m", "contract", *ns.pytest_args)).returncode
    return max(lint, 0 if pytest_ok(code) else code)


def cmd_integration(ns: argparse.Namespace) -> int:
    code = run(uv_run("pytest", "-m", "integration", *ns.pytest_args)).returncode
    return 0 if pytest_ok(code) else code


def cmd_isolation(ns: argparse.Namespace) -> int:
    if platform.system() != "Linux":
        print("isolation tests run on Linux only (plan.md §9); skipped on", sys.platform)
        return 0
    code = run(uv_run("pytest", "-m", "isolation", *ns.pytest_args)).returncode
    return 0 if pytest_ok(code) else code


def cmd_web(_: argparse.Namespace) -> int:
    if not has_web():
        print("web: no packages under web/ yet (WP-12) - skipped")
        return 0
    corepack = shutil.which("corepack")
    if corepack is None:
        print("corepack not found (Node.js 24 ships it)", file=sys.stderr)
        return 1
    pnpm = [corepack, "pnpm"]
    for args in (
        ["install", "--frozen-lockfile"],
        ["-r", "--if-present", "lint"],
        ["-r", "--if-present", "typecheck"],
        ["-r", "--if-present", "test"],
    ):
        code = run([*pnpm, *args]).returncode
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
}


def load_or_create_credentials(project: str) -> dict[str, str]:
    path = stack_file(project)
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if "env" in data:
            return dict(data["env"])
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
    return services


def cmd_up(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    env = load_or_create_credentials(project)
    args = ["up", "-d", "--wait", "--wait-timeout", str(ns.wait_timeout)]
    if not ns.no_build:
        args.append("--build")
    code = compose(project, env, *args, *ns.services).returncode
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
    ):
        env.setdefault(var, "unused")
    args = ["down", "--remove-orphans"] + (["-v"] if ns.volumes else [])
    code = compose(project, env, *args).returncode
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
    return compose(project, _stack_env(project), "ps").returncode


def cmd_logs(ns: argparse.Namespace) -> int:
    project = ns.project or default_project()
    return compose(project, _stack_env(project), "logs", "--tail", str(ns.tail), *ns.services).returncode


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
def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="dev", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, fn: object, help_: str, pytest_args: bool = False) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_)
        p.set_defaults(fn=fn)
        if pytest_args:
            p.add_argument("pytest_args", nargs=argparse.REMAINDER, help="extra pytest arguments")
        return p

    add("sync", cmd_sync, "uv sync --all-packages")
    add("lint", cmd_lint, "ruff check + format check + contracts lint")
    add("fmt", cmd_fmt, "ruff fix + format")
    add("types", cmd_types, "mypy for every workspace member")
    add("unit", cmd_unit, "unit tests", True)
    add("contract", cmd_contract, "contracts lint + contract tests", True)
    add("integration", cmd_integration, "integration tests (need `just up`)", True)
    add("isolation", cmd_isolation, "sandbox isolation tests (Linux only)", True)
    add("web", cmd_web, "pnpm install/lint/typecheck/test for web/* (if present)")
    add("check", cmd_check, "lint + types + unit + contract (+ web)", True)
    p = add("test", cmd_test, "tests of one service/library")
    p.add_argument("target")
    p.add_argument("pytest_args", nargs=argparse.REMAINDER, help="extra pytest arguments")

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

    ns = ap.parse_args(argv)
    if getattr(ns, "pytest_args", None) and ns.pytest_args[:1] == ["--"]:
        ns.pytest_args = ns.pytest_args[1:]
    return int(ns.fn(ns))


if __name__ == "__main__":
    sys.exit(main())
