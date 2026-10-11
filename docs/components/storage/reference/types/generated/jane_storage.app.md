# jane_storage.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.app.log](#jane_storageapplog)
- [jane_storage.app.REQUEST_LIMIT_PATHS](#jane_storageapprequest_limit_paths)
- [jane_storage.app.entity_state](#jane_storageappentity_state)
- [jane_storage.app.history_entry](#jane_storageapphistory_entry)
- [jane_storage.app.InvocationResults](#jane_storageappinvocationresults)
- [jane_storage.app.InvocationResults.__init__](#jane_storageappinvocationresults__init__)
- [jane_storage.app.InvocationResults.max_entries](#jane_storageappinvocationresultsmax_entries)
- [jane_storage.app.InvocationResults.put](#jane_storageappinvocationresultsput)
- [jane_storage.app.InvocationResults.get](#jane_storageappinvocationresultsget)
- [jane_storage.app.build_app](#jane_storageappbuild_app)
- [jane_storage.app.manifest_test_cases](#jane_storageappmanifest_test_cases)

## jane_storage.app.log

**Змінна.** Код: [services/storage/src/jane_storage/app.py:65](../../../../../../services/storage/src/jane_storage/app.py#L65).

```python
log = logging.getLogger(__name__)
```

## jane_storage.app.REQUEST_LIMIT_PATHS

**Константа.** Код: [services/storage/src/jane_storage/app.py:67](../../../../../../services/storage/src/jane_storage/app.py#L67).

```python
REQUEST_LIMIT_PATHS = {'timeouts.sync_response_max_ms', 'timeouts.request_timeout_ms'}
```

### Опис із вихідного коду

```text
Parts of ``HandlerInvocation.limits`` this executor applies (min with its own hard caps). The stage's
``retries`` is the caller's policy (the orchestrator re-sends with the same key) and is ignored here: the core's
own ``CONFLICT`` retries come from ``limits.conflict_retries`` of the service configuration.
```

## jane_storage.app.entity_state

**Функція.** Код: [services/storage/src/jane_storage/app.py:148](../../../../../../services/storage/src/jane_storage/app.py#L148).

```python
def entity_state(snap: EntitySnapshot) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `snap` | `EntitySnapshot` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_storage.app.history_entry

**Функція.** Код: [services/storage/src/jane_storage/app.py:154](../../../../../../services/storage/src/jane_storage/app.py#L154).

```python
def history_entry(event: HistoryEvent) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `event` | `HistoryEvent` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_storage.app.InvocationResults

**Клас.** Код: [services/storage/src/jane_storage/app.py:164](../../../../../../services/storage/src/jane_storage/app.py#L164).

```python
class InvocationResults:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.app.md#jane_storageappinvocationresults__init__) | Конструктор | ні |
| [max_entries](jane_storage.app.md#jane_storageappinvocationresultsmax_entries) | Поле екземпляра | ні |
| [put](jane_storage.app.md#jane_storageappinvocationresultsput) | Метод | ні |
| [get](jane_storage.app.md#jane_storageappinvocationresultsget) | Метод | ні |

### Опис із вихідного коду

```text
Recent HandlerResults of this instance (``GET /v1/invocations/{id}``).
```

## jane_storage.app.InvocationResults.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/app.py:167](../../../../../../services/storage/src/jane_storage/app.py#L167).

```python
def __init__(self, max_entries: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `max_entries` | `int` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.app.InvocationResults.max_entries

**Поле екземпляра.** Код: [services/storage/src/jane_storage/app.py:168](../../../../../../services/storage/src/jane_storage/app.py#L168).

```python
self.max_entries = max_entries
```

## jane_storage.app.InvocationResults.put

**Метод.** Код: [services/storage/src/jane_storage/app.py:171](../../../../../../services/storage/src/jane_storage/app.py#L171).

```python
def put(self, result: dict[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `result` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.app.InvocationResults.get

**Метод.** Код: [services/storage/src/jane_storage/app.py:176](../../../../../../services/storage/src/jane_storage/app.py#L176).

```python
def get(self, invocation_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage.app.build_app

**Функція.** Код: [services/storage/src/jane_storage/app.py:220](../../../../../../services/storage/src/jane_storage/app.py#L220).

```python
def build_app(settings: Settings | None=None, *, registry_transport: httpx.AsyncBaseTransport | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |
| `registry_transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |

Результат: `FastAPI`.

### Опис із вихідного коду

```text
The storage service. ``registry_transport`` Р В Р вЂ Р В РІР‚С™Р Р†Р вЂљРЎСљ HTTP transport to the registry (tests).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/conftest.py:125](../../../../../../services/storage/tests/conftest.py#L125).

```python
build_app(settings)
```

Контекст і передумови: [services/storage/tests/test_adapter_swap.py:144](../../../../../../services/storage/tests/test_adapter_swap.py#L144).

```python
build_app(Settings(log_format="console", connections_file=conns))
```

## jane_storage.app.manifest_test_cases

**Функція.** Код: [services/storage/src/jane_storage/app.py:972](../../../../../../services/storage/src/jane_storage/app.py#L972).

```python
def manifest_test_cases(pkg: StoragePackage, body: Mapping[str, Any]) -> list[tuple[str, dict[str, Any], str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pkg` | `StoragePackage` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `list[tuple[str, dict[str, Any], str]]`.

### Опис із вихідного коду

```text
Invocations (``test_mode``) for the package's manifest tests and extra cases of a test run.
```
