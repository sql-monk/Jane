# getUsage

Облік витрат LLM

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
GET /v1/usage
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
| `scope_type` | `query` | ні |
| `scope_id` | `query` | ні |
| `since` | `query` | ні |
| `until` | `query` | ні |
| `group_by` | `query` | ні |

```json
[
  {
    "in": "query",
    "name": "scope_type",
    "required": false,
    "schema": {
      "$ref": "#/components/schemas/ScopeType"
    }
  },
  {
    "in": "query",
    "name": "scope_id",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "since",
    "required": false,
    "schema": {
      "format": "date-time",
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "until",
    "required": false,
    "schema": {
      "format": "date-time",
      "type": "string"
    }
  },
  {
    "in": "query",
    "name": "group_by",
    "required": false,
    "schema": {
      "default": "day",
      "enum": [
        "day",
        "model",
        "purpose",
        "scope"
      ],
      "type": "string"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Звіт витрат. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "daily": {
            "value": {
              "items": [
                {
                  "cost": {
                    "amount": 0.42,
                    "currency": "USD"
                  },
                  "input_tokens": 240112,
                  "output_tokens": 18230,
                  "period_start": "2026-09-27T00:00:00Z",
                  "requests": 128,
                  "test_mode": false
                }
              ],
              "totals": {
                "cost": {
                  "amount": 0.42,
                  "currency": "USD"
                },
                "input_tokens": 240112,
                "output_tokens": 18230,
                "requests": 128
              }
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/UsageReport"
        }
      }
    },
    "description": "Звіт витрат."
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

- [contracts/openapi/llm.v1.yaml#/components/schemas/ScopeType](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/ScopeType)
- [contracts/openapi/llm.v1.yaml#/components/schemas/UsageReport](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/UsageReport)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
