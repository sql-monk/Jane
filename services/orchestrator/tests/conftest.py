from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent))

from orch_support import CONTRACTS, Neighbours, admin_dsn, create_database, start_neighbours

from jane_orchestrator.app import build_app
from jane_orchestrator.settings import ExecutorConfig, Settings

FAST_ENGINE = {
    "POLL_INTERVAL_MS": "20",
    "FEED_WAIT_MS": "20",
    "LEASE_MS": "3000",
    "HEARTBEAT_MS": "300",
    "SCHEDULER_INTERVAL_MS": "100",
    "BACKPRESSURE_RECHECK_MS": "30",
    "SYNC_RETRY_MS": "100",
    "JOB_POLL_INTERVAL_MS": "20",
}


@pytest.fixture(scope="session")
def pg_admin() -> Iterator[str]:
    found = admin_dsn()
    if found is None:
        pytest.skip(
            "no PostgreSQL: set JANE_ORCHESTRATOR_TEST_DSN, run `just up postgres`, or install Docker"
        )
    dsn, stop = found
    try:
        yield dsn
    finally:
        stop()


@pytest.fixture
def db_dsn(pg_admin: str) -> Iterator[str]:
    dsn, drop = create_database(pg_admin)
    try:
        yield dsn
    finally:
        drop()


@pytest.fixture
def fast_engine(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    env = {f"JANE_ORCHESTRATOR_LIMITS__ENGINE__{k}": v for k, v in FAST_ENGINE.items()}
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return env


@pytest.fixture
def neighbours() -> Iterator[Neighbours]:
    n = start_neighbours()
    try:
        yield n
    finally:
        n.stop()


AppFactory = Callable[..., TestClient]


@pytest.fixture
def make_client(db_dsn: str, neighbours: Neighbours, fast_engine: dict[str, str]) -> Iterator[AppFactory]:
    clients: list[TestClient] = []

    def factory(**overrides: Any) -> TestClient:
        settings = Settings(
            database_url=db_dsn,
            executors=[ExecutorConfig.model_validate(e) for e in neighbours.executors()],
            contracts_dir=CONTRACTS,
            log_format="console",
            log_level="WARNING",
            **overrides,
        )
        client = TestClient(build_app(settings))
        client.__enter__()
        clients.append(client)
        return client

    yield factory
    for c in reversed(clients):
        c.__exit__(None, None, None)
