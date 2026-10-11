# POST /v1/connections/{connection_id}/test

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L644). Не редагуйте вручну.

**Перевірити підключення й розв'язання секретів**

| Властивість | Значення |
|---|---|
| operationId | `testConnection` |
| Метод і шлях | `POST /v1/connections/{connection_id}/test` |
| Scope | `connections:write` |
| Ідемпотентність | не потрібна: read-only check without side effects |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Результат перевірки (невдала перевірка — теж 200 з ok=false). | `ConnectionTestResult` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `ok` | `boolean` | так |  |
| `checked_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `latency_ms` | `integer` | ні | мін. `0` |
| `secrets_resolved` | `object` | ні | Для кожного secret_ref — чи вдалося його розв'язати в середовищі виконавця (без значень). |
| `message` | `string` | ні |  |

Приклад `ok`:

```json
{
  "ok": true,
  "checked_at": "2026-09-27T10:00:00Z",
  "latency_ms": 12,
  "secrets_resolved": {
    "username": true,
    "password": true
  }
}
```

Приклад `missingSecret`:

```json
{
  "ok": false,
  "checked_at": "2026-09-27T10:00:00Z",
  "secrets_resolved": {
    "username": true,
    "password": false
  },
  "message": "environment variable RESULTS_PG_PASSWORD is not set"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `503`.
