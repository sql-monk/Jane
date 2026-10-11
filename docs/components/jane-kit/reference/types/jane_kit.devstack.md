# Модуль `jane_kit.devstack`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/devstack.py](../../../../../libs/jane-kit/src/jane_kit/devstack.py). Не редагуйте вручну.

Access to the local dev stack started by ``just up`` (for integration tests).

``just up`` writes ``.jane/stack-<project>.json`` with host ports and generated credentials. Tests call :func:`load_stack` and skip when the stack is not running.

API keys of the stacks (ADR-0005, ``auth_mode=api_key``): one key per identity of :data:`STACK_IDENTITIES` in ``JANE_API_KEY_<IDENTITY>`` (the caller's own token) and its SHA-256 in ``JANE_API_KEY_<IDENTITY>_SHA256`` (what the services verify, ``infra/compose.yaml``). ``scripts/dev.py`` (stdlib only) keeps a copy of :func:`new_api_keys`; ``infra/tests/test_auth_config.py`` keeps them equal.

## Зміст

- [Клас `StackInfo`](#клас-stackinfo)
- [Функція `api_key_var`](#функція-api_key_var)
- [Функція `default_project`](#функція-default_project)
- [Функція `find_repo_root`](#функція-find_repo_root)
- [Функція `load_stack`](#функція-load_stack)
- [Функція `new_api_keys`](#функція-new_api_keys)

## Класи

### Клас `StackInfo`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.devstack` |
| Код | [devstack.py:83](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L83) |

```python
@dataclass(frozen=True)
class StackInfo: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `project` | `str` | — | читання |  |
| `services` | `dict[str, dict[str, Any]]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `StackInfo.url`

```python
def url(self, service: str, scheme: str = 'http') -> str: ...
```

Код: [devstack.py:87](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L87).

#### Метод `StackInfo.get`

```python
def get(self, service: str, key: str) -> Any: ...
```

Код: [devstack.py:91](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L91).

## Функції

### Функція `api_key_var`

```python
def api_key_var(identity: str) -> str: ...
```

``admin`` -> ``JANE_API_KEY_ADMIN`` (the key); ``+ "_SHA256"`` is its hash.

Код: [devstack.py:48](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L48).

### Функція `default_project`

```python
def default_project(root: Path) -> str: ...
```

Compose project name of a checkout; must stay identical to ``scripts/dev.py:default_project``.

Код: [devstack.py:73](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L73).

### Функція `find_repo_root`

```python
def find_repo_root(start: Path | None = None) -> Path: ...
```

Винятки в коді функції: `FileNotFoundError`.

Код: [devstack.py:65](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L65).

### Функція `load_stack`

```python
def load_stack(project: str | None = None, root: Path | None = None) -> StackInfo | None: ...
```

Stack description or ``None`` if ``just up`` has not been run for that project.

Resolution: explicit ``project`` -> env ``JANE_STACK_FILE`` (set by ``just integration``) -> this checkout's default project (``JANE_COMPOSE_PROJECT`` or the name ``just up`` derives from the checkout path). Never falls back to another project's stack file.

Код: [devstack.py:95](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L95).

### Функція `new_api_keys`

```python
def new_api_keys(existing: dict[str, str] | None = None) -> dict[str, str]: ...
```

Keys (and their SHA-256) of every identity missing from ``existing``; existing keys are kept.

Код: [devstack.py:53](../../../../../libs/jane-kit/src/jane_kit/devstack.py#L53).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `STACK_IDENTITIES` | `tuple[str, ...]` | `('admin', 'orchestrator', 'assistant', 'handler-runtime', 'storage', 'llm', 'web` | Callers that get a key in a local stack: the operator (admin UI, e2e harness) and every service that calls another one with its own token (ADR-0005 §5). |
