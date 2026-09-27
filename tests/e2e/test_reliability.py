"""Reliability scenarios R-* (docs/acceptance/scenarios.md) on the services already merged into main.

R-02/R-04 (restart + redelivery), R-05 (late results) and R-06 (several instances) run now for storage and
handler-runtime; the orchestrator-driven variants (kill of a worker mid-chain, network partitions between
orchestrator and executors) are added when WP-09 is merged.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.materials import fetch_page, standin_web_material
from jane_e2e.stack import E2EStack
from jane_e2e.steps import extract, store

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M1")]


def _material(stack: E2EStack, run_id: str, path: str = "/product/phone-alpha") -> dict[str, Any]:
    page = fetch_page(stack.url("testsite") + path)
    return standin_web_material(page, source_id=f"e2e-{run_id}", observation_id=f"obs_e2e_{run_id}")


@pytest.mark.criteria(8)
def test_r_02_redelivery_after_restart_of_storage_and_runtime(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """R-02/R-04: a result delivered before a crash (docker kill) is a duplicate after the restart."""
    require("testsite", "storage", "handler-runtime")
    material = _material(stack, run_id)
    extract_body, extracted = extract(client("handler-runtime"), material, run_id)
    assert extracted["status"] == "success", extracted
    inputs = [{"kind": "entities", "entities": extracted["output"]["entities"]}]
    store_body, stored = store(
        client("storage"),
        package_id="jane.storage-postgresql",
        connection="results-pg",
        inputs=inputs,
        run_id=run_id,
        stage_id="store-products",
        key_part=extracted["invocation_id"],
    )
    assert stored["output"]["writes"][0]["status"] == "written"

    for service in ("storage", "handler-runtime"):
        stack.kill(service)
        stack.restart(service)

    _, extracted_again = client("handler-runtime").invoke(extract_body)
    assert extracted_again["duplicate"] is True
    assert extracted_again["invocation_id"] == extracted["invocation_id"]
    _, stored_again = client("storage").invoke(store_body)
    assert stored_again["duplicate"] is True
    assert stored_again["output"]["writes"][0]["status"] == "duplicate"


@pytest.mark.criteria(8)
def test_r_05_late_result_does_not_replace_newer_one(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """R-05 (TZ §11): an older observation delivered after a newer one lands in history, not in the state."""
    require("testsite", "storage", "handler-runtime")
    storage = client("storage")
    material = _material(stack, run_id)
    _, extracted = extract(client("handler-runtime"), material, run_id)
    (base,) = extracted["output"]["entities"]
    t0 = datetime.now(UTC).replace(microsecond=0)

    def observation(minutes: int, price: float) -> dict[str, Any]:
        e: dict[str, Any] = copy.deepcopy(base)
        e["fields"]["price"] = {"amount": price, "currency": "UAH"}
        e["observation"]["observation_id"] = f"obs_e2e_{run_id}_{minutes}"
        e["observation"]["observed_at"] = (t0 + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return e

    newer, older = observation(20, 199.0), observation(10, 249.0)
    acks = []
    for entity in (newer, older):
        _, result = store(
            storage,
            package_id="jane.storage-postgresql",
            connection="results-pg",
            inputs=[{"kind": "entities", "entities": [entity]}],
            run_id=run_id,
            stage_id="store-price",
            key_part=entity["observation"]["observation_id"],
        )
        assert result["status"] == "success", result
        acks.append(result["output"]["writes"][0])
    assert acks[0]["status"] == "written"
    assert acks[1]["status"] in {"stale", "partially_stale"}, acks[1]
    assert "price" in acks[1]["stale_fields"]

    r = storage.api("storage").get(
        "/v1/entities",
        params={"connection_id": "results-pg", "entity_type": "product", "scope": f"e2e-{run_id}"},
    )
    (state,) = r.json()["items"]
    assert state["fields"]["price"] == {"amount": 199.0, "currency": "UAH"}
    history = storage.api("storage").get(
        "/v1/entity-history",
        params={"connection_id": "results-pg", "entity_type": "product", "key": state["canonical_key"]},
    )
    assert len(history.json()["items"]) == 2  # the late one is kept in history


@pytest.mark.criteria(8)
def test_r_06_two_runtime_instances_share_idempotency(
    stack: E2EStack, require: Callable[..., None], client: Callable[..., JaneClient], run_id: str
) -> None:
    """R-06: with two handler-runtime instances a redelivery to the other instance is a duplicate."""
    require("testsite", "handler-runtime")
    stack.scale("handler-runtime", 2)
    try:
        material = _material(stack, run_id)
        body, first = extract(client("handler-runtime", 1), material, run_id)
        assert first["status"] == "success"
        _, second = client("handler-runtime", 2).invoke(body)
        assert second["duplicate"] is True
        assert second["invocation_id"] == first["invocation_id"]
        job_view = (
            client("handler-runtime", 2).api("handler").get(f"/v1/invocations/{first['invocation_id']}")
        )
        assert job_view.status_code == 200
    finally:
        stack.scale("handler-runtime", 1)
