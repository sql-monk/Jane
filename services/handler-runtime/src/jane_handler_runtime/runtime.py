"""Wiring shared by the HTTP service and the CLI."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from jane_kit.config import ResolvedLimits

from .docker_sandbox import DockerSandbox
from .executor import Executor
from .packages import ContentFetcher, PackageStore
from .sandbox import SandboxBackend, SubprocessSandbox
from .schemas import ContractSchemas, find_contracts_dir
from .settings import ServiceLimits, Settings, resolve_service_limits

__all__ = ["Runtime", "build_backend", "build_runtime"]


@dataclass
class Runtime:
    settings: Settings
    limits: ResolvedLimits[ServiceLimits]
    backend: SandboxBackend
    store: PackageStore
    executor: Executor
    schemas: ContractSchemas

    def close(self) -> None:
        self.store.close()


def build_backend(settings: Settings, limits: ServiceLimits) -> SandboxBackend:
    if settings.sandbox_backend == "subprocess":
        return SubprocessSandbox(settings.allow_unsafe_subprocess, limits.packages.kill_grace_ms)
    return DockerSandbox(
        base_url=settings.docker_host,
        runtime=settings.docker_runtime,
        user=settings.sandbox_user,
        api_timeout_s=limits.packages.docker_api_timeout_ms / 1000,
        kill_grace_ms=limits.packages.kill_grace_ms,
        extra_labels=settings.sandbox_labels,
    )


def build_runtime(
    settings: Settings,
    *,
    backend: SandboxBackend | None = None,
    registry_transport: httpx.AsyncBaseTransport | None = None,
    download_transport: httpx.AsyncBaseTransport | None = None,
) -> Runtime:
    resolved = resolve_service_limits(settings)
    limits = resolved.limits
    timeout_s = limits.timeouts.request_timeout_ms / 1000
    schemas = ContractSchemas(find_contracts_dir(settings.contracts_dir))
    fetcher = ContentFetcher(settings, timeout_s, transport=download_transport)
    store = PackageStore(
        settings, limits.packages, fetcher, registry_transport=registry_transport, request_timeout_s=timeout_s
    )
    backend = backend or build_backend(settings, limits)
    executor = Executor(settings, store, fetcher, backend, schemas)
    return Runtime(settings, resolved, backend, store, executor, schemas)
