# Storage: залежності

Що потрібно Storage для роботи, які версії перевірені та як сервіс поводиться, коли залежність недоступна.

## Зміст

- [Обов'язкові](#обовязкові)
- [Цільові сховища](#цільові-сховища)
- [Опційні](#опційні)
- [Бібліотеки Python](#бібліотеки-python)
- [Поведінка за недоступності](#поведінка-за-недоступності)

## Обов'язкові

| Залежність | Версія | Для чого |
|---|---|---|
| Python | 3.12+ (`requires-python = ">=3.12"`; образ — `python:3.12-slim`) | Виконання сервісу |
| `jane-kit` | workspace | HTTP-застосунок, ліміти, автентифікація, job, ідемпотентність — [jane-kit](../jane-kit/README.md) |
| `jane-contracts` | workspace | Протокол `StorageAdapter`, типи адаптера |
| Хоча б один пакет адаптера | `jane-storage-<назва>` 0.1.0 | Без адаптера немає куди писати; `uv sync --all-packages` і образ установлюють усі шість |
| Цільове сховище | див. нижче | Місце, куди адаптер записує дані |
| Каталог `contracts/` | ревізія репозиторію | Перевірка `HandlerInvocation` і `Connection` за схемами; без нього лишаються лише перевірки ядра (попередження в журналі) |

Каталог `contracts/` сервіс шукає за `JANE_CONTRACTS_DIR`, інакше вгору від коду до кореня checkout; образ копіює його в `/app/contracts`.

## Цільові сховища

Версії сервісів — образи dev-стеку з [infra/compose.yaml](../../../infra/compose.yaml); на них проходить набір сумісності C-01…C-16.

| Адаптер | Сховище | Образ у dev-стеку | Драйвер |
|---|---|---|---|
| `filesystem` | Локальний або змонтований каталог | — | стандартна бібліотека |
| `postgresql` | PostgreSQL | `postgres:18` | `asyncpg>=0.30` |
| `sqlserver` | SQL Server | `mcr.microsoft.com/mssql/server:2022-latest` | `pymssql>=2.3` (FreeTDS у wheel, ODBC не потрібен) |
| `mongodb` | MongoDB (standalone, реплікасет не потрібен) | `mongo:8.0` | `pymongo>=4.13` (`AsyncMongoClient`) |
| `minio` | MinIO | `pgsty/minio:RELEASE.2026-08-04T00-00-00Z` (закріплений digest) | `boto3>=1.35.66` через пакет `jane-storage-s3` |
| `s3` | AWS S3 або S3-сумісне сховище з умовними записами | `chrislusf/seaweedfs:4.47` (замінник S3 у тестах) | `boto3>=1.35.66` |

Вимоги до сховищ:

- **S3 і MinIO** мають підтримувати умовний `PutObject` (`If-None-Match: *`, `If-Match`). Без них атомарність коміту сутності неможлива — це дефект середовища, а не привід пропустити сценарії сумісності.
- **AWS S3** у цій документації не перевірявся: S3-адаптер тестується на SeaweedFS.

Параметри підключення кожного сховища — [адаптери](adapters.md).

## Опційні

| Залежність | Коли потрібна | Налаштування |
|---|---|---|
| Registry (`registry.v1`) | Пакет збереження, якого немає серед вбудованих `jane.storage-*` і не передано в `package_archive` | `JANE_STORAGE_REGISTRY_URL`, `JANE_STORAGE_REGISTRY_TOKEN` |
| Транзитне сховище S3/MinIO | Вхідний `ContentRef` із `s3://` URI | `JANE_STORAGE_TRANSIT_CONNECTION_ID` — підключення типу `s3` або `minio` |
| Каталог локальних blob | Вхідний `ContentRef` із `file:///` (повторна обробка RAW файлового адаптера) | `JANE_STORAGE_CONTENT_FILES_DIR` |
| Власний транзитний каталог | Видача великого RAW без постійного URI через `GET /v1/objects/{id}` | `JANE_STORAGE_TRANSIT_DIR` |
| Хости `download_url` | Вхідний `ContentRef` за попередньо підписаним HTTP(S)-посиланням | `JANE_STORAGE_DOWNLOAD_HOST_ALLOWLIST` |
| Постачальник ідентичності (JWKS) | Режим `auth_mode=jwt` | Спільні параметри [jane-kit](../jane-kit/configuration.md) |

Orchestrator для Storage не є залежністю: він лише один із клієнтів.

## Бібліотеки Python

З [services/storage/pyproject.toml](../../../services/storage/pyproject.toml):

| Пакет | Обмеження | Призначення |
|---|---|---|
| `jane-kit`, `jane-contracts` | workspace | Спільний каркас і протокол |
| `boto3` | `>=1.35` | Читання `s3://` blob транзитного підключення |
| `pytest`, `pytest-asyncio` | `>=8.3`, `>=0.24` | Лише extra `compat`: набір сумісності для пакетів адаптерів |

Кожен адаптер оголошує свій драйвер у власному `pyproject.toml` (таблиця вище).

## Поведінка за недоступності

| Що недоступне | Запис (`POST /v1/invocations`) | Читання (`storage.v1`) |
|---|---|---|
| Цільове сховище | `200`, `HandlerResult.status = failed`, `failure.kind = connection_error`, `retryable: true`; записи до збою лишаються, повтор тим самим ключем їх пропускає | `502 upstream_unavailable`, `retryable: true` |
| Секрет підключення не розв'язується | `502 upstream_unavailable`, нічого не записано | `502 upstream_unavailable` |
| Підключення порушує політику секретів | `422` з кодами `secret_ref_not_allowed` або `host_not_allowed` | `422` |
| Registry (пакет не вбудований) | `502 upstream_unavailable`, `retryable: true` | не використовується |
| Транзитне сховище або `download_url` | `HandlerResult.failed`: мережева помилка — `connection_error`, `retryable: true`; відсутній blob — `retryable: false` | не використовується |
| Каталог `contracts/` | Сервіс стартує; перевірка лише ядром | без змін |

`GET /v1/health` не перевіряє цільові сховища й лишається `ok`, коли сховище недоступне; стан конкретного підключення показує `POST /v1/connections/{id}/test`. Перевірено на PostgreSQL: після зупинки контейнера запис повернув `connection_error`, `retryable: true`, читання — `502`, health — `ok`; після старту бази повтор того самого виклику пройшов.
