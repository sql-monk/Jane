# Експлуатація Orchestrator

Моніторинг, масштабування, оновлення, резервування й типові проблеми окремого Orchestrator. Параметри, які згадуються тут, описано в [configuration.md](configuration.md).

## Зміст

- [Стан і здоров'я](#стан-і-здоровя)
- [Метрики](#метрики)
- [Журнали](#журнали)
- [Діагностика запусків](#діагностика-запусків)
- [Масштабування](#масштабування)
- [Міграції](#міграції)
- [Оновлення](#оновлення)
- [Резервування й відновлення](#резервування-й-відновлення)
- [Зростання бази](#зростання-бази)
- [Власність даних](#власність-даних)
- [Типові проблеми](#типові-проблеми)

## Стан і здоров'я

| Ендпоінт | Що показує |
|---|---|
| `GET /v1/health` | `status` і перевірка `database` (`SELECT 1` у межах `HEALTH_CHECK_TIMEOUT_MS`); без токена |
| `GET /v1/info` | Версія, `auth_mode`, імена виконавців, `queue: postgresql-skip-locked`, ліміти процесу |
| `GET /v1/executors` | Кожен виконавець зі статусом `ok`, `degraded`, `down` або `unknown` за його `/v1/health` |

Вивід перевірочного запуску (Windows 11, ревізія `48389a3`):

```text
{"status":"ok","checks":{"database":{"status":"ok"}}}
```

`/v1/health` перевіряє лише власну базу: недоступний виконавець здоров'я Orchestrator не змінює, його видно в `GET /v1/executors`. Образ має `HEALTHCHECK` на `/v1/health`.

## Метрики

`GET /metrics` (Prometheus), доки `METRICS_ENABLED=true`. Окрім спільних `jane_http_requests_total`, `jane_http_request_duration_seconds` і `jane_http_requests_in_flight`:

| Метрика | Мітки | Що рахує |
|---|---|---|
| `jane_orchestrator_items_total` | `outcome` | Завершені обробки елементів: `result_status` (`success`, `unrecognized`…), `failed`, `retrying` |
| `jane_orchestrator_materials_total` | — | Матеріали, отримані від колекторів або Storage |
| `jane_orchestrator_backpressure_total` | — | Ітерації подачі, зупинені повною чергою |
| `jane_orchestrator_runs_total` | `status` | Завершені запуски за станом |
| `jane_orchestrator_leases_reclaimed_total` | — | Перехоплення простроченого lease елемента |

Лічильники рахує кожен процес окремо (і процес API з воркерами, і процес `worker`); підсумок — сума по екземплярах. Уривок після запуску з quickstart:

```text
jane_orchestrator_items_total{outcome="success"} 2.0
jane_orchestrator_materials_total 2.0
jane_orchestrator_backpressure_total 0.0
jane_orchestrator_runs_total{status="succeeded"} 1.0
jane_orchestrator_leases_reclaimed_total 0.0
```

На що зважати: зростання `leases_reclaimed_total` — воркери падають або не встигають продовжувати lease; стабільне `backpressure_total` — виконавці не встигають за колектором; `items_total{outcome="retrying"}` — виконавці відповідають повторюваними помилками.

## Журнали

JSON у stdout (`LOG_FORMAT=json`), поля `service`, `instance`, `trace_id`. Основні події:

| Подія | Рівень | Значення |
|---|---|---|
| `orchestrator started` | info | Старт API; поле `limits` — ефективні ліміти процесу, `workers` — потоків |
| `workers started` | info | Старт процесу `worker` |
| `schema migrated` | info | Застосовано міграцію `version` |
| `run created` / `run finished` | info | Створення й завершення запуску (`run_id`, `trigger`, `status`) |
| `item retry scheduled` | info | Повтор елемента (`delay_ms`, `code`) |
| `in-progress delivery parked` | info | Обробник ще виконує ту саму доставку |
| `item lease reclaimed` | info | Перехоплення простроченого lease |
| `item lease lost during invocation` | warning | Воркер втратив lease під час виклику |
| `feed call failed` | warning | Помилка виклику колектора чи Storage під час подачі |
| `collection cancel failed` | warning | Колектор не прийняв скасування колекції |
| `executor has no bearer token` | warning | Виклики виконавця підуть без `Authorization` |
| `worker step failed` | error | Неочікувана помилка кроку воркера (наприклад, недоступна база); крок повторюється |

Запити до виконавців пишуть рядки `httpx` з методом, адресою й статусом. За ними видно цикл подачі: `POST /v1/collections`, далі `GET …/materials` з `after=` — підтвердження попередньої сторінки. Уривок журналу процесу `worker` (формат `console`):

```text
INFO    jane.orchestrator: workers started {"count": 1}
INFO    httpx: HTTP Request: POST http://127.0.0.1:18611/v1/collections "HTTP/1.1 202 Accepted"
INFO    httpx: HTTP Request: GET http://127.0.0.1:18611/v1/collections/job_26455dd2bc944f42880276bc7041fb9d/materials?limit=100&wait_ms=1000 "HTTP/1.1 200 OK"
INFO    httpx: HTTP Request: POST http://127.0.0.1:18612/v1/invocations "HTTP/1.1 200 OK"
INFO    httpx: HTTP Request: GET http://127.0.0.1:18611/v1/collections/job_26455dd2bc944f42880276bc7041fb9d/materials?limit=100&wait_ms=1000&after=c_0000000000000001 "HTTP/1.1 200 OK"
INFO    jane_orchestrator.runs: run finished {"run_id": "run_01M4N6N8GS31411A8HD1VYPK88", "status": "succeeded"}
```

Кожен запуск має `trace_id`; він передається виконавцям у `traceparent` і в `context.trace` виклику, тож журнали всіх сервісів одного запуску зв'язуються.

## Діагностика запусків

| Питання | Запит |
|---|---|
| Стан і прогрес | `GET /v1/jobs/{run_id}` або `GET /v1/runs/{run_id}` (лічильники етапів, `backpressure`, `collection_id`, `error`) |
| Що з елементами етапу | `GET /v1/runs/{run_id}/items?stage_id=&status=` — `attempts`, `available_at`, `attempt_history`, `error` |
| Шлях одного матеріалу | `GET /v1/materials/{material_id}/trace` |
| Повторювані проблеми пакета | `GET /v1/problem-groups?source_id=&status=open` |
| Що змінювали | `GET /v1/audit-events?subject_type=task&subject_id=` |
| Підключення не дійшли | `GET /v1/connections/{connection_id}` — `executors[].sync_status`, `message` |

## Масштабування

| Схема | Налаштування |
|---|---|
| Один процес | `python -m jane_orchestrator` з типовими 2 воркерами |
| API окремо від воркерів | API з `RUN_WORKERS=false`; N процесів `python -m jane_orchestrator worker` з `LIMITS__ENGINE__WORKERS` потоків |
| Кілька екземплярів API | Будь-яка кількість за балансувальником; `Idempotency-Key` спільні через базу |

Усі процеси ділять одну базу; черга, подача, розклади й синхронізації захоплюються з `SKIP LOCKED` і lease, тож подвійної роботи немає. Розклад можна залишити лише в частині процесів (`SCHEDULER_ENABLED=false` в інших) — один запуск на такт гарантується й без цього. Режим API без воркерів і окремий процес `worker` перевірено: запуск, створений через API, лишався `queued`, доки не стартував `worker`, після чого завершився `succeeded`.

Межі масштабування: кожен процес тримає до `DB_POOL_MAX` з'єднань (типово 10) і по одному потоку на воркер плюс потік heartbeat на кожен активний виклик. Паралельність викликів одного етапу запуску обмежує `concurrency.max_parallel_stage_items`, а не кількість воркерів. Профілі лімітів для середовищ розгортання — [deploy/profiles](../../../deploy/profiles/).

## Міграції

Схема оновлюється автоматично під час старту кожного процесу (API й `worker`): міграції з `db.py` застосовуються по черзі під advisory-блокуванням, номер записується в `schema_migrations`. Кілька процесів можуть стартувати одночасно. Міграції лише додають таблиці, колонки й індекси; відкату (down-міграцій) немає.

Поточна схема — версія 7. Перший старт на порожній базі:

```text
INFO    jane_orchestrator.db: schema migrated {"version": 1}
INFO    jane_orchestrator.db: schema migrated {"version": 2}
INFO    jane_orchestrator.db: schema migrated {"version": 3}
INFO    jane_orchestrator.db: schema migrated {"version": 4}
INFO    jane_orchestrator.db: schema migrated {"version": 5}
INFO    jane_orchestrator.db: schema migrated {"version": 6}
INFO    jane_orchestrator.db: schema migrated {"version": 7}
```

## Оновлення

1. Зробіть резервну копію бази ([нижче](#резервування-й-відновлення)).
2. Щоб не залишати незавершених викликів, зупиніть нові запуски й воркери: перезапустіть API з `SCHEDULER_ENABLED=false` і `RUN_WORKERS=false`, зупиніть процеси `worker`, дочекайтесь, поки активні запуски завершаться, або скасуйте їх.
3. Розгорніть нову версію; міграції застосує перший процес, що стартує.
4. Поверніть `SCHEDULER_ENABLED` і `RUN_WORKERS`, запустіть воркери.

Крок 2 бажаний, але не обов'язковий: елемент, що виконувався під час зупинки, після закінчення lease перехопить новий воркер з тим самим `delivery_key`. Пропущені за час простою такти не відтворюються поодинці: завдання, чий `next_run_at` минув, запускається одразу після старту, а далі розклад рахується від поточного часу.

У dev-стеку ці змінні передаються з середовища викликача: `JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false` і `JANE_ORCHESTRATOR_RUN_WORKERS=false` перед `just up` ([infra/compose.yaml](../../../infra/compose.yaml)).

## Резервування й відновлення

Усе стійке Orchestrator зберігає в базі `jane_orchestrator`; локальних файлів немає. Резервна копія — стандартний `pg_dump` цієї бази, відновлення — `pg_restore` у порожню базу з подальшим стартом сервісу. Конкретні команди для dev-стеку не перевірялися в межах цієї документації.

Для узгодженої копії зупиніть воркери й розклади, як у кроці 2 оновлення. Після відновлення зі старої копії:

- запуски, активні на момент копії, продовжаться: lease прострочені, елементи перехоплять воркери з тими самими `delivery_key`, тож ідемпотентні обробники повернуть збережені результати;
- колекції в колекторах можуть уже не існувати — такий запуск завершиться помилкою колектора;
- підключення в реєстрі є, але виконавці могли їх втратити: повторіть `PUT /v1/connections/{connection_id}`.

Секретів база не містить: підключення зберігають лише `secret_refs`, ключі API — лише хеші (в конфігурації процесу, не в базі).

## Зростання бази

Автоматичного видалення старих запусків, елементів, аудиту, груп проблем і реєстру невідомих матеріалів немає; прибираються лише прострочені `Idempotency-Key`. Вхід елемента (`items.payload`) очищується після завершення, тож основний обсяг — рядки `items` (по одному на матеріал і етап) з `attempt_history` та посиланнями на результати. Розмір цих полів обмежують `ATTEMPT_HISTORY_MAX` і `TRACE_OUTPUTS_MAX`. Політику зберігання історії треба визначати під час розгортання; API для видалення запусків немає.

## Власність даних

Orchestrator — єдиний власник бази `jane_orchestrator` ([data-ownership.md](../../../contracts/docs/data-ownership.md)). Він не читає таблиць інших сервісів: RAW і сутності лежать у сховищах, з якими працює Storage, стан обходу — у колекторах, пакети — в Registry. Посилання на збережений RAW (`stored_object_id`) Orchestrator бере з відповіді обробника збереження, а не з бази Storage. Інші сервіси отримують його дані лише через `orchestrator.v1`.

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| `422` з `Idempotency-Key header is required` | `POST` створення без заголовка | Додайте `Idempotency-Key` до `POST /v1/sources`, `/v1/tasks`, `/v1/tasks/{id}/runs`, активацій і `/v1/reprocessing` |
| `409 conflict`: «A run of this task is already in progress» | `overlap: skip` і є активний запуск | Дочекайтесь, скасуйте попередній або задайте `overlap: queue`/`allow` |
| `412 precondition_failed` | `If-Match` не відповідає поточному `ETag` | Перечитайте ресурс і повторіть з новим `ETag` |
| Запуск довго в `queued` | Немає воркерів (`RUN_WORKERS=false` без процесу `worker`) або чекає попереднього за `overlap: queue` | Запустіть воркери; перевірте активні запуски завдання |
| Запуск `failed` з `validation_failed`: «no collector rules» | Немає правил ні в етапі `collect`, ні в джерелі | Задайте `stages[collect].collector.rules` або `collector_rules` джерела |
| Запуск `running` без матеріалів, у журналі `feed call failed` з `503` | Немає виконавця-колектора з потрібним `capabilities.collector` | Додайте виконавця й перезапустіть процес |
| `backpressure: true` тривалий час | Черга завдання заповнена, обробники не встигають | Збільште `concurrency.max_parallel_stage_items` чи кількість виконавців; перевірте помилки елементів |
| Елементи `retrying` з `service_unavailable` «no executor for package» | Немає обробника для `package_id` | Додайте `capabilities.packages`, `handler_kinds` з Registry або `default: true` |
| Підключення `sync_status: failed` для колектора | Виконавець не приймає цей тип підключення (Web Collector — лише `http`) | Вимкніть `sync_connections` для нього або не використовуйте підключення там |
| Обробник відповідає `404`: «connection … is not known to this executor» | Виконавець перезапустився й втратив підключення, отримані від Orchestrator | Повторіть `PUT /v1/connections/{connection_id}` з тим самим документом; Orchestrator не відновлює синхронізацію сам |
| `POST /v1/reprocessing` → `503` | Немає виконавця `storage_read` | Додайте його в `EXECUTORS` |
| Активація → `503` | Немає виконавця `registry` | Додайте його в `EXECUTORS` |
| Сервіс не стартує: «platform limits file does not match» | `LIMITS_FILE` не відповідає `PlatformLimits` | Виправте файл за [limits.schema.json](../../../contracts/schemas/common/limits.schema.json) |
| Сервіс не стартує через `token_ref` | Посилання `env:`/`file:` не розв'язується | Задайте змінну чи файл або приберіть посилання |
