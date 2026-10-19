# Модуль `jane_storage_postgres`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py). Не редагуйте вручну.

PostgreSQL adapter of the Jane storage handler (``kind: postgresql``, asyncpg).

Tables in ``<schema>`` with ``<table_prefix>`` (default ``jane_``):

| Table | Content | |---|---| | ``<p>entities`` | current state: ``(entity_type, canonical_key)`` PK, ``fields``/``field_orders``/``cleared_fields`` jsonb, ``version`` | | ``<p>entity_history`` | one row per accepted update (also stale): PK ``(entity_type, canonical_key, version)`` | | ``<p>deliveries`` | ``delivery_key`` PK + acknowledged writes (jsonb) — kept forever (ADR-0008) | | ``<p>objects`` | RAW / result documents: bytes in ``content`` (bytea), media type, sha256, Material metadata |

``commit_entity`` is one transaction: ``INSERT … ON CONFLICT DO NOTHING`` into deliveries (nothing inserted → ``DUPLICATE``), compare-and-swap of the snapshot (``UPDATE … WHERE version = $expected`` or ``INSERT … ON CONFLICT DO NOTHING`` for a new entity; nothing changed → ``CONFLICT``) and the history insert — all or nothing. Connection parameters: ``host``, ``port``, ``database``, ``schema``, ``table_prefix``, ``sslmode``, ``layout``; secrets ``username``, ``password`` (resolved by the core).

Relational layout (``params.layout``, absent by default): with ``"news"`` the adapter also keeps the normalized tables of :mod:`jane_storage_postgres.news_layout` in the same schema. ``ensure_schema`` applies the layout's numbered migrations under the same advisory lock, and ``commit_entity`` lays the snapshot of an ``article``, ``post``, ``news_article`` or ``news_event`` out in the same transaction, only after a successful compare-and-swap (``DUPLICATE`` and ``CONFLICT`` leave the projection untouched). A projection error rolls the whole commit back, so the projection always matches the state; other types use the engine tables only. The layout comes from the connection only. An unknown layout, or a stage that overrides ``schema`` / ``table_prefix`` of a connection with a layout (it would share one projection per schema), is a non-retryable ``AdapterError`` in ``open``.

## Класи

### Клас `PostgresAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_postgres` |
| Код | [__init__.py:126](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L126) |

```python
class PostgresAdapter: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'postgresql'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання |  |
| `layout` | `str \| None` | — | читання (властивість) | Relational layout of the opened connection (``params.layout``); ``None`` — engine tables only. |
| `pool` | `asyncpg.Pool` | — | читання (властивість) |  |

#### Конструктор `PostgresAdapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:130](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L130).

#### Метод `PostgresAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:160](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L160).

#### Метод `PostgresAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:209](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L209).

#### Метод `PostgresAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:214](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L214).

#### Метод `PostgresAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:221](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L221).

#### Метод `PostgresAdapter.rebuild_layout`

```python
async def rebuild_layout(
    self,
    *,
    batch_size: int = news_layout.DEFAULT_REBUILD_BATCH_SIZE,
) -> dict[str, int]: ...
```

Clear the relational projection and lay every stored snapshot out again (:func:`news_layout.rebuild`).

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:278](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L278).

#### Метод `PostgresAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:306](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L306).

#### Метод `PostgresAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:348](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L348).

#### Метод `PostgresAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:355](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L355).

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

Код: [__init__.py:364](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L364).

#### Метод `PostgresAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:419](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L419).

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

Код: [__init__.py:429](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L429).

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

Код: [__init__.py:514](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L514).

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

Код: [__init__.py:527](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L527).

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

Код: [__init__.py:541](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L541).

#### Метод `PostgresAdapter.object_statistics`

```python
async def object_statistics(self) -> dict[str, int]: ...
```

Код: [__init__.py:560](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L560).

#### Метод `PostgresAdapter.entity_statistics`

```python
async def entity_statistics(self) -> dict[str, Any]: ...
```

Код: [__init__.py:567](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L567).

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

Код: [__init__.py:617](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L617).

#### Метод `PostgresAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:648](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L648).

#### Метод `PostgresAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Код: [__init__.py:660](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L660).

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-postgresql`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:91](../../../../../services/storage/adapters/postgres/src/jane_storage_postgres/__init__.py#L91).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'pool_min_size': 1, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). |
| `LAYOUTS` | `frozenset[str]` | `frozenset({news_layout.LAYOUT})` | Supported values of the connection parameter ``layout``. |
