# GET /v1/audit-events

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1438). Не редагуйте вручну.

**Журнал аудиту (активації, відкати, зміни конфігурацій, підключень і лімітів)**

| Властивість | Значення |
|---|---|
| operationId | `listAuditEvents` |
| Метод і шлях | `GET /v1/audit-events` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | audit |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `since` | query | `string` (date-time) | ні | Події від цього часу включно (UTC RFC 3339). |
| `until` | query | `string` (date-time) | ні | Події до цього часу, не включно (UTC RFC 3339). |
| `subject_type` | query | enum: `source`, `task`, `stage`, `connection`, `limits`, `problem_group` | ні |  |
| `subject_id` | query | `string` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка подій. | `object` |
| `400` | Некоректний синтаксис запиту (`bad_request`). | `problem` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `AuditEvent` | так |  |
| `items[].event_id` | `string` | так |  |
| `items[].at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].actor` | `string` | так |  |
| `items[].action` | `string` | так |  |
| `items[].subject_type` | `string` | так |  |
| `items[].subject_id` | `string` | так |  |
| `items[].details` | `object` | ні | Для оновлень changed містить змінені поля; before та after — їх фактичні значення із прихованими секретами. Старі події можуть містити лише назви полів. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `events`:

```json
{
  "items": [
    {
      "event_id": "aud_01J9ZV0000000000000000001",
      "at": "2026-09-27T10:20:00Z",
      "actor": "admin@example.org",
      "action": "stage.activate",
      "subject_type": "stage",
      "subject_id": "shop-catalog/extract-products",
      "details": {
        "version": "1.2.0",
        "previous": "1.1.0",
        "before": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.1.0"
          }
        },
        "after": {
          "package": {
            "package_id": "shop-example.product-extractor",
            "version": "1.2.0"
          }
        }
      }
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `400`, `401`.
