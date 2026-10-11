# GET /v1/jobs/{job_id}

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L683). Не редагуйте вручну.

**Стан, прогрес і результат тривалої операції**

| Властивість | Значення |
|---|---|
| operationId | `getJob` |
| Метод і шлях | `GET /v1/jobs/{job_id}` |
| Scope | `collector:read` |
| Ідемпотентність | — |
| Теги | jobs |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `job_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Поточний стан job. | `job` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `job_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `kind` | `string` | так | Вид операції в межах сервісу, наприклад 'collection', 'invocation', 'test_run', 'run', 'onboarding', 'improvement', 'upstream_port'.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `progress` | `JobProgress` | ні |  |
| `progress.completed` | `integer` | ні | мін. `0` |
| `progress.total` | `integer \| null` | ні | Відома загальна кількість одиниць; null — невідома (наприклад під час рекурсивного обходу).; мін. `0` |
| `progress.unit` | `string` | ні |  |
| `progress.message` | `string` | ні |  |
| `progress.counters` | `object` | ні | Довільні лічильники, наприклад {"fetched": 10, "skipped_robots": 2}. |
| `progress.updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `result` | `object` | ні | Результат, коли status = succeeded. Форма залежить від 'kind' і описана в API відповідної операції. Великий результат передається як result_ref. |
| `result_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `error` | `problem` | ні | Причина, коли status = failed. Для cancelled причина — у cancellation. |
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
| `cancellation` | `JobCancellation` | ні |  |
| `cancellation.requested_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `cancellation.requested_by` | `string` | ні |  |
| `cancellation.reason` | `string` | ні | макс. довжина `1000` |
| `idempotency_key` | `string` | ні | макс. довжина `255` |
| `links` | `object` | ні | Пов'язані ресурси: self, cancel, result, run, collection тощо. |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `running`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "running",
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:01Z",
  "updated_at": "2026-09-27T10:02:00Z",
  "progress": {
    "completed": 120,
    "total": null,
    "unit": "pages",
    "counters": {
      "fetched": 120,
      "skipped_robots": 3,
      "skipped_out_of_scope": 41,
      "duplicates": 17
    },
    "updated_at": "2026-09-27T10:02:00Z"
  },
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

Приклад `failed`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "failed",
  "created_at": "2026-09-27T10:00:00Z",
  "started_at": "2026-09-27T10:00:01Z",
  "finished_at": "2026-09-27T10:00:09Z",
  "error": {
    "type": "urn:jane:problem:source_unavailable",
    "title": "Source unavailable",
    "status": 502,
    "code": "source_unavailable",
    "retryable": true,
    "detail": "https://shop.example.test/ returned HTTP 503 for 5 consecutive attempts"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `503`.
