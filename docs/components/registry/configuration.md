# Registry: конфігурація

Registry налаштовується змінними середовища з префіксом `JANE_REGISTRY_`; вкладені значення розділяються `__`. Налаштування читаються один раз під час старту, тому будь-яка зміна — включно з лімітами — застосовується перезапуском процесу. Код налаштувань — [settings.py](../../../services/registry/src/jane_registry/settings.py); спільні поля процесу й автентифікації — `jane_kit.config.JaneSettings` і `jane_kit.auth.AuthSettings`.

## Зміст

- [Процес](#процес)
- [Сховище метаданих](#сховище-метаданих)
- [Blob-сховище](#blob-сховище)
- [Перевірка пакетів](#перевірка-пакетів)
- [Автентифікація](#автентифікація)
- [Ліміти](#ліміти)
- [Приклади конфігурацій](#приклади-конфігурацій)

## Процес

| Змінна | Тип | Типово | Зміст |
|---|---|---|---|
| `JANE_REGISTRY_HOST` | рядок | `127.0.0.1` (в образі `0.0.0.0`) | Адреса прослуховування |
| `JANE_REGISTRY_PORT` | ціле | `8105` (в образі `8000`) | Порт HTTP |
| `JANE_REGISTRY_SERVICE_NAME` | рядок | `registry` | Ім'я в журналах і `/v1/info` |
| `JANE_REGISTRY_INSTANCE_ID` | рядок | `<hostname>-<pid>-<uuid>` | Ідентифікатор екземпляра в журналах; власник job — він же з випадковим суфіксом |
| `JANE_REGISTRY_LOG_LEVEL` | рядок | `INFO` | Рівень журналу |
| `JANE_REGISTRY_LOG_FORMAT` | `json` або `console` | `json` | Формат журналу в stdout |
| `JANE_REGISTRY_METRICS_ENABLED` | boolean | `true` | Endpoint `/metrics` і лічильник публікацій |
| `JANE_REGISTRY_HEALTH_CHECK_TIMEOUT_MS` | ціле ≥ 1 | `2000` | Тайм-аут кожної перевірки `/v1/health` |
| `JANE_REGISTRY_LIMITS_FILE` | шлях | — | Файл лімітів платформи ([Ліміти](#ліміти)) |

## Сховище метаданих

| Змінна | Тип | Типово | Зміст |
|---|---|---|---|
| `JANE_REGISTRY_DB` | `postgres` або `memory` | `postgres` | `memory` — один процес без збереження, лише для дослідів і тестів |
| `JANE_REGISTRY_DB_URL` | секретний рядок | — | DSN власної бази, наприклад `postgresql://jane_registry:<пароль>@host:5432/jane_registry`; обов'язковий для `postgres` |
| `JANE_REGISTRY_DB_SCHEMA` | рядок `^[a-z_][a-z0-9_]{0,62}$` | `public` | Схема таблиць; створюється, якщо її немає (у dev-стеку — `jane_registry`) |

`JANE_REGISTRY_DB_URL` містить пароль: його передають через середовище або менеджер секретів і не комітять.

## Blob-сховище

| Змінна | Тип | Типово | Зміст |
|---|---|---|---|
| `JANE_REGISTRY_BLOB` | `s3` або `filesystem` | `s3` | Де зберігати архіви |
| `JANE_REGISTRY_BLOB_BUCKET` | рядок | `jane-registry` | Бакет (для `filesystem` — підкаталог `BLOB_ROOT`) |
| `JANE_REGISTRY_BLOB_PREFIX` | рядок | `sha256/` | Префікс ключа; ключ = `<prefix><sha256 hex>` |
| `JANE_REGISTRY_BLOB_ROOT` | шлях | — | Для `filesystem`: каталог, що замінює бакет; обов'язковий |
| `JANE_REGISTRY_S3_ENDPOINT_URL` | URL | — | Адреса MinIO чи іншого S3-сумісного сховища; порожньо — AWS S3 |
| `JANE_REGISTRY_S3_REGION` | рядок | `us-east-1` | Регіон |
| `JANE_REGISTRY_S3_ACCESS_KEY` | секретний рядок | — | Ключ доступу |
| `JANE_REGISTRY_S3_SECRET_KEY` | секретний рядок | — | Секретний ключ |
| `JANE_REGISTRY_S3_CREATE_BUCKET` | boolean | `true` | Створити бакет під час старту, якщо його немає |

## Перевірка пакетів

| Змінна | Тип | Типово | Зміст |
|---|---|---|---|
| `JANE_REGISTRY_CONTRACTS_DIR` | шлях | `contracts/` checkout або `/app/contracts` | Каталог із `schemas/package-manifest.schema.json` та іншими схемами |
| `JANE_REGISTRY_RUNTIME_PROFILES` | JSON-список рядків | `[]` | Джерела профілів runtime: шляхи до файлів або http(s) URL (`<handler-runtime>/v1/info`) |
| `JANE_REGISTRY_RUNTIME_PROFILES_TOKEN_REF` | посилання на секрет `env:VAR` або `file:/шлях` | — | Токен Registry для http(s)-джерел профілів |
| `JANE_REGISTRY_REQUIRE_TESTS` | boolean | `true` | Вимагати від `extractor` і `llm` тести `success` і `empty`/`unrecognized` |

Джерело профілів може бути одним документом профілю, списком профілів, об'єктом `{"runtime_profiles": {...}}`, картою `{"<профіль>": {...}}` або відповіддю `ServiceInfo` Handler Runtime. Приклад значення: `JANE_REGISTRY_RUNTIME_PROFILES='["http://handler-runtime:8000/v1/info"]'`.

## Автентифікація

Клієнти передають `Authorization: Bearer <токен>`; scope перевіряється для кожної операції ([integration.md](integration.md#автентифікація)).

| Змінна | Тип | Типово | Зміст |
|---|---|---|---|
| `JANE_REGISTRY_AUTH_MODE` | `none`, `api_key`, `jwt` | `none` | `none` — будь-який клієнт має всі scope (лише локально; у журналі попередження) |
| `JANE_REGISTRY_AUTH_NONE_ALLOW_REMOTE` | boolean | `false` | Без нього `auth_mode=none` з не-loopback `HOST` не стартує |
| `JANE_REGISTRY_API_KEYS` | JSON-список | `[]` | Ключі для `api_key` |
| `JANE_REGISTRY_API_KEYS_FILE` | шлях | — | JSON або YAML з тим самим списком (додається до `API_KEYS`) |
| `JANE_REGISTRY_JWT_JWKS_URL` | URL | — | JWKS постачальника ідентичності (HTTPS; HTTP — лише для loopback) |
| `JANE_REGISTRY_JWT_ISSUER`, `JANE_REGISTRY_JWT_AUDIENCE` | рядок | — | Обов'язкові `iss` і `aud` |
| `JANE_REGISTRY_JWT_ALGORITHMS` | JSON-список | `["RS256", "ES256"]` | Дозволені алгоритми |
| `JANE_REGISTRY_JWT_SCOPE_CLAIM` | рядок | `scope` | Claim зі scope |
| `JANE_REGISTRY_JWT_LEEWAY_SECONDS` | 0–600 | `30` | Допустимий зсув годинника |
| `JANE_REGISTRY_JWT_JWKS_CACHE_TTL_SECONDS` | ціле ≥ 1 | `300` | Скільки використовувати завантажені ключі |
| `JANE_REGISTRY_JWT_JWKS_TIMEOUT_MS` | ціле ≥ 1 | `5000` | Тайм-аут запиту JWKS |
| `JANE_REGISTRY_JWT_JWKS_REFRESH_COOLDOWN_SECONDS` | ціле ≥ 0 | `10` | Пауза між позаплановими оновленнями JWKS |
| `JANE_REGISTRY_JWT_JWKS_MAX_BYTES` | ціле | `1048576` | Найбільший документ JWKS |
| `JANE_REGISTRY_AUTH_MAX_TOKEN_BYTES` | ціле | `16384` | Довший токен — `401` без розбору |
| `JANE_REGISTRY_METRICS_PUBLIC` | boolean | `true` | `/metrics` без токена; `false` — потрібен будь-який дійсний токен |

Елемент `API_KEYS`: `{"name": "...", "sha256": "<hex ключа>" | "secret_ref": "env:VAR" | "file:/шлях", "scopes": [...], "actor": "human" | "llm" | "import"}`. Registry зберігає лише хеші; `secret_ref` розв'язується один раз під час старту. Ключ із недопустимим `actor` зупиняє старт. Для `jwt` актор береться з claim `actor` (типово `human`).

Ключі dev-стеку з [infra/compose.yaml](../../../infra/compose.yaml):

| Ключ | Scope | Актор |
|---|---|---|
| `admin` | `registry:read`, `registry:write`, `registry:approve` | `human` |
| `assistant` | `registry:read`, `registry:write`, `registry:approve` | `llm` |
| `orchestrator`, `handler-runtime`, `storage`, `llm`, `web-collector`, `telegram-collector` | `registry:read` | `human` |

## Ліміти

Ліміти — окрема модель `ServiceLimits` з безпечними типовими значеннями. Порядок шарів: типові значення → файл `JANE_REGISTRY_LIMITS_FILE` → змінні `JANE_REGISTRY_LIMITS__<група>__<ліміт>`. Невідома назва ліміту в змінній зупиняє старт (`LimitError: unknown limit(s)`); ліміти файлу платформи, яких у Registry немає, ігноруються. Ефективні значення друкуються в рядку журналу `registry started`, а контрактні (`transfer.*`) — у `GET /v1/info`.

| Ліміт (`група.ліміт`) | Типово | Зміст |
|---|---|---|
| `packages.max_archive_bytes` | 20 MiB | Найбільший ZIP (завантажений або канонічний) |
| `packages.max_unpacked_bytes` | 50 MiB | Сума розмірів файлів пакета |
| `packages.max_files` | 2000 | Файлів у пакеті |
| `packages.max_versions_per_package` | 1000 | Версій одного пакета; більше — `422 limit_exceeded` |
| `packages.archive_cache_bytes` | 64 MiB | LRU-кеш архівів у пам'яті екземпляра; `0` — без кешу |
| `secrets.max_scan_bytes_per_file` | 2 MiB | Більший файл не сканується й відхиляє пакет (`limit_exceeded`) |
| `secrets.min_entropy_token_length` | 32 | Найкоротший рядок для перевірки ентропії |
| `secrets.scan_time_budget_ms` | 20000 | Час сканування одного пакета |
| `secrets.max_findings_per_file` | 20 | Знахідок у відповіді на файл |
| `secrets.entropy_threshold` | 4.3 | Поріг ентропії Шеннона (біт на символ) |
| `diff.max_context_lines` | 50 | Верхня межа `context_lines` |
| `diff.max_diff_file_bytes` | 1 MiB | Більші файли в diff — лише статус |
| `diff.max_merge_file_bytes` | 1 MiB | Більші текстові файли, змінені з обох боків, — конфлікт перенесення |
| `requests.max_request_body_bytes` | 30 MiB | Тіло запиту; контрактний `transfer.max_request_body_bytes` |
| `profiles.fetch_timeout_ms` | 5000 | Тайм-аут читання профілю за URL |
| `profiles.refresh_seconds` | 300 | Кеш профілів |
| `db.pool_min_size`, `db.pool_max_size` | 1, 10 | Пул з'єднань PostgreSQL |
| `db.connect_timeout_ms` | 5000 | Тайм-аут з'єднання й очікування пулу |
| `db.statement_timeout_ms` | 30000 | `statement_timeout` сесій |
| `blob.connect_timeout_ms`, `blob.read_timeout_ms` | 5000, 60000 | Тайм-аути S3 |
| `blob.max_attempts` | 3 | Спроби одного запиту S3 |
| `recovery.in_progress_lease_ms` | 120000 | Оренда незавершеного `Idempotency-Key` |
| `recovery.job_lease_ms` | 60000 | Оренда job екземпляром |
| `recovery.job_heartbeat_ms` | 15000 | Як часто екземпляр поновлює оренди (менше за `job_lease_ms`) |
| `jobs.max_concurrent_jobs` | 4 | Job, що виконуються одночасно в екземплярі |
| `jobs.max_queued_jobs` | 1000 | Більше — `503 service_unavailable` |
| `jobs.job_timeout_ms` | 3600000 | Найдовший job |
| `jobs.job_retention_seconds` | 86400 | Скільки зберігати завершені job; контрактний `transfer.job_retention_seconds` |
| `jobs.queue_full_retry_after_seconds` | 1 | `Retry-After` для `503` |
| `idempotency.idempotency_ttl_seconds` | 86400 | Скільки пам'ятати ключ; контрактний `transfer.idempotency_ttl_seconds` |
| `idempotency.in_memory_max_entries` | 10000 | Лише для `memory`: найбільше ключів |
| `pages.default_page_size`, `pages.max_page_size` | 50, 500 | Пагінація |

Змінні середовища використовують назви груп Registry, а файл платформи — назви контракту. Наприклад, ліміт тіла запиту задається як `JANE_REGISTRY_LIMITS__REQUESTS__MAX_REQUEST_BODY_BYTES=4096`; змінна `JANE_REGISTRY_LIMITS__TRANSFER__MAX_REQUEST_BODY_BYTES` зупиняє старт помилкою `unknown limit(s) ['transfer.max_request_body_bytes']`. Профіль [deploy/profiles/single-node.json](../../../deploy/profiles/single-node.json) як `JANE_REGISTRY_LIMITS_FILE` дає Registry `requests.max_request_body_bytes` = 16 MiB, `jobs.job_retention_seconds` = 7 діб і `idempotency.idempotency_ttl_seconds` = 1 добу; решта його лімітів до Registry не належить і ігнорується. Перевірено командою (PowerShell):

```powershell
$env:JANE_REGISTRY_LIMITS_FILE = "deploy/profiles/single-node.json"
uv run --package jane-registry python -c "from jane_registry.settings import Settings, resolve_service_limits; r = resolve_service_limits(Settings()); print(r.limits.requests.max_request_body_bytes, r.limits.jobs.job_retention_seconds, r.limits.idempotency.idempotency_ttl_seconds)"
```

```text
16777216 604800 86400
```

Жорсткі межі платформи задаються змінними `JANE_REGISTRY_LIMITS__HARD_CAPS__<група>__<ліміт>` або розділом `hard_caps` файлу.

## Приклади конфігурацій

Локальні досліди без зовнішніх сервісів — [quickstart.md](quickstart.md#запуск). Робочий екземпляр із PostgreSQL і MinIO (значення секретів — з менеджера секретів, тут заповнювачі):

```ini
JANE_REGISTRY_HOST=0.0.0.0
JANE_REGISTRY_PORT=8000
JANE_REGISTRY_DB=postgres
JANE_REGISTRY_DB_URL=postgresql://jane_registry:<пароль>@postgres:5432/jane_registry
JANE_REGISTRY_DB_SCHEMA=jane_registry
JANE_REGISTRY_BLOB=s3
JANE_REGISTRY_S3_ENDPOINT_URL=http://minio:9000
JANE_REGISTRY_S3_ACCESS_KEY=<ключ>
JANE_REGISTRY_S3_SECRET_KEY=<секрет>
JANE_REGISTRY_AUTH_MODE=api_key
JANE_REGISTRY_API_KEYS_FILE=/run/secrets/registry-api-keys.json
JANE_REGISTRY_RUNTIME_PROFILES=["http://handler-runtime:8000/v1/info"]
JANE_REGISTRY_RUNTIME_PROFILES_TOKEN_REF=env:JANE_SECRET_REGISTRY_TOKEN
JANE_REGISTRY_LIMITS_FILE=/etc/jane/single-node.json
```

Так налаштовано сервіс `registry` у [infra/compose.yaml](../../../infra/compose.yaml) (ключі — в `JANE_REGISTRY_API_KEYS`, а не у файлі; профілі — через `infra/compose.local.yaml`).
