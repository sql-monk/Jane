"""Unit tests of the executor HTTP client: pooled keep-alive expiry and re-sending on a dropped connection.

The executor is a real HTTP/1.1 server on a loopback port (``http.server``), not a mock of the client: the
tests observe which TCP connections and requests actually reached it.
"""

from __future__ import annotations

import inspect
import json
import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
import uvicorn

from jane_orchestrator.executors import ExecutorError, Executors
from jane_orchestrator.settings import ExecutorConfig, ServiceLimits, Settings, resolve_service_limits


class FakeExecutor:
    """Keeps connections open (HTTP/1.1 keep-alive) and can drop one without a response, as a server does
    when it closes an idle keep-alive connection at the moment the client reuses it."""

    def __init__(self) -> None:
        self.connections = 0
        self.requests: list[tuple[str, str, str | None]] = []
        self.drop_next: set[tuple[str, str]] = set()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def setup(self) -> None:
                super().setup()
                with lock:
                    owner.connections += 1

            def log_message(self, format: str, *args: Any) -> None:
                return

            def _serve(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                with lock:
                    owner.requests.append((self.command, self.path, self.headers.get("Idempotency-Key")))
                    drop = (self.command, self.path) in owner.drop_next
                    owner.drop_next.discard((self.command, self.path))
                if drop:
                    self.close_connection = True  # no status line: "Server disconnected without a response"
                    return
                body = json.dumps({"ok": True}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            do_GET = _serve  # noqa: N815 - http.server naming
            do_POST = _serve  # noqa: N815
            do_PUT = _serve  # noqa: N815

        lock = threading.Lock()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.server.block_on_close = False
        self.thread = threading.Thread(target=self.server.serve_forever, args=(0.05,), daemon=True)

    @property
    def url(self) -> str:
        host, port = self.server.server_address[:2]
        return f"http://{host!s}:{port}"

    def __enter__(self) -> FakeExecutor:
        self.thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def executor() -> Iterator[FakeExecutor]:
    with FakeExecutor() as ex:
        yield ex


def make(ex: FakeExecutor, **kwargs: Any) -> tuple[Executors, ExecutorConfig]:
    cfg = ExecutorConfig(executor="handler", role="handler", base_url=ex.url)
    return Executors([cfg], connect_timeout_ms=2_000, request_timeout_ms=5_000, **kwargs), cfg


def test_default_keepalive_expiry_is_below_the_service_server_keepalive() -> None:
    limits = ServiceLimits()
    # Every Jane service runs uvicorn with its default timeout_keep_alive (jane_kit.service.run passes none).
    server_keepalive_s = inspect.signature(uvicorn.Config).parameters["timeout_keep_alive"].default
    assert limits.engine.executor_keepalive_expiry_ms == 4_000
    assert limits.engine.executor_keepalive_expiry_ms / 1000 < server_keepalive_s
    assert limits.engine.executor_stale_connection_retries == 1


def test_keepalive_settings_come_from_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__EXECUTOR_KEEPALIVE_EXPIRY_MS", "1500")
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__EXECUTOR_STALE_CONNECTION_RETRIES", "0")
    engine = resolve_service_limits(Settings()).limits.engine
    assert engine.executor_keepalive_expiry_ms == 1500
    assert engine.executor_stale_connection_retries == 0


@pytest.mark.parametrize(("expiry_ms", "connections"), [(150, 2), (10_000, 1)])
def test_idle_pooled_connection_is_dropped_after_keepalive_expiry(
    executor: FakeExecutor, expiry_ms: int, connections: int
) -> None:
    executors, cfg = make(executor, keepalive_expiry_ms=expiry_ms)
    try:
        executors.call(cfg, "GET", "/v1/health")
        time.sleep(0.5)  # idle longer than 150 ms, shorter than 10 s
        executors.call(cfg, "GET", "/v1/health")
    finally:
        executors.close()
    assert executor.connections == connections


def test_dropped_connection_is_resent_for_idempotent_and_keyed_requests(executor: FakeExecutor) -> None:
    executors, cfg = make(executor)
    executor.drop_next = {
        ("GET", "/v1/packages/p"),
        ("POST", "/v1/invocations"),
        ("PUT", "/v1/connections/c"),
    }
    try:
        assert executors.call(cfg, "GET", "/v1/packages/p").json() == {"ok": True}
        r = executors.call(cfg, "POST", "/v1/invocations", json={"x": 1}, idempotency_key="dk-1")
        assert r.status_code == 200
        assert executors.call(cfg, "PUT", "/v1/connections/c", json={}).status_code == 200
    finally:
        executors.close()
    assert executor.requests == [
        ("GET", "/v1/packages/p", None),
        ("GET", "/v1/packages/p", None),
        # the same delivery key: the executor replays instead of repeating the effect
        ("POST", "/v1/invocations", "dk-1"),
        ("POST", "/v1/invocations", "dk-1"),
        ("PUT", "/v1/connections/c", None),
        ("PUT", "/v1/connections/c", None),
    ]


def test_dropped_connection_is_not_resent_without_idempotency(executor: FakeExecutor) -> None:
    executors, cfg = make(executor)
    executor.drop_next = {("POST", "/v1/jobs/j/cancel")}
    try:
        with pytest.raises(ExecutorError) as err:
            executors.call(cfg, "POST", "/v1/jobs/j/cancel", json={})
    finally:
        executors.close()
    assert err.value.status is None and err.value.retryable
    assert executor.requests == [("POST", "/v1/jobs/j/cancel", None)]


def test_resend_can_be_disabled(executor: FakeExecutor) -> None:
    executors, cfg = make(executor, stale_connection_retries=0)
    executor.drop_next = {("GET", "/v1/packages/p")}
    try:
        with pytest.raises(ExecutorError) as err:
            executors.call(cfg, "GET", "/v1/packages/p")
    finally:
        executors.close()
    assert err.value.status is None and err.value.code == "upstream_unavailable"
    assert executor.requests == [("GET", "/v1/packages/p", None)]
