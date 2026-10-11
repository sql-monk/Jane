# GET /v1/entities

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L457). Не редагуйте вручну.

**Актуальний стан сутностей**

| Властивість | Значення |
|---|---|
| operationId | `listEntities` |
| Метод і шлях | `GET /v1/entities` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | entities |

Необов’язковий search шукає без урахування регістру буквальний підрядок у canonical_key, key і fields по всьому сховищу перед пагінацією. Без search поведінка незмінна. Адаптер без можливості пошуку повертає 501 not_implemented. Курсор чинний для тих самих фільтрів. Приклад: GET /v1/entities?connection_id=results-pg&entity_type=product&search=Kettle.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | query | `string` | так |  |
| `entity_type` | query | `string` | так |  |
| `scope` | query | `string` | ні |  |
| `key` | query | `string` | ні | Канонічний ключ (EntityState.canonical_key); тоді сторінка містить 0 або 1 елемент. |
| `search` | query | `string` | ні | Буквальний підрядок; пробіли на початку й кінці ігноруються. |
| `updated_since` | query | `string` (date-time) | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка актуальних станів. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `501` | Каталог або пошук сутностей не підтримується цим адаптером. | `problem` |
| `504` | Перевищено налаштований timeouts.request_timeout_ms під час читання сховища. | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `EntityState` | так |  |
| `items[].entity_type` | `string` | так |  |
| `items[].key` | `EntityKey` | так | Ідентичність об'єкта. natural — значення ключових полів схеми (наприклад {"sku": "A-1"}); scope — простір імен (зазвичай source_id), щоб однакові SKU різних джерел не злилися. Сховище будує канонічний рядок ключа: scope + '\|' + пари natural, відсортовані за іменем, серіалізовані як JSON без пробілів. |
| `items[].key.scope` | `string` | так | мін. довжина `1` |
| `items[].key.natural` | `object` | так |  |
| `items[].canonical_key` | `string` | ні |  |
| `items[].fields` | `object` | так |  |
| `items[].field_orders` | `object` | ні | Для кожного поля — порядок спостереження, з якого взято значення; для очищених полів — порядок очищення. |
| `items[].cleared_fields` | array of `string` | ні |  |
| `items[].version` | `integer` | ні | Лічильник змін актуального стану.; мін. `1` |
| `items[].updated_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `one`:

```json
{
  "items": [
    {
      "entity_type": "product",
      "key": {
        "scope": "shop-example",
        "natural": {
          "sku": "A-100"
        }
      },
      "canonical_key": "shop-example|{\"sku\":\"A-100\"}",
      "fields": {
        "sku": "A-100",
        "title": "Kettle A-100",
        "price": {
          "amount": 1199.0,
          "currency": "UAH"
        }
      },
      "version": 2,
      "updated_at": "2026-09-28T06:00:09Z"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `422`, `501`, `504`.
