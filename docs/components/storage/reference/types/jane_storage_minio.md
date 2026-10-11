# Модуль `jane_storage_minio`

> Згенеровано `scripts/docs_reference.py` з [services/storage/adapters/minio/src/jane_storage_minio/__init__.py](../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py). Не редагуйте вручну.

MinIO adapter of the Jane storage handler (``kind: minio``).

MinIO speaks the S3 API, so the storage protocol — key layout, conditional writes, the commit algorithm and crash recovery — is the one of :mod:`jane_storage_s3` (tested against both MinIO and SeaweedFS). Only the profile differs:

| | ``s3`` | ``minio`` | |---|---|---| | ``params.endpoint`` | optional (AWS derives it from ``region``) | required | | ``addressing_style`` | ``auto`` (virtual-hosted on AWS) | ``path`` | | ``create_bucket`` default | ``false`` (buckets are provisioned in AWS) | ``true`` | | ``sse`` / ``sse_kms_key_id`` | accepted (SSE-S3 / SSE-KMS) | rejected (MinIO KMS is server configuration) |

## Класи

### Клас `MinioAdapter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage_minio` |
| Успадкування | `S3Adapter` |
| Код | [__init__.py:30](../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py#L30) |

```python
class MinioAdapter(S3Adapter): ...
```

``StorageAdapter`` over a MinIO bucket (``params.endpoint``, ``params.bucket``; secrets ``access_key``, ``secret_key``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `ClassVar[str]` | `'minio'` | читання |  |
| `profile` | `ClassVar[S3Profile]` | `S3Profile(addressing_style='path', endpoint_required=True, create_bucket=True, s` | читання |  |

## Функції

### Функція `package_dir`

```python
def package_dir() -> Path: ...
```

Directory of the ``jane.storage-minio`` storage package (entry point ``jane.storage.packages``).

Код: [__init__.py:25](../../../../../services/storage/adapters/minio/src/jane_storage_minio/__init__.py#L25).
