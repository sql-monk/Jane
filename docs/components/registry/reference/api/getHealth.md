# GET /v1/health

> Згенеровано `scripts/docs_reference.py` з [common.yaml](../../../../../contracts/openapi/common.yaml#L423). Не редагуйте вручну.

**Стан сервісу (liveness/readiness)**

| Властивість | Значення |
|---|---|
| operationId | `getHealth` |
| Метод і шлях | `GET /v1/health` |
| Scope | без автентифікації |
| Ідемпотентність | — |
| Теги | system |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сервіс працює (ok або degraded). | `Health` |
| `503` | Сервіс не готовий. | `Health` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `status` | enum: `ok`, `degraded`, `down` | так |  |
| `checks` | `object` | ні |  |

Приклад `ok`:

```json
{
  "status": "ok",
  "checks": {
    "state_store": {
      "status": "ok"
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `503`.
