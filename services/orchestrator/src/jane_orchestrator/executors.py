"""Calls to the services the orchestrator combines (collector.v1, handler.v1, storage.v1, registry.v1).

Only their versioned APIs are used — never their databases (ТЗ §4). Retries are decided by the caller
(item-level retry policy with the same ``Idempotency-Key``), so this client does not retry by itself.
"""

from __future__ import annotations

import fnmatch
import logging
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from jane_kit.tracing import TRACEPARENT, child_traceparent
from jane_orchestrator.settings import ExecutorConfig

__all__ = ["ExecutorError", "Executors"]

log = logging.getLogger(__name__)

RETRYABLE_STATUSES = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


@dataclass
class ExecutorError(Exception):
    """A call did not happen or was rejected (HTTP error, connection error, timeout)."""

    executor: str
    status: int | None
    problem: dict[str, Any] | None
    message: str

    def __str__(self) -> str:
        return f"{self.executor}: {self.message}"

    @property
    def code(self) -> str:
        if self.problem and self.problem.get("code"):
            return str(self.problem["code"])
        if self.status is None:
            return "upstream_unavailable"
        return "upstream_unavailable" if self.status >= 500 else "upstream_conflict"

    @property
    def retryable(self) -> bool:
        if self.problem is not None and isinstance(self.problem.get("retryable"), bool):
            return bool(self.problem["retryable"])
        return self.status is None or self.status in RETRYABLE_STATUSES

    def as_problem(self) -> dict[str, Any]:
        status = self.status if self.status and self.status >= 400 else 502
        detail = self.message[:1000]
        if self.problem:
            out = {
                k: v for k, v in self.problem.items() if k in {"type", "title", "status", "code", "detail"}
            }
            out.setdefault("detail", detail)
            out["retryable"] = self.retryable
            out["details"] = {"executor": self.executor}
            return out
        return {
            "type": f"urn:jane:problem:{self.code}",
            "title": "Executor call failed",
            "status": status,
            "code": self.code,
            "retryable": self.retryable,
            "detail": detail,
            "details": {"executor": self.executor},
        }


class Executors:
    def __init__(
        self, configs: list[ExecutorConfig], *, connect_timeout_ms: int, request_timeout_ms: int
    ) -> None:
        self.configs = {c.executor: c for c in configs}
        self._clients: dict[str, httpx.Client] = {}
        self._lock = threading.Lock()
        self._kind_cache: dict[str, str] = {}
        self.connect_timeout_ms = connect_timeout_ms
        self.request_timeout_ms = request_timeout_ms

    def close(self) -> None:
        with self._lock:
            for c in self._clients.values():
                c.close()
            self._clients.clear()

    def _client(self, name: str) -> httpx.Client:
        with self._lock:
            client = self._clients.get(name)
            if client is None:
                cfg = self.configs[name]
                headers = {"Authorization": f"Bearer {cfg.token}"} if cfg.token else {}
                client = httpx.Client(base_url=cfg.base_url.rstrip("/"), headers=headers)
                self._clients[name] = client
            return client

    # ------------------------------------------------------------------ routing
    def by_role(self, role: str) -> list[ExecutorConfig]:
        return [c for c in self.configs.values() if c.role == role]

    def first(self, role: str) -> ExecutorConfig | None:
        found = self.by_role(role)
        return found[0] if found else None

    def collector(self, name: str) -> ExecutorConfig | None:
        candidates = self.by_role("collector")
        for c in candidates:
            if c.capabilities.get("collector") == name:
                return c
        untagged = [c for c in candidates if "collector" not in c.capabilities]
        return untagged[0] if len(untagged) == 1 else None

    def handler_for(self, package_id: str) -> ExecutorConfig | None:
        handlers = [c for c in self.configs.values() if c.role in {"handler", "llm"}]
        for c in handlers:
            if any(fnmatch.fnmatchcase(package_id, str(p)) for p in c.capabilities.get("packages") or []):
                return c
        kind = self._package_kind(package_id)
        if kind is not None:
            for c in handlers:
                if kind in (c.capabilities.get("handler_kinds") or []):
                    return c
        defaults = [c for c in handlers if c.capabilities.get("default")]
        if defaults:
            return defaults[0]
        return handlers[0] if len(handlers) == 1 else None

    def _package_kind(self, package_id: str) -> str | None:
        if package_id in self._kind_cache:
            return self._kind_cache[package_id]
        registry = self.first("registry")
        if registry is None:
            return None
        try:
            pkg = self.call(registry, "GET", f"/v1/packages/{package_id}").json()
        except ExecutorError:
            return None
        kind = pkg.get("kind")
        if isinstance(kind, str):
            self._kind_cache[package_id] = kind
            return kind
        return None

    # ------------------------------------------------------------------ calls
    def call(
        self,
        executor: ExecutorConfig,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
        timeout_ms: int | None = None,
        ok: tuple[int, ...] = (),
    ) -> httpx.Response:
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if trace_id:
            headers[TRACEPARENT] = child_traceparent(trace_id)
        timeout = httpx.Timeout(
            (timeout_ms or self.request_timeout_ms) / 1000, connect=self.connect_timeout_ms / 1000
        )
        try:
            response = self._client(executor.executor).request(
                method, path, json=json, params=params, headers=headers, timeout=timeout
            )
        except httpx.HTTPError as exc:
            raise ExecutorError(
                executor.executor, None, None, f"{method} {path}: {type(exc).__name__}: {exc}"
            ) from exc
        if response.status_code < 400 or response.status_code in ok:
            return response
        problem = None
        if "json" in response.headers.get("content-type", ""):
            try:
                body = response.json()
                problem = body if isinstance(body, dict) else None
            except ValueError:
                problem = None
        raise ExecutorError(
            executor.executor,
            response.status_code,
            problem,
            f"{method} {path}: HTTP {response.status_code}",
        )

    def health(self, executor: ExecutorConfig, timeout_ms: int) -> str:
        try:
            r = self._client(executor.executor).get("/v1/health", timeout=timeout_ms / 1000)
        except httpx.HTTPError:
            return "down"
        if r.status_code >= 500 and r.status_code != 503:
            return "down"
        try:
            status = r.json().get("status")
        except ValueError:
            return "unknown"
        return status if status in {"ok", "degraded", "down"} else "unknown"
