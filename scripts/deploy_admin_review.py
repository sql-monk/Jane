"""Deploy the CI-verified admin revision without reconstructing the shared stack.

The default ``plan`` command is read-only. ``apply`` requires the completed GitHub
``ci`` run for the exact source SHA and an explicit ``drain`` or ``recover`` strategy.
It builds from git archive, retains the old containers/images, snapshots PostgreSQL
and RAW data, and changes only storage, running orchestrator writers and the UI mount.
Other collectors, runtimes, LLM services, ports and concrete environment stay intact.

Examples (run in the accepted, clean coordinator checkout):
  python scripts/deploy_admin_review.py plan --stack-state /path/.jane/stack-jane-demo.json
  python scripts/deploy_admin_review.py apply --stack-state /path/.jane/stack-jane-demo.json \
    --sha FULL_SHA --ci-run RUN_ID --strategy drain --drain-seconds 1800

``drain`` pauses schedules with ETags, waits for active runs, then restores the original
schedule on the latest task document. A timeout restores schedules before touching any
container. ``recover`` keeps collection jobs alive and resumes durable runs after an
orderly writer restart; it relies on the exact revision's CI recovery/idempotency tests.
The stop/health/API/poll bounds are configurable below. An automatic rollback restores
the original containers and UI, not a database dump over potentially newer user data.
The additive migration remains compatible with old writers. Database dumps are private
disaster-recovery artifacts; restoring them requires separately quiescing all writers.
Rollback attempts independent safe steps and retains every failure in its private
journal. Original writers stay stopped while any replacement writer is running or its
state cannot be confirmed. Shared container state, identity and network configuration
are checked after the build and immediately before the first container stop.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any, BinaryIO

CI_JOBS = frozenset(
    {
        "lint",
        "unit",
        "contract",
        "contracts-compat",
        "web",
        "web-mock-e2e",
        "isolation",
        "stack",
        "e2e",
        "limits",
    }
    | {f"adapters ({name})" for name in ("sqlserver", "mongodb", "minio", "s3")}
)
ACTIVE = ("queued", "running", "cancelling")
SOURCE = Path(__file__).resolve().parents[1]

# The pinned old orchestrator image supplies Python, so no helper image is downloaded.
# Its only purpose is transporting a JSON request to the local Docker Unix socket.
# Config/environment travel over stdin, never over command arguments or public output.
ENGINE_HELPER = """
import http.client,json,socket,sys
class Local(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
  self.sock.connect('/var/run/docker.sock')
p=json.load(sys.stdin); c=Local('localhost',timeout=p['timeout'])
c.request(p['method'],p['path'],json.dumps(p.get('body',{})),{'Content-Type':'application/json'})
r=c.getresponse(); data=r.read()
if r.status>=300:
 print(json.dumps({'status':r.status}));sys.exit(1)
print(data.decode() or '{}')
"""


class DeploymentError(RuntimeError):
    """A public, credential-free deployment failure."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward the private Bearer token away from the checked local proxy."""

    def redirect_request(
        self, req: urllib.request.Request, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


def private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=False, mode=0o700)
    if os.name == "nt":
        identity = subprocess.run(["whoami"], capture_output=True, text=True, check=True).stdout.strip()
        result = subprocess.run(
            ["icacls", str(path), "/inheritance:r", "/grant:r", f"{identity}:(OI)(CI)F"],
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise DeploymentError("Could not restrict the private deployment directory permissions")
    else:
        path.chmod(0o700)


def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    path.chmod(0o600)


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    stdin: bytes | None = None,
    output: BinaryIO | None = None,
    log: Path | None = None,
) -> bytes:
    result = subprocess.run(
        args, cwd=cwd, input=stdin, stdout=output or subprocess.PIPE, stderr=subprocess.PIPE
    )
    if log is not None:
        with log.open("ab") as stream:
            stream.write(result.stdout or b"")
            stream.write(result.stderr or b"")
    if result.returncode:
        # Docker/Git/HTTP errors may include credentials/configuration: do not echo them.
        raise DeploymentError(f"{Path(args[0]).name} operation failed; inspect the private deployment log")
    return result.stdout or b""


def git(*args: str) -> str:
    return run(["git", *args], cwd=SOURCE).decode().strip()


def inspect(names: list[str]) -> list[dict[str, Any]]:
    return list(json.loads(run(["docker", "inspect", *names])))


def environment(container: dict[str, Any]) -> dict[str, str]:
    return dict(value.split("=", 1) for value in container["Config"].get("Env", []))


def fingerprint(containers: list[dict[str, Any]]) -> dict[str, str]:
    return {
        c["Name"]: hashlib.sha256(
            json.dumps(
                {
                    "id": c["Id"],
                    "image": c["Image"],
                    "config": c["Config"],
                    "host": c["HostConfig"],
                    "running": c["State"]["Running"],
                    "networks": {
                        name: {key: endpoint.get(key) for key in ("Aliases", "IPAMConfig", "DriverOpts")}
                        for name, endpoint in c["NetworkSettings"]["Networks"].items()
                    },
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        for c in containers
    }


def replacement_config(
    old: dict[str, Any], image: str, sha: str, *, ui_release: Path | None = None
) -> dict[str, Any]:
    """Preserve effective Docker configuration, ports, resources, env and aliases."""
    config = copy.deepcopy(old["Config"])
    config["Image"] = image
    # Absence of an old health check must not inherit a new image's HTTP probe on a worker-only process.
    if not config.get("Healthcheck"):
        config["Healthcheck"] = {"Test": ["NONE"]}
    config.pop("Hostname", None)  # Generated container ID is not a stable hostname.
    config["Labels"] = {**(config.get("Labels") or {}), "com.jane.admin-review.revision": sha}
    host = copy.deepcopy(old["HostConfig"])
    # These values belong to the old container identity, not the deployment configuration.
    host.pop("ContainerIDFile", None)
    if host.get("AutoRemove"):
        raise DeploymentError("AutoRemove containers cannot be retained for rollback")
    if ui_release is not None:
        found = 0
        binds: list[str] = []
        for bind in host.get("Binds") or []:
            if ":/srv/admin:" in bind or bind.endswith(":/srv/admin"):
                binds.append(f"{ui_release.resolve()}:/srv/admin:ro")
                found += 1
            else:
                binds.append(bind)
        host["Binds"] = binds
        for mount in host.get("Mounts") or []:
            if mount.get("Target") == "/srv/admin":
                mount["Source"] = str(ui_release.resolve())
                mount["ReadOnly"] = True
                found += 1
        if found != 1:
            raise DeploymentError("Expected exactly one existing /srv/admin mount")
    networks: dict[str, Any] = {}
    for name, endpoint in old["NetworkSettings"]["Networks"].items():
        aliases = [a for a in (endpoint.get("Aliases") or []) if a not in (old["Id"], old["Id"][:12])]
        networks[name] = {"Aliases": aliases, "DriverOpts": endpoint.get("DriverOpts") or {}}
        # Keep explicit IPAM addresses, not dynamic addresses assigned to the old container.
        if endpoint.get("IPAMConfig"):
            networks[name]["IPAMConfig"] = endpoint["IPAMConfig"]
    return {**config, "HostConfig": host, "NetworkingConfig": {"EndpointsConfig": networks}}


def validate_ci(run_info: dict[str, Any], jobs: list[dict[str, Any]], sha: str) -> None:
    if (
        run_info.get("head_sha") != sha
        or run_info.get("status") != "completed"
        or run_info.get("conclusion") != "success"
    ):
        raise DeploymentError("Full CI has not succeeded for the exact deployment SHA")
    if run_info.get("path") != ".github/workflows/ci.yml":
        raise DeploymentError("The supplied run is not Jane's full CI workflow")
    by_name = {job["name"]: job for job in jobs}
    if CI_JOBS - by_name.keys() or any(by_name[name].get("conclusion") != "success" for name in CI_JOBS):
        raise DeploymentError("Full CI must contain all 14 required jobs, without skipped or failed jobs")


def migrations(source: str) -> list[str]:
    for node in ast.parse(source).body:
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "MIGRATIONS"
            and node.value is not None
        ):
            return list(ast.literal_eval(node.value))
    raise DeploymentError("Could not inspect the orchestrator's migration definitions")


def validate_additive_migrations(previous: list[str], candidate: list[str]) -> None:
    if candidate[: len(previous)] != previous:
        raise DeploymentError("Previously applied migrations changed; image-only rollback would be unsafe")
    for sql in candidate[len(previous) :]:
        statements = [part.strip() for part in sql.split(";") if part.strip()]
        if any(
            not re.match(
                r"(?:CREATE\s+(?:TABLE|INDEX)|ALTER\s+TABLE\s+\w+\s+ADD\s+COLUMN)\b", part, re.IGNORECASE
            )
            for part in statements
        ):
            raise DeploymentError(
                "New migration contains a non-additive operation; review a separate rollback strategy"
            )


class Deploy:
    def __init__(self, options: argparse.Namespace) -> None:
        self.options = options
        self.state_path = options.stack_state.resolve()
        self.stack_root = self.state_path.parent.parent
        self.state: dict[str, Any] = json.loads(self.state_path.read_text(encoding="utf-8-sig"))
        self.project: str = self.state["project"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]+", self.project):
            raise DeploymentError("Invalid stack project identity")
        self.proxy: str = self.state["services"]["proxy"]["url"].rstrip("/")
        parsed = urllib.parse.urlsplit(self.proxy)
        if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise DeploymentError("Stack API must use the existing local loopback proxy")
        self.key: str = self.state["services"]["auth"]["admin_api_key"]
        self.http = urllib.request.build_opener(NoRedirect())
        ids = (
            run(
                [
                    "docker",
                    "ps",
                    "-aq",
                    "--no-trunc",
                    "--filter",
                    f"label=com.docker.compose.project={self.project}",
                ]
            )
            .decode()
            .split()
        )
        self.containers = inspect(ids)
        self.by_name = {c["Name"].lstrip("/"): c for c in self.containers}
        self.orchestrator = self.by_name[f"{self.project}-orchestrator-1"]
        self.storage = self.by_name[f"{self.project}-storage-1"]
        self.proxy_container = self.by_name[f"{self.project}-proxy-1"]
        self.postgres = self.by_name[f"{self.project}-postgres-1"]
        dsn = environment(self.orchestrator)["JANE_ORCHESTRATOR_DATABASE_URL"]
        self.writers = [
            c
            for c in self.containers
            if c["State"]["Running"] and environment(c).get("JANE_ORCHESTRATOR_DATABASE_URL") == dsn
        ]
        for c in self.writers:
            if c["Config"].get("Entrypoint") not in (None, []) or c["Config"].get("Cmd") not in (
                ["python", "-m", "jane_orchestrator"],
                ["python", "-m", "jane_orchestrator", "worker"],
            ):
                raise DeploymentError(
                    "An orchestrator writer has a custom entrypoint; review it before deployment"
                )
        self.original_fingerprint = fingerprint(self.containers)
        self.backup: Path | None = None
        self.log: Path | None = None
        self.paused: dict[str, dict[str, Any]] = {}
        self.retained: list[tuple[dict[str, Any], str]] = []
        self.created: list[str] = []
        self.replacement_by_old: dict[str, str] = {}
        self.suffix = uuid.uuid4().hex[:8]

    def api(
        self, service: str, path: str, *, body: Any = None, method: str = "GET", etag: str | None = None
    ) -> tuple[Any, str | None]:
        headers = {"Authorization": f"Bearer {self.key}"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        if method == "POST":
            headers["Idempotency-Key"] = str(uuid.uuid4())
        if etag is not None:
            headers["If-Match"] = etag
        # self.proxy is restricted to HTTP loopback above; redirect handling is disabled.
        request = urllib.request.Request(  # noqa: S310 - checked HTTP loopback, no redirects
            f"{self.proxy}/api/{service}{path}", data=data, headers=headers, method=method
        )
        try:
            with self.http.open(request, timeout=self.options.api_seconds) as response:
                return json.load(response), response.headers.get("ETag")
        except urllib.error.HTTPError as exc:
            raise DeploymentError(f"{service} API returned HTTP {exc.code}") from None
        except (urllib.error.URLError, TimeoutError):
            raise DeploymentError(f"{service} API is unavailable") from None

    def page(self, service: str, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor = None
        for _ in range(self.options.max_pages):
            query = ("&" if "?" in path else "?") + urllib.parse.urlencode(
                {"limit": 200, **({"cursor": cursor} if cursor else {})}
            )
            body, _ = self.api(service, path + query)
            items.extend(body["items"])
            cursor = body["next_cursor"]
            if not cursor:
                return items
        raise DeploymentError("Pagination exceeded the configured deployment bound")

    def active_runs(self) -> list[dict[str, Any]]:
        return [item for status in ACTIVE for item in self.page("orchestrator", f"/v1/runs?status={status}")]

    def plan(self) -> None:
        active = self.active_runs()
        print(
            json.dumps(
                {
                    "mode": "read-only",
                    "project": self.project,
                    "source_head": git("rev-parse", "HEAD"),
                    "active_runs": len(active),
                    "writer_containers": [c["Name"].lstrip("/") for c in self.writers],
                    "replace_services": ["storage", "orchestrator writers", "proxy UI mount"],
                    "preserved_other_containers": len(self.containers) - len(self.writers) - 2,
                    "backup_root": str(self.stack_root / ".jane" / "backups"),
                    "strategies": [
                        "drain: reversible schedule pause and bounded natural completion",
                        "recover: durable lease/idempotency recovery; no collection cancellation",
                    ],
                },
                ensure_ascii=False,
            )
        )

    def ensure_ci(self) -> str:
        sha = self.options.sha
        if not sha or not re.fullmatch(r"[0-9a-f]{40}", sha) or git("rev-parse", "HEAD") != sha:
            raise DeploymentError("Supply the full SHA of the current accepted checkout")
        if git("status", "--porcelain"):
            raise DeploymentError("The source checkout must be clean before deployment")
        if not self.options.ci_run:
            raise DeploymentError("Supply the exact successful full CI run ID")
        origin = git("remote", "get-url", "origin")
        match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([\w.-]+/[\w.-]+?)(?:\.git)?", origin)
        if not match:
            raise DeploymentError("The source repository must have a GitHub origin")
        repo = match.group(1)
        run_info = json.loads(run(["gh", "api", f"repos/{repo}/actions/runs/{self.options.ci_run}"]))
        jobs = json.loads(
            run(["gh", "api", f"repos/{repo}/actions/runs/{self.options.ci_run}/jobs?per_page=100"])
        )
        validate_ci(run_info, jobs["jobs"], sha)
        live_main = json.loads(run(["gh", "api", f"repos/{repo}/commits/main"]))["sha"]
        run(["git", "merge-base", "--is-ancestor", live_main, sha], cwd=SOURCE)
        return str(sha)

    def engine(self, method: str, path: str, body: Any = None) -> Any:
        request = json.dumps(
            {"method": method, "path": path, "body": body or {}, "timeout": self.options.health_seconds}
        ).encode()
        data = run(
            [
                "docker",
                "run",
                "--rm",
                "-i",
                "--user",
                "0",
                "--entrypoint",
                "python",
                "--mount",
                f"type=bind,src={self.options.docker_socket},dst=/var/run/docker.sock",
                self.orchestrator["Image"],
                "-c",
                ENGINE_HELPER,
            ],
            stdin=request,
            log=self.log,
        )
        return json.loads(data)

    def pause_schedules(self) -> None:
        if self.backup is None:
            raise DeploymentError("Private backup must exist before pausing schedules")
        for item in self.page("orchestrator", "/v1/tasks"):
            task_id = item["task_id"]
            doc, etag = self.api("orchestrator", "/v1/tasks/" + urllib.parse.quote(task_id, safe=""))
            schedule = doc.get("schedule")
            if not schedule or schedule.get("type") == "manual" or not schedule.get("enabled", True):
                continue
            if not etag:
                raise DeploymentError("Task response has no ETag; cannot pause schedules safely")
            paused = copy.deepcopy(doc)
            paused["schedule"]["enabled"] = False
            # Persist intention before the API write, so interrupted deployment is recoverable.
            self.paused[task_id] = {"original_schedule": schedule, "paused_schedule": paused["schedule"]}
            save_json(self.backup / "paused-schedules.json", self.paused)
            self.api(
                "orchestrator",
                "/v1/tasks/" + urllib.parse.quote(task_id, safe=""),
                body=paused,
                method="PUT",
                etag=etag,
            )

    def restore_schedules(self) -> None:
        failures = 0
        for task_id, entry in list(self.paused.items()):
            try:
                path = "/v1/tasks/" + urllib.parse.quote(task_id, safe="")
                doc, etag = self.api("orchestrator", path)
                if doc.get("schedule") == entry["original_schedule"]:
                    del self.paused[task_id]
                    continue
                if doc.get("schedule") != entry["paused_schedule"] or not etag:
                    raise DeploymentError("Schedule changed concurrently; refusing to overwrite it")
                doc["schedule"] = entry["original_schedule"]
                self.api("orchestrator", path, body=doc, method="PUT", etag=etag)
                del self.paused[task_id]
            except DeploymentError:
                failures += 1
            if self.backup:
                save_json(self.backup / "paused-schedules.json", self.paused)
        if failures:
            raise DeploymentError(
                "Some schedules need manual restoration; exact originals remain in the private receipt"
            )

    def wait_drain(self) -> None:
        deadline = time.monotonic() + self.options.drain_seconds
        while self.active_runs():
            if time.monotonic() >= deadline:
                raise DeploymentError("Drain deadline expired; containers were not replaced")
            time.sleep(self.options.poll_seconds)

    def build(self, sha: str) -> tuple[Path, dict[str, str]]:
        if self.backup is None:
            raise DeploymentError("Missing private deployment directory")
        archive = self.backup / "source.tar"
        with archive.open("wb") as stream:
            run(["git", "archive", "--format=tar", sha], cwd=SOURCE, output=stream, log=self.log)
        exact = self.backup / "source"
        exact.mkdir()
        with tarfile.open(archive) as source:
            source.extractall(exact, filter="data")
        candidate_migrations = migrations(
            (exact / "services/orchestrator/src/jane_orchestrator/db.py").read_text(encoding="utf-8")
        )
        code = "from pathlib import Path; print(Path('/app/.venv/lib/python3.12/site-packages/jane_orchestrator/db.py').read_text())"
        for writer in self.writers:
            old_source = run(["docker", "exec", writer["Id"], "python", "-c", code], log=self.log).decode()
            validate_additive_migrations(migrations(old_source), candidate_migrations)
        package = exact / "web" / "admin"
        corepack = shutil.which("corepack")
        if not corepack:
            raise DeploymentError("Corepack is required to build the exact immutable admin release")
        prefix = (
            ["cmd", "/d", "/c", corepack]
            if os.name == "nt" and corepack.lower().endswith((".cmd", ".bat"))
            else [corepack]
        )
        run([*prefix, "pnpm", "install", "--frozen-lockfile"], cwd=package, log=self.log)
        run([*prefix, "pnpm", "build"], cwd=package, log=self.log)
        release = self.stack_root / ".jane" / "releases" / f"admin-{sha}-{self.suffix}"
        shutil.copytree(package / "dist", release)
        tags = {
            name: f"{self.project}-{name}:admin-{sha}-{self.suffix}" for name in ("orchestrator", "storage")
        }
        for name, tag in tags.items():
            run(
                [
                    "docker",
                    "build",
                    "--label",
                    f"org.opencontainers.image.revision={sha}",
                    "--file",
                    str(exact / "services" / name / "Dockerfile"),
                    "--tag",
                    tag,
                    str(exact),
                ],
                log=self.log,
            )
        return release, tags

    def backup_data(self, destination: Path) -> None:
        if self.backup is None:
            raise DeploymentError("Missing private deployment directory")
        destination.mkdir(mode=0o700)
        pg_user = environment(self.postgres)["POSTGRES_USER"]
        for name in ("orchestrator", "storage-results"):
            database = self.state["services"][f"db-{name}"]["db_name"]
            with (destination / f"{name}.dump").open("wb") as stream:
                run(
                    [
                        "docker",
                        "exec",
                        self.postgres["Id"],
                        "sh",
                        "-c",
                        'PGPASSWORD="$POSTGRES_PASSWORD" exec pg_dump -U "$1" -Fc "$2"',
                        "sh",
                        pg_user,
                        database,
                    ],
                    output=stream,
                    log=self.log,
                )
        raw = destination / "storage-data"
        raw.mkdir()
        run(["docker", "cp", f"{self.storage['Id']}:/var/lib/jane/storage/.", str(raw)], log=self.log)
        run(
            [
                "docker",
                "cp",
                f"{self.storage['Id']}:/cfg/storage-connections.json",
                str(destination / "storage-connections.json"),
            ],
            log=self.log,
        )

    def wait_health(self, name: str) -> None:
        deadline = time.monotonic() + self.options.health_seconds
        while time.monotonic() < deadline:
            state = inspect([name])[0]["State"]
            if state.get("Health", {}).get("Status") == "healthy":
                return
            if not state.get("Running"):
                break
            time.sleep(self.options.poll_seconds)
        raise DeploymentError("A replacement service did not become healthy within the configured bound")

    def replace(self, old: dict[str, Any], image: str, sha: str, release: Path | None = None) -> None:
        name = old["Name"].lstrip("/")
        retained = f"{name}-before-admin-{self.suffix}"
        run(["docker", "rename", old["Id"], retained], log=self.log)
        self.retained.append((old, retained))
        for network in old["NetworkSettings"]["Networks"]:
            self.engine(
                "POST",
                f"/networks/{urllib.parse.quote(network, safe='')}/disconnect",
                {"Container": old["Id"], "Force": False},
            )
        body = replacement_config(old, image, sha, ui_release=release)
        created = self.engine("POST", "/containers/create?" + urllib.parse.urlencode({"name": name}), body)
        self.created.append(created["Id"])
        self.replacement_by_old[old["Id"]] = created["Id"]
        if self.backup:
            save_json(
                self.backup / "replacement-containers.json",
                {
                    "retained": [c[0]["Id"] for c in self.retained],
                    "created": self.created,
                    "replacement_by_old": self.replacement_by_old,
                },
            )
        self.engine("POST", f"/containers/{created['Id']}/start")
        if old["Config"].get("Healthcheck", {}).get("Test", ["NONE"]) != ["NONE"]:
            self.wait_health(name)
        else:
            self.verify_running(name)

    def verify_running(self, name: str) -> None:
        if not inspect([name])[0]["State"]["Running"]:
            raise DeploymentError("Replacement writer is not running")

    def rollback(self) -> None:
        """Try independent recovery steps; never start an old writer beside an unconfirmed new writer."""
        journal: list[dict[str, Any]] = []
        failed = 0

        def record(
            action: str, container_id: str | None, status: str, error: Exception | None = None
        ) -> None:
            nonlocal failed
            entry: dict[str, Any] = {
                "at": time.time(),
                "action": action,
                "container_id": container_id,
                "status": status,
            }
            if error is not None:
                entry.update({"error_class": type(error).__name__, "detail": str(error)})
            if status in ("failed", "held"):
                failed += 1
            journal.append(entry)
            if self.backup:
                try:
                    save_json(self.backup / "rollback-journal.json", journal)
                except OSError as journal_error:
                    failed += 1
                    journal.append(
                        {
                            "at": time.time(),
                            "action": "journal_write",
                            "status": "failed",
                            "error_class": type(journal_error).__name__,
                        }
                    )

        def attempt(action: str, container_id: str | None, operation: Callable[[], Any]) -> tuple[bool, Any]:
            try:
                value = operation()
            except Exception as error:
                record(action, container_id, "failed", error)
                return False, None
            record(action, container_id, "succeeded")
            return True, value

        stopped: dict[str, bool] = {}
        for container_id in reversed(self.created):
            attempt(
                "stop_new",
                container_id,
                partial(
                    run,
                    ["docker", "stop", "--time", str(self.options.stop_seconds), container_id],
                    log=self.log,
                ),
            )
            checked, current = attempt("inspect_new_stop", container_id, partial(inspect, [container_id]))
            stopped[container_id] = checked and not current[0]["State"]["Running"]
            if stopped[container_id]:
                removed, _ = attempt(
                    "remove_new",
                    container_id,
                    partial(run, ["docker", "rm", container_id], log=self.log),
                )
                if removed:
                    stopped[container_id] = True
            else:
                record(
                    "remove_new",
                    container_id,
                    "held",
                    DeploymentError(
                        "Replacement is still running or its state is unknown; refusing to remove it"
                    ),
                )
        restored: dict[str, bool] = {}
        for old, _ in reversed(self.retained):
            cid = old["Id"]
            renamed, _ = attempt(
                "rename_old",
                cid,
                partial(run, ["docker", "rename", old["Id"], old["Name"].lstrip("/")], log=self.log),
            )
            checked, current = attempt("inspect_old_networks", cid, partial(inspect, [old["Id"]]))
            if not checked:
                restored[cid] = False
                continue
            present = current[0]["NetworkSettings"]["Networks"]
            network_ok = True
            for network, endpoint in replacement_config(old, old["Image"], "rollback")["NetworkingConfig"][
                "EndpointsConfig"
            ].items():
                if network not in present:
                    connected, _ = attempt(
                        "connect_old_network",
                        cid,
                        partial(
                            self.engine,
                            "POST",
                            f"/networks/{urllib.parse.quote(network, safe='')}/connect",
                            {"Container": old["Id"], "EndpointConfig": endpoint},
                        ),
                    )
                    network_ok = connected and network_ok
            restored[cid] = (renamed or current[0]["Name"] == old["Name"]) and network_ok

        # When no replacement was created, restarting the unchanged old writer remains safe.
        writer_ids = {old["Id"] for old in self.writers}
        non_writer_replacements = {
            new_id for old_id, new_id in self.replacement_by_old.items() if old_id not in writer_ids
        }
        # A created container with an interrupted mapping write may itself be a writer: fail closed.
        writer_replacements = [cid for cid in self.created if cid not in non_writer_replacements]
        writers_safe = all(stopped.get(cid, False) for cid in writer_replacements)
        running_old: dict[str, bool] = {}
        for old in [self.storage, *self.writers, self.proxy_container]:
            cid = old["Id"]
            replacement = self.replacement_by_old.get(cid)
            safe = (replacement is None or stopped.get(replacement, False)) and restored.get(cid, True)
            if cid in writer_ids:
                safe = safe and writers_safe
            if not old["State"]["Running"]:
                continue
            if not safe:
                record(
                    "start_old",
                    cid,
                    "held",
                    DeploymentError(
                        "Original identity/network is not restored or a parallel replacement is not confirmed stopped"
                    ),
                )
                running_old[cid] = False
                continue
            attempt("start_old", cid, partial(run, ["docker", "start", old["Id"]], log=self.log))
            checked, current = attempt("inspect_old_running", cid, partial(inspect, [old["Id"]]))
            running_old[cid] = checked and current[0]["State"]["Running"]
            if not running_old[cid]:
                record(
                    "old_not_running",
                    cid,
                    "failed",
                    DeploymentError("Original container is not running after restart"),
                )
            elif old["Config"].get("Healthcheck", {}).get("Test", ["NONE"]) != ["NONE"]:
                attempt("health_old", cid, partial(self.wait_health, old["Id"]))
        if all(stopped.values()) and all(running_old.values()):
            attempt("restore_stack_state", None, partial(save_json, self.state_path, self.state))
        else:
            record(
                "restore_stack_state",
                None,
                "held",
                DeploymentError("Rollback is incomplete; leaving current stack metadata for diagnosis"),
            )
        if failed:
            raise DeploymentError(
                f"Rollback incomplete: {failed} recovery actions failed or were held; inspect private rollback-journal.json"
            )

    def assert_stack_unchanged(self) -> None:
        ids = (
            run(
                [
                    "docker",
                    "ps",
                    "-aq",
                    "--no-trunc",
                    "--filter",
                    f"label=com.docker.compose.project={self.project}",
                ]
            )
            .decode()
            .split()
        )
        if (
            set(ids) != {c["Id"] for c in self.containers}
            or fingerprint(inspect(ids)) != self.original_fingerprint
        ):
            raise DeploymentError(
                "Shared stack state or network configuration changed; no containers were stopped, inspect a fresh plan before applying"
            )

    def samples(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for connection in self.page("storage", "/v1/connections"):
            cid = connection["connection_id"]
            body, _ = self.api(
                "storage", "/v1/objects?" + urllib.parse.urlencode({"connection_id": cid, "limit": 1})
            )
            if body["items"]:
                item = body["items"][0]
                result[cid] = {
                    "object": item["object"],
                    "stored_at": item.get("stored_at"),
                    "content_sha256": self.content_hash(cid, item["object"]["object_id"]),
                }
        return result

    def content_hash(self, connection_id: str, object_id: str) -> str:
        path = (
            "/v1/objects/"
            + urllib.parse.quote(object_id, safe="")
            + "/content?"
            + urllib.parse.urlencode({"connection_id": connection_id})
        )
        request = urllib.request.Request(  # noqa: S310 - checked HTTP loopback, no redirects
            f"{self.proxy}/api/storage{path}", headers={"Authorization": f"Bearer {self.key}"}
        )
        digest = hashlib.sha256()
        size = 0
        try:
            with self.http.open(request, timeout=self.options.api_seconds) as response:
                while chunk := response.read(65536):
                    size += len(chunk)
                    if size > self.options.max_sample_bytes:
                        raise DeploymentError("RAW sample exceeds the configured verification bound")
                    digest.update(chunk)
        except (urllib.error.URLError, TimeoutError):
            raise DeploymentError("Could not read a stored RAW verification sample") from None
        return digest.hexdigest()

    def verify_samples(self, before: dict[str, Any]) -> None:
        for cid, item in before.items():
            object_id = item["object"]["object_id"]
            body, _ = self.api(
                "storage",
                "/v1/objects/"
                + urllib.parse.quote(object_id, safe="")
                + "?"
                + urllib.parse.urlencode({"connection_id": cid}),
            )
            if (
                body["object"] != item["object"]
                or body.get("stored_at") != item["stored_at"]
                or self.content_hash(cid, object_id) != item["content_sha256"]
            ):
                raise DeploymentError("A previously stored RAW sample changed across deployment")

    def verify_modules(self, exact: Path) -> None:
        code = "import pathlib,hashlib,json; p=pathlib.Path('/app/.venv/lib/python3.12/site-packages/jane_orchestrator'); print(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*.py')}))"
        expected = {
            f.name: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in (exact / "services/orchestrator/src/jane_orchestrator").glob("*.py")
        }
        for old in self.writers:
            actual = json.loads(
                run(["docker", "exec", old["Name"].lstrip("/"), "python", "-c", code], log=self.log)
            )
            if actual != expected:
                raise DeploymentError("A deployed orchestrator writer differs from the exact accepted source")

    def verify_recovery(self, active: list[dict[str, Any]]) -> None:
        for previous in active:
            current, _ = self.api(
                "orchestrator", "/v1/runs/" + urllib.parse.quote(previous["run_id"], safe="")
            )
            if current.get("run_id") != previous["run_id"] or current.get("task_id") != previous["task_id"]:
                raise DeploymentError("A durable run identity was not preserved across deployment")
            if current.get("status") == "cancelled" and previous["status"] != "cancelling":
                raise DeploymentError("An active run was unexpectedly cancelled during deployment")

    def verify_ui(self, release: Path) -> None:
        try:
            with self.http.open(self.proxy + "/index.html", timeout=self.options.api_seconds) as response:
                if response.read() != (release / "index.html").read_bytes():
                    raise DeploymentError("Proxy is not serving the exact immutable admin release")
        except (urllib.error.URLError, TimeoutError):
            raise DeploymentError("Deployed admin page is unavailable") from None

    def apply(self) -> None:
        sha = self.ensure_ci()
        if not self.options.strategy:
            raise DeploymentError("Choose an explicit drain or recover strategy")
        if self.options.strategy == "drain" and not self.options.drain_seconds:
            raise DeploymentError("Drain strategy requires an explicit positive --drain-seconds bound")
        self.backup = self.stack_root / ".jane" / "backups" / f"admin-{sha}-{self.suffix}"
        private_directory(self.backup)
        self.log = self.backup / "deployment.log"
        save_json(self.backup / "original-stack-state.json", self.state)
        save_json(self.backup / "original-containers.json", self.containers)
        rollback_images = sorted({c["Image"] for c in [*self.writers, self.storage, self.proxy_container]})
        save_json(
            self.backup / "original-images.json",
            json.loads(run(["docker", "image", "inspect", *rollback_images], log=self.log)),
        )
        release, tags = self.build(sha)
        self.assert_stack_unchanged()
        stopped = False
        try:
            # Independent PostgreSQL dumps + live RAW copy precede even reversible schedule writes.
            # A second, quiescent snapshot follows the writer stop before any image/migration change.
            self.backup_data(self.backup / "pre-pause")
            self.pause_schedules()
            if self.options.strategy == "drain":
                self.wait_drain()
            active = self.active_runs()
            save_json(self.backup / "active-runs.json", active)
            before = self.samples()
            save_json(self.backup / "stored-samples.json", before)
            # No cancellation: graceful shutdown lets current work finish; durable leases/jobs recover.
            self.assert_stack_unchanged()
            stopped = True
            for old in self.writers:
                run(["docker", "stop", "--time", str(self.options.stop_seconds), old["Id"]], log=self.log)
            run(
                ["docker", "stop", "--time", str(self.options.stop_seconds), self.storage["Id"]], log=self.log
            )
            self.backup_data(self.backup / "quiescent")
            self.replace(self.storage, tags["storage"], sha)
            self.replace(self.orchestrator, tags["orchestrator"], sha)
            for old in self.writers:
                if old["Id"] != self.orchestrator["Id"]:
                    self.replace(old, tags["orchestrator"], sha)
            self.verify_modules(self.backup / "source")
            self.verify_recovery(active)
            self.verify_samples(before)
            # Do not restart proxy until backend readiness and data preservation are verified.
            run(
                ["docker", "stop", "--time", str(self.options.stop_seconds), self.proxy_container["Id"]],
                log=self.log,
            )
            self.replace(self.proxy_container, self.proxy_container["Image"], sha, release)
            self.verify_ui(release)
            changed = {c[0]["Id"] for c in self.retained}
            untouched = [c for c in self.containers if c["Id"] not in changed]
            if fingerprint(inspect([c["Id"] for c in untouched])) != fingerprint(untouched):
                raise DeploymentError("A surrounding service configuration changed during deployment")
            updated = copy.deepcopy(self.state)
            updated["env"].update(
                {
                    "JANE_IMAGE_ORCHESTRATOR": tags["orchestrator"],
                    "JANE_IMAGE_STORAGE": tags["storage"],
                    "JANE_ADMIN_DIST_PATH": str(release),
                }
            )
            updated["admin_review_deployment"] = {
                "revision": sha,
                "ci_run": self.options.ci_run,
                "backup": str(self.backup),
                "ui_release": str(release),
            }
            save_json(self.state_path, updated)
        except BaseException:
            if stopped:
                self.rollback()
            raise
        finally:
            self.restore_schedules()
        save_json(
            self.backup / "receipt.json",
            {
                "revision": sha,
                "ci_run": self.options.ci_run,
                "strategy": self.options.strategy,
                "images": tags,
                "backup": str(self.backup),
                "ui_release": str(release),
                "samples_preserved": len(before),
                "writers_updated": len(self.writers),
                "rollback": "Retained original containers and additive-schema compatibility; database dumps are not automatically restored",
            },
        )
        print(
            json.dumps(
                {
                    "revision": sha,
                    "ci_run": self.options.ci_run,
                    "deployed": True,
                    "writers_updated": len(self.writers),
                    "samples_preserved": len(before),
                    "backup": str(self.backup),
                    "ui_release": str(release),
                },
                ensure_ascii=False,
            )
        )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    result.add_argument("command", choices=("plan", "apply"))
    result.add_argument("--stack-state", type=Path, required=True)
    result.add_argument("--sha")
    result.add_argument("--ci-run", type=int)
    result.add_argument("--strategy", choices=("drain", "recover"))
    result.add_argument("--drain-seconds", type=int)
    result.add_argument(
        "--stop-seconds", type=int, default=120, help="Graceful Docker stop bound (default 120s)"
    )
    result.add_argument(
        "--health-seconds", type=int, default=180, help="Service readiness bound (default 180s)"
    )
    result.add_argument("--api-seconds", type=int, default=30, help="API read/write timeout (default 30s)")
    result.add_argument(
        "--poll-seconds", type=float, default=2, help="Drain/health polling interval (default 2s)"
    )
    result.add_argument(
        "--max-pages", type=int, default=10000, help="API pagination safety bound (default 10000 pages)"
    )
    result.add_argument(
        "--max-sample-bytes",
        type=int,
        default=512 * 1024 * 1024,
        help="Maximum bytes read per existing RAW sample (default 512 MiB)",
    )
    result.add_argument(
        "--docker-socket",
        default="/var/run/docker.sock",
        help="Linux Docker Engine socket on the Docker host",
    )
    return result


def main() -> int:
    options = parser().parse_args()
    for name in (
        "stop_seconds",
        "health_seconds",
        "api_seconds",
        "poll_seconds",
        "max_pages",
        "max_sample_bytes",
    ):
        if getattr(options, name) <= 0:
            raise DeploymentError(f"{name} must be positive")
    if options.drain_seconds is not None and options.drain_seconds <= 0:
        raise DeploymentError("drain_seconds must be positive")
    deployment = Deploy(options)
    if options.command == "plan":
        deployment.plan()
    else:
        lock = deployment.state_path.parent / "deploy-admin-review.lock"
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise DeploymentError(
                "Another admin deployment holds the stack lock; inspect it before retrying"
            ) from None
        try:
            os.write(fd, json.dumps({"pid": os.getpid(), "sha": options.sha}).encode())
            deployment.apply()
        finally:
            os.close(fd)
            lock.unlink()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except DeploymentError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
