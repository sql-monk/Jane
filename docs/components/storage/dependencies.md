# Storage: залежності

Обирайте адаптер за потрібним постійним сховищем. Orchestrator не потрібний для прямого `POST /v1/invocations`.

## Обов’язкові залежності

| Залежність | Умова | Сумісність і відмова |
|---|---|---|
| Jane Kit та Jane Contracts | Усі запуски | Workspace-версії з uv.lock; спільні jobs, auth і StorageAdapter |
| Пакет адаптера | Принаймні один цільовий запис | Python entry point `jane.storage_adapters`; адаптер має реалізувати [StorageAdapter](../../../contracts/python/src/jane_contracts/storage_adapter.py) |
| Цільове сховище | Кожна connection | Недоступність дає `HandlerResult.status=failed`, `failure.kind=connection_error`, `retryable=true` |
| Локальний каталог | filesystem | Право читання/запису; блокування й атомарна заміна файлів |

Версії Python-пакетів зафіксовано в [uv.lock](../../../uv.lock), точні runtime-залежності — у [pyproject.toml](../../../services/storage/pyproject.toml). Не припускайте підтримку довільної версії зовнішнього сховища: compatibility suite і тестовий стек є доказом лише своїх протестованих версій.

## Адаптери

| kind | Пакет | Постійна залежність |
|---|---|---|
| `filesystem` | `jane.storage-files@1.0.0` | Каталог диска |
| `postgresql` | `jane.storage-postgresql@1.0.0` | PostgreSQL та власна схема |
| `minio` | `jane.storage-minio@1.0.0` | S3-сумісний endpoint MinIO |
| `s3` | `jane.storage-s3@1.0.0` | S3 endpoint та bucket |
| `mongodb` | `jane.storage-mongodb@1.0.0` | MongoDB та власна база/колекції |
| `sqlserver` | `jane.storage-sqlserver@1.0.0` | SQL Server та доступний ODBC-драйвер |

Дивіться [дистрибутиви адаптерів](../../../services/storage/adapters/) та їхні `package/schemas/params.schema.json`. Пакет визначає формат, параметри й потрібні connection bindings; kind підключення має збігатися з адаптером пакета.

## Опційні залежності

| Залежність | Для чого | Якщо відсутня |
|---|---|---|
| Registry `registry.v1` | Завантажити не встановлений пакет | Локальні пакети доступні; невідомий пакет дає `not_found` |
| Transit S3/MinIO connection | Прочитати матеріал `s3://` | Потрібний відповідний transport; inline працює без нього |
| Дозволений каталог blobs | Прочитати `file://` | Читання заборонене без `content_files_dir` або власного transit |
| Дозволений download host | Прочитати `download_url` | Порожній allowlist відхиляє завантаження |
| Orchestrator | Ланцюжок етапів і повтори доставки | Прямий HTTP-клієнт продовжує працювати |

## Заміна сумісного сховища

[Приклад заміни](integration.md#заміна-адаптера) змінює connection і пакет, зберігаючи HandlerInvocation та семантику ключів/спостережень. Compatibility suite перевіряє контракт адаптера; міграція вже записаних даних між різними сховищами не виконується зміною connection.
