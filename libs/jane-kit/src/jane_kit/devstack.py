"""Access to the local dev stack started by ``just up`` (for integration tests).

``just up`` writes ``.jane/stack-<project>.json`` with host ports and generated credentials.
Tests call :func:`load_stack` and skip when the stack is not running.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = ["StackInfo", "default_project", "find_repo_root", "load_stack"]


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "justfile").is_file() and (candidate / "infra").is_dir():
            return candidate
    raise FileNotFoundError("Jane repository root (justfile + infra/) not found")


def default_project(root: Path) -> str:
    """Compose project name of a checkout; must stay identical to ``scripts/dev.py:default_project``."""
    if env := os.environ.get("JANE_COMPOSE_PROJECT"):
        return env
    slug = re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")[:24] or "repo"
    digest = hashlib.sha256(str(root).lower().encode()).hexdigest()[:6]
    return f"jane-{slug}-{digest}"


@dataclass(frozen=True)
class StackInfo:
    project: str
    services: dict[str, dict[str, Any]]

    def url(self, service: str, scheme: str = "http") -> str:
        s = self.services[service]
        return f"{scheme}://{s['host']}:{s['port']}"

    def get(self, service: str, key: str) -> Any:
        return self.services[service][key]


def load_stack(project: str | None = None, root: Path | None = None) -> StackInfo | None:
    """Stack description or ``None`` if ``just up`` has not been run for that project.

    Resolution: explicit ``project`` -> env ``JANE_STACK_FILE`` (set by ``just integration``) ->
    this checkout's default project (``JANE_COMPOSE_PROJECT`` or the name ``just up`` derives from the
    checkout path). Never falls back to another project's stack file.
    """
    path: Path
    if project is None and (env_file := os.environ.get("JANE_STACK_FILE")):
        path = Path(env_file)
    else:
        try:
            repo = find_repo_root(root)
        except FileNotFoundError:
            return None
        path = repo / ".jane" / f"stack-{project or default_project(repo)}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return StackInfo(project=data["project"], services=data["services"])
