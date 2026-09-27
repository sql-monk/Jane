"""Fixtures: the real testsite (WP-01) with a request log, the real collector app and service process.

The testsite is the unmodified ``jane_testsite`` handler; the subclass only records which paths were
requested (to prove "no cycles", "robots obeyed", "no requests outside the bounds").
"""

from __future__ import annotations

import sys
import threading
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_testsite import expected  # type: ignore[import-untyped]
from jane_testsite.server import TestSiteHandler  # type: ignore[import-untyped]
from jane_web_collector.app import build_app
from jane_web_collector.settings import Settings
from jane_web_collector.testing import (
    REPO_ROOT,
    ServiceFactory,
    ServiceProcess,
    Site,
    free_port,
    make_settings,
)


def _recording_handler(site: Site) -> type[TestSiteHandler]:
    class Recording(TestSiteHandler):  # type: ignore[misc]
        def do_GET(self) -> None:
            with site.lock:
                site.requests[self.path] += 1
                site.user_agents.add(self.headers.get("User-Agent", ""))
            super().do_GET()

    return Recording


class _QuietServer(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        # a collector process killed by a test drops its connections: not a test failure
        if not isinstance(sys.exc_info()[1], ConnectionError):
            super().handle_error(request, client_address)  # type: ignore[arg-type]


@pytest.fixture
def site() -> Iterator[Site]:
    holder = Site(base="")
    server = _QuietServer(("127.0.0.1", 0), _recording_handler(holder))
    server.daemon_threads = True
    holder.base = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield holder
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture(scope="session")
def expected_sets() -> dict[str, set[str]]:
    sets: dict[str, set[str]] = expected().sets
    return sets


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return make_settings(tmp_path)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(settings)) as c:
        yield c


@pytest.fixture
def service_factory(tmp_path: Path) -> Iterator[ServiceFactory]:
    started: list[ServiceProcess] = []

    def factory(state_dir: Path | None = None, **env_overrides: str) -> ServiceProcess:
        state_dir = state_dir or tmp_path / "svc-state"
        port = free_port()
        env = ServiceProcess.environment(
            port,
            state_dir,
            JANE_WEB_COLLECTOR_LEASE_SECONDS="3",
            JANE_WEB_COLLECTOR_DISCOVERY_PATH=str(tmp_path / "no-discovery-package"),
            JANE_CONTRACTS_DIR=str(REPO_ROOT / "contracts"),
            **env_overrides,
        )
        svc = ServiceProcess(port=port, state_dir=state_dir, env=env)
        started.append(svc)
        return svc

    yield factory
    for svc in started:
        svc.stop()
