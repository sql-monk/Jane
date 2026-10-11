# DELETE /v1/sources/{source_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L185). Не редагуйте вручну.

**Видалити джерело (заборонено, якщо є завдання)**

| Властивість | Значення |
|---|---|
| operationId | `deleteSource` |
| Метод і шлях | `DELETE /v1/sources/{source_id}` |
| Scope | `orchestrator:write`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | sources |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `source_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `204` | Видалено. | — |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `409`.
