"""The scope tables of jane_kit.auth_scopes cover exactly the operations of each contract (ADR-0005 §3)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from jane_kit.auth import SCOPE_RE
from jane_kit.auth_scopes import HANDLER, LLM, TABLES, merge
from jane_kit.contracts import contracts_dir

pytestmark = pytest.mark.contract

_FOUND = contracts_dir(Path(__file__).parent)
if _FOUND is None or not (_FOUND / "openapi" / "common.yaml").is_file():
    pytest.skip("WP-00 contracts not available", allow_module_level=True)
OPENAPI: Path = (_FOUND or Path()) / "openapi"
METHODS = ("get", "post", "put", "patch", "delete")
ADR_SCOPES = {
    "collector:read",
    "collector:run",
    "handler:invoke",
    "handler:test",
    "connections:write",
    "storage:read",
    "registry:read",
    "registry:write",
    "registry:approve",
    "orchestrator:read",
    "orchestrator:write",
    "orchestrator:admin",
    "llm:invoke",
    "llm:admin",
    "assistant:use",
}


def _load(name: str) -> dict[str, Any]:
    doc: dict[str, Any] = yaml.safe_load((OPENAPI / name).read_text(encoding="utf-8"))
    return doc


def operations(api: str) -> set[str]:
    """``METHOD /path`` of the contract, path items from common.yaml resolved; health/info excluded."""
    common = _load("common.yaml")["components"]["pathItems"]
    out: set[str] = set()
    for path, item in _load(f"{api}.v1.yaml")["paths"].items():
        if "$ref" in item:
            name = item["$ref"].rsplit("/", 1)[-1]
            if name in {"Health", "Info"}:
                continue
            item = common[name]
        out |= {f"{m.upper()} {path}" for m in METHODS if m in item}
    return out


@pytest.mark.parametrize("api", sorted(TABLES))
def test_table_equals_contract(api: str) -> None:
    assert set(TABLES[api]) == operations(api)


def test_only_adr_scopes_are_used() -> None:
    used = {
        s for table in TABLES.values() for v in table.values() for s in ((v,) if isinstance(v, str) else v)
    }
    assert used <= ADR_SCOPES and all(SCOPE_RE.match(s) for s in used)
    assert all(v for table in TABLES.values() for v in table.values())  # no "any token" operation


def test_merge_unions_shared_operations() -> None:
    merged = merge(HANDLER, LLM)
    assert merged["GET /v1/jobs/{job_id}"] == ("handler:invoke", "handler:test", "llm:admin", "llm:invoke")
    assert merged["POST /v1/completions"] == ("llm:invoke",)
