"""Unit tests of the pure logic: DAG validation, conditions, bindings, routing, limits, schedules, keys."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from orch_support import catalog_task, price_task, source_doc

from jane_orchestrator.common import delivery_key, new_id, parse_etag, rfc3339
from jane_orchestrator.conditions import evaluate, glob_to_regex, stage_bindings_match, url_pattern_matches
from jane_orchestrator.dag import effective_forward_unknown, topo_order, validate_task
from jane_orchestrator.engine import backoff_ms
from jane_orchestrator.limits import LimitsLayer, merge_limits
from jane_orchestrator.routing import route_material, route_result
from jane_orchestrator.runs import canonical_key
from jane_orchestrator.schedule import CronError, next_fire, parse_cron
from jane_orchestrator.settings import ContractDefaults, Settings, resolve_service_limits


def material(url: str, section: str | None = None, media: str = "text/html") -> dict[str, Any]:
    return {
        "material_id": "web:1",
        "observation_id": "obs_1",
        "source": {"kind": "web", "source_id": "shop-example"},
        "locator": {"url": url, "canonical_url": url},
        "format": {"media_type": media, "content_kind": "page"},
        "discovery": {"section": section} if section else {},
    }


# ---------------------------------------------------------------- DAG
def test_valid_catalog_and_price_tasks() -> None:
    for task in (catalog_task(), price_task()):
        errors, _ = validate_task(task, source_doc(), set())
        assert errors == []
    order = topo_order(catalog_task())
    assert order is not None and order[0] == "collect"


def test_dag_errors() -> None:
    t = catalog_task()
    t["stages"].append({"stage_id": "collect2", "kind": "collect", "collector": {"collector": "web"}})
    errors, _ = validate_task(t, source_doc())
    assert any(e.code == "collect_stage_count" for e in errors)
    t = catalog_task()
    t["stages"][2]["inputs"].append({"from": "store-products"})
    errors, _ = validate_task(t, source_doc())
    assert [e.code for e in errors] == ["cycle"]
    t = catalog_task()
    t["stages"][1]["inputs"] = [{"from": "extract-products", "select": "unmatched_materials"}]
    errors, _ = validate_task(t, source_doc())
    assert errors[0].code == "invalid_select"
    errors, _ = validate_task(catalog_task(), None)
    assert errors[0].pointer == "/input/source_id"
    t = catalog_task()
    t["stages"][2]["bindings"] = [{"url_patterns": [{"type": "regex", "value": "("}]}]
    errors, _ = validate_task(t, source_doc())
    assert errors[0].code == "invalid_regex"


def test_unknown_flag_warning_and_inheritance() -> None:
    _, warnings = validate_task(catalog_task(), source_doc(), {"raw-files"})
    codes = {w.code for w in warnings}
    assert "unknown_flag_off" in codes and "unknown_connection" in codes
    assert effective_forward_unknown(catalog_task(), source_doc(forward_unknown=True)) is True
    assert (
        effective_forward_unknown(
            catalog_task(forward_unknown_to_llm=False), source_doc(forward_unknown=True)
        )
        is False
    )
    assert effective_forward_unknown(catalog_task(), {"source_id": "x"}) is False


# ---------------------------------------------------------------- conditions & bindings
@pytest.mark.parametrize(
    ("pattern", "url", "ok"),
    [
        ("shop.example.test/product/*", "https://shop.example.test/product/a-1", True),
        ("shop.example.test/product/*", "https://shop.example.test/product/a/b", False),
        ("shop.example.test/**", "https://shop.example.test/product/a/b", True),
        ("shop.example.test/p?", "https://shop.example.test/px", True),
    ],
)
def test_url_glob(pattern: str, url: str, ok: bool) -> None:
    assert url_pattern_matches({"value": pattern}, url) is ok
    assert glob_to_regex(pattern).pattern.startswith("^")


def test_regex_pattern_on_full_url() -> None:
    assert url_pattern_matches(
        {"type": "regex", "value": r"^https://shop\.example\.test/product/"},
        "https://shop.example.test/product/x",
    )


def test_bindings_and_or_semantics() -> None:
    m = material("https://shop.example.test/product/a-1", "products")
    assert stage_bindings_match(None, m, "shop-example")
    assert stage_bindings_match([{"sections": ["products"], "media_types": ["text/html"]}], m, "shop-example")
    assert not stage_bindings_match(
        [{"sections": ["products"], "media_types": ["application/json"]}], m, "shop-example"
    )
    assert stage_bindings_match(
        [{"sections": ["news"]}, {"url_patterns": [{"value": "shop.example.test/product/*"}]}],
        m,
        "shop-example",
    )
    assert not stage_bindings_match([{"source_ids": ["other"], "sections": ["products"]}], m, "shop-example")
    assert stage_bindings_match([{"content_kinds": ["page"]}], m, "shop-example")


def test_conditions() -> None:
    ctx = {
        "material": material("https://x.test/a"),
        "result": {"status": "success", "entities_count": 3},
        "entity": {"fields": {"price": 5}},
    }
    assert evaluate({"field": "material.format.media_type", "op": "eq", "value": "text/html"}, ctx)
    assert evaluate({"field": "result.status", "op": "in", "value": ["success", "unrecognized"]}, ctx)
    assert evaluate({"field": "result.entities_count", "op": "gte", "value": 3}, ctx)
    assert evaluate({"field": "result.failure.kind", "op": "not_exists"}, ctx)
    assert evaluate({"field": "result.failure.kind", "op": "ne", "value": "timeout"}, ctx)
    assert evaluate(
        {
            "all": [
                {"field": "entity.fields.price", "op": "lt", "value": 10},
                {"not": {"field": "result.status", "op": "eq", "value": "failed"}},
            ]
        },
        ctx,
    )
    assert evaluate(
        {"any": [{"field": "material.locator.url", "op": "matches_glob", "value": "https://x.test/*"}]}, ctx
    )
    assert evaluate({"field": "material.locator.url", "op": "matches_regex", "value": "x\\.test"}, ctx)
    assert not evaluate({"field": "material.nope", "op": "eq", "value": 1}, ctx)
    assert evaluate(None, ctx)


# ---------------------------------------------------------------- routing
def test_route_material_bindings_and_unknown() -> None:
    task = catalog_task()
    prod = material("https://shop.example.test/product/a-1", "products")
    r = route_material(task, "shop-example", prod, forward_unknown=False)
    assert sorted(i.stage_id for i in r.items) == ["extract-products", "store-raw"]
    assert not r.unknown.unknown and all(i.item_key == "obs_1" for i in r.items)
    gift = material("https://shop.example.test/gift-cards/1")
    r = route_material(task, "shop-example", gift, forward_unknown=False)
    assert [i.stage_id for i in r.items] == ["store-raw"]
    assert r.unknown.unknown and not r.unknown.forwarded
    r = route_material(task, "shop-example", gift, forward_unknown=True)
    assert sorted(i.stage_id for i in r.items) == ["store-raw", "unknown-pages"] and r.unknown.forwarded
    json_mat = material("https://shop.example.test/product/a-2", "products", media="application/json")
    r = route_material(task, "shop-example", json_mat, forward_unknown=False)
    assert [i.stage_id for i in r.items] == ["store-raw"]  # `when` on media type
    r = route_material(task, "shop-example", prod, forward_unknown=False, from_stage="extract-products")
    assert [i.stage_id for i in r.items] == ["extract-products"]


def test_route_result_output_problems_and_input_material() -> None:
    task = catalog_task()
    task["stages"].append(
        {
            "stage_id": "triage",
            "kind": "handler",
            "handler": {"package_id": "jane.llm-x", "version": "1.0.0"},
            "inputs": [{"from": "extract-products", "select": "problems"}],
        }
    )
    task["stages"].append(
        {
            "stage_id": "raw-ok",
            "kind": "handler",
            "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
            "inputs": [
                {
                    "from": "extract-products",
                    "select": "input_material",
                    "when": {"field": "result.status", "op": "eq", "value": "success"},
                }
            ],
        }
    )
    mat = material("https://shop.example.test/product/a-1", "products")
    inputs = [{"kind": "material", "material": mat}]
    entity = {
        "entity_type": "product",
        "key": {"scope": "s", "natural": {"sku": "A"}},
        "fields": {"sku": "A"},
        "observation": {"observation_id": "obs_1", "observed_at": "2026-01-01T00:00:00Z"},
    }
    ok = {"invocation_id": "inv_1", "status": "success", "output": {"entities": [entity]}}
    items = route_result(task, "shop-example", "extract-products", "itm_1", inputs, ok)
    by = {i.stage_id: i for i in items}
    assert set(by) == {"store-products", "raw-ok"}
    assert (
        by["store-products"].inputs[0]["kind"] == "entities"
        and by["store-products"].inputs[0]["material"] == mat
    )
    assert by["store-products"].inputs[0]["from_invocation_id"] == "inv_1"
    assert by["raw-ok"].inputs == [{"kind": "material", "material": mat}]
    bad = {
        "invocation_id": "inv_2",
        "status": "unrecognized",
        "unrecognized": {"partial": False, "signature": "s"},
    }
    items = route_result(task, "shop-example", "extract-products", "itm_2", inputs, bad)
    assert [i.stage_id for i in items] == ["triage"]
    assert items[0].inputs[1]["data"]["problem"]["unrecognized"]["signature"] == "s"
    empty = {"invocation_id": "inv_3", "status": "empty", "output": {"entities": []}}
    assert route_result(task, "shop-example", "extract-products", "itm_3", inputs, empty) == []


def test_route_result_entity_condition_filters_entities() -> None:
    task = price_task()
    task["stages"][2]["inputs"] = [
        {"from": "extract-price", "when": {"field": "entity.fields.price", "op": "gt", "value": 10}}
    ]

    def mk(p: int) -> dict[str, Any]:
        return {
            "entity_type": "price",
            "key": {"scope": "s", "natural": {"sku": str(p)}},
            "fields": {"price": p},
            "observation": {"observation_id": "o", "observed_at": "2026-01-01T00:00:00Z"},
        }

    result = {"invocation_id": "i", "status": "success", "output": {"entities": [mk(5), mk(20)]}}
    items = route_result(task, "shop-example", "extract-price", "itm", [], result)
    assert [e["fields"]["price"] for e in items[0].inputs[0]["entities"]] == [20]


# ---------------------------------------------------------------- limits
def test_merge_limits_levels_caps_and_provenance() -> None:
    fallback = ContractDefaults().model_dump(mode="json")
    eff = merge_limits(
        fallback,
        [
            LimitsLayer(
                "platform", {"rate": {"requests_per_second_per_host": 1}, "sandbox": {"memory_mb": 256}}
            ),
            LimitsLayer("source", {"rate": {"requests_per_second_per_host": 2}}),
            LimitsLayer(
                "task",
                {
                    "crawl": {"max_depth": 5},
                    "llm": {"budget": {"amount": 1, "currency": "USD", "period": "day"}},
                },
            ),
            LimitsLayer("stage", {"sandbox": {"memory_mb": 4096}, "crawl": {"max_depth": 3}}),
        ],
        {"sandbox": {"memory_mb": 2048}},
    )
    p = eff.provenance
    assert (
        eff.limits["rate"]["requests_per_second_per_host"] == 2
        and p["rate.requests_per_second_per_host"] == "source"
    )
    assert eff.limits["sandbox"]["memory_mb"] == 2048 and p["sandbox.memory_mb"] == "hard_cap"
    assert eff.limits["crawl"]["max_depth"] == 3 and p["crawl.max_depth"] == "stage"
    assert p["queue.max_queue_depth"] == "platform" and eff.get("queue.max_queue_depth") == 10_000
    assert eff.limits["llm"]["budget"]["period"] == "day" and p["llm.budget"] == "task"


def test_service_limits_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__ENGINE__LEASE_MS", "1234")
    monkeypatch.setenv("JANE_ORCHESTRATOR_LIMITS__CONTRACT__QUEUE__MAX_QUEUE_DEPTH", "7")
    resolved = resolve_service_limits(Settings())
    assert resolved.limits.engine.lease_ms == 1234
    assert resolved.limits.contract.queue.max_queue_depth == 7
    info = resolved.platform_limits()
    assert info["defaults"]["queue"]["max_queue_depth"] == 7


def test_backoff() -> None:
    policy = {"initial_backoff_ms": 100, "backoff_multiplier": 2, "max_backoff_ms": 300, "jitter": False}
    assert [backoff_ms(policy, a) for a in (1, 2, 3, 4)] == [100, 200, 300, 300]
    jit = backoff_ms({**policy, "jitter": True}, 1)
    assert 100 <= jit <= 150


# ---------------------------------------------------------------- schedules
T0 = datetime(2026, 9, 27, 10, 0, tzinfo=UTC)


def test_cron_next_with_timezone() -> None:
    nxt = next_fire({"type": "cron", "cron": "0 2 * * 0", "timezone": "Europe/Kyiv"}, T0, None)
    assert nxt == datetime(2026, 10, 3, 23, 0, tzinfo=UTC)  # Sun 04 Oct 02:00 EEST
    assert next_fire({"type": "cron", "cron": "*/15 * * * *"}, T0, None) == T0 + timedelta(minutes=15)
    assert next_fire({"type": "cron", "cron": "30 9 1 * mon"}, T0, None) == datetime(
        2026, 9, 28, 9, 30, tzinfo=UTC
    )
    with pytest.raises(CronError):
        parse_cron("61 * * * *")


def test_interval_once_manual_bounds() -> None:
    sched = {"type": "interval", "interval_seconds": 60}
    assert next_fire(sched, T0, None) == T0 + timedelta(seconds=60)
    assert next_fire(sched, T0, T0 - timedelta(seconds=30)) == T0 + timedelta(seconds=30)
    assert next_fire(sched, T0, T0 - timedelta(hours=1)) == T0  # missed ticks: once now
    at = "2026-09-28T00:00:00Z"
    assert next_fire({"type": "once", "at": at}, T0, None) == datetime(2026, 9, 28, tzinfo=UTC)
    assert next_fire({"type": "once", "at": at}, T0, T0) is None
    assert next_fire({"type": "manual"}, T0, None) is None
    assert next_fire({**sched, "enabled": False}, T0, None) is None
    assert next_fire({**sched, "end_at": "2026-09-27T10:00:30Z"}, T0, None) is None
    assert next_fire({**sched, "start_at": "2026-09-30T00:00:00Z"}, T0, None) == datetime(
        2026, 9, 30, tzinfo=UTC
    )


# ---------------------------------------------------------------- keys & ids
def test_delivery_key_is_deterministic() -> None:
    assert delivery_key("run_1", "s", "obs_1") == delivery_key("run_1", "s", "obs_1")
    assert delivery_key("run_1", "s", "obs_1") != delivery_key("run_2", "s", "obs_1")
    assert len(delivery_key("r", "s", "k")) == 64


def test_ids_etags_time_keys() -> None:
    a, b = new_id("run"), new_id("run")
    assert a != b and a.startswith("run_") and len(a) == 30
    assert parse_etag('"v7"') == 7 and parse_etag('W/"v3"') == 3 and parse_etag("junk") == -1
    assert rfc3339(T0) == "2026-09-27T10:00:00.000Z"
    assert (
        canonical_key({"key": {"scope": "shop", "natural": {"sku": "A-1", "b": 2}}})
        == 'shop|{"b":2,"sku":"A-1"}'
    )
