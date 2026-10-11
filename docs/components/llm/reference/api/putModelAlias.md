# PUT /v1/model-aliases/{alias}

> Згенеровано `scripts/docs_reference.py` з [llm.v1.yaml](../../../../../contracts/openapi/llm.v1.yaml#L189). Не редагуйте вручну.

**Призначити псевдонім моделі**

| Властивість | Значення |
|---|---|
| operationId | `putModelAlias` |
| Метод і шлях | `PUT /v1/model-aliases/{alias}` |
| Scope | `llm:admin` |
| Ідемпотентність | — |
| Теги | providers |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `alias` | path | `string` | так |  |

## Тіло запиту

Тип вмісту `application/json`, схема `ModelAlias`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `alias` | `string` | так |  |
| `provider_id` | `string` | так |  |
| `model_id` | `string` | так |  |

Приклад `strong`:

```json
{
  "alias": "strong",
  "provider_id": "main-llm",
  "model_id": "large-model-2026"
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Збережено. | `ModelAlias` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `alias` | `string` | так |  |
| `provider_id` | `string` | так |  |
| `model_id` | `string` | так |  |

Приклад `strong`:

```json
{
  "alias": "strong",
  "provider_id": "main-llm",
  "model_id": "large-model-2026"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `422`.
