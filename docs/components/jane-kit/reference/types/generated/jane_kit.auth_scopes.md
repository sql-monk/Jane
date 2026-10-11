# jane_kit.auth_scopes

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.auth_scopes.COLLECTOR](#jane_kitauth_scopescollector)
- [jane_kit.auth_scopes.HANDLER](#jane_kitauth_scopeshandler)
- [jane_kit.auth_scopes.STORAGE](#jane_kitauth_scopesstorage)
- [jane_kit.auth_scopes.LLM](#jane_kitauth_scopesllm)
- [jane_kit.auth_scopes.ASSISTANT](#jane_kitauth_scopesassistant)
- [jane_kit.auth_scopes.REGISTRY](#jane_kitauth_scopesregistry)
- [jane_kit.auth_scopes.ORCHESTRATOR](#jane_kitauth_scopesorchestrator)
- [jane_kit.auth_scopes.TABLES](#jane_kitauth_scopestables)
- [jane_kit.auth_scopes.merge](#jane_kitauth_scopesmerge)

## jane_kit.auth_scopes.COLLECTOR

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:58](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L58).

```python
COLLECTOR: dict[str, Scopes] = {'POST /v1/fetches': 'collector:run', 'POST /v1/collections': 'collector:run', 'GET /v1/collections/{collection_id}': 'collector:read', 'GET /v1/collections/{collection_id}/materials': 'collector:read', 'GET /v1/collections/{collection_id}/errors': 'collector:read', 'POST /v1/rules/validations': ('collector:read', 'collector:run'), 'GET /v1/states/{state_key}': 'collector:read', 'DELETE /v1/states/{state_key}': 'collector:run', **_connections('collector:read'), **_jobs('collector:read', 'collector:run')}
```

## jane_kit.auth_scopes.HANDLER

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:72](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L72).

```python
HANDLER: dict[str, Scopes] = {'POST /v1/invocations': 'handler:invoke', 'GET /v1/invocations/{invocation_id}': 'handler:invoke', 'POST /v1/test-runs': 'handler:test', **_connections('handler:invoke'), **_jobs(_HANDLER_ANY, _HANDLER_ANY)}
```

## jane_kit.auth_scopes.STORAGE

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:80](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L80).

```python
STORAGE: dict[str, Scopes] = {'GET /v1/entities': 'storage:read', 'GET /v1/entity-history': 'storage:read', 'GET /v1/objects': 'storage:read', 'GET /v1/objects/{object_id}': 'storage:read', 'GET /v1/objects/{object_id}/content': 'storage:read'}
```

## jane_kit.auth_scopes.LLM

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:89](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L89).

```python
LLM: dict[str, Scopes] = {'GET /v1/providers': _LLM_READ, 'GET /v1/providers/{provider_id}': _LLM_READ, 'PUT /v1/providers/{provider_id}': 'llm:admin', 'DELETE /v1/providers/{provider_id}': 'llm:admin', 'GET /v1/model-aliases': _LLM_READ, 'PUT /v1/model-aliases/{alias}': 'llm:admin', 'POST /v1/completions': 'llm:invoke', 'GET /v1/budgets': 'llm:admin', 'PUT /v1/budgets/{scope_type}/{scope_id}': 'llm:admin', 'DELETE /v1/budgets/{scope_type}/{scope_id}': 'llm:admin', 'GET /v1/usage': 'llm:admin', **_jobs(_LLM_READ, _LLM_READ)}
```

## jane_kit.auth_scopes.ASSISTANT

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:104](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L104).

```python
ASSISTANT: dict[str, Scopes] = {'GET /v1/onboarding-sessions': 'assistant:use', 'POST /v1/onboarding-sessions': 'assistant:use', 'GET /v1/onboarding-sessions/{session_id}': 'assistant:use', 'POST /v1/onboarding-sessions/{session_id}/candidate-selection': 'assistant:use', 'POST /v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance': 'assistant:use', 'GET /v1/improvement-runs': 'assistant:use', 'POST /v1/improvement-runs': 'assistant:use', 'POST /v1/unknown-materials': 'assistant:use', **_jobs('assistant:use', 'assistant:use')}
```

## jane_kit.auth_scopes.REGISTRY

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:116](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L116).

```python
REGISTRY: dict[str, Scopes] = {'GET /v1/packages': 'registry:read', 'POST /v1/packages': 'registry:write', 'GET /v1/packages/{package_id}': 'registry:read', 'PATCH /v1/packages/{package_id}': 'registry:write', 'GET /v1/packages/{package_id}/versions': 'registry:read', 'POST /v1/packages/{package_id}/versions': 'registry:write', 'GET /v1/packages/{package_id}/versions/{version}': 'registry:read', 'GET /v1/packages/{package_id}/versions/{version}/archive': 'registry:read', 'GET /v1/packages/{package_id}/versions/{version}/file': 'registry:read', 'POST /v1/packages/{package_id}/versions/{version}/status': 'registry:approve', 'POST /v1/packages/{package_id}/versions/{version}/test-results': 'registry:write', 'POST /v1/packages/{package_id}/forks': 'registry:write', 'GET /v1/packages/{package_id}/diff': 'registry:read', 'GET /v1/packages/{package_id}/upstream': 'registry:read', 'POST /v1/packages/{package_id}/upstream-ports': 'registry:write', **_jobs('registry:read', 'registry:write')}
```

## jane_kit.auth_scopes.ORCHESTRATOR

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:138](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L138).

```python
ORCHESTRATOR: dict[str, Scopes] = {'GET /v1/sources': _O_READ, 'POST /v1/sources': _O_WRITE, 'GET /v1/sources/{source_id}': _O_READ, 'PUT /v1/sources/{source_id}': _O_WRITE, 'DELETE /v1/sources/{source_id}': _O_WRITE, 'GET /v1/tasks': _O_READ, 'POST /v1/tasks': _O_WRITE, 'GET /v1/tasks/{task_id}': _O_READ, 'PUT /v1/tasks/{task_id}': _O_WRITE, 'DELETE /v1/tasks/{task_id}': _O_WRITE, 'POST /v1/task-validations': _O_READ, 'POST /v1/tasks/{task_id}/runs': _O_WRITE, 'GET /v1/tasks/{task_id}/stages/{stage_id}/activations': _O_READ, 'POST /v1/tasks/{task_id}/stages/{stage_id}/activations': _O_WRITE, 'GET /v1/runs': _O_READ, 'GET /v1/runs/{run_id}': _O_READ, 'POST /v1/runs/{run_id}/cancel': _O_WRITE, 'GET /v1/runs/{run_id}/items': _O_READ, 'GET /v1/materials/{material_id}/trace': _O_READ, 'GET /v1/unknown-materials': _O_READ, 'GET /v1/problem-groups': _O_READ, 'PATCH /v1/problem-groups/{group_id}': _O_WRITE, 'POST /v1/reprocessing': _O_WRITE, 'GET /v1/connections': _O_READ, 'GET /v1/connections/{connection_id}': _O_READ, 'PUT /v1/connections/{connection_id}': _O_ADMIN, 'DELETE /v1/connections/{connection_id}': _O_ADMIN, 'GET /v1/limits/platform': _O_READ, 'PUT /v1/limits/platform': _O_ADMIN, 'GET /v1/limits/effective': _O_READ, 'GET /v1/executors': _O_READ, 'GET /v1/audit-events': _O_READ, **_jobs(_O_READ, _O_WRITE)}
```

## jane_kit.auth_scopes.TABLES

**Константа.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:174](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L174).

```python
TABLES: dict[str, dict[str, Scopes]] = {'collector': COLLECTOR, 'handler': HANDLER, 'storage': STORAGE, 'llm': LLM, 'assistant': ASSISTANT, 'registry': REGISTRY, 'orchestrator': ORCHESTRATOR}
```

### Опис із вихідного коду

```text
Contract name (``contracts/openapi/<name>.v1.yaml``) -> its table.
```

## jane_kit.auth_scopes.merge

**Функція.** Код: [libs/jane-kit/src/jane_kit/auth_scopes.py:190](../../../../../../libs/jane-kit/src/jane_kit/auth_scopes.py#L190).

```python
def merge(*tables: Mapping[str, str | Sequence[str]]) -> dict[str, tuple[str, ...]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `tables` | `Mapping[str, str \| Sequence[str]]` | `—` | var-positional |

Результат: `dict[str, tuple[str, ...]]`.

### Опис із вихідного коду

```text
Tables of several APIs one service implements; an operation present in several gets the union.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth_scopes.py:183](../../../../../../libs/jane-kit/tests/test_auth_scopes.py#L183).

```python
merged = merge(*(TABLES[api] for api in apis))
```

Контекст і передумови: [libs/jane-kit/tests/test_auth_scopes.py:256](../../../../../../libs/jane-kit/tests/test_auth_scopes.py#L256).

```python
merged = merge(HANDLER, LLM)
```
