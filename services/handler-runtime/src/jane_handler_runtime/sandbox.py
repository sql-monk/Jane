"""Sandbox backends (ADR-0003): ``SandboxBackend`` protocol, the workdir bundle, the ``subprocess`` backend.

A run gets a *bundle* - files for the runner's ``<workdir>`` (``request.json``, ``package/...``,
``inputs/<n>``) - and returns raw stdout/stderr and how the process ended. Interpreting the output is the
executor's job, so every backend behaves the same way.
"""

from __future__ import annotations

import io
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Protocol

from .settings import SandboxLimits

__all__ = [
    "INVOCATION_LABEL",
    "Bundle",
    "SandboxBackend",
    "SandboxOutcome",
    "SandboxUnavailable",
    "SubprocessSandbox",
    "read_limited",
]

log = logging.getLogger(__name__)

INVOCATION_LABEL = "io.jane.invocation-id"
"""Label (and subprocess key) that identifies the sandbox of an invocation, used to stop it on cancel."""


class SandboxUnavailable(RuntimeError):
    """The backend cannot run anything (no container engine, image missing, backend disabled)."""


@dataclass
class Bundle:
    """Files of the runner workdir: package path -> bytes (``/`` separators)."""

    files: dict[str, bytes] = field(default_factory=dict)

    def add(self, name: str, data: bytes) -> None:
        if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
            raise ValueError(f"invalid bundle path {name!r}")
        self.files[name] = data

    def tar(self) -> bytes:
        """Tar owned by root with read-only modes: the non-root sandbox user can read but not modify."""
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tar:
            dirs: set[str] = set()
            for name in sorted(self.files):
                parts = PurePosixPath(name).parts
                for i in range(1, len(parts)):
                    d = "/".join(parts[:i])
                    if d not in dirs:
                        dirs.add(d)
                        info = tarfile.TarInfo(d)
                        info.type = tarfile.DIRTYPE
                        info.mode = 0o555
                        tar.addfile(info)
                data = self.files[name]
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o444
                tar.addfile(info, io.BytesIO(data))
        return buf.getvalue()

    def write_to(self, root: Path) -> None:
        for name, data in self.files.items():
            target = root / PurePosixPath(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


@dataclass
class SandboxOutcome:
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    duration_ms: int
    timed_out: bool = False
    oom_killed: bool = False
    stdout_truncated: bool = False
    stderr_truncated: bool = False
    backend: str = ""
    details: dict[str, object] = field(default_factory=dict)


class SandboxBackend(Protocol):
    name: str

    def run(
        self, image: str, bundle: Bundle, limits: SandboxLimits, labels: Mapping[str, str]
    ) -> SandboxOutcome:
        """Run the runner over ``bundle`` with ``limits``; blocks (call it in a worker thread)."""
        ...

    def ping(self) -> None:
        """Raise :class:`SandboxUnavailable` if runs are impossible."""
        ...

    def kill(self, invocation_id: str) -> int:
        """Force-stop the sandbox(es) of ``invocation_id``; returns how many were stopped."""
        ...


def read_limited(stream: io.BufferedIOBase | None, limit: int) -> tuple[bytes, bool]:
    if stream is None:
        return b"", False
    data = stream.read(limit + 1)
    return data[:limit], len(data) > limit


class SubprocessSandbox:
    """Runs the runner as a local process. **No isolation** (no network block, no FS or memory limits):
    only for trusted packages in local development and unit tests; refused unless explicitly allowed."""

    name = "subprocess"

    def __init__(self, allowed: bool, kill_grace_ms: int = 0) -> None:
        self.allowed = allowed
        self.kill_grace_ms = kill_grace_ms
        self._running: dict[str, subprocess.Popen[bytes]] = {}
        self._killed: set[str] = set()

    def kill(self, invocation_id: str) -> int:
        proc = self._running.get(invocation_id)
        if proc is None or proc.poll() is not None:
            return 0
        self._killed.add(invocation_id)
        proc.kill()
        return 1

    def ping(self) -> None:
        if not self.allowed:
            raise SandboxUnavailable(
                "subprocess backend is disabled (set JANE_HANDLER_RUNTIME_ALLOW_UNSAFE_SUBPROCESS=true for "
                "trusted local packages only)"
            )

    def run(
        self, image: str, bundle: Bundle, limits: SandboxLimits, labels: Mapping[str, str]
    ) -> SandboxOutcome:
        self.ping()
        workdir = Path(tempfile.mkdtemp(prefix="jane-sbx-"))
        started = time.monotonic()
        try:
            bundle.write_to(workdir)
            env = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"}
            if os.name == "nt":  # Windows needs these to start Python at all
                env.update({k: os.environ[k] for k in ("SYSTEMROOT", "TEMP", "TMP") if k in os.environ})
            with (
                tempfile.TemporaryFile() as out,
                tempfile.TemporaryFile() as err,
                subprocess.Popen(  # noqa: S603 - fixed argv, no shell
                    [sys.executable, "-I", "-m", "jane_extractor_sdk.runner", str(workdir)],
                    stdout=out,
                    stderr=err,
                    stdin=subprocess.DEVNULL,
                    env=env,
                    cwd=workdir,
                ) as proc,
            ):
                key = labels.get(INVOCATION_LABEL, "")
                self._running[key] = proc
                timed_out = False
                try:
                    proc.wait(timeout=limits.wall_time_ms / 1000)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    proc.kill()
                    proc.wait()
                finally:
                    self._running.pop(key, None)
                killed = key in self._killed
                self._killed.discard(key)
                out.seek(0)
                err.seek(0)
                stdout, out_trunc = read_limited(out, limits.max_output_bytes)  # type: ignore[arg-type,unused-ignore]
                stderr, err_trunc = read_limited(err, limits.max_output_bytes)  # type: ignore[arg-type,unused-ignore]
                return SandboxOutcome(
                    exit_code=proc.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=int((time.monotonic() - started) * 1000),
                    timed_out=timed_out,
                    stdout_truncated=out_trunc,
                    stderr_truncated=err_trunc,
                    backend=self.name,
                    details={"killed": True} if killed else {},
                )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
