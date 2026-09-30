"""Compatibility suite C-01…C-16 for the SQL Server adapter against the dev stack (SQL Server 2022 Developer).

Needs `just up --project <name> sqlserver`, then
`just integration --project <name> services/storage/adapters/sqlserver`.
Tests share the database ``jane_compat`` (created on first use); every test gets its own schema,
dropped with its tables afterwards.
"""

from __future__ import annotations

import asyncio
import json
import socket
import uuid
from collections.abc import Mapping
from typing import Any

import pymssql
import pytest

from jane_contracts.storage_adapter import ResolvedConnection
from jane_kit.devstack import StackInfo, load_stack
from jane_storage.compat import AdapterCompatSuite, CompatTarget
from jane_storage.keys import key_digest

pytestmark = pytest.mark.integration

DATABASE = "jane_compat"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class SqlServerTarget(CompatTarget):
    kind = "sqlserver"

    def __init__(self, stack: StackInfo) -> None:
        self.info = stack.services["sqlserver"]
        self.schema = f"compat_{uuid.uuid4().hex[:12]}"
        self._ensure_database()

    def _connect(self, database: str) -> Any:
        return pymssql.connect(
            server=self.info["host"],
            port=str(self.info["port"]),
            user=self.info["user"],
            password=self.info["password"],
            database=database,
            autocommit=True,
            login_timeout=10,
            tds_version="7.4",
        )

    def _ensure_database(self) -> None:
        con = self._connect("master")
        try:
            with con.cursor() as cur:
                cur.execute(f"IF DB_ID(N'{DATABASE}') IS NULL CREATE DATABASE [{DATABASE}]")
        finally:
            con.close()

    def _conn(self, port: int, cid: str) -> ResolvedConnection:
        return ResolvedConnection(
            connection_id=cid,
            kind="sqlserver",
            params={"host": self.info["host"], "port": port, "database": DATABASE, "schema": self.schema},
            secrets={"username": self.info["user"], "password": self.info["password"]},
        )

    def connection(self) -> ResolvedConnection:
        return self._conn(int(self.info["port"]), "compat-mssql")

    def unavailable_connection(self) -> ResolvedConnection:
        return self._conn(_free_port(), "compat-mssql-down")

    def options(self) -> dict[str, Any]:
        return {"connect_timeout_ms": 2000, "pool_max_size": 4}

    def _query_docs(self, sql: str, *args: Any) -> list[Any]:
        con = self._connect(DATABASE)
        try:
            with con.cursor() as cur:
                cur.execute(sql, args)
                return [json.loads(row[0]) for row in cur.fetchall()]
        finally:
            con.close()

    async def native_entity_document(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> Any | None:
        sql = f"SELECT doc FROM [{self.schema}].[jane_entities] WHERE entity_type = %s AND key_hash = %s"
        docs = await asyncio.to_thread(self._query_docs, sql, entity_type, key_digest(canonical_key))
        return docs[0] if docs else None

    async def native_history_documents(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> list[Any] | None:
        sql = (
            f"SELECT doc FROM [{self.schema}].[jane_entity_history] WHERE entity_type = %s AND key_hash = %s "
            "ORDER BY version"
        )
        return await asyncio.to_thread(self._query_docs, sql, entity_type, key_digest(canonical_key))

    async def cleanup(self) -> None:
        def drop() -> None:
            con = self._connect(DATABASE)
            try:
                with con.cursor() as cur:
                    cur.execute(
                        "SELECT t.name FROM sys.tables t WHERE t.schema_id = SCHEMA_ID(%s)", (self.schema,)
                    )
                    for (name,) in cur.fetchall():
                        cur.execute(f"DROP TABLE [{self.schema}].[{name}]")
                    cur.execute(f"IF SCHEMA_ID(N'{self.schema}') IS NOT NULL DROP SCHEMA [{self.schema}]")
            finally:
                con.close()

        await asyncio.to_thread(drop)


class TestSqlServerCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        stack = load_stack()
        if stack is None or "sqlserver" not in stack.services:
            pytest.skip("dev stack with sqlserver is not running (just up sqlserver)")
        return SqlServerTarget(stack)
