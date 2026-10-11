# jane_storage_sqlserver

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage_sqlserver.DEFAULT_OPTIONS](#jane_storage_sqlserverdefault_options)
- [jane_storage_sqlserver.package_dir](#jane_storage_sqlserverpackage_dir)
- [jane_storage_sqlserver.SqlServerAdapter](#jane_storage_sqlserversqlserveradapter)
- [jane_storage_sqlserver.SqlServerAdapter.kind](#jane_storage_sqlserversqlserveradapterkind)
- [jane_storage_sqlserver.SqlServerAdapter.capabilities](#jane_storage_sqlserversqlserveradaptercapabilities)
- [jane_storage_sqlserver.SqlServerAdapter.__init__](#jane_storage_sqlserversqlserveradapter__init__)
- [jane_storage_sqlserver.SqlServerAdapter.open](#jane_storage_sqlserversqlserveradapteropen)
- [jane_storage_sqlserver.SqlServerAdapter.close](#jane_storage_sqlserversqlserveradapterclose)
- [jane_storage_sqlserver.SqlServerAdapter.health](#jane_storage_sqlserversqlserveradapterhealth)
- [jane_storage_sqlserver.SqlServerAdapter.ensure_schema](#jane_storage_sqlserversqlserveradapterensure_schema)
- [jane_storage_sqlserver.SqlServerAdapter.put_object](#jane_storage_sqlserversqlserveradapterput_object)
- [jane_storage_sqlserver.SqlServerAdapter.get_object](#jane_storage_sqlserversqlserveradapterget_object)
- [jane_storage_sqlserver.SqlServerAdapter.read_object_content](#jane_storage_sqlserversqlserveradapterread_object_content)
- [jane_storage_sqlserver.SqlServerAdapter.list_objects](#jane_storage_sqlserversqlserveradapterlist_objects)
- [jane_storage_sqlserver.SqlServerAdapter.read_entity](#jane_storage_sqlserversqlserveradapterread_entity)
- [jane_storage_sqlserver.SqlServerAdapter.commit_entity](#jane_storage_sqlserversqlserveradaptercommit_entity)
- [jane_storage_sqlserver.SqlServerAdapter.list_entities](#jane_storage_sqlserversqlserveradapterlist_entities)
- [jane_storage_sqlserver.SqlServerAdapter.list_history](#jane_storage_sqlserversqlserveradapterlist_history)
- [jane_storage_sqlserver.SqlServerAdapter.get_delivery](#jane_storage_sqlserversqlserveradapterget_delivery)
- [jane_storage_sqlserver.SqlServerAdapter.record_delivery](#jane_storage_sqlserversqlserveradapterrecord_delivery)

## jane_storage_sqlserver.DEFAULT_OPTIONS

**Константа.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:75](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L75).

```python
DEFAULT_OPTIONS: dict[str, int] = {'pool_min_size': 1, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_timeout_ms': 30000, 'lock_timeout_ms': 30000}
```

### Опис із вихідного коду

```text
Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``lock_timeout_ms`` bounds the wait for the ``ensure_schema`` application lock.
```

## jane_storage_sqlserver.package_dir

**Функція.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:98](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L98).

```python
def package_dir() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
Directory of the ``jane.storage-sqlserver`` storage package (entry point ``jane.storage.packages``).
```

## jane_storage_sqlserver.SqlServerAdapter

**Клас.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:173](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L173).

```python
class SqlServerAdapter:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterkind) | Поле | ні |
| [capabilities](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradaptercapabilities) | Поле | ні |
| [__init__](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapter__init__) | Конструктор | ні |
| [open](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapteropen) | Метод | ні |
| [close](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterclose) | Метод | ні |
| [health](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterhealth) | Метод | ні |
| [ensure_schema](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterensure_schema) | Метод | ні |
| [put_object](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterput_object) | Метод | ні |
| [get_object](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterget_object) | Метод | ні |
| [read_object_content](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterread_object_content) | Метод | ні |
| [list_objects](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterlist_objects) | Метод | ні |
| [read_entity](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterread_entity) | Метод | ні |
| [commit_entity](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradaptercommit_entity) | Метод | ні |
| [list_entities](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterlist_entities) | Метод | ні |
| [list_history](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterlist_history) | Метод | ні |
| [get_delivery](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterget_delivery) | Метод | ні |
| [record_delivery](jane_storage_sqlserver.md#jane_storage_sqlserversqlserveradapterrecord_delivery) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/sqlserver/tests/test_sqlserver_config.py:38](../../../../../../services/storage/adapters/sqlserver/tests/test_sqlserver_config.py#L38).

```python
adapter = SqlServerAdapter()
```

## jane_storage_sqlserver.SqlServerAdapter.kind

**Поле.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:174](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L174).

```python
kind: ClassVar[str] = 'sqlserver'
```

Доступ: читання — так; запис — так.

## jane_storage_sqlserver.SqlServerAdapter.capabilities

**Поле.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:175](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L175).

```python
capabilities: ClassVar[frozenset[str]] = frozenset({'objects', 'entities', 'history'})
```

Доступ: читання — так; запис — так.

## jane_storage_sqlserver.SqlServerAdapter.__init__

**Конструктор.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:177](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L177).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/sqlserver/tests/test_sqlserver_config.py:38](../../../../../../services/storage/adapters/sqlserver/tests/test_sqlserver_config.py#L38).

```python
adapter = SqlServerAdapter()
```

## jane_storage_sqlserver.SqlServerAdapter.open

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:204](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L204).

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

Контекст і передумови: [services/storage/adapters/sqlserver/tests/test_sqlserver_config.py:39](../../../../../../services/storage/adapters/sqlserver/tests/test_sqlserver_config.py#L39).

```python
await adapter.open(
        ResolvedConnection(
            "s", "sqlserver", {"host": "mssql.invalid", "database": "jane", "schema": "stage"}
        ),
        {"pool_min_size": 0, "table_prefix": "raw_"},
    )
```

## jane_storage_sqlserver.SqlServerAdapter.close

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:248](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L248).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/sqlserver/tests/test_sqlserver_config.py:48](../../../../../../services/storage/adapters/sqlserver/tests/test_sqlserver_config.py#L48).

```python
await adapter.close()
```

## jane_storage_sqlserver.SqlServerAdapter.health

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:253](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L253).

```python
async def health(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_storage_sqlserver.SqlServerAdapter.ensure_schema

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:260](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L260).

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entity_types` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage_sqlserver.SqlServerAdapter.put_object

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:314](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L314).

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

## jane_storage_sqlserver.SqlServerAdapter.get_object

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:374](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L374).

```python
async def get_object(self, object_id: str) -> ObjectRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `ObjectRecord | None`.

## jane_storage_sqlserver.SqlServerAdapter.read_object_content

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:379](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L379).

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

## jane_storage_sqlserver.SqlServerAdapter.list_objects

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:386](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L386).

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

## jane_storage_sqlserver.SqlServerAdapter.read_entity

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:429](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L429).

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

## jane_storage_sqlserver.SqlServerAdapter.commit_entity

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:435](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L435).

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

## jane_storage_sqlserver.SqlServerAdapter.list_entities

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:495](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L495).

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

## jane_storage_sqlserver.SqlServerAdapter.list_history

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:526](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L526).

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

## jane_storage_sqlserver.SqlServerAdapter.get_delivery

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:541](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L541).

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `DeliveryRecord | None`.

## jane_storage_sqlserver.SqlServerAdapter.record_delivery

**Метод.** Код: [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py:548](../../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L548).

```python
async def record_delivery(self, record: DeliveryRecord) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `bool`.
