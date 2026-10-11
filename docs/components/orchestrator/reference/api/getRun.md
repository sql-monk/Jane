# GET /v1/runs/{run_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L688). Не редагуйте вручну.

**Стан запуску, прогрес етапів, витрати**

| Властивість | Значення |
|---|---|
| operationId | `getRun` |
| Метод і шлях | `GET /v1/runs/{run_id}` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | runs |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `run_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Запуск. | `Run` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `run_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `task_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `task_etag` | `string` | ні | Версія конфігурації завдання, з якою виконується запуск. |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `trigger` | enum: `manual`, `schedule`, `reprocess`, `assistant`, `api` | так |  |
| `test_mode` | `boolean` | ні |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `collection_id` | `string` | ні | job_id збору в колекторі. |
| `stages` | array of `StageProgress` | ні |  |
| `stages[].stage_id` | `string` | так |  |
| `stages[].handler` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `stages[].handler.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `stages[].handler.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `stages[].handler.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `stages[].counts` | `object` | ні | Кількість елементів за станом виконання (ItemStatus) і за станом результату (success, empty, unrecognized, failed). |
| `counters` | `object` | ні |  |
| `backpressure` | `boolean` | ні | Збір пригальмовано через заповнену чергу. |
| `costs` | `object` | ні |  |
| `costs.llm` | `Money` | ні |  |
| `costs.llm.amount` | `number` | так | мін. `0` |
| `costs.llm.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `error` | `problem` | ні | Єдина модель помилки всіх API Jane: RFC 9457 (application/problem+json) з розширеннями 'code', 'retryable', 'errors', 'trace_id'. Клієнт приймає рішення за 'code' (стабільний машинний код), а не за 'title'/'detail'. Невідомий 'code' обробляється за HTTP-статусом і 'retryable'. |
| `error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `error.status` | `integer` | так | мін. `400`; макс. `599` |
| `error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `error.instance` | `string` (uri-reference) | ні |  |
| `error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `error.errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `error.errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `error.errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.errors[].message` | `string` | так |  |
| `error.trace_id` | `string` | ні |  |
| `error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |

Приклад `running`:

```json
{
  "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "task_id": "shop-catalog",
  "task_etag": "\"v7\"",
  "status": "running",
  "trigger": "schedule",
  "test_mode": false,
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:01Z",
  "collection_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "backpressure": false,
  "stages": [
    {
      "stage_id": "collect",
      "counts": {
        "completed": 620
      }
    },
    {
      "stage_id": "store-raw",
      "handler": {
        "package_id": "jane.storage-files",
        "version": "1.0.0"
      },
      "counts": {
        "completed": 598,
        "success": 598
      }
    },
    {
      "stage_id": "extract-products",
      "handler": {
        "package_id": "shop-example.product-extractor",
        "version": "1.2.0"
      },
      "counts": {
        "completed": 540,
        "running": 8,
        "success": 480,
        "empty": 21,
        "unrecognized": 37,
        "failed": 2
      }
    }
  ],
  "counters": {
    "unknown_materials": 12
  },
  "costs": {
    "llm": {
      "amount": 0.42,
      "currency": "USD"
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
