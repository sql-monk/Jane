# POST /v1/reprocessing

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1119). Не редагуйте вручну.

**Повторно обробити збережені RAW етапами завдання**

| Властивість | Значення |
|---|---|
| operationId | `startReprocessing` |
| Метод і шлях | `POST /v1/reprocessing` |
| Scope | `orchestrator:write`, `orchestrator:admin` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | runs |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `ReprocessRequest`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `task_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `stored_materials` | `stored_materials` | так | Повторна обробка збережених RAW (ТЗ §10): фільтр збережених об'єктів замість нового збору. Завжди лише RAW джерела завдання (Material.source.source_id). Фільтри поєднуються через AND. material_ids обирає всі збережені спостереження цих матеріалів у часовому вікні since/until; точний вибір — object_ids (конкретні збережені RAW) або observation_ids (конкретні спостереження). |
| `stored_materials.storage_connection_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `stored_materials.since` | `string` (date-time) | ні | Час збереження (stored_at) не раніше. |
| `stored_materials.until` | `string` (date-time) | ні | Час збереження (stored_at) раніше за це значення. |
| `stored_materials.material_ids` | array of `string` | ні | Усі збережені спостереження цих матеріалів (у межах since/until). |
| `stored_materials.object_ids` | array of `string` | ні | Точний вибір: саме ці збережені RAW (StoredObjectRef.object_id у підключенні storage_connection_id), у заданому порядку; кожен читається через storage.v1 GET /v1/objects/{object_id}. Відсутній об'єкт завершує запуск помилкою not_found; RAW іншого джерела чи без відновлюваного Material пропускається. Кількість обмежує конфігурація оркестратора (більше — 422 limit_exceeded). |
| `stored_materials.observation_ids` | array of `string` | ні | Точний вибір спостережень (Material.observation_id): лише RAW цих спостережень серед відібраних іншими фільтрами. Кілька збережених копій одного спостереження не вгадуються (одна копія обробляється, посилання на RAW не записується). Кількість обмежує конфігурація оркестратора. |
| `from_stage` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `test_mode` | `boolean` | ні |  |
| `reason` | `string` | ні |  |

Приклад `reprocess`:

```json
{
  "task_id": "shop-catalog",
  "stored_materials": {
    "storage_connection_id": "raw-files",
    "since": "2026-09-20T00:00:00Z"
  },
  "from_stage": "extract-products",
  "reason": "extractor 1.2.0 fixes price parsing"
}
```

Приклад `exactRaw`:

```json
{
  "task_id": "shop-catalog",
  "stored_materials": {
    "storage_connection_id": "raw-files",
    "object_ids": [
      "obj_01J9ZQ4C00000000000000D1"
    ]
  },
  "from_stage": "extract-products",
  "test_mode": true,
  "reason": "check the fix on the problem sample"
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `202` | Операцію прийнято до асинхронного виконання. | `job` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 202

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

Приклад `queued`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "queued",
  "created_at": "2026-09-27T10:00:00Z",
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `422`.
- Операція асинхронна: `202` повертає job; стан, прогрес і результат — через `GET /v1/jobs/{job_id}`.
