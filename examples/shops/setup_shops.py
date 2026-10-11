"""Laptop prices of five real shops (Rozetka, Allo, Citrus, Foxtrot, Moyo) on a running Jane stack.

Publishes and approves the packages of ``examples/shops/packages`` (a JSON-LD and a product-card extractor,
collector rules per shop) and the storage packages ``jane.storage-files`` / ``jane.storage-mongodb``, puts the
connections ``raw-files`` / ``results-mongo`` (from ``examples/documents/connections.json``), creates or replaces
a source and a task per shop and starts every task once: category pages 1-5 -> RAW in files -> entities of the
taxonomy type ``product_electronics`` (the extractor stage parameter ``entity_type``) in MongoDB, a collection
per entity type. The tasks then run on their schedule.

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
JSONLD, CARDS = "shops.jsonld-offers", "shops.product-cards"
# shop -> (category URL, title, extractor package)
SHOPS = {
    "rozetka": ("https://rozetka.com.ua/ua/notebooks/c80004/", "Rozetka — ноутбуки", JSONLD),
    "allo": ("https://allo.ua/ua/products/notebooks/", "Allo — ноутбуки", JSONLD),
    "citrus": ("https://citrus.ua/noutbuki-i-ultrabuki/", "Цитрус — ноутбуки", JSONLD),
    "foxtrot": ("https://www.foxtrot.com.ua/uk/shop/noutbuki.html", "Фокстрот — ноутбуки", CARDS),
    "moyo": ("https://www.moyo.ua/ua/comp-and-periphery/notebooks/", "MOYO — ноутбуки", CARDS),
}
# the taxonomy type of the laptop category (docs/delivery/mongo-entities.md): the extractors take it from the
# stage parameter entity_type, it names the entity collection in MongoDB
ENTITY_TYPE = "product_electronics"
# (storage package, connection id): RAW pages in files, entities in MongoDB
RAW = ("jane.storage-files", "raw-files")
RESULTS = ("jane.storage-mongodb", "results-mongo")
STORAGE = (RAW[0], RESULTS[0])
CONNECTIONS = HERE.parent / "documents" / "connections.json"


def package_dirs(packages: Path = PACKAGES) -> dict[str, Path]:
    from jane_storage.adapters import package_dirs as storage_dirs

    dirs = {ex.read_json(p / "jane-package.json")["package_id"]: p for p in sorted(packages.iterdir())}
    for root in storage_dirs().values():
        pid = ex.read_json(Path(root) / "jane-package.json")["package_id"]
        if pid in STORAGE:
            dirs[pid] = Path(root)
    return dirs


def publish(svc: ex.Services, packages: Path = PACKAGES) -> dict[str, dict[str, str]]:
    """Publish, check and approve every package of ``packages`` and the storage packages; their references."""
    from jane_registry.archive import canonical_archive, digest_of, files_from_dir

    refs: dict[str, dict[str, str]] = {}
    for pid, directory in package_dirs(packages).items():
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


def connection_docs(path: Path = CONNECTIONS) -> list[dict[str, Any]]:
    """The connections the tasks use (``raw-files``, ``results-mongo``) from ``path``."""
    wanted = {RAW[1], RESULTS[1]}
    docs = [c for c in ex.read_json(path)["connections"] if c["connection_id"] in wanted]
    if missing := wanted - {c["connection_id"] for c in docs}:
        raise RuntimeError(f"{path}: connections {sorted(missing)} are missing")
    return docs


def upsert(orch: ex.Api, collection: str, id_field: str, doc: dict[str, Any]) -> int:
    """Create a source or a task, or replace the existing one (new package versions, another storage)."""
    if collection == "tasks":
        check = orch.call("POST", "/v1/task-validations", json=doc).json()
        if not check["valid"]:
            raise RuntimeError(f"task {doc['task_id']} is invalid: {check['errors']}")
    r = orch.call("POST", f"/v1/{collection}", ok=(201, 409), json=doc, headers={"Idempotency-Key": ex.key()})
    if r.status_code == 409:
        current = orch.call("GET", f"/v1/{collection}/{doc[id_field]}")
        r = orch.call(
            "PUT",
            f"/v1/{collection}/{doc[id_field]}",
            json=doc,
            headers={"If-Match": current.headers["ETag"]},
        )
    ex.log(f"orchestrator: {collection[:-1]} {doc[id_field]} -> {r.status_code}")
    return r.status_code


def source_doc(shop: str, url: str, title: str, refs: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "source_id": f"shop-{shop}",
        "kind": "web",
        "title": title,
        "description": f"Ціни ноутбуків {url}: сторінки категорії 1-5.",
        "locator": {"url": url},
        "collector_rules": refs[f"shops.{shop}-notebooks-rules"],
        "limits": {"rate": {"requests_per_second_per_host": 1, "min_delay_ms_per_host": 1000}},
        "forward_unknown_to_llm": False,
        "expected_entity_types": [ENTITY_TYPE],
        "labels": {"group": "notebook-prices"},
    }


def task_doc(shop: str, title: str, extractor: str, refs: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "task_id": f"notebooks-{shop}",
        "title": f"{title}: ціни",
        "description": f"Сторінки категорії → RAW у files, товари з цінами ({ENTITY_TYPE}) у MongoDB.",
        "input": {"source_id": f"shop-{shop}"},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web", "mode": "full"}},
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": refs[RAW[0]],
                "connections": {"target": RAW[1]},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "extract-offers",
                "kind": "handler",
                "handler": refs[extractor],
                "params": {"entity_type": ENTITY_TYPE},
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
                "handler": refs[RESULTS[0]],
                "connections": {"target": RESULTS[1]},
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
        for conn in connection_docs():
            orch.call("PUT", f"/v1/connections/{conn['connection_id']}", ok=(200, 201), json=conn)
        for shop, (url, title, extractor) in SHOPS.items():
            upsert(orch, "sources", "source_id", source_doc(shop, url, title, refs))
            upsert(orch, "tasks", "task_id", task_doc(shop, title, extractor, refs))
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
            products = svc.storage.pages(
                "/v1/entities",
                {"connection_id": RESULTS[1], "entity_type": ENTITY_TYPE, "scope": f"shop-{shop}"},
            )
            ex.log(f"storage: {len(products)} {ENTITY_TYPE} of shop-{shop}")
        return 1 if failed else 0
    finally:
        svc.close()


if __name__ == "__main__":
    sys.exit(main())
