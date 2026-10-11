# Модуль `jane_storage_mongodb`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py). Не редагуйте вручну.

MongoDB adapter of the Jane storage handler (``kind: mongodb``, PyMongo ``AsyncMongoClient``).

Layout in ``params.database`` with ``<prefix>`` (``params.prefix``, empty by default): one collection per entity type, its history next to it, service collections apart.

* ``<prefix><entity_type>`` — current state: ``_id = sha256(canonical_key)``, the ``EntitySnapshot`` document, ``search_text`` (see search below) and ``pending`` while a commit is being rolled forward;
* ``<prefix><entity_type>.history`` — one ``HistoryEvent`` document per version (``_id = <sha256(canonical_key)>|<version:012d>``, ``key_hash``);
* ``<prefix>_deliveries`` — ``_id = sha256(delivery_key)``: the ``DeliveryRecord`` (kept forever, ADR-0008) or the intent of an entity commit (``intent = {entity_type, entity_id}``) until that commit is rolled forward;
* ``<prefix>_objects`` — ``_id = object_id``, the ``ObjectRecord`` document (commit marker of an object);
* ``<prefix>_object_chunks`` — RAW bytes in chunks of ``chunk_bytes`` (``_id = <object_id>:<sha256>:<n>``).

``entity_type`` matches ``^[a-z][a-z0-9_]{0,63}$``: it never starts with ``_`` and never contains ``.``, so with any prefix a type collection collides neither with a service collection (``<prefix>_…``) nor with a history collection (``<prefix>….history``). The namespace ``<prefix>*`` belongs to one connection: every collection ``<prefix><entity_type>`` is an entity type of the catalog. With the empty prefix that is the whole database; connections may share a database only with prefixes none of which is the start of another one. The type ``system`` needs a non-empty prefix (MongoDB reserves ``system.*``, so ``system.history`` cannot exist).

Multi-document transactions need a replica set; the adapter does not, so a standalone ``mongod`` works. Atomicity of ``commit_entity`` comes from single-document operations:

1. read the snapshot, then the delivery document of the key: the key in the snapshot's ``pending`` or a delivery record → ``DUPLICATE`` (in this order: the roll-forward writes the delivery record before it drops ``pending``, so a key committed by another instance is seen in one of the two reads);
2. roll forward a ``pending`` left by an earlier commit of the entity; ``version`` differs → ``CONFLICT``;
3. write the intent ``{_id: sha256(delivery_key), delivery_key, intent: {entity_type, entity_id}}`` to ``_deliveries``: inserted, or replacing another intent of the key (a crashed or concurrent attempt points to the same snapshot); a delivery record already there → ``DUPLICATE``. The intent commits nothing: it only names the one snapshot document that can hold the key in ``pending``;
4. compare-and-swap of the snapshot — ``replace_one({_id, version: expected})`` or ``insert_one`` for a new entity (duplicate ``_id`` → ``CONFLICT``). The document carries the history event and the delivery acknowledgement in ``pending``, so this write is the single commit point: state, version, history event and delivery key become visible together;
5. roll forward: insert the history event, replace the intent with the delivery record, ``$unset`` ``pending``. A crash here loses nothing: ``get_delivery``, readers of the history and the next commit of the entity finish the roll-forward first (every step is idempotent).

``get_delivery`` never scans the type collections: it reads ``_deliveries`` by ``_id``. A delivery record is the answer. An intent leads to one snapshot: the key in its ``pending`` means committed (rolled forward on the spot); otherwise the delivery document is read once more — a roll-forward may have replaced the intent between the two reads — and an intent that is still there means "not committed": a commit in progress or one that crashed before its compare-and-swap; the next attempt with the key replaces it.

Indexes of a type collection are created by its first write in the process (cached per adapter instance) and by ``ensure_schema`` for the types it is given: ``canonical_key`` (order and cursor of lists and search), ``key.scope`` + ``canonical_key``, ``updated_at``, ``pending.delivery_key`` (partial: commits not yet rolled forward); history: unique ``key_hash`` + ``version``.

Catalog and search (``EntityDiscoveryAdapter``): types come from the collection names of the namespace, with exact counts (``key.scope`` filter optional), types without entities are left out. Search is a literal, case-insensitive substring match on the server, before pagination: ``search_text`` holds ``casefold()`` of the JSON of ``canonical_key``, ``key`` and ``fields`` (the same text the core matches for an exact key) and the filter is ``$indexOfBytes`` of the casefolded term as a ``$literal`` — there is no pattern language, so regex metacharacters, ``%`` and ``_`` match only themselves.

Statistics (``StorageStatisticsAdapter``): objects — count and the sum of ``size_bytes`` of ``_objects``; entities — exact counts per type and ``storageSize + totalIndexSize`` of the type collections (``$collStats``; history, deliveries and objects excluded); each collection is counted at its own moment, without a common snapshot.

Connection parameters: ``host``, ``port``, ``database``, ``prefix``, ``auth_source`` (``admin``), ``tls``, ``replica_set``, ``direct_connection``, ``chunk_bytes``; secrets ``username``, ``password``.

## Класи

### Клас `MongoAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_mongodb` |
| Код | [__init__.py:194](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L194) |

```python
class MongoAdapter: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'mongodb'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання | Fixed by the contract; catalog, search and statistics are the optional protocols ``EntityDiscoveryAdapter`` and ``StorageStatisticsAdapter`` (detected by their methods). |

#### Конструктор `MongoAdapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:200](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L200).

#### Метод `MongoAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:276](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L276).

#### Метод `MongoAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:314](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L314).

#### Метод `MongoAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:319](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L319).

#### Метод `MongoAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:329](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L329).

#### Метод `MongoAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:344](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L344).

#### Метод `MongoAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:397](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L397).

#### Метод `MongoAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:402](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L402).

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

Код: [__init__.py:419](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L419).

#### Метод `MongoAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:461](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L461).

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

Код: [__init__.py:517](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L517).

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

Код: [__init__.py:577](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L577).

#### Метод `MongoAdapter.search_entities`

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

Код: [__init__.py:590](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L590).

#### Метод `MongoAdapter.list_entity_types`

```python
async def list_entity_types(
    self,
    *,
    scope: str | None = None,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[Mapping[str, Any]], str | None]: ...
```

Код: [__init__.py:640](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L640).

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

Код: [__init__.py:658](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L658).

#### Метод `MongoAdapter.object_statistics`

```python
async def object_statistics(self) -> dict[str, int]: ...
```

Код: [__init__.py:684](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L684).

#### Метод `MongoAdapter.entity_statistics`

```python
async def entity_statistics(self) -> dict[str, Any]: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:701](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L701).

#### Метод `MongoAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:735](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L735).

#### Метод `MongoAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Insert-if-absent (object writes; their keys never equal entity keys ``<key>#<n>``, which alone get intents).

Код: [__init__.py:763](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L763).

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-mongodb`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:150](../../../../../services/storage/adapters/mongodb/src/jane_storage_mongodb/__init__.py#L150).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'pool_min_size': 0, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). ``chunk_bytes`` — size of one RAW chunk document (BSON documents are limited to 16 MiB). |
| `SIZE_BASIS` | — | `'mongodb_collections_with_indexes'` | ``entity_statistics().size_basis``: ``storageSize + totalIndexSize`` of the type collections (current states). |
