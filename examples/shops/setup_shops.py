"""Laptop prices of three real shops (Rozetka, Allo, Citrus) on a running Jane stack.

Publishes and approves the packages of ``examples/shops/packages`` (one shared JSON-LD extractor, collector
rules per shop) and the storage packages, puts the connections ``raw-files`` / ``results-pg`` (as
``examples/documents/connections.json``), creates a source and a task per shop and starts every task once:
category pages 1-5 -> RAW in files -> ``offer`` entities in PostgreSQL. The tasks then run on their schedule.

    uv run --all-packages python examples/shops/setup_shops.py --project <compose-project> [--no-run]

The stack needs the cross-service wiring of ``infra/compose.local.example.yaml``. Real sites: robots.txt is
respected, one request per second per host, five pages per shop and run.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import jane_examples as ex  # noqa: E402 - examples/jane_examples.py: contract-validated API clients

PACKAGES = HERE / "packages"
EXTRACTOR = "shops.jsonld-offers"
SHOPS = {
    "rozetka": ("https://rozetka.com.ua/ua/notebooks/c80004/", "Rozetka — ноутбуки"),
    "allo": ("https://allo.ua/ua/products/notebooks/", "Allo — ноутбуки"),
    "citrus": ("https://citrus.ua/noutbuki-i-ultrabuki/", "Цитрус — ноутбуки"),
}
STORAGE = ("jane.storage-files", "jane.storage-postgresql")


def package_dirs() -> dict[str, Path]:
    from jane_storage.adapters import package_dirs as storage_dirs

    dirs = {ex.read_json(p / "jane-package.json")["package_id"]: p for p in sorted(PACKAGES.iterdir())}
    for root in storage_dirs().values():
        pid = ex.read_json(Path(root) / "jane-package.json")["package_id"]
        if pid in STORAGE:
            dirs[pid] = Path(root)
    return dirs


def publish(svc: ex.Services) -> dict[str, dict[str, str]]:
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    refs: dict[str, dict[str, str]] = {}
    for pid, directory in package_dirs().items():
        manifest = ex.read_json(directory / "jane-package.json")
        archive = bytes(canonical_archive(files_from_dir(directory)))
        digest = str(digest_of(archive))
        svc.registry.call(
            "POST",
            "/v1/packages",
            ok=(201, 409),
            json={
                "package_id": pid,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "description": manifest.get("description", ""),
                "auto_changes_allowed": False,
            },
            headers={"Idempotency-Key": ex.key()},
        )
        path = f"/v1/packages/{pid}/versions/{manifest['version']}"
        r = svc.registry.call(
            "POST",
            f"/v1/packages/{pid}/versions",
            ok=(201, 409),
            content=archive,
            headers={"Content-Type": "application/zip", "Idempotency-Key": ex.key()},
        )
        version = r.json() if r.status_code == 201 else svc.registry.call("GET", path).json()
        if version["digest"] != digest:
            raise RuntimeError(
                f"{pid}: registry has {version['digest']}, this checkout {digest}; bump the version"
            )
        if version["status"] == "draft":
            version = svc.registry.call(
                "POST",
                f"{path}/status",
                json={"status": "approved", "reason": "examples/shops: package tests pass locally"},
                headers={"Idempotency-Key": ex.key()},
            ).json()
        refs[pid] = {"package_id": pid, "version": manifest["version"], "digest": digest}
        ex.log(f"registry: {pid}@{manifest['version']} {version['status']}")
    return refs


def source_doc(shop: str, url: str, title: str, refs: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "source_id": f"shop-{shop}",
        "kind": "web",
        "title": title,
        "description": f"Ціни ноутбуків {url}: сторінки категорії 1-5, JSON-LD.",
        "locator": {"url": url},
        "collector_rules": refs[f"shops.{shop}-notebooks-rules"],
        "limits": {"rate": {"requests_per_second_per_host": 1, "min_delay_ms_per_host": 1000}},
        "forward_unknown_to_llm": False,
        "expected_entity_types": ["offer"],
        "labels": {"group": "notebook-prices"},
    }


def task_doc(shop: str, title: str, refs: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "task_id": f"notebooks-{shop}",
        "title": f"{title}: ціни",
        "description": "Сторінки категорії → RAW у files, пропозиції (offer) у PostgreSQL.",
        "input": {"source_id": f"shop-{shop}"},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}},
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": refs["jane.storage-files"],
                "connections": {"target": "raw-files"},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "extract-offers",
                "kind": "handler",
                "handler": refs[EXTRACTOR],
                "inputs": [
                    {
                        "from": "collect",
                        "when": {"field": "material.format.media_type", "op": "eq", "value": "text/html"},
                    }
                ],
            },
            {
                "stage_id": "store-offers",
                "kind": "handler",
                "handler": refs["jane.storage-postgresql"],
                "connections": {"target": "results-pg"},
                "inputs": [
                    {
                        "from": "extract-offers",
                        "select": "output",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
            },
        ],
        "schedule": {"type": "cron", "cron": "0 9,21 * * *", "timezone": "Europe/Kyiv", "overlap": "skip"},
        "limits": {"crawl": {"max_depth": 1, "max_pages_per_run": 10}},
        "forward_unknown_to_llm": False,
        "labels": {"group": "notebook-prices"},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--no-run", action="store_true", help="create everything, start no run")
    ap.add_argument("--timeout", type=float, default=900)
    ns = ap.parse_args(argv)
    svc = ex.Services.of_project(ns.project)
    try:
        refs = publish(svc)
        orch = svc.orchestrator
        for conn in ex.read_json(HERE.parent / "documents" / "connections.json")["connections"]:
            orch.call("PUT", f"/v1/connections/{conn['connection_id']}", ok=(200, 201), json=conn)
        for shop, (url, title) in SHOPS.items():
            source = source_doc(shop, url, title, refs)
            r = orch.call(
                "POST", "/v1/sources", ok=(201, 409), json=source, headers={"Idempotency-Key": ex.key()}
            )
            if r.status_code == 409:  # exists: replace it (e.g. a new rules version)
                current = orch.call("GET", f"/v1/sources/{source['source_id']}")
                r = orch.call(
                    "PUT",
                    f"/v1/sources/{source['source_id']}",
                    json=source,
                    headers={"If-Match": current.headers["ETag"]},
                )
            ex.log(f"orchestrator: source {source['source_id']} -> {r.status_code}")
            ex.create_task(orch, task_doc(shop, title, refs))
        if ns.no_run:
            return 0
        runs = {shop: ex.start_run(orch, f"notebooks-{shop}", "examples/shops: first run") for shop in SHOPS}
        failed = 0
        for shop, run_id in runs.items():
            run = ex.wait_run(orch, run_id, ns.timeout)
            ex.log(f"run notebooks-{shop}: {run['status']} counters={run.get('counters')}")
            failed += run["status"] != "succeeded"
        time.sleep(2)
        for shop in SHOPS:
            offers = svc.storage.pages(
                "/v1/entities",
                {"connection_id": "results-pg", "entity_type": "offer", "scope": f"shop-{shop}"},
            )
            ex.log(f"storage: {len(offers)} offers of shop-{shop}")
        return 1 if failed else 0
    finally:
        svc.close()


if __name__ == "__main__":
    sys.exit(main())
