"""Fetch current shop prices and verify a partial update through the running Jane APIs.

    uv run --all-packages python examples/sites/verify_prices.py --project jane-demo

Select an existing priced product with attributes, fetch a new material, invoke the published catalog
extractor, then send only its observed price fields to the published PostgreSQL storage handler. The
projection retains the extractor's key, observation and provenance; it never clears omitted metadata.
No source/task configuration or primary collector state is modified. VARUS uses a separate bounded
API-feed state because its product data is provided by the public GraphQL endpoint.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import jane_examples as ex  # noqa: E402 - shared, contract-validating example client

SHOPS = ("bi", "epicentrk", "prostor", "varus", "yakaboo")
PRICE_FIELDS = {"shop", "product_id", "price", "currency", "availability", "old_price"}
TERMINAL = {"succeeded", "failed", "cancelled"}


def amount_valid(value: Any) -> bool:
    return (
        isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value) and value > 0
    )


def identity(record: dict[str, Any]) -> str:
    return json.dumps(record["key"], sort_keys=True, separators=(",", ":"))


def invoke(api: ex.Api, body: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    delivery_key = ex.key()
    body = {**body, "delivery": {"delivery_key": delivery_key}, "mode": "sync"}
    response = api.call(
        "POST", "/v1/invocations", ok=(200, 202), json=body, headers={"Idempotency-Key": delivery_key}
    )
    result = cast(dict[str, Any], response.json())
    if response.status_code == 202:
        deadline = time.monotonic() + timeout_s
        job_id = result["job_id"]
        while result["status"] not in TERMINAL:
            if time.monotonic() > deadline:
                raise TimeoutError(f"handler job {job_id} exceeded the verification timeout")
            time.sleep(0.5)
            result = cast(dict[str, Any], api.call("GET", f"/v1/jobs/{job_id}").json())
        if result["status"] != "succeeded" or not isinstance(result.get("result"), dict):
            raise RuntimeError(f"handler job {job_id}: {result['status']}; no inline result")
        result = cast(dict[str, Any], result["result"])
    if result["status"] != "success":
        failure = result.get("failure") or result.get("unrecognized") or {}
        raise RuntimeError(f"{body['handler']['package_id']}: {result['status']}: {failure}")
    return result


def current(storage: ex.Api, connection: str, key: str) -> dict[str, Any]:
    page = storage.call(
        "GET", "/v1/entities", params={"connection_id": connection, "entity_type": "product", "key": key}
    ).json()
    if len(page["items"]) != 1:
        raise RuntimeError(f"existing product disappeared: {key}")
    return cast(dict[str, Any], page["items"][0])


def history(storage: ex.Api, connection: str, key: str) -> list[dict[str, Any]]:
    return storage.pages(
        "/v1/entity-history", {"connection_id": connection, "entity_type": "product", "key": key}
    )


def candidates(storage: ex.Api, source_id: str, connection: str, limit: int) -> list[dict[str, Any]]:
    page = storage.call(
        "GET",
        "/v1/entities",
        params={"connection_id": connection, "entity_type": "product", "scope": source_id, "limit": limit},
    ).json()
    records = [
        record
        for record in page["items"]
        if amount_valid(record["fields"].get("price")) and record["fields"].get("attributes")
    ]
    # Prefer an old discount so an ended discount can be checked when the source actually confirms it.
    return sorted(records, key=lambda record: not bool(record["fields"].get("old_price")))


def varus_materials(
    collector: ex.Api,
    source_id: str,
    category_id: str,
    task: dict[str, Any],
    timeout_s: float,
    page_size: int,
    product_id: str | None = None,
) -> list[dict[str, Any]]:
    rules = copy.deepcopy(ex.read_json(HERE / "packages/catalog.varus-catalog-rules/rules.json"))
    strategy = rules["strategies"][0]
    strategy.pop("partitions", None)
    strategy["body"]["variables"].update(id=category_id, page=1, pageSize=page_size)
    if product_id is not None:
        # Reuse the reviewed field selection, including every attribute union variant.
        query = strategy["body"]["query"]
        start = query.index("{", query.index("items"))
        depth = 0
        end = start
        for end in range(start, len(query)):
            depth += (query[end] == "{") - (query[end] == "}")
            if depth == 0:
                break
        fields = query[start : end + 1]
        strategy["body"] = {
            "operationName": "VarusPriceVerification",
            "query": "query VarusPriceVerification($id: ID!) { product(id: $id, shopId: null, "
            'regionId: 0, locale: "ua", deliveryMethod: null) ' + fields + " }",
            "variables": {"id": product_id},
        }
        strategy["items_path"] = "$.data.product"
        strategy.pop("pagination", None)
    limits = copy.deepcopy(task.get("limits") or {})
    limits.setdefault("crawl", {})["max_pages_per_run"] = 1
    limits.setdefault("queue", {})["max_inflight_materials"] = page_size
    job = collector.call(
        "POST",
        "/v1/collections",
        ok=(202,),
        json={
            "source_kind": "web",
            "source_id": source_id,
            "rules": rules,
            "state_key": f"verify-prices-varus-{ex.key()}",
            "mode": "full",
            "content_delivery": "auto",
            "limits": limits,
        },
        headers={"Idempotency-Key": ex.key()},
    ).json()
    collection_id = job["job_id"]
    deadline = time.monotonic() + timeout_s
    after = None
    materials: list[dict[str, Any]] = []
    while True:
        params = {"limit": page_size, **({"after": after} if after else {})}
        page = collector.call("GET", f"/v1/collections/{collection_id}/materials", params=params).json()
        materials.extend(page["items"])
        after = page.get("next_cursor") or after
        if page["end_of_stream"]:
            if after:
                collector.call("GET", f"/v1/collections/{collection_id}/materials", params={"after": after})
            if page["collection_status"] != "succeeded":
                raise RuntimeError(f"VARUS verification collection {page['collection_status']}")
            return materials
        if time.monotonic() > deadline:
            collector.call(
                "POST",
                f"/v1/jobs/{collection_id}/cancel",
                ok=(200, 202),
                json={},
                headers={"Idempotency-Key": ex.key()},
            )
            raise TimeoutError("VARUS verification collection exceeded the verification timeout")
        time.sleep(0.5)


def verify_one(
    svc: ex.Services, collector: ex.Api, runtime: ex.Api, writer: ex.Api, name: str, ns: argparse.Namespace
) -> dict[str, Any]:
    config = ex.read_json(HERE / "sites" / f"{name}.json")
    catalog = next(task for task in config["tasks"] if task.get("labels", {}).get("kind") == "catalog")
    task = svc.orchestrator.call("GET", f"/v1/tasks/{catalog['task_id']}").json()
    source_id = task["input"]["source_id"]
    source = svc.orchestrator.call("GET", f"/v1/sources/{source_id}").json()
    extract_stage = next(
        stage for stage in task["stages"] if stage.get("stage_id", "").startswith("extract-")
    )
    store_stage = next(
        stage
        for stage in task["stages"]
        if stage.get("stage_id", "").startswith("store-")
        and stage.get("handler", {}).get("package_id") == "jane.storage-postgresql"
    )
    connection = store_stage["connections"]["target"]
    records = candidates(svc.storage, source_id, connection, ns.candidate_limit)
    if not records:
        raise RuntimeError(
            f"{source_id}: no existing priced product with attributes in the bounded candidate page"
        )
    by_identity = {identity(record): record for record in records}
    material_and_result = None
    selected = None
    attempts: list[str] = []

    def extract(material: dict[str, Any]) -> dict[str, Any]:
        return invoke(
            runtime,
            {
                "handler": extract_stage["handler"],
                "params": extract_stage.get("params", {}),
                "inputs": [{"kind": "material", "material": material}],
            },
            ns.timeout_s,
        )

    if name == "varus":
        known_urls = {record["fields"].get("url") for record in records}
        lookups = [("2", None), ("53041", None)] + [
            ("2", str(record["fields"]["product_id"])) for record in records[: ns.max_candidates]
        ]
        for category_id, product_id in lookups:
            materials = varus_materials(
                collector, source_id, category_id, task, ns.timeout_s, ns.varus_page_size, product_id
            )
            for material in materials:
                locator = material.get("locator", {})
                if product_id is None and not {locator.get("url"), locator.get("final_url")} & known_urls:
                    continue
                result = extract(material)
                for entity in result.get("output", {}).get("entities", []):
                    if identity(entity) in by_identity and amount_valid(entity["fields"].get("price")):
                        selected = by_identity[identity(entity)]
                        material_and_result = (material, result, entity)
                        break
                if selected:
                    break
            if selected:
                break
    else:
        for record in records[: ns.max_candidates]:
            url = record["fields"].get("url")
            if not url:
                continue
            try:
                request = {
                    "source_kind": "web",
                    "source_id": source_id,
                    "url": url,
                    "rules_ref": source["collector_rules"],
                    "content_delivery": "auto",
                    "limits": task.get("limits", {}),
                }
                material = collector.call("POST", "/v1/fetches", json=request).json()
                result = extract(material)
                entity = next(
                    (
                        item
                        for item in result.get("output", {}).get("entities", [])
                        if identity(item) == identity(record) and amount_valid(item["fields"].get("price"))
                    ),
                    None,
                )
                if entity:
                    selected = record
                    material_and_result = (material, result, entity)
                    break
                attempts.append(f"{url}: no matching priced output")
            except (RuntimeError, TimeoutError) as exc:
                attempts.append(f"{url}: {exc}")
    if selected is None or material_and_result is None:
        raise RuntimeError(f"{source_id}: no freshly observed existing priced product; {attempts}")
    material, extraction, entity = material_and_result
    key = selected["canonical_key"]
    before = current(svc.storage, connection, key)
    before_history = history(svc.storage, connection, key)
    partial = copy.deepcopy(entity)
    partial["fields"] = {field: value for field, value in entity["fields"].items() if field in PRICE_FIELDS}
    partial["cleared"] = [field for field in entity.get("cleared", []) if field == "old_price"]
    partial["completeness"] = "partial"
    # The originating full-card schema is not a schema for this deliberately narrower projection.
    partial.pop("schema", None)
    stored = invoke(
        writer,
        {
            "handler": store_stage["handler"],
            "params": store_stage.get("params", {}),
            "connections": store_stage["connections"],
            "inputs": [
                {"kind": "entities", "entities": [partial], "from_invocation_id": extraction["invocation_id"]}
            ],
        },
        ns.timeout_s,
    )
    after = current(svc.storage, connection, key)
    after_history = history(svc.storage, connection, key)
    observation_id = partial["observation"]["observation_id"]
    delivered = [
        entry for entry in after_history if entry["record"]["observation"]["observation_id"] == observation_id
    ]
    omitted = set(before["fields"]) - set(partial["fields"]) - set(partial["cleared"])
    preserved = all(after["fields"].get(field) == before["fields"][field] for field in omitted)
    old_cleared = "old_price" in partial["cleared"]
    checks = {
        "amount_matches_live_output": after["fields"].get("price") == entity["fields"]["price"],
        "history_advanced": len(after_history) > len(before_history) and len(delivered) == 1,
        "version_advanced": after.get("version", 0) > before.get("version", 0),
        "price_applied": bool(delivered) and "price" in delivered[0]["applied_fields"],
        "fresh_price_observation": after.get("field_orders", {}).get("price", {}).get("observation_id")
        == observation_id,
        "attributes_preserved": after["fields"].get("attributes") == before["fields"]["attributes"],
        "omitted_metadata_preserved": preserved,
        "old_price_cleared_when_source_confirmed": not old_cleared or "old_price" not in after["fields"],
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "source_id": source_id,
        "canonical_key": key,
        "url": entity["fields"].get("url") or material.get("locator", {}).get("url"),
        "extractor": extraction["handler"],
        "extraction_invocation_id": extraction["invocation_id"],
        "storage_invocation_id": stored["invocation_id"],
        "observation": partial["observation"],
        "live_price": entity["fields"]["price"],
        "currency": entity["fields"].get("currency"),
        "price_before": before["fields"].get("price"),
        "price_after": after["fields"].get("price"),
        "old_price_before": before["fields"].get("old_price"),
        "old_price_after": after["fields"].get("old_price"),
        "old_price_clear_requested": old_cleared,
        "cleared_fields": partial["cleared"],
        "version_before": before.get("version"),
        "version_after": after.get("version"),
        "updated_at_before": before.get("updated_at"),
        "updated_at_after": after.get("updated_at"),
        "history_before": len(before_history),
        "history_after": len(after_history),
        "attributes_before": before["fields"]["attributes"],
        "attributes_after": after["fields"].get("attributes"),
        "omitted_metadata_fields": sorted(omitted),
        "applied_fields": delivered[0]["applied_fields"] if delivered else [],
        "stale_fields": delivered[0]["stale_fields"] if delivered else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--out", type=Path, default=HERE / "catalogs/price-verification.json")
    parser.add_argument("--timeout-s", type=float, default=120)
    parser.add_argument("--candidate-limit", type=int, default=500)
    parser.add_argument("--max-candidates", type=int, default=4)
    parser.add_argument("--varus-page-size", type=int, default=48)
    parser.add_argument("shops", nargs="*", choices=SHOPS)
    ns = parser.parse_args()
    stack = ex.read_json(ex.STACK_DIR / f"stack-{ns.project}.json")
    token = stack.get("env", {}).get("JANE_API_KEY_ADMIN")
    svc = ex.Services.of_project(ns.project)
    collector = ex.Api(stack["services"]["web-collector"]["url"], "collector", ns.timeout_s, token=token)
    runtime = ex.Api(stack["services"]["handler-runtime"]["url"], "handler", ns.timeout_s, token=token)
    writer = ex.Api(stack["services"]["storage"]["url"], "handler", ns.timeout_s, token=token)
    report: dict[str, Any] = {"checked_at": datetime.now(UTC).isoformat(), "project": ns.project, "sites": {}}
    try:
        for name in ns.shops or SHOPS:
            try:
                report["sites"][name] = verify_one(svc, collector, runtime, writer, name, ns)
                result = report["sites"][name]
                ex.log(
                    f"{name}: price={result['price_after']} {result['currency']}; partial update {'ok' if result['passed'] else 'FAILED'}"
                )
            except Exception as exc:
                error = str(exc).replace(token, "[redacted]") if token else str(exc)
                report["sites"][name] = {"passed": False, "error": error}
                ex.log(f"{name}: verification FAILED: {error}")
            ns.out.parent.mkdir(parents=True, exist_ok=True)
            ex.write_json(ns.out, report)
        return 0 if all(site["passed"] for site in report["sites"].values()) else 1
    finally:
        collector.close()
        runtime.close()
        writer.close()
        svc.close()


if __name__ == "__main__":
    sys.exit(main())
