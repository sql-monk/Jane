"""ADR-0005 configuration of the stacks (no stack needed): every application service of ``infra/compose.yaml``
runs in ``auth_mode=api_key`` with valid keys, scopes that exist in its API, a full-scope admin key, and the
generators of the keys (``scripts/dev.py``, ``jane_kit.devstack``) agree on the identities."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

from jane_kit.auth import ApiKeyConfig
from jane_kit.auth_scopes import ASSISTANT, COLLECTOR, HANDLER, LLM, ORCHESTRATOR, REGISTRY, STORAGE, merge
from jane_kit.devstack import STACK_IDENTITIES, api_key_var, new_api_keys

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = yaml.safe_load((ROOT / "infra" / "compose.yaml").read_text(encoding="utf-8"))
TABLES = {
    "storage": merge(HANDLER, STORAGE),
    "handler-runtime": merge(HANDLER),
    "llm": merge(HANDLER, LLM),
    "web-collector": merge(COLLECTOR),
    "telegram-collector": merge(COLLECTOR),
    "orchestrator": merge(ORCHESTRATOR),
    "registry": merge(REGISTRY),
    "assistant": merge(ASSISTANT),
}
VAR = re.compile(r"\$\{(?P<name>[A-Z0-9_]+)(?::?[-?][^}]*)?\}")


def load_dev(path: Path = ROOT / "scripts" / "dev.py") -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"jane_auth_copy_{path.parent.name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def interpolate(value: str, env: dict[str, str]) -> str:
    return VAR.sub(lambda m: env[m.group("name")], value)


def service_env(name: str) -> dict[str, Any]:
    env = COMPOSE["services"][name].get("environment") or {}
    assert isinstance(env, dict), name
    return env


@pytest.mark.parametrize("copy", ["scripts/dev.py", "deploy/profiles/stack.py"])
def test_generators_agree(copy: str) -> None:
    """The stdlib copies (``just up``, ``deploy/profiles/stack.py``) generate the same variables as jane-kit."""
    module = load_dev(ROOT / copy)
    assert module.STACK_IDENTITIES == STACK_IDENTITIES
    generated = module.new_api_keys()
    assert set(generated) == set(new_api_keys())
    assert module.new_api_keys(generated) == new_api_keys(generated)  # same hashes, existing keys are kept


@pytest.mark.parametrize("service", sorted(TABLES))
def test_service_runs_with_api_keys(service: str) -> None:
    env = service_env(service)
    prefix = "JANE_" + service.upper().replace("-", "_") + "_"
    assert env[f"{prefix}AUTH_MODE"] == "api_key"
    keys = new_api_keys()
    entries = json.loads(interpolate(env[f"{prefix}API_KEYS"], keys))
    parsed = [ApiKeyConfig.model_validate(e) for e in entries]
    known = {s for scopes in TABLES[service].values() for s in scopes}
    by_name = {k.name: k for k in parsed}
    assert set(by_name) <= set(STACK_IDENTITIES)
    for key in parsed:
        assert set(key.scopes) <= known, (service, key.name, set(key.scopes) - known)
        assert key.sha256 == keys[f"{api_key_var(key.name)}_SHA256"]
    # the operator's key (admin UI, e2e harness) can call every operation of the service
    assert set(by_name["admin"].scopes) == known
    # no secret values in the file: only references to generated variables
    assert not re.search(r"[0-9a-f]{64}", yaml.safe_dump(env))


def test_service_tokens_are_accepted_by_their_neighbours() -> None:
    """Every service that calls a neighbour with its own key is configured at that neighbour."""
    accepted = {
        service: {
            e["name"]
            for e in json.loads(
                interpolate(
                    service_env(service)[f"JANE_{service.upper().replace('-', '_')}_API_KEYS"], new_api_keys()
                )
            )
        }
        for service in TABLES
    }
    callers = {
        "orchestrator": [
            "storage",
            "handler-runtime",
            "web-collector",
            "telegram-collector",
            "registry",
            "llm",
        ],
        "assistant": ["llm", "registry", "handler-runtime", "storage", "web-collector", "orchestrator"],
        "handler-runtime": ["registry"],
        "storage": ["registry"],
        "llm": ["registry"],
        "web-collector": ["registry"],
        "telegram-collector": ["registry"],
        "registry": ["handler-runtime"],
    }
    for caller, neighbours in callers.items():
        own = f"${{{api_key_var(caller)}:?run `just up`}}"
        assert own in yaml.safe_dump(service_env(caller), width=1000), caller
        for neighbour in neighbours:
            assert caller in accepted[neighbour], (caller, neighbour)
