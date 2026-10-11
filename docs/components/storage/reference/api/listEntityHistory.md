# GET /v1/entity-history

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L108). Не редагуйте вручну.

**Історія оновлень однієї сутності (включно із запізнілими)**

| Властивість | Значення |
|---|---|
| operationId | `listEntityHistory` |
| Метод і шлях | `GET /v1/entity-history` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | entities |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | query | `string` | так |  |
| `entity_type` | query | `string` | так |  |
| `key` | query | `string` | так |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка історії, від новіших до старіших за received_at. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `EntityHistoryEntry` | так |  |
| `items[].record` | `entity` | так | Сутність, витягнута обробником, і водночас часткове оновлення ідентифікованого об'єкта (ТЗ §6, §11). Семантика застосування (реалізує обробник збереження, перевіряє набір сумісності): (1) поле з 'fields' встановлює значення; (2) поле, відсутнє в 'fields', НЕ змінюється — пропуск не означає видалення; (3) явне очищення — лише через 'cleared' (null у 'fields' заборонено); (4) порядок спостережень: кожне поле поточного стану пам'ятає order свого останнього значення; оновлення поля застосовується, лише якщо order запису новіший (див. $defs/ObservationOrder), інакше запис потрапляє лише в історію, а підтвердження містить stale_fields; (5) той самий delivery_key вдруге — дубль, без нових записів. |
| `items[].record.entity_type` | `string` | так | Тип сутності зі схеми результату пакета (наприклад 'product', 'price', 'event').; шаблон `"^[a-z][a-z0-9_]{0,63}$"` |
| `items[].record.schema` | `string` | ні | Посилання на схему сутності всередині пакета: '&lt;package_id>@&lt;version>#&lt;entity_type>'. |
| `items[].record.key` | `EntityKey` | так | Ідентичність об'єкта. natural — значення ключових полів схеми (наприклад {"sku": "A-1"}); scope — простір імен (зазвичай source_id), щоб однакові SKU різних джерел не злилися. Сховище будує канонічний рядок ключа: scope + '\|' + пари natural, відсортовані за іменем, серіалізовані як JSON без пробілів. |
| `items[].record.fields` | `object` | так | Значення полів. Відсутнє поле — без змін; null заборонено (для очищення — 'cleared'). |
| `items[].record.cleared` | array of `string` | ні | Поля, які треба явно очистити в поточному стані. |
| `items[].record.completeness` | enum: `full`, `partial` | ні | full — обробник заявляє, що передав усі поля, які знайшов у матеріалі (інформативно; семантику злиття не змінює); partial — лише частину полів (наприклад, завдання перевірки ціни).; типово `"partial"` |
| `items[].record.observation` | `ObservationOrder` | так | Порядок спостережень. Порівняння: спочатку observed_at (час отримання матеріалу колектором), потім sequence (ревізія джерела, якщо є), потім observation_id лексикографічно. Більше — новіше. Час обробки чи доставки в порівнянні не бере участі. |
| `items[].record.provenance` | `Provenance` | ні |  |
| `items[].record.confidence` | `number` | ні | мін. `0`; макс. `1` |
| `items[].received_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].delivery_key` | `string` | ні |  |
| `items[].applied_fields` | array of `string` | так |  |
| `items[].stale_fields` | array of `string` | так |  |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `history`:

```json
{
  "items": [
    {
      "record": {
        "entity_type": "product",
        "key": {
          "scope": "shop-example",
          "natural": {
            "sku": "A-100"
          }
        },
        "fields": {
          "price": {
            "amount": 1399.0,
            "currency": "UAH"
          }
        },
        "observation": {
          "observation_id": "obs_01J9ZQ0000000000000000LATE",
          "observed_at": "2026-09-26T08:00:00Z"
        }
      },
      "received_at": "2026-09-28T07:00:00Z",
      "delivery_key": "7e1c0b9f1e4d4a8a9c0d2e1f3a4b5c6d",
      "applied_fields": [],
      "stale_fields": [
        "price"
      ]
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
