# putPlatformLimits

Змінити ліміти платформи без зміни коду

Контракт: [contracts/openapi/orchestrator.v1.yaml](../../../../../../contracts/openapi/orchestrator.v1.yaml).

```http
PUT /v1/limits/platform
```

## Доступ

```json
{
  "scope": "orchestrator:admin",
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
| `If-Match` | `header` | ні |

```json
[
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
        "dev": {
          "$ref": "../examples/openapi/platform-limits-dev.json"
        }
      },
      "schema": {
        "$ref": "../schemas/common/limits.schema.json#/$defs/PlatformLimits"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Збережено; нові запуски використовують нові значення. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `403` | Бракує прав (`forbidden`) або дію заборонено політикою (`access_denied_by_policy`). | так |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "dev": {
            "$ref": "../examples/openapi/platform-limits-dev.json"
          }
        },
        "schema": {
          "$ref": "../schemas/common/limits.schema.json#/$defs/PlatformLimits"
        }
      }
    },
    "description": "Збережено; нові запуски використовують нові значення.",
    "headers": {
      "ETag": {
        "$ref": "common.yaml#/components/headers/ETag"
      }
    }
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
  "403": {
    "content": {
      "application/problem+json": {
        "examples": {
          "forbidden": {
            "value": {
              "code": "forbidden",
              "detail": "scope registry:write required",
              "status": 403,
              "title": "Forbidden",
              "type": "urn:jane:problem:forbidden"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Бракує прав (`forbidden`) або дію заборонено політикою (`access_denied_by_policy`)."
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
  "x-jane-scope": "orchestrator:admin"
}
```

## Схеми

- [contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits](../../../../../../contracts/schemas/common/limits.schema.json#/$defs/PlatformLimits)
- [contracts/examples/openapi/platform-limits-dev.json](../../../../../../contracts/examples/openapi/platform-limits-dev.json)
- [contracts/openapi/common.yaml#/components/headers/ETag](../../../../../../contracts/openapi/common.yaml#/components/headers/ETag)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
