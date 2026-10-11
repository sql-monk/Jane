# jane_storage_mongodb

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage_mongodb.DEFAULT_OPTIONS](#jane_storage_mongodbdefault_options)
- [jane_storage_mongodb.package_dir](#jane_storage_mongodbpackage_dir)
- [jane_storage_mongodb.MongoAdapter](#jane_storage_mongodbmongoadapter)
- [jane_storage_mongodb.MongoAdapter.kind](#jane_storage_mongodbmongoadapterkind)
- [jane_storage_mongodb.MongoAdapter.capabilities](#jane_storage_mongodbmongoadaptercapabilities)
- [jane_storage_mongodb.MongoAdapter.__init__](#jane_storage_mongodbmongoadapter__init__)
- [jane_storage_mongodb.MongoAdapter.open](#jane_storage_mongodbmongoadapteropen)
- [jane_storage_mongodb.MongoAdapter.close](#jane_storage_mongodbmongoadapterclose)
- [jane_storage_mongodb.MongoAdapter.health](#jane_storage_mongodbmongoadapterhealth)
- [jane_storage_mongodb.MongoAdapter.ensure_schema](#jane_storage_mongodbmongoadapterensure_schema)
- [jane_storage_mongodb.MongoAdapter.put_object](#jane_storage_mongodbmongoadapterput_object)
- [jane_storage_mongodb.MongoAdapter.get_object](#jane_storage_mongodbmongoadapterget_object)
- [jane_storage_mongodb.MongoAdapter.read_object_content](#jane_storage_mongodbmongoadapterread_object_content)
- [jane_storage_mongodb.MongoAdapter.list_objects](#jane_storage_mongodbmongoadapterlist_objects)
- [jane_storage_mongodb.MongoAdapter.read_entity](#jane_storage_mongodbmongoadapterread_entity)
- [jane_storage_mongodb.MongoAdapter.commit_entity](#jane_storage_mongodbmongoadaptercommit_entity)
- [jane_storage_mongodb.MongoAdapter.list_entities](#jane_storage_mongodbmongoadapterlist_entities)
- [jane_storage_mongodb.MongoAdapter.list_history](#jane_storage_mongodbmongoadapterlist_history)
- [jane_storage_mongodb.MongoAdapter.get_delivery](#jane_storage_mongodbmongoadapterget_delivery)
- [jane_storage_mongodb.MongoAdapter.record_delivery](#jane_storage_mongodbmongoadapterrecord_delivery)

## jane_storage_mongodb.DEFAULT_OPTIONS

**Константа.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:83](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L83).

```python
DEFAULT_OPTIONS: dict[str, int] = {'pool_min_size': 0, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_timeout_ms': 30000, 'chunk_bytes': 4 * 1024 * 1024}
```

### Опис із вихідного коду

```text
Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``chunk_bytes`` — size of one RAW chunk document (BSON documents are limited to 16 MiB).
```

## jane_storage_mongodb.package_dir

**Функція.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:107](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L107).

```python
def package_dir() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
Directory of the ``jane.storage-mongodb`` storage package (entry point ``jane.storage.packages``).
```

## jane_storage_mongodb.MongoAdapter

**Клас.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:141](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L141).

```python
class MongoAdapter:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterkind) | Поле | ні |
| [capabilities](jane_storage_mongodb.md#jane_storage_mongodbmongoadaptercapabilities) | Поле | ні |
| [__init__](jane_storage_mongodb.md#jane_storage_mongodbmongoadapter__init__) | Конструктор | ні |
| [open](jane_storage_mongodb.md#jane_storage_mongodbmongoadapteropen) | Метод | ні |
| [close](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterclose) | Метод | ні |
| [health](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterhealth) | Метод | ні |
| [ensure_schema](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterensure_schema) | Метод | ні |
| [put_object](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterput_object) | Метод | ні |
| [get_object](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterget_object) | Метод | ні |
| [read_object_content](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterread_object_content) | Метод | ні |
| [list_objects](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterlist_objects) | Метод | ні |
| [read_entity](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterread_entity) | Метод | ні |
| [commit_entity](jane_storage_mongodb.md#jane_storage_mongodbmongoadaptercommit_entity) | Метод | ні |
| [list_entities](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterlist_entities) | Метод | ні |
| [list_history](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterlist_history) | Метод | ні |
| [get_delivery](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterget_delivery) | Метод | ні |
| [record_delivery](jane_storage_mongodb.md#jane_storage_mongodbmongoadapterrecord_delivery) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:37](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L37).

```python
adapter = MongoAdapter()
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:45](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L45).

```python
adapter = MongoAdapter()
```

## jane_storage_mongodb.MongoAdapter.kind

**Поле.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:142](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L142).

```python
kind: ClassVar[str] = 'mongodb'
```

Доступ: читання — так; запис — так.

## jane_storage_mongodb.MongoAdapter.capabilities

**Поле.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:143](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L143).

```python
capabilities: ClassVar[frozenset[str]] = frozenset({'objects', 'entities', 'history'})
```

Доступ: читання — так; запис — так.

## jane_storage_mongodb.MongoAdapter.__init__

**Конструктор.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:145](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L145).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:37](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L37).

```python
adapter = MongoAdapter()
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:45](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L45).

```python
adapter = MongoAdapter()
```

## jane_storage_mongodb.MongoAdapter.open

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:166](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L166).

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection` | `ResolvedConnection` | `—` | positional-or-keyword |
| `options` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `AdapterError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:38](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L38).

```python
await adapter.open(
        ResolvedConnection("m", "mongodb", {"host": "mongo.invalid", "database": "jane"}, {"username": "u"}),
        {"prefix": "stage_", "connect_timeout_ms": 1500, "pool_max_size": 3, "chunk_bytes": 1024},
    )
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:52](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L52).

```python
await adapter.open(conn, {"connect_timeout_ms": 3000})
```

## jane_storage_mongodb.MongoAdapter.close

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:203](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L203).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:49](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L49).

```python
await adapter.close()
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:86](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L86).

```python
await adapter.close()
```

## jane_storage_mongodb.MongoAdapter.health

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:208](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L208).

```python
async def health(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_storage_mongodb.MongoAdapter.ensure_schema

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:218](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L218).

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_types` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:53](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L53).

```python
await adapter.ensure_schema(["product"])
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:112](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L112).

```python
await adapter.ensure_schema(["product"])
```

## jane_storage_mongodb.MongoAdapter.put_object

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:239](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L239).

```python
async def put_object(self, obj: RawObject) -> ObjectRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `obj` | `RawObject` | `—` | positional-or-keyword |

Результат: `ObjectRecord`.

Явні `raise` у тілі: `AdapterError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage_mongodb.MongoAdapter.get_object

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:292](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L292).

```python
async def get_object(self, object_id: str) -> ObjectRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `ObjectRecord | None`.

## jane_storage_mongodb.MongoAdapter.read_object_content

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:297](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L297).

```python
async def read_object_content(self, object_id: str) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `AdapterError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage_mongodb.MongoAdapter.list_objects

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:314](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L314).

```python
async def list_objects(self, *, source_id: str | None=None, material_id: str | None=None, since: datetime | None=None, until: datetime | None=None, cursor: str | None=None, limit: int) -> tuple[Sequence[ObjectRecord], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `None` | keyword-only |
| `material_id` | `str \| None` | `None` | keyword-only |
| `since` | `datetime \| None` | `None` | keyword-only |
| `until` | `datetime \| None` | `None` | keyword-only |
| `cursor` | `str \| None` | `None` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[Sequence[ObjectRecord], str | None]`.

## jane_storage_mongodb.MongoAdapter.read_entity

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:356](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L356).

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |

Результат: `EntitySnapshot | None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:65](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L65).

```python
snap = await adapter.read_entity("product", key)
```

## jane_storage_mongodb.MongoAdapter.commit_entity

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:391](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L391).

```python
async def commit_entity(self, *, new: EntitySnapshot, expected_version: int | None, event: HistoryEvent) -> CommitResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `new` | `EntitySnapshot` | `—` | keyword-only |
| `expected_version` | `int \| None` | `—` | keyword-only |
| `event` | `HistoryEvent` | `—` | keyword-only |

Результат: `CommitResult`.

## jane_storage_mongodb.MongoAdapter.list_entities

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:443](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L443).

```python
async def list_entities(self, entity_type: str, *, scope: str | None=None, updated_since: datetime | None=None, cursor: str | None=None, limit: int) -> tuple[Sequence[EntitySnapshot], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `scope` | `str \| None` | `None` | keyword-only |
| `updated_since` | `datetime \| None` | `None` | keyword-only |
| `cursor` | `str \| None` | `None` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[Sequence[EntitySnapshot], str | None]`.

## jane_storage_mongodb.MongoAdapter.list_history

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:471](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L471).

```python
async def list_history(self, entity_type: str, canonical_key: str, *, cursor: str | None=None, limit: int) -> tuple[Sequence[HistoryEvent], str | None]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_type` | `str` | `—` | positional-or-keyword |
| `canonical_key` | `str` | `—` | positional-or-keyword |
| `cursor` | `str \| None` | `None` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `tuple[Sequence[HistoryEvent], str | None]`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:117](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L117).

```python
events, _ = await adapter.list_history("product", key, limit=100)
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:67](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L67).

```python
history, _ = await adapter.list_history("product", key, limit=1)
```

## jane_storage_mongodb.MongoAdapter.get_delivery

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:496](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L496).

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `DeliveryRecord | None`.

## jane_storage_mongodb.MongoAdapter.record_delivery

**Метод.** Код: [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py:514](../../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L514).

```python
async def record_delivery(self, record: DeliveryRecord) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `bool`.
