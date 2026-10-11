# GET /v1/states/{state_key}

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L458). Не редагуйте вручну.

**Стан обходу/курсори, збережені колектором**

| Властивість | Значення |
|---|---|
| operationId | `getCollectorState` |
| Метод і шлях | `GET /v1/states/{state_key}` |
| Scope | `collector:read` |
| Ідемпотентність | — |
| Теги | state |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `state_key` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Підсумок збереженого стану. | `CollectorState` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `state_key` | `string` | так |  |
| `collector` | `string` | так |  |
| `updated_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `known_urls` | `integer` | ні | мін. `0` |
| `frontier_size` | `integer` | ні | мін. `0` |
| `cursors` | `object` | ні | Курсори, збережені для `state_key` (читаються наступним `mode: incremental`). Telegram — ключ `channel_id` (`-100…`), значення: `last_message_id` (найбільший виданий id), `last_edit_date` (найпізніший виданий `edit_date`, RFC 3339), `pts` (стан оновлень каналу, з якого наступний збір читає `getChannelDifference`; відсутній, поки збір каналу не дочитав історію до кінця — тоді наступний збір дочитує історію після `last_message_id`), `username`. Web — ключ `strategy_id`, значення: непорожній `snapshot()` стратегії (стан і діагностичні лічильники, наприклад `stats`); стан черги й історії URL не показується, лише `known_urls` і `frontier_size`. |

Приклад `web`:

```json
{
  "state_key": "shop-example",
  "collector": "web",
  "updated_at": "2026-09-27T12:00:00Z",
  "known_urls": 18234,
  "frontier_size": 0,
  "cursors": {}
}
```

Приклад `telegram`:

```json
{
  "state_key": "news-tg",
  "collector": "telegram",
  "updated_at": "2026-09-27T12:30:00Z",
  "cursors": {
    "-1001234567890": {
      "last_message_id": 4530,
      "last_edit_date": "2026-09-27T12:10:00Z",
      "pts": 9112,
      "username": "city_events_example"
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `503`.
