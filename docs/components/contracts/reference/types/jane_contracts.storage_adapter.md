# Модуль `jane_contracts.storage_adapter`

> Згенеровано `scripts/docs_reference.py` з [contracts/python/src/jane_contracts/storage_adapter.py](../../../../../contracts/python/src/jane_contracts/storage_adapter.py). Не редагуйте вручну.

Storage adapter contract for the storage handler.

Owners: WP-07 implements the storage core (handler protocol, merge semantics, ordering, delivery dedup, test mode, default formats) plus the ``filesystem`` and ``postgresql`` adapters and the **compatibility suite**; WP-08 implements ``sqlserver``, ``mongodb``, ``minio`` and ``s3``.

Principle: the *core* owns all semantics of EntityRecord application (partial update, explicit clear, observation ordering, stale detection) as a pure function; an adapter only provides durable primitives with two guarantees:

1. :meth:`StorageAdapter.commit_entity` is atomic: delivery-key uniqueness, compare-and-swap on the snapshot ``version`` and the history append succeed or fail together.
2. :meth:`StorageAdapter.put_object` is idempotent by ``object_key``.

Scenarios every adapter must pass are listed in contracts/docs/storage-adapter.md (C-01…C-16); all of them are mandatory for all six initial adapters, including the object stores. Adapters never read environment variables or secret stores: the core resolves ``secret_refs`` and passes a :class:`ResolvedConnection`.

## Зміст

- [Клас `ResolvedConnection`](#клас-resolvedconnection)
- [Клас `OrderKey`](#клас-orderkey)
- [Клас `RawObject`](#клас-rawobject)
- [Клас `ObjectRecord`](#клас-objectrecord)
- [Клас `EntitySnapshot`](#клас-entitysnapshot)
- [Клас `HistoryEvent`](#клас-historyevent)
- [Клас `DeliveryRecord`](#клас-deliveryrecord)
- [Клас `CommitOutcome`](#клас-commitoutcome)
- [Клас `CommitResult`](#клас-commitresult)
- [Клас `AdapterError`](#клас-adaptererror)
- [Клас `StorageAdapter`](#клас-storageadapter)
- [Функція `order_tuple`](#функція-order_tuple)

## Класи

### Клас `ResolvedConnection`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:33](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L33) |

```python
@dataclass(frozen=True, slots=True)
class ResolvedConnection: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connection_id` | `str` | — | читання |  |
| `kind` | `str` | — | читання |  |
| `params` | `Mapping[str, Any]` | — | читання |  |
| `secrets` | `Mapping[str, str]` | `field(repr=False, default_factory=dict)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `OrderKey`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:41](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L41) |

```python
@dataclass(frozen=True, slots=True)
class OrderKey: ...
```

Observation order (entity.schema.json#/$defs/ObservationOrder). Compare with :func:`order_tuple`.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `observed_at` | `datetime` | — | читання |  |
| `observation_id` | `str` | — | читання |  |
| `sequence` | `int \| None` | `None` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `RawObject`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:55](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L55) |

```python
@dataclass(frozen=True, slots=True)
class RawObject: ...
```

A material (RAW) or result document to persist as an object.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `object_key` | `str` | — | читання | Deterministic key built by the core: ``<source_id>/<yyyy>/<mm>/<dd>/<material_id>/<observation_id>.<ext>`` (filesystem-safe: ':' replaced by '_'). Same key + same sha256 = same object. |
| `material_id` | `str` | — | читання |  |
| `observation_id` | `str` | — | читання |  |
| `source_id` | `str \| None` | — | читання |  |
| `media_type` | `str` | — | читання |  |
| `format` | `RawFormat` | — | читання |  |
| `content` | `bytes` | — | читання |  |
| `sha256` | `str` | — | читання |  |
| `metadata` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання | Material without content (JSON-compatible), stored next to the object for reprocessing. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ObjectRecord`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:73](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L73) |

```python
@dataclass(frozen=True, slots=True)
class ObjectRecord: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `object_id` | `str` | — | читання |  |
| `object_key` | `str` | — | читання |  |
| `locator` | `Mapping[str, str \| int]` | — | читання |  |
| `media_type` | `str` | — | читання |  |
| `size_bytes` | `int` | — | читання |  |
| `sha256` | `str` | — | читання |  |
| `stored_at` | `datetime` | — | читання |  |
| `metadata` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `EntitySnapshot`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:85](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L85) |

```python
@dataclass(frozen=True, slots=True)
class EntitySnapshot: ...
```

Current state of one entity (entity.schema.json#/$defs/EntityState).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `entity_type` | `str` | — | читання |  |
| `canonical_key` | `str` | — | читання |  |
| `key` | `Mapping[str, Any]` | — | читання |  |
| `fields` | `Mapping[str, Any]` | — | читання |  |
| `field_orders` | `Mapping[str, OrderKey]` | — | читання |  |
| `cleared_fields` | `frozenset[str]` | — | читання |  |
| `version` | `int` | — | читання |  |
| `updated_at` | `datetime` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `HistoryEvent`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:99](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L99) |

```python
@dataclass(frozen=True, slots=True)
class HistoryEvent: ...
```

One accepted update (also stale ones) — entity.schema.json#/$defs/EntityHistoryEntry.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `entity_type` | `str` | — | читання |  |
| `canonical_key` | `str` | — | читання |  |
| `record` | `Mapping[str, Any]` | — | читання |  |
| `delivery_key` | `str` | — | читання |  |
| `received_at` | `datetime` | — | читання |  |
| `applied_fields` | `Sequence[str]` | — | читання |  |
| `stale_fields` | `Sequence[str]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `DeliveryRecord`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:112](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L112) |

```python
@dataclass(frozen=True, slots=True)
class DeliveryRecord: ...
```

What was acknowledged for a delivery key (serialized WriteAck list).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `delivery_key` | `str` | — | читання |  |
| `recorded_at` | `datetime` | — | читання |  |
| `acks` | `Sequence[Mapping[str, Any]]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `CommitOutcome`

| Властивість | Значення |
|---|---|
| Вид | перелік |
| Модуль | `jane_contracts.storage_adapter` |
| Успадкування | `Enum` |
| Код | [storage_adapter.py:120](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L120) |

```python
class CommitOutcome(Enum): ...
```

**Значення переліку**

| Назва | Значення | Опис |
|---|---|---|
| `COMMITTED` | `'committed'` |  |
| `CONFLICT` | `'conflict'` | ``expected_version`` did not match: the core re-reads, re-merges and retries (bounded). |
| `DUPLICATE` | `'duplicate'` | The delivery key (for this entity) was already committed: nothing written. |

### Клас `CommitResult`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.storage_adapter` |
| Код | [storage_adapter.py:129](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L129) |

```python
@dataclass(frozen=True, slots=True)
class CommitResult: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `outcome` | `CommitOutcome` | — | читання |  |
| `snapshot` | `EntitySnapshot \| None` | — | читання | Snapshot after the commit (COMMITTED) or the current one (CONFLICT/DUPLICATE), if known. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `AdapterError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_contracts.storage_adapter` |
| Успадкування | `Exception` |
| Код | [storage_adapter.py:135](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L135) |

```python
class AdapterError(Exception): ...
```

Adapter failure. ``retryable`` maps to Problem.retryable / HandlerResult.failure.retryable.

#### Конструктор `AdapterError.__init__`

```python
def __init__(self, message: str, *, retryable: bool) -> None: ...
```

Код: [storage_adapter.py:138](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L138).

### Клас `StorageAdapter`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_contracts.storage_adapter` |
| Успадкування | `Protocol` |
| Код | [storage_adapter.py:144](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L144) |

```python
@runtime_checkable
class StorageAdapter(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | — | читання | ``filesystem``, ``postgresql``, ``sqlserver``, ``mongodb``, ``minio``, ``s3``. |
| `capabilities` | `ClassVar[frozenset[str]]` | — | читання | Must equal {"objects", "entities", "history"} for every initial adapter (TZ §12 item 12: each adapter stores both RAW and structured results). Object stores (minio, s3) keep entity snapshots, history events and delivery records as JSON documents and implement :meth:`commit_entity` with conditional writes (If-None-Match: * for create, If-Match: &lt;ETag> for update); see contracts/docs/storage-adapter.md, section "Object stores". |

#### Метод `StorageAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Код: [storage_adapter.py:154](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L154).

#### Метод `StorageAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [storage_adapter.py:156](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L156).

#### Метод `StorageAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [storage_adapter.py:158](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L158).

#### Метод `StorageAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Idempotently create tables/collections/buckets/directories.

Код: [storage_adapter.py:160](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L160).

#### Метод `StorageAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Idempotent by ``object_key``: an existing object with the same sha256 is returned as is; a different sha256 raises ``AdapterError(retryable=False)``.

Код: [storage_adapter.py:166](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L166).

#### Метод `StorageAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [storage_adapter.py:171](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L171).

#### Метод `StorageAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Код: [storage_adapter.py:173](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L173).

#### Метод `StorageAdapter.list_objects`

```python
async def list_objects(
    self,
    *,
    source_id: str | None = None,
    material_id: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[ObjectRecord], str | None]: ...
```

Код: [storage_adapter.py:175](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L175).

#### Метод `StorageAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [storage_adapter.py:188](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L188).

#### Метод `StorageAdapter.commit_entity`

```python
async def commit_entity(
    self,
    *,
    new: EntitySnapshot,
    expected_version: int | None,
    event: HistoryEvent,
) -> CommitResult: ...
```

Atomically: if (event.delivery_key, entity) already recorded → DUPLICATE; else if the stored version != expected_version (None = must not exist) → CONFLICT; else write ``new`` (whose version = expected_version + 1, or 1) and append ``event`` → COMMITTED. A stale-only update is committed with ``new`` equal to the current snapshot fields and the same version + 1.

Код: [storage_adapter.py:190](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L190).

#### Метод `StorageAdapter.list_entities`

```python
async def list_entities(
    self,
    entity_type: str,
    *,
    scope: str | None = None,
    updated_since: datetime | None = None,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[EntitySnapshot], str | None]: ...
```

Код: [storage_adapter.py:199](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L199).

#### Метод `StorageAdapter.list_history`

```python
async def list_history(
    self,
    entity_type: str,
    canonical_key: str,
    *,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[HistoryEvent], str | None]: ...
```

Код: [storage_adapter.py:209](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L209).

#### Метод `StorageAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [storage_adapter.py:215](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L215).

#### Метод `StorageAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Insert-if-absent. Returns False if the key already exists (used for object-only writes).

Код: [storage_adapter.py:217](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L217).

## Функції

### Функція `order_tuple`

```python
def order_tuple(key: OrderKey) -> tuple[datetime, int, str]: ...
```

Total order used by the core: observed_at, then sequence (missing = -1), then observation_id.

Код: [storage_adapter.py:49](../../../../../contracts/python/src/jane_contracts/storage_adapter.py#L49).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `RawFormat` | — | `Literal['original', 'html', 'json']` |  |
