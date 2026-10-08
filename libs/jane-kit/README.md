# jane-kit

Спільна бібліотека сервісів Jane. Дає однакову поведінку всім сервісам і реалізує конвенції контрактів
WP-00 (скіл `jane-contracts`): модель помилок, ідемпотентність, асинхронні job, health/info, ліміти з
успадкуванням, курсорна пагінація, `traceparent`, контрактні тести й моки, генерація клієнтів.

Підключення в сервісі (uv workspace):

```toml
[project]
dependencies = ["jane-kit"]

[tool.uv.sources]
jane-kit = { workspace = true }
```

`JaneSettings.instance_id` за замовчуванням має вигляд `hostname-pid-<uuid>` і створюється окремо для
кожного запуску процесу. Власник оренди після рестарту контейнера мусить відрізнятися, навіть коли
hostname і PID збігаються. Явний `<ПРЕФІКС>INSTANCE_ID` лишається можливим; його значення має бути
унікальним для кожного запуску екземпляра.

## Модулі

| Модуль | Що дає | Контракт WP-00 |
|---|---|---|
| `jane_kit.config` | `Limits` (кожне поле з безпечним типовим значенням, інакше `TypeError`); `resolve_limits(model, *layers)` — злиття platform → source → task → stage → request, `hard_caps`, `effective()` у формі `EffectiveLimits`, `platform_limits()` у формі `PlatformLimits` (лише поля, позначені `contract_field`); `load_layer` (`PlatformLimits` у TOML/JSON/YAML), `layer_from_env`; `JaneSettings` | `schemas/common/limits.schema.json` |
| `jane_kit.errors` | `Problem`, `FieldError`, `JaneError(code=...)` і підкласи; статус і `retryable` — з каталогу `KNOWN_CODES`; обробники FastAPI (404/405/422/500 теж Problem) | `schemas/common/problem.schema.json`, `docs/errors.md` |
| `jane_kit.idempotency` | `Idempotency-Key`: повтор → збережена відповідь і `Idempotency-Replayed: true`, інше тіло → 422 `idempotency_key_reused`, паралельно → 409 `idempotency_in_progress`; протокол сховища | `common.yaml` `IdempotencyKey` |
| `jane_kit.jobs` | `202` + `Job` + `Location`; `queued/running/cancelling/succeeded/failed/cancelled`; прогрес, скасування (202 / 200 для завершених); ліміти паралельності, черги, тайм-ауту, зберігання | `schemas/common/job.schema.json`, `common.yaml` `Job`/`JobCancel` |
| `jane_kit.health` | `GET /v1/health` (`ok`/`degraded`/`down`, 503 для down), `GET /v1/info` (`ServiceInfo` з `limits` = `PlatformLimits` сервісу, якщо `create_app(limits=...)`); тайм-аут перевірок — `JaneSettings.health_check_timeout_ms` | `common.yaml` `Health`/`Info` |
| `jane_kit.pagination` | `Page[T]` (`items`, `next_cursor`), `clamp_limit`, непрозорі курсори | конвенція пагінації |
| `jane_kit.tracing` | `traceparent` (W3C): продовження траси, `trace_id` у журналах і Problem | конвенція простежуваності |
| `jane_kit.logs` | JSON-журнали в stdout, `bind_context(trace_id=..., job_id=...)` через `contextvars` | — |
| `jane_kit.metrics` | `Metrics` з окремим реєстром на застосунок, `/metrics`, HTTP-метрики за шаблоном маршруту | — |
| `jane_kit.content` | `ContentReader` — читання `ContentRef` за явною політикою: `inline` (utf-8/base64); `download_url` лише `http(s)` на хости з allowlist (`hostname` / `hostname:port`, типово порожньо — вимкнено; хост звіряється в ASCII-формі, з якою йде з'єднання, тож IDN дозволяється записом у punycode `xn--…`, а URL з не-ASCII символами відхиляється), без редиректів, `trust_env=False`, лише `Content-Encoding: identity`, ліміт розміру під час потоку й тайм-аут усього завантаження; `file://` лише строго всередині коренів (типово немає — вимкнено), шлях спершу розв'язується (`..`, symlink) і читається розв'язаний звичайний файл; перевірка `size_bytes` blob і `sha256`; помилки — `JaneError` (422 `validation_failed` / `limit_exceeded`, 404, 502) без шляхів і вмісту; `parse_host_allowlist` — перевірка налаштування на старті. Налаштування сервісу: `<ПРЕФІКС>BLOB_ROOTS`, `<ПРЕФІКС>DOWNLOAD_HOST_ALLOWLIST`; ліміти розміру й тайм-аут — з лімітів сервісу | `schemas/common/content-ref.schema.json`, ADR-0004 |
| `jane_kit.clients` | `ServiceClient` (httpx): `timeouts.*_ms` і `RetryPolicy` з конфігурації, повтор лише для безпечних методів або з `Idempotency-Key` і лише retryable-помилок, `Retry-After`, `traceparent`, `wait_for_job` | `RetryPolicy` у limits |
| `jane_kit.contracts` | `OpenAPISpec` (OpenAPI 3.1, `$ref` між файлами, `$ref` на path items), `ContractClient` — перевіряє кожну відповідь справжнього сервісу, `build_mock_app` — мок сусіда з прикладів контракту, `contracts_dir()`, `find_specs()` | `contracts/openapi/*.v1.yaml` |
| `jane_kit.codegen` | `uv run jane-codegen client <spec> --out <pkg>/_generated/<svc>` — моделі Pydantic (datamodel-code-generator) + асинхронний клієнт на `ServiceClient` | — |
| `jane_kit.auth` | автентифікація й scopes за ADR-0005: `none` / `api_key` / `jwt`, middleware (401) і залежність авторизації маршруту (403), `resolve_secret_ref` (`env:`/`file:`), `bearer_header` — див. «Автентифікація» | `common.yaml` `bearerAuth`, `Unauthenticated`, `Forbidden` |
| `jane_kit.auth_scopes` | scope кожної операції кожного контракту (`COLLECTOR`, `HANDLER`, `STORAGE`, `LLM`, `ASSISTANT`, `REGISTRY`, `ORCHESTRATOR`), `merge()` для сервісу з кількома API | `contracts/openapi/*.v1.yaml` |
| `jane_kit.service` | `create_app(settings, capabilities=..., auth_scopes=...)` — FastAPI з усім вищенаведеним; `run()` — uvicorn | — |
| `jane_kit.devstack` | `load_stack()` — порти й облікові дані стеку `just up` (для інтеграційних тестів); `new_api_keys()` — ключі API стеків | — |

`ServiceClient` повторює `httpx.ReadError` (зокрема закрите сервером простоюване з'єднання) лише для
безпечного методу або запиту з `Idempotency-Key`, з тими самими тілом і ключем та в межах
`RetryPolicy.max_attempts`. POST без ключа повертає помилку без повтору.

## Автентифікація (ADR-0005)

Один модуль для всіх сервісів: `create_app` вмикає перевірку сам, сервіс лише передає таблицю scopes своїх
операцій (`auth_scopes=merge(HANDLER, STORAGE)` тощо з `jane_kit.auth_scopes`; таблиці дорівнюють контрактам —
`tests/test_auth_scopes.py`). Без таблиці (`auth_scopes=None`) лишається лише автентифікація, а scopes
перевіряють обробники (`Depends(require("x:y"))`, `principal_of(request)`).

| Налаштування (env `<PREFIX><НАЗВА>`) | Типово | Значення |
|---|---|---|
| `AUTH_MODE` | `none` | `none` — лише локальні тести: усі мають усі scopes, попередження в журналі, `HOST` не loopback → сервіс не стартує (крім `AUTH_NONE_ALLOW_REMOTE=true`); `api_key` — типовий для dev-стеку; `jwt` — для прод |
| `API_KEYS` | `[]` | JSON `[{"name", "scopes": [...], "sha256": "<hex ключа>"}]` або замість `sha256` — `"secret_ref": "env:VAR"` / `"file:/run/secrets/x"` (розв'язується один раз на старті, зберігається лише хеш); інші поля (напр. `actor` у registry) — атрибути принципала |
| `API_KEYS_FILE` | — | JSON/YAML із тим самим списком (додається до `API_KEYS`) |
| `JWT_JWKS_URL` / `JWT_ISSUER` / `JWT_AUDIENCE` | — | обов'язкові для `jwt`; JWKS лише `https://` (http — тільки loopback) |
| `JWT_ALGORITHMS` | `["RS256","ES256"]` | підмножина RS*/PS*/ES*; `none` і `HS*` заборонені конфігурацією |
| `JWT_SCOPE_CLAIM` | `scope` | рядок через пробіл або список рядків |
| `JWT_LEEWAY_SECONDS` | 30 | допуск годинника для `exp`/`nbf`/`iat` |
| `JWT_JWKS_CACHE_TTL_SECONDS` / `JWT_JWKS_TIMEOUT_MS` | 300 / 5000 | кеш JWKS і тайм-аут одного запиту до IdP |
| `JWT_JWKS_REFRESH_COOLDOWN_SECONDS` / `JWT_JWKS_MAX_BYTES` | 10 / 1048576 | невідомий `kid` оновлює JWKS один раз, не частіше; найбільший JWKS |
| `AUTH_MAX_TOKEN_BYTES` | 16384 | довший токен — 401 без розбору |
| `METRICS_PUBLIC` | `true` | `/metrics` без токена (скрейпер Prometheus у внутрішній мережі); `false` — будь-який дійсний токен |

Поведінка: `/v1/health` — завжди без токена; `/v1/info` (контракт `common.yaml` Info: `bearerAuth`, 401),
`/openapi.json`, `/docs` — будь-який дійсний токен без scope; решта — токен (401 `unauthenticated`,
`WWW-Authenticate: Bearer`) і scope операції (403 `forbidden`, `detail: scope x:y required`), обидва у форматі
`application/problem+json`. Операція без рядка в таблиці — 403 і помилка в журналі, а на старті — відмова
стартувати. JWT: `iss`/`aud`/`exp` обов'язкові, `nbf` перевіряється, ключ за `kid` (без `kid` — лише якщо в JWKS
один ключ), алгоритм заголовка має збігатися з ключем; недоступний IdP без ключів у кеші — 503
`service_unavailable`, а не 401. Неповна конфігурація (`api_key` без ключів, `jwt` без URL/issuer/audience,
нерозв'язне `secret_ref`) — `AuthConfigError` під час `create_app`, сервіс не стартує. Значення ключів не
потрапляють у журнали й повідомлення про помилки; на старті журналюються лише режим та імена ключів.

Вихідні виклики: сервіс викликає сусідів **власним** токеном (ADR-0005 §5); `resolve_secret_ref` і
`bearer_header` — спільні помічники (налаштування — у README кожного сервісу).

## Ліміти

Числові ліміти не зашиваються в код (plan.md §3.6). Сервіс описує модель з назвами полів контракту:

```python
class Crawl(Limits):
    max_depth: int = Field(default=3, ge=0)


class CollectorLimits(Limits):
    crawl: Crawl = Crawl()


resolved = resolve_limits(
    CollectorLimits,
    *settings.platform_layers("JANE_WEB_COLLECTOR_LIMITS__"),  # файл PlatformLimits + змінні середовища
    LimitLayer("source", source_limits, name="shop"),
    LimitLayer("task", task_limits, name="prices"),
    LimitLayer("stage", stage_limits, name="fetch"),
)
resolved.limits.crawl.max_depth  # значення
resolved.effective()  # {"limits": {...}, "provenance": {"crawl.max_depth": "task" | "hard_cap" | ...}}
```

`hard_caps` платформи обмежують результат (`min`); нижчий рівень може лише звузити стелю. Автономний
режим: ліміти із запиту — шар `LimitLayer("request", ...)`, для відмови замість обрізання —
`on_exceed="error"` (→ `limit_exceeded`).

Ліміт, що є в `limits.schema.json`, оголошуйте через `contract_field("<група>.<поле>", типове, ...)` (для
групи — `contract_field("retries", RetryPolicy())`): такі поля потрапляють у `/v1/info` → `limits`
(`PlatformLimits`: `defaults` і `hard_caps`). Специфічні для сервісу ліміти лишаються внутрішніми, бо схема
контракту строга. Ефективні ліміти з походженням для джерела/завдання/етапу рахує лише оркестратор.

**Один профіль на всі сервіси** (ТЗ §12, критерій 13). Файл платформи (`<ПРЕФІКС>LIMITS_FILE`, `load_layer(...,
"platform")`) — це спільний шар (`LimitLayer.shared`): у нього можна покласти цілий профіль
`deploy/profiles/<профіль>.json`. Для такого шару:

- шлях контракту (`timeouts.request_timeout_ms`) потрапляє в усі поля моделі, що його оголошують через
  `contract_field` (наприклад `client.request_timeout_ms`), або в неоголошене поле за тим самим шляхом;
- шлях контракту, якого сервіс не моделює (`sandbox.memory_mb` для storage), ігнорується й записується в
  `ResolvedLimits.ignored` / `ignored_hard_caps`; `create_app(limits=...)` пише їх у журнал старту
  (`platform limits profile applied partially`, поля `profile`, `ignored`, `ignored_hard_caps`);
- шлях моделі сервісу (`jobs.max_concurrent_jobs`) теж приймається, як і раніше;
- шлях, невідомий і моделі, і контракту (опечатка), `null`, некоректне значення чи тип поля, яке сервіс моделює,
  та одне поле двічі з різними значеннями (`transfer.job_retention_seconds` і `jobs.job_retention_seconds`) —
  `LimitError`, тобто сервіс не стартує.

Решта шарів (змінні `<ПРЕФІКС>LIMITS__*`, джерело, завдання, запит) приймають лише шляхи моделі: невідоме поле
запиту — далі `LimitError` (→ 422 / `limit_exceeded` у сервісі). Перелік шляхів контракту — `CONTRACT_LIMIT_PATHS`
(копія `limits.schema.json`, бо сервіси працюють і без `contracts/`; рівність перевіряє контрактний тест).

Типові значення лімітів самої бібліотеки:

| Модель | Параметр | Типово |
|---|---|---|
| `JobLimits` | `max_concurrent_jobs` / `max_queued_jobs` | 4 / 1000 |
| `JobLimits` | `job_timeout_ms` / `job_retention_seconds` / `queue_full_retry_after_seconds` | 3600000 / 86400 / 1 |
| `IdempotencyLimits` | `idempotency_ttl_seconds` / `in_memory_max_entries` | 86400 / 10000 |
| `ClientLimits` | `connect_timeout_ms` / `request_timeout_ms` / `max_connections` | 5000 / 30000 / 20 |
| `ClientLimits.retries` | `max_attempts` / `initial_backoff_ms` / `max_backoff_ms` / `backoff_multiplier` / `jitter` | 4 / 200 / 10000 / 2.0 / true |
| `ClientLimits` | `job_poll_interval_ms` / `job_wait_timeout_ms` | 1000 / 3600000 |
| `PageLimits` | `default_page_size` / `max_page_size` | 50 / 500 |
| `JaneSettings` | `health_check_timeout_ms` (env `<PREFIX>HEALTH_CHECK_TIMEOUT_MS`) | 2000 |

## Кілька екземплярів

`InMemoryIdempotencyStore` і `InMemoryJobStore` — для одного екземпляра й тестів. Для кількох екземплярів
сервіс реалізує протоколи `IdempotencyStore` і `JobStore` у власній БД; решта коду не змінюється.

## Тести

```
just test jane-kit
JANE_CONTRACTS_DIR=<шлях до contracts> just test jane-kit -m contract   # проти контрактів WP-00
```

`tests/test_wp00_contracts.py` перевіряє відповідність контрактам WP-00 (каталог кодів помилок, Problem,
Job, Health, ServiceInfo, EffectiveLimits, моки й клієнт для кожного `contracts/openapi/*.v1.yaml`);
пропускається, доки `contracts/` немає в checkout.
