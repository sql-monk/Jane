"""Access to the local dev stack started by ``just up`` (for integration tests).

``just up`` writes ``.jane/stack-<project>.json`` with host ports and generated credentials.
Tests call :func:`load_stack` and skip when the stack is not running.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = ["StackInfo", "find_repo_root", "load_stack"]


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "justfile").is_file() and (candidate / "infra").is_dir():
            return candidate
    raise FileNotFoundError("Jane repository root (justfile + infra/) not found")


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
    """Stack description or ``None`` if ``just up`` has not been run for this project.

    Resolution: explicit ``project`` -> env ``JANE_STACK_FILE`` -> the only/first ``.jane/stack-*.json``.
    """
    if env_file := os.environ.get("JANE_STACK_FILE"):
        path: Path | None = Path(env_file)
    else:
        try:
            base = find_repo_root(root) / ".jane"
        except FileNotFoundError:
            return None
        if project:
            path = base / f"stack-{project}.json"
        else:
            found = sorted(base.glob("stack-*.json"))
            path = found[0] if found else None
    if path is None or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return StackInfo(project=data["project"], services=data["services"])
