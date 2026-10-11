# assistant: конфігурація

Параметри процесу читаються під час старту з `JANE_ASSISTANT_`. Для вкладених лімітів використовуйте `JANE_ASSISTANT_LIMITS__<GROUP>__<FIELD>`; назви в таблицях — шляхи моделей. Списки у середовищі передавайте JSON-масивами. Зміна середовища/limits_file/seed потребує рестарту; керовані API-конфігурації застосовуються через свої PUT-операції.

[Параметри процесу](#параметри-процесу) · [Ліміти](#ліміти) · [Автентифікація](#автентифікація) · [Постійний стан](#постійний-стан)

## Параметри процесу

Усі Settings мають типові значення; умовно обов’язкові параметри зазначено окремо. Джерело — [settings.py](../../../services/assistant/src/jane_assistant/settings.py), успадковані поля — [JaneSettings](../../../libs/jane-kit/src/jane_kit/config.py) і [AuthSettings](../../../libs/jane-kit/src/jane_kit/auth.py). Наприклад, `port` відповідає `JANE_ASSISTANT_PORT`.

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
| `service_name` | `str` | `"assistant"` | ні | Назва в info й логах |
| `instance_id` | `str` | `hostname + UUID` | ні | Унікальний власник процесу й leases |
| `host` | `str` | `"127.0.0.1"` | ні | Адреса прослуховування |
| `port` | `int` | `8000` | ні | HTTP порт |
| `log_level` | `str` | `"INFO"` | ні | Рівень журналу |
| `log_format` | `enum` | `"json"` | ні | Формат json або console; json, console |
| `metrics_enabled` | `bool` | `true` | ні | Увімкнути /metrics |
| `health_check_timeout_ms` | `int` | `2000` | ні | Timeout однієї health-перевірки; ≥ 1 |
| `limits_file` | `Path \| None` | `null` | ні | Профіль лімітів TOML/JSON/YAML |
| `state_dsn` | `SecretStr \| None` | `null` | ні | DSN власного Assistant стану; без нього memory |
| `state_schema` | `str` | `"jane_assistant"` | ні | Власна схема Assistant; regex ^[a-z_][a-z0-9_]{0,62}$ |
| `llm_url` | `str \| None` | `null` | ні | Base URL LLM API |
| `registry_url` | `str \| None` | `null` | ні | Base URL Registry для нелокальних пакетів |
| `collector_web_url` | `str \| None` | `null` | ні | Base URL Web Collector API |
| `collector_telegram_url` | `str \| None` | `null` | ні | Base URL Telegram Collector API |
| `handler_runtime_url` | `str \| None` | `null` | ні | Base URL Handler Runtime API |
| `orchestrator_url` | `str \| None` | `null` | ні | Base URL Orchestrator API |
| `storage_url` | `str \| None` | `null` | ні | Base URL Storage API |
| `service_token_ref` | `str \| None` | `null` | ні | Спільний bearer ref для сусідів без окремого ref |
| `llm_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref LLM |
| `registry_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref Registry |
| `collector_web_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref Web Collector |
| `collector_telegram_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref Telegram Collector |
| `handler_runtime_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref Handler Runtime |
| `orchestrator_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref Orchestrator |
| `storage_token_ref` | `str \| None` | `null` | ні | Окремий bearer ref Storage |
| `service_token_env` | `str \| None` | `null` | ні | Застаріла назва env зі спільним token; замініть service_token_ref |
| `search_provider` | `enum` | `"none"` | ні | none, static або http_json; none, static, http_json |
| `search_static_file` | `Path \| None` | `null` | так при search_provider=static | JSON-файл пошукових кандидатів |
| `search_url_template` | `str \| None` | `null` | так при search_provider=http_json | HTTP URL із {query} |
| `search_items_path` | `str` | `"results"` | ні | Шлях до масиву результатів HTTP пошуку |
| `search_title_field` | `str` | `"title"` | ні | Поле назви пошукового кандидата |
| `search_url_field` | `str` | `"url"` | ні | Поле URL пошукового кандидата |
| `search_description_field` | `str` | `"description"` | ні | Поле опису пошукового кандидата |
| `blob_roots` | `list[Path]` | `[]` | ні | Дозволені file ContentRef каталоги |
| `download_host_allowlist` | `list[str]` | `[]` | ні | Дозволені hosts ContentRef download_url |
| `contracts_dir` | `Path \| None` | `null` | ні | Корінь contracts/schemas для локальної перевірки |
| `default_storage_package` | `str \| None` | `null` | ні | package_id@version для storage stage у task draft |
| `default_storage_connection` | `str \| None` | `null` | ні | Binding storage stage у task draft |
| `llm_model_cheap` | `str` | `"cheap"` | ні | Alias класифікаційної моделі |
| `llm_model_strong` | `str` | `"strong"` | ні | Alias моделі аналізу й генерації коду |
| `llm_completion_mode` | `enum` | `"sync"` | ні | sync або async очікування LLM gateway; sync, async |
| `generated_code_allowed_modules` | `list[str]` | `["re", "html", "json", "math", "datetime", "decimal", "string", "unicodedata", "itertools", "functools", "collections", "typing", "dataclasses"]` | ні | Дозволені imports generated Python коду до sandbox |
| `onboarding_allow_activation` | `bool` | `true` | ні | Дозволити acceptProposal із activate=true |

## Ліміти

Порядок: default моделі → platform file (`defaults`) → env процесу → дозволений request layer. У композиції Orchestrator передає вже resolved source/task/stage значення; сервіс не читає їх із чужої бази. Поле, пропущене в шарі, успадковується; `null` не є способом успадкування. Hard caps застосовуються після merge через мінімум; нижчий рівень може тільки посилити cap. Типові значення й контрактні caps видно у `/v1/info`; внутрішні групи не додаються до strict контракту Limits.

Всі leaf-поля нижче необов’язкові в override, мають default та успадкування за цим порядком. Числові одиниці задані суфіксом: `_ms`, `_seconds`, `_bytes`; суфікс `_chars` означає символи, `_tokens` — токени. Невідоме поле викликає LimitError. Профіль може містити чужі відомі контрактні ліміти: вони обліковуються як ignored; помилки назв не ігноруються.

### state

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `state.pool_max_size` | `int` | `10` | ≥ 1 | Максимальний connection pool |
| `state.connect_timeout_ms` | `int` | `10000` | ≥ 1 | Час встановлення з’єднання |
| `state.in_progress_lease_ms` | `int` | `900000` | ≥ 1 | Lease незавершеного Idempotency claim |
| `state.job_lease_ms` | `int` | `60000` | ≥ 1 | Після прострочення job lease власник вважається втраченим |
| `state.heartbeat_interval_ms` | `int` | `15000` | ≥ 1 | Інтервал продовження leases |
| `state.session_retention_seconds` | `int` | `2592000` | ≥ 60 | TTL неоновленої onboarding-сесії |

### llm

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `llm.max_requests_per_minute` | `int` | `30` | ≥ 1 | Виклики моделі на хвилину |
| `llm.max_input_tokens_per_request` | `int` | `16000` | ≥ 1 | Вхідні токени одного виклику |
| `llm.max_output_tokens_per_request` | `int` | `8000` | ≥ 1 | Вихідні токени одного виклику |
| `llm.budget.amount` | `float` | `2.0` | ≥ 0 | Ліміт вартості |
| `llm.budget.currency` | `str` | `"USD"` | regex ^[A-Z]{3}$ | Код валюти бюджету |
| `llm.budget.period` | `enum` | `"run"` | run, day, week, month, total | Вікно бюджету |
| `llm.max_improvement_attempts` | `int` | `3` | ≥ 0 | Спроби поліпшення пакета |
| `llm.max_onboarding_samples` | `int` | `60` | ≥ 1 | Зразки adaptive sampling |
| `llm.min_onboarding_confidence` | `float` | `0.8` | > 0; ≤ 1 | Мінімальна впевненість покриття sampling |

### transfer

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `transfer.inline_max_bytes` | `int` | `262144` | ≥ 0 | Поріг inline вмісту |

### onboarding

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `onboarding.min_distinct_types` | `int` | `2` | ≥ 1 | Різні типи матеріалів для раннього завершення sampling |
| `onboarding.sample_batch_size` | `int` | `10` | ≥ 1 | Матеріали на класифікаційний запит |
| `onboarding.max_sample_chars` | `int` | `6000` | ≥ 200 | Символи одного класифікаційного зразка |
| `onboarding.max_example_chars` | `int` | `12000` | ≥ 200 | Символи прикладу для аналізу/генерації |
| `onboarding.min_examples_per_type` | `int` | `2` | ≥ 1 | Зразки для підтвердження типу |
| `onboarding.max_examples_per_type` | `int` | `3` | ≥ 1 | Приклади типу на аналіз |
| `onboarding.max_negative_examples` | `int` | `1` | ≥ 1 | Негативні empty тестові приклади |
| `onboarding.poll_page_factor` | `int` | `3` | ≥ 1 | Множник batch для сторінки sampling pool |
| `onboarding.max_candidates` | `int` | `5` | ≥ 1 | Кандидати джерела для вибору |
| `onboarding.auto_select_confidence` | `float` | `0.8` | > 0; ≤ 1 | Поріг автоматичного вибору джерела |
| `onboarding.auto_select_margin` | `float` | `0.2` | ≥ 0; ≤ 1 | Перевага першого кандидата |
| `onboarding.max_candidate_packages` | `int` | `5` | ≥ 1 | Пакети для перевірки на один тип |
| `onboarding.bind_threshold` | `float` | `0.9` | ≥ 0; ≤ 1 | Частка успішних тестів для прямої прив’язки |
| `onboarding.fork_threshold` | `float` | `0.5` | ≥ 0; ≤ 1 | Частка успішних тестів для форку й адаптації |
| `onboarding.max_generation_attempts` | `int` | `2` | ≥ 1 | Генерації екстрактора до успішних тестів |
| `onboarding.max_proposals` | `int` | `4` | ≥ 1 | Кількість пропозицій onboarding |
| `onboarding.fetch_ratio` | `int` | `3` | ≥ 1 | Множник max_onboarding_samples для fetch колектора |
| `onboarding.collection_poll_wait_ms` | `int` | `1000` | ≥ 0 | Long-poll матеріалів колектора |
| `onboarding.max_empty_polls` | `int` | `30` | ≥ 1 | Порожні polls до завершення очікування |
| `onboarding.requests_overhead_ratio` | `float` | `0.05` | ≥ 0 | Надбавка до оцінки requests/run |
| `onboarding.max_link_patterns` | `int` | `20` | ≥ 0 | Збережені link/pagination patterns |
| `onboarding.link_pattern_examples` | `int` | `2` | ≥ 0 | Посилання-приклади на pattern |
| `onboarding.max_pages_listed` | `int` | `20` | ≥ 1 | Перераховані сторінки на pagination template |
| `onboarding.max_evidence_examples` | `int` | `5` | ≥ 1 | Приклади canonical/URL evidence |
| `onboarding.max_risk_url_chars` | `int` | `200` | ≥ 20 | Символи URL у ризику пропозиції |

### material

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `material.max_fixture_bytes` | `int` | `131072` | ≥ 1024 | HTML fixture після зменшення |
| `material.head_share` | `float` | `0.1` | ≥ 0; ≤ 1 | Частка digest для head tags |
| `material.structured_share` | `float` | `0.6` | ≥ 0; ≤ 1 | Частка digest для структурованих даних |
| `material.text_share` | `float` | `0.15` | ≥ 0; ≤ 1 | Частка digest для видимого тексту |
| `material.max_list_items` | `int` | `3` | ≥ 1 | Елементи довгого structured list у digest |
| `material.max_string_chars` | `int` | `1000` | ≥ 20 | Символи structured string у digest |
| `material.short_string_chars` | `int` | `200` | ≥ 20 | Символи string коли structured share бракує |
| `material.max_head_tags` | `int` | `60` | ≥ 0 | Head tags у digest |
| `material.max_microdata_types` | `int` | `20` | ≥ 0 | Microdata типи у digest |
| `material.max_microdata_props` | `int` | `30` | ≥ 0 | Microdata властивості у digest |

### improvement

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `improvement.max_sample_chars` | `int` | `6000` | ≥ 200 | Символи одного класифікаційного зразка |
| `improvement.max_problem_samples` | `int` | `10` | ≥ 1 | Проблемні зразки для improvement |
| `improvement.max_successful_examples` | `int` | `5` | ≥ 0 | Успішні приклади improvement |
| `improvement.max_file_chars` | `int` | `20000` | ≥ 200 | Символи одного файла пакета для моделі |
| `improvement.max_proposal_bytes` | `int` | `1048576` | ≥ 1024 | Компактний UTF-8 JSON proposal_only |

### unknown

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `unknown.max_sample_chars` | `int` | `6000` | ≥ 200 | Символи одного класифікаційного зразка |
| `unknown.min_confidence` | `float` | `0.6` | ≥ 0; ≤ 1 | Поріг suggestion невідомого матеріалу |

### content

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `content.max_material_bytes` | `int` | `16777216` | ≥ 1 | Розмір прочитаного material ContentRef |
| `content.fetch_timeout_ms` | `int` | `30000` | ≥ 1 | Весь download матеріалу |
| `content.connect_timeout_ms` | `int` | `5000` | ≥ 1 | Час встановлення з’єднання |

### search

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `search.request_timeout_ms` | `int` | `10000` | ≥ 1 | Час одного HTTP/адаптерного запиту відповідної групи |
| `search.connect_timeout_ms` | `int` | `5000` | ≥ 1 | Час встановлення з’єднання |

### clients

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `clients.connect_timeout_ms` | `int` | `5000` | ≥ 1 | Час встановлення з’єднання |
| `clients.request_timeout_ms` | `int` | `30000` | ≥ 1 | Час одного HTTP/адаптерного запиту відповідної групи |
| `clients.retries.max_attempts` | `int` | `4` | ≥ 1 | Кількість спроб разом із першою |
| `clients.retries.initial_backoff_ms` | `int` | `200` | ≥ 0 | Початкова пауза повтору |
| `clients.retries.max_backoff_ms` | `int` | `10000` | ≥ 0 | Найбільша пауза повтору |
| `clients.retries.backoff_multiplier` | `float` | `2.0` | ≥ 1 | Множник exponential backoff |
| `clients.retries.jitter` | `bool` | `true` | Тип поля | Випадкове скорочення паузи повтору |
| `clients.max_connections` | `int` | `20` | ≥ 1 | Паралельні HTTP connections до сусідів |
| `clients.job_poll_interval_ms` | `int` | `1000` | ≥ 1 | Пауза polling jobs сусідів |
| `clients.job_wait_timeout_ms` | `int` | `3600000` | ≥ 1 | Час очікування job сусіда |

### llm_call

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `llm_call.request_timeout_ms` | `int` | `900000` | ≥ 1 | Час одного HTTP/адаптерного запиту відповідної групи |
| `llm_call.chars_per_token` | `float` | `2.0` | > 0 | Оцінка символів на токен для fit prompt |
| `llm_call.prompt_overhead_chars` | `int` | `2000` | ≥ 0 | Резерв prompt preamble |
| `llm_call.part_overhead_chars` | `int` | `150` | ≥ 0 | Резерв delimiters data part |

### pages

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `pages.default_page_size` | `int` | `50` | ≥ 1 | Розмір сторінки без limit |
| `pages.max_page_size` | `int` | `500` | ≥ 1 | Верхня межа limit списків |

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

Приклад override та cap у `.env.assistant.local`:

```ini
JANE_ASSISTANT_LIMITS__JOBS__MAX_CONCURRENT_JOBS=2
JANE_ASSISTANT_LIMITS__HARD_CAPS__JOBS__MAX_CONCURRENT_JOBS=4
```

## Автентифікація

`none` за замовчуванням обмежує віддалені записи loopback-політикою. Для мережевого доступу застосуйте `api_key` або `jwt` та scopes відповідних [API](reference/api/README.md). Для api_key потрібна конфігурація ключів із refs; для JWT — JWKS та issuer/audience за політикою. `/v1/health` публічний; `/metrics` визначає metrics_public. Не передавайте bearer token сусіда як клієнтський ключ свого API.

Секрети в connections — лише `secret_refs`; env/file refs мають дозволені оператором корені. Підтримку конкретного виду ref визначає resolver; наявність `vault:` у загальній схемі не означає налаштований Vault transport цього процесу.

## Постійний стан

Без state_dsn state memory, дані втрачаються з процесом. PostgreSQL зберігає sessions/jobs/idempotency у state_schema; pool/leases/retention керуються state.*. heartbeat_interval_ms тримайте значно нижче job_lease_ms. Рестарт не означає автоматичне поновлення втраченого довгого виклику: прострочена job lease позначає збій.

## Пошук

`search_provider=static` вимагає JSON-масив кандидатів у search_static_file, `http_json` — search_url_template із `{query}`. Шлях items і назви title/url/description задаються окремо. `none` не виконує зовнішній пошук; URL або username запиту може прямо визначити джерело. Недоступний потрібний сусід завершує сценарій upstream_unavailable.

## Обробка матеріалів і LLM

Сума material.head_share + structured_share + text_share не може перевищувати 1. HTML fixture зменшується до max_fixture_bytes; видаляються виконувані script/style/SVG/comments, JSON-LD зберігається цілим доки вміщується. Це зменшений зразок, а не повний оригінал.

`llm_call.request_timeout_ms=900000` відрізняється від clients.request_timeout_ms=30000: синхронна генерація може містити schema retries і provider attempts. `llm_call.chars_per_token` має бути не більшим за gateway.chars_per_token_estimate. При async LLM completion використовується clients.job_poll_interval_ms/job_wait_timeout_ms. Budget period=run передає стабільний session/run ID на всі LLM виклики й locally зупиняє перевищення бюджету.

generated_code_allowed_modules є політикою ранньої перевірки, не sandbox; остаточна ізоляція належить Handler Runtime. onboarding_allow_activation дозволяє activation лише за успішних тестів і налаштованого Orchestrator.
