# jane_kit.devstack

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.devstack.STACK_IDENTITIES](#jane_kitdevstackstack_identities)
- [jane_kit.devstack.api_key_var](#jane_kitdevstackapi_key_var)
- [jane_kit.devstack.new_api_keys](#jane_kitdevstacknew_api_keys)
- [jane_kit.devstack.find_repo_root](#jane_kitdevstackfind_repo_root)
- [jane_kit.devstack.default_project](#jane_kitdevstackdefault_project)
- [jane_kit.devstack.StackInfo](#jane_kitdevstackstackinfo)
- [jane_kit.devstack.StackInfo.__init__](#jane_kitdevstackstackinfo__init__)
- [jane_kit.devstack.StackInfo.project](#jane_kitdevstackstackinfoproject)
- [jane_kit.devstack.StackInfo.services](#jane_kitdevstackstackinfoservices)
- [jane_kit.devstack.StackInfo.url](#jane_kitdevstackstackinfourl)
- [jane_kit.devstack.StackInfo.get](#jane_kitdevstackstackinfoget)
- [jane_kit.devstack.load_stack](#jane_kitdevstackload_stack)

## jane_kit.devstack.STACK_IDENTITIES

**Константа.** Код: [libs/jane-kit/src/jane_kit/devstack.py:33](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L33).

```python
STACK_IDENTITIES: tuple[str, ...] = ('admin', 'orchestrator', 'assistant', 'handler-runtime', 'storage', 'llm', 'web-collector', 'telegram-collector', 'registry')
```

### Опис із вихідного коду

```text
Callers that get a key in a local stack: the operator (admin UI, e2e harness) and every service that calls
another one with its own token (ADR-0005 §5).
```

## jane_kit.devstack.api_key_var

**Функція.** Код: [libs/jane-kit/src/jane_kit/devstack.py:48](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L48).

```python
def api_key_var(identity: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `identity` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``admin`` -> ``JANE_API_KEY_ADMIN`` (the key); ``+ "_SHA256"`` is its hash.
```

## jane_kit.devstack.new_api_keys

**Функція.** Код: [libs/jane-kit/src/jane_kit/devstack.py:53](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L53).

```python
def new_api_keys(existing: dict[str, str] | None=None) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `existing` | `dict[str, str] \| None` | `None` | positional-or-keyword |

Результат: `dict[str, str]`.

### Опис із вихідного коду

```text
Keys (and their SHA-256) of every identity missing from ``existing``; existing keys are kept.
```

## jane_kit.devstack.find_repo_root

**Функція.** Код: [libs/jane-kit/src/jane_kit/devstack.py:65](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L65).

```python
def find_repo_root(start: Path | None=None) -> Path:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `start` | `Path \| None` | `None` | positional-or-keyword |

Результат: `Path`.

Явні `raise` у тілі: `FileNotFoundError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.devstack.default_project

**Функція.** Код: [libs/jane-kit/src/jane_kit/devstack.py:73](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L73).

```python
def default_project(root: Path) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Compose project name of a checkout; must stay identical to ``scripts/dev.py:default_project``.
```

## jane_kit.devstack.StackInfo

**Клас.** Код: [libs/jane-kit/src/jane_kit/devstack.py:83](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L83).

```python
class StackInfo:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [project](jane_kit.devstack.md#jane_kitdevstackstackinfoproject) | Поле | ні |
| [services](jane_kit.devstack.md#jane_kitdevstackstackinfoservices) | Поле | ні |
| [url](jane_kit.devstack.md#jane_kitdevstackstackinfourl) | Метод | ні |
| [get](jane_kit.devstack.md#jane_kitdevstackstackinfoget) | Метод | ні |
| [__init__](jane_kit.devstack.md#jane_kitdevstackstackinfo__init__) | Конструктор dataclass | ні |

## jane_kit.devstack.StackInfo.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/devstack.py:83](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L83).

```python
def __init__(self, project: str, services: dict[str, dict[str, Any]]) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `project` | `str` | `—` | positional-or-keyword |
| `services` | `dict[str, dict[str, Any]]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.devstack.StackInfo.project

**Поле.** Код: [libs/jane-kit/src/jane_kit/devstack.py:84](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L84).

```python
project: str
```

Доступ: читання — так; запис — ні.

## jane_kit.devstack.StackInfo.services

**Поле.** Код: [libs/jane-kit/src/jane_kit/devstack.py:85](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L85).

```python
services: dict[str, dict[str, Any]]
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_compat.py:39](../../../../../../services/storage/adapters/minio/tests/test_compat.py#L39).

```python
self.info = stack.services["minio"]
```

Контекст і передумови: [services/storage/adapters/minio/tests/test_compat.py:118](../../../../../../services/storage/adapters/minio/tests/test_compat.py#L118).

```python
stack.services
```

## jane_kit.devstack.StackInfo.url

**Метод.** Код: [libs/jane-kit/src/jane_kit/devstack.py:87](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L87).

```python
def url(self, service: str, scheme: str='http') -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `service` | `str` | `—` | positional-or-keyword |
| `scheme` | `str` | `'http'` | positional-or-keyword |

Результат: `str`.

## jane_kit.devstack.StackInfo.get

**Метод.** Код: [libs/jane-kit/src/jane_kit/devstack.py:91](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L91).

```python
def get(self, service: str, key: str) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `service` | `str` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `Any`.

## jane_kit.devstack.load_stack

**Функція.** Код: [libs/jane-kit/src/jane_kit/devstack.py:95](../../../../../../libs/jane-kit/src/jane_kit/devstack.py#L95).

```python
def load_stack(project: str | None=None, root: Path | None=None) -> StackInfo | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `project` | `str \| None` | `None` | positional-or-keyword |
| `root` | `Path \| None` | `None` | positional-or-keyword |

Результат: `StackInfo | None`.

### Опис із вихідного коду

```text
Stack description or ``None`` if ``just up`` has not been run for that project.

Resolution: explicit ``project`` -> env ``JANE_STACK_FILE`` (set by ``just integration``) ->
this checkout's default project (``JANE_COMPOSE_PROJECT`` or the name ``just up`` derives from the
checkout path). Never falls back to another project's stack file.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:105](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L105).

```python
stack = load_stack()
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:35](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L35).

```python
stack = load_stack()
```
