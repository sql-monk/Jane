"""Fixtures for the WP-03 strategies: the real testsite (WP-01) with a request log and the real collector core
(WP-02) with this package plugged in exactly as in production (``discovery_path`` / ``DISCOVERY_PATH``).

The testsite is the unmodified ``jane_testsite`` handler; the subclass only records requested paths and can hold
a request until the test releases it (:class:`.helpers.HoldingSite`).
"""

from __future__ import annotations

import os
import sys
import threading
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_testsite import expected  # type: ignore[import-untyped]
from jane_testsite.server import TestSiteHandler  # type: ignore[import-untyped]
from jane_web_collector.app import build_app
from jane_web_collector.discovery.registry import DISCOVERY_MODULE, load_discovery_package
from jane_web_collector.testing import (
    REPO_ROOT,
    ServiceFactory,
    ServiceProcess,
    free_port,
    make_settings,
)

from .helpers import HoldingSite

PACKAGE_DIR = Path(__file__).resolve().parents[1]
"""``services/web-collector/strategies/discovery`` — the package under test."""
START_S = float(os.environ.get("JANE_DISCOVERY_TEST_START_S", "120"))
"""How long a collector process may take to answer ``/v1/health`` (``ServiceProcess.start`` waits 30 s, which
a loaded machine exceeded for the Telegram collector's processes in a full ``just check``)."""


class _Process(ServiceProcess):
    def start(self, timeout: float = START_S) -> None:
        super().start(timeout)


def _recording_handler(site: HoldingSite) -> type[TestSiteHandler]:
    class Recording(TestSiteHandler):  # type: ignore[misc]
        def do_GET(self) -> None:
            with site.lock:
                site.requests[self.path] += 1
                site.user_agents.add(self.headers.get("User-Agent", ""))
            hold = site.take_hold(self.path)
            if hold is not None:
                # until the test releases it (the fixture releases every hold at teardown): a time bound here
                # could answer the held request before a slow test has killed the collector
                hold.released.wait()
            super().do_GET()

    return Recording


class _QuietServer(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        # a collector process killed by a test drops its connections: not a test failure
        if not isinstance(sys.exc_info()[1], ConnectionError):
            super().handle_error(request, client_address)  # type: ignore[arg-type]


@pytest.fixture
def site() -> Iterator[HoldingSite]:
    holder = HoldingSite(base="")
    server = _QuietServer(("127.0.0.1", 0), _recording_handler(holder))
    server.daemon_threads = True
    holder.base = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield holder
    finally:
        holder.release_all()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture(scope="session")
def expected_sets() -> dict[str, set[str]]:
    sets: dict[str, set[str]] = expected().sets
    return sets


def _load_package() -> ModuleType:
    current = sys.modules.get(DISCOVERY_MODULE)
    if (
        current is not None
        and Path(getattr(current, "__file__", "") or "").resolve() != PACKAGE_DIR / "__init__.py"
    ):
        # another test put a stand-in package under the same name (the core's own registry tests)
        for name in [n for n in sys.modules if n == DISCOVERY_MODULE or n.startswith(DISCOVERY_MODULE + ".")]:
            sys.modules.pop(name, None)
    module = load_discovery_package(PACKAGE_DIR)
    assert module is not None, PACKAGE_DIR
    return module


@pytest.fixture
def discovery() -> ModuleType:
    """The package as the core imports it (``jane_web_collector_discovery``)."""
    return _load_package()


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    _load_package()
    with TestClient(build_app(make_settings(tmp_path, discovery_path=PACKAGE_DIR))) as c:
        yield c


@pytest.fixture
def service_factory(tmp_path: Path) -> Iterator[ServiceFactory]:
    """The collector as a separate OS process with this package (``JANE_WEB_COLLECTOR_DISCOVERY_PATH``)."""
    started: list[ServiceProcess] = []

    def factory(state_dir: Path | None = None, **env_overrides: str) -> ServiceProcess:
        state_dir = state_dir or tmp_path / "svc-state"
        port = free_port()
        env: dict[str, Any] = ServiceProcess.environment(
            port,
            state_dir,
            JANE_WEB_COLLECTOR_LEASE_SECONDS="3",
            JANE_WEB_COLLECTOR_HEARTBEAT_INTERVAL_MS="500",
            JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS="1000",
            JANE_WEB_COLLECTOR_DISCOVERY_PATH=str(PACKAGE_DIR),
            JANE_CONTRACTS_DIR=str(REPO_ROOT / "contracts"),
            **env_overrides,
        )
        svc = _Process(port=port, state_dir=state_dir, env=env)
        started.append(svc)
        return svc

    yield factory
    for svc in started:
        svc.stop()
