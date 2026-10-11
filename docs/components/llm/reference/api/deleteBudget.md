# DELETE /v1/budgets/{scope_type}/{scope_id}

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L483). Не редагуйте вручну.

**Прибрати бюджет рівня (діє успадкований)**

| Властивість | Значення |
|---|---|
| operationId | `deleteBudget` |
| Метод і шлях | `DELETE /v1/budgets/{scope_type}/{scope_id}` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | budgets |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `scope_type` | path | enum: `platform`, `source`, `task` | так |  |
| `scope_id` | path | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `204` | Видалено. | — |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
