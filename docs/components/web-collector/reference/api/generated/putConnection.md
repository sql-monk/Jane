# putConnection

Створити або замінити підключення (секрети — лише посиланнями)

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
PUT /v1/connections/{connection_id}
```

## Опис із контракту

```text
Викликає оркестратор, синхронізуючи реєстр підключень, або адміністратор автономного
виконавця. Значення, схожі на секрети, у `params` відхиляються (`secret_detected`).
```

## Доступ

```json
{
  "scope": "connections:write",
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
| `connection_id` | `path` | так |
| `If-Match` | `header` | ні |

```json
[
  {
    "in": "path",
    "name": "connection_id",
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
        "llm": {
          "$ref": "../examples/openapi/connection-llm.json"
        },
        "pg": {
          "$ref": "../examples/openapi/connection-pg.json"
        }
      },
      "schema": {
        "$ref": "../schemas/common/connection.schema.json"
      }
    }
  },
  "required": true
}
```


## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Підключення замінено. | ні |
| `201` | Підключення створено. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `412` | If-Match не збігається з поточним ETag (`precondition_failed`). | так |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | так |
| `501` | Виконавець не використовує підключень (`not_implemented`). | так |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "pg": {
            "$ref": "../examples/openapi/connection-pg.json"
          }
        },
        "schema": {
          "$ref": "../schemas/common/connection.schema.json"
        }
      }
    },
    "description": "Підключення замінено.",
    "headers": {
      "ETag": {
        "$ref": "common.yaml#/components/headers/ETag"
      }
    }
  },
  "201": {
    "content": {
      "application/json": {
        "examples": {
          "pg": {
            "$ref": "../examples/openapi/connection-pg.json"
          }
        },
        "schema": {
          "$ref": "../schemas/common/connection.schema.json"
        }
      }
    },
    "description": "Підключення створено.",
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
  },
  "501": {
    "content": {
      "application/problem+json": {
        "examples": {
          "notImplemented": {
            "value": {
              "code": "not_implemented",
              "status": 501,
              "title": "Not implemented",
              "type": "urn:jane:problem:not_implemented"
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/problem.schema.json"
        }
      }
    },
    "description": "Виконавець не використовує підключень (`not_implemented`)."
  },
  "503": {
    "content": {
      "application/problem+json": {
        "examples": {
          "unavailable": {
            "value": {
              "code": "service_unavailable",
              "retry_after_seconds": 5,
              "retryable": true,
              "status": 503,
              "title": "Service unavailable",
              "type": "urn:jane:problem:service_unavailable"
            }
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`).",
    "headers": {
      "Retry-After": {
        "$ref": "#/components/headers/RetryAfter"
      }
    }
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-scope": "connections:write"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/schemas/common/connection.schema.json](../../../../../../contracts/schemas/common/connection.schema.json)
- [contracts/examples/openapi/connection-pg.json](../../../../../../contracts/examples/openapi/connection-pg.json)
- [contracts/examples/openapi/connection-llm.json](../../../../../../contracts/examples/openapi/connection-llm.json)
- [contracts/openapi/common.yaml#/components/headers/ETag](../../../../../../contracts/openapi/common.yaml#/components/headers/ETag)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemValidation](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemValidation)
- [contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemIdempotencyReused)
- [contracts/schemas/common/problem.schema.json](../../../../../../contracts/schemas/common/problem.schema.json)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
