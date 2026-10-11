# Модуль `jane_storage_files`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/files/src/jane_storage_files/__init__.py](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py). Не редагуйте вручну.

Filesystem adapter of the Jane storage handler (``kind: filesystem``).

Layout under ``<base_path>/<prefix>`` (contracts/docs/storage-adapter.md, object stores and files):

| Path | Content | |---|---| | ``entities/<entity_type>/<sha256(canonical_key)>.json`` | ``EntitySnapshot`` | | ``history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json`` | ``HistoryEvent`` (``entities_format: json``) | | ``history/<entity_type>/<sha256(canonical_key)>.jsonl`` | one event per line (``entities_format: jsonl``) | | ``deliveries/<sha256(delivery_key)>.json`` | ``DeliveryRecord`` | | ``objects/<object_key>`` + ``.meta.json`` | bytes + ``ObjectRecord`` (the meta file is the commit marker) | | ``index/objects/<object_id>.json`` | ``object_id`` → ``object_key`` | | ``locks/…/<name>.lock`` | lock files (``O_CREAT | O_EXCL``) |

Atomicity on Windows and Linux: every document is written to a temporary file in the same directory, flushed with ``fsync`` and moved into place with ``os.replace`` (retried while Windows reports the target as in use by a reader); exclusive creation uses ``os.link`` of a complete temporary file (falls back to ``O_CREAT | O_EXCL`` where hard links are unavailable). ``commit_entity`` and ``put_object`` run under a per-key lock file created with ``O_CREAT | O_EXCL``; a lock older than ``lock_stale_ms`` (a crashed writer) is broken. Commit order: delivery record → history event → snapshot; a delivery record whose snapshot/history does not confirm it is incomplete (crash) and is redone.

## Класи

### Клас `FilesystemAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_files` |
| Код | [__init__.py:642](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L642) |

```python
class FilesystemAdapter: ...
```

``StorageAdapter`` over a local or mounted directory (connection ``params.base_path``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'filesystem'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання |  |
| `store` | `_Store` | — | читання (властивість) |  |

#### Конструктор `FilesystemAdapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:648](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L648).

#### Метод `FilesystemAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:673](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L673).

#### Метод `FilesystemAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:691](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L691).

#### Метод `FilesystemAdapter.content_uri`

```python
def content_uri(self, rec: ObjectRecord) -> str | None: ...
```

Persistent ``file://`` URI of a stored object (``ContentRef`` blob, single-node deployments).

Код: [__init__.py:694](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L694).

#### Метод `FilesystemAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:698](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L698).

#### Метод `FilesystemAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:704](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L704).

#### Метод `FilesystemAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Код: [__init__.py:707](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L707).

#### Метод `FilesystemAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:710](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L710).

#### Метод `FilesystemAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Код: [__init__.py:713](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L713).

#### Метод `FilesystemAdapter.object_statistics`

```python
async def object_statistics(self) -> dict[str, int]: ...
```

Код: [__init__.py:716](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L716).

#### Метод `FilesystemAdapter.list_objects`

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

Код: [__init__.py:724](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L724).

#### Метод `FilesystemAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:736](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L736).

#### Метод `FilesystemAdapter.commit_entity`

```python
async def commit_entity(
    self,
    *,
    new: EntitySnapshot,
    expected_version: int | None,
    event: HistoryEvent,
) -> CommitResult: ...
```

Код: [__init__.py:739](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L739).

#### Метод `FilesystemAdapter.list_entities`

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

Код: [__init__.py:744](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L744).

#### Метод `FilesystemAdapter.search_entities`

```python
async def search_entities(
    self,
    entity_type: str,
    *,
    search: str,
    scope: str | None = None,
    updated_since: datetime | None = None,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[EntitySnapshot], str | None]: ...
```

Код: [__init__.py:755](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L755).

#### Метод `FilesystemAdapter.list_entity_types`

```python
async def list_entity_types(
    self,
    *,
    scope: str | None = None,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[Mapping[str, Any]], str | None]: ...
```

Код: [__init__.py:769](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L769).

#### Метод `FilesystemAdapter.entity_statistics`

```python
async def entity_statistics(self) -> dict[str, Any]: ...
```

Код: [__init__.py:774](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L774).

#### Метод `FilesystemAdapter.list_history`

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

Код: [__init__.py:781](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L781).

#### Метод `FilesystemAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:786](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L786).

#### Метод `FilesystemAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Код: [__init__.py:789](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L789).

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-files`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:82](../../../../../services/storage/adapters/files/src/jane_storage_files/__init__.py#L82).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'lock_timeout_ms': 30000, 'lock_stale_ms': 120000, 'lock_poll_ms': 10, 'replace` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). |
