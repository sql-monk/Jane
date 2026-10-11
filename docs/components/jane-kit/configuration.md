# jane-kit: конфігурація

Параметри, які бібліотека дає кожному сервісу, і механізм лімітів з успадкуванням. Назви змінних середовища залежать від префікса сервісу: `JaneSettings` має префікс `JANE_`, а сервіс у своєму підкласі задає власний, наприклад `JANE_WEB_COLLECTOR_`. Нижче `<PREFIX>` — цей префікс.

## Зміст

- [Параметри процесу](#параметри-процесу)
- [Автентифікація](#автентифікація)
- [Ліміти](#ліміти)
- [Вбудовані моделі лімітів](#вбудовані-моделі-лімітів)
- [Читання ContentRef і секрети](#читання-contentref-і-секрети)
- [Як застосовуються зміни](#як-застосовуються-зміни)

## Параметри процесу

Поля `jane_kit.config.JaneSettings`; змінна середовища — `<PREFIX><НАЗВА>` великими літерами.

| Поле | Тип | Типово | Вплив |
|---|---|---|---|
| `service_name` | рядок | `jane-service` | Поле `service` у журналах, `/v1/info` і мітці метрики `jane_service_info` |
| `instance_id` | рядок | `<hostname>-<pid>-<uuid>` | Унікальний для кожного старту процесу; власник оренд job і ключів ідемпотентності |
| `host` | рядок | `127.0.0.1` | Адреса прослуховування |
| `port` | ціле | `8000` | Порт |
| `log_level` | рядок | `INFO` | Рівень кореневого логера |
| `log_format` | `json` \| `console` | `json` | JSON-рядок на запис або читабельний формат для консолі |
| `metrics_enabled` | булеве | `true` | Чи є `/metrics` і HTTP-метрики |
| `health_check_timeout_ms` | ціле `>=1` | `2000` | Тайм-аут кожної перевірки `/v1/health` |
| `limits_file` | шлях | — | Файл лімітів платформи (`PlatformLimits`, TOML/JSON/YAML) |

Усі поля необов'язкові. Сервіс додає власні поля у свій підклас `JaneSettings`, а операційні числові обмеження — лише в модель `Limits`.

## Автентифікація

Поля `jane_kit.auth.AuthSettings` (частина `JaneSettings`), змінні `<PREFIX><НАЗВА>`.

| Поле | Тип | Типово | Вплив |
|---|---|---|---|
| `auth_mode` | `none` \| `api_key` \| `jwt` | `none` | Режим автентифікації |
| `auth_none_allow_remote` | булеве | `false` | Дозволяє `none` на адресі, що не є loopback (лише ізольовані тестові мережі) |
| `api_keys` | JSON-список | `[]` | Ключі режиму `api_key` |
| `api_keys_file` | шлях | — | JSON- або YAML-файл зі списком ключів, додається до `api_keys` |
| `jwt_jwks_url` | URL | — | JWKS постачальника: `https://`, `http://` лише для loopback |
| `jwt_issuer` | рядок | — | Обов'язковий `iss` |
| `jwt_audience` | рядок | — | Обов'язковий `aud` |
| `jwt_algorithms` | список | `["RS256", "ES256"]` | Підмножина `RS256/384/512`, `PS256/384/512`, `ES256/384/512` |
| `jwt_scope_claim` | рядок | `scope` | Claim зі scopes: рядок через пробіл або список |
| `jwt_leeway_seconds` | ціле `0..600` | `30` | Допустимий розсинхрон годинників для `exp`, `nbf`, `iat` |
| `jwt_jwks_cache_ttl_seconds` | ціле `>=1` | `300` | Скільки використовуються завантажені ключі |
| `jwt_jwks_timeout_ms` | ціле `>=1` | `5000` | Тайм-аут одного запиту JWKS |
| `jwt_jwks_refresh_cooldown_seconds` | ціле `>=0` | `10` | Мінімальний інтервал між запитами до JWKS |
| `jwt_jwks_max_bytes` | ціле `>=1024` | `1048576` | Найбільший прийнятний документ JWKS |
| `auth_max_token_bytes` | ціле `>=256` | `16384` | Довший токен відхиляється з `401` до розбору |
| `metrics_public` | булеве | `true` | `/metrics` без токена; `false` — потрібен будь-який чинний токен |

Правила режимів:

- **`none`** — кожен виклик має всі scopes; на старті попередження. З `host`, що не є loopback, сервіс не стартує без `auth_none_allow_remote=true`.
- **`api_key`** — запис ключа: `{"name", "scopes": [...], "sha256": "<hex SHA-256 ключа>"}` або замість `sha256` — `"secret_ref": "env:VAR"` чи `"file:/шлях"`. Посилання розв'язується один раз на старті, зберігається лише хеш. `vault:` не підтримується. Додаткові поля запису стають `Principal.attributes`. Scope має форму `service:action`, наприклад `collector:run`.
- **`jwt`** — підпис перевіряється ключами JWKS; `iss`, `aud`, `exp` обов'язкові; `alg=none` і HMAC не приймаються.

Неповна конфігурація зупиняє старт з `AuthConfigError`: `api_key` без ключів, `jwt` без URL, issuer чи audience, нерозв'язане `secret_ref`, маршрут без scope в таблиці сервісу. Шляхи без токена: `/v1/health` завжди, `/metrics` — коли `metrics_public=true`. Таблиці scopes операцій усіх контрактів — `jane_kit.auth_scopes` ([інтеграція](integration.md#автентифікація-й-scopes)).

## Ліміти

Числові обмеження сервісу описує модель — підклас `jane_kit.config.Limits`. Кожне поле **зобов'язане** мати типове значення: клас без нього не створюється (`TypeError` під час імпорту). Ці типові значення — значення платформи за відсутності конфігурації.

![Ланцюжок успадкування лімітів: типові значення, рівні й жорсткі стелі](../../diagrams/jane-kit/limits-inheritance.light.png#gh-light-mode-only)
![Ланцюжок успадкування лімітів: типові значення, рівні й жорсткі стелі](../../diagrams/jane-kit/limits-inheritance.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/jane-kit/limits-inheritance.light.png), [темне](../../diagrams/jane-kit/limits-inheritance.dark.png); джерело — [limits-inheritance.drawio](../../diagrams/jane-kit/limits-inheritance.drawio).

`resolve_limits(model, *layers)` зливає шари від найменш до найбільш конкретного:

1. Типові значення моделі.
2. Платформа: файл `<PREFIX>LIMITS_FILE`, потім змінні `<PREFIX>LIMITS__<ГРУПА>__<ПАРАМЕТР>` (`JaneSettings.platform_layers`).
3. Джерело, завдання, етап, запит — шари `LimitLayer(level=...)`, які сервіс будує з даних запиту. Рівні — `LEVELS = ("platform", "source", "task", "stage", "request")`.

Правила злиття:

- Глибоке злиття: шар задає будь-яку підмножину полів, відсутнє поле успадковується.
- `null` не є значенням — `LimitError`. Щоб успадкувати, поле не передають.
- Невідоме поле — `LimitError` (помилка в назві не проходить мовчки).
- `hard_caps` обмежують результат: ефективне = `min(значення, стеля)`. Конкретніший шар може стелю лише зменшити; спроба підняти — `LimitError`.
- `on_exceed="clamp"` (типово) знижує значення до стелі й записує це в `clamped`; `on_exceed="error"` кидає `LimitError` — так сервіс відхиляє запит, що просить більше дозволеного (`422 limit_exceeded`).

Результат `ResolvedLimits` містить `limits` (модель), `origin` (шар кожного значення), `clamped`, `hard_caps`, `profile`, `ignored`. Методи: `effective()` — документ `EffectiveLimits` контракту з походженням (`platform`, `source`, `task`, `stage`, `request`, `hard_cap`); `explain()` — рядки для журналу.

### Файл лімітів платформи

Файл має форму `PlatformLimits` з [limits.schema.json](../../../contracts/schemas/common/limits.schema.json): `{"profile", "defaults", "hard_caps"}`. Один файл профілю спільний для всіх сервісів (наприклад, [deploy/profiles/ci.json](../../../deploy/profiles/ci.json)), тому шар платформи «спільний»:

- шлях контракту (наприклад `transfer.idempotency_ttl_seconds`) потрапляє в поле моделі, що його оголошує через `contract_field`, або в поле з тим самим шляхом;
- шлях контракту, якого сервіс не має, ігнорується й записується в `ResolvedLimits.ignored` (на старті — запис у журналі);
- шлях, невідомий і моделі, і контракту, — `LimitError`.

Інші шари (змінні середовища, джерело, завдання, запит) приймають лише шляхи моделі.

Змінні середовища: `<PREFIX>LIMITS__JOBS__MAX_CONCURRENT_JOBS=8` — значення, `<PREFIX>LIMITS__HARD_CAPS__JOBS__MAX_CONCURRENT_JOBS=16` — стеля. Значення лишаються рядками, pydantic перетворює їх на оголошені типи.

### Ліміти в `/v1/info`

`create_app(..., limits=resolved)` публікує в `GET /v1/info` поле `limits` — документ `PlatformLimits` із налаштованими типовими значеннями й `hard_caps` сервісу. Туди потрапляють **лише** поля, пов'язані з контрактом (`contract_field` або група з контрактним шляхом), бо схема контракту строга. Специфічні ліміти сервісу видно лише в журналі старту. Ефективні ліміти конкретного джерела, завдання чи етапу з походженням обчислює Orchestrator (`GET /v1/limits/effective`), а не бібліотека.

Оголошення поля з відповідником у контракті:

```python
from pydantic import Field

from jane_kit.config import Limits, contract_field


class FetchLimits(Limits):
    request_timeout_ms: int = contract_field("timeouts.request_timeout_ms", 30_000, ge=1)
    max_retries_per_page: int = Field(default=2, ge=0)  # service-specific, not in the contract
```

## Вбудовані моделі лімітів

Сервіс вкладає ці моделі у свою модель `Limits` як групи. Колонка «Контракт» — шлях у `limits.schema.json`.

| Модель і поле | Типово | Контракт | Вплив |
|---|---|---|---|
| `JobLimits.max_concurrent_jobs` | 4 | — | Job, що виконуються одночасно в екземплярі |
| `JobLimits.max_queued_jobs` | 1000 | — | Понад це — `503 service_unavailable` |
| `JobLimits.job_timeout_ms` | 3600000 | — | Тривалість job; перевищення — `failed`, код `timeout` |
| `JobLimits.job_retention_seconds` | 86400 | `transfer.job_retention_seconds` | Скільки зберігається завершений job |
| `JobLimits.queue_full_retry_after_seconds` | 1 | — | `Retry-After` у відповіді `503` |
| `IdempotencyLimits.idempotency_ttl_seconds` | 86400 | `transfer.idempotency_ttl_seconds` | Скільки пам'ятається `Idempotency-Key` (мінімум 60) |
| `IdempotencyLimits.in_memory_max_entries` | 10000 | — | Розмір сховища ключів у пам'яті |
| `PageLimits.default_page_size` | 50 | — | `limit` без значення |
| `PageLimits.max_page_size` | 500 | — | Більший `limit` обрізається |
| `ClientLimits.connect_timeout_ms` | 5000 | `timeouts.connect_timeout_ms` | Встановлення з'єднання `ServiceClient` |
| `ClientLimits.request_timeout_ms` | 30000 | `timeouts.request_timeout_ms` | Тайм-аут запиту `ServiceClient` |
| `ClientLimits.retries` | `RetryPolicy()` | `retries` | Політика повторів |
| `ClientLimits.max_connections` | 20 | — | Пул з'єднань |
| `ClientLimits.job_poll_interval_ms` | 1000 | — | Інтервал опитування job у `wait_for_job` |
| `ClientLimits.job_wait_timeout_ms` | 3600000 | — | Найдовше очікування job |
| `RetryPolicy.max_attempts` | 4 | `retries.max_attempts` | Усі спроби разом із першою |
| `RetryPolicy.initial_backoff_ms` | 200 | `retries.initial_backoff_ms` | Перша пауза |
| `RetryPolicy.max_backoff_ms` | 10000 | `retries.max_backoff_ms` | Найдовша пауза |
| `RetryPolicy.backoff_multiplier` | 2.0 | `retries.backoff_multiplier` | Множник паузи |
| `RetryPolicy.jitter` | `true` | `retries.jitter` | Випадкова добавка до половини паузи |
| `ClaimLimits.in_progress_lease_ms` | 900000 | — | Захоплений ключ без поновлення стає доступним знову |
| `ClaimLimits.heartbeat_interval_ms` | 15000 | — | Як часто екземпляр поновлює оренди |
| `LeaseLimits.job_lease_ms` | 60000 | — | Job без поновлення оренди закінчується `failed` |

`LeaseLimits` успадковує поля `ClaimLimits`. Обмеження допустимих значень (`ge=...`) — у коді моделей у [libs/jane-kit/src/jane_kit](../../../libs/jane-kit/src/jane_kit/).

## Читання ContentRef і секрети

Ці параметри сервіс передає в конструктори; назви змінних — рекомендація бібліотеки, сервіс оголошує їх сам.

| Параметр | Де | Типово | Вплив |
|---|---|---|---|
| `blob_roots` (`<PREFIX>BLOB_ROOTS`, JSON-список) | `ContentReader` | порожньо | Каталоги, з яких дозволено читати `file://`; порожньо — `file://` вимкнено |
| `download_host_allowlist` (`<PREFIX>DOWNLOAD_HOST_ALLOWLIST`) | `ContentReader` | порожньо | `hostname` або `hostname:port` для `download_url`; порожньо — завантаження вимкнено |
| `timeout_ms`, `connect_timeout_ms` | `ContentReader` | обов'язковий / як `timeout_ms` | Межа всього завантаження й з'єднання |
| `mode` | `ContentWriter` | обов'язковий | `auto` (inline до `inline_max_bytes`, інакше blob), `inline`, `blob` |
| `inline_max_bytes`, `transit_ttl_seconds` | `ContentWriter` | обов'язкові | Ліміти контракту `transfer.*` |
| `env_prefix` | `SecretPolicy` | `JANE_SECRET_` | `env:` лише для змінних із цим префіксом |
| `files_dir` | `SecretPolicy` | `/run/secrets` | `file:` лише всередині каталогу; `None` вимикає |

Невалідний запис allowlist зупиняє старт (`ValueError`).

## Як застосовуються зміни

| Що змінюється | Коли діє |
|---|---|
| `JaneSettings`, автентифікація, файл і змінні лімітів платформи | Після перезапуску процесу — читаються на старті |
| Ліміти джерела, завдання, етапу | У наступному запиті, що несе ці шари |
| Ліміти запиту в автономному режимі | Лише для цього запиту: `min(запит, hard_caps сервісу)` |
| Профіль лімітів платформи | Новий файл і перезапуск усіх сервісів, що його читають |
