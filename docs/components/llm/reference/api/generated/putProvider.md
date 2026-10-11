# putProvider

Створити або замінити провайдера (облікові дані — через connection_id)

Контракт: [contracts/openapi/llm.v1.yaml](../../../../../../contracts/openapi/llm.v1.yaml).

```http
PUT /v1/providers/{provider_id}
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
| `provider_id` | `path` | так |
| `If-Match` | `header` | ні |

```json
[
  {
    "in": "path",
    "name": "provider_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  },
  {
    "description": "ETag ресурсу для оптимістичного блокування. Розбіжність — 412 `precondition_failed`.",
    "example": "\"v7\"",
    "in": "header",
    "name": "If-Match",
    "required": false,
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
        "openaiCompatible": {
          "$ref": "#/components/examples/ProviderOpenAICompatible"
        }
      },
      "schema": {
        "$ref": "#/components/schemas/Provider"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Провайдера збережено. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "openaiCompatible": {
            "$ref": "#/components/examples/ProviderOpenAICompatible"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Provider"
        }
      }
    },
    "description": "Провайдера збережено."
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
  "412": {
    "content": {
      "application/problem+json": {
        "examples": {
          "precondition": {
            "value": {
              "code": "precondition_failed",
              "status": 412,
              "title": "Precondition failed",
              "type": "urn:jane:problem:precondition_failed"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "If-Match не збігається з поточним ETag (`precondition_failed`)."
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

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/llm.v1.yaml#/components/schemas/Provider](../../../../../../contracts/openapi/llm.v1.yaml#/components/schemas/Provider)
- [contracts/openapi/llm.v1.yaml#/components/examples/ProviderOpenAICompatible](../../../../../../contracts/openapi/llm.v1.yaml#/components/examples/ProviderOpenAICompatible)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
