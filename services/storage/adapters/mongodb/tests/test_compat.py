"""Compatibility suite C-01…C-16 for the MongoDB adapter against the dev stack (standalone mongod, no replica set).

Needs `just up --project <name> mongodb`, then `just integration --project <name> services/storage/adapters/mongodb`.
Every test gets its own database, dropped afterwards.
"""

from __future__ import annotations

import socket
import uuid
from collections.abc import Mapping
from typing import Any

import pytest
from pymongo import AsyncMongoClient

from jane_contracts.storage_adapter import ResolvedConnection
from jane_kit.devstack import StackInfo, load_stack
from jane_storage.compat import AdapterCompatSuite, CompatTarget
from jane_storage.keys import key_digest

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
        # small chunks, so C-12/C-15 objects span several chunk documents
        return {"connect_timeout_ms": 2000, "pool_max_size": 4, "chunk_bytes": 16}

    def _client(self) -> AsyncMongoClient[dict[str, Any]]:
        return AsyncMongoClient(self.info["uri"], tz_aware=True)

    async def native_entity_document(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> Any | None:
        client = self._client()
        try:
            return await client[self.database]["jane_entities"].find_one(
                {"_id": f"{entity_type}|{key_digest(canonical_key)}"}
            )
        finally:
            await client.close()

    async def native_history_documents(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> list[Any] | None:
        client = self._client()
        try:
            cursor = client[self.database]["jane_entity_history"].find(
                {"entity_type": entity_type, "key_hash": key_digest(canonical_key)}
            )
            return await cursor.to_list()
        finally:
            await client.close()

    async def cleanup(self) -> None:
        client = self._client()
        try:
            await client.drop_database(self.database)
        finally:
            await client.close()


class TestMongoCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        stack = load_stack()
        if stack is None or "mongodb" not in stack.services:
            pytest.skip("dev stack with mongodb is not running (just up mongodb)")
        return MongoTarget(stack)
