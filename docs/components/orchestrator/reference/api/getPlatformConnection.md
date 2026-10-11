# GET /v1/connections/{connection_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1211). Не редагуйте вручну.

**Підключення і стан синхронізації з виконавцями**

| Властивість | Значення |
|---|---|
| operationId | `getPlatformConnection` |
| Метод і шлях | `GET /v1/connections/{connection_id}` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Підключення. | `PlatformConnection` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

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
      "sync_status": "synced"
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
