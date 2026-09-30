"""An isolated Jane stack with one limits profile applied to every service (WP-14).

    uv run --all-packages python deploy/profiles/stack.py up [--project NAME] [--profile dev-laptop] [--probe]
    uv run --all-packages python deploy/profiles/stack.py env [--project NAME]         # URLs (no secrets)
    uv run --all-packages python deploy/profiles/stack.py down [--project NAME]        # containers, volumes, images
    uv run --all-packages python deploy/profiles/stack.py leftovers [--project NAME]   # exit 1 if anything remains

Compose files: ``infra/compose.yaml`` (WP-01) + ``deploy/profiles/compose.stack.yaml`` (this WP). Isolation
(plan.md §3.4): a unique compose project, host ports chosen by Docker on 127.0.0.1, generated credentials,
project-prefixed volumes and images. The stack file ``.jane/stack-<project>.json`` has the shape written by
``just up`` (``env`` + ``services``), so ``just env --project <project>`` and ``jane_kit.devstack`` read it too.
Stdlib only; works on Windows (Docker Desktop) and Linux.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROFILES_DIR = Path(__file__).resolve().parent
INFRA_COMPOSE = ROOT / "infra" / "compose.yaml"
STACK_COMPOSE = PROFILES_DIR / "compose.stack.yaml"
STACK_DIR = ROOT / ".jane"
PROFILES = ("dev-laptop", "ci", "single-node")
# The chain of the catalog / price-check examples; `--services` adds more (e.g. telegram-collector).
DEFAULT_SERVICES = ("testsite", "registry", "storage", "handler-runtime", "web-collector", "orchestrator")
APP_SERVICES = frozenset(
    {
        "storage",
        "handler-runtime",
        "web-collector",
        "telegram-collector",
        "orchestrator",
        "registry",
        "llm",
        "assistant",
    }
)
CONTAINER_PORTS = {
    "testsite": 8080,
    "proxy": 8080,
    "postgres": 5432,
    "minio": 9000,
    "storage": 8000,
    "handler-runtime": 8000,
    "web-collector": 8101,
    "telegram-collector": 8102,
    "orchestrator": 8000,
    "registry": 8000,
    "llm": 8110,
    "assistant": 8000,
    "probe-site": 8080,
}
PG_PASSWORD_KEYS = (
    "JANE_PG_HANDLER_RUNTIME_PASSWORD",
    "JANE_PG_ORCHESTRATOR_PASSWORD",
    "JANE_PG_REGISTRY_PASSWORD",
    "JANE_PG_LLM_PASSWORD",
    "JANE_PG_ASSISTANT_PASSWORD",
    "JANE_PG_STORAGE_RESULTS_PASSWORD",
)
SANDBOX_LABEL = "io.jane.stack"
RECORDINGS = ROOT / "examples" / "telegram" / "recordings"
# Executors the orchestrator gets for each service of the stack (orchestrator.v1 Executor, README of WP-09).
EXECUTORS: dict[str, list[dict[str, Any]]] = {
    "web-collector": [
        {
            "executor": "web-collector",
            "role": "collector",
            "base_url": "http://web-collector:8101",
            "capabilities": {"collector": "web"},
            "sync_connections": False,
        }
    ],
    "telegram-collector": [
        {
            "executor": "telegram-collector",
            "role": "collector",
            "base_url": "http://telegram-collector:8102",
            "capabilities": {"collector": "telegram"},
            # telegram_account connections are pushed only for the real backend (recorded needs none).
            "sync_connections": False,
        }
    ],
    "storage": [
        {
            "executor": "storage",
            "role": "handler",
            "base_url": "http://storage:8000",
            "capabilities": {"packages": ["jane.storage-*"]},
        },
        {
            "executor": "storage-read",
            "role": "storage_read",
            "base_url": "http://storage:8000",
            "sync_connections": False,
        },
    ],
    "handler-runtime": [
        {
            "executor": "handler-runtime",
            "role": "handler",
            "base_url": "http://handler-runtime:8000",
            "capabilities": {"default": True, "handler_kinds": ["extractor", "transform"]},
            "sync_connections": False,
        }
    ],
    "registry": [{"executor": "registry", "role": "registry", "base_url": "http://registry:8000"}],
}


def executors_for(services: Sequence[str], *, telegram_backend: str = "recorded") -> list[dict[str, Any]]:
    out = [dict(e) for name in services for e in EXECUTORS.get(name, [])]
    for e in out:
        if e["executor"] == "telegram-collector" and telegram_backend != "recorded":
            e["sync_connections"] = True
    return out


class StackError(RuntimeError):
    """A docker / compose command failed."""


def default_project(root: Path = ROOT) -> str:
    if env := os.environ.get("JANE_STACK_PROJECT"):
        return env
    return "jane-stack-" + hashlib.sha256(str(root).lower().encode()).hexdigest()[:6]


def profile_path(profile: str) -> Path:
    path = PROFILES_DIR / f"{profile}.json"
    if not path.is_file():
        raise SystemExit(f"unknown profile {profile!r}: expected one of {', '.join(PROFILES)}")
    return path


def stack_file(project: str) -> Path:
    return STACK_DIR / f"stack-{project}.json"


def sandbox_image(project: str) -> str:
    return f"{project}-python-extractor:1"


def executors_file(project: str) -> Path:
    return STACK_DIR / f"executors-{project}.json"


def recordings_dir(project: str) -> Path:
    """Writable copy of the Telegram recordings of this stack (the example edits it between runs)."""
    return STACK_DIR / f"telegram-recordings-{project}"


def new_credentials() -> dict[str, str]:
    """Random credentials of one stack (the same keys as `just up`); stored only in the ignored stack file."""
    creds = {
        "JANE_PG_USER": "jane",
        "JANE_PG_DB": "jane",
        "JANE_PG_PASSWORD": secrets.token_urlsafe(18),
        "JANE_MSSQL_SA_PASSWORD": "Jn1_" + secrets.token_hex(12),
        "JANE_MONGO_USER": "jane",
        "JANE_MONGO_PASSWORD": secrets.token_urlsafe(18),
        "JANE_MINIO_ACCESS_KEY": "jane-" + secrets.token_hex(4),
        "JANE_MINIO_SECRET_KEY": secrets.token_urlsafe(24),
        "JANE_S3_ACCESS_KEY": "jane-" + secrets.token_hex(4),
        "JANE_S3_SECRET_KEY": secrets.token_urlsafe(24),
    }
    creds.update({key: secrets.token_urlsafe(24) for key in PG_PASSWORD_KEYS})
    return creds


def read_stack(project: str) -> dict[str, Any] | None:
    path = stack_file(project)
    if not path.is_file():
        return None
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def write_stack(project: str, data: Mapping[str, Any]) -> None:
    STACK_DIR.mkdir(exist_ok=True)
    stack_file(project).write_text(json.dumps(dict(data), indent=2), encoding="utf-8")


def service_urls(project: str) -> dict[str, str]:
    """``{service: base URL}`` of a running stack, from its stack file."""
    data = read_stack(project)
    if data is None:
        raise SystemExit(f"no stack {project!r}: run `deploy/profiles/stack.py up --project {project}` first")
    return {name: str(info["url"]) for name, info in data.get("services", {}).items() if "url" in info}


class Stack:
    def __init__(self, project: str, profile: str = "dev-laptop", *, verbose: bool = True) -> None:
        self.project = project
        self.profile = profile
        self.verbose = verbose
        data = read_stack(project) or {}
        env = dict(data.get("env") or {})
        if not all(k in env for k in ("JANE_PG_PASSWORD", *PG_PASSWORD_KEYS)):
            env = new_credentials()
        self.creds = env

    # ------------------------------------------------------------------ environment
    def env(self) -> dict[str, str]:
        return {
            **self.creds,
            "JANE_PROFILE_FILE": profile_path(self.profile).as_posix(),
            "JANE_SANDBOX_IMAGE": sandbox_image(self.project),
            "JANE_STACK_PROJECT": self.project,
            "JANE_DOCKER_SOCKET": os.environ.get("JANE_DOCKER_SOCKET", "/var/run/docker.sock"),
            "JANE_DOCKER_GID": os.environ.get("JANE_DOCKER_GID", self.creds.get("JANE_DOCKER_GID", "0")),
            "JANE_EXECUTORS_FILE": executors_file(self.project).resolve().as_posix(),
            "JANE_TELEGRAM_RECORDINGS_DIR": recordings_dir(self.project).resolve().as_posix(),
        }

    def run(
        self, cmd: Sequence[str], *, check: bool = True, timeout: float | None = None, quiet: bool = False
    ) -> subprocess.CompletedProcess[str]:
        if self.verbose and not quiet:
            print("$ " + " ".join(cmd), file=sys.stderr, flush=True)
        r = subprocess.run(  # noqa: S603 - fixed docker/python command lines built by this module
            list(cmd),
            cwd=ROOT,
            env={**os.environ, **self.env()},
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if check and r.returncode != 0:
            raise StackError(f"{' '.join(cmd)} -> exit {r.returncode}\n{(r.stderr or r.stdout)[-4000:]}")
        return r

    def compose(self, *args: str, **kw: Any) -> subprocess.CompletedProcess[str]:
        base = ["docker", "compose", "-f", str(INFRA_COMPOSE), "-f", str(STACK_COMPOSE), "-p", self.project]
        return self.run([*base, *args], **kw)

    # ------------------------------------------------------------------ lifecycle
    def up(self, services: Sequence[str], *, wait_timeout_s: int = 900) -> dict[str, str]:
        if "handler-runtime" in services:
            self._prepare_sandbox()
        apps = sorted(APP_SERVICES & set(services))
        profiles = [*apps, *(["limits-probe"] if "probe-site" in services else [])]
        os.environ["COMPOSE_PROFILES"] = ",".join(profiles)
        STACK_DIR.mkdir(exist_ok=True)
        backend = os.environ.get("JANE_TELEGRAM_BACKEND", "recorded")
        executors_file(self.project).write_text(
            json.dumps(executors_for(services, telegram_backend=backend), indent=2), encoding="utf-8"
        )
        recordings = recordings_dir(self.project)
        recordings.mkdir(exist_ok=True)
        for path in sorted(RECORDINGS.glob("*.json")):
            if not (recordings / path.name).exists():
                shutil.copyfile(path, recordings / path.name)
        self._save({})
        self.compose(
            "up",
            "-d",
            "--build",
            "--wait",
            "--wait-timeout",
            str(wait_timeout_s),
            *services,
            timeout=wait_timeout_s + 1800,
        )
        urls = {name: f"http://127.0.0.1:{self.host_port(name)}" for name in services}
        self._save({name: {"host": "127.0.0.1", "url": url} for name, url in urls.items()})
        return urls

    def _save(self, services: Mapping[str, Any]) -> None:
        write_stack(
            self.project,
            {
                "project": self.project,
                "compose_file": str(INFRA_COMPOSE),
                "compose_overlay": str(STACK_COMPOSE),
                "profile": self.profile,
                "env": self.creds,
                "services": dict(services),
            },
        )

    def host_port(self, service: str) -> int:
        r = self.compose("port", service, str(CONTAINER_PORTS[service]), quiet=True)
        lines = r.stdout.strip().splitlines()
        if not lines:
            raise StackError(f"{service}: no published port")
        return int(lines[0].rsplit(":", 1)[1])

    def _prepare_sandbox(self) -> None:
        image = sandbox_image(self.project)
        if self.run(["docker", "image", "inspect", image], check=False, quiet=True).returncode != 0:
            cli = [sys.executable, "-m", "jane_handler_runtime.cli", "build-image", "--tag", image]
            self.run(cli, timeout=1800)
        if "JANE_DOCKER_GID" not in os.environ:
            sock = self.env()["JANE_DOCKER_SOCKET"]
            probe = "import os; print(os.stat('/var/run/docker.sock').st_gid)"
            r = self.run(
                ["docker", "run", "--rm", "-v", f"{sock}:/var/run/docker.sock", image, "python", "-c", probe]
            )
            self.creds["JANE_DOCKER_GID"] = r.stdout.strip().splitlines()[-1]

    def down(self) -> None:
        os.environ["COMPOSE_PROFILES"] = "*"
        self.compose("--profile", "*", "down", "--remove-orphans", "-v", "--rmi", "local", timeout=900)
        for cid in self._ids(
            ["docker", "ps", "-a", "-q", "--filter", f"label={SANDBOX_LABEL}={self.project}"]
        ):
            self.run(["docker", "rm", "-f", cid], check=False)
        self.run(["docker", "image", "rm", "-f", sandbox_image(self.project)], check=False)
        stack_file(self.project).unlink(missing_ok=True)
        executors_file(self.project).unlink(missing_ok=True)
        shutil.rmtree(recordings_dir(self.project), ignore_errors=True)

    def _ids(self, cmd: Sequence[str]) -> list[str]:
        r = self.run(cmd, check=False, quiet=True)
        return [line.strip() for line in r.stdout.splitlines() if line.strip()]

    def leftovers(self) -> dict[str, list[str]]:
        label = f"label=com.docker.compose.project={self.project}"
        images = self._ids(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"])
        return {
            "containers": self._ids(["docker", "ps", "-a", "--filter", label, "--format", "{{.Names}}"]),
            "sandboxes": self._ids(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    f"label={SANDBOX_LABEL}={self.project}",
                    "--format",
                    "{{.Names}}",
                ]
            ),
            "volumes": self._ids(["docker", "volume", "ls", "-q", "--filter", label]),
            "networks": self._ids(["docker", "network", "ls", "-q", "--filter", label]),
            "images": [i for i in images if i.startswith(f"{self.project}-")],
            "files": [
                str(p)
                for p in (
                    stack_file(self.project),
                    executors_file(self.project),
                    recordings_dir(self.project),
                )
                if p.exists()
            ],
        }


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="stack.py", description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    ap.add_argument("command", choices=["up", "env", "down", "leftovers"])
    ap.add_argument("--project", default=None, help="compose project (default: jane-stack-<checkout hash>)")
    ap.add_argument(
        "--profile", default="dev-laptop", choices=PROFILES, help="limits profile (default dev-laptop)"
    )
    ap.add_argument("--services", nargs="*", default=None, help=f"default: {' '.join(DEFAULT_SERVICES)}")
    ap.add_argument("--probe", action="store_true", help="also start probe-site of the limits harness")
    ap.add_argument(
        "--telegram", action="store_true", help="also start telegram-collector (recorded backend)"
    )
    ap.add_argument("--wait-timeout", type=int, default=900, help="seconds for health checks (default 900)")
    ns = ap.parse_args(argv)
    project = ns.project or default_project()
    stack = Stack(project, ns.profile)
    if ns.command == "up":
        services = list(ns.services or DEFAULT_SERVICES)
        services += (["telegram-collector"] if ns.telegram else []) + (["probe-site"] if ns.probe else [])
        urls = stack.up(services, wait_timeout_s=ns.wait_timeout)
        print(f"project: {project}   profile: {ns.profile}   stack file: {stack_file(project).as_posix()}")
        for name, url in urls.items():
            print(f"  {name:<18} {url}")
        return 0
    if ns.command == "env":
        for name, url in service_urls(project).items():
            print(f"{name}={url}")
        return 0
    if ns.command == "down":
        stack.down()
    left = stack.leftovers()
    remaining = {k: v for k, v in left.items() if v}
    print(json.dumps({"project": project, "leftovers": remaining}, indent=2))
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
