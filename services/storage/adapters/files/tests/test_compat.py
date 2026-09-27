"""Compatibility suite C-01…C-16 for the filesystem adapter (runs in `just check`, no services needed)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from jane_contracts.storage_adapter import ObjectRecord, ResolvedConnection
from jane_storage.compat import AdapterCompatSuite, CompatTarget
from jane_storage.keys import key_digest


class FilesTarget(CompatTarget):
    kind = "filesystem"
    entity_formats = ("json", "jsonl")

    def __init__(self, base: Path) -> None:
        self.base = base

    def connection(self) -> ResolvedConnection:
        return ResolvedConnection(
            connection_id="compat-files", kind="filesystem", params={"base_path": str(self.base / "store")}
        )

    def unavailable_connection(self) -> ResolvedConnection:
        blocker = self.base / "blocker"
        blocker.write_text("not a directory", encoding="utf-8")
        return ResolvedConnection(
            connection_id="compat-files-down", kind="filesystem", params={"base_path": str(blocker / "store")}
        )

    def options(self) -> dict[str, Any]:
        return {"prefix": "compat"}

    def _root(self, options: Mapping[str, Any]) -> Path:
        return self.base / "store" / str(options.get("prefix", "compat"))

    async def native_object_path(self, rec: ObjectRecord) -> str | None:
        path = self.base / "store" / str(rec.locator["path"])
        assert path.is_file()
        return path.name

    async def native_entity_document(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> Any | None:
        path = self._root(options) / "entities" / entity_type / f"{key_digest(canonical_key)}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    async def native_history_documents(
        self, entity_type: str, canonical_key: str, options: Mapping[str, Any]
    ) -> list[Any] | None:
        root = self._root(options) / "history" / entity_type
        digest = key_digest(canonical_key)
        if options.get("entities_format") == "jsonl":
            lines = (root / f"{digest}.jsonl").read_text(encoding="utf-8").splitlines()
            return [json.loads(line) for line in lines]
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / digest).glob("*.json"))]


class TestFilesystemCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self, tmp_path: Path) -> CompatTarget:
        return FilesTarget(tmp_path)
