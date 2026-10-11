# Модуль `jane_storage_sqlserver`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py). Не редагуйте вручну.

SQL Server adapter of the Jane storage handler (``kind: sqlserver``, pymssql / FreeTDS).

Tables in ``<schema>`` (default ``dbo``) with ``<table_prefix>`` (default ``jane_``):

| Table | Content | |---|---| | ``<p>entities`` | current state: PK ``(entity_type, key_hash)``, ``doc`` = ``EntitySnapshot`` JSON (nvarchar(max)), ``version`` | | ``<p>entity_history`` | one row per accepted update (also stale): PK ``(entity_type, key_hash, version)`` | | ``<p>deliveries`` | PK ``delivery_hash`` + ``delivery_key`` + acknowledged writes (JSON) — kept forever (ADR-0008) | | ``<p>objects`` | RAW / result documents: ``content`` varbinary(max), ``meta`` = ``ObjectRecord`` JSON |

Keys (canonical key, delivery key, object key) have no length limit, so indexes use their sha256 (``key_hash``, ``delivery_hash``) — SQL Server index keys are limited to 900/1700 bytes. Timestamps are stored as fixed-width RFC 3339 UTC strings (``jane_storage.codec.format_ts``): they sort chronologically and keep microseconds on any TDS version.

``commit_entity`` is one T-SQL batch in one transaction (``XACT_ABORT ON``): insert the delivery row (a duplicate key → ``DUPLICATE``), compare-and-swap of the snapshot (``UPDATE … WHERE version = @expected`` or ``INSERT`` for a new entity; nothing changed or a duplicate key → ``CONFLICT``) and the history insert — all or nothing. A deadlock victim (1205) is reported as ``CONFLICT``: nothing was written and the core retries. ``ensure_schema`` is idempotent and serialised with ``sp_getapplock``.

Connection parameters: ``host``, ``port``, ``database``, ``schema``, ``encryption`` (FreeTDS: ``off`` | ``request`` | ``require``), ``tds_version``; secrets ``username``, ``password``.

## Класи

### Клас `SqlServerAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_sqlserver` |
| Код | [__init__.py:173](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L173) |

```python
class SqlServerAdapter: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'sqlserver'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання |  |

#### Конструктор `SqlServerAdapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:177](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L177).

#### Метод `SqlServerAdapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:204](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L204).

#### Метод `SqlServerAdapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:248](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L248).

#### Метод `SqlServerAdapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:253](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L253).

#### Метод `SqlServerAdapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:260](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L260).

#### Метод `SqlServerAdapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:314](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L314).

#### Метод `SqlServerAdapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:374](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L374).

#### Метод `SqlServerAdapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:379](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L379).

#### Метод `SqlServerAdapter.list_objects`

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

Код: [__init__.py:386](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L386).

#### Метод `SqlServerAdapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:429](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L429).

#### Метод `SqlServerAdapter.commit_entity`

```python
async def commit_entity(
    self,
    *,
    new: EntitySnapshot,
    expected_version: int | None,
    event: HistoryEvent,
) -> CommitResult: ...
```

Код: [__init__.py:435](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L435).

#### Метод `SqlServerAdapter.list_entities`

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

Код: [__init__.py:495](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L495).

#### Метод `SqlServerAdapter.list_history`

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

Код: [__init__.py:526](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L526).

#### Метод `SqlServerAdapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:541](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L541).

#### Метод `SqlServerAdapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Код: [__init__.py:548](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L548).

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-sqlserver`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:98](../../../../../services/storage/adapters/sqlserver/src/jane_storage_sqlserver/__init__.py#L98).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'pool_min_size': 1, 'pool_max_size': 10, 'connect_timeout_ms': 10000, 'command_` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). ``lock_timeout_ms`` bounds the wait for the ``ensure_schema`` application lock. |
