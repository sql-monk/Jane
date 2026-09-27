"""Test helpers for the Telegram Collector API (this service's tests; usable by WP-13 too).

Only the standard library, httpx and the service itself. Clients may be ``httpx.Client`` or FastAPI
``TestClient`` (a subclass of it). Channels are recordings (:class:`~jane_telegram_collector.recorded.Recording`).
"""

from __future__ import annotations

import contextlib
import os
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from .recorded import Recording
from .settings import Settings

__all__ = [
    "CHANNEL_ID",
    "FAST_LIMITS",
    "REPO_ROOT",
    "T0",
    "USERNAME",
    "Recording",
    "ServiceFactory",
    "ServiceProcess",
    "drain",
    "errors",
    "free_port",
    "make_channel",
    "make_settings",
    "page",
    "start",
    "telegram_rules",
    "wait_done",
]

FAST_LIMITS: dict[str, Any] = {
    "rate": {"min_delay_ms_per_host": 0},
    "retries": {"max_attempts": 2, "initial_backoff_ms": 0, "max_backoff_ms": 0},
}
"""No pacing between calls to a recorded channel, one quick retry."""

REPO_ROOT = Path(__file__).resolve().parents[4]
"""Checkout root (``services/telegram-collector/src/jane_telegram_collector`` -> repository), for ``contracts/``."""


CHANNEL_ID = "-1001234567890"
USERNAME = "city_events_example"
T0 = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)


def make_channel(
    root: Path, count: int, *, username: str = USERNAME, channel_id: str = CHANNEL_ID
) -> Recording:
    """A recorded channel with ``count`` messages, one per minute from :data:`T0`."""
    rec = Recording.create(root, channel_id=channel_id, username=username, title="City events")
    for i in range(count):
        rec.post(f"Event {i + 1}: concert at 19:00", date=T0 + timedelta(minutes=i), views=10 * i, save=False)
    rec.save()
    return rec


def make_settings(tmp: Path, **overrides: Any) -> Settings:
    """Settings for an in-process test app: state and recordings in ``tmp``."""
    values: dict[str, Any] = {
        "state_dir": tmp / "state",
        "recordings_dir": tmp / "recordings",
        "log_format": "console",
        "lease_seconds": 5,
        "heartbeat_interval_ms": 500,
        "state_busy_timeout_ms": 2000,
        "contracts_dir": REPO_ROOT / "contracts",
    }
    values.update(overrides)
    return Settings(**values)


def telegram_rules(*channels: str, **overrides: Any) -> dict[str, Any]:
    """Rules for channels given as usernames or ``-100...`` ids."""
    specs = [{"channel_id": c} if c.lstrip("-").isdigit() else {"username": c} for c in channels]
    rules: dict[str, Any] = {"collector": "telegram", "channels": specs}
    rules.update(overrides)
    return rules


def start(client: httpx.Client, body: dict[str, Any], key: str | None = None) -> str:
    body = {**body, "limits": {**FAST_LIMITS, **(body.get("limits") or {})}}
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


def page(client: httpx.Client, cid: str, after: str | None = None, **params: Any) -> dict[str, Any]:
    query: dict[str, Any] = dict(params)
    if after:
        query["after"] = after
    r = client.get(f"/v1/collections/{cid}/materials", params=query)
    assert r.status_code == 200, r.text
    body: dict[str, Any] = r.json()
    return body


def drain(client: httpx.Client, cid: str, *, limit: int = 50, timeout: float = 60) -> list[dict[str, Any]]:
    """Pull every material (acknowledging each page with ``after``) until ``end_of_stream``."""
    items: list[dict[str, Any]] = []
    after: str | None = None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        body = page(client, cid, after, limit=limit, wait_ms=500)
        items.extend(body["items"])
        after = body["next_cursor"] or after
        if body["end_of_stream"]:
            if body["items"] and after:  # acknowledge the last page too
                page(client, cid, after, limit=1)
            return items
    raise AssertionError("materials stream did not end")


def errors(client: httpx.Client, cid: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = None
    while True:
        params: dict[str, Any] = {"limit": 200, **({"cursor": cursor} if cursor else {})}
        body = client.get(f"/v1/collections/{cid}/errors", params=params).json()
        out.extend(body["items"])
        cursor = body["next_cursor"]
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

    def client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base, timeout=30, trust_env=False)

    def start(self, timeout: float = 30) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.state_dir.parent / f"service-{self.port}-{time.time_ns()}.log"
        with self.log_path.open("wb") as log:
            self.proc = subprocess.Popen(
                [sys.executable, "-m", "jane_telegram_collector"],
                env=self.env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise AssertionError(f"service exited: {self.log_path.read_text(errors='replace')}")
            try:
                if httpx.get(self.base + "/v1/health", timeout=1, trust_env=False).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        raise AssertionError("service did not become healthy")

    def _tree(self) -> list[Any]:
        if self.proc is None:
            return []
        try:
            import psutil  # type: ignore[import-untyped]

            root = psutil.Process(self.proc.pid)
            return [root, *root.children(recursive=True)]
        except Exception:
            return []

    def suspend(self) -> None:
        """Freeze the process tree (a stalled owner: alive, but not renewing its lease)."""
        for p in self._tree():
            with contextlib.suppress(Exception):
                p.suspend()

    def resume(self) -> None:
        for p in self._tree():
            with contextlib.suppress(Exception):
                p.resume()

    def kill(self) -> None:
        """Hard kill of the whole process tree (on Windows a venv ``python.exe`` is a launcher with a child)."""
        if self.proc is None:
            return
        for p in reversed(self._tree()):
            with contextlib.suppress(Exception):
                p.kill()
        with contextlib.suppress(Exception):
            self.proc.kill()
        self.proc.wait(timeout=10)

    def stop(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.kill()

    def log(self) -> str:
        return self.log_path.read_text(encoding="utf-8", errors="replace") if self.log_path else ""

    @staticmethod
    def environment(port: int, state_dir: Path, recordings_dir: Path, **overrides: str) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("JANE_TELEGRAM_COLLECTOR_")}
        return {
            **env,
            "JANE_TELEGRAM_COLLECTOR_PORT": str(port),
            "JANE_TELEGRAM_COLLECTOR_STATE_DIR": str(state_dir),
            "JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR": str(recordings_dir),
            "JANE_TELEGRAM_COLLECTOR_LOG_FORMAT": "json",
            "JANE_CONTRACTS_DIR": str(REPO_ROOT / "contracts"),
            "PYTHONUNBUFFERED": "1",  # logs reach the file even if the process is killed
            **overrides,
        }
