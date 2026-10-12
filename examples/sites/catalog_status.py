"""Validate stored catalogs and save a dated, reproducible snapshot without credentials.

Products are read from the entity storage of the site's tasks (``results-mongo``): every ``product_*`` type the
site's extractors declare, a MongoDB collection each; ``status.json`` counts them per type.

The count of stored products is not proof of a completed site scan. Collector checkpoints,
budget stops and discovery truncation are reported separately from entity validation.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup_sites as sites  # noqa: E402

import jane_examples as ex  # noqa: E402

PRODUCT_PREFIX = "product_"  # catalog types: product_<group> of the shop's category table


def snapshot_site(
    svc: ex.Services, config: dict[str, Any], dirs: dict[str, Path]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Every stored product of each source: all ``product_*`` types its extractors declare (one MongoDB
    collection per type), checked against the schema of its own type."""
    counts: dict[str, Any] = {}
    snapshots: dict[str, Any] = {}
    for source in config["sources"]:
        source_id = source["source_id"]
        extractors = sites.source_extractors(config, dirs, source_id)
        schemas = sites.entity_schemas({pid: dirs[pid] for pid in extractors})
        validators = {
            kind: [Draft202012Validator(s, format_checker=FormatChecker()) for s in found]
            for kind, found in schemas.items()
            if kind.startswith(PRODUCT_PREFIX)
        }
        connection = sites.results_connection(config, source_id)
        entities = sites.stored_entities(svc, connection, sorted(validators), source_id)
        invalid: list[str] = []
        priced = 0
        attributes: set[str] = set()
        by_type: dict[str, int] = {}
        for record in entities:
            fields = record["fields"]
            kind = record["entity_type"]
            by_type[kind] = by_type.get(kind, 0) + 1
            if not any(v.is_valid(fields) for v in validators.get(kind, [])):
                invalid.append(str(fields.get("product_id", "unknown")))
            amount = fields.get("price")
            if amount is not None:
                if (
                    isinstance(amount, bool)
                    or not isinstance(amount, int | float)
                    or not math.isfinite(amount)
                ):
                    invalid.append(str(fields.get("product_id", "unknown")) + ":price")
                elif amount > 0:
                    priced += 1
            attributes.update((fields.get("attributes") or {}).keys())
        histories = []
        for record in entities[:3]:
            key = record.get("canonical_key")
            if key:
                history = svc.storage.pages(
                    "/v1/entity-history",
                    {"connection_id": connection, "entity_type": record["entity_type"], "key": key},
                )
                histories.append(
                    {
                        "product_id": record["fields"].get("product_id"),
                        "entity_type": record["entity_type"],
                        "observations": len(history),
                        "received_at": [h.get("received_at") for h in history[-3:]],
                        "prices": [
                            (h.get("record", {}).get("fields") or {}).get("price") for h in history[-3:]
                        ],
                    }
                )
        source_counts = {
            "connection_id": connection,
            "stored_products": len(entities),
            "products_by_type": dict(sorted(by_type.items())),
            "priced_products": priced,
            "schema_invalid": len(set(invalid)),
            "invalid_examples": sorted(set(invalid))[:10],
            "attribute_names": sorted(attributes),
            "history_samples": histories,
            "entity_validation_passed": bool(entities) and not invalid,
        }
        counts[source_id] = source_counts
        snapshots[source_id] = entities
    return counts, snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--out", type=Path, default=HERE / "catalogs")
    parser.add_argument("sites", nargs="*")
    ns = parser.parse_args()
    ns.out.mkdir(parents=True, exist_ok=True)
    svc = ex.Services.of_project(ns.project)
    stack = ex.read_json(ex.STACK_DIR / f"stack-{ns.project}.json")
    collector = ex.Api(
        stack["services"]["web-collector"]["url"], "collector", token=stack["env"].get("JANE_API_KEY_ADMIN")
    )
    report: dict[str, Any] = {"checked_at": datetime.now(UTC).isoformat(), "project": ns.project, "sites": {}}
    try:
        dirs = sites.package_dirs()
        for path in sites.site_files(ns.sites):
            config = ex.read_json(path)
            counts, snapshots = snapshot_site(svc, config, dirs)
            for source_id, source_report in counts.items():
                state = collector.call("GET", f"/v1/states/{source_id}", ok=(200, 404))
                data = state.json() if state.status_code == 200 else {}
                source_report["collector_state"] = {
                    k: data.get(k)
                    for k in ("state_key", "known_urls", "url_count", "frontier_size", "last_collection_at")
                    if k in data
                }
            report["sites"][path.stem] = {
                "sources": counts,
                "coverage": config.get("coverage", {}),
                "tasks": [],
                "full_scan_complete": False,
            }
            for task in config["tasks"]:
                current = svc.orchestrator.call("GET", f"/v1/tasks/{task['task_id']}").json()
                report["sites"][path.stem]["tasks"].append(
                    {
                        "task_id": task["task_id"],
                        "schedule": current.get("schedule"),
                        "collector": next(
                            (
                                s.get("collector")
                                for s in current.get("stages", [])
                                if s.get("kind") == "collect"
                            ),
                            None,
                        ),
                    }
                )
            for source_id, entities in snapshots.items():
                payload = {
                    "checked_at": report["checked_at"],
                    "source_id": source_id,
                    "full_scan_complete": False,
                    "entities": entities,
                }
                data = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
                (ns.out / f"{source_id}.json.gz").write_bytes(gzip.compress(data, mtime=0))
                ex.log(
                    f"{source_id}: {counts[source_id]['stored_products']} products; "
                    f"{counts[source_id]['priced_products']} priced; {counts[source_id]['schema_invalid']} invalid"
                )
        ex.write_json(ns.out / "status.json", report)
        return (
            0
            if all(
                s["entity_validation_passed"]
                for site in report["sites"].values()
                for s in site["sources"].values()
            )
            else 1
        )
    finally:
        collector.close()
        svc.close()


if __name__ == "__main__":
    sys.exit(main())
