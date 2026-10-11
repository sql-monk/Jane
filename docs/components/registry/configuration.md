# Конфігурація registry

Параметри читаються при створенні Settings. Зміни env потребують перезапуску; значення секретів у таблицях не наводяться. Джерело — [Settings](../../../services/registry/src/jane_registry/settings.py) і [спільні моделі Jane Kit](../jane-kit/configuration.md).

## Зміст

- [Параметри процесу](#параметри-процесу)
- [Ліміти](#ліміти)
- [Застосування](#застосування)

## Параметри процесу

| Поле / env suffix | Тип | Типове / вимога | Вплив |
|---|---|---|---|
| `auth_mode` / `AUTH_MODE` | `AuthMode` | `'none'` | none/api_key/jwt; визначає перевірку bearer. |
| `auth_none_allow_remote` / `AUTH_NONE_ALLOW_REMOTE` | `bool` | `False` | Параметр спільної перевірки доступу; точна семантика нижче. |
| `api_keys` / `API_KEYS` | `list[dict[str, Any]]` | `[]` | JSON-конфіг ключів із sha256/secret_ref/scopes. |
| `api_keys_file` / `API_KEYS_FILE` | `Path \| None` | `None` | Файл конфігурації API keys. |
| `jwt_jwks_url` / `JWT_JWKS_URL` | `str \| None` | `None` | JWKS endpoint перевірки JWT. |
| `jwt_issuer` / `JWT_ISSUER` | `str \| None` | `None` | Очікуваний JWT issuer. |
| `jwt_audience` / `JWT_AUDIENCE` | `str \| None` | `None` | Очікувана JWT audience. |
| `jwt_algorithms` / `JWT_ALGORITHMS` | `list[str]` | `['RS256', 'ES256']` | Дозволені алгоритми підпису. |
| `jwt_scope_claim` / `JWT_SCOPE_CLAIM` | `str` | `'scope'` | Параметр спільної перевірки доступу; точна семантика нижче. |
| `jwt_leeway_seconds` / `JWT_LEEWAY_SECONDS` | `int` | `30`; ge=0; le=600 | Параметр спільної перевірки доступу; точна семантика нижче. |
| `jwt_jwks_cache_ttl_seconds` / `JWT_JWKS_CACHE_TTL_SECONDS` | `int` | `300`; ge=1 | Параметр спільної перевірки доступу; точна семантика нижче. |
| `jwt_jwks_timeout_ms` / `JWT_JWKS_TIMEOUT_MS` | `int` | `5000`; ge=1 | Тайм-аут JWKS. |
| `jwt_jwks_refresh_cooldown_seconds` / `JWT_JWKS_REFRESH_COOLDOWN_SECONDS` | `int` | `10`; ge=0 | Параметр спільної перевірки доступу; точна семантика нижче. |
| `jwt_jwks_max_bytes` / `JWT_JWKS_MAX_BYTES` | `int` | `1048576`; ge=1024 | Параметр спільної перевірки доступу; точна семантика нижче. |
| `auth_max_token_bytes` / `AUTH_MAX_TOKEN_BYTES` | `int` | `16384`; ge=256 | Параметр спільної перевірки доступу; точна семантика нижче. |
| `metrics_public` / `METRICS_PUBLIC` | `bool` | `True` | Параметр спільної перевірки доступу; точна семантика нижче. |
| `service_name` / `SERVICE_NAME` | `str` | `'registry'` | Ім’я у health/info/log. |
| `instance_id` / `INSTANCE_ID` | `str` | `f'{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex}'` | Унікальний owner lease для кожного старту. |
| `host` / `HOST` | `str` | `'127.0.0.1'` | Адреса слухання; none auth дозволено на loopback. |
| `port` / `PORT` | `int` | `8105` | Порт HTTP. |
| `log_level` / `LOG_LEVEL` | `str` | `'INFO'` | Рівень журналу. |
| `log_format` / `LOG_FORMAT` | `Literal['json', 'console']` | `'json'` | JSON або console. |
| `metrics_enabled` / `METRICS_ENABLED` | `bool` | `True` | Увімкнення /metrics. |
| `health_check_timeout_ms` / `HEALTH_CHECK_TIMEOUT_MS` | `int` | `2000`; ge=1 | Бюджет одного health check. |
| `limits_file` / `LIMITS_FILE` | `Path \| None` | `None` | Файл PlatformLimits; правила застосування нижче. |
| `db` / `DB` | `Literal['postgres', 'memory']` | `'postgres'` | Backend метаданих; postgres довговічний, memory одноекземплярний. |
| `db_url` / `DB_URL` | `SecretStr \| None` | `None` | Секретний DSN власної PostgreSQL; обов’язковий для postgres. |
| `db_schema` / `DB_SCHEMA` | `str` | `'public'`; `pattern='^[a-z_][a-z0-9_]{0,62}$'` | Власна схема метаданих. |
| `blob` / `BLOB` | `Literal['s3', 'filesystem']` | `'s3'` | Backend архівів: s3 або filesystem. |
| `blob_bucket` / `BLOB_BUCKET` | `str` | `'jane-registry'` | Власний bucket/каталог архівів. |
| `blob_prefix` / `BLOB_PREFIX` | `str` | `'sha256/'` | Префікс content-addressed ключа. |
| `blob_root` / `BLOB_ROOT` | `Path \| None` | `None` | Файловий root; обов’язковий для filesystem. |
| `s3_endpoint_url` / `S3_ENDPOINT_URL` | `str \| None` | `None` | S3-сумісний endpoint; None використовує AWS endpoint. |
| `s3_region` / `S3_REGION` | `str` | `'us-east-1'` | Регіон S3. |
| `s3_access_key` / `S3_ACCESS_KEY` | `SecretStr \| None` | `None` | Секретний access key. |
| `s3_secret_key` / `S3_SECRET_KEY` | `SecretStr \| None` | `None` | Секретний secret key. |
| `s3_create_bucket` / `S3_CREATE_BUCKET` | `bool` | `True` | Створювати bucket при старті. |
| `contracts_dir` / `CONTRACTS_DIR` | `Path \| None` | `None` | Каталог JSON Schemas; None шукає checkout/env. |
| `runtime_profiles` / `RUNTIME_PROFILES` | `list[str]` | `[]` | JSON-список шляхів/URL runtime-профілів. |
| `require_tests` / `REQUIRE_TESTS` | `bool` | `True` | Пакет потребує success та empty/unrecognized кейсу. |
| `runtime_profiles_token_ref` / `RUNTIME_PROFILES_TOKEN_REF` | `str \| None` | `None` | Secret ref власного token для HTTP runtime profile. |

Для кожного suffix префікс — `JANE_REGISTRY_`; наприклад `JANE_REGISTRY_HOST`. JSON списки/mapping задавайте JSON-рядком, booleans — true/false. Paths інтерпретуються від робочого каталогу. `None` означає відсутнє значення, а не рядок для env.


### Спільна перевірка доступу

`auth_none_allow_remote` явно дозволяє anonymous поза loopback для ізольованого тесту. `jwt_scope_claim` обирає claim зі scopes; `jwt_leeway_seconds` задає допуск часу. `jwt_jwks_cache_ttl_seconds` — строк кешу ключів, `jwt_jwks_refresh_cooldown_seconds` — мінімальна пауза refresh, `jwt_jwks_max_bytes` — максимум документа JWKS. `auth_max_token_bytes` обмежує bearer bytes. `metrics_public` дозволяє metrics без автентифікації, якщо metrics_enabled=true. Паролі/токени задавайте через secret refs або захищене середовище, а не файл пакета.

## Ліміти

Nested env має форму `JANE_REGISTRY_LIMITS__<GROUP>__<FIELD>`. Hard cap — `JANE_REGISTRY_LIMITS__HARD_CAPS__<GROUP>__<FIELD>`. Далі наведені всі власні scalar limit fields; моделі jobs/idempotency/pages/claims успадковують [ліміти Jane Kit](../jane-kit/configuration.md).

### packages

Розмір/кількість архівів, файлів, input і кешу; перевищення відхиляє роботу.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_archive_bytes` | `int` | `20971520` | ge=1024 |
| `max_unpacked_bytes` | `int` | `52428800` | ge=1024 |
| `max_files` | `int` | `2000` | ge=1 |
| `max_versions_per_package` | `int` | `1000` | ge=1 |
| `archive_cache_bytes` | `int` | `67108864` | ge=0 |
### secrets

Бюджет сканування; жоден файл не приймається без перевірки.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_scan_bytes_per_file` | `int` | `2097152` | ge=1024 |
| `min_entropy_token_length` | `int` | `32` | ge=8 |
| `scan_time_budget_ms` | `int` | `20000` | ge=1 |
| `max_findings_per_file` | `int` | `20` | ge=1 |
| `entropy_threshold` | `float` | `4.3` | gt=0 |
### diff

Ліміти текстового diff/merge; великі файли показують status або conflict.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_context_lines` | `int` | `50` | ge=0 |
| `max_diff_file_bytes` | `int` | `1048576` | ge=1024 |
| `max_merge_file_bytes` | `int` | `1048576` | ge=1024 |
### requests

Максимум HTTP body; перевищення → 413.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_request_body_bytes` | `int` | `31457280` | ge=1024 |
### profiles

Бюджет читання/оновлення runtime-профілів.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `fetch_timeout_ms` | `int` | `5000` | ge=1 |
| `refresh_seconds` | `int` | `300` | ge=1 |
### db

Пул і тайм-аути власної PostgreSQL.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `pool_min_size` | `int` | `1` | ge=0 |
| `pool_max_size` | `int` | `10` | ge=1 |
| `connect_timeout_ms` | `int` | `5000` | ge=1 |
| `statement_timeout_ms` | `int` | `30000` | ge=1 |
### blob

Тайм-аути й кількість S3 спроб.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `connect_timeout_ms` | `int` | `5000` | ge=1 |
| `read_timeout_ms` | `int` | `60000` | ge=1 |
| `max_attempts` | `int` | `3` | ge=1 |
### recovery

Тривалість claim/job lease і heartbeat.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `in_progress_lease_ms` | `int` | `120000` | ge=1000 |
| `job_lease_ms` | `int` | `60000` | ge=1000 |
| `job_heartbeat_ms` | `int` | `15000` | ge=100 |

## Застосування

Порядок: defaults → PlatformLimits file → env → додаткові programmatic layers. Спільні контрактні поля, які Registry не споживає, позначаються ignored; помилки власних назв не замовчуються. `db=postgres` потребує db_url, `blob=filesystem` — blob_root. Job heartbeat має бути коротшим за job lease.

Secret scan перевищення розміру/бюджету повертає limit_exceeded; package не приймається unscanned. Максимум request body дає 413; archive/version caps — 422. Для profile URL використовуйте runtime_profiles_token_ref, не пароль у URL.

GET /v1/info показує configured limits/caps; ефективні source/task/stage з provenance має лише Orchestrator. Повні типи, успадкування та default factory — у [генерованому довіднику Settings](reference/types/generated/jane_registry.settings.md). Обмеження й recovery описані в [operations](operations.md).
