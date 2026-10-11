"""Deploy operations on top of live images, preserving other chats' runtime patches.

Private deployment manifests (including existing environment) remain in ignored .jane/.
No volume or operational record is removed. Only explicitly selected module containers restart.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "web-collector",
    "telegram-collector",
    "handler-runtime",
    "storage",
    "llm",
    "assistant",
    "registry",
    "orchestrator",
]


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd or ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"{args[0]} {args[1]} failed (exit {result.returncode}): {result.stderr[-2000:]}")
    return result.stdout


def merge_live(source: str, live: Path, output: Path) -> None:
    original = run("git", "show", f"0b554fce30bce5aa7def84d351575e23862f66b8:{source}")
    base = output.with_suffix(".base")
    base.write_text(original, encoding="utf-8", newline="\n")
    live.write_text(live.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    output.write_text((ROOT / source).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    merged = run("git", "merge-file", "-p", str(output), str(base), str(live))
    output.write_text(merged, encoding="utf-8", newline="\n")


def snapshot_service(container: dict[str, Any], image: str) -> dict[str, Any]:
    config, host = container["Config"], container["HostConfig"]
    service: dict[str, Any] = {
        "image": image,
        "container_name": container["Name"].lstrip("/"),
        "environment": dict(item.split("=", 1) for item in config["Env"]),
        "networks": {
            name: {"aliases": network.get("Aliases") or []}
            for name, network in container["NetworkSettings"]["Networks"].items()
        },
        "volumes": [],
    }
    for mount in container["Mounts"]:
        service["volumes"].append(
            {
                "type": mount["Type"],
                "source": mount.get("Name") or mount["Source"],
                "target": mount["Destination"],
                "read_only": not mount["RW"],
            }
        )
    for source, target in [
        ("Cmd", "command"),
        ("Entrypoint", "entrypoint"),
        ("User", "user"),
        ("WorkingDir", "working_dir"),
    ]:
        if config.get(source):
            service[target] = config[source]
    if host.get("PortBindings"):
        service["ports"] = [
            f"{binding['HostIp'] or '127.0.0.1'}:{binding['HostPort']}:{port}"
            for port, bindings in host["PortBindings"].items()
            for binding in bindings or []
        ]
    policy = host["RestartPolicy"]
    service["restart"] = policy["Name"] or "no"
    if policy["Name"] == "on-failure" and policy["MaximumRetryCount"]:
        service["restart"] += f":{policy['MaximumRetryCount']}"
    for source, target in [
        ("ExtraHosts", "extra_hosts"),
        ("SecurityOpt", "security_opt"),
        ("CapAdd", "cap_add"),
        ("CapDrop", "cap_drop"),
    ]:
        if host.get(source):
            service[target] = host[source]
    service["shm_size"] = host["ShmSize"]
    if host.get("GroupAdd"):
        service["group_add"] = host["GroupAdd"]
    if host.get("Tmpfs"):
        service["tmpfs"] = [f"{path}:{options}" for path, options in host["Tmpfs"].items()]
    if host.get("ReadonlyRootfs"):
        service["read_only"] = True
    if host.get("Init") is not None:
        service["init"] = host["Init"]
    if host.get("Memory"):
        service["mem_limit"] = host["Memory"]
    if host.get("NanoCpus"):
        service["cpus"] = host["NanoCpus"] / 1_000_000_000
    if config.get("Healthcheck"):
        health = config["Healthcheck"]
        service["healthcheck"] = {"test": health["Test"]}
        for source, target in [
            ("Interval", "interval"),
            ("Timeout", "timeout"),
            ("StartPeriod", "start_period"),
        ]:
            if health.get(source):
                service["healthcheck"][target] = f"{health[source]}ns"
        if health.get("Retries"):
            service["healthcheck"]["retries"] = health["Retries"]
    return service


def prepare(project: str, names: list[str]) -> Path:
    directory = ROOT / ".jane" / "operations-deploy" / project
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "compose.private.json"
    previous = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    services, networks, volumes = (previous.get(key, {}) for key in ["services", "networks", "volumes"])
    snapshot_path = directory / "before.private.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8")) if snapshot_path.exists() else []
    for name in names:
        container = json.loads(run("docker", "inspect", f"{project}-{name}-1"))[0]
        if container["Config"]["Labels"].get("com.docker.compose.project") != project:
            raise RuntimeError("Container project does not match requested deployment")
        snapshot = [item for item in snapshot if item["Name"] != container["Name"]]
        snapshot.append(container)
        context = directory / name
        context.mkdir(exist_ok=True)
        base_tag = f"{project}-operations-base-{name}:{container['Image'][7:19]}"
        run("docker", "image", "tag", container["Image"], base_tag)
        package = "/app/.venv/lib/python3.12/site-packages/jane_kit"
        for file in ["config.py", "service.py", "auth.py"]:
            live = context / f"{file}.live"
            run("docker", "cp", f"{container['Id']}:{package}/{file}", str(live))
            merge_live(f"libs/jane-kit/src/jane_kit/{file}", live, context / file)
        shutil.copyfile(ROOT / "libs/jane-kit/src/jane_kit/operations.py", context / "operations.py")
        dockerfile = (
            f"FROM {base_tag}\nUSER root\nCOPY config.py service.py auth.py operations.py {package}/\n"
        )
        if name == "orchestrator":
            live = context / "app.py.live"
            run(
                "docker",
                "cp",
                f"{container['Id']}:/app/.venv/lib/python3.12/site-packages/jane_orchestrator/app.py",
                str(live),
            )
            merge_live("services/orchestrator/src/jane_orchestrator/app.py", live, context / "app.py")
            dockerfile += "COPY app.py /app/.venv/lib/python3.12/site-packages/jane_orchestrator/app.py\n"
        user = container["Config"]["User"] or "root"
        if not all(character.isalnum() or character in ":_-" for character in user):
            raise RuntimeError("Unexpected image user")
        dockerfile += (
            f"RUN mkdir -p /var/lib/jane-operations && chown {user} /var/lib/jane-operations\nUSER {user}\n"
        )
        (context / "Dockerfile").write_text(dockerfile, encoding="utf-8")
        image = f"{project}-operations-{name}:stage1"
        print(f"Building operations overlay: {name}", flush=True)
        run("docker", "build", "-t", image, str(context))
        service = snapshot_service(container, image)
        service["volumes"] = [
            mount for mount in service["volumes"] if mount["target"] != "/var/lib/jane-operations"
        ]
        prefix = "JANE_" + name.upper().replace("-", "_") + "_"
        service["environment"][prefix + "OPERATIONS_DIR"] = "/var/lib/jane-operations"
        keys_name = prefix + "API_KEYS"
        if keys_name in service["environment"]:
            keys = json.loads(service["environment"][keys_name])
            for key in keys:
                if key.get("name") == "admin":
                    key["scopes"] = sorted(set(key.get("scopes", [])) | {"modules:read", "modules:write"})
            service["environment"][keys_name] = json.dumps(keys)
        volume = f"{project}-operations-{name}"
        service["volumes"].append({"type": "volume", "source": volume, "target": "/var/lib/jane-operations"})
        volumes[volume] = {"name": volume}
        services[name] = service
        for network in service["networks"]:
            networks[network] = {"external": True, "name": network}
        for mount in container["Mounts"]:
            if mount["Type"] == "volume":
                volumes[mount["Name"]] = {"external": True, "name": mount["Name"]}
    (directory / "before.private.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    manifest.write_text(
        json.dumps({"services": services, "networks": networks, "volumes": volumes}, indent=2),
        encoding="utf-8",
    )
    # Only report syntax, never render the private compose environment in tool output.
    run("docker", "compose", "-p", project, "-f", str(manifest), "config", "--quiet")
    print(f"Prepared {len(services)} module overlays; operational volumes preserved", flush=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="jane-demo")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--services", nargs="+", choices=MODULES, default=MODULES)
    args = parser.parse_args()
    if not args.project or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in args.project):
        raise ValueError("Project must be a lowercase Docker project name")
    manifest = (
        prepare(args.project, args.services)
        if args.prepare
        else ROOT / ".jane" / "operations-deploy" / args.project / "compose.private.json"
    )
    if args.deploy:
        prepared = json.loads(manifest.read_text(encoding="utf-8"))
        snapshots = json.loads((manifest.parent / "before.private.json").read_text(encoding="utf-8"))
        for name in args.services:
            live = json.loads(run("docker", "inspect", f"{args.project}-{name}-1"))[0]
            before = next(item for item in snapshots if item["Name"] == live["Name"])
            desired = run(
                "docker", "image", "inspect", prepared["services"][name]["image"], "--format", "{{.Id}}"
            ).strip()
            if live["Image"] not in {before["Image"], desired}:
                raise RuntimeError(
                    f"{name} changed since preparation; prepare its overlay again to preserve newer changes"
                )
            print(f"Updating module: {name}", flush=True)
            run(
                "docker",
                "compose",
                "-p",
                args.project,
                "-f",
                str(manifest),
                "up",
                "-d",
                "--no-deps",
                name,
            )
            deadline = time.monotonic() + 180
            while True:
                state = json.loads(run("docker", "inspect", f"{args.project}-{name}-1"))[0]["State"]
                if state.get("Running") and state.get("Health", {}).get("Status", "healthy") == "healthy":
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError(f"{name} did not become healthy within startup allowance")
                time.sleep(2)
            print(f"Healthy: {name}", flush=True)


if __name__ == "__main__":
    main()
