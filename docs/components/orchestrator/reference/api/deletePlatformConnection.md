# DELETE /v1/connections/{connection_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1290). Не редагуйте вручну.

**Видалити підключення (заборонено, якщо на нього посилаються етапи)**

| Властивість | Значення |
|---|---|
| operationId | `deletePlatformConnection` |
| Метод і шлях | `DELETE /v1/connections/{connection_id}` |
| Scope | `orchestrator:admin` |
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
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `409`.
