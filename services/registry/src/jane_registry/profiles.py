"""Runtime profiles and the check of ``dependencies.python`` (ADR-0002 §4, ADR-0003).

A profile (``python-extractor@1``) is published by handler-runtime (WP-06) as a JSON document::

    {"profile": "python-extractor@1", "python": "3.12", "libraries": {"lxml": "6.1.3", ...}, ...}

The registry does not hard-code profiles: it reads them from the configured sources
(``JANE_REGISTRY_RUNTIME_PROFILES`` - files or URLs, e.g. ``<handler-runtime>/v1/info``). The check uses
the same rules as the runtime: every requirement is PEP 508; direct URL requirements are not allowed;
a requirement whose environment marker is false for the sandbox (Linux, the profile's Python) is
skipped; otherwise the distribution must be in the profile and its exact version must satisfy the
specifier (pre-releases allowed).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

from .settings import ProfileLimits

__all__ = ["DependencyProblem", "ProfileSource", "RuntimeProfile", "check_dependencies", "parse_profiles"]

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuntimeProfile:
    name: str
    python: str
    libraries: Mapping[str, str]

    def marker_environment(self) -> dict[str, str]:
        """PEP 508 marker values of the sandbox (a Linux container), not of the registry host."""
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
    index: int
    requirement: str
    message: str


def _profile(doc: Mapping[str, Any]) -> RuntimeProfile:
    return RuntimeProfile(str(doc["profile"]), str(doc["python"]), dict(doc.get("libraries") or {}))


def parse_profiles(doc: Any) -> dict[str, RuntimeProfile]:
    """Profiles from one source document (profile, list, ``runtime_profiles`` map or ``ServiceInfo``)."""
    if isinstance(doc, list):
        out: dict[str, RuntimeProfile] = {}
        for item in doc:
            out.update(parse_profiles(item))
        return out
    if not isinstance(doc, Mapping):
        raise ValueError("runtime profile source must be a JSON object or array")
    if isinstance(doc.get("capabilities"), Mapping) and "runtime_profiles" in doc["capabilities"]:
        return parse_profiles(doc["capabilities"]["runtime_profiles"])
    if "runtime_profiles" in doc:
        return parse_profiles(doc["runtime_profiles"])
    if "profile" in doc and "python" in doc:
        p = _profile(doc)
        return {p.name: p}
    # {"python-extractor@1": {...}, ...}
    out = {}
    for value in doc.values():
        out.update(parse_profiles(value))
    return out


class ProfileSource:
    """Loads profiles from the configured sources and caches them for ``refresh_seconds``."""

    def __init__(
        self,
        sources: Sequence[str],
        limits: ProfileLimits,
        transport: httpx.AsyncBaseTransport | None = None,
        token: str | None = None,
    ) -> None:
        self.sources = list(sources)
        self.limits = limits
        self.transport = transport
        self._token = token
        """Bearer token of the registry for http(s) sources (``GET <runtime>/v1/info`` needs one, ADR-0005)."""
        self._profiles: dict[str, RuntimeProfile] = {}
        self._loaded_at: float | None = None
        self._lock = asyncio.Lock()
        self.errors: list[str] = []

    def known(self) -> list[str]:
        """Names of the profiles loaded so far (``/v1/info``)."""
        return sorted(self._profiles)

    async def _read(self, source: str) -> Any:
        if source.startswith(("http://", "https://")):
            async with httpx.AsyncClient(
                timeout=self.limits.fetch_timeout_ms / 1000, transport=self.transport
            ) as client:
                headers = {"Authorization": f"Bearer {self._token}"} if self._token else None
                response = await client.get(source, headers=headers)
                response.raise_for_status()
                return response.json()
        return json.loads(await asyncio.to_thread(Path(source).read_text, encoding="utf-8"))

    async def profiles(self) -> dict[str, RuntimeProfile]:
        async with self._lock:
            now = time.monotonic()
            if self._loaded_at is not None and now - self._loaded_at < self.limits.refresh_seconds:
                return self._profiles
            loaded: dict[str, RuntimeProfile] = {}
            errors: list[str] = []
            for source in self.sources:
                try:
                    loaded.update(parse_profiles(await self._read(source)))
                except (OSError, ValueError, KeyError, httpx.HTTPError) as exc:
                    errors.append(f"{source}: {type(exc).__name__}: {exc}")
                    log.warning("runtime profile source failed", extra={"source": source, "error": str(exc)})
            if errors and self._profiles:
                loaded = {**self._profiles, **loaded}  # keep the last good copy of failed sources
            self._profiles, self.errors, self._loaded_at = loaded, errors, now
            return self._profiles


def check_dependencies(profile: RuntimeProfile, requirements: Sequence[str]) -> list[DependencyProblem]:
    problems: list[DependencyProblem] = []
    for index, raw in enumerate(requirements):
        try:
            req = Requirement(raw)
        except InvalidRequirement as exc:
            problems.append(DependencyProblem(index, raw, f"invalid requirement: {exc}"))
            continue
        if req.url:
            problems.append(DependencyProblem(index, raw, "direct URL requirements are not allowed"))
            continue
        if req.marker is not None and not req.marker.evaluate(profile.marker_environment()):
            continue
        version = profile.version_of(req.name)
        if version is None:
            problems.append(
                DependencyProblem(
                    index, raw, f"{req.name} is not available in runtime profile {profile.name}"
                )
            )
            continue
        try:
            ok = req.specifier.contains(Version(version), prereleases=True)
        except InvalidVersion:
            ok = False
        if not ok:
            problems.append(
                DependencyProblem(
                    index,
                    raw,
                    f"{req.name}=={version} in runtime profile {profile.name} does not satisfy {raw}",
                )
            )
    return problems
