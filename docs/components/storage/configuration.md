# Storage: конфігурація

Усі параметри Storage задаються змінними середовища з префіксом `JANE_STORAGE_`, ліміти — групою `JANE_STORAGE_LIMITS__*` або файлом лімітів платформи. Підключення до сховищ описуються окремо: файлом або через API. Код — [settings.py](../../../services/storage/src/jane_storage/settings.py).

## Зміст

- [Параметри процесу](#параметри-процесу)
- [Параметри Storage](#параметри-storage)
- [Ліміти](#ліміти)
- [Підключення](#підключення)
- [Політика секретів і хостів](#політика-секретів-і-хостів)
- [Пакети збереження й формати](#пакети-збереження-й-формати)
- [Як застосовуються зміни](#як-застосовуються-зміни)

## Параметри процесу

Спільні для всіх сервісів поля `JaneSettings` і `AuthSettings`; повний опис — [jane-kit: конфігурація](../jane-kit/configuration.md).

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_STORAGE_HOST` | рядок | `127.0.0.1` (образ: `0.0.0.0`) | Адреса прослуховування |
| `JANE_STORAGE_PORT` | ціле | `8107` (образ: `8000`) | Порт HTTP |
| `JANE_STORAGE_LOG_LEVEL` | рядок | `INFO` | Рівень журналу |
| `JANE_STORAGE_LOG_FORMAT` | `json` \| `console` | `json` | Формат журналу |
| `JANE_STORAGE_METRICS_ENABLED` | bool | `true` | `/metrics` і лічильники Storage |
| `JANE_STORAGE_HEALTH_CHECK_TIMEOUT_MS` | ціле | `2000` | Час на перевірки `/v1/health` |
| `JANE_STORAGE_LIMITS_FILE` | шлях | — | Файл лімітів платформи, наприклад `deploy/profiles/<профіль>.json` |
| `JANE_STORAGE_AUTH_MODE` | `none` \| `api_key` \| `jwt` | `none` | Автентифікація; `none` — лише для локальної роботи |
| `JANE_STORAGE_API_KEYS`, `JANE_STORAGE_API_KEYS_FILE` | JSON / шлях | — | Ключі для `api_key` із scopes |
| `JANE_STORAGE_JWT_*` | — | — | Параметри режиму `jwt` |
| `JANE_CONTRACTS_DIR` | шлях | пошук від коду до кореня checkout | Каталог `contracts/` для перевірки запитів |

Scopes операцій Storage: `handler:invoke` (запис, читання результатів викликів і підключень), `handler:test` (тести пакета), `connections:write` (зміна й перевірка підключень), `storage:read` (увесь `storage.v1`). Таблиця — [auth_scopes.py](../../../libs/jane-kit/src/jane_kit/auth_scopes.py), правила — [безпека](../../architecture/security.md).

## Параметри Storage

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_STORAGE_CONNECTIONS_FILE` | шлях | — | JSON або YAML `{"connections": [...]}` з постійними підключеннями |
| `JANE_STORAGE_SECRET_ENV_PREFIX` | рядок | `JANE_SECRET_` | `env:` у `secret_refs` може називати лише змінні з цим префіксом; порожній рядок вимикає `env:` |
| `JANE_STORAGE_SECRET_FILES_DIR` | шлях | `/run/secrets` | `file:` у `secret_refs` — лише файли в цьому каталозі; порожній рядок вимикає `file:` |
| `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST` | JSON-список | `[]` | Хости, до яких може звертатися адаптер підключення: `hostname` (будь-який порт) або `hostname:port`. Порожній — відхиляється кожне підключення з мережевою адресою |
| `JANE_STORAGE_TRANSIT_CONNECTION_ID` | рядок | — | Підключення типу `s3` або `minio` для читання вхідних `s3://` blob |
| `JANE_STORAGE_CONTENT_FILES_DIR` | шлях | — | Дозволений корінь для вхідних `file:///` blob; без нього локальні blob вимкнено |
| `JANE_STORAGE_TRANSIT_DIR` | шлях | — | Власні транзитні blob: великий RAW без постійного URI віддається як `file://` у `<каталог>/storage/` |
| `JANE_STORAGE_DOWNLOAD_HOST_ALLOWLIST` | JSON-список | `[]` | Хости `download_url` у `ContentRef`; порожній — завантаження вимкнено |
| `JANE_STORAGE_REGISTRY_URL` | URL | — | Registry для пакетів, яких немає серед вбудованих; лише `http(s)://host[:port][/шлях]` |
| `JANE_STORAGE_REGISTRY_TOKEN` | секрет | — | Bearer-токен для Registry; ніколи не журналюється й не доступний через `secret_refs` |
| `JANE_STORAGE_PACKAGE_DIRS` | JSON-список шляхів | `[]` | Додаткові каталоги пакетів збереження поряд із вбудованими |
| `JANE_STORAGE_VALIDATE_REQUESTS` | bool | `true` | Перевіряти `HandlerInvocation` і `Connection` за контрактами |

Порожній рядок у `JANE_STORAGE_SECRET_FILES_DIR`, `JANE_STORAGE_CONTENT_FILES_DIR`, `JANE_STORAGE_TRANSIT_DIR` і `JANE_STORAGE_REGISTRY_URL` означає «вимкнено». Хибний запис allowlist (не `hostname[:port]`) або хибний `REGISTRY_URL` зупиняє старт.

Dev-стек ([infra/compose.yaml](../../../infra/compose.yaml)) задає `AUTH_MODE=api_key`, файл підключень `infra/config/storage-connections.json`, allowlist `postgres:5432`, `sqlserver:1433`, `mongodb:27017`, `minio:9000`, `s3:8333`, а також `CONTENT_FILES_DIR=/var/lib/jane/storage/objects` і `TRANSIT_DIR=/var/lib/jane/storage/transit`.

## Ліміти

Значення збираються шарами: типові → файл платформи (`JANE_STORAGE_LIMITS_FILE`) → змінні `JANE_STORAGE_LIMITS__<група>__<поле>` → шар запиту. Жорсткі межі — `JANE_STORAGE_LIMITS__HARD_CAPS__<група>__<поле>`. Механізм шарів, контрактні назви й `hard_caps` — [jane-kit: ліміти](../jane-kit/configuration.md#ліміти). Ефективні значення друкуються в журналі під час старту (`configured limits`), контрактні — у `GET /v1/info`.

| Група і поле | Типово | Вплив |
|---|---|---|
| `conflict_retries.max_attempts` | `4` | Спроби коміту сутності при `CONFLICT`, включно з першою |
| `conflict_retries.initial_backoff_ms` / `max_backoff_ms` | `200` / `10000` | Пауза між спробами |
| `conflict_retries.backoff_multiplier` / `jitter` | `2.0` / `true` | Ріст паузи й випадковий множник |
| `timeouts.sync_response_max_ms` | `30000` | Синхронний виклик довший за це повертає `202` і job |
| `timeouts.request_timeout_ms` | `30000` | Читання blob (`download_url`, `s3://`) |
| `transfer.max_request_body_bytes` | `16777216` (16 МіБ) | Більше тіло — `413 payload_too_large` |
| `transfer.inline_max_bytes` | `1048576` (1 МіБ) | До цього розміру `GET /v1/objects/{id}` повертає вміст inline |
| `transfer.transit_ttl_seconds` | `604800` (7 днів), мін. `60` | Скільки живе власний транзитний blob |
| `transfer.transit_cleanup_interval_seconds` | `600` | Як часто прибираються прострочені транзитні blob |
| `objects.max_object_bytes` | `104857600` (100 МіБ) | Найбільший RAW або документ (вміст читається в пам'ять); більше — `resource_exceeded` |
| `objects.max_filter_material_ids` | `200` | Найбільше значень `material_id` у одному `GET /v1/objects` |
| `pages.default_page_size` / `max_page_size` | `50` / `500` | Розмір сторінки списків |
| `jobs.max_concurrent_jobs` | `4` | Виклики, що виконуються одночасно в одному екземплярі |
| `jobs.max_queued_jobs` | `1000` | Черга; понад неї — `503` з `Retry-After` |
| `jobs.job_timeout_ms` | `3600000` | Межа часу одного job |
| `jobs.job_retention_seconds` | `86400` | Скільки зберігається завершений job |
| `idempotency.idempotency_ttl_seconds` | `86400` | Скільки екземпляр пам'ятає `Idempotency-Key` |
| `idempotency.in_memory_max_entries` | `10000` | Найбільше ключів у пам'яті |
| `invocations.max_results_in_memory` | `10000` | Скільки `HandlerResult` зберігає `GET /v1/invocations/{id}` |
| `packages.max_archive_bytes` / `max_unpacked_bytes` | 20 МіБ / 50 МіБ | Межі архіву пакета з запиту чи Registry |
| `packages.max_files` | `2000` | Найбільше файлів у пакеті |
| `packages.cache_max_entries` | `128` | Пакети Registry в пам'яті (LRU за digest) |
| `packages.registry_connect_timeout_ms` / `registry_request_timeout_ms` | `5000` / `30000` | Завантаження архіву з Registry |
| `adapters.*` | див. нижче | Параметри, які сервіс передає в `open` кожного адаптера |

Параметри адаптерів (група `adapters`):

| Поле | Типово | Хто використовує |
|---|---|---|
| `lock_timeout_ms` | `30000` | filesystem (файли-блокування), sqlserver (блокування `ensure_schema`) |
| `lock_stale_ms` | `120000` | filesystem (старе блокування ламається), s3/minio (покинута заявка доставки) |
| `lock_poll_ms`, `replace_retry_ms` | `10`, `5000` | filesystem: опитування блокування, повтори `os.replace` на Windows |
| `pool_min_size`, `pool_max_size` | `1`, `10` | postgresql, sqlserver, mongodb; s3/minio — `pool_max_size` |
| `connect_timeout_ms`, `command_timeout_ms` | `10000`, `30000` | БД і S3 |
| `chunk_bytes` | не задано (адаптер: 4 МіБ, макс. 15 МіБ) | mongodb: розмір фрагмента RAW |
| `retry_max_attempts` | не задано (адаптер: 3) | s3/minio: спроби botocore на запит |

Поля `adapters.*` сервісу **перекривають** однойменні `params` підключення. Виняток — `chunk_bytes` і `retry_max_attempts`: це лише типові значення, `params` підключення має перевагу.

Шар запиту: з `HandlerInvocation.limits` Storage бере лише `timeouts.sync_response_max_ms` і `timeouts.request_timeout_ms`, обмежені `hard_caps`. Контрактний `limits.retries` етапу — політика викликача (повтор тим самим `Idempotency-Key`); повтори `CONFLICT` він не змінює.

Застаріла група `JANE_STORAGE_LIMITS__RETRIES__*` досі діє як синонім `conflict_retries` з попередженням у журналі; у спільному файлі платформи `retries` ігнорується.

## Підключення

Підключення — документ за [connection.schema.json](../../../contracts/schemas/common/connection.schema.json):

| Поле | Значення |
|---|---|
| `connection_id` | Ідентифікатор: малі літери, цифри, `.`, `_`, `-` |
| `kind` | Тип адаптера: `filesystem`, `postgresql`, `sqlserver`, `mongodb`, `minio`, `s3` |
| `title`, `labels` | Опис для людей |
| `params` | Місце в сховищі й параметри драйвера; секретів тут бути не може |
| `secret_refs` | Ім'я секрету → посилання `env:VAR`, `file:/шлях` (`vault:` вимкнено) |

Два способи передати підключення:

- **Файл** `JANE_STORAGE_CONNECTIONS_FILE` — постійний опис, читається під час старту. Помилка схеми зупиняє старт; порушення політики секретів лише журналюється, а підключення відхиляється під час використання.
- **API** `PUT /v1/connections/{connection_id}` — так Orchestrator синхронізує свій реєстр. Порушення політики — `422`, нічого не збережено. Підключення живе в пам'яті процесу до перезапуску.

Приклад файлу dev-стеку ([storage-connections.json](../../../infra/config/storage-connections.json)):

```json
{
  "connections": [
    {
      "connection_id": "raw-files",
      "kind": "filesystem",
      "title": "Development raw materials",
      "params": { "base_path": "/var/lib/jane/storage" }
    },
    {
      "connection_id": "results-pg",
      "kind": "postgresql",
      "title": "Development results",
      "params": { "host": "postgres", "port": 5432, "database": "jane_storage_results", "schema": "public", "sslmode": "disable" },
      "secret_refs": { "username": "env:JANE_SECRET_DEV_PG_USER", "password": "env:JANE_SECRET_DEV_PG_PASSWORD" }
    }
  ]
}
```

Значення в `params`, схожі на секрет (імена на кшталт `password`, `token`, `api_key`; рядки з ключем AWS, приватним ключем або `user:pass@` в URL), відхиляються з `422 secret_detected`. Параметри `params` кожного адаптера — [адаптери](adapters.md).

## Політика секретів і хостів

Підключення визначає, **куди** піде розв'язаний секрет, тому Storage обмежує обидва кінці ([policy.py](../../../services/storage/src/jane_storage/policy.py)):

- `env:VAR` — лише змінні з префіксом `JANE_STORAGE_SECRET_ENV_PREFIX` (типово `JANE_SECRET_`), тож не `PGPASSWORD` і не чужа конфігурація;
- `file:/шлях` — лише всередині `JANE_STORAGE_SECRET_FILES_DIR`; шлях розв'язується до читання, `..` і символьні посилання не виводять за межі;
- кожна мережева адреса адаптера має бути в `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST`.

Які адреси перевіряються:

| `kind` | Адреса | Типово |
|---|---|---|
| `filesystem` | — | — |
| `postgresql` | `params.host` + `params.port` | `localhost:5432` |
| `sqlserver` | `params.host` + `params.port` | `localhost:1433` |
| `mongodb` | `params.host`: `hostname[:port]`, кожен хост `mongodb://…` або ім'я `mongodb+srv://` (без порту) | `localhost:27017` |
| `minio` | хост `params.endpoint` | — (endpoint обов'язковий) |
| `s3` | фактичний хост запиту botocore до бакета (віртуальний хост AWS або `params.endpoint`) | регіон `us-east-1` |

Для будь-якого `kind` також перевіряються параметри `host`, `hosts`, `hostname`, `server`, `address`, `endpoint`, `endpoint_url`, `url`, `uri`, `dsn`, `connection_string`, `base_url`, `api_base`. Значення з `@`, зворотною скісною, пробілами, керівними символами чи IPv6-літералами відхиляються, а не нормалізуються. Власний `endpoint` для `s3` і `minio` вимагає `addressing_style: path`.

Приклад відповіді на підключення, що порушує політику (реальний запуск, порожній allowlist):

```json
{
  "status": 422,
  "code": "validation_failed",
  "detail": "connection violates the secret policy of this executor",
  "errors": [
    {"pointer": "/secret_refs/password", "code": "secret_ref_not_allowed", "message": "env: references must name variables starting with 'JANE_SECRET_'"},
    {"pointer": "/params/host", "code": "host_not_allowed", "message": "host 127.0.0.1:18210 is not in JANE_STORAGE_CONNECTION_HOST_ALLOWLIST"}
  ]
}
```

Повідомлення про помилки відкриття адаптера проходять редагування: розв'язані значення секретів замінюються на `***`. Спільна модель секретів платформи — [безпека](../../architecture/security.md).

## Пакети збереження й формати

Пакет збереження — маніфест без коду. Кожен пакет адаптера постачає свій стандартний пакет і реєструє його в entry point `jane.storage.packages`:

| Пакет | Адаптер | `writes` | Приймає | Параметри етапу (`params`) |
|---|---|---|---|---|
| `jane.storage-files@1.0.0` | `filesystem` | `raw_and_entities` | `material`, `entities` | `prefix`, `format.raw`, `format.entities` (`json` \| `jsonl`) |
| `jane.storage-postgresql@1.0.0` | `postgresql` | `raw_and_entities` | `material`, `entities` | `schema`, `table_prefix`, `format.raw` |
| `jane.storage-sqlserver@1.0.0` | `sqlserver` | `raw_and_entities` | `material`, `entities` | `schema`, `table_prefix`, `format.raw` |
| `jane.storage-mongodb@1.0.0` | `mongodb` | `raw_and_entities` | `material`, `entities` | `prefix`, `format.raw` |
| `jane.storage-minio@1.0.0` | `minio` | `raw_and_entities` | `material`, `entities` | `prefix`, `format.raw` |
| `jane.storage-s3@1.0.0` | `s3` | `raw_and_entities` | `material`, `entities` | `prefix`, `format.raw` |

Параметри етапу перевіряються за `schemas/params.schema.json` пакета; `prefix`, `schema`, `table_prefix` вибирають простір **усередині** підключення й перекривають однойменні `params` підключення. Таблиця просторів імен і типових значень — [storage-adapter.md](../../../contracts/docs/storage-adapter.md#простір-імен).

Формат RAW (`format.raw`) береться з параметрів етапу, потім з маніфесту, інакше діє типова поведінка ТЗ §5:

| Значення | Що зберігається |
|---|---|
| не задано | HTML/XHTML-сторінка — байт-у-байт як `text/html` (`.html`); будь-який інший RAW — JSON-документ `Material` із вбудованим вмістом (`.json`) |
| `original` | Байти як отримано; розширення — за медіатипом |
| `html` | Сторінка як `text/html`; не-HTML матеріал — `HandlerResult.failed` з `invalid_params` |
| `json` | JSON-документ `Material` із вмістом у `content.data` (`utf-8` або `base64`) |

Сутності завжди зберігаються як JSON-документи; файловий адаптер може вести історію у JSON Lines (`format.entities: jsonl`).

Перелік установлених пакетів із digest:

```powershell
uv run --all-packages jane-storage-packages list
```

```text
jane.storage-files@1.0.0  adapter=filesystem  writes=raw_and_entities  sha256:b87649411631a78b58f4e44e304dab362526e21861705a2e04f8a8a6d6aec12f
jane.storage-minio@1.0.0  adapter=minio  writes=raw_and_entities  sha256:aa521ad477f613472271ed9b46e9afa68b1f03d09974a50f0eb2146907d1a680
jane.storage-mongodb@1.0.0  adapter=mongodb  writes=raw_and_entities  sha256:f9bf94e803118d0d28d4fe004b59df865b6679a1bbc0025d10832a02a5d44dff
jane.storage-postgresql@1.0.0  adapter=postgresql  writes=raw_and_entities  sha256:4765e62faa6e82fa25a863dff2ef133905bf8e9b5e0b8f0f9e6285d2a451ac3b
jane.storage-s3@1.0.0  adapter=s3  writes=raw_and_entities  sha256:f67fc13b21711b053e96929d1ce38f6cc16b87368ea64407bdf9f1715ac1b07b
jane.storage-sqlserver@1.0.0  adapter=sqlserver  writes=raw_and_entities  sha256:a3fd13c6e28ae187a2a68303a8440722cb75bd4718349a4b3e27214b6e3954bd
```

Інші підкоманди: `archive <package_id> --out <файл>` пише канонічний архів, `publish --registry <url> [--token-env <змінна>]` публікує всі встановлені пакети в Registry. Формат пакетів — [contracts/docs/handler-packages.md](../../../contracts/docs/handler-packages.md).

## Як застосовуються зміни

| Що змінюється | Як застосувати |
|---|---|
| Змінні середовища, файл лімітів, файл підключень | Перезапуск процесу |
| Підключення через API | `PUT /v1/connections/{id}`: нові виклики відкривають новий адаптер, виклики в роботі завершуються на старому; незмінений документ адаптер не перевідкриває |
| Таймаути виклику | Поле `limits` у `HandlerInvocation`, у межах `hard_caps` |
| Параметри етапу (`prefix`, `schema`, `format`) | Поле `params` у `HandlerInvocation` — для кожного виклику |
| Новий адаптер або пакет | Установлення пакета адаптера й перезапуск; пакет збереження також можна передати в `package_archive` або через Registry |
