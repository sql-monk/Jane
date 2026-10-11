# GET /v1/connections

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L511). Не редагуйте вручну.

**Підключення, відомі цьому виконавцю**

| Властивість | Значення |
|---|---|
| operationId | `listConnections` |
| Метод і шлях | `GET /v1/connections` |
| Scope | `connections:write`, `collector:read` |
| Ідемпотентність | — |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка підключень (без значень секретів). | `ConnectionList` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `connection` | так |  |
| `items[].connection_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].kind` | `string` | так | шаблон `"^[a-z][a-z0-9_]{1,31}$"` |
| `items[].title` | `string` | ні | макс. довжина `200` |
| `items[].params` | `object` | ні | Несекретні параметри: host, port, database, schema, bucket, endpoint, region, base_path, api_base, model_aliases тощо. Сервіс відхиляє params, схожі на секрети (secret_detected). |
| `items[].secret_refs` | `object` | ні | Ім'я секрету → посилання на нього. Схеми: env:&lt;VAR>, file:&lt;шлях у контейнері>, vault:&lt;шлях>#&lt;ключ> (опційний провайдер). |
| `items[].labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `list`:

```json
{
  "items": [
    {
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
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `503`.
