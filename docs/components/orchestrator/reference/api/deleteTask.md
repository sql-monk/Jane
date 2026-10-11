# DELETE /v1/tasks/{task_id}

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L388). Не редагуйте вручну.

**Видалити завдання (історія запусків зберігається)**

| Властивість | Значення |
|---|---|
| operationId | `deleteTask` |
| Метод і шлях | `DELETE /v1/tasks/{task_id}` |
| Scope | `orchestrator:write`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | tasks |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `task_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `204` | Видалено. | — |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `409`.
