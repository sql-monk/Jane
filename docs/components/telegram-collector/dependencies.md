# Telegram Collector: залежності

Що потрібно Telegram Collector, які залежності опційні та як сервіс поводиться за їхньої недоступності. Версії — з `services/telegram-collector/pyproject.toml` і `uv.lock` ревізії `48389a3`.

## Зміст

- [Обов'язкові](#обовязкові)
- [Опційні](#опційні)
- [Поведінка за недоступності](#поведінка-за-недоступності)

## Обов'язкові

| Залежність | Версія | Призначення |
|---|---|---|
| Python | ≥ 3.12 (образ `python:3.12-slim`) | середовище виконання |
| `jane-kit` | workspace | конфігурація й ліміти, помилки, job, Idempotency-Key, автентифікація, метрики, правила |
| `httpx` | ≥ 0.27 (у lock — 0.28.1) | запити до Registry |
| `jsonschema` | ≥ 4.23 (у lock — 4.26.0) | перевірка запитів, правил і підключень |
| JSON Schema контрактів | каталог `contracts/` | шукається в `JANE_TELEGRAM_COLLECTOR_CONTRACTS_DIR`, `JANE_CONTRACTS_DIR` або в checkout |
| Каталог стану | `JANE_TELEGRAM_COLLECTOR_STATE_DIR` | файл SQLite `state.db` (WAL), доступний на запис |
| Клієнт Telegram | один із бекендів | `recorded` — каталог записів `RECORDINGS_DIR`; `telethon` — пакет Telethon і обліковий запис |

## Опційні

| Залежність | Коли потрібна | Як підключити |
|---|---|---|
| Telethon | реальний Telegram | `uv sync --package jane-telegram-collector --extra telethon` (`telethon>=1.36,<2`, у lock — 1.45.0); Docker — `--build-arg EXTRAS="--extra telethon"` |
| Обліковий запис Telegram | бекенд `telethon` | `api_id`, `api_hash` з my.telegram.org і готова `StringSession` авторизованого облікового запису |
| Registry (`registry.v1`) | правила за `rules_ref` з репозиторію | `JANE_TELEGRAM_COLLECTOR_REGISTRY_URL`, токен — через `REGISTRY_TOKEN_ENV` |
| Локальні пакети правил | `rules_ref` без Registry | `JANE_TELEGRAM_COLLECTOR_RULES_DIR` |
| Транзитне сховище | медіа й великі повідомлення, `content_delivery: blob` | `JANE_TELEGRAM_COLLECTOR_TRANSIT_DIR` |

Orchestrator, Storage, Handler Runtime і PostgreSQL колектору не потрібні. Інтеграцію з реальним Telegram через Telethon у проєкті не перевіряли.

## Поведінка за недоступності

| Що недоступно | Поведінка |
|---|---|
| Telegram (мережа, внутрішня помилка) | повтори за `retries.*`; після `max_attempts` збір `failed` з `source_unavailable` (повторюваний), прогрес збережено |
| FloodWait до `telegram.max_flood_wait_seconds` | колектор чекає й продовжує; лічильник `flood_waits` у прогресі job |
| FloodWait довший | збір `failed` з `rate_limited` і `retry_after_seconds`; наступний збір продовжить із курсора. Разове отримання одразу повертає `429` з `Retry-After` |
| Канал не існує або недоступний | у зборі — запис `not_found` у `/errors`, збір іде до наступного каналу; у разовому отриманні — `502 source_unavailable` |
| Сесію не авторизовано | збір `failed` з `source_unavailable`, `details.reason: account_unauthorized` (не повторюваний) |
| `RECORDINGS_DIR` не задано (бекенд `recorded`) | відкриття клієнта — `ClientUnavailable`; збір після повторів `failed` з `source_unavailable` |
| Пакет `telethon` не встановлено | те саме, з повідомленням про відсутній extra |
| Секрет підключення не розв'язується | `422 validation_failed` під час старту збору чи отримання |
| Registry не відповідає | `502 upstream_unavailable` на запит із `rules_ref` |
| Транзитне сховище не налаштоване | `content_delivery: blob` — `422`; велике повідомлення в `auto` — помилка `limit_exceeded` для цього повідомлення; медіа понад inline — пропускається з діагностикою `media_skipped` |
| Файл стану зайнятий довше за `STATE_BUSY_TIMEOUT_MS` | `503 service_unavailable` з `Retry-After` |
| Файл стану записав новіший колектор | сервіс не стартує (`StateFileTooNew`) |
