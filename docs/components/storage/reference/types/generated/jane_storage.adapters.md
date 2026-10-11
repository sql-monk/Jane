# jane_storage.adapters

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.adapters.ADAPTER_GROUP](#jane_storageadaptersadapter_group)
- [jane_storage.adapters.PACKAGE_GROUP](#jane_storageadapterspackage_group)
- [jane_storage.adapters.REQUIRED_CAPABILITIES](#jane_storageadaptersrequired_capabilities)
- [jane_storage.adapters.UnknownAdapter](#jane_storageadaptersunknownadapter)
- [jane_storage.adapters.available_adapters](#jane_storageadaptersavailable_adapters)
- [jane_storage.adapters.adapter_class](#jane_storageadaptersadapter_class)
- [jane_storage.adapters.create_adapter](#jane_storageadapterscreate_adapter)
- [jane_storage.adapters.package_dirs](#jane_storageadapterspackage_dirs)

## jane_storage.adapters.ADAPTER_GROUP

**Константа.** Код: [services/storage/src/jane_storage/adapters.py:36](../../../../../../services/storage/src/jane_storage/adapters.py#L36).

```python
ADAPTER_GROUP = 'jane.storage.adapters'
```

## jane_storage.adapters.PACKAGE_GROUP

**Константа.** Код: [services/storage/src/jane_storage/adapters.py:37](../../../../../../services/storage/src/jane_storage/adapters.py#L37).

```python
PACKAGE_GROUP = 'jane.storage.packages'
```

## jane_storage.adapters.REQUIRED_CAPABILITIES

**Константа.** Код: [services/storage/src/jane_storage/adapters.py:38](../../../../../../services/storage/src/jane_storage/adapters.py#L38).

```python
REQUIRED_CAPABILITIES = frozenset({'objects', 'entities', 'history'})
```

## jane_storage.adapters.UnknownAdapter

**Клас.** Код: [services/storage/src/jane_storage/adapters.py:41](../../../../../../services/storage/src/jane_storage/adapters.py#L41).

```python
class UnknownAdapter(LookupError):
```

Базові типи / інтерфейси: `LookupError`.

## jane_storage.adapters.available_adapters

**Функція.** Код: [services/storage/src/jane_storage/adapters.py:45](../../../../../../services/storage/src/jane_storage/adapters.py#L45).

```python
def available_adapters() -> dict[str, type[StorageAdapter]]:
```

Результат: `dict[str, type[StorageAdapter]]`.

Явні `raise` у тілі: `TypeError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``kind`` → adapter class for every installed adapter distribution.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_packages.py:24](../../../../../../services/storage/tests/test_packages.py#L24).

```python
adapters = available_adapters()
```

## jane_storage.adapters.adapter_class

**Функція.** Код: [services/storage/src/jane_storage/adapters.py:60](../../../../../../services/storage/src/jane_storage/adapters.py#L60).

```python
def adapter_class(kind: str) -> type[StorageAdapter]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `kind` | `str` | `—` | positional-or-keyword |

Результат: `type[StorageAdapter]`.

Явні `raise` у тілі: `UnknownAdapter`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:17](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L17).

```python
assert adapter_class("minio") is MinioAdapter
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:16](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L16).

```python
assert adapter_class("mongodb") is MongoAdapter
```

## jane_storage.adapters.create_adapter

**Функція.** Код: [services/storage/src/jane_storage/adapters.py:70](../../../../../../services/storage/src/jane_storage/adapters.py#L70).

```python
def create_adapter(kind: str, **kwargs: Any) -> StorageAdapter:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `kind` | `str` | `—` | positional-or-keyword |
| `kwargs` | `Any` | `—` | var-keyword |

Результат: `StorageAdapter`.

### Опис із вихідного коду

```text
New, not yet opened adapter instance of ``kind``.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:26](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L26).

```python
await create_adapter("minio").open(
            ResolvedConnection("m", "minio", {"bucket": "jane-raw"}, SECRETS), {}
        )
```

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:35](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L35).

```python
await create_adapter("minio").open(ResolvedConnection("m", "minio", params, SECRETS), {})
```

## jane_storage.adapters.package_dirs

**Функція.** Код: [services/storage/src/jane_storage/adapters.py:76](../../../../../../services/storage/src/jane_storage/adapters.py#L76).

```python
def package_dirs() -> Mapping[str, Path]:
```

Результат: `Mapping[str, Path]`.

Явні `raise` у тілі: `FileNotFoundError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``package_id`` → directory with ``jane-package.json`` for every installed storage package.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:19](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L19).

```python
pkg = load_package(package_dirs()["jane.storage-minio"])
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_mongo_config.py:17](../../../../../../services/storage/adapters/mongodb/tests/test_mongo_config.py#L17).

```python
pkg = load_package(package_dirs()["jane.storage-mongodb"])
```
