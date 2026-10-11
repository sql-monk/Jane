# listBudgets

Визначення бюджетів за рівнями й поточні витрати

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
GET /v1/budgets
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

Параметрів у контракті немає.

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Бюджети. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "list": {
            "value": {
              "items": [
                {
                  "budget": {
                    "amount": 50,
                    "currency": "USD",
                    "period": "day"
                  },
                  "max_requests_per_minute": 60,
                  "scope_id": "platform",
                  "scope_type": "platform"
                },
                {
                  "budget": {
                    "amount": 5,
                    "currency": "USD",
                    "period": "day"
                  },
                  "scope_id": "news-tg-events",
                  "scope_type": "task"
                }
              ]
            }
          }
        },
        "schema": {
          "properties": {
            "items": {
              "items": {
                "$ref": "#/components/schemas/BudgetDefinition"
              },
              "type": "array"
            }
          },
          "required": [
            "items"
          ],
          "type": "object"
        }
      }
    },
    "description": "Бюджети."
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

- [contracts/openapi/llm.v1.yaml#/components/schemas/BudgetDefinition](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/BudgetDefinition)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
