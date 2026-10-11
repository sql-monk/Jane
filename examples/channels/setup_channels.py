"""Posts of public Telegram channels on a running Jane stack (real Telegram through the owner's account).

Needs the Telethon collector of ``infra/compose.local.example.yaml`` and the account secrets written by
``scripts/tg_session.py`` (``.jane/secrets/tg_api_hash``, ``tg_session``). Generates a collector rules package
per channel (``packages/channels.<username>-rules``), publishes it with ``channels.telegram-posts`` and the
storage packages, puts the ``tg-main`` connection (``api_id`` from the command line, secrets as ``file:``
references), creates a source ``tg-<username>`` and a task ``posts-<username>`` per channel (history since
``--since``, then new and edited messages every 15 minutes) and starts each task once.

    uv run --all-packages python examples/channels/setup_channels.py --project <p> --api-id <id> [channel ...]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "shops"))

from setup_shops import publish  # noqa: E402

import jane_examples as ex  # noqa: E402

PACKAGES = HERE / "packages"
EXTRACTOR = "channels.telegram-posts"
DEFAULT_CHANNELS = ["suspilnenews", "unian", "hromadske_ua", "ukrpravda_news", "radiosvoboda"]


def write_rules(channel: str, since: str) -> None:
    d = PACKAGES / f"channels.{channel.lower()}-rules"
    d.mkdir(parents=True, exist_ok=True)
    rules = {
        "collector": "telegram",
        "channels": [{"username": channel}],
        "history": {"enabled": True, "since": since},
        "updates": {"new_messages": True, "edits": True},
        "media": {"download": False},
        "account_connection_id": "tg-main",
    }
    manifest = {
        "schema_version": "1",
        "package_id": f"channels.{channel.lower()}-rules",
        "version": "1.0.0",
        "kind": "collector-rules",
        "title": f"Telegram channel @{channel}",
        "description": f"Правила Telegram Collector: публічний канал @{channel}, історія з {since}, нові й змінені повідомлення.",
        "tags": ["telegram", "news"],
        "entry": {"collector": "telegram", "rules": "rules.json"},
        "tests": [],
        "provenance": {
            "created_by": "human",
            "authors": ["Claude (coordinator)"],
            "created_at": "2026-10-10T00:00:00Z",
            "change_summary": f"Posts of @{channel}.",
        },
    }
    ex.write_json(d / "rules.json", rules)
    ex.write_json(d / "jane-package.json", manifest)


def task_doc(channel: str, refs: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "task_id": f"posts-{channel.lower().replace('_', '-')}",
        "title": f"Пости @{channel}",
        "description": "Повідомлення каналу → RAW у files, пости (post) у MongoDB.",
        "input": {"source_id": f"tg-{channel.lower().replace('_', '-')}"},
        "stages": [
            {
                "stage_id": "collect",
                "kind": "collect",
                "collector": {"collector": "telegram", "mode": "incremental"},
            },
            {
                "stage_id": "store-raw",
                "kind": "handler",
                "handler": refs["jane.storage-files"],
                "connections": {"target": ex.RAW_CONNECTION},
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "extract-posts",
                "kind": "handler",
                "handler": refs[EXTRACTOR],
                "inputs": [{"from": "collect"}],
            },
            {
                "stage_id": "store-posts",
                "kind": "handler",
                "handler": refs[ex.RESULTS_PACKAGE],
                "connections": {"target": ex.RESULTS_CONNECTION},
                "inputs": [
                    {
                        "from": "extract-posts",
                        "select": "output",
                        "when": {"field": "result.status", "op": "eq", "value": "success"},
                    }
                ],
            },
        ],
        "schedule": {"type": "interval", "interval_seconds": 900, "overlap": "skip"},
        "limits": {"telegram": {"max_messages_per_run": 500}},
        "forward_unknown_to_llm": False,
        "labels": {"group": "telegram-news"},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument(
        "--api-id", type=int, required=True, help="api_id of the Telegram application (not a secret)"
    )
    ap.add_argument("--since", default="2026-10-08T00:00:00Z", help="history start (RFC 3339)")
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("channels", nargs="*", default=DEFAULT_CHANNELS)
    ns = ap.parse_args(argv)
    for channel in ns.channels:
        write_rules(channel, ns.since)
    svc = ex.Services.of_project(ns.project)
    try:
        refs = publish(svc, PACKAGES)
        orch = svc.orchestrator
        for conn in ex.read_json(HERE.parent / "documents" / "connections.json")["connections"]:
            orch.call("PUT", f"/v1/connections/{conn['connection_id']}", ok=(200, 201), json=conn)
        account = {
            "connection_id": "tg-main",
            "kind": "telegram_account",
            "title": "Обліковий запис Telegram власника",
            "params": {"api_id": ns.api_id},
            "secret_refs": {
                "api_hash": "file:/run/secrets/tg_api_hash",
                "session": "file:/run/secrets/tg_session",
            },
        }
        orch.call("PUT", "/v1/connections/tg-main", ok=(200, 201), json=account)
        runs: dict[str, str] = {}
        for channel in ns.channels:
            slug = channel.lower().replace("_", "-")
            source = {
                "source_id": f"tg-{slug}",
                "kind": "telegram",
                "title": f"Telegram @{channel}",
                "description": f"Публічний канал https://t.me/{channel}",
                "locator": {"telegram_username": channel},
                "collector_rules": refs[f"channels.{channel.lower()}-rules"],
                "connections": {"account": "tg-main"},
                "forward_unknown_to_llm": False,
                "expected_entity_types": ["post"],
                "labels": {"group": "telegram-news"},
            }
            r = orch.call(
                "POST", "/v1/sources", ok=(201, 409), json=source, headers={"Idempotency-Key": ex.key()}
            )
            if r.status_code == 409:
                current = orch.call("GET", f"/v1/sources/{source['source_id']}")
                r = orch.call(
                    "PUT",
                    f"/v1/sources/{source['source_id']}",
                    json=source,
                    headers={"If-Match": current.headers["ETag"]},
                )
            ex.log(f"orchestrator: source {source['source_id']} -> {r.status_code}")
            task = task_doc(channel, refs)
            ex.create_task(orch, task)
            runs[channel] = ex.start_run(orch, task["task_id"], "examples/channels: first run")
        failed = 0
        for channel, run_id in runs.items():
            run = ex.wait_run(orch, run_id, ns.timeout)
            ex.log(f"run @{channel}: {run['status']} counters={run.get('counters')} error={run.get('error')}")
            failed += run["status"] != "succeeded"
        for channel in ns.channels:
            posts = svc.storage.pages(
                "/v1/entities",
                {
                    "connection_id": ex.RESULTS_CONNECTION,
                    "entity_type": "post",
                    "scope": f"tg-{channel.lower().replace('_', '-')}",
                },
            )
            ex.log(f"storage: {len(posts)} posts of @{channel}")
        return 1 if failed else 0
    finally:
        svc.close()


if __name__ == "__main__":
    sys.exit(main())
