# jane_registry.blobs

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.blobs.BlobIntegrityError](#jane_registryblobsblobintegrityerror)
- [jane_registry.blobs.BlobStore](#jane_registryblobsblobstore)
- [jane_registry.blobs.BlobStore.name](#jane_registryblobsblobstorename)
- [jane_registry.blobs.BlobStore.put](#jane_registryblobsblobstoreput)
- [jane_registry.blobs.BlobStore.get](#jane_registryblobsblobstoreget)
- [jane_registry.blobs.BlobStore.exists](#jane_registryblobsblobstoreexists)
- [jane_registry.blobs.BlobStore.check](#jane_registryblobsblobstorecheck)
- [jane_registry.blobs.BlobStore.location](#jane_registryblobsblobstorelocation)
- [jane_registry.blobs.FileBlobStore](#jane_registryblobsfileblobstore)
- [jane_registry.blobs.FileBlobStore.name](#jane_registryblobsfileblobstorename)
- [jane_registry.blobs.FileBlobStore.__init__](#jane_registryblobsfileblobstore__init__)
- [jane_registry.blobs.FileBlobStore.base](#jane_registryblobsfileblobstorebase)
- [jane_registry.blobs.FileBlobStore.bucket](#jane_registryblobsfileblobstorebucket)
- [jane_registry.blobs.FileBlobStore.prefix](#jane_registryblobsfileblobstoreprefix)
- [jane_registry.blobs.FileBlobStore.location](#jane_registryblobsfileblobstorelocation)
- [jane_registry.blobs.FileBlobStore.put](#jane_registryblobsfileblobstoreput)
- [jane_registry.blobs.FileBlobStore.get](#jane_registryblobsfileblobstoreget)
- [jane_registry.blobs.FileBlobStore.exists](#jane_registryblobsfileblobstoreexists)
- [jane_registry.blobs.FileBlobStore.check](#jane_registryblobsfileblobstorecheck)
- [jane_registry.blobs.S3BlobStore](#jane_registryblobss3blobstore)
- [jane_registry.blobs.S3BlobStore.name](#jane_registryblobss3blobstorename)
- [jane_registry.blobs.S3BlobStore.__init__](#jane_registryblobss3blobstore__init__)
- [jane_registry.blobs.S3BlobStore.bucket](#jane_registryblobss3blobstorebucket)
- [jane_registry.blobs.S3BlobStore.prefix](#jane_registryblobss3blobstoreprefix)
- [jane_registry.blobs.S3BlobStore.client](#jane_registryblobss3blobstoreclient)
- [jane_registry.blobs.S3BlobStore.location](#jane_registryblobss3blobstorelocation)
- [jane_registry.blobs.S3BlobStore.ensure_bucket](#jane_registryblobss3blobstoreensure_bucket)
- [jane_registry.blobs.S3BlobStore.put](#jane_registryblobss3blobstoreput)
- [jane_registry.blobs.S3BlobStore.get](#jane_registryblobss3blobstoreget)
- [jane_registry.blobs.S3BlobStore.exists](#jane_registryblobss3blobstoreexists)
- [jane_registry.blobs.S3BlobStore.check](#jane_registryblobss3blobstorecheck)

## jane_registry.blobs.BlobIntegrityError

**Клас.** Код: [services/registry/src/jane_registry/blobs.py:23](../../../../../../services/registry/src/jane_registry/blobs.py#L23).

```python
class BlobIntegrityError(RuntimeError):
```

Базові типи / інтерфейси: `RuntimeError`.

### Опис із вихідного коду

```text
Stored bytes do not match their digest.
```

## jane_registry.blobs.BlobStore

**Клас.** Код: [services/registry/src/jane_registry/blobs.py:37](../../../../../../services/registry/src/jane_registry/blobs.py#L37).

```python
class BlobStore(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.blobs.md#jane_registryblobsblobstorename) | Поле | ні |
| [put](jane_registry.blobs.md#jane_registryblobsblobstoreput) | Метод | ні |
| [get](jane_registry.blobs.md#jane_registryblobsblobstoreget) | Метод | ні |
| [exists](jane_registry.blobs.md#jane_registryblobsblobstoreexists) | Метод | ні |
| [check](jane_registry.blobs.md#jane_registryblobsblobstorecheck) | Метод | ні |
| [location](jane_registry.blobs.md#jane_registryblobsblobstorelocation) | Метод | ні |

## jane_registry.blobs.BlobStore.name

**Поле.** Код: [services/registry/src/jane_registry/blobs.py:38](../../../../../../services/registry/src/jane_registry/blobs.py#L38).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_registry.blobs.BlobStore.put

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:40](../../../../../../services/registry/src/jane_registry/blobs.py#L40).

```python
async def put(self, digest: str, data: bytes) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.blobs.BlobStore.get

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:41](../../../../../../services/registry/src/jane_registry/blobs.py#L41).

```python
async def get(self, digest: str) -> bytes | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `bytes | None`.

## jane_registry.blobs.BlobStore.exists

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:42](../../../../../../services/registry/src/jane_registry/blobs.py#L42).

```python
async def exists(self, digest: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.blobs.BlobStore.check

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:43](../../../../../../services/registry/src/jane_registry/blobs.py#L43).

```python
async def check(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.blobs.BlobStore.location

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:44](../../../../../../services/registry/src/jane_registry/blobs.py#L44).

```python
def location(self, digest: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_registry.blobs.FileBlobStore

**Клас.** Код: [services/registry/src/jane_registry/blobs.py:47](../../../../../../services/registry/src/jane_registry/blobs.py#L47).

```python
class FileBlobStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.blobs.md#jane_registryblobsfileblobstorename) | Поле | ні |
| [__init__](jane_registry.blobs.md#jane_registryblobsfileblobstore__init__) | Конструктор | ні |
| [base](jane_registry.blobs.md#jane_registryblobsfileblobstorebase) | Поле екземпляра | ні |
| [bucket](jane_registry.blobs.md#jane_registryblobsfileblobstorebucket) | Поле екземпляра | ні |
| [prefix](jane_registry.blobs.md#jane_registryblobsfileblobstoreprefix) | Поле екземпляра | ні |
| [location](jane_registry.blobs.md#jane_registryblobsfileblobstorelocation) | Метод | ні |
| [put](jane_registry.blobs.md#jane_registryblobsfileblobstoreput) | Метод | ні |
| [get](jane_registry.blobs.md#jane_registryblobsfileblobstoreget) | Метод | ні |
| [exists](jane_registry.blobs.md#jane_registryblobsfileblobstoreexists) | Метод | ні |
| [check](jane_registry.blobs.md#jane_registryblobsfileblobstorecheck) | Метод | ні |

## jane_registry.blobs.FileBlobStore.name

**Поле.** Код: [services/registry/src/jane_registry/blobs.py:48](../../../../../../services/registry/src/jane_registry/blobs.py#L48).

```python
name = 'filesystem'
```

Доступ: читання — так; запис — так.

## jane_registry.blobs.FileBlobStore.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/blobs.py:50](../../../../../../services/registry/src/jane_registry/blobs.py#L50).

```python
def __init__(self, root: Path, bucket: str, prefix: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |
| `bucket` | `str` | `—` | positional-or-keyword |
| `prefix` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.blobs.FileBlobStore.base

**Поле екземпляра.** Код: [services/registry/src/jane_registry/blobs.py:51](../../../../../../services/registry/src/jane_registry/blobs.py#L51).

```python
self.base = root / bucket
```

## jane_registry.blobs.FileBlobStore.bucket

**Поле екземпляра.** Код: [services/registry/src/jane_registry/blobs.py:52](../../../../../../services/registry/src/jane_registry/blobs.py#L52).

```python
self.bucket = bucket
```

## jane_registry.blobs.FileBlobStore.prefix

**Поле екземпляра.** Код: [services/registry/src/jane_registry/blobs.py:53](../../../../../../services/registry/src/jane_registry/blobs.py#L53).

```python
self.prefix = prefix
```

## jane_registry.blobs.FileBlobStore.location

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:58](../../../../../../services/registry/src/jane_registry/blobs.py#L58).

```python
def location(self, digest: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_registry.blobs.FileBlobStore.put

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:77](../../../../../../services/registry/src/jane_registry/blobs.py#L77).

```python
async def put(self, digest: str, data: bytes) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.blobs.FileBlobStore.get

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:81](../../../../../../services/registry/src/jane_registry/blobs.py#L81).

```python
async def get(self, digest: str) -> bytes | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `bytes | None`.

## jane_registry.blobs.FileBlobStore.exists

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:89](../../../../../../services/registry/src/jane_registry/blobs.py#L89).

```python
async def exists(self, digest: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.blobs.FileBlobStore.check

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:92](../../../../../../services/registry/src/jane_registry/blobs.py#L92).

```python
async def check(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.blobs.S3BlobStore

**Клас.** Код: [services/registry/src/jane_registry/blobs.py:97](../../../../../../services/registry/src/jane_registry/blobs.py#L97).

```python
class S3BlobStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.blobs.md#jane_registryblobss3blobstorename) | Поле | ні |
| [__init__](jane_registry.blobs.md#jane_registryblobss3blobstore__init__) | Конструктор | ні |
| [bucket](jane_registry.blobs.md#jane_registryblobss3blobstorebucket) | Поле екземпляра | ні |
| [prefix](jane_registry.blobs.md#jane_registryblobss3blobstoreprefix) | Поле екземпляра | ні |
| [client](jane_registry.blobs.md#jane_registryblobss3blobstoreclient) | Поле екземпляра | ні |
| [location](jane_registry.blobs.md#jane_registryblobss3blobstorelocation) | Метод | ні |
| [ensure_bucket](jane_registry.blobs.md#jane_registryblobss3blobstoreensure_bucket) | Метод | ні |
| [put](jane_registry.blobs.md#jane_registryblobss3blobstoreput) | Метод | ні |
| [get](jane_registry.blobs.md#jane_registryblobss3blobstoreget) | Метод | ні |
| [exists](jane_registry.blobs.md#jane_registryblobss3blobstoreexists) | Метод | ні |
| [check](jane_registry.blobs.md#jane_registryblobss3blobstorecheck) | Метод | ні |

## jane_registry.blobs.S3BlobStore.name

**Поле.** Код: [services/registry/src/jane_registry/blobs.py:98](../../../../../../services/registry/src/jane_registry/blobs.py#L98).

```python
name = 's3'
```

Доступ: читання — так; запис — так.

## jane_registry.blobs.S3BlobStore.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/blobs.py:100](../../../../../../services/registry/src/jane_registry/blobs.py#L100).

```python
def __init__(self, *, bucket: str, prefix: str, endpoint_url: str | None, region: str, access_key: str | None, secret_key: str | None, connect_timeout_s: float, read_timeout_s: float, max_attempts: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `bucket` | `str` | `—` | keyword-only |
| `prefix` | `str` | `—` | keyword-only |
| `endpoint_url` | `str \| None` | `—` | keyword-only |
| `region` | `str` | `—` | keyword-only |
| `access_key` | `str \| None` | `—` | keyword-only |
| `secret_key` | `str \| None` | `—` | keyword-only |
| `connect_timeout_s` | `float` | `—` | keyword-only |
| `read_timeout_s` | `float` | `—` | keyword-only |
| `max_attempts` | `int` | `—` | keyword-only |

Результат: `None`.

## jane_registry.blobs.S3BlobStore.bucket

**Поле екземпляра.** Код: [services/registry/src/jane_registry/blobs.py:116](../../../../../../services/registry/src/jane_registry/blobs.py#L116).

```python
self.bucket = bucket
```

## jane_registry.blobs.S3BlobStore.prefix

**Поле екземпляра.** Код: [services/registry/src/jane_registry/blobs.py:117](../../../../../../services/registry/src/jane_registry/blobs.py#L117).

```python
self.prefix = prefix
```

## jane_registry.blobs.S3BlobStore.client

**Поле екземпляра.** Код: [services/registry/src/jane_registry/blobs.py:118](../../../../../../services/registry/src/jane_registry/blobs.py#L118).

```python
self.client: Any = boto3.client('s3', endpoint_url=endpoint_url, region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, config=Config(connect_timeout=connect_timeout_s, read_timeout=read_timeout_s, retries={'max_attempts': max_attempts, 'mode': 'standard'}, s3={'addressing_style': 'path'}))
```

## jane_registry.blobs.S3BlobStore.location

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:135](../../../../../../services/registry/src/jane_registry/blobs.py#L135).

```python
def location(self, digest: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_registry.blobs.S3BlobStore.ensure_bucket

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:138](../../../../../../services/registry/src/jane_registry/blobs.py#L138).

```python
def ensure_bucket(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.blobs.S3BlobStore.put

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:179](../../../../../../services/registry/src/jane_registry/blobs.py#L179).

```python
async def put(self, digest: str, data: bytes) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.blobs.S3BlobStore.get

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:183](../../../../../../services/registry/src/jane_registry/blobs.py#L183).

```python
async def get(self, digest: str) -> bytes | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `bytes | None`.

## jane_registry.blobs.S3BlobStore.exists

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:187](../../../../../../services/registry/src/jane_registry/blobs.py#L187).

```python
async def exists(self, digest: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.blobs.S3BlobStore.check

**Метод.** Код: [services/registry/src/jane_registry/blobs.py:190](../../../../../../services/registry/src/jane_registry/blobs.py#L190).

```python
async def check(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.
