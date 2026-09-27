# Orchestrator (WP-09)

Оркестратор поєднує автономні сервіси Jane в налаштовані процеси: джерела, завдання (DAG етапів з умовами
й розгалуженням), зафіксовані версії пакетів, одноразові запуски й розклади, черга етапів у власній
PostgreSQL (`SELECT … FOR UPDATE SKIP LOCKED`) з воркерами на lease, передавання даних за посиланнями
(`ContentRef`), підтвердження, повтори, відновлення, скасування, повторна обробка RAW, простежуваність,
маршрутизація матеріалів до екстракторів за прив'язками, реєстр підключень, активації з аудитом, ліміти.

Контракт: [`contracts/openapi/orchestrator.v1.yaml`](../../contracts/openapi/orchestrator.v1.yaml) (конвенції —
скіл `jane-contracts`). Сусіди — лише через їхні API: `collector.v1`, `handler.v1`, `storage.v1`
(читання збережених RAW), `registry.v1` (перевірка версій). Оркестратор володіє лише своєю БД
(`jane_orchestrator`) і не зберігає вмісту матеріалів — лише ідентифікатори й посилання; транзитний вхід
елемента черги (Material з `ContentRef`, сутності) очищається, щойно елемент завершено.

## Незалежний запуск

Потрібна PostgreSQL (наприклад, dev-стек: `just up postgres`, адреса — `just env`).

```
uv sync --all-packages
set JANE_ORCHESTRATOR_DATABASE_URL=postgresql://jane:<пароль>@127.0.0.1:<порт>/jane     # Linux: export …
set JANE_ORCHESTRATOR_EXECUTORS=[{"executor":"web-collector","role":"collector","base_url":"http://127.0.0.1:8101","capabilities":{"collector":"web"}}, …]
uv run --package jane-orchestrator python -m jane_orchestrator            # API + воркери, порт 8109
uv run --package jane-orchestrator python -m jane_orchestrator worker     # лише воркери (окремий процес)
curl http://127.0.0.1:8109/v1/health
```

Docker (контекст — корінь репозиторію; образ містить `contracts/` для валідації запитів):

```
docker build -f services/orchestrator/Dockerfile -t jane-orchestrator .
docker run --rm -p 8109:8000 -e JANE_ORCHESTRATOR_DATABASE_URL=postgresql://… jane-orchestrator
```

**Кілька екземплярів.** API й воркери можна запускати будь-якою кількістю процесів/контейнерів на одну БД:
черга, lease, ключі ідемпотентності (`Idempotency-Key`), розклади (блокування рядка завдання) і синхронізація
підключень координуються через PostgreSQL. Схема мігрує сама під advisory lock.

## Як це працює

| Робота | Механізм |
|---|---|
| Збір (feed) | Запуск збору в колекторі (`Idempotency-Key: run:<run_id>:collect` — повтор після збою не створює другого збору), вибірка сторінок `GET /v1/collections/{id}/materials?after=`; елементи етапів створюються в одній транзакції з курсором, наступна вибірка підтверджує сторінку. Повторно видане спостереження (`observation_id`) не створює другого елемента |
| Backpressure | Перед вибіркою: `queue.max_queue_depth` (активні елементи завдання) і `queue.max_inflight_materials` (матеріали запуску в обробці). Якщо місця немає — вибірка не робиться (`Run.backpressure=true`), буфер колектора (`queue.max_unacked_materials`, передається в запиті збору) заповнюється, і колектор призупиняє обхід |
| Етап (item) | Воркер бере елемент з lease (`FOR UPDATE SKIP LOCKED`), викликає `POST /v1/invocations` з `delivery_key = sha256(run_id|stage_id|item_key)` як `Idempotency-Key`, heartbeat подовжує lease. Результат, наступні елементи й позначка завершення — одна транзакція. Після kill воркера lease спливає, інший воркер повторює з тим самим ключем, виконавець повертає збережений результат (`duplicate: true`) — без подвійного ефекту. Перехоплення простроченого lease **не** витрачає `retries.max_attempts` (ефект міг відбутися); «отруйний» елемент, на якому воркери гинуть знову й знову, падає після `engine.max_lease_reclaims` перехоплень |
| Повтори | `RetryPolicy` (platform → source → task(`retries`) → stage): лише для retryable-помилок (HTTP 409/429/5xx, `failure.retryable`), backoff із jitter, той самий ключ. Остаточна помилка → `on_failure`: `continue` (проблема записується) або `fail_run` |
| DAG | `inputs[].from`, `select` (`output`, `input_material`, `problems`, `unmatched_materials`), умови `when` (`material.*`, `result.*`, `entity.*` — фільтр сутностей) |
| Прив'язки | Етап із `bindings` отримує матеріал, що відповідає хоча б одній прив'язці (у прив'язці всі задані властивості — І). Матеріал, що не відповідає жодній прив'язці жодного етапу, — «невідомий»: реєструється (`/v1/unknown-materials`) і доставляється споживачам `unmatched_materials` **лише** за ефективного `forward_unknown_to_llm=true` (завдання, інакше джерело, типово false) |
| Розклади | `manual`, `once`, `cron` (5 полів, IANA-зона), `interval` (перший запуск — `start_at` або через інтервал); `overlap: skip/queue/allow` (+ `max_parallel_runs_per_task`). Створення запуску й перехід `queued → running` серіалізуються per task (`pg_advisory_xact_lock`), тож ліміт діє для будь-якої кількості воркерів і екземплярів; черга — FIFO |
| Скасування | `POST /v1/runs/{id}/cancel` = `/v1/jobs/{id}/cancel`: черга елементів скасовується, збір у колекторі скасовується, записане не відкочується |
| Прибирання | Кожен воркер періодично (`scheduler_interval_ms`) закриває запуски, які інакше ніхто б не закрив: `cancelling` чи вичерпані (`feed_done`) запуски, чий воркер помер (елементи з простроченим lease скасовуються), і запуски понад `timeouts.run_timeout_ms` у будь-якій фазі (`failed`, код `timeout`) |
| Повторна обробка | `POST /v1/reprocessing`: збережені RAW з `storage.v1 GET /v1/objects` (+ `GET /v1/objects/{id}` → Material) подаються на `from_stage` (або як вихід collect) |
| Простежуваність | `/v1/materials/{id}/trace`: спостереження → етапи → `invocation_id`, стан, версія пакета (з digest), виходи (ключі сутностей, `object_id`, підключення) |
| Активації | `POST …/stages/{stage}/activations`: `activate` (версія `approved` у registry), `rollback` (до попередньої або вказаної), `auto_activate` (лише якщо `change_policy.llm_versions=auto_after_checks`, `auto_changes_allowed`, `test_status=passed`; інакше 403 з `details.reason`). Аудит — `/v1/audit-events` |
| Підключення | `/v1/connections`: лише несекретні `params` і `secret_refs` (секретоподібні `params` → 422 `secret_detected`); синхронізація `PUT/DELETE /v1/connections/{id}` у колектори, обробники й llm — асинхронно з повторами, стан у `executors[]`. Оркестратор не розв'язує `secret_refs` і не має значень секретів: виконавцям пересилається той самий документ |
| Бюджети LLM | `limits.llm.budget` і `limits.llm.max_requests_per_minute` джерела/завдання синхронізуються в LLM-шлюз (`llm.v1 PUT /v1/budgets/{source\|task}/{id}`, `BudgetDefinition`) при створенні/зміні; прибраний бюджет або видалений об'єкт → `DELETE` (діє успадкований). Асинхронно, ідемпотентно, з повторами (`sync_retry_ms`, `sync_max_attempts`) |

## Конфігурація

Змінні середовища з префіксом `JANE_ORCHESTRATOR_`:

| Параметр | Типово | Опис |
|---|---|---|
| `DATABASE_URL` | `postgresql://jane@127.0.0.1:5432/jane_orchestrator` | власна БД |
| `EXECUTORS` / `EXECUTORS_FILE` | `[]` | виконавці (JSON: `executor`, `role` = collector/handler/storage_read/registry/llm, `base_url`, `capabilities`, `sync_connections`, `token`). Маршрутизація пакета: `capabilities.packages` (glob id пакета) → тип пакета з registry ↔ `handler_kinds` → `default: true` |
| `CONTRACTS_DIR` | `JANE_CONTRACTS_DIR` або `contracts/` checkout | схеми для валідації запитів |
| `LIMITS_FILE` | — | `PlatformLimits` (TOML/JSON/YAML, напр. профіль WP-14) для **першого** заповнення лімітів платформи в БД; далі — `PUT /v1/limits/platform` |
| `AUTH_MODE` | `none` | `none` \| `api_key` (`API_KEYS=[{"name","sha256","scopes"}]`, scopes `orchestrator:read/write/admin`) |
| `RUN_WORKERS` / `SCHEDULER_ENABLED` | `true` / `true` | воркери в процесі API; планувальник |
| `PORT`, `HOST`, `LOG_LEVEL`, `LOG_FORMAT` | `8109`, `127.0.0.1`, `INFO`, `json` | процес |

## Ліміти

Ліміти контракту (`limits.schema.json`) — документ платформи в БД (`GET/PUT /v1/limits/platform`), злиття
platform → source → task → stage → request (`RunRequest.limits`), `hard_caps` платформи обмежують усе;
`GET /v1/limits/effective?source_id=&task_id=&stage_id=` показує значення й походження. Запуск фіксує
ефективні ліміти на старті (нові значення — для нових запусків). Колектору передаються ліміти collect-етапу,
обробникам — ліміти етапу. Зміна лімітів не потребує змін у коді (тест `test_changing_limits_needs_no_code_change`).

Резервні значення полів, які оркестратор використовує сам (рівень `platform`, якщо документ їх не задає;
також перше заповнення документа платформи, коли `LIMITS_FILE` не задано; env `…_LIMITS__CONTRACT__<ГРУПА>__<ПОЛЕ>`):

| Ліміт | Типово |
|---|---|
| `queue.max_queue_depth` / `queue.max_inflight_materials` | 10000 / 100 |
| `concurrency.max_parallel_runs_per_task` / `max_parallel_stage_items` | 1 / 4 |
| `timeouts.connect_timeout_ms` / `request_timeout_ms` / `invocation_timeout_ms` / `run_timeout_ms` | 5000 / 30000 / 60000 / 21600000 |
| `retries` (`max_attempts`, `initial_backoff_ms`, `max_backoff_ms`, `backoff_multiplier`, `jitter`) | 3, 1000, 60000, 2.0, true |
| `transfer.idempotency_ttl_seconds` | 86400 |

Внутрішні параметри рушія (`…_LIMITS__ENGINE__<ПОЛЕ>`):

| Параметр | Типово | Опис |
|---|---|---|
| `workers` | 2 | потоків-воркерів у процесі |
| `lease_ms` / `heartbeat_ms` | 30000 / 10000 | lease елемента/збору та його подовження |
| `poll_interval_ms` | 500 | пауза воркера без роботи |
| `feed_page_size` / `feed_wait_ms` | 100 / 1000 | розмір сторінки матеріалів і long-poll колектора |
| `backpressure_recheck_ms` | 500 | повторна перевірка заповненої черги |
| `scheduler_interval_ms` | 1000 | перевірка розкладів |
| `sync_retry_ms` / `sync_max_attempts` | 5000 / 5 | синхронізація підключень |
| `executor_health_timeout_ms` | 2000 | `/v1/executors` → статус |
| `job_poll_interval_ms` | 500 | опитування 202-job виконавця |
| `problem_samples` / `trace_outputs_max` | 10 / 100 | зразки в групі проблем / посилання виходів на елемент |
| `db_pool_max` | 10 | з'єднань із БД на процес |
| `max_lease_reclaims` | 5 | перехоплень простроченого lease до позначення елемента `failed` (не спроби `retries`) |
| `schedule_batch` | 20 | завдань, що стали запусками за один прохід планувальника |
| `reap_batch` | 50 | запусків за один прохід прибирання |

Ліміти сторінок: `…_LIMITS__PAGES__DEFAULT_PAGE_SIZE` = 50, `MAX_PAGE_SIZE` = 500.

## Тести

```
just test orchestrator                        # unit + contract (PostgreSQL: див. нижче)
just test orchestrator -m integration         # «Готово, коли» і функції: kill воркера, кілька воркерів, …
just up postgres --project jane-wp09 && just integration --project jane-wp09 services/orchestrator
```

PostgreSQL для тестів: `JANE_ORCHESTRATOR_TEST_DSN` → dev-стек цього checkout (`just up`) → власний
контейнер `postgres:18` через Docker (прибирається після тестів); інакше тести з БД пропускаються. Кожен тест
отримує окрему базу. Сусіди — фейки з контрактів (`tests/orch_support.py`): кожен запит оркестратора й кожна
відповідь фейка перевіряються за OpenAPI сусіда. Оркестратор не мокається.

## Приклад виклику зі стороннього застосунку

```python
import httpx, uuid

api = httpx.Client(base_url="http://127.0.0.1:8109")
api.post(
    "/v1/sources",
    json={
        "source_id": "shop",
        "kind": "web",
        "title": "Shop",
        "locator": {"url": "https://shop.example.test/"},
        "collector_rules": {"package_id": "shop.web-rules", "version": "1.0.0"},
    },
    headers={"Idempotency-Key": str(uuid.uuid4())},
)
api.post(
    "/v1/tasks",
    json={
        "task_id": "shop-prices",
        "title": "Prices",
        "input": {"source_id": "shop", "urls": ["https://shop.example.test/product/a-1"]},
        "stages": [
            {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web"}},
            {
                "stage_id": "extract",
                "kind": "handler",
                "inputs": [{"from": "collect"}],
                "handler": {"package_id": "shop.price-extractor", "version": "1.0.0"},
            },
        ],
    },
    headers={"Idempotency-Key": str(uuid.uuid4())},
)
job = api.post("/v1/tasks/shop-prices/runs", json={}, headers={"Idempotency-Key": str(uuid.uuid4())}).json()
print(api.get(f"/v1/runs/{job['job_id']}").json()["status"])
```

## Відомі обмеження

- `concurrency.max_parallel_stage_items` — м'яке обмеження (кілька воркерів можуть на мить перевищити його).
- Не застосовуються: `timeouts.stage_timeout_ms`, `timeouts.sync_response_max_ms`, `transfer.job_retention_seconds` (старі запуски не прибираються); ці ліміти лише передаються виконавцям.
- Активація/відкат — лише для `handler`-етапів (не для версій правил колектора).
- `auth_mode=jwt` не реалізовано (`none` — лише локально, `api_key` — працює).

## Журнали й метрики

JSON-журнали (jane-kit) з `trace_id`, `run_id`, `item_id`; `traceparent` передається виконавцям, `trace_id`
запуску — у `context.trace` кожного виклику. `/metrics`: HTTP-метрики jane-kit, `jane_orchestrator_items_total{outcome}`,
`jane_orchestrator_materials_total`, `jane_orchestrator_backpressure_total`, `jane_orchestrator_runs_total{status}`,
`jane_orchestrator_leases_reclaimed_total`. Health: `/v1/health` з перевіркою БД.
