# Модуль `jane_kit.auth_scopes`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/auth_scopes.py](../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py). Не редагуйте вручну.

Scopes of every operation of Jane's contracts (ADR-0005 §3), one table per API.

A service passes the tables of the APIs it implements to ``create_app(auth_scopes=...)``, merged with :func:`merge` (storage = ``merge(HANDLER, STORAGE)``, llm = ``merge(HANDLER, LLM)``). Keys are ``"METHOD /path"`` exactly as in ``contracts/openapi/<api>.v1.yaml``; ``tests/test_auth_scopes.py`` keeps each table equal to its contract: the same operations and, for each, the scopes of its ``x-jane-scope``. A value is one scope or a tuple meaning "any of".

Rules behind the choices that ADR-0005 leaves open:

* reading connection definitions (no secret values) - ``connections:write`` or the executor's basic scope (``collector:read`` / ``handler:invoke``); changing and testing them - ``connections:write``;
* ``/v1/jobs`` - whoever may start the operations whose jobs the service runs (``handler:invoke`` or ``handler:test``, ``llm:invoke``...); cancelling a collection needs ``collector:run``;
* rules validation is a read-only check (``collector:read`` or ``collector:run``); resetting collector state changes what the next run collects (``collector:run``);
* llm providers and aliases are readable with ``llm:invoke`` (callers choose a model alias), budgets and usage only with ``llm:admin``;
* orchestrator: ``orchestrator:admin`` also grants read and write (as the orchestrator always did).

## Функції

### Функція `merge`

```python
def merge(*tables: Mapping[str, str | Sequence[str]]) -> dict[str, tuple[str, ...]]: ...
```

Tables of several APIs one service implements; an operation present in several gets the union.

Код: [auth_scopes.py:190](../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L190).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ASSISTANT` | `dict[str, Scopes]` | `{'GET /v1/onboarding-sessions': 'assistant:use', 'POST /v1/onboarding-sessions':` |  |
| `COLLECTOR` | `dict[str, Scopes]` | `{'POST /v1/fetches': 'collector:run', 'POST /v1/collections': 'collector:run', '` |  |
| `HANDLER` | `dict[str, Scopes]` | `{'POST /v1/invocations': 'handler:invoke', 'GET /v1/invocations/{invocation_id}'` |  |
| `LLM` | `dict[str, Scopes]` | `{'GET /v1/providers': _LLM_READ, 'GET /v1/providers/{provider_id}': _LLM_READ, '` |  |
| `ORCHESTRATOR` | `dict[str, Scopes]` | `{'GET /v1/sources': _O_READ, 'POST /v1/sources': _O_WRITE, 'GET /v1/sources/{sou` |  |
| `REGISTRY` | `dict[str, Scopes]` | `{'GET /v1/packages': 'registry:read', 'POST /v1/packages': 'registry:write', 'GE` |  |
| `STORAGE` | `dict[str, Scopes]` | `{'GET /v1/entities': 'storage:read', 'GET /v1/entity-history': 'storage:read', '` |  |
| `TABLES` | `dict[str, dict[str, Scopes]]` | `{'collector': COLLECTOR, 'handler': HANDLER, 'storage': STORAGE, 'llm': LLM, 'as` | Contract name (``contracts/openapi/<name>.v1.yaml``) -> its table. |
