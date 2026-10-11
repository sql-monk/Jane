# llm: конфігурація

Параметри процесу читаються під час старту з `JANE_LLM_`. Для вкладених лімітів використовуйте `JANE_LLM_LIMITS__<GROUP>__<FIELD>`; назви в таблицях — шляхи моделей. Списки у середовищі передавайте JSON-масивами. Зміна середовища/limits_file/seed потребує рестарту; керовані API-конфігурації застосовуються через свої PUT-операції.

[Параметри процесу](#параметри-процесу) · [Ліміти](#ліміти) · [Автентифікація](#автентифікація) · [Постійний стан](#постійний-стан)

## Параметри процесу

Усі Settings мають типові значення; умовно обов’язкові параметри зазначено окремо. Джерело — [settings.py](../../../services/llm/src/jane_llm/settings.py), успадковані поля — [JaneSettings](../../../libs/jane-kit/src/jane_kit/config.py) і [AuthSettings](../../../libs/jane-kit/src/jane_kit/auth.py). Наприклад, `port` відповідає `JANE_LLM_PORT`.

| Поле | Тип | Default | Обов’язковість | Допустиме / вплив |
|---|---|---|---|---|
| `auth_mode` | `enum` | `"none"` | ні | Режим серверної перевірки Bearer: none, api_key або jwt; none, api_key, jwt |
| `auth_none_allow_remote` | `bool` | `false` | ні | Дозволити none поза loopback; явно ризикована операторська політика |
| `api_keys` | `list[dict[str, Any]]` | `[]` | ні | Список конфігурацій ключів і scopes; секрети через refs |
| `api_keys_file` | `Path \| None` | `null` | ні | Файл конфігурацій ключів |
| `jwt_jwks_url` | `str \| None` | `null` | так при auth_mode=jwt | URL набору публічних JWT ключів |
| `jwt_issuer` | `str \| None` | `null` | за JWT політикою | Очікуваний issuer JWT |
| `jwt_audience` | `str \| None` | `null` | за JWT політикою | Очікувана audience JWT |
| `jwt_algorithms` | `list[str]` | `["RS256", "ES256"]` | ні | Дозволені алгоритми JWT |
| `jwt_scope_claim` | `str` | `"scope"` | ні | Claim з переліком scopes |
| `jwt_leeway_seconds` | `int` | `30` | ні | Допуск часових claims JWT; ≥ 0; ≤ 600 |
| `jwt_jwks_cache_ttl_seconds` | `int` | `300` | ні | TTL кешу JWKS; ≥ 1 |
| `jwt_jwks_timeout_ms` | `int` | `5000` | ні | Timeout завантаження JWKS; ≥ 1 |
| `jwt_jwks_refresh_cooldown_seconds` | `int` | `10` | ні | Мінімальна пауза повторного refresh JWKS; ≥ 0 |
| `jwt_jwks_max_bytes` | `int` | `1048576` | ні | Максимальний JWKS документ; ≥ 1024 |
| `auth_max_token_bytes` | `int` | `16384` | ні | Максимальний bearer token; ≥ 256 |
| `metrics_public` | `bool` | `true` | ні | Доступність metrics без auth |
| `service_name` | `str` | `"llm"` | ні | Назва в info й логах |
| `instance_id` | `str` | `hostname + UUID` | ні | Унікальний власник процесу й leases |
| `host` | `str` | `"127.0.0.1"` | ні | Адреса прослуховування |
| `port` | `int` | `8110` | ні | HTTP порт |
| `log_level` | `str` | `"INFO"` | ні | Рівень журналу |
| `log_format` | `enum` | `"json"` | ні | Формат json або console; json, console |
| `metrics_enabled` | `bool` | `true` | ні | Увімкнути /metrics |
| `health_check_timeout_ms` | `int` | `2000` | ні | Timeout однієї health-перевірки; ≥ 1 |
| `limits_file` | `Path \| None` | `null` | ні | Профіль лімітів TOML/JSON/YAML |
| `store` | `enum` | `"postgres"` | ні | postgres для постійного стану або memory для одного процесу; postgres, memory |
| `database_url` | `str \| None` | `null` | так при store=postgres | DSN власного PostgreSQL стану |
| `db_schema` | `str` | `"llm"` | ні | Власна PostgreSQL схема; regex ^[a-z_][a-z0-9_]{0,62}$ |
| `seed_file` | `Path \| None` | `null` | ні | YAML/JSON початкових providers, aliases, connections, budgets |
| `fake_provider_enabled` | `bool` | `true` | ні | Створити fake provider і alias default |
| `packages_dir` | `Path \| None` | `null` | ні | Корінь розпакованих LLM-пакетів |
| `registry_url` | `str \| None` | `null` | ні | Base URL Registry для нелокальних пакетів |
| `registry_token` | `SecretStr \| None` | `null` | ні | Власний bearer token до Registry; тільки середовище |
| `db_pool_min_size` | `int` | `1` | ні | Найменша кількість PostgreSQL connections процесу; ≥ 0 |
| `db_pool_max_size` | `int` | `10` | ні | Найбільша кількість PostgreSQL connections процесу; ≥ 1 |
| `secret_env_prefix` | `str` | `"JANE_SECRET_"` | ні | Дозволений префікс env secret refs |
| `secret_files_dir` | `Path \| None` | `"\\run\\secrets"` | ні | Дозволений корінь file secret refs |
| `provider_api_base_allowlist` | `list[str]` | `["https://api.anthropic.com"]` | ні | Дозволені API origins для provider connection |
| `blob_roots` | `list[Path]` | `[]` | ні | Дозволені file ContentRef каталоги |
| `download_host_allowlist` | `list[str]` | `[]` | ні | Дозволені hosts ContentRef download_url |

## Ліміти

Порядок: default моделі → platform file (`defaults`) → env процесу → дозволений request layer. У композиції Orchestrator передає вже resolved source/task/stage значення; сервіс не читає їх із чужої бази. Поле, пропущене в шарі, успадковується; `null` не є способом успадкування. Hard caps застосовуються після merge через мінімум; нижчий рівень може тільки посилити cap. Типові значення й контрактні caps видно у `/v1/info`; внутрішні групи не додаються до strict контракту Limits.

Всі leaf-поля нижче необов’язкові в override, мають default та успадкування за цим порядком. Числові одиниці задані суфіксом: `_ms`, `_seconds`, `_bytes`; суфікс `_chars` означає символи, `_tokens` — токени. Невідоме поле викликає LimitError. Профіль може містити чужі відомі контрактні ліміти: вони обліковуються як ignored; помилки назв не ігноруються.

### llm

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `llm.max_requests_per_minute` | `int` | `60` | ≥ 1 | Виклики моделі на хвилину |
| `llm.max_input_tokens_per_request` | `int` | `100000` | ≥ 1 | Вхідні токени одного виклику |
| `llm.max_output_tokens_per_request` | `int` | `4096` | ≥ 1 | Вихідні токени одного виклику |
| `llm.budget.amount` | `float` | `10.0` | ≥ 0 | Ліміт вартості |
| `llm.budget.currency` | `str` | `"USD"` | regex ^[A-Z]{3}$ | Код валюти бюджету |
| `llm.budget.period` | `enum` | `"day"` | run, day, week, month, total | Вікно бюджету |

### gateway

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `gateway.default_max_output_tokens` | `int` | `1024` | ≥ 1 | Токени відповіді без значення в запиті/пакеті |
| `gateway.max_schema_retries` | `int` | `1` | ≥ 0 | Повторні генерації після невідповідності output schema |
| `gateway.chars_per_token_estimate` | `float` | `2.0` | > 0 | Символів на токен для резервування бюджету |
| `gateway.reservation_ttl_seconds` | `int` | `900` | ≥ 1 | Після TTL зависле резервування списується за оцінкою |
| `gateway.max_data_part_bytes` | `int` | `2000000` | ≥ 1 | Розмір одного data part |
| `gateway.content_fetch_timeout_ms` | `int` | `30000` | ≥ 1 | Весь download ContentRef |
| `gateway.max_package_bytes` | `int` | `20000000` | ≥ 1 | Стиснений і розпакований розмір LLM-пакета |
| `gateway.max_package_files` | `int` | `1000` | ≥ 1 | Файли LLM-пакета |

### fake

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `fake.max_delay_ms` | `int` | `30000` | ≥ 0 | Гранична штучна затримка fake; 0 вимикає |

### provider

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `provider.connect_timeout_ms` | `int` | `5000` | ≥ 1 | Час встановлення з’єднання |
| `provider.request_timeout_ms` | `int` | `120000` | ≥ 1 | Час одного HTTP/адаптерного запиту відповідної групи |
| `provider.retries.max_attempts` | `int` | `4` | ≥ 1 | Кількість спроб разом із першою |
| `provider.retries.initial_backoff_ms` | `int` | `200` | ≥ 0 | Початкова пауза повтору |
| `provider.retries.max_backoff_ms` | `int` | `10000` | ≥ 0 | Найбільша пауза повтору |
| `provider.retries.backoff_multiplier` | `float` | `2.0` | ≥ 1 | Множник exponential backoff |
| `provider.retries.jitter` | `bool` | `true` | Тип поля | Випадкове скорочення паузи повтору |

### registry

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `registry.connect_timeout_ms` | `int` | `5000` | ≥ 1 | Час встановлення з’єднання |
| `registry.request_timeout_ms` | `int` | `30000` | ≥ 1 | Час одного HTTP/адаптерного запиту відповідної групи |
| `registry.max_attempts` | `int` | `3` | ≥ 1 | Кількість спроб разом із першою |

### jobs

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `jobs.max_concurrent_jobs` | `int` | `4` | ≥ 1 | Паралельні jobs процесу |
| `jobs.max_queued_jobs` | `int` | `1000` | ≥ 0 | Черга jobs |
| `jobs.job_timeout_ms` | `int` | `3600000` | ≥ 1 | Граничний час job |
| `jobs.job_retention_seconds` | `int` | `86400` | ≥ 60 | Зберігання завершених jobs |
| `jobs.queue_full_retry_after_seconds` | `int` | `1` | ≥ 0 | Retry-After при заповненій черзі |

### idempotency

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `idempotency.idempotency_ttl_seconds` | `int` | `86400` | ≥ 60 | TTL відповіді за Idempotency-Key |
| `idempotency.in_memory_max_entries` | `int` | `10000` | ≥ 1 | Місткість memory кешу ідемпотентності |

### state

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `state.in_progress_lease_ms` | `int` | `900000` | ≥ 1000 | Lease незавершеного Idempotency claim |
| `state.heartbeat_interval_ms` | `int` | `15000` | ≥ 100 | Інтервал продовження leases |
| `state.job_lease_ms` | `int` | `60000` | ≥ 1000 | Після прострочення job lease власник вважається втраченим |

Приклад override та cap у `.env.llm.local`:

```ini
JANE_LLM_LIMITS__JOBS__MAX_CONCURRENT_JOBS=2
JANE_LLM_LIMITS__HARD_CAPS__JOBS__MAX_CONCURRENT_JOBS=4
```

## Автентифікація

`none` за замовчуванням обмежує віддалені записи loopback-політикою. Для мережевого доступу застосуйте `api_key` або `jwt` та scopes відповідних [API](reference/api/README.md). Для api_key потрібна конфігурація ключів із refs; для JWT — JWKS та issuer/audience за політикою. `/v1/health` публічний; `/metrics` визначає metrics_public. Не передавайте bearer token сусіда як клієнтський ключ свого API.

Секрети в connections — лише `secret_refs`; env/file refs мають дозволені оператором корені. Підтримку конкретного виду ref визначає resolver; наявність `vault:` у загальній схемі не означає налаштований Vault transport цього процесу.

## Постійний стан

Default `store=postgres` вимагає database_url. db_schema — власна схема; вона не надає доступу до таблиць сусідніх сервісів. Під час open створюються/оновлюються власні таблиці та Jane Kit jobs/idempotency state. Пароль DSN передавайте секретом середовища; не зберігайте його в seed або репозиторії. `store=memory` утрачає весь state після рестарту й не підходить для спільних бюджетів кількох процесів.

Seed створює тільки відсутні записи; перезапуск не перезаписує керовані API provider/alias/budget зміни. packages_dir без значення використовує вбудований каталог, якщо він доступний.

## Ліміти провайдера

`provider.request_timeout_ms=120000` визначає generation timeout. Shared `timeouts.connect_timeout_ms` і `retries` мапуються у provider, але shared `timeouts.request_timeout_ms` не замінює generation timeout. Registry має власну групу registry. `gateway.max_schema_retries` додає нові платні виклики після schema validation, тому клієнтський timeout і budget повинні це враховувати.

Stored budget definitions для platform/source/task поєднуються з переданим LlmLimits запиту й provider limits. Бюджети резервуються до HTTP виклику; lease TTL і reservation TTL мають узгоджуватися з найгіршим часом provider attempts/schema retries. Expired reservation списується за оцінкою, а не повертається автоматично як нульова вартість.
