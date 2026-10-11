"""Inspect news run stages through the orchestrator API, without reading service tables."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from setup_news import NewsServices


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stack-file", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    ns = parser.parse_args()
    svc = NewsServices.of_stack(ns.stack_file)
    try:
        for task_id, run_id in json.loads(ns.runs.read_text(encoding="utf-8")).items():
            run = svc.orchestrator.call("GET", f"/v1/runs/{run_id}").json()
            items = svc.orchestrator.pages(f"/v1/runs/{run_id}/items", {})
            counts = Counter(
                f"{item['stage_id']}:{item['status']}:{item.get('result_status', '')}" for item in items
            )
            print(
                json.dumps(
                    {
                        "task_id": task_id,
                        "run_id": run_id,
                        "status": run["status"],
                        "stages": dict(counts),
                        "errors": [item for item in items if item.get("error")],
                    },
                    ensure_ascii=False,
                )
            )
    finally:
        svc.close()


if __name__ == "__main__":
    main()
