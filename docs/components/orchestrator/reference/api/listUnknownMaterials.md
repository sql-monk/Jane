# GET /v1/unknown-materials

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L947). Не редагуйте вручну.

**Матеріали без відповідного обробника (і чи були передані в LLM)**

| Властивість | Значення |
|---|---|
| operationId | `listUnknownMaterials` |
| Метод і шлях | `GET /v1/unknown-materials` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | problems |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `source_id` | query | `string` | ні |  |
| `forwarded` | query | `boolean` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка невідомих матеріалів. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `UnknownMaterial` | так |  |
| `items[].material_id` | `string` | так |  |
| `items[].observation_id` | `string` | так |  |
| `items[].source_id` | `string` | так |  |
| `items[].run_id` | `string` | ні |  |
| `items[].url` | `string` | ні |  |
| `items[].registered_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].forwarded_to_llm` | `boolean` | так |  |
| `items[].reason` | `string` | ні |  |
| `items[].stored_object_id` | `string` | ні |  |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `list`:

```json
{
  "items": [
    {
      "material_id": "web:0a1b2c3d4e5f60718293a4b5c6d7e8f9",
      "observation_id": "obs_01J9ZQ5A0000000000000007",
      "source_id": "shop-example",
      "run_id": "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
      "url": "https://shop.example.test/gift-cards",
      "registered_at": "2026-09-27T10:05:00Z",
      "forwarded_to_llm": false,
      "reason": "no binding matched and forward_unknown_to_llm=false"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
