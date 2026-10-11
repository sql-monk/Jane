# putBudget

Задати бюджет рівня (оркестратор синхронізує сюди ліміти llm.budget джерел і завдань)

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
PUT /v1/budgets/{scope_type}/{scope_id}
```

## Доступ

```json
{
  "scope": "llm:admin",
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
| `scope_type` | `path` | так |
| `scope_id` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "scope_type",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/ScopeType"
    }
  },
  {
    "in": "path",
    "name": "scope_id",
    "required": true,
    "schema": {
      "type": "string"
    }
  }
]
```

## Тіло запиту

```json
{
  "content": {
    "application/json": {
      "examples": {
        "llmOff": {
          "summary": "amount 0 — LLM вимкнено для завдання: відхиляється будь-який виклик, навіть безкоштовної моделі",
          "value": {
            "budget": {
              "amount": 0,
              "currency": "USD",
              "period": "run"
            },
            "scope_id": "shop-price-check",
            "scope_type": "task"
          }
        },
        "task": {
          "value": {
            "budget": {
              "amount": 5,
              "currency": "USD",
              "period": "day"
            },
            "scope_id": "news-tg-events",
            "scope_type": "task"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/BudgetDefinition"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Збережено. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "task": {
            "value": {
              "budget": {
                "amount": 5,
                "currency": "USD",
                "period": "day"
              },
              "scope_id": "news-tg-events",
              "scope_type": "task"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/BudgetDefinition"
        }
      }
    },
    "description": "Збережено."
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
  "x-jane-scope": "llm:admin"
}
```

## Схеми

- [contracts/openapi/llm.v1.yaml#/components/schemas/ScopeType](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/ScopeType)
- [contracts/openapi/llm.v1.yaml#/components/schemas/BudgetDefinition](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/BudgetDefinition)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
