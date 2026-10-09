"""R04: a state store held by another instance answers 503 ``service_unavailable`` with ``Retry-After``.

Several Web Collector instances may share one state file (one node, one ``STATE_DIR``). A write that cannot
take the SQLite lock within ``STATE_BUSY_TIMEOUT_MS`` is not an internal error but a retryable 503, as
``collector.v1`` documents; nothing is half-written, so the same request succeeds once the lock is free.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jane_kit.contracts import ContractClient, OpenAPISpec
from jane_web_collector.app import build_app
from jane_web_collector.testing import (
    FAST_LIMITS,
    REPO_ROOT,
    Site,
    make_settings,
    start,
    wait_done,
    web_rules,
)

SPEC = OpenAPISpec.load(REPO_ROOT / "contracts" / "openapi" / "collector.v1.yaml")


@pytest.fixture
def busy_client(tmp_path: Path) -> Iterator[TestClient]:
    """The app with a short lock wait, so a held SQLite lock turns into 503 quickly."""
    with TestClient(build_app(make_settings(tmp_path, state_busy_timeout_ms=200))) as client:
        yield client


def test_busy_state_store_answers_503_with_retry_after(
    busy_client: TestClient, site: Site, tmp_path: Path
) -> None:
    api = ContractClient(SPEC, busy_client)
    rules = web_rules(site, strategies=[{"type": "seed_list", "urls": [site.url("/"), site.url("/about")]}])
    cid = start(
        busy_client, {"source_kind": "web", "source_id": "busy", "rules": rules, "limits": FAST_LIMITS}
    )
    assert wait_done(busy_client, cid)["status"] == "succeeded"
    page = api.get(f"/v1/collections/{cid}/materials", params={"limit": 1}).json()
    # another instance holds the write lock of the shared state file (here: a plain SQLite connection)
    other = sqlite3.connect(tmp_path / "state" / "state.db", isolation_level=None)
    other.execute("BEGIN IMMEDIATE")
    try:
        ack = api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"]})
        assert ack.status_code == 503, ack.text
        assert ack.json()["code"] == "service_unavailable" and ack.json()["retryable"] is True
        assert int(ack.headers["Retry-After"]) >= 1
        reset = api.delete("/v1/states/busy")
        assert reset.status_code == 503 and reset.json()["code"] == "service_unavailable"
    finally:
        other.execute("ROLLBACK")
        other.close()
    assert (
        api.get(f"/v1/collections/{cid}/materials", params={"after": page["next_cursor"]}).status_code == 200
    )
    assert api.delete("/v1/states/busy").status_code == 204
