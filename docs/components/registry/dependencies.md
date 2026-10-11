# Registry: залежності

Registry не залежить від інших сервісів Jane. У робочому режимі йому потрібні власна база PostgreSQL і S3-сумісне blob-сховище; для дослідів і тестів обидва замінюються режимами без зовнішніх сервісів. Профілі runtime — опційна залежність, потрібна для публікації пакетів із `dependencies.runtime_profile`.

## Зміст

- [Огляд](#огляд)
- [PostgreSQL](#postgresql)
- [Blob-сховище](#blob-сховище)
- [Контрактні схеми](#контрактні-схеми)
- [Профілі runtime](#профілі-runtime)
- [Середовище виконання й бібліотеки](#середовище-виконання-й-бібліотеки)

## Огляд

| Залежність | Обов'язковість | Замінник без зовнішніх сервісів | Перевірені версії |
|---|---|---|---|
| PostgreSQL, власна БД `jane_registry` | обов'язкова для `JANE_REGISTRY_DB=postgres` (типово) | `JANE_REGISTRY_DB=memory` | образ `postgres:18` dev-стеку |
| S3-сумісне сховище, бакет `jane-registry` | обов'язкова для `JANE_REGISTRY_BLOB=s3` (типово) | `JANE_REGISTRY_BLOB=filesystem` | образ MinIO `pgsty/minio:RELEASE.2026-08-04T00-00-00Z` dev-стеку |
| Каталог контрактних схем `contracts/schemas` | обов'язкова | — | схеми тієї самої ревізії репозиторію |
| Джерела профілів runtime | опційна | файл профілю з репозиторію | профіль `python-extractor@1` Handler Runtime |

Версії PostgreSQL і MinIO — ті, з якими 2026-10-11 пройшли інтеграційні тести Registry (`just integration`, 30 тестів) і перевірки з [operations.md](operations.md); інші версії не перевірялися. AWS S3 і інші S3-сумісні сховища не перевірялися.

## PostgreSQL

Registry зберігає в PostgreSQL метадані пакетів і версій, історію статусів, звіти тестів, ключі ідемпотентності та job перенесення змін. Схему таблиць він створює й оновлює сам під час старту ([internals.md](internals.md#власні-дані)). Базу й роль створює оператор; у dev-стеку це робить [provision.sql](../../../infra/postgres/provision.sql) (база й роль `jane_registry`).

| Ситуація | Поведінка |
|---|---|
| `JANE_REGISTRY_DB_URL` не задано | Процес не стартує: `ValueError: JANE_REGISTRY_DB_URL is required for db=postgres (or set JANE_REGISTRY_DB=memory)` |
| База недоступна під час старту | Пул чекає `db.connect_timeout_ms` (типово 5 с), потім `Application startup failed. Exiting.` |
| База стала недоступна під час роботи | `GET /v1/health` — `503`, `metadata_store: down`; запити, що читають або пишуть метадані, — `500 internal_error` (`retryable: true`) |
| База повернулася | Пул відновлює з'єднання; після перезапуску контейнера PostgreSQL health знову `200` за кілька секунд (перевірено) |

Розбіжність із контрактом: за недоступності сховищ запити повертають `500 internal_error`, хоча [errors.md](../../../contracts/docs/errors.md) передбачає для недоступного сховища `502 upstream_unavailable`. Обидва коди мають `retryable: true`, тож клієнти з повторами за `retryable` поводяться однаково.

У режимі `memory` усе зберігається в пам'яті одного процесу й зникає після зупинки; кілька екземплярів у цьому режимі стан не поділяють.

## Blob-сховище

Архіви версій зберігаються як незмінні об'єкти з ключем `<prefix><sha256>` (типово `jane-registry/sha256/<hex>`). Об'єкт із тим самим дайджестом записується лише один раз.

| Режим | Налаштування | Призначення |
|---|---|---|
| `s3` (типово) | `JANE_REGISTRY_S3_*`, бакет `JANE_REGISTRY_BLOB_BUCKET` | MinIO або інше S3-сумісне сховище; бакет створюється під час старту, якщо його немає і `JANE_REGISTRY_S3_CREATE_BUCKET=true` |
| `filesystem` | `JANE_REGISTRY_BLOB_ROOT` | Каталог замість бакета: один хост, тести, ізольоване середовище |

| Ситуація | Поведінка |
|---|---|
| `blob=filesystem` без `JANE_REGISTRY_BLOB_ROOT` | Процес не стартує: `ValueError: JANE_REGISTRY_BLOB_ROOT is required for blob=filesystem` |
| Сховище недоступне під час роботи | Health — `503`, `blob_store: down`; публікація й завантаження архіву — `500 internal_error`; архіви, які вже є в кеші процесу (`packages.archive_cache_bytes`), віддаються з кешу |
| Сховище повернулося | Запити знову успішні без перезапуску Registry (перевірено з MinIO) |
| Байти об'єкта не збігаються з дайджестом | Помилка цілісності; пошкоджений архів не віддається |

Запити до S3 мають тайм-аути й повтори з `JANE_REGISTRY_LIMITS__BLOB__*` ([configuration.md](configuration.md#ліміти)).

## Контрактні схеми

Registry перевіряє маніфести, правила колекторів і звіти тестів за схемами з `contracts/schemas` і власних копій не має. Каталог шукається в такому порядку: `JANE_REGISTRY_CONTRACTS_DIR`, `JANE_CONTRACTS_DIR` або `contracts/` поточного checkout, `/app/contracts` в образі. Якщо схеми не знайдено, процес не стартує з `FileNotFoundError` і порадою задати `JANE_REGISTRY_CONTRACTS_DIR`. Образ [Dockerfile](../../../services/registry/Dockerfile) копіює `contracts/schemas` у `/app/contracts/schemas`.

## Профілі runtime

Профіль runtime (`python-extractor@1`) визначає версію Python і бібліотеки пісочниці Handler Runtime. Registry читає профілі з джерел `JANE_REGISTRY_RUNTIME_PROFILES` — файлів або URL `GET <handler-runtime>/v1/info` — і кешує їх на `profiles.refresh_seconds` (типово 300 с). Для URL Registry надсилає власний токен із `JANE_REGISTRY_RUNTIME_PROFILES_TOKEN_REF`.

| Ситуація | Поведінка |
|---|---|
| Джерел не задано | Пакети без `runtime_profile` публікуються; пакет із `runtime_profile` — `422 dependency_not_allowed` («known: none configured») |
| Профіль не знайдено в джерелах | `422 dependency_not_allowed` зі списком відомих профілів |
| Жодне джерело не завантажилося й профілів у кеші немає | `502 upstream_unavailable` з `details.sources` |
| Частина джерел недоступна, профілі вже завантажувалися | Використовується остання вдала копія недоступних джерел |

Реальна відповідь, коли URL профілів недоступний:

```json
{
  "type": "urn:jane:problem:upstream_unavailable",
  "title": "Upstream unavailable",
  "status": 502,
  "detail": "runtime profiles cannot be loaded",
  "instance": "/v1/packages/examples.testsite-price-extractor/versions",
  "code": "upstream_unavailable",
  "retryable": true,
  "trace_id": "07444c4adc8769aed0b51fb1c5749995",
  "details": {"sources": ["http://127.0.0.1:18499/v1/info: ConnectError: All connection attempts failed"]}
}
```

Базовий dev-стек (`infra/compose.yaml`) джерел профілів Registry не задає: екстрактори в ньому не публікуються, доки не додано `JANE_REGISTRY_RUNTIME_PROFILES` — наприклад через [infra/compose.local.example.yaml](../../../infra/compose.local.example.yaml), скопійований у `infra/compose.local.yaml`. Без Handler Runtime можна вказати файл профілю з репозиторію, як у [quickstart](quickstart.md).

Розбіжність із картою власності даних: [data-ownership.md](../../../contracts/docs/data-ownership.md) називає опційною залежністю Registry Handler Runtime для «прогону тестів при публікації». Registry тестів не запускає; від Handler Runtime він використовує лише профілі runtime.

## Середовище виконання й бібліотеки

| Компонент | Вимога |
|---|---|
| Python | `>=3.12` (образ — `python:3.12-slim`) |
| [jane-kit](../../../libs/jane-kit/README.md) | спільна бібліотека workspace: конфігурація, ліміти, автентифікація, помилки, ідемпотентність, job |
| `psycopg[binary]`, `psycopg-pool` | `>=3.2` |
| `boto3` | `>=1.35` |
| `jsonschema` | `>=4.23` |
| `referencing` | `>=0.35` |
| `packaging` | `>=24` |
| `httpx` | `>=0.27` |

Точні версії зафіксовано в `uv.lock`; вимоги — у [pyproject.toml](../../../services/registry/pyproject.toml).
