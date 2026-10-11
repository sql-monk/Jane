"""Add bounded queue consumers to an existing stack, preserving its API container and published ports."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def ensure_workers(stack_file: Path, compose_root: Path, workers: int) -> dict[str, Any]:
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker CLI is not installed")
    stack = json.loads(stack_file.read_text(encoding="utf-8"))
    project = stack.get("project") or stack_file.stem.removeprefix("stack-")
    name = f"{project}-automarket-worker"
    result = subprocess.run(  # noqa: S603 - trusted local stack; argv only
        [docker, "container", "inspect", name], capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        container = json.loads(result.stdout)[0]
        if container["Config"].get("Labels", {}).get("com.docker.compose.project") != project:
            raise RuntimeError(f"{name}: container belongs to another project")
        settings = dict(entry.split("=", 1) for entry in container["Config"]["Env"])
        if settings.get("JANE_ORCHESTRATOR_SCHEDULER_ENABLED") != "false":
            raise RuntimeError(f"{name}: existing container has a scheduler; review it before reuse")
        if settings.get("JANE_ORCHESTRATOR_LIMITS__ENGINE__WORKERS") != str(workers):
            raise RuntimeError(
                f"{name}: another worker count is already configured; review active work before replacing"
            )
        if not container["State"]["Running"]:
            subprocess.run([docker, "start", name], check=True)  # noqa: S603 - verified project container
    else:
        override = stack_file.parent / "automarket-worker.compose.yaml"
        override.write_text(
            "services:\n  orchestrator:\n    healthcheck:\n      disable: true\n", encoding="utf-8"
        )
        command = [
            docker,
            "compose",
            "-f",
            str(compose_root / "infra" / "compose.yaml"),
            "-f",
            str(compose_root / "infra" / "compose.local.yaml"),
            "-f",
            str(override),
            "-p",
            project,
            "run",
            "-d",
            "--no-deps",
            "--pull",
            "never",
            "--name",
            name,
            "-e",
            f"JANE_ORCHESTRATOR_LIMITS__ENGINE__WORKERS={workers}",
            "-e",
            "JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false",
            "orchestrator",
            "python",
            "-m",
            "jane_orchestrator",
            "worker",
        ]
        subprocess.run(command, env={**os.environ, **stack["env"]}, check=True)  # noqa: S603 - local operator configuration; argv only
    subprocess.run([docker, "update", "--restart", "unless-stopped", name], check=True, capture_output=True)  # noqa: S603 - verified project container
    receipt = {"container": name, "workers": workers, "scheduler": False, "restart_policy": "unless-stopped"}
    print(json.dumps(receipt), flush=True)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack-file", required=True, type=Path)
    parser.add_argument("--compose-root", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    ensure_workers(args.stack_file, args.compose_root, args.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
