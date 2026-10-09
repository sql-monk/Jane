"""The scope tables of jane_kit.auth_scopes match each contract (ADR-0005 §3): the same operations, and for
every operation the same scopes as its ``x-jane-scope`` in ``contracts/openapi/<api>.v1.yaml``.

``x-jane-scope`` (contracts README, skill ``jane-contracts`` rule 10): a string is one scope, an array means
"any one of" (order does not matter), ``[]`` - any valid token (only the shared ``common.yaml`` Health/Info
path items; health additionally has ``security: []``). Path items an API takes by ``$ref`` from
``common.yaml`` are resolved; a shared item carries no API-specific scope, so an API expands it (Job,
Connections...) and declares the scope on its own copy.
"""

from __future__ import annotations

import copy
import functools
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest
import yaml

from jane_kit.auth import AUTHENTICATED, BUILTIN_SCOPES, OPEN_PATHS, SCOPE_RE
from jane_kit.auth_scopes import COLLECTOR, HANDLER, LLM, ORCHESTRATOR, TABLES, merge
from jane_kit.contracts import contracts_dir

pytestmark = pytest.mark.contract

_FOUND = contracts_dir(Path(__file__).parent)
if _FOUND is None or not (_FOUND / "openapi" / "common.yaml").is_file():
    pytest.skip("WP-00 contracts not available", allow_module_level=True)
OPENAPI: Path = (_FOUND or Path()) / "openapi"
METHODS = ("get", "post", "put", "patch", "delete")
SYSTEM = {"Health", "Info"}  # common.yaml path items outside the scope tables (jane_kit.auth handles them)
SCOPE_KEY = "x-jane-scope"
MISSING = object()
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
# Services that implement several contracts pass merge() of their tables to create_app (auth_scopes docstring).
MERGED_SERVICES = {"storage": ("handler", "storage"), "llm": ("handler", "llm")}


@functools.cache
def _load(name: str) -> dict[str, Any]:
    doc: dict[str, Any] = yaml.safe_load((OPENAPI / name).read_text(encoding="utf-8"))
    return doc


def _resolve(doc: str, item: Mapping[str, Any]) -> tuple[Mapping[str, Any], str | None]:
    """Follow a path item ``$ref`` (``file#/pointer`` or ``#/pointer``) -> (item, the ref it came from)."""
    origin: str | None = None
    for _ in range(8):
        ref = item.get("$ref")
        if not isinstance(ref, str):
            return item, origin
        file, _, pointer = ref.partition("#")
        doc = file or doc
        node: Any = _load(doc)
        for token in pointer.lstrip("/").split("/"):
            node = node[token.replace("~1", "/").replace("~0", "~")]
        item, origin = node, f"{Path(doc).name}#{pointer}"
    raise AssertionError(f"path item $ref chain too long in {doc}")


def _shared_name(origin: str | None) -> str | None:
    """``common.yaml#/components/pathItems/Job`` -> ``Job``."""
    if origin and origin.startswith("common.yaml#/components/pathItems/"):
        return origin.rsplit("/", 1)[-1]
    return None


Walked = Iterator[tuple[str, str, Mapping[str, Any], str | None]]


def _walk_paths(doc: str, paths: Mapping[str, Mapping[str, Any]]) -> Walked:
    """(``METHOD /path``, path, operation, the ref of the path item it comes from) of every operation."""
    for path, raw in paths.items():
        item, origin = _resolve(doc, raw)
        for method in METHODS:
            if method in item:
                yield f"{method.upper()} {path}", path, item[method], origin


def _walk(api: str) -> Walked:
    name = f"{api}.v1.yaml"
    return _walk_paths(name, _load(name)["paths"])


def operations(api: str) -> set[str]:
    """``METHOD /path`` of the contract, path items from common.yaml resolved; health/info excluded."""
    return {key for key, _, _, origin in _walk(api) if _shared_name(origin) not in SYSTEM}


def contract_scopes(api: str) -> dict[str, Any]:
    """``METHOD /path`` -> ``x-jane-scope`` as written (``MISSING`` when absent); health/info excluded."""
    return {
        key: op.get(SCOPE_KEY, MISSING)
        for key, _, op, origin in _walk(api)
        if _shared_name(origin) not in SYSTEM
    }


def any_of(value: object) -> frozenset[str] | None:
    """A table value or an ``x-jane-scope`` -> the scopes any one of which grants access (empty = any valid
    token); ``None`` when it is absent or not a scope / a list of distinct scopes."""
    if isinstance(value, str):
        return frozenset({value})
    if (
        isinstance(value, Sequence)
        and all(isinstance(s, str) for s in value)
        and len(set(value)) == len(value)
    ):
        return frozenset(value)
    return None


def scope_mismatches(
    table: Mapping[str, object], contract: Mapping[str, object]
) -> dict[str, tuple[object, object]]:
    """Operations whose any-of scope sets differ (or that only one side has): key -> (table, contract)."""
    out: dict[str, tuple[object, object]] = {}
    for key in sorted(set(table) | set(contract)):
        mine, theirs = table.get(key, MISSING), contract.get(key, MISSING)
        if mine is MISSING or theirs is MISSING or any_of(mine) is None or any_of(mine) != any_of(theirs):
            out[key] = (mine, theirs)
    return out


def _union(*contracts: Mapping[str, object]) -> dict[str, frozenset[str]]:
    out: dict[str, frozenset[str]] = {}
    for contract in contracts:
        for key, value in contract.items():
            out[key] = out.get(key, frozenset()) | (any_of(value) or frozenset())
    return out


@pytest.mark.parametrize("api", sorted(TABLES))
def test_table_equals_contract(api: str) -> None:
    assert set(TABLES[api]) == operations(api)


@pytest.mark.parametrize("api", sorted(TABLES))
def test_every_operation_declares_its_scopes(api: str) -> None:
    """Every operation except health/info has a non-empty ``x-jane-scope`` of ADR scopes. An operation taken
    as is from a shared common.yaml path item (Job, Connections...) has none: expand the item instead."""
    bad = []
    for key, _, op, origin in _walk(api):
        if _shared_name(origin) in SYSTEM:
            continue
        value = op.get(SCOPE_KEY, MISSING)
        scopes = any_of(value)
        if not scopes or not scopes <= ADR_SCOPES or op.get("security") == []:
            source = f" (shared path item {origin})" if origin else ""
            shown = "<absent>" if value is MISSING else repr(value)
            bad.append(f"{key}{source}: x-jane-scope={shown}, security={op.get('security', '<inherited>')!r}")
    assert bad == []


@pytest.mark.parametrize("api", sorted(TABLES))
def test_table_scopes_equal_contract(api: str) -> None:
    """R32: not just the same operations - the same scope (any-of set) for each of them."""
    assert scope_mismatches(TABLES[api], contract_scopes(api)) == {}


@pytest.mark.parametrize("service", sorted(MERGED_SERVICES))
def test_merged_service_table_equals_union_of_its_contracts(service: str) -> None:
    """An operation present in several contracts of one service (``/v1/jobs`` of llm + handler) gets the union."""
    apis = MERGED_SERVICES[service]
    merged = merge(*(TABLES[api] for api in apis))
    expected = _union(*(contract_scopes(api) for api in apis))
    assert set(merged) == set(expected)
    assert {k: frozenset(v) for k, v in merged.items()} == expected


@pytest.mark.parametrize("api", sorted(TABLES))
def test_health_and_info_match_jane_kit(api: str) -> None:
    """The shared Health/Info items: ``x-jane-scope: []``; health is open (``security: []``, OPEN_PATHS), info
    needs any valid token (inherits bearerAuth, BUILTIN_SCOPES = AUTHENTICATED)."""
    system = {
        name: (key, path, op)
        for key, path, op, origin in _walk(api)
        if (name := _shared_name(origin)) in SYSTEM
    }
    assert set(system) == SYSTEM
    key, path, health = system["Health"]
    assert key == "GET /v1/health"
    assert health.get(SCOPE_KEY, MISSING) == []
    assert health.get("security") == []
    assert path in OPEN_PATHS
    key, _, info = system["Info"]
    assert key == "GET /v1/info"
    assert info.get(SCOPE_KEY, MISSING) == []
    assert "security" not in info
    assert _load(f"{api}.v1.yaml")["security"] == [{"bearerAuth": []}]
    assert BUILTIN_SCOPES[key] == AUTHENTICATED


def test_comparison_catches_changed_scopes() -> None:
    """Guard against a vacuous comparison: each mutant of a real table is reported, and only it."""
    mutants: list[tuple[str, dict[str, Any], str, object]] = [
        ("collector", COLLECTOR, "POST /v1/collections", "collector:read"),  # other scope
        ("orchestrator", ORCHESTRATOR, "GET /v1/sources", ("orchestrator:read",)),  # any-of lost a scope
        ("handler", HANDLER, "POST /v1/test-runs", ("handler:test", "handler:invoke")),  # any-of gained one
        ("handler", HANDLER, "GET /v1/jobs/{job_id}", "handler:invoke"),  # expanded common Job item
        ("llm", LLM, "GET /v1/providers", ()),  # "any valid token"
    ]
    for api, table, key, value in mutants:
        mutated = copy.deepcopy(table)
        mutated[key] = value
        assert set(scope_mismatches(mutated, contract_scopes(api))) == {key}, (api, key, value)
    contract = contract_scopes("storage")
    contract["GET /v1/entities"] = MISSING
    assert set(scope_mismatches(TABLES["storage"], contract)) == {"GET /v1/entities"}
    # A shared common.yaml item taken by $ref without expanding it carries no scope of this API.
    shared = {
        "/v1/health": {"$ref": "common.yaml#/components/pathItems/Health"},
        "/v1/jobs/{job_id}": {"$ref": "./common.yaml#/components/pathItems/Job"},
    }
    found = {
        key: (op.get(SCOPE_KEY, MISSING), _shared_name(origin))
        for key, _, op, origin in _walk_paths("handler.v1.yaml", shared)
    }
    assert found == {"GET /v1/health": ([], "Health"), "GET /v1/jobs/{job_id}": (MISSING, "Job")}
    # Order inside an any-of does not matter, a string equals a one-item list.
    assert (
        scope_mismatches(
            {"GET /x": ("a:b", "c:d"), "GET /y": "e:f"}, {"GET /x": ["c:d", "a:b"], "GET /y": ["e:f"]}
        )
        == {}
    )


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
