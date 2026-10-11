# GET /v1/usage

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L496). Не редагуйте вручну.

**Облік витрат LLM**

| Властивість | Значення |
|---|---|
| operationId | `getUsage` |
| Метод і шлях | `GET /v1/usage` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | usage |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `scope_type` | query | enum: `platform`, `source`, `task` | ні |  |
| `scope_id` | query | `string` | ні |  |
| `since` | query | `string` (date-time) | ні |  |
| `until` | query | `string` (date-time) | ні |  |
| `group_by` | query | enum: `day`, `model`, `purpose`, `scope` | ні |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Звіт витрат. | `UsageReport` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `UsageRow` | так |  |
| `items[].period_start` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].scope_type` | enum: `platform`, `source`, `task` | ні |  |
| `items[].scope_id` | `string` | ні |  |
| `items[].model` | `string` | ні |  |
| `items[].purpose` | `string` | ні |  |
| `items[].requests` | `integer` | так | мін. `0` |
| `items[].input_tokens` | `integer` | так | мін. `0` |
| `items[].output_tokens` | `integer` | так | мін. `0` |
| `items[].cost` | `Money` | так |  |
| `items[].cost.amount` | `number` | так | мін. `0` |
| `items[].cost.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `items[].test_mode` | `boolean` | ні |  |
| `totals` | `UsageRow` | так |  |
| `totals.period_start` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `totals.scope_type` | enum: `platform`, `source`, `task` | ні |  |
| `totals.scope_id` | `string` | ні |  |
| `totals.model` | `string` | ні |  |
| `totals.purpose` | `string` | ні |  |
| `totals.requests` | `integer` | так | мін. `0` |
| `totals.input_tokens` | `integer` | так | мін. `0` |
| `totals.output_tokens` | `integer` | так | мін. `0` |
| `totals.cost` | `Money` | так |  |
| `totals.cost.amount` | `number` | так | мін. `0` |
| `totals.cost.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `totals.test_mode` | `boolean` | ні |  |

Приклад `daily`:

```json
{
  "items": [
    {
      "period_start": "2026-09-27T00:00:00Z",
      "requests": 128,
      "input_tokens": 240112,
      "output_tokens": 18230,
      "cost": {
        "amount": 0.42,
        "currency": "USD"
      },
      "test_mode": false
    }
  ],
  "totals": {
    "requests": 128,
    "input_tokens": 240112,
    "output_tokens": 18230,
    "cost": {
      "amount": 0.42,
      "currency": "USD"
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
