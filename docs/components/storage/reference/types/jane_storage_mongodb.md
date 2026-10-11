# Модуль `jane_storage_mongodb`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py). Не редагуйте вручну.

MongoDB adapter of the Jane storage handler (``kind: mongodb``, PyMongo ``AsyncMongoClient``).

Collections in ``params.database`` with ``<prefix>`` (default ``jane_``):

| Collection | Content | |---|---| | ``<p>entities`` | ``_id = <entity_type>|<sha256(canonical_key)>``, the ``EntitySnapshot`` document (+ ``pending``) | | ``<p>entity_history`` | one ``HistoryEvent`` document per version (``_id = <entity_type>|<hash>|<version:012d>``) | | ``<p>deliveries`` | ``_id = sha256(delivery_key)``, the ``DeliveryRecord`` document — kept forever | | ``<p>objects`` | ``_id = object_id``, the ``ObjectRecord`` document (commit marker of an object) | | ``<p>object_chunks`` | RAW bytes in chunks of ``chunk_bytes`` (``_id = <object_id>:<sha256>:<n>``) |

Multi-document transactions need a replica set; the adapter does not, so a standalone ``mongod`` works. Atomicity of ``commit_entity`` comes from single-document operations:

1. the stored snapshot has the key in ``pending``, or ``deliveries`` has it → ``DUPLICATE`` (read in this order: the roll-forward inserts the delivery record before it drops ``pending``);
2. compare-and-swap of the snapshot document — ``replace_one({_id, version: expected})`` or ``insert_one`` for a new entity (duplicate ``_id`` → ``CONFLICT``). The replacement carries the history event and the delivery acknowledgement in ``pending``, so the snapshot write is the single commit point: state, version, history event and delivery key become visible together;
3. roll forward: insert the history event and the delivery record, then ``$unset`` ``pending``. A crash here loses nothing — ``get_delivery`` finds keys in ``pending`` (indexed), readers and the next commit roll a pending event forward first (all steps are idempotent).

Connection parameters: ``host``, ``port``, ``database``, ``auth_source`` (``admin``), ``tls``, ``replica_set``, ``direct_connection``, ``chunk_bytes``; secrets ``username``, ``password``.

## Класи

### Клас `MongoAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_mongodb` |
| Код | [__init__.py:141](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L141) |

```python
class MongoAdapter: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'mongodb'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання |  |

#### Конструктор `MongoAdapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:145](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L145).

#### Метод `MongoAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:166](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L166).

#### Метод `MongoAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:203](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L203).

#### Метод `MongoAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:208](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L208).

#### Метод `MongoAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:218](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L218).

#### Метод `MongoAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:239](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L239).

#### Метод `MongoAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:292](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L292).

#### Метод `MongoAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:297](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L297).

#### Метод `MongoAdapter.list_objects`

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

Код: [__init__.py:314](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L314).

#### Метод `MongoAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:356](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L356).

#### Метод `MongoAdapter.commit_entity`

```python
async def commit_entity(
    self,
    *,
    new: EntitySnapshot,
    expected_version: int | None,
    event: HistoryEvent,
) -> CommitResult: ...
```

Код: [__init__.py:391](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L391).

#### Метод `MongoAdapter.list_entities`

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

Код: [__init__.py:443](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L443).

#### Метод `MongoAdapter.list_history`

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

Код: [__init__.py:471](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L471).

#### Метод `MongoAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:496](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L496).

#### Метод `MongoAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Код: [__init__.py:514](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L514).

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-mongodb`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:107](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L107).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'pool_min_size': 0, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). ``chunk_bytes`` — size of one RAW chunk document (BSON documents are limited to 16 MiB). |
