# Telegram Collector: налаштування

Параметри процесу задаються змінними середовища з префіксом `JANE_TELEGRAM_COLLECTOR_`; ліміти — шарами від платформи до запиту. Джерело фактів — `services/telegram-collector/src/jane_telegram_collector/settings.py` і `libs/jane-kit` (ревізія `48389a3`).

## Зміст

- [Застосування змін](#застосування-змін)
- [Процес і API](#процес-і-api)
- [Клієнт Telegram](#клієнт-telegram)
- [Стан, правила й доставка](#стан-правила-й-доставка)
- [Секрети й підключення](#секрети-й-підключення)
- [Оренда й кілька екземплярів](#оренда-й-кілька-екземплярів)
- [Ліміти](#ліміти)
- [Успадкування лімітів](#успадкування-лімітів)

## Застосування змін

| Що змінюється | Як застосувати |
|---|---|
| Змінні середовища, файл лімітів платформи | перезапуск процесу |
| `rules.limits` | у правилах наступного запиту |
| `limits` запиту `POST /v1/collections` чи `POST /v1/fetches` | у цьому запиті |
| Записи каналів бекенда `recorded` | одразу: файл перечитується на кожен виклик |

## Процес і API

Спільні параметри процесу ті самі, що в Web Collector, з префіксом `JANE_TELEGRAM_COLLECTOR_`: `HOST` (`127.0.0.1`), `PORT` (**`8102`**), `INSTANCE_ID`, `LOG_LEVEL` (`INFO`), `LOG_FORMAT` (`json`), `METRICS_ENABLED` (`true`), `HEALTH_CHECK_TIMEOUT_MS` (`2000`), `AUTH_MODE` (`none`), `API_KEYS`, `API_KEYS_FILE`, `AUTH_NONE_ALLOW_REMOTE`, `METRICS_PUBLIC` і параметри `JWT_*`. Опис — [налаштування Web Collector](../web-collector/configuration.md#процес-і-api); права операцій однакові (`collector:run`, `collector:read`, `connections:write`).

## Клієнт Telegram

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND` | `recorded`, `telethon`, `<module>:<factory>` | `recorded` | реалізація клієнта Telegram |
| `JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR` | шлях | не задано | `recorded`: каталог файлів `<username або channel_id>.json` |
| `JANE_TELEGRAM_COLLECTOR_DEFAULT_ACCOUNT_CONNECTION_ID` | рядок | не задано | підключення `telegram_account`, якщо правила його не називають (наприклад, `POST /v1/fetches` без правил) |
| `JANE_TELEGRAM_COLLECTOR_TELEGRAM_HOST_ALLOWLIST` | JSON-список | `[]` | хости, дозволені в параметрах підключення `server`, `host`, `proxy_host`, `proxy`, `api_base`, `dc_address`; порожньо — такі параметри відхиляються |

Для `<module>:<factory>` модуль імпортується, а `factory` — об'єкт або викликаний з `Settings` результат, що реалізує `ClientFactory` (`name`, `open(account, connect_timeout_s)`, `requires_account()`).

## Стан, правила й доставка

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_TELEGRAM_COLLECTOR_STATE_DIR` | шлях | `.jane/telegram-collector` | каталог `state.db`; спільний для екземплярів одного вузла |
| `JANE_TELEGRAM_COLLECTOR_TRANSIT_DIR` | шлях | не задано | транзитні blob для медіа й великих повідомлень |
| `JANE_TELEGRAM_COLLECTOR_RULES_DIR` | шлях | не задано | локальні пакети правил для `rules_ref` |
| `JANE_TELEGRAM_COLLECTOR_REGISTRY_URL` | URL | не задано | Registry для `rules_ref`, після `RULES_DIR` |
| `JANE_TELEGRAM_COLLECTOR_REGISTRY_TOKEN_ENV` | рядок | не задано | **ім'я** змінної з токеном Registry |
| `JANE_TELEGRAM_COLLECTOR_CONTRACTS_DIR` | шлях | `JANE_CONTRACTS_DIR` або `contracts/` checkout | JSON Schema контрактів |

## Секрети й підключення

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_TELEGRAM_COLLECTOR_SECRET_ENV_PREFIX` | рядок | `JANE_SECRET_` | `env:`-посилання лише на змінні з цим префіксом |
| `JANE_TELEGRAM_COLLECTOR_SECRET_FILES_DIR` | шлях | `/run/secrets` | `file:`-посилання лише всередині каталогу; порожньо — вимкнено |

Підключення `kind=telegram_account` (`PUT /v1/connections/{id}`) для бекенда `telethon`:

| Поле | Значення |
|---|---|
| `params.api_id` | ідентифікатор застосунку з my.telegram.org (не секрет) |
| `secret_refs.api_hash` | хеш застосунку, наприклад `env:JANE_SECRET_TG_API_HASH` |
| `secret_refs.session` | Telethon `StringSession` уже авторизованого облікового запису |

Зразок — [examples/telegram/connection.telegram-account.json](../../../examples/telegram/connection.telegram-account.json). Значення секретів через API не передаються; посилання `vault:` вимкнено. Ключі з назвами на кшталт `password`, `token`, `session` у `params` відхиляються як секрети.

## Оренда й кілька екземплярів

`LEASE_SECONDS` (30), `HEARTBEAT_INTERVAL_MS` (5000), `STATE_BUSY_TIMEOUT_MS` (10 000), `IDEMPOTENCY_LEASE_MS` (900 000) — те саме значення й правило старту `HEARTBEAT_INTERVAL_MS + STATE_BUSY_TIMEOUT_MS < LEASE_SECONDS × 1000`, що й у [Web Collector](../web-collector/configuration.md#оренда-й-кілька-екземплярів).

## Ліміти

Групи й поля відповідають [limits.schema.json](../../../contracts/schemas/common/limits.schema.json); група `collector` — службові ліміти сервісу.

| Ліміт | Типово | Призначення |
|---|---|---|
| `rate.min_delay_ms_per_host` | 200 | мінімальна пауза між викликами Telegram API в межах збору |
| `timeouts.connect_timeout_ms` | 15 000 | відкриття клієнта й перевірка авторизації |
| `timeouts.request_timeout_ms` | 30 000 | один виклик API (сторінка історії, зміни, повідомлення, медіа) |
| `retries.max_attempts` | 3 | спроби для тимчасових збоїв |
| `retries.initial_backoff_ms`, `max_backoff_ms` | 1000, 60 000 | межі паузи між спробами |
| `retries.backoff_multiplier`, `jitter` | 2.0, `true` | зростання паузи й випадковий розкид |
| `queue.max_unacked_materials` | 500 | непідтверджених матеріалів у буфері; далі збір чекає |
| `transfer.inline_max_bytes` | 262 144 | більше — транзитний blob |
| `transfer.transit_ttl_seconds` | 604 800 | термін життя транзитного blob |
| `transfer.job_retention_seconds` | 86 400 | зберігання завершених зборів; потім `410` |
| `transfer.idempotency_ttl_seconds` | 86 400 | зберігання `Idempotency-Key` |
| `telegram.max_messages_per_run` | 10 000 | бюджет повідомлень збору; вичерпано — `succeeded` зі `stopped_by` |
| `telegram.max_media_bytes` | 20 МіБ | більші медіа не завантажуються (`media_too_large`) |
| `telegram.max_flood_wait_seconds` | 300 | довший FloodWait зупиняє збір із `rate_limited` |
| `collector.history_page_size` | 100 | повідомлень на запит історії (Telegram віддає не більше 100) |
| `collector.changes_page_size` | 100 | оновлень на запит `getChannelDifference` |
| `collector.max_wait_ms` | 30 000 | верхня межа `wait_ms` у `/materials` |
| `collector.long_poll_interval_ms` | 100 | як часто довге опитування перевіряє буфер |
| `collector.backpressure_poll_ms` | 1000 | як часто збір на паузі перевіряє буфер |
| `collector.gc_interval_seconds` | 3600 | прибирання прострочених зборів і транзитних файлів |
| `jobs.max_concurrent_jobs`, `max_queued_jobs`, `job_timeout_ms` | 4, 1000, 3 600 000 | паралельні збори, черга, межа часу збору |
| `page.default_page_size`, `max_page_size` | 50, 500 | розмір сторінок `/materials`, `/errors`, `/v1/connections` |

## Успадкування лімітів

Порядок шарів: типові значення → файл профілю `JANE_TELEGRAM_COLLECTOR_LIMITS_FILE` → змінні `JANE_TELEGRAM_COLLECTOR_LIMITS__<ГРУПА>__<ПОЛЕ>` (жорсткі межі — `..._LIMITS__HARD_CAPS__<ГРУПА>__<ПОЛЕ>`) → `rules.limits` → `limits` запиту. Групи, яких у колектора немає (`crawl`, `sandbox`, `llm`), у файлі профілю ігноруються. Механізм той самий, що в [Web Collector](../web-collector/configuration.md#успадкування-лімітів), без рівня стратегії. Ефективні ліміти збору — у `effective_limits` відповіді `GET /v1/collections/{id}`.
