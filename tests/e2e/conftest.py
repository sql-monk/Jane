"""Jane end-to-end acceptance tests (WP-13). Scenarios: docs/acceptance/scenarios.md.

Not collected by ``just check`` (``tests/e2e`` is outside the root ``testpaths``). Run explicitly:

    uv run --all-packages pytest tests/e2e -m e2e -v

Environment:
    JANE_E2E_PROJECT       compose project (default ``jane-e2e-<checkout hash>``; unique per checkout)
    JANE_E2E_KEEP=1        keep the stack after the session (default: ``down -v`` - containers, volumes, images)
    JANE_E2E_WAIT_TIMEOUT  seconds to wait for health-checks (default 900)
    JANE_E2E_DOCKER_SOCKET / JANE_E2E_DOCKER_GID   docker API for handler-runtime sandboxes (auto-detected)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

# tests/e2e is not a workspace member; make the helper package importable (importlib import mode).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from jane_e2e.clients import JaneClient
from jane_e2e.stack import SERVICES, E2EStack

E2E_DIR = Path(__file__).resolve().parent


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: end-to-end acceptance scenario on the full stack (WP-13)")
    config.addinivalue_line(
        "markers", "criteria(*numbers): acceptance criteria of TZ §12 the scenario proves"
    )
    config.addinivalue_line("markers", "milestone(name): M1 / M2 / M3 (plan.md §6)")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if Path(str(item.path)).resolve().is_relative_to(E2E_DIR):
            item.add_marker(pytest.mark.e2e)


def _docker_ok() -> str | None:
    if shutil.which("docker") is None:
        return "docker не знайдено"
    r = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True, check=False)
    return None if r.returncode == 0 else "docker daemon недоступний"


@pytest.fixture(scope="session")
def stack() -> Iterator[E2EStack]:
    if reason := _docker_ok():
        pytest.skip(reason)
    s = E2EStack()
    try:
        yield s
    finally:
        if os.environ.get("JANE_E2E_KEEP") != "1":
            s.down(volumes=True)


@pytest.fixture
def require(stack: E2EStack) -> Callable[..., None]:
    """``require("storage", "handler-runtime")`` - skip with the WP reason if absent, otherwise start them."""

    def _require(*names: str) -> None:
        unknown = [n for n in names if n not in SERVICES]
        assert not unknown, f"unknown services {unknown}"
        if reasons := stack.missing(names):
            pytest.skip("; ".join(reasons))
        stack.ensure(*[n for n in names if SERVICES[n].kind != "feature"])

    return _require


@pytest.fixture
def client(stack: E2EStack) -> Iterator[Callable[..., JaneClient]]:
    """``client("storage")`` - contract-validating client of a running service (instance ``index``)."""
    opened: list[JaneClient] = []

    def _client(service: str, index: int = 1) -> JaneClient:
        c = JaneClient(stack.url(service, index))
        opened.append(c)
        return c

    yield _client
    for c in opened:
        c.close()


@pytest.fixture
def run_id() -> str:
    """Unique id of one scenario run: namespaces sources, observations and delivery keys on a reused stack."""
    return uuid.uuid4().hex[:12]
