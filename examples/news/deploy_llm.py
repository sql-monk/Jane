"""Deploy news fixes and queue settings while preserving the running stack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def capture(args: list[str], *, env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(args, env=env, text=True, encoding="utf-8")  # noqa: S603 - argv, no shell


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack-file", type=Path, required=True)
    parser.add_argument(
        "--service", choices=("llm", "handler-runtime", "orchestrator", "web-collector"), default="llm"
    )
    parser.add_argument("--image")
    ns = parser.parse_args()
    stack_path = ns.stack_file.resolve()
    stack = json.loads(stack_path.read_text(encoding="utf-8"))
    project = stack["project"]
    service = ns.service
    container = f"{project}-{service}-1"
    current = json.loads(capture(["docker", "inspect", container]))[0]
    image = ns.image or (
        current["Config"]["Image"] if service == "web-collector" else f"{project}-{service}:news-monitoring"
    )
    directory = stack_path.parent / "news-deploy" / service
    directory.mkdir(parents=True, exist_ok=True)
    modules = {
        "llm": ("jane_llm.handler",),
        "handler-runtime": ("jane_handler_runtime.executor",),
        "orchestrator": ("jane_orchestrator.engine", "jane_orchestrator.settings"),
        "web-collector": (),
    }[service]
    deployed_files = {}
    dockerfile = f"FROM {current['Config']['Image']}\n"
    for module in modules:
        module_path = module.replace(".", "/") + ".py"
        source = Path(__file__).resolve().parents[2] / f"services/{service}/src/{module_path}"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        target = capture(
            [
                "docker",
                "exec",
                container,
                "python",
                "-c",
                f"import {module}; print({module}.__file__)",
            ]
        ).strip()
        filename = source.name
        shutil.copyfile(source, directory / filename)
        dockerfile += f"COPY {filename} {target}\n"
        deployed_files[module_path] = {"path": target, "sha256": digest}
    if modules:
        (directory / "Dockerfile").write_text(dockerfile, encoding="utf-8", newline="\n")
        subprocess.run(["docker", "build", "-t", image, str(directory)], check=True)  # noqa: S603,S607 - local CLI, no shell
    env = {**os.environ, **{k: str(v) for k, v in stack.get("env", {}).items()}}
    service_env: dict[str, None] = {}
    for value in current["Config"]["Env"]:
        key, _, val = value.partition("=")
        if key.startswith("JANE_"):
            env[key] = val
            service_env[key] = None
    intentional_settings = {}
    if service == "orchestrator":
        intentional_settings = {
            "JANE_ORCHESTRATOR_LIMITS__ENGINE__IDEMPOTENCY_IN_PROGRESS_MAX_WAIT_MS": "1000",
            "JANE_ORCHESTRATOR_LIMITS__ENGINE__IDEMPOTENCY_IN_PROGRESS_RETRY_MS": "5000",
            "JANE_ORCHESTRATOR_LIMITS__ENGINE__ITEM_QUEUE_ORDERING": "run_round_robin",
        }
    elif service == "handler-runtime":
        intentional_settings = {"JANE_HANDLER_RUNTIME_LIMITS__JOBS__MAX_CONCURRENT_JOBS": "8"}
    elif service == "web-collector":
        intentional_settings = {
            "JANE_WEB_COLLECTOR_LIMITS__JOBS__MAX_CONCURRENT_JOBS": "32",
            "JANE_WEB_COLLECTOR_LIMITS__JOBS__JOB_TIMEOUT_MS": "14400000",
        }
    env.update(intentional_settings)
    service_env.update(dict.fromkeys(intentional_settings))
    port = {"llm": "8110", "web-collector": "8101"}.get(service, "8000")
    ports = current["NetworkSettings"]["Ports"][f"{port}/tcp"]
    if len(ports) != 1:
        raise RuntimeError("Expected one published service port")
    env[f"JANE_PORT_{service.upper().replace('-', '_')}"] = ports[0]["HostPort"]
    env["JANE_BIND"] = ports[0]["HostIp"]
    override = directory / "compose.override.json"
    override.write_text(
        json.dumps({"services": {service: {"image": image, "environment": service_env}}}),
        encoding="utf-8",
        newline="\n",
    )
    files = current["Config"]["Labels"]["com.docker.compose.project.config_files"].split(",")
    files = list(dict.fromkeys([*files, str(override)]))
    compose = ["docker", "compose", "--profile", "*", "-p", project]
    for file in files:
        compose.extend(["-f", file])
    # Config contains secrets. Keep it in-process; compare keys without printing any values.
    configured = json.loads(capture([*compose, "config", "--format", "json"], env=env))["services"][service]
    changed = [key for key in service_env if configured["environment"].get(key) != env[key]]
    if changed:
        raise RuntimeError(f"Service environment changed unexpectedly: {changed}")
    subprocess.run([*compose, "up", "-d", "--no-deps", "--no-build", "--wait", service], env=env, check=True)  # noqa: S603 - argv, no shell
    for deployed_file in deployed_files.values():
        code = (
            f"import hashlib; print(hashlib.sha256(open({deployed_file['path']!r},'rb').read()).hexdigest())"
        )
        deployed = capture(["docker", "exec", container, "python", "-c", code]).strip()
        if deployed != deployed_file["sha256"]:
            raise RuntimeError("Deployed service source does not match this checkout")
    receipt: dict[str, Any] = {
        "project": project,
        "container": container,
        "image": image,
        "source_files": deployed_files,
        "port_preserved": ports[0]["HostPort"],
        "environment_preserved": True,
        "intentional_settings": intentional_settings,
    }
    (directory / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
