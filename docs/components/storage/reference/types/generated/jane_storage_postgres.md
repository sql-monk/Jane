# jane_storage_postgres

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage_postgres.DEFAULT_OPTIONS](#jane_storage_postgresdefault_options)
- [jane_storage_postgres.package_dir](#jane_storage_postgrespackage_dir)
- [jane_storage_postgres.PostgresAdapter](#jane_storage_postgrespostgresadapter)
- [jane_storage_postgres.PostgresAdapter.kind](#jane_storage_postgrespostgresadapterkind)
- [jane_storage_postgres.PostgresAdapter.capabilities](#jane_storage_postgrespostgresadaptercapabilities)
- [jane_storage_postgres.PostgresAdapter.__init__](#jane_storage_postgrespostgresadapter__init__)
- [jane_storage_postgres.PostgresAdapter.pool](#jane_storage_postgrespostgresadapterpool)
- [jane_storage_postgres.PostgresAdapter.open](#jane_storage_postgrespostgresadapteropen)
- [jane_storage_postgres.PostgresAdapter.close](#jane_storage_postgrespostgresadapterclose)
- [jane_storage_postgres.PostgresAdapter.health](#jane_storage_postgrespostgresadapterhealth)
- [jane_storage_postgres.PostgresAdapter.ensure_schema](#jane_storage_postgrespostgresadapterensure_schema)
- [jane_storage_postgres.PostgresAdapter.put_object](#jane_storage_postgrespostgresadapterput_object)
- [jane_storage_postgres.PostgresAdapter.get_object](#jane_storage_postgrespostgresadapterget_object)
- [jane_storage_postgres.PostgresAdapter.read_object_content](#jane_storage_postgrespostgresadapterread_object_content)
- [jane_storage_postgres.PostgresAdapter.list_objects](#jane_storage_postgrespostgresadapterlist_objects)
- [jane_storage_postgres.PostgresAdapter.read_entity](#jane_storage_postgrespostgresadapterread_entity)
- [jane_storage_postgres.PostgresAdapter.commit_entity](#jane_storage_postgrespostgresadaptercommit_entity)
- [jane_storage_postgres.PostgresAdapter.list_entities](#jane_storage_postgrespostgresadapterlist_entities)
- [jane_storage_postgres.PostgresAdapter.list_history](#jane_storage_postgrespostgresadapterlist_history)
- [jane_storage_postgres.PostgresAdapter.get_delivery](#jane_storage_postgrespostgresadapterget_delivery)
- [jane_storage_postgres.PostgresAdapter.record_delivery](#jane_storage_postgrespostgresadapterrecord_delivery)

## jane_storage_postgres.DEFAULT_OPTIONS

**Константа.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:51](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L51).

```python
DEFAULT_OPTIONS: dict[str, int] = {'pool_min_size': 1, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_timeout_ms': 30000}
```

### Опис із вихідного коду

```text
Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
```

## jane_storage_postgres.package_dir

**Функція.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:76](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L76).

```python
def package_dir() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
Directory of the ``jane.storage-postgresql`` storage package (entry point ``jane.storage.packages``).
```

## jane_storage_postgres.PostgresAdapter

**Клас.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:111](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L111).

```python
class PostgresAdapter:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage_postgres.md#jane_storage_postgrespostgresadapterkind) | Поле | ні |
| [capabilities](jane_storage_postgres.md#jane_storage_postgrespostgresadaptercapabilities) | Поле | ні |
| [__init__](jane_storage_postgres.md#jane_storage_postgrespostgresadapter__init__) | Конструктор | ні |
| [pool](jane_storage_postgres.md#jane_storage_postgrespostgresadapterpool) | Властивість | ні |
| [open](jane_storage_postgres.md#jane_storage_postgrespostgresadapteropen) | Метод | ні |
| [close](jane_storage_postgres.md#jane_storage_postgrespostgresadapterclose) | Метод | ні |
| [health](jane_storage_postgres.md#jane_storage_postgrespostgresadapterhealth) | Метод | ні |
| [ensure_schema](jane_storage_postgres.md#jane_storage_postgrespostgresadapterensure_schema) | Метод | ні |
| [put_object](jane_storage_postgres.md#jane_storage_postgrespostgresadapterput_object) | Метод | ні |
| [get_object](jane_storage_postgres.md#jane_storage_postgrespostgresadapterget_object) | Метод | ні |
| [read_object_content](jane_storage_postgres.md#jane_storage_postgrespostgresadapterread_object_content) | Метод | ні |
| [list_objects](jane_storage_postgres.md#jane_storage_postgrespostgresadapterlist_objects) | Метод | ні |
| [read_entity](jane_storage_postgres.md#jane_storage_postgrespostgresadapterread_entity) | Метод | ні |
| [commit_entity](jane_storage_postgres.md#jane_storage_postgrespostgresadaptercommit_entity) | Метод | ні |
| [list_entities](jane_storage_postgres.md#jane_storage_postgrespostgresadapterlist_entities) | Метод | ні |
| [list_history](jane_storage_postgres.md#jane_storage_postgrespostgresadapterlist_history) | Метод | ні |
| [get_delivery](jane_storage_postgres.md#jane_storage_postgrespostgresadapterget_delivery) | Метод | ні |
| [record_delivery](jane_storage_postgres.md#jane_storage_postgrespostgresadapterrecord_delivery) | Метод | ні |

## jane_storage_postgres.PostgresAdapter.kind

**Поле.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:112](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L112).

```python
kind: ClassVar[str] = 'postgresql'
```

Доступ: читання — так; запис — так.

## jane_storage_postgres.PostgresAdapter.capabilities

**Поле.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:113](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L113).

```python
capabilities: ClassVar[frozenset[str]] = frozenset({'objects', 'entities', 'history'})
```

Доступ: читання — так; запис — так.

## jane_storage_postgres.PostgresAdapter.__init__

**Конструктор.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:115](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L115).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage_postgres.PostgresAdapter.pool

**Властивість.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:125](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L125).

```python
def pool(self) -> asyncpg.Pool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `asyncpg.Pool`.

Доступ: читання — так; запис — ні.

Явні `raise` у тілі: `AdapterError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage_postgres.PostgresAdapter.open

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:139](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L139).

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

## jane_storage_postgres.PostgresAdapter.close

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:170](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L170).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage_postgres.PostgresAdapter.health

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:175](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L175).

```python
async def health(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_storage_postgres.PostgresAdapter.ensure_schema

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:182](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L182).

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_types` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage_postgres.PostgresAdapter.put_object

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:252](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L252).

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

## jane_storage_postgres.PostgresAdapter.get_object

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:294](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L294).

```python
async def get_object(self, object_id: str) -> ObjectRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `ObjectRecord | None`.

## jane_storage_postgres.PostgresAdapter.read_object_content

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:301](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L301).

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

## jane_storage_postgres.PostgresAdapter.list_objects

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:310](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L310).

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

## jane_storage_postgres.PostgresAdapter.read_entity

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:365](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L365).

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

## jane_storage_postgres.PostgresAdapter.commit_entity

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:375](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L375).

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

Явні `raise` у тілі: `_Outcome`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage_postgres.PostgresAdapter.list_entities

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:445](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L445).

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

## jane_storage_postgres.PostgresAdapter.list_history

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:475](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L475).

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

## jane_storage_postgres.PostgresAdapter.get_delivery

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:506](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L506).

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `DeliveryRecord | None`.

## jane_storage_postgres.PostgresAdapter.record_delivery

**Метод.** Код: [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py:518](../../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L518).

```python
async def record_delivery(self, record: DeliveryRecord) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `bool`.
