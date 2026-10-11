from __future__ import annotations

import copy
import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

import pytest

SPEC = importlib.util.spec_from_file_location(
    "jane_deploy_admin_review", Path(__file__).parents[1] / "deploy_admin_review.py"
)
assert SPEC and SPEC.loader
deploy = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = deploy
SPEC.loader.exec_module(deploy)


def container() -> dict[str, Any]:
    return {
        "Id": "a" * 64,
        "Name": "/jane-demo-automarket-priority-worker",
        "Image": "old-image",
        "State": {"Running": True},
        "Config": {
            "Image": "old-tag",
            "Hostname": "a" * 12,
            "Env": ["TOKEN=private", 'TASK_IDS=["ads-autoria"]'],
            "Cmd": ["python", "-m", "jane_orchestrator", "worker"],
            "Entrypoint": None,
            "Labels": {"com.docker.compose.project": "jane-demo"},
            "User": "jane",
        },
        "HostConfig": {
            "Binds": ["volume:/var/lib/data:rw", "C:\\private\\admin:/srv/admin:ro"],
            "PortBindings": {"8000/tcp": [{"HostIp": "127.0.0.1", "HostPort": "54347"}]},
            "RestartPolicy": {"Name": "unless-stopped"},
            "Memory": 1048576,
            "NetworkMode": "jane-demo_default",
        },
        "NetworkSettings": {
            "Networks": {
                "jane-demo_default": {
                    "Aliases": ["orchestrator", "a" * 12],
                    "IPAddress": "172.17.0.8",
                    "IPAMConfig": None,
                }
            }
        },
    }


def test_replacement_preserves_concrete_worker_settings_and_surrounding_mounts(tmp_path: Path) -> None:
    original = container()
    unchanged = copy.deepcopy(original)
    actual = deploy.replacement_config(original, "exact-image", "b" * 40, ui_release=tmp_path)
    assert original == unchanged
    assert actual["Image"] == "exact-image"
    assert actual["Env"] == original["Config"]["Env"]
    assert actual["Cmd"] == ["python", "-m", "jane_orchestrator", "worker"]
    assert actual["HostConfig"]["PortBindings"] == original["HostConfig"]["PortBindings"]
    assert actual["HostConfig"]["Memory"] == 1048576
    assert actual["HostConfig"]["Binds"] == ["volume:/var/lib/data:rw", f"{tmp_path.resolve()}:/srv/admin:ro"]
    assert actual["NetworkingConfig"]["EndpointsConfig"] == {
        "jane-demo_default": {"Aliases": ["orchestrator"], "DriverOpts": {}}
    }
    assert "Hostname" not in actual
    assert actual["Healthcheck"] == {"Test": ["NONE"]}


@pytest.mark.parametrize("binds", [[], ["a:/srv/admin:ro", "b:/srv/admin:ro"]])
def test_ui_mount_must_have_one_unambiguous_existing_target(tmp_path: Path, binds: list[str]) -> None:
    original = container()
    original["HostConfig"]["Binds"] = binds
    with pytest.raises(deploy.DeploymentError, match="exactly one"):
        deploy.replacement_config(original, "image", "sha", ui_release=tmp_path)


def test_ci_rejects_skipped_adapter_and_wrong_revision() -> None:
    sha = "b" * 40
    info = {
        "head_sha": sha,
        "status": "completed",
        "conclusion": "success",
        "path": ".github/workflows/ci.yml",
    }
    jobs = [{"name": name, "conclusion": "success"} for name in deploy.CI_JOBS]
    deploy.validate_ci(info, jobs, sha)
    next(job for job in jobs if job["name"] == "adapters (s3)")["conclusion"] = "skipped"
    with pytest.raises(deploy.DeploymentError, match="14 required"):
        deploy.validate_ci(info, jobs, sha)
    with pytest.raises(deploy.DeploymentError, match="exact"):
        deploy.validate_ci(info, jobs, "c" * 40)


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE items;",
        "ALTER TABLE items DROP COLUMN payload;",
        "UPDATE items SET status='cancelled';",
        "TRUNCATE runs;",
    ],
)
def test_rollback_refuses_destructive_migrations(sql: str) -> None:
    with pytest.raises(deploy.DeploymentError, match="non-additive"):
        deploy.validate_additive_migrations(
            ["CREATE TABLE old (a integer);"], ["CREATE TABLE old (a integer);", sql]
        )


def test_additive_migration_preserves_previous_definitions() -> None:
    old = ["CREATE TABLE old (a integer);"]
    new = [
        *old,
        "ALTER TABLE items ADD COLUMN outputs_complete boolean; CREATE TABLE ids (id text REFERENCES old(a) ON DELETE CASCADE);",
    ]
    deploy.validate_additive_migrations(old, new)
    with pytest.raises(deploy.DeploymentError, match="Previously applied"):
        deploy.validate_additive_migrations(old, ["CREATE TABLE old (a text);"])
    assert deploy.migrations("MIGRATIONS: list[str] = ['CREATE TABLE old (a integer);']") == old


def fake_deployment(tmp_path: Path) -> Any:
    instance = deploy.Deploy.__new__(deploy.Deploy)
    instance.backup = tmp_path
    instance.replacement_by_old = {}
    instance.paused = {
        "task": {
            "original_schedule": {"type": "interval", "interval_seconds": 3600},
            "paused_schedule": {"type": "interval", "interval_seconds": 3600, "enabled": False},
        }
    }
    return instance


def test_schedule_restore_keeps_concurrent_task_edits_and_uses_latest_etag(tmp_path: Path) -> None:
    instance = fake_deployment(tmp_path)
    current = {
        "task_id": "task",
        "title": "User's new title",
        "schedule": instance.paused["task"]["paused_schedule"],
    }
    calls: list[dict[str, Any]] = []

    def api(_service: str, _path: str, **kwargs: Any) -> tuple[Any, str]:
        if kwargs.get("method") == "PUT":
            calls.append(kwargs)
        return copy.deepcopy(current), '"latest"'

    instance.api = api
    instance.restore_schedules()
    assert calls[0]["body"]["title"] == "User's new title"
    assert calls[0]["body"]["schedule"] == {"type": "interval", "interval_seconds": 3600}
    assert calls[0]["etag"] == '"latest"'
    assert instance.paused == {}


def test_schedule_restore_refuses_to_overwrite_user_schedule_change(tmp_path: Path) -> None:
    instance = fake_deployment(tmp_path)
    calls: list[dict[str, Any]] = []

    def api(_service: str, _path: str, **kwargs: Any) -> tuple[Any, str]:
        calls.append(kwargs)
        return {"schedule": {"type": "manual"}}, '"new"'

    instance.api = api
    with pytest.raises(deploy.DeploymentError, match="manual restoration"):
        instance.restore_schedules()
    assert all(call.get("method") != "PUT" for call in calls)
    assert "task" in instance.paused


def test_drain_timeout_never_cancels_a_real_run(tmp_path: Path) -> None:
    instance = fake_deployment(tmp_path)
    instance.options = Namespace(drain_seconds=0, poll_seconds=0.01)
    instance.active_runs = lambda: [{"run_id": "real-user-run", "status": "running"}]
    with pytest.raises(deploy.DeploymentError, match="Drain deadline expired"):
        instance.wait_drain()


def test_private_tokens_are_not_forwarded_on_redirect() -> None:
    handler = deploy.NoRedirect()
    assert handler.redirect_request(None, None, 302, "Moved", {}, "https://external.invalid") is None


def test_worker_only_replacement_preserves_disabled_health_probe_and_checks_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    instance = fake_deployment(tmp_path)
    instance.backup = None
    instance.log = None
    instance.retained = []
    instance.created = []
    instance.suffix = "test"
    calls: list[str] = []

    def engine(_method: str, path: str, _body: Any = None) -> dict[str, str]:
        return {"Id": "new-writer"} if path.startswith("/containers/create?") else {}

    def must_not_wait(_name: str) -> None:
        pytest.fail("Worker-only process has no HTTP health endpoint")

    instance.engine = engine
    instance.wait_health = must_not_wait
    instance.verify_running = calls.append
    monkeypatch.setattr(deploy, "run", lambda *_args, **_kwargs: b"")
    old = container()
    old["Config"]["Healthcheck"] = {"Test": ["NONE"]}
    instance.replace(old, "exact-image", "b" * 40)
    assert calls == ["jane-demo-automarket-priority-worker"]
    assert instance.created == ["new-writer"]


class DockerNeighbor:
    """Effective Docker state and failures; deployment/rollback code stays real."""

    def __init__(self, originals: list[dict[str, Any]], fault: tuple[str, str] | None = None) -> None:
        self.containers: dict[str, dict[str, Any]] = {}
        self.calls: list[tuple[str, str]] = []
        self.fault = fault
        for original in originals:
            old = copy.deepcopy(original)
            old["Name"] += "-before-admin"
            old["State"]["Running"] = False
            old["NetworkSettings"]["Networks"] = {}
            self.containers[old["Id"]] = old
            new = copy.deepcopy(original)
            new["Id"] = original["Id"].replace("old-", "new-")
            self.containers[new["Id"]] = new

    def failure(self, phase: str, container_id: str) -> None:
        self.calls.append((phase, container_id))
        if self.fault == (phase, container_id):
            self.fault = None
            raise deploy.DeploymentError("Injected Docker failure with private configuration detail")

    def resolve(self, name: str) -> dict[str, Any]:
        if name in self.containers:
            return self.containers[name]
        return next(c for c in self.containers.values() if c["Name"].lstrip("/") == name)

    def run(self, args: list[str], **kwargs: Any) -> bytes:
        assert args[0] == "docker"
        operation = args[1]
        if operation == "inspect":
            for name in args[2:]:
                self.failure("inspect", name)
            return json.dumps([self.resolve(name) for name in args[2:]]).encode()
        if operation in ("stop", "rm", "rename", "start"):
            container_id = args[-2] if operation == "rename" else args[-1]
            self.failure(operation, container_id)
            actual = self.resolve(container_id)
            if operation == "stop":
                actual["State"]["Running"] = False
            elif operation == "rm":
                assert not actual["State"]["Running"]
                del self.containers[container_id]
            elif operation == "rename":
                target = "/" + args[-1]
                if any(c["Name"] == target and c["Id"] != container_id for c in self.containers.values()):
                    raise deploy.DeploymentError("Container name still occupied")
                actual["Name"] = target
            else:
                actual["State"]["Running"] = True
            return b""
        if operation == "run":
            request = json.loads(kwargs["stdin"])
            container_id = request["body"]["Container"]
            self.failure("connect", container_id)
            assert request["path"].endswith("/connect")
            network = request["path"].split("/")[2]
            self.resolve(container_id)["NetworkSettings"]["Networks"][network] = request["body"][
                "EndpointConfig"
            ]
            return b"{}"
        raise AssertionError(f"Unexpected Docker neighbor operation {operation}")


def rollback_fixture(tmp_path: Path, fault: tuple[str, str] | None = None) -> tuple[Any, DockerNeighbor]:
    instance = fake_deployment(tmp_path)
    instance.log = tmp_path / "deployment.log"
    instance.options = Namespace(
        stop_seconds=1, health_seconds=0.01, poll_seconds=0.001, docker_socket="/var/run/docker.sock"
    )
    originals = []
    for kind in ("storage", "main", "priority", "proxy"):
        original = container()
        original["Id"] = "old-" + kind
        original["Name"] = "/jane-demo-" + kind
        original["Config"]["Healthcheck"] = (
            {"Test": ["NONE"]} if kind == "priority" else {"Test": ["CMD", "true"]}
        )
        original["State"] = {"Running": True, "Health": {"Status": "healthy"}}
        originals.append(original)
    instance.storage, instance.orchestrator, priority, instance.proxy_container = originals
    instance.writers = [instance.orchestrator, priority]
    instance.created = ["new-" + kind for kind in ("storage", "main", "priority", "proxy")]
    instance.retained = [(original, original["Name"] + "-before-admin") for original in originals]
    instance.replacement_by_old = {
        old["Id"]: new for old, new in zip(originals, instance.created, strict=True)
    }
    instance.state_path = tmp_path / "stack-state.json"
    instance.state = {"project": "jane-demo", "preserved": "original"}
    return instance, DockerNeighbor(originals, fault)


@pytest.mark.parametrize("phase", ["stop", "rm", "rename", "connect", "start", "inspect"])
def test_rollback_continues_independent_writer_restore_after_other_container_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    # Proxy is first in reverse stop order. Its failure must not abandon old backend writers.
    target = "new-proxy" if phase in ("stop", "rm", "inspect") else "old-proxy"
    instance, docker = rollback_fixture(tmp_path, (phase, target))
    monkeypatch.setattr(deploy, "run", docker.run)
    with pytest.raises(deploy.DeploymentError, match="Rollback incomplete") as caught:
        instance.rollback()
    assert ("start", "old-main") in docker.calls
    assert ("start", "old-priority") in docker.calls
    assert docker.containers["old-main"]["State"]["Running"]
    assert "private configuration" not in str(caught.value)
    journal = json.loads((tmp_path / "rollback-journal.json").read_text())
    assert any(entry["status"] == "failed" for entry in journal)
    assert any(
        entry["action"] == "start_old"
        and entry["container_id"] == "old-main"
        and entry["status"] == "succeeded"
        for entry in journal
    )


@pytest.mark.parametrize("phase", ["stop", "inspect"])
def test_rollback_never_starts_old_writers_beside_unconfirmed_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    instance, docker = rollback_fixture(tmp_path, (phase, "new-priority"))
    monkeypatch.setattr(deploy, "run", docker.run)
    with pytest.raises(deploy.DeploymentError, match="Rollback incomplete"):
        instance.rollback()
    assert ("start", "old-main") not in docker.calls
    assert ("start", "old-priority") not in docker.calls
    # Other safe recovery phases still run despite holding the original writer pool.
    assert ("start", "old-storage") in docker.calls
    assert ("start", "old-proxy") in docker.calls
    journal = json.loads((tmp_path / "rollback-journal.json").read_text())
    assert any(
        entry["action"] == "start_old" and entry["container_id"] == "old-main" and entry["status"] == "held"
        for entry in journal
    )


def test_successful_rollback_restores_original_identity_and_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    instance, docker = rollback_fixture(tmp_path)
    monkeypatch.setattr(deploy, "run", docker.run)
    instance.rollback()
    assert set(docker.containers) == {"old-storage", "old-main", "old-priority", "old-proxy"}
    assert all(c["State"]["Running"] for c in docker.containers.values())
    assert json.loads(instance.state_path.read_text()) == instance.state
    assert all(
        entry["status"] == "succeeded"
        for entry in json.loads((tmp_path / "rollback-journal.json").read_text())
    )


@pytest.mark.parametrize("drift", ["running", "aliases", "ipam", "network"])
def test_pre_stop_drift_guard_aborts_without_container_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, drift: str
) -> None:
    instance = fake_deployment(tmp_path)
    instance.project = "jane-demo"
    original = container()
    instance.containers = [original]
    instance.original_fingerprint = deploy.fingerprint([original])
    current = copy.deepcopy(original)
    if drift == "running":
        current["State"]["Running"] = False
    elif drift == "aliases":
        current["NetworkSettings"]["Networks"]["jane-demo_default"]["Aliases"] = ["user-selected-alias"]
    elif drift == "ipam":
        current["NetworkSettings"]["Networks"]["jane-demo_default"]["IPAMConfig"] = {
            "IPv4Address": "172.17.0.17"
        }
    else:
        current["NetworkSettings"]["Networks"] = {}
    calls: list[list[str]] = []

    def docker(args: list[str], **_kwargs: Any) -> bytes:
        calls.append(args)
        if args[:2] == ["docker", "ps"]:
            return str(original["Id"]).encode()
        assert args[:2] == ["docker", "inspect"]
        return json.dumps([current]).encode()

    monkeypatch.setattr(deploy, "run", docker)
    with pytest.raises(deploy.DeploymentError, match="no containers were stopped"):
        instance.assert_stack_unchanged()
    assert calls == [
        ["docker", "ps", "-aq", "--filter", "label=com.docker.compose.project=jane-demo"],
        ["docker", "inspect", original["Id"]],
    ]


def test_new_shared_writer_during_build_aborts_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    instance = fake_deployment(tmp_path)
    instance.project = "jane-demo"
    original = container()
    instance.containers = [original]
    instance.original_fingerprint = deploy.fingerprint([original])
    calls: list[list[str]] = []

    def docker(args: list[str], **_kwargs: Any) -> bytes:
        calls.append(args)
        assert args[:2] == ["docker", "ps"]
        return (str(original["Id"]) + "\nnew-user-writer").encode()

    monkeypatch.setattr(deploy, "run", docker)
    with pytest.raises(deploy.DeploymentError, match="no containers were stopped"):
        instance.assert_stack_unchanged()
    assert len(calls) == 1
