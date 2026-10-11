# Залежності Registry

Registry автономний від Orchestrator. Мінімум визначають backend і залежності пакета.

| Залежність | Коли потрібна | Недоступність |
|---|---|---|
| Python ≥3.12, Jane Kit та [pyproject](../../../services/registry/pyproject.toml) | Завжди | Старт/імпорт не працює |
| contracts зі схемами | Валідація API і пакетів | Неправильний шлях зупиняє побудову app |
| Власна PostgreSQL | db=postgres, типовий режим | Старт/health/операція помилкова |
| S3/MinIO bucket | blob=s3, типовий режим | Створення bucket або archive operation не працює |
| Файлова система | blob=filesystem | Потрібні права читання/запису blob_root |
| Runtime-профіль | Python/runtime залежності пакета | Невідомий профіль/бібліотека відхиляється |
| Handler Runtime HTTP | Лише джерело профілю або зовнішній запуск тестів | Локальний JSON-профіль усуває HTTP-залежність |

Точні Python-залежності фіксує [uv.lock](../../../uv.lock). Версії тестової інфраструктури задає [infra/compose.yaml](../../../infra/compose.yaml); довільні версії PostgreSQL/S3 не оголошені перевіреними.

## Заміна backend

MetadataStore і BlobStore — Python-протоколи. Adapter передають через Components у build_app; він зберігає унікальність package_id/version, optimistic concurrency, порядок пагінації та async lifecycle. Для кількох екземплярів потрібні також спільні JobStore і IdempotencyStore.

S3-сумісний endpoint задає s3_endpoint_url. Заміна endpoint сама не переносить blobs: перенесіть ті самі байти за digest. Memory усуває PostgreSQL лише для одиночного недовговічного експерименту.

## Власність

Registry не читає чужих таблиць. Профіль надходить із файла або GET /v1/info, пакетні залежності перевіряються у власному каталозі. Матеріали й бізнес-сутності належать [Storage](../storage/README.md).
