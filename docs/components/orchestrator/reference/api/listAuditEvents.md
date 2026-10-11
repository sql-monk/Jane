# GET /v1/audit-events

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1432). Не редагуйте вручну.

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
| `subject_type` | query | enum: `source`, `task`, `stage`, `connection`, `limits`, `problem_group` | ні |  |
| `subject_id` | query | `string` | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка подій. | `object` |
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
| `items[].details` | `object` | ні |  |
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
        "previous": "1.1.0"
      }
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
