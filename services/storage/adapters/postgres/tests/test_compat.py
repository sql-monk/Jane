"""Compatibility suite C-01…C-16 for the PostgreSQL adapter against the dev stack.

Needs `just up --project <name> postgres`, then `just integration --project <name> services/storage`.
Every test gets its own schema, dropped afterwards.
"""

from __future__ import annotations

import socket
import uuid
from typing import Any

import asyncpg  # type: ignore[import-untyped]
import pytest

from jane_contracts.storage_adapter import ResolvedConnection
from jane_kit.devstack import StackInfo, load_stack
from jane_storage.compat import AdapterCompatSuite, CompatTarget

pytestmark = pytest.mark.integration


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class PostgresTarget(CompatTarget):
    kind = "postgresql"

    def __init__(self, stack: StackInfo) -> None:
        self.pg = stack.services["postgres"]
        self.schema = f"compat_{uuid.uuid4().hex[:12]}"

    def _conn(self, port: int, cid: str) -> ResolvedConnection:
        return ResolvedConnection(
            connection_id=cid,
            kind="postgresql",
            params={
                "host": self.pg["host"],
                "port": port,
                "database": self.pg["database"],
                "schema": self.schema,
                "sslmode": "disable",
            },
            secrets={"username": self.pg["user"], "password": self.pg["password"]},
        )

    def connection(self) -> ResolvedConnection:
        return self._conn(int(self.pg["port"]), "compat-pg")

    def unavailable_connection(self) -> ResolvedConnection:
        return self._conn(_free_port(), "compat-pg-down")

    def options(self) -> dict[str, Any]:
        return {"connect_timeout_ms": 3000, "pool_max_size": 4}

    async def cleanup(self) -> None:
        con = await asyncpg.connect(self.pg["dsn"])
        try:
            await con.execute(f'DROP SCHEMA IF EXISTS "{self.schema}" CASCADE')
        finally:
            await con.close()


class TestPostgresCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        stack = load_stack()
        if stack is None or "postgres" not in stack.services:
            pytest.skip("dev stack with postgres is not running (just up postgres)")
        return PostgresTarget(stack)

    async def test_discovery_search_and_entity_statistics(self, env: Any) -> None:
        from jane_storage.compat.suite import raw_object, record

        adapter = await env.adapter()
        engine = env.engine(adapter)
        for i, title in enumerate(["first", "Needle 100%_ match", "Needle second"]):
            await engine.store_entity(record(f"A-{i}", fields={"title": title}), f"discovery-{i}")
        article = record("article", scope="another-space", fields={"title": "Article"})
        article["entity_type"] = "article"
        await engine.store_entity(article, "discovery-article")
        catalog, cursor = await adapter.list_entity_types(limit=1)
        assert list(catalog) == [{"entity_type": "article", "entity_count": 1}]
        assert cursor
        catalog, cursor = await adapter.list_entity_types(limit=1, cursor=cursor)
        assert list(catalog) == [{"entity_type": "product", "entity_count": 3}]
        assert cursor is None
        scoped, _ = await adapter.list_entity_types(scope="another-space", limit=10)
        assert list(scoped) == [{"entity_type": "article", "entity_count": 1}]
        first, _ = await adapter.list_entities("product", limit=1)
        assert first[0].fields["title"] == "first"
        found, cursor = await adapter.search_entities("product", search="NEEDLE", limit=1)
        assert found[0].fields["title"] == "Needle 100%_ match"
        found, cursor = await adapter.search_entities("product", search="needle", cursor=cursor, limit=1)
        assert found[0].fields["title"] == "Needle second"
        assert cursor is None
        literal, _ = await adapter.search_entities("product", search="%_", limit=10)
        assert len(literal) == 1
        no_match, _ = await adapter.search_entities(
            "product", search="needle", scope="another-space", limit=10
        )
        assert not no_match
        before = await adapter.object_statistics()
        assert before == {"object_count": 0, "total_size_bytes": 0}
        await adapter.put_object(raw_object("raw/test.html", b"raw payload"))
        assert await adapter.object_statistics() == {"object_count": 1, "total_size_bytes": 11}
        stats = await adapter.entity_statistics()
        assert stats["entity_count"] == 4
        assert stats["total_size_bytes"] > 0
        assert stats["size_basis"] == "postgresql_relation_with_indexes"
        assert stats["types"] == [
            {"entity_type": "article", "entity_count": 1},
            {"entity_type": "product", "entity_count": 3},
        ]
