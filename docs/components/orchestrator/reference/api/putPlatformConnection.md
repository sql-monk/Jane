# PUT /v1/connections/{connection_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1247). Не редагуйте вручну.

**Створити або замінити підключення й синхронізувати з виконавцями**

| Властивість | Значення |
|---|---|
| operationId | `putPlatformConnection` |
| Метод і шлях | `PUT /v1/connections/{connection_id}` |
| Scope | `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | path | `string` | так |  |
| `If-Match` | header | `string` | ні | ETag ресурсу для оптимістичного блокування. Розбіжність — 412 `precondition_failed`. |

## Тіло запиту

Тип вмісту `application/json`, схема `connection`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `connection_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `kind` | `string` | так | шаблон `"^[a-z][a-z0-9_]{1,31}$"` |
| `title` | `string` | ні | макс. довжина `200` |
| `params` | `object` | ні | Несекретні параметри: host, port, database, schema, bucket, endpoint, region, base_path, api_base, model_aliases тощо. Сервіс відхиляє params, схожі на секрети (secret_detected). |
| `secret_refs` | `object` | ні | Ім'я секрету → посилання на нього. Схеми: env:&lt;VAR>, file:&lt;шлях у контейнері>, vault:&lt;шлях>#&lt;ключ> (опційний провайдер). |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `pg`:

```json
{
  "connection_id": "results-pg",
  "kind": "postgresql",
  "title": "Results DB",
  "params": {
    "host": "postgres",
    "port": 5432,
    "database": "jane_results",
    "schema": "public",
    "sslmode": "prefer"
  },
  "secret_refs": {
    "username": "env:JANE_SECRET_RESULTS_PG_USER",
    "password": "env:JANE_SECRET_RESULTS_PG_PASSWORD"
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Збережено; синхронізація з виконавцями — асинхронна, стан у executors. | `PlatformConnection` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `connection` | `connection` | так | Кероване підключення (ТЗ §11): іменоване підключення до сховища, провайдера LLM, облікового запису Telegram тощо. Містить лише несекретні параметри та посилання на секрети (secret_refs). Значення секретів ніколи не передаються через API, не зберігаються в пакетах і не копіюються під час форку. Сервіс-виконавець розв'язує secret_refs у власному середовищі. Див. docs/adr/0006-secrets-and-connections.md. |
| `connection.connection_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `connection.kind` | `string` | так | шаблон `"^[a-z][a-z0-9_]{1,31}$"` |
| `connection.title` | `string` | ні | макс. довжина `200` |
| `connection.params` | `object` | ні | Несекретні параметри: host, port, database, schema, bucket, endpoint, region, base_path, api_base, model_aliases тощо. Сервіс відхиляє params, схожі на секрети (secret_detected). |
| `connection.secret_refs` | `object` | ні | Ім'я секрету → посилання на нього. Схеми: env:&lt;VAR>, file:&lt;шлях у контейнері>, vault:&lt;шлях>#&lt;ключ> (опційний провайдер). |
| `connection.labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `executors` | array of `object` | ні |  |
| `executors[].executor` | `string` | так |  |
| `executors[].sync_status` | enum: `pending`, `synced`, `failed` | так |  |
| `executors[].synced_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `executors[].message` | `string` | ні |  |
| `executors[].attempts` | `integer` | ні | мін. `0` |
| `executors[].next_retry_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `executors[].error` | `problem` | ні | Єдина модель помилки всіх API Jane: RFC 9457 (application/problem+json) з розширеннями 'code', 'retryable', 'errors', 'trace_id'. Клієнт приймає рішення за 'code' (стабільний машинний код), а не за 'title'/'detail'. Невідомий 'code' обробляється за HTTP-статусом і 'retryable'. |
| `executors[].error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `executors[].error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `executors[].error.status` | `integer` | так | мін. `400`; макс. `599` |
| `executors[].error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `executors[].error.instance` | `string` (uri-reference) | ні |  |
| `executors[].error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `executors[].error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `executors[].error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `executors[].error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `executors[].error.trace_id` | `string` | ні |  |
| `executors[].error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `unsupported_executors` | array of `object` | ні | Виконавці з 501 not_implemented для керованих підключень; це не збій синхронізації. |
| `unsupported_executors[].executor` | `string` | ні |  |
| `unsupported_executors[].reason` | `string` | ні |  |

Приклад `pg`:

```json
{
  "connection": {
    "connection_id": "results-pg",
    "kind": "postgresql",
    "secret_refs": {
      "password": "env:JANE_SECRET_RESULTS_PG_PASSWORD"
    }
  },
  "executors": [
    {
      "executor": "storage",
      "sync_status": "pending"
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `412`, `422`.
