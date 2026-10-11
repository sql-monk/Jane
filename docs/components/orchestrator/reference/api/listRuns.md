# GET /v1/runs

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L634). Не редагуйте вручну.

**Запуски**

| Властивість | Значення |
|---|---|
| operationId | `listRuns` |
| Метод і шлях | `GET /v1/runs` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | runs |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `task_id` | query | `string` | ні |  |
| `status` | query | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | ні |  |
| `since` | query | `string` (date-time) | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка запусків. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `Run` | так |  |
| `items[].run_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].task_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].task_etag` | `string` | ні | Версія конфігурації завдання, з якою виконується запуск. |
| `items[].status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `items[].trigger` | enum: `manual`, `schedule`, `reprocess`, `assistant`, `api` | так |  |
| `items[].test_mode` | `boolean` | ні |  |
| `items[].created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].collection_id` | `string` | ні | job_id збору в колекторі. |
| `items[].stages` | array of `StageProgress` | ні |  |
| `items[].stages[].stage_id` | `string` | так |  |
| `items[].stages[].handler` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `items[].stages[].counts` | `object` | ні | Кількість елементів за станом виконання (ItemStatus) і за станом результату (success, empty, unrecognized, failed). |
| `items[].counters` | `object` | ні |  |
| `items[].backpressure` | `boolean` | ні | Збір пригальмовано через заповнену чергу. |
| `items[].costs` | `object` | ні |  |
| `items[].costs.llm` | `Money` | ні |  |
| `items[].error` | `problem` | ні | Єдина модель помилки всіх API Jane: RFC 9457 (application/problem+json) з розширеннями 'code', 'retryable', 'errors', 'trace_id'. Клієнт приймає рішення за 'code' (стабільний машинний код), а не за 'title'/'detail'. Невідомий 'code' обробляється за HTTP-статусом і 'retryable'. |
| `items[].error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `items[].error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `items[].error.status` | `integer` | так | мін. `400`; макс. `599` |
| `items[].error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `items[].error.instance` | `string` (uri-reference) | ні |  |
| `items[].error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `items[].error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `items[].error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `items[].error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `items[].error.trace_id` | `string` | ні |  |
| `items[].error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `list`:

```json
{
  "items": [
    {
      "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
      "task_id": "shop-catalog",
      "status": "running",
      "trigger": "schedule",
      "created_at": "2026-09-27T10:00:00Z"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
