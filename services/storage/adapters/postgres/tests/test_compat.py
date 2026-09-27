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
