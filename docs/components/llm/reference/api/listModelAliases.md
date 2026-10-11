# GET /v1/model-aliases

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L154). Не редагуйте вручну.

**Псевдоніми моделей, на які посилаються пакети (default, cheap, strong)**

| Властивість | Значення |
|---|---|
| operationId | `listModelAliases` |
| Метод і шлях | `GET /v1/model-aliases` |
| Scope | `llm:admin`, `llm:invoke` |
| Ідемпотентність | — |
| Теги | providers |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Псевдоніми. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `ModelAlias` | так |  |
| `items[].alias` | `string` | так |  |
| `items[].provider_id` | `string` | так |  |
| `items[].model_id` | `string` | так |  |

Приклад `list`:

```json
{
  "items": [
    {
      "alias": "default",
      "provider_id": "fake",
      "model_id": "fake-deterministic-1"
    }
  ]
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
