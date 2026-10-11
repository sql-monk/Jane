# Модуль `jane_storage_s3`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/s3/src/jane_storage_s3/__init__.py](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py). Не редагуйте вручну.

S3 adapter of the Jane storage handler (``kind: s3``); also the base of the MinIO adapter.

Layout in the connection bucket under ``<prefix>/`` (contracts/docs/storage-adapter.md, "Object stores"):

| Key | Content | |---|---| | ``entities/<entity_type>/<sha256(canonical_key)>.json`` | ``EntitySnapshot`` (+ ``pending``: the history event of its version until it is rolled forward) | | ``history/<entity_type>/<sha256(canonical_key)>/<version:012d>.json`` | ``HistoryEvent`` | | ``deliveries/<sha256(delivery_key)>.json`` | ``DeliveryRecord`` (+ ``claimed_at``) | | ``objects/<object_key>`` + ``objects/<object_key>.meta.json`` | bytes (``x-amz-meta-sha256``) + ``ObjectRecord`` | | ``index/objects/<object_id>.json`` | ``ObjectRecord`` (lookup by ``object_id``, listing) |

Atomicity uses only conditional ``PutObject`` (``If-None-Match: *`` to create, ``If-Match: <ETag>`` to replace), which AWS S3, MinIO and SeaweedFS implement. ``commit_entity``:

1. claim the delivery key: ``PUT deliveries/<h>.json`` with ``If-None-Match: *``. A 412 means the key exists: a complete delivery → ``DUPLICATE``; a claim of a commit still in flight → ``CONFLICT`` (the core retries); a dead claim (its commit lost the race or crashed more than ``lock_stale_ms`` ago) is removed and the claim repeated;
2. compare-and-swap the snapshot: ``PUT entities/…json`` with ``If-Match`` of the snapshot read at ``expected_version`` (``If-None-Match: *`` for a new entity). The new snapshot carries its history event in ``pending``, so the snapshot write is the single commit point: the version, the state and the event become visible together. A 412 → the claim is deleted (compensation) → ``CONFLICT``;
3. roll forward: ``PUT history/…/<version>.json`` and drop ``pending`` (``If-Match``). A crash here loses nothing: readers and the next commit roll a pending event forward first.

History versions are contiguous (``1..snapshot.version``), so history pages are read by key without listing. ETags are content hashes; a snapshot document always contains its ``version``, so a replaced document never gets the ETag of an older one.

## Класи

### Клас `S3Adapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_s3` |
| Код | [__init__.py:154](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L154) |

```python
class S3Adapter: ...
```

``StorageAdapter`` over an S3 bucket (connection ``params.bucket``; secrets ``access_key``, ``secret_key``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'s3'` | читання |  |
| `capabilities` | `ClassVar[frozenset[str]]` | `frozenset({'objects', 'entities', 'history'})` | читання |  |
| `profile` | `ClassVar[S3Profile]` | `S3Profile(addressing_style='auto', endpoint_required=False, create_bucket=False,` | читання |  |
| `client` | `Any` | — | читання (властивість) |  |

#### Конструктор `S3Adapter.__init__`

```python
def __init__(self) -> None: ...
```

Код: [__init__.py:163](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L163).

#### Метод `S3Adapter.open`

```python
async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `AdapterError`.

Код: [__init__.py:173](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L173).

#### Метод `S3Adapter.close`

```python
async def close(self) -> None: ...
```

Код: [__init__.py:237](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L237).

#### Метод `S3Adapter.health`

```python
async def health(self) -> bool: ...
```

Код: [__init__.py:391](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L391).

#### Метод `S3Adapter.ensure_schema`

```python
async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
```

Код: [__init__.py:398](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L398).

#### Метод `S3Adapter.content_uri`

```python
def content_uri(self, rec: ObjectRecord) -> str | None: ...
```

Persistent ``s3://`` URI of a stored object (``ContentRef`` blob).

Код: [__init__.py:403](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L403).

#### Метод `S3Adapter.put_object`

```python
async def put_object(self, obj: RawObject) -> ObjectRecord: ...
```

Код: [__init__.py:463](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L463).

#### Метод `S3Adapter.get_object`

```python
async def get_object(self, object_id: str) -> ObjectRecord | None: ...
```

Код: [__init__.py:472](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L472).

#### Метод `S3Adapter.read_object_content`

```python
async def read_object_content(self, object_id: str) -> bytes: ...
```

Код: [__init__.py:482](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L482).

#### Метод `S3Adapter.list_objects`

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

Код: [__init__.py:517](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L517).

#### Метод `S3Adapter.read_entity`

```python
async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
```

Код: [__init__.py:558](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L558).

#### Метод `S3Adapter.commit_entity`

```python
async def commit_entity(
    self,
    *,
    new: EntitySnapshot,
    expected_version: int | None,
    event: HistoryEvent,
) -> CommitResult: ...
```

Код: [__init__.py:681](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L681).

#### Метод `S3Adapter.list_entities`

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

Код: [__init__.py:714](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L714).

#### Метод `S3Adapter.list_history`

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

Код: [__init__.py:749](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L749).

#### Метод `S3Adapter.get_delivery`

```python
async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
```

Код: [__init__.py:761](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L761).

#### Метод `S3Adapter.record_delivery`

```python
async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Код: [__init__.py:781](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L781).

### Клас `S3Profile`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage_s3` |
| Код | [__init__.py:141](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L141) |

```python
@dataclass(frozen=True, slots=True)
class S3Profile: ...
```

What differs between S3-compatible services; the protocol (and the code) is the same.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `addressing_style` | `str` | — | читання | Default ``addressing_style``: ``auto`` (AWS: virtual-hosted), ``path`` (MinIO, most self-hosted). |
| `endpoint_required` | `bool` | — | читання | AWS S3 derives the endpoint from ``region``; a self-hosted service needs ``params.endpoint``. |
| `create_bucket` | `bool` | — | читання | Default of ``params.create_bucket`` (``ensure_schema`` creates a missing bucket). |
| `server_side_encryption` | `bool` | — | читання | ``params.sse`` (``AES256`` \| ``aws:kms``) and ``params.sse_kms_key_id`` are accepted. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-s3`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:118](../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L118).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_OPTIONS` | `dict[str, int]` | `{'connect_timeout_ms': 10000, 'command_timeout_ms': 30000, 'pool_max_size': 10,` | Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``). ``lock_stale_ms`` — age after which a delivery claim without its snapshot is a leftover of a crash; ``claim_attempts`` — how many times a dead claim is removed and the delivery key claimed again. |
