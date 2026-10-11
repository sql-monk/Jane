# Інтеграція Orchestrator

Як керувати Orchestrator зі стороннього застосунку, як він поєднує модулі Jane і як замінити виконавця чи сам Orchestrator сумісною реалізацією. Повний перелік операцій — [довідник orchestrator.v1](reference/api/README.md).

## Зміст

- [Правила API](#правила-api)
- [Типовий сценарій стороннього застосунку](#типовий-сценарій-стороннього-застосунку)
- [Зміна завдання з If-Match](#зміна-завдання-з-if-match)
- [Прив'язки й невідомі матеріали](#привязки-й-невідомі-матеріали)
- [Повторна обробка збережених RAW](#повторна-обробка-збережених-raw)
- [Групи проблем і активація версій](#групи-проблем-і-активація-версій)
- [Композиція в Jane](#композиція-в-jane)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Правила API

Спільні конвенції Jane — версія `/v1`, Problem (`application/problem+json`), курсорна пагінація, асинхронні job — описано в [errors.md](../../../contracts/docs/errors.md) і [contracts/README.md](../../../contracts/README.md). Для Orchestrator важливо:

| Правило | Деталі |
|---|---|
| Автентифікація | `Authorization: Bearer <ключ або JWT>`; scopes — у [configuration.md](configuration.md#автентифікація) |
| `Idempotency-Key` | Обов'язковий для `POST /v1/sources`, `/v1/tasks`, `/v1/tasks/{task_id}/runs`, `…/stages/{stage_id}/activations`, `/v1/reprocessing`; без нього — `422`. Повтор з тим самим ключем і тілом повертає збережену відповідь |
| `ETag` / `If-Match` | `GET` джерела, завдання, підключення й лімітів платформи повертає `ETag: "vN"`; `PUT` з неактуальним `If-Match` → `412 precondition_failed`; без `If-Match` зміна безумовна |
| Асинхронний запуск | `202` з `Job` (`kind: run`), заголовок `Location: /v1/jobs/{run_id}`; стан — `GET /v1/jobs/{job_id}` до `succeeded`, `failed` або `cancelled` |
| Пагінація | `?limit=` (типово 50, не більше 500) і `?cursor=` з `next_cursor` |
| Перевірка тіла | Запити перевіряються за JSON Schema контракту; порушення — `422 validation_failed` з `errors[].pointer` |

## Типовий сценарій стороннього застосунку

1. `POST /v1/sources` — джерело ([source.schema.json](../../../contracts/schemas/source.schema.json)).
2. `POST /v1/task-validations` — перевірка конфігурації без збереження: схема, DAG, посилання, розклад; повертає `valid`, `errors`, `warnings`.
3. `POST /v1/tasks` — завдання ([task-config.schema.json](../../../contracts/schemas/task-config.schema.json)).
4. `POST /v1/tasks/{task_id}/runs` — запуск; тіло може містити `reason`, `test_mode`, `input_override` (наприклад інші `urls`), `limits` рівня `request`.
5. `GET /v1/jobs/{job_id}` — опитування; `GET /v1/runs/{run_id}`, `/items`, `/v1/materials/{material_id}/trace` — деталі.
6. `POST /v1/runs/{run_id}/cancel` (або `/v1/jobs/{job_id}/cancel`) — скасування: `202` для активного запуску, `200` для завершеного.

Усі кроки з реальними відповідями — у [quickstart.md](quickstart.md). Скасування перевірено: запуск у `queued` після `POST /v1/jobs/{job_id}/cancel` з `{"reason": "docs check"}` повернув `202` зі станом `cancelling`, а за кілька секунд став `cancelled` з `cancellation.requested_by` і `reason`.

## Зміна завдання з If-Match

Приклад для завдання з [quickstart](quickstart.md), команди з кореня репозиторію.

PowerShell:

```powershell
$api = 'http://127.0.0.1:18610/v1'
$ex = 'docs/components/orchestrator/examples/quickstart'
(Invoke-WebRequest -Uri "$api/tasks/quickstart-products").Headers.ETag
$r = Invoke-WebRequest -Method Put -Uri "$api/tasks/quickstart-products" -Headers @{'If-Match' = '"v1"'} -ContentType application/json -InFile "$ex/task.json"
$r.StatusCode; $r.Headers.ETag
```

```text
"v1"
200
"v2"
```

Bash (Git Bash на Windows; на Linux не перевірено):

```bash
curl -s -i http://127.0.0.1:18610/v1/tasks/quickstart-products | grep -i etag
curl -s -X PUT http://127.0.0.1:18610/v1/tasks/quickstart-products -H 'If-Match: "v1"' -H 'Content-Type: application/json' --data-binary @docs/components/orchestrator/examples/quickstart/task.json
```

Неактуальний `If-Match` дає (перевірено):

```json
{"type": "urn:jane:problem:precondition_failed", "title": "Precondition failed", "status": 412, "detail": "If-Match \"v0\" does not match current ETag \"v1\"", "instance": "/v1/tasks/quickstart-products", "code": "precondition_failed", "retryable": false, "trace_id": "9c7da2e367b78eef14bc5288db8e8265"}
```

Зміна потрапляє в аудит (`GET /v1/audit-events?subject_type=task&subject_id=…`) з переліком змінених полів верхнього рівня, наприклад `"details": {"changed": ["enabled"]}`. Запуски, створені до зміни, працюють зі своїм знімком.

## Прив'язки й невідомі матеріали

Етап із `bindings` отримує лише матеріали, що їм відповідають; матеріал, якому не відповідає жодна прив'язка, стає невідомим. Перевірений приклад: завдання з розкладом `interval` і етапом лише для ноутбуків (джерело й підключення — з [quickstart](quickstart.md)).

```json
{
  "task_id": "quickstart-bindings",
  "title": "Laptops only; other pages are unknown",
  "input": {"source_id": "quickstart-testsite"},
  "stages": [
    {"stage_id": "collect", "kind": "collect", "collector": {"collector": "web"}},
    {
      "stage_id": "store-laptops",
      "kind": "handler",
      "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
      "connections": {"target": "quickstart-raw"},
      "inputs": [{"from": "collect"}],
      "bindings": [{"url_patterns": [{"value": "127.0.0.1:18620/product/laptop-*"}]}]
    }
  ],
  "schedule": {"type": "interval", "interval_seconds": 20, "overlap": "skip"}
}
```

Через 20 секунд після створення планувальник створив запуск `trigger: schedule`: 2 матеріали, на етапі `store-laptops` — 1 елемент, `counters.unknown_materials: 1`. `GET /v1/unknown-materials?source_id=quickstart-testsite`:

```json
{"items": [{"material_id": "web:33ff398d154b658ae710e19726c55a1a", "observation_id": "obs_01a12a8a66010000fdedbd2c", "source_id": "quickstart-testsite", "run_id": "run_01M4N8MQ0FFWEYJYY3XN2GFEPT", "registered_at": "2026-10-11T10:37:57.004Z", "forwarded_to_llm": false, "url": "http://127.0.0.1:18620/product/phone-alpha", "reason": "no binding matched and forward_unknown_to_llm=false"}], "next_cursor": null}
```

Щоб передавати невідомі сторінки в LLM, додайте етап з ребром `{"from": "collect", "select": "unmatched_materials"}` (обробник `llm`) і `forward_unknown_to_llm: true` у завданні або джерелі. Цей варіант у межах документації не перевірявся: потрібен LLM gateway; поведінку покриває тест `test_unknown_material_goes_to_llm_only_with_flag` ([test_features.py](../../../services/orchestrator/tests/test_features.py)).

## Повторна обробка збережених RAW

Потрібен виконавець `storage_read` (той самий Storage) і підключення, в якому лежать RAW:

```json
{
  "task_id": "quickstart-products",
  "stored_materials": {"storage_connection_id": "quickstart-raw"},
  "from_stage": "store-raw",
  "test_mode": true,
  "reason": "docs check"
}
```

`POST /v1/reprocessing` з цим тілом і `Idempotency-Key` повернув `202` з `Job`. Запуск `trigger: reprocess` прочитав 4 збережені RAW джерела й передав їх одразу на етап `store-raw`: `succeeded`, 4 елементи `success`. Перша спроба завершилась 4 невдалими елементами з `local blob reading is disabled`: Storage читає збережені файли лише з `JANE_STORAGE_CONTENT_FILES_DIR` (налаштування Storage, а не Orchestrator). Невдалі елементи утворили групу проблем `execution_error` пакета `jane.storage-files`.

Фільтри `material_ids`, `observation_ids`, `object_ids`, `since`, `until` поєднуються через AND; деталі — [internals.md](internals.md#повторна-обробка-збережених-raw).

## Групи проблем і активація версій

Assistant і Admin UI беруть приклади з `GET /v1/problem-groups`, а після роботи над виправленням оновлюють групу:

```json
{"status": "resolved", "note": "storage content_files_dir was not set"}
```

`PATCH /v1/problem-groups/{group_id}` з `Content-Type: application/merge-patch+json` (перевірено) повертає групу з новим станом; зміна йде в аудит.

Нова версія пакета застосовується до етапу активацією:

```json
{"kind": "activate", "package": {"package_id": "shop-example.product-extractor", "version": "1.3.0"}, "reason": "fixes price parsing"}
```

`POST /v1/tasks/{task_id}/stages/{stage_id}/activations` перевіряє версію в Registry, тож у цій документації не виконувався (Registry не піднімався). Відкат — `{"kind": "rollback"}` без `package`; історія — `GET` того самого шляху. Правила — [internals.md](internals.md#активації-версій-пакетів).

## Композиція в Jane

- **Admin UI** працює лише через `orchestrator.v1`: джерела, завдання, запуски, групи проблем, підключення, ліміти.
- **Assistant** читає групи проблем і, коли політика джерела дозволяє, активує перевірені версії (`kind: auto_activate`).
- **Колектори й обробники** не знають про Orchestrator: він викликає їх через `collector.v1` і `handler.v1` з власним токеном і `Idempotency-Key`. Ті самі сервіси можна викликати напряму, без Orchestrator.
- **Dev-стек**: `just up … orchestrator` піднімає сервіс з `api_key`, базою `jane_orchestrator` і токеном `JANE_SECRET_ORCHESTRATOR_TOKEN` для виконавців ([infra/compose.yaml](../../../infra/compose.yaml)). Список виконавців задає `infra/compose.local.yaml` ([зразок](../../../infra/compose.local.example.yaml)); без нього запуски не просуваються. Через proxy API доступний як `/api/orchestrator/v1/...` ([README](../../../README.md#швидкий-старт)).

## Заміна сумісною реалізацією

**Виконавця** можна замінити будь-яким сервісом, що реалізує контракт ролі, і зареєструвати в `EXECUTORS`:

| Роль | Що Orchestrator очікує |
|---|---|
| `collector` | `POST /v1/collections` з `Idempotency-Key` (`202` + `job_id`); `GET /v1/collections/{id}/materials?limit&wait_ms&after` з підтвердженням сторінки через `after`; `end_of_stream`, `collection_status`; `GET /v1/jobs/{id}`, `POST /v1/jobs/{id}/cancel` ([collector.v1](../../reference/api/collector/README.md)) |
| `handler`, `llm` | `POST /v1/invocations` з `Idempotency-Key` = `delivery_key`: `200` з `HandlerResult` або `202` + job; повтор того самого ключа — збережений результат; `409 idempotency_in_progress`, поки доставка триває ([handler.v1](../../reference/api/handler/README.md)) |
| будь-яка з підключеннями | `PUT`/`DELETE /v1/connections/{id}`; `501 not_implemented` — підключення не підтримуються |
| `storage_read` | `GET /v1/objects` з `connection_id`, `source_id`, `cursor`, `since`, `until`, `material_ids`; `GET /v1/objects/{id}` з відновленим `material` |
| `registry` | `GET /v1/packages/{id}`, `GET /v1/packages/{id}/versions/{version}` |

Головна умова коректності — ідемпотентність за `Idempotency-Key`: без неї повтор після збою воркера може повторити ефект.

**Сам Orchestrator** замінюється реалізацією `orchestrator.v1`: Admin UI й Assistant звертаються лише до цього API. Колекторів і обробників заміна не зачіпає.
