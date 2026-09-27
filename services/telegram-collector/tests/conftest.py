"""Fixtures: the real collector app (in process) and the collector as separate OS processes.

The Telegram side is a recording (``jane_telegram_collector.recorded``): the service's own backend that
replays channels from JSON files; tests post and edit messages by rewriting the file.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from jane_telegram_collector.app import build_app
from jane_telegram_collector.settings import Settings
from jane_telegram_collector.testing import (
    REPO_ROOT,
    Recording,
    ServiceFactory,
    ServiceProcess,
    free_port,
    make_channel,
    make_settings,
)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return make_settings(tmp_path)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(build_app(settings)) as c:
        yield c


@pytest.fixture
def channel(settings: Settings) -> Recording:
    assert settings.recordings_dir is not None
    return make_channel(settings.recordings_dir, 25)


@pytest.fixture(scope="session")
def material_validator() -> Draft202012Validator:
    schemas = REPO_ROOT / "contracts" / "schemas"
    resources = []
    for path in schemas.rglob("*.schema.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        resources.append((path.resolve().as_uri(), Resource.from_contents(doc)))
    registry: Registry[Any] = Registry().with_resources(resources)
    uri = (schemas / "material.schema.json").resolve().as_uri()
    return Draft202012Validator(
        {"$ref": uri}, registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER
    )


@pytest.fixture
def service_factory(tmp_path: Path) -> Iterator[ServiceFactory]:
    started: list[ServiceProcess] = []

    def factory(state_dir: Path | None = None, **env_overrides: str) -> ServiceProcess:
        state_dir = state_dir or tmp_path / "svc-state"
        port = free_port()
        env = ServiceProcess.environment(
            port,
            state_dir,
            tmp_path / "recordings",
            JANE_TELEGRAM_COLLECTOR_LEASE_SECONDS="3",
            JANE_TELEGRAM_COLLECTOR_HEARTBEAT_INTERVAL_MS="500",
            JANE_TELEGRAM_COLLECTOR_STATE_BUSY_TIMEOUT_MS="1000",
            **env_overrides,
        )
        svc = ServiceProcess(port=port, state_dir=state_dir, env=env)
        started.append(svc)
        return svc

    yield factory
    for svc in started:
        svc.resume()
        svc.stop()
