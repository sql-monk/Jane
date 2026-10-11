# DELETE /v1/states/{state_key}

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L496). Не редагуйте вручну.

**Скинути збережений стан (наступний збір — з нуля)**

| Властивість | Значення |
|---|---|
| operationId | `resetCollectorState` |
| Метод і шлях | `DELETE /v1/states/{state_key}` |
| Scope | `collector:run` |
| Ідемпотентність | — |
| Теги | state |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `state_key` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `204` | Стан видалено. | — |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `409`, `503`.
