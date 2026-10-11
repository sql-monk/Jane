# GET /v1/connections/{connection_id}

> Згенеровано `scripts/docs_reference.py` з [handler.v1.yaml](../../../../contracts/openapi/handler.v1.yaml#L310). Не редагуйте вручну.

**Прочитати підключення**

| Властивість | Значення |
|---|---|
| operationId | `getConnection` |
| Метод і шлях | `GET /v1/connections/{connection_id}` |
| Scope | `connections:write`, `handler:invoke` |
| Ідемпотентність | — |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Підключення. | `connection` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

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

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`.
