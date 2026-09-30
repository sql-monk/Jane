"""The Jane stack for end-to-end tests: `infra/compose.yaml` + the overlay `tests/e2e/compose.e2e.yaml`.

Isolation (plan.md §3.4): a unique compose project (``JANE_E2E_PROJECT`` or ``jane-e2e-<checkout hash>``),
host ports chosen by Docker, generated credentials, project-prefixed volumes and images. The stack file
``.jane/stack-<project>.json`` has the same shape as the one written by ``just up``, so
``jane_kit.devstack.load_stack(project)`` and ``just env --project <project>`` work for it too.

Application services join the stack only when their directory exists in this checkout (they are enabled
through compose profiles); otherwise :meth:`E2EStack.missing` explains which WP has not been merged yet.
Services are started lazily - a scenario brings up only what it needs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = ["SERVICES", "E2EStack", "ServiceSpec", "StackError"]

ROOT = Path(__file__).resolve().parents[3]
INFRA_COMPOSE = ROOT / "infra" / "compose.yaml"
E2E_COMPOSE = ROOT / "tests" / "e2e" / "compose.e2e.yaml"
STACK_DIR = ROOT / ".jane"
CREDENTIAL_KEYS = (
    "JANE_PG_USER",
    "JANE_PG_DB",
    "JANE_PG_PASSWORD",
    "JANE_PG_HANDLER_RUNTIME_PASSWORD",
    "JANE_PG_ORCHESTRATOR_PASSWORD",
    "JANE_PG_REGISTRY_PASSWORD",
    "JANE_PG_LLM_PASSWORD",
    "JANE_PG_ASSISTANT_PASSWORD",
    "JANE_PG_STORAGE_RESULTS_PASSWORD",
    "JANE_MSSQL_SA_PASSWORD",
    "JANE_MONGO_USER",
    "JANE_MONGO_PASSWORD",
    "JANE_MINIO_ACCESS_KEY",
    "JANE_MINIO_SECRET_KEY",
    "JANE_S3_ACCESS_KEY",
    "JANE_S3_SECRET_KEY",
)


class StackError(RuntimeError):
    """A docker / compose command failed."""


@dataclass(frozen=True)
class ServiceSpec:
    """A service of the full stack.

    ``requires`` - paths (relative to the checkout root) that must exist for the service to be available;
    ``compose`` - False for services that are not yet described in any compose file (the overlay gets an
    entry when the WP is merged, WP-13 phase M1/M2).
    """

    name: str
    wp: str
    port: int
    kind: str  # "infra" | "app"
    requires: tuple[str, ...] = ()
    compose: bool = True
    depends: tuple[str, ...] = ()
    note: str = ""


SERVICES: dict[str, ServiceSpec] = {
    s.name: s
    for s in (
        # Infrastructure of WP-01 (infra/compose.yaml).
        ServiceSpec("postgres", "WP-01", 5432, "infra"),
        ServiceSpec("sqlserver", "WP-01", 1433, "infra"),
        ServiceSpec("mongodb", "WP-01", 27017, "infra"),
        ServiceSpec("minio", "WP-01", 9000, "infra"),
        ServiceSpec("s3", "WP-01", 8333, "infra", note="SeaweedFS - S3-compatible substitute"),
        ServiceSpec("testsite", "WP-01", 8080, "infra"),
        ServiceSpec("proxy", "WP-01", 8080, "infra"),
        # Application services (tests/e2e/compose.e2e.yaml, compose profile == service name).
        ServiceSpec("storage", "WP-07", 8000, "app", ("services/storage/Dockerfile",), depends=("postgres",)),
        ServiceSpec(
            "handler-runtime",
            "WP-06",
            8000,
            "app",
            ("services/handler-runtime/Dockerfile",),
            depends=("postgres",),
        ),
        ServiceSpec(
            "web-collector",
            "WP-02",
            8101,
            "app",
            ("services/web-collector/Dockerfile",),
            depends=("testsite",),
        ),
        ServiceSpec(
            "telegram-collector",
            "WP-04",
            8102,
            "app",
            ("services/telegram-collector/Dockerfile",),
        ),
        ServiceSpec("registry", "WP-05", 8000, "app", ("services/registry/Dockerfile",)),
        ServiceSpec(
            "orchestrator", "WP-09", 8000, "app", ("services/orchestrator/Dockerfile",), depends=("postgres",)
        ),
        # STAND-IN for the registry (WP-05) serving LOCAL package archives - see jane_e2e/package_host.py.
        ServiceSpec("package-host", "WP-13", 8080, "app", ("tests/e2e/jane_e2e/package_host.py",)),
        ServiceSpec("llm", "WP-10", 8110, "app", ("services/llm/Dockerfile",), depends=("postgres",)),
        ServiceSpec(
            "assistant", "WP-11", 8000, "app", ("services/assistant/Dockerfile",), depends=("postgres", "llm")
        ),
        ServiceSpec("admin", "WP-12", 8080, "app", ("web/admin/package.json",), compose=False),
        # Adapters live inside the storage image; they are "available" when their package is merged.
        ServiceSpec(
            "storage-adapters-wp08",
            "WP-08",
            0,
            "feature",
            tuple(
                f"services/storage/adapters/{a}/pyproject.toml"
                for a in ("sqlserver", "mongodb", "minio", "s3")
            ),
            compose=False,
        ),
        ServiceSpec(
            "discovery-strategies-wp03",
            "WP-03",
            0,
            "feature",
            ("services/web-collector/strategies/discovery",),
            compose=False,
        ),
    )
}


def default_project(root: Path = ROOT) -> str:
    if env := os.environ.get("JANE_E2E_PROJECT"):
        return env
    digest = hashlib.sha256(str(root).lower().encode()).hexdigest()[:8]
    return f"jane-e2e-{digest}"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@dataclass
class E2EStack:
    project: str = field(default_factory=default_project)
    root: Path = ROOT
    timeout_s: int = int(os.environ.get("JANE_E2E_WAIT_TIMEOUT", "900"))
    _env: dict[str, str] = field(default_factory=dict)
    _started: set[str] = field(default_factory=set)

    # ------------------------------------------------------------------ availability
    def missing(self, names: Iterable[str]) -> list[str]:
        """Human-readable reasons why some of ``names`` cannot run in this checkout (empty = all fine)."""
        reasons: list[str] = []
        for name in names:
            spec = SERVICES[name]
            absent = [p for p in spec.requires if not (self.root / p).exists()]
            if absent:
                reasons.append(f"{name}: {spec.wp} ще не злито в main (немає {', '.join(absent)})")
            elif not spec.compose:
                reasons.append(
                    f"{name}: {spec.wp} злито, але сервіс ще не описано в tests/e2e/compose.e2e.yaml (WP-13)"
                )
        return reasons

    def available_apps(self) -> list[str]:
        return [
            s.name for s in SERVICES.values() if s.kind == "app" and s.compose and not self.missing([s.name])
        ]

    # ------------------------------------------------------------------ environment
    @property
    def stack_file(self) -> Path:
        return STACK_DIR / f"stack-{self.project}.json"

    @property
    def sandbox_image(self) -> str:
        return os.environ.get("JANE_E2E_SANDBOX_IMAGE") or f"{_slug(self.project)}-python-extractor:1"

    def env(self) -> dict[str, str]:
        if not self._env:
            self._env = {**self._credentials(), **self._runtime_env()}
        return self._env

    def _credentials(self) -> dict[str, str]:
        if self.stack_file.is_file():
            data = json.loads(self.stack_file.read_text(encoding="utf-8"))
            if all(k in data.get("env", {}) for k in CREDENTIAL_KEYS):
                return {k: str(data["env"][k]) for k in CREDENTIAL_KEYS}
        creds = {
            "JANE_PG_USER": "jane",
            "JANE_PG_DB": "jane",
            "JANE_PG_PASSWORD": secrets.token_urlsafe(18),
            "JANE_PG_HANDLER_RUNTIME_PASSWORD": secrets.token_urlsafe(18),
            "JANE_PG_ORCHESTRATOR_PASSWORD": secrets.token_urlsafe(18),
            "JANE_PG_REGISTRY_PASSWORD": secrets.token_urlsafe(18),
            "JANE_PG_LLM_PASSWORD": secrets.token_urlsafe(18),
            "JANE_PG_ASSISTANT_PASSWORD": secrets.token_urlsafe(18),
            "JANE_PG_STORAGE_RESULTS_PASSWORD": secrets.token_urlsafe(18),
            "JANE_MSSQL_SA_PASSWORD": "Jn1_" + secrets.token_hex(12),
            "JANE_MONGO_USER": "jane",
            "JANE_MONGO_PASSWORD": secrets.token_urlsafe(18),
            "JANE_MINIO_ACCESS_KEY": "jane-" + secrets.token_hex(4),
            "JANE_MINIO_SECRET_KEY": secrets.token_urlsafe(24),
            "JANE_S3_ACCESS_KEY": "jane-" + secrets.token_hex(4),
            "JANE_S3_SECRET_KEY": secrets.token_urlsafe(24),
        }
        self._write_stack_file(creds, {})
        return creds

    def _runtime_env(self) -> dict[str, str]:
        return {
            "JANE_E2E_PROJECT": self.project,
            "JANE_E2E_SANDBOX_IMAGE": self.sandbox_image,
            "JANE_DOCKER_SOCKET": os.environ.get("JANE_E2E_DOCKER_SOCKET", "/var/run/docker.sock"),
            "JANE_DOCKER_GID": os.environ.get("JANE_E2E_DOCKER_GID", ""),
            "JANE_STORAGE_CONNECTIONS_FILE_HOST": (
                self.root / "tests" / "e2e" / "config" / "storage-connections.json"
            )
            .resolve()
            .as_posix(),
            "COMPOSE_PROFILES": ",".join(self.available_apps()),
            "JANE_E2E_PACKAGES_DIR": self.packages_dir.as_posix(),
            "JANE_E2E_TELEGRAM_RECORDINGS_DIR": self.telegram_recordings_dir.as_posix(),
        }

    @property
    def packages_dir(self) -> Path:
        """Archives of local packages served by the ``package-host`` stand-in (``<id>/<version>.zip``)."""
        path = STACK_DIR / f"e2e-packages-{self.project}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def telegram_recordings_dir(self) -> Path:
        """Writable host directory mounted into the recorded Telegram backend for S-M2-02."""
        path = STACK_DIR / f"e2e-telegram-recordings-{self.project}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def publish_local_package(self, package_id: str, version: str, archive: bytes) -> None:
        target = self.packages_dir / package_id / f"{version}.zip"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive)

    def _write_stack_file(self, creds: Mapping[str, str], services: Mapping[str, Any]) -> None:
        STACK_DIR.mkdir(exist_ok=True)
        self.stack_file.write_text(
            json.dumps(
                {
                    "project": self.project,
                    "compose_file": str(INFRA_COMPOSE),
                    "compose_overlay": str(E2E_COMPOSE),
                    "env": dict(creds),
                    "services": dict(services),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------ docker / compose
    def _run(
        self, cmd: Sequence[str], *, check: bool = True, text: bool = True, timeout: float | None = None
    ) -> subprocess.CompletedProcess[Any]:
        print(f"$ {' '.join(cmd)}", file=sys.stderr, flush=True)
        r = subprocess.run(
            list(cmd),
            cwd=self.root,
            env={**os.environ, **self.env()},
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            timeout=timeout,
            check=False,
        )
        if check and r.returncode != 0:
            err = r.stderr if text else r.stderr.decode("utf-8", "replace")
            raise StackError(f"{' '.join(cmd)} -> exit {r.returncode}\n{err[-4000:]}")
        return r

    def compose(
        self, *args: str, check: bool = True, text: bool = True, timeout: float | None = None
    ) -> subprocess.CompletedProcess[Any]:
        return self._run(
            [
                "docker",
                "compose",
                "-f",
                str(INFRA_COMPOSE),
                "-f",
                str(E2E_COMPOSE),
                "-p",
                self.project,
                *args,
            ],
            check=check,
            text=text,
            timeout=timeout,
        )

    def ensure(self, *names: str) -> None:
        """Start ``names`` (and their dependencies) if they are not running yet; waits for health-checks."""
        wanted: list[str] = []
        for name in names:
            for dep in (*SERVICES[name].depends, name):
                if dep not in wanted and dep not in self._started:
                    wanted.append(dep)
        if not wanted:
            return
        if reasons := self.missing(wanted):
            raise StackError("; ".join(reasons))
        if "handler-runtime" in wanted:
            self._prepare_handler_runtime()
        self.compose(
            "up",
            "-d",
            "--build",
            "--wait",
            "--wait-timeout",
            str(self.timeout_s),
            *wanted,
            timeout=self.timeout_s + 600,
        )
        self._started.update(wanted)
        self._write_stack_file(self._credentials(), self.describe())

    def _prepare_handler_runtime(self) -> None:
        """Sandbox image of profile python-extractor@1 (built by the runtime CLI) and the docker socket gid."""
        env = self.env()
        if not self._image_exists(self.sandbox_image):
            cli = [sys.executable, "-m", "jane_handler_runtime.cli"]
            self._run([*cli, "build-image", "--tag", self.sandbox_image], timeout=1800)
        if not env["JANE_DOCKER_GID"]:
            env["JANE_DOCKER_GID"] = self._docker_socket_gid()

    def _docker_socket_gid(self) -> str:
        """Group of the docker socket *as seen inside a container* (0 on Docker Desktop, docker gid on Linux)."""
        sock = self.env()["JANE_DOCKER_SOCKET"]
        r = self._run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{sock}:/var/run/docker.sock",
                self.sandbox_image,
                "python",
                "-c",
                "import os; print(os.stat('/var/run/docker.sock').st_gid)",
            ],
            timeout=600,
        )
        return str(r.stdout).strip().splitlines()[-1]

    def _image_exists(self, image: str) -> bool:
        return self._run(["docker", "image", "inspect", image], check=False).returncode == 0

    def host_port(self, service: str, index: int = 1) -> int:
        spec = SERVICES[service]
        r = self.compose("port", "--index", str(index), service, str(spec.port))
        lines = r.stdout.strip().splitlines()
        if not lines:
            raise StackError(f"{service}#{index}: no published port")
        return int(lines[0].rsplit(":", 1)[1])

    def url(self, service: str, index: int = 1) -> str:
        return f"http://127.0.0.1:{self.host_port(service, index)}"

    def describe(self) -> dict[str, dict[str, Any]]:
        """Stack-file ``services`` section (same keys as `just up` for infra services)."""
        env = self.env()
        out: dict[str, dict[str, Any]] = {}
        for name in sorted(self._started):
            spec = SERVICES[name]
            port = self.host_port(name)
            info: dict[str, Any] = {"host": "127.0.0.1", "port": port, "url": f"http://127.0.0.1:{port}"}
            if name == "postgres":
                info.update(
                    user=env["JANE_PG_USER"],
                    password=env["JANE_PG_PASSWORD"],
                    database=env["JANE_PG_DB"],
                    dsn=f"postgresql://{env['JANE_PG_USER']}:{env['JANE_PG_PASSWORD']}@127.0.0.1:{port}/{env['JANE_PG_DB']}",
                )
                del info["url"]
            info["wp"] = spec.wp
            out[name] = info
        return out

    def exec(self, service: str, *cmd: str, index: int = 1) -> bytes:
        """Run a command inside a service container; returns stdout bytes."""
        r = self.compose("exec", "-T", "--index", str(index), service, *cmd, text=False, timeout=300)
        return bytes(r.stdout)

    def kill(self, service: str) -> None:
        self.compose("kill", service)

    def container(self, service: str, index: int = 1) -> str:
        """Container id of one replica of a service."""
        labels = {
            "com.docker.compose.project": self.project,
            "com.docker.compose.service": service,
            "com.docker.compose.container-number": str(index),
        }
        filters = [arg for k, v in labels.items() for arg in ("--filter", f"label={k}={v}")]
        r = self._run(["docker", "ps", "-a", "-q", *filters])
        cid = str(r.stdout).strip().splitlines()
        if not cid:
            raise StackError(f"{service}#{index}: no container")
        return str(cid[0])

    def kill_instance(self, service: str, index: int) -> None:
        """``docker kill`` (SIGKILL) of one replica - the others keep running."""
        self._run(["docker", "kill", self.container(service, index)])

    def start_instance(self, service: str, index: int) -> None:
        self._run(["docker", "start", self.container(service, index)])

    def pause_instance(self, service: str, index: int = 1) -> None:
        """``docker pause`` (cgroup freezer): the replica keeps its sockets but answers nothing."""
        self._run(["docker", "pause", self.container(service, index)])

    def unpause_instance(self, service: str, index: int = 1) -> None:
        self._run(["docker", "unpause", self.container(service, index)])

    def state(self, service: str, index: int = 1) -> dict[str, Any]:
        """``docker inspect`` ``.State`` of one replica (``Status``, ``Paused``, ``Health.Status``...)."""
        r = self._run(["docker", "inspect", "--format", "{{json .State}}", self.container(service, index)])
        state: dict[str, Any] = json.loads(str(r.stdout))
        return state

    def wait_healthy(self, service: str, index: int = 1, timeout_s: float | None = None) -> None:
        """Wait for the health-check of one replica (after ``start_instance``)."""
        deadline = time.monotonic() + (timeout_s or self.timeout_s)
        while True:
            state = self.state(service, index)
            if state.get("Running") and (state.get("Health") or {}).get("Status") == "healthy":
                return
            if time.monotonic() > deadline:
                raise StackError(f"{service}#{index} is not healthy: {state}")
            time.sleep(1.0)

    def logs(self, service: str, index: int = 1) -> str:
        """Everything one replica wrote to stdout/stderr (kept across ``docker kill`` + ``docker start``)."""
        r = self._run(["docker", "logs", self.container(service, index)])
        return f"{r.stdout}\n{r.stderr}"

    @property
    def network(self) -> str:
        return f"{self.project}_default"

    def disconnect(self, service: str, index: int = 1) -> None:
        """Network partition: detach one replica from the stack network."""
        self._run(["docker", "network", "disconnect", "-f", self.network, self.container(service, index)])

    def reconnect(self, service: str, index: int = 1) -> None:
        self._run(
            ["docker", "network", "connect", "--alias", service, self.network, self.container(service, index)]
        )

    def restart(self, service: str) -> None:
        self.compose(
            "up", "-d", "--wait", "--wait-timeout", str(self.timeout_s), service, timeout=self.timeout_s + 60
        )

    def scale(self, service: str, replicas: int) -> None:
        self.compose(
            "up",
            "-d",
            "--wait",
            "--wait-timeout",
            str(self.timeout_s),
            "--scale",
            f"{service}={replicas}",
            service,
            timeout=self.timeout_s + 60,
        )

    def down(self, volumes: bool = True) -> None:
        args = ["down", "--remove-orphans"] + (["-v", "--rmi", "local"] if volumes else [])
        self.compose(*args, timeout=900)
        if volumes:
            self._run(["docker", "image", "rm", "-f", self.sandbox_image], check=False)
            self.stack_file.unlink(missing_ok=True)
            recordings = self.telegram_recordings_dir.resolve()
            if recordings.is_relative_to(STACK_DIR.resolve()):
                shutil.rmtree(recordings)
        self._started.clear()
