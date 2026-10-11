# GET /v1/executors

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1391). Не редагуйте вручну.

**Сервіси-виконавці, відомі оркестратору (з конфігурації), і їхній стан**

| Властивість | Значення |
|---|---|
| operationId | `listExecutors` |
| Метод і шлях | `GET /v1/executors` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | system |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Виконавці. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `Executor` | так |  |
| `items[].executor` | `string` | так |  |
| `items[].role` | enum: `collector`, `handler`, `storage_read`, `registry`, `llm`, `assistant` | так |  |
| `items[].base_url` | `string` (uri) | так |  |
| `items[].status` | enum: `ok`, `degraded`, `down`, `unknown` | так |  |
| `items[].capabilities` | `object` | ні |  |

Приклад `list`:

```json
{
  "items": [
    {
      "executor": "web-collector",
      "role": "collector",
      "base_url": "http://web-collector:8000",
      "status": "ok",
      "capabilities": {
        "collector": "web"
      }
    },
    {
      "executor": "handler-runtime",
      "role": "handler",
      "base_url": "http://handler-runtime:8000",
      "status": "ok",
      "capabilities": {
        "handler_kinds": [
          "extractor",
          "transform"
        ]
      }
    },
    {
      "executor": "storage",
      "role": "handler",
      "base_url": "http://storage:8000",
      "status": "degraded"
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
