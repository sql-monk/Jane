# jane_storage.engine

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.engine.ConflictRetriesExhausted](#jane_storageengineconflictretriesexhausted)
- [jane_storage.engine.ConflictRetriesExhausted.__init__](#jane_storageengineconflictretriesexhausted__init__)
- [jane_storage.engine.backoff_ms](#jane_storageenginebackoff_ms)
- [jane_storage.engine.stored_object_ref](#jane_storageenginestored_object_ref)
- [jane_storage.engine.StorageEngine](#jane_storageenginestorageengine)
- [jane_storage.engine.StorageEngine.__init__](#jane_storageenginestorageengine__init__)
- [jane_storage.engine.StorageEngine.adapter](#jane_storageenginestorageengineadapter)
- [jane_storage.engine.StorageEngine.connection_id](#jane_storageenginestorageengineconnection_id)
- [jane_storage.engine.StorageEngine.retries](#jane_storageenginestorageengineretries)
- [jane_storage.engine.StorageEngine.target](#jane_storageenginestorageenginetarget)
- [jane_storage.engine.StorageEngine.store_entity](#jane_storageenginestorageenginestore_entity)
- [jane_storage.engine.StorageEngine.store_object](#jane_storageenginestorageenginestore_object)

## jane_storage.engine.ConflictRetriesExhausted

**Клас.** Код: [services/storage/src/jane_storage/engine.py:41](../../../../../../services/storage/src/jane_storage/engine.py#L41).

```python
class ConflictRetriesExhausted(AdapterError):
```

Базові типи / інтерфейси: `AdapterError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.engine.md#jane_storageengineconflictretriesexhausted__init__) | Конструктор | ні |
| [retryable](../../../../jane-kit/reference/types/generated/jane_contracts.storage_adapter.md#jane_contractsstorage_adapteradaptererrorretryable) | Поле екземпляра | так |

### Опис із вихідного коду

```text
Concurrent writers kept winning for longer than ``limits.conflict_retries.max_attempts``.
```

## jane_storage.engine.ConflictRetriesExhausted.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/engine.py:44](../../../../../../services/storage/src/jane_storage/engine.py#L44).

```python
def __init__(self, message: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage.engine.backoff_ms

**Функція.** Код: [services/storage/src/jane_storage/engine.py:48](../../../../../../services/storage/src/jane_storage/engine.py#L48).

```python
def backoff_ms(policy: RetryPolicy, attempt: int, rnd: Callable[[], float]=random.random) -> float:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `policy` | `RetryPolicy` | `—` | positional-or-keyword |
| `attempt` | `int` | `—` | positional-or-keyword |
| `rnd` | `Callable[[], float]` | `random.random` | positional-or-keyword |

Результат: `float`.

### Опис із вихідного коду

```text
Delay before attempt ``attempt + 1`` (``attempt`` >= 1).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:162](../../../../../../services/storage/tests/test_core.py#L162).

```python
assert backoff_ms(jittered, 1, rnd=lambda: 0.5) == 50
```

Контекст і передумови: [services/storage/tests/test_core.py:160](../../../../../../services/storage/tests/test_core.py#L160).

```python
assert [backoff_ms(policy, n) for n in (1, 2, 3)] == [100, 200, 250]
```

## jane_storage.engine.stored_object_ref

**Функція.** Код: [services/storage/src/jane_storage/engine.py:54](../../../../../../services/storage/src/jane_storage/engine.py#L54).

```python
def stored_object_ref(rec: ObjectRecord, adapter_kind: str, connection_id: str | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `rec` | `ObjectRecord` | `—` | positional-or-keyword |
| `adapter_kind` | `str` | `—` | positional-or-keyword |
| `connection_id` | `str \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``StoredObjectRef`` of an object record.
```

## jane_storage.engine.StorageEngine

**Клас.** Код: [services/storage/src/jane_storage/engine.py:69](../../../../../../services/storage/src/jane_storage/engine.py#L69).

```python
class StorageEngine:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.engine.md#jane_storageenginestorageengine__init__) | Конструктор | ні |
| [adapter](jane_storage.engine.md#jane_storageenginestorageengineadapter) | Поле екземпляра | ні |
| [connection_id](jane_storage.engine.md#jane_storageenginestorageengineconnection_id) | Поле екземпляра | ні |
| [retries](jane_storage.engine.md#jane_storageenginestorageengineretries) | Поле екземпляра | ні |
| [target](jane_storage.engine.md#jane_storageenginestorageenginetarget) | Властивість | ні |
| [store_entity](jane_storage.engine.md#jane_storageenginestorageenginestore_entity) | Метод | ні |
| [store_object](jane_storage.engine.md#jane_storageenginestorageenginestore_object) | Метод | ні |

### Опис із вихідного коду

```text
Core semantics over one opened adapter (one connection).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:94](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L94).

```python
engine = StorageEngine(adapter)
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:118](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L118).

```python
engine = StorageEngine(adapter)
```

## jane_storage.engine.StorageEngine.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/engine.py:72](../../../../../../services/storage/src/jane_storage/engine.py#L72).

```python
def __init__(self, adapter: StorageAdapter, *, connection_id: str | None=None, retries: RetryPolicy | None=None, clock: Callable[[], datetime]=utcnow, sleep: Callable[[float], Awaitable[None]]=asyncio.sleep) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `adapter` | `StorageAdapter` | `—` | positional-or-keyword |
| `connection_id` | `str \| None` | `None` | keyword-only |
| `retries` | `RetryPolicy \| None` | `None` | keyword-only |
| `clock` | `Callable[[], datetime]` | `utcnow` | keyword-only |
| `sleep` | `Callable[[float], Awaitable[None]]` | `asyncio.sleep` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:94](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L94).

```python
engine = StorageEngine(adapter)
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:118](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L118).

```python
engine = StorageEngine(adapter)
```

## jane_storage.engine.StorageEngine.adapter

**Поле екземпляра.** Код: [services/storage/src/jane_storage/engine.py:81](../../../../../../services/storage/src/jane_storage/engine.py#L81).

```python
self.adapter = adapter
```

## jane_storage.engine.StorageEngine.connection_id

**Поле екземпляра.** Код: [services/storage/src/jane_storage/engine.py:82](../../../../../../services/storage/src/jane_storage/engine.py#L82).

```python
self.connection_id = connection_id
```

## jane_storage.engine.StorageEngine.retries

**Поле екземпляра.** Код: [services/storage/src/jane_storage/engine.py:83](../../../../../../services/storage/src/jane_storage/engine.py#L83).

```python
self.retries = retries or RetryPolicy()
```

## jane_storage.engine.StorageEngine.target

**Властивість.** Код: [services/storage/src/jane_storage/engine.py:88](../../../../../../services/storage/src/jane_storage/engine.py#L88).

```python
def target(self) -> dict[str, Any]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Доступ: читання — так; запис — ні.

## jane_storage.engine.StorageEngine.store_entity

**Метод.** Код: [services/storage/src/jane_storage/engine.py:100](../../../../../../services/storage/src/jane_storage/engine.py#L100).

```python
async def store_entity(self, record: Mapping[str, Any], delivery_key: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ConflictRetriesExhausted`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Apply one EntityRecord; returns a ``WriteAck``.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:109](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L109).

```python
ack = await engine.store_entity(rec("price", 2, 5, "o1"), "dk-1#0")
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:119](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L119).

```python
await engine.store_entity(rec("price", 1, 0, "o0"), "dk-0#0")
```

## jane_storage.engine.StorageEngine.store_object

**Метод.** Код: [services/storage/src/jane_storage/engine.py:146](../../../../../../services/storage/src/jane_storage/engine.py#L146).

```python
async def store_object(self, obj: RawObject, delivery_key: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `obj` | `RawObject` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Persist one object (RAW or result document); returns a ``WriteAck``.
```
