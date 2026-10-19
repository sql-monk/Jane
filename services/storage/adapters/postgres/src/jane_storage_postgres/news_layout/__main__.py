"""CLI of the ``news`` layout: ``python -m jane_storage_postgres.news_layout rebuild --schema news …``.

Connection parameters come from arguments or the libpq environment variables (``PGHOST``, ``PGPORT``,
``PGDATABASE``, ``PGUSER``, ``PGSSLMODE``). The password is read only from an environment variable
(``--password-env``, default ``PGPASSWORD``), never from the command line. Prints a JSON summary.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections.abc import Sequence
from typing import Any

from jane_contracts.storage_adapter import AdapterError, ResolvedConnection

from . import DEFAULT_REBUILD_BATCH_SIZE, LAYOUT


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m jane_storage_postgres.news_layout",
        description="Relational layout 'news' of the PostgreSQL storage adapter.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser(
        "rebuild",
        help="apply missing layout migrations, clear the projection and lay every stored snapshot out again",
    )
    cmd.add_argument("--host", default=os.environ.get("PGHOST", "localhost"))
    cmd.add_argument("--port", type=int, default=int(os.environ.get("PGPORT", "5432")))
    cmd.add_argument("--database", default=os.environ.get("PGDATABASE"))
    cmd.add_argument("--user", default=os.environ.get("PGUSER"))
    cmd.add_argument(
        "--password-env",
        default="PGPASSWORD",
        help="name of the environment variable with the password (default PGPASSWORD)",
    )
    cmd.add_argument("--schema", required=True, help="schema with the engine tables and the projection")
    cmd.add_argument("--table-prefix", default="jane_", help="prefix of the engine tables (default jane_)")
    cmd.add_argument("--sslmode", default=os.environ.get("PGSSLMODE", "prefer"))
    cmd.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_REBUILD_BATCH_SIZE,
        help=f"snapshots read per query (default {DEFAULT_REBUILD_BATCH_SIZE})",
    )
    cmd.add_argument(
        "--command-timeout-ms", type=int, help="statement timeout of the adapter (default: adapter default)"
    )
    return parser


async def _rebuild(ns: argparse.Namespace) -> dict[str, Any]:
    from jane_storage_postgres import PostgresAdapter

    connection = ResolvedConnection(
        connection_id="news-layout-cli",
        kind="postgresql",
        params={
            "host": ns.host,
            "port": ns.port,
            "database": ns.database,
            "schema": ns.schema,
            "table_prefix": ns.table_prefix,
            "sslmode": ns.sslmode,
            "layout": LAYOUT,
        },
        secrets={
            name: value
            for name, value in (("username", ns.user), ("password", os.environ.get(ns.password_env)))
            if value is not None
        },
    )
    options: dict[str, Any] = {}
    if ns.command_timeout_ms is not None:
        options["command_timeout_ms"] = ns.command_timeout_ms
    adapter = PostgresAdapter()
    await adapter.open(connection, options)
    try:
        await adapter.ensure_schema([])
        counts = await adapter.rebuild_layout(batch_size=ns.batch_size)
    finally:
        await adapter.close()
    return {"layout": LAYOUT, "schema": ns.schema, "table_prefix": ns.table_prefix, "rebuilt": counts}


def main(argv: Sequence[str] | None = None) -> int:
    ns = _parser().parse_args(argv)
    try:
        summary = asyncio.run(_rebuild(ns))
    except AdapterError as exc:
        print(f"rebuild failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
