"""Validate explicit manual reference coverage without inferring semantic acceptance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from check import parse
from common import digest, read


def load(root: Path, symbols: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_id = {x["id"]: x for x in symbols}
    inputs: list[dict[str, Any]] = []
    entries: dict[str, Any] = {}
    fields = {"purpose_doc", "example_doc", "exceptions_doc", "constraints_doc"}
    for path in sorted((root / "docs/components").glob("*/reference/types/coverage.json")):
        data = json.loads(read(path))
        if data.get("format_version") != 1 or not isinstance(data.get("symbols"), dict):
            raise ValueError(f"Invalid manual coverage: {path}")
        component = path.parents[2].name
        for symbol_id, record in data["symbols"].items():
            if symbol_id not in by_id or by_id[symbol_id]["component"] != component:
                raise ValueError(f"Unknown or foreign public symbol: {symbol_id}")
            if symbol_id in entries or not isinstance(record, dict) or not record:
                raise ValueError(f"Invalid duplicate/empty coverage: {symbol_id}")
            if set(record) - fields - {"exceptions_not_applicable", "constraints_not_applicable"}:
                raise ValueError(f"Unknown coverage field: {symbol_id}")
            for key, value in record.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"Empty coverage value: {symbol_id} {key}")
                if key.endswith("_not_applicable"):
                    if key.removesuffix("_not_applicable") + "_doc" in record:
                        raise ValueError(f"Contradictory coverage: {symbol_id} {key}")
                    continue
                url = urlsplit(value)
                target = (root / unquote(url.path)).resolve()
                if url.scheme or url.netloc or not target.is_relative_to(root.resolve()):
                    raise ValueError(f"Coverage must reference local documentation: {value}")
                if not target.is_file() or target.suffix != ".md" or "generated" in target.parts:
                    raise ValueError(f"Manual documentation missing: {value}")
                if url.fragment and unquote(url.fragment) not in parse(read(target)).anchors:
                    raise ValueError(f"Manual heading missing: {value}")
            entries[symbol_id] = record
        inputs.append(
            {"path": path.relative_to(root).as_posix(), "sha256": digest(path), "role": "manual-coverage-map"}
        )
    return inputs, entries
