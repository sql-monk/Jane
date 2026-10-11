# jane_storage.connections

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.connections.SecretUnresolved](#jane_storageconnectionssecretunresolved)
- [jane_storage.connections.SecretUnresolved.code](#jane_storageconnectionssecretunresolvedcode)
- [jane_storage.connections.StoredConnection](#jane_storageconnectionsstoredconnection)
- [jane_storage.connections.StoredConnection.__init__](#jane_storageconnectionsstoredconnection__init__)
- [jane_storage.connections.StoredConnection.document](#jane_storageconnectionsstoredconnectiondocument)
- [jane_storage.connections.StoredConnection.etag](#jane_storageconnectionsstoredconnectionetag)
- [jane_storage.connections.StoredConnection.connection_id](#jane_storageconnectionsstoredconnectionconnection_id)
- [jane_storage.connections.StoredConnection.kind](#jane_storageconnectionsstoredconnectionkind)
- [jane_storage.connections.ConnectionRegistry](#jane_storageconnectionsconnectionregistry)
- [jane_storage.connections.ConnectionRegistry.__init__](#jane_storageconnectionsconnectionregistry__init__)
- [jane_storage.connections.ConnectionRegistry.policy](#jane_storageconnectionsconnectionregistrypolicy)
- [jane_storage.connections.ConnectionRegistry.load_file](#jane_storageconnectionsconnectionregistryload_file)
- [jane_storage.connections.ConnectionRegistry.validate](#jane_storageconnectionsconnectionregistryvalidate)
- [jane_storage.connections.ConnectionRegistry.put](#jane_storageconnectionsconnectionregistryput)
- [jane_storage.connections.ConnectionRegistry.add_resolved](#jane_storageconnectionsconnectionregistryadd_resolved)
- [jane_storage.connections.ConnectionRegistry.get](#jane_storageconnectionsconnectionregistryget)
- [jane_storage.connections.ConnectionRegistry.delete](#jane_storageconnectionsconnectionregistrydelete)
- [jane_storage.connections.ConnectionRegistry.list](#jane_storageconnectionsconnectionregistrylist)
- [jane_storage.connections.ConnectionRegistry.policy_errors](#jane_storageconnectionsconnectionregistrypolicy_errors)
- [jane_storage.connections.ConnectionRegistry.ensure_allowed](#jane_storageconnectionsconnectionregistryensure_allowed)
- [jane_storage.connections.ConnectionRegistry.secrets_resolved](#jane_storageconnectionsconnectionregistrysecrets_resolved)
- [jane_storage.connections.ConnectionRegistry.secret_values](#jane_storageconnectionsconnectionregistrysecret_values)
- [jane_storage.connections.ConnectionRegistry.resolve](#jane_storageconnectionsconnectionregistryresolve)
- [jane_storage.connections.AdapterPool](#jane_storageconnectionsadapterpool)
- [jane_storage.connections.AdapterPool.__init__](#jane_storageconnectionsadapterpool__init__)
- [jane_storage.connections.AdapterPool.registry](#jane_storageconnectionsadapterpoolregistry)
- [jane_storage.connections.AdapterPool.default_options](#jane_storageconnectionsadapterpooldefault_options)
- [jane_storage.connections.AdapterPool.connection_first](#jane_storageconnectionsadapterpoolconnection_first)
- [jane_storage.connections.AdapterPool.check](#jane_storageconnectionsadapterpoolcheck)
- [jane_storage.connections.AdapterPool.adapter_for](#jane_storageconnectionsadapterpooladapter_for)
- [jane_storage.connections.AdapterPool.lease](#jane_storageconnectionsadapterpoollease)
- [jane_storage.connections.AdapterPool.forget](#jane_storageconnectionsadapterpoolforget)
- [jane_storage.connections.AdapterPool.close](#jane_storageconnectionsadapterpoolclose)

## jane_storage.connections.SecretUnresolved

**Клас.** Код: [services/storage/src/jane_storage/connections.py:49](../../../../../../services/storage/src/jane_storage/connections.py#L49).

```python
class SecretUnresolved(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_storage.connections.md#jane_storageconnectionssecretunresolvedcode) | Поле | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

### Опис із вихідного коду

```text
A secret reference cannot be resolved in this executor's environment.
```

## jane_storage.connections.SecretUnresolved.code

**Поле.** Код: [services/storage/src/jane_storage/connections.py:52](../../../../../../services/storage/src/jane_storage/connections.py#L52).

```python
code = 'upstream_unavailable'
```

Доступ: читання — так; запис — так.

## jane_storage.connections.StoredConnection

**Клас.** Код: [services/storage/src/jane_storage/connections.py:56](../../../../../../services/storage/src/jane_storage/connections.py#L56).

```python
class StoredConnection:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [document](jane_storage.connections.md#jane_storageconnectionsstoredconnectiondocument) | Поле | ні |
| [etag](jane_storage.connections.md#jane_storageconnectionsstoredconnectionetag) | Поле | ні |
| [connection_id](jane_storage.connections.md#jane_storageconnectionsstoredconnectionconnection_id) | Властивість | ні |
| [kind](jane_storage.connections.md#jane_storageconnectionsstoredconnectionkind) | Властивість | ні |
| [__init__](jane_storage.connections.md#jane_storageconnectionsstoredconnection__init__) | Конструктор dataclass | ні |

## jane_storage.connections.StoredConnection.__init__

**Конструктор dataclass.** Код: [services/storage/src/jane_storage/connections.py:56](../../../../../../services/storage/src/jane_storage/connections.py#L56).

```python
def __init__(self, document: dict[str, Any], etag: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `document` | `dict[str, Any]` | `—` | positional-or-keyword |
| `etag` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.connections.StoredConnection.document

**Поле.** Код: [services/storage/src/jane_storage/connections.py:57](../../../../../../services/storage/src/jane_storage/connections.py#L57).

```python
document: dict[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_storage.connections.StoredConnection.etag

**Поле.** Код: [services/storage/src/jane_storage/connections.py:58](../../../../../../services/storage/src/jane_storage/connections.py#L58).

```python
etag: str
```

Доступ: читання — так; запис — ні.

## jane_storage.connections.StoredConnection.connection_id

**Властивість.** Код: [services/storage/src/jane_storage/connections.py:61](../../../../../../services/storage/src/jane_storage/connections.py#L61).

```python
def connection_id(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.connections.StoredConnection.kind

**Властивість.** Код: [services/storage/src/jane_storage/connections.py:65](../../../../../../services/storage/src/jane_storage/connections.py#L65).

```python
def kind(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_storage.connections.ConnectionRegistry

**Клас.** Код: [services/storage/src/jane_storage/connections.py:84](../../../../../../services/storage/src/jane_storage/connections.py#L84).

```python
class ConnectionRegistry:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.connections.md#jane_storageconnectionsconnectionregistry__init__) | Конструктор | ні |
| [policy](jane_storage.connections.md#jane_storageconnectionsconnectionregistrypolicy) | Поле екземпляра | ні |
| [load_file](jane_storage.connections.md#jane_storageconnectionsconnectionregistryload_file) | Метод | ні |
| [validate](jane_storage.connections.md#jane_storageconnectionsconnectionregistryvalidate) | Метод | ні |
| [put](jane_storage.connections.md#jane_storageconnectionsconnectionregistryput) | Метод | ні |
| [add_resolved](jane_storage.connections.md#jane_storageconnectionsconnectionregistryadd_resolved) | Метод | ні |
| [get](jane_storage.connections.md#jane_storageconnectionsconnectionregistryget) | Метод | ні |
| [delete](jane_storage.connections.md#jane_storageconnectionsconnectionregistrydelete) | Метод | ні |
| [list](jane_storage.connections.md#jane_storageconnectionsconnectionregistrylist) | Метод | ні |
| [policy_errors](jane_storage.connections.md#jane_storageconnectionsconnectionregistrypolicy_errors) | Метод | ні |
| [ensure_allowed](jane_storage.connections.md#jane_storageconnectionsconnectionregistryensure_allowed) | Метод | ні |
| [secrets_resolved](jane_storage.connections.md#jane_storageconnectionsconnectionregistrysecrets_resolved) | Метод | ні |
| [secret_values](jane_storage.connections.md#jane_storageconnectionsconnectionregistrysecret_values) | Метод | ні |
| [resolve](jane_storage.connections.md#jane_storageconnectionsconnectionregistryresolve) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:330](../../../../../../services/storage/tests/test_reprocess_reads.py#L330).

```python
registry = ConnectionRegistry()
```

## jane_storage.connections.ConnectionRegistry.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/connections.py:85](../../../../../../services/storage/src/jane_storage/connections.py#L85).

```python
def __init__(self, validator: Any=None, environ: Mapping[str, str] | None=None, policy: ConnectionPolicy | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `validator` | `Any` | `None` | positional-or-keyword |
| `environ` | `Mapping[str, str] \| None` | `None` | positional-or-keyword |
| `policy` | `ConnectionPolicy \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:330](../../../../../../services/storage/tests/test_reprocess_reads.py#L330).

```python
registry = ConnectionRegistry()
```

## jane_storage.connections.ConnectionRegistry.policy

**Поле екземпляра.** Код: [services/storage/src/jane_storage/connections.py:95](../../../../../../services/storage/src/jane_storage/connections.py#L95).

```python
self.policy = policy if policy is not None else ConnectionPolicy()
```

## jane_storage.connections.ConnectionRegistry.load_file

**Метод.** Код: [services/storage/src/jane_storage/connections.py:98](../../../../../../services/storage/src/jane_storage/connections.py#L98).

```python
def load_file(self, path: Path) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `Path` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Connections of the config file. A policy violation does not stop the service (the connection is
kept, gets no secrets and is rejected when used); other validation errors do.
```

## jane_storage.connections.ConnectionRegistry.validate

**Метод.** Код: [services/storage/src/jane_storage/connections.py:108](../../../../../../services/storage/src/jane_storage/connections.py#L108).

```python
def validate(self, doc: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `JaneError`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.connections.ConnectionRegistry.put

**Метод.** Код: [services/storage/src/jane_storage/connections.py:120](../../../../../../services/storage/src/jane_storage/connections.py#L120).

```python
def put(self, doc: dict[str, Any], *, enforce_policy: bool=True) -> tuple[StoredConnection, bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |
| `enforce_policy` | `bool` | `True` | keyword-only |

Результат: `tuple[StoredConnection, bool]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Store a definition. ``enforce_policy`` (the API): a secret-policy violation → 422 and nothing is
stored; otherwise (config file) the connection is stored with a warning and rejected when used.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:331](../../../../../../services/storage/tests/test_reprocess_reads.py#L331).

```python
registry.put(
        {"connection_id": "plain", "kind": "filesystem", "params": {"base_path": str(tmp_path / "a")}}
    )
```

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:334](../../../../../../services/storage/tests/test_reprocess_reads.py#L334).

```python
registry.put(
        {
            "connection_id": "own",
            "kind": "filesystem",
            "params": {"base_path": str(tmp_path / "b"), "chunk_bytes": 512},
        }
    )
```

## jane_storage.connections.ConnectionRegistry.add_resolved

**Метод.** Код: [services/storage/src/jane_storage/connections.py:143](../../../../../../services/storage/src/jane_storage/connections.py#L143).

```python
def add_resolved(self, conn: ResolvedConnection) -> StoredConnection:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `conn` | `ResolvedConnection` | `—` | positional-or-keyword |

Результат: `StoredConnection`.

### Опис із вихідного коду

```text
Register an already resolved connection (embedding, tests of adapters).
```

## jane_storage.connections.ConnectionRegistry.get

**Метод.** Код: [services/storage/src/jane_storage/connections.py:151](../../../../../../services/storage/src/jane_storage/connections.py#L151).

```python
def get(self, connection_id: str) -> StoredConnection:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `StoredConnection`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.connections.ConnectionRegistry.delete

**Метод.** Код: [services/storage/src/jane_storage/connections.py:157](../../../../../../services/storage/src/jane_storage/connections.py#L157).

```python
def delete(self, connection_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.connections.ConnectionRegistry.list

**Метод.** Код: [services/storage/src/jane_storage/connections.py:162](../../../../../../services/storage/src/jane_storage/connections.py#L162).

```python
def list(self) -> list[StoredConnection]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[StoredConnection]`.

## jane_storage.connections.ConnectionRegistry.policy_errors

**Метод.** Код: [services/storage/src/jane_storage/connections.py:166](../../../../../../services/storage/src/jane_storage/connections.py#L166).

```python
def policy_errors(self, connection_id: str) -> builtins.list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `builtins.list[FieldError]`.

### Опис із вихідного коду

```text
Secret-policy violations of a stored connection (``add_resolved`` ones are the embedder's).
```

## jane_storage.connections.ConnectionRegistry.ensure_allowed

**Метод.** Код: [services/storage/src/jane_storage/connections.py:173](../../../../../../services/storage/src/jane_storage/connections.py#L173).

```python
def ensure_allowed(self, connection_id: str, *, pointer: str | None=None, parameter: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `pointer` | `str \| None` | `None` | keyword-only |
| `parameter` | `str \| None` | `None` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
422 (``secret_ref_not_allowed`` / ``host_not_allowed``) if the connection violates the policy.
```

## jane_storage.connections.ConnectionRegistry.secrets_resolved

**Метод.** Код: [services/storage/src/jane_storage/connections.py:197](../../../../../../services/storage/src/jane_storage/connections.py#L197).

```python
def secrets_resolved(self, connection_id: str) -> dict[str, bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, bool]`.

### Опис із вихідного коду

```text
Name → resolvable (never values); all ``False`` for a connection that violates the policy.
```

## jane_storage.connections.ConnectionRegistry.secret_values

**Метод.** Код: [services/storage/src/jane_storage/connections.py:207](../../../../../../services/storage/src/jane_storage/connections.py#L207).

```python
def secret_values(self, connection_id: str) -> builtins.list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `builtins.list[str]`.

### Опис із вихідного коду

```text
Resolved values of the connection — only to redact error messages.
```

## jane_storage.connections.ConnectionRegistry.resolve

**Метод.** Код: [services/storage/src/jane_storage/connections.py:216](../../../../../../services/storage/src/jane_storage/connections.py#L216).

```python
def resolve(self, connection_id: str) -> ResolvedConnection:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `ResolvedConnection`.

Явні `raise` у тілі: `SecretUnresolved`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.connections.AdapterPool

**Клас.** Код: [services/storage/src/jane_storage/connections.py:242](../../../../../../services/storage/src/jane_storage/connections.py#L242).

```python
class AdapterPool:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.connections.md#jane_storageconnectionsadapterpool__init__) | Конструктор | ні |
| [registry](jane_storage.connections.md#jane_storageconnectionsadapterpoolregistry) | Поле екземпляра | ні |
| [default_options](jane_storage.connections.md#jane_storageconnectionsadapterpooldefault_options) | Поле екземпляра | ні |
| [connection_first](jane_storage.connections.md#jane_storageconnectionsadapterpoolconnection_first) | Поле екземпляра | ні |
| [check](jane_storage.connections.md#jane_storageconnectionsadapterpoolcheck) | Метод | ні |
| [adapter_for](jane_storage.connections.md#jane_storageconnectionsadapterpooladapter_for) | Метод | ні |
| [lease](jane_storage.connections.md#jane_storageconnectionsadapterpoollease) | Метод | ні |
| [forget](jane_storage.connections.md#jane_storageconnectionsadapterpoolforget) | Метод | ні |
| [close](jane_storage.connections.md#jane_storageconnectionsadapterpoolclose) | Метод | ні |

### Опис із вихідного коду

```text
Opened adapters per connection; implements ``jane_storage.handler.AdapterProvider``.

One adapter per (connection, definition ETag, options). A changed definition (``PUT``) or a deleted connection
*retires* the connection's adapters: new work opens a new adapter, while work that already holds one through
:meth:`lease` finishes on it; a retired adapter is closed when its last lease ends. An unchanged ``PUT`` keeps
the open adapter.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:343](../../../../../../services/storage/tests/test_reprocess_reads.py#L343).

```python
pool = AdapterPool(registry, lim.model_dump(exclude_none=True), connection_first=CONNECTION_FIRST_OPTIONS)
```

## jane_storage.connections.AdapterPool.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/connections.py:251](../../../../../../services/storage/src/jane_storage/connections.py#L251).

```python
def __init__(self, registry: ConnectionRegistry, default_options: Mapping[str, Any] | None=None, *, connection_first: Iterable[str]=()) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `registry` | `ConnectionRegistry` | `—` | positional-or-keyword |
| `default_options` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |
| `connection_first` | `Iterable[str]` | `()` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:343](../../../../../../services/storage/tests/test_reprocess_reads.py#L343).

```python
pool = AdapterPool(registry, lim.model_dump(exclude_none=True), connection_first=CONNECTION_FIRST_OPTIONS)
```

## jane_storage.connections.AdapterPool.registry

**Поле екземпляра.** Код: [services/storage/src/jane_storage/connections.py:258](../../../../../../services/storage/src/jane_storage/connections.py#L258).

```python
self.registry = registry
```

## jane_storage.connections.AdapterPool.default_options

**Поле екземпляра.** Код: [services/storage/src/jane_storage/connections.py:259](../../../../../../services/storage/src/jane_storage/connections.py#L259).

```python
self.default_options = dict(default_options or {})
```

## jane_storage.connections.AdapterPool.connection_first

**Поле екземпляра.** Код: [services/storage/src/jane_storage/connections.py:260](../../../../../../services/storage/src/jane_storage/connections.py#L260).

```python
self.connection_first = frozenset(connection_first)
```

## jane_storage.connections.AdapterPool.check

**Метод.** Код: [services/storage/src/jane_storage/connections.py:270](../../../../../../services/storage/src/jane_storage/connections.py#L270).

```python
def check(self, connection_id: str, adapter_kind: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.connections.AdapterPool.adapter_for

**Метод.** Код: [services/storage/src/jane_storage/connections.py:316](../../../../../../services/storage/src/jane_storage/connections.py#L316).

```python
async def adapter_for(self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]) -> StorageAdapter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `StorageAdapter`.

### Опис із вихідного коду

```text
The opened adapter without a lease: a retirement may close it under the caller (prefer :meth:`lease`).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:348](../../../../../../services/storage/tests/test_reprocess_reads.py#L348).

```python
await pool.adapter_for("plain", "filesystem", {})
```

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:349](../../../../../../services/storage/tests/test_reprocess_reads.py#L349).

```python
await pool.adapter_for("own", "filesystem", {"prefix": "p"})
```

## jane_storage.connections.AdapterPool.lease

**Метод.** Код: [services/storage/src/jane_storage/connections.py:323](../../../../../../services/storage/src/jane_storage/connections.py#L323).

```python
async def lease(self, connection_id: str, adapter_kind: str, options: Mapping[str, Any]) -> AsyncIterator[StorageAdapter]:
```

Декоратори: `asynccontextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `AsyncIterator[StorageAdapter]`.

### Опис із вихідного коду

```text
The opened adapter for the duration of the block: retiring it waits for the block to end.
```

## jane_storage.connections.AdapterPool.forget

**Метод.** Код: [services/storage/src/jane_storage/connections.py:367](../../../../../../services/storage/src/jane_storage/connections.py#L367).

```python
async def forget(self, connection_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
The connection changed or was deleted: retire all its adapters (in-flight work finishes first).
```

## jane_storage.connections.AdapterPool.close

**Метод.** Код: [services/storage/src/jane_storage/connections.py:372](../../../../../../services/storage/src/jane_storage/connections.py#L372).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.
