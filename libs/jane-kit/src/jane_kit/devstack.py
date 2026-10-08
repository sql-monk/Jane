"""Access to the local dev stack started by ``just up`` (for integration tests).

``just up`` writes ``.jane/stack-<project>.json`` with host ports and generated credentials.
Tests call :func:`load_stack` and skip when the stack is not running.

API keys of the stacks (ADR-0005, ``auth_mode=api_key``): one key per identity of
:data:`STACK_IDENTITIES` in ``JANE_API_KEY_<IDENTITY>`` (the caller's own token) and its SHA-256 in
``JANE_API_KEY_<IDENTITY>_SHA256`` (what the services verify, ``infra/compose.yaml``). ``scripts/dev.py``
(stdlib only) keeps a copy of :func:`new_api_keys`; ``infra/tests/test_auth_config.py`` keeps them equal.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "STACK_IDENTITIES",
    "StackInfo",
    "api_key_var",
    "default_project",
    "find_repo_root",
    "load_stack",
    "new_api_keys",
]

STACK_IDENTITIES: tuple[str, ...] = (
    "admin",
    "orchestrator",
    "assistant",
    "handler-runtime",
    "storage",
    "llm",
    "web-collector",
    "telegram-collector",
    "registry",
)
"""Callers that get a key in a local stack: the operator (admin UI, e2e harness) and every service that calls
another one with its own token (ADR-0005 §5)."""


def api_key_var(identity: str) -> str:
    """``admin`` -> ``JANE_API_KEY_ADMIN`` (the key); ``+ "_SHA256"`` is its hash."""
    return "JANE_API_KEY_" + identity.upper().replace("-", "_")


def new_api_keys(existing: dict[str, str] | None = None) -> dict[str, str]:
    """Keys (and their SHA-256) of every identity missing from ``existing``; existing keys are kept."""
    out: dict[str, str] = {}
    have = existing or {}
    for identity in STACK_IDENTITIES:
        var = api_key_var(identity)
        key = have.get(var) or "jk_" + secrets.token_urlsafe(32)
        out[var] = key
        out[f"{var}_SHA256"] = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return out


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
