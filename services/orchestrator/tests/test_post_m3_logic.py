"""WP-17 pure logic (no PostgreSQL): input shapes of R05, rate-limited restarts (WP-04 -> WP-09), R06 time
window of objects read by id, R02 executors without managed connections."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

sys.path.insert(0, str(Path(__file__).parent))

from orch_support import CONTRACTS, catalog_task

from jane_orchestrator.engine import Engine, _stored_within
from jane_orchestrator.routing import route_result
from jane_orchestrator.settings import ExecutorConfig

assert CONTRACTS is not None
SCHEMAS = CONTRACTS / "schemas"
_REGISTRY: Registry = Registry().with_resources(
    (p.resolve().as_uri(), Resource.from_contents(json.loads(p.read_text(encoding="utf-8"))))
    for p in SCHEMAS.rglob("*.schema.json")
)
INVOCATION = (SCHEMAS / "handler-invocation.schema.json").resolve().as_uri()


def check(fragment: str, instance: Any) -> None:
    errors = [
        e.message
        for e in Draft202012Validator({"$ref": INVOCATION + fragment}, registry=_REGISTRY).iter_errors(
            instance
        )
    ]
    assert errors == [], errors


MATERIAL = json.loads(
    (CONTRACTS / "examples" / "schemas" / "material" / "web-product-page.json").read_text("utf-8")
)


def _task() -> dict[str, Any]:
    task = catalog_task()
    task["stages"] += [
        {
            "stage_id": "triage",
            "kind": "handler",
            "handler": {"package_id": "jane.llm-x", "version": "1.0.0"},
            "inputs": [{"from": "extract-products", "select": "problems"}],
        },
        {
            "stage_id": "after-raw",
            "kind": "handler",
            "handler": {"package_id": "jane.llm-y", "version": "1.0.0"},
            "inputs": [{"from": "store-raw"}],
        },
    ]
    return task


# ------------------------------------------------------------------ R05: documented input shapes
@pytest.mark.parametrize(
    "result",
    [
        {
            "invocation_id": "inv_2",
            "handler": {"package_id": "shop-example.product-extractor", "version": "1.2.0"},
            "status": "unrecognized",
            "unrecognized": {"partial": False, "signature": "missing-selector:.price"},
            "diagnostics": {"messages": [{"level": "warning", "message": "no .price"}]},
        },
        {
            "invocation_id": "inv_3",
            "handler": {"package_id": "shop-example.product-extractor", "version": "1.2.0"},
            "status": "failed",
            "failure": {"kind": "execution_error", "message": "boom", "retryable": False},
        },
        {"status": "failed", "failure": {"kind": "timeout", "message": "slow"}},  # no ids: fields are omitted
    ],
)
def test_select_problems_delivers_material_and_problem_data(result: dict[str, Any]) -> None:
    inputs = [{"kind": "material", "material": MATERIAL}]
    items = route_result(_task(), "shop-example", "extract-products", "itm_1", inputs, result)
    (item,) = [i for i in items if i.stage_id == "triage"]
    material_input, data_input = item.inputs
    check("#/$defs/HandlerInput", material_input)
    check("#/$defs/HandlerInput", data_input)
    check("#/$defs/ProblemData", data_input["data"])
    problem = data_input["data"]["problem"]
    assert problem["stage_id"] == "extract-products" and problem["status"] == result["status"]
    assert all(v is not None for v in problem.values())
    assert data_input.get("from_invocation_id") == result.get("invocation_id")


def test_storage_stage_output_is_writes_data() -> None:
    writes = [
        {
            "status": "written",
            "target": {"adapter": "filesystem", "connection_id": "raw-files"},
            "object": {"object_id": "obj_1", "adapter": "filesystem", "media_type": "text/html"},
            "delivery_key": "dk",
        }
    ]
    result = {"invocation_id": "inv_9", "status": "success", "output": {"writes": writes}}
    inputs = [{"kind": "material", "material": MATERIAL}]
    (item,) = route_result(_task(), "shop-example", "store-raw", "itm_9", inputs, result)
    (data_input,) = item.inputs
    check("#/$defs/HandlerInput", data_input)
    check("#/$defs/WritesData", data_input["data"])
    assert data_input == {"kind": "data", "data": {"writes": writes}, "from_invocation_id": "inv_9"}


# ------------------------------------------------------------------ WP-04 -> WP-09: rate-limited restart
def _rate_run(max_attempts: int, restarts: int = 0) -> dict[str, Any]:
    retries = {
        "max_attempts": max_attempts,
        "initial_backoff_ms": 100,
        "max_backoff_ms": 10_000,
        "backoff_multiplier": 2,
        "jitter": False,
    }
    return {
        "config": catalog_task(),
        "limits": {"stages": {"collect": {"retries": retries}}},
        "collection_restarts": restarts,
    }


def test_rate_limited_restart_waits_for_retry_after_wherever_the_collector_puts_it() -> None:
    engine = Engine.__new__(Engine)  # the method uses neither the database nor the executors
    top = {"code": "rate_limited", "retryable": True, "retry_after_seconds": 7}
    assert engine._rate_limit_restart(_rate_run(3), top) == 7_000
    in_details = {"code": "rate_limited", "retryable": True, "details": {"retry_after_seconds": 5}}
    assert engine._rate_limit_restart(_rate_run(3), in_details) == 5_000  # Telegram flood wait (WP-04)
    fractional = {"code": "rate_limited", "retryable": True, "retry_after_seconds": 1.2}
    assert engine._rate_limit_restart(_rate_run(3), fractional) == 1_200  # never rounded down
    no_hint = {"code": "rate_limited", "retryable": True}
    assert engine._rate_limit_restart(_rate_run(3, restarts=1), no_hint) == 200  # collect stage backoff
    short_hint = {**top, "retry_after_seconds": 0.05}
    assert engine._rate_limit_restart(_rate_run(3), short_hint) == 100  # backoff when it is longer
    assert engine._rate_limit_restart(_rate_run(3, restarts=2), top) is None  # attempts used up
    assert engine._rate_limit_restart(_rate_run(1), top) is None
    assert engine._rate_limit_restart(_rate_run(3), {**top, "retryable": False}) is None
    assert engine._rate_limit_restart(_rate_run(3), {**top, "code": "source_unavailable"}) is None


# ------------------------------------------------------------------ R06: since/until of objects read by id
def test_objects_read_by_id_keep_the_storage_time_window() -> None:
    at = "2026-09-27T10:00:06Z"
    assert _stored_within(at, None, None)
    assert _stored_within(at, "2026-09-27T10:00:06Z", None)  # since is inclusive
    assert not _stored_within(at, None, "2026-09-27T10:00:06Z")  # until is exclusive
    assert _stored_within("2026-09-27T12:00:06+02:00", "2026-09-27T10:00:00Z", "2026-09-27T10:01:00Z")
    assert not _stored_within(None, "2026-01-01T00:00:00Z", None)


# ------------------------------------------------------------------ R02: executors without managed connections
def test_only_executors_with_managed_connections_are_synced() -> None:
    def cfg(**kw: Any) -> ExecutorConfig:
        return ExecutorConfig.model_validate({"executor": "x", "base_url": "http://x", **kw})

    assert cfg(role="handler").syncs_connections
    assert not cfg(role="handler", capabilities={"connections": False}).syncs_connections
    assert cfg(role="handler", capabilities={"connections": False}, sync_connections=True).syncs_connections
    assert cfg(role="llm", capabilities={"connections": True}).syncs_connections
    assert not cfg(role="registry").syncs_connections
