"""Test helpers for the Web Collector API (this service's tests; usable by WP-03 and WP-13 too).

Only the standard library, httpx and the service itself: the testsite fixture lives in ``tests/conftest.py``.
Clients may be ``httpx.Client`` or FastAPI ``TestClient`` (a subclass of it).
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from .settings import Settings
from .urls import Normalizer

__all__ = [
    "FAST_LIMITS",
    "REPO_ROOT",
    "ServiceFactory",
    "ServiceProcess",
    "Site",
    "drain",
    "errors",
    "free_port",
    "make_settings",
    "start",
    "wait_done",
    "web_rules",
]

FAST_LIMITS: dict[str, Any] = {
    "rate": {"requests_per_second_per_host": 500, "min_delay_ms_per_host": 0},
    "concurrency": {"max_parallel_fetches": 4, "max_parallel_fetches_per_host": 4},
    "retries": {"max_attempts": 1, "initial_backoff_ms": 0, "max_backoff_ms": 0},
    "crawl": {"max_depth": 20},
}
"""Politeness limits for a local test site: fast, but still through the per-host limiter."""

REPO_ROOT = Path(__file__).resolve().parents[4]
"""Checkout root (``services/web-collector/src/jane_web_collector`` -> repository), for ``contracts/``."""


def make_settings(tmp: Path, **overrides: Any) -> Settings:
    """Settings for an in-process test app: state in ``tmp``, no WP-03 package unless given."""
    values: dict[str, Any] = {
        "state_dir": tmp / "state",
        "log_format": "console",
        "lease_seconds": 5,
        "heartbeat_interval_ms": 1000,
        "state_busy_timeout_ms": 2000,
        "discovery_path": tmp / "no-discovery-package",
    }
    values.update(overrides)
    return Settings(**values)


@dataclass
class Site:
    """A running test site: base URL plus a log of requested paths and User-Agents."""

    base: str
    requests: Counter[str] = field(default_factory=Counter)
    user_agents: set[str] = field(default_factory=set)
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def host(self) -> str:
        return self.base.split("://", 1)[1].split(":")[0]

    def url(self, path: str) -> str:
        return self.base + path

    def canonical(self, paths: set[str] | list[str]) -> set[str]:
        """Root-relative paths -> canonical URLs (same normalization as the default test rules)."""
        norm = Normalizer(strip_query_params=("utm_*",))
        return {n for p in paths if (n := norm.normalize(self.base + p))}

    def reset(self) -> None:
        with self.lock:
            self.requests.clear()


def web_rules(site: Site, **overrides: Any) -> dict[str, Any]:
    """Home page + recursion inside the site host, without the /calendar/ trap, without utm_* params."""
    rules: dict[str, Any] = {
        "collector": "web",
        "scope": {"allowed_domains": [site.host], "exclude": [{"type": "glob", "value": "*/calendar/**"}]},
        "strategies": [{"type": "seed_list", "urls": [site.url("/")]}, {"type": "recursive"}],
        "normalization": {"strip_query_params": ["utm_*"]},
    }
    rules.update(overrides)
    return rules


def start(client: httpx.Client, body: dict[str, Any], key: str | None = None) -> str:
    r = client.post("/v1/collections", json=body, headers={"Idempotency-Key": key or os.urandom(8).hex()})
    assert r.status_code == 202, r.text
    return str(r.json()["job_id"])


def wait_done(client: httpx.Client, cid: str, timeout: float = 60) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    body: dict[str, Any] = {}
    while time.monotonic() < deadline:
        body = client.get(f"/v1/collections/{cid}").json()
        if body["status"] in {"succeeded", "failed", "cancelled"}:
            return body
        time.sleep(0.05)
    raise AssertionError(f"collection {cid} did not finish: {body}")


def drain(client: httpx.Client, cid: str, *, limit: int = 50, timeout: float = 60) -> list[dict[str, Any]]:
    """Pull every material (acknowledging each page with ``after``) until ``end_of_stream``."""
    items: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        params: dict[str, Any] = {"limit": limit, "wait_ms": 500}
        if after:
            params["after"] = after
        page = client.get(f"/v1/collections/{cid}/materials", params=params).json()
        items.extend(page["items"])
        after = page["next_cursor"] or after
        if page["end_of_stream"]:
            return items
    raise AssertionError("materials stream did not end")


def errors(client: httpx.Client, cid: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = None
    while True:
        params: dict[str, Any] = {"limit": 200, **({"cursor": cursor} if cursor else {})}
        page = client.get(f"/v1/collections/{cid}/errors", params=params).json()
        out.extend(page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            return out


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


ServiceFactory = Callable[..., "ServiceProcess"]
"""Type of the ``service_factory`` fixture: ``factory(state_dir=None, **env) -> ServiceProcess``."""


@dataclass
class ServiceProcess:
    """The collector as a separate OS process (what a third-party application talks to)."""

    port: int
    state_dir: Path
    env: dict[str, str]
    proc: subprocess.Popen[bytes] | None = None
    log_path: Path | None = None

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def start(self, timeout: float = 30) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.state_dir.parent / f"service-{time.time_ns()}.log"
        with self.log_path.open("wb") as log:
            self.proc = subprocess.Popen(
                [sys.executable, "-m", "jane_web_collector"],
                env=self.env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise AssertionError(f"service exited: {self.log_path.read_text(errors='replace')}")
            try:
                if httpx.get(self.base + "/v1/health", timeout=1).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        raise AssertionError("service did not become healthy")

    def kill(self) -> None:
        """Hard kill (SIGKILL on Linux, TerminateProcess on Windows): no graceful shutdown at all."""
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait(timeout=10)

    def stop(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.kill()

    @staticmethod
    def environment(port: int, state_dir: Path, **overrides: str) -> dict[str, str]:
        return {
            **os.environ,
            "JANE_WEB_COLLECTOR_PORT": str(port),
            "JANE_WEB_COLLECTOR_STATE_DIR": str(state_dir),
            "JANE_WEB_COLLECTOR_LOG_FORMAT": "json",
            **overrides,
        }
