# Конфігурація handler-runtime

Параметри читаються при створенні Settings. Зміни env потребують перезапуску; значення секретів у таблицях не наводяться. Джерело — [Settings](../../../services/handler-runtime/src/jane_handler_runtime/settings.py) і [спільні моделі Jane Kit](../jane-kit/configuration.md).

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
| `service_name` / `SERVICE_NAME` | `str` | `'handler-runtime'` | Ім’я у health/info/log. |
| `instance_id` / `INSTANCE_ID` | `str` | `f'{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex}'` | Унікальний owner lease для кожного старту. |
| `host` / `HOST` | `str` | `'127.0.0.1'` | Адреса слухання; none auth дозволено на loopback. |
| `port` / `PORT` | `int` | `8000` | Порт HTTP. |
| `log_level` / `LOG_LEVEL` | `str` | `'INFO'` | Рівень журналу. |
| `log_format` / `LOG_FORMAT` | `Literal['json', 'console']` | `'json'` | JSON або console. |
| `metrics_enabled` / `METRICS_ENABLED` | `bool` | `True` | Увімкнення /metrics. |
| `health_check_timeout_ms` / `HEALTH_CHECK_TIMEOUT_MS` | `int` | `2000`; ge=1 | Бюджет одного health check. |
| `limits_file` / `LIMITS_FILE` | `Path \| None` | `None` | Файл PlatformLimits; правила застосування нижче. |
| `sandbox_backend` / `SANDBOX_BACKEND` | `Literal['docker', 'subprocess']` | `'docker'` | docker або явно дозволений subprocess. |
| `allow_unsafe_subprocess` / `ALLOW_UNSAFE_SUBPROCESS` | `bool` | `False` | Дозволяє довірений subprocess без контейнерної ізоляції. |
| `docker_host` / `DOCKER_HOST` | `str \| None` | `None` | Endpoint engine; None використовує DOCKER_HOST/socket. |
| `docker_runtime` / `DOCKER_RUNTIME` | `str \| None` | `None` | OCI runtime контейнера. |
| `sandbox_user` / `SANDBOX_USER` | `str` | `'65534:65534'` | Непривілейований uid:gid. |
| `sandbox_labels` / `SANDBOX_LABELS` | `dict[str, str]` | `{}` | Додаткові labels sandbox для власного стенда. |
| `profile_images` / `PROFILE_IMAGES` | `dict[str, str]` | `{'python-extractor@1': 'jane/python-extractor:1'}` | JSON mapping profile → image; production pin за digest. |
| `registry_url` / `REGISTRY_URL` | `str \| None` | `None` | Registry v1 для викликів без package_archive. |
| `registry_token` / `REGISTRY_TOKEN` | `SecretStr \| None` | `None` | Секретний bearer для Registry. |
| `package_cache_dir` / `PACKAGE_CACHE_DIR` | `Path \| None` | `None` | Кеш за digest; None створює тимчасовий каталог. |
| `blob_roots` / `BLOB_ROOTS` | `list[Path]` | `[]` | Дозволені каталоги file://; [] відхиляє файлові blob. |
| `download_host_allowlist` / `DOWNLOAD_HOST_ALLOWLIST` | `list[str]` | `[]` | Дозволені hostname/hostname:port; [] відхиляє download. |
| `state_dsn` / `STATE_DSN` | `SecretStr \| None` | `None` | Власна PostgreSQL state; None — пам’ять одного процесу. |
| `state_schema` / `STATE_SCHEMA` | `str` | `'jane_handler_runtime'`; `pattern='^[a-z_][a-z0-9_]{0,62}$'` | Власна схема results/job/keys. |
| `contracts_dir` / `CONTRACTS_DIR` | `Path \| None` | `None` | Каталог JSON Schemas; None шукає checkout/env. |

Для кожного suffix префікс — `JANE_HANDLER_RUNTIME_`; наприклад `JANE_HANDLER_RUNTIME_HOST`. JSON списки/mapping задавайте JSON-рядком, booleans — true/false. Paths інтерпретуються від робочого каталогу. `None` означає відсутнє значення, а не рядок для env.


### Спільна перевірка доступу

`auth_none_allow_remote` явно дозволяє anonymous поза loopback для ізольованого тесту. `jwt_scope_claim` обирає claim зі scopes; `jwt_leeway_seconds` задає допуск часу. `jwt_jwks_cache_ttl_seconds` — строк кешу ключів, `jwt_jwks_refresh_cooldown_seconds` — мінімальна пауза refresh, `jwt_jwks_max_bytes` — максимум документа JWKS. `auth_max_token_bytes` обмежує bearer bytes. `metrics_public` дозволяє metrics без автентифікації, якщо metrics_enabled=true. Паролі/токени задавайте через secret refs або захищене середовище, а не файл пакета.

## Ліміти

Nested env має форму `JANE_HANDLER_RUNTIME_LIMITS__<GROUP>__<FIELD>`. Hard cap — `JANE_HANDLER_RUNTIME_LIMITS__HARD_CAPS__<GROUP>__<FIELD>`. Далі наведені всі власні scalar limit fields; моделі jobs/idempotency/pages/claims успадковують [ліміти Jane Kit](../jane-kit/configuration.md).

### sandbox

Ресурсний бюджет одного контейнера.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `cpu_cores` | `float` | `1.0` | gt=0 |
| `memory_mb` | `int` | `512` | ge=16 |
| `wall_time_ms` | `int` | `30000` | ge=1 |
| `max_output_bytes` | `int` | `4194304` | ge=1 |
| `max_processes` | `int` | `16` | ge=1 |
| `tmpfs_mb` | `int` | `64` | ge=0 |
### timeouts

Бюджети виклику, sync очікування й зовнішніх запитів.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `invocation_timeout_ms` | `int` | `60000` | ge=1 |
| `sync_response_max_ms` | `int` | `25000` | ge=1 |
| `request_timeout_ms` | `int` | `30000` | ge=1 |
### concurrency

Межі паралельного виконання.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_parallel_invocations` | `int` | `2` | ge=1 |
### packages

Розмір/кількість архівів, файлів, input і кешу; перевищення відхиляє роботу.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_archive_bytes` | `int` | `52428800` | ge=1 |
| `max_unpacked_bytes` | `int` | `209715200` | ge=1 |
| `max_files` | `int` | `5000` | ge=1 |
| `cache_max_entries` | `int` | `64` | ge=1 |
| `max_input_bytes` | `int` | `67108864` | ge=1 |
| `max_stored_results` | `int` | `10000` | ge=1 |
| `docker_api_timeout_ms` | `int` | `60000` | ge=1 |
| `max_stderr_in_result_bytes` | `int` | `16000` | ge=0 |
| `unavailable_retry_after_seconds` | `int` | `5` | ge=0 |
| `kill_grace_ms` | `int` | `2000` | ge=0 |
### state

Пул і leases власного shared state.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `pool_max_size` | `int` | `10` | ge=1 |
| `connect_timeout_ms` | `int` | `10000` | ge=1 |
| `in_progress_lease_ms` | `int` | `900000` | ge=1 |
| `job_lease_ms` | `int` | `30000` | ge=1 |
| `heartbeat_interval_ms` | `int` | `5000` | ge=1 |

## Застосування

Порядок: defaults → service hard caps → PlatformLimits file → env → request sandbox/timeouts. Request не підвищує hard caps. Типові caps: CPU 4, memory 4096 MB, wall 600000 ms, output 67108864 bytes, processes 256, tmpfs 1024 MB, invocation timeout 900000 ms. Явний platform/env cap замінює відповідний default cap.

Semaphore concurrency діє per instance. Empty blob_roots/host allowlist відхиляє зовнішні читання. `state_dsn=None` втрачає replay/job/results при restart. Subprocess відмовляється працювати без allow_unsafe_subprocess. Runtime підтримує тільки request groups sandbox/timeouts; решта належить сусідам.

GET /v1/info показує configured limits/caps; ефективні source/task/stage з provenance має лише Orchestrator. Повні типи, успадкування та default factory — у [генерованому довіднику Settings](reference/types/generated/jane_handler_runtime.settings.md). Обмеження й recovery описані в [operations](operations.md).
