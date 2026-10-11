# Модуль `jane_storage_postgres`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py). Не редагуйте вручну.

PostgreSQL adapter of the Jane storage handler (``kind: postgresql``, asyncpg).

Tables in ``<schema>`` with ``<table_prefix>`` (default ``jane_``):

| Table | Content | |---|---| | ``<p>entities`` | current state: ``(entity_type, canonical_key)`` PK, ``fields``/``field_orders``/``cleared_fields`` jsonb, ``version`` | | ``<p>entity_history`` | one row per accepted update (also stale): PK ``(entity_type, canonical_key, version)`` | | ``<p>deliveries`` | ``delivery_key`` PK + acknowledged writes (jsonb) — kept forever (ADR-0008) | | ``<p>objects`` | RAW / result documents: bytes in ``content`` (bytea), media type, sha256, Material metadata |

``commit_entity`` is one transaction: ``INSERT … ON CONFLICT DO NOTHING`` into deliveries (nothing inserted → ``DUPLICATE``), compare-and-swap of the snapshot (``UPDATE … WHERE version = $expected`` or ``INSERT … ON CONFLICT DO NOTHING`` for a new entity; nothing changed → ``CONFLICT``) and the history insert — all or nothing. Connection parameters: ``host``, ``port``, ``database``, ``schema``, ``sslmode``; secrets ``username``, ``password`` (resolved by the core).

## Класи

### Клас `PostgresAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_postgres` |
| Код | [__init__.py:111](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L111) |

```python
class PostgresAdapter: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'postgresql'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання |  |
| `pool` | `asyncpg.Pool` | — | читання (властивість) |  |

#### Конструктор `PostgresAdapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:115](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L115).

#### Метод `PostgresAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:139](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L139).

#### Метод `PostgresAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:170](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L170).

#### Метод `PostgresAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:175](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L175).

#### Метод `PostgresAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:182](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L182).

#### Метод `PostgresAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:252](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L252).

#### Метод `PostgresAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:294](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L294).

#### Метод `PostgresAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:301](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L301).

#### Метод `PostgresAdapter.list_objects`

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

Код: [__init__.py:310](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L310).

#### Метод `PostgresAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:365](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L365).

#### Метод `PostgresAdapter.commit_entity`

```python
async def commit_entity(
    self,
    *,
    new: EntitySnapshot,
    expected_version: int | None,
    event: HistoryEvent,
) -> CommitResult: ...
```

Код: [__init__.py:375](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L375).

#### Метод `PostgresAdapter.list_entities`

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

Код: [__init__.py:445](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L445).

#### Метод `PostgresAdapter.search_entities`

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

Код: [__init__.py:458](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L458).

#### Метод `PostgresAdapter.list_entity_types`

```python
async def list_entity_types(
    self,
    *,
    scope: str | None = None,
    cursor: str | None = None,
    limit: int,
) -> tuple[Sequence[Mapping[str, Any]], str | None]: ...
```

Код: [__init__.py:472](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L472).

#### Метод `PostgresAdapter.object_statistics`

```python
async def object_statistics(self) -> dict[str, int]: ...
```

Код: [__init__.py:491](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L491).

#### Метод `PostgresAdapter.entity_statistics`

```python
async def entity_statistics(self) -> dict[str, Any]: ...
```

Код: [__init__.py:498](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L498).

#### Метод `PostgresAdapter.list_history`

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

Код: [__init__.py:548](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L548).

#### Метод `PostgresAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:579](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L579).

#### Метод `PostgresAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Код: [__init__.py:591](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L591).

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-postgresql`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:76](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L76).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'pool_min_size': 1, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). |
