# Модуль `jane_registry.blobs`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/blobs.py](../../../../../services/registry/src/jane_registry/blobs.py). Не редагуйте вручну.

Content-addressed archive storage (ADR-0002 §2): object ``<bucket>/<prefix><sha256 hex>``.

* :class:`S3BlobStore` - MinIO / S3 (``boto3``), the default;
* :class:`FileBlobStore` - a directory standing in for the bucket (single host, tests, air-gapped use).

Objects are immutable: ``put`` of an existing digest is a no-op (identical content deduplicates).

## Зміст

- [Клас `BlobIntegrityError`](#клас-blobintegrityerror)
- [Клас `BlobStore`](#клас-blobstore)
- [Клас `FileBlobStore`](#клас-fileblobstore)
- [Клас `S3BlobStore`](#клас-s3blobstore)

## Класи

### Клас `BlobIntegrityError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.blobs` |
| Успадкування | `RuntimeError` |
| Код | [blobs.py:23](../../../../../services/registry/src/jane_registry/blobs.py#L23) |

```python
class BlobIntegrityError(RuntimeError): ...
```

Stored bytes do not match their digest.

### Клас `BlobStore`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_registry.blobs` |
| Успадкування | `Protocol` |
| Код | [blobs.py:37](../../../../../services/registry/src/jane_registry/blobs.py#L37) |

```python
class BlobStore(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |

#### Метод `BlobStore.put`

```python
async def put(self, digest: str, data: bytes) -> None: ...
```

Код: [blobs.py:40](../../../../../services/registry/src/jane_registry/blobs.py#L40).

#### Метод `BlobStore.get`

```python
async def get(self, digest: str) -> bytes | None: ...
```

Код: [blobs.py:41](../../../../../services/registry/src/jane_registry/blobs.py#L41).

#### Метод `BlobStore.exists`

```python
async def exists(self, digest: str) -> bool: ...
```

Код: [blobs.py:42](../../../../../services/registry/src/jane_registry/blobs.py#L42).

#### Метод `BlobStore.check`

```python
async def check(self) -> bool: ...
```

Код: [blobs.py:43](../../../../../services/registry/src/jane_registry/blobs.py#L43).

#### Метод `BlobStore.location`

```python
def location(self, digest: str) -> str: ...
```

Код: [blobs.py:44](../../../../../services/registry/src/jane_registry/blobs.py#L44).

### Клас `FileBlobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.blobs` |
| Код | [blobs.py:47](../../../../../services/registry/src/jane_registry/blobs.py#L47) |

```python
class FileBlobStore: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'filesystem'` |  |

#### Конструктор `FileBlobStore.__init__`

```python
def __init__(self, root: Path, bucket: str, prefix: str) -> None: ...
```

Код: [blobs.py:50](../../../../../services/registry/src/jane_registry/blobs.py#L50).

#### Метод `FileBlobStore.location`

```python
def location(self, digest: str) -> str: ...
```

Код: [blobs.py:58](../../../../../services/registry/src/jane_registry/blobs.py#L58).

#### Метод `FileBlobStore.put`

```python
async def put(self, digest: str, data: bytes) -> None: ...
```

Код: [blobs.py:77](../../../../../services/registry/src/jane_registry/blobs.py#L77).

#### Метод `FileBlobStore.get`

```python
async def get(self, digest: str) -> bytes | None: ...
```

Код: [blobs.py:81](../../../../../services/registry/src/jane_registry/blobs.py#L81).

#### Метод `FileBlobStore.exists`

```python
async def exists(self, digest: str) -> bool: ...
```

Код: [blobs.py:89](../../../../../services/registry/src/jane_registry/blobs.py#L89).

#### Метод `FileBlobStore.check`

```python
async def check(self) -> bool: ...
```

Код: [blobs.py:92](../../../../../services/registry/src/jane_registry/blobs.py#L92).

### Клас `S3BlobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.blobs` |
| Код | [blobs.py:97](../../../../../services/registry/src/jane_registry/blobs.py#L97) |

```python
class S3BlobStore: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'s3'` |  |

#### Конструктор `S3BlobStore.__init__`

```python
def __init__(
    self,
    *,
    bucket: str,
    prefix: str,
    endpoint_url: str | None,
    region: str,
    access_key: str | None,
    secret_key: str | None,
    connect_timeout_s: float,
    read_timeout_s: float,
    max_attempts: int,
) -> None: ...
```

Код: [blobs.py:100](../../../../../services/registry/src/jane_registry/blobs.py#L100).

#### Метод `S3BlobStore.location`

```python
def location(self, digest: str) -> str: ...
```

Код: [blobs.py:135](../../../../../services/registry/src/jane_registry/blobs.py#L135).

#### Метод `S3BlobStore.ensure_bucket`

```python
def ensure_bucket(self) -> None: ...
```

Код: [blobs.py:138](../../../../../services/registry/src/jane_registry/blobs.py#L138).

#### Метод `S3BlobStore.put`

```python
async def put(self, digest: str, data: bytes) -> None: ...
```

Код: [blobs.py:179](../../../../../services/registry/src/jane_registry/blobs.py#L179).

#### Метод `S3BlobStore.get`

```python
async def get(self, digest: str) -> bytes | None: ...
```

Код: [blobs.py:183](../../../../../services/registry/src/jane_registry/blobs.py#L183).

#### Метод `S3BlobStore.exists`

```python
async def exists(self, digest: str) -> bool: ...
```

Код: [blobs.py:187](../../../../../services/registry/src/jane_registry/blobs.py#L187).

#### Метод `S3BlobStore.check`

```python
async def check(self) -> bool: ...
```

Код: [blobs.py:190](../../../../../services/registry/src/jane_registry/blobs.py#L190).
