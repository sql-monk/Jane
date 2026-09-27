# Telegram Collector

Колектор Jane для Telegram-каналів (ТЗ §3, WP-04): історія, нові повідомлення, редагування як нові ревізії,
курсори, відновлення після збою, обмеження частоти (flood-wait), доступ через налаштований обліковий запис.
API — спільний контракт колекторів [`collector.v1`](../../contracts/openapi/collector.v1.yaml); матеріали —
[`material.schema.json`](../../contracts/schemas/material.schema.json); правила —
`TelegramRules` з [`collector-rules.schema.json`](../../contracts/schemas/collector-rules.schema.json).

Сервіс автономний (ТЗ §4, критерій 1): не звертається до оркестратора, екстрактора чи сховища; правила
приходять inline, з локального пакета або з репозиторію; споживач сам забирає матеріали курсором.

## Запуск

```bash
uv sync --all-packages
# записаний канал (без Telegram): JSON-файли в каталозі, див. «Записи каналів»
JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR=./recordings \
  uv run --package jane-telegram-collector python -m jane_telegram_collector      # http://127.0.0.1:8102

# справжній Telegram (Telethon, необов'язкова залежність)
uv sync --package jane-telegram-collector --extra telethon
JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND=telethon uv run --package jane-telegram-collector python -m jane_telegram_collector
```

Docker (контекст — корінь репозиторію):

```bash
docker build -f services/telegram-collector/Dockerfile -t jane-telegram-collector .
docker build -f services/telegram-collector/Dockerfile --build-arg EXTRAS="--extra telethon" -t jane-telegram-collector .
docker run -p 8102:8102 -v tgstate:/var/lib/jane-telegram-collector \
  -e JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND=telethon -e TG_SESSION=... -e TG_API_HASH=... jane-telegram-collector
```

`HEALTHCHECK` — `GET /v1/health` (перевірка сховища стану). Журнали — JSON у stdout; метрики — `GET /metrics`.

## Тести

```bash
just test telegram-collector          # усе: unit, сценарії на справжньому сервісі, процеси, контракт
```

Тести запускають справжній сервіс (у процесі через TestClient і окремими процесами ОС) проти записаних
каналів; «Telegram» — бекенд `recorded` самого сервісу. Dev-стек (`just up`) не потрібен.
Жоден тест не перевіряє справжній Telegram — тестового облікового запису в проєкті немає.

## Конфігурація

Змінні середовища з префіксом `JANE_TELEGRAM_COLLECTOR_` (див. [settings.py](src/jane_telegram_collector/settings.py)):

| Параметр | Типово | Опис |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `8102` | адреса HTTP |
| `STATE_DIR` | `.jane/telegram-collector` | власне сховище стану (SQLite `state.db`, WAL) |
| `CLIENT_BACKEND` | `recorded` | `recorded`, `telethon` або `<module>:<factory>` (власна реалізація `ClientFactory`) |
| `RECORDINGS_DIR` | — | каталог записів каналів для `recorded` |
| `DEFAULT_ACCOUNT_CONNECTION_ID` | — | підключення, якщо правила не називають `account_connection_id` |
| `TRANSIT_DIR` | — | транзитні blob (`file://`) для великого вмісту й медіа; без нього — лише inline |
| `RULES_DIR` | — | локальні пакети правил для `rules_ref` без репозиторію |
| `REGISTRY_URL` / `REGISTRY_TOKEN_ENV` | — | `registry.v1` для `rules_ref`; ім'я змінної з токеном (не значення) |
| `CONTRACTS_DIR` | `JANE_CONTRACTS_DIR` або `contracts/` checkout | схеми для валідації |
| `LEASE_SECONDS` | `30` | lease збору; без heartbeat довше — збір перехоплює інший екземпляр |
| `HEARTBEAT_INTERVAL_MS` | `5000` | як часто власник продовжує lease і перевіряє скасування |
| `STATE_BUSY_TIMEOUT_MS` | `10000` | скільки запис чекає блокування SQLite іншим процесом |
| `LIMITS_FILE` | — | файл `PlatformLimits` (TOML/JSON/YAML) |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | журнали |

Правило: `HEARTBEAT_INTERVAL_MS + STATE_BUSY_TIMEOUT_MS < LEASE_SECONDS × 1000`, інакше сервіс не стартує
(живий власник не повинен втрачати lease через одне довге очікування блокування).

## Ліміти

Рівні: типові значення сервісу → platform (`LIMITS_FILE`, потім `JANE_TELEGRAM_COLLECTOR_LIMITS__<ГРУПА>__<ПОЛЕ>`,
жорсткі стелі — `..._LIMITS__HARD_CAPS__...`) → source (`rules.limits`) → request (`limits` у запиті).
Після злиття значення обмежуються `hard_caps` (`min`). Ефективні ліміти збору — у `GET /v1/collections/{id}`
→ `effective_limits`; типові значення й стелі — у `GET /v1/info` → `limits`. Групи контракту, яких колектор
не використовує (`crawl`, `sandbox`, `llm`…), ігноруються.

| Ліміт | Типово | Що обмежує |
|---|---|---|
| `rate.min_delay_ms_per_host` | 200 | мінімальний інтервал між двома викликами Telegram API одного збору |
| `timeouts.connect_timeout_ms` | 15000 | відкриття клієнта (з'єднання, перевірка авторизації) |
| `timeouts.request_timeout_ms` | 30000 | один виклик API (сторінка історії, difference, повідомлення, медіа) |
| `retries.max_attempts` / `initial_backoff_ms` / `max_backoff_ms` / `backoff_multiplier` / `jitter` | 3 / 1000 / 60000 / 2.0 / true | повтори тимчасових помилок і тайм-аутів |
| `queue.max_unacked_materials` | 500 | буфер невитягнутих матеріалів; переповнення призупиняє збір (backpressure) |
| `transfer.inline_max_bytes` | 262144 | більший вміст — blob (або `limit_exceeded` без `TRANSIT_DIR`) |
| `transfer.transit_ttl_seconds` | 604800 | час життя транзитних blob (прибиральник сервісу) |
| `telegram.max_messages_per_run` | 10000 | повідомлень за один збір; далі збір завершується з `stopped_by`, наступний продовжує з курсора |
| `telegram.max_media_bytes` | 20971520 | більші медіа пропускаються з діагностикою `media_too_large` |
| `telegram.max_flood_wait_seconds` | 300 | довший flood-wait зупиняє збір з `rate_limited` замість блокування |
| `transfer.job_retention_seconds` (модель: `jobs.job_retention_seconds`) | 86400 | скільки зберігаються завершені збори (потім 410) |
| `transfer.idempotency_ttl_seconds` (модель: `idempotency.idempotency_ttl_seconds`) | 86400 | скільки пам'ятається `Idempotency-Key` |
| `jobs.max_concurrent_jobs` / `max_queued_jobs` / `job_timeout_ms` | 4 / 1000 / 3600000 | збори на екземпляр (jane-kit) |
| `page.default_page_size` / `max_page_size` | 50 / 500 | сторінки `/materials`, `/errors`, `/connections` |
| `collector.history_page_size` | 100 | повідомлень за запит історії (Telegram віддає ≤ 100) |
| `collector.changes_page_size` | 100 | оновлень за запит `getChannelDifference` |
| `collector.max_wait_ms` | 30000 | верхня межа long-poll `wait_ms` |
| `collector.long_poll_interval_ms` | 100 | як часто long-poll перевіряє нові матеріали |
| `collector.backpressure_poll_ms` | 1000 | як часто призупинений збір перевіряє буфер |
| `collector.gc_interval_seconds` | 3600 | прибирання прострочених зборів і транзитних файлів |

Групи `jobs`, `idempotency`, `page`, `collector` — внутрішні (їх немає в контракті; у `limits` запиту чи правил ігноруються).

## Поведінка

**Матеріал** повідомлення: `material_id = tg:<channel_id>:<message_id>` (однаковий для всіх спостережень),
новий `observation_id` на кожне читання, `locator.url` = `https://t.me/<username>/<id>` (або `t.me/c/...`),
`published_at`, `edited_at`, вміст — текст (`text/plain`, UTF-8), `revision.sequence` = `edit_date` (або `date`)
в секундах epoch, `revision.is_edit` = Telegram позначив повідомлення відредагованим,
`revision.content_sha256` — sha256 тексту, `discovery.strategy` — `telegram_history` / `telegram_updates`,
`metadata` — перегляди, підпис автора, опис медіа; медіа (якщо `media.download`) — `attachments`.

**Режими** (`CollectionRequest.mode`):
- `full` — історія каналу (`history.since`, `history.from_message_id`) від старих до нових; кожне повідомлення —
  нове спостереження. `pts` каналу на початку запам'ятовується, тож наступний інкрементальний збір побачить
  і редагування, зроблені під час читання історії.
- `incremental` — з курсора: `getChannelDifference` від `pts` дає нові (`updates.new_messages`) і відредаговані
  (`updates.edits`) повідомлення. Без курсора — як `full`. Якщо Telegram відповідає «difference too long»,
  нові повідомлення читаються з історії після `last_message_id`, а в `/errors` з'являється запис, що
  редагування в проміжку недоступні.

**Редагування ≠ повторна доставка.** Редагування — нове спостереження того самого `material_id` з більшим
`revision.sequence`, `is_edit: true` і новим вмістом. Повторна доставка тієї самої ревізії джерелом (та сама
`sequence` і текст — наприклад, оновлення, повторене після рестарту) в інкрементальному режимі не видається
(`stats.duplicates`); два редагування в одну секунду з різним текстом — різні ревізії. Технічна повторна
доставка непідтвердженого матеріалу споживачу має **той самий** `observation_id` (at-least-once).

**Курсори** (`GET /v1/states/{state_key}` → `cursors.<channel_id>`): `last_message_id`, `last_edit_date`, `pts`.
`DELETE /v1/states/{state_key}` скидає курсори й відомі ревізії (наступний збір — з нуля).

**Відновлення.** Кожне видане повідомлення комітиться однією транзакцією разом із прогресом збору, курсором,
відомою ревізією й статистикою. Після kill інший (або той самий) процес на тому самому `STATE_DIR` перехоплює
збір після `LEASE_SECONDS` і продовжує рівно після останнього виданого повідомлення.

**Flood-wait.** Очікування до `telegram.max_flood_wait_seconds` пересиджується (heartbeat працює далі);
довше — збір завершується `failed` з `rate_limited` (`retryable: true`, `retry_after_seconds`), курсор
збережено, наступний збір продовжує. `POST /v1/fetches` ніколи не чекає: 429 з `Retry-After`.
Тимчасові помилки й тайм-аути повторюються за `retries`, потім — `source_unavailable` (`retryable: true`).
Недоступний канал — запис `not_found` у `/errors`, інші канали збираються далі. Відхилена сесія —
`source_unavailable` з `details.reason = account_unauthorized`.

**Backpressure.** Якщо непідтверджених матеріалів ≥ `queue.max_unacked_materials`, збір чекає
(`paused_by_backpressure: true`); `GET .../materials?after=<cursor>` підтверджує все до курсора.

**Кілька екземплярів** (один вузол, спільний `STATE_DIR`): збір виконує власник lease; heartbeat
(`HEARTBEAT_INTERVAL_MS`) продовжує lease і помічає скасування з іншого екземпляра; кожен запис збору
перевіряє lease (fencing) — «завислий» власник після пробудження нічого не запише. Читати матеріали,
підтверджувати, скасовувати й повторювати `POST /v1/collections` з тим самим `Idempotency-Key` можна через
будь-який екземпляр. Між вузлами стан не спільний (ADR-0007: v1 одновузловий).

## Підключення (обліковий запис)

`PUT /v1/connections/{id}` з `kind: telegram_account` (ADR-0006). Секрети — лише `secret_refs`
(`env:VAR`, `file:/run/secrets/x`), їх розв'язує колектор у своєму середовищі безпосередньо перед відкриттям
клієнта; значення не зберігаються й не повертаються. Секретоподібні `params` → 422 `secret_detected`.
`POST /v1/connections/{id}/test` показує `secrets_resolved`. Для `telethon`:

```json
{"connection_id": "tg-main", "kind": "telegram_account",
 "params": {"api_id": 123456},
 "secret_refs": {"api_hash": "env:TG_API_HASH", "session": "env:TG_SESSION"}}
```

`session` — Telethon `StringSession` уже авторизованого облікового запису (створюється поза сервісом;
інтерактивного входу немає). Правила називають підключення в `account_connection_id`.

## Записи каналів (бекенд `recorded`)

`<RECORDINGS_DIR>/<username або channel_id>.json` — формат описано в
[recorded.py](src/jane_telegram_collector/recorded.py) (`channel`, `messages`, `events` з `pts`, `min_pts`,
`required_secrets`, `faults` для flood-wait/затримок/збоїв). Файл перечитується на кожен виклик, тож його
можна доповнювати під час роботи (`Recording.post/edit` у `testing.py`).

## Приклад виклику зі стороннього застосунку

```python
import uuid
import httpx

rules = {"collector": "telegram", "channels": [{"username": "city_events_example"}],
         "updates": {"new_messages": True, "edits": True}}
with httpx.Client(base_url="http://127.0.0.1:8102") as api:
    job = api.post("/v1/collections", headers={"Idempotency-Key": str(uuid.uuid4())},
                   json={"source_kind": "telegram", "rules": rules, "mode": "incremental",
                         "state_key": "city-events"}).json()
    after = None
    while True:
        page = api.get(f"/v1/collections/{job['job_id']}/materials",
                       params={"wait_ms": 5000, **({"after": after} if after else {})}).json()
        for m in page["items"]:
            print(m["material_id"], m["revision"]["is_edit"], m["content"]["data"])
        after = page["next_cursor"] or after
        if page["end_of_stream"]:
            api.get(f"/v1/collections/{job['job_id']}/materials", params={"after": after})  # підтвердити останню сторінку
            break
```

## Обмеження

- Бекенд `telethon` не перевірено на реальному сервісі (немає тестового облікового запису).
- Канали одного збору читаються послідовно; паралельність — кількома зборами (`jobs.max_concurrent_jobs`).
- `revision.content_sha256` рахується за текстом; зміна лише медіа видно за `sequence`, не за хешем.
- Стан — SQLite на одному вузлі; спільного сховища для кількох вузлів немає.
