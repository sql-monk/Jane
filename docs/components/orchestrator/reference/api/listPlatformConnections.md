# GET /v1/connections

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1155). Не редагуйте вручну.

**Реєстр підключень платформи (без значень секретів)**

| Властивість | Значення |
|---|---|
| operationId | `listPlatformConnections` |
| Метод і шлях | `GET /v1/connections` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `kind` | query | `string` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка підключень. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `PlatformConnection` | так |  |
| `items[].connection` | `connection` | так | Кероване підключення (ТЗ §11): іменоване підключення до сховища, провайдера LLM, облікового запису Telegram тощо. Містить лише несекретні параметри та посилання на секрети (secret_refs). Значення секретів ніколи не передаються через API, не зберігаються в пакетах і не копіюються під час форку. Сервіс-виконавець розв'язує secret_refs у власному середовищі. Див. docs/adr/0006-secrets-and-connections.md. |
| `items[].connection.connection_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].connection.kind` | `string` | так | шаблон `"^[a-z][a-z0-9_]{1,31}$"` |
| `items[].connection.title` | `string` | ні | макс. довжина `200` |
| `items[].connection.params` | `object` | ні | Несекретні параметри: host, port, database, schema, bucket, endpoint, region, base_path, api_base, model_aliases тощо. Сервіс відхиляє params, схожі на секрети (secret_detected). |
| `items[].connection.secret_refs` | `object` | ні | Ім'я секрету → посилання на нього. Схеми: env:&lt;VAR>, file:&lt;шлях у контейнері>, vault:&lt;шлях>#&lt;ключ> (опційний провайдер). |
| `items[].connection.labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `items[].executors` | array of `object` | ні |  |
| `items[].executors[].executor` | `string` | так |  |
| `items[].executors[].sync_status` | enum: `pending`, `synced`, `failed` | так |  |
| `items[].executors[].synced_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].executors[].message` | `string` | ні |  |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `list`:

```json
{
  "items": [
    {
      "connection": {
        "connection_id": "results-pg",
        "kind": "postgresql",
        "params": {
          "host": "postgres",
          "port": 5432,
          "database": "jane_results"
        },
        "secret_refs": {
          "username": "env:JANE_SECRET_RESULTS_PG_USER",
          "password": "env:JANE_SECRET_RESULTS_PG_PASSWORD"
        }
      },
      "executors": [
        {
          "executor": "storage",
          "synced_at": "2026-09-27T09:00:00Z",
          "sync_status": "synced"
        }
      ]
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
