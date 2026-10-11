# jane_storage_files

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage_files.DEFAULT_OPTIONS](#jane_storage_filesdefault_options)
- [jane_storage_files.package_dir](#jane_storage_filespackage_dir)
- [jane_storage_files.FilesystemAdapter](#jane_storage_filesfilesystemadapter)
- [jane_storage_files.FilesystemAdapter.kind](#jane_storage_filesfilesystemadapterkind)
- [jane_storage_files.FilesystemAdapter.capabilities](#jane_storage_filesfilesystemadaptercapabilities)
- [jane_storage_files.FilesystemAdapter.__init__](#jane_storage_filesfilesystemadapter__init__)
- [jane_storage_files.FilesystemAdapter.store](#jane_storage_filesfilesystemadapterstore)
- [jane_storage_files.FilesystemAdapter.open](#jane_storage_filesfilesystemadapteropen)
- [jane_storage_files.FilesystemAdapter.close](#jane_storage_filesfilesystemadapterclose)
- [jane_storage_files.FilesystemAdapter.content_uri](#jane_storage_filesfilesystemadaptercontent_uri)
- [jane_storage_files.FilesystemAdapter.health](#jane_storage_filesfilesystemadapterhealth)
- [jane_storage_files.FilesystemAdapter.ensure_schema](#jane_storage_filesfilesystemadapterensure_schema)
- [jane_storage_files.FilesystemAdapter.put_object](#jane_storage_filesfilesystemadapterput_object)
- [jane_storage_files.FilesystemAdapter.get_object](#jane_storage_filesfilesystemadapterget_object)
- [jane_storage_files.FilesystemAdapter.read_object_content](#jane_storage_filesfilesystemadapterread_object_content)
- [jane_storage_files.FilesystemAdapter.object_statistics](#jane_storage_filesfilesystemadapterobject_statistics)
- [jane_storage_files.FilesystemAdapter.list_objects](#jane_storage_filesfilesystemadapterlist_objects)
- [jane_storage_files.FilesystemAdapter.read_entity](#jane_storage_filesfilesystemadapterread_entity)
- [jane_storage_files.FilesystemAdapter.commit_entity](#jane_storage_filesfilesystemadaptercommit_entity)
- [jane_storage_files.FilesystemAdapter.list_entities](#jane_storage_filesfilesystemadapterlist_entities)
- [jane_storage_files.FilesystemAdapter.list_history](#jane_storage_filesfilesystemadapterlist_history)
- [jane_storage_files.FilesystemAdapter.get_delivery](#jane_storage_filesfilesystemadapterget_delivery)
- [jane_storage_files.FilesystemAdapter.record_delivery](#jane_storage_filesfilesystemadapterrecord_delivery)

## jane_storage_files.DEFAULT_OPTIONS

**Константа.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:73](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L73).

```python
DEFAULT_OPTIONS: dict[str, int] = {'lock_timeout_ms': 30000, 'lock_stale_ms': 120000, 'lock_poll_ms': 10, 'replace_retry_ms': 5000}
```

### Опис із вихідного коду

```text
Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:162](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L162).

```python
store = mod._Store(tmp_path, None, {**mod.DEFAULT_OPTIONS, "lock_stale_ms": 60_000})
```

## jane_storage_files.package_dir

**Функція.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:82](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L82).

```python
def package_dir() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
Directory of the ``jane.storage-files`` storage package (entry point ``jane.storage.packages``).
```

## jane_storage_files.FilesystemAdapter

**Клас.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:566](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L566).

```python
class FilesystemAdapter:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage_files.md#jane_storage_filesfilesystemadapterkind) | Поле | ні |
| [capabilities](jane_storage_files.md#jane_storage_filesfilesystemadaptercapabilities) | Поле | ні |
| [__init__](jane_storage_files.md#jane_storage_filesfilesystemadapter__init__) | Конструктор | ні |
| [store](jane_storage_files.md#jane_storage_filesfilesystemadapterstore) | Властивість | ні |
| [open](jane_storage_files.md#jane_storage_filesfilesystemadapteropen) | Метод | ні |
| [close](jane_storage_files.md#jane_storage_filesfilesystemadapterclose) | Метод | ні |
| [content_uri](jane_storage_files.md#jane_storage_filesfilesystemadaptercontent_uri) | Метод | ні |
| [health](jane_storage_files.md#jane_storage_filesfilesystemadapterhealth) | Метод | ні |
| [ensure_schema](jane_storage_files.md#jane_storage_filesfilesystemadapterensure_schema) | Метод | ні |
| [put_object](jane_storage_files.md#jane_storage_filesfilesystemadapterput_object) | Метод | ні |
| [get_object](jane_storage_files.md#jane_storage_filesfilesystemadapterget_object) | Метод | ні |
| [read_object_content](jane_storage_files.md#jane_storage_filesfilesystemadapterread_object_content) | Метод | ні |
| [object_statistics](jane_storage_files.md#jane_storage_filesfilesystemadapterobject_statistics) | Метод | ні |
| [list_objects](jane_storage_files.md#jane_storage_filesfilesystemadapterlist_objects) | Метод | ні |
| [read_entity](jane_storage_files.md#jane_storage_filesfilesystemadapterread_entity) | Метод | ні |
| [commit_entity](jane_storage_files.md#jane_storage_filesfilesystemadaptercommit_entity) | Метод | ні |
| [list_entities](jane_storage_files.md#jane_storage_filesfilesystemadapterlist_entities) | Метод | ні |
| [list_history](jane_storage_files.md#jane_storage_filesfilesystemadapterlist_history) | Метод | ні |
| [get_delivery](jane_storage_files.md#jane_storage_filesfilesystemadapterget_delivery) | Метод | ні |
| [record_delivery](jane_storage_files.md#jane_storage_filesfilesystemadapterrecord_delivery) | Метод | ні |

### Опис із вихідного коду

```text
``StorageAdapter`` over a local or mounted directory (connection ``params.base_path``).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:39](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L39).

```python
adapter = FilesystemAdapter()
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:146](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L146).

```python
adapter = FilesystemAdapter()
```

## jane_storage_files.FilesystemAdapter.kind

**Поле.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:569](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L569).

```python
kind: ClassVar[str] = 'filesystem'
```

Доступ: читання — так; запис — так.

## jane_storage_files.FilesystemAdapter.capabilities

**Поле.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:570](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L570).

```python
capabilities: ClassVar[frozenset[str]] = frozenset({'objects', 'entities', 'history'})
```

Доступ: читання — так; запис — так.

## jane_storage_files.FilesystemAdapter.__init__

**Конструктор.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:572](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L572).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:39](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L39).

```python
adapter = FilesystemAdapter()
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:146](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L146).

```python
adapter = FilesystemAdapter()
```

## jane_storage_files.FilesystemAdapter.store

**Властивість.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:576](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L576).

```python
def store(self) -> _Store:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `_Store`.

Доступ: читання — так; запис — ні.

Явні `raise` у тілі: `AdapterError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_storage_files.FilesystemAdapter.open

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:589](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L589).

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

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:40](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L40).

```python
await adapter.open(conn(base), options)
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:148](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L148).

```python
await adapter.open(conn(tmp_path), {"prefix": "../escape"})
```

## jane_storage_files.FilesystemAdapter.close

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:607](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L607).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage_files.FilesystemAdapter.content_uri

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:610](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L610).

```python
def content_uri(self, rec: ObjectRecord) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `rec` | `ObjectRecord` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Persistent ``file://`` URI of a stored object (``ContentRef`` blob, single-node deployments).
```

## jane_storage_files.FilesystemAdapter.health

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:614](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L614).

```python
async def health(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_storage_files.FilesystemAdapter.ensure_schema

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:620](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L620).

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

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:41](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L41).

```python
await adapter.ensure_schema(["product"])
```

## jane_storage_files.FilesystemAdapter.put_object

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:623](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L623).

```python
async def put_object(self, obj: RawObject) -> ObjectRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `obj` | `RawObject` | `—` | positional-or-keyword |

Результат: `ObjectRecord`.

## jane_storage_files.FilesystemAdapter.get_object

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:626](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L626).

```python
async def get_object(self, object_id: str) -> ObjectRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `ObjectRecord | None`.

## jane_storage_files.FilesystemAdapter.read_object_content

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:629](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L629).

```python
async def read_object_content(self, object_id: str) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `bytes`.

## jane_storage_files.FilesystemAdapter.object_statistics

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:632](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L632).

```python
async def object_statistics(self) -> dict[str, int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, int]`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_storage_status.py:135](../../../../../../services/storage/tests/test_storage_status.py#L135).

```python
original = FilesystemAdapter.object_statistics
```

## jane_storage_files.FilesystemAdapter.list_objects

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:640](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L640).

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

## jane_storage_files.FilesystemAdapter.read_entity

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:652](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L652).

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

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:82](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L82).

```python
snap = await adapter.read_entity("product", KEY)
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:111](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L111).

```python
snap = await adapter.read_entity("product", KEY)
```

## jane_storage_files.FilesystemAdapter.commit_entity

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:655](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L655).

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

## jane_storage_files.FilesystemAdapter.list_entities

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:660](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L660).

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

## jane_storage_files.FilesystemAdapter.list_history

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:671](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L671).

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

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:86](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L86).

```python
history, cursor = await adapter.list_history("product", KEY, limit=1000)
```

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:124](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L124).

```python
history, _ = await adapter.list_history("product", KEY, limit=10)
```

## jane_storage_files.FilesystemAdapter.get_delivery

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:676](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L676).

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `delivery_key` | `str` | `—` | positional-or-keyword |

Результат: `DeliveryRecord | None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:108](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L108).

```python
assert await adapter.get_delivery("dk-1#0") is None
```

## jane_storage_files.FilesystemAdapter.record_delivery

**Метод.** Код: [services/storage/adapters/files/src/jane_storage_files/__init__.py:679](../../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L679).

```python
async def record_delivery(self, record: DeliveryRecord) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `bool`.
