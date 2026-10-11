# jane_llm.connections

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.connections.FAKE_SCRIPTS_KEY](#jane_llmconnectionsfake_scripts_key)
- [jane_llm.connections.ConnectionPolicy](#jane_llmconnectionsconnectionpolicy)
- [jane_llm.connections.ConnectionPolicy.__init__](#jane_llmconnectionsconnectionpolicy__init__)
- [jane_llm.connections.ConnectionPolicy.api_base_allowlist](#jane_llmconnectionsconnectionpolicyapi_base_allowlist)
- [jane_llm.connections.ConnectionPolicy.api_base_error](#jane_llmconnectionsconnectionpolicyapi_base_error)
- [jane_llm.connections.ConnectionPolicy.violations](#jane_llmconnectionsconnectionpolicyviolations)
- [jane_llm.connections.resolve_ref](#jane_llmconnectionsresolve_ref)
- [jane_llm.connections.find_secret_like](#jane_llmconnectionsfind_secret_like)
- [jane_llm.connections.resolve_connection](#jane_llmconnectionsresolve_connection)

## jane_llm.connections.FAKE_SCRIPTS_KEY

**Константа.** Код: [services/llm/src/jane_llm/connections.py:41](../../../../../../services/llm/src/jane_llm/connections.py#L41).

```python
FAKE_SCRIPTS_KEY = 'responses'
```

### Опис із вихідного коду

```text
Scripts of the ``fake`` provider may contain arbitrary text; exempt only when ``params.provider == "fake"``.
```

## jane_llm.connections.ConnectionPolicy

**Клас.** Код: [services/llm/src/jane_llm/connections.py:54](../../../../../../services/llm/src/jane_llm/connections.py#L54).

```python
class ConnectionPolicy(SecretPolicy):
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [api_base_allowlist](jane_llm.connections.md#jane_llmconnectionsconnectionpolicyapi_base_allowlist) | Поле | ні |
| [api_base_error](jane_llm.connections.md#jane_llmconnectionsconnectionpolicyapi_base_error) | Метод | ні |
| [violations](jane_llm.connections.md#jane_llmconnectionsconnectionpolicyviolations) | Метод | ні |
| [env_prefix](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyenv_prefix) | Поле | так |
| [files_dir](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyfiles_dir) | Поле | так |
| [secret_file](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicysecret_file) | Метод | так |
| [ref_error](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyref_error) | Метод | так |
| [resolve](../../../../jane-kit/reference/types/generated/jane_kit.secrets.md#jane_kitsecretssecretpolicyresolve) | Метод | так |
| [__init__](jane_llm.connections.md#jane_llmconnectionsconnectionpolicy__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
jane-kit's secret policy plus the allowed origins of ``params.api_base``.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_api_base.py:17](../../../../../../services/llm/tests/test_api_base.py#L17).

```python
error = ConnectionPolicy().api_base_error(api_base)
```

Контекст і передумови: [services/llm/tests/test_secret_files.py:31](../../../../../../services/llm/tests/test_secret_files.py#L31).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

## jane_llm.connections.ConnectionPolicy.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/connections.py:54](../../../../../../services/llm/src/jane_llm/connections.py#L54).

```python
def __init__(self, env_prefix: str = 'JANE_SECRET_', files_dir: Path | None = Path('/run/secrets'), api_base_allowlist: tuple[str, ...] = ('https://api.anthropic.com',)) -> None:
```

Базові типи / інтерфейси: `SecretPolicy`.

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `env_prefix` | `str` | `'JANE_SECRET_'` | positional-or-keyword |
| `files_dir` | `Path \| None` | `Path('/run/secrets')` | positional-or-keyword |
| `api_base_allowlist` | `tuple[str, ...]` | `('https://api.anthropic.com',)` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_api_base.py:17](../../../../../../services/llm/tests/test_api_base.py#L17).

```python
error = ConnectionPolicy().api_base_error(api_base)
```

Контекст і передумови: [services/llm/tests/test_secret_files.py:31](../../../../../../services/llm/tests/test_secret_files.py#L31).

```python
policy = ConnectionPolicy(files_dir=secrets_dir)
```

## jane_llm.connections.ConnectionPolicy.api_base_allowlist

**Поле.** Код: [services/llm/src/jane_llm/connections.py:57](../../../../../../services/llm/src/jane_llm/connections.py#L57).

```python
api_base_allowlist: tuple[str, ...] = ('https://api.anthropic.com',)
```

Доступ: читання — так; запис — ні.

## jane_llm.connections.ConnectionPolicy.api_base_error

**Метод.** Код: [services/llm/src/jane_llm/connections.py:63](../../../../../../services/llm/src/jane_llm/connections.py#L63).

```python
def api_base_error(self, api_base: Any) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `api_base` | `Any` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_llm.connections.ConnectionPolicy.violations

**Метод.** Код: [services/llm/src/jane_llm/connections.py:73](../../../../../../services/llm/src/jane_llm/connections.py#L73).

```python
def violations(self, doc: Any, pointer: str='/secret_refs') -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Any` | `—` | positional-or-keyword |
| `pointer` | `str` | `'/secret_refs'` | positional-or-keyword |

Результат: `list[FieldError]`.

### Опис із вихідного коду

```text
Violations of a Connection document: its ``secret_refs`` and ``params.api_base``.
```

## jane_llm.connections.resolve_ref

**Функція.** Код: [services/llm/src/jane_llm/connections.py:82](../../../../../../services/llm/src/jane_llm/connections.py#L82).

```python
def resolve_ref(ref: str, policy: ConnectionPolicy) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ref` | `str` | `—` | positional-or-keyword |
| `policy` | `ConnectionPolicy` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Value of an allowed ``env:VAR`` / ``file:<path>``; ``None`` if missing or not allowed.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_secret_files.py:33](../../../../../../services/llm/tests/test_secret_files.py#L33).

```python
assert resolve_ref(f"file:{link}", policy) == "inside-secret"
```

Контекст і передумови: [services/llm/tests/test_secret_files.py:48](../../../../../../services/llm/tests/test_secret_files.py#L48).

```python
assert resolve_ref(f"file:{link}", SwapAfterCheck(files_dir=secrets_dir)) is None
```

## jane_llm.connections.find_secret_like

**Функція.** Код: [services/llm/src/jane_llm/connections.py:87](../../../../../../services/llm/src/jane_llm/connections.py#L87).

```python
def find_secret_like(params: dict[str, Any], prefix: str='/params') -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `params` | `dict[str, Any]` | `—` | positional-or-keyword |
| `prefix` | `str` | `'/params'` | positional-or-keyword |

Результат: `list[FieldError]`.

### Опис із вихідного коду

```text
Pointers to values in ``params`` that look like secrets (they belong in ``secret_refs``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:109](../../../../../../services/llm/tests/test_units.py#L109).

```python
leaks = find_secret_like({"api_base": "http://x", "password": "p", "nested": {"note": "sk-" + "a" * 20}})
```

Контекст і передумови: [services/llm/tests/test_units.py:112](../../../../../../services/llm/tests/test_units.py#L112).

```python
assert find_secret_like(fake_scripts) == []
```

## jane_llm.connections.resolve_connection

**Функція.** Код: [services/llm/src/jane_llm/connections.py:113](../../../../../../services/llm/src/jane_llm/connections.py#L113).

```python
def resolve_connection(doc: dict[str, Any], policy: ConnectionPolicy) -> tuple[ResolvedConnection, dict[str, bool]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |
| `policy` | `ConnectionPolicy` | `—` | positional-or-keyword |

Результат: `tuple[ResolvedConnection, dict[str, bool]]`.

### Опис із вихідного коду

```text
Resolve ``secret_refs`` of a stored connection under ``policy``. Returns the connection and, per
secret, whether it was resolved (for ``POST /v1/connections/{id}/test``). A connection whose
``api_base`` is not allowed gets no secrets at all.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:130](../../../../../../services/llm/tests/test_units.py#L130).

```python
conn, resolved = resolve_connection(
        {
            "connection_id": "c",
            "kind": "llm_provider",
            "secret_refs": {"a": "env:JANE_SECRET_TEST_REF", "b": "env:NOPE_X"},
        },
        policy,
    )
```
