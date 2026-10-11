# listOnboardingSessions

Сесії підключення, новіші першими (відновлення стану адмінки після перезавантаження)

Контракт: [contracts/openapi/assistant.v1.yaml](../../../../../../contracts/openapi/assistant.v1.yaml).

```http
GET /v1/onboarding-sessions
```

## Опис із контракту

```text
Курсорна пагінація (`limit`, `cursor` → `next_cursor`, `null` — сторінок більше немає; чужий курсор — 422).
Порядок — `created_at` спадно, за рівності — `session_id` спадно; нові сесії новіші за курсор, тож не
з'являються на наступних сторінках і не зсувають їх. Фільтр `status` бачить той самий стан, що й `GET` сесії.
Елементи — короткий стан сесії; повний (кандидати, вибірка, аналіз, варіанти) —
`GET /v1/onboarding-sessions/{session_id}`. Сесії без змін довше за налаштований строк зберігання
асистента (`state.session_retention_seconds`) видаляються.
```

## Доступ

```json
{
  "scope": "assistant:use",
  "security": [
    {
      "bearerAuth": []
    }
  ]
}
```

## Параметри

| Ім’я | Розміщення | Обов’язковий |
|---|---|---|
| `cursor` | `query` | ні |
| `limit` | `query` | ні |
| `status` | `query` | ні |

```json
[
  {
    "description": "Непрозорий курсор з `next_cursor` попередньої сторінки.",
    "in": "query",
    "name": "cursor",
    "required": false,
    "schema": {
      "maxLength": 2048,
      "type": "string"
    }
  },
  {
    "description": "Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму.",
    "in": "query",
    "name": "limit",
    "required": false,
    "schema": {
      "default": 50,
      "minimum": 1,
      "type": "integer"
    }
  },
  {
    "description": "Лише сесії в цих станах (параметр можна повторити, наприклад `?status=sampling&status=analyzing`).",
    "explode": true,
    "in": "query",
    "name": "status",
    "required": false,
    "schema": {
      "items": {
        "$ref": "#/components/schemas/OnboardingStatus"
      },
      "type": "array"
    },
    "style": "form"
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Сторінка сесій. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "page": {
            "value": {
              "items": [
                {
                  "costs": {
                    "amount": 0.05,
                    "currency": "USD"
                  },
                  "created_at": "2026-09-27T10:00:00Z",
                  "job_id": "job_01J9ZY0000000000000000JO2",
                  "proposal_count": 0,
                  "query": "https://tiny.example.test/",
                  "session_id": "onb_01J9ZY0000000000000000002",
                  "status": "insufficient_sample"
                },
                {
                  "costs": {
                    "amount": 0.31,
                    "currency": "USD"
                  },
                  "created_at": "2026-09-27T09:00:00Z",
                  "job_id": "job_01J9ZY0000000000000000JOB",
                  "proposal_count": 2,
                  "query": "Shop Example kettles",
                  "selected_candidate_id": "cand_1",
                  "session_id": "onb_01J9ZY0000000000000000001",
                  "status": "proposals_ready"
                }
              ],
              "next_cursor": "WyIyMDI2LTA5LTI3VDA5OjAwOjAwWiIsIm9uYl8wMUo5WlkwMDAwMDAwMDAwMDAwMDAwMDAxIl0"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/OnboardingSessionList"
        }
      }
    },
    "description": "Сторінка сесій."
  },
  "401": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unauthenticated": {
            "value": {
              "code": "unauthenticated",
              "status": 401,
              "title": "Unauthenticated",
              "type": "urn:jane:problem:unauthenticated"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Немає або недійсний токен (`unauthenticated`)."
  },
  "422": {
    "content": {
      "application/problem+json": {
        "examples": {
          "idempotencyReused": {
            "$ref": "#/components/examples/ProblemIdempotencyReused"
          },
          "validation": {
            "$ref": "#/components/examples/ProblemValidation"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо)."
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "assistant:use"
}
```

## Схеми

- [contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingStatus](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingStatus)
- [contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingSessionList](../../../../../../contracts/openapi/assistant.v1.yaml#/components/schemas/OnboardingSessionList)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
