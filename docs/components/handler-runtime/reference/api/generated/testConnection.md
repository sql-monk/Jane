# testConnection

Перевірити підключення й розв'язання секретів

Контракт: [contracts/openapi/handler.v1.yaml](../../../../../../contracts/openapi/handler.v1.yaml).

```http
POST /v1/connections/{connection_id}/test
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
| `200` | Результат перевірки (невдала перевірка — теж 200 з ok=false). | ні |
| `401` | Немає або недійсний токен (`unauthenticated`). | так |
| `404` | Ресурс не знайдено (`not_found`). | так |

```json
{
  "200": {
    "content": {
      "application/json": {
        "examples": {
          "missingSecret": {
            "value": {
              "checked_at": "2026-09-27T10:00:00Z",
              "message": "environment variable RESULTS_PG_PASSWORD is not set",
              "ok": false,
              "secrets_resolved": {
                "password": false,
                "username": true
              }
            }
          },
          "ok": {
            "value": {
              "checked_at": "2026-09-27T10:00:00Z",
              "latency_ms": 12,
              "ok": true,
              "secrets_resolved": {
                "password": true,
                "username": true
              }
            }
          }
        },
        "schema": {
          "$ref": "../schemas/common/connection.schema.json#/$defs/ConnectionTestResult"
        }
      }
    },
    "description": "Результат перевірки (невдала перевірка — теж 200 з ok=false)."
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
  }
}
```

## Метадані поведінки

```json
{
  "x-jane-no-idempotency-key": "read-only check without side effects",
  "x-jane-scope": "connections:write"
}
```

## Схеми

- [contracts/schemas/common/defs.schema.json#/$defs/Slug](../../../../../../contracts/schemas/common/defs.schema.json#/$defs/Slug)
- [contracts/schemas/common/connection.schema.json#/$defs/ConnectionTestResult](../../../../../../contracts/schemas/common/connection.schema.json#/$defs/ConnectionTestResult)
- [contracts/openapi/common.yaml#/components/schemas/Problem](../../../../../../contracts/openapi/common.yaml#/components/schemas/Problem)
- [contracts/openapi/common.yaml#/components/examples/ProblemNotFound](../../../../../../contracts/openapi/common.yaml#/components/examples/ProblemNotFound)
