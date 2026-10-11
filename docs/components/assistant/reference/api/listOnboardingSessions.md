# GET /v1/onboarding-sessions

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L37). Не редагуйте вручну.

**Сесії підключення, новіші першими (відновлення стану адмінки після перезавантаження)**

| Властивість | Значення |
|---|---|
| operationId | `listOnboardingSessions` |
| Метод і шлях | `GET /v1/onboarding-sessions` |
| Scope | `assistant:use` |
| Ідемпотентність | — |
| Теги | onboarding |

Курсорна пагінація (`limit`, `cursor` → `next_cursor`, `null` — сторінок більше немає; чужий курсор — 422). Порядок — `created_at` спадно, за рівності — `session_id` спадно; нові сесії новіші за курсор, тож не з'являються на наступних сторінках і не зсувають їх. Фільтр `status` бачить той самий стан, що й `GET` сесії. Елементи — короткий стан сесії; повний (кандидати, вибірка, аналіз, варіанти) — `GET /v1/onboarding-sessions/{session_id}`. Сесії без змін довше за налаштований строк зберігання асистента (`state.session_retention_seconds`) видаляються.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |
| `status` | query | array of enum: `resolving`, `needs_disambiguation`, `sampling`, `analyzing`, `proposals_ready`, `insufficient_sample`, `applying`, `completed`, `failed`, `cancelled` | ні | Лише сесії в цих станах (параметр можна повторити, наприклад `?status=sampling&status=analyzing`). |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка сесій. | `OnboardingSessionList` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `OnboardingSessionSummary` | так |  |
| `items[].session_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].status` | enum: `resolving`, `needs_disambiguation`, `sampling`, `analyzing`, `proposals_ready`, `insufficient_sample`, `applying`, `completed`, `failed`, `cancelled` | так |  |
| `items[].query` | `string` | так |  |
| `items[].selected_candidate_id` | `string` | ні |  |
| `items[].proposal_count` | `integer` | ні | Скільки варіантів збору запропоновано.; мін. `0` |
| `items[].costs` | `Money` | ні |  |
| `items[].costs.amount` | `number` | так | мін. `0` |
| `items[].costs.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `items[].job_id` | `string` | ні | Останній job сесії (`GET /v1/jobs/{job_id}`). |
| `items[].created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
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

Приклад `page`:

```json
{
  "items": [
    {
      "session_id": "onb_01J9ZY0000000000000000002",
      "status": "insufficient_sample",
      "query": "https://tiny.example.test/",
      "proposal_count": 0,
      "costs": {
        "amount": 0.05,
        "currency": "USD"
      },
      "job_id": "job_01J9ZY0000000000000000JO2",
      "created_at": "2026-09-27T10:00:00Z"
    },
    {
      "session_id": "onb_01J9ZY0000000000000000001",
      "status": "proposals_ready",
      "query": "Shop Example kettles",
      "selected_candidate_id": "cand_1",
      "proposal_count": 2,
      "costs": {
        "amount": 0.31,
        "currency": "USD"
      },
      "job_id": "job_01J9ZY0000000000000000JOB",
      "created_at": "2026-09-27T09:00:00Z"
    }
  ],
  "next_cursor": "WyIyMDI2LTA5LTI3VDA5OjAwOjAwWiIsIm9uYl8wMUo5WlkwMDAwMDAwMDAwMDAwMDAwMDAxIl0"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `422`.
