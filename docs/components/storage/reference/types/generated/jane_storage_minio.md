# jane_storage_minio

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage_minio.package_dir](#jane_storage_miniopackage_dir)
- [jane_storage_minio.MinioAdapter](#jane_storage_miniominioadapter)
- [jane_storage_minio.MinioAdapter.kind](#jane_storage_miniominioadapterkind)
- [jane_storage_minio.MinioAdapter.profile](#jane_storage_miniominioadapterprofile)

## jane_storage_minio.package_dir

**Функція.** Код: [services/storage/adapters/minio/src/jane_storage_minio/__init__.py:25](../../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py#L25).

```python
def package_dir() -> Path:
```

Результат: `Path`.

### Опис із вихідного коду

```text
Directory of the ``jane.storage-minio`` storage package (entry point ``jane.storage.packages``).
```

## jane_storage_minio.MinioAdapter

**Клас.** Код: [services/storage/adapters/minio/src/jane_storage_minio/__init__.py:30](../../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py#L30).

```python
class MinioAdapter(S3Adapter):
```

Базові типи / інтерфейси: `S3Adapter`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_storage_minio.md#jane_storage_miniominioadapterkind) | Поле | ні |
| [profile](jane_storage_minio.md#jane_storage_miniominioadapterprofile) | Поле | ні |
| [capabilities](jane_storage_s3.md#jane_storage_s3s3adaptercapabilities) | Поле | так |
| [__init__](jane_storage_s3.md#jane_storage_s3s3adapter__init__) | Конструктор | так |
| [open](jane_storage_s3.md#jane_storage_s3s3adapteropen) | Метод | так |
| [close](jane_storage_s3.md#jane_storage_s3s3adapterclose) | Метод | так |
| [client](jane_storage_s3.md#jane_storage_s3s3adapterclient) | Властивість | так |
| [health](jane_storage_s3.md#jane_storage_s3s3adapterhealth) | Метод | так |
| [ensure_schema](jane_storage_s3.md#jane_storage_s3s3adapterensure_schema) | Метод | так |
| [content_uri](jane_storage_s3.md#jane_storage_s3s3adaptercontent_uri) | Метод | так |
| [put_object](jane_storage_s3.md#jane_storage_s3s3adapterput_object) | Метод | так |
| [get_object](jane_storage_s3.md#jane_storage_s3s3adapterget_object) | Метод | так |
| [read_object_content](jane_storage_s3.md#jane_storage_s3s3adapterread_object_content) | Метод | так |
| [list_objects](jane_storage_s3.md#jane_storage_s3s3adapterlist_objects) | Метод | так |
| [read_entity](jane_storage_s3.md#jane_storage_s3s3adapterread_entity) | Метод | так |
| [commit_entity](jane_storage_s3.md#jane_storage_s3s3adaptercommit_entity) | Метод | так |
| [list_entities](jane_storage_s3.md#jane_storage_s3s3adapterlist_entities) | Метод | так |
| [list_history](jane_storage_s3.md#jane_storage_s3s3adapterlist_history) | Метод | так |
| [get_delivery](jane_storage_s3.md#jane_storage_s3s3adapterget_delivery) | Метод | так |
| [record_delivery](jane_storage_s3.md#jane_storage_s3s3adapterrecord_delivery) | Метод | так |

### Опис із вихідного коду

```text
``StorageAdapter`` over a MinIO bucket (``params.endpoint``, ``params.bucket``; secrets ``access_key``, ``secret_key``).
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/minio/tests/test_minio_profile.py:40](../../../../../../services/storage/adapters/minio/tests/test_minio_profile.py#L40).

```python
adapter = MinioAdapter()
```

## jane_storage_minio.MinioAdapter.kind

**Поле.** Код: [services/storage/adapters/minio/src/jane_storage_minio/__init__.py:33](../../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py#L33).

```python
kind: ClassVar[str] = 'minio'
```

Доступ: читання — так; запис — так.

## jane_storage_minio.MinioAdapter.profile

**Поле.** Код: [services/storage/adapters/minio/src/jane_storage_minio/__init__.py:34](../../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py#L34).

```python
profile: ClassVar[S3Profile] = S3Profile(addressing_style='path', endpoint_required=True, create_bucket=True, server_side_encryption=False)
```

Доступ: читання — так; запис — так.
