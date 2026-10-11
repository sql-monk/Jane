# storage: конфігурація

Параметри процесу читаються під час старту з `JANE_STORAGE_`. Для вкладених лімітів використовуйте `JANE_STORAGE_LIMITS__<GROUP>__<FIELD>`; назви в таблицях — шляхи моделей. Списки у середовищі передавайте JSON-масивами. Зміна середовища/limits_file/seed потребує рестарту; керовані API-конфігурації застосовуються через свої PUT-операції.

[Параметри процесу](#параметри-процесу) · [Ліміти](#ліміти) · [Автентифікація](#автентифікація) · [Постійний стан](#постійний-стан)

## Параметри процесу

Усі Settings мають типові значення; умовно обов’язкові параметри зазначено окремо. Джерело — [settings.py](../../../services/storage/src/jane_storage/settings.py), успадковані поля — [JaneSettings](../../../libs/jane-kit/src/jane_kit/config.py) і [AuthSettings](../../../libs/jane-kit/src/jane_kit/auth.py). Наприклад, `port` відповідає `JANE_STORAGE_PORT`.

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
| `service_name` | `str` | `"storage"` | ні | Назва в info й логах |
| `instance_id` | `str` | `hostname + UUID` | ні | Унікальний власник процесу й leases |
| `host` | `str` | `"127.0.0.1"` | ні | Адреса прослуховування |
| `port` | `int` | `8107` | ні | HTTP порт |
| `log_level` | `str` | `"INFO"` | ні | Рівень журналу |
| `log_format` | `enum` | `"json"` | ні | Формат json або console; json, console |
| `metrics_enabled` | `bool` | `true` | ні | Увімкнути /metrics |
| `health_check_timeout_ms` | `int` | `2000` | ні | Timeout однієї health-перевірки; ≥ 1 |
| `limits_file` | `Path \| None` | `null` | ні | Профіль лімітів TOML/JSON/YAML |
| `connections_file` | `Path \| None` | `null` | ні | Початковий JSON/YAML список connections |
| `transit_connection_id` | `str \| None` | `null` | ні | S3/MinIO connection для читання transit blobs |
| `package_dirs` | `list[Path]` | `[]` | ні | Додаткові локальні storage-пакети |
| `validate_requests` | `bool` | `true` | ні | Валідувати запити чинними schemas, коли вони доступні |
| `secret_env_prefix` | `str` | `"JANE_SECRET_"` | ні | Дозволений префікс env secret refs |
| `secret_files_dir` | `Path \| None` | `"\\run\\secrets"` | ні | Дозволений корінь file secret refs |
| `connection_host_allowlist` | `list[str]` | `[]` | ні | Дозволені hostname або hostname:port цільових connections |
| `content_files_dir` | `Path \| None` | `null` | ні | Корінь дозволених file ContentRef |
| `transit_dir` | `Path \| None` | `null` | ні | Каталог власних тимчасових RAW blobs |
| `download_host_allowlist` | `list[str]` | `[]` | ні | Дозволені hosts ContentRef download_url |
| `registry_url` | `str \| None` | `null` | ні | Base URL Registry для нелокальних пакетів |
| `registry_token` | `SecretStr \| None` | `null` | ні | Власний bearer token до Registry; тільки середовище |

## Ліміти

Порядок: default моделі → platform file (`defaults`) → env процесу → дозволений request layer. У композиції Orchestrator передає вже resolved source/task/stage значення; сервіс не читає їх із чужої бази. Поле, пропущене в шарі, успадковується; `null` не є способом успадкування. Hard caps застосовуються після merge через мінімум; нижчий рівень може тільки посилити cap. Типові значення й контрактні caps видно у `/v1/info`; внутрішні групи не додаються до strict контракту Limits.

Всі leaf-поля нижче необов’язкові в override, мають default та успадкування за цим порядком. Числові одиниці задані суфіксом: `_ms`, `_seconds`, `_bytes`; суфікс `_chars` означає символи, `_tokens` — токени. Невідоме поле викликає LimitError. Профіль може містити чужі відомі контрактні ліміти: вони обліковуються як ignored; помилки назв не ігноруються.

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

### conflict_retries

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `conflict_retries.max_attempts` | `int` | `4` | ≥ 1 | Кількість спроб разом із першою |
| `conflict_retries.initial_backoff_ms` | `int` | `200` | ≥ 0 | Початкова пауза повтору |
| `conflict_retries.max_backoff_ms` | `int` | `10000` | ≥ 0 | Найбільша пауза повтору |
| `conflict_retries.backoff_multiplier` | `float` | `2.0` | ≥ 1 | Множник exponential backoff |
| `conflict_retries.jitter` | `bool` | `true` | Тип поля | Випадкове скорочення паузи повтору |

### timeouts

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `timeouts.sync_response_max_ms` | `int` | `30000` | ≥ 1 | Після цього sync виклик переходить у 202 Job |
| `timeouts.request_timeout_ms` | `int` | `30000` | ≥ 1 | Час одного HTTP/адаптерного запиту відповідної групи |

### transfer

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `transfer.max_request_body_bytes` | `int` | `16777216` | ≥ 1 | Граничне тіло HTTP запиту |
| `transfer.inline_max_bytes` | `int` | `1048576` | ≥ 0 | Поріг inline вмісту |
| `transfer.transit_ttl_seconds` | `int` | `604800` | ≥ 60 | TTL transit blobs |
| `transfer.transit_cleanup_interval_seconds` | `int` | `600` | ≥ 1 | Частота видалення власних прострочених transit blobs |

### objects

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `objects.max_object_bytes` | `int` | `104857600` | ≥ 1 | Розмір одного RAW або result document |
| `objects.max_filter_material_ids` | `int` | `200` | ≥ 1 | Кількість material IDs у фільтрі objects |

### adapters

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `adapters.lock_timeout_ms` | `int` | `30000` | ≥ 1 | Час очікування блокування filesystem |
| `adapters.lock_stale_ms` | `int` | `120000` | ≥ 1 | Строк прострочення filesystem lock |
| `adapters.lock_poll_ms` | `int` | `10` | ≥ 1 | Пауза перевірки filesystem lock |
| `adapters.replace_retry_ms` | `int` | `5000` | ≥ 0 | Вікно повтору атомарної заміни файла |
| `adapters.pool_min_size` | `int` | `1` | ≥ 0 | Мінімальний connection pool адаптера |
| `adapters.pool_max_size` | `int` | `10` | ≥ 1 | Максимальний connection pool |
| `adapters.connect_timeout_ms` | `int` | `10000` | ≥ 1 | Час встановлення з’єднання |
| `adapters.command_timeout_ms` | `int` | `30000` | ≥ 1 | Час команди адаптера |
| `adapters.chunk_bytes` | `int \| None` | `null` | ≥ 1 | Типовий RAW chunk MongoDB; connection має пріоритет |
| `adapters.retry_max_attempts` | `int \| None` | `null` | ≥ 1 | Типові S3/MinIO attempts; connection має пріоритет |

### pages

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `pages.default_page_size` | `int` | `50` | ≥ 1 | Розмір сторінки без limit |
| `pages.max_page_size` | `int` | `500` | ≥ 1 | Верхня межа limit списків |

### invocations

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `invocations.max_results_in_memory` | `int` | `10000` | ≥ 1 | Недавні результати invocation на процес |

### packages

| Шлях | Тип | Default | Межі | Вплив |
|---|---|---|---|---|
| `packages.max_archive_bytes` | `int` | `20971520` | ≥ 1 | Стиснений архів пакета |
| `packages.max_unpacked_bytes` | `int` | `52428800` | ≥ 1 | Сума розпакованих файлів |
| `packages.max_files` | `int` | `2000` | ≥ 1 | Кількість файлів архіву |
| `packages.cache_max_entries` | `int` | `128` | ≥ 1 | LRU кеш Registry пакетів на процес |
| `packages.registry_connect_timeout_ms` | `int` | `5000` | ≥ 1 | Час connect до Registry |
| `packages.registry_request_timeout_ms` | `int` | `30000` | ≥ 1 | Весь download архіву з Registry |

Приклад override та cap у `.env.storage.local`:

```ini
JANE_STORAGE_LIMITS__JOBS__MAX_CONCURRENT_JOBS=2
JANE_STORAGE_LIMITS__HARD_CAPS__JOBS__MAX_CONCURRENT_JOBS=4
```

## Автентифікація

`none` за замовчуванням обмежує віддалені записи loopback-політикою. Для мережевого доступу застосуйте `api_key` або `jwt` та scopes відповідних [API](reference/api/README.md). Для api_key потрібна конфігурація ключів із refs; для JWT — JWKS та issuer/audience за політикою. `/v1/health` публічний; `/metrics` визначає metrics_public. Не передавайте bearer token сусіда як клієнтський ключ свого API.

Секрети в connections — лише `secret_refs`; env/file refs мають дозволені оператором корені. Підтримку конкретного виду ref визначає resolver; наявність `vault:` у загальній схемі не означає налаштований Vault transport цього процесу.

## Постійний стан

Storage не має окремого settings DSN для власних jobs: process state memory. Постійні RAW, entity state/history і delivery records зберігає цільовий адаптер. Connection із мережевим адресом потребує непорожнього connection_host_allowlist; секретні env-поля обмежено secret_env_prefix. Порожній рядок secret_files_dir/content_files_dir/transit_dir вимикає відповідний filesystem transport.

## Політики адаптерів

`adapters.chunk_bytes` і `adapters.retry_max_attempts` застосовуються лише за відсутності відповідного connection.params. Інші service adapter options перекривають connection params. MongoDB chunk без override — 4 MiB, адаптер відхиляє понад 15 MiB; S3/MinIO retry_max_attempts без override — 3. Розміри — байти, не мегабайти у рядку.

`conflict_retries` повторює optimistic commit усередині Storage. Контрактний `retries` належить HTTP-клієнту і не керує цим циклом. Старий власний env `LIMITS__RETRIES__*` залишається deprecated alias conflict_retries з warning; shared platform retries не переноситься.

Якщо адаптер не має persistent URI, RAW до inline_max_bytes повертається inline. Для більшого RAW material потребує transit_dir; без нього object metadata доступні, але material може бути відсутній. Transit видаляє тільки власний cleanup процесу після transit_ttl_seconds; consumers повинні мати дозволений відповідний root.
