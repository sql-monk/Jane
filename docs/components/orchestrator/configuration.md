# Конфігурація orchestrator

Параметри читаються при створенні Settings. Зміни env потребують перезапуску; значення секретів у таблицях не наводяться. Джерело — [Settings](../../../services/orchestrator/src/jane_orchestrator/settings.py) і [спільні моделі Jane Kit](../jane-kit/configuration.md).

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
| `service_name` / `SERVICE_NAME` | `str` | `'orchestrator'` | Ім’я у health/info/log. |
| `instance_id` / `INSTANCE_ID` | `str` | `f'{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex}'` | Унікальний owner lease для кожного старту. |
| `host` / `HOST` | `str` | `'127.0.0.1'` | Адреса слухання; none auth дозволено на loopback. |
| `port` / `PORT` | `int` | `8109` | Порт HTTP. |
| `log_level` / `LOG_LEVEL` | `str` | `'INFO'` | Рівень журналу. |
| `log_format` / `LOG_FORMAT` | `Literal['json', 'console']` | `'json'` | JSON або console. |
| `metrics_enabled` / `METRICS_ENABLED` | `bool` | `True` | Увімкнення /metrics. |
| `health_check_timeout_ms` / `HEALTH_CHECK_TIMEOUT_MS` | `int` | `2000`; ge=1 | Бюджет одного health check. |
| `limits_file` / `LIMITS_FILE` | `Path \| None` | `None` | Файл PlatformLimits; правила застосування нижче. |
| `database_url` / `DATABASE_URL` | `str` | `'postgresql://jane@127.0.0.1:5432/jane_orchestrator'` | DSN власної БД Orchestrator; пароль задайте зовні. |
| `executors` / `EXECUTORS` | `list[ExecutorConfig]` | `[]` | JSON-список ExecutorConfig. |
| `executors_file` / `EXECUTORS_FILE` | `Path \| None` | `None` | JSON-файл додаткових executor; доповнює список. |
| `contracts_dir` / `CONTRACTS_DIR` | `Path \| None` | `None` | Каталог JSON Schemas; None шукає checkout/env. |
| `service_token_ref` / `SERVICE_TOKEN_REF` | `str \| None` | `None` | Типовий bearer secret ref для executor без власного. |
| `scheduler_enabled` / `SCHEDULER_ENABLED` | `bool` | `True` | Створення due runs worker scheduler. |
| `run_workers` / `RUN_WORKERS` | `bool` | `True` | Worker threads усередині HTTP-процесу. |

Для кожного suffix префікс — `JANE_ORCHESTRATOR_`; наприклад `JANE_ORCHESTRATOR_HOST`. JSON списки/mapping задавайте JSON-рядком, booleans — true/false. Paths інтерпретуються від робочого каталогу. `None` означає відсутнє значення, а не рядок для env.


### Спільна перевірка доступу

`auth_none_allow_remote` явно дозволяє anonymous поза loopback для ізольованого тесту. `jwt_scope_claim` обирає claim зі scopes; `jwt_leeway_seconds` задає допуск часу. `jwt_jwks_cache_ttl_seconds` — строк кешу ключів, `jwt_jwks_refresh_cooldown_seconds` — мінімальна пауза refresh, `jwt_jwks_max_bytes` — максимум документа JWKS. `auth_max_token_bytes` обмежує bearer bytes. `metrics_public` дозволяє metrics без автентифікації, якщо metrics_enabled=true. Паролі/токени задавайте через secret refs або захищене середовище, а не файл пакета.

## Ліміти

Nested env має форму `JANE_ORCHESTRATOR_LIMITS__<GROUP>__<FIELD>`. Hard cap — `JANE_ORCHESTRATOR_LIMITS__HARD_CAPS__<GROUP>__<FIELD>`. Далі наведені всі власні scalar limit fields; моделі jobs/idempotency/pages/claims успадковують [ліміти Jane Kit](../jane-kit/configuration.md).

### contract.queue

Місткість черги й inflight; дає backpressure.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_queue_depth` | `int` | `10000` | ge=1 |
| `max_inflight_materials` | `int` | `100` | ge=1 |
### contract.concurrency

Межі паралельного виконання.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `max_parallel_runs_per_task` | `int` | `1` | ge=1 |
| `max_parallel_stage_items` | `int` | `4` | ge=1 |
### contract.timeouts

Бюджети виклику, sync очікування й зовнішніх запитів.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `connect_timeout_ms` | `int` | `5000` | ge=1 |
| `request_timeout_ms` | `int` | `30000` | ge=1 |
| `invocation_timeout_ms` | `int` | `60000` | ge=1 |
| `run_timeout_ms` | `int` | `21600000` | ge=1 |
### contract.transfer

TTL повторів доставки.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `idempotency_ttl_seconds` | `int` | `86400` | ge=60 |
### contract

Типові контрактні бюджети для snapshot run.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `retries` | `RetryPolicy` | `RetryPolicy(max_attempts=3, initial_backoff_ms=1000, max_backoff_ms=60000)` | за типом поля |
### engine

Параметр worker/queue/lease/diagnostics; застосовується при старті.

| Поле | Тип | Типове | Допустимість |
|---|---|---|---|
| `workers` | `int` | `2` | ge=0 |
| `lease_ms` | `int` | `30000` | ge=100 |
| `heartbeat_ms` | `int` | `10000` | ge=50 |
| `poll_interval_ms` | `int` | `500` | ge=10 |
| `feed_page_size` | `int` | `100` | ge=1 |
| `feed_wait_ms` | `int` | `1000` | ge=0 |
| `backpressure_recheck_ms` | `int` | `500` | ge=10 |
| `scheduler_interval_ms` | `int` | `1000` | ge=10 |
| `sync_retry_ms` | `int` | `5000` | ge=10 |
| `sync_max_attempts` | `int` | `5` | ge=1 |
| `executor_health_timeout_ms` | `int` | `2000` | ge=1 |
| `executor_keepalive_expiry_ms` | `int` | `4000` | ge=0 |
| `executor_stale_connection_retries` | `int` | `1` | ge=0 |
| `job_poll_interval_ms` | `int` | `500` | ge=10 |
| `idempotency_in_progress_poll_ms` | `int` | `500` | ge=10 |
| `idempotency_in_progress_max_wait_ms` | `int` | `120000` | ge=1 |
| `idempotency_in_progress_retry_ms` | `int` | `5000` | ge=10 |
| `problem_samples` | `int` | `10` | ge=0 |
| `trace_outputs_max` | `int` | `100` | ge=0 |
| `attempt_history_max` | `int` | `20` | ge=0 |
| `stored_selection_max_ids` | `int` | `10000` | ge=1 |
| `stored_material_ids_per_request` | `int` | `100` | ge=0 |
| `db_pool_max` | `int` | `10` | ge=1 |
| `max_lease_reclaims` | `int` | `5` | ge=1 |
| `schedule_batch` | `int` | `20` | ge=1 |
| `reap_batch` | `int` | `50` | ge=1 |

## Застосування

Є два різні контури. Внутрішні ServiceLimits читаються defaults → env → programmatic layer; limits_file не є цим контуром. PlatformLimits file засіває власний DB-документ платформи. Runtime API `/v1/limits/platform` керує ним; effective limits обчислюються platform → source → task → stage → request з hard_caps та provenance і фіксуються в run.

Heartbeat має бути коротшим за engine lease. Зменшення queue/inflight дає backpressure. `run_workers=false` робить HTTP API-only; standalone worker command запускає щонайменше один thread. ExecutorConfig приймає token_ref або deprecated token, не обидва; unresolved ref зупиняє старт.

GET /v1/info показує configured limits/caps; ефективні source/task/stage з provenance має лише Orchestrator. Повні типи, успадкування та default factory — у [генерованому довіднику Settings](reference/types/generated/jane_orchestrator.settings.md). Обмеження й recovery описані в [operations](operations.md).
