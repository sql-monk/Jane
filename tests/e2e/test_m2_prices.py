"""S-M2-04 (criterion 5): a full catalog task and a separate scheduled price check (docs/acceptance/scenarios.md).

Real services (Р): orchestrator (WP-09), web-collector (WP-02), handler-runtime (WP-06), storage (WP-07),
registry (WP-05), PostgreSQL and the test site code (WP-01). The packages and the source/task documents are
the reproducible examples of WP-14 (``examples/packages``, ``examples/documents``), published to the real
registry as canonical archives whose digests must equal ``examples/packages.lock.json``. The documents are
sent verbatim; only the price check's ``schedule.start_at`` is changed later through ``PUT /v1/tasks``.

STAND-IN (Т): the test site cannot change a price (request to WP-01). The module's own stack runs the
unchanged ``jane_testsite`` code through ``jane_e2e/testsite_prices.py`` (``compose.prices.yaml``), which adds
``PUT /_e2e/products/{slug}`` to change the price, availability or name of one product between the runs.

Flow (one test, the phases depend on each other):

A. catalog run -> 23 RAW pages, 16 full cards (sku, title, price, availability, category, url);
B. the price-check task is created as written (interval 1 h, first tick in an hour); a second catalog run is
   cancelled while it collects - the price-check task, its schedule and the stored cards stay as they were;
C. the site changes prices, one availability and one product NAME; ``PUT`` moves the first tick of the price
   check to ``now + JANE_E2E_PRICE_CHECK_START_IN_S``; the catalog task is unchanged; the run fired by the
   schedule updates only ``price``/``availability`` of its 4 products (``completeness: partial``), the title
   stays the catalog's although the page shows a new name, the other 12 cards are untouched;
D. the price check's page limit is changed to 2 -> its next run reads 2 pages, while the next catalog run still
   reads all 23 pages (limit 200 of its own task) and now takes the new name and the price of a product the
   price check does not cover.
"""

from __future__ import annotations

import copy
import json
import os
import time
import uuid
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest

from jane_e2e.clients import JaneClient
from jane_e2e.orchestration import TERMINAL, TESTSITE, list_items, put_connections, start_run, wait_run
from jane_e2e.stack import ROOT, E2EStack, default_project
from jane_e2e.verify import entities, expected_set, history, objects_by_source
from jane_registry.archive import canonical_archive, digest_of, files_from_dir
from jane_testsite import site as testsite_model  # type: ignore[import-untyped]

pytestmark = [pytest.mark.e2e, pytest.mark.milestone("M2"), pytest.mark.criteria(5)]

E2E_DIR = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
DOCUMENTS = EXAMPLES / "documents"
PRICES_OVERLAY = E2E_DIR / "compose.prices.yaml"
SERVICES = ("testsite", "registry", "handler-runtime", "storage", "web-collector", "orchestrator")
# Like S-M2-06/07: the runtime, the collector and the orchestrator use the REAL registry.
REGISTRY_ENV = {
    "JANE_E2E_RUNTIME_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_REGISTRY_RUNTIME_PROFILES": '["http://handler-runtime:8000/v1/info"]',
    "JANE_E2E_COLLECTOR_REGISTRY_URL": "http://registry:8000",
    "JANE_E2E_ORCHESTRATOR_EXTRA_EXECUTORS": "executors-registry.json",
}
RAW, RESULTS = (
    "raw-files",
    "results-pg",
)  # connection ids of the documents (tests/e2e/config/storage-connections.json)
CATALOG_EXTRACTOR, PRICE_EXTRACTOR = (
    "examples.testsite-catalog-extractor",
    "examples.testsite-price-extractor",
)
AVAILABILITY = {"InStock": "in_stock", "OutOfStock": "out_of_stock", "PreOrder": "preorder"}
CARD_FIELDS = frozenset({"sku", "title", "price", "availability", "category", "url"})
PRICE_FIELDS = frozenset({"sku", "price", "availability"})
# Changes on the site after the catalog (phase C). phone-zeta (checked) stays as it is; phone-beta is not in
# the price check's URL list, so only the next catalog run may show its new price.
SITE_CHANGES: dict[str, dict[str, str]] = {
    "phone-alpha": {"price": "279.00", "name": "Phone Alpha 2027"},
    "phone-gamma": {"price": "389.00", "availability": "InStock"},
    "laptop-four": {"price": "1149.00"},
    "phone-beta": {"price": "339.00"},
}
START_IN_S = int(os.environ.get("JANE_E2E_PRICE_CHECK_START_IN_S", "15"))
SCHEDULE_TOLERANCE_S = float(os.environ.get("JANE_E2E_SCHEDULE_TOLERANCE_S", "30"))
RUN_TIMEOUT_S = float(os.environ.get("JANE_E2E_RUN_TIMEOUT_S", "600"))


def read_json(path: Path) -> dict[str, Any]:
    doc: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return doc


SOURCE_DOC = read_json(DOCUMENTS / "source.testsite-shop.json")
CATALOG_DOC = read_json(DOCUMENTS / "task.testsite-catalog.json")
PRICE_DOC = read_json(DOCUMENTS / "task.testsite-price-check.json")
LOCK: dict[str, dict[str, Any]] = read_json(EXAMPLES / "packages.lock.json")["packages"]
SOURCE_ID = str(SOURCE_DOC["source_id"])
CATALOG, PRICE_CHECK = str(CATALOG_DOC["task_id"]), str(PRICE_DOC["task_id"])
CHECKED = sorted(url.rsplit("/", 1)[-1] for url in PRICE_DOC["input"]["urls"])
CATALOG_PAGES = expected_set("categories")  # category pages with pagination + listed products
PRODUCTS = sorted(p.rsplit("/", 1)[-1] for p in CATALOG_PAGES if p.startswith("/product/"))


# ---------------------------------------------------------------------------- stack
@dataclass
class Shop:
    stack: E2EStack
    clients: dict[str, JaneClient] = field(default_factory=dict)

    def __getitem__(self, service: str) -> JaneClient:
        if service not in self.clients:
            self.clients[service] = JaneClient(self.stack.url(service))
        return self.clients[service]

    def change_site(self, slug: str, changes: Mapping[str, str]) -> dict[str, Any]:
        """Price switch of the test site stand-in (Т); returns the product as the site now holds it."""
        r = httpx.put(f"{self.stack.url('testsite')}/_e2e/products/{slug}", json=dict(changes), timeout=10)
        assert r.status_code == 200, r.text
        product: dict[str, Any] = r.json()
        return product

    def product_page(self, slug: str) -> str:
        r = httpx.get(f"{self.stack.url('testsite')}/product/{slug}", timeout=10)
        assert r.status_code == 200, r.text
        return r.text


@pytest.fixture(scope="module")
def shop(stack: E2EStack) -> Iterator[Shop]:
    """An isolated stack: real registry everywhere and the test site with the price switch (``stack`` - the
    session one - only checks Docker; this module never starts services in it)."""
    own = E2EStack(project=f"{default_project()}-prices-{uuid.uuid4().hex[:6]}", overlays=(PRICES_OVERLAY,))
    own.env().update(REGISTRY_ENV)
    shop = Shop(own)
    try:
        if reasons := own.missing(SERVICES):
            pytest.skip("; ".join(reasons))
        own.ensure(*SERVICES)
        note("stack", {"project": own.project, "services": list(SERVICES)})
        yield shop
    finally:
        for client in shop.clients.values():
            client.close()
        if os.environ.get("JANE_E2E_KEEP") != "1":
            own.down(volumes=True)


# ---------------------------------------------------------------------------- helpers
def key() -> str:
    return uuid.uuid4().hex


def note(what: str, value: Any = None) -> None:
    """One evidence line for the report (visible with ``pytest -s``)."""
    text = what if value is None else f"{what}: {json.dumps(value, ensure_ascii=False, sort_keys=True)}"
    print(f"[S-M2-04] {text}", flush=True)


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def rfc3339(moment: datetime) -> str:
    return moment.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def document_refs() -> list[dict[str, Any]]:
    """Every package the source and both tasks pin (collector rules, extractors, storage handlers)."""
    refs = [SOURCE_DOC["collector_rules"]]
    for task in (CATALOG_DOC, PRICE_DOC):
        refs += [s["handler"] for s in task["stages"] if isinstance(s.get("handler"), dict)]
    return list({r["package_id"]: r for r in refs}.values())


def publish(registry: JaneClient, ref: Mapping[str, Any]) -> dict[str, Any]:
    """Create the package, publish its canonical archive, approve it; digests must equal the lock and the
    documents (the same steps as ``examples/jane_examples.py publish``, through contract-checked clients)."""
    api = registry.api("registry")
    package_id, entry = str(ref["package_id"]), LOCK[str(ref["package_id"])]
    assert (ref["version"], ref["digest"]) == (entry["version"], entry["digest"]), (ref, entry)
    directory = ROOT / entry["path"]
    manifest = read_json(directory / "jane-package.json")
    archive = canonical_archive(files_from_dir(directory))
    assert digest_of(archive) == entry["digest"], f"{package_id}: archive digest differs from the lock"
    body = {"package_id": package_id, "kind": manifest["kind"], "title": manifest["title"]}
    if manifest.get("description"):
        body["description"] = manifest["description"]
    created = api.post("/v1/packages", json=body, headers={"Idempotency-Key": key()})
    assert created.status_code == 201, created.text
    published = api.post(
        f"/v1/packages/{package_id}/versions",
        content=archive,
        headers={"Content-Type": "application/zip", "Idempotency-Key": key()},
    )
    assert published.status_code == 201, published.text
    assert published.json()["digest"] == entry["digest"], published.json()
    version_path = f"/v1/packages/{package_id}/versions/{entry['version']}"
    approved = api.post(
        f"{version_path}/status",
        json={"status": "approved", "reason": "S-M2-04: WP-14 example, tests in examples/tests"},
        headers={"Idempotency-Key": key()},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"
    downloaded = api.get(f"{version_path}/archive")
    assert downloaded.status_code == 200, downloaded.text
    assert digest_of(downloaded.content) == entry["digest"]
    return {"package_id": package_id, "version": entry["version"], "digest": entry["digest"]}


def create_task(orch: JaneClient, doc: Mapping[str, Any]) -> str:
    """Validate and create a task exactly as written; returns its ETag."""
    api = orch.api("orchestrator")
    check = api.post("/v1/task-validations", json=dict(doc))
    assert check.status_code == 200, check.text
    assert check.json()["valid"], check.json()
    created = api.post("/v1/tasks", json=dict(doc), headers={"Idempotency-Key": key()})
    assert created.status_code == 201, created.text
    return str(created.headers["etag"])


def get_task(orch: JaneClient, task_id: str) -> tuple[dict[str, Any], str]:
    r = orch.api("orchestrator").get(f"/v1/tasks/{task_id}")
    assert r.status_code == 200, r.text
    return dict(r.json()), str(r.headers["etag"])


def replace_task(orch: JaneClient, doc: Mapping[str, Any], etag: str) -> str:
    r = orch.api("orchestrator").put(
        f"/v1/tasks/{doc['task_id']}", json=dict(doc), headers={"If-Match": etag}
    )
    assert r.status_code == 200, r.text
    return str(r.headers["etag"])


def summaries(orch: JaneClient) -> dict[str, dict[str, Any]]:
    r = orch.api("orchestrator").get("/v1/tasks", params={"source_id": SOURCE_ID})
    assert r.status_code == 200, r.text
    return {t["task_id"]: t for t in r.json()["items"]}


def runs_of(orch: JaneClient, task_id: str) -> list[dict[str, Any]]:
    r = orch.api("orchestrator").get("/v1/runs", params={"task_id": task_id, "limit": 100})
    assert r.status_code == 200, r.text
    return sorted(r.json()["items"], key=lambda run: run["created_at"])


def effective_pages(orch: JaneClient, task_id: str) -> tuple[int, str]:
    """``crawl.max_pages_per_run`` of the task's collect stage and the level it comes from."""
    r = orch.api("orchestrator").get(
        "/v1/limits/effective", params={"source_id": SOURCE_ID, "task_id": task_id, "stage_id": "collect"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    return int(body["limits"]["crawl"]["max_pages_per_run"]), str(
        body["provenance"]["crawl.max_pages_per_run"]
    )


def run_task(orch: JaneClient, task_id: str, reason: str) -> dict[str, Any]:
    run = wait_run(orch, start_run(orch, task_id, body={"reason": reason}), timeout_s=RUN_TIMEOUT_S)
    assert run["status"] == "succeeded", run
    return run


def cards(storage: JaneClient) -> dict[str, dict[str, Any]]:
    return {e["key"]["natural"]["sku"]: e for e in entities(storage, RESULTS, SOURCE_ID)}


def expected_card(sku: str, changes: Mapping[str, Mapping[str, str]] | None = None) -> dict[str, Any]:
    """Full card of the catalog extractor for the test site model (+ the changes made on the site)."""
    product = testsite_model.product_by_slug(sku)
    values = {"name": product.name, "price": product.price, "availability": product.availability}
    values.update((changes or {}).get(sku, {}))
    return {
        "sku": sku,
        "title": values["name"],
        "price": {"amount": float(values["price"]), "currency": "UAH"},
        "availability": AVAILABILITY[values["availability"]],
        "category": product.category,
        "url": f"{TESTSITE}/product/{sku}",
    }


def run_records(storage: JaneClient, state: Mapping[str, Any], run_id: str) -> list[dict[str, Any]]:
    """History entries of one entity written by one run."""
    return [
        h
        for h in history(storage, RESULTS, str(state["canonical_key"]))
        if (h["record"].get("provenance") or {}).get("run_id") == run_id
    ]


def raw_count(storage: JaneClient) -> int:
    return len(objects_by_source(storage, RAW, SOURCE_ID))


# ---------------------------------------------------------------------------- phases
def phase_a_catalog(shop: Shop) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    orch, storage = shop["orchestrator"], shop["storage"]
    run = run_task(orch, CATALOG, "S-M2-04 A: full catalog")
    assert run["trigger"] == "manual" and run["counters"]["materials"] == len(CATALOG_PAGES), run
    raw = objects_by_source(storage, RAW, SOURCE_ID)
    raw_paths = {httpx.URL(o["material"]["url"]).raw_path.decode() for o in raw}
    assert raw_paths == CATALOG_PAGES, sorted(raw_paths ^ CATALOG_PAGES)
    assert len(raw) == len(CATALOG_PAGES), len(raw)
    state = cards(storage)
    assert sorted(state) == PRODUCTS, sorted(state)
    for sku, entity in state.items():
        assert entity["fields"] == expected_card(sku), entity
        assert entity["version"] == 1, entity
        (record,) = run_records(storage, entity, run["run_id"])
        assert record["record"]["completeness"] == "full", record
        assert set(record["record"]["fields"]) == CARD_FIELDS, record
        assert record["record"]["provenance"]["package"]["package_id"] == CATALOG_EXTRACTOR, record
    note(
        "A catalog run",
        {"run": run["run_id"], "counters": run["counters"], "raw": len(raw), "cards": len(state)},
    )
    note("A card phone-alpha", state["phone-alpha"]["fields"])
    return run, state


def phase_b_cancel_catalog(shop: Shop, baseline: Mapping[str, Mapping[str, Any]]) -> str:
    """Price-check task as written; a catalog run cancelled mid-way changes neither it nor the cards."""
    orch, storage = shop["orchestrator"], shop["storage"]
    created_at = datetime.now(UTC)
    price_etag = create_task(orch, PRICE_DOC)
    before = summaries(orch)
    first_tick = ts(before[PRICE_CHECK]["next_run_at"])
    assert abs((first_tick - created_at).total_seconds() - PRICE_DOC["schedule"]["interval_seconds"]) < 120, (
        before
    )
    note(
        "B price-check task created", {"etag": price_etag, "next_run_at": before[PRICE_CHECK]["next_run_at"]}
    )

    api = orch.api("orchestrator")
    run_id = start_run(orch, CATALOG, body={"reason": "S-M2-04 B: catalog run to cancel"})
    deadline = time.monotonic() + RUN_TIMEOUT_S
    while True:
        run: dict[str, Any] = api.get(f"/v1/runs/{run_id}").json()
        assert run["status"] not in TERMINAL, f"the catalog run ended before it could be cancelled: {run}"
        if run["status"] == "running" and (run.get("counters") or {}).get("materials", 0) >= 1:
            break
        assert time.monotonic() < deadline, run
        time.sleep(0.2)
    cancel = api.post(f"/v1/runs/{run_id}/cancel", json={"reason": "S-M2-04: cancel the catalog run only"})
    assert cancel.status_code == 202, cancel.text
    assert cancel.json()["status"] == "cancelling", cancel.json()
    cancelled = wait_run(orch, run_id, timeout_s=RUN_TIMEOUT_S)
    assert cancelled["status"] == "cancelled", cancelled
    note(
        "B catalog run cancelled",
        {"run": run_id, "materials_at_cancel": run["counters"], "final_counters": cancelled.get("counters")},
    )

    doc, etag = get_task(orch, PRICE_CHECK)
    assert doc == PRICE_DOC and etag == price_etag, (doc, etag, price_etag)
    after = summaries(orch)
    assert after[PRICE_CHECK]["next_run_at"] == before[PRICE_CHECK]["next_run_at"], (before, after)
    assert after[CATALOG]["next_run_at"] == before[CATALOG]["next_run_at"], (before, after)
    assert runs_of(orch, PRICE_CHECK) == [], runs_of(orch, PRICE_CHECK)
    state = cards(storage)
    assert sorted(state) == PRODUCTS
    for sku, entity in state.items():
        assert entity["fields"] == baseline[sku]["fields"], (sku, entity)
    return price_etag


def phase_c_scheduled_price_check(
    shop: Shop, price_etag: str, catalog_run: Mapping[str, Any]
) -> tuple[str, dict[str, Any]]:
    orch, storage = shop["orchestrator"], shop["storage"]
    for slug, changes in SITE_CHANGES.items():
        product = shop.change_site(slug, changes)
        assert {k: product[k] for k in changes} == changes, product
        page = shop.product_page(slug)
        assert f'"price": "{product["price"]}"' in page, page[:2000]
    assert "<title>Phone Alpha 2027 | Jane Test Shop</title>" in shop.product_page("phone-alpha")
    note("C site changed through the price switch (stand-in)", SITE_CHANGES)

    catalog_doc, catalog_etag = get_task(orch, CATALOG)
    before = summaries(orch)
    before_cards = cards(storage)
    raw_before = raw_count(storage)

    start_at = (datetime.now(UTC) + timedelta(seconds=START_IN_S)).replace(microsecond=0)
    changed = copy.deepcopy(PRICE_DOC)
    changed["schedule"]["start_at"] = rfc3339(start_at)
    price_etag = replace_task(orch, changed, price_etag)
    after_put = summaries(orch)
    assert ts(after_put[PRICE_CHECK]["next_run_at"]) == start_at, after_put[PRICE_CHECK]
    assert get_task(orch, CATALOG) == (catalog_doc, catalog_etag) and catalog_doc == CATALOG_DOC
    assert after_put[CATALOG]["next_run_at"] == before[CATALOG]["next_run_at"], (before, after_put)
    note("C price-check schedule changed", {"start_at": rfc3339(start_at), "etag": price_etag})

    deadline = time.monotonic() + START_IN_S + SCHEDULE_TOLERANCE_S
    while not (scheduled := [r for r in runs_of(orch, PRICE_CHECK) if r["trigger"] == "schedule"]):
        assert time.monotonic() < deadline, f"no scheduled price-check run by {rfc3339(start_at)}"
        time.sleep(0.5)
    (fired,) = scheduled
    lag = (ts(fired["created_at"]) - start_at).total_seconds()
    assert -1.0 <= lag <= SCHEDULE_TOLERANCE_S, (fired, rfc3339(start_at))
    assert [r["trigger"] for r in runs_of(orch, PRICE_CHECK)] == ["schedule"]
    run = wait_run(orch, fired["run_id"], timeout_s=RUN_TIMEOUT_S)
    assert run["status"] == "succeeded", run
    assert run["counters"]["materials"] == len(CHECKED), run
    assert run.get("task_etag") in (None, price_etag), (run.get("task_etag"), price_etag)
    extracted = list_items(orch, run["run_id"], "extract-price")
    assert sorted(i["result_status"] for i in extracted) == ["success"] * len(CHECKED), extracted
    assert len(list_items(orch, run["run_id"], "store-price")) == len(CHECKED)
    assert raw_count(storage) == raw_before, "the price check has no RAW stage"
    nxt = summaries(orch)[PRICE_CHECK]["next_run_at"]
    assert ts(nxt) == start_at + timedelta(seconds=PRICE_DOC["schedule"]["interval_seconds"]), nxt
    note(
        "C scheduled price-check run",
        {
            "run": run["run_id"],
            "start_at": rfc3339(start_at),
            "created_at": fired["created_at"],
            "lag_s": round(lag, 3),
            "counters": run["counters"],
            "next_run_at": nxt,
        },
    )

    state = cards(storage)
    assert sorted(state) == PRODUCTS
    for sku in CHECKED:
        entity, old = state[sku], before_cards[sku]
        (entry,) = run_records(storage, entity, run["run_id"])
        record = entry["record"]
        assert record["completeness"] == "partial" and set(record["fields"]) == PRICE_FIELDS, entry
        assert record["provenance"]["package"]["package_id"] == PRICE_EXTRACTOR, entry
        assert {"price", "availability"} <= set(entry["applied_fields"]), entry
        assert "title" not in entry["applied_fields"] and entry["stale_fields"] == [], entry
        new = expected_card(sku, SITE_CHANGES)
        assert entity["fields"]["price"] == new["price"], (sku, entity)
        assert entity["fields"]["availability"] == new["availability"], (sku, entity)
        for name in CARD_FIELDS - {"price", "availability"}:
            assert entity["fields"][name] == old["fields"][name], (sku, name, entity, old)
        if orders := entity.get("field_orders"):
            assert orders["price"]["observation_id"] == record["observation"]["observation_id"], orders
            assert orders["title"]["observation_id"] != record["observation"]["observation_id"], orders
        if sku in SITE_CHANGES:
            assert entity["version"] > old["version"], (entity, old)
    assert state["phone-alpha"]["fields"]["title"] == "Phone Alpha", "the price check must not rename"
    for sku in sorted(set(PRODUCTS) - set(CHECKED)):
        assert state[sku] == before_cards[sku], (sku, state[sku], before_cards[sku])
    alpha_history = history(storage, RESULTS, str(state["phone-alpha"]["canonical_key"]))
    alpha = state["phone-alpha"]
    note("C card phone-alpha", {"fields": alpha["fields"], "version": alpha["version"]})
    orders = alpha.get("field_orders") or {}
    note(
        "C field orders phone-alpha",
        {name: (orders.get(name) or {}).get("observation_id") for name in ("price", "title")},
    )
    note(
        "C history phone-alpha",
        [
            {
                "run": h["record"]["provenance"].get("run_id"),
                "completeness": h["record"].get("completeness"),
                "fields": sorted(h["record"]["fields"]),
                "applied": h["applied_fields"],
            }
            for h in alpha_history
        ],
    )
    assert any(h["record"]["provenance"].get("run_id") == catalog_run["run_id"] for h in alpha_history), (
        alpha_history
    )
    return price_etag, run


def phase_d_change_price_limit(shop: Shop, price_etag: str) -> None:
    orch, storage = shop["orchestrator"], shop["storage"]
    catalog_doc, catalog_etag = get_task(orch, CATALOG)
    assert effective_pages(orch, CATALOG) == (CATALOG_DOC["limits"]["crawl"]["max_pages_per_run"], "task")
    doc, _ = get_task(orch, PRICE_CHECK)
    doc["limits"]["crawl"]["max_pages_per_run"] = 2
    replace_task(orch, doc, price_etag)
    assert effective_pages(orch, PRICE_CHECK) == (2, "task")
    assert effective_pages(orch, CATALOG) == (CATALOG_DOC["limits"]["crawl"]["max_pages_per_run"], "task")
    assert get_task(orch, CATALOG) == (catalog_doc, catalog_etag)

    limited = run_task(orch, PRICE_CHECK, "S-M2-04 D: price check with 2 pages")
    assert limited["counters"]["materials"] == 2, limited
    state = cards(storage)
    touched = sorted(sku for sku in CHECKED if run_records(storage, state[sku], limited["run_id"]))
    assert len(touched) == 2, touched
    note("D price check limited to 2 pages", {"run": limited["run_id"], "counters": limited["counters"]})

    raw_before = raw_count(storage)
    catalog = run_task(orch, CATALOG, "S-M2-04 D: full catalog after the price-check change")
    assert catalog["counters"]["materials"] == len(CATALOG_PAGES), catalog
    assert raw_count(storage) == raw_before + len(CATALOG_PAGES)
    state = cards(storage)
    assert sorted(state) == PRODUCTS
    for sku, entity in state.items():
        assert entity["fields"] == expected_card(sku, SITE_CHANGES), entity
    assert get_task(orch, CATALOG) == (catalog_doc, catalog_etag)
    note(
        "D catalog run after the change",
        {
            "run": catalog["run_id"],
            "counters": catalog["counters"],
            "phone-alpha": state["phone-alpha"]["fields"],
            "phone-beta price": state["phone-beta"]["fields"]["price"],
        },
    )


# ---------------------------------------------------------------------------- S-M2-04
def test_s_m2_04_catalog_and_scheduled_price_check_are_separate_tasks(shop: Shop) -> None:
    registry, orch = shop["registry"], shop["orchestrator"]
    published = [publish(registry, ref) for ref in document_refs()]
    note("registry: published and approved", published)
    put_connections(orch)
    source = orch.api("orchestrator").post("/v1/sources", json=SOURCE_DOC, headers={"Idempotency-Key": key()})
    assert source.status_code == 201, source.text
    catalog_etag = create_task(orch, CATALOG_DOC)
    assert get_task(orch, CATALOG) == (CATALOG_DOC, catalog_etag)

    catalog_run, baseline = phase_a_catalog(shop)
    price_etag = phase_b_cancel_catalog(shop, baseline)
    price_etag, _ = phase_c_scheduled_price_check(shop, price_etag, catalog_run)
    phase_d_change_price_limit(shop, price_etag)
    assert [r["trigger"] for r in runs_of(orch, CATALOG)] == ["manual"] * 3, runs_of(orch, CATALOG)
    assert [r["trigger"] for r in runs_of(orch, PRICE_CHECK)] == ["schedule", "manual"], runs_of(
        orch, PRICE_CHECK
    )
    note(
        "runs",
        {task: [(r["trigger"], r["status"]) for r in runs_of(orch, task)] for task in (CATALOG, PRICE_CHECK)},
    )
