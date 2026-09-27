"""Docker/Podman backend (ADR-0003): one fresh container per invocation through the Engine API.

Container settings - every number comes from ``limits.sandbox``:

* ``network_mode=none`` (no interfaces but loopback), no host volumes, no secrets in the environment;
* read-only root FS, ``tmpfs`` ``/tmp`` (``tmpfs_mb``), non-root user, ``cap_drop=ALL``,
  ``no-new-privileges``, default seccomp, optional OCI runtime (``runsc``);
* ``memory_mb`` (swap disabled: ``memswap == memory``), ``cpu_cores`` (``nano_cpus``), ``max_processes``
  (``pids_limit``);
* the workdir (package + request + inputs) is copied into an anonymous volume ``/work`` before start, owned by
  root with read-only modes; the volume is removed together with the container;
* ``wall_time_ms``: the runtime kills the container when it is exceeded (``failed``/``timeout``), and inside the
  container ``timeout -s KILL`` fires ``kill_grace_ms`` later as a safety net if the runtime itself died;
* stdout/stderr are read up to ``max_output_bytes``; OOM is taken from the container state.
"""

from __future__ import annotations

import contextlib
import logging
import time
import uuid
from collections.abc import Iterator, Mapping
from typing import Any

import docker  # type: ignore[import-untyped]
from docker.errors import APIError, DockerException, ImageNotFound, NotFound  # type: ignore[import-untyped]
from docker.types import LogConfig  # type: ignore[import-untyped]
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout

from .sandbox import INVOCATION_LABEL, Bundle, SandboxOutcome, SandboxUnavailable
from .settings import SandboxLimits

__all__ = ["SANDBOX_LABEL", "DockerSandbox"]

log = logging.getLogger(__name__)

SANDBOX_LABEL = "io.jane.handler-runtime.sandbox"
WORKDIR = "/work"
SANDBOX_TMP = "/tmp"  # noqa: S108 - a tmpfs inside the container, not a host path
RUNNER = ["python", "-I", "-m", "jane_extractor_sdk.runner", WORKDIR]


def _read_stream(chunks: Iterator[bytes], limit: int) -> tuple[bytes, bool]:
    buf = bytearray()
    for chunk in chunks:
        buf.extend(chunk)
        if len(buf) > limit:
            return bytes(buf[:limit]), True
    return bytes(buf), False


class DockerSandbox:
    name = "docker"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        runtime: str | None = None,
        user: str = "65534:65534",
        api_timeout_s: float = 60.0,
        kill_grace_ms: int = 2_000,
        extra_labels: Mapping[str, str] | None = None,
    ) -> None:
        self._base_url = base_url
        self._api_timeout_s = api_timeout_s
        self._client: Any = None
        self.runtime = runtime
        self.user = user
        self.kill_grace_ms = kill_grace_ms
        self.extra_labels = dict(extra_labels or {})

    @property
    def api(self) -> Any:
        if self._client is None:
            try:
                if self._base_url:
                    self._client = docker.DockerClient(
                        base_url=self._base_url, version="auto", timeout=self._api_timeout_s
                    )
                else:
                    self._client = docker.from_env(version="auto", timeout=self._api_timeout_s)
            except DockerException as exc:
                raise SandboxUnavailable(f"container engine is not reachable: {exc}") from exc
        return self._client.api

    def ping(self) -> None:
        try:
            self.api.ping()
        except (DockerException, RequestsConnectionError) as exc:
            raise SandboxUnavailable(f"container engine is not reachable: {exc}") from exc

    def has_image(self, image: str) -> bool:
        try:
            self.api.inspect_image(image)
        except ImageNotFound:
            return False
        return True

    def run(
        self, image: str, bundle: Bundle, limits: SandboxLimits, labels: Mapping[str, str]
    ) -> SandboxOutcome:
        api = self.api
        wall_s = limits.wall_time_ms / 1000
        safety_s = max(1, int((limits.wall_time_ms + self.kill_grace_ms + 999) // 1000))
        tmpfs = (
            {SANDBOX_TMP: f"rw,nosuid,nodev,noexec,size={limits.tmpfs_mb}m,mode=1777"}
            if limits.tmpfs_mb
            else None
        )
        host_config = api.create_host_config(
            network_mode="none",
            read_only=True,
            tmpfs=tmpfs,
            mem_limit=f"{limits.memory_mb}m",
            memswap_limit=f"{limits.memory_mb}m",
            nano_cpus=int(limits.cpu_cores * 1e9),
            pids_limit=limits.max_processes,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            ipc_mode="none",
            runtime=self.runtime,
            init=False,
            # Bounded engine-side log: both streams fit (reading stops at max_output_bytes each).
            log_config=LogConfig(
                type="json-file",
                config={"max-size": f"{(2 * limits.max_output_bytes + 2**20) // 1024 + 1}k", "max-file": "2"},
            ),
        )
        all_labels = {SANDBOX_LABEL: "1", **self.extra_labels, **dict(labels)}
        name = f"jane-sbx-{uuid.uuid4().hex[:16]}"
        try:
            container = api.create_container(
                image,
                command=["timeout", "-s", "KILL", str(safety_s), *RUNNER],
                user=self.user,
                environment={"HOME": SANDBOX_TMP, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"},
                working_dir=SANDBOX_TMP,
                volumes=[WORKDIR],
                labels=all_labels,
                network_disabled=True,
                host_config=host_config,
                name=name,
                stdin_open=False,
                tty=False,
            )
        except ImageNotFound as exc:
            raise SandboxUnavailable(
                f"sandbox image {image!r} not found; build it: jane-handler-runtime build-image"
            ) from exc
        except (DockerException, RequestsConnectionError) as exc:
            raise SandboxUnavailable(f"cannot create sandbox container: {exc}") from exc
        cid = container["Id"]
        timed_out = False
        try:
            api.put_archive(cid, WORKDIR, bundle.tar())
            started = time.monotonic()
            api.start(cid)
            try:
                result = api.wait(cid, timeout=wall_s)
                exit_code: int | None = int(result.get("StatusCode", -1))
            except (ReadTimeout, RequestsConnectionError, APIError, TimeoutError):
                # Not finished within wall_time_ms (or the wait call itself timed out): force stop.
                timed_out = True
                exit_code = None
                with contextlib.suppress(NotFound, APIError):
                    api.kill(cid)
                try:
                    exit_code = int(api.wait(cid, timeout=self._api_timeout_s).get("StatusCode", -1))
                except (ReadTimeout, RequestsConnectionError, APIError):
                    exit_code = None
            duration_ms = int((time.monotonic() - started) * 1000)
            if not timed_out and duration_ms >= limits.wall_time_ms:
                timed_out = True  # the in-container safety timeout fired first
            stdout, out_trunc = _read_stream(
                api.logs(cid, stdout=True, stderr=False, stream=True, follow=False), limits.max_output_bytes
            )
            stderr, err_trunc = _read_stream(
                api.logs(cid, stdout=False, stderr=True, stream=True, follow=False), limits.max_output_bytes
            )
            state = api.inspect_container(cid).get("State", {})
            return SandboxOutcome(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms,
                timed_out=timed_out,
                oom_killed=bool(state.get("OOMKilled")),
                stdout_truncated=out_trunc,
                stderr_truncated=err_trunc,
                backend=self.name,
                details={"container": name, "image": image},
            )
        finally:
            try:
                api.remove_container(cid, v=True, force=True)
            except (NotFound, APIError) as exc:  # pragma: no cover - best effort
                log.warning(
                    "could not remove sandbox container", extra={"container": name, "error": str(exc)}
                )

    def kill(self, invocation_id: str) -> int:
        """Stop the sandbox of an invocation (job cancel), on this engine, by label."""
        filters = {"label": [f"{INVOCATION_LABEL}={invocation_id}"]}
        killed = 0
        for c in self.api.containers(filters=filters):
            with contextlib.suppress(NotFound, APIError):
                self.api.kill(c["Id"])
                killed += 1
        return killed

    def cleanup(self, label_selector: Mapping[str, str]) -> int:
        """Remove sandbox containers matching labels (stale ones after a crash; tests)."""
        filters = {"label": [f"{k}={v}" for k, v in label_selector.items()]}
        removed = 0
        for c in self.api.containers(all=True, filters=filters):
            try:
                self.api.remove_container(c["Id"], v=True, force=True)
                removed += 1
            except (NotFound, APIError):
                continue
        return removed
