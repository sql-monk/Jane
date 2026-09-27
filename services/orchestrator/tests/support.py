"""Test support: PostgreSQL for the orchestrator's own DB and **neighbour fakes built on the contracts**.

The orchestrator itself is never mocked. Its neighbours (collector.v1, handler.v1, storage.v1, registry.v1)
are small HTTP servers whose every request and response is validated against the neighbour's OpenAPI
contract (``violations`` must stay empty), with the delivery semantics the contracts prescribe:
collector pull with cursor/ack and a bounded unacked buffer, handler idempotency by ``Idempotency-Key``
(= ``delivery_key``) with ``duplicate: true`` replays, storage objects for reprocessing.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from collections import Counter, defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psycopg
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from jane_kit.contracts import ContractViolation, OpenAPISpec, contracts_dir
from jane_kit.devstack import load_stack

CONTRACTS = contracts_dir(Path(__file__).parent)
assert CONTRACTS is not None, "contracts/ not found"
SPECS = {
    name: OpenAPISpec.load(CONTRACTS / "openapi" / f"{name}.v1.yaml")
    for name in ("collector", "handler", "storage", "registry", "orchestrator")
}

PG_IMAGE = os.environ.get("JANE_ORCHESTRATOR_TEST_PG_IMAGE", "postgres:18")


# ====================================================================== PostgreSQL
def _docker_postgres() -> tuple[str, Callable[[], None]] | None:
    docker = shutil.which("docker")
    if docker is None:
        return None
    name = f"jane-wp09-test-pg-{uuid.uuid4().hex[:8]}"
    password = uuid.uuid4().hex
    try:
        subprocess.run(
            [
                docker,
                "run",
                "-d",
                "--rm",
                "--name",
                name,
                "-e",
                f"POSTGRES_PASSWORD={password}",
                "-p",
                "127.0.0.1::5432",
                PG_IMAGE,
            ],
            check=True,
            capture_output=True,
            timeout=300,
        )
        port_out = subprocess.run(
            [docker, "port", name, "5432/tcp"], check=True, capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    port = port_out.splitlines()[0].rsplit(":", 1)[1]
    dsn = f"postgresql://postgres:{password}@127.0.0.1:{port}/postgres"

    def stop() -> None:
        subprocess.run([docker, "rm", "-f", name], capture_output=True, check=False, timeout=60)

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(dsn, connect_timeout=2) as conn:
                conn.execute("SELECT 1")
            return dsn, stop
        except psycopg.OperationalError:
            time.sleep(0.5)
    stop()
    return None


def admin_dsn() -> tuple[str, Callable[[], None]] | None:
    """Admin DSN: ``JANE_ORCHESTRATOR_TEST_DSN`` → dev stack of this checkout (``just up``) → own container."""
    if env := os.environ.get("JANE_ORCHESTRATOR_TEST_DSN"):
        return env, lambda: None
    stack = load_stack()
    if stack is not None and "postgres" in stack.services:
        return str(stack.get("postgres", "dsn")), lambda: None
    return _docker_postgres()


def create_database(admin: str) -> tuple[str, Callable[[], None]]:
    name = f"orch_test_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(admin, autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{name}"')
    base, _, _ = admin.rpartition("/")
    dsn = f"{base}/{name}"

    def drop() -> None:
        with psycopg.connect(admin, autocommit=True) as conn:
            conn.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')

    return dsn, drop


# ====================================================================== servers
class ServerThread:
    def __init__(self, app: Starlette) -> None:
        self.server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning", lifespan="off")
        )
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def start(self) -> str:
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("fake server did not start")
            time.sleep(0.01)
        port = self.server.servers[0].sockets[0].getsockname()[1]
        return f"http://127.0.0.1:{port}"

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(5)


def problem(status: int, code: str, detail: str = "", retryable: bool = False) -> JSONResponse:
    return JSONResponse(
        {
            "type": f"urn:jane:problem:{code}",
            "title": code,
            "status": status,
            "code": code,
            "retryable": retryable,
            "detail": detail,
        },
        status_code=status,
        media_type="application/problem+json",
    )


class ContractFake:
    """Base: validates requests and responses against ``spec``; records violations."""

    api = "handler"

    def __init__(self) -> None:
        self.spec = SPECS[self.api]
        self.violations: list[str] = []
        self.lock = threading.Lock()
        self.requests: list[tuple[str, str, Any]] = []
        self.connections: dict[str, Any] = {}

    async def _body(self, request: Request) -> Any:
        raw = await request.body()
        body = json.loads(raw) if raw else None
        with self.lock:
            self.requests.append((request.method, request.url.path, body))
        if body is not None:
            try:
                self.spec.validate_request(request.method, request.url.path, body)
            except ContractViolation as exc:
                self.violations.append(f"request {request.method} {request.url.path}: {exc}")
        return body

    def respond(
        self, request: Request, status: int, body: Any, headers: dict[str, str] | None = None
    ) -> JSONResponse:
        try:
            self.spec.validate_response(request.method, request.url.path, status, body, "application/json")
        except ContractViolation as exc:
            self.violations.append(f"response {request.method} {request.url.path} {status}: {exc}")
        return JSONResponse(body, status_code=status, headers=headers)

    # --- shared connections endpoints (common.yaml Connection*)
    async def put_connection(self, request: Request) -> Response:
        body = await self._body(request)
        cid = request.path_params["connection_id"]
        created = cid not in self.connections
        self.connections[cid] = body
        return self.respond(request, 201 if created else 200, body, {"ETag": '"1"'})

    async def delete_connection(self, request: Request) -> Response:
        await self._body(request)
        self.connections.pop(request.path_params["connection_id"], None)
        return Response(status_code=204)

    def connection_routes(self) -> list[Route]:
        return [
            Route("/v1/connections/{connection_id}", self.put_connection, methods=["PUT"]),
            Route("/v1/connections/{connection_id}", self.delete_connection, methods=["DELETE"]),
        ]

    async def health(self, request: Request) -> Response:
        return JSONResponse({"status": "ok"})


# ====================================================================== collector
@dataclass
class Page:
    url: str
    html: str
    section: str | None = None
    media_type: str = "text/html"


def default_site(n_products: int = 5, n_unknown: int = 1) -> list[Page]:
    pages = [
        Page(
            f"https://shop.example.test/product/a-{i}",
            f"<html><h1>A-{i}</h1><b class=price>{100 + i}</b></html>",
            "products",
        )
        for i in range(n_products)
    ]
    pages += [
        Page(f"https://shop.example.test/gift-cards/{i}", "<html>gift</html>") for i in range(n_unknown)
    ]
    return pages


@dataclass
class Collection:
    cid: str
    request: dict[str, Any]
    materials: list[dict[str, Any]]
    max_unacked: int
    acked: int = 0
    status: str = "running"
    max_unacked_seen: int = 0
    paused: bool = False
    pulls: int = 0
    redelivered: int = 0
    delivered_upto: int = 0


class FakeCollector(ContractFake):
    api = "collector"
    DEFAULT_UNACKED = 500

    def __init__(self, site: list[Page] | None = None) -> None:
        super().__init__()
        self.site = site or default_site()
        self.collections: dict[str, Collection] = {}
        self.by_key: dict[str, str] = {}
        self.cancelled: list[str] = []

    def material(self, cid: str, i: int, page: Page, source_id: str | None) -> dict[str, Any]:
        digest = hashlib.sha256(page.html.encode()).hexdigest()
        m: dict[str, Any] = {
            "material_id": "web:" + hashlib.sha256(page.url.encode()).hexdigest()[:32],
            "observation_id": f"obs_{cid}_{i:05d}",
            "source": {"kind": "web", **({"source_id": source_id} if source_id else {})},
            "locator": {"url": page.url, "canonical_url": page.url},
            "fetched_at": "2026-09-27T10:00:05Z",
            "format": {"media_type": page.media_type, "content_kind": "page"},
            "revision": {"content_sha256": digest},
            "content": {
                "kind": "inline",
                "media_type": page.media_type,
                "encoding": "utf-8",
                "data": page.html,
                "sha256": digest,
            },
            "discovery": {
                "strategy": "seed_list",
                "depth": 0,
                **({"section": page.section} if page.section else {}),
            },
            "collector": {"name": "fake-collector", "version": "0.0.1", "collection_id": cid},
        }
        return m

    async def start(self, request: Request) -> Response:
        body = await self._body(request)
        key = request.headers.get("idempotency-key")
        if not key:
            return problem(422, "validation_failed", "Idempotency-Key required")
        with self.lock:
            if key in self.by_key:
                col = self.collections[self.by_key[key]]
                return self.respond(
                    request,
                    202,
                    self._job(col),
                    {"Location": f"/v1/jobs/{col.cid}", "Idempotency-Replayed": "true"},
                )
            cid = f"job_{uuid.uuid4().hex[:20]}"
            pages = self.site
            if body.get("urls"):
                wanted = set(body["urls"])
                pages = [p for p in self.site if p.url in wanted]
            unacked = ((body.get("limits") or {}).get("queue") or {}).get(
                "max_unacked_materials", self.DEFAULT_UNACKED
            )
            col = Collection(
                cid,
                body,
                [self.material(cid, i, p, body.get("source_id")) for i, p in enumerate(pages)],
                unacked,
            )
            self.collections[cid] = col
            self.by_key[key] = cid
        return self.respond(request, 202, self._job(col), {"Location": f"/v1/jobs/{cid}"})

    def _job(self, col: Collection) -> dict[str, Any]:
        return {
            "job_id": col.cid,
            "kind": "collection",
            "status": col.status,
            "created_at": "2026-09-27T10:00:00Z",
            "links": {"self": f"/v1/jobs/{col.cid}"},
        }

    async def materials(self, request: Request) -> Response:
        await self._body(request)
        col = self.collections.get(request.path_params["collection_id"])
        if col is None:
            return problem(404, "not_found")
        q = request.query_params
        with self.lock:
            col.pulls += 1
            if "after" in q:
                idx = int(q["after"].split("_")[1]) + 1
                col.acked = max(col.acked, idx)
            limit = int(q.get("limit", 50))
            # the collector emits only up to acked + max_unacked (backpressure pauses crawling)
            emitted = min(len(col.materials), col.acked + col.max_unacked)
            col.paused = emitted < len(col.materials)
            if col.status == "cancelled":
                emitted = col.acked
            items = col.materials[col.acked : min(emitted, col.acked + limit)]
            if col.acked < col.delivered_upto:
                col.redelivered += min(len(items), col.delivered_upto - col.acked)
            col.delivered_upto = max(col.delivered_upto, col.acked + len(items))
            col.max_unacked_seen = max(col.max_unacked_seen, col.delivered_upto - col.acked)
            end = col.acked + len(items) >= len(col.materials) or col.status == "cancelled"
            if end and col.status == "running":
                col.status = "succeeded"
            last = col.acked + len(items) - 1
        page = {
            "items": items,
            "next_cursor": f"c_{last:010d}" if items else None,
            "end_of_stream": end,
            "collection_status": col.status,
        }
        return self.respond(request, 200, page)

    async def job(self, request: Request) -> Response:
        col = self.collections.get(request.path_params["job_id"])
        if col is None:
            return problem(404, "not_found")
        return self.respond(request, 200, self._job(col))

    async def cancel(self, request: Request) -> Response:
        await self._body(request)
        col = self.collections.get(request.path_params["job_id"])
        if col is None:
            return problem(404, "not_found")
        with self.lock:
            self.cancelled.append(col.cid)
            if col.status in {"succeeded", "failed", "cancelled"}:
                return self.respond(request, 200, self._job(col))
            col.status = "cancelled"
        return self.respond(request, 202, self._job(col))

    def app(self) -> Starlette:
        return Starlette(
            routes=[
                Route("/v1/health", self.health),
                Route("/v1/collections", self.start, methods=["POST"]),
                Route("/v1/collections/{collection_id}/materials", self.materials),
                Route("/v1/jobs/{job_id}", self.job),
                Route("/v1/jobs/{job_id}/cancel", self.cancel, methods=["POST"]),
                *self.connection_routes(),
            ]
        )


# ====================================================================== handlers
Behavior = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def _now() -> str:
    return "2026-09-27T10:00:06Z"


def _input_refs(body: dict[str, Any]) -> list[dict[str, Any]]:
    refs = []
    for inp in body["inputs"]:
        ref: dict[str, Any] = {"kind": inp["kind"]}
        mat = inp.get("material")
        if mat:
            ref["material_id"] = mat["material_id"]
            ref["observation_id"] = mat["observation_id"]
        if inp.get("from_invocation_id"):
            ref["from_invocation_id"] = inp["from_invocation_id"]
        refs.append(ref)
    return refs


def base_result(body: dict[str, Any], status: str, kind: str) -> dict[str, Any]:
    h = dict(body["handler"])
    h.setdefault(
        "digest", "sha256:" + hashlib.sha256(f"{h['package_id']}@{h['version']}".encode()).hexdigest()
    )
    return {
        "invocation_id": "inv_" + uuid.uuid4().hex[:20],
        "handler": h,
        "handler_kind": kind,
        "status": status,
        "inputs": _input_refs(body),
        "delivery_key": body["delivery"]["delivery_key"],
        "test_mode": bool((body.get("context") or {}).get("test_mode")),
        "started_at": _now(),
        "finished_at": _now(),
    }


def product_extractor(body: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    mat = next(i["material"] for i in body["inputs"] if i["kind"] == "material")
    url = mat["locator"]["url"]
    if "/product/" not in url:
        r = base_result(body, "unrecognized", "extractor")
        r["unrecognized"] = {
            "partial": False,
            "reason": "not a product page",
            "signature": "no-product-markup",
        }
        return r
    sku = url.rsplit("/", 1)[1].upper()
    r = base_result(body, "success", "extractor")
    r["output"] = {
        "entities": [
            {
                "entity_type": "product",
                "key": {"scope": mat["source"].get("source_id", "shop-example"), "natural": {"sku": sku}},
                "fields": {
                    "sku": sku,
                    "title": f"Product {sku}",
                    "price": {"amount": 100, "currency": "UAH"},
                },
                "completeness": "full",
                "observation": {"observation_id": mat["observation_id"], "observed_at": mat["fetched_at"]},
            }
        ]
    }
    return r


def price_extractor(body: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    r = product_extractor(body, _)
    for e in (r.get("output") or {}).get("entities", []):
        e["fields"] = {"price": e["fields"]["price"]}
        e["completeness"] = "partial"
    return r


def llm_triage(body: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
    r = base_result(body, "success", "llm")
    r["output"] = {"data": {"page_type": "unknown", "suggestion": "gift card page"}}
    r["usage"] = {
        "llm": {
            "provider": "fake",
            "model": "fake-1",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost": {"amount": 0.01, "currency": "USD"},
        }
    }
    return r


class FakeHandler(ContractFake):
    """handler.v1 executor. ``behaviors``: package_id → function(body, state) → HandlerResult.

    Idempotency per contract: same key → stored result with ``duplicate: true`` (no second effect); key in
    flight → 409 ``idempotency_in_progress`` (retryable). ``effects`` counts real executions per key.
    """

    api = "handler"

    def __init__(self, behaviors: dict[str, Behavior], *, kind: str = "extractor") -> None:
        super().__init__()
        self.behaviors = behaviors
        self.kind = kind
        self.results: dict[str, dict[str, Any]] = {}
        self.in_flight: set[str] = set()
        self.effects: Counter[str] = Counter()
        self.calls: Counter[str] = Counter()
        self.duplicates: Counter[str] = Counter()
        self.key_mismatch: list[str] = []
        self.delay_s = 0.0
        self.hang_after_effect: threading.Event | None = None
        """If set: the first execution records its effect, then never answers until the event is set."""
        self.hung = threading.Event()
        self.fail_retryable: Counter[str] = Counter()
        """package_id → how many more calls should fail with a retryable failure."""
        self.concurrent = 0
        self.max_concurrent = 0
        self.stored_objects: dict[str, dict[str, Any]] = {}
        self.object_order: list[str] = []

    async def invoke(self, request: Request) -> Response:
        body = await self._body(request)
        key = request.headers.get("idempotency-key", "")
        with self.lock:
            self.calls[key] += 1
            if key != body["delivery"]["delivery_key"]:
                self.key_mismatch.append(key)
            if key in self.results:
                self.duplicates[key] += 1
                stored = {**self.results[key], "duplicate": True}
                return self.respond(request, 200, stored, {"Idempotency-Replayed": "true"})
            if key in self.in_flight:
                return problem(409, "idempotency_in_progress", retryable=True)
            self.in_flight.add(key)
            self.concurrent += 1
            self.max_concurrent = max(self.max_concurrent, self.concurrent)
        try:
            if self.delay_s:
                await asyncio.sleep(self.delay_s)
            pkg = body["handler"]["package_id"]
            with self.lock:
                if self.fail_retryable[pkg] > 0:
                    self.fail_retryable[pkg] -= 1
                    r = base_result(body, "failed", self.kind)
                    r["failure"] = {"kind": "connection_error", "message": "temporary", "retryable": True}
                    return self.respond(request, 200, r)
            behavior = self.behaviors.get(pkg) or self.behaviors["*"]
            result = behavior(body, {})
            with self.lock:
                self.effects[key] += 1
                self.results[key] = result
            hang = self.hang_after_effect
            if hang is not None and not self.hung.is_set():
                self.hung.set()
                deadline = time.monotonic() + 60
                while not hang.is_set() and time.monotonic() < deadline:
                    await asyncio.sleep(0.05)
            return self.respond(request, 200, result)
        finally:
            with self.lock:
                self.in_flight.discard(key)
                self.concurrent -= 1

    def app(self) -> Starlette:
        return Starlette(
            routes=[
                Route("/v1/health", self.health),
                Route("/v1/invocations", self.invoke, methods=["POST"]),
                *self.connection_routes(),
            ]
        )


class FakeStorage(FakeHandler):
    """Storage executor: handler.v1 writes (RAW objects, entities) + storage.v1 reads for reprocessing."""

    def __init__(self) -> None:
        super().__init__({"*": self.write}, kind="storage")
        self.read_spec = SPECS["storage"]

    def write(self, body: dict[str, Any], _: dict[str, Any]) -> dict[str, Any]:
        target = (body.get("connections") or {}).get("target", "default")
        adapter = "filesystem" if "files" in body["handler"]["package_id"] else "postgresql"
        writes = []
        test_mode = bool((body.get("context") or {}).get("test_mode"))
        for inp in body["inputs"]:
            if inp["kind"] == "material":
                mat = inp["material"]
                oid = "obj_" + uuid.uuid4().hex[:20]
                ref = {
                    "object_id": oid,
                    "adapter": adapter,
                    "connection_id": target,
                    "media_type": mat["format"]["media_type"],
                }
                if not test_mode:
                    with self.lock:
                        self.stored_objects[oid] = {"object": ref, "material": mat, "stored_at": _now()}
                        self.object_order.append(oid)
                writes.append(
                    {
                        "status": "simulated" if test_mode else "written",
                        "target": {"adapter": adapter, "connection_id": target},
                        "object": ref,
                    }
                )
            elif inp["kind"] == "entities":
                for e in inp.get("entities") or []:
                    ck = f"{e['key']['scope']}|{json.dumps(e['key']['natural'], sort_keys=True, separators=(',', ':'))}"
                    writes.append(
                        {
                            "status": "simulated" if test_mode else "written",
                            "target": {"adapter": adapter, "connection_id": target},
                            "entity": {"entity_type": e["entity_type"], "canonical_key": ck, "version": 1},
                        }
                    )
        r = base_result(body, "success", "storage")
        r["output"] = {"writes": writes}
        return r

    def respond_read(self, request: Request, status: int, body: Any) -> JSONResponse:
        try:
            self.read_spec.validate_response(
                request.method, request.url.path, status, body, "application/json"
            )
        except ContractViolation as exc:
            self.violations.append(f"storage response {request.url.path}: {exc}")
        return JSONResponse(body, status_code=status)

    async def list_objects(self, request: Request) -> Response:
        q = request.query_params
        if "connection_id" not in q:
            self.violations.append("storage GET /v1/objects without connection_id")
        start = int(q.get("cursor", "0"))
        limit = int(q.get("limit", "50"))
        with self.lock:
            ids = self.object_order[start : start + limit]
            more = start + limit < len(self.object_order)
        items = []
        for oid in ids:
            o = self.stored_objects[oid]
            m = o["material"]
            items.append(
                {
                    "object": o["object"],
                    "stored_at": o["stored_at"],
                    "material": {
                        "material_id": m["material_id"],
                        "observation_id": m["observation_id"],
                        "url": m["locator"]["url"],
                    },
                }
            )
        return self.respond_read(
            request, 200, {"items": items, "next_cursor": str(start + limit) if more else None}
        )

    async def get_object(self, request: Request) -> Response:
        o = self.stored_objects.get(request.path_params["object_id"])
        if o is None:
            return problem(404, "not_found")
        return self.respond_read(request, 200, o)

    def app(self) -> Starlette:
        return Starlette(
            routes=[
                Route("/v1/health", self.health),
                Route("/v1/invocations", self.invoke, methods=["POST"]),
                Route("/v1/objects", self.list_objects),
                Route("/v1/objects/{object_id}", self.get_object),
                *self.connection_routes(),
            ]
        )


# ====================================================================== registry
class FakeRegistry(ContractFake):
    api = "registry"

    def __init__(self) -> None:
        super().__init__()
        self.packages: dict[str, dict[str, Any]] = {}
        self.versions: dict[tuple[str, str], dict[str, Any]] = {}

    def add(
        self,
        package_id: str,
        version: str,
        *,
        status: str = "approved",
        test_status: str = "passed",
        auto: bool = True,
        kind: str = "extractor",
    ) -> None:
        self.packages[package_id] = {
            "package_id": package_id,
            "kind": kind,
            "title": package_id,
            "auto_changes_allowed": auto,
            "deprecated": False,
            "created_at": "2026-09-01T00:00:00Z",
            "updated_at": "2026-09-01T00:00:00Z",
        }
        digest = "sha256:" + hashlib.sha256(f"{package_id}@{version}".encode()).hexdigest()
        self.versions[(package_id, version)] = {
            "package_id": package_id,
            "version": version,
            "digest": digest,
            "status": status,
            "test_status": test_status,
            "created_at": "2026-09-01T00:00:00Z",
        }

    async def package(self, request: Request) -> Response:
        p = self.packages.get(request.path_params["package_id"])
        return self.respond(request, 200, p) if p else problem(404, "not_found")

    async def version(self, request: Request) -> Response:
        v = self.versions.get((request.path_params["package_id"], request.path_params["version"]))
        return self.respond(request, 200, v) if v else problem(404, "not_found")

    def app(self) -> Starlette:
        return Starlette(
            routes=[
                Route("/v1/health", self.health),
                Route("/v1/packages/{package_id}", self.package),
                Route("/v1/packages/{package_id}/versions/{version}", self.version),
            ]
        )


# ====================================================================== neighbourhood
@dataclass
class Neighbours:
    collector: FakeCollector
    runtime: FakeHandler
    storage: FakeStorage
    llm: FakeHandler
    registry: FakeRegistry
    servers: list[ServerThread] = field(default_factory=list)
    urls: dict[str, str] = field(default_factory=dict)

    def executors(self) -> list[dict[str, Any]]:
        return [
            {
                "executor": "web-collector",
                "role": "collector",
                "base_url": self.urls["collector"],
                "capabilities": {"collector": "web"},
            },
            {
                "executor": "handler-runtime",
                "role": "handler",
                "base_url": self.urls["runtime"],
                "capabilities": {"handler_kinds": ["extractor", "transform"], "default": True},
            },
            {
                "executor": "storage",
                "role": "handler",
                "base_url": self.urls["storage"],
                "capabilities": {"packages": ["jane.storage-*"], "handler_kinds": ["storage"]},
            },
            {
                "executor": "storage-read",
                "role": "storage_read",
                "base_url": self.urls["storage"],
                "sync_connections": False,
            },
            {
                "executor": "llm",
                "role": "llm",
                "base_url": self.urls["llm"],
                "capabilities": {"packages": ["jane.llm-*"], "handler_kinds": ["llm"]},
            },
            {"executor": "registry", "role": "registry", "base_url": self.urls["registry"]},
        ]

    def all_violations(self) -> list[str]:
        return [
            *self.collector.violations,
            *self.runtime.violations,
            *self.storage.violations,
            *self.llm.violations,
            *self.registry.violations,
        ]

    def stop(self) -> None:
        for fake in (self.runtime, self.storage, self.llm):
            if fake.hang_after_effect is not None:
                fake.hang_after_effect.set()
        for s in self.servers:
            s.stop()


def start_neighbours(site: list[Page] | None = None) -> Neighbours:
    n = Neighbours(
        collector=FakeCollector(site),
        runtime=FakeHandler({"*": product_extractor, "shop-example.price-extractor": price_extractor}),
        storage=FakeStorage(),
        llm=FakeHandler({"*": llm_triage}, kind="llm"),
        registry=FakeRegistry(),
    )
    for name, fake in (
        ("collector", n.collector),
        ("runtime", n.runtime),
        ("storage", n.storage),
        ("llm", n.llm),
        ("registry", n.registry),
    ):
        server = ServerThread(fake.app())
        n.urls[name] = server.start()
        n.servers.append(server)
    return n


# ====================================================================== configs
def source_doc(
    source_id: str = "shop-example", *, forward_unknown: bool = False, **extra: Any
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "kind": "web",
        "title": "Shop Example",
        "locator": {"url": "https://shop.example.test/"},
        "collector_rules": {"package_id": "shop-example.web-rules", "version": "1.0.0"},
        "forward_unknown_to_llm": forward_unknown,
        **extra,
    }


def catalog_task(
    task_id: str = "shop-catalog", source_id: str = "shop-example", **extra: Any
) -> dict[str, Any]:
    """Web → RAW to files ‖ extraction with a local package → results to PostgreSQL (M1 shape)."""
    return {
        "task_id": task_id,
        "title": "Full catalog",
        "input": {"source_id": source_id},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web"}},
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
                "connections": {"target": "raw-files"},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "extract-products",
                "kind": "handler",
                "handler": {"package_id": "shop-example.product-extractor", "version": "1.2.0"},
                "inputs": [
                    {
                        "from": "collect",
                        "when": {"field": "material.format.media_type", "op": "eq", "value": "text/html"},
                    }
                ],
                "bindings": [{"sections": ["products"]}],
            },
            {
                "stage_id": "store-products",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
                "connections": {"target": "results-pg"},
                "inputs": [
                    {
                        "from": "extract-products",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
            },
            {
                "stage_id": "unknown-pages",
                "kind": "handler",
                "handler": {"package_id": "jane.llm-page-triage", "version": "1.0.0"},
                "inputs": [{"from": "collect", "select": "unmatched_materials"}],
            },
        ],
        **extra,
    }


def price_task(
    task_id: str = "shop-price-check", source_id: str = "shop-example", urls: list[str] | None = None
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "title": "Price check",
        "input": {
            "source_id": source_id,
            "urls": urls
            or ["https://shop.example.test/product/a-0", "https://shop.example.test/product/a-1"],
        },
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web"}},
            {
                "stage_id": "extract-price",
                "kind": "handler",
                "handler": {"package_id": "shop-example.price-extractor", "version": "1.0.0"},
                "inputs": [{"from": "collect"}],
                "bindings": [{"sections": ["products"]}],
            },
            {
                "stage_id": "store-price",
                "kind": "handler",
                "handler": {"package_id": "jane.storage-postgresql", "version": "1.0.0"},
                "connections": {"target": "results-pg"},
                "inputs": [
                    {
                        "from": "extract-price",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
            },
        ],
        "schedule": {"type": "interval", "interval_seconds": 86400, "overlap": "skip"},
    }


def wait_until(predicate: Callable[[], Any], timeout: float = 30.0, interval: float = 0.05) -> Any:
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    raise AssertionError(f"condition not met within {timeout}s (last={last!r})")


def items_by_stage(db_dsn: str, run_id: str) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with psycopg.connect(db_dsn, row_factory=psycopg.rows.dict_row) as conn:
        for r in conn.execute("SELECT * FROM items WHERE run_id = %s ORDER BY seq", (run_id,)).fetchall():
            out[r["stage_id"]].append(r)
    return out


def iter_lines(path: Path) -> Iterator[str]:
    yield from path.read_text(encoding="utf-8").splitlines()
