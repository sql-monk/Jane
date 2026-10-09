"""R18 / WP-15 review: a large HTML RAW in PostgreSQL storage keeps its Material (``@pytest.mark.integration``).

The PostgreSQL adapter keeps RAW in a BLOB column and has no persistent URI; before WP-19 ``GET /v1/objects/{id}``
dropped ``material`` for such a RAW over ``transfer.inline_max_bytes`` and the assistant answered 501. Now storage
returns a transit blob of its own that a consumer reads within its ``BLOB_ROOTS``.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from jane_kit.content import ContentReader
from jane_kit.devstack import load_stack
from jane_storage.app import build_app
from jane_storage.settings import Settings

pytestmark = pytest.mark.integration


def test_large_html_in_postgresql_storage_is_returned_by_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, h: SimpleNamespace
) -> None:
    stack = load_stack()
    if stack is None or "postgres" not in stack.services:
        pytest.skip("dev stack with postgres is not running (just up postgres)")
    pg = stack.services["postgres"]
    monkeypatch.setenv("JANE_SECRET_WP19_PG_USER", pg["user"])
    monkeypatch.setenv("JANE_SECRET_WP19_PG_PASSWORD", pg["password"])
    monkeypatch.setenv("JANE_STORAGE_LIMITS__TRANSFER__INLINE_MAX_BYTES", "1024")
    schema = f"wp19_{hashlib.sha256(str(tmp_path).encode()).hexdigest()[:10]}"
    conns = tmp_path / "c.json"
    conns.write_text(
        json.dumps(
            {
                "connections": [
                    {
                        "connection_id": "raw-pg",
                        "kind": "postgresql",
                        "params": {
                            "host": pg["host"],
                            "port": pg["port"],
                            "database": pg["database"],
                            "schema": schema,
                            "sslmode": "disable",
                        },
                        "secret_refs": {
                            "username": "env:JANE_SECRET_WP19_PG_USER",
                            "password": "env:JANE_SECRET_WP19_PG_PASSWORD",
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    transit = tmp_path / "transit"
    settings = Settings(
        log_format="console",
        connections_file=conns,
        connection_host_allowlist=[f"{pg['host']}:{pg['port']}"],
        transit_dir=transit,
    )
    page = b"<html><body>" + b"<p>Kettle A-100 1299 UAH</p>" * 400 + b"</body></html>"
    try:
        with TestClient(build_app(settings)) as client:
            body = h.invocation(
                [{"kind": "material", "material": h.material(page)}],
                "wp19-pg-large",
                package="jane.storage-postgresql",
                target="raw-pg",
            )
            result = h.post(client, body).json()
            assert result["status"] == "success", result
            obj = result["output"]["writes"][0]["object"]
            detail = client.get(f"/v1/objects/{obj['object_id']}", params={"connection_id": "raw-pg"}).json()
            content = detail["material"]["content"]
            assert content["kind"] == "blob" and content["store"] == "transit"
            assert (
                content["size_bytes"] == len(page) and content["sha256"] == hashlib.sha256(page).hexdigest()
            )
            assert detail["material"]["material_id"] == h.material(page)["material_id"]
            reader = ContentReader(timeout_ms=5000, blob_roots=[transit])
            assert asyncio.run(reader.read(content, max_bytes=10_000_000)) == page
    finally:
        import asyncpg  # type: ignore[import-untyped]

        async def drop() -> None:
            con = await asyncpg.connect(pg["dsn"])
            try:
                await con.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
            finally:
                await con.close()

        asyncio.run(drop())
