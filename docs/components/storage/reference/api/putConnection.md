# PUT /v1/connections/{connection_id}

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L90). Не редагуйте вручну.

**Створити або замінити підключення (секрети — лише посиланнями)**

| Властивість | Значення |
|---|---|
| operationId | `putConnection` |
| Метод і шлях | `PUT /v1/connections/{connection_id}` |
| Scope | `connections:write` |
| Ідемпотентність | — |
| Теги | connections |

Викликає оркестратор, синхронізуючи реєстр підключень, або адміністратор автономного виконавця. Значення, схожі на секрети, у `params` відхиляються (`secret_detected`). Виконавець без керованих підключень відповідає 501 `not_implemented`; клієнт не вважає це збоєм (див. опис API). 404/405 — збій синхронізації.

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

Приклад `llm`:

```json
{
  "connection_id": "llm-main",
  "kind": "llm_provider",
  "params": {
    "provider": "openai-compatible",
    "api_base": "http://llm-proxy.localhost:8080/v1"
  },
  "secret_refs": {
    "api_key": "file:/run/secrets/llm_api_key"
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Підключення замінено. | `connection` |
| `201` | Підключення створено. | `connection` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `501` | Виконавець не використовує підключень (`not_implemented`). | `problem` |

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

### Відповідь 201

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

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `412`, `422`, `501`.
