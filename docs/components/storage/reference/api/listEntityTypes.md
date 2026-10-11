# GET /v1/entity-types

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L409). Не редагуйте вручну.

**Типи фактично збережених сутностей і їх кількість**

| Властивість | Значення |
|---|---|
| operationId | `listEntityTypes` |
| Метод і шлях | `GET /v1/entity-types` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | entities |

Каталог поточного простору підключення; не очікувані типи джерел. Порожній items означає відсутність сутностей. Приклад запиту — GET /v1/entity-types?connection_id=results-pg&limit=50. Необов'язкова можливість адаптера: 501 not_implemented означає недоступність каталогу.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | query | `string` | так |  |
| `scope` | query | `string` | ні | Фактична key.scope сутності, визначена обробником; не source_id. |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка типів у лексикографічному порядку. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `501` | Каталог або пошук сутностей не підтримується цим адаптером. | `problem` |
| `504` | Перевищено налаштований timeouts.request_timeout_ms під час читання сховища. | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `EntityTypeSummary` | так |  |
| `items[].entity_type` | `string` | так |  |
| `items[].entity_count` | `integer` | так | мін. `0` |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |
| `search_supported` | `boolean` | так |  |

Приклад `catalog`:

```json
{
  "items": [
    {
      "entity_type": "offer",
      "entity_count": 1172
    },
    {
      "entity_type": "product",
      "entity_count": 30
    }
  ],
  "next_cursor": null,
  "search_supported": true
}
```

Приклад `empty`:

```json
{
  "items": [],
  "next_cursor": null,
  "search_supported": true
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `422`, `501`, `504`.
