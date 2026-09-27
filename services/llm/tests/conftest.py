"""Fixtures: the real LLM service app over a memory store (unit) or the dev-stack PostgreSQL (integration).

``store_kind`` is parametrised; the ``postgres`` variant is marked ``integration`` and needs
``just up --project jane-wp10 postgres`` + ``just integration --project jane-wp10``.
Each PostgreSQL test gets its own schema, dropped afterwards.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jane_kit.devstack import load_stack
from jane_llm.app import build_app
from jane_llm.providers import ADAPTERS, FakeProvider, ProviderRequest, ProviderResponse, ResolvedConnection
from jane_llm.settings import ServiceLimits, Settings
from jane_llm.store import MemoryStore, PostgresStore, Store


class CountingFake(FakeProvider):
    """The real fake provider plus a call counter (a neighbour, not the gateway)."""

    def __init__(self) -> None:
        self.calls: list[ProviderRequest] = []

    async def complete(
        self, request: ProviderRequest, connection: ResolvedConnection | None, limits: ServiceLimits
    ) -> ProviderResponse:
        self.calls.append(request)
        return await super().complete(request, connection, limits)


def pg_dsn() -> str | None:
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        return None
    return str(stack.get("postgres", "dsn"))


def new_schema() -> str:
    return f"llm_t_{uuid.uuid4().hex[:10]}"


def drop_schema(dsn: str, schema: str) -> None:
    import psycopg

    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')


@pytest.fixture(params=["memory", pytest.param("postgres", marks=pytest.mark.integration)])
def store_kind(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture
def make_store(store_kind: str) -> Iterator[Callable[[], tuple[Store, dict[str, Any]]]]:
    """Factory of stores sharing one backend (several instances share one PostgreSQL schema)."""
    created: list[Store] = []
    schema = new_schema()
    dsn = pg_dsn() if store_kind == "postgres" else None
    if store_kind == "postgres" and dsn is None:
        pytest.skip("dev stack PostgreSQL not running (just up --project jane-wp10 postgres)")
    memory = MemoryStore()

    def factory() -> tuple[Store, dict[str, Any]]:
        if store_kind == "memory":
            return memory, {"store": "memory"}
        assert dsn is not None
        defaults = Settings()
        store = PostgresStore(
            dsn, schema, min_size=defaults.db_pool_min_size, max_size=defaults.db_pool_max_size
        )
        created.append(store)
        return store, {"store": "postgres", "database_url": dsn, "db_schema": schema}

    yield factory
    for s in created:
        s.close()
    if dsn is not None:
        drop_schema(dsn, schema)


@pytest.fixture
def fake() -> CountingFake:
    return CountingFake()


@pytest.fixture
def make_client(
    make_store: Callable[[], tuple[Store, dict[str, Any]]], fake: CountingFake
) -> Iterator[Callable[..., TestClient]]:
    clients: list[TestClient] = []

    def factory(**kwargs: Any) -> TestClient:
        store, cfg = make_store()
        settings = Settings(log_format="console", **cfg, **kwargs.pop("settings", {}))
        app = build_app(settings, store=store, adapters={**ADAPTERS, "fake": fake}, **kwargs)
        client = TestClient(app)
        client.__enter__()
        clients.append(client)
        return client

    yield factory
    for c in clients:
        c.__exit__(None, None, None)


@pytest.fixture
def client(make_client: Callable[..., TestClient]) -> TestClient:
    return make_client()


PRICED_FAKE = {
    "provider_id": "fake",
    "kind": "fake",
    "enabled": True,
    "models": [
        {
            "model_id": "fake-deterministic-1",
            "max_context_tokens": 128000,
            "supports_structured_output": True,
            # 1000 USD per million tokens = 0.001 USD per token: budgets run out after a few calls.
            "pricing": {"input_per_mtok": 1000, "output_per_mtok": 1000, "currency": "USD"},
        }
    ],
}


def completion(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": "default",
        "instructions": "Classify the page type.",
        "data": [{"name": "page", "media_type": "text/plain", "text": "Kettle A-100, 1299 UAH"}],
        "output_schema": {
            "type": "object",
            "required": ["page_type"],
            "properties": {
                "page_type": {"type": "string", "enum": ["product", "category", "article", "other"]}
            },
        },
        "max_output_tokens": 64,
        "scope": {"purpose": "other"},
    }
    body.update(overrides)
    return body


def idem() -> dict[str, str]:
    return {"Idempotency-Key": f"t-{uuid.uuid4().hex}"}


class Helpers:
    """Shared helpers for test modules (tests import no conftest directly in importlib mode)."""

    completion = staticmethod(completion)
    idem = staticmethod(idem)
    priced_fake = PRICED_FAKE
    counting_fake = CountingFake
    pg_dsn = staticmethod(pg_dsn)
    new_schema = staticmethod(new_schema)
    drop_schema = staticmethod(drop_schema)


@pytest.fixture
def h() -> type[Helpers]:
    return Helpers
