# putModelAlias

Призначити псевдонім моделі

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
PUT /v1/model-aliases/{alias}
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
| `alias` | `path` | так |

```json
[
  {
    "in": "path",
    "name": "alias",
    "required": true,
    "schema": {
      "pattern": "^[a-z][a-z0-9_-]{0,31}$",
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
        "strong": {
          "value": {
            "alias": "strong",
            "model_id": "large-model-2026",
            "provider_id": "main-llm"
          }
        }
      },
      "schema": {
        "$ref": "#/components/schemas/ModelAlias"
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
          "strong": {
            "value": {
              "alias": "strong",
              "model_id": "large-model-2026",
              "provider_id": "main-llm"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/ModelAlias"
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

- [contracts/openapi/llm.v1.yaml#/components/schemas/ModelAlias](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/ModelAlias)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
