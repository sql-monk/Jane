# Конфігурація Orchestrator

Процес налаштовується змінними середовища з префіксом `JANE_ORCHESTRATOR_` (модель — [settings.py](../../../services/orchestrator/src/jane_orchestrator/settings.py)). Вкладені поля розділяються `__`, списки й об'єкти передаються як JSON. Ліміти виконання завдань — окремий документ у базі, який змінюється через API без перезапуску.

## Зміст

- [Процес](#процес)
- [Режими API і воркера](#режими-api-і-воркера)
- [Автентифікація](#автентифікація)
- [Виконавці](#виконавці)
- [Ліміти завдань](#ліміти-завдань)
- [Внутрішні параметри черги](#внутрішні-параметри-черги)
- [Як застосовуються зміни](#як-застосовуються-зміни)

## Процес

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_ORCHESTRATOR_DATABASE_URL` | DSN PostgreSQL | `postgresql://jane@127.0.0.1:5432/jane_orchestrator` | Власна база; єдина обов'язкова залежність |
| `JANE_ORCHESTRATOR_HOST` | рядок | `127.0.0.1` | Адреса HTTP-сервера; в образі — `0.0.0.0` |
| `JANE_ORCHESTRATOR_PORT` | ціле | `8109` | Порт HTTP; в образі — `8000` |
| `JANE_ORCHESTRATOR_EXECUTORS` | JSON-список | `[]` | Виконавці ([нижче](#виконавці)) |
| `JANE_ORCHESTRATOR_EXECUTORS_FILE` | шлях | — | JSON-файл зі списком виконавців; додається до `EXECUTORS` |
| `JANE_ORCHESTRATOR_SERVICE_TOKEN_REF` | `env:VAR` або `file:/path` | — | Bearer-токен Orchestrator для виконавців без власного `token_ref` |
| `JANE_ORCHESTRATOR_SCHEDULER_ENABLED` | bool | `true` | Чи створюють воркери цього процесу запуски за розкладом |
| `JANE_ORCHESTRATOR_RUN_WORKERS` | bool | `true` | Чи запускати воркери всередині процесу API |
| `JANE_ORCHESTRATOR_LIMITS_FILE` | шлях | — | Файл `PlatformLimits` для першого заповнення документа лімітів |
| `JANE_ORCHESTRATOR_CONTRACTS_DIR` | шлях | `JANE_CONTRACTS_DIR` або `contracts/` checkout | JSON Schema для перевірки запитів |
| `JANE_ORCHESTRATOR_LOG_LEVEL` | рядок | `INFO` | Рівень журналу |
| `JANE_ORCHESTRATOR_LOG_FORMAT` | `json` або `console` | `json` | Формат журналу |
| `JANE_ORCHESTRATOR_METRICS_ENABLED` | bool | `true` | Ендпоінт `/metrics` і лічильники черги |
| `JANE_ORCHESTRATOR_HEALTH_CHECK_TIMEOUT_MS` | ціле | `2000` | Ліміт часу перевірки `database` у `/v1/health` |
| `JANE_ORCHESTRATOR_INSTANCE_ID` | рядок | хост-PID-випадковий суфікс | Ім'я екземпляра в журналах і власника lease (`<instance>-w<N>`) |
| `JANE_ORCHESTRATOR_SERVICE_NAME` | рядок | `orchestrator` | Ім'я сервісу в журналах і `/v1/info` |

`INSTANCE_ID` має бути унікальним для кожного процесу: за ним воркер перевіряє, що lease належить саме йому. Типове значення таке й є; задавайте вручну лише унікальні імена.

## Режими API і воркера

| Запуск | Що працює |
|---|---|
| `python -m jane_orchestrator` | HTTP API і `LIMITS__ENGINE__WORKERS` потоків-воркерів (типово 2) |
| `python -m jane_orchestrator` з `RUN_WORKERS=false` | Лише HTTP API: запуски створюються, але стоять у `queued` |
| `python -m jane_orchestrator worker` | Лише воркери, без HTTP; щонайменше один потік, навіть якщо `WORKERS=0` |

Кожен воркер по черзі бере подачу матеріалів запуску, елемент етапу, а раз на `LIMITS__ENGINE__SCHEDULER_INTERVAL_MS` — розклади (якщо `SCHEDULER_ENABLED=true`), синхронізацію підключень і бюджетів та закриття завислих запусків. Синхронізація й закриття запусків виконуються навіть за `SCHEDULER_ENABLED=false`.

Процесів API й воркерів може бути скільки завгодно: вони ділять одну базу, а lease не дає двом воркерам виконати ту саму роботу. Типові конфігурації — в [operations.md](operations.md#масштабування).

## Автентифікація

Спільний механізм `jane-kit` (bearer-токени, ADR-0005). Режим — `JANE_ORCHESTRATOR_AUTH_MODE`:

| Режим | Налаштування | Примітка |
|---|---|---|
| `none` (типово) | — | Усі виклики мають усі права, `actor` в аудиті — `anonymous`; лише для loopback (інакше потрібен `AUTH_NONE_ALLOW_REMOTE=true`) |
| `api_key` | `API_KEYS` або `API_KEYS_FILE`: `[{"name", "sha256" або "secret_ref", "scopes"}]` | Зберігаються лише хеші ключів; так працює dev-стек |
| `jwt` | `JWT_JWKS_URL`, `JWT_ISSUER`, `JWT_AUDIENCE`, інші `JWT_*` | Для розгортань з провайдером ідентичності |

Права (scopes):

| Scope | Операції |
|---|---|
| `orchestrator:read` | Усі `GET`, `POST /v1/task-validations` |
| `orchestrator:write` | Джерела, завдання, запуски, скасування, активації, повторна обробка, групи проблем |
| `orchestrator:admin` | `PUT`/`DELETE /v1/connections/{id}`, `PUT /v1/limits/platform`; також дає read і write |

`/v1/health` доступний без токена, `/metrics` — без токена, доки `METRICS_PUBLIC=true`. Ім'я ключа (`name`) записується в `requested_by` запуску та `actor` аудиту.

## Виконавці

Список об'єктів `Executor` у `JANE_ORCHESTRATOR_EXECUTORS` або файлі `EXECUTORS_FILE`:

| Поле | Обов'язкове | Значення |
|---|---|---|
| `executor` | так | Унікальне ім'я; з'являється в журналах, синхронізації підключень, `GET /v1/executors` |
| `role` | так | `collector`, `handler`, `storage_read`, `registry`, `llm`, `assistant` |
| `base_url` | так | Базова адреса API виконавця |
| `capabilities` | ні | Правила вибору ([нижче](#можливості-capabilities)) |
| `sync_connections` | ні | Надсилати підключення цьому виконавцю; типово `true` для `collector`, `handler`, `llm` |
| `token_ref` | ні | `env:VAR` або `file:/path` з bearer-токеном для цього виконавця |
| `token` | ні | Токен відкритим текстом; застаріле, пишеться попередження. Разом з `token_ref` — помилка |

Порядок вибору токена: `token_ref` → `token` → `SERVICE_TOKEN_REF`. Нерозв'язне посилання зупиняє старт; виконавець без жодного токена дає попередження `executor has no bearer token`.

### Можливості (capabilities)

| Ключ | Роль | Значення |
|---|---|---|
| `collector` | `collector` | Ім'я колектора, яке вказують у `stages[collect].collector.collector` (`web`, `telegram`) |
| `packages` | `handler`, `llm` | Glob-шаблони `package_id`, що йдуть на цього виконавця, наприклад `jane.storage-*` |
| `handler_kinds` | `handler`, `llm` | Типи пакетів (`kind` з Registry): `storage`, `extractor`, `transform`, `llm` |
| `default` | `handler`, `llm` | `true` — виконавець за замовчуванням для інших пакетів |
| `connections` | `handler` | `false` — виконавець не приймає підключень (рівнозначно `sync_connections: false`) |

Приклад для локальних процесів (з [quickstart](quickstart.md)):

```json
[
  {"executor": "web-collector", "role": "collector", "base_url": "http://127.0.0.1:18611",
   "capabilities": {"collector": "web"}, "sync_connections": false},
  {"executor": "storage", "role": "handler", "base_url": "http://127.0.0.1:18612",
   "capabilities": {"packages": ["jane.storage-*"], "handler_kinds": ["storage"]}},
  {"executor": "storage-read", "role": "storage_read", "base_url": "http://127.0.0.1:18612",
   "sync_connections": false}
]
```

Повний набір для dev-стеку — у [compose.local.example.yaml](../../../infra/compose.local.example.yaml). Web Collector приймає лише підключення типу `http`; якщо підключення іншого типу надсилається йому, синхронізація стає `failed` — тому в прикладі вона вимкнена.

## Ліміти завдань

Ліміти за контрактом [limits.schema.json](../../../contracts/schemas/common/limits.schema.json) зливаються за рівнями `platform → source → task → stage → request`: нижчий рівень перекриває вищий, `null` значенням не вважається, числа обмежуються `hard_caps` документа платформи. Ефективні значення з походженням кожного поля повертає `GET /v1/limits/effective?source_id=&task_id=&stage_id=`.

Документ рівня `platform` зберігається в базі. Під час першого старту його заповнює `LIMITS_FILE` (формат `PlatformLimits`, наприклад [deploy/profiles/single-node.json](../../../deploy/profiles/single-node.json)) або типові значення з профілем `orchestrator-defaults`. Далі він змінюється лише через `PUT /v1/limits/platform` (scope `orchestrator:admin`, `If-Match`), зміна пишеться в аудит.

Поля, які Orchestrator використовує сам:

| Поле | Типово | Рівень, з якого береться | Вплив |
|---|---|---|---|
| `queue.max_queue_depth` | 10000 | task | Найбільше активних елементів завдання; далі подача стоїть (backpressure) |
| `queue.max_inflight_materials` | 100 | task | Найбільше спостережень запуску з активними елементами |
| `concurrency.max_parallel_runs_per_task` | 1 | task | Одночасні запуски завдання за `overlap: allow` |
| `concurrency.max_parallel_stage_items` | 4 | stage | Одночасні виклики етапу в межах запуску |
| `timeouts.invocation_timeout_ms` | 60000 | stage | Час виклику обробника, включно з опитуванням його job |
| `timeouts.run_timeout_ms` | 21600000 | task | Найдовший запуск; далі `failed` з кодом `timeout` |
| `retries.*` | 3 спроби, 1000–60000 мс, ×2, jitter | stage; task; collect | Повтори елементів; повтор подачі; перезапуски колекції за `rate_limited` |
| `crawl.max_seed_urls` | не задано | collect stage | Якщо задано: більше URL у `input.urls` → `422 limit_exceeded` під час створення запуску |
| `llm.budget`, `llm.max_requests_per_minute` | — | source, task | Синхронізуються в LLM gateway як бюджети `source/{id}` і `task/{id}` |

`retries` і `limits.retries` завдання й етапу зливаються: поле `retries` має перевагу над `limits.retries` того самого рівня. Решта полів (`crawl`, `rate`, `sandbox`, `llm` тощо) Orchestrator лише передає виконавцям: ефективні ліміти етапу йдуть у `limits` виклику обробника, ліміти етапу `collect` — у `limits` запиту колекції.

`timeouts.connect_timeout_ms` і `timeouts.request_timeout_ms` для HTTP-клієнта виконавців беруться не з документа платформи, а з налаштувань процесу: `JANE_ORCHESTRATOR_LIMITS__CONTRACT__TIMEOUTS__CONNECT_TIMEOUT_MS` і `…__REQUEST_TIMEOUT_MS` (типово 5000 і 30000).

Змінні `JANE_ORCHESTRATOR_LIMITS__CONTRACT__*` (наприклад `…__QUEUE__MAX_QUEUE_DEPTH`) задають запасні значення й зміст документа платформи під час першого старту без `LIMITS_FILE`. Після цього документ у базі має перевагу: змінювати його треба через API.

## Внутрішні параметри черги

Не входять у контракт; змінюються лише змінними `JANE_ORCHESTRATOR_LIMITS__ENGINE__<NAME>` і перезапуском.

| Параметр | Типово | Вплив |
|---|---|---|
| `WORKERS` | 2 | Потоків-воркерів у процесі (0 — API без воркерів) |
| `LEASE_MS` | 30000 | Lease елемента, подачі й синхронізації; продовжується heartbeat-ом |
| `HEARTBEAT_MS` | 10000 | Період продовження lease під час виклику |
| `POLL_INTERVAL_MS` | 500 | Пауза воркера, коли роботи немає |
| `FEED_PAGE_SIZE` | 100 | Найбільше матеріалів, що запитуються в колектора за раз |
| `FEED_WAIT_MS` | 1000 | `wait_ms` довгого опитування сторінки матеріалів |
| `BACKPRESSURE_RECHECK_MS` | 500 | Повторна перевірка подачі за повної черги чи очікування черги запусків |
| `SCHEDULER_INTERVAL_MS` | 1000 | Період розкладів, синхронізацій і закриття запусків |
| `SYNC_RETRY_MS` | 5000 | Затримка перед повтором синхронізації підключення чи бюджету |
| `SYNC_MAX_ATTEMPTS` | 5 | Спроб синхронізації до стану `failed` |
| `EXECUTOR_HEALTH_TIMEOUT_MS` | 2000 | Ліміт перевірки здоров'я виконавця в `GET /v1/executors` |
| `EXECUTOR_KEEPALIVE_EXPIRY_MS` | 4000 | Простій, після якого з'єднання з виконавцем закривається; має бути менше за keep-alive виконавців (5 с) |
| `EXECUTOR_STALE_CONNECTION_RETRIES` | 1 | Повторне надсилання безпечного запиту, якщо виконавець закрив з'єднання без відповіді; спроб елемента не витрачає |
| `JOB_POLL_INTERVAL_MS` | 500 | Опитування `202`-job обробника |
| `IDEMPOTENCY_IN_PROGRESS_POLL_MS` | 500 | Повтор запиту, поки обробник ще виконує ту саму доставку |
| `IDEMPOTENCY_IN_PROGRESS_MAX_WAIT_MS` | 120000 | Скільки один воркер чекає таку доставку, перш ніж відкласти елемент |
| `IDEMPOTENCY_IN_PROGRESS_RETRY_MS` | 5000 | Через скільки відкладений елемент перевіряється знову |
| `MAX_LEASE_RECLAIMS` | 5 | Перехоплень простроченого lease, після яких елемент `failed` як отруйний |
| `PROBLEM_SAMPLES` | 10 | Прикладів у групі проблем |
| `TRACE_OUTPUTS_MAX` | 100 | Посилань на результати елемента в простежуваності |
| `ATTEMPT_HISTORY_MAX` | 20 | Подій `attempt_history` на елемент (зберігаються перші) |
| `STORED_SELECTION_MAX_IDS` | 10000 | Найбільше `object_ids` чи `observation_ids` у повторній обробці; більше — `422 limit_exceeded` |
| `STORED_MATERIAL_IDS_PER_REQUEST` | 100 | До скількох `material_ids` передається Storage як фільтр; більше — фільтрація в Orchestrator |
| `DB_POOL_MAX` | 10 | Розмір пулу з'єднань з базою на процес |
| `SCHEDULE_BATCH` | 20 | Завдань за один прохід розкладу |
| `REAP_BATCH` | 50 | Запусків за один прохід закриття |

Інші групи процесу:

| Змінна | Типово | Вплив |
|---|---|---|
| `JANE_ORCHESTRATOR_LIMITS__IDEMPOTENCY__IDEMPOTENCY_TTL_SECONDS` | 86400 | Скільки пам'ятається `Idempotency-Key` запитів до API |
| `JANE_ORCHESTRATOR_LIMITS__CLAIMS__IN_PROGRESS_LEASE_MS` | 900000 | Через скільки незавершений запит зупиненого екземпляра можна повторити з тим самим ключем |
| `JANE_ORCHESTRATOR_LIMITS__CLAIMS__HEARTBEAT_INTERVAL_MS` | 15000 | Як часто екземпляр продовжує свої незавершені ключі |
| `JANE_ORCHESTRATOR_LIMITS__PAGES__DEFAULT_PAGE_SIZE` | 50 | `limit` списків за замовчуванням |
| `JANE_ORCHESTRATOR_LIMITS__PAGES__MAX_PAGE_SIZE` | 500 | Найбільший `limit` списків |

Ефективні значення всіх параметрів процесу пишуться в журнал під час старту (подія `orchestrator started`, поле `limits`).

## Як застосовуються зміни

| Що змінюється | Як застосувати | Коли діє |
|---|---|---|
| Джерело, завдання | `PUT` з `If-Match` | Для нових запусків: запуск зберігає знімок конфігурації, джерела й лімітів |
| Розклад завдання | `PUT /v1/tasks/{task_id}` | Наступний час запуску перераховується одразу |
| Версія пакета в етапі | `POST /v1/tasks/{task_id}/stages/{stage_id}/activations` | Для нових запусків |
| Документ лімітів платформи | `PUT /v1/limits/platform` | Для нових запусків; поточні працюють зі своїм знімком |
| Підключення | `PUT /v1/connections/{connection_id}` | Після синхронізації з виконавцями (`sync_status: synced`) |
| Змінні середовища, виконавці | перезапуск процесу | Після старту |
