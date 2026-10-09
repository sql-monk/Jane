"""Scopes of every operation of Jane's contracts (ADR-0005 §3), one table per API.

A service passes the tables of the APIs it implements to ``create_app(auth_scopes=...)``, merged with
:func:`merge` (storage = ``merge(HANDLER, STORAGE)``, llm = ``merge(HANDLER, LLM)``). Keys are
``"METHOD /path"`` exactly as in ``contracts/openapi/<api>.v1.yaml``; ``tests/test_auth_scopes.py`` keeps
each table equal to its contract: the same operations and, for each, the scopes of its ``x-jane-scope``.
A value is one scope or a tuple meaning "any of".

Rules behind the choices that ADR-0005 leaves open:

* reading connection definitions (no secret values) - ``connections:write`` or the executor's basic scope
  (``collector:read`` / ``handler:invoke``); changing and testing them - ``connections:write``;
* ``/v1/jobs`` - whoever may start the operations whose jobs the service runs (``handler:invoke`` or
  ``handler:test``, ``llm:invoke``...); cancelling a collection needs ``collector:run``;
* rules validation is a read-only check (``collector:read`` or ``collector:run``); resetting collector state
  changes what the next run collects (``collector:run``);
* llm providers and aliases are readable with ``llm:invoke`` (callers choose a model alias), budgets and usage
  only with ``llm:admin``;
* orchestrator: ``orchestrator:admin`` also grants read and write (as the orchestrator always did).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

__all__ = [
    "ASSISTANT",
    "COLLECTOR",
    "HANDLER",
    "LLM",
    "ORCHESTRATOR",
    "REGISTRY",
    "STORAGE",
    "TABLES",
    "merge",
]

Scopes = str | tuple[str, ...]


def _connections(*read: str) -> dict[str, Scopes]:
    """``common.yaml`` Connections / Connection / ConnectionTest path items."""
    readers = ("connections:write", *read)
    return {
        "GET /v1/connections": readers,
        "GET /v1/connections/{connection_id}": readers,
        "PUT /v1/connections/{connection_id}": "connections:write",
        "DELETE /v1/connections/{connection_id}": "connections:write",
        "POST /v1/connections/{connection_id}/test": "connections:write",
    }


def _jobs(read: Scopes, cancel: Scopes) -> dict[str, Scopes]:
    """``common.yaml`` Job / JobCancel path items."""
    return {"GET /v1/jobs/{job_id}": read, "POST /v1/jobs/{job_id}/cancel": cancel}


COLLECTOR: dict[str, Scopes] = {
    "POST /v1/fetches": "collector:run",
    "POST /v1/collections": "collector:run",
    "GET /v1/collections/{collection_id}": "collector:read",
    "GET /v1/collections/{collection_id}/materials": "collector:read",
    "GET /v1/collections/{collection_id}/errors": "collector:read",
    "POST /v1/rules/validations": ("collector:read", "collector:run"),
    "GET /v1/states/{state_key}": "collector:read",
    "DELETE /v1/states/{state_key}": "collector:run",
    **_connections("collector:read"),
    **_jobs("collector:read", "collector:run"),
}

_HANDLER_ANY = ("handler:invoke", "handler:test")
HANDLER: dict[str, Scopes] = {
    "POST /v1/invocations": "handler:invoke",
    "GET /v1/invocations/{invocation_id}": "handler:invoke",
    "POST /v1/test-runs": "handler:test",
    **_connections("handler:invoke"),
    **_jobs(_HANDLER_ANY, _HANDLER_ANY),
}

STORAGE: dict[str, Scopes] = {
    "GET /v1/entities": "storage:read",
    "GET /v1/entity-history": "storage:read",
    "GET /v1/objects": "storage:read",
    "GET /v1/objects/{object_id}": "storage:read",
    "GET /v1/objects/{object_id}/content": "storage:read",
}

_LLM_READ = ("llm:admin", "llm:invoke")
LLM: dict[str, Scopes] = {
    "GET /v1/providers": _LLM_READ,
    "GET /v1/providers/{provider_id}": _LLM_READ,
    "PUT /v1/providers/{provider_id}": "llm:admin",
    "DELETE /v1/providers/{provider_id}": "llm:admin",
    "GET /v1/model-aliases": _LLM_READ,
    "PUT /v1/model-aliases/{alias}": "llm:admin",
    "POST /v1/completions": "llm:invoke",
    "GET /v1/budgets": "llm:admin",
    "PUT /v1/budgets/{scope_type}/{scope_id}": "llm:admin",
    "DELETE /v1/budgets/{scope_type}/{scope_id}": "llm:admin",
    "GET /v1/usage": "llm:admin",
    **_jobs(_LLM_READ, _LLM_READ),
}

ASSISTANT: dict[str, Scopes] = {
    "GET /v1/onboarding-sessions": "assistant:use",
    "POST /v1/onboarding-sessions": "assistant:use",
    "GET /v1/onboarding-sessions/{session_id}": "assistant:use",
    "POST /v1/onboarding-sessions/{session_id}/candidate-selection": "assistant:use",
    "POST /v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance": "assistant:use",
    "GET /v1/improvement-runs": "assistant:use",
    "POST /v1/improvement-runs": "assistant:use",
    "POST /v1/unknown-materials": "assistant:use",
    **_jobs("assistant:use", "assistant:use"),
}

REGISTRY: dict[str, Scopes] = {
    "GET /v1/packages": "registry:read",
    "POST /v1/packages": "registry:write",
    "GET /v1/packages/{package_id}": "registry:read",
    "PATCH /v1/packages/{package_id}": "registry:write",
    "GET /v1/packages/{package_id}/versions": "registry:read",
    "POST /v1/packages/{package_id}/versions": "registry:write",
    "GET /v1/packages/{package_id}/versions/{version}": "registry:read",
    "GET /v1/packages/{package_id}/versions/{version}/archive": "registry:read",
    "GET /v1/packages/{package_id}/versions/{version}/file": "registry:read",
    "POST /v1/packages/{package_id}/versions/{version}/status": "registry:approve",
    "POST /v1/packages/{package_id}/versions/{version}/test-results": "registry:write",
    "POST /v1/packages/{package_id}/forks": "registry:write",
    "GET /v1/packages/{package_id}/diff": "registry:read",
    "GET /v1/packages/{package_id}/upstream": "registry:read",
    "POST /v1/packages/{package_id}/upstream-ports": "registry:write",
    **_jobs("registry:read", "registry:write"),
}

_O_READ = ("orchestrator:read", "orchestrator:admin")
_O_WRITE = ("orchestrator:write", "orchestrator:admin")
_O_ADMIN = "orchestrator:admin"
ORCHESTRATOR: dict[str, Scopes] = {
    "GET /v1/sources": _O_READ,
    "POST /v1/sources": _O_WRITE,
    "GET /v1/sources/{source_id}": _O_READ,
    "PUT /v1/sources/{source_id}": _O_WRITE,
    "DELETE /v1/sources/{source_id}": _O_WRITE,
    "GET /v1/tasks": _O_READ,
    "POST /v1/tasks": _O_WRITE,
    "GET /v1/tasks/{task_id}": _O_READ,
    "PUT /v1/tasks/{task_id}": _O_WRITE,
    "DELETE /v1/tasks/{task_id}": _O_WRITE,
    "POST /v1/task-validations": _O_READ,
    "POST /v1/tasks/{task_id}/runs": _O_WRITE,
    "GET /v1/tasks/{task_id}/stages/{stage_id}/activations": _O_READ,
    "POST /v1/tasks/{task_id}/stages/{stage_id}/activations": _O_WRITE,
    "GET /v1/runs": _O_READ,
    "GET /v1/runs/{run_id}": _O_READ,
    "POST /v1/runs/{run_id}/cancel": _O_WRITE,
    "GET /v1/runs/{run_id}/items": _O_READ,
    "GET /v1/materials/{material_id}/trace": _O_READ,
    "GET /v1/unknown-materials": _O_READ,
    "GET /v1/problem-groups": _O_READ,
    "PATCH /v1/problem-groups/{group_id}": _O_WRITE,
    "POST /v1/reprocessing": _O_WRITE,
    "GET /v1/connections": _O_READ,
    "GET /v1/connections/{connection_id}": _O_READ,
    "PUT /v1/connections/{connection_id}": _O_ADMIN,
    "DELETE /v1/connections/{connection_id}": _O_ADMIN,
    "GET /v1/limits/platform": _O_READ,
    "PUT /v1/limits/platform": _O_ADMIN,
    "GET /v1/limits/effective": _O_READ,
    "GET /v1/executors": _O_READ,
    "GET /v1/audit-events": _O_READ,
    **_jobs(_O_READ, _O_WRITE),
}

TABLES: dict[str, dict[str, Scopes]] = {
    "collector": COLLECTOR,
    "handler": HANDLER,
    "storage": STORAGE,
    "llm": LLM,
    "assistant": ASSISTANT,
    "registry": REGISTRY,
    "orchestrator": ORCHESTRATOR,
}
"""Contract name (``contracts/openapi/<name>.v1.yaml``) -> its table."""


def _as_tuple(value: str | Sequence[str]) -> tuple[str, ...]:
    return (value,) if isinstance(value, str) else tuple(value)


def merge(*tables: Mapping[str, str | Sequence[str]]) -> dict[str, tuple[str, ...]]:
    """Tables of several APIs one service implements; an operation present in several gets the union."""
    out: dict[str, tuple[str, ...]] = {}
    for table in tables:
        for key, value in table.items():
            out[key] = tuple(dict.fromkeys((*out.get(key, ()), *_as_tuple(value))))
    return out
