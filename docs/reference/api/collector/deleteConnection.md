# DELETE /v1/connections/{connection_id}

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L627). Не редагуйте вручну.

**Видалити підключення**

| Властивість | Значення |
|---|---|
| operationId | `deleteConnection` |
| Метод і шлях | `DELETE /v1/connections/{connection_id}` |
| Scope | `connections:write` |
| Ідемпотентність | — |
| Теги | connections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `204` | Видалено. | — |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `503`.
