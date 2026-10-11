# LLM gateway: конфігурація

Параметри LLM gateway: змінні середовища процесу, ліміти, seed-файл і конфігурація, яку сервіс зберігає у своєму сховищі (провайдери, псевдоніми, бюджети, підключення). Джерело фактів — `services/llm/src/jane_llm/settings.py`, `models.py`, `app.py` і спільні налаштування `jane_kit.config.JaneSettings` ревізії `48389a3`.

## Зміст

- [Як задаються параметри](#як-задаються-параметри)
- [Параметри процесу](#параметри-процесу)
- [Сховище](#сховище)
- [Провайдери, пакети й Registry](#провайдери-пакети-й-registry)
- [Секрети й доступ до вмісту](#секрети-й-доступ-до-вмісту)
- [Автентифікація](#автентифікація)
- [Ліміти](#ліміти)
- [Seed-файл](#seed-файл)
- [Конфігурація через API](#конфігурація-через-api)
- [Як застосовуються зміни](#як-застосовуються-зміни)

## Як задаються параметри

Усі змінні мають префікс `JANE_LLM_`. Списки задаються JSON-рядком, наприклад `JANE_LLM_BLOB_ROOTS='["/var/lib/jane/storage/objects"]'`. Вкладені групи лімітів — через подвійне підкреслення: `JANE_LLM_LIMITS__LLM__BUDGET__AMOUNT=20`.

Частину конфігурації (провайдери, псевдоніми, бюджети, підключення) сервіс зберігає у своєму сховищі й змінює через API; seed-файл лише створює відсутні записи під час старту.

## Параметри процесу

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_LLM_HOST` | рядок | `127.0.0.1` | адреса прослуховування; в образі Docker — `0.0.0.0` |
| `JANE_LLM_PORT` | ціле | `8110` | порт HTTP |
| `JANE_LLM_LOG_LEVEL` | рядок | `INFO` | рівень журналу |
| `JANE_LLM_LOG_FORMAT` | `json`, `console` | `json` | формат журналу |
| `JANE_LLM_METRICS_ENABLED` | булеве | `true` | `/metrics` у форматі Prometheus і лічильники шлюзу |
| `JANE_LLM_HEALTH_CHECK_TIMEOUT_MS` | ціле ≥ 1 | `2000` | тайм-аут кожної перевірки `/v1/health` |
| `JANE_LLM_INSTANCE_ID` | рядок | `<hostname>-<pid>-<uuid>` | ідентифікатор екземпляра: власник оренди job і ключів ідемпотентності |
| `JANE_LLM_LIMITS_FILE` | шлях | — | файл лімітів платформи (див. [Ліміти](#ліміти)) |

## Сховище

| Змінна | Тип | Типово | Обов'язковість | Вплив |
|---|---|---|---|---|
| `JANE_LLM_STORE` | `postgres`, `memory` | `postgres` | — | де живе стан; `memory` — лише один процес, стан зникає з процесом |
| `JANE_LLM_DATABASE_URL` | DSN | — | для `postgres` | `postgresql://user:pass@host:5432/db`; пароль краще передавати через середовище (наприклад `PGPASSWORD`) |
| `JANE_LLM_DB_SCHEMA` | рядок `^[a-z_][a-z0-9_]{0,62}$` | `llm` | — | власна схема сервісу; створюється під час старту |
| `JANE_LLM_DB_POOL_MIN_SIZE` | ціле ≥ 0 | `1` | — | мінімум з'єднань на екземпляр |
| `JANE_LLM_DB_POOL_MAX_SIZE` | ціле ≥ 1 | `10` | — | максимум з'єднань; узгоджуйте з `jobs.max_concurrent_jobs` і навантаженням |

## Провайдери, пакети й Registry

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_LLM_FAKE_PROVIDER_ENABLED` | булеве | `true` | під час старту створює провайдер `fake` (модель `fake-deterministic-1`, нульова ціна) і псевдонім `default` на нього, якщо їх ще немає. Образ Docker задає `false`; dev-стек (`infra/compose.yaml`) знову вмикає `true` |
| `JANE_LLM_SEED_FILE` | шлях | — | YAML або JSON з підключеннями, провайдерами, псевдонімами й бюджетами (див. [Seed-файл](#seed-файл)) |
| `JANE_LLM_PACKAGES_DIR` | шлях | вбудований `services/llm/packages`, якщо каталог є | локальні LLM-пакети `<каталог>/<package_id>/jane-package.json`; в образі Docker — `/app/packages` |
| `JANE_LLM_REGISTRY_URL` | URL | — | Registry (`registry.v1`) для пакетів за посиланням |
| `JANE_LLM_REGISTRY_TOKEN` | секрет | — | власний bearer-токен шлюзу для Registry; не потрапляє в журнал |

Псевдонім `default` береться пакетами й запитами без поля `model`. Якщо seed-файл задає `default` на реальну модель, вбудований `default → fake` не створюється, бо seed застосовується першим.

## Секрети й доступ до вмісту

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_LLM_SECRET_ENV_PREFIX` | рядок | `JANE_SECRET_` | посилання `env:` у `secret_refs` можуть називати лише змінні з цим префіксом |
| `JANE_LLM_SECRET_FILES_DIR` | шлях | `/run/secrets` | посилання `file:` можуть вказувати лише всередину цього каталогу; порожнє значення вимикає `file:` |
| `JANE_LLM_PROVIDER_API_BASE_ALLOWLIST` | список URL | `["https://api.anthropic.com"]` | дозволені точні origin для `params.api_base` підключення; інший origin — 422, і секрети такому підключенню не видаються |
| `JANE_LLM_BLOB_ROOTS` | список шляхів | `[]` | каталоги, з яких можна читати `file://` вміст матеріалів, сутностей і архівів пакетів; порожньо — `file://` заборонено |
| `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST` | список | `[]` | `hostname` або `hostname:port` для `download_url`; порожньо — завантаження заборонено; помилка формату зупиняє старт |

Модель секретів і підключень платформи — [безпека](../../architecture/security.md#секрети-й-підключення).

## Автентифікація

Параметри автентифікації спільні для всіх сервісів (`JANE_LLM_AUTH_MODE`: `none`, `api_key`, `jwt`; `JANE_LLM_API_KEYS`, `JANE_LLM_API_KEYS_FILE`, `JANE_LLM_JWT_*`) і описані в [безпеці](../../architecture/security.md#автентифікація). Типово `none` — лише для локальної роботи.

Дозволи операцій LLM gateway:

| Операції | Дозвіл |
|---|---|
| `GET /v1/providers*`, `GET /v1/model-aliases` | `llm:admin` або `llm:invoke` |
| `PUT`/`DELETE /v1/providers/*`, `PUT /v1/model-aliases/*` | `llm:admin` |
| `POST /v1/completions` | `llm:invoke` |
| `/v1/budgets*`, `GET /v1/usage` | `llm:admin` |
| `POST /v1/invocations`, `GET /v1/invocations/{id}` | `handler:invoke` |
| `POST /v1/test-runs` | `handler:test` |
| `GET /v1/connections*` | `connections:write` або `handler:invoke` |
| `PUT`/`DELETE /v1/connections/*`, `POST …/test` | `connections:write` |
| `GET /v1/jobs/{id}`, `POST …/cancel` | `llm:admin`, `llm:invoke`, `handler:invoke` або `handler:test` |

`/v1/health` відповідає без ключа; `/metrics` — без ключа, поки `JANE_LLM_METRICS_PUBLIC=true` (типово).

## Ліміти

Ліміти розв'язуються шарами: типові значення → файл `JANE_LLM_LIMITS_FILE` (документ `PlatformLimits`, можна цілий профіль `deploy/profiles/<профіль>.json`) → змінні `JANE_LLM_LIMITS__<ГРУПА>__<ПОЛЕ>` → поле `limits.llm` запиту. Загальні правила й стелі `hard_caps` — [ліміти й профілі](../../operations/limits.md).

### Група `llm` (контракт `limits.llm`)

| Поле | Типово | Вплив |
|---|---|---|
| `max_requests_per_minute` | `60` | викликів провайдера на хвилину для рівня `platform`, спільно для всіх екземплярів |
| `max_input_tokens_per_request` | `100000` | оцінка вхідних токенів понад цей ліміт — 422 `limit_exceeded` до виклику |
| `max_output_tokens_per_request` | `4096` | верхня межа `max_output_tokens` запиту чи пакета |
| `budget.amount` | `10.0` | бюджет платформи, коли збереженого визначення `platform/platform` немає |
| `budget.currency` | `USD` | валюта; має збігатися з валютою ціни моделі, інакше 422 |
| `budget.period` | `day` | `run`, `day`, `week`, `month`, `total` |

### Група `gateway` (внутрішня)

| Поле | Типово | Вплив |
|---|---|---|
| `default_max_output_tokens` | `1024` | `max_output_tokens`, коли його не задали ні запит, ні пакет |
| `max_schema_retries` | `1` | типове значення й верхня межа додаткових спроб за невалідного виходу |
| `chars_per_token_estimate` | `2.0` | символів на токен в оцінці вхідних токенів для резерву бюджету |
| `reservation_ttl_seconds` | `900` | резерв, старший за це (екземпляр упав під час виклику), списується за оцінкою |
| `max_data_part_bytes` | `2000000` | найбільша частина даних (вміст матеріалу) з `inline` чи за посиланням |
| `content_fetch_timeout_ms` | `30000` | тайм-аут завантаження вмісту за `download_url`, разом зі з'єднанням |
| `max_package_bytes` | `20000000` | найбільший архів пакета, стиснутий і розпакований |
| `max_package_files` | `1000` | найбільша кількість файлів в архіві пакета |

### Група `provider`

| Поле | Типово | Вплив |
|---|---|---|
| `connect_timeout_ms` | `5000` | з'єднання з провайдером (контракт `timeouts.connect_timeout_ms`) |
| `request_timeout_ms` | `120000` | один HTTP-виклик провайдера з очікуванням усієї генерації; це не контрактний `timeouts.request_timeout_ms` |
| `retries.max_attempts` | `2` | спроб разом із першою (контракт `retries`) |
| `retries.initial_backoff_ms` | `500` | перша затримка |
| `retries.max_backoff_ms` | `10000` | найбільша затримка, також межа для `Retry-After` |
| `retries.backoff_multiplier` | `2.0` | множник затримки |
| `retries.jitter` | `true` | випадкова надбавка до затримки |

Профіль платформи задає `timeouts.connect_timeout_ms` і `retries` для `provider`; його `timeouts.request_timeout_ms` до виклику моделі не застосовується — тайм-аут генерації задається лише `JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS`.

### Інші групи

| Група | Поля й типові значення | Вплив |
|---|---|---|
| `fake` | `max_delay_ms=30000` | найбільша затримка відповіді `fake`; `0` вимикає затримки |
| `registry` | `connect_timeout_ms=5000`, `request_timeout_ms=30000`, `max_attempts=3` | виклики Registry |
| `jobs` | `max_concurrent_jobs=4`, `max_queued_jobs=1000`, `job_timeout_ms=3600000`, `job_retention_seconds=86400`, `queue_full_retry_after_seconds=1` | асинхронні job; переповнена черга — 503 `service_unavailable` |
| `idempotency` | `idempotency_ttl_seconds=86400`, `in_memory_max_entries=10000` | скільки пам'ятається `Idempotency-Key`; ліміт записів лише для `memory` |
| `state` | `in_progress_lease_ms=900000`, `heartbeat_interval_ms=15000`, `job_lease_ms=60000` | оренди спільного стану PostgreSQL між екземплярами |

### Ліміти в запиті

`CompletionRequest.limits` і `HandlerInvocation.limits.llm` приймають контрактні поля `limits.llm`:

- `max_input_tokens_per_request`, `max_output_tokens_per_request` — шар `request` поверх платформних значень, обмежений `hard_caps`;
- `max_requests_per_minute` — додатковий ліміт найконкретнішого рівня запиту (береться менше значення);
- `budget` — ще один бюджет найконкретнішого рівня; він лише звужує, а не замінює збережений бюджет (див. [internals.md](internals.md#бюджети)).

Поля `max_improvement_attempts`, `max_onboarding_samples`, `min_onboarding_confidence` приймаються, але шлюз їх не використовує — це ліміти Assistant.

## Seed-файл

`JANE_LLM_SEED_FILE` — YAML або JSON із розділами `connections`, `providers`, `model_aliases`, `budgets`. Під час кожного старту створюються лише відсутні записи; існуючі не змінюються. Підключення перевіряються тією самою політикою секретів, що й `PUT /v1/connections`: порушення зупиняє старт. Секретів у файлі немає — лише посилання. Приклад — `services/llm/config/seed.example.yaml` (уривок):

```yaml
connections:
  - connection_id: anthropic-main
    kind: llm_provider
    title: Anthropic Messages API
    params:
      api_base: https://api.anthropic.com
    secret_refs:
      api_key: env:JANE_SECRET_ANTHROPIC_API_KEY

providers:
  - provider_id: anthropic
    kind: anthropic
    connection_id: anthropic-main
    enabled: true
    models:
      - model_id: claude-haiku-5-5
        max_context_tokens: 1000000
        supports_structured_output: true
        pricing: {input_per_mtok: 0.1, output_per_mtok: 0.5, currency: USD}

model_aliases:
  - {alias: default, provider_id: anthropic, model_id: claude-haiku-5-5}
  - {alias: cheap, provider_id: anthropic, model_id: claude-haiku-5-5}

budgets:
  - scope_type: platform
    scope_id: platform
    budget: {amount: 10, currency: USD, period: day}
    max_requests_per_minute: 60
```

Ціни й назви моделей у прикладі взято з `seed.example.yaml` і `scripts/llm_anthropic.py`; актуальність цін провайдера в цій документації не перевірялася.

## Конфігурація через API

| Документ | Операції | Ключові поля |
|---|---|---|
| Провайдер | `GET`/`PUT`/`DELETE /v1/providers/{provider_id}` | `kind` (`anthropic` або `fake`), `connection_id`, `enabled`, `models[]` з `pricing` і `max_context_tokens`, `limits.max_requests_per_minute` |
| Псевдонім | `GET /v1/model-aliases`, `PUT /v1/model-aliases/{alias}` | `provider_id`, `model_id` (модель має бути в провайдері) |
| Бюджет | `GET /v1/budgets`, `PUT`/`DELETE /v1/budgets/{scope_type}/{scope_id}` | `budget` (`amount`, `currency`, `period`), `max_requests_per_minute` |
| Підключення | `GET`/`PUT`/`DELETE /v1/connections/{connection_id}`, `POST …/test` | `kind: llm_provider`, `params`, `secret_refs` |

Правила:

- `PUT` провайдера й підключення приймає `If-Match` з `ETag` попереднього `GET`; розбіжність — 412 `precondition_failed`.
- Провайдер, на який посилається псевдонім, не видаляється — 409 `conflict`.
- Провайдер може посилатися лише на існуюче підключення — інакше 422.
- `params` підключення з ключами чи значеннями, схожими на секрет (`api_key`, `token`, `sk-…` тощо), відхиляються з 422 `secret_detected`; секрети задаються тільки в `secret_refs`. Формат посилання дозволяє `env:VAR`, `file:<шлях>` і `vault:<шлях>#<ключ>`, але політика шлюзу приймає лише `env:` з префіксом `JANE_LLM_SECRET_ENV_PREFIX` і `file:` усередині `JANE_LLM_SECRET_FILES_DIR`; решта — 422 з кодом поля `secret_ref_not_allowed`.
- Для рівня `platform` ідентифікатор лише `platform`. Без збереженого визначення `platform/platform` діє `limits.llm.budget` із конфігурації.

Повні схеми — [reference/api](reference/api/README.md).

## Як застосовуються зміни

| Що змінено | Як застосувати |
|---|---|
| Змінні `JANE_LLM_*`, файл лімітів | перезапуск сервісу |
| Seed-файл | перезапуск; створюються лише нові записи, змінені записи оновлюйте через API |
| Провайдери, псевдоніми, бюджети, підключення | запит до API; діє з наступного виклику на всіх екземплярах зі спільним PostgreSQL |
| Ліміти одного запиту | поле `limits` у тілі запиту |
