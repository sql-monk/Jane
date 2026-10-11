# jane_storage_s3

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage_s3.DEFAULT_OPTIONS](#jane_storage_s3default_options)
- [jane_storage_s3.package_dir](#jane_storage_s3package_dir)
- [jane_storage_s3.S3Profile](#jane_storage_s3s3profile)
- [jane_storage_s3.S3Profile.__init__](#jane_storage_s3s3profile__init__)
- [jane_storage_s3.S3Profile.addressing_style](#jane_storage_s3s3profileaddressing_style)
- [jane_storage_s3.S3Profile.endpoint_required](#jane_storage_s3s3profileendpoint_required)
- [jane_storage_s3.S3Profile.create_bucket](#jane_storage_s3s3profilecreate_bucket)
- [jane_storage_s3.S3Profile.server_side_encryption](#jane_storage_s3s3profileserver_side_encryption)
- [jane_storage_s3.S3Adapter](#jane_storage_s3s3adapter)
- [jane_storage_s3.S3Adapter.kind](#jane_storage_s3s3adapterkind)
- [jane_storage_s3.S3Adapter.capabilities](#jane_storage_s3s3adaptercapabilities)
- [jane_storage_s3.S3Adapter.profile](#jane_storage_s3s3adapterprofile)
- [jane_storage_s3.S3Adapter.__init__](#jane_storage_s3s3adapter__init__)
- [jane_storage_s3.S3Adapter.open](#jane_storage_s3s3adapteropen)
- [jane_storage_s3.S3Adapter.close](#jane_storage_s3s3adapterclose)
- [jane_storage_s3.S3Adapter.client](#jane_storage_s3s3adapterclient)
- [jane_storage_s3.S3Adapter.health](#jane_storage_s3s3adapterhealth)
- [jane_storage_s3.S3Adapter.ensure_schema](#jane_storage_s3s3adapterensure_schema)
- [jane_storage_s3.S3Adapter.content_uri](#jane_storage_s3s3adaptercontent_uri)
- [jane_storage_s3.S3Adapter.put_object](#jane_storage_s3s3adapterput_object)
- [jane_storage_s3.S3Adapter.get_object](#jane_storage_s3s3adapterget_object)
- [jane_storage_s3.S3Adapter.read_object_content](#jane_storage_s3s3adapterread_object_content)
- [jane_storage_s3.S3Adapter.list_objects](#jane_storage_s3s3adapterlist_objects)
- [jane_storage_s3.S3Adapter.read_entity](#jane_storage_s3s3adapterread_entity)
- [jane_storage_s3.S3Adapter.commit_entity](#jane_storage_s3s3adaptercommit_entity)
- [jane_storage_s3.S3Adapter.list_entities](#jane_storage_s3s3adapterlist_entities)
- [jane_storage_s3.S3Adapter.list_history](#jane_storage_s3s3adapterlist_history)
- [jane_storage_s3.S3Adapter.get_delivery](#jane_storage_s3s3adapterget_delivery)
- [jane_storage_s3.S3Adapter.record_delivery](#jane_storage_s3s3adapterrecord_delivery)

## jane_storage_s3.DEFAULT_OPTIONS

**Константа.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:88](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L88).

```python
DEFAULT_OPTIONS: dict[str, int] = {'connect_timeout_ms': 10000, 'command_timeout_ms': 30000, 'pool_max_size': 10, 'lock_stale_ms': 120000, 'retry_max_attempts': 3, 'claim_attempts': 3}
```

### Опис із вихідного коду

```text
Safe defaults; overridden by connection params or adapter options (service config ``adapters.*``).
``lock_stale_ms`` — age after which a delivery claim without its snapshot is a leftover of a crash;
``claim_attempts`` — how many times a dead claim is removed and the delivery key claimed again.
```

## jane_storage_s3.package_dir

**Функція.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:118](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L118).

```python
def package_dir() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
Directory of the ``jane.storage-s3`` storage package (entry point ``jane.storage.packages``).
```

## jane_storage_s3.S3Profile

**Клас.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:141](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L141).

```python
class S3Profile:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [addressing_style](jane_storage_s3.md#jane_storage_s3s3profileaddressing_style) | Поле | ні |
| [endpoint_required](jane_storage_s3.md#jane_storage_s3s3profileendpoint_required) | Поле | ні |
| [create_bucket](jane_storage_s3.md#jane_storage_s3s3profilecreate_bucket) | Поле | ні |
| [server_side_encryption](jane_storage_s3.md#jane_storage_s3s3profileserver_side_encryption) | Поле | ні |
| [__init__](jane_storage_s3.md#jane_storage_s3s3profile__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
What differs between S3-compatible services; the protocol (and the code) is the same.
```

## jane_storage_s3.S3Profile.__init__

**Конструктор dataclass.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:141](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L141).

```python
def __init__(self, addressing_style: str, endpoint_required: bool, create_bucket: bool, server_side_encryption: bool) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `addressing_style` | `str` | `—` | positional-or-keyword |
| `endpoint_required` | `bool` | `—` | positional-or-keyword |
| `create_bucket` | `bool` | `—` | positional-or-keyword |
| `server_side_encryption` | `bool` | `—` | positional-or-keyword |

Результат: `None`.

## jane_storage_s3.S3Profile.addressing_style

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:144](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L144).

```python
addressing_style: str
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Default ``addressing_style``: ``auto`` (AWS: virtual-hosted), ``path`` (MinIO, most self-hosted).
```

## jane_storage_s3.S3Profile.endpoint_required

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:146](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L146).

```python
endpoint_required: bool
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
AWS S3 derives the endpoint from ``region``; a self-hosted service needs ``params.endpoint``.
```

## jane_storage_s3.S3Profile.create_bucket

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:148](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L148).

```python
create_bucket: bool
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Default of ``params.create_bucket`` (``ensure_schema`` creates a missing bucket).
```

## jane_storage_s3.S3Profile.server_side_encryption

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:150](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L150).

```python
server_side_encryption: bool
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``params.sse`` (``AES256`` | ``aws:kms``) and ``params.sse_kms_key_id`` are accepted.
```

## jane_storage_s3.S3Adapter

**Клас.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:154](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L154).

```python
class S3Adapter:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage_s3.md#jane_storage_s3s3adapterkind) | Поле | ні |
| [capabilities](jane_storage_s3.md#jane_storage_s3s3adaptercapabilities) | Поле | ні |
| [profile](jane_storage_s3.md#jane_storage_s3s3adapterprofile) | Поле | ні |
| [__init__](jane_storage_s3.md#jane_storage_s3s3adapter__init__) | Конструктор | ні |
| [open](jane_storage_s3.md#jane_storage_s3s3adapteropen) | Метод | ні |
| [close](jane_storage_s3.md#jane_storage_s3s3adapterclose) | Метод | ні |
| [client](jane_storage_s3.md#jane_storage_s3s3adapterclient) | Властивість | ні |
| [health](jane_storage_s3.md#jane_storage_s3s3adapterhealth) | Метод | ні |
| [ensure_schema](jane_storage_s3.md#jane_storage_s3s3adapterensure_schema) | Метод | ні |
| [content_uri](jane_storage_s3.md#jane_storage_s3s3adaptercontent_uri) | Метод | ні |
| [put_object](jane_storage_s3.md#jane_storage_s3s3adapterput_object) | Метод | ні |
| [get_object](jane_storage_s3.md#jane_storage_s3s3adapterget_object) | Метод | ні |
| [read_object_content](jane_storage_s3.md#jane_storage_s3s3adapterread_object_content) | Метод | ні |
| [list_objects](jane_storage_s3.md#jane_storage_s3s3adapterlist_objects) | Метод | ні |
| [read_entity](jane_storage_s3.md#jane_storage_s3s3adapterread_entity) | Метод | ні |
| [commit_entity](jane_storage_s3.md#jane_storage_s3s3adaptercommit_entity) | Метод | ні |
| [list_entities](jane_storage_s3.md#jane_storage_s3s3adapterlist_entities) | Метод | ні |
| [list_history](jane_storage_s3.md#jane_storage_s3s3adapterlist_history) | Метод | ні |
| [get_delivery](jane_storage_s3.md#jane_storage_s3s3adapterget_delivery) | Метод | ні |
| [record_delivery](jane_storage_s3.md#jane_storage_s3s3adapterrecord_delivery) | Метод | ні |

### Опис із вихідного коду

```text
``StorageAdapter`` over an S3 bucket (connection ``params.bucket``; secrets ``access_key``, ``secret_key``).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/s3/tests/test_s3_config.py:49](../../../../../../services/storage/adapters/s3/tests/test_s3_config.py#L49).

```python
adapter = S3Adapter()
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_s3_config.py:68](../../../../../../services/storage/adapters/s3/tests/test_s3_config.py#L68).

```python
await S3Adapter().read_entity("product", "k")
```

## jane_storage_s3.S3Adapter.kind

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:157](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L157).

```python
kind: ClassVar[str] = 's3'
```

Доступ: читання — так; запис — так.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:55](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L55).

```python
self.kind = kind
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:88](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L88).

```python
return StorageEngine(adapter, connection_id=f"recovery-{self.kind}", retries=COMPAT_RETRIES)
```

## jane_storage_s3.S3Adapter.capabilities

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:158](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L158).

```python
capabilities: ClassVar[frozenset[str]] = frozenset({'objects', 'entities', 'history'})
```

Доступ: читання — так; запис — так.

## jane_storage_s3.S3Adapter.profile

**Поле.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:159](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L159).

```python
profile: ClassVar[S3Profile] = S3Profile(addressing_style='auto', endpoint_required=False, create_bucket=False, server_side_encryption=True)
```

Доступ: читання — так; запис — так.

## jane_storage_s3.S3Adapter.__init__

**Конструктор.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:163](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L163).

```python
def __init__(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/s3/tests/test_s3_config.py:49](../../../../../../services/storage/adapters/s3/tests/test_s3_config.py#L49).

```python
adapter = S3Adapter()
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_s3_config.py:68](../../../../../../services/storage/adapters/s3/tests/test_s3_config.py#L68).

```python
await S3Adapter().read_entity("product", "k")
```

## jane_storage_s3.S3Adapter.open

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:173](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L173).

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

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:41](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L41).

```python
await adapter.open(
        ResolvedConnection("m", "minio", {"bucket": "jane-raw", "endpoint": "http://minio:9000"}, SECRETS), {}
    )
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:79](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L79).

```python
await adapter.open(
            ResolvedConnection(f"recovery-{self.kind}", self.kind, params, secrets),
            {"prefix": PREFIX, **options},
        )
```

## jane_storage_s3.S3Adapter.close

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:237](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L237).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:48](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L48).

```python
await adapter.close()
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:109](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L109).

```python
await adapter.close()
```

## jane_storage_s3.S3Adapter.client

**Властивість.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:243](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L243).

```python
def client(self) -> Any:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Any`.

Доступ: читання — так; запис — ні.

Явні `raise` у тілі: `AdapterError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:45](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L45).

```python
assert adapter.client.meta.config.s3["addressing_style"] == "path"
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:58](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L58).

```python
self.client = boto3.client(
            "s3",
            endpoint_url=info["endpoint"],
            region_name=info.get("region", "us-east-1"),
            aws_access_key_id=info["access_key"],
            aws_secret_access_key=info["secret_key"],
            config=Config(s3={"addressing_style": "path"}),
        )
```

## jane_storage_s3.S3Adapter.health

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:391](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L391).

```python
async def health(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_storage_s3.S3Adapter.ensure_schema

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:398](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L398).

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

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:83](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L83).

```python
await adapter.ensure_schema(["product"])
```

## jane_storage_s3.S3Adapter.content_uri

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:403](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L403).

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
Persistent ``s3://`` URI of a stored object (``ContentRef`` blob).
```

## jane_storage_s3.S3Adapter.put_object

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:463](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L463).

```python
async def put_object(self, obj: RawObject) -> ObjectRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `obj` | `RawObject` | `—` | positional-or-keyword |

Результат: `ObjectRecord`.

## jane_storage_s3.S3Adapter.get_object

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:472](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L472).

```python
async def get_object(self, object_id: str) -> ObjectRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `ObjectRecord | None`.

## jane_storage_s3.S3Adapter.read_object_content

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:482](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L482).

```python
async def read_object_content(self, object_id: str) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `object_id` | `str` | `—` | positional-or-keyword |

Результат: `bytes`.

## jane_storage_s3.S3Adapter.list_objects

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:517](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L517).

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

## jane_storage_s3.S3Adapter.read_entity

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:558](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L558).

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

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:176](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L176).

```python
assert await adapter.read_entity("product", KEY) is None
```

## jane_storage_s3.S3Adapter.commit_entity

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:681](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L681).

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

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:170](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L170).

```python
result = await adapter.commit_entity(
        new=merged.snapshot, expected_version=None, event=event_for(rec, "crash-dk#0", merged.applied)
    )
```

## jane_storage_s3.S3Adapter.list_entities

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:714](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L714).

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

## jane_storage_s3.S3Adapter.list_history

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:749](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L749).

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

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:104](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L104).

```python
events, _ = await adapter.list_history("product", KEY, limit=100)
```

## jane_storage_s3.S3Adapter.get_delivery

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:761](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L761).

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

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:175](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L175).

```python
assert await adapter.get_delivery("crash-dk#0") is None
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:181](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L181).

```python
assert (await adapter.get_delivery("crash-dk#0")) is not None
```

## jane_storage_s3.S3Adapter.record_delivery

**Метод.** Код: [services/storage/adapters/s3/src/jane_storage_s3/__init__.py:781](../../../../../../services/storage/adapters/s3/src/jane_storage_s3/__init__.py#L781).

```python
async def record_delivery(self, record: DeliveryRecord) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `record` | `DeliveryRecord` | `—` | positional-or-keyword |

Результат: `bool`.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:312](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L312).

```python
assert await adapter.record_delivery(rec) is True
```

Контекст і передумови: [services/storage/adapters/s3/tests/test_recovery.py:313](../../../../../../services/storage/adapters/s3/tests/test_recovery.py#L313).

```python
assert await adapter.record_delivery(rec) is False
```
