"""Contract-bound fakes of the assistant's neighbours and the scenario world."""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from fastapi.testclient import TestClient

from jane_assistant.app import Dependencies, build_app
from jane_assistant.search import Candidate
from jane_assistant.settings import Settings
from jane_kit.contracts import ContractClient, OpenAPISpec

from .base import load_spec
from .llm import FakeLlm
from .registry import FakeRegistry
from .services import FakeCollector, FakeHandler, FakeOrchestrator, FakeStorage

__all__ = ["FakeSearch", "World", "world"]


class FakeSearch:
    """In-process search provider (the real ones are ``static`` and ``http_json``)."""

    def __init__(self, results: dict[str, list[Candidate]]) -> None:
        self.results = results
        self.queries: list[str] = []

    async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
        self.queries.append(query)
        return self.results.get(query, [])[:limit]


DEFAULT_SEARCH = {
    "Shop Example kettles": [
        Candidate("Shop Example", url="https://shop.example.test/", confidence=0.62),
        Candidate("Shop Example Outlet", url="https://outlet.shop.example.test/", confidence=0.35),
    ],
    "Shop Example store": [Candidate("Shop Example", url="https://shop.example.test/", confidence=0.95)],
}


@dataclass
class World:
    contracts: Path
    llm: FakeLlm
    registry: FakeRegistry
    collector: FakeCollector
    tg_collector: FakeCollector
    handler: FakeHandler
    orchestrator: FakeOrchestrator
    storage: FakeStorage
    search: FakeSearch
    client: TestClient
    api: ContractClient
    spec: OpenAPISpec
    extra: dict[str, Any] = field(default_factory=dict)

    def fakes(self) -> list[Any]:
        return [
            self.llm,
            self.registry,
            self.collector,
            self.tg_collector,
            self.handler,
            self.orchestrator,
            self.storage,
        ]

    def instance(self, settings: Settings) -> TestClient:
        """Another assistant instance wired to the same neighbour fakes (use as a context manager)."""
        deps = Dependencies(transports=self.extra["transports"], search=self.search)
        return TestClient(build_app(settings, deps))

    def violations(self) -> list[str]:
        return [v for f in self.fakes() for v in f.app.violations]

    def wait(self, job_id: str, timeout_s: float = 20.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_s
        while True:
            job: dict[str, Any] = self.api.get(f"/v1/jobs/{job_id}").json()
            if job["status"] in {"succeeded", "failed", "cancelled"}:
                return job
            if time.monotonic() > deadline:
                raise AssertionError(f"job {job_id} still {job['status']}")
            time.sleep(0.01)

    def result(self, job_id: str, component: str) -> dict[str, Any]:
        job = self.wait(job_id)
        assert job["status"] == "succeeded", job
        self.spec.validate_component(component, job["result"])
        return dict(job["result"])


@contextmanager
def world(
    contracts: Path, settings: Settings | None = None, search: dict[str, list[Candidate]] | None = None
) -> Iterator[World]:
    llm = FakeLlm(contracts)
    registry = FakeRegistry(contracts)
    collector = FakeCollector(contracts, "collector-web")
    tg = FakeCollector(contracts, "collector-telegram")
    handler = FakeHandler(contracts, registry)
    orch = FakeOrchestrator(contracts, registry)
    storage = FakeStorage(contracts)
    fake_search = FakeSearch(search or DEFAULT_SEARCH)
    transports = {
        "llm": httpx.ASGITransport(app=llm.app),
        "registry": httpx.ASGITransport(app=registry.app),
        "collector_web": httpx.ASGITransport(app=collector.app),
        "collector_telegram": httpx.ASGITransport(app=tg.app),
        "handler": httpx.ASGITransport(app=handler.app),
        "orchestrator": httpx.ASGITransport(app=orch.app),
        "storage": httpx.ASGITransport(app=storage.app),
    }
    settings = settings or Settings(log_format="console", contracts_dir=contracts)
    app = build_app(settings, Dependencies(transports=transports, search=fake_search))
    spec = load_spec(contracts / "openapi" / "assistant.v1.yaml")
    with TestClient(app) as client:
        yield World(
            contracts,
            llm,
            registry,
            collector,
            tg,
            handler,
            orch,
            storage,
            fake_search,
            client,
            ContractClient(spec, client),
            spec,
            extra={"transports": transports},
        )
