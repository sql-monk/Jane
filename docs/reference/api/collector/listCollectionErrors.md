# GET /v1/collections/{collection_id}/errors

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L375). Не редагуйте вручну.

**Помилки й пропуски окремих URL/повідомлень**

| Властивість | Значення |
|---|---|
| operationId | `listCollectionErrors` |
| Метод і шлях | `GET /v1/collections/{collection_id}/errors` |
| Scope | `collector:read` |
| Ідемпотентність | — |
| Теги | collections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `collection_id` | path | `string` | так | Дорівнює job_id, повернутому POST /v1/collections. |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка помилок. | `FetchErrorPage` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `FetchError` | так |  |
| `items[].url` | `string` | ні |  |
| `items[].telegram_message` | `string` | ні |  |
| `items[].code` | `string` | так |  |
| `items[].http_status` | `integer` | ні |  |
| `items[].attempts` | `integer` | ні | мін. `1` |
| `items[].message` | `string` | так |  |
| `items[].at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `errors`:

```json
{
  "items": [
    {
      "url": "https://shop.example.test/private/x",
      "code": "access_denied_by_policy",
      "message": "disallowed by robots.txt",
      "at": "2026-09-27T10:00:07Z"
    },
    {
      "url": "https://shop.example.test/product/z-9",
      "code": "source_unavailable",
      "http_status": 500,
      "attempts": 3,
      "message": "HTTP 500",
      "at": "2026-09-27T10:01:10Z"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `503`.
