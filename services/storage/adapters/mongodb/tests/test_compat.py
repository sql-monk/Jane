"""Compatibility suite C-01…C-16 for the MongoDB adapter against the dev stack (standalone mongod, no replica set),
plus the collection-per-type layout, catalog, server-side search and statistics.

Needs `just up --project <name> mongodb`, then `just integration --project <name> services/storage/adapters/mongodb`.
Every test gets its own database, dropped afterwards.
"""

from __future__ import annotations

import socket
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest
from pymongo import AsyncMongoClient

from jane_contracts.storage_adapter import ResolvedConnection
from jane_kit.devstack import StackInfo, load_stack
from jane_storage.compat import AdapterCompatSuite, CompatEnv, CompatTarget
from jane_storage.compat.suite import raw_object, record
from jane_storage.keys import canonical_key, key_digest
from jane_storage_mongodb import SIZE_BASIS, MongoAdapter

pytestmark = pytest.mark.integration


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class MongoTarget(CompatTarget):
    kind = "mongodb"

    def __init__(self, stack: StackInfo) -> None:
        self.info = stack.services["mongodb"]
        self.database = f"compat_{uuid.uuid4().hex[:12]}"

    def _conn(self, port: int, cid: str) -> ResolvedConnection:
        return ResolvedConnection(
            connection_id=cid,
            kind="mongodb",
            params={
                "host": self.info["host"],
                "port": port,
                "database": self.database,
                "auth_source": "admin",
            },
            secrets={"username": self.info["user"], "password": self.info["password"]},
        )

    def connection(self) -> ResolvedConnection:
        return self._conn(int(self.info["port"]), "compat-mongo")

    def unavailable_connection(self) -> ResolvedConnection:
        return self._conn(_free_port(), "compat-mongo-down")

    def options(self) -> dict[str, Any]:
        # small chunks, so C-12/C-15 objects span several chunk documents; the default (empty) prefix
        return {"connect_timeout_ms": 2000, "pool_max_size": 4, "chunk_bytes": 16}

    def client(self) -> AsyncMongoClient[dict[str, Any]]:
        return AsyncMongoClient(self.info["uri"], tz_aware=True)

    async def native_entity_document(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> Any | None:
        client = self.client()
        try:
            return await client[self.database][entity_type].find_one({"_id": key_digest(canonical_key)})
        finally:
            await client.close()

    async def native_history_documents(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> list[Any] | None:
        client = self.client()
        try:
            cursor = client[self.database][f"{entity_type}.history"].find(
                {"key_hash": key_digest(canonical_key)}
            )
            return await cursor.to_list()
        finally:
            await client.close()

    async def cleanup(self) -> None:
        client = self.client()
        try:
            await client.drop_database(self.database)
        finally:
            await client.close()


async def _search(adapter: MongoAdapter, entity_type: str, term: str, **filters: Any) -> list[str]:
    """Titles of every match, page by page (one entity per page): the server filters before pagination."""
    titles: list[str] = []
    cursor: str | None = None
    for _ in range(100):
        page, cursor = await adapter.search_entities(
            entity_type, search=term, cursor=cursor, limit=1, **filters
        )
        assert len(page) <= 1
        titles += [str(s.fields["title"]) for s in page]
        if cursor is None:
            return titles
    raise AssertionError("search_entities did not finish")


class TestMongoCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        stack = load_stack()
        if stack is None or "mongodb" not in stack.services:
            pytest.skip("dev stack with mongodb is not running (just up mongodb)")
        return MongoTarget(stack)

    async def test_collection_per_type_and_lazy_indexes(self, env: CompatEnv) -> None:
        target = cast(MongoTarget, env.target)
        adapter = cast(MongoAdapter, await env.adapter())  # ensure_schema(["product"])
        book = record("B-1", fields={"title": "Кобзар"})
        book["entity_type"] = "product_book"  # first write of a type ensure_schema was not given
        ack = await env.engine(adapter).store_entity(book, "layout#0")
        assert ack["status"] == "written"
        rec = await adapter.put_object(raw_object("raw/layout.html", b"<html/>"))
        assert rec.locator == {"collection": "_objects", "id": rec.object_id}
        client = target.client()
        db = client[target.database]
        try:
            names = set(await db.list_collection_names())
            assert names == {
                "product",
                "product.history",
                "product_book",
                "product_book.history",
                "_deliveries",
                "_objects",
                "_object_chunks",
            }
            indexes = {
                tuple(spec["key"]): spec for spec in (await db["product_book"].index_information()).values()
            }
            assert set(indexes) == {
                (("_id", 1),),
                (("canonical_key", 1),),
                (("key.scope", 1), ("canonical_key", 1)),
                (("updated_at", 1),),
                (("pending.delivery_key", 1),),
            }
            assert indexes[(("pending.delivery_key", 1),)]["partialFilterExpression"] == {
                "pending": {"$exists": True}
            }
            history = {
                tuple(spec["key"]): spec
                for spec in (await db["product_book.history"].index_information()).values()
            }
            assert history[(("key_hash", 1), ("version", -1))]["unique"] is True
            key = canonical_key(book["key"])
            state = await db["product_book"].find_one({"_id": key_digest(key)})
            assert state is not None and "pending" not in state
            assert state["fields"] == {"title": "Кобзар"} and "кобзар" in state["search_text"]
            delivery = await db["_deliveries"].find_one({"_id": key_digest("layout#0")})
            assert delivery is not None and "intent" not in delivery
            assert delivery["acks"][0]["entity"]["entity_type"] == "product_book"
        finally:
            await client.close()

    async def test_discovery_search_and_statistics(self, env: CompatEnv) -> None:
        adapter = cast(MongoAdapter, await env.adapter())
        engine = env.engine(adapter)
        titles = ["first", "Needle 100%_ match", "Needle second", "needle .*(x)? $title"]
        for i, title in enumerate(titles):
            await engine.store_entity(record(f"A-{i}", fields={"title": title}), f"discovery-{i}#0")
        article = record("article", scope="another-space", fields={"title": "Стаття про ЇЖАКА"})
        article["entity_type"] = "article"
        await engine.store_entity(article, "discovery-article#0")
        assert await adapter.object_statistics() == {"object_count": 0, "total_size_bytes": 0}
        await adapter.put_object(raw_object("raw/test.html", b"raw payload"))

        # catalog: type collections only (not .history, _deliveries, _objects, _object_chunks), cursor, scope
        catalog, cursor = await adapter.list_entity_types(limit=1)
        assert list(catalog) == [{"entity_type": "article", "entity_count": 1}]
        assert cursor
        catalog, cursor = await adapter.list_entity_types(limit=1, cursor=cursor)
        assert list(catalog) == [{"entity_type": "product", "entity_count": 4}]
        assert cursor is None
        scoped, _ = await adapter.list_entity_types(scope="another-space", limit=10)
        assert list(scoped) == [{"entity_type": "article", "entity_count": 1}]
        assert (await adapter.list_entity_types(scope="nobody", limit=10)) == ([], None)

        # lists keep canonical_key order; search filters on the server before pagination, literally
        first, _ = await adapter.list_entities("product", limit=1)
        assert first[0].fields["title"] == "first"
        assert await _search(adapter, "product", "NEEDLE") == titles[1:]
        assert await _search(adapter, "product", "%_") == ["Needle 100%_ match"]
        assert await _search(adapter, "product", ".*(x)?") == ["needle .*(x)? $title"]
        assert await _search(adapter, "product", "$title") == ["needle .*(x)? $title"]  # not a field path
        assert await _search(adapter, "product", '"sku": "a-2"') == ["Needle second"]  # key, casefolded
        assert await _search(adapter, "article", "їжака") == ["Стаття про ЇЖАКА"]
        assert await _search(adapter, "product", "needle", scope="another-space") == []
        future, past = datetime.now(UTC) + timedelta(hours=1), datetime.now(UTC) - timedelta(hours=1)
        assert await _search(adapter, "product", "needle", updated_since=future) == []
        assert await _search(adapter, "product", "needle", updated_since=past) == titles[1:]
        assert await _search(adapter, "product", "no such text") == []
        assert await _search(adapter, "missing_type", "needle") == []

        # statistics: RAW/documents apart from the current states (history and deliveries excluded)
        assert await adapter.object_statistics() == {"object_count": 1, "total_size_bytes": 11}
        stats = await adapter.entity_statistics()
        assert stats["entity_count"] == 5
        assert stats["types"] == [
            {"entity_type": "article", "entity_count": 1},
            {"entity_type": "product", "entity_count": 4},
        ]
        assert stats["size_basis"] == SIZE_BASIS == "mongodb_collections_with_indexes"
        assert isinstance(stats["total_size_bytes"], int) and stats["total_size_bytes"] > 0

        # another prefix in the same database is another namespace
        other = cast(MongoAdapter, await env.adapter(prefix="other_"))
        assert await other.list_entity_types(limit=10) == ([], None)
        assert await other.object_statistics() == {"object_count": 0, "total_size_bytes": 0}
        empty = await other.entity_statistics()
        assert (empty["entity_count"], empty["types"]) == (0, [])
