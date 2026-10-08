"""Reproducible examples of WP-14: a full product catalog and a separate scheduled price check (TZ §12, c. 5).

Offline, without services::

    uv run --all-packages python examples/jane_examples.py check      # packages, digests, documents vs contracts/
    uv run --all-packages python examples/jane_examples.py lock       # recompute digests -> lock + documents
    uv run --all-packages python examples/jane_examples.py snapshot   # regenerate test pages from the testsite

Against a running stack (``deploy/profiles/stack.py up --project <p>``)::

    uv run --all-packages python examples/jane_examples.py demo --project <p>
    # = publish -> apply -> catalog -> price-check -> verify; each step is also a command of its own
    uv run --all-packages python examples/jane_examples.py telegram --project <p>   # publish -> apply -> telegram

Packages are archived with the registry's canonical algorithm (``jane_registry.archive``: zip stored, sorted
paths, fixed time and mode), so the digests in ``packages.lock.json`` and in the task documents are exactly the
digests the registry reports after publication. Every request to and response from a service is validated
against its OpenAPI contract in ``contracts/openapi`` (``jane_kit.contracts.ContractClient``).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from jane_kit.contracts import ContractClient, OpenAPISpec

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = Path(__file__).resolve().parent
PACKAGES_DIR = EXAMPLES / "packages"
DOCUMENTS_DIR = EXAMPLES / "documents"
LOCK_FILE = EXAMPLES / "packages.lock.json"
CONTRACTS = ROOT / "contracts"
STACK_DIR = ROOT / ".jane"

LOCAL_PACKAGES = (
    "examples.testsite-web-rules",
    "examples.testsite-catalog-extractor",
    "examples.testsite-price-extractor",
    "examples.telegram-rules",
    "examples.telegram-event-extractor",
)
STORAGE_PACKAGES = ("jane.storage-files", "jane.storage-postgresql")
SOURCE_DOC = "source.testsite-shop.json"
CATALOG_DOC = "task.testsite-catalog.json"
PRICE_DOC = "task.testsite-price-check.json"
CONNECTIONS_DOC = "connections.json"
TG_SOURCE_DOC = "source.telegram-events.json"
TG_TASK_DOC = "task.telegram-events.json"
TG_ACCOUNT_DOC = EXAMPLES / "telegram" / "connection.telegram-account.json"
TG_CHANNEL = "jane_events_example"
TESTSITE_HOST = "testsite:8080"  # the test site as the services see it inside the compose network
TERMINAL = frozenset({"succeeded", "failed", "cancelled"})
PRICE_FIELDS = frozenset({"sku", "price", "availability"})

# Test pages of the extractor packages, rendered by the real testsite (tests/fixtures/testsite).
SNAPSHOTS: dict[str, dict[str, str]] = {
    "examples.testsite-catalog-extractor": {
        "product-phone-alpha": "/product/phone-alpha",
        "product-phone-zeta": "/product/phone-zeta",
        "product-laptop-four": "/product/laptop-four",
        "category-phones": "/catalog/phones/",
        "unknown-faq": "/pages/faq",
    },
    "examples.testsite-price-extractor": {
        "product-phone-alpha": "/product/phone-alpha",
        "product-laptop-four": "/product/laptop-four",
        "category-laptops": "/catalog/laptops/",
    },
}


# ============================================================================================ offline
def write_json(path: Path, doc: Any) -> None:
    """The canonical JSON form of this directory (and of registry manifests): UTF-8, indent 2, LF."""
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def package_dir(package_id: str) -> Path:
    if package_id in LOCAL_PACKAGES:
        return PACKAGES_DIR / package_id
    from jane_storage.adapters import package_dirs

    for root in package_dirs().values():
        if read_json(root / "jane-package.json")["package_id"] == package_id:
            return Path(root)
    raise KeyError(package_id)


def canonical_archive(package_id: str) -> bytes:
    """Archive bytes the registry stores for this package (its own canonical algorithm)."""
    from jane_registry.archive import canonical_archive as registry_archive
    from jane_registry.archive import files_from_dir

    return bytes(registry_archive(files_from_dir(package_dir(package_id))))


def digest_of(data: bytes) -> str:
    from jane_registry.archive import digest_of as registry_digest

    return str(registry_digest(data))


def compute_lock() -> dict[str, Any]:
    packages: dict[str, Any] = {}
    for package_id in (*LOCAL_PACKAGES, *STORAGE_PACKAGES):
        directory = package_dir(package_id)
        manifest = read_json(directory / "jane-package.json")
        packages[package_id] = {
            "version": manifest["version"],
            "kind": manifest["kind"],
            "digest": digest_of(canonical_archive(package_id)),
            "path": directory.resolve().relative_to(ROOT.resolve()).as_posix(),
        }
    return {
        "comment": "Generated by `uv run --all-packages python examples/jane_examples.py lock`; "
        "digest = sha256 of the registry canonical archive (jane_registry.archive).",
        "packages": packages,
    }


def document_refs(doc: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
    """Every package reference of a source (``collector_rules``) or task (stage ``handler`` / ``rules``)."""
    if isinstance(doc.get("collector_rules"), dict):
        yield doc["collector_rules"]
    for stage in doc.get("stages") or []:
        if isinstance(stage.get("handler"), dict):
            yield stage["handler"]
        rules = (stage.get("collector") or {}).get("rules")
        if isinstance(rules, dict):
            yield rules


def cmd_lock(_: argparse.Namespace) -> int:
    lock = compute_lock()
    write_json(LOCK_FILE, lock)
    for name in (SOURCE_DOC, CATALOG_DOC, PRICE_DOC, TG_SOURCE_DOC, TG_TASK_DOC):
        path = DOCUMENTS_DIR / name
        doc = read_json(path)
        for ref in document_refs(doc):
            entry = lock["packages"][ref["package_id"]]
            ref["version"], ref["digest"] = entry["version"], entry["digest"]
        write_json(path, doc)
    for package_id, entry in lock["packages"].items():
        print(f"{package_id}@{entry['version']}  {entry['digest']}")
    return 0


def cmd_snapshot(_: argparse.Namespace) -> int:
    from jane_testsite import serve_in_thread  # type: ignore[import-untyped]

    with serve_in_thread() as base:
        for package_id, cases in SNAPSHOTS.items():
            for case, path in cases.items():
                page = render_page(base, path)
                target = PACKAGES_DIR / package_id / "tests" / case / "page.html"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(page)
                print(f"{target.relative_to(ROOT).as_posix()} <- {path}")
    return 0


def render_page(base: str, path: str) -> bytes:
    """One testsite page as the services see it (Host of the compose network)."""
    r = httpx.get(base + path, headers={"Host": TESTSITE_HOST}, timeout=10)
    r.raise_for_status()
    return r.content


@cache
def schema_registry() -> Registry[Any]:
    registry: Registry[Any] = Registry()
    schemas = CONTRACTS / "schemas"
    for path in sorted(schemas.rglob("*.schema.json")):
        uri = "https://jane.local/contracts/" + path.relative_to(CONTRACTS).as_posix()
        doc = read_json(path)
        doc["$id"] = uri
        registry = registry.with_resource(uri, Resource.from_contents(doc))
    return registry


def validate(schema: str, doc: Any) -> list[str]:
    """Errors of ``doc`` against ``contracts/schemas/<schema>`` (``file.schema.json#/$defs/X`` allowed)."""
    uri = "https://jane.local/contracts/schemas/" + schema
    validator = Draft202012Validator({"$ref": uri}, registry=schema_registry())
    return [f"{'/'.join(map(str, e.absolute_path)) or '/'}: {e.message}" for e in validator.iter_errors(doc)]


def package_json_problems(directory: Path, manifest: Mapping[str, Any]) -> list[str]:
    """Every JSON file of a package parses; params and entity schemas are valid JSON Schemas.

    The SDK's in-process test run does not load the schemas, the registry and the runtime do (422).
    """
    problems: list[str] = []
    for path in sorted(directory.rglob("*.json")):
        try:
            read_json(path)
        except ValueError as exc:
            problems.append(f"{path.relative_to(directory).as_posix()}: invalid JSON: {exc}")
    schemas = [manifest.get("params_schema")] + [
        e.get("schema") for e in (manifest.get("output") or {}).get("entities", [])
    ]
    for rel in [s for s in schemas if isinstance(s, str)]:
        try:
            Draft202012Validator.check_schema(read_json(directory / rel))
        except (ValueError, SchemaError) as exc:
            problems.append(f"{rel}: not a valid JSON Schema: {str(exc)[:200]}")
    return problems


def check_offline() -> list[str]:
    """Problems of the examples in this checkout (empty = reproducible): the same checks as the tests."""
    from jane_extractor_sdk.testing import run_package_tests

    problems: list[str] = []
    lock = read_json(LOCK_FILE)
    computed = compute_lock()
    if lock["packages"] != computed["packages"]:
        problems.append("packages.lock.json is stale: run `examples/jane_examples.py lock`")
    for package_id in LOCAL_PACKAGES:
        directory = PACKAGES_DIR / package_id
        raw = (directory / "jane-package.json").read_text(encoding="utf-8")
        manifest = json.loads(raw)
        problems += [
            f"{package_id}: manifest {e}" for e in validate("package-manifest.schema.json", manifest)
        ]
        if raw != json.dumps(manifest, ensure_ascii=False, indent=2) + "\n":
            problems.append(f"{package_id}: jane-package.json is not in canonical JSON form (see write_json)")
        problems += [f"{package_id}: {e}" for e in package_json_problems(directory, manifest)]
        if manifest["kind"] == "collector-rules":
            rules = read_json(directory / manifest["entry"]["rules"])
            problems += [f"{package_id}: rules {e}" for e in validate("collector-rules.schema.json", rules)]
        else:
            for result in run_package_tests(directory):
                if not result.passed:
                    problems.append(
                        f"{package_id}: test {result.name} expected {result.expected_status}, "
                        f"got {result.actual_status} {result.differences}"
                    )
    for name, schema in (
        (SOURCE_DOC, "source.schema.json"),
        (CATALOG_DOC, "task-config.schema.json"),
        (PRICE_DOC, "task-config.schema.json"),
        (TG_SOURCE_DOC, "source.schema.json"),
        (TG_TASK_DOC, "task-config.schema.json"),
    ):
        doc = read_json(DOCUMENTS_DIR / name)
        problems += [f"{name}: {e}" for e in validate(schema, doc)]
        for ref in document_refs(doc):
            entry = computed["packages"].get(ref["package_id"])
            if entry is None or (ref.get("version"), ref.get("digest")) != (
                entry["version"],
                entry["digest"],
            ):
                problems.append(f"{name}: {ref['package_id']} is not pinned to the lock (version + digest)")
    for conn in [*read_json(DOCUMENTS_DIR / CONNECTIONS_DOC)["connections"], read_json(TG_ACCOUNT_DOC)]:
        problems += [
            f"connections {conn['connection_id']}: {e}"
            for e in validate("common/connection.schema.json", conn)
        ]
    return problems


def cmd_check(_: argparse.Namespace) -> int:
    problems = check_offline()
    for p in problems:
        print("FAIL", p)
    print("examples: ok" if not problems else f"examples: {len(problems)} problem(s)")
    return 1 if problems else 0


# ============================================================================================ online
@cache
def spec(api: str) -> OpenAPISpec:
    return OpenAPISpec.load(CONTRACTS / "openapi" / f"{api}.v1.yaml")


class Api:
    """One service; every request body and response is validated against its contract."""

    def __init__(
        self, base_url: str, api: str, timeout_s: float = 120.0, *, token: str | None = None
    ) -> None:
        # ADR-0005: the stack runs in auth_mode=api_key; the driver calls as the stack's operator (admin key).
        headers = {"Authorization": f"Bearer {token}"} if token else None
        self.http = httpx.Client(base_url=base_url, timeout=timeout_s, headers=headers)
        self.client = ContractClient(spec(api), self.http)

    def close(self) -> None:
        self.http.close()

    def call(self, method: str, path: str, *, ok: Sequence[int] = (200,), **kw: Any) -> httpx.Response:
        r = self.client.request(method, path, **kw)
        if r.status_code not in ok:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:2000]}")
        return r

    def pages(self, path: str, params: Mapping[str, Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query = {**params, "limit": 500, **({"cursor": cursor} if cursor else {})}
            body = self.call("GET", path, params=query).json()
            items.extend(body["items"])
            cursor = body.get("next_cursor")
            if not cursor:
                return items


def key() -> str:
    return uuid.uuid4().hex


@dataclass
class Services:
    registry: Api
    orchestrator: Api
    storage: Api

    @classmethod
    def of_project(cls, project: str) -> Services:
        path = STACK_DIR / f"stack-{project}.json"
        if not path.is_file():
            raise SystemExit(f"no stack file {path}: start the stack with deploy/profiles/stack.py up")
        stack = read_json(path)
        urls = {name: info["url"] for name, info in stack["services"].items() if "url" in info}
        missing = [s for s in ("registry", "orchestrator", "storage") if s not in urls]
        if missing:
            raise SystemExit(f"stack {project} has no {', '.join(missing)}")
        token = (stack.get("env") or {}).get("JANE_API_KEY_ADMIN")  # generated with the stack, never in git
        return cls(
            Api(urls["registry"], "registry", token=token),
            Api(urls["orchestrator"], "orchestrator", token=token),
            Api(urls["storage"], "storage", token=token),
        )

    def close(self) -> None:
        for api in (self.registry, self.orchestrator, self.storage):
            api.close()


def log(message: str) -> None:
    """Progress line; the time is UTC and says so (``Z``), like the API timestamps it sits next to."""
    print(f"[{datetime.now(UTC).strftime('%H:%M:%SZ')}] {message}", flush=True)


def publish(svc: Services) -> dict[str, Any]:
    """Create each package, publish its canonical archive, check the digest and approve the version."""
    lock = read_json(LOCK_FILE)["packages"]
    out: dict[str, Any] = {}
    for package_id in (*STORAGE_PACKAGES, *LOCAL_PACKAGES):
        entry = lock[package_id]
        archive = canonical_archive(package_id)
        if digest_of(archive) != entry["digest"]:
            raise RuntimeError(f"{package_id}: archive digest differs from packages.lock.json; run `lock`")
        manifest = read_json(package_dir(package_id) / "jane-package.json")
        created = svc.registry.call(
            "POST",
            "/v1/packages",
            ok=(201, 409),
            json={
                "package_id": package_id,
                "kind": manifest["kind"],
                "title": manifest["title"],
                "description": manifest.get("description", ""),
                "auto_changes_allowed": False,
            },
            headers={"Idempotency-Key": key()},
        )
        version_path = f"/v1/packages/{package_id}/versions/{entry['version']}"
        r = svc.registry.call(
            "POST",
            f"/v1/packages/{package_id}/versions",
            ok=(201, 409),
            content=archive,
            headers={"Content-Type": "application/zip", "Idempotency-Key": key()},
        )
        version = r.json() if r.status_code == 201 else svc.registry.call("GET", version_path).json()
        if version["digest"] != entry["digest"]:
            raise RuntimeError(f"{package_id}: registry digest {version['digest']} != lock {entry['digest']}")
        if version["status"] == "draft":
            version = svc.registry.call(
                "POST",
                f"{version_path}/status",
                json={"status": "approved", "reason": "WP-14 example: package tests pass (examples/tests)"},
                headers={"Idempotency-Key": key()},
            ).json()
        downloaded = svc.registry.call("GET", f"{version_path}/archive").content
        if digest_of(downloaded) != entry["digest"]:
            raise RuntimeError(f"{package_id}: downloaded archive digest differs from the lock")
        out[package_id] = {
            "version": entry["version"],
            "digest": version["digest"],
            "status": version["status"],
            "package": "created" if created.status_code == 201 else "existed",
            "version_publish": r.status_code,
        }
        log(f"registry: {package_id}@{entry['version']} {version['digest']} {version['status']}")
    return out


def apply(svc: Services) -> dict[str, Any]:
    """Connections, the source and the catalog task in the orchestrator (the price check comes later)."""
    orch = svc.orchestrator
    for conn in [*read_json(DOCUMENTS_DIR / CONNECTIONS_DOC)["connections"], read_json(TG_ACCOUNT_DOC)]:
        orch.call("PUT", f"/v1/connections/{conn['connection_id']}", ok=(200, 201), json=conn)
    source = read_json(DOCUMENTS_DIR / SOURCE_DOC)
    r = orch.call("POST", "/v1/sources", ok=(201, 409), json=source, headers={"Idempotency-Key": key()})
    log(f"orchestrator: source {source['source_id']} -> {r.status_code}")
    return {
        "source": r.status_code,
        "catalog_task": create_task(orch, read_json(DOCUMENTS_DIR / CATALOG_DOC)),
    }


def create_task(orch: Api, task: dict[str, Any]) -> int:
    check = orch.call("POST", "/v1/task-validations", json=task).json()
    if not check["valid"]:
        raise RuntimeError(f"task {task['task_id']} is invalid: {check['errors']}")
    r = orch.call("POST", "/v1/tasks", ok=(201, 409), json=task, headers={"Idempotency-Key": key()})
    log(
        f"orchestrator: task {task['task_id']} -> {r.status_code} (warnings: {len(check.get('warnings') or [])})"
    )
    return r.status_code


def start_run(orch: Api, task_id: str, reason: str) -> str:
    r = orch.call(
        "POST",
        f"/v1/tasks/{task_id}/runs",
        ok=(202,),
        json={"reason": reason},
        headers={"Idempotency-Key": key()},
    )
    return str(r.json()["job_id"])


def wait_run(orch: Api, run_id: str, timeout_s: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    while True:
        run: dict[str, Any] = orch.call("GET", f"/v1/runs/{run_id}").json()
        if run["status"] in TERMINAL:
            return run
        if time.monotonic() > deadline:
            raise TimeoutError(f"run {run_id} still {run['status']} after {timeout_s:.0f}s")
        time.sleep(1.0)


def run_summary(run: Mapping[str, Any]) -> dict[str, Any]:
    stages = {s["stage_id"]: {k: v for k, v in s.items() if k != "stage_id"} for s in run.get("stages") or []}
    return {
        k: run.get(k) for k in ("run_id", "task_id", "trigger", "status", "started_at", "finished_at")
    } | {
        "counters": run.get("counters"),
        "stages": stages,
    }


def catalog(svc: Services, timeout_s: float) -> dict[str, Any]:
    run_id = start_run(svc.orchestrator, "testsite-catalog", "WP-14 example: full catalog")
    log(f"catalog: run {run_id} started")
    run = wait_run(svc.orchestrator, run_id, timeout_s)
    log(f"catalog: run {run_id} {run['status']}")
    if run["status"] != "succeeded":
        raise RuntimeError(f"catalog run failed: {json.dumps(run)[:2000]}")
    return run_summary(run)


def price_check(svc: Services, first_in_s: int, timeout_s: float) -> dict[str, Any]:
    """Create the price-check task so that its schedule fires ``first_in_s`` from now; wait for that run.

    The document keeps its cadence (``schedule.interval_seconds``); only ``schedule.start_at`` - the time of
    the first tick - is set here, because a fresh interval schedule otherwise fires one interval after creation.
    """
    orch = svc.orchestrator
    task = read_json(DOCUMENTS_DIR / PRICE_DOC)
    start_at = (datetime.now(UTC) + timedelta(seconds=first_in_s)).replace(microsecond=0)
    task["schedule"]["start_at"] = start_at.isoformat().replace("+00:00", "Z")
    status = create_task(orch, task)
    log(f"price-check: first scheduled run at {task['schedule']['start_at']}")
    deadline = time.monotonic() + first_in_s + timeout_s
    run_id: str | None = None
    while run_id is None:
        runs = orch.call("GET", "/v1/runs", params={"task_id": task["task_id"], "limit": 50}).json()["items"]
        scheduled = [r for r in runs if r["trigger"] == "schedule"]
        if scheduled:
            run_id = str(sorted(scheduled, key=lambda r: r["created_at"])[0]["run_id"])
        elif time.monotonic() > deadline:
            raise TimeoutError("the scheduled price-check run did not start")
        else:
            time.sleep(1.0)
    log(f"price-check: scheduled run {run_id} started")
    run = wait_run(orch, run_id, timeout_s)
    log(f"price-check: run {run_id} {run['status']}")
    if run["status"] != "succeeded":
        raise RuntimeError(f"price-check run failed: {json.dumps(run)[:2000]}")
    task_view = orch.call("GET", f"/v1/tasks/{task['task_id']}").json()
    return run_summary(run) | {
        "task_create": status,
        "start_at": task["schedule"]["start_at"],
        "task": task_view,
    }


def check_price_update(
    sku: str, state: Mapping[str, Any], entry: Mapping[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    """Check that a partial price record actually changed both requested fields."""
    record = entry["record"]
    orders = state.get("field_orders") or {}
    price_obs = (orders.get("price") or {}).get("observation_id")
    title_obs = (orders.get("title") or {}).get("observation_id")
    info = {
        "completeness": record.get("completeness"),
        "record_fields": sorted(record["fields"]),
        "applied_fields": entry.get("applied_fields"),
        "package": (record.get("provenance") or {}).get("package"),
        "state_fields": sorted(state.get("fields") or {}),
        "state_version": state.get("version"),
        "price_observation_is_price_check": price_obs == record["observation"]["observation_id"],
        "title_observation_kept_from_catalog": bool(title_obs) and title_obs != price_obs,
    }
    failures: list[str] = []
    if record.get("completeness") != "partial" or set(record["fields"]) != PRICE_FIELDS:
        failures.append(f"{sku}: price-check record is not a partial price/availability update: {info}")
    if not {"price", "availability"} <= set(entry.get("applied_fields") or []):
        failures.append(f"{sku}: price and availability were not both applied: {info}")
    if (info["package"] or {}).get("package_id") != "examples.testsite-price-extractor":
        failures.append(f"{sku}: price-check record was not produced by the price extractor: {info}")
    if not {"title", "category", "url"} <= set(state.get("fields") or {}):
        failures.append(f"{sku}: fields of the full card were lost after the partial update: {info}")
    if orders and not (
        info["price_observation_is_price_check"] and info["title_observation_kept_from_catalog"]
    ):
        failures.append(f"{sku}: field orders do not show a partial update: {orders}")
    return info, failures


def verify(svc: Services, catalog_run: Mapping[str, Any], price_run: Mapping[str, Any]) -> dict[str, Any]:
    """Effects through the public read APIs: RAW, full cards, partial price update, limits provenance."""
    source_id = read_json(DOCUMENTS_DIR / SOURCE_DOC)["source_id"]
    expected = read_json(ROOT / "tests" / "fixtures" / "testsite" / "expected_urls.json")
    category_set = set(expected["sets"]["categories"])
    products = sorted(p for p in category_set if p.startswith("/product/"))
    failures: list[str] = []

    raw = svc.storage.pages("/v1/objects", {"connection_id": "raw-files", "source_id": source_id})
    raw_paths = {site_path(obj["material"]["url"]) for obj in raw if "url" in obj.get("material", {})}
    if missing_raw := sorted({site_path(p) for p in category_set} - raw_paths):
        failures.append(f"RAW: catalog pages not stored: {missing_raw}")

    entities = {
        e["key"]["natural"]["sku"]: e
        for e in svc.storage.pages(
            "/v1/entities", {"connection_id": "results-pg", "entity_type": "product", "scope": source_id}
        )
    }
    skus = sorted(p.rsplit("/", 1)[-1] for p in products)
    if sorted(entities) != skus:
        failures.append(f"entities: expected {skus}, got {sorted(entities)}")
    for sku in skus:
        fields = (entities.get(sku) or {}).get("fields") or {}
        missing = {"sku", "title", "price", "availability", "category", "url"} - set(fields)
        if missing:
            failures.append(f"{sku}: full card lacks {sorted(missing)}")

    price_task = read_json(DOCUMENTS_DIR / PRICE_DOC)
    checked = sorted(u.rsplit("/", 1)[-1] for u in price_task["input"]["urls"])
    partial: dict[str, Any] = {}
    for sku in checked:
        state = entities.get(sku) or {}
        history = svc.storage.pages(
            "/v1/entity-history",
            {"connection_id": "results-pg", "entity_type": "product", "key": state.get("canonical_key", "")},
        )
        records = [
            h for h in history if (h["record"].get("provenance") or {}).get("run_id") == price_run["run_id"]
        ]
        if len(records) != 1:
            failures.append(f"{sku}: expected one history entry of the price-check run, got {len(records)}")
            continue
        info, update_failures = check_price_update(sku, state, records[0])
        partial[sku] = info
        failures.extend(update_failures)

    orch = svc.orchestrator
    platform = orch.call("GET", "/v1/limits/platform").json()
    effective = {
        task_id: orch.call(
            "GET",
            "/v1/limits/effective",
            params={"source_id": source_id, "task_id": task_id, "stage_id": "collect"},
        ).json()
        for task_id in ("testsite-catalog", "testsite-price-check")
    }
    provenance = {task_id: doc.get("provenance") or {} for task_id, doc in effective.items()}
    for task_id, origin in (("testsite-catalog", "task"), ("testsite-price-check", "task")):
        if provenance[task_id].get("crawl.max_pages_per_run") != origin:
            failures.append(
                f"{task_id}: crawl.max_pages_per_run should come from the task: {provenance[task_id]}"
            )
        if provenance[task_id].get("rate.requests_per_second_per_host") != "source":
            failures.append(f"{task_id}: the source rate limit is not effective: {provenance[task_id]}")
    catalog_task = orch.call("GET", "/v1/tasks/testsite-catalog").json()
    if catalog_task.get("schedule") != read_json(DOCUMENTS_DIR / CATALOG_DOC)["schedule"]:
        failures.append("catalog task schedule changed after the price check was added")
    return {
        "ok": not failures,
        "failures": failures,
        "raw_objects": len(raw),
        "entities": len(entities),
        "catalog_run": catalog_run["run_id"],
        "price_check_run": price_run["run_id"],
        "partial_updates": partial,
        "platform_profile": platform.get("profile") if isinstance(platform, dict) else None,
        "effective_collect_limits": effective,
    }


def site_path(url: str) -> str:
    """Path + query (parameters sorted) of a testsite URL, comparable with ``expected_urls.json``."""
    parts = urlsplit(url)
    query = "&".join(sorted(parts.query.split("&"))) if parts.query else ""
    return parts.path + (f"?{query}" if query else "")


# ============================================================================================ telegram
def telegram_run(svc: Services, timeout_s: float, reason: str) -> dict[str, Any]:
    run_id = start_run(svc.orchestrator, "telegram-events", reason)
    run = wait_run(svc.orchestrator, run_id, timeout_s)
    log(f"telegram: run {run_id} {run['status']} {run.get('counters')}")
    if run["status"] != "succeeded":
        raise RuntimeError(f"telegram run failed: {json.dumps(run)[:2000]}")
    return run_summary(run)


def telegram(svc: Services, project: str, timeout_s: float) -> dict[str, Any]:
    """Events from Telegram on the RECORDED backend (external-service substitute, mark "З").

    Run 1 reads the channel history; then the recording gets an edit of message 1 and a new message 4 (as
    the channel would), run 2 (incremental) must see exactly these two as new observations; the edit updates
    the stored event instead of adding one.
    """
    from jane_telegram_collector.recorded import Recording  # type: ignore[import-untyped]

    orch = svc.orchestrator
    source = read_json(DOCUMENTS_DIR / TG_SOURCE_DOC)
    r = orch.call("POST", "/v1/sources", ok=(201, 409), json=source, headers={"Idempotency-Key": key()})
    log(f"orchestrator: source {source['source_id']} -> {r.status_code}")
    create_task(orch, read_json(DOCUMENTS_DIR / TG_TASK_DOC))
    history = telegram_run(svc, timeout_s, "WP-14 example: channel history")
    recording_path = STACK_DIR / f"telegram-recordings-{project}" / f"{TG_CHANNEL}.json"
    rec = Recording(recording_path, channel_id="", username=TG_CHANNEL)
    rec.reload()
    rec.edit(
        1,
        "Подія: Лекція про історію міста | 2026-10-05 19:00 | Міська бібліотека, зала 2",
        edit_date=datetime(2026, 9, 30, 8, 0, tzinfo=UTC),
    )
    rec.post(
        "Подія: Осінній ярмарок | 2026-10-19 10:00 | Центральна площа",
        date=datetime(2026, 9, 30, 9, 0, tzinfo=UTC),
    )
    log("telegram: recording changed (message 1 edited, message 4 posted)")
    changes = telegram_run(svc, timeout_s, "WP-14 example: new and edited messages")
    return {"history": history, "changes": changes, "verify": verify_telegram(svc, history, changes)}


def verify_telegram(svc: Services, history: Mapping[str, Any], changes: Mapping[str, Any]) -> dict[str, Any]:
    source_id = read_json(DOCUMENTS_DIR / TG_SOURCE_DOC)["source_id"]
    failures: list[str] = []
    if (history.get("counters") or {}).get("materials") != 3:
        failures.append(f"history run: expected 3 messages, got {history.get('counters')}")
    if (changes.get("counters") or {}).get("materials") != 2:
        failures.append(f"changes run: expected 2 observations (edit + new), got {changes.get('counters')}")
    raw = svc.storage.pages("/v1/objects", {"connection_id": "raw-files", "source_id": source_id})
    if len(raw) != 5 or len({o["material"]["observation_id"] for o in raw}) != 5:
        failures.append(f"RAW: expected 5 distinct observations, got {len(raw)}")
    events = {
        e["key"]["natural"]["event_id"]: e
        for e in svc.storage.pages(
            "/v1/entities", {"connection_id": "results-pg", "entity_type": "event", "scope": source_id}
        )
    }
    expected = {f"{TG_CHANNEL}/1/1", f"{TG_CHANNEL}/3/2", f"{TG_CHANNEL}/4/1"}
    if set(events) != expected:
        failures.append(f"events: expected {sorted(expected)}, got {sorted(events)}")
    lecture = events.get(f"{TG_CHANNEL}/1/1") or {}
    fields = lecture.get("fields") or {}
    if fields.get("time") != "19:00" or not str(fields.get("place", "")).endswith("зала 2"):
        failures.append(f"edited message did not update the event: {fields}")
    history_of_lecture = svc.storage.pages(
        "/v1/entity-history",
        {"connection_id": "results-pg", "entity_type": "event", "key": lecture.get("canonical_key", "")},
    )
    if len(history_of_lecture) != 2:
        failures.append(f"the edited event should have 2 history entries, got {len(history_of_lecture)}")
    return {
        "ok": not failures,
        "failures": failures,
        "raw_objects": len(raw),
        "events": {k: v.get("fields") for k, v in sorted(events.items())},
        "lecture_version": lecture.get("version"),
        "substitute": "Telegram = recorded backend of telegram-collector (З)",
    }


def summary_path(project: str) -> Path:
    return STACK_DIR / f"examples-{project}.json"


def cmd_online(ns: argparse.Namespace) -> int:
    svc = Services.of_project(ns.project)
    out_path = summary_path(ns.project)
    state: dict[str, Any] = read_json(out_path) if out_path.is_file() else {}
    try:
        steps = {
            "demo": ["publish", "apply", "catalog", "price-check", "verify"],
            "telegram": ["publish", "apply", "telegram"],  # publish/apply are idempotent
        }.get(ns.command, [ns.command])
        for step in steps:
            if step == "publish":
                state["publish"] = publish(svc)
            elif step == "apply":
                state["apply"] = apply(svc)
            elif step == "catalog":
                state["catalog"] = catalog(svc, ns.timeout)
            elif step == "price-check":
                state["price_check"] = price_check(svc, ns.first_check_in, ns.timeout)
            elif step == "telegram":
                state["telegram"] = telegram(svc, ns.project, ns.timeout)
            elif step == "verify":
                if "catalog" not in state or "price_check" not in state:
                    raise SystemExit("verify needs the catalog and price-check runs of this project")
                state["verify"] = verify(svc, state["catalog"], state["price_check"])
            STACK_DIR.mkdir(exist_ok=True)
            write_json(out_path, state)
    finally:
        svc.close()
    if ns.command == "telegram":
        print(json.dumps(state["telegram"]["verify"], ensure_ascii=False, indent=2))
        print(f"summary: {out_path.relative_to(ROOT).as_posix()}")
        return 0 if state["telegram"]["verify"]["ok"] else 1
    result = state.get("verify")
    if result is not None:
        print(json.dumps({k: v for k, v in result.items() if k != "effective_collect_limits"}, indent=2))
        print(f"summary: {out_path.relative_to(ROOT).as_posix()}")
        return 0 if result["ok"] else 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Ukrainian text also when redirected on Windows
    ap = argparse.ArgumentParser(
        prog="jane_examples.py", description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="offline: packages, tests, digests and documents").set_defaults(fn=cmd_check)
    sub.add_parser("lock", help="offline: recompute digests into the lock and the documents").set_defaults(
        fn=cmd_lock
    )
    sub.add_parser("snapshot", help="offline: regenerate package test pages from the testsite").set_defaults(
        fn=cmd_snapshot
    )
    for name in ("demo", "publish", "apply", "catalog", "price-check", "verify", "telegram"):
        p = sub.add_parser(name, help=f"against a running stack: {name}")
        p.add_argument("--project", required=True, help="compose project of deploy/profiles/stack.py up")
        p.add_argument("--timeout", type=float, default=600.0, help="seconds per run (default 600)")
        p.add_argument(
            "--first-check-in", type=int, default=15, help="seconds until the first scheduled price check"
        )
        p.set_defaults(fn=cmd_online)
    ns = ap.parse_args(argv)
    return int(ns.fn(ns))


if __name__ == "__main__":
    sys.exit(main())
