"""Build the reviewed collector and apply catalog capacity settings to an existing stack.

Reads the git-ignored dev-stack state. Credentials stay in the subprocess environment.
Collector, registry, orchestrator and handler containers are recreated; volumes are preserved.
Optionally publish the built admin UI as an immutable release and recreate the proxy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--publish-admin", action="store_true")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--sandboxes", type=int, default=8)
    ns = parser.parse_args()
    if ns.workers < 1 or ns.sandboxes < 1:
        parser.error("workers and sandboxes must be positive")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", ns.project):
        parser.error("invalid compose project name")
    state_path = ns.state or ROOT / ".jane" / f"stack-{ns.project}.json"
    stack = json.loads(state_path.read_text(encoding="utf-8"))
    if stack["project"] != ns.project:
        parser.error("stack state belongs to a different project")
    base = Path(stack["compose_file"])
    env = os.environ.copy()
    env.update({k: str(v) for k, v in stack["env"].items()})
    # Docker-selected ports otherwise change when a container is recreated.
    for service, config in stack["services"].items():
        if config.get("port"):
            env[f"JANE_PORT_{service.upper().replace('-', '_')}"] = str(config["port"])
    env["JANE_CATALOG_WORKERS"] = str(ns.workers)
    env["JANE_CATALOG_SANDBOXES"] = str(ns.sandboxes)
    command = ["docker", "compose", "-p", ns.project, "-f", str(base)]
    local = base.with_name("compose.local.yaml")
    if local.is_file():
        command += ["-f", str(local)]
    command += ["-f", str(HERE / "compose.catalogs.yaml")]
    # Build context must be this reviewed checkout, while ports and volumes belong to the existing stack.
    override = ROOT / ".jane" / f"catalog-build-{ns.project}.json"
    override.parent.mkdir(parents=True, exist_ok=True)
    override_doc: dict[str, Any] = {
        "services": {name: {"build": {"context": str(ROOT)}} for name in ("web-collector", "registry")}
    }
    override_doc["services"]["registry"]["image"] = f"{ns.project}-catalog-registry:latest"
    override_doc["services"]["web-collector"]["image"] = f"{ns.project}-catalog-web-collector:latest"
    # Capacity changes must preserve modules deployed by other coordinated work in this stack.
    for service in ("orchestrator", "handler-runtime"):
        running_image = subprocess.check_output(  # noqa: S603 - fixed docker argv and validated project
            ["docker", "inspect", f"{ns.project}-{service}-1", "--format", "{{json .Config.Image}}"],  # noqa: S607 - docker is the required CLI
            text=True,
        )
        override_doc["services"][service] = {"image": json.loads(running_image), "pull_policy": "never"}
    command += ["-f", str(override)]
    if ns.publish_admin:
        dist = ROOT / "web" / "admin" / "dist"
        if not (dist / "index.html").is_file():
            parser.error("build web/admin before --publish-admin")
        digest = hashlib.sha256()
        for path in sorted(p for p in dist.rglob("*") if p.is_file()):
            digest.update(path.relative_to(dist).as_posix().encode())
            digest.update(path.read_bytes())
        release = base.parent.parent / ".jane" / "releases" / f"admin-{digest.hexdigest()[:16]}"
        if not release.exists():
            shutil.copytree(dist, release)
        env["JANE_ADMIN_DIST_PATH"] = str(release)
        # Replace a possible hard-coded local override by mount target, preserving config/Caddyfile mounts.
        override_doc["services"]["proxy"] = {
            "volumes": [{"type": "bind", "source": str(release), "target": "/srv/admin", "read_only": True}]
        }
    override.write_text(json.dumps(override_doc), encoding="utf-8")
    if ns.build:
        subprocess.run([*command, "build", "web-collector", "registry"], check=True, env=env)  # noqa: S603 - argv, validated project, trusted stack
    subprocess.run(  # noqa: S603 - fixed executable and argv, never a shell
        [*command, "up", "-d", "--no-deps", "web-collector", "registry", "orchestrator", "handler-runtime"],
        check=True,
        env=env,
    )
    if ns.publish_admin:
        subprocess.run([*command, "up", "-d", "--no-deps", "proxy"], check=True, env=env)  # noqa: S603 - fixed argv
        stack["env"]["JANE_ADMIN_DIST_PATH"] = str(release)
        # Persist only the new release pointer in the already private stack-state file.
        state_path.write_text(json.dumps(stack, ensure_ascii=False, indent=2), encoding="utf-8")
        primary_state = base.parent.parent / ".jane" / state_path.name
        if primary_state.resolve() != state_path.resolve() and primary_state.is_file():
            primary = json.loads(primary_state.read_text(encoding="utf-8"))
            if primary.get("project") == ns.project:
                primary["env"]["JANE_ADMIN_DIST_PATH"] = str(release)
                primary_state.write_text(json.dumps(primary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Applied catalog runtime to {ns.project}: workers={ns.workers}, sandboxes={ns.sandboxes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
