"""Export what the sites of examples/sites collected: catalogs, ads and analysed news as CSV tables.

    uv run --all-packages python examples/sites/export_sites.py --project <p> [--out DIR] [--history TYPE ...]

One file per entity type (``product.csv``, ``car_ad.csv``, ``classified_ad.csv``, ``article.csv``, ``post.csv``,
``news_item.csv``, ``news_event.csv`` …) with the current state of every entity: the source (``scope``), the
key, ``updated_at``, ``version`` and the fields (nested values as JSON). ``news_event_sources.csv`` groups the
analysed news by ``event_key``: how many items and which sources describe each event. ``--history product``
also writes ``product_history.csv`` - every stored observation of every product (price changes over time).
CSV is UTF-8 with a BOM so that Excel opens Cyrillic text correctly. Default output: ``.jane/sites-export-<p>/``.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import jane_examples as ex  # noqa: E402

CONNECTION = "results-pg"
TYPES = (
    "product",
    "offer",
    "car_ad",
    "classified_ad",
    "article",
    "post",
    "news_item",
    "news_event",
    "news_mention",
)


def cell(value: Any) -> Any:
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False)
    return value


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], first: Sequence[str]) -> int:
    rows = list(rows)
    columns = list(first) + sorted({k for r in rows for k in r} - set(first))
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: cell(v) for k, v in r.items()})
    ex.log(f"{path.name}: {len(rows)} rows")
    return len(rows)


def scope_of(item: Mapping[str, Any]) -> str:
    key = item.get("key") or {}
    return str(key.get("scope", "")) if isinstance(key, Mapping) else ""


def state_rows(items: Iterable[Mapping[str, Any]]) -> Iterator[dict[str, Any]]:
    for item in items:
        yield {
            "source": scope_of(item),
            "updated_at": item.get("updated_at"),
            "version": item.get("version"),
            **item["fields"],
        }


def history_rows(
    svc: ex.Services, entity_type: str, items: Iterable[Mapping[str, Any]]
) -> Iterator[dict[str, Any]]:
    for item in items:
        key = item.get("canonical_key")
        if not key:
            continue
        for entry in svc.storage.pages(
            "/v1/entity-history", {"connection_id": CONNECTION, "entity_type": entity_type, "key": key}
        ):
            record = entry["record"]
            yield {
                "source": scope_of(item),
                "canonical_key": key,
                "received_at": entry["received_at"],
                "applied_fields": entry.get("applied_fields"),
                **(record.get("fields") or {}),
            }


def event_rows(
    news: Iterable[Mapping[str, Any]], events: Mapping[str, Mapping[str, Any]]
) -> Iterator[dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in news:
        if item["fields"].get("event_key"):
            groups[str(item["fields"]["event_key"])].append(item["fields"])
    for event_key, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        sources = sorted({str(m.get("source", "")) for m in members})
        event = events.get(event_key, {})
        yield {
            "event_key": event_key,
            "event_title": event.get("title") or members[0].get("event_title"),
            "items": len(members),
            "sources_count": len(sources),
            "sources": sources,
            "titles": [m.get("title") for m in members],
        }


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--history", action="append", default=[], help="entity type whose full history to export")
    ns = ap.parse_args(argv)
    out: Path = ns.out or ex.STACK_DIR / f"sites-export-{ns.project}"
    out.mkdir(parents=True, exist_ok=True)
    svc = ex.Services.of_project(ns.project)
    try:
        states: dict[str, list[dict[str, Any]]] = {}
        for entity_type in TYPES:
            items = svc.storage.pages(
                "/v1/entities", {"connection_id": CONNECTION, "entity_type": entity_type}
            )
            if not items:
                continue
            states[entity_type] = items
            write_csv(out / f"{entity_type}.csv", state_rows(items), ("source", "updated_at", "version"))
        for entity_type in ns.history:
            write_csv(
                out / f"{entity_type}_history.csv",
                history_rows(svc, entity_type, states.get(entity_type, [])),
                ("source", "canonical_key", "received_at", "applied_fields"),
            )
        if "news_item" in states:
            events = {str(e["fields"].get("event_key")): e["fields"] for e in states.get("news_event", [])}
            write_csv(out / "news_event_sources.csv", event_rows(states["news_item"], events), ("event_key",))
        ex.log(f"export: {out}")
        return 0
    finally:
        svc.close()


if __name__ == "__main__":
    sys.exit(main())
