# DELETE /v1/providers/{provider_id}

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L141). Не редагуйте вручну.

**Видалити провайдера**

| Властивість | Значення |
|---|---|
| operationId | `deleteProvider` |
| Метод і шлях | `DELETE /v1/providers/{provider_id}` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | providers |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `provider_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `204` | Видалено. | — |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `409`.
