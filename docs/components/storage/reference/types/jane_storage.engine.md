# Модуль `jane_storage.engine`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/engine.py](../../../../../services/storage/src/jane_storage/engine.py). Не редагуйте вручну.

Storage core: applies one entity record or one object to an adapter (contracts/docs/storage-adapter.md).

Algorithm for one ``EntityRecord`` (delivery key ``<invocation delivery_key>#<n>``):

1. ``get_delivery`` — already recorded → the stored ack with ``status: duplicate``;
2. ``read_entity`` → :func:`jane_storage.merge.merge` (pure) → ``commit_entity`` with the read version;
3. ``CONFLICT`` → re-read and retry (bounded by ``limits.conflict_retries``); ``DUPLICATE`` → as in step 1; ``COMMITTED`` → ``WriteAck`` ``written | partially_stale | stale``.

Objects: ``get_delivery`` → ``put_object`` (idempotent by key) → ``record_delivery`` (insert-if-absent). The engine never interprets storage-specific errors: ``AdapterError`` propagates to the handler, which turns it into ``HandlerResult.failed``.

## Зміст

- [Клас `ConflictRetriesExhausted`](#клас-conflictretriesexhausted)
- [Клас `StorageEngine`](#клас-storageengine)
- [Функція `backoff_ms`](#функція-backoff_ms)
- [Функція `stored_object_ref`](#функція-stored_object_ref)

## Класи

### Клас `ConflictRetriesExhausted`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.engine` |
| Успадкування | `AdapterError` |
| Код | [engine.py:41](../../../../../services/storage/src/jane_storage/engine.py#L41) |

```python
class ConflictRetriesExhausted(AdapterError): ...
```

Concurrent writers kept winning for longer than ``limits.conflict_retries.max_attempts``.

#### Конструктор `ConflictRetriesExhausted.__init__`

```python
def __init__(self, message: str) -> None: ...
```

Код: [engine.py:44](../../../../../services/storage/src/jane_storage/engine.py#L44).

### Клас `StorageEngine`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.engine` |
| Код | [engine.py:69](../../../../../services/storage/src/jane_storage/engine.py#L69) |

```python
class StorageEngine: ...
```

Core semantics over one opened adapter (one connection).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `target` | `dict[str, Any]` | — | читання (властивість) |  |

#### Конструктор `StorageEngine.__init__`

```python
def __init__(
    self,
    adapter: StorageAdapter,
    *,
    connection_id: str | None = None,
    retries: RetryPolicy | None = None,
    clock: Callable[[], datetime] = utcnow,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> None: ...
```

Код: [engine.py:72](../../../../../services/storage/src/jane_storage/engine.py#L72).

#### Метод `StorageEngine.store_entity`

```python
async def store_entity(self, record: Mapping[str, Any], delivery_key: str) -> dict[str, Any]: ...
```

Apply one EntityRecord; returns a ``WriteAck``.

Винятки в коді методу: `ConflictRetriesExhausted`.

Код: [engine.py:100](../../../../../services/storage/src/jane_storage/engine.py#L100).

#### Метод `StorageEngine.store_object`

```python
async def store_object(self, obj: RawObject, delivery_key: str) -> dict[str, Any]: ...
```

Persist one object (RAW or result document); returns a ``WriteAck``.

Код: [engine.py:146](../../../../../services/storage/src/jane_storage/engine.py#L146).

## Функції

### Функція `backoff_ms`

```python
def backoff_ms(
    policy: RetryPolicy,
    attempt: int,
    rnd: Callable[[], float] = random.random,
) -> float: ...
```

Delay before attempt ``attempt + 1`` (``attempt`` >= 1).

Код: [engine.py:48](../../../../../services/storage/src/jane_storage/engine.py#L48).

### Функція `stored_object_ref`

```python
def stored_object_ref(
    rec: ObjectRecord,
    adapter_kind: str,
    connection_id: str | None,
) -> dict[str, Any]: ...
```

``StoredObjectRef`` of an object record.

Код: [engine.py:54](../../../../../services/storage/src/jane_storage/engine.py#L54).
