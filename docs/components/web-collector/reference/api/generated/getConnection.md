# getConnection

Прочитати підключення

Контракт: [contracts/openapi/collector.v1.yaml](../../../../../../contracts/openapi/collector.v1.yaml).

```http
GET /v1/connections/{connection_id}
```

## Доступ

```json
{
  "scope": [
    "connections:write",
    "collector:read"
  ],
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

```json
[
  {
    "in": "path",
    "name": "connection_id",
    "required": true,
    "schema": {
      "$ref": "../schemas/common/defs.schema.json#/$defs/Slug"
    }
  }
]
```

## Тіло запиту

Тіло запиту не визначено.

## Відповіді та помилки

| HTTP | Опис | Помилка |
|---|---|---|
| `200` | Підключення. | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |
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
    "description": "Підключення.",
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
  "404": {
    "content": {
      "application/problem+json": {
        "examples": {
          "notFound": {
            "$ref": "#/components/examples/ProblemNotFound"
          }
        },
        "schema": {
          "$ref": "#/components/schemas/Problem"
        }
      }
    },
    "description": "Ресурс не знайдено (`not_found`)."
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
  "x-jane-scope": [
    "connections:write",
    "collector:read"
  ]
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/openapi/common.yaml#/components/headers/ETag](../../../../../../contracts/openapi/common.yaml#/components/headers/ETag)
- [contracts/schemas/common/connection.schema.json](../../../../../../contracts/schemas/common/connection.schema.json)
- [contracts/examples/openapi/connection-pg.json](../../../../../../contracts/examples/openapi/connection-pg.json)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
- [contracts/openapi/common.yaml#/components/headers/RetryAfter](../../../../../../contracts/openapi/common.yaml#/components/headers/RetryAfter)
