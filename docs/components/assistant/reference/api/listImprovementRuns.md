# GET /v1/improvement-runs

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L277). Не редагуйте вручну.

**Запуски вдосконалення (job `kind = improvement`), новіші першими**

| Властивість | Значення |
|---|---|
| operationId | `listImprovementRuns` |
| Метод і шлях | `GET /v1/improvement-runs` |
| Scope | `assistant:use` |
| Ідемпотентність | — |
| Теги | improvement |

Job, створені `startImprovement`, з `result` = `ImprovementResult` для завершених — щоб адмінка відновила список після перезавантаження. Курсорна пагінація (`limit`, `cursor` → `next_cursor`); порядок — `created_at` спадно, за рівності — `job_id` спадно. Фільтри — за мітками job (`labels.package_id`, `labels.source_id`, `labels.problem_group_id`) і станом. Завершені job зберігаються `limits.transfer.job_retention_seconds` асистента.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |
| `package_id` | query | `string` | ні |  |
| `source_id` | query | `string` | ні |  |
| `problem_group_id` | query | `string` | ні |  |
| `status` | query | array of enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | ні | Лише job у цих станах (параметр можна повторити). |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка job вдосконалення. | `JobList` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `job` | так |  |
| `items[].job_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].kind` | `string` | так | Вид операції в межах сервісу, наприклад 'collection', 'invocation', 'test_run', 'run', 'onboarding', 'improvement', 'upstream_port'.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `items[].status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `items[].created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].progress` | `JobProgress` | ні |  |
| `items[].progress.completed` | `integer` | ні | мін. `0` |
| `items[].progress.total` | `integer \| null` | ні | Відома загальна кількість одиниць; null — невідома (наприклад під час рекурсивного обходу).; мін. `0` |
| `items[].progress.unit` | `string` | ні |  |
| `items[].progress.message` | `string` | ні |  |
| `items[].progress.counters` | `object` | ні | Довільні лічильники, наприклад {"fetched": 10, "skipped_robots": 2}. |
| `items[].progress.updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].result` | `object` | ні | Результат, коли status = succeeded. Форма залежить від 'kind' і описана в API відповідної операції. Великий результат передається як result_ref. |
| `items[].result_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `items[].error` | `problem` | ні | Причина, коли status = failed. Для cancelled причина — у cancellation. |
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
| `items[].cancellation` | `JobCancellation` | ні |  |
| `items[].cancellation.requested_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].cancellation.requested_by` | `string` | ні |  |
| `items[].cancellation.reason` | `string` | ні | макс. довжина `1000` |
| `items[].idempotency_key` | `string` | ні | макс. довжина `255` |
| `items[].links` | `object` | ні | Пов'язані ресурси: self, cancel, result, run, collection тощо. |
| `items[].labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `page`:

```json
{
  "items": [
    {
      "job_id": "job_01J9ZW00000000000000IMPROV",
      "kind": "improvement",
      "status": "succeeded",
      "created_at": "2026-09-27T10:00:00Z",
      "finished_at": "2026-09-27T10:01:30Z",
      "labels": {
        "package_id": "shop-example.product-extractor",
        "source_id": "shop-example",
        "problem_group_id": "pg_01J9ZW0000000000000000001"
      },
      "links": {
        "self": "/v1/jobs/job_01J9ZW00000000000000IMPROV",
        "cancel": "/v1/jobs/job_01J9ZW00000000000000IMPROV/cancel"
      },
      "result": {
        "outcome": "new_version",
        "version": {
          "package_id": "shop-example.product-extractor",
          "version": "1.2.1"
        },
        "attempts": 1,
        "activated": false
      }
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `422`.
