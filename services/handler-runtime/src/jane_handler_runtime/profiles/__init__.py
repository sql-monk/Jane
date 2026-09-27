"""Runtime profiles: which Python and libraries a sandbox image provides (``dependencies.runtime_profile``).

The machine-readable description (``python-extractor-1.json``) is the list the registry (WP-05) uses to
check ``dependencies.python`` of a manifest (``dependency_not_allowed``); ``GET /v1/info`` publishes it in
``capabilities.runtime_profiles`` and the CLI prints it with ``jane-handler-runtime profile``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from importlib import resources
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

__all__ = ["DependencyProblem", "RuntimeProfile", "check_dependencies", "load_profiles"]


@dataclass(frozen=True)
class RuntimeProfile:
    name: str
    python: str
    libraries: Mapping[str, str]
    document: Mapping[str, Any]

    def marker_environment(self) -> dict[str, str]:
        """PEP 508 marker values of the sandbox (Linux container), not of the host running the runtime."""
        return {
            "python_version": self.python,
            "python_full_version": f"{self.python}.0",
            "sys_platform": "linux",
            "platform_system": "Linux",
            "os_name": "posix",
            "implementation_name": "cpython",
            "platform_python_implementation": "CPython",
        }

    def version_of(self, distribution: str) -> str | None:
        wanted = canonicalize_name(distribution)
        for name, version in self.libraries.items():
            if canonicalize_name(name) == wanted:
                return version
        return None


@dataclass(frozen=True)
class DependencyProblem:
    requirement: str
    message: str


@cache
def load_profiles() -> dict[str, RuntimeProfile]:
    out: dict[str, RuntimeProfile] = {}
    for item in resources.files(__package__).iterdir():
        if item.name.endswith(".json"):
            doc = json.loads(item.read_text(encoding="utf-8"))
            out[doc["profile"]] = RuntimeProfile(doc["profile"], doc["python"], dict(doc["libraries"]), doc)
    return out


def check_dependencies(profile: RuntimeProfile, requirements: Sequence[str]) -> list[DependencyProblem]:
    """PEP 508 requirements of a manifest vs the exact versions of the profile."""
    problems: list[DependencyProblem] = []
    for raw in requirements:
        try:
            req = Requirement(raw)
        except InvalidRequirement as exc:
            problems.append(DependencyProblem(raw, f"invalid requirement: {exc}"))
            continue
        if req.url:
            problems.append(DependencyProblem(raw, "direct URL requirements are not allowed"))
            continue
        if req.marker is not None and not req.marker.evaluate(profile.marker_environment()):
            continue
        version = profile.version_of(req.name)
        if version is None:
            problems.append(
                DependencyProblem(raw, f"{req.name} is not available in runtime profile {profile.name}")
            )
            continue
        try:
            ok = req.specifier.contains(Version(version), prereleases=True)
        except InvalidVersion:
            ok = False
        if not ok:
            problems.append(
                DependencyProblem(
                    raw, f"{req.name}=={version} in runtime profile {profile.name} does not satisfy {raw}"
                )
            )
    return problems
