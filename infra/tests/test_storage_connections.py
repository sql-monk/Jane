"""Storage connections of the dev stack (no stack needed): every document of ``infra/config/storage-connections.json``
is a valid contract Connection, passes the real Storage connection registry under the environment that
``infra/compose.yaml`` gives the storage container (secret policy, host allowlist, every ``secret_refs`` resolvable),
and compose starts the databases the connections address together with storage."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from jane_kit.schemas import ContractSchemas
from jane_storage.connections import ConnectionRegistry
from jane_storage.settings import Settings

ROOT = Path(__file__).resolve().parents[2]
COMPOSE: dict[str, Any] = yaml.safe_load((ROOT / "infra" / "compose.yaml").read_text(encoding="utf-8"))
CONNECTIONS_FILE = ROOT / "infra" / "config" / "storage-connections.json"
CONNECTIONS: list[dict[str, Any]] = json.loads(CONNECTIONS_FILE.read_text(encoding="utf-8"))["connections"]
CONNECTION_IDS = [str(c["connection_id"]) for c in CONNECTIONS]
VAR = re.compile(r"\$\{(?P<name>[A-Z0-9_]+)(?::?[-?][^}]*)?\}")


def storage_environment() -> dict[str, str]:
    """Environment of the storage container; each stack variable ``${X...}`` becomes ``value-of-X``."""
    env = COMPOSE["services"]["storage"]["environment"]
    return {str(k): VAR.sub(lambda m: f"value-of-{m.group('name')}", str(v)) for k, v in env.items()}


def registry() -> ConnectionRegistry:
    env = storage_environment()
    settings = Settings(connection_host_allowlist=json.loads(env["JANE_STORAGE_CONNECTION_HOST_ALLOWLIST"]))
    reg = ConnectionRegistry(policy=settings.connection_policy(), environ=env)
    assert reg.load_file(CONNECTIONS_FILE) == len(CONNECTIONS)
    return reg


def started_with(service: str) -> set[str]:
    """Services compose starts together with ``service`` (transitive ``depends_on``)."""
    out: set[str] = set()
    todo = [service]
    while todo:
        for dep in COMPOSE["services"][todo.pop()].get("depends_on") or {}:
            if dep not in out:
                out.add(dep)
                todo.append(dep)
    return out


@pytest.mark.parametrize("index", range(len(CONNECTIONS)), ids=CONNECTION_IDS)
def test_dev_connection_is_a_contract_connection(index: int) -> None:
    errors = ContractSchemas(ROOT / "contracts").iter_errors(
        "common/connection.schema.json", CONNECTIONS[index]
    )
    assert [e.message for e in errors] == []


@pytest.mark.parametrize("connection_id", CONNECTION_IDS)
def test_dev_connection_resolves_in_the_storage_container(connection_id: str) -> None:
    reg = registry()
    assert reg.policy_errors(connection_id) == []
    assert all(reg.resolve(connection_id).secrets.values())


def test_results_mongo_uses_the_mongodb_of_the_stack() -> None:
    """Entities whose fields a package defines (plan docs/delivery/mongo-entities.md): database ``jane_results``,
    the adapter's default (empty) collection prefix, the stack's MongoDB user."""
    resolved = registry().resolve("results-mongo")
    assert resolved.kind == "mongodb"
    assert resolved.params == {
        "host": "mongodb",
        "port": 27017,
        "database": "jane_results",
        "auth_source": "admin",
    }
    assert resolved.secrets == {
        "username": "value-of-JANE_MONGO_USER",
        "password": "value-of-JANE_MONGO_PASSWORD",
    }


def test_compose_starts_the_databases_of_the_connections_with_storage() -> None:
    hosts = {str(c["params"]["host"]) for c in CONNECTIONS if "host" in (c.get("params") or {})}
    assert hosts == {"postgres", "mongodb"}
    assert hosts <= started_with("storage")
    assert COMPOSE["services"]["storage"]["depends_on"]["mongodb"] == {"condition": "service_healthy"}
